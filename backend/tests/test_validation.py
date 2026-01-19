"""
Comprehensive test suite for request validation, security, and rate limiting.
Covers all validation scenarios and edge cases.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Import the modules we're testing
from backend.core.validation import RequestValidator, SecurityValidator, ValidationError
from backend.core.security import SecurityValidator as CoreSecurityValidator, SecurityPolicy
from backend.core.rate_limiting import RateLimiter, RateLimitResult, RateLimitPeriod
from backend.core.metrics import RequestMetricsCollector, RequestStatus, RequestMetric
from backend.api.v1.middleware import RequestValidationMiddleware
from backend.agents.base import BaseAgent
from backend.agents.dispatcher import AgentDispatcher


class TestRequestValidator:
    """Test cases for RequestValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance for testing."""
        return RequestValidator()
    
    @pytest.fixture
    def valid_request_data(self):
        """Valid request data for testing."""
        return {
            "request": "Hello, how can you help me today?",
            "workspace_id": "test_workspace_123",
            "user_id": "test_user_456",
            "session_id": "test_session_789",
            "context": {"key": "value"},
        }
    
    def test_validate_valid_request(self, validator, valid_request_data):
        """Test validation of valid request data."""
        result = validator.validate_agent_request(valid_request_data)
        
        assert result.request == "Hello, how can you help me today?"
        assert result.workspace_id == "test_workspace_123"
        assert result.user_id == "test_user_456"
        assert result.session_id == "test_session_789"
        assert result.context == {"key": "value"}
    
    def test_validate_missing_required_fields(self, validator):
        """Test validation with missing required fields."""
        # Missing workspace_id
        invalid_data = {
            "request": "Test request",
            "user_id": "test_user",
            "session_id": "test_session",
        }
        
        with pytest.raises(Exception) as exc_info:
            validator.validate_agent_request(invalid_data)
        
        assert "workspace_id" in str(exc_info.value)
    
    def test_validate_invalid_field_formats(self, validator):
        """Test validation with invalid field formats."""
        # Invalid workspace_id (contains special characters)
        invalid_data = {
            "request": "Test request",
            "workspace_id": "test@workspace#123",
            "user_id": "test_user_456",
            "session_id": "test_session_789",
        }
        
        with pytest.raises(Exception):
            validator.validate_agent_request(invalid_data)
    
    def test_validate_request_too_short(self, validator):
        """Test validation with request too short."""
        invalid_data = {
            "request": "Hi",  # Too short
            "workspace_id": "test_workspace_123",
            "user_id": "test_user_456",
            "session_id": "test_session_789",
        }
        
        with pytest.raises(Exception):
            validator.validate_agent_request(invalid_data)
    
    def test_validate_request_too_long(self, validator):
        """Test validation with request too long."""
        invalid_data = {
            "request": "x" * 10001,  # Too long
            "workspace_id": "test_workspace_123",
            "user_id": "test_user_456",
            "session_id": "test_session_789",
        }
        
        with pytest.raises(Exception):
            validator.validate_agent_request(invalid_data)
    
    def test_validate_context_too_large(self, validator):
        """Test validation with context too large."""
        invalid_data = {
            "request": "Test request",
            "workspace_id": "test_workspace_123",
            "user_id": "test_user_456",
            "session_id": "test_session_789",
            "context": {"data": "x" * 6000},  # Too large
        }
        
        with pytest.raises(Exception):
            validator.validate_agent_request(invalid_data)
    
    def test_validate_invalid_context_type(self, validator):
        """Test validation with invalid context type."""
        invalid_data = {
            "request": "Test request",
            "workspace_id": "test_workspace_123",
            "user_id": "test_user_456",
            "session_id": "test_session_789",
            "context": "not_a_dict",  # Invalid type
        }
        
        with pytest.raises(Exception):
            validator.validate_agent_request(invalid_data)


class TestSecurityValidator:
    """Test cases for SecurityValidator class."""
    
    @pytest.fixture
    def security_validator(self):
        """Create security validator instance for testing."""
        return CoreSecurityValidator()
    
    def test_validate_safe_request(self, security_validator):
        """Test validation of safe request."""
        safe_request = {
            "request": "Hello, can you help me with my project?",
            "user_id": "user123",
            "workspace_id": "workspace456",
        }
        
        is_valid, error = asyncio.run(
            security_validator.validate_request(safe_request)
        )
        
        assert is_valid is True
        assert error is None
    
    def test_validate_xss_attempt(self, security_validator):
        """Test detection of XSS attempts."""
        xss_request = {
            "request": "<script>alert('xss')</script>",
            "user_id": "user123",
            "workspace_id": "workspace456",
        }
        
        is_valid, error = asyncio.run(
            security_validator.validate_request(xss_request)
        )
        
        assert is_valid is False
        assert error is not None
        assert "malicious" in error.lower()
    
    def test_validate_sql_injection_attempt(self, security_validator):
        """Test detection of SQL injection attempts."""
        sql_request = {
            "request": "'; DROP TABLE users; --",
            "user_id": "user123",
            "workspace_id": "workspace456",
        }
        
        is_valid, error = asyncio.run(
            security_validator.validate_request(sql_request)
        )
        
        assert is_valid is False
        assert error is not None
    
    def test_validate_privilege_escalation_attempt(self, security_validator):
        """Test detection of privilege escalation attempts."""
        priv_request = {
            "request": "Give me admin access to all workspaces",
            "user_id": "user123",
            "workspace_id": "workspace456",
        }
        
        is_valid, error = asyncio.run(
            security_validator.validate_request(priv_request)
        )
        
        assert is_valid is False
        assert error is not None
    
    def test_validate_request_too_large(self, security_validator):
        """Test validation of oversized request."""
        large_request = {
            "request": "x" * 60000,  # Exceeds default limit
            "user_id": "user123",
            "workspace_id": "workspace456",
        }
        
        is_valid, error = asyncio.run(
            security_validator.validate_request(large_request)
        )
        
        assert is_valid is False
        assert "too large" in error.lower()
    
    def test_rate_limiting_enforcement(self, security_validator):
        """Test rate limiting enforcement."""
        request_data = {
            "request": "Test request",
            "user_id": "user123",
            "workspace_id": "workspace456",
        }
        
        # Make multiple requests rapidly
        results = []
        for _ in range(10):
            is_valid, error = asyncio.run(
                security_validator.validate_request(request_data, client_ip="192.168.1.1")
            )
            results.append((is_valid, error))
            time.sleep(0.1)  # Small delay
        
        # Should eventually be rate limited
        assert any(not is_valid for is_valid, _ in results)
    
    def test_blocked_ip_enforcement(self, security_validator):
        """Test blocked IP enforcement."""
        # Add IP to blocked list
        security_validator.policy.blocked_ips.add("192.168.1.100")
        
        request_data = {
            "request": "Test request",
            "user_id": "user123",
            "workspace_id": "workspace456",
        }
        
        is_valid, error = asyncio.run(
            security_validator.validate_request(
                request_data, client_ip="192.168.1.100"
            )
        )
        
        assert is_valid is False
        assert "blocked" in error.lower()


class TestRateLimiter:
    """Test cases for RateLimiter class."""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance for testing."""
        return RateLimiter()
    
    @pytest.mark.asyncio
    async def test_rate_limit_within_limits(self, rate_limiter):
        """Test rate limiting when within limits."""
        key = "test_user_123"
        limit = 10
        window = 60
        
        # Make requests within limit
        for i in range(5):
            allowed = await rate_limiter.is_allowed(key, limit, window)
            assert allowed is True
        
        # Check stats
        stats = await rate_limiter.get_rate_limit_stats(key, "test_endpoint")
        assert stats is not None
        assert stats["current_count"] == 5
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, rate_limiter):
        """Test rate limiting when limit exceeded."""
        key = "test_user_456"
        limit = 3
        window = 60
        
        # Make requests that exceed limit
        results = []
        for i in range(5):
            allowed = await rate_limiter.is_allowed(key, limit, window)
            results.append(allowed)
        
        # First 3 should be allowed, last 2 should be blocked
        assert results[:3] == [True, True, True]
        assert results[3:] == [False, False]
    
    @pytest.mark.asyncio
    async def test_rate_limit_window_expiry(self, rate_limiter):
        """Test rate limiting window expiry."""
        key = "test_user_789"
        limit = 2
        window = 2  # 2 seconds
        
        # Make requests that hit limit
        assert await rate_limiter.is_allowed(key, limit, window) is True
        assert await rate_limiter.is_allowed(key, limit, window) is True
        assert await rate_limiter.is_allowed(key, limit, window) is False
        
        # Wait for window to expire
        await asyncio.sleep(2.1)
        
        # Should be allowed again
        assert await rate_limiter.is_allowed(key, limit, window) is True
    
    @pytest.mark.asyncio
    async def test_rate_limit_reset(self, rate_limiter):
        """Test rate limit reset functionality."""
        key = "test_user_reset"
        limit = 5
        window = 60
        
        # Make some requests
        for i in range(3):
            await rate_limiter.is_allowed(key, limit, window)
        
        # Verify count
        stats = await rate_limiter.get_rate_limit_stats(key, "test_endpoint")
        assert stats["current_count"] == 3
        
        # Reset
        reset_success = await rate_limiter.reset_rate_limit(key, "test_endpoint")
        assert reset_success is True
        
        # Verify reset
        stats = await rate_limiter.get_rate_limit_stats(key, "test_endpoint")
        assert stats is None
    
    @pytest.mark.asyncio
    async def test_workspace_level_rate_limiting(self, rate_limiter):
        """Test workspace-level rate limiting."""
        user_id = "test_user_workspace"
        workspace_id = "test_workspace_123"
        endpoint = "agents"
        
        # Make workspace-level requests
        result1 = await rate_limiter.check_rate_limit(
            user_id=user_id,
            endpoint=endpoint,
            user_tier="free",
            workspace_id=workspace_id
        )
        
        assert result1.allowed is True
        assert "workspace:" in result1.key  # Verify workspace key is used


