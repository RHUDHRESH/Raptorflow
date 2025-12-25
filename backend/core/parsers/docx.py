import io
from typing import Dict, List

from docx import Document

from backend.core.parsers.types import ParsedAsset


def parse_docx(content: bytes) -> ParsedAsset:
    document = Document(io.BytesIO(content))
    section_entries: List[Dict[str, Any]] = []
    text_parts: List[str] = []
    section_index = 0

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue

        style_name = paragraph.style.name if paragraph.style else ""
        is_heading = style_name.lower().startswith("heading")
        if is_heading:
            section_index += 1
            section_entries.append(
                {
                    "page_number": section_index,
                    "title": text,
                    "style": style_name,
                }
            )
            text_parts.append(f"[Section {section_index}]\n{text}")
        else:
            text_parts.append(text)

    combined_text = "\n\n".join(text_parts).strip()
    asset_metadata = {
        "page_count": max(section_index, 1) if text_parts else 0,
        "pages": section_entries,
    }
    title = section_entries[0]["title"] if section_entries else ""
    return ParsedAsset(text=combined_text, title=title, metadata=asset_metadata)
