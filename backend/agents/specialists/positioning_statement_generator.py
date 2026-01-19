"""
Positioning Statement Generator Agent
Creates strategic positioning statements and frameworks
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class PositioningFramework(Enum):
    """Positioning framework types"""
    CLASSIC = "classic"  # For [target], [product] is [category] that [benefit]
    CHALLENGER = "challenger"  # Unlike [status quo], we [different approach]
    CATEGORY_CREATOR = "category_creator"  # We invented [new category] for [problem]
    BENEFIT_FOCUSED = "benefit_focused"  # Get [benefit] without [pain]
    COMPARISON = "comparison"  # Like [familiar] but [difference]


class StatementType(Enum):
    """Types of positioning statements"""
    FULL = "full"  # Complete positioning statement
    ELEVATOR = "elevator"  # 30-second pitch
    TAGLINE = "tagline"  # One-liner
    VALUE_PROP = "value_prop"  # Value proposition
    CATEGORY = "category"  # Category definition


@dataclass
class PositioningStatement:
    """A positioning statement"""
    id: str
    type: StatementType
    framework: PositioningFramework
    statement: str
    audience: str
    key_elements: Dict[str, str]  # target, product, category, benefit, etc.
    score: float = 0.0
    notes: str = ""


@dataclass
class PositioningMatrix:
    """Positioning comparison matrix"""
    axes: List[str]  # e.g., ["Price", "Features"]
    your_position: Dict[str, float]  # Position on each axis (0-10)
    competitor_positions: Dict[str, Dict[str, float]]
    white_space: str  # Identified white space


@dataclass
class PositioningResult:
    """Complete positioning result"""
    statements: List[PositioningStatement]
    primary_statement: PositioningStatement
    matrix: Optional[PositioningMatrix]
    only_we_claims: List[str]
    recommendations: List[str]
    summary: str


class PositioningStatementGenerator:
    """AI-powered positioning statement generator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.statement_counter = 0
        self.templates = self._load_templates()
    
    def _generate_statement_id(self) -> str:
        self.statement_counter += 1
        return f"POS-{self.statement_counter:03d}"
    
    def _load_templates(self) -> Dict[str, str]:
        """Load positioning templates"""
        return {
            PositioningFramework.CLASSIC: "For {target} who {need}, {product} is the {category} that {benefit}. Unlike {alternative}, we {differentiator}.",
            PositioningFramework.CHALLENGER: "Most {category} solutions {old_way}. We believe {new_belief}. That's why {product} {approach}.",
            PositioningFramework.CATEGORY_CREATOR: "We created {new_category} because {audience} deserved a better way to {action}. {product} is the first {category} that {unique_capability}.",
            PositioningFramework.BENEFIT_FOCUSED: "Get {benefit} without {pain}. {product} helps {audience} {action} so they can {outcome}.",
            PositioningFramework.COMPARISON: "{product} is like {familiar_reference} for {target}. We make {complex_thing} as simple as {simple_thing}.",
        }
    
    def _fill_template(self, template: str, elements: Dict[str, str]) -> str:
        """Fill template with elements"""
        result = template
        for key, value in elements.items():
            placeholder = "{" + key + "}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        # Remove unfilled placeholders
        import re
        result = re.sub(r'\{[^}]+\}', '[TBD]', result)
        return result
    
    def _generate_elements(self, company_info: Dict[str, Any], positioning: Dict[str, Any], icp_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate positioning elements from inputs"""
        return {
            "target": icp_data.get("name", "growth-focused teams"),
            "need": positioning.get("primary_pain", "need to scale efficiently"),
            "product": company_info.get("product_name", "Our product"),
            "category": company_info.get("category", "solution"),
            "benefit": positioning.get("primary_benefit", "achieve better results"),
            "alternative": positioning.get("alternative", "traditional solutions"),
            "differentiator": positioning.get("differentiator", "focus on outcomes over features"),
            "old_way": "focus on features over outcomes",
            "new_belief": "results matter more than functionality",
            "approach": "measures what matters",
            "new_category": positioning.get("new_category", "outcome-driven software"),
            "audience": icp_data.get("name", "modern teams"),
            "action": company_info.get("core_action", "grow"),
            "unique_capability": positioning.get("unique_capability", "guarantees results"),
            "pain": positioning.get("primary_pain", "complexity"),
            "outcome": positioning.get("outcome", "focus on what matters"),
            "familiar_reference": positioning.get("comparison", "Stripe"),
            "complex_thing": company_info.get("problem_domain", "complex workflows"),
            "simple_thing": positioning.get("simplicity_reference", "a simple dashboard"),
        }
    
    def _score_statement(self, statement: str) -> float:
        """Score a positioning statement"""
        score = 0.5
        
        # Length check (50-200 chars for tagline, more for full)
        length = len(statement)
        if 100 <= length <= 300:
            score += 0.15
        
        # Has specific benefit
        benefit_words = ["help", "achieve", "get", "save", "reduce", "increase", "grow"]
        if any(word in statement.lower() for word in benefit_words):
            score += 0.1
        
        # Has differentiation
        diff_words = ["unlike", "only", "first", "different", "unique"]
        if any(word in statement.lower() for word in diff_words):
            score += 0.1
        
        # Not too generic
        generic_words = ["best", "leading", "innovative", "cutting-edge"]
        if not any(word in statement.lower() for word in generic_words):
            score += 0.1
        
        # No unfilled placeholders
        if "[TBD]" not in statement:
            score += 0.05
        
        return min(1.0, score)
    
    def _generate_only_we_claims(self, company_info: Dict[str, Any], positioning: Dict[str, Any]) -> List[str]:
        """Generate 'Only We' differentiator claims"""
        differentiator = positioning.get("differentiator", "focus on outcomes")
        unique = positioning.get("unique_capability", "measure results")
        
        return [
            f"Only we {differentiator}",
            f"We're the only {company_info.get('category', 'solution')} that {unique}",
            f"No one else {positioning.get('exclusive_approach', 'takes this approach')}",
        ]
    
    async def generate_positioning(self, company_info: Dict[str, Any], positioning: Dict[str, Any] = None, icp_data: Dict[str, Any] = None) -> PositioningResult:
        """
        Generate positioning statements
        
        Args:
            company_info: Company information
            positioning: Existing positioning data
            icp_data: ICP profile data
        
        Returns:
            PositioningResult with statements and matrix
        """
        positioning = positioning or {}
        icp_data = icp_data or {}
        
        elements = self._generate_elements(company_info, positioning, icp_data)
        statements = []
        
        # Generate statement for each framework
        for framework in PositioningFramework:
            template = self.templates[framework]
            content = self._fill_template(template, elements)
            score = self._score_statement(content)
            
            statement = PositioningStatement(
                id=self._generate_statement_id(),
                type=StatementType.FULL,
                framework=framework,
                statement=content,
                audience=elements["target"],
                key_elements=elements,
                score=score
            )
            statements.append(statement)
        
        # Generate elevator pitch
        elevator_template = "We help {target} {action} by {approach}. Unlike {alternative}, we {differentiator}."
        elevator_content = self._fill_template(elevator_template, elements)
        statements.append(PositioningStatement(
            id=self._generate_statement_id(),
            type=StatementType.ELEVATOR,
            framework=PositioningFramework.BENEFIT_FOCUSED,
            statement=elevator_content,
            audience=elements["target"],
            key_elements=elements,
            score=self._score_statement(elevator_content)
        ))
        
        # Generate tagline
        tagline_template = "{benefit} without {pain}."
        tagline_content = self._fill_template(tagline_template, elements)
        statements.append(PositioningStatement(
            id=self._generate_statement_id(),
            type=StatementType.TAGLINE,
            framework=PositioningFramework.BENEFIT_FOCUSED,
            statement=tagline_content,
            audience=elements["target"],
            key_elements=elements,
            score=self._score_statement(tagline_content)
        ))
        
        # Sort by score and pick primary
        statements.sort(key=lambda s: s.score, reverse=True)
        primary = statements[0] if statements else None
        
        # Generate Only We claims
        only_we_claims = self._generate_only_we_claims(company_info, positioning)
        
        # Create positioning matrix
        matrix = PositioningMatrix(
            axes=["Price/Value", "Ease of Use", "Feature Depth", "Support Quality"],
            your_position={"Price/Value": 8, "Ease of Use": 9, "Feature Depth": 7, "Support Quality": 9},
            competitor_positions={
                "Competitor A": {"Price/Value": 5, "Ease of Use": 6, "Feature Depth": 9, "Support Quality": 5},
                "Competitor B": {"Price/Value": 7, "Ease of Use": 7, "Feature Depth": 6, "Support Quality": 7},
            },
            white_space="High value + ease of use combination"
        )
        
        recommendations = [
            f"Lead with {primary.framework.value} framework in sales conversations",
            "Test tagline variations in A/B tests",
            "Use 'Only We' claims sparingly and only when verifiable"
        ]
        
        summary = f"Generated {len(statements)} positioning statements across {len(PositioningFramework)} frameworks. "
        summary += f"Top framework: {primary.framework.value if primary else 'N/A'}. Score: {primary.score:.0%}."
        
        return PositioningResult(
            statements=statements,
            primary_statement=primary,
            matrix=matrix,
            only_we_claims=only_we_claims,
            recommendations=recommendations,
            summary=summary
        )
    
    def get_result_summary(self, result: PositioningResult) -> Dict[str, Any]:
        """Get summary for display"""
        return {
            "statement_count": len(result.statements),
            "primary_statement": result.primary_statement.statement if result.primary_statement else None,
            "primary_framework": result.primary_statement.framework.value if result.primary_statement else None,
            "only_we_claims": result.only_we_claims,
            "summary": result.summary,
            "recommendations": result.recommendations[:3]
        }