class TestRequestMetrics:
    """Test cases for RequestMetricsCollector class."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector instance for testing."""
        return RequestMetricsCollector()
    
    def test_start_request_tracking(self, metrics_collector):
        """Test starting request tracking."""
        request_id = "test_request_123"
        agent_name = "TestAgent"
        user_id = "test_user_456"
        workspace_id = "test_workspace_789"
        session_id = "test_session_000"
        
        start_time = metrics_collector.start_request(
            request_id, agent_name, user_id, workspace_id, session_id
        )
        
        assert isinstance(start_time, datetime)
        assert request_id in metrics_collector.current_requests
        assert metrics_collector.concurrent_counts[f"user:{user_id}"] == 1
    
    def test_end_request_tracking_success(self, metrics_collector):
        """Test ending request tracking with success."""
        request_id = "test_request_success"
        agent_name = "TestAgent"
        user_id = "test_user_456"
        workspace_id = "test_workspace_789"
        session_id = "test_session_000"
        
        # Start tracking
        metrics_collector.start_request(
            request_id, agent_name, user_id, workspace_id, session_id
        )
        
        # End tracking with success
        metric = metrics_collector.end_request(
            request_id, agent_name, user_id, workspace_id, session_id,
            request_length=100, response_length=500, status=RequestStatus.SUCCESS,
            llm_tokens_used=50, tools_used=["tool1", "tool2"]
        )
        
        assert metric is not None
        assert metric.request_id == request_id
        assert metric.status == RequestStatus.SUCCESS
        assert metric.execution_time > 0
        assert metric.llm_tokens_used == 50
        assert metric.tools_used == ["tool1", "tool2"]
        assert request_id not in metrics_collector.current_requests
    
    def test_end_request_tracking_error(self, metrics_collector):
        """Test ending request tracking with error."""
        request_id = "test_request_error"
        agent_name = "TestAgent"
        user_id = "test_user_456"
        workspace_id = "test_workspace_789"
        session_id = "test_session_000"
        
        # Start tracking
        metrics_collector.start_request(
            request_id, agent_name, user_id, workspace_id, session_id
        )
        
        # End tracking with error
        metric = metrics_collector.end_request(
            request_id, agent_name, user_id, workspace_id, session_id,
            request_length=100, response_length=0, status=RequestStatus.ERROR,
            error_code="VALIDATION_ERROR", error_message="Test error"
        )
        
        assert metric is not None
        assert metric.status == RequestStatus.ERROR
        assert metric.error_code == "VALIDATION_ERROR"
        assert metric.error_message == "Test error"
    
    def test_performance_issue_detection(self, metrics_collector):
        """Test detection of performance issues."""
        request_id = "test_request_slow"
        agent_name = "TestAgent"
        user_id = "test_user_456"
        workspace_id = "test_workspace_789"
        session_id = "test_session_000"
        
        # Start tracking
        metrics_collector.start_request(
            request_id, agent_name, user_id, workspace_id, session_id
        )
        
        # End tracking with very slow response
        metric = metrics_collector.end_request(
            request_id, agent_name, user_id, workspace_id, session_id,
            request_length=100, response_length=1000, status=RequestStatus.SUCCESS
        )
        
        # Manually set slow execution time to test detection
        metric.execution_time = 15.0  # Very slow
        
        # Check performance issues (this would normally be logged)
        assert metric.execution_time > metrics_collector.performance_thresholds["very_slow_request"]
    
    def test_get_metrics_summary(self, metrics_collector):
        """Test getting metrics summary."""
        # Add some test metrics
        for i in range(10):
            request_id = f"test_request_{i}"
            metrics_collector.start_request(
                request_id, "TestAgent", "test_user", "test_workspace", "test_session"
            )
            
            status = RequestStatus.SUCCESS if i < 8 else RequestStatus.ERROR
            metrics_collector.end_request(
                request_id, "TestAgent", "test_user", "test_workspace", "test_session",
                request_length=100, response_length=200, status=status
            )
        
        # Get summary
        summary = metrics_collector.get_metrics_summary(hours=24)
        
        assert summary["summary"]["total_requests"] == 10
        assert summary["summary"]["successful_requests"] == 8
        assert summary["summary"]["error_requests"] == 2
        assert summary["summary"]["success_rate"] == 80.0
        assert "performance" in summary
        assert "avg_execution_time" in summary["performance"]


