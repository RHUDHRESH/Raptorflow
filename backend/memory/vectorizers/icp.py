"""
ICP vectorizer for Ideal Customer Profile data.

This module provides the ICPVectorizer class for converting
ICP profile information into searchable vector embeddings.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from chunker import ContentChunker
from embeddings import get_embedding_model
from ..models import MemoryChunk, MemoryType
from vector_store import VectorMemory

logger = logging.getLogger(__name__)


class ICPVectorizer:
    """
    Vectorizer for ICP (Ideal Customer Profile) data.

    Extracts and vectorizes ICP sections like demographics, psychographics,
    behaviors, pain points, and other customer profile information.
    """

    def __init__(self, vector_store: Optional[VectorMemory] = None):
        """
        Initialize ICP vectorizer.

        Args:
            vector_store: Vector memory store instance
        """
        self.vector_store = vector_store or VectorMemory()
        self.embedding_model = get_embedding_model()
        self.chunker = ContentChunker(chunk_size=350, overlap=40)

        # Section priorities for search ranking
        self.section_priorities = {
            "demographics": 0.8,
            "psychographics": 0.9,
            "behaviors": 0.8,
            "pain_points": 1.0,
            "challenges": 0.9,
            "goals": 0.8,
            "motivations": 0.8,
            "buying_process": 0.7,
            "decision_factors": 0.8,
            "objections": 0.7,
            "solutions": 0.6,
            "messaging": 0.7,
            "channels": 0.6,
        }

    async def vectorize_icp(self, workspace_id: str, icp: Dict[str, Any]) -> List[str]:
        """
        Vectorize ICP data and store in vector memory.

        Args:
            workspace_id: Workspace identifier
            icp: ICP data dictionary

        Returns:
            List of created chunk IDs
        """
        chunk_ids = []

        try:
            # Extract and process each section
            for section_name, section_data in self._extract_sections(icp):
                chunks = await self._vectorize_section(
                    workspace_id, section_name, section_data, icp.get("id")
                )
                chunk_ids.extend(chunks)

            logger.info(
                f"Vectorized ICP with {len(chunk_ids)} chunks for workspace {workspace_id}"
            )
            return chunk_ids

        except Exception as e:
            logger.error(f"Error vectorizing ICP: {e}")
            raise

    def _extract_sections(self, icp: Dict[str, Any]) -> List[tuple]:
        """
        Extract searchable sections from ICP data.

        Args:
            icp: ICP data dictionary

        Returns:
            List of (section_name, section_data) tuples
        """
        sections = []

        # Core ICP sections
        core_sections = [
            "demographics",
            "psychographics",
            "behaviors",
            "pain_points",
            "challenges",
            "problems",
            "goals",
            "objectives",
            "motivations",
            "buying_process",
            "decision_factors",
            "objections",
            "solutions",
            "messaging",
            "channels",
            "firmographics",
            "technographics",
            "budget",
        ]

        for section in core_sections:
            if section in icp and icp[section]:
                sections.append((section, icp[section]))

        # Handle nested structures
        if "basic_info" in icp:
            basic_info = icp["basic_info"]
            for field in ["name", "description", "industry", "size"]:
                if field in basic_info and basic_info[field]:
                    sections.append((f"icp_{field}", basic_info[field]))

        # Handle firmographics if present
        if "firmographics" in icp:
            firmographics = icp["firmographics"]
            for field in ["company_size", "industry", "revenue", "location"]:
                if field in firmographics and firmographics[field]:
                    sections.append((f"firmographic_{field}", firmographics[field]))

        return sections

    async def _vectorize_section(
        self,
        workspace_id: str,
        section_name: str,
        section_data: Any,
        icp_id: Optional[str] = None,
    ) -> List[str]:
        """
        Vectorize a single ICP section.

        Args:
            workspace_id: Workspace identifier
            section_name: Name of the section
            section_data: Section content data
            icp_id: ICP record ID

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
                "icp_id": icp_id,
            }

            # Add section-specific metadata
            if section_name in ["pain_points", "challenges", "problems"]:
                metadata["content_type"] = "pain_point"
            elif section_name in ["goals", "objectives", "motivations"]:
                metadata["content_type"] = "goal"
            elif section_name in ["demographics", "firmographics"]:
                metadata["content_type"] = "demographic"
            elif section_name in ["psychographics"]:
                metadata["content_type"] = "psychographic"
            elif section_name in ["behaviors"]:
                metadata["content_type"] = "behavior"
            elif section_name in ["channels"]:
                metadata["content_type"] = "channel"
            elif section_name in ["messaging"]:
                metadata["content_type"] = "messaging"

            chunk = MemoryChunk(
                workspace_id=workspace_id,
                memory_type=MemoryType.ICP,
                content=chunk_text,
                metadata=metadata,
                reference_id=icp_id,
                reference_table="icp_profiles",
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
                # Handle list of dictionaries (e.g., pain points with details)
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

    async def update_icp_vectors(
        self, workspace_id: str, icp: Dict[str, Any]
    ) -> List[str]:
        """
        Update ICP vectors (delete old ones and create new ones).

        Args:
            workspace_id: Workspace identifier
            icp: Updated ICP data

        Returns:
            List of new chunk IDs
        """
        icp_id = icp.get("id")

        # Delete existing ICP vectors
        if icp_id:
            await self.delete_icp_vectors(workspace_id, icp_id)

        # Create new vectors
        return await self.vectorize_icp(workspace_id, icp)

    async def delete_icp_vectors(self, workspace_id: str, icp_id: str) -> int:
        """
        Delete all vectors for an ICP.

        Args:
            workspace_id: Workspace identifier
            icp_id: ICP record ID

        Returns:
            Number of deleted chunks
        """
        try:
            # Search for ICP chunks
            chunks = await self.vector_store.search(
                workspace_id=workspace_id,
                query="",
                memory_types=[MemoryType.ICP],
                limit=1000,  # Large limit to get all ICP chunks
            )

            # Filter chunks by icp_id
            icp_chunks = [chunk for chunk in chunks if chunk.reference_id == icp_id]

            # Delete chunks
            deleted_count = 0
            for chunk in icp_chunks:
                if chunk.id:
                    await self.vector_store.delete(chunk.id)
                    deleted_count += 1

            logger.info(f"Deleted {deleted_count} ICP vectors for ICP {icp_id}")
            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting ICP vectors: {e}")
            return 0

    async def search_icp(
        self,
        workspace_id: str,
        query: str,
        section_filter: Optional[List[str]] = None,
        content_type_filter: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[MemoryChunk]:
        """
        Search ICP vectors with optional filtering.

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
            memory_types=[MemoryType.ICP],
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

    async def get_pain_points(
        self, workspace_id: str, icp_id: Optional[str] = None, limit: int = 20
    ) -> List[MemoryChunk]:
        """
        Get pain points from ICP data.

        Args:
            workspace_id: Workspace identifier
            icp_id: Optional ICP ID to filter by
            limit: Maximum number of results

        Returns:
            List of pain point chunks
        """
        return await self.search_icp(
            workspace_id=workspace_id,
            query="pain challenges problems issues",
            content_type_filter=["pain_point"],
            limit=limit,
        )

    async def get_goals(
        self, workspace_id: str, icp_id: Optional[str] = None, limit: int = 20
    ) -> List[MemoryChunk]:
        """
        Get goals from ICP data.

        Args:
            workspace_id: Workspace identifier
            icp_id: Optional ICP ID to filter by
            limit: Maximum number of results

        Returns:
            List of goal chunks
        """
        return await self.search_icp(
            workspace_id=workspace_id,
            query="goals objectives motivations",
            content_type_filter=["goal"],
            limit=limit,
        )
