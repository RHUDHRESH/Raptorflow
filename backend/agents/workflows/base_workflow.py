"""
Base workflow class for LangGraph integration.
Provides the foundation for creating and managing agent workflows.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

try:
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import END, StateGraph

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available. Workflow functionality will be limited.")

from ..base import BaseAgent
from ..exceptions import ValidationError, WorkflowError
from ..state import AgentState

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeType(Enum):
    """Node types in workflow graph."""

    AGENT = "agent"
    CONDITION = "condition"
    ACTION = "action"
    PARALLEL = "parallel"
    MERGE = "merge"


@dataclass
class WorkflowNode:
    """Individual node in workflow graph."""

    node_id: str
    node_type: NodeType
    name: str
    description: str
    agent_class: Optional[type] = None
    agent_name: Optional[str] = None
    condition_function: Optional[Callable] = None
    action_function: Optional[Callable] = None
    input_mapping: Optional[Dict[str, str]] = None
    output_mapping: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEdge:
    """Edge connecting workflow nodes."""

    from_node: str
    to_node: str
    condition: Optional[Callable] = None
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """Workflow execution state."""

    workflow_id: str
    status: WorkflowStatus
    current_node: Optional[str] = None
    completed_nodes: List[str] = field(default_factory=list)
    failed_nodes: List[str] = field(default_factory=list)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    agent_states: Dict[str, AgentState] = field(default_factory=dict)
    shared_data: Dict[str, Any] = field(default_factory=dict)
    error_log: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowConfig:
    """Workflow configuration."""

    workflow_id: str
    name: str
    description: str
    version: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    entry_point: str
    exit_points: List[str]
    checkpoint_enabled: bool = True
    timeout: Optional[int] = None
    retry_policy: str = "exponential"
    max_execution_time: int = 3600  # 1 hour
    parallel_execution: bool = True
    error_handling: str = "continue"
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseWorkflow(ABC):
    """Base class for all agent workflows."""

    def __init__(self):
        self.config: Optional[WorkflowConfig] = None
        self.state: Optional[WorkflowState] = None
        self.graph: Optional[Any] = None
        self.checkpointer: Optional[Any] = None
        self.agent_registry: Optional[Dict[str, BaseAgent]] = None
        self.is_initialized = False

        if not LANGGRAPH_AVAILABLE:
            logger.warning(
                "LangGraph not available. Workflow functionality will be limited."
            )

    @abstractmethod
    def define_workflow(self) -> WorkflowConfig:
        """Define the workflow structure. Must be implemented by subclasses."""
        pass

    def initialize(self, agent_registry: Dict[str, BaseAgent]) -> bool:
        """Initialize the workflow with agent registry."""
        try:
            self.agent_registry = agent_registry

            # Define workflow structure
            self.config = self.define_workflow()

            # Validate configuration
            self._validate_config()

            # Build LangGraph if available
            if LANGGRAPH_AVAILABLE:
                self._build_graph()

            # Initialize state
            self.state = WorkflowState(
                workflow_id=self.config.workflow_id, status=WorkflowStatus.PENDING
            )

            # Setup checkpointing if enabled
            if self.config.checkpoint_enabled and LANGGRAPH_AVAILABLE:
                self.checkpointer = MemorySaver()

            self.is_initialized = True
            logger.info(f"Workflow {self.config.workflow_id} initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize workflow: {e}")
            return False

    def _validate_config(self):
        """Validate workflow configuration."""
        if not self.config:
            raise WorkflowError("Workflow configuration is required")

        if not self.config.nodes:
            raise WorkflowError("Workflow must have at least one node")

        if not self.config.entry_point:
            raise WorkflowError("Workflow must have an entry point")

        # Validate entry point exists
        entry_node_exists = any(
            node.node_id == self.config.entry_point for node in self.config.nodes
        )
        if not entry_node_exists:
            raise WorkflowError(
                f"Entry point {self.config.entry_point} not found in nodes"
            )

        # Validate all nodes referenced in edges exist
        node_ids = {node.node_id for node in self.config.nodes}
        for edge in self.config.edges:
            if edge.from_node not in node_ids:
                raise WorkflowError(
                    f"Edge from_node {edge.from_node} not found in nodes"
                )
            if edge.to_node not in node_ids:
                raise WorkflowError(f"Edge to_node {edge.to_node} not found in nodes")

        # Validate agent references
        for node in self.config.nodes:
            if node.node_type == NodeType.AGENT:
                if not node.agent_name and not node.agent_class:
                    raise WorkflowError(
                        f"Agent node {node.node_id} must specify agent_name or agent_class"
                    )

                if node.agent_name and node.agent_name not in self.agent_registry:
                    raise WorkflowError(
                        f"Agent {node.agent_name} not found in registry"
                    )

    def _build_graph(self):
        """Build LangGraph from configuration."""
        if not LANGGRAPH_AVAILABLE:
            return

        try:
            # Create state graph
            self.graph = StateGraph(dict)

            # Add nodes
            for node in self.config.nodes:
                self._add_node_to_graph(node)

            # Add edges
            for edge in self.config.edges:
                self._add_edge_to_graph(edge)

            # Set entry point
            self.graph.set_entry_point(self.config.entry_point)

            # Set exit points
            for exit_point in self.config.exit_points:
                self.graph.add_edge(exit_point, END)

            # Compile graph
            self.graph.compile()

            logger.info(
                f"LangGraph built successfully for workflow {self.config.workflow_id}"
            )

        except Exception as e:
            logger.error(f"Failed to build LangGraph: {e}")
            raise WorkflowError(f"Failed to build LangGraph: {str(e)}")

    def _add_node_to_graph(self, node: WorkflowNode):
        """Add a node to the LangGraph."""
        if not LANGGRAPH_AVAILABLE or not self.graph:
            return

        try:
            if node.node_type == NodeType.AGENT:
                # Create agent node function
                def agent_node_function(state: Dict[str, Any]) -> Dict[str, Any]:
                    return self._execute_agent_node(state, node)

                self.graph.add_node(node.node_id, agent_node_function)

            elif node.node_type == NodeType.CONDITION:
                # Create condition node function
                def condition_node_function(state: Dict[str, Any]) -> str:
                    return self._execute_condition_node(state, node)

                self.graph.add_node(node.node_id, condition_node_function)

            elif node.node_type == NodeType.ACTION:
                # Create action node function
                def action_node_function(state: Dict[str, Any]) -> Dict[str, Any]:
                    return self._execute_action_node(state, node)

                self.graph.add_node(node.node_id, action_node_function)

            elif node.node_type == NodeType.PARALLEL:
                # Create parallel node function
                def parallel_node_function(state: Dict[str, Any]) -> Dict[str, Any]:
                    return self._execute_parallel_node(state, node)

                self.graph.add_node(node.node_id, parallel_node_function)

            elif node.node_type == NodeType.MERGE:
                # Create merge node function
                def merge_node_function(state: Dict[str, Any]) -> Dict[str, Any]:
                    return self._execute_merge_node(state, node)

                self.graph.add_node(node.node_id, merge_node_function)

            else:
                raise WorkflowError(f"Unsupported node type: {node.node_type}")

        except Exception as e:
            logger.error(f"Failed to add node {node.node_id} to graph: {e}")
            raise WorkflowError(f"Failed to add node {node.node_id} to graph: {str(e)}")

    def _add_edge_to_graph(self, edge: WorkflowEdge):
        """Add an edge to the LangGraph."""
        if not LANGGRAPH_AVAILABLE or not self.graph:
            return

        try:
            if edge.condition:
                # Conditional edge
                def conditional_edge_function(state: Dict[str, Any]) -> str:
                    return edge.to_node if edge.condition(state) else edge.from_node

                self.graph.add_conditional_edges(
                    edge.from_node, conditional_edge_function
                )
            else:
                # Regular edge
                self.graph.add_edge(edge.from_node, edge.to_node)

        except Exception as e:
            logger.error(
                f"Failed to add edge {edge.from_node} -> {edge.to_node} to graph: {e}"
            )
            raise WorkflowError(
                f"Failed to add edge {edge.from_node} -> {edge.to_node} to graph: {str(e)}"
            )

    async def execute(self, initial_state: Dict[str, Any]) -> WorkflowState:
        """Execute the workflow."""
        if not self.is_initialized:
            raise WorkflowError("Workflow must be initialized before execution")

        try:
            # Reset state
            self.state = WorkflowState(
                workflow_id=self.config.workflow_id,
                status=WorkflowStatus.RUNNING,
                start_time=datetime.now(),
                shared_data=initial_state.copy(),
            )

            # Execute using LangGraph if available
            if LANGGRAPH_AVAILABLE and self.graph:
                return await self._execute_with_langgraph()
            else:
                return await self._execute_fallback()

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            self.state.status = WorkflowStatus.FAILED
            self.state.error_log.append(str(e))
            self.state.end_time = datetime.now()
            raise WorkflowError(f"Workflow execution failed: {str(e)}")

    async def _execute_with_langgraph(self) -> WorkflowState:
        """Execute workflow using LangGraph."""
        if not self.graph:
            raise WorkflowError("LangGraph not built")

        try:
            # Prepare initial state for LangGraph
            langgraph_state = {
                "workflow_id": self.config.workflow_id,
                "shared_data": self.state.shared_data.copy(),
                "agent_states": self.state.agent_states.copy(),
                "execution_history": self.state.execution_history.copy(),
            }

            # Execute with checkpointing if enabled
            if self.checkpointer:
                config = {"configurable": {"checkpointer": self.checkpointer}}
                result = await self.graph.ainvoke(langgraph_state, config=config)
            else:
                result = await self.graph.ainvoke(langgraph_state)

            # Update state with results
            self.state.shared_data.update(result.get("shared_data", {}))
            self.state.agent_states.update(result.get("agent_states", {}))
            self.state.execution_history.extend(result.get("execution_history", []))

            # Mark as completed
            self.state.status = WorkflowStatus.COMPLETED
            self.state.end_time = datetime.now()

            return self.state

        except Exception as e:
            logger.error(f"LangGraph execution failed: {e}")
            self.state.status = WorkflowStatus.FAILED
            self.state.error_log.append(str(e))
            self.state.end_time = datetime.now()
            raise

    async def _execute_fallback(self) -> WorkflowState:
        """Fallback execution without LangGraph."""
        try:
            # Simple sequential execution
            current_node = self.config.entry_point
            visited_nodes = set()

            while current_node and current_node not in visited_nodes:
                visited_nodes.add(current_node)

                # Find node
                node = next(
                    (n for n in self.config.nodes if n.node_id == current_node), None
                )
                if not node:
                    break

                # Execute node
                await self._execute_node(node)

                # Find next node
                next_edges = [
                    e for e in self.config.edges if e.from_node == current_node
                ]
                if next_edges:
                    current_node = next_edges[0].to_node
                else:
                    break

            self.state.status = WorkflowStatus.COMPLETED
            self.state.end_time = datetime.now()

            return self.state

        except Exception as e:
            logger.error(f"Fallback execution failed: {e}")
            self.state.status = WorkflowStatus.FAILED
            self.state.error_log.append(str(e))
            self.state.end_time = datetime.now()
            raise

    async def _execute_node(self, node: WorkflowNode):
        """Execute a single workflow node."""
        try:
            self.state.current_node = node.node_id

            if node.node_type == NodeType.AGENT:
                await self._execute_agent_node(self.state.shared_data, node)
            elif node.node_type == NodeType.CONDITION:
                await self._execute_condition_node(self.state.shared_data, node)
            elif node.node_type == NodeType.ACTION:
                await self._execute_action_node(self.state.shared_data, node)
            elif node.node_type == NodeType.PARALLEL:
                await self._execute_parallel_node(self.state.shared_data, node)
            elif node.node_type == NodeType.MERGE:
                await self._execute_merge_node(self.state.shared_data, node)

            self.state.completed_nodes.append(node.node_id)

        except Exception as e:
            logger.error(f"Node execution failed for {node.node_id}: {e}")
            self.state.failed_nodes.append(node.node_id)
            self.state.error_log.append(f"Node {node.node_id} failed: {str(e)}")

            # Handle retry logic
            if node.retry_count < node.max_retries:
                node.retry_count += 1
                await asyncio.sleep(2**node.retry_count)  # Exponential backoff
                await self._execute_node(node)
            else:
                raise

    def _execute_agent_node(
        self, state: Dict[str, Any], node: WorkflowNode
    ) -> Dict[str, Any]:
        """Execute an agent node."""
        try:
            # Get agent
            agent = None
            if node.agent_name:
                agent = self.agent_registry.get(node.agent_name)
            elif node.agent_class:
                agent = node.agent_class()

            if not agent:
                raise WorkflowError(f"Agent not found for node {node.node_id}")

            # Prepare agent state
            agent_state = AgentState(
                workspace_id=state.get("workspace_id", ""),
                user_id=state.get("user_id", ""),
                session_id=state.get(
                    "session_id", f"workflow_{self.config.workflow_id}"
                ),
                messages=[],
                context=state.get("context", {}),
                metadata=state.get("metadata", {}),
            )

            # Map input if specified
            if node.input_mapping:
                mapped_data = {}
                for state_key, agent_key in node.input_mapping.items():
                    mapped_data[agent_key] = state.get(state_key)
                agent_state.update(mapped_data)

            # Execute agent
            result_state = asyncio.run(agent.execute(agent_state))

            # Map output if specified
            if node.output_mapping:
                mapped_result = {}
                for agent_key, state_key in node.output_mapping.items():
                    mapped_result[state_key] = result_state.get(agent_key)
                state.update(mapped_result)
            else:
                # Update with all agent state data
                state.update(result_state)

            # Store agent state
            self.state.agent_states[node.node_id] = result_state

            # Add to execution history
            self.state.execution_history.append(
                {
                    "node_id": node.node_id,
                    "node_type": node.node_type.value,
                    "agent": node.agent_name,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                }
            )

            return state

        except Exception as e:
            logger.error(f"Agent node execution failed: {e}")
            raise

    def _execute_condition_node(self, state: Dict[str, Any], node: WorkflowNode) -> str:
        """Execute a condition node."""
        try:
            if not node.condition_function:
                raise WorkflowError(
                    f"Condition node {node.node_id} has no condition function"
                )

            result = node.condition_function(state)

            # Add to execution history
            self.state.execution_history.append(
                {
                    "node_id": node.node_id,
                    "node_type": node.node_type.value,
                    "condition_result": result,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                }
            )

            return result

        except Exception as e:
            logger.error(f"Condition node execution failed: {e}")
            raise

    def _execute_action_node(
        self, state: Dict[str, Any], node: WorkflowNode
    ) -> Dict[str, Any]:
        """Execute an action node."""
        try:
            if not node.action_function:
                raise WorkflowError(
                    f"Action node {node.node_id} has no action function"
                )

            result = node.action_function(state)

            # Add to execution history
            self.state.execution_history.append(
                {
                    "node_id": node.node_id,
                    "node_type": node.node_type.value,
                    "action_result": result,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                }
            )

            return result

        except Exception as e:
            logger.error(f"Action node execution failed: {e}")
            raise

    def _execute_parallel_node(
        self, state: Dict[str, Any], node: WorkflowNode
    ) -> Dict[str, Any]:
        """Execute a parallel node."""
        try:
            # Get dependent nodes
            dependent_nodes = [
                n for n in self.config.nodes if n.node_id in node.dependencies
            ]

            # Execute dependent nodes in parallel
            tasks = []
            for dep_node in dependent_nodes:
                task = self._execute_node(dep_node)
                tasks.append(task)

            # Wait for all tasks to complete
            await asyncio.gather(*tasks)

            # Add to execution history
            self.state.execution_history.append(
                {
                    "node_id": node.node_id,
                    "node_type": node.node_type.value,
                    "parallel_nodes": [n.node_id for n in dependent_nodes],
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                }
            )

            return state

        except Exception as e:
            logger.error(f"Parallel node execution failed: {e}")
            raise

    def _execute_merge_node(
        self, state: Dict[str, Any], node: WorkflowNode
    ) -> Dict[str, Any]:
        """Execute a merge node."""
        try:
            # Get results from dependent nodes
            merged_data = {}

            for dep_node_id in node.dependencies:
                if dep_node_id in self.state.agent_states:
                    dep_state = self.state.agent_states[dep_node_id]
                    merged_data[dep_node_id] = dep_state

            # Add to execution history
            self.state.execution_history.append(
                {
                    "node_id": node.node_id,
                    "node_type": node.node_type.value,
                    "merged_nodes": node.dependencies,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                }
            )

            return {"merged_data": merged_data}

        except Exception as e:
            logger.error(f"Merge node execution failed: {e}")
            raise

    def get_status(self) -> WorkflowState:
        """Get current workflow status."""
        return self.state

    def pause(self):
        """Pause workflow execution."""
        if self.state:
            self.state.status = WorkflowStatus.PAUSED
            logger.info(f"Workflow {self.config.workflow_id} paused")

    def resume(self):
        """Resume workflow execution."""
        if self.state and self.state.status == WorkflowStatus.PAUSED:
            self.state.status = WorkflowStatus.RUNNING
            logger.info(f"Workflow {self.config.workflow_id} resumed")

    def cancel(self):
        """Cancel workflow execution."""
        if self.state:
            self.state.status = WorkflowStatus.CANCELLED
            self.state.end_time = datetime.now()
            logger.info(f"Workflow {self.config.workflow_id} cancelled")

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get workflow execution history."""
        return self.state.execution_history.copy() if self.state else []

    def get_agent_states(self) -> Dict[str, AgentState]:
        """Get all agent states from workflow."""
        return self.state.agent_states.copy() if self.state else {}

    def get_shared_data(self) -> Dict[str, Any]:
        """Get shared workflow data."""
        return self.state.shared_data.copy() if self.state else {}

    def update_shared_data(self, data: Dict[str, Any]):
        """Update shared workflow data."""
        if self.state:
            self.state.shared_data.update(data)

    def add_error(self, error: str):
        """Add error to workflow log."""
        if self.state:
            self.state.error_log.append(error)
            logger.error(f"Workflow {self.config.workflow_id} error: {error}")

    def get_config(self) -> WorkflowConfig:
        """Get workflow configuration."""
        return self.config

    def is_completed(self) -> bool:
        """Check if workflow is completed."""
        return self.state.status == WorkflowStatus.COMPLETED if self.state else False

    def is_failed(self) -> bool:
        """Check if workflow failed."""
        return self.state.status == WorkflowStatus.FAILED if self.state else False

    def is_running(self) -> bool:
        """Check if workflow is running."""
        return self.state.status == WorkflowStatus.RUNNING if self.state else False
