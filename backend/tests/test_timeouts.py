"""
Comprehensive test suite for timeout handling and caching functionality.
Tests timeout management, recovery strategies, circuit breakers, and cache performance.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch

# Import the modules we're testing
from backend.core.timeouts import (
    TimeoutManager, TimeoutConfig, TimeoutError, OperationType, 
    RecoveryStrategy, CircuitBreaker, get_timeout_manager, execute_with_timeout
)
from backend.core.cache import (
    AgentCache, CacheConfig, CacheEntry, CacheEntryPriority,
    get_agent_cache, cache_agent_response, get_cached_response
)
from backend.core.metrics import (
    TimeoutMetrics, CacheMetrics, get_metrics_collector
)
from backend.agents.base import BaseAgent


class TestTimeouts:
    """Test suite for timeout handling functionality."""
    
    @pytest.fixture
    async def timeout_manager(self):
        """Create a test timeout manager."""
        config = TimeoutConfig(
            default_timeout=30,  # Shorter timeouts for testing
            max_timeout=120,
            retry_on_timeout=True,
            max_retries=2,
            base_backoff=0.5,
            max_backoff=5.0,
            circuit_breaker_threshold=3,
            circuit_breaker_timeout=60
        )
        return TimeoutManager(config=config)
    
    @pytest.fixture
    async def agent_cache(self):
        """Create a test agent cache."""
        config = CacheConfig(
            default_ttl=60,  # Shorter TTL for testing
            max_ttl=300,
            max_entries=100,
            cleanup_interval=30,
            enable_compression=True,
            max_memory_mb=50,
            eviction_policy="score_based"
        )
        from backend.core.cache import AgentCache
        return AgentCache(config=config)
    
    @pytest.fixture
    async def mock_agent(self):
        """Create a mock agent for testing."""
        agent = AsyncMock(spec=BaseAgent)
        agent.name = "test_agent"
        agent.description = "Test agent for timeout and caching"
        agent.tools = ["test_tool"]
        agent.skills = ["test_skill"]
        agent.metadata = {
            "name": "test_agent",
            "version": "1.0.0",
            "initialized_at": datetime.now().isoformat(),
        }
        return agent
    
    @pytest.fixture
    async def metrics_collector(self):
        """Create a test metrics collector."""
        from backend.core.metrics import get_metrics_collector
        return get_metrics_collector()
    
    @pytest.mark.asyncio
    async def test_timeout_manager_basic_functionality(self, timeout_manager, agent_cache):
        """Test basic timeout manager functionality."""
        # Test timeout configuration
        assert timeout_manager.config.default_timeout == 30
        assert timeout_manager.config.max_timeout == 120
        
        # Test task tracking
        active_tasks = timeout_manager.get_active_tasks()
        assert isinstance(active_tasks, dict)
        
        # Test timeout statistics
        stats = timeout_manager.get_timeout_stats()
        assert "stats" in stats
        assert "operation_stats" in stats
        assert "circuit_breakers" in stats
        
        logger.info("✓ Timeout manager basic functionality test passed")
    
    @pytest.mark.asyncio
    async def test_timeout_manager_per_operation_timeouts(self, timeout_manager):
        """Test per-operation timeout configuration."""
        # Test that different operations have different timeouts
        llm_timeout = timeout_manager.config.get_timeout_for_operation(OperationType.LLM_INFERENCE)
        tool_timeout = timeout_manager.config.get_timeout_for_operation(OperationType.TOOL_EXECUTION)
        db_timeout = timeout_manager.config.get_timeout_for_operation(OperationType.DATABASE_QUERY)
        
        assert llm_timeout == 60
        assert tool_timeout == 30
        assert db_timeout == 10
        
        logger.info("✓ Per-operation timeout configuration test passed")
    
    @pytest.mark.asyncio
    async def test_timeout_manager_recovery_strategies(self, timeout_manager):
        """Test timeout recovery strategies."""
        # Test that recovery strategies are properly configured
        strategies = timeout_manager._get_default_recovery_strategies(OperationType.AGENT_EXECUTION)
        assert RecoveryStrategy.RETRY_WITH_BACKOFF in strategies
        assert RecoveryStrategy.GRACEFUL_DEGRADATION in strategies
        assert RecoveryStrategy.PARTIAL_RESPONSE in strategies
        
        logger.info("✓ Timeout recovery strategies test passed")
    
    @pytest.mark.asyncio
    async def test_timeout_manager_circuit_breaker(self, timeout_manager):
        """Test circuit breaker functionality."""
        # Test circuit breaker creation and state management
        circuit_breaker = timeout_manager._get_circuit_breaker("test_operation")
        
        # Initially closed
        assert not circuit_breaker.is_open()
        
        # Record failures to open circuit
        for i in range(5):
            circuit_breaker.record_failure()
        
        # Should be open now
        assert circuit_breaker.is_open()
        
        # Test recovery after timeout
        circuit_breaker.record_success()
        
        # Should be closed after successful recovery
        assert not circuit_breaker.is_open()
        
        logger.info("✓ Circuit breaker functionality test passed")
    
    @pytest.mark.asyncio
    async def test_agent_cache_basic_operations(self, agent_cache):
        """Test basic cache operations."""
        # Test cache set and get
        test_request = "test_request"
        test_response = {"result": "test_response", "cached": True}
        
        # Test cache set
        success = await agent_cache.set("test_agent", test_request, test_response)
        assert success
        
        # Test cache get (hit)
        cached_response = await agent_cache.get("test_agent", test_request)
        assert cached_response == test_response
        
        # Test cache get (miss)
        await agent_cache.invalidate("test_agent")  # Clear to test miss
        cached_response = await agent_cache.get("test_agent", test_request)
        assert cached_response is None
        
        logger.info("✓ Agent cache basic operations test passed")
    
    @pytest.mark.asyncio
    async def test_agent_cache_ttl_expiration(self, agent_cache):
        """Test cache TTL expiration."""
        test_request = "ttl_test"
        test_response = {"result": "ttl_test_response"}
        
        # Set with short TTL
        success = await agent_cache.set("test_agent", test_request, test_response, ttl=5)
        assert success
        
        # Should get cached response
        cached_response = await agent_cache.get("test_agent", test_request)
        assert cached_response == test_response
        
        # Wait for expiration
        await asyncio.sleep(6)
        
        # Should be expired now
        cached_response = await agent_cache.get("test_agent", test_request)
        assert cached_response is None
        
        logger.info("✓ Cache TTL expiration test passed")
    
    @pytest.mark.asyncio
    async def test_agent_cache_memory_management(self, agent_cache):
        """Test cache memory management and eviction."""
        # Fill cache to test eviction
        for i in range(150):
            await agent_cache.set(
                "test_agent", 
                f"request_{i}", 
                {"result": f"response_{i}", "cached": True},
                ttl=3600
            )
        
        # Check memory usage
        stats = agent_cache.get_stats()
        assert stats["memory_usage_mb"] > 0
        
        # Trigger eviction by exceeding memory limit
        await agent_cache.set(
                "test_agent", 
                f"request_{i+150}", 
                {"result": f"response_{i+150}", "cached": True},
                ttl=3600
            )
        
        # Should have evicted some entries
        stats = agent_cache.get_stats()
        assert stats["cache_evictions"] > 0
        
        logger.info("✓ Cache memory management test passed")
    
    @pytest.mark.asyncio
    async def test_agent_cache_compression(self, agent_cache):
        """Test cache compression functionality."""
        # Create a large response to test compression
        large_response = {"data": "x" * 10000, "metadata": {"test": True}}
        
        # Set without compression
        success = await agent_cache.set("test_agent", "compression_test", large_response)
        assert success
        
        # Get and check compression
        cached_response = await agent_cache.get("test_agent", "compression_test")
        assert cached_response["data"] == large_response["data"]
        
        # Check compression stats
        stats = agent_cache.get_stats()
        assert stats["compression_ratio"] > 0
        
        logger.info("✓ Cache compression test passed")
    
    @pytest.mark.asyncio
    async def test_agent_cache_intelligent_invalidation(self, agent_cache):
        """Test cache intelligent invalidation."""
        # Test invalidation by agent name
        test_response = {"result": "invalidation_test", "cached": True}
        
        # Set cache entry
        success = await agent_cache.set("test_agent", "invalidation_test", test_response)
        assert success
        
        # Invalidate by agent name
        invalidated = await agent_cache.invalidate(agent_name="test_agent")
        assert invalidated > 0
        
        # Should not get cached response after invalidation
        cached_response = await agent_cache.get("test_agent", "invalidation_test")
        assert cached_response is None
        
        logger.info("✓ Cache intelligent invalidation test passed")
    
    @pytest.mark.asyncio
    async def test_timeout_monitoring(self, timeout_manager, metrics_collector):
        """Test timeout monitoring and alerting."""
        # Record some timeout events
        await timeout_manager.record_timeout(
            "agent_execution", "test_agent", 30, 25.5, 
            ["retry_with_backoff", "graceful_degradation"]
        )
        await timeout_manager.record_timeout(
            "llm_inference", "test_agent", 60, 45.2, 
            ["fallback_model", "cached_response"]
        )
        await timeout_manager.record_failure("agent_execution", "test_agent", "TestError")
        
        # Check timeout stats
        stats = timeout_manager.get_timeout_stats()
        assert stats["total_timeouts"] == 2
        assert stats["recoveries"] == 1
        assert stats["failures"] == 1
        
        # Check alert conditions
        # Should trigger alert due to high failure rate (50%)
        # This would trigger an alert in a real implementation
        
        logger.info("✓ Timeout monitoring test passed")
    
    @pytest.mark.asyncio
    async def test_cache_performance_monitoring(self, agent_cache, metrics_collector):
        """Test cache performance monitoring."""
        # Record cache operations
        await agent_cache.record_cache_request("test_agent", "test_operation", True, 0.1)
        await agent_cache.record_cache_request("test_agent", "test_operation", False, 0.2)
        await agent_cache.record_cache_request("test_agent", "test_operation", True, 0.05)
        
        # Record cache set
        await agent_cache.record_cache_set("test_agent", "test_operation", 1000, True)
        
        # Record eviction
        await agent_cache.record_cache_eviction("test_agent", "memory_pressure")
        
        # Check performance metrics
        stats = agent_cache.get_stats()
        assert stats["total_requests"] == 4
        assert stats["cache_hits"] == 2
        assert stats["cache_misses"] == 2
        assert stats["hit_rate"] == 0.5
        
        logger.info("✓ Cache performance monitoring test passed")
    
    @pytest.mark.asyncio
    async def test_integration_scenarios(self, timeout_manager, agent_cache, mock_agent):
        """Test integration scenarios between timeout and caching."""
        # Test timeout with cache miss
        with patch.object(mock_agent, 'get_cached_response') as mock_get_cached:
            mock_get_cached.return_value = None  # Cache miss
            mock_agent.execute_logic.return_value = {"result": "test_result"}
            
            result = await mock_agent.execute_with_enhanced_timeout({"request": "test"})
            
            # Should have attempted cache lookup
            mock_get_cached.assert_called_once_with("test_agent", "test", context=None)
            mock_agent.execute_logic.assert_called_once()
            
            # Should have executed logic
            mock_agent.execute_logic.assert_called_once()
            assert result["result"] == "test_result"
        
        # Test timeout with cache hit and recovery
        with patch.object(mock_agent, 'get_cached_response') as mock_get_cached:
            mock_get_cached.return_value = {"result": "cached_result", "recovered": True}  # Cache hit with recovery
            mock_agent.execute_logic.return_value = {"result": "timeout_result"}
            
            result = await mock_agent.execute_with_enhanced_timeout({"request": "test"})
            
            # Should have attempted cache lookup
            mock_get_cached.assert_called_once_with("test_agent", "test", context=None)
            mock_agent.execute_logic.assert_called_once()
            
            # Should have recovered from cache
            mock_agent.execute_logic.assert_not_called()  # Logic not called due to cache hit
        
        logger.info("✓ Integration scenarios test passed")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, timeout_manager, agent_cache, mock_agent):
        """Test error handling and recovery."""
        # Test timeout with recovery strategies
        with patch.object(mock_agent, 'handle_execution_error') as mock_handle_error:
            mock_handle_error.return_value = {
                "error_type": "TimeoutError",
                "recovery_result": {"success": True, "strategy": "retry_with_backoff"}
            }
            
            result = await mock_agent.execute_with_enhanced_timeout({"request": "test"})
            
            # Should have called error handler
            mock_handle_error.assert_called_once_with(
                "test_agent", 
                error=pytest.any(TimeoutError),
                context=pytest.any(dict)
            )
            
            # Should have recovered successfully
            assert result["recovery_result"]["success"] is True
        
        logger.info("✓ Error handling and recovery test passed")
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, timeout_manager, agent_cache):
        """Test performance requirements."""
        start_time = time.time()
        
        # Execute multiple operations to test performance
        for i in range(100):
            await agent_cache.set(f"perf_test_{i}", f"response_{i}", ttl=60)
            cached_response = await agent_cache.get(f"perf_test_{i}")
            assert cached_response is not None
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (100ms per operation average)
        assert duration < 10.0  # 100 operations * 100ms = 10s
        
        # Check cache hit rate
        stats = agent_cache.get_stats()
        hit_rate = stats.get("hit_rate", 0)
        
        # Should have good hit rate after warmup
        assert hit_rate > 0.8  # 80% hit rate
        
        logger.info(f"✓ Performance requirements test passed - Duration: {duration:.3f}s, Hit Rate: {hit_rate:.2f}")
    
    @pytest.mark.asyncio
    async def run_all_tests(self):
        """Run all timeout and caching tests."""
        logger.info("Starting timeout and caching test suite...")
        
        timeout_manager = await self.timeout_manager()
        agent_cache = await self.agent_cache()
        metrics_collector = await self.metrics_collector()
        mock_agent = await self.mock_agent()
        
        # Run all test categories
        await self.test_timeout_manager_basic_functionality(timeout_manager, agent_cache)
        await self.test_timeout_manager_per_operation_timeouts(timeout_manager, agent_cache)
        await self.test_timeout_manager_recovery_strategies(timeout_manager, agent_cache)
        await self.test_timeout_manager_circuit_breaker(timeout_manager, agent_cache)
        
        await self.test_agent_cache_basic_operations(agent_cache)
        await self.test_agent_cache_ttl_expiration(agent_cache)
        await self.test_agent_cache_memory_management(agent_cache)
        await self.test_agent_cache_compression(agent_cache)
        await self.test_agent_cache_intelligent_invalidation(agent_cache)
        
        await self.test_timeout_monitoring(timeout_manager, metrics_collector)
        await self.test_cache_performance_monitoring(agent_cache, metrics_collector)
        
        await self.test_integration_scenarios(timeout_manager, agent_cache, mock_agent)
        await self.test_error_handling(timeout_manager, agent_cache, mock_agent)
        await self.test_performance_requirements(timeout_manager, agent_cache)
        
        logger.info("✓ All timeout and caching tests passed!")


if __name__ == "__main__":
    asyncio.run(self.run_all_tests())
