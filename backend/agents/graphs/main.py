"""
Main Raptorflow workflow graph using LangGraph.
"""

from typing import Annotated, Any, Dict, List, Optional, TypedDict

from langchain_core.messages import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from ..base import BaseAgent
from ..dispatcher import AgentDispatcher
from ..preprocessing import RequestPreprocessor
from ..routing.pipeline import RoutingPipeline
from ..specialists.quality_checker import QualityChecker
from ..state import AgentState, create_initial_state
from ..tools.registry import ToolRegistry


class WorkflowState(AgentState):
    """Extended state for workflow execution."""

    current_step: str
    workflow_result: Optional[Dict[str, Any]]
    quality_score: Optional[float]
    requires_approval: bool
    approval_gate_id: Optional[str]


def create_preprocess_node(preprocessor: RequestPreprocessor):
    """Create preprocessing node."""

    async def preprocess(state: WorkflowState) -> WorkflowState:
        """Preprocess request and load context."""
        try:
            updated_state = await preprocessor.preprocess(state)
            updated_state["current_step"] = "preprocessed"
            return updated_state
        except Exception as e:
            state["error"] = f"Preprocessing failed: {str(e)}"
            return state

    return preprocess


def create_route_node(routing_pipeline: RoutingPipeline):
    """Create routing node."""

    async def route(state: WorkflowState) -> WorkflowState:
        """Route request to appropriate agent."""
        try:
            request = state.get("messages", [])[-1] if state.get("messages") else ""
            routing_decision = await routing_pipeline.route(
                request=(
                    request.content if hasattr(request, "content") else str(request)
                ),
                workspace_id=state.get("workspace_id"),
                fast_mode=False,
            )

            state["current_agent"] = routing_decision.target_agent
            state["routing_path"] = routing_decision.routing_path
            state["current_step"] = "routed"
            return state
        except Exception as e:
            state["error"] = f"Routing failed: {str(e)}"
            return state

    return route


def create_execute_node(dispatcher: AgentDispatcher):
    """Create execution node."""

    async def execute(state: WorkflowState) -> WorkflowState:
        """Execute the routed agent."""
        try:
            result = await dispatcher.dispatch(
                request=state.get("messages", [])[-1] if state.get("messages") else "",
                workspace_id=state.get("workspace_id"),
                user_id=state.get("user_id"),
                session_id=state.get("session_id"),
                fast_mode=False,
            )

            state["output"] = result.get("output")
            state["tokens_used"] = result.get("tokens_used", 0)
            state["cost_usd"] = result.get("cost_usd", 0.0)
            state["workflow_result"] = result
            state["current_step"] = "executed"
            return state
        except Exception as e:
            state["error"] = f"Execution failed: {str(e)}"
            return state

    return execute


def create_quality_check_node(quality_checker: QualityChecker):
    """Create quality check node."""

    async def quality_check(state: WorkflowState) -> WorkflowState:
        """Check output quality."""
        try:
            output = state.get("output")
            if not output:
                state["quality_score"] = 0.0
                state["current_step"] = "quality_checked"
                return state

            report = await quality_checker.check_quality(
                content=output,
                workspace_id=state.get("workspace_id"),
                foundation_summary=state.get("foundation_summary", {}),
                active_icps=state.get("active_icps", []),
            )

            state["quality_score"] = report.overall_score
            state["requires_approval"] = not report.approved
            state["current_step"] = "quality_checked"
            return state
        except Exception as e:
            state["error"] = f"Quality check failed: {str(e)}"
            return state

    return quality_check


def create_approval_gate_node():
    """Create approval gate node."""

    async def approval_gate(state: WorkflowState) -> WorkflowState:
        """Handle approval gate logic."""
        if not state.get("requires_approval", False):
            state["current_step"] = "approved"
            return state

        # Generate approval gate ID
        gate_id = f"gate_{state.get('session_id')}_{state.get('user_id')}_{hash(str(state.get('output')))}"
        state["approval_gate_id"] = gate_id
        state["pending_approval"] = True
        state["current_step"] = "awaiting_approval"
        return state

    return approval_gate


