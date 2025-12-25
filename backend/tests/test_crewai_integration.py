"""
S.W.A.R.M. Phase 1: Comprehensive Testing Suite for CrewAI Integration
Full test coverage for CrewAI agents, tasks, coordination, and hybrid integration
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest
from crewai import Agent as CrewAIAgent
from crewai import Task as CrewAITask
from langgraph.graph import StateGraph
from pydantic import BaseModel

from backend.agents.crewai_adapter import (
    RAPTORFLOW_AGENT_CONFIGS,
    AgentRole,
    CrewAgentConfig,
    CrewAIAgentAdapter,
)
from backend.agents.crewai_coordination import (
    AdvancedCrewCoordinator,
    ConflictType,
    CrewConflictResolver,
    CrewProcess,
    CrewScalingManager,
    get_crew_coordinator,
)
from backend.agents.crewai_tasks import (
    CrewTaskManager,
    EnhancedTask,
    TaskPriority,
    TaskStatus,
)
from backend.agents.hybrid_integration import (
    AgentType,
    ExecutionMode,
    HybridAgent,
    HybridAgentConfig,
    HybridWorkflowManager,
    HybridWorkflowState,
    get_workflow_manager,
)

logger = logging.getLogger(__name__)


class TestCrewAIAgentAdapter:
    """Test suite for CrewAI Agent Adapter."""

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        llm = Mock()
        llm.ainvoke = AsyncMock(return_value=Mock(content="Test response"))
        return llm

    @pytest.fixture
    def agent_config(self):
        """Sample agent configuration for testing."""
        return CrewAgentConfig(
            name="Test Agent",
            role=AgentRole.RESEARCHER,
            goal="Test goal",
            backstory="Test backstory",
            temperature=0.1,
            max_iter=5,
        )

    @pytest.fixture
    def crewai_adapter(self, agent_config, mock_llm):
        """CrewAI adapter fixture."""
        with patch("backend.agents.crewai_adapter.InferenceProvider") as mock_provider:
            mock_provider.get_model.return_value = mock_llm
            return CrewAIAgentAdapter(agent_config)

    def test_crewai_adapter_initialization(self, crewai_adapter):
        """Test CrewAI adapter initialization."""
        assert crewai_adapter.config.name == "Test Agent"
        assert crewai_adapter.config.role == AgentRole.RESEARCHER
        assert crewai_adapter.crewai_agent is not None
        assert crewai_adapter.crewai_agent.role == "researcher"

    def test_adapt_to_cognitive_state(self, crewai_adapter):
        """Test cognitive state adaptation."""
        from backend.models.cognitive import AgentMessage

        state = {
            "messages": [
                AgentMessage(role="human", content="Test message"),
                AgentMessage(role="assistant", content="Test response"),
            ],
            "current_task": "test_task",
        }

        result = crewai_adapter.adapt_to_cognitive_state(state)

        assert "context" in result
        assert "Test message" in result["context"]
        assert "Test response" in result["context"]
        assert result["current_task"] == "test_task"

    def test_adapt_from_crewai_result(self, crewai_adapter):
        """Test CrewAI result adaptation."""
        crewai_result = "Test CrewAI response"

        result = crewai_adapter.adapt_from_crewai_result(crewai_result)

        assert "messages" in result
        assert len(result["messages"]) == 1
        assert result["messages"][0].content == crewai_result
        assert result["messages"][0].role == "researcher"
        assert result["agent_type"] == "crewai"

    def test_predefined_agent_configs(self):
        """Test predefined agent configurations."""
        assert "researcher" in RAPTORFLOW_AGENT_CONFIGS
        assert "strategist" in RAPTORFLOW_AGENT_CONFIGS
        assert "creative" in RAPTORFLOW_AGENT_CONFIGS

        researcher_config = RAPTORFLOW_AGENT_CONFIGS["researcher"]
        assert researcher_config.role == AgentRole.RESEARCHER
        assert researcher_config.temperature == 0.1


class TestCrewTaskManager:
    """Test suite for CrewAI Task Manager."""

    @pytest.fixture
    def mock_agent(self):
        """Mock agent for testing."""
        agent = Mock()
        agent.execute = Mock(return_value="Test task result")
        return agent

    @pytest.fixture
    def task_manager(self):
        """Task manager fixture."""
        return CrewTaskManager(max_concurrent_tasks=3)

    def test_task_manager_initialization(self, task_manager):
        """Test task manager initialization."""
        assert task_manager.max_concurrent_tasks == 3
        assert len(task_manager.tasks) == 0
        assert len(task_manager.task_queue) == 0
        assert len(task_manager.running_tasks) == 0

    def test_create_task(self, task_manager, mock_agent):
        """Test task creation."""
        task_id = task_manager.create_task(
            description="Test task",
            expected_output="Test output",
            agent=mock_agent,
            priority=TaskPriority.HIGH,
        )

        assert task_id in task_manager.tasks
        task = task_manager.get_task(task_id)
        assert task is not None
        assert task.description == "Test task"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.PENDING

    def test_task_dependencies(self, task_manager, mock_agent):
        """Test task dependency management."""
        # Create dependent tasks
        task1_id = task_manager.create_task(
            "Task 1", "Output 1", mock_agent, TaskPriority.HIGH
        )
        task2_id = task_manager.create_task(
            "Task 2",
            "Output 2",
            mock_agent,
            TaskPriority.MEDIUM,
            dependencies=[task1_id],
        )

        task2 = task_manager.get_task(task2_id)
        assert len(task2.dependencies) == 1
        assert task2.dependencies[0].depends_on == task1_id

        # Task 2 should not be ready until Task 1 is completed
        assert not task2.is_ready(task_manager)

        # Complete Task 1
        task1 = task_manager.get_task(task1_id)
        task1.status = TaskStatus.COMPLETED

        # Now Task 2 should be ready
        assert task2.is_ready(task_manager)

    def test_task_priority_queue(self, task_manager, mock_agent):
        """Test priority-based task queue."""
        # Create tasks with different priorities
        low_task_id = task_manager.create_task(
            "Low priority task", "Output", mock_agent, TaskPriority.LOW
        )
        high_task_id = task_manager.create_task(
            "High priority task", "Output", mock_agent, TaskPriority.HIGH
        )
        medium_task_id = task_manager.create_task(
            "Medium priority task", "Output", mock_agent, TaskPriority.MEDIUM
        )

        # Check queue order (high, medium, low)
        assert task_manager.task_queue[0] == high_task_id
        assert task_manager.task_queue[1] == medium_task_id
        assert task_manager.task_queue[2] == low_task_id

    @pytest.mark.asyncio
    async def test_task_execution(self, task_manager, mock_agent):
        """Test task execution."""
        task_id = task_manager.create_task("Test task", "Test output", mock_agent)

        # Start scheduler
        await task_manager.start_scheduler()

        # Wait for task completion
        result = await task_manager.wait_for_task(task_id, timeout=5.0)

        assert result == "Test task result"
        assert task_manager.get_task_status(task_id) == TaskStatus.COMPLETED

        # Stop scheduler
        await task_manager.stop_scheduler()

    def test_task_metrics(self, task_manager, mock_agent):
        """Test task management metrics."""
        # Create some tasks
        task_ids = []
        for i in range(5):
            task_id = task_manager.create_task(f"Task {i}", f"Output {i}", mock_agent)
            task_ids.append(task_id)

        # Simulate some completions
        task_manager.completed_tasks.extend(task_ids[:3])
        task_manager.failed_tasks.extend(task_ids[3:])

        metrics = task_manager.get_metrics()

        assert metrics["total_tasks"] == 5
        assert metrics["completed_tasks"] == 3
        assert metrics["failed_tasks"] == 2
        assert metrics["success_rate"] == 0.6


class TestAdvancedCrewCoordinator:
    """Test suite for Advanced Crew Coordinator."""

    @pytest.fixture
    def mock_agents(self):
        """Mock agents for testing."""
        agents = []
        for i in range(3):
            agent = Mock()
            agent.role = f"agent_{i}"
            agents.append(agent)
        return agents

    @pytest.fixture
    def mock_tasks(self):
        """Mock tasks for testing."""
        tasks = []
        for i in range(3):
            task = Mock()
            task.execute = Mock(return_value=f"Task {i} result")
            tasks.append(task)
        return tasks

    @pytest.fixture
    def crew_coordinator(self):
        """Crew coordinator fixture."""
        return AdvancedCrewCoordinator()

    def test_crew_coordinator_initialization(self, crew_coordinator):
        """Test crew coordinator initialization."""
        assert len(crew_coordinator.active_crews) == 0
        assert len(crew_coordinator.crew_metrics) == 0
        assert crew_coordinator.scaling_manager is not None
        assert crew_coordinator.conflict_resolver is not None

    def test_create_crew(self, crew_coordinator, mock_agents, mock_tasks):
        """Test crew creation."""
        crew_id = "test_crew"

        with patch("crewai.Crew") as mock_crew_class:
            mock_crew = Mock()
            mock_crew.kickoff = Mock(return_value="Crew result")
            mock_crew_class.return_value = mock_crew

            crew = crew_coordinator.create_crew(
                crew_id=crew_id,
                agents=mock_agents,
                tasks=mock_tasks,
                process=CrewProcess.SEQUENTIAL,
            )

            assert crew_id in crew_coordinator.active_crews
            assert crew_id in crew_coordinator.crew_metrics
            assert crew_id in crew_coordinator.task_managers
            assert crew_coordinator.crew_metrics[crew_id].crew_id == crew_id

    @pytest.mark.asyncio
    async def test_execute_crew(self, crew_coordinator, mock_agents, mock_tasks):
        """Test crew execution."""
        crew_id = "test_crew"

        with patch("crewai.Crew") as mock_crew_class:
            mock_crew = Mock()
            mock_crew.kickoff = Mock(return_value="Crew result")
            mock_crew.tasks = mock_tasks
            mock_crew_class.return_value = mock_crew

            crew_coordinator.create_crew(
                crew_id=crew_id, agents=mock_agents, tasks=mock_tasks
            )

            result = await crew_coordinator.execute_crew(crew_id)

            assert result == "Crew result"
            metrics = crew_coordinator.get_crew_metrics(crew_id)
            assert metrics.tasks_completed == len(mock_tasks)

    def test_crew_metrics(self, crew_coordinator):
        """Test crew metrics calculation."""
        crew_id = "test_crew"
        metrics = crew_coordinator.crew_metrics[crew_id] = (
            crew_coordinator.crew_metrics[crew_id]
            or type(
                crew_coordinator.crew_metrics.get(
                    crew_id, type("MockMetrics", (), {})()
                )
            ).__bases__[0]()
        )

        # Simulate some metrics
        metrics.tasks_completed = 8
        metrics.tasks_failed = 2
        metrics.total_execution_time = 100.0

        success_rate = metrics.calculate_success_rate()
        throughput = metrics.calculate_throughput()

        assert success_rate == 0.8
        assert throughput == 0.08

    @pytest.mark.asyncio
    async def test_conflict_resolution(self, crew_coordinator):
        """Test conflict resolution."""
        conflict_type = ConflictType.RESOURCE
        involved_agents = ["agent_1", "agent_2"]
        context = {"agent_priorities": {"agent_1": 10, "agent_2": 5}}

        resolution = await crew_coordinator.handle_conflict(
            "test_crew", conflict_type, involved_agents, context
        )

        assert resolution.conflict_type == conflict_type
        assert resolution.involved_agents == involved_agents
        assert resolution.resolution_strategy == "priority_allocation"
        assert "agent_1" in resolution.outcome  # Higher priority agent


class TestHybridIntegration:
    """Test suite for Hybrid Integration."""

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        llm = Mock()
        llm.ainvoke = AsyncMock(return_value=Mock(content="Test response"))
        return llm

    @pytest.fixture
    def hybrid_agent_config(self):
        """Hybrid agent configuration fixture."""
        return HybridAgentConfig(
            agent_id="test_hybrid_agent",
            agent_type=AgentType.HYBRID_AGENT,
            name="Test Hybrid Agent",
            role="test_role",
            execution_mode=ExecutionMode.ADAPTIVE,
        )

    @pytest.fixture
    def hybrid_agent(self, hybrid_agent_config, mock_llm):
        """Hybrid agent fixture."""
        with patch(
            "backend.agents.hybrid_integration.InferenceProvider"
        ) as mock_provider:
            mock_provider.get_model.return_value = mock_llm
            return HybridAgent(hybrid_agent_config)

    def test_hybrid_agent_initialization(self, hybrid_agent):
        """Test hybrid agent initialization."""
        assert hybrid_agent.agent_id == "test_hybrid_agent"
        assert hybrid_agent.name == hybrid_agent.config.name
        assert hybrid_agent.config.role == "test_role"

    def test_execution_mode_selection(self, hybrid_agent):
        """Test execution mode selection logic."""
        # Test LangGraph preference
        state = HybridWorkflowState()
        state.langgraph_state = {"complex_data": "value"} * 10  # Complex state

        mode = asyncio.run(hybrid_agent._select_execution_mode(state, {}))
        assert mode == ExecutionMode.LANGGRAPH_ONLY

        # Test CrewAI preference
        state.crewai_tasks = ["task1", "task2", "task3"]
        mode = asyncio.run(hybrid_agent._select_execution_mode(state, {}))
        assert mode == ExecutionMode.CREWAI_ONLY

    def test_performance_tracking(self, hybrid_agent):
        """Test performance tracking."""
        # Record some performance data
        hybrid_agent._record_performance(ExecutionMode.LANGGRAPH_ONLY, 1.5, True)
        hybrid_agent._record_performance(
            ExecutionMode.CREWAI_ONLY, 2.0, False, "Test error"
        )

        metrics = hybrid_agent.get_performance_metrics()

        assert metrics["total_executions"] == 2
        assert "langgraph_only" in metrics["mode_metrics"]
        assert "crewai_only" in metrics["mode_metrics"]
        assert metrics["mode_metrics"]["langgraph_only"]["success_rate"] == 1.0
        assert metrics["mode_metrics"]["crewai_only"]["success_rate"] == 0.0

    def test_workflow_manager_initialization(self):
        """Test workflow manager initialization."""
        manager = get_workflow_manager()
        assert len(manager.hybrid_agents) == 0
        assert len(manager.workflows) == 0
        assert len(manager.workflow_templates) == 0

    def test_register_hybrid_agent(self):
        """Test hybrid agent registration."""
        manager = get_workflow_manager()

        config = HybridAgentConfig(
            agent_id="test_agent",
            agent_type=AgentType.HYBRID_AGENT,
            name="Test Agent",
            role="test",
        )

        with patch("backend.agents.hybrid_integration.InferenceProvider"):
            agent = HybridAgent(config)
            manager.register_agent(agent)

            assert "test_agent" in manager.hybrid_agents
            assert manager.hybrid_agents["test_agent"] == agent

    def test_create_workflow(self):
        """Test workflow creation."""
        manager = get_workflow_manager()

        # Register some mock agents
        agent_ids = ["agent1", "agent2"]
        for agent_id in agent_ids:
            config = HybridAgentConfig(
                agent_id=agent_id,
                agent_type=AgentType.HYBRID_AGENT,
                name=f"Agent {agent_id}",
                role="test",
            )
            with patch("backend.agents.hybrid_integration.InferenceProvider"):
                agent = HybridAgent(config)
                manager.register_agent(agent)

        # Create workflow
        workflow = manager.create_workflow(
            workflow_id="test_workflow",
            agents=agent_ids,
            workflow_config={"edges": [{"from": "agent1", "to": "agent2"}]},
        )

        assert "test_workflow" in manager.workflows
        assert workflow is not None

    def test_workflow_templates(self):
        """Test workflow template functionality."""
        manager = get_workflow_manager()

        # Create template
        template_config = {
            "description": "Test template",
            "agents": ["agent1", "agent2"],
            "edges": [{"from": "agent1", "to": "agent2"}],
        }

        manager.create_workflow_template("test_template", template_config)

        assert "test_template" in manager.workflow_templates
        assert (
            manager.workflow_templates["test_template"]["description"]
            == "Test template"
        )


class TestIntegrationScenarios:
    """Integration tests for complete scenarios."""

    @pytest.mark.asyncio
    async def test_complete_crewai_workflow(self):
        """Test complete CrewAI workflow execution."""
        # Create task manager
        task_manager = CrewTaskManager(max_concurrent_tasks=2)

        # Create mock agents
        agents = []
        for i in range(3):
            agent = Mock()
            agent.execute = AsyncMock(return_value=f"Agent {i} result")
            agents.append(agent)

        # Create tasks with dependencies
        task_ids = []
        for i, agent in enumerate(agents):
            dependencies = task_ids[:i] if i > 0 else []
            task_id = task_manager.create_task(
                description=f"Task {i}",
                expected_output=f"Output {i}",
                agent=agent,
                dependencies=dependencies,
            )
            task_ids.append(task_id)

        # Start scheduler and wait for completion
        await task_manager.start_scheduler()
        results = await task_manager.wait_for_all_tasks(timeout=10.0)
        await task_manager.stop_scheduler()

        # Verify results
        assert len(results) == 3
        for task_id in task_ids:
            assert task_id in results
            assert "result" in results[task_id]

    @pytest.mark.asyncio
    async def test_hybrid_execution_scenario(self):
        """Test hybrid execution scenario."""
        # Create hybrid agent
        config = HybridAgentConfig(
            agent_id="hybrid_test",
            agent_type=AgentType.HYBRID_AGENT,
            name="Hybrid Test Agent",
            role="test",
        )

        with patch(
            "backend.agents.hybrid_integration.InferenceProvider"
        ) as mock_provider:
            mock_llm = Mock()
            mock_llm.ainvoke = AsyncMock(return_value=Mock(content="Hybrid result"))
            mock_provider.get_model.return_value = mock_llm

            agent = HybridAgent(config)

            # Create initial state
            state = HybridWorkflowState()
            state.messages = []
            state.execution_mode = ExecutionMode.ADAPTIVE

            # Execute agent
            result_state = await agent.execute(state, {"test_context": "value"})

            # Verify execution
            assert result_state.current_step.startswith("hybrid_")
            assert len(result_state.routing_decisions) > 0
            assert len(agent.performance_history) > 0

    @pytest.mark.asyncio
    async def test_crew_coordination_scenario(self):
        """Test crew coordination scenario."""
        coordinator = get_crew_coordinator()

        # Create mock crew
        with patch("crewai.Crew") as mock_crew_class:
            mock_crew = Mock()
            mock_crew.kickoff = AsyncMock(return_value="Coordinated result")
            mock_crew.tasks = [Mock(), Mock(), Mock()]
            mock_crew_class.return_value = mock_crew

            # Create crew
            crew_id = "coordination_test"
            agents = [Mock() for _ in range(3)]
            tasks = [Mock() for _ in range(3)]

            coordinator.create_crew(
                crew_id=crew_id, agents=agents, tasks=tasks, auto_start_scheduler=True
            )

            # Start coordination loop
            await coordinator.start_coordination_loop()

            # Execute crew
            result = await coordinator.execute_crew(crew_id)

            # Verify coordination
            assert result == "Coordinated result"
            metrics = coordinator.get_all_metrics()
            assert metrics["total_crews"] == 1

            # Stop coordination
            await coordinator.stop_coordination_loop()


# Test data and utilities
class TestDataFactory:
    """Factory for creating test data."""

    @staticmethod
    def create_mock_agent(name: str, role: str) -> Mock:
        """Create a mock agent."""
        agent = Mock()
        agent.name = name
        agent.role = role
        agent.execute = AsyncMock(return_value=f"{name} result")
        return agent

    @staticmethod
    def create_mock_task(description: str, agent: Mock) -> Mock:
        """Create a mock task."""
        task = Mock()
        task.description = description
        task.agent = agent
        task.execute = AsyncMock(return_value=f"{description} result")
        return task

    @staticmethod
    def create_hybrid_state(messages: List[str] = None) -> HybridWorkflowState:
        """Create a hybrid workflow state."""
        state = HybridWorkflowState()
        if messages:
            from backend.models.cognitive import AgentMessage

            state.messages = [
                AgentMessage(role="user", content=msg) for msg in messages
            ]
        return state


# Performance tests
class TestPerformance:
    """Performance tests for CrewAI integration."""

    @pytest.mark.asyncio
    async def test_concurrent_task_execution(self):
        """Test concurrent task execution performance."""
        import time

        task_manager = CrewTaskManager(max_concurrent_tasks=10)

        # Create many tasks
        task_ids = []
        for i in range(20):
            agent = Mock()
            agent.execute = AsyncMock(return_value=f"Task {i}")

            task_id = task_manager.create_task(
                description=f"Task {i}", expected_output=f"Output {i}", agent=agent
            )
            task_ids.append(task_id)

        # Measure execution time
        start_time = time.time()

        await task_manager.start_scheduler()
        results = await task_manager.wait_for_all_tasks(timeout=30.0)
        await task_manager.stop_scheduler()

        execution_time = time.time() - start_time

        # Verify performance
        assert len(results) == 20
        assert execution_time < 10.0  # Should complete in under 10 seconds

        metrics = task_manager.get_metrics()
        assert metrics["success_rate"] == 1.0

    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test memory usage during extended operation."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create and execute many tasks
        task_manager = CrewTaskManager(max_concurrent_tasks=5)

        for batch in range(5):
            task_ids = []
            for i in range(10):
                agent = Mock()
                agent.execute = AsyncMock(return_value=f"Batch {batch} Task {i}")

                task_id = task_manager.create_task(
                    description=f"Batch {batch} Task {i}",
                    expected_output=f"Output {i}",
                    agent=agent,
                )
                task_ids.append(task_id)

            await task_manager.start_scheduler()
            await task_manager.wait_for_all_tasks(timeout=15.0)
            await task_manager.stop_scheduler()

            # Clear completed tasks to test cleanup
            task_manager.completed_tasks.clear()

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024


# Configuration tests
class TestConfiguration:
    """Test configuration and setup."""

    def test_dependency_installation(self):
        """Test that all required dependencies are available."""
        try:
            import crewai
            import crewai_tools
            import langgraph

            assert True
        except ImportError as e:
            pytest.fail(f"Missing dependency: {e}")

    def test_environment_configuration(self):
        """Test environment configuration."""
        # Test that configuration files exist
        import os

        backend_dir = "backend"

        assert os.path.exists(os.path.join(backend_dir, "pyproject.toml"))

        # Test that our created files exist
        agent_files = [
            "crewai_adapter.py",
            "crewai_tasks.py",
            "crewai_coordination.py",
            "hybrid_integration.py",
        ]

        for file in agent_files:
            assert os.path.exists(os.path.join(backend_dir, "agents", file))


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
