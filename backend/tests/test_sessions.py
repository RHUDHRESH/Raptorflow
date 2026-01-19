"""
Comprehensive test suite for enhanced session management system.
Tests Redis-based sessions, performance tracking, and analytics.
"""

import asyncio
import pytest
import time
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from backend.core.sessions import (
    RedisSessionManager,
    EnhancedSession,
    SessionContext,
    SessionMetadata,
    SessionType,
    SessionStatus,
    SessionSecurityManager
)
from backend.core.metrics import MetricsCollector, MetricType, AnalyticsManager
from backend.core.performance import PerformanceOptimizer, ResourcePool
from backend.core.resource_pool import ConnectionPool, MemoryBufferPool


class TestSessionSecurityManager:
    """Test session security functionality."""
    
    @pytest.fixture
    def security_manager(self):
        """Create session security manager for testing."""
        return SessionSecurityManager("test-secret-key")
    
    def test_generate_security_token(self, security_manager):
        """Test JWT token generation."""
        session_id = str(uuid.uuid4())
        user_id = "test-user"
        
        token = security_manager.generate_security_token(session_id, user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_valid_security_token(self, security_manager):
        """Test valid token verification."""
        session_id = str(uuid.uuid4())
        user_id = "test-user"
        
        token = security_manager.generate_security_token(session_id, user_id)
        payload = security_manager.verify_security_token(token)
        
        assert payload is not None
        assert payload["session_id"] == session_id
        assert payload["user_id"] == user_id
        assert "exp" in payload
        assert "iat" in payload
    
    def test_verify_invalid_security_token(self, security_manager):
        """Test invalid token verification."""
        invalid_token = "invalid.token.here"
        payload = security_manager.verify_security_token(invalid_token)
        
        assert payload is None
    
    def test_encrypt_decrypt_data(self, security_manager):
        """Test data encryption and decryption."""
        original_data = "sensitive session data"
        
        encrypted = security_manager.encrypt_data(original_data)
        decrypted = security_manager.decrypt_data(encrypted)
        
        assert encrypted != original_data
        assert decrypted == original_data


class TestRedisSessionManager:
    """Test Redis-based session management."""
    
    @pytest.fixture
    async def session_manager(self):
        """Create Redis session manager for testing."""
        with patch('core.sessions.redis.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.return_value = True
            mock_client.setex.return_value = True
            mock_client.get.return_value = None
            mock_client.exists.return_value = False
            mock_redis.return_value = mock_client
            
            manager = RedisSessionManager(
                redis_url="redis://localhost:6379",
                secret_key="test-secret",
                session_ttl_minutes=30
            )
            await manager.initialize()
            yield manager
            await manager.stop()
    
    @pytest.mark.asyncio
    async def test_create_session(self, session_manager):
        """Test session creation."""
        user_id = "test-user"
        workspace_id = "test-workspace"
        session_type = SessionType.CHAT
        
        session_id = await session_manager.create_session(
            user_id=user_id,
            workspace_id=workspace_id,
            session_type=session_type
        )
        
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        
        # Verify session was stored
        session_manager.redis_client.setex.assert_called()
    
    @pytest.mark.asyncio
    async def test_validate_valid_session(self, session_manager):
        """Test valid session validation."""
        user_id = "test-user"
        workspace_id = "test-workspace"
        
        # Create session
        session_id = await session_manager.create_session(
            user_id=user_id,
            workspace_id=workspace_id
        )
        
        # Mock session data
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "session_type": "chat",
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "context": {},
            "metadata": {}
        }
        
        session_manager.redis_client.get.return_value = json.dumps(session_data).encode()
        
        # Validate session
        session = await session_manager.validate_session(session_id)
        
        assert session is not None
        assert session.session_id == session_id
        assert session.user_id == user_id
        assert session.workspace_id == workspace_id
    
    @pytest.mark.asyncio
    async def test_validate_expired_session(self, session_manager):
        """Test expired session validation."""
        user_id = "test-user"
        workspace_id = "test-workspace"
        
        # Create session
        session_id = await session_manager.create_session(
            user_id=user_id,
            workspace_id=workspace_id
        )
        
        # Mock expired session data
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "session_type": "chat",
            "status": "active",
            "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "expires_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "context": {},
            "metadata": {}
        }
        
        session_manager.redis_client.get.return_value = json.dumps(session_data).encode()
        
        # Validate session
        session = await session_manager.validate_session(session_id)
        
        assert session is None
    
    @pytest.mark.asyncio
    async def test_update_session_context(self, session_manager):
        """Test session context update."""
        user_id = "test-user"
        workspace_id = "test-workspace"
        
        # Create session
        session_id = await session_manager.create_session(
            user_id=user_id,
            workspace_id=workspace_id
        )
        
        # Update context
        context_update = {
            "conversation_history": [{"role": "user", "content": "hello"}],
            "agent_state": {"mood": "happy"}
        }
        
        success = await session_manager.update_session_context(
            session_id,
            context_update
        )
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_invalidate_session(self, session_manager):
        """Test session invalidation."""
        user_id = "test-user"
        workspace_id = "test-workspace"
        
        # Create session
        session_id = await session_manager.create_session(
            user_id=user_id,
            workspace_id=workspace_id
        )
        
        # Invalidate session
        success = await session_manager.invalidate_session(session_id, "test reason")
        
        assert success is True


