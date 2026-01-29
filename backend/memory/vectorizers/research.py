"""
Research vectorizer for research findings data.

This module provides the ResearchVectorizer class for converting
research findings into searchable vector embeddings.
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


class ResearchVectorizer:
    """
    Vectorizer for research findings data.

    Extracts and vectorizes research sections like findings,
    insights, data, conclusions, and source information.
    """

    def __init__(self, vector_store: Optional[VectorMemory] = None):
        """
        Initialize research vectorizer.

        Args:
            vector_store: Vector memory store instance
        """
        self.vector_store = vector_store or VectorMemory()
        self.embedding_model = get_embedding_model()
        self.chunker = ContentChunker(chunk_size=400, overlap=50)

        # Section priorities for search ranking
        self.section_priorities = {
            "title": 1.0,
            "summary": 0.9,
            "key_findings": 1.0,
            "insights": 0.9,
            "conclusions": 0.8,
            "recommendations": 0.8,
            "data": 0.7,
            "methodology": 0.6,
            "sources": 0.6,
            "limitations": 0.5,
            "context": 0.6,
            "background": 0.5,
        }

    async def vectorize_research(
        self, workspace_id: str, research: Dict[str, Any]
    ) -> List[str]:
        """
        Vectorize research data and store in vector memory.

        Args:
            workspace_id: Workspace identifier
            research: Research data dictionary

        Returns:
            List of created chunk IDs
        """
        chunk_ids = []

        try:
            # Extract and process each section
            for section_name, section_data in self._extract_sections(research):
                chunks = await self._vectorize_section(
                    workspace_id, section_name, section_data, research.get("id")
                )
                chunk_ids.extend(chunks)

            logger.info(
                f"Vectorized research with {len(chunk_ids)} chunks for workspace {workspace_id}"
            )
            return chunk_ids

        except Exception as e:
            logger.error(f"Error vectorizing research: {e}")
            raise

    def _extract_sections(self, research: Dict[str, Any]) -> List[tuple]:
        """
        Extract searchable sections from research data.

        Args:
            research: Research data dictionary

        Returns:
            List of (section_name, section_data) tuples
        """
        sections = []

        # Core research sections
        core_sections = [
            "title",
            "summary",
            "key_findings",
            "insights",
            "conclusions",
            "recommendations",
            "data",
            "methodology",
            "sources",
            "limitations",
            "context",
            "background",
            "objectives",
            "findings",
            "results",
            "analysis",
        ]

        for section in core_sections:
            if section in research and research[section]:
                sections.append((section, research[section]))

        # Handle nested structures
        if "metadata" in research:
            metadata = research["metadata"]
            for field in ["research_type", "date", "author", "tags"]:
                if field in metadata and metadata[field]:
                    sections.append((f"research_{field}", metadata[field]))

        return sections

    async def _vectorize_section(
        self,
        workspace_id: str,
        section_name: str,
        section_data: Any,
        research_id: Optional[str] = None,
    ) -> List[str]:
        """
        Vectorize a single research section.

        Args:
            workspace_id: Workspace identifier
            section_name: Name of the section
            section_data: Section content data
            research_id: Research record ID

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
                "research_id": research_id,
            }

            # Add section-specific metadata
            if section_name in ["key_findings", "findings", "results"]:
                metadata["content_type"] = "finding"
            elif section_name in ["insights"]:
                metadata["content_type"] = "insight"
            elif section_name in ["conclusions"]:
                metadata["content_type"] = "conclusion"
            elif section_name in ["recommendations"]:
                metadata["content_type"] = "recommendation"
            elif section_name in ["data"]:
                metadata["content_type"] = "data"
            elif section_name in ["sources"]:
                metadata["content_type"] = "source"
            elif section_name in ["methodology"]:
                metadata["content_type"] = "methodology"

            chunk = MemoryChunk(
                workspace_id=workspace_id,
                memory_type=MemoryType.RESEARCH,
                content=chunk_text,
                metadata=metadata,
                reference_id=research_id,
                reference_table="research_findings",
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
                # Handle list of dictionaries (e.g., findings with details)
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

    async def update_research_vectors(
        self, workspace_id: str, research: Dict[str, Any]
    ) -> List[str]:
        """
        Update research vectors (delete old ones and create new ones).

        Args:
            workspace_id: Workspace identifier
            research: Updated research data

        Returns:
            List of new chunk IDs
        """
        research_id = research.get("id")

        # Delete existing research vectors
        if research_id:
            await self.delete_research_vectors(workspace_id, research_id)

        # Create new vectors
        return await self.vectorize_research(workspace_id, research)

    async def delete_research_vectors(self, workspace_id: str, research_id: str) -> int:
        """
        Delete all vectors for a research finding.

        Args:
            workspace_id: Workspace identifier
            research_id: Research record ID

        Returns:
            Number of deleted chunks
        """
        try:
            # Search for research chunks
            chunks = await self.vector_store.search(
                workspace_id=workspace_id,
                query="",
                memory_types=[MemoryType.RESEARCH],
                limit=1000,  # Large limit to get all research chunks
            )

            # Filter chunks by research_id
            research_chunks = [
                chunk for chunk in chunks if chunk.reference_id == research_id
            ]

            # Delete chunks
            deleted_count = 0
            for chunk in research_chunks:
                if chunk.id:
                    await self.vector_store.delete(chunk.id)
                    deleted_count += 1

            logger.info(
                f"Deleted {deleted_count} research vectors for research {research_id}"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting research vectors: {e}")
            return 0

    async def search_research(
        self,
        workspace_id: str,
        query: str,
        section_filter: Optional[List[str]] = None,
        content_type_filter: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[MemoryChunk]:
        """
        Search research vectors with optional filtering.

        Args:
            workspace_id: Workspace identifier
            query: Search query
            section_filter: Optional list of sections to filter by
            content_type_filter: Optional list of content types to filter by
            limit: Maximum number of results

        Returns:
            List of matching memory chunks
        """
        chunks = await self.vector_store.search(
            workspace_id=workspace_id,
            query=query,
            memory_types=[MemoryType.RESEARCH],
            limit=limit * 2,  # Get more for filtering
        )

        # Apply filters
        if section_filter or content_type_filter:
            chunks = [
                chunk
                for chunk in chunks
                if chunk.metadata
                and (
                    (
                        not section_filter
                        or chunk.metadata.get("section") in section_filter
                    )
                    and (
                        not content_type_filter
                        or chunk.metadata.get("content_type") in content_type_filter
                    )
                )
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

    async def search_past_research(
        self, workspace_id: str, query: str, limit: int = 10
    ) -> List[MemoryChunk]:
        """
        Search past research findings.

        Args:
            workspace_id: Workspace identifier
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching research chunks
        """
        return await self.search_research(
            workspace_id=workspace_id, query=query, limit=limit
        )

    async def get_key_findings(
        self, workspace_id: str, research_id: Optional[str] = None, limit: int = 20
    ) -> List[MemoryChunk]:
        """
        Get key findings from research data.

        Args:
            workspace_id: Workspace identifier
            research_id: Optional research ID to filter by
            limit: Maximum number of results

        Returns:
            List of finding chunks
        """
        return await self.search_research(
            workspace_id=workspace_id,
            query="findings results data insights",
            content_type_filter=["finding"],
            limit=limit,
        )

    async def get_insights(
        self, workspace_id: str, research_id: Optional[str] = None, limit: int = 20
    ) -> List[MemoryChunk]:
        """
        Get insights from research data.

        Args:
            workspace_id: Workspace identifier
            research_id: Optional research ID to filter by
            limit: Maximum number of results

        Returns:
            List of insight chunks
        """
        return await self.search_research(
            workspace_id=workspace_id,
            query="insights conclusions analysis",
            content_type_filter=["insight"],
            limit=limit,
        )

    async def get_recommendations(
        self, workspace_id: str, research_id: Optional[str] = None, limit: int = 20
    ) -> List[MemoryChunk]:
        """
        Get recommendations from research data.

        Args:
            workspace_id: Workspace identifier
            research_id: Optional research ID to filter by
            limit: Maximum number of results

        Returns:
            List of recommendation chunks
        """
        return await self.search_research(
            workspace_id=workspace_id,
            query="recommendations suggestions actions",
            content_type_filter=["recommendation"],
            limit=limit,
        )
