import fitz, faiss, json, requests, numpy as np, os
from tqdm import tqdm

EMBED_URL = "https://abhinavdread-bge-en-ft-optimised.hf.space/embed"
EMBED_DIM = 128

class Ingestor:
    def __init__(self, chunk_size=500, overlap=100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text):
        chunks, i = [], 0
        while i < len(text):
            chunks.append(text[i:i+self.chunk_size])
            i += self.chunk_size - self.overlap
        return chunks

    def embed(self, texts):
        r = requests.post(EMBED_URL, json={"chunks": texts}, timeout=120)
        r.raise_for_status()
        return np.array(r.json()["embeddings"], dtype="float32")

    def ingest(self, pdf_path, index_path, meta_path):
        doc = fitz.open(pdf_path)
        records = []

        for p, page in enumerate(tqdm(doc, desc="Ingesting")):
            txt = page.get_text().strip()
            for ch in self.chunk(txt):
                records.append({
                    "text": ch,
                    "meta": {"page": p+1}
                })

        doc.close() # Explicitly close to release file lock
        embeds = self.embed([r["text"] for r in records])

        index = faiss.IndexFlatIP(EMBED_DIM)
        index.add(embeds)
        faiss.write_index(index, index_path)

        with open(meta_path, "w") as f:
            json.dump({i: records[i] for i in range(len(records))}, f)

        return len(records)
