"""
Cognitive Engine Module

This module implements the cognitive processing pipeline for Raptorflow agents.
It provides perception, planning, reflection, and human-in-the-loop capabilities.
"""

from .critic import AdversarialCritic

# Import main engine
from .engine import CognitiveEngine
from .hitl import ApprovalGate

# Import models first - they don't depend on other modules
from .models import ExecutionPlan, PerceivedInput, ReflectionResult

# Import core modules
from .perception import PerceptionModule
from .planning import PlanningModule

# Import protocols
from .protocols import AgentMessage, HandoffProtocol, MessageFormat
from .reflection import ReflectionModule

__all__ = [
    # Core classes
    "CognitiveEngine",
    "PerceptionModule",
    "PlanningModule",
    "ReflectionModule",
    "ApprovalGate",
    "AdversarialCritic",
    # Protocol classes
    "AgentMessage",
    "MessageFormat",
    "HandoffProtocol",
    # Data models
    "PerceivedInput",
    "ExecutionPlan",
    "ReflectionResult",
]
