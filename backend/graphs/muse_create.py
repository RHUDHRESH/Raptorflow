import logging
from datetime import datetime

from langgraph.graph import END, START, StateGraph

from agents.base import BaseCognitiveAgent
from agents.shared.agents import IntentRouter, QualityGate
from agents.shared.context_assembler import ContextAssemblerAgent
from core.lifecycle import apply_lifecycle_transition
from models.cognitive import AgentMessage, CognitiveIntelligenceState, CognitiveStatus
from services.budget_governor import BudgetGovernor

logger = logging.getLogger("raptorflow.graphs.muse_create")

_budget_governor = BudgetGovernor()


async def _guard_budget(state: CognitiveIntelligenceState, agent_id: str) -> dict:
    workspace_id = state.get("workspace_id") or state.get("tenant_id")
    budget_check = await _budget_governor.check_budget(
        workspace_id=workspace_id, agent_id=agent_id
    )
    if not budget_check["allowed"]:
        return {
            "status": CognitiveStatus.ERROR,
            "messages": [
                AgentMessage(
                    role="system",
                    content=f"Budget governor blocked {agent_id}: {budget_check['reason']}",
                )
            ],
            "error": budget_check["reason"],
        }
    return {}


# --- Nodes ---


async def router_node(state: CognitiveIntelligenceState):
    """A00: Determines the intent and family of the asset."""
    router = IntentRouter()
    budget_guard = await _guard_budget(state, "IntentRouter")
    if budget_guard:
        return budget_guard
    intent = await router.execute(state["raw_prompt"])

    # Initialize brief with intent
    brief = state.get("brief", {})
    brief["asset_family"] = intent.asset_family
    brief["goal"] = intent.goal
    brief["mentions"] = intent.entities

    msg = AgentMessage(
        role="router",
        content=f"Intent routed to {intent.asset_family} family. Goal: {intent.goal}",
    )

    return apply_lifecycle_transition(
        state,
        CognitiveStatus.PLANNING,
        "router",
        {
            "brief": brief,
            "messages": [msg],
            "last_agent": "router",
        },
    )


async def context_node(state: CognitiveIntelligenceState):
    """A03: Pulls full context including learned memories."""
    assembler = ContextAssemblerAgent()
    budget_guard = await _guard_budget(state, "ContextAssemblerAgent")
    if budget_guard:
        return budget_guard
    # Assuming workspace_id and tenant_id are present in state
    ctx = await assembler.assemble(
        state.get("workspace_id", "default"),
        state.get("tenant_id", "default"),
        state["raw_prompt"],
    )

    # Merge with brief
    brief = state.get("brief", {})
    brief.update(ctx)

    msg = AgentMessage(
        role="assembler",
        content="Context assembled: Brand voice, memories, and constraints loaded.",
    )

    return apply_lifecycle_transition(
        state,
        CognitiveStatus.RESEARCHING,
        "assembler",
        {
            "brief": brief,
            "messages": [msg],
            "last_agent": "assembler",
        },
    )


async def drafting_node(state: CognitiveIntelligenceState):
    """A04: Generates the first draft of the asset."""
    family = state["brief"].get("asset_family", "text")

    if family == "image":
        from agents.creatives import ImageArchitect, VisualPrompter
        from inference import InferenceProvider

        # 1. Generate visual prompt first
        prompter = VisualPrompter(InferenceProvider.get_model("reasoning"))
        budget_guard = await _guard_budget(state, "VisualPrompter")
        if budget_guard:
            return budget_guard
        # VisualPrompter expects TypedDict state, but CognitiveIntelligenceState is similar
        # We might need a small adapter if schemas differ significantly
        prompt_res = await prompter(state)
        state["brief"]["image_prompt"] = prompt_res["current_brief"]["image_prompt"]

        # 2. Generate actual image
        architect = ImageArchitect(model_tier="nano")
        budget_guard = await _guard_budget(state, "ImageArchitect")
        if budget_guard:
            return budget_guard
        res = await architect(state)

        if "error" in res:
            msg = AgentMessage(role="drafter", content=f"Error: {res['error']}")
            return apply_lifecycle_transition(
                state,
                CognitiveStatus.FAILED,
                "drafter",
                {"messages": [msg], "last_agent": "drafter"},
            )

        return apply_lifecycle_transition(
            state,
            CognitiveStatus.EXECUTING,
            "drafter",
            {
                "generated_assets": res["generated_assets"],
                "last_agent": "drafter",
            },
        )

    drafter = BaseCognitiveAgent(
        name="drafter",
        role="creator",
        system_prompt=(
            f"You are the RaptorFlow Creative Engine. "
            f"Create a high-quality {family} asset based on the provided brief."
        ),
        model_tier="driver",
    )

    # We pass the full state to the agent
    budget_guard = await _guard_budget(state, "BaseCognitiveAgent:drafter")
    if budget_guard:
        return budget_guard
    res = await drafter(state)

    # Extract the content from the message
    draft_content = res["messages"][0].content

    return apply_lifecycle_transition(
        state,
        CognitiveStatus.EXECUTING,
        "drafter",
        {
            "messages": res["messages"],
            "generated_assets": [
                {"family": family, "content": draft_content, "version": "draft"}
            ],
            "last_agent": "drafter",
            "token_usage": res["token_usage"],
        },
    )


