"""
Onboarding workflow graph v2 for the 23-step "Master System" process.
"""

import logging
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from ..state import AgentState
from ...schemas.business_context import BusinessContext
from ...services.bcm_service import BCMService
from ...utils.ucid import UCIDGenerator
from ..specialists.onboarding_orchestrator_v2 import OnboardingOrchestratorV2
from ..specialists.evidence_classifier import EvidenceClassifier, EvidenceType
from ..specialists.extraction_orchestrator import ExtractionOrchestrator
from ..specialists.contradiction_detector import ContradictionDetector
from ..specialists.truth_sheet_generator import TruthSheetGenerator
from ..specialists.brand_audit_agent import BrandAuditEngine
from ...infrastructure.storage import delete_file

logger = logging.getLogger(__name__)

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

# Instantiate specialists
orchestrator = OnboardingOrchestratorV2()
classifier = EvidenceClassifier()
extractor = ExtractionOrchestrator()
contradiction_detector = ContradictionDetector()
truth_sheet_generator = TruthSheetGenerator()
brand_audit_engine = BrandAuditEngine()

async def handle_evidence_vault(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 1: Process uploaded evidence and auto-classify."""
    logger.info("Handling Evidence Vault (Step 1)")
    
    if "evidence" in state and state["evidence"]:
        for item in state["evidence"]:
            if "evidence_type" not in item:
                classification = await classifier.classify_evidence(item)
                item["evidence_type"] = classification.evidence_type.value
                item["confidence"] = classification.confidence
                item["reasoning"] = classification.reasoning
    
    # Calculate Coverage & Recommendations
    recommended = classifier.get_recommended_evidence()
    missing = [r["type"] for r in recommended if r["type"] not in [e.get("evidence_type") for e in state.get("evidence", [])]]
    
    if "step_data" not in state:
        state["step_data"] = {}
        
    state["step_data"]["evidence_vault"] = {
        "missing_recommended": missing,
        "recommendations": classifier._generate_coverage_recommendations(missing, (len(recommended)-len(missing))/len(recommended) if recommended else 1.0)
    }
    
    # Update universal state
    state = await orchestrator.update_universal_state(state, {
        "evidence_ids": [e.get("file_id") for e in state.get("evidence", []) if e.get("file_id")]
    })
    
    state["onboarding_progress"] = (1 / 23) * 100
    return state

async def handle_auto_extraction(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 2: Deep fact extraction from multi-source evidence."""
    logger.info("Handling Auto Extraction (Step 2)")
    
    if "evidence" in state and state["evidence"]:
        # Run extraction
        result = await extractor.execute(state)
        state["step_data"]["auto_extraction"] = result.get("output", {})
        
        # Incremental Sync to Business Context
        facts = state["step_data"]["auto_extraction"].get("facts", [])
        updates = {}
        for fact in facts:
            if fact.get("category") == "identity":
                if "identity" not in updates:
                    updates["identity"] = {}
                updates["identity"][fact.get("label", "").lower().replace(" ", "_")] = fact.get("value")
        
        state = await orchestrator.update_universal_state(state, updates)
        
    state["onboarding_progress"] = (2 / 23) * 100
    return state

async def handle_data_purge(state: OnboardingStateV2) -> OnboardingStateV2:
    """Phase 4 Helper: Purge temporary GCS blobs after extraction."""
    logger.info("Handling Data Purge (Lifecycle Enforcement)")
    
    if "evidence" in state and state["evidence"]:
        for item in state["evidence"]:
            file_id = item.get("file_id")
            if file_id:
                success = await delete_file(file_id)
                logger.info(f"Purged file {file_id}: {success}")
                item["purged"] = success
                
    return state

async def handle_contradiction_check(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 3: Adversarial audit for logical consistency."""
    logger.info("Handling Contradiction Check (Step 3)")
    
    result = await contradiction_detector.execute(state)
    report = result.get("output", {})
    
    state["contradictions"] = report.get("contradictions", [])
    state["step_data"]["contradiction_check"] = report
    
    state["onboarding_progress"] = (3 / 23) * 100
    return state

async def handle_truth_sheet(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 4: Consolidate Candidate Truths."""
    logger.info("Handling Truth Sheet (Step 4)")
    
    result = await truth_sheet_generator.execute(state)
    sheet = result.get("output", {})
    
    state["step_data"]["truth_sheet"] = sheet
    
    state["onboarding_progress"] = (4 / 23) * 100
    return state

async def handle_brand_audit(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 5: Adversarial Brand Audit."""
    logger.info("Handling Brand Audit (Step 5)")
    
    result = await brand_audit_engine.execute(state)
    audit = result.get("output", {})
    
    state["step_data"]["brand_audit"] = audit
    
    state["onboarding_progress"] = (5 / 23) * 100
    return state

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

        # Add nodes
        workflow.add_node("handle_evidence_vault", handle_evidence_vault)
        workflow.add_node("handle_auto_extraction", handle_auto_extraction)
        workflow.add_node("handle_data_purge", handle_data_purge)
        workflow.add_node("handle_contradiction_check", handle_contradiction_check)
        workflow.add_node("handle_truth_sheet", handle_truth_sheet)
        workflow.add_node("handle_brand_audit", handle_brand_audit)
        
        # Add remaining nodes as placeholders
        for step in self.step_order[5:]:
            workflow.add_node(f"handle_{step}", generic_handler)

        # Set entry point
        workflow.set_entry_point("handle_evidence_vault")

        # Routing with Data Purge after Auto Extraction
        workflow.add_edge("handle_evidence_vault", "handle_auto_extraction")
        workflow.add_edge("handle_auto_extraction", "handle_data_purge")
        workflow.add_edge("handle_data_purge", "handle_contradiction_check")
        workflow.add_edge("handle_contradiction_check", "handle_truth_sheet")
        workflow.add_edge("handle_truth_sheet", "handle_brand_audit")

        # Remaining linear routing
        for i in range(5, len(self.step_order) - 1):
            workflow.add_edge(f"handle_{self.step_order[i]}", f"handle_{self.step_order[i+1]}")
        
        workflow.add_edge(f"handle_{self.step_order[-1]}", END)

        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

__all__ = [
    "OnboardingGraphV2", 
    "OnboardingStateV2", 
    "handle_evidence_vault", 
    "handle_auto_extraction", 
    "handle_contradiction_check", 
    "handle_truth_sheet", 
    "handle_data_purge",
    "handle_brand_audit"
]
