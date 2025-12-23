import operator
from typing import Annotated, List, Dict, TypedDict, Union


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
    """Lazy-loader for BlackboxService inside graph nodes."""
    from backend.services.blackbox_service import BlackboxService
    from backend.core.vault import Vault
    return BlackboxService(Vault())


def ingest_telemetry_node(state: AnalysisState) -> Dict:
    """
    Node: Ingests all telemetry associated with the move_id.
    """
    service = get_blackbox_service()
    session = service.vault.get_session()
    
    result = (
        session.table("blackbox_telemetry_industrial")
        .select("*")
        .eq("move_id", state["move_id"])
        .execute()
    )
    
    return {"telemetry_data": result.data, "status": "ingested"}


def get_blackbox_service():
    """Dependency provider for BlackboxService."""
    from backend.core.vault import Vault
    from backend.services.blackbox_service import BlackboxService

    vault = Vault()
    return BlackboxService(vault)


def ingest_telemetry_node(state: AnalysisState):
    """Retrieves all telemetry traces for the given move."""
    service = get_blackbox_service()
    # In a real scenario, we might need a more specific filter than agent_id
    # But for this node, we'll simulate fetching by move context
    traces = service.get_agent_audit_log(agent_id=state["move_id"])

    return {"telemetry_data": traces, "status": "ingested"}
