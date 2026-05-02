#!/usr/bin/env python3
import os
import sys

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub


def _sanitize_filename_component(s: str, max_len: int = 80) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    s = "".join(c if c.isalnum() or c in " -_" else "_" for c in s)
    s = " ".join(s.split())
    return s[:max_len].strip(" ._-")


def _iter_toc_entries(toc):
    """
    Yields (title, href) pairs from ebooklib's nested TOC structure.
    """
    if toc is None:
        return
    if isinstance(toc, (list, tuple)):
        for entry in toc:
            yield from _iter_toc_entries(entry)
        return
    # ebooklib.epub.Link / ebooklib.epub.Section both carry title + href
    title = getattr(toc, "title", None)
    href = getattr(toc, "href", None)
    if title and href:
        yield (str(title), str(href))


def _build_href_title_map(book: epub.EpubBook) -> dict:
    href_to_title: dict[str, str] = {}
    for title, href in _iter_toc_entries(getattr(book, "toc", None)):
        href_base = href.split("#", 1)[0]
        if href_base and href_base not in href_to_title:
            href_to_title[href_base] = title.strip()
    return href_to_title


def extract_chapters(epub_path, output_dir="chapters"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    book = epub.read_epub(epub_path)
    href_to_title = _build_href_title_map(book)
    used_filenames: set[str] = set()

    # Process documents in the order defined by the spine (reading order)
    spine_ids = [
        idref for (idref, _linear) in getattr(book, "spine", []) if idref != "nav"
    ]
    spine_items = [book.get_item_with_id(idref) for idref in spine_ids]
    spine_items = [
        it
        for it in spine_items
        if it is not None and it.get_type() == ebooklib.ITEM_DOCUMENT
    ]

    # Fallback if spine is missing/empty
    if not spine_items:
        spine_items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

    for i, item in enumerate(spine_items):
        content = item.get_content()
        soup = BeautifulSoup(content, "html.parser")

        # Extract clean text
        text = soup.get_text(separator="\n", strip=True)

        # Prefer EPUB TOC title for this document; fall back to headings/title tag; then numbering.
        chapter_title = None
        item_href = getattr(item, "file_name", None)
        if item_href:
            chapter_title = href_to_title.get(item_href)

        if not chapter_title:
            heading = soup.find(["h1", "h2", "h3"])
            if heading:
                chapter_title = heading.get_text(separator=" ", strip=True)

        if not chapter_title:
            title_tag = soup.find("title")
            if title_tag:
                chapter_title = title_tag.get_text(separator=" ", strip=True)

        if not chapter_title:
            chapter_title = f"chapter_{i + 1:03d}"

        # Sanitize filename
        safe_title = (
            _sanitize_filename_component(chapter_title) or f"chapter_{i + 1:03d}"
        )
        base = f"{i + 1:03d}_{safe_title}"
        filename = f"{base}.txt"
        dedupe_n = 2
        while filename in used_filenames:
            filename = f"{base}_{dedupe_n}.txt"
            dedupe_n += 1
        used_filenames.add(filename)

        output_path = os.path.join(output_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Extracted: {filename}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 epub_to_chapters.py <input.epub>")
        sys.exit(1)

    extract_chapters(sys.argv[1])
    # print(f"\nAll chapters have been extracted to the '{os.path.join(os.getcwd(), 'chapters')}' directory.")
