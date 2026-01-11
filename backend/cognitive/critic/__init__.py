"""
Adversarial Critic Module - Advanced Quality Assurance

Provides adversarial critique, bias detection, failure mode analysis,
and comprehensive quality assessment from multiple perspectives.
"""

from .adversarial import AdversarialCritic
from .bias_detector import BiasDetector
from .competitor_lens import CompetitorLens
from .customer_lens import CustomerLens
from .edge_cases import EdgeCaseTester
from .failure_modes import FailureModeAnalyzer
from .red_team import RedTeamAgent

__all__ = [
    "AdversarialCritic",
    "RedTeamAgent",
    "BiasDetector",
    "FailureModeAnalyzer",
    "EdgeCaseTester",
    "CompetitorLens",
    "CustomerLens",
]
