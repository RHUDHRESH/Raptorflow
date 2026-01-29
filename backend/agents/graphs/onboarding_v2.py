"""
Onboarding workflow graph v2 for the 23-step "Master System" process.
Uses Reducers to ensure state persistence across nodes.
"""

import logging
import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from specialists.brand_audit_agent import BrandAuditEngine
from specialists.buying_process_agent import BuyingProcessArchitect
from specialists.capability_rating_agent import CapabilityRatingEngine
from specialists.category_advisor import CategoryAdvisor
from specialists.channel_recommender import ChannelRecommender
from specialists.comparative_angle_agent import ComparativeAngleGenerator
from specialists.constraint_engine import ConstraintEngine
from specialists.contradiction_detector import ContradictionDetector
from specialists.evidence_classifier import EvidenceClassifier
from specialists.extraction_orchestrator import ExtractionOrchestrator
from specialists.final_synthesis_agent import FinalSynthesis
from specialists.icp_architect import ICPArchitect
from specialists.insight_extractor import InsightExtractor
from specialists.market_sizer import MarketSizer
from specialists.message_hierarchy_agent import MessageHierarchyArchitect
from specialists.messaging_rules_engine import MessagingRulesEngine
from specialists.neuroscience_copywriter import NeuroscienceCopywriter
from specialists.offer_architect import OfferArchitect

# Import Specialists
from specialists.onboarding_orchestrator_v2 import OnboardingOrchestratorV2
from specialists.perceptual_map_generator import PerceptualMapGenerator
from specialists.soundbites_generator import SoundbitesGenerator
from specialists.strategic_grid_agent import StrategicGridGenerator
from specialists.truth_sheet_generator import TruthSheetGenerator
from specialists.validation_tracker import ValidationTracker

from ...infrastructure.storage import delete_file
from ..services.titan.orchestrator import TitanOrchestrator

logger = logging.getLogger(__name__)


