from gguf import GGUFReader
import os

GGUF_MODEL = r"C:\Codes\Projects\Actual RAG\rag\llama-b7564-bin-win-cpu-x64\qwen2.5-1.5b-instruct-q4_k_m.gguf"

QUANTIZATION_MAP = {
    2: "Q4_0", 3: "Q4_1", 6: "Q5_0", 7: "Q5_1", 8: "Q8_0",
    12: "Q4_K_S", 13: "Q4_K_M", 14: "Q5_K_S", 15: "Q5_K_M", 
    16: "Q2_K", 17: "Q3_K_S", 18: "Q3_K_M", 19: "Q3_K_L",
}

def get_val(reader, key, default="Unknown"):
    if key not in reader.fields:
        return default
    val = reader.fields[key].parts[-1]
    if hasattr(val, 'item'):
        if val.size == 1: return val.item()
        if val.dtype.kind in ('u', 'i'): val = val.tobytes()
    if isinstance(val, (bytes, bytearray)):
        return val.decode('utf-8', errors='ignore').strip('\x00')
    return val

def count_parameters_manually(reader):
    """Counts parameters by summing the elements of every tensor in the file."""
    total_params = 0
    for tensor in reader.tensors:
        total_params += tensor.n_elements
    return total_params

def main():
    if not os.path.exists(GGUF_MODEL):
        print(f"Error: Model not found at {GGUF_MODEL}")
        return

    print(f"Scanning tensors in {os.path.basename(GGUF_MODEL)}...")
    reader = GGUFReader(GGUF_MODEL, "r")

    arch = get_val(reader, "general.architecture", default="qwen2")
    
    # 1. Try metadata count first
    param_count = get_val(reader, "general.parameter_count", default=None)
    
    # 2. If metadata missing, calculate manually (The Fix)
    if param_count is None:
        print(" -> Metadata missing. Calculating actual parameters from tensors...")
        param_count = count_parameters_manually(reader)

    # Formatting
    ft_id = get_val(reader, "general.file_type", default=0)
    
    report = {
        "Model Family": str(arch).upper(),
        "Parameter Count": f"{param_count / 1e9:.2f} B",
        "Context Length": get_val(reader, f"{arch}.context_length"),
        "Embedding Dim": get_val(reader, f"{arch}.embedding_length"),
        "Attention Heads": get_val(reader, f"{arch}.attention.head_count"),
        "Layer Count": get_val(reader, f"{arch}.block_count"),
        "Quantization": QUANTIZATION_MAP.get(ft_id, f"Type-ID: {ft_id}"),
        "File Size": f"{os.path.getsize(GGUF_MODEL) / (1024**2):.2f} MB"
    }

    print("\nGenerative Model Specifications")
    print("-" * 45)
    for k, v in report.items():
        print(f"{k:<25} : {v}")

if __name__ == "__main__":
    main()