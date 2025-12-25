from typing import Dict, Optional
from urllib.parse import urlparse

from backend.core.parsers.docx import parse_docx
from backend.core.parsers.pdf import parse_pdf
from backend.core.parsers.pptx import parse_pptx
from backend.core.parsers.types import ParsedAsset

ASSET_SUFFIXES = {
    ".pdf": "pdf",
    ".pptx": "pptx",
    ".ppt": "pptx",
    ".docx": "docx",
    ".doc": "docx",
}

ASSET_CONTENT_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
    "application/vnd.ms-powerpoint": "pptx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/msword": "docx",
}

PARSERS = {
    "pdf": parse_pdf,
    "pptx": parse_pptx,
    "docx": parse_docx,
}


def detect_asset_type(url: str, content_type: Optional[str] = None) -> Optional[str]:
    parsed = urlparse(url)
    path = parsed.path.lower()
    for suffix, asset_type in ASSET_SUFFIXES.items():
        if path.endswith(suffix):
            return asset_type

    if content_type:
        normalized = content_type.split(";")[0].strip().lower()
        return ASSET_CONTENT_TYPES.get(normalized)

    return None


def parse_asset(asset_type: str, content: bytes) -> ParsedAsset:
    parser = PARSERS.get(asset_type)
    if not parser:
        raise ValueError(f"Unsupported asset type: {asset_type}")
    return parser(content)