def create_postprocess_node():
    """Create postprocessing node."""

    async def postprocess(state: WorkflowState) -> WorkflowState:
        """Postprocess results."""
        try:
            # Format final output
            result = {
                "success": not state.get("error"),
                "output": state.get("output"),
                "quality_score": state.get("quality_score"),
                "tokens_used": state.get("tokens_used", 0),
                "cost_usd": state.get("cost_usd", 0.0),
                "requires_approval": state.get("requires_approval", False),
                "approval_gate_id": state.get("approval_gate_id"),
                "routing_path": state.get("routing_path", []),
                "agent": state.get("current_agent"),
                "error": state.get("error"),
            }

            state["workflow_result"] = result
            state["current_step"] = "completed"
            return state
        except Exception as e:
            state["error"] = f"Postprocessing failed: {str(e)}"
            return state

    return postprocess


def should_continue_execution(state: WorkflowState) -> str:
    """Determine next step based on state."""
    if state.get("error"):
        return "postprocess"

    current_step = state.get("current_step", "")

    if current_step == "preprocessed":
        return "route"
    elif current_step == "routed":
        return "execute"
    elif current_step == "executed":
        return "quality_check"
    elif current_step == "quality_checked":
        return "approval_gate"
    elif current_step == "approval_gate":
        if state.get("requires_approval", False):
            return "await_approval"
        else:
            return "postprocess"
    elif current_step == "await_approval":
        return "postprocess"
    else:
        return "postprocess"


def create_raptorflow_graph(
    preprocessor: Optional[RequestPreprocessor] = None,
    routing_pipeline: Optional[RoutingPipeline] = None,
    dispatcher: Optional[AgentDispatcher] = None,
    quality_checker: Optional[QualityChecker] = None,
) -> StateGraph:
    """
    Create the main Raptorflow workflow graph.

    Args:
        preprocessor: Request preprocessor instance
        routing_pipeline: Routing pipeline instance
        dispatcher: Agent dispatcher instance
        quality_checker: Quality checker instance

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create default instances if not provided
    if preprocessor is None:
        preprocessor = RequestPreprocessor()
    if routing_pipeline is None:
        routing_pipeline = RoutingPipeline()
    if dispatcher is None:
        dispatcher = AgentDispatcher()
    if quality_checker is None:
        quality_checker = QualityChecker()

    # Create the workflow graph
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("preprocess", create_preprocess_node(preprocessor))
    workflow.add_node("route", create_route_node(routing_pipeline))
    workflow.add_node("execute", create_execute_node(dispatcher))
    workflow.add_node("quality_check", create_quality_check_node(quality_checker))
    workflow.add_node("approval_gate", create_approval_gate_node())
    workflow.add_node("postprocess", create_postprocess_node())

    # Add edges
    workflow.set_entry_point("preprocess")
    workflow.add_conditional_edges(
        "preprocess",
        should_continue_execution,
        {"route": "route", "postprocess": "postprocess"},
    )
    workflow.add_conditional_edges(
        "route",
        should_continue_execution,
        {"execute": "execute", "postprocess": "postprocess"},
    )
    workflow.add_conditional_edges(
        "execute",
        should_continue_execution,
        {"quality_check": "quality_check", "postprocess": "postprocess"},
    )
    workflow.add_conditional_edges(
        "quality_check",
        should_continue_execution,
        {"approval_gate": "approval_gate", "postprocess": "postprocess"},
    )
    workflow.add_conditional_edges(
        "approval_gate",
        should_continue_execution,
        {"await_approval": "await_approval", "postprocess": "postprocess"},
    )
    workflow.add_edge("postprocess", END)

    # Add memory checkpointing
    memory = MemorySaver()

    # Compile the graph
    compiled_graph = workflow.compile(checkpointer=memory)

    return compiled_graph


async def execute_workflow(
    graph: StateGraph,
    request: str,
    workspace_id: str,
    user_id: str,
    session_id: str,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute the Raptorflow workflow.

    Args:
        graph: Compiled workflow graph
        request: User request
        workspace_id: Workspace ID
        user_id: User ID
        session_id: Session ID
        config: Optional configuration

    Returns:
        Workflow execution result
    """
    # Create initial state
    initial_state = create_initial_state(
        workspace_id=workspace_id, user_id=user_id, session_id=session_id
    )
    initial_state["messages"] = [{"role": "user", "content": request}]
    initial_state["current_step"] = "initialized"

    # Configure execution
    thread_config = {
        "configurable": {
            "thread_id": session_id,
            "checkpoint_ns": f"workspace_{workspace_id}",
        }
    }
    if config:
        thread_config.update(config)

    try:
        # Execute the workflow
        result = await graph.ainvoke(initial_state, config=thread_config)

        return result.get(
            "workflow_result",
            {"success": False, "error": "No workflow result produced"},
        )

    except Exception as e:
        return {"success": False, "error": f"Workflow execution failed: {str(e)}"}
