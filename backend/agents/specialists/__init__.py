"""
Raptorflow Specialists Package
==============================

Comprehensive specialist agents package for the Raptorflow AI agent system.
Provides specialized AI agents for different business functions and tasks.

Specialist Categories:
- Onboarding & Customer Success
- Strategy & Planning
- Content & Marketing
- Analytics & Intelligence
- Communication & Outreach
- Quality & Optimization

Agent Capabilities:
- Domain-specific expertise
- Specialized tool integration
- Custom workflows and processes
- Performance metrics and KPIs
- Inter-agent collaboration
- Context-aware decision making
"""

from typing import Any, Dict, List, Type

import structlog

logger = structlog.get_logger(__name__)

from .analytics_agent import AnalyticsAgent
from .blackbox_strategist import BlackboxStrategist
from .blog_writer import BlogWriter
from .campaign_planner import CampaignPlanner
from .competitor_intel import CompetitorIntelAgent
from .content_creator import ContentCreator
from .daily_wins import DailyWinsGenerator
from .email_specialist import EmailSpecialist
from .evidence_processor import EvidenceProcessor
from .fact_extractor import FactExtractor
from .icp_architect import ICPArchitect
from .market_research import MarketResearch
from .move_strategist import MoveStrategist

# Import all specialist agents
from .onboarding_orchestrator import OnboardingOrchestrator
from .persona_simulator import PersonaSimulator
from .quality_checker import QualityChecker
from .revision_agent import RevisionAgent
from .social_media_agent import SocialMediaAgent
from .trend_analyzer import TrendAnalyzer

# 23-step onboarding specialist agents
from .evidence_classifier import EvidenceClassifier
from .extraction_orchestrator import ExtractionOrchestrator
from .contradiction_detector import ContradictionDetector
from .reddit_researcher import RedditResearcher
from .perceptual_map_generator import PerceptualMapGenerator
from .neuroscience_copywriter import NeuroscienceCopywriter
from .channel_recommender import ChannelRecommender
from .category_advisor import CategoryAdvisor
from .market_size_calculator import MarketSizeCalculator
from .competitor_analyzer import CompetitorAnalyzer
from .focus_sacrifice_engine import FocusSacrificeEngine
from .proof_point_validator import ProofPointValidator
from .truth_sheet_generator import TruthSheetGenerator
from .messaging_rules_engine import MessagingRulesEngine
from .soundbites_generator import SoundbitesGenerator
from .icp_deep_generator import ICPDeepGenerator
from .positioning_statement_generator import PositioningStatementGenerator
from .launch_readiness_checker import LaunchReadinessChecker
from .channel_strategy_optimizer import ChannelStrategyOptimizer

# Specialist registry
SPECIALIST_REGISTRY: Dict[str, Type] = {
    "OnboardingOrchestrator": OnboardingOrchestrator,
    "EvidenceProcessor": EvidenceProcessor,
    "FactExtractor": FactExtractor,
    "ICPArchitect": ICPArchitect,
    "MoveStrategist": MoveStrategist,
    "ContentCreator": ContentCreator,
    "CampaignPlanner": CampaignPlanner,
    "BlackboxStrategist": BlackboxStrategist,
    "MarketResearch": MarketResearch,
    "AnalyticsAgent": AnalyticsAgent,
    "DailyWinsGenerator": DailyWinsGenerator,
    "EmailSpecialist": EmailSpecialist,
    "SocialMediaAgent": SocialMediaAgent,
    "BlogWriter": BlogWriter,
    "QualityChecker": QualityChecker,
    "RevisionAgent": RevisionAgent,
    "CompetitorIntel": CompetitorIntelAgent,
    "TrendAnalyzer": TrendAnalyzer,
    "PersonaSimulator": PersonaSimulator,
    # 23-step onboarding agents
    "EvidenceClassifier": EvidenceClassifier,
    "ExtractionOrchestrator": ExtractionOrchestrator,
    "ContradictionDetector": ContradictionDetector,
    "RedditResearcher": RedditResearcher,
    "PerceptualMapGenerator": PerceptualMapGenerator,
    "NeuroscienceCopywriter": NeuroscienceCopywriter,
    "ChannelRecommender": ChannelRecommender,
    "CategoryAdvisor": CategoryAdvisor,
    "MarketSizeCalculator": MarketSizeCalculator,
    "CompetitorAnalyzer": CompetitorAnalyzer,
    "FocusSacrificeEngine": FocusSacrificeEngine,
    "ProofPointValidator": ProofPointValidator,
    "TruthSheetGenerator": TruthSheetGenerator,
    "MessagingRulesEngine": MessagingRulesEngine,
    "SoundbitesGenerator": SoundbitesGenerator,
    "ICPDeepGenerator": ICPDeepGenerator,
    "PositioningStatementGenerator": PositioningStatementGenerator,
    "LaunchReadinessChecker": LaunchReadinessChecker,
    "ChannelStrategyOptimizer": ChannelStrategyOptimizer,
}

