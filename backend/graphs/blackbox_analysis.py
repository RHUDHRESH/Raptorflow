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
