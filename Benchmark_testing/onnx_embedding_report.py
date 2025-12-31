import os
import onnx
import numpy as np
from transformers import AutoTokenizer

ONNX_DIR = r"C:\Codes\Projects\Actual RAG\rag\bge-onnx-int8"
ONNX_MODEL_PATH = os.path.join(ONNX_DIR, "model.onnx")
TOKENIZER_PATH = ONNX_DIR
USED_DIM = 128  # Matryoshka effective dimension

def count_parameters(model):
    total = 0
    for tensor in model.graph.initializer:
        total += np.prod(tensor.dims)
    return total

def get_embedding_dim(model):
    for out in model.graph.output:
        shape = [d.dim_value for d in out.type.tensor_type.shape.dim]
        if len(shape) == 2:
            return shape[1]
    return "Unknown"

def main():
    print("\nLoading ONNX model...")
    model = onnx.load(ONNX_MODEL_PATH)

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)

    param_count = count_parameters(model)
    native_dim = get_embedding_dim(model)
    model_size_mb = os.path.getsize(ONNX_MODEL_PATH) / (1024 * 1024)

    report = {
        "Model Type": "Embedding Model (Bi-Encoder)",
        "Base Model": "BGE (Matryoshka fine-tuned)",
        "Parameters": f"{param_count/1e6:.2f} Million",
        "Embedding Dimension (native)": native_dim,
        "Embedding Dimension (used)": USED_DIM,
        "Embedding Strategy": "Matryoshka truncation",
        "Context Length": tokenizer.model_max_length,
        "Vocabulary Size": tokenizer.vocab_size,
        "Inference Engine": "ONNX Runtime",
        "Model Size": f"{model_size_mb:.2f} MB",
    }

    print("\nEmbedding Model Specifications")
    print("-" * 55)
    for k, v in report.items():
        print(f"{k:<35} {v}")

if __name__ == "__main__":
    main()