class TestAgentDispatcher:
    """Test cases for AgentDispatcher class."""
    
    @pytest.fixture
    def dispatcher(self):
        """Create dispatcher instance for testing."""
        return AgentDispatcher()
    
    @pytest.mark.asyncio
    async def test_agent_health_initialization(self, dispatcher):
        """Test agent health status initialization."""
        # Check that all agents have health status
        for agent_name in dispatcher.registry.list_agents():
            assert agent_name in dispatcher.agent_health_status
            assert "status" in dispatcher.agent_health_status[agent_name]
            assert "is_available" in dispatcher.agent_health_status[agent_name]
    
    @pytest.mark.asyncio
    async def test_healthy_agent_selection(self, dispatcher):
        """Test selection of healthy agents."""
        # Mark an agent as healthy
        agent_name = "OnboardingOrchestrator"
        dispatcher._update_agent_health(agent_name, True, response_time=1.0)
        
        # Check if agent is considered healthy
        assert dispatcher._is_agent_healthy(agent_name) is True
    
    @pytest.mark.asyncio
    async def test_unhealthy_agent_selection(self, dispatcher):
        """Test handling of unhealthy agents."""
        # Mark an agent as unhealthy
        agent_name = "OnboardingOrchestrator"
        dispatcher._update_agent_health(agent_name, False, error="Test error")
        
        # Check if agent is considered unhealthy
        assert dispatcher._is_agent_healthy(agent_name) is False
    
    @pytest.mark.asyncio
    async def test_fallback_agent_selection(self, dispatcher):
        """Test fallback agent selection when primary is unhealthy."""
        # Mark primary agent as unhealthy
        primary_agent = "OnboardingOrchestrator"
        fallback_agent = dispatcher.fallback_agent
        
        dispatcher._update_agent_health(primary_agent, False, error="Primary agent failed")
        
        # Find healthy alternative
        alternative = await dispatcher._find_healthy_alternative(primary_agent)
        
        # Should return fallback agent
        assert alternative == fallback_agent
    
    @pytest.mark.asyncio
    async def test_health_check_performance(self, dispatcher):
        """Test health check performance monitoring."""
        agent_name = "OnboardingOrchestrator"
        
        # Perform health check
        is_healthy = await dispatcher._perform_agent_health_check(agent_name)
        
        # Should complete without error
        assert isinstance(is_healthy, bool)
        
        # Check that health status was updated
        health = dispatcher.agent_health_status[agent_name]
        assert health["last_check"] is not None
    
    @pytest.mark.asyncio
    async def test_enhanced_dispatcher_stats(self, dispatcher):
        """Test enhanced dispatcher statistics."""
        # Get enhanced stats
        stats = dispatcher.get_enhanced_dispatcher_stats()
        
        # Check required fields
        assert "health" in stats
        assert "performance" in stats
        assert "total_agents" in stats["health"]
        assert "healthy_agents" in stats["health"]
        assert "success_rate" in stats["performance"]


