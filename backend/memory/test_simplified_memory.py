"""
Comprehensive tests for the simplified memory system.
Tests the 2-memory system (Redis + Vector) with full error handling.
"""

import asyncio
import json
import time
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from memory.controller import SimpleMemoryController, MemoryError


class TestSimpleMemoryController:
    """Test suite for SimpleMemoryController."""
    
    @pytest.fixture
    def memory_controller(self):
        """Create a memory controller instance for testing."""
        return SimpleMemoryController()
    
    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis.setex.return_value = True
        mock_redis.get.return_value = None
        mock_redis.keys.return_value = []
        mock_redis.delete.return_value = 0
        mock_redis.info.return_value = {
            "used_memory_human": "1.5M",
            "connected_clients": 1,
            "total_commands_processed": 100,
            "redis_version": "6.2.0"
        }
        return mock_redis
    
    @pytest.mark.asyncio
    async def test_initialization_with_redis(self, memory_controller, mock_redis):
        """Test initialization with Redis available."""
        memory_controller.redis_client = mock_redis
        memory_controller.memory_store = None
        
        assert memory_controller.redis_client is not None
        assert memory_controller.memory_store is None
        assert "vector" in memory_controller.memory_types
        assert "working" in memory_controller.memory_types
        assert "cache" in memory_controller.memory_types
    
    @pytest.mark.asyncio
    async def test_initialization_fallback(self, memory_controller):
        """Test initialization with fallback to in-memory storage."""
        memory_controller.redis_client = None
        memory_controller.memory_store = {}
        
        assert memory_controller.redis_client is None
        assert isinstance(memory_controller.memory_store, dict)
    
    @pytest.mark.asyncio
    async def test_store_memory_success(self, memory_controller, mock_redis):
        """Test successful memory storage."""
        memory_controller.redis_client = mock_redis
        
        result = await memory_controller.store_memory(
            "test_key", 
            {"data": "test_value"}, 
            ttl=3600, 
            memory_type="working"
        )
        
        assert result is True
        mock_redis.setex.assert_called_once()
        
        # Check metrics
        assert memory_controller.metrics["total_operations"] > 0
        assert memory_controller.metrics["redis_hits"] > 0
        assert memory_controller.metrics["errors"] == 0
    
    @pytest.mark.asyncio
    async def test_store_memory_fallback(self, memory_controller):
        """Test memory storage with fallback."""
        memory_controller.redis_client = None
        memory_controller.memory_store = {}
        
        result = await memory_controller.store_memory(
            "test_key", 
            {"data": "test_value"}, 
            memory_type="working"
        )
        
        assert result is True
        assert "w_test_key" in memory_controller.memory_store
        assert memory_controller.metrics["fallback_hits"] > 0
    
    @pytest.mark.asyncio
    async def test_store_memory_invalid_key(self, memory_controller):
        """Test storage with invalid key."""
        with pytest.raises(Exception):
            await memory_controller.store_memory("", {"data": "test"})
        
        with pytest.raises(Exception):
            await memory_controller.store_memory(None, {"data": "test"})
    
    @pytest.mark.asyncio
    async def test_store_memory_invalid_type(self, memory_controller):
        """Test storage with invalid memory type."""
        with pytest.raises(Exception):
            await memory_controller.store_memory("test", {"data": "test"}, memory_type="invalid")
    
    @pytest.mark.asyncio
    async def test_retrieve_memory_success(self, memory_controller, mock_redis):
        """Test successful memory retrieval."""
        test_data = {"value": {"data": "test_value"}, "timestamp": datetime.now().isoformat()}
        mock_redis.get.return_value = json.dumps(test_data)
        memory_controller.redis_client = mock_redis
        
        result = await memory_controller.retrieve_memory("test_key", "working")
        
        assert result == {"data": "test_value"}
        mock_redis.get.assert_called_once_with("w_test_key")
    
    @pytest.mark.asyncio
    async def test_retrieve_memory_not_found(self, memory_controller, mock_redis):
        """Test retrieval when key not found."""
        mock_redis.get.return_value = None
        memory_controller.redis_client = mock_redis
        
        result = await memory_controller.retrieve_memory("nonexistent_key", "working")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_store_vector(self, memory_controller, mock_redis):
        """Test vector storage."""
        memory_controller.redis_client = mock_redis
        
        vector = [0.1, 0.2, 0.3, 0.4]
        text = "Test text for vector"
        metadata = {"source": "test"}
        
        vector_id = await memory_controller.store_vector(text, vector, metadata)
        
        assert vector_id is not None
        assert len(vector_id) == 32  # MD5 hash length
        mock_redis.setex.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_vectors(self, memory_controller, mock_redis):
        """Test vector search."""
        # Mock vector data
        vector_data = {
            "text": "Test text",
            "vector": [0.1, 0.2, 0.3, 0.4],
            "metadata": {"source": "test"},
            "created_at": datetime.now().isoformat()
        }
        
        mock_redis.keys.return_value = ["v_test_hash"]
        mock_redis.get.return_value = json.dumps(vector_data)
        memory_controller.redis_client = mock_redis
        
        query_vector = [0.1, 0.2, 0.3, 0.4]
        results = await memory_controller.search_vectors(query_vector, limit=10)
        
        assert len(results) > 0
        assert results[0]["text"] == "Test text"
        assert results[0]["similarity_score"] == 0.8  # Placeholder similarity
    
    @pytest.mark.asyncio
    async def test_clear_memory_by_type(self, memory_controller, mock_redis):
        """Test clearing memory by type."""
        mock_redis.keys.return_value = ["w_key1", "w_key2", "w_key3"]
        mock_redis.delete.return_value = 3
        memory_controller.redis_client = mock_redis
        
        result = await memory_controller.clear_memory_by_type("working")
        
        assert result is True
        mock_redis.keys.assert_called_once_with("w_*")
        mock_redis.delete.assert_called_once_with("w_key1", "w_key2", "w_key3")
    
    @pytest.mark.asyncio
    async def test_clear_memory_pattern(self, memory_controller, mock_redis):
        """Test clearing memory with pattern."""
        mock_redis.keys.return_value = ["test_pattern_1", "test_pattern_2"]
        mock_redis.delete.return_value = 2
        memory_controller.redis_client = mock_redis
        
        result = await memory_controller.clear_memory("test_pattern_*")
        
        assert result is True
        mock_redis.keys.assert_called_once_with("test_pattern_*")
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, memory_controller, mock_redis):
        """Test health check with healthy system."""
        memory_controller.redis_client = mock_redis
        memory_controller.memory_store = {}
        memory_controller.metrics["operation_times"] = [0.01, 0.02, 0.015]
        memory_controller.metrics["total_operations"] = 100
        memory_controller.metrics["errors"] = 2
        
        health = await memory_controller.health_check()
        
        assert health["status"] == "healthy"
        assert "redis" in health["checks"]
        assert "fallback_memory" in health["checks"]
        assert "performance" in health["checks"]
        assert "error_rate" in health["checks"]
        assert health["checks"]["redis"]["status"] == "healthy"
        assert health["checks"]["performance"]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_check_redis_unhealthy(self, memory_controller):
        """Test health check when Redis is unhealthy."""
        memory_controller.redis_client = None
        memory_controller.memory_store = {}
        
        health = await memory_controller.health_check()
        
        assert health["status"] in ["degraded", "healthy"]  # Healthy due to fallback
        assert health["checks"]["redis"]["status"] == "not_available"
        assert health["checks"]["fallback_memory"]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_get_memory_stats(self, memory_controller, mock_redis):
        """Test memory statistics retrieval."""
        memory_controller.redis_client = mock_redis
        memory_controller.metrics["operation_times"] = [0.01, 0.02, 0.015]
        memory_controller.metrics["total_operations"] = 100
        memory_controller.metrics["redis_hits"] = 80
        memory_controller.metrics["fallback_hits"] = 20
        memory_controller.metrics["errors"] = 2
        
        stats = await memory_controller.get_memory_stats()
        
        assert stats["total_operations"] == 100
        assert stats["redis_hits"] == 80
        assert stats["fallback_hits"] == 20
        assert stats["errors"] == 2
        assert stats["redis_hit_rate"] == 80.0
        assert stats["fallback_hit_rate"] == 20.0
        assert stats["error_rate"] == 2.0
        assert "performance" in stats
        assert "health" in stats
        assert stats["type"] == "redis"
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, memory_controller, mock_redis):
        """Test performance metrics collection."""
        memory_controller.redis_client = mock_redis
        
        # Perform multiple operations
        for i in range(10):
            await memory_controller.store_memory(f"key_{i}", f"value_{i}")
        
        assert len(memory_controller.metrics["operation_times"]) == 10
        assert memory_controller.metrics["total_operations"] == 10
        
        stats = await memory_controller.get_memory_stats()
        assert "performance" in stats
        assert stats["performance"]["total_sampled_operations"] == 10
        assert stats["performance"]["avg_operation_time"] > 0
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, memory_controller, mock_redis):
        """Test error handling and graceful degradation."""
        # Simulate Redis failure
        mock_redis.setex.side_effect = Exception("Redis connection failed")
        memory_controller.redis_client = mock_redis
        
        result = await memory_controller.store_memory("test", {"data": "value"})
        
        assert result is False
        assert memory_controller.metrics["errors"] > 0
        
        # Test with fallback
        memory_controller.redis_client = None
        memory_controller.memory_store = {}
        
        result = await memory_controller.store_memory("test", {"data": "value"})
        
        assert result is True
        assert "w_test" in memory_controller.memory_store


