import io, re, json, uuid, fitz, faiss, os
import numpy as np
import onnxruntime as ort
import pytesseract
from PIL import Image
from transformers import AutoTokenizer
from tqdm import tqdm

class Ingestor:
    def __init__(self, model_dir, embed_dim=128, chunk_size=500, chunk_overlap=100):
        self.model_dir = model_dir
        self.embed_dim = embed_dim
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.session = ort.InferenceSession(
            os.path.join(model_dir, "model.onnx"),
            providers=["CPUExecutionProvider"]
        )
        self.input_names = {i.name for i in self.session.get_inputs()}
        self.section_patterns = {
            "abstract": re.compile(r"\babstract\b", re.I),
            "introduction": re.compile(r"\bintroduction\b", re.I),
            "methods": re.compile(r"\b(methods?|materials)\b", re.I),
            "results": re.compile(r"\bresults?\b", re.I),
            "discussion": re.compile(r"\bdiscussion\b", re.I),
            "conclusion": re.compile(r"\bconclusion\b", re.I),
        }
        self.figure_regex = re.compile(r"\b(fig\.?|figure|table)\b", re.I)

    def detect_section(self, text, current_section):
        head = text[:300]
        for sec, pat in self.section_patterns.items():
            if pat.search(head): return sec
        return current_section

    def embed_batch(self, texts, batch_size=8):
        all_vecs = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            encoded = self.tokenizer(batch, padding="max_length", truncation=True, max_length=512, return_tensors="np")
            inputs = {k: encoded[k] for k in self.input_names}
            outputs = self.session.run(None, inputs)[0]
            vecs = outputs[:, 0, :] # CLS Pooling
            all_vecs.append(vecs[:, :self.embed_dim].astype("float32"))
        return np.vstack(all_vecs)

    def chunk_text(self, text):
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
        return chunks

    def run_ingestion(self, pdf_path, index_path, meta_path):
        doc = fitz.open(pdf_path)
        records = []
        current_section = "unknown"
        
        for pidx, page in enumerate(tqdm(doc, desc="Ingesting PDF")):
            page_text = page.get_text().strip()
            if page_text:
                current_section = self.detect_section(page_text, current_section)
                for i, ch in enumerate(self.chunk_text(page_text)):
                    records.append({"text": ch, "metadata": {"page": pidx+1, "section": current_section, "type": "text"}})
            
            # OCR Figures
            for img in page.get_images(full=True):
                img_dict = doc.extract_image(img[0])
                ocr_text = pytesseract.image_to_string(Image.open(io.BytesIO(img_dict["image"])).convert("RGB")).strip()
                if ocr_text:
                    for i, ch in enumerate(self.chunk_text(ocr_text)):
                        records.append({"text": ch, "metadata": {"page": pidx+1, "section": current_section, "type": "figure"}})

        print("Embedding chunks...")
        embeddings = self.embed_batch([r["text"] for r in records])
        
        index = faiss.IndexFlatIP(self.embed_dim)
        index.add(embeddings)
        faiss.write_index(index, index_path)
        
        meta = {i: records[i] for i in range(len(records))}
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        return len(records)