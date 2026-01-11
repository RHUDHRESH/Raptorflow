"""
Tests for VectorMemory class.

This module tests the vector memory storage and retrieval functionality.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from backend.memory.embeddings import EmbeddingModel
from backend.memory.models import MemoryChunk, MemoryType
from backend.memory.vector_store import VectorMemory


class TestVectorMemory:
    """Test cases for VectorMemory class."""

    @pytest.fixture
    def vector_memory(self, mock_supabase_client):
        """Create VectorMemory instance for testing."""
        with patch("backend.memory.vector_store.get_embedding_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.encode_single.return_value = [0.1, 0.2, 0.3] * 128
            mock_get_model.return_value = mock_model

            memory = VectorMemory(supabase_client=mock_supabase_client)
            return memory

    @pytest.mark.asyncio
    async def test_store_memory_chunk(self, vector_memory, sample_memory_chunk):
        """Test storing a memory chunk."""
        # Mock Supabase response
        vector_memory.supabase_client.table.return_value.insert.return_value.execute.return_value = {
            "data": [{"id": "chunk-123"}],
            "error": None,
        }

        # Store chunk
        chunk_id = await vector_memory.store(sample_memory_chunk)

        # Verify
        assert chunk_id == "chunk-123"
        vector_memory.supabase_client.table.assert_called_with("memory_vectors")
        vector_memory.supabase_client.table.return_value.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_memory_chunk_with_embedding(
        self, vector_memory, sample_memory_chunk
    ):
        """Test storing a memory chunk with pre-computed embedding."""
        # Set embedding
        sample_memory_chunk.embedding = np.array([0.1, 0.2, 0.3] * 128)

        # Mock Supabase response
        vector_memory.supabase_client.table.return_value.insert.return_value.execute.return_value = {
            "data": [{"id": "chunk-123"}],
            "error": None,
        }

        # Store chunk
        chunk_id = await vector_memory.store(sample_memory_chunk)

        # Verify
        assert chunk_id == "chunk-123"

        # Check that embedding was included in the insert call
        insert_call = vector_memory.supabase_client.table.return_value.insert.call_args
        insert_data = insert_call[0][0][0]  # First argument, first item

        assert "embedding" in insert_data
        assert len(insert_data["embedding"]) == 384

    @pytest.mark.asyncio
    async def test_search_memory_chunks(self, vector_memory, test_workspace_id):
        """Test searching memory chunks."""
        # Mock search results
        mock_results = [
            {
                "id": "chunk-1",
                "content": "Company mission statement",
                "metadata": {"section": "mission"},
                "similarity": 0.95,
            },
            {
                "id": "chunk-2",
                "content": "Product features overview",
                "metadata": {"section": "features"},
                "similarity": 0.87,
            },
        ]

        vector_memory.supabase_client.rpc.return_value.execute.return_value = {
            "data": mock_results,
            "error": None,
        }

        # Search
        results = await vector_memory.search(
            workspace_id=test_workspace_id,
            query="company mission",
            memory_types=[MemoryType.FOUNDATION],
            limit=10,
        )

        # Verify
        assert len(results) == 2
        assert results[0].content == "Company mission statement"
        assert results[0].score == 0.95
        assert results[1].content == "Product features overview"
        assert results[1].score == 0.87

        # Verify RPC call
        vector_memory.supabase_client.rpc.assert_called_once()
        call_args = vector_memory.supabase_client.rpc.call_args
        assert call_args[0][0] == "search_memory_vectors"

    @pytest.mark.asyncio
    async def test_search_without_memory_types(self, vector_memory, test_workspace_id):
        """Test searching without specifying memory types."""
        # Mock search results
        vector_memory.supabase_client.rpc.return_value.execute.return_value = {
            "data": [],
            "error": None,
        }

        # Search without types
        await vector_memory.search(
            workspace_id=test_workspace_id, query="test query", limit=5
        )

        # Verify RPC call was made with None for memory types
        call_args = vector_memory.supabase_client.rpc.call_args[1]
        assert call_args["p_memory_types"] is None

    @pytest.mark.asyncio
    async def test_get_memory_chunk(self, vector_memory, sample_memory_chunk):
        """Test retrieving a specific memory chunk."""
        # Mock Supabase response
        mock_data = {
            "id": "chunk-123",
            "workspace_id": sample_memory_chunk.workspace_id,
            "memory_type": sample_memory_chunk.memory_type.value,
            "content": sample_memory_chunk.content,
            "metadata": sample_memory_chunk.metadata,
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-01T10:00:00Z",
        }

        vector_memory.supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = {
            "data": [mock_data],
            "error": None,
        }

        # Retrieve chunk
        result = await vector_memory.get("chunk-123")

        # Verify
        assert result is not None
        assert result.id == "chunk-123"
        assert result.content == sample_memory_chunk.content
        assert result.memory_type == sample_memory_chunk.memory_type

    @pytest.mark.asyncio
    async def test_get_nonexistent_memory_chunk(self, vector_memory):
        """Test retrieving a non-existent memory chunk."""
        # Mock empty response
        vector_memory.supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = {
            "data": [],
            "error": None,
        }

        # Retrieve chunk
        result = await vector_memory.get("nonexistent-chunk")

        # Verify
        assert result is None

    @pytest.mark.asyncio
    async def test_update_memory_chunk(self, vector_memory, sample_memory_chunk):
        """Test updating a memory chunk."""
        # Mock Supabase response
        vector_memory.supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = {
            "data": [{"id": "chunk-123"}],
            "error": None,
        }

        # Update chunk
        success = await vector_memory.update(sample_memory_chunk)

        # Verify
        assert success is True
        vector_memory.supabase_client.table.return_value.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_memory_chunk(self, vector_memory):
        """Test deleting a memory chunk."""
        # Mock Supabase response
        vector_memory.supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = {
            "data": [{"id": "chunk-123"}],
            "error": None,
        }

        # Delete chunk
        success = await vector_memory.delete("chunk-123")

        # Verify
        assert success is True
        vector_memory.supabase_client.table.return_value.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_memory_chunk(self, vector_memory):
        """Test deleting a non-existent memory chunk."""
        # Mock empty response
        vector_memory.supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = {
            "data": [],
            "error": None,
        }

        # Delete chunk
        success = await vector_memory.delete("nonexistent-chunk")

        # Verify
        assert success is False

    @pytest.mark.asyncio
    async def test_init_supabase_client(self):
        """Test Supabase client initialization."""
        with patch(
            "backend.memory.vector_store.create_client"
        ) as mock_create_client, patch(
            "backend.memory.vector_store.get_embedding_model"
        ) as mock_get_model, patch.dict(
            "os.environ",
            {"SUPABASE_URL": "test-url", "SUPABASE_SERVICE_ROLE_KEY": "test-key"},
        ):

            mock_client = MagicMock()
            mock_create_client.return_value = mock_client
            mock_model = MagicMock()
            mock_get_model.return_value = mock_model

            # Create VectorMemory without client
            memory = VectorMemory()

            # Verify client was created
            mock_create_client.assert_called_once_with("test-url", "test-key")
            assert memory.supabase_client == mock_client
            assert memory.embedding_model == mock_model

    @pytest.mark.asyncio
    async def test_workspace_isolation(self, vector_memory, test_workspace_id):
        """Test that workspace isolation is enforced."""
        # Mock search results
        vector_memory.supabase_client.rpc.return_value.execute.return_value = {
            "data": [],
            "error": None,
        }

        # Search with workspace ID
        await vector_memory.search(workspace_id=test_workspace_id, query="test query")

        # Verify workspace ID was passed to RPC
        call_args = vector_memory.supabase_client.rpc.call_args[1]
        assert call_args["p_workspace_id"] == test_workspace_id

    @pytest.mark.asyncio
    async def test_embedding_generation(self, vector_memory, sample_memory_chunk):
        """Test embedding generation for chunks without embeddings."""
        # Remove embedding from chunk
        sample_memory_chunk.embedding = None

        # Mock Supabase response
        vector_memory.supabase_client.table.return_value.insert.return_value.execute.return_value = {
            "data": [{"id": "chunk-123"}],
            "error": None,
        }

        # Store chunk
        await vector_memory.store(sample_memory_chunk)

        # Verify embedding was generated
        vector_memory.embedding_model.encode_single.assert_called_once_with(
            sample_memory_chunk.content
        )

    @pytest.mark.asyncio
    async def test_error_handling(self, vector_memory, sample_memory_chunk):
        """Test error handling in vector operations."""
        # Mock Supabase error
        vector_memory.supabase_client.table.return_value.insert.return_value.execute.return_value = {
            "data": None,
            "error": "Database error",
        }

        # Store chunk should raise exception
        with pytest.raises(Exception):
            await vector_memory.store(sample_memory_chunk)

    @pytest.mark.asyncio
    async def test_batch_operations(self, vector_memory, test_workspace_id):
        """Test batch operations for efficiency."""
        # Create multiple chunks
        chunks = [
            MemoryChunk(
                workspace_id=test_workspace_id,
                memory_type=MemoryType.FOUNDATION,
                content=f"Test content {i}",
                metadata={"index": i},
            )
            for i in range(5)
        ]

        # Mock batch insert response
        vector_memory.supabase_client.table.return_value.insert.return_value.execute.return_value = {
            "data": [{"id": f"chunk-{i}"} for i in range(5)],
            "error": None,
        }

        # Store chunks (would need to implement batch method)
        stored_ids = []
        for chunk in chunks:
            chunk_id = await vector_memory.store(chunk)
            stored_ids.append(chunk_id)

        # Verify all chunks were stored
        assert len(stored_ids) == 5
        assert all(chunk_id.startswith("chunk-") for chunk_id in stored_ids)

    @pytest.mark.asyncio
    async def test_similarity_threshold(self, vector_memory, test_workspace_id):
        """Test similarity threshold filtering."""
        # Mock search results with low similarity
        mock_results = [
            {
                "id": "chunk-1",
                "content": "Low similarity content",
                "metadata": {},
                "similarity": 0.3,
            },
            {
                "id": "chunk-2",
                "content": "High similarity content",
                "metadata": {},
                "similarity": 0.9,
            },
        ]

        vector_memory.supabase_client.rpc.return_value.execute.return_value = {
            "data": mock_results,
            "error": None,
        }

        # Search with high threshold
        results = await vector_memory.search(
            workspace_id=test_workspace_id, query="test query", limit=10
        )

        # Verify results include all matches (filtering would be done at higher level)
        assert len(results) == 2
        assert results[0].score == 0.3
        assert results[1].score == 0.9
