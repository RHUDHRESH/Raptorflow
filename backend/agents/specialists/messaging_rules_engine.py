"""
Messaging Rules Engine
Generates and enforces brand messaging guardrails
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import re

from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)


class RuleCategory(Enum):
    """Categories for messaging rules"""
    TONE = "tone"
    LANGUAGE = "language"
    CLAIMS = "claims"
    COMPETITORS = "competitors"
    PRICING = "pricing"
    LEGAL = "legal"
    BRAND = "brand"


class RuleSeverity(Enum):
    """Severity level of rule violations"""
    ERROR = "error"
    WARNING = "warning"
    SUGGESTION = "suggestion"


class RuleStatus(Enum):
    """Status of a rule"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


@dataclass
class MessagingRule:
    """A single messaging rule/guardrail"""
    id: str
    category: RuleCategory
    name: str
    description: str
    pattern: Optional[str] = None
    examples_good: List[str] = field(default_factory=list)
    examples_bad: List[str] = field(default_factory=list)
    severity: RuleSeverity = RuleSeverity.WARNING
    status: RuleStatus = RuleStatus.ACTIVE
    auto_generated: bool = True
    rationale: str = ""

    def to_dict(self):
        d = asdict(self)
        d["category"] = self.category.value
        d["severity"] = self.severity.value
        d["status"] = self.status.value
        return d


@dataclass
class MessagingRulesResult:
    """Complete messaging rules result"""
    rules: List[MessagingRule]
    rule_count: int
    categories_covered: List[str]
    recommendations: List[str]
    summary: str

    def to_dict(self):
        return {
            "rules": [r.to_dict() for r in self.rules],
            "rule_count": self.rule_count,
            "categories_covered": self.categories_covered,
            "recommendations": self.recommendations,
            "summary": self.summary
        }


class MessagingRulesEngine(BaseAgent):
    """AI-powered messaging rules and guardrails engine"""
    
    def __init__(self):
        super().__init__(
            name="MessagingRulesEngine",
            description="Generates and enforces messaging guardrails",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["brand_governance", "copywriting_standards", "compliance_enforcement"]
        )
        self.rule_counter = 0

    def get_system_prompt(self) -> str:
        return """You are the MessagingRulesEngine.
        Your goal is to define 'Guardrails' for brand communication.
        Define what we say (Voice), how we say it (Tone), and what we never say (Anti-Patterns)."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute rules generation using current state."""
        company_info = state.get("business_context", {}).get("identity", {})
        positioning = state.get("positioning", {})
        
        result = await self.generate_messaging_rules(company_info, positioning)
        return {"output": result.to_dict()}
    
    def _generate_rule_id(self) -> str:
        self.rule_counter += 1
        return f"RUL-{self.rule_counter:03d}"

    async def generate_messaging_rules(self, company_info: Dict[str, Any], positioning: Dict[str, Any] = None) -> MessagingRulesResult:
        """Generation logic"""
        rules = [
            MessagingRule(
                id=self._generate_rule_id(),
                category=RuleCategory.TONE,
                name="Scientific Precision",
                description="Use data-backed claims, avoid hype",
                severity=RuleSeverity.WARNING,
                rationale="Enterprise security buyers trust data over hype"
            ),
            MessagingRule(
                id=self._generate_rule_id(),
                category=RuleCategory.LEGAL,
                name="No 100% Guarantees",
                description="Never promise 100% security",
                severity=RuleSeverity.ERROR,
                rationale="Legally dangerous and factually impossible"
            )
        ]
        
        return MessagingRulesResult(
            rules=rules,
            rule_count=len(rules),
            categories_covered=["tone", "legal"],
            recommendations=["Verify with legal team"],
            summary="Messaging guardrails established."
        )