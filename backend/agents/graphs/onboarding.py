"""
Onboarding workflow graph for 23-step onboarding process.
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
        "auto_extraction",
        "contradiction_check",
        "reddit_research",
        "competitor_analysis",
        "category_paths",
        "capability_rating",
        "perceptual_map",
        "neuroscience_copy",
        "focus_sacrifice",
        "icp_generation",
        "truth_sheet",
        "proof_points",
        "positioning_statements",
        "messaging_rules",
        "soundbites_merge",
        "icp_deep",
        "channel_strategy",
        "tam_sam_som",
        "brand_voice",
        "guardrails",
        "icp_cohorts",
        "market_research",
        "differentiators",
        "launch_readiness",
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
            "auto_extraction",
            "contradiction_check",
            "reddit_research",
            "competitor_analysis",
            "category_paths",
            "capability_rating",
            "perceptual_map",
            "neuroscience_copy",
            "focus_sacrifice",
            "icp_generation",
            "truth_sheet",
            "proof_points",
            "positioning_statements",
            "messaging_rules",
            "soundbites_merge",
            "icp_deep",
            "channel_strategy",
            "tam_sam_som",
            "brand_voice",
            "guardrails",
            "icp_cohorts",
            "market_research",
            "differentiators",
            "launch_readiness",
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
            state["current_step"] = "auto_extraction"

        return state
    except Exception as e:
        state["error"] = f"Evidence vault step failed: {str(e)}"
        return state


async def handle_auto_extraction(state: OnboardingState) -> OnboardingState:
    """Handle auto extraction from evidence."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["auto_extraction"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("auto_extraction")
            state["current_step"] = "contradiction_check"

        return state
    except Exception as e:
        state["error"] = f"Auto extraction step failed: {str(e)}"
        return state


