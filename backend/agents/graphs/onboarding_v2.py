"""
Onboarding workflow graph v2 for the 23-step "Master System" process.
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from ..state import AgentState
from ...schemas.business_context import BusinessContext
from ...services.bcm_service import BCMService
from ...utils.ucid import UCIDGenerator

class OnboardingStateV2(AgentState):
    """Extended state for onboarding master system."""
    
    # Universal Context
    business_context: Dict[str, Any]
    bcm_state: Dict[str, Any]
    ucid: str
    
    # Flow Control
    current_step: str
    completed_steps: List[str]
    onboarding_progress: float
    needs_user_input: bool
    user_input_request: Optional[str]
    
    # Step Data
    evidence: List[Dict[str, Any]]
    step_data: Dict[str, Any]
    contradictions: List[Dict[str, Any]]
    market_insights: List[Dict[str, Any]]
    competitors: List[Dict[str, Any]]
    positioning: Dict[str, Any]
    icp_profiles: List[Dict[str, Any]]
    
    # Audit
    red_team_logs: List[Dict[str, Any]]

class OnboardingGraphV2:
    """Updated onboarding workflow graph with 23-step master logic."""

    def __init__(self):
        self.step_order = [
            "evidence_vault",           # Step 1
            "auto_extraction",          # Step 2
            "contradiction_check",      # Step 3
            "truth_sheet",              # Step 4
            "brand_audit",              # Step 5
            "offer_pricing",            # Step 6
            "market_intelligence",      # Step 7
            "comparative_angle",        # Step 8
            "category_paths",           # Step 9
            "capability_rating",        # Step 10
            "perceptual_map",           # Step 11
            "strategic_grid",           # Step 12
            "positioning_statements",   # Step 13
            "focus_sacrifice",          # Step 14
            "icp_profiles",             # Step 15
            "buying_process",           # Step 16
            "messaging_guardrails",     # Step 17
            "soundbites_library",       # Step 18
            "message_hierarchy",        # Step 19
            "channel_mapping",          # Step 20
            "tam_sam_som",              # Step 21
            "validation_todos",         # Step 22
            "final_synthesis",          # Step 23
        ]

    def create_graph(self) -> StateGraph:
        """Create the updated onboarding workflow graph."""
        workflow = StateGraph(OnboardingStateV2)

        # Placeholder handler nodes
        async def generic_handler(state: OnboardingStateV2) -> OnboardingStateV2:
            return state

        # Add nodes for all steps
        for step in self.step_order:
            workflow.add_node(f"handle_{step}", generic_handler)

        # Set entry point
        workflow.set_entry_point(f"handle_{self.step_order[0]}")

        # Basic linear routing for now
        for i in range(len(self.step_order) - 1):
            workflow.add_edge(f"handle_{self.step_order[i]}", f"handle_{self.step_order[i+1]}")
        
        workflow.add_edge(f"handle_{self.step_order[-1]}", END)

        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
