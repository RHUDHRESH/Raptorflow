"""
Onboarding workflow graph for 13-step onboarding process.
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from ..specialists.onboarding_orchestrator import OnboardingOrchestrator
from ..state import AgentState


class OnboardingState(AgentState):
    """Extended state for onboarding workflow."""

    current_step: Literal[
        "evidence_vault",
        "brand_voice",
        "guardrails",
        "icp_cohorts",
        "market_research",
        "competitor_analysis",
        "differentiators",
        "proof_points",
        "muse_calibration",
        "move_strategy",
        "campaign_planning",
        "blackbox_activation",
        "launch",
    ]
    completed_steps: List[str]
    evidence: List[Dict[str, Any]]
    step_data: Dict[str, Any]
    onboarding_progress: float
    needs_user_input: bool
    user_input_request: Optional[str]


class OnboardingStepHandler:
    """Handler for individual onboarding steps."""

    def __init__(self):
        self.orchestrator = OnboardingOrchestrator()
        self.step_order = [
            "evidence_vault",
            "brand_voice",
            "guardrails",
            "icp_cohorts",
            "market_research",
            "competitor_analysis",
            "differentiators",
            "proof_points",
            "muse_calibration",
            "move_strategy",
            "campaign_planning",
            "blackbox_activation",
            "launch",
        ]

    def get_next_step(self, current_step: Optional[str]) -> Optional[str]:
        """Get the next step in the onboarding sequence."""
        if current_step is None:
            return self.step_order[0]

        try:
            current_index = self.step_order.index(current_step)
            if current_index < len(self.step_order) - 1:
                return self.step_order[current_index + 1]
            return None  # Onboarding complete
        except ValueError:
            return self.step_order[0]

    def calculate_progress(self, completed_steps: List[str]) -> float:
        """Calculate onboarding progress percentage."""
        return len(completed_steps) / len(self.step_order) * 100


async def handle_evidence_vault(state: OnboardingState) -> OnboardingState:
    """Handle evidence vault collection step."""
    try:
        # Use onboarding orchestrator to guide evidence collection
        result = await state.orchestrator.execute(state)

        state["step_data"]["evidence_vault"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("evidence_vault")
            state["current_step"] = "brand_voice"

        return state
    except Exception as e:
        state["error"] = f"Evidence vault step failed: {str(e)}"
        return state


async def handle_brand_voice(state: OnboardingState) -> OnboardingState:
    """Handle brand voice definition step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["brand_voice"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("brand_voice")
            state["current_step"] = "guardrails"

        return state
    except Exception as e:
        state["error"] = f"Brand voice step failed: {str(e)}"
        return state


async def handle_guardrails(state: OnboardingState) -> OnboardingState:
    """Handle guardrails definition step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["guardrails"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("guardrails")
            state["current_step"] = "icp_cohorts"

        return state
    except Exception as e:
        state["error"] = f"Guardrails step failed: {str(e)}"
        return state


async def handle_icp_cohorts(state: OnboardingState) -> OnboardingState:
    """Handle ICP cohorts creation step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["icp_cohorts"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("icp_cohorts")
            state["current_step"] = "market_research"

        return state
    except Exception as e:
        state["error"] = f"ICP cohorts step failed: {str(e)}"
        return state


async def handle_market_research(state: OnboardingState) -> OnboardingState:
    """Handle market research step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["market_research"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("market_research")
            state["current_step"] = "competitor_analysis"

        return state
    except Exception as e:
        state["error"] = f"Market research step failed: {str(e)}"
        return state


async def handle_competitor_analysis(state: OnboardingState) -> OnboardingState:
    """Handle competitor analysis step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["competitor_analysis"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("competitor_analysis")
            state["current_step"] = "differentiators"

        return state
    except Exception as e:
        state["error"] = f"Competitor analysis step failed: {str(e)}"
        return state


async def handle_differentiators(state: OnboardingState) -> OnboardingState:
    """Handle differentiators definition step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["differentiators"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("differentiators")
            state["current_step"] = "proof_points"

        return state
    except Exception as e:
        state["error"] = f"Differentiators step failed: {str(e)}"
        return state


async def handle_proof_points(state: OnboardingState) -> OnboardingState:
    """Handle proof points collection step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["proof_points"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("proof_points")
            state["current_step"] = "muse_calibration"

        return state
    except Exception as e:
        state["error"] = f"Proof points step failed: {str(e)}"
        return state


async def handle_muse_calibration(state: OnboardingState) -> OnboardingState:
    """Handle Muse calibration step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["muse_calibration"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("muse_calibration")
            state["current_step"] = "move_strategy"

        return state
    except Exception as e:
        state["error"] = f"Muse calibration step failed: {str(e)}"
        return state


async def handle_move_strategy(state: OnboardingState) -> OnboardingState:
    """Handle move strategy creation step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["move_strategy"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("move_strategy")
            state["current_step"] = "campaign_planning"

        return state
    except Exception as e:
        state["error"] = f"Move strategy step failed: {str(e)}"
        return state


async def handle_campaign_planning(state: OnboardingState) -> OnboardingState:
    """Handle campaign planning step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["campaign_planning"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("campaign_planning")
            state["current_step"] = "blackbox_activation"

        return state
    except Exception as e:
        state["error"] = f"Campaign planning step failed: {str(e)}"
        return state


async def handle_blackbox_activation(state: OnboardingState) -> OnboardingState:
    """Handle Blackbox activation step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["blackbox_activation"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("blackbox_activation")
            state["current_step"] = "launch"

        return state
    except Exception as e:
        state["error"] = f"Blackbox activation step failed: {str(e)}"
        return state


async def handle_launch(state: OnboardingState) -> OnboardingState:
    """Handle launch step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["launch"] = result.get("output", {})
        state["completed_steps"].append("launch")
        state["onboarding_progress"] = 100.0
        state["current_step"] = "completed"

        return state
    except Exception as e:
        state["error"] = f"Launch step failed: {str(e)}"
        return state


def should_continue_onboarding(state: OnboardingState) -> str:
    """Determine next step based on onboarding state."""
    if state.get("error"):
        return END

    if state.get("needs_user_input", False):
        return "await_input"

    current_step = state.get("current_step", "")

    # Map steps to their handler functions
    step_handlers = {
        "evidence_vault": "handle_evidence_vault",
        "brand_voice": "handle_brand_voice",
        "guardrails": "handle_guardrails",
        "icp_cohorts": "handle_icp_cohorts",
        "market_research": "handle_market_research",
        "competitor_analysis": "handle_competitor_analysis",
        "differentiators": "handle_differentiators",
        "proof_points": "handle_proof_points",
        "muse_calibration": "handle_muse_calibration",
        "move_strategy": "handle_move_strategy",
        "campaign_planning": "handle_campaign_planning",
        "blackbox_activation": "handle_blackbox_activation",
        "launch": "handle_launch",
    }

    return step_handlers.get(current_step, END)


class OnboardingGraph:
    """Onboarding workflow graph."""

    def __init__(self):
        self.step_handler = OnboardingStepHandler()
        self.graph = None

    def create_graph(self) -> StateGraph:
        """Create the onboarding workflow graph."""
        workflow = StateGraph(OnboardingState)

        # Add step handler nodes
        workflow.add_node("handle_evidence_vault", handle_evidence_vault)
        workflow.add_node("handle_brand_voice", handle_brand_voice)
        workflow.add_node("handle_guardrails", handle_guardrails)
        workflow.add_node("handle_icp_cohorts", handle_icp_cohorts)
        workflow.add_node("handle_market_research", handle_market_research)
        workflow.add_node("handle_competitor_analysis", handle_competitor_analysis)
        workflow.add_node("handle_differentiators", handle_differentiators)
        workflow.add_node("handle_proof_points", handle_proof_points)
        workflow.add_node("handle_muse_calibration", handle_muse_calibration)
        workflow.add_node("handle_move_strategy", handle_move_strategy)
        workflow.add_node("handle_campaign_planning", handle_campaign_planning)
        workflow.add_node("handle_blackbox_activation", handle_blackbox_activation)
        workflow.add_node("handle_launch", handle_launch)

        # Set entry point based on current step
        workflow.set_entry_point("handle_evidence_vault")

        # Add conditional routing
        workflow.add_conditional_edges(
            "handle_evidence_vault",
            should_continue_onboarding,
            {"handle_brand_voice": "handle_brand_voice", "await_input": END, END: END},
        )
        workflow.add_conditional_edges(
            "handle_brand_voice",
            should_continue_onboarding,
            {"handle_guardrails": "handle_guardrails", "await_input": END, END: END},
        )
        workflow.add_conditional_edges(
            "handle_guardrails",
            should_continue_onboarding,
            {"handle_icp_cohorts": "handle_icp_cohorts", "await_input": END, END: END},
        )
        workflow.add_conditional_edges(
            "handle_icp_cohorts",
            should_continue_onboarding,
            {
                "handle_market_research": "handle_market_research",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_market_research",
            should_continue_onboarding,
            {
                "handle_competitor_analysis": "handle_competitor_analysis",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_competitor_analysis",
            should_continue_onboarding,
            {
                "handle_differentiators": "handle_differentiators",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_differentiators",
            should_continue_onboarding,
            {
                "handle_proof_points": "handle_proof_points",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_proof_points",
            should_continue_onboarding,
            {
                "handle_muse_calibration": "handle_muse_calibration",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_muse_calibration",
            should_continue_onboarding,
            {
                "handle_move_strategy": "handle_move_strategy",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_move_strategy",
            should_continue_onboarding,
            {
                "handle_campaign_planning": "handle_campaign_planning",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_campaign_planning",
            should_continue_onboarding,
            {
                "handle_blackbox_activation": "handle_blackbox_activation",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_blackbox_activation",
            should_continue_onboarding,
            {"handle_launch": "handle_launch", "await_input": END, END: END},
        )
        workflow.add_edge("handle_launch", END)

        # Add memory checkpointing
        memory = MemorySaver()

        # Compile the graph
        self.graph = workflow.compile(checkpointer=memory)
        return self.graph

    async def start_onboarding(
        self, workspace_id: str, user_id: str, session_id: str
    ) -> Dict[str, Any]:
        """Start the onboarding process."""
        if not self.graph:
            self.create_graph()

        # Create initial state
        initial_state = OnboardingState(
            workspace_id=workspace_id,
            user_id=user_id,
            session_id=session_id,
            current_step="evidence_vault",
            completed_steps=[],
            evidence=[],
            step_data={},
            onboarding_progress=0.0,
            needs_user_input=False,
            user_input_request=None,
            messages=[],
            routing_path=[],
            memory_context={},
            foundation_summary={},
            active_icps=[],
            pending_approval=False,
            error=None,
            output=None,
            tokens_used=0,
            cost_usd=0.0,
        )

        # Configure execution
        thread_config = {
            "configurable": {
                "thread_id": session_id,
                "checkpoint_ns": f"onboarding_{workspace_id}",
            }
        }

        try:
            result = await self.graph.ainvoke(initial_state, config=thread_config)

            return {
                "success": True,
                "current_step": result.get("current_step"),
                "progress": result.get("onboarding_progress", 0),
                "needs_user_input": result.get("needs_user_input", False),
                "user_input_request": result.get("user_input_request"),
                "completed_steps": result.get("completed_steps", []),
                "step_data": result.get("step_data", {}),
                "error": result.get("error"),
            }

        except Exception as e:
            return {"success": False, "error": f"Onboarding failed: {str(e)}"}

    async def continue_onboarding(
        self, workspace_id: str, user_id: str, session_id: str, user_input: str
    ) -> Dict[str, Any]:
        """Continue onboarding with user input."""
        if not self.graph:
            self.create_graph()

        # Load existing state
        thread_config = {
            "configurable": {
                "thread_id": session_id,
                "checkpoint_ns": f"onboarding_{workspace_id}",
            }
        }

        try:
            # Get current checkpoint
            checkpoint = await self.graph.aget_state(thread_config)
            if not checkpoint:
                return {"success": False, "error": "No onboarding session found"}

            # Update state with user input
            current_state = checkpoint.values
            current_state["messages"].append({"role": "user", "content": user_input})
            current_state["needs_user_input"] = False
            current_state["user_input_request"] = None

            # Continue execution
            result = await self.graph.ainvoke(current_state, config=thread_config)

            return {
                "success": True,
                "current_step": result.get("current_step"),
                "progress": result.get("onboarding_progress", 0),
                "needs_user_input": result.get("needs_user_input", False),
                "user_input_request": result.get("user_input_request"),
                "completed_steps": result.get("completed_steps", []),
                "step_data": result.get("step_data", {}),
                "error": result.get("error"),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to continue onboarding: {str(e)}",
            }
