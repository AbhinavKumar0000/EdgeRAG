import os
import json
import time
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer, util # type: ignore

API_KEY = ""
BASE_DIR = './markdown'  
OUTPUT_FILE = 'triplets.jsonl'
MODEL_NAME = 'bge-small-en-v1.5' 

genai.configure(api_key=API_KEY)
llm = genai.GenerativeModel('gemini-2.5-flash')
embedder = SentenceTransformer(f'BAAI/{MODEL_NAME}')


def generate_query(text_chunk):
    """Teacher LLM generates a technical question."""
    prompt = f"""You are an academic expert. Based on the research paper chunk below, 
    generate ONE highly specific technical question that can only be answered by this text.
    
    Text: {text_chunk}
    
    Question:"""
    try:
        response = llm.generate_content(prompt)
        if response.text:
            return response.text.strip()
        return None
    except Exception as e:
        print(f"   [!] API Error: {e}")
        return None

def get_hard_negative(query, positive_chunk, all_chunks):
    """Finds a 'distractor' chunk from the same context."""
    if len(all_chunks) < 2:
        return "Not enough context for a hard negative."
    
    query_emb = embedder.encode(query, convert_to_tensor=True)
    doc_embs = embedder.encode(all_chunks, convert_to_tensor=True)
    
    hits = util.semantic_search(query_emb, doc_embs, top_k=3)[0]
    
    for hit in hits:
        candidate = all_chunks[hit['corpus_id']]
        if candidate.strip() != positive_chunk.strip():
            return candidate
    return all_chunks[0]


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

with open(OUTPUT_FILE, 'a', encoding='utf-8') as f_out:
    for root, dirs, files in os.walk(BASE_DIR):
        for filename in files:
            if filename.endswith('.md'):
                file_path = os.path.join(root, filename)
                category = os.path.basename(root) 
                
                print(f"\n>>> Processing [{category.upper()}]: {filename}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f_in:
                        content = f_in.read()
                    
                    doc_chunks = text_splitter.split_text(content)
                    print(f"    Found {len(doc_chunks)} chunks.")

                    for i, chunk in enumerate(doc_chunks):
                        time.sleep(2) 
                        
                        query = generate_query(chunk)
                        if not query: continue
                        
                        hard_neg = get_hard_negative(query, chunk, doc_chunks)
                        
                        triplet = {
                            "query": query,
                            "pos": [chunk],
                            "neg": [hard_neg],
                            "meta": {"source": filename, "category": category}
                        }
                        
                        f_out.write(json.dumps(triplet) + '\n')
                        print(f"    Done {i+1}/{len(doc_chunks)}", end='\r')
                        
                except Exception as e:
                    print(f"   [!!] Failed to process {filename}: {e}")

print("\n\nSuccess! 150 files processed into triplets.jsonl")