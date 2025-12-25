import io
from typing import Any, Dict, List

import fitz
import pdfplumber

from backend.core.parsers.types import ParsedAsset


def _extract_title(metadata: Dict[str, Any]) -> str:
    title = metadata.get("title")
    if isinstance(title, str):
        return title.strip()
    return ""


def parse_pdf(content: bytes) -> ParsedAsset:
    page_entries: List[Dict[str, Any]] = []
    text_parts: List[str] = []

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            page_text = page_text.strip()
            if page_text:
                text_parts.append(f"[Page {index}]\n{page_text}")
            page_title = page_text.splitlines()[0].strip() if page_text else ""
            page_entries.append(
                {"page_number": index, "title": page_title, "char_count": len(page_text)}
            )

    with fitz.open(stream=content, filetype="pdf") as doc:
        metadata = doc.metadata or {}
        title = _extract_title(metadata)

    combined_text = "\n\n".join(text_parts).strip()
    asset_metadata = {
        "page_count": len(page_entries),
        "pages": page_entries,
        "document_title": title,
    }
    return ParsedAsset(text=combined_text, title=title, metadata=asset_metadata)
