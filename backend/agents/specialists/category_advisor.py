"""
Category Advisor Agent
Generates Safe/Clever/Bold category path recommendations for market positioning
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class CategoryPath(Enum):
    """Market category positioning paths"""
    SAFE = "safe"
    CLEVER = "clever"
    BOLD = "bold"


class EffortLevel(Enum):
    """Effort required for each path"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class EducationRequired(Enum):
    """Market education required"""
    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    EXTENSIVE = "extensive"


@dataclass
class CategoryPathOption:
    """Represents a category path option"""
    id: str
    path: CategoryPath
    category_name: str
    description: str
    effort_level: EffortLevel
    education_required: EducationRequired
    pricing_implication: str
    time_to_traction: str
    pros: List[str]
    cons: List[str]
    competitors_in_space: List[str]
    example_positioning: str
    confidence_score: float
    rationale: str


@dataclass
class CategoryAdvisorResult:
    """Result of category analysis"""
    safe_path: CategoryPathOption
    clever_path: CategoryPathOption
    bold_path: CategoryPathOption
    recommended_path: CategoryPath
    recommendation_rationale: str
    market_context: Dict[str, Any]
    decision_factors: List[str]


class CategoryAdvisor:
    """AI-powered category path advisor for market positioning"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.path_templates = self._load_path_templates()
        self.industry_mappings = self._load_industry_mappings()
        self.option_counter = 0
    
    def _load_path_templates(self) -> Dict[CategoryPath, Dict[str, Any]]:
        """Load templates for each category path"""
        return {
            CategoryPath.SAFE: {
                "description": "Compete in an established category with clear demand",
                "effort_level": EffortLevel.LOW,
                "education_required": EducationRequired.NONE,
                "pricing_implication": "Market-rate pricing, compete on value",
                "time_to_traction": "1-3 months",
                "default_pros": [
                    "Established demand - buyers already searching",
                    "Clear competitive landscape",
                    "Easier sales conversations",
                    "Lower marketing education costs"
                ],
                "default_cons": [
                    "Crowded market with established players",
                    "Price pressure from competitors",
                    "Harder to differentiate",
                    "May be seen as 'just another X'"
                ]
            },
            CategoryPath.CLEVER: {
                "description": "Reframe an existing category with a unique angle",
                "effort_level": EffortLevel.MEDIUM,
                "education_required": EducationRequired.MODERATE,
                "pricing_implication": "Premium potential with differentiated positioning",
                "time_to_traction": "3-6 months",
                "default_pros": [
                    "Stand out from direct competitors",
                    "Own a unique conversation",
                    "Premium pricing opportunity",
                    "Builds on existing demand"
                ],
                "default_cons": [
                    "Requires market education",
                    "May confuse some buyers initially",
                    "Harder to explain quickly",
                    "Risk of being too clever"
                ]
            },
            CategoryPath.BOLD: {
                "description": "Create or define a new category",
                "effort_level": EffortLevel.VERY_HIGH,
                "education_required": EducationRequired.EXTENSIVE,
                "pricing_implication": "Category leader premium, value-based pricing",
                "time_to_traction": "6-18 months",
                "default_pros": [
                    "No direct competitors initially",
                    "Category king advantages",
                    "Maximum differentiation",
                    "Shape the narrative"
                ],
                "default_cons": [
                    "High market education costs",
                    "Longer sales cycles",
                    "Risk of category not taking off",
                    "Significant investment required"
                ]
            }
        }
    
    def _load_industry_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load industry-specific category mappings"""
        return {
            "saas": {
                "safe_categories": ["CRM", "Project Management", "Email Marketing", "Analytics", "Help Desk"],
                "clever_angles": ["AI-powered", "No-code", "Privacy-first", "Developer-focused", "SMB-optimized"],
                "bold_examples": ["Revenue Operations", "Product-Led Growth Platform", "Customer Success Intelligence"]
            },
            "fintech": {
                "safe_categories": ["Payment Processing", "Accounting Software", "Expense Management"],
                "clever_angles": ["Embedded Finance", "Real-time", "API-first", "Vertical-specific"],
                "bold_examples": ["Treasury-as-a-Service", "Financial Workflow Automation"]
            },
            "martech": {
                "safe_categories": ["Marketing Automation", "Social Media Management", "SEO Tools"],
                "clever_angles": ["AI-generated", "Intent-based", "Community-driven", "Privacy-compliant"],
                "bold_examples": ["Growth Intelligence Platform", "Autonomous Marketing Engine"]
            },
            "default": {
                "safe_categories": ["Software Platform", "Business Solution", "Management Tool"],
                "clever_angles": ["AI-enhanced", "Modern", "Streamlined", "Integrated"],
                "bold_examples": ["Intelligence Platform", "Autonomous Solution"]
            }
        }
    
    def _generate_option_id(self, path: CategoryPath) -> str:
        """Generate unique option ID"""
        self.option_counter += 1
        return f"CAT-{path.value.upper()}-{self.option_counter:03d}"
    
    def _determine_industry(self, company_info: Dict[str, Any]) -> str:
        """Determine industry from company info"""
        industry = company_info.get("industry", "").lower()
        product_desc = company_info.get("product_description", "").lower()
        
        if any(word in industry or word in product_desc for word in ["saas", "software", "platform", "app"]):
            return "saas"
        elif any(word in industry or word in product_desc for word in ["fintech", "payment", "banking", "finance"]):
            return "fintech"
        elif any(word in industry or word in product_desc for word in ["marketing", "advertising", "growth", "social"]):
            return "martech"
        else:
            return "default"
    
    def _generate_safe_path(self, company_info: Dict[str, Any], competitors: List[Dict[str, Any]], industry: str) -> CategoryPathOption:
        """Generate safe category path option"""
        template = self.path_templates[CategoryPath.SAFE]
        industry_data = self.industry_mappings.get(industry, self.industry_mappings["default"])
        
        # Determine safe category based on product
        product_type = company_info.get("product_type", "")
        existing_category = company_info.get("current_category", "")
        
        if existing_category:
            category_name = existing_category
        elif product_type:
            category_name = f"{product_type} Software"
        else:
            category_name = industry_data["safe_categories"][0] if industry_data["safe_categories"] else "Business Software"
        
        # Get competitors in this category
        competitors_in_space = [c.get("name", "Competitor") for c in competitors[:3]] if competitors else ["Established players exist"]
        
        return CategoryPathOption(
            id=self._generate_option_id(CategoryPath.SAFE),
            path=CategoryPath.SAFE,
            category_name=category_name,
            description=f"Position as a {category_name} solution in the established market",
            effort_level=template["effort_level"],
            education_required=template["education_required"],
            pricing_implication=template["pricing_implication"],
            time_to_traction=template["time_to_traction"],
            pros=template["default_pros"],
            cons=template["default_cons"],
            competitors_in_space=competitors_in_space,
            example_positioning=f"The {category_name} built for {company_info.get('target_audience', 'modern teams')}",
            confidence_score=0.8,
            rationale="Established category with proven demand. Lower risk but more competition."
        )
    
    def _generate_clever_path(self, company_info: Dict[str, Any], competitors: List[Dict[str, Any]], industry: str) -> CategoryPathOption:
        """Generate clever category path option"""
        template = self.path_templates[CategoryPath.CLEVER]
        industry_data = self.industry_mappings.get(industry, self.industry_mappings["default"])
        
        # Determine clever angle based on differentiators
        differentiators = company_info.get("differentiators", [])
        product_type = company_info.get("product_type", "Software")
        
        # Select clever angle
        clever_angles = industry_data.get("clever_angles", ["Modern", "AI-powered"])
        angle = clever_angles[0] if clever_angles else "Next-generation"
        
        # Build category name
        if differentiators:
            angle = differentiators[0] if isinstance(differentiators[0], str) else "Specialized"
        
        category_name = f"{angle} {product_type}"
        
        return CategoryPathOption(
            id=self._generate_option_id(CategoryPath.CLEVER),
            path=CategoryPath.CLEVER,
            category_name=category_name,
            description=f"Reframe as {category_name} - same problem, unique approach",
            effort_level=template["effort_level"],
            education_required=template["education_required"],
            pricing_implication=template["pricing_implication"],
            time_to_traction=template["time_to_traction"],
            pros=template["default_pros"],
            cons=template["default_cons"],
            competitors_in_space=["Fewer direct competitors", "Some overlap with traditional solutions"],
            example_positioning=f"The {angle.lower()} way to {company_info.get('core_benefit', 'solve your problem')}",
            confidence_score=0.7,
            rationale="Differentiated positioning that builds on existing demand while standing out."
        )
    
    def _generate_bold_path(self, company_info: Dict[str, Any], competitors: List[Dict[str, Any]], industry: str) -> CategoryPathOption:
        """Generate bold category path option"""
        template = self.path_templates[CategoryPath.BOLD]
        industry_data = self.industry_mappings.get(industry, self.industry_mappings["default"])
        
        # Generate new category name
        bold_examples = industry_data.get("bold_examples", ["Intelligence Platform"])
        product_type = company_info.get("product_type", "Platform")
        mission = company_info.get("mission", "")
        
        # Create bold category name
        if mission:
            words = mission.split()[:3]
            category_name = " ".join(word.capitalize() for word in words) + " Platform"
        elif bold_examples:
            category_name = bold_examples[0]
        else:
            category_name = f"{product_type} Intelligence"
        
        return CategoryPathOption(
            id=self._generate_option_id(CategoryPath.BOLD),
            path=CategoryPath.BOLD,
            category_name=category_name,
            description=f"Create and own the '{category_name}' category",
            effort_level=template["effort_level"],
            education_required=template["education_required"],
            pricing_implication=template["pricing_implication"],
            time_to_traction=template["time_to_traction"],
            pros=template["default_pros"],
            cons=template["default_cons"],
            competitors_in_space=["No direct competitors yet", "Must educate the market"],
            example_positioning=f"The world's first {category_name.lower()} for {company_info.get('target_audience', 'forward-thinking teams')}",
            confidence_score=0.5,
            rationale="Category creation opportunity. High risk, high reward. Requires significant investment."
        )
    
    def _determine_recommendation(self, company_info: Dict[str, Any], safe: CategoryPathOption, clever: CategoryPathOption, bold: CategoryPathOption) -> Tuple[CategoryPath, str]:
        """Determine recommended path based on company context"""
        # Factors to consider
        funding_stage = company_info.get("funding_stage", "").lower()
        team_size = company_info.get("team_size", 0)
        runway = company_info.get("runway_months", 0)
        market_maturity = company_info.get("market_maturity", "").lower()
        risk_tolerance = company_info.get("risk_tolerance", "medium").lower()
        
        # Scoring
        scores = {
            CategoryPath.SAFE: 0,
            CategoryPath.CLEVER: 0,
            CategoryPath.BOLD: 0
        }
        
        # Early stage / limited resources -> Safe
        if funding_stage in ["pre-seed", "bootstrapped", "seed"] or team_size < 10:
            scores[CategoryPath.SAFE] += 2
            scores[CategoryPath.CLEVER] += 1
        
        # Well-funded -> Bold is viable
        if funding_stage in ["series a", "series b", "series c"] or team_size > 50:
            scores[CategoryPath.BOLD] += 2
            scores[CategoryPath.CLEVER] += 1
        
        # Short runway -> Safe
        if runway and runway < 12:
            scores[CategoryPath.SAFE] += 2
        elif runway and runway > 24:
            scores[CategoryPath.BOLD] += 1
        
        # Market maturity
        if market_maturity in ["mature", "saturated"]:
            scores[CategoryPath.CLEVER] += 2
            scores[CategoryPath.BOLD] += 1
        elif market_maturity in ["emerging", "new"]:
            scores[CategoryPath.BOLD] += 2
        
        # Risk tolerance
        if risk_tolerance == "low":
            scores[CategoryPath.SAFE] += 2
        elif risk_tolerance == "high":
            scores[CategoryPath.BOLD] += 2
        else:
            scores[CategoryPath.CLEVER] += 1
        
        # Determine winner
        recommended = max(scores, key=scores.get)
        
        # Generate rationale
        rationales = {
            CategoryPath.SAFE: "Based on your company stage and resources, a safe category path minimizes risk while allowing you to gain traction quickly.",
            CategoryPath.CLEVER: "Your positioning suggests a clever reframe would help you stand out while building on existing market demand.",
            CategoryPath.BOLD: "Your resources and market position suggest you could successfully create and own a new category."
        }
        
        return recommended, rationales[recommended]
    
    async def analyze_category_paths(self, company_info: Dict[str, Any], competitors: List[Dict[str, Any]] = None) -> CategoryAdvisorResult:
        """
        Analyze and recommend category positioning paths
        
        Args:
            company_info: Company information including product, market, resources
            competitors: List of competitor information
        
        Returns:
            CategoryAdvisorResult with all three paths and recommendation
        """
        competitors = competitors or []
        
        # Determine industry
        industry = self._determine_industry(company_info)
        
        # Generate all three paths
        safe_path = self._generate_safe_path(company_info, competitors, industry)
        clever_path = self._generate_clever_path(company_info, competitors, industry)
        bold_path = self._generate_bold_path(company_info, competitors, industry)
        
        # Determine recommendation
        recommended_path, recommendation_rationale = self._determine_recommendation(
            company_info, safe_path, clever_path, bold_path
        )
        
        # Build market context
        market_context = {
            "industry": industry,
            "competitor_count": len(competitors),
            "market_maturity": company_info.get("market_maturity", "unknown"),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Decision factors
        decision_factors = [
            f"Company stage: {company_info.get('funding_stage', 'Unknown')}",
            f"Team size: {company_info.get('team_size', 'Unknown')}",
            f"Market maturity: {company_info.get('market_maturity', 'Unknown')}",
            f"Risk tolerance: {company_info.get('risk_tolerance', 'Medium')}",
            f"Competitor landscape: {len(competitors)} known competitors"
        ]
        
        return CategoryAdvisorResult(
            safe_path=safe_path,
            clever_path=clever_path,
            bold_path=bold_path,
            recommended_path=recommended_path,
            recommendation_rationale=recommendation_rationale,
            market_context=market_context,
            decision_factors=decision_factors
        )
    
    def get_path_comparison(self, result: CategoryAdvisorResult) -> Dict[str, Any]:
        """Get comparison table of all paths"""
        return {
            "paths": [
                {
                    "name": result.safe_path.path.value,
                    "category": result.safe_path.category_name,
                    "effort": result.safe_path.effort_level.value,
                    "education": result.safe_path.education_required.value,
                    "time_to_traction": result.safe_path.time_to_traction,
                    "confidence": result.safe_path.confidence_score,
                    "recommended": result.recommended_path == CategoryPath.SAFE
                },
                {
                    "name": result.clever_path.path.value,
                    "category": result.clever_path.category_name,
                    "effort": result.clever_path.effort_level.value,
                    "education": result.clever_path.education_required.value,
                    "time_to_traction": result.clever_path.time_to_traction,
                    "confidence": result.clever_path.confidence_score,
                    "recommended": result.recommended_path == CategoryPath.CLEVER
                },
                {
                    "name": result.bold_path.path.value,
                    "category": result.bold_path.category_name,
                    "effort": result.bold_path.effort_level.value,
                    "education": result.bold_path.education_required.value,
                    "time_to_traction": result.bold_path.time_to_traction,
                    "confidence": result.bold_path.confidence_score,
                    "recommended": result.recommended_path == CategoryPath.BOLD
                }
            ],
            "recommendation": result.recommended_path.value,
            "rationale": result.recommendation_rationale
        }
