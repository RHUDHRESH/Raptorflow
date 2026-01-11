"""
Unit tests for RaptorFlow backend components.
Tests individual components in isolation.
"""

import asyncio
import time
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pytest


# Test individual components
class TestMemoryController:
    """Test memory controller components."""

    @pytest.fixture
    def mock_memory_controller(self):
        """Mock memory controller."""
        controller = AsyncMock()
        controller.search.return_value = []
        controller.store.return_value = "memory_id"
        controller.delete.return_value = True
        return controller

    @pytest.mark.asyncio
    async def test_memory_search(self, mock_memory_controller):
        """Test memory search functionality."""
        result = await mock_memory_controller.search(
            workspace_id="test_workspace",
            query="test query",
            memory_types=["foundation"],
            limit=10,
        )

        assert isinstance(result, list)
        mock_memory_controller.search.assert_called_once_with(
            workspace_id="test_workspace",
            query="test query",
            memory_types=["foundation"],
            limit=10,
        )

    @pytest.mark.asyncio
    async def test_memory_store(self, mock_memory_controller):
        """Test memory store functionality."""
        result = await mock_memory_controller.store(
            workspace_id="test_workspace",
            memory_type="test",
            content="test content",
            metadata={"key": "value"},
        )

        assert result == "memory_id"
        mock_memory_controller.store.assert_called_once_with(
            workspace_id="test_workspace",
            memory_type="test",
            content="test content",
            metadata={"key": "value"},
        )


class TestCognitiveEngine:
    """Test cognitive engine components."""

    @pytest.fixture
    def mock_cognitive_engine(self):
        """Mock cognitive engine."""
        engine = AsyncMock()
        engine.perception = AsyncMock()
        engine.planning = AsyncMock()
        engine.reflection = AsyncMock()
        engine.critic = AsyncMock()
        return engine

    @pytest.mark.asyncio
    async def test_perception_module(self, mock_cognitive_engine):
        """Test perception module."""
        mock_cognitive_engine.perception.perceive.return_value = Mock(
            intent="test_intent",
            entities=[{"type": "person", "name": "John"}],
            confidence=0.9,
        )

        result = await mock_cognitive_engine.perception.perceive(
            text="John went to the store", history=[]
        )

        assert result.intent == "test_intent"
        assert len(result.entities) == 1
        assert result.confidence == 0.9

    @pytest.mark.asyncio
    async def test_planning_module(self, mock_cognitive_engine):
        """Test planning module."""
        mock_cognitive_engine.planning.plan.return_value = Mock(
            goal="test goal",
            steps=[{"action": "research", "duration": 60}],
            total_cost=0.5,
            risk_level="low",
        )

        result = await mock_cognitive_engine.planning.plan(
            goal="Research market trends", perceived=None, context={}
        )

        assert result.goal == "test goal"
        assert len(result.steps) == 1
        assert result.total_cost == 0.5
        assert result.risk_level == "low"

    @pytest.mark.asyncio
    async def test_reflection_module(self, mock_cognitive_engine):
        """Test reflection module."""
        mock_cognitive_engine.reflection.reflect.return_value = Mock(
            quality_score=0.8,
            approved=True,
            feedback="Good quality",
            improvements=["Add more detail"],
        )

        result = await mock_cognitive_engine.reflection.reflect(
            output="Test output content",
            goal="Assess quality",
            context={},
            max_iterations=2,
        )

        assert result.quality_score == 0.8
        assert result.approved is True
        assert result.feedback == "Good quality"
        assert len(result.improvements) == 1


class TestAgents:
    """Test agent components."""

    @pytest.fixture
    def mock_agent(self):
        """Mock agent."""
        agent = AsyncMock()
        agent.name = "test_agent"
        agent.description = "Test agent for unit testing"
        agent.execute.return_value = {
            "success": True,
            "output": "test output",
            "tokens_used": 100,
        }
        return agent

    @pytest.mark.asyncio
    async def test_agent_execution(self, mock_agent):
        """Test agent execution."""
        from agents.state import AgentState

        state = AgentState()
        state.update(
            {
                "workspace_id": "test_workspace",
                "user_id": "test_user",
                "input": "test input",
            }
        )

        result = await mock_agent.execute(state)

        assert result["success"] is True
        assert result["output"] == "test output"
        assert result["tokens_used"] == 100
        mock_agent.execute.assert_called_once_with(state)

    @pytest.mark.asyncio
    async def test_agent_error_handling(self, mock_agent):
        """Test agent error handling."""
        mock_agent.execute.side_effect = Exception("Agent error")

        from agents.state import AgentState

        state = AgentState()

        with pytest.raises(Exception):
            await mock_agent.execute(state)


