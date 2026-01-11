"""
Reflection Module Data Models

Defines data structures for quality assessment, critique, and improvement.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Issue:
    """Issue found in content during reflection."""

    severity: Severity
    dimension: str
    description: str
    location: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class QualityScore:
    """Quality assessment of agent output."""

    overall: int  # 0-100
    dimensions: Dict[str, int]  # Individual dimension scores
    issues: List[Issue]
    passed: bool  # Meets quality threshold


@dataclass
class Critique:
    """Self-critique of output."""

    issues: List[Issue]
    severity_counts: Dict[Severity, int]
    recommendations: List[str]
    overall_assessment: str


@dataclass
class Correction:
    """Correction to be applied to content."""

    target: str  # What to correct
    action: str  # How to correct it
    expected_improvement: str  # What improvement is expected


@dataclass
class BrandCheckResult:
    """Result of brand compliance check."""

    compliant: bool
    violations: List[Issue]
    suggestions: List[str]


@dataclass
class FactCheckResult:
    """Result of fact checking."""

    verified_claims: List[str]
    unverified_claims: List[str]
    contradictions: List[str]
    confidence_score: float


@dataclass
class ConsistencyResult:
    """Result of consistency checking."""

    consistent: bool
    inconsistencies: List[Issue]
    recommended_changes: List[str]


@dataclass
class OriginalityResult:
    """Result of originality/plagiarism check."""

    score: float  # 0-1, higher is more original
    similar_sources: List[Dict[str, Any]]
    potential_plagiarism: bool


@dataclass
class ToneAnalysisResult:
    """Result of tone analysis."""

    detected_tone: str
    matches_target: bool
    adjustments_needed: List[str]


@dataclass
class ReadabilityResult:
    """Result of readability analysis."""

    flesch_kincaid_grade: float
    avg_sentence_length: float
    complex_word_percentage: float
    suggestions: List[str]


@dataclass
class SEOCheckResult:
    """Result of SEO checking."""

    keyword_density: Dict[str, float]
    title_optimization: Issue
    meta_suggestions: List[str]
    internal_link_opportunities: List[str]


@dataclass
class ReflectionResult:
    """Complete reflection result."""

    initial_score: QualityScore
    final_score: QualityScore
    corrections_applied: List[Correction]
    iterations: int
    approved: bool
    processing_time: float
    timestamp: datetime
