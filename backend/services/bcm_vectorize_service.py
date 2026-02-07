"""
BCM Vectorization Service

Takes a BCM/businesscontext manifest JSON and stores it into vector memory
so agents can use semantic search to retrieve relevant context.
"""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from memory.models import MemoryType
from memory.vector_store import VectorMemory

logger = logging.getLogger(__name__)


class BCMVectorizeService:
    def __init__(self, vector_memory: Optional[VectorMemory] = None):
        self.vector_memory = vector_memory or VectorMemory()

    async def vectorize_manifest(
        self,
        workspace_id: str,
        manifest: Dict[str, Any],
        version: Optional[str] = None,
        source: str = "bcm_manifest",
    ) -> Dict[str, Any]:
        """
        Vectorize BCM manifest sections and optionally the full manifest.

        Returns summary stats and list of stored section keys.
        """
        if not manifest or not isinstance(manifest, dict):
            return {"success": False, "error": "Invalid manifest"}

        stored_sections: List[str] = []

        # Determine numeric version for section upserts
        numeric_version = self._to_numeric_version(
            version
            or manifest.get("version")
            or manifest.get("version_string")
            or manifest.get("version_major")
        )

        # Vectorize top-level sections (skip obvious metadata keys)
        for section_name, section_data in self._iter_sections(manifest):
            content = self._section_to_text(section_name, section_data)
            if not content:
                continue

            try:
                await self.vector_memory.upsert_section(
                    workspace_id=workspace_id,
                    section=section_name,
                    content=content,
                    version=numeric_version,
                    metadata={
                        "source": source,
                        "section": section_name,
                        "content_hash": self._hash_content(content),
                    },
                )
                stored_sections.append(section_name)
            except Exception as e:
                logger.warning(
                    "BCM vectorization failed for section %s: %s",
                    section_name,
                    e,
                )

        # Optionally store full manifest as a single BCM memory chunk
        try:
            full_text = self._manifest_to_text(manifest)
            if full_text:
                await self.vector_memory.store(
                    workspace_id=workspace_id,
                    memory_type=MemoryType.BCM,
                    content=full_text,
                    metadata={
                        "source": source,
                        "section": "__full__",
                        "version": str(version or ""),
                    },
                )
        except Exception as e:
            logger.warning("BCM full-manifest vectorization failed: %s", e)

        return {
            "success": True,
            "sections_vectorized": len(stored_sections),
            "sections": stored_sections,
            "version": numeric_version,
        }

    def _iter_sections(self, manifest: Dict[str, Any]) -> List[Tuple[str, Any]]:
        skip_keys = {
            "checksum",
            "generated_at",
            "workspace_id",
            "user_id",
            "links",
            "raw_step_ids",
            "completion_percentage",
            "version",
            "version_major",
            "version_minor",
            "version_patch",
            "version_string",
        }
        sections = []
        for key, value in manifest.items():
            if key in skip_keys:
                continue
            sections.append((key, value))
        return sections

    def _section_to_text(self, section_name: str, section_data: Any) -> str:
        if section_data is None:
            return ""
        if isinstance(section_data, str):
            return section_data.strip()
        try:
            # Compact, deterministic JSON for embedding stability
            section_json = json.dumps(
                section_data, sort_keys=True, separators=(",", ":")
            )
            return f"{section_name}: {section_json}"
        except Exception:
            return f"{section_name}: {str(section_data)}"

    def _manifest_to_text(self, manifest: Dict[str, Any]) -> str:
        try:
            return json.dumps(manifest, sort_keys=True, separators=(",", ":"))
        except Exception:
            return str(manifest)

    def _hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _to_numeric_version(self, version: Any) -> int:
        """
        Convert version info into an integer for section versioning.
        Accepts int, float, or semver string.
        """
        if isinstance(version, int):
            return version
        if isinstance(version, float):
            return int(version)
        if isinstance(version, str):
            parts = version.split(".")
            if len(parts) >= 3 and all(p.isdigit() for p in parts[:3]):
                major, minor, patch = (int(parts[0]), int(parts[1]), int(parts[2]))
                return major * 1_000_000 + minor * 1_000 + patch
            if version.isdigit():
                return int(version)
        # Fallback to hash-based int
        return int(hashlib.md5(str(version).encode("utf-8")).hexdigest()[:6], 16)
