import operator
from typing import Annotated, Dict, List, TypedDict


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


def get_blackbox_service():
    """Dependency provider for BlackboxService."""
    from backend.core.vault import Vault
    from backend.services.blackbox_service import BlackboxService
    return BlackboxService(Vault())


def ingest_telemetry_node(state: AnalysisState) -> Dict:
    """
    Node: Ingests all telemetry associated with the move_id.
    """
    service = get_blackbox_service()
    traces = service.get_telemetry_by_move(state["move_id"])
    return {"telemetry_data": traces, "status": "ingested"}


def extract_insights_node(state: AnalysisState) -> Dict:
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
    
    response = llm.invoke(prompt)
    finding = response.content.strip()

    return {"findings": [finding], "status": "analyzed"}


def attribute_outcomes_node(state: AnalysisState) -> Dict:
    """
    Node: Attributes business outcomes to the current move.
    """
    service = get_blackbox_service()
    outcomes = service.get_outcomes_for_move(state["move_id"])
    return {"outcomes": outcomes, "status": "attributed"}


def reflect_and_validate_node(state: AnalysisState) -> Dict:
    """
    Node: Critiques the findings and outcomes, assigning confidence.
    """
    from backend.inference import InferenceProvider
    llm = InferenceProvider.get_model(model_tier="ultra")
    
    findings = "\n".join(state.get("findings", []))
    outcomes = "\n".join([str(o) for o in state.get("outcomes", [])])
    
    prompt = (
        "Review the following findings and attributed outcomes for consistency and strategic depth.\n"
        "Assign a confidence score between 0.0 and 1.0 and provide a brief reflection.\n\n"
        f"Findings:\n{findings}\n\n"
        f"Outcomes:\n{outcomes}\n\n"
        "Format: Confidence: [score]\nReflection: [text]"
    )
    
    response = llm.invoke(prompt)
    content = response.content
    
    confidence = 0.5
    if "Confidence:" in content:
        try:
            conf_str = content.split("Confidence:")[1].split("\n")[0].strip()
            confidence = float(conf_str)
        except (ValueError, IndexError):
            pass
            
    reflection = content.split("Reflection:")[1].strip() if "Reflection:" in content else content
    
    return {"reflection": reflection, "confidence": confidence, "status": "validated"}


def should_continue(state: AnalysisState) -> str:
    """
    Conditional edge logic: decide whether to retry analysis.
    """
    if state.get("confidence", 0.0) < 0.7:
        return "extract_insights"
    return "__end__"


def create_blackbox_graph():
    """
    Constructs and returns the Blackbox Analysis Graph.
    Uses Strictly Synchronous LangGraph orchestration.
    """
    from langgraph.graph import StateGraph, START, END
    
    workflow = StateGraph(AnalysisState)
    
    workflow.add_node("ingest_telemetry", ingest_telemetry_node)
    workflow.add_node("extract_insights", extract_insights_node)
    workflow.add_node("attribute_outcomes", attribute_outcomes_node)
    workflow.add_node("reflect_and_validate", reflect_and_validate_node)
    
    workflow.add_edge(START, "ingest_telemetry")
    workflow.add_edge("ingest_telemetry", "extract_insights")
    workflow.add_edge("extract_insights", "attribute_outcomes")
    workflow.add_edge("attribute_outcomes", "reflect_and_validate")
    
    workflow.add_conditional_edges(
        "reflect_and_validate",
        should_continue,
        {
            "extract_insights": "extract_insights",
            "__end__": END
        }
    )
    
    return workflow.compile()