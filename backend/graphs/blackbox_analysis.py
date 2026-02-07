import operator
from typing import Annotated, Any, Dict, List, TypedDict


class AnalysisState(TypedDict):
    """
    State definition for the Blackbox Analysis Graph.
    Uses strictly synchronous operations.
    """

    move_id: str

    # Annotated with operator.add to allow multiple nodes to append findings/data
    telemetry_data: Annotated[List[Dict], operator.add]
    findings: Annotated[List[str], operator.add]
    outcomes: Annotated[List[Dict], operator.add]

    reflection: str
    confidence: float
    status: Annotated[List[str], operator.add]
    evaluation: Dict[str, Any]


def get_blackbox_service():
    """Dependency provider for BlackboxService."""
    from core.vault import Vault
    from services.blackbox_service import BlackboxService

    vault = Vault()
    return BlackboxService(vault)


def ingest_telemetry_node(state: AnalysisState) -> Dict:
    """
    Node: Ingests all telemetry associated with the move_id.
    """
    service = get_blackbox_service()
    traces = service.get_telemetry_by_move(state["move_id"])
    return {"telemetry_data": traces, "status": ["ingested"]}


async def extract_insights_node(state: AnalysisState) -> Dict:
    """
    Node: Analyzes telemetry via LLM to extract strategic findings.
    """
    from inference import InferenceProvider

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

    return {"findings": [finding], "status": ["analyzed"]}


def attribute_outcomes_node(state: AnalysisState) -> Dict:
    """
    Node: Attributes business outcomes to the current move.
    """
    service = get_blackbox_service()
    outcomes = service.get_outcomes_for_move(state["move_id"])
    return {"outcomes": outcomes, "status": ["attributed"]}


async def reflect_and_validate_node(state: AnalysisState) -> Dict:
    """
    Node: Critiques the findings and outcomes, assigning confidence.
    """
    from inference import InferenceProvider

    llm = InferenceProvider.get_model(
        model_tier="ultra"
    )  # Use highest tier for reflection

    findings = "\n".join(state.get("findings", []))
    outcomes = "\n".join([str(o) for o in state.get("outcomes", [])])

    prompt = (
        "Review the following findings and attributed outcomes for consistency and strategic depth.\n"
        "Assign a confidence score between 0.0 and 1.0 and provide a brief reflection.\n\n"
        f"Findings:\n{findings}\n\n"
        f"Outcomes:\n{outcomes}\n\n"
        "Format: Confidence: [score]\nReflection: [text]"
    )

    response = await llm.ainvoke(prompt)
    content = response.content

    # Simple parsing logic
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

    return {"reflection": reflection, "confidence": confidence, "status": ["validated"]}


def should_continue(state: AnalysisState) -> str:
    """
    Conditional edge logic: decide whether to retry analysis.
    """
    if state.get("confidence", 0.0) < 0.7:
        return "extract_insights"
    return "__end__"


def evaluate_run(state: AnalysisState) -> Dict[str, Any]:
    """Evaluates telemetry and findings at the end of the run."""
    from services.evaluation import EvaluationService

    evaluator = EvaluationService()
    evaluation = evaluator.evaluate_run(
        telemetry_events=state.get("telemetry_events", state.get("telemetry_data", [])),
        output_summary=state.get("reflection") or "\n".join(state.get("findings", [])),
        run_id=state.get("move_id"),
        tenant_id=state.get("tenant_id"),
    )
    return {"evaluation": evaluation}


def create_blackbox_graph():
    """
    Constructs and returns the Blackbox Analysis Graph.
    Uses Strictly Synchronous LangGraph orchestration.
    """
    from langgraph.graph import END, START, StateGraph

    from agents.blackbox_specialist import (
        BlackboxCritiqueAgent,
        CompetitorIntelligenceAgent,
        ROIAnalystAgent,
        StrategicDriftAgent,
    )

    workflow = StateGraph(AnalysisState)

    # 1. Specialized Agents
    roi_analyst = ROIAnalystAgent()
    drift_agent = StrategicDriftAgent()
    comp_agent = CompetitorIntelligenceAgent()
    critique_agent = BlackboxCritiqueAgent()

    # 2. Add Nodes
    workflow.add_node("ingest_telemetry", ingest_telemetry_node)
    workflow.add_node("extract_insights", extract_insights_node)
    workflow.add_node("attribute_outcomes", attribute_outcomes_node)
    workflow.add_node("roi_analysis", roi_analyst)
    workflow.add_node("drift_analysis", drift_agent)
    workflow.add_node("competitor_analysis", comp_agent)
    workflow.add_node("reflect_and_validate", reflect_and_validate_node)
    workflow.add_node("critique_analysis", critique_agent)
    workflow.add_node("evaluate", evaluate_run)

    # 3. Define Flow
    workflow.add_edge(START, "ingest_telemetry")
    workflow.add_edge("ingest_telemetry", "extract_insights")
    workflow.add_edge("extract_insights", "attribute_outcomes")

    # Parallel/Collaborative branch
    workflow.add_edge("attribute_outcomes", "roi_analysis")
    workflow.add_edge("attribute_outcomes", "drift_analysis")
    workflow.add_edge("attribute_outcomes", "competitor_analysis")

    # Fan-in to reflection
    workflow.add_edge("roi_analysis", "reflect_and_validate")
    workflow.add_edge("drift_analysis", "reflect_and_validate")
    workflow.add_edge("competitor_analysis", "reflect_and_validate")

    # Critique Loop
    workflow.add_edge("reflect_and_validate", "critique_analysis")

    workflow.add_conditional_edges(
        "critique_analysis",
        should_continue,
        {"extract_insights": "extract_insights", "__end__": "evaluate"},
    )
    workflow.add_edge("evaluate", END)

    return workflow.compile()
