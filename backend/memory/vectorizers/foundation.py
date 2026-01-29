"""
Foundation vectorizer for company foundation data.

This module provides the FoundationVectorizer class for converting
company foundation information into searchable vector embeddings.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from chunker import ContentChunker
from embeddings import get_embedding_model
from vector_store import VectorMemory

from ..models import MemoryChunk, MemoryType

logger = logging.getLogger(__name__)


class FoundationVectorizer:
    """
    Vectorizer for company foundation data.

    Extracts and vectorizes foundation sections like mission, vision,
    USPs, features, and other company information for semantic search.
    """

    def __init__(self, vector_store: Optional[VectorMemory] = None):
        """
        Initialize foundation vectorizer.

        Args:
            vector_store: Vector memory store instance
        """
        self.vector_store = vector_store or VectorMemory()
        self.embedding_model = get_embedding_model()
        self.chunker = ContentChunker(chunk_size=400, overlap=50)

        # Section priorities for search ranking
        self.section_priorities = {
            "mission": 1.0,
            "vision": 1.0,
            "usps": 0.9,
            "features": 0.8,
            "values": 0.7,
            "target_market": 0.8,
            "competitive_advantage": 0.9,
            "business_model": 0.7,
            "revenue_streams": 0.6,
            "key_partnerships": 0.6,
            "cost_structure": 0.5,
        }

    async def vectorize_foundation(
        self, workspace_id: str, foundation: Dict[str, Any]
    ) -> List[str]:
        """
        Vectorize foundation data and store in vector memory.

        Args:
            workspace_id: Workspace identifier
            foundation: Foundation data dictionary

        Returns:
            List of created chunk IDs
        """
        chunk_ids = []

        try:
            # Extract and process each section
            for section_name, section_data in self._extract_sections(foundation):
                chunks = await self._vectorize_section(
                    workspace_id, section_name, section_data, foundation.get("id")
                )
                chunk_ids.extend(chunks)

            logger.info(
                f"Vectorized foundation with {len(chunk_ids)} chunks for workspace {workspace_id}"
            )
            return chunk_ids

        except Exception as e:
            logger.error(f"Error vectorizing foundation: {e}")
            raise

    def _extract_sections(self, foundation: Dict[str, Any]) -> List[tuple]:
        """
        Extract searchable sections from foundation data.

        Args:
            foundation: Foundation data dictionary

        Returns:
            List of (section_name, section_data) tuples
        """
        sections = []

        # Core foundation sections
        core_sections = [
            "mission",
            "vision",
            "values",
            "purpose",
            "usps",
            "unique_selling_propositions",
            "features",
            "product_features",
            "target_market",
            "ideal_customer",
            "competitive_advantage",
            "competitive_landscape",
            "business_model",
            "revenue_model",
            "revenue_streams",
            "pricing_strategy",
            "key_partnerships",
            "strategic_partnerships",
            "cost_structure",
            "operational_costs",
        ]

        for section in core_sections:
            if section in foundation and foundation[section]:
                sections.append((section, foundation[section]))

        # Handle nested structures
        if "company_info" in foundation:
            company_info = foundation["company_info"]
            for field in ["name", "description", "industry", "size"]:
                if field in company_info and company_info[field]:
                    sections.append((f"company_{field}", company_info[field]))

        return sections

    async def _vectorize_section(
        self,
        workspace_id: str,
        section_name: str,
        section_data: Any,
        foundation_id: Optional[str] = None,
    ) -> List[str]:
        """
        Vectorize a single foundation section.

        Args:
            workspace_id: Workspace identifier
            section_name: Name of the section
            section_data: Section content data
            foundation_id: Foundation record ID

        Returns:
            List of created chunk IDs
        """
        chunk_ids = []

        # Convert section data to text
        content = self._convert_to_text(section_data)
        if not content or len(content.strip()) < 10:
            return chunk_ids

        # Split into chunks
        chunks = self.chunker.chunk(content)

        # Create memory chunks
        for i, chunk_text in enumerate(chunks):
            metadata = {
                "section": section_name,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "priority": self.section_priorities.get(section_name, 0.5),
                "foundation_id": foundation_id,
            }

            # Add section-specific metadata
            if section_name in ["usps", "unique_selling_propositions"]:
                metadata["content_type"] = "usp"
            elif section_name in ["features", "product_features"]:
                metadata["content_type"] = "feature"
            elif section_name in ["mission", "vision", "values"]:
                metadata["content_type"] = "core_value"
            elif section_name in ["target_market", "ideal_customer"]:
                metadata["content_type"] = "market_info"

            chunk = MemoryChunk(
                workspace_id=workspace_id,
                memory_type=MemoryType.FOUNDATION,
                content=chunk_text,
                metadata=metadata,
                reference_id=foundation_id,
                reference_table="foundations",
            )

            chunk_id = await self.vector_store.store(chunk)
            chunk_ids.append(chunk_id)

        return chunk_ids

    def _convert_to_text(self, data: Any) -> str:
        """
        Convert various data types to searchable text.

        Args:
            data: Data to convert

        Returns:
            Text representation
        """
        if isinstance(data, str):
            return data
        elif isinstance(data, list):
            if all(isinstance(item, str) for item in data):
                return " ".join(data)
            elif all(isinstance(item, dict) for item in data):
                # Handle list of dictionaries (e.g., USPs with details)
                texts = []
                for item in data:
                    if isinstance(item, dict):
                        # Extract all string values
                        values = [str(v) for v in item.values() if isinstance(v, str)]
                        texts.append(" ".join(values))
                    else:
                        texts.append(str(item))
                return " ".join(texts)
            else:
                return " ".join(str(item) for item in data)
        elif isinstance(data, dict):
            # Convert dictionary to structured text
            texts = []
            for key, value in data.items():
                if isinstance(value, str):
                    texts.append(f"{key}: {value}")
                elif isinstance(value, (list, dict)):
                    texts.append(f"{key}: {self._convert_to_text(value)}")
                else:
                    texts.append(f"{key}: {value}")
            return " ".join(texts)
        else:
            return str(data)

    async def update_foundation_vectors(
        self, workspace_id: str, foundation: Dict[str, Any]
    ) -> List[str]:
        """
        Update foundation vectors (delete old ones and create new ones).

        Args:
            workspace_id: Workspace identifier
            foundation: Updated foundation data

        Returns:
            List of new chunk IDs
        """
        foundation_id = foundation.get("id")

        # Delete existing foundation vectors
        if foundation_id:
            await self.delete_foundation_vectors(workspace_id, foundation_id)

        # Create new vectors
        return await self.vectorize_foundation(workspace_id, foundation)

    async def delete_foundation_vectors(
        self, workspace_id: str, foundation_id: str
    ) -> int:
        """
        Delete all vectors for a foundation.

        Args:
            workspace_id: Workspace identifier
            foundation_id: Foundation record ID

        Returns:
            Number of deleted chunks
        """
        try:
            # Search for foundation chunks
            chunks = await self.vector_store.search(
                workspace_id=workspace_id,
                query="",
                memory_types=[MemoryType.FOUNDATION],
                limit=1000,  # Large limit to get all foundation chunks
            )

            # Filter chunks by foundation_id
            foundation_chunks = [
                chunk for chunk in chunks if chunk.reference_id == foundation_id
            ]

            # Delete chunks
            deleted_count = 0
            for chunk in foundation_chunks:
                if chunk.id:
                    await self.vector_store.delete(chunk.id)
                    deleted_count += 1

            logger.info(
                f"Deleted {deleted_count} foundation vectors for foundation {foundation_id}"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting foundation vectors: {e}")
            return 0

    async def search_foundation(
        self,
        workspace_id: str,
        query: str,
        section_filter: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[MemoryChunk]:
        """
        Search foundation vectors with optional section filtering.

        Args:
            workspace_id: Workspace identifier
            query: Search query
            section_filter: Optional list of sections to filter by
            limit: Maximum number of results

        Returns:
            List of matching memory chunks
        """
        chunks = await self.vector_store.search(
            workspace_id=workspace_id,
            query=query,
            memory_types=[MemoryType.FOUNDATION],
            limit=limit * 2,  # Get more for filtering
        )

        # Apply section filter if provided
        if section_filter:
            chunks = [
                chunk
                for chunk in chunks
                if chunk.metadata and chunk.metadata.get("section") in section_filter
            ]

        # Sort by priority and relevance
        chunks.sort(
            key=lambda x: (
                x.metadata.get("priority", 0.5) if x.metadata else 0.5,
                x.score or 0.0,
            ),
            reverse=True,
        )

        return chunks[:limit]
