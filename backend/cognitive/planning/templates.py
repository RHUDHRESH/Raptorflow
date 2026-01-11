"""
Plan Templates for Cognitive Engine

Pre-defined templates for common planning scenarios.
Implements PROMPT 25 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..models import CostEstimate, EntityType, ExecutionPlan, PlanStep, RiskLevel


class TemplateCategory(Enum):
    """Categories of plan templates."""

    CONTENT_CREATION = "content_creation"
    DATA_ANALYSIS = "data_analysis"
    RESEARCH = "research"
    MARKETING = "marketing"
    SALES = "sales"
    OPERATIONS = "operations"
    DEVELOPMENT = "development"
    CUSTOMER_SERVICE = "customer_service"


@dataclass
class TemplateVariable:
    """Variable definition for template."""

    name: str
    type: str  # "string", "number", "list", "boolean"
    description: str
    required: bool = True
    default_value: Any = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanTemplate:
    """Template for generating execution plans."""

    id: str
    name: str
    description: str
    category: TemplateCategory
    variables: List[TemplateVariable]
    steps: List[Dict[str, Any]]  # Template steps with variable placeholders
    estimated_cost_range: Dict[str, float]  # min, max
    estimated_time_range: Dict[str, int]  # min, max
    risk_level: RiskLevel
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0


class PlanTemplates:
    """
    Pre-defined templates for common planning scenarios.

    Enables rapid plan generation for frequent use cases.
    """

    def __init__(self):
        """Initialize plan templates with common scenarios."""
        self.templates: Dict[str, PlanTemplate] = {}
        self._initialize_common_templates()

    def _initialize_common_templates(self) -> None:
        """Initialize common plan templates."""

        # Content Creation Templates
        self._add_blog_post_template()
        self._add_social_media_template()
        self._add_email_campaign_template()

        # Research Templates
        self._add_competitor_research_template()
        self._add_market_research_template()
        self._add_trend_analysis_template()

        # Marketing Templates
        self._add_landing_page_template()
        self._add_ad_copy_template()
        self._add_content_calendar_template()

        # Sales Templates
        self._add_sales_proposal_template()
        self._add_follow_up_sequence_template()

        # Operations Templates
        self._add_process_optimization_template()
        self._add_report_generation_template()

        # Development Templates
        self._add_feature_specification_template()
        self._add_bug_analysis_template()

        # Customer Service Templates
        self._add_customer_response_template()
        self._add_faq_generation_template()

    def _add_blog_post_template(self) -> None:
        """Add blog post creation template."""
        template = PlanTemplate(
            id="generate_blog_post",
            name="Generate Blog Post",
            description="Create a comprehensive blog post with research, outline, and final content",
            category=TemplateCategory.CONTENT_CREATION,
            variables=[
                TemplateVariable(
                    name="topic",
                    type="string",
                    description="Main topic of the blog post",
                    required=True,
                ),
                TemplateVariable(
                    name="target_audience",
                    type="string",
                    description="Target audience for the blog post",
                    required=True,
                    default_value="general business audience",
                ),
                TemplateVariable(
                    name="word_count",
                    type="number",
                    description="Target word count for the blog post",
                    required=False,
                    default_value=1500,
                    validation_rules={"min": 500, "max": 5000},
                ),
                TemplateVariable(
                    name="tone",
                    type="string",
                    description="Tone of the blog post",
                    required=False,
                    default_value="professional",
                    validation_rules={
                        "options": [
                            "professional",
                            "casual",
                            "technical",
                            "promotional",
                        ]
                    },
                ),
                TemplateVariable(
                    name="include_research",
                    type="boolean",
                    description="Include external research and sources",
                    required=False,
                    default_value=True,
                ),
            ],
            steps=[
                {
                    "id": "research_topic",
                    "description": "Research the {topic} and gather relevant information",
                    "agent": "research_agent",
                    "tools": ["web_search", "knowledge_base"],
                    "estimated_tokens": 2000,
                    "estimated_cost": 0.05,
                    "estimated_time_seconds": 300,
                    "dependencies": [],
                },
                {
                    "id": "create_outline",
                    "description": "Create detailed outline for {topic} blog post targeting {target_audience}",
                    "agent": "content_planner",
                    "tools": ["outline_generator"],
                    "estimated_tokens": 1500,
                    "estimated_cost": 0.04,
                    "estimated_time_seconds": 180,
                    "dependencies": ["research_topic"],
                },
                {
                    "id": "write_content",
                    "description": "Write {word_count} word blog post with {tone} tone for {target_audience}",
                    "agent": "content_writer",
                    "tools": ["content_generator", "style_checker"],
                    "estimated_tokens": 3000,
                    "estimated_cost": 0.08,
                    "estimated_time_seconds": 600,
                    "dependencies": ["create_outline"],
                },
                {
                    "id": "review_edit",
                    "description": "Review and edit blog post for quality and consistency",
                    "agent": "content_editor",
                    "tools": ["grammar_checker", "seo_analyzer"],
                    "estimated_tokens": 2000,
                    "estimated_cost": 0.06,
                    "estimated_time_seconds": 300,
                    "dependencies": ["write_content"],
                },
                {
                    "id": "optimize_seo",
                    "description": "Optimize blog post for SEO with keywords and meta descriptions",
                    "agent": "seo_specialist",
                    "tools": ["keyword_research", "meta_generator"],
                    "estimated_tokens": 1500,
                    "estimated_cost": 0.04,
                    "estimated_time_seconds": 240,
                    "dependencies": ["review_edit"],
                },
            ],
            estimated_cost_range={"min": 0.27, "max": 0.35},
            estimated_time_range={"min": 1620, "max": 1800},
            risk_level=RiskLevel.LOW,
            tags=["blog", "content", "seo", "writing"],
        )

        self.templates[template.id] = template

    def _add_competitor_research_template(self) -> None:
        """Add competitor research template."""
        template = PlanTemplate(
            id="research_competitor",
            name="Competitor Research Analysis",
            description="Comprehensive research and analysis of competitors",
            category=TemplateCategory.RESEARCH,
            variables=[
                TemplateVariable(
                    name="company_name",
                    type="string",
                    description="Name of the company to research",
                    required=True,
                ),
                TemplateVariable(
                    name="industry",
                    type="string",
                    description="Industry sector",
                    required=True,
                ),
                TemplateVariable(
                    name="research_depth",
                    type="string",
                    description="Depth of research required",
                    required=False,
                    default_value="comprehensive",
                    validation_rules={
                        "options": ["basic", "comprehensive", "deep_dive"]
                    },
                ),
                TemplateVariable(
                    name="focus_areas",
                    type="list",
                    description="Specific areas to focus on",
                    required=False,
                    default_value=["products", "marketing", "pricing", "strategy"],
                ),
            ],
            steps=[
                {
                    "id": "company_overview",
                    "description": "Gather basic company information and overview",
                    "agent": "research_agent",
                    "tools": ["company_database", "web_search"],
                    "estimated_tokens": 2000,
                    "estimated_cost": 0.06,
                    "estimated_time_seconds": 300,
                    "dependencies": [],
                },
                {
                    "id": "product_analysis",
                    "description": "Analyze {company_name} products and services",
                    "agent": "product_analyst",
                    "tools": ["product_database", "review_analyzer"],
                    "estimated_tokens": 2500,
                    "estimated_cost": 0.07,
                    "estimated_time_seconds": 400,
                    "dependencies": ["company_overview"],
                },
                {
                    "id": "marketing_analysis",
                    "description": "Analyze marketing strategies and campaigns",
                    "agent": "marketing_analyst",
                    "tools": ["social_media_monitor", "ad_analyzer"],
                    "estimated_tokens": 2500,
                    "estimated_cost": 0.07,
                    "estimated_time_seconds": 400,
                    "dependencies": ["company_overview"],
                },
                {
                    "id": "competitive_positioning",
                    "description": "Analyze competitive positioning in {industry}",
                    "agent": "strategy_analyst",
                    "tools": ["market_analyzer", "positioning_mapper"],
                    "estimated_tokens": 2000,
                    "estimated_cost": 0.06,
                    "estimated_time_seconds": 350,
                    "dependencies": ["product_analysis", "marketing_analysis"],
                },
                {
                    "id": "generate_report",
                    "description": "Generate comprehensive competitor research report",
                    "agent": "report_generator",
                    "tools": ["report_builder", "chart_generator"],
                    "estimated_tokens": 3000,
                    "estimated_cost": 0.08,
                    "estimated_time_seconds": 450,
                    "dependencies": ["competitive_positioning"],
                },
            ],
            estimated_cost_range={"min": 0.34, "max": 0.42},
            estimated_time_range={"min": 1900, "max": 2100},
            risk_level=RiskLevel.MEDIUM,
            tags=["competitor", "research", "analysis", "strategy"],
        )

        self.templates[template.id] = template

    def _add_landing_page_template(self) -> None:
        """Add landing page creation template."""
        template = PlanTemplate(
            id="create_landing_page",
            name="Create Landing Page",
            description="Create a high-converting landing page with copy and design",
            category=TemplateCategory.MARKETING,
            variables=[
                TemplateVariable(
                    name="product_service",
                    type="string",
                    description="Product or service to promote",
                    required=True,
                ),
                TemplateVariable(
                    name="target_audience",
                    type="string",
                    description="Target audience for the landing page",
                    required=True,
                ),
                TemplateVariable(
                    name="conversion_goal",
                    type="string",
                    description="Primary conversion goal",
                    required=True,
                    validation_rules={
                        "options": ["lead_generation", "sales", "sign_up", "download"]
                    },
                ),
                TemplateVariable(
                    name="value_proposition",
                    type="string",
                    description="Main value proposition",
                    required=True,
                ),
                TemplateVariable(
                    name="page_sections",
                    type="list",
                    description="Required sections on the page",
                    required=False,
                    default_value=[
                        "hero",
                        "benefits",
                        "features",
                        "testimonials",
                        "cta",
                    ],
                ),
            ],
            steps=[
                {
                    "id": "audience_research",
                    "description": "Research {target_audience} pain points and motivations",
                    "agent": "market_researcher",
                    "tools": ["audience_analyzer", "survey_data"],
                    "estimated_tokens": 2000,
                    "estimated_cost": 0.05,
                    "estimated_time_seconds": 300,
                    "dependencies": [],
                },
                {
                    "id": "copy_strategy",
                    "description": "Develop copy strategy and messaging framework",
                    "agent": "copy_strategist",
                    "tools": ["messaging_framework", "tone_analyzer"],
                    "estimated_tokens": 1500,
                    "estimated_cost": 0.04,
                    "estimated_time_seconds": 240,
                    "dependencies": ["audience_research"],
                },
                {
                    "id": "write_headline",
                    "description": "Create compelling headline for {product_service}",
                    "agent": "copywriter",
                    "tools": ["headline_generator", "ab_test_variants"],
                    "estimated_tokens": 1000,
                    "estimated_cost": 0.03,
                    "estimated_time_seconds": 180,
                    "dependencies": ["copy_strategy"],
                },
                {
                    "id": "write_body_copy",
                    "description": "Write persuasive body copy for landing page sections",
                    "agent": "copywriter",
                    "tools": ["copy_generator", "persuasion_analyzer"],
                    "estimated_tokens": 3000,
                    "estimated_cost": 0.08,
                    "estimated_time_seconds": 480,
                    "dependencies": ["write_headline"],
                },
                {
                    "id": "create_cta",
                    "description": "Create compelling call-to-action for {conversion_goal}",
                    "agent": "cta_specialist",
                    "tools": ["cta_generator", "conversion_optimizer"],
                    "estimated_tokens": 1000,
                    "estimated_cost": 0.03,
                    "estimated_time_seconds": 150,
                    "dependencies": ["write_body_copy"],
                },
                {
                    "id": "optimize_conversion",
                    "description": "Optimize copy for maximum conversion rate",
                    "agent": "conversion_optimizer",
                    "tools": ["conversion_analyzer", "psychology_triggers"],
                    "estimated_tokens": 2000,
                    "estimated_cost": 0.06,
                    "estimated_time_seconds": 300,
                    "dependencies": ["create_cta"],
                },
            ],
            estimated_cost_range={"min": 0.29, "max": 0.37},
            estimated_time_range={"min": 1650, "max": 1850},
            risk_level=RiskLevel.MEDIUM,
            tags=["landing_page", "copywriting", "conversion", "marketing"],
        )

        self.templates[template.id] = template

    def _add_sales_proposal_template(self) -> None:
        """Add sales proposal template."""
        template = PlanTemplate(
            id="create_sales_proposal",
            name="Create Sales Proposal",
            description="Generate a comprehensive sales proposal",
            category=TemplateCategory.SALES,
            variables=[
                TemplateVariable(
                    name="client_name",
                    type="string",
                    description="Client company name",
                    required=True,
                ),
                TemplateVariable(
                    name="solution_offered",
                    type="string",
                    description="Solution being proposed",
                    required=True,
                ),
                TemplateVariable(
                    name="proposal_type",
                    type="string",
                    description="Type of proposal",
                    required=False,
                    default_value="standard",
                    validation_rules={"options": ["standard", "complex", "simple"]},
                ),
                TemplateVariable(
                    name="budget_range",
                    type="string",
                    description="Client budget range",
                    required=False,
                ),
            ],
            steps=[
                {
                    "id": "client_research",
                    "description": "Research {client_name} background and needs",
                    "agent": "sales_researcher",
                    "tools": ["company_profiler", "needs_analyzer"],
                    "estimated_tokens": 2000,
                    "estimated_cost": 0.05,
                    "estimated_time_seconds": 300,
                    "dependencies": [],
                },
                {
                    "id": "solution_customization",
                    "description": "Customize {solution_offered} for client needs",
                    "agent": "solution_architect",
                    "tools": ["solution_builder", "customization_engine"],
                    "estimated_tokens": 2500,
                    "estimated_cost": 0.07,
                    "estimated_time_seconds": 400,
                    "dependencies": ["client_research"],
                },
                {
                    "id": "pricing_strategy",
                    "description": "Develop pricing strategy and options",
                    "agent": "pricing_specialist",
                    "tools": ["pricing_calculator", "value_analyzer"],
                    "estimated_tokens": 1500,
                    "estimated_cost": 0.04,
                    "estimated_time_seconds": 240,
                    "dependencies": ["solution_customization"],
                },
                {
                    "id": "write_executive_summary",
                    "description": "Write compelling executive summary",
                    "agent": "proposal_writer",
                    "tools": ["summary_generator", "persuasion_writer"],
                    "estimated_tokens": 1500,
                    "estimated_cost": 0.04,
                    "estimated_time_seconds": 240,
                    "dependencies": ["pricing_strategy"],
                },
                {
                    "id": "create_proposal_document",
                    "description": "Create complete proposal document",
                    "agent": "proposal_builder",
                    "tools": ["document_generator", "proposal_templates"],
                    "estimated_tokens": 3000,
                    "estimated_cost": 0.08,
                    "estimated_time_seconds": 480,
                    "dependencies": ["write_executive_summary"],
                },
            ],
            estimated_cost_range={"min": 0.28, "max": 0.36},
            estimated_time_range={"min": 1660, "max": 1860},
            risk_level=RiskLevel.MEDIUM,
            tags=["sales", "proposal", "client", "pricing"],
        )

        self.templates[template.id] = template

    async def apply_template(
        self, template_name: str, variables: Dict[str, Any]
    ) -> ExecutionPlan:
        """
        Apply a template with given variables to create an execution plan.

        Args:
            template_name: Name or ID of the template
            variables: Dictionary of variable values

        Returns:
            ExecutionPlan created from template
        """
        template = self._get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        # Validate variables
        validated_vars = await self._validate_variables(template, variables)

        # Create plan steps from template
        plan_steps = await self._create_plan_steps(template, validated_vars)

        # Calculate total cost and time
        total_cost = sum(step.estimated_cost for step in plan_steps)
        total_time = sum(step.estimated_time_seconds for step in plan_steps)

        # Create cost estimate
        cost_estimate = CostEstimate(
            total_tokens=sum(step.estimated_tokens for step in plan_steps),
            total_cost_usd=total_cost,
            total_time_seconds=total_time,
            breakdown_by_agent=self._calculate_agent_breakdown(plan_steps),
            breakdown_by_step={step.id: step.estimated_cost for step in plan_steps},
        )

        # Create execution plan
        plan = ExecutionPlan(
            goal=self._substitute_variables(template.description, validated_vars),
            steps=plan_steps,
            total_cost=cost_estimate,
            total_time_seconds=total_time,
            risk_level=template.risk_level,
            requires_approval=template.risk_level
            in [RiskLevel.HIGH, RiskLevel.CRITICAL],
            approval_reason=f"Template '{template_name}' with {template.risk_level.value} risk",
            metadata={
                "template_id": template.id,
                "template_name": template.name,
                "variables": validated_vars,
                "created_from_template": datetime.now().isoformat(),
            },
        )

        # Update template usage count
        template.usage_count += 1
        template.updated_at = datetime.now()

        return plan

    async def get_template_suggestions(
        self, goal: str, context: Dict[str, Any] = None
    ) -> List[PlanTemplate]:
        """
        Get template suggestions based on goal and context.

        Args:
            goal: User goal description
            context: Additional context information

        Returns:
            List of suggested templates
        """
        suggestions = []
        goal_lower = goal.lower()

        # Simple keyword matching for suggestions
        keyword_mappings = {
            "blog": ["generate_blog_post"],
            "article": ["generate_blog_post"],
            "content": ["generate_blog_post", "create_landing_page"],
            "competitor": ["research_competitor"],
            "research": ["research_competitor", "market_research"],
            "landing page": ["create_landing_page"],
            "proposal": ["create_sales_proposal"],
            "sales": ["create_sales_proposal"],
            "marketing": ["create_landing_page"],
        }

        for keyword, template_ids in keyword_mappings.items():
            if keyword in goal_lower:
                for template_id in template_ids:
                    if template_id in self.templates:
                        suggestions.append(self.templates[template_id])

        # Remove duplicates and return
        seen = set()
        unique_suggestions = []
        for template in suggestions:
            if template.id not in seen:
                seen.add(template.id)
                unique_suggestions.append(template)

        return unique_suggestions[:5]  # Return top 5 suggestions

    def list_templates(
        self, category: TemplateCategory = None, tags: List[str] = None
    ) -> List[PlanTemplate]:
        """
        List available templates with optional filtering.

        Args:
            category: Filter by category
            tags: Filter by tags

        Returns:
            List of matching templates
        """
        templates = list(self.templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]

        return templates

    def get_template(self, template_id: str) -> Optional[PlanTemplate]:
        """Get template by ID."""
        return self.templates.get(template_id)

    def _get_template(self, template_name: str) -> Optional[PlanTemplate]:
        """Get template by name or ID."""
        # Try by ID first
        template = self.templates.get(template_name)
        if template:
            return template

        # Try by name
        for template in self.templates.values():
            if template.name.lower() == template_name.lower():
                return template

        return None

    async def _validate_variables(
        self, template: PlanTemplate, variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate template variables."""
        validated = {}

        for var in template.variables:
            value = variables.get(var.name)

            # Check required variables
            if var.required and value is None:
                if var.default_value is not None:
                    value = var.default_value
                else:
                    raise ValueError(f"Required variable '{var.name}' is missing")

            # Use default value if not provided
            if value is None and var.default_value is not None:
                value = var.default_value

            # Type validation
            if value is not None:
                value = self._validate_variable_type(var, value)

            validated[var.name] = value

        return validated

    def _validate_variable_type(self, var: TemplateVariable, value: Any) -> Any:
        """Validate individual variable type and rules."""
        # Type conversion
        if var.type == "number":
            try:
                value = float(value)
            except (ValueError, TypeError):
                raise ValueError(f"Variable '{var.name}' must be a number")
        elif var.type == "boolean":
            if isinstance(value, str):
                value = value.lower() in ["true", "1", "yes", "on"]
            else:
                value = bool(value)
        elif var.type == "list":
            if isinstance(value, str):
                value = [item.strip() for item in value.split(",")]
            elif not isinstance(value, list):
                value = [value]

        # Validation rules
        if var.validation_rules:
            if "min" in var.validation_rules and var.type == "number":
                if value < var.validation_rules["min"]:
                    raise ValueError(
                        f"Variable '{var.name}' must be at least {var.validation_rules['min']}"
                    )

            if "max" in var.validation_rules and var.type == "number":
                if value > var.validation_rules["max"]:
                    raise ValueError(
                        f"Variable '{var.name}' must be at most {var.validation_rules['max']}"
                    )

            if "options" in var.validation_rules:
                if value not in var.validation_rules["options"]:
                    raise ValueError(
                        f"Variable '{var.name}' must be one of: {var.validation_rules['options']}"
                    )

        return value

    async def _create_plan_steps(
        self, template: PlanTemplate, variables: Dict[str, Any]
    ) -> List[PlanStep]:
        """Create plan steps from template."""
        steps = []

        for step_data in template.steps:
            # Substitute variables in description
            description = self._substitute_variables(
                step_data["description"], variables
            )

            # Create PlanStep
            step = PlanStep(
                id=step_data["id"],
                description=description,
                agent=step_data["agent"],
                tools=step_data.get("tools", []),
                inputs=variables,
                outputs={},
                dependencies=step_data.get("dependencies", []),
                estimated_tokens=step_data["estimated_tokens"],
                estimated_cost=step_data["estimated_cost"],
                estimated_time_seconds=step_data["estimated_time_seconds"],
                risk_level=RiskLevel.LOW,
            )

            steps.append(step)

        return steps

    def _substitute_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in text."""
        for var_name, var_value in variables.items():
            placeholder = "{" + var_name + "}"
            if placeholder in text:
                text = text.replace(placeholder, str(var_value))

        return text

    def _calculate_agent_breakdown(self, steps: List[PlanStep]) -> Dict[str, float]:
        """Calculate cost breakdown by agent."""
        breakdown = {}

        for step in steps:
            agent_cost = breakdown.get(step.agent, 0.0)
            breakdown[step.agent] = agent_cost + step.estimated_cost

        return breakdown

    def get_template_stats(self) -> Dict[str, Any]:
        """Get template usage statistics."""
        total_templates = len(self.templates)
        category_counts = {}
        total_usage = 0

        for template in self.templates.values():
            category = template.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
            total_usage += template.usage_count

        most_used = (
            max(self.templates.values(), key=lambda t: t.usage_count)
            if self.templates
            else None
        )

        return {
            "total_templates": total_templates,
            "category_distribution": category_counts,
            "total_usage": total_usage,
            "most_used_template": most_used.name if most_used else None,
            "average_usage": (
                total_usage / total_templates if total_templates > 0 else 0
            ),
        }
