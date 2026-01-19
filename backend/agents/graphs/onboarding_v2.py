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
from ..specialists.pricing_optimization_agent import PricingOptimizationAgent
from ...services.titan.orchestrator import TitanOrchestrator
from ..specialists.comparative_angle_agent import ComparativeAngleGenerator
from ..specialists.category_advisor import CategoryAdvisor
from ..specialists.capability_rating_agent import CapabilityRatingEngine
from ..specialists.perceptual_map_generator import PerceptualMapGenerator
from ..specialists.strategic_grid_agent import StrategicGridGenerator
from ..specialists.positioning_statement_generator import PositioningStatementGenerator
from ..specialists.focus_sacrifice_engine import FocusSacrificeEngine
from ..specialists.icp_deep_generator import ICPDeepGenerator
from ..specialists.buying_process_agent import BuyingProcessArchitect
from ..specialists.messaging_rules_engine import MessagingRulesEngine
from ..specialists.soundbites_generator import SoundbitesGenerator
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
pricing_agent = PricingOptimizationAgent()
titan_sorter = TitanOrchestrator()
angle_generator = ComparativeAngleGenerator()
category_advisor = CategoryAdvisor()
capability_rating_engine = CapabilityRatingEngine()
perceptual_map_generator = PerceptualMapGenerator()
strategic_grid_generator = StrategicGridGenerator()
positioning_generator = PositioningStatementGenerator()
focus_sacrifice_engine = FocusSacrificeEngine()
icp_generator = ICPDeepGenerator()
buying_process_architect = BuyingProcessArchitect()
messaging_rules_engine = MessagingRulesEngine()
soundbites_generator = SoundbitesGenerator()

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