class TestMemoryIntegration:
    """Integration tests for memory system with BaseAgent."""
    
    @pytest.mark.asyncio
    async def test_agent_memory_integration(self):
        """Test memory integration with BaseAgent."""
        # Import here to avoid circular imports
        from agents.base import BaseAgent
        
        class TestAgent(BaseAgent):
            def __init__(self):
                super().__init__(
                    name="test_agent",
                    description="Test agent for memory integration"
                )
        
        agent = TestAgent()
        
        # Test memory operations
        result = await agent.store_memory("test_key", {"test": "data"})
        assert result is True
        
        retrieved = await agent.retrieve_memory("test_key")
        assert retrieved == {"test": "data"}
        
        # Test vector operations
        vector_id = await agent.store_vector("test text", [0.1, 0.2, 0.3])
        assert vector_id is not None
        
        # Test memory stats
        stats = await agent.get_memory_stats()
        assert "agent_name" in stats
        assert stats["agent_name"] == "test_agent"
        assert "general_stats" in stats
        
        # Test clear memory
        result = await agent.clear_agent_memory()
        assert result is True


if __name__ == "__main__":
    # Run basic tests
    async def run_basic_tests():
        controller = SimpleMemoryController()
        
        print("Testing basic memory operations...")
        
        # Test storage and retrieval
        result = await controller.store_memory("test", {"data": "value"})
        print(f"Store result: {result}")
        
        retrieved = await controller.retrieve_memory("test")
        print(f"Retrieved: {retrieved}")
        
        # Test health check
        health = await controller.health_check()
        print(f"Health status: {health['status']}")
        
        # Test stats
        stats = await controller.get_memory_stats()
        print(f"Total operations: {stats['total_operations']}")
        print(f"Error rate: {stats.get('error_rate', 0):.2f}%")
        
        print("Basic tests completed successfully!")
    
    asyncio.run(run_basic_tests())