def merge_dict(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Reducer to deeply merge dictionaries with safety checks."""
    if a is None:
        a = {}
    if b is None:
        b = {}

    res = a.copy()
    for k, v in b.items():
        if isinstance(v, dict) and k in res and isinstance(res[k], dict):
            res[k] = merge_dict(res[k], v)
        else:
            res[k] = v
    return res


class OnboardingStateV2(TypedDict):
    """State for onboarding master system with Reducers."""

    business_context: Annotated[Dict[str, Any], merge_dict]
    ucid: str
    current_step: str
    completed_steps: Annotated[List[str], operator.add]
    onboarding_progress: float
    evidence: List[Dict[str, Any]]
    step_data: Annotated[Dict[str, Any], merge_dict]
    contradictions: Annotated[List[Dict[str, Any]], operator.add]
    single_step: bool


# Global Specialists
orchestrator = OnboardingOrchestratorV2()
classifier = EvidenceClassifier()
extractor = ExtractionOrchestrator()
contradiction_detector = ContradictionDetector()
truth_sheet_generator = TruthSheetGenerator()
brand_audit_engine = BrandAuditEngine()
offer_architect = OfferArchitect()
insight_extractor = InsightExtractor()
angle_generator = ComparativeAngleGenerator()
category_advisor = CategoryAdvisor()
capability_rating_engine = CapabilityRatingEngine()
perceptual_map_generator = PerceptualMapGenerator()
strategic_grid_generator = StrategicGridGenerator()
neuroscience_copywriter = NeuroscienceCopywriter()
constraint_engine = ConstraintEngine()
icp_architect = ICPArchitect()
buying_process_architect = BuyingProcessArchitect()
messaging_rules_engine = MessagingRulesEngine()
soundbites_generator = SoundbitesGenerator()
hierarchy_architect = MessageHierarchyArchitect()
channel_recommender = ChannelRecommender()
market_sizer = MarketSizer()
validation_tracker = ValidationTracker()
final_synthesis_agent = FinalSynthesis()

# Tool Helper
reddit_tool_instance = None


def get_reddit_tool():
    global reddit_tool_instance
    if reddit_tool_instance is None:
        try:
            from ...tools.reddit_scraper import RedditScraperTool

            reddit_tool_instance = RedditScraperTool()
        except Exception as e:
            logger.error(f"Failed to init Reddit tool: {e}")
            return None
    return reddit_tool_instance


# --- NODE HANDLERS (Simplified for Reducer compatibility) ---


async def handle_evidence_vault(state: OnboardingStateV2):
    logger.info("Handling Evidence Vault (Step 1)")
    # Logic omitted for brevity, just return updates
    return {"current_step": "evidence_vault", "onboarding_progress": (1 / 23) * 100}


async def handle_auto_extraction(state: OnboardingStateV2):
    logger.info("Handling Auto Extraction (Step 2)")
    return {"current_step": "auto_extraction", "onboarding_progress": (2 / 23) * 100}


async def handle_data_purge(state: OnboardingStateV2):
    logger.info("Handling Data Purge (Lifecycle Enforcement)")
    return {"current_step": "data_purge"}


async def handle_contradiction_check(state: OnboardingStateV2):
    logger.info("Handling Contradiction Check (Step 3)")
    return {
        "current_step": "contradiction_check",
        "onboarding_progress": (3 / 23) * 100,
    }


async def handle_truth_sheet(state: OnboardingStateV2):
    logger.info("Handling Truth Sheet (Step 4)")
    return {"current_step": "truth_sheet", "onboarding_progress": (4 / 23) * 100}


async def handle_brand_audit(state: OnboardingStateV2):
    logger.info("Handling Brand Audit (Step 5)")
    return {"current_step": "brand_audit", "onboarding_progress": (5 / 23) * 100}


async def handle_offer_pricing(state: OnboardingStateV2):
    logger.info("Handling Offer & Pricing (Step 6)")
    result = await offer_architect.execute(state)
    out = result.get("output", {})
    return {
        "current_step": "offer_pricing",
        "step_data": {"offer_pricing": out},
        "business_context": {"offer": {"revenue_model": out.get("revenue_model")}},
        "onboarding_progress": (6 / 23) * 100,
    }


async def handle_market_intelligence(state: OnboardingStateV2):
    logger.info("Handling Market Intelligence (Step 7)")
    return {
        "current_step": "market_intelligence",
        "onboarding_progress": (7 / 23) * 100,
    }


async def handle_comparative_angle(state: OnboardingStateV2):
    logger.info("Handling Comparative Angle (Step 8)")
    return {"current_step": "comparative_angle", "onboarding_progress": (8 / 23) * 100}


async def handle_category_paths(state: OnboardingStateV2):
    logger.info("Handling Category Paths (Step 9)")
    return {"current_step": "category_paths", "onboarding_progress": (9 / 23) * 100}


async def handle_capability_rating(state: OnboardingStateV2):
    logger.info("Handling Capability Rating (Step 10)")
    return {"current_step": "capability_rating", "onboarding_progress": (10 / 23) * 100}


async def handle_perceptual_map(state: OnboardingStateV2):
    logger.info("Handling Perceptual Map (Step 11)")
    return {"current_step": "perceptual_map", "onboarding_progress": (11 / 23) * 100}


async def handle_strategic_grid(state: OnboardingStateV2):
    logger.info("Handling Strategic Grid (Step 12)")
    return {"current_step": "strategic_grid", "onboarding_progress": (12 / 23) * 100}


async def handle_positioning_statements(state: OnboardingStateV2):
    logger.info("Handling Positioning Statements (Step 13)")
    result = await neuroscience_copywriter.execute(state)
    out = result.get("output", {})
    return {
        "current_step": "positioning_statements",
        "step_data": {"positioning_statements": out},
        "business_context": {"positioning": {"manifesto": out.get("manifesto")}},
        "onboarding_progress": (13 / 23) * 100,
    }


async def handle_focus_sacrifice(state: OnboardingStateV2):
    logger.info("Handling Focus & Sacrifice (Step 14)")
    result = await constraint_engine.execute(state)
    out = result.get("output", {})
    return {
        "current_step": "focus_sacrifice",
        "step_data": {"focus_sacrifice": out},
        "business_context": {"strategy": {"logic": out.get("logic")}},
        "onboarding_progress": (14 / 23) * 100,
    }


async def handle_icp_profiles(state: OnboardingStateV2):
    logger.info("Handling ICP Profiles (Step 15)")
    return {"current_step": "icp_profiles", "onboarding_progress": (15 / 23) * 100}


async def handle_buying_process(state: OnboardingStateV2):
    logger.info("Handling Buying Process (Step 16)")
    return {"current_step": "buying_process", "onboarding_progress": (16 / 23) * 100}


async def handle_messaging_guardrails(state: OnboardingStateV2):
    logger.info("Handling Messaging Guardrails (Step 17)")
    return {
        "current_step": "messaging_guardrails",
        "onboarding_progress": (17 / 23) * 100,
    }


async def handle_soundbites_library(state: OnboardingStateV2):
    logger.info("Handling Soundbites Library (Step 18)")
    return {
        "current_step": "soundbites_library",
        "onboarding_progress": (18 / 23) * 100,
    }


async def handle_message_hierarchy(state: OnboardingStateV2):
    logger.info("Handling Message Hierarchy (Step 19)")
    return {"current_step": "message_hierarchy", "onboarding_progress": (19 / 23) * 100}


async def handle_channel_mapping(state: OnboardingStateV2):
    logger.info("Handling Channel Mapping (Step 20)")
    return {"current_step": "channel_mapping", "onboarding_progress": (20 / 23) * 100}


async def handle_tam_sam_som(state: OnboardingStateV2):
    logger.info("Handling TAM/SAM/SOM (Step 21)")
    return {"current_step": "tam_sam_som", "onboarding_progress": (21 / 23) * 100}


async def handle_validation_todos(state: OnboardingStateV2):
    logger.info("Handling Validation Todos (Step 22)")
    return {"current_step": "validation_todos", "onboarding_progress": (22 / 23) * 100}


async def handle_final_synthesis(state: OnboardingStateV2):
    logger.info("Handling Final Synthesis (Step 23)")
    return {"current_step": "final_synthesis", "onboarding_progress": 100.0}


class OnboardingGraphV2:
    def __init__(self):
        self.step_order = [
            "evidence_vault",
            "auto_extraction",
            "data_purge",
            "contradiction_check",
            "truth_sheet",
            "brand_audit",
            "offer_pricing",
            "market_intelligence",
            "comparative_angle",
            "category_paths",
            "capability_rating",
            "perceptual_map",
            "strategic_grid",
            "positioning_statements",
            "focus_sacrifice",
            "icp_profiles",
            "buying_process",
            "messaging_guardrails",
            "soundbites_library",
            "message_hierarchy",
            "channel_mapping",
            "tam_sam_som",
            "validation_todos",
            "final_synthesis",
        ]

    def create_graph(self) -> StateGraph:
        workflow = StateGraph(OnboardingStateV2)
        nodes = [f"handle_{s}" for s in self.step_order]
        for node in nodes:
            workflow.add_node(node, globals()[node])

        def route_to_step(state: OnboardingStateV2) -> str:
            step = state.get("current_step")
            if not step:
                return "handle_evidence_vault"
            node_name = f"handle_{step}"
            return node_name if node_name in nodes else "handle_evidence_vault"

        workflow.set_conditional_entry_point(route_to_step, {n: n for n in nodes})

        def route_next(state: OnboardingStateV2) -> str:
            if state.get("single_step"):
                return END
            current = state.get("current_step", "")
            try:
                idx = self.step_order.index(current)
                if idx < len(self.step_order) - 1:
                    return f"handle_{self.step_order[idx + 1]}"
            except ValueError:
                pass
            return END

        for node in nodes:
            workflow.add_conditional_edges(
                node, route_next, {n: n for n in nodes} | {END: END}
            )

        return workflow.compile(checkpointer=MemorySaver())


__all__ = ["OnboardingGraphV2", "OnboardingStateV2"]
