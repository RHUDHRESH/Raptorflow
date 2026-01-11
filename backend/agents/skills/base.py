"""
Base classes for skills system.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SkillCategory(str, Enum):
    """Categories of skills."""

    CONTENT = "content"
    RESEARCH = "research"
    STRATEGY = "strategy"
    ANALYTICS = "analytics"
    TECHNICAL = "technical"
    COMMUNICATION = "communication"
    CREATIVE = "creative"
    OPERATIONS = "operations"


class SkillLevel(str, Enum):
    """Proficiency levels for skills."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class Skill:
    """Individual skill definition."""

    name: str
    category: SkillCategory
    level: SkillLevel
    description: str
    prerequisites: List[str] = None
    tools_required: List[str] = None
    capabilities: List[str] = None
    examples: List[str] = None
    certification_required: bool = False

    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.tools_required is None:
            self.tools_required = []
        if self.capabilities is None:
            self.capabilities = []
        if self.examples is None:
            self.examples = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary."""
        return {
            "name": self.name,
            "category": self.category.value,
            "level": self.level.value,
            "description": self.description,
            "prerequisites": self.prerequisites,
            "tools_required": self.tools_required,
            "capabilities": self.capabilities,
            "examples": self.examples,
            "certification_required": self.certification_required,
        }

    def can_execute(self, agent_tools: List[str]) -> bool:
        """Check if agent has required tools for this skill."""
        missing_tools = set(self.tools_required) - set(agent_tools)
        if missing_tools:
            logger.warning(
                f"Skill '{self.name}' requires missing tools: {missing_tools}"
            )
            return False
        return True

    def meets_prerequisites(self, agent_skills: List[str]) -> bool:
        """Check if agent meets skill prerequisites."""
        missing_skills = set(self.prerequisites) - set(agent_skills)
        if missing_skills:
            logger.warning(
                f"Skill '{self.name}' requires missing prerequisites: {missing_skills}"
            )
            return False
        return True


@dataclass
class SkillAssessment:
    """Assessment of an agent's skill proficiency."""

    skill_name: str
    current_level: SkillLevel
    assessed_level: SkillLevel
    confidence: float  # 0.0 to 1.0
    evidence: List[str]
    recommendations: List[str]
    next_steps: List[str]
    assessment_date: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary."""
        return {
            "skill_name": self.skill_name,
            "current_level": self.current_level.value,
            "assessed_level": self.assessed_level.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "recommendations": self.recommendations,
            "next_steps": self.next_steps,
            "assessment_date": self.assessment_date,
        }


@dataclass
class SkillPath:
    """Learning path for skill development."""

    skill_name: str
    target_level: SkillLevel
    current_level: SkillLevel
    steps: List[Dict[str, Any]]
    estimated_duration_hours: int
    resources: List[str]
    milestones: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert skill path to dictionary."""
        return {
            "skill_name": self.skill_name,
            "target_level": self.target_level.value,
            "current_level": self.current_level.value,
            "steps": self.steps,
            "estimated_duration_hours": self.estimated_duration_hours,
            "resources": self.resources,
            "milestones": self.milestones,
        }
