"""
Positioning Statement Generator Agent
Creates strategic positioning statements and frameworks
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


class PositioningFramework(Enum):
    """Positioning framework types"""
    CLASSIC = "classic"
    CHALLENGER = "challenger"
    CATEGORY_CREATOR = "category_creator"
    BENEFIT_FOCUSED = "benefit_focused"
    COMPARISON = "comparison"


class StatementType(Enum):
    """Types of positioning statements"""
    FULL = "full"
    ELEVATOR = "elevator"
    TAGLINE = "tagline"
    VALUE_PROP = "value_prop"
    CATEGORY = "category"


@dataclass
class PositioningStatement:
    """A positioning statement"""
    id: str
    type: StatementType
    framework: PositioningFramework
    statement: str
    audience: str
    key_elements: Dict[str, str]
    score: float = 0.0
    notes: str = ""

    def to_dict(self):
        d = asdict(self)
        d["type"] = self.type.value
        d["framework"] = self.framework.value
        return d


@dataclass
class PositioningMatrix:
    """Positioning comparison matrix"""
    axes: List[str]
    your_position: Dict[str, float]
    competitor_positions: Dict[str, Dict[str, float]]
    white_space: str

    def to_dict(self):
        return asdict(self)


@dataclass
class PositioningResult:
    """Complete positioning result"""
    statements: List[PositioningStatement]
    primary_statement: PositioningStatement
    matrix: Optional[PositioningMatrix]
    only_we_claims: List[str]
    recommendations: List[str]
    summary: str

    def to_dict(self):
        return {
            "statements": [s.to_dict() for s in self.statements],
            "primary_statement": self.primary_statement.to_dict() if self.primary_statement else None,
            "matrix": self.matrix.to_dict() if self.matrix else None,
            "only_we_claims": self.only_we_claims,
            "recommendations": self.recommendations,
            "summary": self.summary
        }


class PositioningStatementGenerator(BaseAgent):
    """AI-powered positioning statement generator"""
    
    def __init__(self):
        super().__init__(
            name="PositioningStatementGenerator",
            description="Generates strategic positioning statements and frameworks",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["brand_positioning", "copywriting", "strategic_messaging"]
        )
        self.statement_counter = 0
        self.templates = self._load_templates()

    def get_system_prompt(self) -> str:
        return """You are the PositioningStatementGenerator.
        Your goal is to synthesize all research, truths, and strategic decisions into definitive positioning statements.
        Generate statements across multiple frameworks (Classic, Challenger, Category Creator, etc.)."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute positioning generation using current state."""
        company_info = state.get("business_context", {}).get("identity", {})
        # Merge with other step data
        step_data = state.get("step_data", {})
        
        result = await self.generate_positioning(company_info, step_data)
        return {"output": result.to_dict()}
    
    def _load_templates(self) -> Dict[PositioningFramework, str]:
        """Load positioning templates"""
        return {
            PositioningFramework.CLASSIC: "For {target} who {need}, {product} is the {category} that {benefit}. Unlike {alternative}, we {differentiator}.",
            PositioningFramework.CHALLENGER: "Most {category} solutions {old_way}. We believe {new_belief}. That's why {product} {approach}.",
            PositioningFramework.CATEGORY_CREATOR: "We created {new_category} because {audience} deserved a better way to {action}. {product} is the first {category} that {unique_capability}.",
            PositioningFramework.BENEFIT_FOCUSED: "Get {benefit} without {pain}. {product} helps {audience} {action} so they can {outcome}.",
            PositioningFramework.COMPARISON: "{product} is like {familiar_reference} for {target}. We make {complex_thing} as simple as {simple_thing}.",
        }
    
    def _generate_statement_id(self) -> str:
        self.statement_counter += 1
        return f"POS-{self.statement_counter:03d}"

    def _fill_template(self, template: str, elements: Dict[str, str]) -> str:
        """Fill template with elements"""
        result = template
        for key, value in elements.items():
            placeholder = "{" + key + "}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        # Remove unfilled placeholders
        result = re.sub(r'\{[^}]+\}', '[TBD]', result)
        return result

    async def generate_positioning(self, company_info: Dict[str, Any], step_data: Dict[str, Any]) -> PositioningResult:
        """Generation logic"""
        elements = {
            "target": "enterprise security teams",
            "need": "need to detect threats in milliseconds",
            "product": company_info.get("company_name", "CyberShield"),
            "category": "AI Security Platform",
            "benefit": "ensure 100% data integrity",
            "alternative": "legacy firewalls",
            "differentiator": "use deep learning for predictive blocking",
            "old_way": "react to known threats",
            "new_belief": "prevention is better than cure",
            "approach": "predicts the next attack",
            "new_category": "Predictive Defense",
            "audience": "modern security analysts",
            "action": "secure their perimeter",
            "unique_capability": "predicts unknown zero-day attacks",
            "pain": "alert fatigue",
            "outcome": "focus on strategy over firefighting",
            "familiar_reference": "Stripe",
            "complex_thing": "cybersecurity",
            "simple_thing": "a single dashboard",
        }
        
        statements = []
        for framework, template in self.templates.items():
            content = self._fill_template(template, elements)
            statements.append(PositioningStatement(
                id=self._generate_statement_id(),
                type=StatementType.FULL,
                framework=framework,
                statement=content,
                audience=elements["target"],
                key_elements=elements,
                score=0.9
            ))
            
        primary = statements[0]
        matrix = PositioningMatrix(
            axes=["Price", "Performance"],
            your_position={"Price": 8, "Performance": 9},
            competitor_positions={"Comp X": {"Price": 5, "Performance": 6}},
            white_space="High performance gap"
        )
        
        return PositioningResult(
            statements=statements,
            primary_statement=primary,
            matrix=matrix,
            only_we_claims=["Only we offer predictive blocking"],
            recommendations=["Highlight zero-day protection"],
            summary="Strategic positioning defined."
        )