# Specialist categories
SPECIALIST_CATEGORIES = {
    "onboarding": [
        "OnboardingOrchestrator",
        "EvidenceProcessor",
        "FactExtractor",
        "EvidenceClassifier",
        "ExtractionOrchestrator",
        "ContradictionDetector",
        "CategoryAdvisor",
        "ProofPointValidator",
        "TruthSheetGenerator",
        "MessagingRulesEngine",
        "SoundbitesGenerator",
    ],
    "strategy": [
        "ICPArchitect",
        "MoveStrategist",
        "BlackboxStrategist",
        "ChannelRecommender",
    ],
    "content": [
        "ContentCreator",
        "CampaignPlanner",
        "BlogWriter",
        "NeuroscienceCopywriter",
    ],
    "intelligence": [
        "MarketResearch",
        "AnalyticsAgent",
        "CompetitorIntelAgent",
        "TrendAnalyzer",
        "RedditResearcher",
        "PerceptualMapGenerator",
        "MarketSizeCalculator",
    ],
    "communication": [
        "DailyWinsGenerator",
        "EmailSpecialist",
        "SocialMediaAgent",
    ],
    "optimization": [
        "QualityChecker",
        "RevisionAgent",
        "PersonaSimulator",
    ],
}


def get_specialist(specialist_name: str) -> Type:
    """Get a specialist class by name."""
    if specialist_name not in SPECIALIST_REGISTRY:
        raise ValueError(f"Specialist not found: {specialist_name}")
    return SPECIALIST_REGISTRY[specialist_name]


def list_specialists(category: str = None) -> List[str]:
    """List all available specialists, optionally filtered by category."""
    if category:
        return SPECIALIST_CATEGORIES.get(category, [])
    return list(SPECIALIST_REGISTRY.keys())


def get_specialist_info(specialist_name: str) -> Dict[str, Any]:
    """Get information about a specialist."""
    specialist_class = get_specialist(specialist_name)
    return {
        "name": specialist_class.__name__,
        "description": specialist_class.__doc__ or "",
        "category": getattr(specialist_class, "CATEGORY", "unknown"),
        "version": getattr(specialist_class, "VERSION", "1.0.0"),
        "author": getattr(specialist_class, "AUTHOR", "Raptorflow Team"),
        "capabilities": getattr(specialist_class, "CAPABILITIES", []),
        "tools": getattr(specialist_class, "TOOLS", []),
        "workflows": getattr(specialist_class, "WORKFLOWS", []),
    }


def get_all_specialists_info() -> Dict[str, Dict[str, Any]]:
    """Get information about all specialists."""
    return {
        specialist_name: get_specialist_info(specialist_name)
        for specialist_name in SPECIALIST_REGISTRY
    }


