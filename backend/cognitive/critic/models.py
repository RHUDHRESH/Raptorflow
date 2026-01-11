"""
Critic Module Data Models

Defines data structures for adversarial critique, vulnerability analysis,
and quality assessment from multiple perspectives.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class VulnerabilityType(str, Enum):
    FACTUAL = "factual"
    LOGICAL = "logical"
    QUALITY = "quality"
    SECURITY = "security"
    BRAND = "brand"
    LEGAL = "legal"
    ACCESSIBILITY = "accessibility"
    BIAS = "bias"
    TECHNICAL = "technical"
    COMPETITIVE = "competitive"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BiasType(str, Enum):
    GENDER = "gender"
    RACIAL = "racial"
    POLITICAL = "political"
    AGE = "age"
    CULTURAL = "cultural"
    ECONOMIC = "economic"
    RELIGIOUS = "religious"
    ABILITY = "ability"


@dataclass
class Vulnerability:
    """Identified vulnerability or weakness."""

    category: VulnerabilityType
    severity: Severity
    description: str
    location: Optional[str] = None
    impact: str = ""
    mitigation: str = ""
    confidence: float = 0.8


@dataclass
class BiasReport:
    """Result of bias detection."""

    detected_biases: List[Dict[str, Any]]
    severity: Severity
    locations: List[str]
    suggestions: List[str]
    overall_bias_score: float


@dataclass
class FailureMode:
    """Potential failure mode."""

    mode: str
    probability: float
    impact: Severity
    description: str
    mitigations: List[str]
    detection_methods: List[str]


@dataclass
class EdgeCase:
    """Edge case for testing."""

    scenario: str
    description: str
    test_input: str
    expected_behavior: str
    risk_level: Severity


@dataclass
class CompetitorCritique:
    """Critique from competitor perspective."""

    competitor_name: str
    attack_points: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threat_level: Severity


@dataclass
class CustomerCritique:
    """Critique from customer perspective."""

    icp_name: str
    trust_level: float
    belief_score: float
    actionability: float
    concerns: List[str]
    improvements: List[str]
