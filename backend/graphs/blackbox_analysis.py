import operator
from typing import Annotated, Dict, List, TypedDict


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
    status: str


def get_blackbox_service():
    """Dependency provider for BlackboxService."""
    from backend.core.vault import Vault
    from backend.services.blackbox_service import BlackboxService

    vault = Vault()
    return BlackboxService(vault)


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
    Math-heavy probabilistic attribution logic placeholder.
    """
    from backend.core.vault import Vault

    session = Vault().get_session()

    # In a production scenario, this would use probabilistic modeling
    # to find outcomes correlated with this move_id.
    result = (
        session.table("blackbox_outcomes_industrial")
        .select("*")
        .eq("move_id", state["move_id"])
        .limit(10)
        .execute()
    )

    return {"outcomes": result.data, "status": "attributed"}


def reflect_and_validate_node(state: AnalysisState) -> Dict:
    """
    Node: Critiques the findings and outcomes, assigning confidence.
    """
    from backend.inference import InferenceProvider
    llm = InferenceProvider.get_model(model_tier="ultra") # Use highest tier for reflection
    
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
    
    # Simple parsing logic
    confidence = 0.5
    if "Confidence:" in content:
        try:
            conf_str = content.split("Confidence:")[1].split("\n")[0].strip()
            confidence = float(conf_str)
        except (ValueError, IndexError):
            pass
            
    reflection = content.split("Reflection:")[1].strip() if "Reflection:" in content else content
    
    return {"reflection": reflection, "confidence": confidence, "status": "validated"}
