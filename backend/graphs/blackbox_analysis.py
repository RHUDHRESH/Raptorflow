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
    from backend.core.vault import Vault
    session = Vault().get_session()
    
    result = (
        session.table("blackbox_telemetry_industrial")
        .select("*")
        .eq("move_id", state["move_id"])
        .execute()
    )
    
    return {"telemetry_data": result.data, "status": "ingested"}

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

def supervisor_node(state: AnalysisState) -> Dict:
    """
    Node: Orchestrates specialized agents (ROI, Drift, Competitor) 
    to provide a multi-faceted analysis.
    """
    from backend.agents.roi_analyst import ROIAnalystAgent
    from backend.agents.drift_detector import StrategicDriftAgent
    from backend.agents.competitor_intel import CompetitorIntelligenceAgent
    
    move_id = state["move_id"]
    
    # 1. ROI Analysis
    roi_agent = ROIAnalystAgent()
    roi_result = roi_agent.run(move_id, {"outcomes": state.get("outcomes", [])})
    
    # 2. Strategic Drift Detection
    drift_agent = StrategicDriftAgent()
    # Mocking brand kit for now
    drift_result = drift_agent.run(move_id, {
        "trace": str(state.get("telemetry_data", [])),
        "brand_kit": "Foundation v1"
    })
    
    # 3. Competitor Intelligence
    intel_agent = CompetitorIntelligenceAgent()
    intel_result = intel_agent.run(move_id, {"telemetry_data": state.get("telemetry_data", [])})
    
    new_findings = [
        roi_result.get("attribution", ""),
        drift_result.get("drift_report", ""),
        intel_result.get("competitor_insights", "")
    ]
    
    # Clean empty strings
    new_findings = [f for f in new_findings if f]
    
    return {"findings": new_findings, "status": "coordinated"}

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
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("reflect_and_validate", reflect_and_validate_node)
    
    workflow.add_edge(START, "ingest_telemetry")
    workflow.add_edge("ingest_telemetry", "extract_insights")
    workflow.add_edge("extract_insights", "attribute_outcomes")
    workflow.add_edge("attribute_outcomes", "supervisor")
    workflow.add_edge("supervisor", "reflect_and_validate")
    
    workflow.add_conditional_edges(
        "reflect_and_validate",
        should_continue,
        {
            "extract_insights": "extract_insights",
            "__end__": END
        }
    )
    
    return workflow.compile()