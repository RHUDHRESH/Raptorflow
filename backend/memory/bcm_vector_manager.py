"""
BCM Vector Manager

Handles vector operations specific to Business Context Manifest (BCM) system:
- Dirty section detection and re-embedding
- Snippet bundle generation
- Embedding caching
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from memory.vector_store import VectorMemory
from services.upstash_client import get_upstash_client


class BCMVectorManager:
    def __init__(self, vector_memory: VectorMemory):
        self.vector_memory = vector_memory
        self.upstash = get_upstash_client()

    async def get_dirty_sections(
        self,
        workspace_id: str,
        current_manifest: Dict[str, Any],
        previous_manifest: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Identify sections of BCM that have changed and need re-embedding

        Args:
            workspace_id: Workspace UUID
            current_manifest: Latest BCM manifest
            previous_manifest: Previous version for comparison (optional)

        Returns:
            List of section keys that need updating
        """
        dirty_sections = []

        if not previous_manifest:
            # First version - all sections are "dirty"
            return list(current_manifest.keys())

        # Compare sections for changes
        for section in current_manifest:
            current_hash = self._hash_section(current_manifest[section])
            previous_hash = self._hash_section(previous_manifest.get(section, {}))

            if current_hash != previous_hash:
                dirty_sections.append(section)

        return dirty_sections

    async def generate_snippet_bundle(
        self,
        workspace_id: str,
        intent: str,
        sections: List[str],
        ttl: int = 21600,  # 6 hours
    ) -> Dict[str, Any]:
        """
        Generate and cache a snippet bundle for a specific intent

        Args:
            workspace_id: Workspace UUID
            intent: Intent/key for the bundle
            sections: List of section keys to include
            ttl: Cache TTL in seconds

        Returns:
            Dictionary of snippet embeddings
        """
        # Check cache first
        cache_key = f"bundle:w:{workspace_id}:i:{intent}"
        cached = await self.upstash.get(cache_key)
        if cached:
            return cached

        # Get embeddings for each section
        bundle = {}
        for section in sections:
            # Get text content from vector store
            content = await self.vector_memory.get_section_content(
                workspace_id, section
            )
            if not content:
                continue

            # Get or create embedding
            embedding = await self._get_or_create_embedding(
                workspace_id, section, content
            )
            bundle[section] = {
                "text": content,
                "embedding": embedding,
                "updated_at": datetime.utcnow().isoformat(),
            }

        # Cache bundle
        await self.upstash.set(cache_key, bundle, ttl)

        return bundle

    async def _get_or_create_embedding(
        self, workspace_id: str, section: str, content: str
    ) -> List[float]:
        """
        Get cached embedding or create new one

        Args:
            workspace_id: Workspace UUID
            section: Section identifier
            content: Text content to embed

        Returns:
            Embedding vector
        """
        # Check cache
        cache_key = f"embed:w:{workspace_id}:s:{section}"
        cached = await self.upstash.get(cache_key)
        if cached:
            return cached

        # Create new embedding
        embedding = await self.vector_memory.embed_text(content)

        # Cache with 24h TTL
        await self.upstash.set(cache_key, embedding, 86400)

        return embedding

    def _hash_section(self, section_data: Any) -> str:
        """Generate hash of section content for change detection"""
        if not section_data:
            return ""

        if isinstance(section_data, (str, int, float, bool)):
            return str(section_data)

        return hashlib.sha256(
            json.dumps(section_data, sort_keys=True).encode()
        ).hexdigest()
