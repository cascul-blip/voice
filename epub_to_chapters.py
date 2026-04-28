#!/usr/bin/env python3
import sys
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def extract_chapters(epub_path, output_dir="chapters"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    book = epub.read_epub(epub_path)

    # Process documents in the order defined by the spine
    for i, item in enumerate(book.get_items_of_type(ebooklib.ITEM_DOCUMENT)):
        content = item.get_content()
        soup = BeautifulSoup(content, 'html.parser')

        # Extract clean text
        text = soup.get_text(separator='\n', strip=True)

        # Generate a clean filename
        title_tag = soup.find('title')
        chapter_title = title_tag.get_text().strip() if title_tag else f"chapter_{i+1:03d}"

        # Sanitize filename
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in chapter_title)[:80]
        filename = f"{i+1:03d}_{safe_title}.txt"

        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"Extracted: {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 epub_to_chapters.py <input.epub>")
        sys.exit(1)

    extract_chapters(sys.argv[1])
    print(f"\nAll chapters have been extracted to the '{os.path.join(os.getcwd(), 'chapters')}' directory.")