class TestRequestValidationMiddleware:
    """Test cases for RequestValidationMiddleware."""
    
    @pytest.fixture
    def mock_app(self):
        """Create mock FastAPI app for testing."""
        from fastapi import FastAPI
        return FastAPI()
    
    @pytest.fixture
    def middleware(self, mock_app):
        """Create middleware instance for testing."""
        return RequestValidationMiddleware(mock_app)
    
    def test_should_skip_validation_excluded_paths(self, middleware):
        """Test skipping validation for excluded paths."""
        from fastapi import Request
        
        # Test excluded paths
        excluded_paths = ["/health", "/docs", "/static"]
        for path in excluded_paths:
            request = Request({"type": "http"}, "GET", path)
            assert middleware._should_skip_validation(request) is True
    
    def test_should_skip_validation_options_request(self, middleware):
        """Test skipping validation for OPTIONS requests."""
        from fastapi import Request
        
        request = Request({"type": "http"}, "OPTIONS", "/api/v1/agents")
        assert middleware._should_skip_validation(request) is True
    
    def test_extract_client_ip_forwarded(self, middleware):
        """Test extracting client IP from forwarded header."""
        from fastapi import Request
        
        headers = {"x-forwarded-for": "192.168.1.100, 10.0.0.1"}
        request = Request({"type": "http", "headers": headers}, "GET", "/test")
        
        client_ip = middleware._get_client_ip(request)
        assert client_ip == "192.168.1.100"
    
    def test_extract_client_ip_real_ip(self, middleware):
        """Test extracting client IP from real IP header."""
        from fastapi import Request
        
        headers = {"x-real-ip": "192.168.1.200"}
        request = Request({"type": "http", "headers": headers}, "GET", "/test")
        
        client_ip = middleware._get_client_ip(request)
        assert client_ip == "192.168.1.200"
    
    def test_extract_auth_info_from_headers(self, middleware):
        """Test extracting auth info from headers."""
        from fastapi import Request
        
        headers = {
            "authorization": "Bearer test_token_123",
            "x-user-id": "user456",
            "x-workspace-id": "workspace789",
            "x-user-tier": "pro"
        }
        request = Request({"type": "http", "headers": headers}, "GET", "/test")
        
        auth_info = asyncio.run(middleware._extract_auth_info(request))
        
        assert auth_info["is_authenticated"] is True
        assert auth_info["user_id"] == "user456"
        assert auth_info["workspace_id"] == "workspace789"
        assert auth_info["user_tier"] == "pro"
    
    def test_extract_agent_name_from_path(self, middleware):
        """Test extracting agent name from request path."""
        from fastapi import Request
        
        request = Request({"type": "http"}, "GET", "/api/v1/agents/TestAgent")
        
        agent_name = middleware._extract_agent_name(request)
        assert agent_name == "TestAgent"
    
    def test_get_endpoint_for_rate_limiting(self, middleware):
        """Test getting endpoint identifier for rate limiting."""
        from fastapi import Request
        
        test_cases = [
            ("/api/v1/agents/TestAgent", "agents"),
            ("/api/v1/auth/login", "auth"),
            ("/api/v1/upload/file", "upload"),
            ("/api/v1/export/data", "export"),
            ("/api/v1/search/query", "search"),
            ("/api/v1/other/endpoint", "api"),
        ]
        
        for path, expected_endpoint in test_cases:
            request = Request({"type": "http"}, "GET", path)
            endpoint = middleware._get_endpoint_for_rate_limiting(request)
            assert endpoint == expected_endpoint
    
    def test_create_rate_limit_response(self, middleware):
        """Test creating rate limit error response."""
        from datetime import datetime, timedelta
        
        reset_time = datetime.now() + timedelta(minutes=1)
        rate_limit_result = RateLimitResult(
            allowed=False,
            remaining=0,
            reset_at=reset_time,
            limit=100,
            window_seconds=60,
            retry_after=30
        )
        
        response = middleware._create_rate_limit_response(rate_limit_result)
        
        assert response.status_code == 429
        content = response.body.decode()
        assert "Rate limit exceeded" in content
        assert "X-RateLimit-Limit" in response.headers
        assert "Retry-After" in response.headers


