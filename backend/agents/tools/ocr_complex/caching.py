"""
FILE-BASED CACHING
Caches processed document results keyed by document hash.
No graceful failures: raises explicit errors or returns misses.
"""

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from .base_processor import BaseProcessor


class DocumentCache(BaseProcessor):
    """Simple file-based cache."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cache_dir = Path(config.get("cache_dir", ".ocr_cache"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

    def _process_document(self, document_path):
        # Not used; cache is utility
        raise NotImplementedError("Use get/set methods")

    def _cache_path(self, doc_hash: str) -> Path:
        return self.cache_dir / f"{doc_hash}.json"

    def get(self, doc_hash: str) -> Optional[Dict[str, Any]]:
        path = self._cache_path(doc_hash)
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def set(self, doc_hash: str, result: Dict[str, Any]) -> None:
        path = self._cache_path(doc_hash)
        with self.lock:
            with path.open("w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
