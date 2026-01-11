"""
Reflection Module - Cognitive Quality Assessment Layer

Evaluates output quality, performs self-correction, and provides
adversarial critique for continuous improvement.
"""

from .brand_checker import BrandChecker
from .consistency_checker import ConsistencyChecker
from .correction_planner import CorrectionPlanner
from .critic import SelfCritic
from .executor import ImprovementExecutor
from .fact_checker import FactChecker
from .learning import ReflectionLearner
from .module import ReflectionModule
from .plagiarism_detector import PlagiarismDetector
from .readability import ReadabilityAnalyzer
from .scorer import QualityScorer
from .seo_checker import SEOChecker
from .tone_analyzer import ToneAnalyzer

__all__ = [
    "ReflectionModule",
    "QualityScorer",
    "SelfCritic",
    "CorrectionPlanner",
    "ImprovementExecutor",
    "BrandChecker",
    "FactChecker",
    "ConsistencyChecker",
    "PlagiarismDetector",
    "ToneAnalyzer",
    "ReadabilityAnalyzer",
    "SEOChecker",
    "ReflectionLearner",
]