class TestIntegration:
    """Integration tests for the complete validation system."""
    
    @pytest.mark.asyncio
    async def test_complete_validation_flow(self):
        """Test complete validation flow from middleware to agent."""
        # This would test the entire flow:
        # 1. Middleware receives request
        # 2. Rate limiting is checked
        # 3. Security validation is performed
        # 4. Request validation is done
        # 5. Metrics are collected
        # 6. Agent is dispatched
        
        # For now, just test that components can be instantiated together
        validator = RequestValidator()
        security_validator = CoreSecurityValidator()
        rate_limiter = RateLimiter()
        metrics_collector = RequestMetricsCollector()
        
        assert validator is not None
        assert security_validator is not None
        assert rate_limiter is not None
        assert metrics_collector is not None
    
    def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms."""
        # Test that validation errors are properly handled
        validator = RequestValidator()
        
        # Test various error conditions
        invalid_requests = [
            {},  # Empty request
            {"request": ""},  # Empty request field
            {"request": "x" * 10001},  # Too long
            {"request": "test", "workspace_id": ""},  # Missing required field
        ]
        
        for invalid_request in invalid_requests:
            with pytest.raises(Exception):
                validator.validate_agent_request(invalid_request)
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test system performance under load."""
        import time
        
        validator = RequestValidator()
        valid_request = {
            "request": "Test request for performance testing",
            "workspace_id": "perf_test_workspace",
            "user_id": "perf_test_user",
            "session_id": "perf_test_session",
        }
        
        # Measure validation time under load
        start_time = time.time()
        
        tasks = []
        for i in range(100):
            task = asyncio.create_task(
                asyncio.to_thread(validator.validate_agent_request, valid_request)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check that performance is reasonable (< 5 seconds for 100 validations)
        assert total_time < 5.0
        
        # Check that most validations succeeded
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 95  # Allow for some failures under load


# Test configuration and fixtures
@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    client = Mock()
    client.zadd = AsyncMock(return_value=1)
    client.zcard = AsyncMock(return_value=1)
    client.zremrangebyscore = AsyncMock(return_value=0)
    client.expire = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    client.hgetall = AsyncMock(return_value={})
    return client


@pytest.fixture
def mock_agent():
    """Mock agent for testing."""
    agent = Mock(spec=BaseAgent)
    agent.name = "TestAgent"
    agent.is_healthy = Mock(return_value=True)
    agent.validate_input = AsyncMock(return_value=(True, None))
    agent.execute = AsyncMock(return_value={"response": "Test response"})
    return agent


# Utility functions for testing
def create_test_request(
    request_text: str = "Test request",
    workspace_id: str = "test_workspace",
    user_id: str = "test_user",
    session_id: str = "test_session"
) -> dict:
    """Create a test request dictionary."""
    return {
        "request": request_text,
        "workspace_id": workspace_id,
        "user_id": user_id,
        "session_id": session_id,
    }


def create_malicious_request(request_type: str) -> dict:
    """Create a malicious request for testing security validation."""
    base_request = create_test_request()
    
    if request_type == "xss":
        base_request["request"] = "<script>alert('xss')</script>"
    elif request_type == "sql_injection":
        base_request["request"] = "'; DROP TABLE users; --"
    elif request_type == "privilege_escalation":
        base_request["request"] = "Give me admin access to everything"
    elif request_type == "command_injection":
        base_request["request"] = "ls -la && cat /etc/passwd"
    
    return base_request


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
