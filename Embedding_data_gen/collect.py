import os
import re
import arxiv
import requests
from tqdm import tqdm  

def sanitize_filename(filename):
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return filename[:150] + '.pdf'

topic = input("Enter the topic: ").strip()
if not topic:
    print("Topic cannot be empty!")
    exit()

try:
    num_papers = int(input("Enter the number of papers to download: ").strip())
    if num_papers <= 0:
        raise ValueError
except ValueError:
    print("Please enter a valid positive number.")
    exit()

download_dir = "download"
topic_dir = os.path.join(download_dir, sanitize_filename(topic.replace(" ", "_")[:-4]))  # Remove .pdf if added
os.makedirs(topic_dir, exist_ok=True)

print(f"\nSearching arXiv for: '{topic}'")
print(f"Goal: Download {num_papers} PDFs into '{topic_dir}'\n")

client = arxiv.Client(
    page_size=500,
    delay_seconds=3.0,
    num_retries=5
)

search = arxiv.Search(
    query=topic,
    max_results=None, 
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending
)

downloaded_count = 0
results_generator = client.results(search)

print("Starting search and downloads...\n")

for result in results_generator:
    if downloaded_count >= num_papers:
        break

    title = result.title or "Untitled"
    safe_filename = sanitize_filename(title)
    filepath = os.path.join(topic_dir, safe_filename)

    if os.path.exists(filepath):
        print(f"Already exists ({downloaded_count + 1}/{num_papers}): {title}")
        downloaded_count += 1
        continue

    pdf_url = result.pdf_url
    if not pdf_url:
        print(f"No PDF URL for: {title}")
        continue

    try:
        print(f"Downloading ({downloaded_count + 1}/{num_papers}): {title}")

        response = requests.get(pdf_url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024  

        with open(filepath, 'wb') as f, tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            desc=safe_filename[:40],  
            leave=False
        ) as pbar:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

        print(f"✓ Saved: {safe_filename}\n")
        downloaded_count += 1

    except Exception as e:
        print(f"✗ Failed to download '{title}': {e}")
        print("Skipping and trying next paper...\n")

print("=" * 60)
if downloaded_count == num_papers:
    print(f"SUCCESS! Downloaded all {num_papers} papers.")
elif downloaded_count > 0:
    print(f"PARTIAL SUCCESS: Downloaded {downloaded_count}/{num_papers} papers.")
    print("   → Many recent papers may not have PDFs available yet.")
else:
    print(f"FAILED: Downloaded 0/{num_papers} papers.")
    print("   → Try a more specific topic or add category like 'cat:cs.LG' to query.")
print(f"Files saved in: {topic_dir}")
print("Done!")