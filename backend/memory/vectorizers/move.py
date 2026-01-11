"""
Move vectorizer for strategic move data.

This module provides the MoveVectorizer class for converting
strategic move information into searchable vector embeddings.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..chunker import ContentChunker
from ..embeddings import get_embedding_model
from ..models import MemoryChunk, MemoryType
from ..vector_store import VectorMemory

logger = logging.getLogger(__name__)


class MoveVectorizer:
    """
    Vectorizer for strategic move data.

    Extracts and vectorizes move sections like goals, strategy,
    execution plan, results, and other strategic move information.
    """

    def __init__(self, vector_store: Optional[VectorMemory] = None):
        """
        Initialize move vectorizer.

        Args:
            vector_store: Vector memory store instance
        """
        self.vector_store = vector_store or VectorMemory()
        self.embedding_model = get_embedding_model()
        self.chunker = ContentChunker(chunk_size=450, overlap=50)

        # Section priorities for search ranking
        self.section_priorities = {
            "title": 1.0,
            "description": 0.9,
            "goals": 1.0,
            "objectives": 0.9,
            "strategy": 0.9,
            "execution_plan": 0.8,
            "tactics": 0.7,
            "resources": 0.6,
            "timeline": 0.6,
            "success_metrics": 0.8,
            "risks": 0.7,
            "dependencies": 0.6,
            "status": 0.5,
            "results": 0.8,
            "outcomes": 0.8,
            "learnings": 0.7,
        }

    async def vectorize_move(
        self, workspace_id: str, move: Dict[str, Any]
    ) -> List[str]:
        """
        Vectorize move data and store in vector memory.

        Args:
            workspace_id: Workspace identifier
            move: Move data dictionary

        Returns:
            List of created chunk IDs
        """
        chunk_ids = []

        try:
            # Extract and process each section
            for section_name, section_data in self._extract_sections(move):
                chunks = await self._vectorize_section(
                    workspace_id, section_name, section_data, move.get("id")
                )
                chunk_ids.extend(chunks)

            logger.info(
                f"Vectorized move with {len(chunk_ids)} chunks for workspace {workspace_id}"
            )
            return chunk_ids

        except Exception as e:
            logger.error(f"Error vectorizing move: {e}")
            raise

    def _extract_sections(self, move: Dict[str, Any]) -> List[tuple]:
        """
        Extract searchable sections from move data.

        Args:
            move: Move data dictionary

        Returns:
            List of (section_name, section_data) tuples
        """
        sections = []

        # Core move sections
        core_sections = [
            "title",
            "description",
            "goals",
            "objectives",
            "strategy",
            "execution_plan",
            "tactics",
            "resources",
            "timeline",
            "success_metrics",
            "risks",
            "dependencies",
            "status",
            "results",
            "outcomes",
            "learnings",
            "context",
            "background",
            "rationale",
        ]

        for section in core_sections:
            if section in move and move[section]:
                sections.append((section, move[section]))

        # Handle nested structures
        if "metadata" in move:
            metadata = move["metadata"]
            for field in ["priority", "category", "tags"]:
                if field in metadata and metadata[field]:
                    sections.append((f"move_{field}", metadata[field]))

        return sections

    async def _vectorize_section(
        self,
        workspace_id: str,
        section_name: str,
        section_data: Any,
        move_id: Optional[str] = None,
    ) -> List[str]:
        """
        Vectorize a single move section.

        Args:
            workspace_id: Workspace identifier
            section_name: Name of the section
            section_data: Section content data
            move_id: Move record ID

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
                "move_id": move_id,
            }

            # Add section-specific metadata
            if section_name in ["goals", "objectives"]:
                metadata["content_type"] = "goal"
            elif section_name in ["strategy"]:
                metadata["content_type"] = "strategy"
            elif section_name in ["execution_plan", "tactics"]:
                metadata["content_type"] = "execution"
            elif section_name in ["risks"]:
                metadata["content_type"] = "risk"
            elif section_name in ["results", "outcomes"]:
                metadata["content_type"] = "result"
            elif section_name in ["learnings"]:
                metadata["content_type"] = "learning"
            elif section_name in ["success_metrics"]:
                metadata["content_type"] = "metric"

            chunk = MemoryChunk(
                workspace_id=workspace_id,
                memory_type=MemoryType.MOVE,
                content=chunk_text,
                metadata=metadata,
                reference_id=move_id,
                reference_table="moves",
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
                # Handle list of dictionaries (e.g., goals with details)
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

    async def update_move_vectors(
        self, workspace_id: str, move: Dict[str, Any]
    ) -> List[str]:
        """
        Update move vectors (delete old ones and create new ones).

        Args:
            workspace_id: Workspace identifier
            move: Updated move data

        Returns:
            List of new chunk IDs
        """
        move_id = move.get("id")

        # Delete existing move vectors
        if move_id:
            await self.delete_move_vectors(workspace_id, move_id)

        # Create new vectors
        return await self.vectorize_move(workspace_id, move)

    async def delete_move_vectors(self, workspace_id: str, move_id: str) -> int:
        """
        Delete all vectors for a move.

        Args:
            workspace_id: Workspace identifier
            move_id: Move record ID

        Returns:
            Number of deleted chunks
        """
        try:
            # Search for move chunks
            chunks = await self.vector_store.search(
                workspace_id=workspace_id,
                query="",
                memory_types=[MemoryType.MOVE],
                limit=1000,  # Large limit to get all move chunks
            )

            # Filter chunks by move_id
            move_chunks = [chunk for chunk in chunks if chunk.reference_id == move_id]

            # Delete chunks
            deleted_count = 0
            for chunk in move_chunks:
                if chunk.id:
                    await self.vector_store.delete(chunk.id)
                    deleted_count += 1

            logger.info(f"Deleted {deleted_count} move vectors for move {move_id}")
            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting move vectors: {e}")
            return 0

    async def vectorize_move_output(
        self, workspace_id: str, move_id: str, output: Dict[str, Any]
    ) -> List[str]:
        """
        Vectorize move output/results and link to the move.

        Args:
            workspace_id: Workspace identifier
            move_id: Move record ID
            output: Move output data

        Returns:
            List of created chunk IDs
        """
        chunk_ids = []

        try:
            # Extract output sections
            output_sections = [
                ("results", output.get("results", "")),
                ("outcomes", output.get("outcomes", "")),
                ("learnings", output.get("learnings", "")),
                ("metrics", output.get("metrics", "")),
                ("summary", output.get("summary", "")),
            ]

            for section_name, section_data in output_sections:
                if section_data:
                    chunks = await self._vectorize_section(
                        workspace_id, section_name, section_data, move_id
                    )
                    chunk_ids.extend(chunks)

            logger.info(
                f"Vectorized move output with {len(chunk_ids)} chunks for move {move_id}"
            )
            return chunk_ids

        except Exception as e:
            logger.error(f"Error vectorizing move output: {e}")
            raise

    async def search_move(
        self,
        workspace_id: str,
        query: str,
        section_filter: Optional[List[str]] = None,
        content_type_filter: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[MemoryChunk]:
        """
        Search move vectors with optional filtering.

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
            memory_types=[MemoryType.MOVE],
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

    async def get_move_context(
        self, workspace_id: str, move_id: str
    ) -> List[MemoryChunk]:
        """
        Get all context for a specific move.

        Args:
            workspace_id: Workspace identifier
            move_id: Move record ID

        Returns:
            List of all move chunks
        """
        return await self.search_move(
            workspace_id=workspace_id,
            query="",
            limit=1000,  # Get all chunks for this move
        )

    async def get_move_goals(
        self, workspace_id: str, move_id: Optional[str] = None, limit: int = 20
    ) -> List[MemoryChunk]:
        """
        Get goals from move data.

        Args:
            workspace_id: Workspace identifier
            move_id: Optional move ID to filter by
            limit: Maximum number of results

        Returns:
            List of goal chunks
        """
        return await self.search_move(
            workspace_id=workspace_id,
            query="goals objectives targets",
            content_type_filter=["goal"],
            limit=limit,
        )

    async def get_move_strategies(
        self, workspace_id: str, move_id: Optional[str] = None, limit: int = 20
    ) -> List[MemoryChunk]:
        """
        Get strategies from move data.

        Args:
            workspace_id: Workspace identifier
            move_id: Optional move ID to filter by
            limit: Maximum number of results

        Returns:
            List of strategy chunks
        """
        return await self.search_move(
            workspace_id=workspace_id,
            query="strategy approach plan",
            content_type_filter=["strategy"],
            limit=limit,
        )