async def handle_truth_sheet(state: OnboardingState) -> OnboardingState:
    """Handle truth sheet generation step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["truth_sheet"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("truth_sheet")
            state["current_step"] = "proof_points"

        return state
    except Exception as e:
        state["error"] = f"Truth sheet step failed: {str(e)}"
        return state


async def handle_proof_points(state: OnboardingState) -> OnboardingState:
    """Handle proof points validation step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["proof_points"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("proof_points")
            state["current_step"] = "positioning_statements"

        return state
    except Exception as e:
        state["error"] = f"Proof points step failed: {str(e)}"
        return state


async def handle_positioning_statements(state: OnboardingState) -> OnboardingState:
    """Handle positioning statements generation step."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["positioning_statements"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("positioning_statements")
            state["current_step"] = "messaging_rules"

        return state
    except Exception as e:
        state["error"] = f"Positioning statements step failed: {str(e)}"
        return state


async def handle_contradiction_check(state: OnboardingState) -> OnboardingState:
    """Handle contradiction detection in evidence."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["contradiction_check"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("contradiction_check")
            state["current_step"] = "reddit_research"

        return state
    except Exception as e:
        state["error"] = f"Contradiction check step failed: {str(e)}"
        return state


async def handle_reddit_research(state: OnboardingState) -> OnboardingState:
    """Handle Reddit research and market intelligence."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["reddit_research"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("reddit_research")
            state["current_step"] = "competitor_analysis"

        return state
    except Exception as e:
        state["error"] = f"Reddit research step failed: {str(e)}"
        return state


async def handle_category_paths(state: OnboardingState) -> OnboardingState:
    """Handle safe/clever/bold category paths."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["category_paths"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("category_paths")
            state["current_step"] = "capability_rating"

        return state
    except Exception as e:
        state["error"] = f"Category paths step failed: {str(e)}"
        return state


async def handle_capability_rating(state: OnboardingState) -> OnboardingState:
    """Handle capability rating (Only You/Unique/etc.)."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["capability_rating"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("capability_rating")
            state["current_step"] = "perceptual_map"

        return state
    except Exception as e:
        state["error"] = f"Capability rating step failed: {str(e)}"
        return state


async def handle_perceptual_map(state: OnboardingState) -> OnboardingState:
    """Handle AI perceptual map generation (3 options)."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["perceptual_map"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("perceptual_map")
            state["current_step"] = "neuroscience_copy"

        return state
    except Exception as e:
        state["error"] = f"Perceptual map step failed: {str(e)}"
        return state


async def handle_neuroscience_copy(state: OnboardingState) -> OnboardingState:
    """Handle neuroscience copywriting engine."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["neuroscience_copy"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("neuroscience_copy")
            state["current_step"] = "focus_sacrifice"

        return state
    except Exception as e:
        state["error"] = f"Neuroscience copy step failed: {str(e)}"
        return state


async def handle_focus_sacrifice(state: OnboardingState) -> OnboardingState:
    """Handle focus/sacrifice position logic."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["focus_sacrifice"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("focus_sacrifice")
            state["current_step"] = "icp_generation"

        return state
    except Exception as e:
        return state


async def handle_icp_generation(state: OnboardingState) -> OnboardingState:
    """Handle ICP generation and refinement."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["icp_generation"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("icp_generation")
            state["current_step"] = "icp_deep"

        return state
    except Exception as e:
        state["error"] = f"ICP generation step failed: {str(e)}"
        return state


async def handle_icp_deep(state: OnboardingState) -> OnboardingState:
    """Handle comprehensive ICP profiles generation."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["icp_deep"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("icp_deep")
            state["current_step"] = "launch_readiness"

        return state
    except Exception as e:
        state["error"] = f"ICP deep step failed: {str(e)}"
        return state


async def handle_launch_readiness(state: OnboardingState) -> OnboardingState:
    """Handle launch readiness check."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["launch_readiness"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("launch_readiness")
            state["current_step"] = "messaging_rules"

        return state
    except Exception as e:
        state["error"] = f"Launch readiness step failed: {str(e)}"
        return state


async def handle_messaging_rules(state: OnboardingState) -> OnboardingState:
    """Handle messaging rules creation."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["messaging_rules"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("messaging_rules")
            state["current_step"] = "soundbites_merge"

        return state
    except Exception as e:
        state["error"] = f"Messaging rules step failed: {str(e)}"
        return state


async def handle_soundbites_merge(state: OnboardingState) -> OnboardingState:
    """Handle soundbites merge process."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["soundbites_merge"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("soundbites_merge")
            state["current_step"] = "channel_strategy"

        return state
    except Exception as e:
        state["error"] = f"Soundbites merge step failed: {str(e)}"
        return state


async def handle_channel_strategy(state: OnboardingState) -> OnboardingState:
    """Handle channel strategy recommendations."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["channel_strategy"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("channel_strategy")
            state["current_step"] = "tam_sam_som"

        return state
    except Exception as e:
        state["error"] = f"Channel strategy step failed: {str(e)}"
        return state


async def handle_tam_sam_som(state: OnboardingState) -> OnboardingState:
    """Handle TAM/SAM/SOM market sizing visualization."""
    try:
        result = await state.orchestrator.execute(state)

        state["step_data"]["tam_sam_som"] = result.get("output", {})
        state["needs_user_input"] = result.get("needs_user_input", False)
        state["user_input_request"] = result.get("user_input_request")

        if not state["needs_user_input"]:
            state["completed_steps"].append("tam_sam_som")
            state["current_step"] = "brand_voice"

        return state
    except Exception as e:
        state["error"] = f"TAM/SAM/SOM step failed: {str(e)}"
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
        "auto_extraction": "handle_auto_extraction",
        "contradiction_check": "handle_contradiction_check",
        "reddit_research": "handle_reddit_research",
        "competitor_analysis": "handle_competitor_analysis",
        "category_paths": "handle_category_paths",
        "capability_rating": "handle_capability_rating",
        "perceptual_map": "handle_perceptual_map",
        "neuroscience_copy": "handle_neuroscience_copy",
        "focus_sacrifice": "handle_focus_sacrifice",
        "icp_generation": "handle_icp_generation",
        "messaging_rules": "handle_messaging_rules",
        "soundbites_merge": "handle_soundbites_merge",
        "channel_strategy": "handle_channel_strategy",
        "tam_sam_som": "handle_tam_sam_som",
        "brand_voice": "handle_brand_voice",
        "guardrails": "handle_guardrails",
        "icp_cohorts": "handle_icp_cohorts",
        "market_research": "handle_market_research",
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
        workflow.add_node("handle_auto_extraction", handle_auto_extraction)
        workflow.add_node("handle_contradiction_check", handle_contradiction_check)
        workflow.add_node("handle_reddit_research", handle_reddit_research)
        workflow.add_node("handle_competitor_analysis", handle_competitor_analysis)
        workflow.add_node("handle_category_paths", handle_category_paths)
        workflow.add_node("handle_capability_rating", handle_capability_rating)
        workflow.add_node("handle_perceptual_map", handle_perceptual_map)
        workflow.add_node("handle_neuroscience_copy", handle_neuroscience_copy)
        workflow.add_node("handle_focus_sacrifice", handle_focus_sacrifice)
        workflow.add_node("handle_icp_generation", handle_icp_generation)
        workflow.add_node("handle_truth_sheet", handle_truth_sheet)
        workflow.add_node("handle_proof_points", handle_proof_points)
        workflow.add_node(
            "handle_positioning_statements", handle_positioning_statements
        )
        workflow.add_node("handle_messaging_rules", handle_messaging_rules)
        workflow.add_node("handle_soundbites_merge", handle_soundbites_merge)
        workflow.add_node("handle_icp_deep", handle_icp_deep)
        workflow.add_node("handle_channel_strategy", handle_channel_strategy)
        workflow.add_node("handle_tam_sam_som", handle_tam_sam_som)
        workflow.add_node("handle_brand_voice", handle_brand_voice)
        workflow.add_node("handle_guardrails", handle_guardrails)
        workflow.add_node("handle_icp_cohorts", handle_icp_cohorts)
        workflow.add_node("handle_market_research", handle_market_research)
        workflow.add_node("handle_differentiators", handle_differentiators)
        workflow.add_node("handle_launch_readiness", handle_launch_readiness)
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
            {
                "handle_auto_extraction": "handle_auto_extraction",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_auto_extraction",
            should_continue_onboarding,
            {
                "handle_contradiction_check": "handle_contradiction_check",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_contradiction_check",
            should_continue_onboarding,
            {
                "handle_reddit_research": "handle_reddit_research",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_reddit_research",
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
                "handle_category_paths": "handle_category_paths",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_category_paths",
            should_continue_onboarding,
            {
                "handle_capability_rating": "handle_capability_rating",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_capability_rating",
            should_continue_onboarding,
            {
                "handle_perceptual_map": "handle_perceptual_map",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_perceptual_map",
            should_continue_onboarding,
            {
                "handle_neuroscience_copy": "handle_neuroscience_copy",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_neuroscience_copy",
            should_continue_onboarding,
            {
                "handle_focus_sacrifice": "handle_focus_sacrifice",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_focus_sacrifice",
            should_continue_onboarding,
            {
                "handle_icp_generation": "handle_icp_generation",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_icp_generation",
            should_continue_onboarding,
            {
                "handle_messaging_rules": "handle_messaging_rules",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_messaging_rules",
            should_continue_onboarding,
            {
                "handle_soundbites_merge": "handle_soundbites_merge",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_soundbites_merge",
            should_continue_onboarding,
            {
                "handle_channel_strategy": "handle_channel_strategy",
                "await_input": END,
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "handle_channel_strategy",
            should_continue_onboarding,
            {"handle_tam_sam_som": "handle_tam_sam_som", "await_input": END, END: END},
        )
        workflow.add_conditional_edges(
            "handle_tam_sam_som",
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
