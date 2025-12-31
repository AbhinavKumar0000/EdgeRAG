import os
from pathlib import Path
import pymupdf4llm # type: ignore
from tqdm import tqdm
import argparse

def convert_pdfs_in_download_folder(download_dir="download", markdown_dir="markdown"):
    download_path = Path(download_dir)
    markdown_root = Path(markdown_dir)
    markdown_root.mkdir(exist_ok=True)

    if not download_path.exists():
        print(f"Error: '{download_dir}' folder not found!")
        return

    pdf_files = list(download_path.rglob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in 'download/' or subfolders.")
        return

    print(f"Found {len(pdf_files)} PDF files. Starting conversion to Markdown...\n")

    converted_count = 0

    for pdf_path in tqdm(pdf_files, desc="Converting PDFs"):
        rel_path = pdf_path.relative_to(download_path).parent
        md_folder = markdown_root / rel_path
        md_folder.mkdir(parents=True, exist_ok=True)

        md_path = md_folder / (pdf_path.stem + ".md")

        if md_path.exists():
            print(f"Skipping (already exists): {md_path.name}")
            continue

        try:
            md_text = pymupdf4llm.to_markdown(str(pdf_path), ignore_graphics=True)

            md_path.write_text(md_text, encoding="utf-8")

            print(f"✓ Converted: {pdf_path.name} → markdown/{rel_path}/{md_path.name}")
            converted_count += 1

        except Exception as e:
            print(f"✗ Failed: {pdf_path.name} → {e}")

    print("\n" + "="*60)
    print(f"Conversion complete! {converted_count}/{len(pdf_files)} PDFs converted.")
    print(f"All Markdown files saved in '{markdown_dir}/' with same topic folder structure.")
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert downloaded arXiv PDFs to Markdown")
    args = parser.parse_args()

    convert_pdfs_in_download_folder()