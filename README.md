# EdgeRAG: Optimized Locally-Running RAG System

**EdgeRAG** is a high-efficiency Retrieval-Augmented Generation (RAG) system designed to run with minimal resources while maintaining high fidelity. It eliminates the need for expensive cloud APIs (like OpenAI or Anthropic) by leveraging heavily optimized open-source models that can run on consumer hardware or free-tier Spaces.

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Stack](https://img.shields.io/badge/stack-Flask%20%7C%20Tailwind%20%7C%20FAISS-forestgreen)

## 🚀 Key Features

*   **Zero External API Keys**: Fully independent stack. No OpenAI/Cohere keys required.
*   **Optimized Inference**:
    *   **Embedding**: Uses a custom fine-tuned `bge-small-en-v1.5` compressed to **ONNX INT8** with Matryoshka Reprsentation Learning (truncating dimensions from 384 → 128) without accuracy loss.
    *   **Generation**: Uses `Qwen2.5-1.5B-Instruct` quantized to **GGUF Q4_K_M** for strictly CPU-based inference.
*   **Private & Local**: Documents are ingested, chunked, and stored in a local FAISS index. Metadata never leaves your control (unless using the remote inference bridge).
*   **Interactive UI**: A modern, responsive web interface built with pure **HTML/JS** and **TailwindCSS** (Glassmorphism design).

---

## 🛠️ Technology Stack

### Backend
*   **Framework**: Python (Flask)
*   **Vector Engine**: FAISS (Facebook AI Similarity Search) - `IndexFlatIP`
*   **PDF Processing**: PyMuPDF (`fitz`)
*   **Task Management**: Threaded remote requests for non-blocking UI.

### Frontend
*   **Core**: HTML5, Vanilla JavaScript (ES6+)
*   **Styling**: TailwindCSS (CDN) + Custom CSS Variables
*   **Animations**: GSAP (GreenSock) for smooth section reveals.

### Models & Optimization
| Component | Original Model | Optimization Applied | Final Artifact |
| :--- | :--- | :--- | :--- |
| **Embedding** | `BAAI/bge-small-en-v1.5` | Matryoshka (384->128 dim) + INT8 Quantization | **ONNX** (~33MB) |
| **LLM** | `Qwen/Qwen2.5-1.5B` | GGUF Quantization (Q4_K_M) | **GGUF** (~900MB) |

---

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/actual-rag.git
    cd actual-rag
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install flask requests pymupdf faiss-cpu numpy tqdm
    ```

4.  **Run the Application**
    ```bash
    python main.py
    ```
    The server will start at `http://127.0.0.1:5000`.

---

## 📖 Usage Guide

1.  **Open the Web Interface**: Navigate to `http://localhost:5000` in your browser.
2.  **Upload Context**:
    *   Click on the **Upload PDF** area in the "Knowledge Base" card.
    *   Select a PDF file (e.g., a research paper, manual).
    *   The system will ingest, chunk, and index the file. Progress is shown in real-time.
3.  **Ask Questions**:
    *   Use the chat input on the right to ask questions about the document.
    *   The AI will retrieve relevant chunks and stream the answer.
4.  **Model Playground**:
    *   Scroll down to the "Model Playground" section to test the raw embedding and generation endpoints independently.

---

## 🔌 API Endpoints

The Flask backend exposes the following endpoints:

### `POST /upload`
Ingests a PDF file into the vector store.
*   **Body**: `multipart/form-data` with `file=@document.pdf`
*   **Process**: Parsing -> Sliding Window Chunking -> Embedding -> FAISS Indexing.

### `POST /ask`
Queries the RAG system.
*   **Body**: `{"question": "What is the transformer architecture?"}`
*   **Response**: Server-Sent Events (SSE) or simple streamed text response.

### `POST /clear`
Resets the session, deleting the temporary vector index and metadata.

---

## 🧠 Model Architecture

### The "Small-to-Big" Optimization
We prove that massive models are not always needed for specific tasks:
1.  **Ingestion**: We use a sliding window approach (`chunk_size=500`, `overlap=100`) to maintain semantic continuity.
2.  **Retrieval**: We use `IP` (Inner Product) similarity on normalized vectors, which is mathematically equivalent to Cosine Similarity but faster.
3.  **Generation**: We use a prompted `Qwen-1.5B` model. The prompt enforces "Strict Context Adherence" to reduce hallucinations.

> **Note**: The inference endpoints are currently hosted on Hugging Face Spaces for demonstration stability, but the code is fully compatible with local `onnxruntime` and `llama-cpp-python` setups.

---

## 📄 License
MIT License. Free to use and modify.
