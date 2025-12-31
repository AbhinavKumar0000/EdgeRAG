import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ingest import Ingestor
from engine import RAGEngine

app = FastAPI(
    title="Paper-Grounded RAG API",
    description="Upload a PDF and ask questions using a local LLM with streaming responses.",
    version="1.0.0"
)

# ================= CONFIG =================
MODEL_DIR = r"rag/bge-onnx-int8"
LLM_PATH = r"rag/llama-b7564-bin-win-cpu-x64/qwen2.5-1.5b-instruct-q4_k_m.gguf"
INDEX_PATH = "faiss.index"
META_PATH = "meta.json"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Global engine instance
engine = None

# Try to load engine on startup if index exists
if os.path.exists(INDEX_PATH):
    engine = RAGEngine(INDEX_PATH, META_PATH, MODEL_DIR, LLM_PATH)

class QueryRequest(BaseModel):
    question: str

@app.post("/upload", tags=["Ingestion"])
async def upload_pdf(file: UploadFile = File(...)):
    """Uploads a PDF, chunks it, and builds a FAISS index."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Run Ingestion
    ingestor = Ingestor(MODEL_DIR)
    ingestor.run_ingestion(file_path, INDEX_PATH, META_PATH)
    
    # Reload Engine with new data
    global engine
    engine = RAGEngine(INDEX_PATH, META_PATH, MODEL_DIR, LLM_PATH)
    
    return {"message": "PDF processed and indexed successfully", "filename": file.filename}

@app.post("/ask", tags=["Retrieval & Generation"])
async def ask_question(request: QueryRequest):
    """Answers a question based on the uploaded PDF with streaming tokens."""
    global engine
    if engine is None:
        raise HTTPException(status_code=400, detail="No PDF indexed yet. Please upload a PDF first.")
    
    chunks = engine.retrieve(request.question)
    if not chunks:
        return {"answer": "OUT OF CONTEXT", "confidence": 0}

    def stream_generator():
        context = "\n\n".join([c["text"] for c in chunks])
        prompt = (
            "<|im_start|>system\nYou are a paper-grounded assistant. Use ONLY the context.\n<|im_end|>\n"
            f"<|im_start|>user\nContext:\n{context}\n\nQuestion:\n{request.question}\n<|im_end|>\n"
            "<|im_start|>assistant\n"
        )
        
        # Stream from llama-cpp-python
        for completion in engine.llm.create_completion(
            prompt=prompt, 
            max_tokens=300, 
            temperature=0.2, 
            stream=True
        ):
            token = completion["choices"][0]["text"]
            yield token

    return StreamingResponse(stream_generator(), media_type="text/plain")