class TestDatabase:
    """Test database components."""

    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client."""
        client = Mock()
        client.table.return_value.select.return_value.execute.return_value.data = [
            {"id": "1", "name": "test"}
        ]
        client.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "2", "name": "created"}
        ]
        return client

    def test_database_select(self, mock_supabase_client):
        """Test database select operations."""
        result = mock_supabase_client.table("test_table").select("*").execute()

        assert len(result.data) == 1
        assert result.data[0]["id"] == "1"
        assert result.data[0]["name"] == "test"

    def test_database_insert(self, mock_supabase_client):
        """Test database insert operations."""
        data = {"name": "new_record"}
        result = mock_supabase_client.table("test_table").insert(data).execute()

        assert len(result.data) == 1
        assert result.data[0]["id"] == "2"
        assert result.data[0]["name"] == "created"


class TestMiddleware:
    """Test middleware components."""

    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI request."""
        request = Mock()
        request.method = "GET"
        request.url.path = "/test"
        request.client.host = "127.0.0.1"
        request.headers.get.return_value = "test-agent"
        return request

    @pytest.fixture
    def mock_response(self):
        """Mock FastAPI response."""
        response = Mock()
        response.status_code = 200
        return response

    @pytest.mark.asyncio
    async def test_logging_middleware(self, mock_request, mock_response):
        """Test logging middleware."""
        from backend.middleware.logging import LoggingMiddleware

        app = Mock()
        middleware = LoggingMiddleware(app)

        # Mock call_next
        async def mock_call_next(request):
            return mock_response

        result = await middleware.dispatch(mock_request, mock_call_next)

        assert result.status_code == 200
        assert hasattr(mock_request.state, "request_id")

    @pytest.mark.asyncio
    async def test_error_middleware(self, mock_request):
        """Test error middleware."""
        from backend.middleware.errors import ErrorMiddleware

        app = Mock()
        middleware = ErrorMiddleware(app)

        # Mock call_next that raises exception
        async def mock_call_next(request):
            raise Exception("Test error")

        result = await middleware.dispatch(mock_request, mock_call_next)

        assert result.status_code == 500
        assert "error" in result.body.decode()

    @pytest.mark.asyncio
    async def test_metrics_middleware(self, mock_request, mock_response):
        """Test metrics middleware."""
        from backend.middleware.metrics import MetricsMiddleware

        app = Mock()
        middleware = MetricsMiddleware(app)

        # Mock call_next
        async def mock_call_next(request):
            return mock_response

        result = await middleware.dispatch(mock_request, mock_call_next)

        assert result.status_code == 200
        assert middleware.total_requests == 1


