import operator
from typing import Annotated, Dict, List, TypedDict

from backend.services.budget_governor import BudgetGovernor


class AnalysisState(TypedDict):
    """
    State definition for the Blackbox Analysis Graph.
    Uses strictly synchronous operations.
    """

    move_id: str
    telemetry_data: Annotated[List[Dict], operator.add]
    findings: Annotated[List[str], operator.add]
    outcomes: Annotated[List[Dict], operator.add]
    reflection: str
    confidence: float
    status: str


_budget_governor = BudgetGovernor()


async def _guard_budget(state: AnalysisState, agent_id: str) -> Dict:
    workspace_id = state.get("workspace_id") or state.get("tenant_id")
    budget_check = await _budget_governor.check_budget(
        workspace_id=workspace_id, agent_id=agent_id
    )
    if not budget_check["allowed"]:
        return {
            "status": "error",
            "findings": [
                f"Budget governor blocked {agent_id}: {budget_check['reason']}"
            ],
            "reflection": budget_check["reason"],
        }
    return {}


def ingest_telemetry_node(state: AnalysisState) -> Dict:
    """
    Node: Ingests all telemetry associated with the move_id.
    """
    from backend.core.vault import Vault
    from backend.services.blackbox_service import BlackboxService

    service = BlackboxService(Vault())
    session = service.vault.get_session()

    result = (
        session.table("blackbox_telemetry_industrial")
        .select("*")
        .eq("move_id", state["move_id"])
        .execute()
    )

    return {"telemetry_data": result.data, "status": "ingested"}


async def extract_insights_node(state: AnalysisState) -> Dict:
    """
    Node: Analyzes telemetry via LLM to extract strategic findings.
    """
    from backend.inference import InferenceProvider

    llm = InferenceProvider.get_model(model_tier="reasoning")

    telemetry_summary = "\n".join([str(t) for t in state.get("telemetry_data", [])])

    prompt = (
        "Analyze the following agent execution telemetry and extract exactly one "
        "concise strategic finding about marketing performance or agent efficacy.\n\n"
        f"Telemetry:\n{telemetry_summary}\n\n"
        "Finding:"
    )

    response = await llm.ainvoke(prompt)
    finding = response.content.strip()

    return {"findings": [finding], "status": "analyzed"}


def attribute_outcomes_node(state: AnalysisState) -> Dict:
    """
    Node: Attributes business outcomes to the current move.
    """
    from backend.core.vault import Vault

    session = Vault().get_session()

    result = (
        session.table("blackbox_outcomes_industrial")
        .select("*")
        .eq("move_id", state["move_id"])
        .limit(10)
        .execute()
    )

    return {"outcomes": result.data, "status": "attributed"}


async def supervisor_node(state: AnalysisState) -> Dict:
    """
    Node: Orchestrates specialized agents (ROI, Drift, Competitor)
    to provide a multi-faceted analysis.
    """
    from backend.agents.competitor_intel import CompetitorIntelligenceAgent
    from backend.agents.drift_detector import StrategicDriftAgent
    from backend.agents.roi_analyst import ROIAnalystAgent

    move_id = state["move_id"]

    # 1. ROI Analysis
    budget_guard = await _guard_budget(state, "ROIAnalystAgent")
    if budget_guard:
        return budget_guard
    roi_agent = ROIAnalystAgent()
    roi_result = roi_agent.run(move_id, {"outcomes": state.get("outcomes", [])})

    # 2. Strategic Drift Detection
    budget_guard = await _guard_budget(state, "StrategicDriftAgent")
    if budget_guard:
        return budget_guard
    drift_agent = StrategicDriftAgent()
    drift_result = drift_agent.run(
        move_id,
        {"trace": str(state.get("telemetry_data", [])), "brand_kit": "Foundation v1"},
    )

    # 3. Competitor Intelligence
    budget_guard = await _guard_budget(state, "CompetitorIntelligenceAgent")
    if budget_guard:
        return budget_guard
    intel_agent = CompetitorIntelligenceAgent()
    intel_result = intel_agent.run(
        move_id, {"telemetry_data": state.get("telemetry_data", [])}
    )

    new_findings = [
        roi_result.get("attribution", ""),
        drift_result.get("drift_report", ""),
        intel_result.get("competitor_insights", ""),
    ]

    new_findings = [f for f in new_findings if f]

    return {"findings": new_findings, "status": "coordinated"}


async def reflect_and_validate_node(state: AnalysisState) -> Dict:
    """
    Node: Critiques the findings and outcomes, assigning confidence.
    Implements the 'Critique' loop logic.
    """
    from backend.inference import InferenceProvider

    llm = InferenceProvider.get_model(model_tier="ultra")

    findings = "\n".join(state.get("findings", []))
    outcomes = "\n".join([str(o) for o in state.get("outcomes", [])])

    prompt = (
        "You are the RaptorFlow Analysis Supervisor. Critically review the following "
        "findings and attributed outcomes generated by specialized agents.\n\n"
        "Your goal is to ensure strategic alignment, mathematical consistency, and actionable depth.\n\n"
        f"Findings:\n{findings}\n\n"
        f"Outcomes:\n{outcomes}\n\n"
        "Provide a confidence score (0.0 to 1.0) and a detailed reflection/critique.\n"
        "If confidence is below 0.7, explain exactly what is missing or weak.\n\n"
        "Format:\nConfidence: [score]\nReflection: [text]"
    )

    response = await llm.ainvoke(prompt)
    content = response.content

    confidence = 0.5
    if "Confidence:" in content:
        try:
            conf_str = content.split("Confidence:")[1].split("\n")[0].strip()
            confidence = float(conf_str)
        except (ValueError, IndexError):
            pass

    reflection = (
        content.split("Reflection:")[1].strip() if "Reflection:" in content else content
    )

    return {"reflection": reflection, "confidence": confidence, "status": "validated"}


def should_continue(state: AnalysisState) -> str:
    """
    Conditional edge logic: decide whether to retry analysis based on critique.
    """
    if state.get("confidence", 0.0) < 0.7:
        return "retry"
    return "__end__"


def create_blackbox_graph():
    """
    Constructs and returns the Blackbox Analysis Graph.
    Uses Strictly Synchronous LangGraph orchestration.
    """
    from langgraph.graph import END, START, StateGraph

    workflow = StateGraph(AnalysisState)

    workflow.add_node("ingest_telemetry", ingest_telemetry_node)
    workflow.add_node("extract_insights", extract_insights_node)
    workflow.add_node("attribute_outcomes", attribute_outcomes_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("reflect_and_validate", reflect_and_validate_node)

    workflow.add_edge(START, "ingest_telemetry")
    workflow.add_edge("ingest_telemetry", "extract_insights")
    workflow.add_edge("extract_insights", "attribute_outcomes")
    workflow.add_edge("attribute_outcomes", "supervisor")
    workflow.add_edge("supervisor", "reflect_and_validate")

    workflow.add_conditional_edges(
        "reflect_and_validate", should_continue, {"retry": "supervisor", "__end__": END}
    )

    return workflow.compile()