class TestMetricsCollector:
    """Test metrics collection system."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector for testing."""
        return MetricsCollector(buffer_size=100)
    
    @pytest.mark.asyncio
    async def test_record_metric(self, metrics_collector):
        """Test metric recording."""
        event_id = await metrics_collector.record_metric(
            metric_type=MetricType.PERFORMANCE,
            name="response_time",
            value=1.5,
            unit="seconds",
            session_id="test-session",
            user_id="test-user"
        )
        
        assert event_id is not None
        assert isinstance(event_id, str)
        
        # Verify metric was stored
        assert len(metrics_collector.metrics_buffer) == 1
        metric = metrics_collector.metrics_buffer[0]
        assert metric.name == "response_time"
        assert metric.value == 1.5
        assert metric.metric_type == MetricType.PERFORMANCE
    
    @pytest.mark.asyncio
    async def test_get_metrics_with_filters(self, metrics_collector):
        """Test metric retrieval with filters."""
        # Record multiple metrics
        await metrics_collector.record_metric(
            MetricType.PERFORMANCE, "response_time", 1.5, "seconds"
        )
        await metrics_collector.record_metric(
            MetricType.SESSION, "session_created", 1, "count"
        )
        await metrics_collector.record_metric(
            MetricType.PERFORMANCE, "memory_usage", 256, "MB"
        )
        
        # Get only performance metrics
        perf_metrics = await metrics_collector.get_metrics(
            metric_type=MetricType.PERFORMANCE
        )
        
        assert len(perf_metrics) == 2
        assert all(m.metric_type == MetricType.PERFORMANCE for m in perf_metrics)
    
    @pytest.mark.asyncio
    async def test_aggregate_metrics(self, metrics_collector):
        """Test metric aggregation."""
        # Record multiple metrics
        for i in range(5):
            await metrics_collector.record_metric(
                MetricType.PERFORMANCE, "response_time", 1.0 + i, "seconds"
            )
        
        # Aggregate metrics
        aggregation = await metrics_collector.aggregate_metrics(
            metric_name="response_time",
            aggregation_type=MetricsCollector.AggregationType.AVERAGE,
            period_start=datetime.utcnow() - timedelta(hours=1),
            period_end=datetime.utcnow()
        )
        
        assert aggregation is not None
        assert aggregation.metric_name == "response_time"
        assert aggregation.aggregation_type == MetricsCollector.AggregationType.AVERAGE
        assert aggregation.value == 3.0  # Average of 1.0, 1.1, 1.2, 1.3, 1.4
        assert aggregation.count == 5


class TestPerformanceOptimizer:
    """Test performance optimization system."""
    
    @pytest.fixture
    def performance_optimizer(self):
        """Create performance optimizer for testing."""
        return PerformanceOptimizer()
    
    def test_start_tracking(self, performance_optimizer):
        """Test performance tracking start."""
        execution_id = "test-execution"
        agent_name = "test-agent"
        session_id = "test-session"
        
        tracker = performance_optimizer.start_tracking(
            execution_id, agent_name, session_id
        )
        
        assert tracker is not None
        assert execution_id in performance_optimizer.active_trackers
    
    def test_end_tracking(self, performance_optimizer):
        """Test performance tracking end."""
        execution_id = "test-execution"
        agent_name = "test-agent"
        session_id = "test-session"
        
        # Start tracking
        tracker = performance_optimizer.start_tracking(
            execution_id, agent_name, session_id
        )
        
        # End tracking with metrics
        additional_metrics = {
            "tokens_used": 100,
            "tool_calls": 5,
            "cache_hits": 10,
            "cache_misses": 2
        }
        
        metrics = asyncio.run(performance_optimizer.end_tracking(
            execution_id, agent_name, session_id, additional_metrics
        ))
        
        assert metrics is not None
        assert metrics.agent_name == agent_name
        assert metrics.execution_id == execution_id
        assert metrics.tokens_used == 100
        assert metrics.tool_calls == 5
        assert execution_id not in performance_optimizer.active_trackers
    
    def test_get_performance_summary(self, performance_optimizer):
        """Test performance summary retrieval."""
        # Add some test metrics
        performance_optimizer.agent_metrics["test1"] = MagicMock()
        performance_optimizer.agent_metrics["test2"] = MagicMock()
        
        summary = performance_optimizer.get_performance_summary()
        
        assert "current_metrics" in summary
        assert "agent_summary" in summary
        assert "total_executions" in summary
        assert summary["total_executions"] == 2