async def reflection_node(state: CognitiveIntelligenceState):
    """A05: Critiques the draft against the quality gate."""
    gate = QualityGate()
    budget_guard = await _guard_budget(state, "QualityGate")
    if budget_guard:
        return budget_guard

    # Get the latest draft
    last_asset = state["generated_assets"][-1]["content"]
    brief = state["brief"]

    audit_result = await gate.audit(last_asset, brief)

    msg = AgentMessage(
        role="critic",
        content=(
            f"Quality Audit: Score {audit_result.score}/100. "
            f"Pass: {audit_result.pass_gate}. "
            f"Fixes: {', '.join(audit_result.critical_fixes)}"
        ),
    )

    reflection = {
        "score": audit_result.score,
        "fixes": audit_result.critical_fixes,
        "pass": audit_result.pass_gate,
        "timestamp": datetime.now().isoformat(),
    }

    return apply_lifecycle_transition(
        state,
        CognitiveStatus.AUDITING,
        "critic",
        {
            "messages": [msg],
            "reflection_log": [reflection],
            "quality_score": audit_result.score / 100,
            "last_agent": "critic",
        },
    )


def decide_refinement(state: CognitiveIntelligenceState):
    """Conditional edge: Should we refine or finalize?"""
    last_reflection = state["reflection_log"][-1]

    # If score is too low or gate failed, and we haven't done too many iterations
    if not last_reflection["pass"] and len(state["reflection_log"]) < 3:
        return "refine"
    return "finalize"


async def refinement_node(state: CognitiveIntelligenceState):
    """A06: Refines the asset based on critique."""
    # last_asset = state["generated_assets"][-1]["content"]
    # fixes = state["reflection_log"][-1]["fixes"]

    refiner = BaseCognitiveAgent(
        name="refiner",
        role="creator",
        system_prompt=(
            "You are the RaptorFlow Polishing Engine. "
            "Refine the asset based on the provided critique and fixes."
        ),
        model_tier="reasoning",
    )

    # We can't easily change the state raw_prompt here without side effects,
    # but BaseCognitiveAgent uses state['messages'] which includes the history.

    budget_guard = await _guard_budget(state, "BaseCognitiveAgent:refiner")
    if budget_guard:
        return budget_guard
    res = await refiner(state)

    refined_content = res["messages"][0].content

    return apply_lifecycle_transition(
        state,
        CognitiveStatus.REFINING,
        "refiner",
        {
            "messages": res["messages"],
            "generated_assets": [
                {
                    "family": state["brief"].get("asset_family"),
                    "content": refined_content,
                    "version": "refined",
                }
            ],
            "last_agent": "refiner",
            "token_usage": res["token_usage"],
        },
    )


async def finalize_node(state: CognitiveIntelligenceState):
    """A07: Finalizes the asset and prepares for delivery."""
    last_asset = state["generated_assets"][-1]
    last_asset["version"] = "final"

    msg = AgentMessage(
        role="finalizer", content="Asset finalized and ready for deployment."
    )

    return apply_lifecycle_transition(
        state,
        CognitiveStatus.COMPLETE,
        "finalizer",
        {"messages": [msg], "last_agent": "finalizer"},
    )


async def memory_update_node(state: CognitiveIntelligenceState):
    """A06: Learns from the final result vs initial draft."""
    if len(state["generated_assets"]) > 1:
        # Placeholder for actual memory update logic
        # updater = MemoryUpdaterAgent()
        # draft = state["generated_assets"][0]["content"]
        # final = state["generated_assets"][-1]["content"]
        # rule = await updater.extract_preference(draft, final)
        pass

    return apply_lifecycle_transition(
        state,
        CognitiveStatus.COMPLETE,
        "memory_updater",
        {"last_agent": "memory_updater"},
    )


# --- Graph Builder ---


def build_muse_spine():
    workflow = StateGraph(CognitiveIntelligenceState)

    workflow.add_node("router", router_node)
    workflow.add_node("context", context_node)
    workflow.add_node("drafter", drafting_node)
    workflow.add_node("critic", reflection_node)
    workflow.add_node("refiner", refinement_node)
    workflow.add_node("finalizer", finalize_node)
    workflow.add_node("memory_update", memory_update_node)

    workflow.add_edge(START, "router")
    workflow.add_edge("router", "context")
    workflow.add_edge("context", "drafter")
    workflow.add_edge("drafter", "critic")

    workflow.add_conditional_edges(
        "critic", decide_refinement, {"refine": "refiner", "finalize": "finalizer"}
    )

    workflow.add_edge("refiner", "critic")
    workflow.add_edge("finalizer", "memory_update")
    workflow.add_edge("memory_update", END)

    return workflow.compile()
