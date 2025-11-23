"""
Predictive Performance Engine for RaptorFlow.

This package provides comprehensive content performance prediction and optimization:
- Engagement prediction using ML models
- Conversion optimization with CTA analysis
- Viral potential scoring
- A/B test orchestration
- Competitive benchmarking

All modules integrate with the memory system for continuous learning and
connect to Supabase for historical data analysis.
"""

from .engagement_predictor import EngagementPredictor
from .conversion_optimizer import ConversionOptimizer
from .viral_potential_scorer import ViralPotentialScorer
from .ab_test_orchestrator import ABTestOrchestrator
from .competitive_benchmarker import CompetitiveBenchmarker
from .performance_memory import PerformanceMemory

__all__ = [
    "EngagementPredictor",
    "ConversionOptimizer",
    "ViralPotentialScorer",
    "ABTestOrchestrator",
    "CompetitiveBenchmarker",
    "PerformanceMemory",
]
