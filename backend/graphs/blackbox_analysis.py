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
