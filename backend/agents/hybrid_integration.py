"""
S.W.A.R.M. Phase 1: Hybrid CrewAI-LangGraph Integration Layer
Unified agent system combining CrewAI and LangGraph capabilities
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union

from crewai import Agent, Crew, Task
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from pydantic import BaseModel

from agents.crewai_adapter import CrewAgentConfig, CrewAIAgentAdapter
from agents.crewai_coordination import AdvancedCrewCoordinator, get_crew_coordinator
from agents.crewai_tasks import CrewTaskManager, TaskPriority
from models.cognitive import AgentMessage, CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.hybrid.integration")


class ExecutionMode(Enum):
    """Execution mode for hybrid system."""

    LANGGRAPH_ONLY = "langgraph_only"
    CREWAI_ONLY = "crewai_only"
    HYBRID_SEQUENTIAL = "hybrid_sequential"
    HYBRID_PARALLEL = "hybrid_parallel"
    ADAPTIVE = "adaptive"


class AgentType(Enum):
    """Type of agent in hybrid system."""

    LANGGRAPH_NODE = "langgraph_node"
    CREWAI_AGENT = "crewai_agent"
    HYBRID_AGENT = "hybrid_agent"


@dataclass
class HybridAgentConfig:
    """Configuration for hybrid agents."""

    agent_id: str
    agent_type: AgentType
    name: str
    role: str
    execution_mode: ExecutionMode = ExecutionMode.ADAPTIVE

    # LangGraph configuration
    langgraph_node_func: Optional[Callable] = None
    langgraph_condition: Optional[Callable] = None

    # CrewAI configuration
    crewai_config: Optional[CrewAgentConfig] = None

    # Hybrid configuration
    fallback_mode: ExecutionMode = ExecutionMode.LANGGRAPH_ONLY
    performance_threshold: float = 0.8
    adaptive_routing: bool = True

    # Common configuration
    tools: Optional[List[Any]] = None
    memory: bool = True
    verbose: bool = False


@dataclass
class HybridWorkflowState:
    """State for hybrid workflow execution."""

    # Core state
    messages: List[AgentMessage] = field(default_factory=list)
    current_step: str = ""
    execution_mode: ExecutionMode = ExecutionMode.ADAPTIVE
    workflow_id: str = ""

    # LangGraph state
    langgraph_state: Dict[str, Any] = field(default_factory=dict)
    langgraph_checkpoint: Optional[str] = None

    # CrewAI state
    crewai_tasks: List[str] = field(default_factory=list)
    crewai_results: Dict[str, str] = field(default_factory=dict)
    active_crews: List[str] = field(default_factory=list)

    # Performance tracking
    performance_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)

    # Adaptive routing
    routing_decisions: List[Dict[str, Any]] = field(default_factory=list)
    mode_switches: List[Dict[str, Any]] = field(default_factory=list)


class HybridAgent:
    """
    Hybrid agent that can operate as both LangGraph node and CrewAI agent.
    Automatically selects optimal execution mode based on context and performance.
    """

    def __init__(self, config: HybridAgentConfig):
        self.config = config
        self.agent_id = config.agent_id
        self.name = config.name
        self.role = config.role

        # Initialize CrewAI adapter if configured
        self.crewai_adapter: Optional[CrewAIAgentAdapter] = None
        if config.crewai_config:
            self.crewai_adapter = CrewAIAgentAdapter(config.crewai_config)

        # Performance tracking
        self.performance_history: List[Dict[str, Any]] = []
        self.current_mode = config.execution_mode

        logger.info(f"Initialized hybrid agent: {self.agent_id}")

    async def execute(
        self, state: HybridWorkflowState, context: Optional[Dict[str, Any]] = None
    ) -> HybridWorkflowState:
        """Execute agent with adaptive mode selection."""
        start_time = datetime.now()

        # Determine optimal execution mode
        execution_mode = await self._select_execution_mode(state, context)

        # Record mode decision
        routing_decision = {
            "agent_id": self.agent_id,
            "timestamp": start_time,
            "selected_mode": execution_mode,
            "reason": self._get_routing_reason(execution_mode, state, context),
        }
        state.routing_decisions.append(routing_decision)

        # Execute in selected mode
        try:
            if execution_mode == ExecutionMode.LANGGRAPH_ONLY:
                state = await self._execute_langgraph(state, context)
            elif execution_mode == ExecutionMode.CREWAI_ONLY:
                state = await self._execute_crewai(state, context)
            elif execution_mode == ExecutionMode.HYBRID_SEQUENTIAL:
                state = await self._execute_hybrid_sequential(state, context)
            elif execution_mode == ExecutionMode.HYBRID_PARALLEL:
                state = await self._execute_hybrid_parallel(state, context)
            else:  # ADAPTIVE
                state = await self._execute_adaptive(state, context)

            # Record performance
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_performance(execution_mode, execution_time, True)

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_performance(execution_mode, execution_time, False, str(e))

            # Try fallback mode
            if self.config.fallback_mode != execution_mode:
                logger.warning(
                    f"Agent {self.agent_id} failed, trying fallback mode {self.config.fallback_mode}"
                )
                state.current_mode = self.config.fallback_mode
                return await self.execute(state, context)
            else:
                logger.error(f"Agent {self.agent_id} failed in fallback mode: {str(e)}")
                raise

        return state

    async def _select_execution_mode(
        self, state: HybridWorkflowState, context: Optional[Dict[str, Any]]
    ) -> ExecutionMode:
        """Select optimal execution mode based on context and performance."""
        if not self.config.adaptive_routing:
            return self.config.execution_mode

        # Analyze current state and context
        if self._should_use_langgraph(state, context):
            return ExecutionMode.LANGGRAPH_ONLY
        elif self._should_use_crewai(state, context):
            return ExecutionMode.CREWAI_ONLY
        elif self._should_use_hybrid_sequential(state, context):
            return ExecutionMode.HYBRID_SEQUENTIAL
        elif self._should_use_hybrid_parallel(state, context):
            return ExecutionMode.HYBRID_PARALLEL
        else:
            return ExecutionMode.ADAPTIVE

    def _should_use_langgraph(
        self, state: HybridWorkflowState, context: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if LangGraph mode is optimal."""
        # Use LangGraph for complex state management and conditional routing
        has_complex_state = len(state.langgraph_state) > 5
        has_conditional_logic = self.config.langgraph_condition is not None
        needs_checkpointing = state.langgraph_checkpoint is not None

        return has_complex_state or has_conditional_logic or needs_checkpointing

    def _should_use_crewai(
        self, state: HybridWorkflowState, context: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if CrewAI mode is optimal."""
        # Use CrewAI for collaborative tasks and agent coordination
        has_multiple_tasks = len(state.crewai_tasks) > 1
        has_active_crews = len(state.active_crews) > 0
        needs_collaboration = context and context.get("requires_collaboration", False)

        return has_multiple_tasks or has_active_crews or needs_collaboration

    def _should_use_hybrid_sequential(
        self, state: HybridWorkflowState, context: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if hybrid sequential mode is optimal."""
        # Use hybrid sequential for step-by-step processing
        has_workflow_steps = len(state.execution_history) > 0
        needs_ordered_processing = context and context.get("ordered_processing", False)

        return has_workflow_steps or needs_ordered_processing

    def _should_use_hybrid_parallel(
        self, state: HybridWorkflowState, context: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if hybrid parallel mode is optimal."""
        # Use hybrid parallel for independent tasks
        has_independent_tasks = context and context.get("independent_tasks", False)
        high_performance_requirement = context and context.get(
            "high_performance", False
        )

        return has_independent_tasks or high_performance_requirement

    def _get_routing_reason(
        self,
        mode: ExecutionMode,
        state: HybridWorkflowState,
        context: Optional[Dict[str, Any]],
    ) -> str:
        """Get reason for routing decision."""
        reasons = {
            ExecutionMode.LANGGRAPH_ONLY: "Complex state management or conditional routing required",
            ExecutionMode.CREWAI_ONLY: "Collaborative tasks or agent coordination needed",
            ExecutionMode.HYBRID_SEQUENTIAL: "Step-by-step processing required",
            ExecutionMode.HYBRID_PARALLEL: "Independent tasks or high performance required",
            ExecutionMode.ADAPTIVE: "Adaptive execution based on real-time analysis",
        }
        return reasons.get(mode, "Default routing")

    async def _execute_langgraph(
        self, state: HybridWorkflowState, context: Optional[Dict[str, Any]]
    ) -> HybridWorkflowState:
        """Execute using LangGraph node function."""
        if not self.config.langgraph_node_func:
            raise ValueError(f"Agent {self.agent_id} missing LangGraph node function")

        # Convert state to LangGraph format
        langgraph_input = self._convert_to_langgraph_state(state, context)

        # Execute LangGraph node
        langgraph_output = await self.config.langgraph_node_func(langgraph_input)

        # Convert back to hybrid state
        state = self._convert_from_langgraph_state(state, langgraph_output)
        state.current_step = f"langgraph_{self.agent_id}"

        return state

    async def _execute_crewai(
        self, state: HybridWorkflowState, context: Optional[Dict[str, Any]]
    ) -> HybridWorkflowState:
        """Execute using CrewAI adapter."""
        if not self.crewai_adapter:
            raise ValueError(f"Agent {self.agent_id} missing CrewAI adapter")

        # Convert state to CrewAI format
        crewai_input = self.crewai_adapter.adapt_to_cognitive_state(
            self._convert_to_cognitive_state(state)
        )

        # Execute CrewAI agent
        crewai_output = self.crewai_adapter.crewai_agent.execute(crewai_input)

        # Convert back to hybrid state
        agent_result = self.crewai_adapter.adapt_from_crewai_result(crewai_output)
        state.messages.extend(agent_result["messages"])
        state.current_step = f"crewai_{self.agent_id}"

        return state

    async def _execute_hybrid_sequential(
        self, state: HybridWorkflowState, context: Optional[Dict[str, Any]]
    ) -> HybridWorkflowState:
        """Execute using hybrid sequential mode."""
        # First execute LangGraph for state management
        if self.config.langgraph_node_func:
            state = await self._execute_langgraph(state, context)

        # Then execute CrewAI for agent tasks
        if self.crewai_adapter:
            state = await self._execute_crewai(state, context)

        state.current_step = f"hybrid_sequential_{self.agent_id}"
        return state

    async def _execute_hybrid_parallel(
        self, state: HybridWorkflowState, context: Optional[Dict[str, Any]]
    ) -> HybridWorkflowState:
        """Execute using hybrid parallel mode."""
        tasks = []

        # Create parallel tasks
        if self.config.langgraph_node_func:
            tasks.append(self._execute_langgraph(state, context))

        if self.crewai_adapter:
            tasks.append(self._execute_crewai(state, context))

        if not tasks:
            raise ValueError(f"Agent {self.agent_id} has no execution capabilities")

        # Execute tasks in parallel
        if len(tasks) == 1:
            state = await tasks[0]
        else:
            # Execute all tasks and merge results
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(
                        f"Parallel task {i} failed for agent {self.agent_id}: {str(result)}"
                    )
                else:
                    state = result

        state.current_step = f"hybrid_parallel_{self.agent_id}"
        return state

    async def _execute_adaptive(
        self, state: HybridWorkflowState, context: Optional[Dict[str, Any]]
    ) -> HybridWorkflowState:
        """Execute using adaptive mode."""
        # Analyze current performance and context
        best_mode = await self._select_execution_mode(state, context)

        # Record mode switch if different from current
        if best_mode != state.execution_mode:
            mode_switch = {
                "agent_id": self.agent_id,
                "timestamp": datetime.now(),
                "from_mode": state.execution_mode,
                "to_mode": best_mode,
                "reason": "Adaptive optimization",
            }
            state.mode_switches.append(mode_switch)
            state.execution_mode = best_mode

        # Execute in best mode
        if best_mode == ExecutionMode.LANGGRAPH_ONLY:
            return await self._execute_langgraph(state, context)
        elif best_mode == ExecutionMode.CREWAI_ONLY:
            return await self._execute_crewai(state, context)
        elif best_mode == ExecutionMode.HYBRID_SEQUENTIAL:
            return await self._execute_hybrid_sequential(state, context)
        elif best_mode == ExecutionMode.HYBRID_PARALLEL:
            return await self._execute_hybrid_parallel(state, context)
        else:
            # Default to sequential if adaptive fails
            return await self._execute_hybrid_sequential(state, context)

    def _convert_to_langgraph_state(
        self, state: HybridWorkflowState, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Convert hybrid state to LangGraph format."""
        langgraph_state = state.langgraph_state.copy()
        langgraph_state.update(
            {
                "messages": [
                    {"role": msg.role, "content": msg.content} for msg in state.messages
                ],
                "current_step": state.current_step,
                "execution_history": state.execution_history,
            }
        )

        if context:
            langgraph_state.update(context)

        return langgraph_state

    def _convert_from_langgraph_state(
        self, state: HybridWorkflowState, langgraph_output: Dict[str, Any]
    ) -> HybridWorkflowState:
        """Convert LangGraph output to hybrid state."""
        # Update LangGraph state
        state.langgraph_state.update(langgraph_output)

        # Convert messages back
        if "messages" in langgraph_output:
            for msg in langgraph_output["messages"]:
                if isinstance(msg, dict):
                    state.messages.append(
                        AgentMessage(
                            role=msg.get("role", "assistant"),
                            content=msg.get("content", ""),
                        )
                    )

        return state

    def _convert_to_cognitive_state(
        self, state: HybridWorkflowState
    ) -> CognitiveIntelligenceState:
        """Convert hybrid state to cognitive state."""
        return {
            "messages": state.messages,
            "current_task": state.current_step,
            "agent_history": state.execution_history,
            "token_usage": {},
        }

    def _record_performance(
        self,
        mode: ExecutionMode,
        execution_time: float,
        success: bool,
        error: Optional[str] = None,
    ):
        """Record performance metrics."""
        performance_record = {
            "timestamp": datetime.now(),
            "mode": mode,
            "execution_time": execution_time,
            "success": success,
            "error": error,
        }
        self.performance_history.append(performance_record)

        # Keep only last 100 records
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this agent."""
        if not self.performance_history:
            return {}

        # Calculate metrics by mode
        mode_metrics = {}
        for record in self.performance_history:
            mode = record["mode"]
            if mode not in mode_metrics:
                mode_metrics[mode] = {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "total_time": 0.0,
                    "errors": [],
                }

            mode_metrics[mode]["total_executions"] += 1
            mode_metrics[mode]["total_time"] += record["execution_time"]

            if record["success"]:
                mode_metrics[mode]["successful_executions"] += 1
            else:
                mode_metrics[mode]["errors"].append(record["error"])

        # Calculate averages and success rates
        for mode, metrics in mode_metrics.items():
            metrics["success_rate"] = (
                metrics["successful_executions"] / metrics["total_executions"]
                if metrics["total_executions"] > 0
                else 0
            )
            metrics["average_time"] = (
                metrics["total_time"] / metrics["total_executions"]
                if metrics["total_executions"] > 0
                else 0
            )

        return {
            "agent_id": self.agent_id,
            "total_executions": len(self.performance_history),
            "mode_metrics": mode_metrics,
            "current_mode": self.current_mode,
        }


class HybridWorkflowManager:
    """
    Manages hybrid workflows combining CrewAI and LangGraph.
    """

    def __init__(self):
        self.hybrid_agents: Dict[str, HybridAgent] = {}
        self.workflows: Dict[str, StateGraph] = {}
        self.crew_coordinator = get_crew_coordinator()
        self.workflow_templates: Dict[str, Dict[str, Any]] = {}

    def register_agent(self, agent: HybridAgent):
        """Register a hybrid agent."""
        self.hybrid_agents[agent.agent_id] = agent
        logger.info(f"Registered hybrid agent: {agent.agent_id}")

    def create_workflow(
        self,
        workflow_id: str,
        agents: List[str],
        workflow_config: Optional[Dict[str, Any]] = None,
    ) -> StateGraph:
        """Create a hybrid workflow with specified agents."""
        if workflow_id in self.workflows:
            raise ValueError(f"Workflow {workflow_id} already exists")

        # Validate agents
        for agent_id in agents:
            if agent_id not in self.hybrid_agents:
                raise ValueError(f"Agent {agent_id} not found")

        # Create LangGraph workflow
        workflow = StateGraph(HybridWorkflowState)

        # Add nodes for each agent
        for agent_id in agents:
            agent = self.hybrid_agents[agent_id]
            workflow.add_node(agent_id, agent.execute)

        # Add edges based on configuration
        if workflow_config and "edges" in workflow_config:
            for edge in workflow_config["edges"]:
                workflow.add_edge(edge["from"], edge["to"])
        else:
            # Default sequential edges
            for i in range(len(agents) - 1):
                workflow.add_edge(agents[i], agents[i + 1])

        # Set entry point
        workflow.set_entry_point(agents[0] if agents else "start")

        # Add conditional edges if specified
        if workflow_config and "conditional_edges" in workflow_config:
            for cond_edge in workflow_config["conditional_edges"]:
                workflow.add_conditional_edges(
                    cond_edge["node"], cond_edge["condition"], cond_edge["mapping"]
                )

        # Compile workflow
        if (
            workflow_config
            and "memory" in workflow_config
            and workflow_config["memory"]
        ):
            memory = MemorySaver()
            compiled_workflow = workflow.compile(checkpointer=memory)
        else:
            compiled_workflow = workflow.compile()

        self.workflows[workflow_id] = compiled_workflow
        logger.info(f"Created hybrid workflow: {workflow_id}")

        return compiled_workflow

    async def execute_workflow(
        self,
        workflow_id: str,
        initial_state: Optional[HybridWorkflowState] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> HybridWorkflowState:
        """Execute a hybrid workflow."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]

        # Prepare initial state
        if initial_state is None:
            initial_state = HybridWorkflowState(workflow_id=workflow_id)
        else:
            initial_state.workflow_id = workflow_id

        # Execute workflow
        result = await workflow.ainvoke(initial_state, config=config)

        logger.info(f"Executed hybrid workflow: {workflow_id}")
        return result

    def get_workflow_metrics(self, workflow_id: str) -> Dict[str, Any]:
        """Get metrics for a workflow."""
        if workflow_id not in self.workflows:
            return {}

        # Aggregate metrics from all agents in the workflow
        workflow_metrics = {
            "workflow_id": workflow_id,
            "agents": [],
            "total_executions": 0,
            "overall_success_rate": 0,
        }

        # This would be populated with actual workflow execution data
        # For now, return agent metrics

        return workflow_metrics

    def create_workflow_template(
        self, template_id: str, template_config: Dict[str, Any]
    ):
        """Create a reusable workflow template."""
        self.workflow_templates[template_id] = template_config
        logger.info(f"Created workflow template: {template_id}")

    def create_workflow_from_template(
        self,
        workflow_id: str,
        template_id: str,
        agent_mappings: Dict[str, str],
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> StateGraph:
        """Create a workflow from a template."""
        if template_id not in self.workflow_templates:
            raise ValueError(f"Template {template_id} not found")

        template = self.workflow_templates[template_id].copy()

        # Map template agents to actual agents
        template_agents = template.get("agents", [])
        actual_agents = [
            agent_mappings.get(agent_id, agent_id) for agent_id in template_agents
        ]

        # Merge custom config
        if custom_config:
            template.update(custom_config)

        return self.create_workflow(workflow_id, actual_agents, template)


# Global workflow manager instance
_workflow_manager: Optional[HybridWorkflowManager] = None


def get_workflow_manager() -> HybridWorkflowManager:
    """Get the global workflow manager instance."""
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = HybridWorkflowManager()
    return _workflow_manager


# Predefined workflow templates
HYBRID_WORKFLOW_TEMPLATES = {
    "research_pipeline": {
        "description": "Research pipeline with data collection and analysis",
        "agents": ["researcher", "analyst", "strategist"],
        "edges": [
            {"from": "researcher", "to": "analyst"},
            {"from": "analyst", "to": "strategist"},
        ],
        "memory": True,
    },
    "creative_campaign": {
        "description": "Creative campaign development workflow",
        "agents": ["creative", "analyst", "strategist"],
        "edges": [
            {"from": "creative", "to": "analyst"},
            {"from": "analyst", "to": "strategist"},
        ],
        "memory": True,
    },
    "problem_solving": {
        "description": "Complex problem solving workflow",
        "agents": ["researcher", "analyst", "creative", "strategist"],
        "conditional_edges": [
            {
                "node": "analyst",
                "condition": "route_based_on_complexity",
                "mapping": {"simple": "strategist", "complex": "creative"},
            },
        ],
        "memory": True,
    },
}
