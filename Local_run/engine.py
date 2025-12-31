import faiss, json, os, sys
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
from llama_cpp import Llama

class RAGEngine:
    def __init__(self, index_path, meta_path, onnx_dir, llm_path):
        self.index = faiss.read_index(index_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        
        self.tokenizer = AutoTokenizer.from_pretrained(onnx_dir)
        self.session = ort.InferenceSession(os.path.join(onnx_dir, "model.onnx"), providers=["CPUExecutionProvider"])
        self.llm = Llama(model_path=llm_path, n_ctx=4096, n_threads=os.cpu_count(), verbose=False)
        self.faiss_dim = self.index.d

    def embed_query(self, text):
        encoded = self.tokenizer(text, return_tensors="np", padding=True, truncation=True, max_length=512)
        inputs = {k: encoded[k] for k in {i.name for i in self.session.get_inputs()}}
        output = self.session.run(None, inputs)[0]
        emb = output.mean(axis=1)[:, :self.faiss_dim]
        emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)
        return emb.astype("float32")

    def retrieve(self, query, top_k=15, final_k=4):
        qvec = self.embed_query(query)
        scores, ids = self.index.search(qvec, top_k)
        chunks = []
        for raw_score, idx in zip(scores[0], ids[0]):
            if idx == -1: continue
            sim = max(0.0, min(float(raw_score) / 2.0, 1.0))
            if sim < 0.40: continue
            chunks.append({"text": self.metadata[str(idx)]["text"], "score": sim})
        chunks.sort(key=lambda x: x["score"], reverse=True)
        return chunks[:final_k]

    def generate(self, question, chunks):
        context = "\n\n".join([c["text"] for c in chunks])
        prompt = f"<|im_start|>system\nUse ONLY the context.\n<|im_end|>\n<|im_start|>user\nContext:\n{context}\n\nQuestion:\n{question}\n<|im_end|>\n<|im_start|>assistant\n"
        
        output = ""
        for c in self.llm.create_completion(prompt=prompt, max_tokens=300, temperature=0.2, stream=True):
            token = c["choices"][0]["text"]
            sys.stdout.write(token); sys.stdout.flush()
            output += token
        return output.strip()