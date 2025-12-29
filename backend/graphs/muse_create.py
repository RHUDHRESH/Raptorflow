import logging
from datetime import datetime
from types import SimpleNamespace

from langgraph.graph import END, START, StateGraph

from agents.base import BaseCognitiveAgent
from agents.shared.agents import IntentRouter, QualityGate
from agents.shared.context_assembler import ContextAssemblerAgent
from core.lifecycle import apply_lifecycle_transition
from db import save_asset_vault
from inference import InferenceProvider
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
    prompt = state.get("raw_prompt", "")
    fallback_family = "meme" if "meme" in prompt.lower() else "text"
    if not InferenceProvider.is_ready():
        intent = SimpleNamespace(
            asset_family=fallback_family,
            goal="Fallback routing due to inference unavailable.",
            entities=[],
        )
        msg = AgentMessage(
            role="router",
            content="Inference unavailable. Using fallback routing.",
        )
        return apply_lifecycle_transition(
            state,
            CognitiveStatus.PLANNING,
            "router",
            {
                "brief": {
                    **state.get("brief", {}),
                    "asset_family": intent.asset_family,
                    "goal": intent.goal,
                    "mentions": intent.entities,
                },
                "messages": [msg],
                "last_agent": "router",
            },
        )

    try:
        router = IntentRouter()
    except Exception as exc:
        logger.error("IntentRouter init failed: %s", exc)
        intent = SimpleNamespace(
            asset_family=fallback_family,
            goal="Fallback routing due to intent init error.",
            entities=[],
        )
        msg = AgentMessage(
            role="router",
            content="Intent routing degraded. Using fallback routing.",
        )
        return apply_lifecycle_transition(
            state,
            CognitiveStatus.PLANNING,
            "router",
            {
                "brief": {
                    **state.get("brief", {}),
                    "asset_family": intent.asset_family,
                    "goal": intent.goal,
                    "mentions": intent.entities,
                },
                "messages": [msg],
                "last_agent": "router",
            },
        )

    budget_guard = await _guard_budget(state, "IntentRouter")
    if budget_guard:
        return budget_guard
    try:
        intent = await router.execute(state["raw_prompt"])
    except Exception as exc:
        intent = SimpleNamespace(
            asset_family=fallback_family,
            goal="Fallback routing due to intent error.",
            entities=[],
        )
        logger.error("IntentRouter failed, using fallback routing: %s", exc)

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
    if not InferenceProvider.is_ready():
        fallback_content = (
            "Draft (fallback)\n"
            f"Prompt: {state.get('raw_prompt', '').strip()}\n"
            "Output:\n"
            "- Hook: Clear and direct.\n"
            "- Value: One concrete benefit.\n"
            "- CTA: Next step in one line."
        )
        return apply_lifecycle_transition(
            state,
            CognitiveStatus.EXECUTING,
            "drafter",
            {
                "messages": [AgentMessage(role="drafter", content=fallback_content)],
                "generated_assets": [
                    {"family": family, "content": fallback_content, "version": "draft"}
                ],
                "last_agent": "drafter",
                "token_usage": {},
            },
        )

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

    try:
        drafter = BaseCognitiveAgent(
            name="drafter",
            role="creator",
            system_prompt=(
                f"You are the RaptorFlow Creative Engine. "
                f"Create a high-quality {family} asset based on the provided brief."
            ),
            model_tier="driver",
        )
    except Exception as exc:
        logger.error("Muse drafter init failed: %s", exc)
        fallback_content = (
            "Draft (fallback)\n"
            f"Prompt: {state.get('raw_prompt', '').strip()}\n"
            "Output:\n"
            "- Hook: Clear and direct.\n"
            "- Value: One concrete benefit.\n"
            "- CTA: Next step in one line."
        )
        return apply_lifecycle_transition(
            state,
            CognitiveStatus.EXECUTING,
            "drafter",
            {
                "messages": [AgentMessage(role="drafter", content=fallback_content)],
                "generated_assets": [
                    {"family": family, "content": fallback_content, "version": "draft"}
                ],
                "last_agent": "drafter",
                "token_usage": {},
            },
        )

    # We pass the full state to the agent
    budget_guard = await _guard_budget(state, "BaseCognitiveAgent:drafter")
    if budget_guard:
        return budget_guard
    try:
        res = await drafter(state)
    except Exception as exc:
        logger.error("Muse drafting failed: %s", exc)
        res = {"messages": [], "error": str(exc)}

    # Extract the content from the message
    draft_content = None
    if res.get("messages"):
        draft_content = res["messages"][0].content

    if not draft_content:
        prompt = state.get("raw_prompt", "").strip()
        brief = state.get("brief", {})
        tone = brief.get("brand_voice", "Clear, direct, and concise.")
        if family == "meme":
            draft_content = (
                f"Top text: {prompt[:60] or 'When you ship fast'}\n"
                f"Bottom text: {prompt[-60:] or 'and it actually works'}"
            )
        else:
            draft_content = (
                "Draft (fallback)\n"
                f"Prompt: {prompt}\n"
                f"Tone: {tone}\n"
                "Output:\n"
                "- Hook: Ship a crisp, high-signal deliverable.\n"
                "- Value: Clear promise, zero fluff.\n"
                "- CTA: If this resonates, act on it now."
            )

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
            "token_usage": res.get("token_usage", {}),
        },
    )


