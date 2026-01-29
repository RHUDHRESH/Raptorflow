"""
Integration tests for RaptorFlow backend.
Tests end-to-end workflows and system integration.
"""

import asyncio
import time
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock

import pytest

from integration.agents_cognitive import execute_with_cognition
from integration.auth_all import inject_auth_context
from integration.billing_usage import deduct_from_budget
from integration.context_builder import build_full_context
from integration.events_all import wire_all_event_handlers
from integration.memory_database import sync_database_to_memory
from integration.output_pipeline import process_output
from integration.redis_sessions import persist_agent_state, restore_agent_state
from integration.routing_memory import route_with_memory_context
from integration.test_harness import run_integration_tests
from integration.validation import (
    validate_agent_state,
    validate_workspace_consistency,
)


class TestIntegration:
    """Test suite for integration components."""

    @pytest.fixture
    def mock_db_client(self):
        """Mock database client."""
        client = Mock()
        client.table.return_value.select.return_value.execute.return_value.data = [
            {"id": "test"}
        ]
        return client

    @pytest.fixture
    def mock_memory_controller(self):
        """Mock memory controller."""
        controller = AsyncMock()
        controller.search.return_value = []
        controller.store.return_value = "memory_id"
        return controller

    @pytest.fixture
    def mock_cognitive_engine(self):
        """Mock cognitive engine."""
        engine = AsyncMock()
        engine.perception.perceive.return_value = Mock(intent="test", entities=[])
        engine.planning.plan.return_value = Mock(steps=[], total_cost=0.1)
        engine.reflection.reflect.return_value = Mock(quality_score=0.8, approved=True)
        return engine

    @pytest.fixture
    def mock_agent_dispatcher(self):
        """Mock agent dispatcher."""
        dispatcher = AsyncMock()
        agent = AsyncMock()
        agent.execute.return_value = {"success": True, "output": "test"}
        dispatcher.get_agent.return_value = agent
        return dispatcher

    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client."""
        redis_client = AsyncMock()
        redis_client.setex.return_value = True
        redis_client.get.return_value = '{"test": "data"}'
        return redis_client

    @pytest.mark.asyncio
    async def test_routing_memory_integration(
        self, mock_memory_controller, mock_agent_dispatcher
    ):
        """Test routing with memory context integration."""
        # Mock dependencies
        routing_pipeline = AsyncMock()
        routing_pipeline.route.return_value = Mock(
            target_agent="test_agent", memory_context=[], context_used=True
        )

        # Test routing with memory
        result = await route_with_memory_context(
            request="test request",
            workspace_id="test_workspace",
            memory_controller=mock_memory_controller,
            routing_pipeline=routing_pipeline,
        )

        assert result.target_agent == "test_agent"
        assert result.context_used is True
        mock_memory_controller.search.assert_called_once()
        routing_pipeline.route.assert_called_once()

    @pytest.mark.asyncio
    async def test_agents_cognitive_integration(
        self, mock_cognitive_engine, mock_agent_dispatcher
    ):
        """Test agents with cognitive engine integration."""
        # Mock agent state
        state = {
            "workspace_id": "test_workspace",
            "user_id": "test_user",
            "input": "test input",
            "messages": [],
        }

        agent = Mock()
        agent.name = "test_agent"

        # Test cognitive execution
        result = await execute_with_cognition(
            agent=agent, state=state, cognitive_engine=mock_cognitive_engine
        )

        assert "perceived_input" in result
        assert "execution_plan" in result
        assert "reflection_result" in result
        assert result["cognitive_processing"] is True
        assert result["quality_score"] == 0.8

    @pytest.mark.asyncio
    async def test_memory_database_integration(
        self, mock_db_client, mock_memory_controller
    ):
        """Test memory and database integration."""
        # Test database to memory sync
        result = await sync_database_to_memory(
            workspace_id="test_workspace",
            db=mock_db_client,
            memory_controller=mock_memory_controller,
        )

        assert "foundation" in result
        assert "icps" in result
        assert "moves" in result
        assert "campaigns" in result
        assert "cross_module" in result

    @pytest.mark.asyncio
    async def test_auth_integration(self):
        """Test authentication integration."""
        # Mock user data
        user = {
            "id": "test_user",
            "email": "test@example.com",
            "subscription_tier": "pro",
        }
        workspace_id = "test_workspace"

        # Mock agent state
        state = {}

        # Test auth context injection
        result = await inject_auth_context(state, user, workspace_id)

        assert result["user_id"] == "test_user"
        assert result["workspace_id"] == workspace_id
        assert result["authenticated"] is True
        assert "permissions" in result

    @pytest.mark.asyncio
    async def test_redis_sessions_integration(self, mock_redis_client):
        """Test Redis sessions integration."""
        from agents.state import AgentState

        # Mock agent state
        state = AgentState()
        state.update(
            {"workspace_id": "test_workspace", "user_id": "test_user", "test": True}
        )

        session_id = "test_session"

        # Test state persistence
        persist_result = await persist_agent_state(session_id, state, mock_redis_client)
        assert persist_result is True

        # Test state restoration
        restored_state = await restore_agent_state(session_id, mock_redis_client)
        assert restored_state is not None
        assert restored_state["workspace_id"] == "test_workspace"

    @pytest.mark.asyncio
    async def test_events_integration(
        self, mock_memory_controller, mock_cognitive_engine, mock_agent_dispatcher
    ):
        """Test events integration."""
        mock_redis_client = AsyncMock()

        # Test event wiring
        result = await wire_all_event_handlers(
            redis_client=mock_redis_client,
            memory_controller=mock_memory_controller,
            cognitive_engine=mock_cognitive_engine,
            billing_service=Mock(),
        )

        assert result is None  # Function doesn't return value, just wires handlers

    @pytest.mark.asyncio
    async def test_billing_usage_integration(self, mock_redis_client):
        """Test billing and usage integration."""
        # Test budget deduction
        result = await deduct_from_budget(
            workspace_id="test_workspace",
            tokens=100,
            cost=0.5,
            redis_client=mock_redis_client,
            user_id="test_user",
        )

        assert result["success"] is True
        assert result["deducted_tokens"] == 100
        assert result["deducted_cost"] == 0.5
        assert "within_budget" in result

    @pytest.mark.asyncio
    async def test_validation_integration(self, mock_db_client, mock_memory_controller):
        """Test validation integration."""
        # Test workspace consistency validation
        result = await validate_workspace_consistency(
            workspace_id="test_workspace",
            db_client=mock_db_client,
            memory_controller=mock_memory_controller,
        )

        assert "database" in result
        assert "memory" in result
        assert "cross_module" in result
        assert "overall" in result

        # Test agent state validation
        from agents.state import AgentState

        state = AgentState()
        state.update(
            {
                "workspace_id": "test_workspace",
                "user_id": "test_user",
                "session_id": "test_session",
            }
        )

        agent_result = await validate_agent_state(state)
        assert agent_result["valid"] is True
        assert "errors" in agent_result
        assert "warnings" in agent_result

    @pytest.mark.asyncio
    async def test_context_builder_integration(
        self, mock_db_client, mock_memory_controller
    ):
        """Test context builder integration."""
        # Test full context building
        result = await build_full_context(
            workspace_id="test_workspace",
            query="test query",
            db_client=mock_db_client,
            memory_controller=mock_memory_controller,
        )

        assert "workspace_id" in result
        assert "query" in result
        assert "database" in result
        assert "memory" in result
        assert "relevant_items" in result
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_output_pipeline_integration(
        self, mock_db_client, mock_memory_controller, mock_cognitive_engine
    ):
        """Test output pipeline integration."""
        # Test output processing
        result = await process_output(
            output="Test output content",
            workspace_id="test_workspace",
            user_id="test_user",
            agent_name="test_agent",
            output_type="content",
            db_client=mock_db_client,
            memory_controller=mock_memory_controller,
            quality_checker=mock_cognitive_engine,
        )

        assert "output" in result
        assert "quality" in result
        assert "storage" in result
        assert "memory" in result
        assert "events" in result
        assert "summary" in result


class TestWorkflows:
    """Test suite for workflow orchestrators."""

    @pytest.fixture
    def mock_workflow_dependencies(self):
        """Mock workflow dependencies."""
        db_client = Mock()
        memory_controller = AsyncMock()
        cognitive_engine = AsyncMock()
        agent_dispatcher = AsyncMock()

        return {
            "db_client": db_client,
            "memory_controller": memory_controller,
            "cognitive_engine": cognitive_engine,
            "agent_dispatcher": agent_dispatcher,
        }

    @pytest.mark.asyncio
    async def test_onboarding_workflow(self, mock_workflow_dependencies):
        """Test onboarding workflow."""
        from workflows.onboarding import OnboardingWorkflow

        workflow = OnboardingWorkflow(**mock_workflow_dependencies)

        # Mock database responses
        mock_workflow_dependencies[
            "db_client"
        ].table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "test_id"}
        ]
        mock_workflow_dependencies[
            "db_client"
        ].table.return_value.select.return_value.execute.return_value.data = []

        # Test evidence upload step
        result = await workflow.execute_step(
            workspace_id="test_workspace",
            step="evidence_upload",
            data={
                "files": [
                    {"filename": "test.pdf", "file_type": "pdf", "file_size": 1024}
                ]
            },
        )

        assert result["success"] is True
        assert result["step"] == "evidence_upload"
        assert "next_step" in result

    @pytest.mark.asyncio
    async def test_move_workflow(self, mock_workflow_dependencies):
        """Test move workflow."""
        from workflows.move import MoveWorkflow

        workflow = MoveWorkflow(**mock_workflow_dependencies)

        # Mock database responses
        mock_workflow_dependencies[
            "db_client"
        ].table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "test_move_id"}
        ]
        mock_workflow_dependencies[
            "db_client"
        ].table.return_value.select.return_value.execute.return_value.data = []

        # Test move creation
        result = await workflow.create_move(
            workspace_id="test_workspace", goal="Test move goal", move_type="strategic"
        )

        assert result["success"] is True
        assert "move_id" in result
        assert "plan" in result

    @pytest.mark.asyncio
    async def test_content_workflow(self, mock_workflow_dependencies):
        """Test content workflow."""
        from workflows.content import ContentWorkflow

        workflow = ContentWorkflow(**mock_workflow_dependencies)

        # Mock database responses
        mock_workflow_dependencies[
            "db_client"
        ].table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "test_content_id"}
        ]

        # Test content generation
        result = await workflow.generate_content(
            workspace_id="test_workspace",
            request={"content_type": "blog", "title": "Test Blog"},
        )

        assert result["success"] is True
        assert "content_id" in result
        assert "content" in result
        assert "quality_score" in result

    @pytest.mark.asyncio
    async def test_research_workflow(self, mock_workflow_dependencies):
        """Test research workflow."""
        from workflows.research import ResearchWorkflow

        workflow = ResearchWorkflow(**mock_workflow_dependencies)

        # Mock database responses
        mock_workflow_dependencies[
            "db_client"
        ].table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "test_research_id"}
        ]

        # Test research execution
        result = await workflow.conduct_research(
            workspace_id="test_workspace",
            query="market research",
            research_type="market",
        )

        assert result["success"] is True
        assert "research_id" in result
        assert "analysis" in result
        assert "insights" in result

    @pytest.mark.asyncio
    async def test_blackbox_workflow(self, mock_workflow_dependencies):
        """Test blackbox workflow."""
        from workflows.blackbox import BlackboxWorkflow

        workflow = BlackboxWorkflow(**mock_workflow_dependencies)

        # Mock database responses
        mock_workflow_dependencies[
            "db_client"
        ].table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "test_strategy_id"}
        ]

        # Test strategy generation
        result = await workflow.generate_strategy(workspace_id="test_workspace")

        assert result["success"] is True
        assert "strategy_id" in result
        assert "strategy" in result
        assert "risk_assessment" in result

    @pytest.mark.asyncio
    async def test_daily_wins_workflow(self, mock_workflow_dependencies):
        """Test daily wins workflow."""
        from workflows.daily_wins import DailyWinsWorkflow

        workflow = DailyWinsWorkflow(**mock_workflow_dependencies)

        # Mock database responses
        mock_workflow_dependencies[
            "db_client"
        ].table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "test_wins_id"}
        ]

        # Test daily wins generation
        result = await workflow.generate_today(workspace_id="test_workspace")

        assert result["success"] is True
        assert "daily_wins_id" in result
        assert "wins" in result
        assert "context" in result

    @pytest.mark.asyncio
    async def test_campaign_workflow(self, mock_workflow_dependencies):
        """Test campaign workflow."""
        from workflows.campaign import CampaignWorkflow

        workflow = CampaignWorkflow(**mock_workflow_dependencies)

        # Mock database responses
        mock_workflow_dependencies[
            "db_client"
        ].table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "test_campaign_id"}
        ]

        # Test campaign planning
        result = await workflow.plan_campaign(
            workspace_id="test_workspace", goal="Test campaign goal"
        )

        assert result["success"] is True
        assert "campaign_id" in result
        assert "plan" in result
        assert "validation" in result

    @pytest.mark.asyncio
    async def test_approval_workflow(self, mock_workflow_dependencies):
        """Test approval workflow."""
        from workflows.approval import ApprovalWorkflow

        workflow = ApprovalWorkflow(**mock_workflow_dependencies)

        # Mock database responses
        mock_workflow_dependencies[
            "db_client"
        ].table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "test_approval_id"}
        ]

        # Test approval submission
        result = await workflow.submit_for_approval(
            output={
                "workspace_id": "test_workspace",
                "user_id": "test_user",
                "type": "content",
            },
            risk_level="medium",
            reason="Test approval",
        )

        assert result["success"] is True
        assert "gate_id" in result
        assert "approval_id" in result
        assert result["status"] == "pending"

    @pytest.mark.asyncio
    async def test_feedback_workflow(self, mock_workflow_dependencies):
        """Test feedback workflow."""
        from workflows.feedback import FeedbackWorkflow

        workflow = FeedbackWorkflow(**mock_workflow_dependencies)

        # Mock database responses
        mock_workflow_dependencies[
            "db_client"
        ].table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "test_feedback_id"}
        ]

        # Test feedback collection
        result = await workflow.collect_feedback(
            workspace_id="test_workspace",
            feedback_data={"content": "Test feedback", "type": "ui", "rating": 4},
            source="user",
        )

        assert result["success"] is True
        assert "feedback_id" in result
        assert result["source"] == "user"


class TestSystemIntegration:
    """Test suite for complete system integration."""

    @pytest.mark.asyncio
    async def test_integration_test_harness(self):
        """Test integration test harness."""
        # Mock all dependencies
        db_client = Mock()
        redis_client = AsyncMock()
        memory_controller = AsyncMock()
        cognitive_engine = AsyncMock()
        agent_dispatcher = AsyncMock()

        # Mock test results
        db_client.table.return_value.select.return_value.limit.return_value.execute.return_value.data = [
            {"id": "test"}
        ]
        redis_client.ping.return_value = True
        memory_controller.search.return_value = []

        # Test integration tests
        result = await run_integration_tests(
            db_client=db_client,
            redis_client=redis_client,
            memory_controller=memory_controller,
            cognitive_engine=cognitive_engine,
            agent_dispatcher=agent_dispatcher,
        )

        assert "start_time" in result
        assert "tests" in result
        assert "summary" in result
        assert "duration" in result

        # Check that all test categories were run
        assert "database" in result["tests"]
        assert "memory" in result["tests"]
        assert "cognitive" in result["tests"]
        assert "agents" in result["tests"]
        assert "cross_module" in result["tests"]
        assert "redis" in result["tests"]

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # This would test a complete user journey
        # For now, just verify the structure exists

        from workflows.content import ContentWorkflow
        from workflows.move import MoveWorkflow
        from workflows.onboarding import OnboardingWorkflow

        # Verify workflow classes exist
        assert OnboardingWorkflow is not None
        assert MoveWorkflow is not None
        assert ContentWorkflow is not None

    @pytest.mark.asyncio
    async def test_system_health_check(self):
        """Test system health check integration."""
        # Mock dependencies
        db_client = Mock()
        redis_client = AsyncMock()
        memory_controller = AsyncMock()

        # Mock healthy responses
        db_client.table.return_value.select.return_value.limit.return_value.execute.return_value.data = [
            {"id": "test"}
        ]
        redis_client.ping.return_value = True
        memory_controller.search.return_value = []

        # Test health check
        from integration.test_harness import run_quick_integration_check

        result = await run_quick_integration_check(
            db_client=db_client,
            redis_client=redis_client,
            memory_controller=memory_controller,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling across integration points."""
        # Mock failing dependencies
        db_client = Mock()
        db_client.table.return_value.select.return_value.execute.side_effect = (
            Exception("Database error")
        )

        memory_controller = AsyncMock()
        memory_controller.search.side_effect = Exception("Memory error")

        # Test that errors are handled gracefully
        from integration.validation import validate_workspace_consistency

        result = await validate_workspace_consistency(
            workspace_id="test_workspace",
            db_client=db_client,
            memory_controller=memory_controller,
        )

        assert result["overall"]["valid"] is False
        assert "error" in result["overall"]

    @pytest.mark.asyncio
    async def test_performance_integration(self):
        """Test performance across integration points."""
        # Mock dependencies with timing
        db_client = Mock()
        db_client.table.return_value.select.return_value.execute.return_value.data = [
            {"id": "test"}
        ]

        memory_controller = AsyncMock()
        memory_controller.search.return_value = []

        # Test performance of context building
        from integration.context_builder import ContextBuilder

        builder = ContextBuilder(db_client, memory_controller)

        start_time = time.time()
        result = await builder.build_context(
            workspace_id="test_workspace", query="test query"
        )
        end_time = time.time()

        assert "workspace_id" in result
        assert "relevant_items" in result
        assert (end_time - start_time) < 1.0  # Should complete within 1 second


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