async def handle_offer_pricing(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 6: Offer & Pricing Analysis."""
    logger.info("Handling Offer & Pricing (Step 6)")
    
    result = await pricing_agent.execute(state)
    analysis = result.get("output", {})
    
    state["step_data"]["offer_pricing"] = analysis
    
    state["onboarding_progress"] = (6 / 23) * 100
    return state

async def handle_market_intelligence(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 7: Autonomous Market Research via Titan Sorter."""
    logger.info("Handling Market Intelligence (Step 7)")
    
    # Seed query from Business Context
    company_name = state.get("business_context", {}).get("identity", {}).get("company_name", "AI Marketing Automation")
    query = f"Competitors and market landscape for {company_name}"
    
    # Run Titan research (Lite mode for onboarding speed)
    result = await titan_sorter.execute(query, mode="LITE")
    
    state["market_insights"] = result.get("results", [])
    state["step_data"]["market_intelligence"] = result
    
    state["onboarding_progress"] = (7 / 23) * 100
    return state

async def handle_comparative_angle(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 8: Define Competitive Alternatives & Angles."""
    logger.info("Handling Comparative Angle (Step 8)")
    
    result = await angle_generator.execute(state)
    angles = result.get("output", {})
    
    state["step_data"]["comparative_angle"] = angles
    
    state["onboarding_progress"] = (8 / 23) * 100
    return state

async def handle_category_paths(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 9: Recommend Safe/Clever/Bold Category Paths."""
    logger.info("Handling Category Paths (Step 9)")
    
    result = await category_advisor.execute(state)
    paths = result.get("output", {})
    
    state["step_data"]["category_paths"] = paths
    
    state["onboarding_progress"] = (9 / 23) * 100
    return state

async def handle_capability_rating(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 10: Rate Differentiated Capabilities."""
    logger.info("Handling Capability Rating (Step 10)")
    
    result = await capability_rating_engine.execute(state)
    ratings = result.get("output", {})
    
    state["step_data"]["capability_rating"] = ratings
    
    state["onboarding_progress"] = (10 / 23) * 100
    return state

async def handle_perceptual_map(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 11: Generate Strategic Perceptual Map."""
    logger.info("Handling Perceptual Map (Step 11)")
    
    result = await perceptual_map_generator.execute(state)
    map_data = result.get("output", {})
    
    state["step_data"]["perceptual_map"] = map_data
    
    state["onboarding_progress"] = (11 / 23) * 100
    return state

async def handle_strategic_grid(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 12: Populate Strategic Grid (Value vs Rarity)."""
    logger.info("Handling Strategic Grid (Step 12)")
    
    result = await strategic_grid_generator.execute(state)
    grid_data = result.get("output", {})
    
    state["step_data"]["strategic_grid"] = grid_data
    
    state["onboarding_progress"] = (12 / 23) * 100
    return state

async def handle_positioning_statements(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 13: Generate Final Positioning Statements."""
    logger.info("Handling Positioning Statements (Step 13)")
    
    result = await positioning_generator.execute(state)
    positioning_data = result.get("output", {})
    
    state["positioning"] = positioning_data
    state["step_data"]["positioning_statements"] = positioning_data
    
    state["onboarding_progress"] = (13 / 23) * 100
    return state

async def handle_focus_sacrifice(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 14: Recommend Strategic Tradeoffs (Focus vs Sacrifice)."""
    logger.info("Handling Focus & Sacrifice (Step 14)")
    
    result = await focus_sacrifice_engine.execute(state)
    tradeoff_data = result.get("output", {})
    
    state["step_data"]["focus_sacrifice"] = tradeoff_data
    
    state["onboarding_progress"] = (14 / 23) * 100
    return state

async def handle_icp_profiles(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 15: Generate Comprehensive ICP Profiles."""
    logger.info("Handling ICP Profiles (Step 15)")
    
    result = await icp_generator.execute(state)
    icp_data = result.get("output", {})
    
    state["icp_profiles"] = icp_data.get("profiles", [])
    state["step_data"]["icp_profiles"] = icp_data
    
    state["onboarding_progress"] = (15 / 23) * 100
    return state

async def handle_buying_process(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 16: Architect the Buying Process & Sales Cycle."""
    logger.info("Handling Buying Process (Step 16)")
    
    result = await buying_process_architect.execute(state)
    buying_data = result.get("output", {})
    
    state["step_data"]["buying_process"] = buying_data
    
    state["onboarding_progress"] = (16 / 23) * 100
    return state

async def handle_messaging_guardrails(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 17: Define Messaging Guardrails & Brand Rules."""
    logger.info("Handling Messaging Guardrails (Step 17)")
    
    result = await messaging_rules_engine.execute(state)
    rules_data = result.get("output", {})
    
    state["step_data"]["messaging_guardrails"] = rules_data
    
    state["onboarding_progress"] = (17 / 23) * 100
    return state

async def handle_soundbites_library(state: OnboardingStateV2) -> OnboardingStateV2:
    """Step 18: Generate High-Impact Soundbites & Messaging Library."""
    logger.info("Handling Soundbites Library (Step 18)")
    
    result = await soundbites_generator.execute(state)
    library_data = result.get("output", {})
    
    state["step_data"]["soundbites_library"] = library_data
    
    state["onboarding_progress"] = (18 / 23) * 100
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
        workflow.add_node("handle_offer_pricing", handle_offer_pricing)
        workflow.add_node("handle_market_intelligence", handle_market_intelligence)
        workflow.add_node("handle_comparative_angle", handle_comparative_angle)
        workflow.add_node("handle_category_paths", handle_category_paths)
        workflow.add_node("handle_capability_rating", handle_capability_rating)
        workflow.add_node("handle_perceptual_map", handle_perceptual_map)
        workflow.add_node("handle_strategic_grid", handle_strategic_grid)
        workflow.add_node("handle_positioning_statements", handle_positioning_statements)
        workflow.add_node("handle_focus_sacrifice", handle_focus_sacrifice)
        workflow.add_node("handle_icp_profiles", handle_icp_profiles)
        workflow.add_node("handle_buying_process", handle_buying_process)
        workflow.add_node("handle_messaging_guardrails", handle_messaging_guardrails)
        workflow.add_node("handle_soundbites_library", handle_soundbites_library)
        
        # Add remaining nodes as placeholders
        for step in self.step_order[18:]:
            workflow.add_node(f"handle_{step}", generic_handler)

        # Set entry point
        workflow.set_entry_point("handle_evidence_vault")

        # Routing
        workflow.add_edge("handle_evidence_vault", "handle_auto_extraction")
        workflow.add_edge("handle_auto_extraction", "handle_data_purge")
        workflow.add_edge("handle_data_purge", "handle_contradiction_check")
        workflow.add_edge("handle_contradiction_check", "handle_truth_sheet")
        workflow.add_edge("handle_truth_sheet", "handle_brand_audit")
        workflow.add_edge("handle_brand_audit", "handle_offer_pricing")
        workflow.add_edge("handle_offer_pricing", "handle_market_intelligence")
        workflow.add_edge("handle_market_intelligence", "handle_comparative_angle")
        workflow.add_edge("handle_comparative_angle", "handle_category_paths")
        workflow.add_edge("handle_category_paths", "handle_capability_rating")
        workflow.add_edge("handle_capability_rating", "handle_perceptual_map")
        workflow.add_edge("handle_perceptual_map", "handle_strategic_grid")
        workflow.add_edge("handle_strategic_grid", "handle_positioning_statements")
        workflow.add_edge("handle_positioning_statements", "handle_focus_sacrifice")
        workflow.add_edge("handle_focus_sacrifice", "handle_icp_profiles")
        workflow.add_edge("handle_icp_profiles", "handle_buying_process")
        workflow.add_edge("handle_buying_process", "handle_messaging_guardrails")
        workflow.add_edge("handle_messaging_guardrails", "handle_soundbites_library")

        # Remaining linear routing
        for i in range(18, len(self.step_order) - 1):
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
    "handle_brand_audit",
    "handle_offer_pricing",
    "handle_market_intelligence",
    "handle_comparative_angle",
    "handle_category_paths",
    "handle_capability_rating",
    "handle_perceptual_map",
    "handle_strategic_grid",
    "handle_positioning_statements",
    "handle_focus_sacrifice",
    "handle_icp_profiles",
    "handle_buying_process",
    "handle_messaging_guardrails",
    "handle_soundbites_library"
]