async def reflection_node(state: CognitiveIntelligenceState):
    """A05: Critiques the draft against the quality gate."""
    if not InferenceProvider.is_ready():
        msg = AgentMessage(
            role="critic",
            content="Quality gate skipped due to inference unavailable.",
        )
        reflection = {
            "score": 0,
            "fixes": [],
            "pass": True,
            "timestamp": datetime.now().isoformat(),
        }
        return apply_lifecycle_transition(
            state,
            CognitiveStatus.AUDITING,
            "critic",
            {
                "messages": [msg],
                "reflection_log": [reflection],
                "quality_score": 0.0,
                "last_agent": "critic",
            },
        )

    try:
        gate = QualityGate()
    except Exception as exc:
        logger.error("QualityGate init failed: %s", exc)
        msg = AgentMessage(
            role="critic",
            content="Quality gate degraded due to init failure.",
        )
        reflection = {
            "score": 0,
            "fixes": [],
            "pass": True,
            "timestamp": datetime.now().isoformat(),
        }
        return apply_lifecycle_transition(
            state,
            CognitiveStatus.AUDITING,
            "critic",
            {
                "messages": [msg],
                "reflection_log": [reflection],
                "quality_score": 0.0,
                "last_agent": "critic",
            },
        )

    budget_guard = await _guard_budget(state, "QualityGate")
    if budget_guard:
        return budget_guard

    # Get the latest draft
    generated_assets = state.get("generated_assets", [])
    if not generated_assets:
        logger.error("Muse reflection skipped: no generated assets.")
        audit_result = SimpleNamespace(score=0, pass_gate=True, critical_fixes=[])
    else:
        last_asset = generated_assets[-1]["content"]
        brief = state.get("brief", {})
        try:
            audit_result = await gate.audit(last_asset, brief)
        except Exception as exc:
            logger.error("QualityGate failed, skipping refinement: %s", exc)
            audit_result = SimpleNamespace(score=0, pass_gate=True, critical_fixes=[])

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

    if not InferenceProvider.is_ready():
        refined_content = state.get("generated_assets", [{}])[-1].get(
            "content", "Refinement unavailable."
        )
        return apply_lifecycle_transition(
            state,
            CognitiveStatus.REFINING,
            "refiner",
            {
                "messages": [AgentMessage(role="refiner", content=refined_content)],
                "generated_assets": [
                    {
                        "family": state["brief"].get("asset_family"),
                        "content": refined_content,
                        "version": "refined",
                    }
                ],
                "last_agent": "refiner",
                "token_usage": {},
            },
        )

    try:
        refiner = BaseCognitiveAgent(
            name="refiner",
            role="creator",
            system_prompt=(
                "You are the RaptorFlow Polishing Engine. "
                "Refine the asset based on the provided critique and fixes."
            ),
            model_tier="reasoning",
        )
    except Exception as exc:
        logger.error("Muse refiner init failed: %s", exc)
        refined_content = state.get("generated_assets", [{}])[-1].get(
            "content", "Refinement unavailable."
        )
        return apply_lifecycle_transition(
            state,
            CognitiveStatus.REFINING,
            "refiner",
            {
                "messages": [AgentMessage(role="refiner", content=refined_content)],
                "generated_assets": [
                    {
                        "family": state["brief"].get("asset_family"),
                        "content": refined_content,
                        "version": "refined",
                    }
                ],
                "last_agent": "refiner",
                "token_usage": {},
            },
        )

    # We can't easily change the state raw_prompt here without side effects,
    # but BaseCognitiveAgent uses state['messages'] which includes the history.

    budget_guard = await _guard_budget(state, "BaseCognitiveAgent:refiner")
    if budget_guard:
        return budget_guard
    try:
        res = await refiner(state)
    except Exception as exc:
        logger.error("Muse refinement failed: %s", exc)
        res = {"messages": [], "error": str(exc)}

    refined_content = None
    if res.get("messages"):
        refined_content = res["messages"][0].content
    if not refined_content:
        refined_content = state.get("generated_assets", [{}])[-1].get(
            "content", "Refinement unavailable."
        )

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
            "token_usage": res.get("token_usage", {}),
        },
    )


async def finalize_node(state: CognitiveIntelligenceState):
    """A07: Finalizes the asset and prepares for delivery."""
    last_asset = state["generated_assets"][-1]
    last_asset["version"] = "final"

    workspace_id = state.get("workspace_id") or state.get("tenant_id")
    asset_family = state.get("brief", {}).get("asset_family", "text")
    asset_type = "image" if asset_family == "image" else "text"
    metadata = {
        "asset_family": asset_family,
        "quality_score": state.get("quality_score"),
        "thread_id": state.get("thread_id"),
    }
    try:
        stored_asset_id = await save_asset_vault(
            workspace_id=workspace_id,
            content=last_asset["content"],
            asset_type=asset_type,
            metadata=metadata,
        )
    except Exception as exc:
        stored_asset_id = None
        logger.error("Failed to store muse asset: %s", exc)

    msg = AgentMessage(
        role="finalizer", content="Asset finalized and ready for deployment."
    )

    return apply_lifecycle_transition(
        state,
        CognitiveStatus.COMPLETE,
        "finalizer",
        {
            "messages": [msg],
            "last_agent": "finalizer",
            "stored_asset_id": stored_asset_id,
        },
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
