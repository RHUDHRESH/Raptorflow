"""
Tests for LangGraph Integration Layer

Tests the ToolContext contracts, tool wrappers, and agent run management.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from backend.agents.tooling.contracts import ToolContext, from_request_data, bind_context_to_logger
from backend.agents.tooling.langgraph_integration import (
    make_model_dispatch_tool,
    make_bus_publish_tool,
    start_agent_run,
    complete_agent_run,
    build_tool_context_from_run,
    require_langgraph,
    langgraph_available,
)


class TestToolContext:
    """Test ToolContext creation and helpers."""

    def test_tool_context_creation(self):
        """Test basic ToolContext creation."""
        ctx = ToolContext(
            workspace_id="ws-123",
            actor_user_id="user-456",
            agent_id="agent-789",
            agent_run_id="run-101",
            correlation_id="corr-202",
        )

        assert ctx.workspace_id == "ws-123"
        assert ctx.actor_user_id == "user-456"
        assert ctx.agent_id == "agent-789"
        assert ctx.agent_run_id == "run-101"
        assert ctx.correlation_id == "corr-202"
        assert ctx.extra == {}

    def test_from_request_data(self):
        """Test context building from request data."""
        ctx = from_request_data(
            workspace_id="ws-123",
            actor_user_id="user-456",
            correlation_id="corr-202",
        )

        assert ctx.workspace_id == "ws-123"
        assert ctx.actor_user_id == "user-456"
        assert ctx.correlation_id == "corr-202"
        assert ctx.agent_id is None
        assert ctx.agent_run_id is None

    def test_bind_context_to_logger(self):
        """Test logger binding with context."""
        ctx = ToolContext(
            workspace_id="ws-123",
            agent_id="agent-789",
            agent_run_id="run-101",
            correlation_id="corr-202",
        )

        mock_logger = MagicMock()
        bound_logger = bind_context_to_logger(ctx, mock_logger)

        # Should call bind with the context fields
        mock_logger.bind.assert_called_once_with(
            workspace_id="ws-123",
            agent_id="agent-789",
            agent_run_id="run-101",
            correlation_id="corr-202",
        )
        assert bound_logger == mock_logger.bind.return_value


@pytest.mark.skipif(not langgraph_available(), reason="LangGraph not available")
class TestLangGraphTools:
    """Test LangGraph tool wrappers."""

    @pytest.fixture
    def sample_context(self):
        """Sample ToolContext dict for tools."""
        return {
            "workspace_id": "ws-123",
            "actor_user_id": "user-456",
            "agent_id": "agent-789",
            "agent_run_id": "run-101",
            "correlation_id": "corr-202",
            "extra": {},
        }

    @pytest.fixture
    async def mock_dispatcher(self):
        """Mock ModelDispatcher for testing."""
        from backend.services.model_dispatcher import ModelDispatchResponse

        dispatcher = AsyncMock()
        dispatcher.dispatch.return_value = ModelDispatchResponse(
            raw_response="Hello world",
            model="fast",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
            estimated_cost_usd=0.1,
            cached=False,
        )
        return dispatcher

    @pytest.fixture
    async def mock_bus(self):
        """Mock RaptorBus for testing."""
        bus = AsyncMock()
        return bus

    @patch('backend.agents.tooling.langgraph_integration.log_tool_call', new_callable=AsyncMock)
    @patch('backend.agents.tooling.langgraph_integration.log_tool_completion', new_callable=AsyncMock)
    async def test_model_dispatch_tool_success(self, mock_log_completion, mock_log_call, mock_dispatcher, sample_context):
        """Test model dispatch tool with successful execution."""
        tool = make_model_dispatch_tool(mock_dispatcher)

        result = await tool.invoke({
            "ctx": sample_context,
            "model": "fast",
            "messages": [{"role": "user", "content": "Hello"}],
        })

        # Verify dispatcher called correctly
        mock_dispatcher.dispatch.assert_called_once()
        call_args = mock_dispatcher.dispatch.call_args[0][0]  # First arg is the request
        assert call_args.workspace_id == "ws-123"
        assert call_args.model == "fast"
        assert call_args.messages == [{"role": "user", "content": "Hello"}]
        assert call_args.agent_id == "agent-789"
        assert call_args.agent_run_id == "run-101"

        # Verify audit logging
        mock_log_call.assert_called_once_with(
            workspace_id="ws-123",
            tool_name="model_dispatch",
            agent_id="agent-789",
            parameters={
                "model": "fast",
                "message_count": 1,
                "cache_key": None,
                "temperature": None,
                "max_tokens": None,
            },
        )

        mock_log_completion.assert_called_once()
        completion_args = mock_log_completion.call_args[1]
        assert completion_args["success"] is True
        assert "Generated 30 tokens" in completion_args["result_summary"]

        # Verify result
        assert result["response"] == "Hello world"
        assert result["model"] == "fast"
        assert result["total_tokens"] == 30
        assert result["estimated_cost_usd"] == 0.1

    @patch('backend.agents.tooling.langgraph_integration.log_tool_call', new_callable=AsyncMock)
    @patch('backend.agents.tooling.langgraph_integration.log_tool_completion', new_callable=AsyncMock)
    async def test_model_dispatch_tool_failure(self, mock_log_completion, mock_log_call, mock_dispatcher, sample_context):
        """Test model dispatch tool with failure."""
        mock_dispatcher.dispatch.side_effect = Exception("Model failed")
        tool = make_model_dispatch_tool(mock_dispatcher)

        with pytest.raises(Exception, match="Model failed"):
            await tool.invoke({
                "ctx": sample_context,
                "model": "fast",
                "messages": [{"role": "user", "content": "Hello"}],
            })

        # Verify failure logging
        mock_log_completion.assert_called_once()
        assert mock_log_completion.call_args[1]["success"] is False
        assert "Model dispatch failed" in mock_log_completion.call_args[1]["result_summary"]

    @patch('backend.agents.tooling.langgraph_integration.get_bus', new_callable=AsyncMock)
    @patch('backend.agents.tooling.langgraph_integration.log_tool_call', new_callable=AsyncMock)
    @patch('backend.agents.tooling.langgraph_integration.log_tool_completion', new_callable=AsyncMock)
    async def test_bus_publish_tool_success(self, mock_log_completion, mock_log_call, mock_get_bus, sample_context):
        """Test bus publish tool with successful execution."""
        mock_bus = AsyncMock()
        mock_get_bus.return_value = mock_bus

        tool = make_bus_publish_tool()

        result = await tool.invoke({
            "ctx": sample_context,
            "event_type": "test.event",
            "payload": {"key": "value"},
        })

        # Verify bus called correctly
        mock_bus.publish.assert_called_once_with(
            event_type="test.event",
            payload={"key": "value"},
            workspace_id="ws-123",
            correlation_id="corr-202",
        )

        # Verify audit logging
        mock_log_call.assert_called_once_with(
            workspace_id="ws-123",
            tool_name="raptor_bus.publish",
            agent_id="agent-789",
            parameters={
                "event_type": "test.event",
                "payload_keys": ["key"],
            },
        )

        mock_log_completion.assert_called_once_with(
            workspace_id="ws-123",
            tool_name="raptor_bus.publish",
            agent_id="agent-789",
            result_summary="Published test.event event",
            success=True,
        )

        # Verify result
        assert result["status"] == "published"
        assert result["event_type"] == "test.event"
        assert result["workspace_id"] == "ws-123"

    @patch('backend.agents.tooling.langgraph_integration.get_bus', new_callable=AsyncMock)
    @patch('backend.agents.tooling.langgraph_integration.log_tool_call', new_callable=AsyncMock)
    @patch('backend.agents.tooling.langgraph_integration.log_tool_completion', new_callable=AsyncMock)
    async def test_bus_publish_tool_failure(self, mock_log_completion, mock_log_call, mock_get_bus, sample_context):
        """Test bus publish tool with failure."""
        mock_bus = AsyncMock()
        mock_bus.publish.side_effect = Exception("Bus failed")
        mock_get_bus.return_value = mock_bus

        tool = make_bus_publish_tool()

        with pytest.raises(Exception, match="Bus failed"):
            await tool.invoke({
                "ctx": sample_context,
                "event_type": "test.event",
                "payload": {"key": "value"},
            })

        # Verify failure logging
        mock_log_completion.assert_called_once()
        assert mock_log_completion.call_args[1]["success"] is False
        assert "Bus publish failed" in mock_log_completion.call_args[1]["result_summary"]


class TestAgentRunManagement:
    """Test agent run management functions."""

    @patch('backend.agents.tooling.langgraph_integration.supabase_client')
    async def test_start_agent_run(self, mock_supabase):
        """Test starting an agent run."""
        mock_supabase.insert = AsyncMock()

        run_id = await start_agent_run(
            workspace_id="ws-123",
            agent_id="agent-789",
            actor_user_id="user-456",
            run_name="Test Run",
        )

        # Should return a UUID string
        assert isinstance(run_id, str)
        assert len(run_id) > 0

        # Should insert correct data
        mock_supabase.insert.assert_called_once()
        call_args = mock_supabase.insert.call_args
        assert call_args[0][0] == "agent_runs"  # table
        run_data = call_args[0][1]  # data dict
        assert run_data["workspace_id"] == "ws-123"
        assert run_data["agent_id"] == "agent-789"
        assert run_data["actor_user_id"] == "user-456"
        assert run_data["run_name"] == "Test Run"
        assert run_data["status"] == "running"
        assert "started_at" in run_data

    @patch('backend.agents.tooling.langgraph_integration.supabase_client')
    async def test_complete_agent_run(self, mock_supabase):
        """Test completing an agent run."""
        mock_supabase.update = AsyncMock()

        await complete_agent_run(
            agent_run_id="run-123",
            status="completed",
            result_summary="Success!",
            error_message=None,
        )

        # Should update with correct data
        mock_supabase.update.assert_called_once()
        call_args = mock_supabase.update.call_args
        assert call_args[0][0] == "agent_runs"  # table
        update_data = call_args[0][1]  # data dict
        assert update_data["status"] == "completed"
        assert update_data["result_summary"] == "Success!"
        assert "completed_at" in update_data
        # error_message should not be in data if None
        assert "error_message" not in update_data

        filters = call_args[0][2]  # filters
        assert filters == {"id": "run-123"}

    @patch('backend.agents.tooling.langgraph_integration.supabase_client')
    async def test_complete_agent_run_with_error(self, mock_supabase):
        """Test completing an agent run with error."""
        mock_supabase.update = AsyncMock()

        await complete_agent_run(
            agent_run_id="run-123",
            status="failed",
            result_summary=None,
            error_message="Something went wrong",
        )

        update_data = mock_supabase.update.call_args[0][1]
        assert update_data["status"] == "failed"
        assert update_data["error_message"] == "Something went wrong"
        assert "result_summary" not in update_data  # Should be omitted when None

    @patch('backend.agents.tooling.langgraph_integration.supabase_client')
    async def test_build_tool_context_from_run(self, mock_supabase):
        """Test building ToolContext from existing run."""
        # Mock the select response
        mock_result = MagicMock()
        mock_result.data = [{
            "workspace_id": "ws-123",
            "agent_id": "agent-789",
            "actor_user_id": "user-456",
        }]
        mock_supabase.select = AsyncMock(return_value=mock_result)

        ctx = await build_tool_context_from_run("run-101")

        # Verify query
        mock_supabase.select.assert_called_once_with(
            "agent_runs",
            ["workspace_id", "agent_id", "actor_user_id"],
            filters={"id": "run-101"}
        )

        # Verify context
        assert ctx.workspace_id == "ws-123"
        assert ctx.agent_id == "agent-789"
        assert ctx.agent_run_id == "run-101"
        assert ctx.actor_user_id == "user-456"
        assert ctx.correlation_id is None  # Depending on context var

    @patch('backend.agents.tooling.langgraph_integration.supabase_client')
    async def test_build_tool_context_run_not_found(self, mock_supabase):
        """Test building ToolContext when run not found."""
        mock_result = MagicMock()
        mock_result.data = []
        mock_supabase.select = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="Agent run not found: run-999"):
            await build_tool_context_from_run("run-999")