# Specialist factory
class SpecialistFactory:
    """Factory for creating specialist instances."""

    @staticmethod
    def create_specialist(specialist_name: str, config: Dict[str, Any] = None):
        """Create a specialist instance."""
        specialist_class = get_specialist(specialist_name)
        return specialist_class(config or {})

    @staticmethod
    def create_specialists(
        specialist_configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create multiple specialist instances."""
        specialists = {}
        for specialist_name, config in specialist_configs.items():
            specialists[specialist_name] = SpecialistFactory.create_specialist(
                specialist_name, config
            )
        return specialists


# Specialist manager
class SpecialistManager:
    """Manager for specialist instances and operations."""

    def __init__(self):
        self.specialists: Dict[str, Any] = {}
        self.specialist_configs: Dict[str, Dict[str, Any]] = {}
        self.active_workflows: Dict[str, Any] = {}

    def add_specialist(self, specialist_name: str, config: Dict[str, Any] = None):
        """Add a specialist instance."""
        specialist = SpecialistFactory.create_specialist(specialist_name, config)
        self.specialists[specialist_name] = specialist
        self.specialist_configs[specialist_name] = config or {}
        return specialist

    def remove_specialist(self, specialist_name: str) -> bool:
        """Remove a specialist instance."""
        if specialist_name in self.specialists:
            del self.specialists[specialist_name]
            del self.specialist_configs[specialist_name]
            return True
        return False

    def get_specialist(self, specialist_name: str):
        """Get a specialist instance."""
        if specialist_name not in self.specialists:
            raise ValueError(f"Specialist not found: {specialist_name}")
        return self.specialists[specialist_name]

    def list_specialists(self) -> List[str]:
        """List all specialist instances."""
        return list(self.specialists.keys())

    def execute_specialist(self, specialist_name: str, **kwargs):
        """Execute a specialist."""
        specialist = self.get_specialist(specialist_name)
        return specialist.execute(**kwargs)

    def get_specialist_status(self, specialist_name: str) -> Dict[str, Any]:
        """Get specialist status."""
        specialist = self.get_specialist(specialist_name)
        return specialist.get_status()

    def get_all_specialists_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all specialists."""
        return {name: self.get_specialist_status(name) for name in self.specialists}

    def cleanup(self):
        """Cleanup all specialists."""
        for specialist in self.specialists.values():
            if hasattr(specialist, "cleanup"):
                specialist.cleanup()
        self.specialists.clear()
        self.specialist_configs.clear()
        self.active_workflows.clear()


# Global specialist manager instance
specialist_manager = SpecialistManager()

# Export all components
__all__ = [
    # Specialist agents
    "OnboardingOrchestrator",
    "EvidenceProcessor",
    "FactExtractor",
    "ICPArchitect",
    "MoveStrategist",
    "ContentCreator",
    "CampaignPlanner",
    "BlackboxStrategist",
    "MarketResearch",
    "AnalyticsAgent",
    "DailyWinsGenerator",
    "EmailSpecialist",
    "SocialMediaAgent",
    "BlogWriter",
    "QualityChecker",
    "RevisionAgent",
    "CompetitorIntelAgent",
    "TrendAnalyzer",
    "PersonaSimulator",
    # 23-step onboarding agents
    "EvidenceClassifier",
    "ExtractionOrchestrator",
    "ContradictionDetector",
    "RedditResearcher",
    "PerceptualMapGenerator",
    "NeuroscienceCopywriter",
    "ChannelRecommender",
    "CategoryAdvisor",
    "MarketSizeCalculator",
    "CompetitorAnalyzer",
    "FocusSacrificeEngine",
    "ProofPointValidator",
    "TruthSheetGenerator",
    "MessagingRulesEngine",
    "SoundbitesGenerator",
    "ICPDeepGenerator",
    "PositioningStatementGenerator",
    "LaunchReadinessChecker",
    "ChannelStrategyOptimizer",
    # Registry and management
    "SPECIALIST_REGISTRY",
    "SPECIALIST_CATEGORIES",
    "get_specialist",
    "list_specialists",
    "get_specialist_info",
    "get_all_specialists_info",
    # Factory and manager
    "SpecialistFactory",
    "SpecialistManager",
    "specialist_manager",
]
