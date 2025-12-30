import faiss, json, requests, numpy as np

EMBED_URL = "https://abhinavdread-bge-en-ft-optimised.hf.space/embed"
GEN_URL   = "https://abhinavdread-qwen-1-5b-q4-k-m.hf.space/generate"

class RAGEngine:
    def __init__(self, index_path, meta_path):
        self.index = faiss.read_index(index_path)
        self.meta = json.load(open(meta_path))

    def embed_query(self, q):
        r = requests.post(EMBED_URL, json={"chunks": [q]}, timeout=30)
        return np.array(r.json()["embeddings"], dtype="float32")

    def retrieve(self, query, k=4):
        qv = self.embed_query(query)
        scores, ids = self.index.search(qv, 15)

        chunks = []
        for s, i in zip(scores[0], ids[0]):
            if i == -1: continue
            if s < 0.4: continue
            chunks.append(self.meta[str(i)]["text"])

        return chunks[:k]

    def stream_answer(self, question, chunks):
        context = "\n\n".join(chunks)
        prompt = f"""<|im_start|>system
Use ONLY the context.
<|im_end|>
<|im_start|>user
Context:
{context}

Question:
{question}
<|im_end|>
<|im_start|>assistant
"""

        with requests.post(
            GEN_URL,
            json={"prompt": prompt},
            stream=True,
            timeout=300
        ) as r:
            for chunk in r.iter_content(chunk_size=None):
                if chunk:
                    yield chunk.decode("utf-8")