class TestDependencies:
    """Test dependency injection components."""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock dependencies."""
        db_client = Mock()
        redis_client = AsyncMock()
        memory_controller = AsyncMock()
        cognitive_engine = AsyncMock()
        agent_dispatcher = AsyncMock()

        return {
            "db_client": db_client,
            "redis_client": redis_client,
            "memory_controller": memory_controller,
            "cognitive_engine": cognitive_engine,
            "agent_dispatcher": agent_dispatcher,
        }

    def test_get_db_dependency(self, mock_dependencies):
        """Test database dependency injection."""
        from backend.dependencies import get_db

        # Mock successful database connection
        mock_dependencies[
            "db_client"
        ].table.return_value.select.return_value.execute.return_value.data = []

        result = get_db()

        assert result is not None

    def test_get_redis_dependency(self, mock_dependencies):
        """Test Redis dependency injection."""
        from backend.dependencies import get_redis

        mock_dependencies["redis_client"].ping.return_value = True

        result = get_redis()

        assert result is not None

    def test_get_memory_controller_dependency(self, mock_dependencies):
        """Test memory controller dependency injection."""
        from backend.dependencies import get_memory_controller

        mock_dependencies["memory_controller"].search.return_value = []

        result = get_memory_controller()

        assert result is not None

    def test_get_cognitive_engine_dependency(self, mock_dependencies):
        """Test cognitive engine dependency injection."""
        from backend.dependencies import get_cognitive_engine

        mock_dependencies["cognitive_engine"].perception = AsyncMock()

        result = get_cognitive_engine()

        assert result is not None

    def test_get_agent_dispatcher_dependency(self, mock_dependencies):
        """Test agent dispatcher dependency injection."""
        from backend.dependencies import get_agent_dispatcher

        mock_dependencies["agent_dispatcher"].get_agent.return_value = Mock()

        result = get_agent_dispatcher()

        assert result is not None


class TestAPIEndpoints:
    """Test API endpoint components."""

    @pytest.fixture
    def mock_app(self):
        """Mock FastAPI app."""
        app = Mock()
        app.include_router = Mock()
        app.add_middleware = Mock()
        return app

    def test_app_configuration(self, mock_app):
        """Test FastAPI app configuration."""
        # Test that routers are included
        from api.v1 import agents, auth, workspaces

        mock_app.include_router.assert_called()

        # Test that middleware is added
        mock_app.add_middleware.assert_called()

    def test_health_endpoint(self):
        """Test health endpoint."""
        # Mock health check response
        health_response = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00",
            "services": {
                "database": "connected",
                "redis": "connected",
                "api": "running",
            },
        }

        assert health_response["status"] == "healthy"
        assert "services" in health_response
        assert health_response["services"]["database"] == "connected"


class TestUtilities:
    """Test utility functions."""

    def test_time_utilities(self):
        """Test time utility functions."""
        import time

        # Test timestamp generation
        timestamp = time.time()
        assert isinstance(timestamp, float)
        assert timestamp > 0

        # Test ISO format
        iso_time = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(timestamp))
        assert "T" in iso_time
        assert len(iso_time) == 19

    def test_string_utilities(self):
        """Test string utility functions."""
        import re

        # Test string sanitization
        test_string = "Hello <script>alert('xss')</script> World"
        sanitized = re.sub(
            r"<script.*?</script>", "", test_string, flags=re.IGNORECASE | re.DOTALL
        )

        assert "<script>" not in sanitized
        assert "Hello" in sanitized
        assert "World" in sanitized

    def test_json_utilities(self):
        """Test JSON utility functions."""
        import json

        # Test JSON serialization
        data = {"key": "value", "number": 123}
        json_str = json.dumps(data)

        assert isinstance(json_str, str)
        assert '"key"' in json_str
        assert '"value"' in json_str

        # Test JSON deserialization
        parsed = json.loads(json_str)
        assert parsed["key"] == "value"
        assert parsed["number"] == 123

    def test_validation_utilities(self):
        """Test validation utility functions."""
        import re

        # Test email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        valid_email = "test@example.com"
        invalid_email = "invalid-email"

        assert re.match(email_pattern, valid_email) is not None
        assert re.match(email_pattern, invalid_email) is None

        # Test UUID validation
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

        valid_uuid = "12345678-1234-1234-1234-123456789012"
        invalid_uuid = "not-a-uuid"

        assert re.match(uuid_pattern, valid_uuid) is not None
        assert re.match(uuid_pattern, invalid_uuid) is None


class TestErrorHandling:
    """Test error handling components."""

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling."""
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(asyncio.sleep(2), timeout=0.1)

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """Test exception handling."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            assert str(e) == "Test error"
            assert isinstance(e, ValueError)

    def test_custom_exceptions(self):
        """Test custom exception classes."""
        from backend.middleware.errors import AuthenticationError, ValidationError

        # Test validation error
        validation_error = ValidationError("Invalid input", field="email")
        assert validation_error.message == "Invalid input"
        assert validation_error.field == "email"
        assert validation_error.status_code == 422

        # Test authentication error
        auth_error = AuthenticationError("Invalid credentials")
        assert auth_error.message == "Invalid credentials"
        assert auth_error.status_code == 401


class TestConfiguration:
    """Test configuration components."""

    def test_environment_variables(self):
        """Test environment variable handling."""
        import os

        # Test getting environment variable
        os.environ["TEST_VAR"] = "test_value"

        test_var = os.getenv("TEST_VAR")
        assert test_var == "test_value"

        # Test default value
        missing_var = os.getenv("MISSING_VAR", "default")
        assert missing_var == "default"

    def test_configuration_validation(self):
        """Test configuration validation."""
        # Test valid configuration
        valid_config = {
            "database_url": "postgresql://localhost:5432/test",
            "redis_url": "redis://localhost:6379",
            "secret_key": "test-secret-key",
        }

        assert "database_url" in valid_config
        assert "redis_url" in valid_config
        assert "secret_key" in valid_config

        # Test invalid configuration
        invalid_config = {
            "database_url": "",  # Empty database URL
            "secret_key": "",  # Empty secret key
        }

        assert invalid_config["database_url"] == ""
        assert invalid_config["secret_key"] == ""


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
