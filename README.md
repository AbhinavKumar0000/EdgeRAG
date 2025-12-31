# EdgeRAG

**A CPU-Optimized, End-to-End Retrieval-Augmented Generation System**

## Overview

EdgeRAG is an end-to-end Retrieval-Augmented Generation (RAG) system designed to run efficiently on CPU-only environments while preserving retrieval quality and generation faithfulness.

The project focuses on model optimization under constraints, combining:

- A fine-tuned embedding model optimized for retrieval
- A quantized generative model optimized for CPU inference
- A local-first design, with optional cloud APIs for demonstration and integration

Unlike API-wrapper RAG systems, EdgeRAG emphasizes:

- Model selection and trade-offs
- Training methodology
- Quantization strategies
- System-level efficiency

The complete system fits under ~1 GB total, making it suitable for edge devices and low-resource environments.

## System Architecture

EdgeRAG consists of three main layers:

### Embedding Layer
- Converts text into dense vectors
- Optimized for fast, CPU-based retrieval

### Retrieval Layer
- FAISS-based vector search
- Local index built from user documents

### Generation Layer
- Autoregressive language model
- Produces answers strictly grounded in retrieved context

The system supports:
- Fully local execution via CLI
- Cloud-hosted inference via FastAPI endpoints
- A web-based demo interface

## Embedding Model

### Base Model Selection

**Base model:** bge-small-en

- **Architecture:** Sentence-level bi-encoder (Transformer encoder)
- **Native embedding dimension:** 384

bge-small-en was chosen for:
- Strong retrieval performance
- Efficient encoder-only architecture
- Compatibility with contrastive fine-tuning

### Fine-Tuning Strategy

The embedding model was fine-tuned specifically for retrieval using contrastive learning.

#### Dataset Construction

A custom dataset (~150 samples) was generated using a triplet-based structure:

```json
{
  "anchor": "Research paper abstract",
  "positive": "Paraphrased or semantically equivalent abstract",
  "negative": "Unrelated research abstract"
}
```

- **Anchors:** Original research-style abstracts
- **Positives:** Semantically equivalent paraphrases
- **Negatives:** Hard negatives sampled from unrelated topics

The dataset was designed to maximize semantic separation, not just similarity scoring.

#### Training Objective

- Triplet loss
- Multi-ranking objective

The goal was to:
- Pull anchor–positive pairs closer
- Push anchor–negative pairs farther apart
- Increase retrieval margin rather than inflate cosine similarity

This improves robustness during nearest-neighbor search.

### Matryoshka Representation Learning

The model was trained using Matryoshka Representation Learning, enabling dimensional truncation without retraining.

- **Native dimension:** 384
- **Used dimension:** 128

**Key idea:**
- Earlier dimensions encode the most important semantic information
- Later dimensions refine details

By truncating embeddings to 128 dimensions:
- Computation is reduced by ~67%
- Retrieval quality (Recall@K) remains unchanged

This makes the system significantly faster and lighter for CPU-based retrieval.

### Embedding Model Optimization

- **Format:** ONNX
- **Precision:** INT8
- **Final size:** ~32 MB
- **Runtime:** ONNX Runtime (CPU)

Post-training quantization was applied with calibration to preserve embedding quality.

## Generative Model

### Base Model Selection

**Base model:** Qwen2.5-1.5B

- **Architecture:** Autoregressive Transformer decoder
- **Parameters:** ~1.5B
- **Context length:** 32,768 tokens

Qwen2.5-1.5B was selected for:
- Strong instruction-following behavior
- Long-context capability (important for RAG)
- Good quantization characteristics

### Quantization Strategy

The generative model was quantized using GGUF Q5_K_M format.

- **Baseline precision:** FP16
- **Quantized precision:** Mixed 5-bit
  - Attention layers: higher precision
  - Feed-forward layers: lower precision

This balances:
- Memory footprint
- Inference speed
- Output quality

### Final Generative Model Characteristics

- **Format:** GGUF
- **File size:** ~940 MB
- **Runtime:** llama.cpp
- **Inference:** CPU-only
- **KV-cache enabled:** Yes

Despite aggressive quantization, the model maintains strong faithfulness when grounded with retrieved context.

## Performance Summary

### Embedding Model

| Metric | Baseline (FP32) | Optimized (INT8 + Matryoshka) |
|--------|----------------|-------------------------------|
| Size | ~382 MB | ~32 MB |
| Dimensions | 384 | 128 |
| Retrieval Quality | Preserved | Preserved |

### Generative Model

| Metric | Baseline (FP16) | Optimized (GGUF Q5_K_M) |
|--------|----------------|------------------------|
| Size | ~4 GB | ~940 MB |
| GPU Required | Yes | No |
| Context Length | 32K | 32K |

## Local Execution (Recommended)

For best performance and full control, the system can be run entirely locally via CLI.

### Requirements

- Python 3.10+
- FAISS (CPU)
- ONNX Runtime
- llama.cpp compatible binary
- Sufficient RAM (~8–12 GB recommended)

### Local Workflow

1. **Ingest documents**
   - PDFs are chunked and embedded
   - FAISS index is built locally

2. **Run retrieval + generation**
   - Queries are embedded
   - Relevant chunks are retrieved
   - Generation is constrained to retrieved context

The main entry point for local execution is provided in the CLI files included in the repository.

## Cloud Deployment & APIs

For demonstration and integration purposes, EdgeRAG also supports cloud-hosted inference.

### Deployed Endpoints

#### Embedding API
- Hosted via FastAPI
- Uses the optimized ONNX INT8 embedding model

#### Generation API
- Hosted via FastAPI
- Streams tokens from the quantized GGUF model

**Important Note:**
- These endpoints are used only for the web demo and optional integrations
- Local CPU inference is the primary design
- Cloud APIs exist for convenience, testing, and demos

## Web Demo

A web-based playground is included to demonstrate the system end-to-end:

- Document upload
- Retrieval
- Streaming answer generation

**Note:** Due to free-tier limitations, performance may vary. For accurate benchmarking and throughput, local execution is recommended.

## Repository Structure

The repository includes:

- **Training files**
  - Contrastive fine-tuning scripts
  - Dataset generation logic

- **Evaluation files**
  - Retrieval and faithfulness evaluation

- **Local runtime**
  - CLI-based ingestion and querying
  - FAISS index management

- **API services**
  - FastAPI embedding service
  - FastAPI generation service with streaming

- **Web interface**
  - Demo website and UI logic

Each component is modular and can be used independently.

## Design Philosophy

EdgeRAG was built with the following principles:

- Optimize under constraints
- Prefer measurable trade-offs over scaling
- Preserve correctness while reducing cost
- Treat deployment as part of model design

This project demonstrates system-level ML engineering, not just model usage.

## When to Use EdgeRAG

- CPU-only environments
- Edge devices
- Low-resource servers
- Research and evaluation setups
- Custom RAG pipelines without vendor lock-in

## Future Work

- Larger contrastive datasets
- Domain-specific embedding fine-tuning
- Quantization-aware training
- Hybrid local + remote orchestration

## License

This project is provided for research and educational purposes. Refer to individual model licenses for redistribution constraints.
