"""
Meta-learning module for RaptorFlow.

This module provides machine learning capabilities for:
- Performance pattern analysis across campaigns and content
- Cross-workspace knowledge transfer
- Predictive model updates and drift detection
- Continuous experimentation and A/B testing

Components:
- PerformanceAnalyzer: Identifies winning/losing patterns from historical data
- TransferLearner: Transfers insights across workspaces
- ModelUpdater: Manages model retraining and drift detection
- ExperimentEngine: Runs continuous experiments and measures outcomes
"""

from backend.meta_learning.performance_analyzer import PerformanceAnalyzer
from backend.meta_learning.transfer_learner import TransferLearner
from backend.meta_learning.model_updater import ModelUpdater
from backend.meta_learning.experiment_engine import ExperimentEngine

__all__ = [
    "PerformanceAnalyzer",
    "TransferLearner",
    "ModelUpdater",
    "ExperimentEngine",
]