class TestResourcePool:
    """Test resource pooling system."""
    
    @pytest.fixture
    def connection_pool(self):
        """Create connection pool for testing."""
        def create_connection():
            return {"id": str(uuid.uuid4()), "active": True}
        
        def destroy_connection(conn):
            conn["active"] = False
        
        return ConnectionPool(
            pool_name="test-connections",
            connection_factory=create_connection,
            max_size=5
        )
    
    @pytest.mark.asyncio
    async def test_acquire_release_connection(self, connection_pool):
        """Test connection acquire and release."""
        # Acquire connection
        connection = connection_pool.acquire()
        
        assert connection is not None
        assert connection["active"] is True
        assert len(connection_pool._in_use) == 1
        
        # Release connection
        pooled_resource = connection_pool._in_use.pop()
        connection_pool.release(pooled_resource)
        
        assert len(connection_pool._available) == 1
        assert len(connection_pool._in_use) == 0
    
    @pytest.fixture
    def memory_pool(self):
        """Create memory pool for testing."""
        return MemoryBufferPool(
            pool_name="test-memory",
            buffer_size=1024,
            max_size=5
        )
    
    @pytest.mark.asyncio
    async def test_acquire_release_memory(self, memory_pool):
        """Test memory buffer acquire and release."""
        # Acquire memory
        memory = memory_pool.acquire()
        
        assert memory is not None
        assert isinstance(memory, bytearray)
        assert len(memory) == 1024
        assert len(memory_pool._in_use) == 1
        
        # Release memory
        pooled_resource = memory_pool._in_use.pop()
        memory_pool.release(pooled_resource)
        
        assert len(memory_pool._available) == 1
        assert len(memory_pool._in_use) == 0
    
    def test_pool_statistics(self, connection_pool):
        """Test pool statistics."""
        # Add some resources
        connection1 = connection_pool.acquire()
        connection2 = connection_pool.acquire()
        
        stats = connection_pool.get_statistics()
        
        assert stats.pool_name == "test-connections"
        assert stats.total_resources == 2
        assert stats.active_resources == 2
        assert stats.idle_resources == 0
        assert stats.total_acquisitions == 2


