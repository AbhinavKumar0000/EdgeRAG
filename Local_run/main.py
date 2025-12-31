import os
from ingest import Ingestor
from engine import RAGEngine

# Paths
MODEL_DIR = r"C:\Codes\Projects\Actual RAG\rag\bge-onnx-int8"
LLM_PATH = r"C:\Codes\Projects\Actual RAG\rag\llama-b7564-bin-win-cpu-x64\qwen2.5-1.5b-instruct-q4_k_m.gguf"
INDEX_PATH = "faiss.index"
META_PATH = "meta.json"

def main():
    # 1. Ingestion Phase
    pdf_input = input("Enter the full path to the PDF file: ").strip()
    if not os.path.exists(pdf_input):
        print("Error: PDF file not found.")
        return

    print("\n--- Starting Ingestion ---")
    ingestor = Ingestor(MODEL_DIR)
    num_chunks = ingestor.run_ingestion(pdf_input, INDEX_PATH, META_PATH)
    print(f"✅ Ingestion Complete. Processed {num_chunks} chunks.")

    # 2. Retrieval/Generation Phase
    print("\n--- Loading RAG Engine ---")
    engine = RAGEngine(INDEX_PATH, META_PATH, MODEL_DIR, LLM_PATH)

    print("\nSystem Ready! Type 'exit' to stop.")
    while True:
        query = input("\nQuestion: ").strip()
        if query.lower() == 'exit': break
        
        chunks = engine.retrieve(query)
        if not chunks:
            print("Answer: OUT OF CONTEXT")
            continue
            
        print("Answer: ", end="")
        engine.generate(query, chunks)
        print("\n")

if __name__ == "__main__":
    main()