class TestSessionIntegration:
    """Test session integration with performance and analytics."""
    
    @pytest.mark.asyncio
    async def test_session_with_performance_tracking(self):
        """Test session with integrated performance tracking."""
        with patch('core.sessions.redis.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.return_value = True
            mock_redis.return_value = mock_client
            
            # Create session manager
            session_manager = RedisSessionManager(
                redis_url="redis://localhost:6379",
                secret_key="test-secret"
            )
            await session_manager.initialize()
            
            # Create performance optimizer
            perf_optimizer = PerformanceOptimizer()
            
            # Create session
            session_id = await session_manager.create_session(
                user_id="test-user",
                workspace_id="test-workspace"
            )
            
            # Simulate performance tracking
            execution_id = str(uuid.uuid4())
            tracker = perf_optimizer.start_tracking(
                execution_id, "test-agent", session_id
            )
            
            # End tracking
            metrics = await perf_optimizer.end_tracking(
                execution_id, "test-agent", session_id
            )
            
            assert metrics is not None
            assert session_id is not None
            
            await session_manager.stop()
    
    @pytest.mark.asyncio
    async def test_conversation_continuity(self):
        """Test conversation continuity across sessions."""
        with patch('core.sessions.redis.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.return_value = True
            mock_redis.return_value = mock_client
            
            session_manager = RedisSessionManager(
                redis_url="redis://localhost:6379",
                secret_key="test-secret"
            )
            await session_manager.initialize()
            
            # Create session with initial context
            session_id = await session_manager.create_session(
                user_id="test-user",
                workspace_id="test-workspace",
                initial_context={
                    "conversation_history": [
                        {"role": "user", "content": "Hello"}
                    ]
                }
            )
            
            # Update context with new message
            await session_manager.update_session_context(
                session_id,
                {
                    "conversation_history": [
                        {"role": "user", "content": "Hello"},
                        {"role": "assistant", "content": "Hi there!"}
                    ]
                }
            )
            
            # Validate session has updated context
            session = await session_manager.validate_session(session_id)
            assert session is not None
            assert len(session.context.conversation_history) == 2
            
            await session_manager.stop()


class TestSessionAnalytics:
    """Test session analytics functionality."""
    
    @pytest.mark.asyncio
    async def test_user_behavior_analysis(self):
        """Test user behavior pattern analysis."""
        metrics_collector = MetricsCollector()
        
        # Simulate user session data
        now = datetime.utcnow()
        for i in range(10):
            await metrics_collector.record_metric(
                MetricType.SESSION,
                "session_duration",
                15.0 + i,  # 15-24 minutes
                "minutes",
                user_id="test-user",
                timestamp=now - timedelta(days=i)
            )
            await metrics_collector.record_metric(
                MetricType.SESSION,
                "session_type",
                1,
                "count",
                user_id="test-user",
                tags={"type": "chat"},
                timestamp=now - timedelta(days=i)
            )
        
        # Create analytics manager
        analytics_manager = AnalyticsManager(metrics_collector)
        await analytics_manager.start()
        
        # Analyze user behavior
        pattern = await analytics_manager.session_analytics.analyze_user_behavior(
            "test-user", days=30
        )
        
        assert pattern is not None
        assert pattern.user_id == "test-user"
        assert pattern.session_frequency > 0
        assert pattern.avg_session_duration > 0
        assert "chat" in pattern.preferred_session_types
        
        await analytics_manager.stop()
    
    @pytest.mark.asyncio
    async def test_performance_insights(self):
        """Test performance insights generation."""
        metrics_collector = MetricsCollector()
        
        # Simulate performance data
        for i in range(10):
            await metrics_collector.record_metric(
                MetricType.PERFORMANCE,
                "response_time",
                2.0 + (i * 0.5),  # Increasing response times
                "seconds",
                agent_name="test-agent"
            )
            await metrics_collector.record_metric(
                MetricType.PERFORMANCE,
                "memory_usage",
                400 + (i * 50),  # Increasing memory usage
                "MB",
                agent_name="test-agent"
            )
        
        # Create analytics manager
        analytics_manager = AnalyticsManager(metrics_collector)
        await analytics_manager.start()
        
        # Analyze performance
        analysis = await analytics_manager.performance_analytics.analyze_performance(
            agent_name="test-agent", hours=24
        )
        
        assert "metrics" in analysis
        assert "insights" in analysis
        assert len(analysis["insights"]) > 0
        
        # Check for high response time insight
        insights = analysis["insights"]
        high_response_insights = [
            insight for insight in insights
            if insight.title == "High Response Times"
        ]
        assert len(high_response_insights) > 0
        
        await analytics_manager.stop()


# Performance and load testing
class TestSessionPerformance:
    """Test session system performance under load."""
    
    @pytest.mark.asyncio
    async def test_concurrent_session_creation(self):
        """Test concurrent session creation performance."""
        with patch('core.sessions.redis.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.return_value = True
            mock_client.setex.return_value = True
            mock_redis.return_value = mock_client
            
            session_manager = RedisSessionManager(
                redis_url="redis://localhost:6379",
                secret_key="test-secret"
            )
            await session_manager.initialize()
            
            # Create many sessions concurrently
            start_time = time.time()
            
            tasks = []
            for i in range(100):
                task = asyncio.create_task(
                    session_manager.create_session(
                        user_id=f"user-{i}",
                        workspace_id="test-workspace"
                    )
                )
                tasks.append(task)
            
            session_ids = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # Verify all sessions were created
            assert len([sid for sid in session_ids if sid is not None]) == 100
            
            # Check performance (should be under 5 seconds for 100 sessions)
            creation_time = end_time - start_time
            assert creation_time < 5.0
            
            await session_manager.stop()
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage under high load."""
        import psutil
        import gc
        
        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create many sessions and track metrics
        metrics_collector = MetricsCollector(buffer_size=10000)
        
        for i in range(1000):
            await metrics_collector.record_metric(
                MetricType.PERFORMANCE,
                "test_metric",
                i,
                "count"
            )
            
            if i % 100 == 0:
                gc.collect()  # Force garbage collection
        
        # Get final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 100MB for 1000 metrics)
        assert memory_increase < 100
        assert len(metrics_collector.metrics_buffer) <= 10000  # Should respect buffer limit


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
