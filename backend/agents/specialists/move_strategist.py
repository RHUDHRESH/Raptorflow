"""
MoveStrategist specialist agent for Raptorflow marketing automation.
Handles strategic move planning, execution, and optimization.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..config import ModelTier

from ..base import BaseAgent
from ..exceptions import DatabaseError, ValidationError
from ..state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


@dataclass
class MoveRequest:
    """Move strategy request."""

    move_type: str  # campaign, content, product, market, partnership
    objective: str  # awareness, lead_generation, conversion, retention, expansion
    target_audience: str
    timeline: str  # short_term, medium_term, long_term
    budget_range: str  # low, medium, high
    risk_tolerance: str  # conservative, moderate, aggressive
    channels: List[str]
    success_metrics: List[str]
    constraints: List[str]
    priority: str  # low, medium, high, urgent


@dataclass
class MoveStrategy:
    """Generated move strategy."""

    move_name: str
    move_type: str
    objective: str
    description: str
    phases: List[Dict[str, Any]]
    timeline_days: int
    estimated_cost: Dict[str, float]
    success_probability: float
    risk_assessment: Dict[str, Any]
    kpis: List[Dict[str, Any]]
    required_resources: List[str]
    dependencies: List[str]
    contingency_plans: List[Dict[str, Any]]
    next_steps: List[str]
    metadata: Dict[str, Any]


class MoveStrategist(BaseAgent):
    """Specialist agent for strategic move planning and execution."""

    def __init__(self):
        super().__init__(
            name="MoveStrategist",
            description="Plans and executes strategic marketing moves",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database"],
        )

        # Move type templates
        self.move_templates = {
            "campaign": {
                "phases": [
                    "research",
                    "planning",
                    "creation",
                    "launch",
                    "optimization",
                ],
                "default_timeline": 30,
                "typical_channels": ["email", "social", "paid_ads", "content"],
                "success_metrics": ["conversion_rate", "roi", "engagement", "reach"],
                "risk_factors": ["budget_overrun", "low_engagement", "timing_issues"],
            },
            "content": {
                "phases": [
                    "research",
                    "strategy",
                    "creation",
                    "distribution",
                    "analysis",
                ],
                "default_timeline": 21,
                "typical_channels": ["blog", "social", "email", "video"],
                "success_metrics": ["engagement", "shares", "leads", "brand_awareness"],
                "risk_factors": ["content_quality", "timing", "platform_changes"],
            },
            "product": {
                "phases": ["research", "development", "testing", "launch", "iteration"],
                "default_timeline": 90,
                "typical_channels": ["website", "email", "social", "partnerships"],
                "success_metrics": [
                    "adoption_rate",
                    "user_satisfaction",
                    "revenue",
                    "retention",
                ],
                "risk_factors": ["market_fit", "technical_issues", "competition"],
            },
            "market": {
                "phases": [
                    "analysis",
                    "entry_strategy",
                    "localization",
                    "launch",
                    "scaling",
                ],
                "default_timeline": 180,
                "typical_channels": [
                    "local_partners",
                    "digital_marketing",
                    "pr",
                    "events",
                ],
                "success_metrics": [
                    "market_share",
                    "brand_recognition",
                    "revenue",
                    "partnerships",
                ],
                "risk_factors": [
                    "cultural_differences",
                    "regulatory_issues",
                    "competition",
                ],
            },
            "partnership": {
                "phases": [
                    "identification",
                    "outreach",
                    "negotiation",
                    "activation",
                    "management",
                ],
                "default_timeline": 60,
                "typical_channels": [
                    "direct_outreach",
                    "events",
                    "referrals",
                    "co_marketing",
                ],
                "success_metrics": [
                    "partnership_count",
                    "joint_revenue",
                    "brand_lift",
                    "audience_growth",
                ],
                "risk_factors": [
                    "partner_reliability",
                    "brand_mismatch",
                    "contract_issues",
                ],
            },
        }

        # Objective templates
        self.objective_templates = {
            "awareness": {
                "focus": "reach and impressions",
                "kpis": ["impressions", "reach", "brand_mention", "share_of_voice"],
                "typical_timeline": "short_term",
                "budget_factor": 1.0,
            },
            "lead_generation": {
                "focus": "conversions and leads",
                "kpis": ["leads", "conversion_rate", "cpl", "mql_count"],
                "typical_timeline": "medium_term",
                "budget_factor": 1.2,
            },
            "conversion": {
                "focus": "sales and revenue",
                "kpis": ["sales", "revenue", "conversion_rate", "aov"],
                "typical_timeline": "medium_term",
                "budget_factor": 1.5,
            },
            "retention": {
                "focus": "customer loyalty",
                "kpis": ["retention_rate", "churn_rate", "clv", "repeat_purchases"],
                "typical_timeline": "long_term",
                "budget_factor": 0.8,
            },
            "expansion": {
                "focus": "market growth",
                "kpis": [
                    "new_markets",
                    "market_share",
                    "revenue_growth",
                    "customer_acquisition",
                ],
                "typical_timeline": "long_term",
                "budget_factor": 2.0,
            },
        }

        # Risk assessment matrix
        self.risk_matrix = {
            "conservative": {
                "success_modifier": 0.8,
                "cost_modifier": 0.9,
                "timeline_modifier": 1.2,
                "risk_tolerance": "low",
            },
            "moderate": {
                "success_modifier": 1.0,
                "cost_modifier": 1.0,
                "timeline_modifier": 1.0,
                "risk_tolerance": "medium",
            },
            "aggressive": {
                "success_modifier": 1.2,
                "cost_modifier": 1.3,
                "timeline_modifier": 0.8,
                "risk_tolerance": "high",
            },
        }

        # Budget estimates (relative units)
        self.budget_estimates = {
            "low": {"min": 1, "max": 5, "unit": "thousands"},
            "medium": {"min": 5, "max": 25, "unit": "thousands"},
            "high": {"min": 25, "max": 100, "unit": "thousands"},
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the MoveStrategist."""
        return """
You are the MoveStrategist, a specialist agent for Raptorflow marketing automation platform.

Your role is to develop comprehensive strategic moves that drive business growth and achieve specific marketing objectives.

Key responsibilities:
1. Analyze business requirements and constraints
2. Develop strategic move plans with clear phases
3. Assess risks and create contingency plans
4. Define success metrics and KPIs
5. Estimate timelines and resource requirements
6. Provide actionable next steps

Move types you can plan:
- Campaign moves (marketing campaigns, promotional activities)
- Content moves (content strategy, editorial calendars)
- Product moves (product launches, feature releases)
- Market moves (market entry, expansion strategies)
- Partnership moves (strategic partnerships, collaborations)

For each move, you should:
- Define clear objectives and success criteria
- Break down into manageable phases with timelines
- Assess risks and mitigation strategies
- Estimate resource requirements and costs
- Define measurable KPIs and success metrics
- Provide actionable implementation steps
- Consider dependencies and constraints

Always focus on practical, executable strategies that align with business goals and available resources. Consider the competitive landscape and market conditions in your recommendations.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute move strategy planning."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for move strategy"
                )

            # Extract move request from state
            move_request = self._extract_move_request(state)

            if not move_request:
                return self._set_error(state, "No move request provided")

            # Validate move request
            self._validate_move_request(move_request)

            # Generate move strategy
            move_strategy = await self._generate_move_strategy(move_request, state)

            # Store move strategy
            await self._store_move_strategy(move_strategy, state)

            # Add assistant message
            response = self._format_strategy_response(move_strategy)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "move_strategy": move_strategy.__dict__,
                    "move_type": move_request.move_type,
                    "objective": move_request.objective,
                    "timeline_days": move_strategy.timeline_days,
                    "success_probability": move_strategy.success_probability,
                    "estimated_cost": move_strategy.estimated_cost,
                },
            )

        except Exception as e:
            logger.error(f"Move strategy planning failed: {e}")
            return self._set_error(state, f"Move strategy planning failed: {str(e)}")

    def _extract_move_request(self, state: AgentState) -> Optional[MoveRequest]:
        """Extract move request from state."""
        # Check if move request is in state
        if "move_request" in state:
            request_data = state["move_request"]
            return MoveRequest(**request_data)

        # Extract from user message
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        # Parse move request from user input
        return self._parse_move_request(user_input, state)

    def _parse_move_request(
        self, user_input: str, state: AgentState
    ) -> Optional[MoveRequest]:
        """Parse move request from user input."""
        # Check for explicit move type mention
        move_types = list(self.move_templates.keys())
        detected_type = None

        for move_type in move_types:
            if move_type.lower() in user_input.lower():
                detected_type = move_type
                break

        if not detected_type:
            # Default to campaign
            detected_type = "campaign"

        # Extract other parameters
        objective = self._extract_parameter(
            user_input, ["objective", "goal", "purpose"], "awareness"
        )
        timeline = self._extract_parameter(
            user_input, ["timeline", "duration", "timeframe"], "medium_term"
        )
        budget = self._extract_parameter(
            user_input, ["budget", "cost", "investment"], "medium"
        )
        risk = self._extract_parameter(
            user_input, ["risk", "tolerance", "approach"], "moderate"
        )
        priority = self._extract_parameter(
            user_input, ["priority", "urgency", "importance"], "medium"
        )

        # Extract channels
        channels = self._extract_channels(user_input)

        # Extract success metrics
        success_metrics = self._extract_success_metrics(user_input)

        # Extract constraints
        constraints = self._extract_constraints(user_input)

        # Get target audience from context
        target_audience = state.get("target_audience", "general")

        # Create move request
        return MoveRequest(
            move_type=detected_type,
            objective=objective,
            target_audience=target_audience,
            timeline=timeline,
            budget_range=budget,
            risk_tolerance=risk,
            channels=channels,
            success_metrics=success_metrics,
            constraints=constraints,
            priority=priority,
        )

    def _extract_parameter(
        self, text: str, param_names: List[str], default: str
    ) -> str:
        """Extract parameter value from text."""
        for param_name in param_names:
            for pattern in [f"{param_name}:", f"{param_name} is", f"{param_name} ="]:
                if pattern in text.lower():
                    start_idx = text.lower().find(pattern)
                    if start_idx != -1:
                        start_idx += len(pattern)
                        remaining = text[start_idx:].strip()
                        # Get first word or phrase
                        words = remaining.split()
                        if words:
                            return words[0].strip(".,!?")
        return default

    def _extract_channels(self, text: str) -> List[str]:
        """Extract marketing channels from text."""
        channel_keywords = {
            "email": ["email", "newsletter", "mailing list"],
            "social": ["social", "facebook", "twitter", "instagram", "linkedin"],
            "paid_ads": ["ads", "advertising", "ppc", "google ads"],
            "content": ["content", "blog", "article", "video"],
            "seo": ["seo", "search", "organic"],
            "events": ["events", "webinars", "conferences"],
            "partnerships": ["partnership", "partner", "collaboration"],
            "pr": ["pr", "press", "media"],
            "direct": ["direct", "sales", "outreach"],
        }

        channels = []
        text_lower = text.lower()

        for channel, keywords in channel_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    channels.append(channel)
                    break

        return channels or ["social", "email"]  # Default channels

    def _extract_success_metrics(self, text: str) -> List[str]:
        """Extract success metrics from text."""
        metric_keywords = {
            "conversion_rate": ["conversion", "rate", "cr"],
            "roi": ["roi", "return", "investment"],
            "engagement": ["engagement", "interactions", "likes"],
            "reach": ["reach", "impressions", "views"],
            "leads": ["leads", "prospects", "mql"],
            "sales": ["sales", "revenue", "income"],
            "retention": ["retention", "churn", "loyalty"],
            "awareness": ["awareness", "brand", "recognition"],
        }

        metrics = []
        text_lower = text.lower()

        for metric, keywords in metric_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    metrics.append(metric)
                    break

        return metrics or ["engagement", "conversion_rate"]  # Default metrics

    def _extract_constraints(self, text: str) -> List[str]:
        """Extract constraints from text."""
        constraint_keywords = {
            "budget": ["budget", "cost", "financial"],
            "time": ["time", "deadline", "timeline"],
            "resources": ["resources", "team", "staff"],
            "technical": ["technical", "technology", "platform"],
            "regulatory": ["regulatory", "compliance", "legal"],
            "brand": ["brand", "guidelines", "identity"],
        }

        constraints = []
        text_lower = text.lower()

        for constraint, keywords in constraint_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    constraints.append(constraint)
                    break

        return constraints

    def _validate_move_request(self, request: MoveRequest):
        """Validate move request."""
        if request.move_type not in self.move_templates:
            raise ValidationError(f"Unsupported move type: {request.move_type}")

        if request.objective not in self.objective_templates:
            raise ValidationError(f"Unsupported objective: {request.objective}")

        if request.timeline not in ["short_term", "medium_term", "long_term"]:
            raise ValidationError(f"Invalid timeline: {request.timeline}")

        if request.budget_range not in self.budget_estimates:
            raise ValidationError(f"Invalid budget range: {request.budget_range}")

        if request.risk_tolerance not in self.risk_matrix:
            raise ValidationError(f"Invalid risk tolerance: {request.risk_tolerance}")

    async def _generate_move_strategy(
        self, request: MoveRequest, state: AgentState
    ) -> MoveStrategy:
        """Generate move strategy based on request."""
        try:
            # Get templates
            move_template = self.move_templates[request.move_type]
            objective_template = self.objective_templates[request.objective]
            risk_profile = self.risk_matrix[request.risk_tolerance]

            # Build strategy generation prompt
            prompt = self._build_strategy_prompt(
                request, move_template, objective_template, risk_profile, state
            )

            # Generate strategy
            strategy_text = await self.llm.generate(prompt)

            # Parse strategy components
            strategy = self._parse_strategy(
                strategy_text, request, move_template, objective_template, risk_profile
            )

            return strategy

        except Exception as e:
            logger.error(f"Strategy generation failed: {e}")
            raise DatabaseError(f"Strategy generation failed: {str(e)}")

    def _build_strategy_prompt(
        self,
        request: MoveRequest,
        move_template: Dict[str, Any],
        objective_template: Dict[str, Any],
        risk_profile: Dict[str, Any],
        state: AgentState,
    ) -> str:
        """Build strategy generation prompt."""
        # Get context from state
        context_summary = state.get("context_summary", "")
        company_name = state.get("company_name", "")
        industry = state.get("industry", "")
        brand_voice = state.get("brand_voice", "professional")

        # Build prompt
        prompt = f"""
Develop a comprehensive {request.move_type} move strategy with the following specifications:

MOVE TYPE: {request.move_type}
OBJECTIVE: {request.objective}
TARGET AUDIENCE: {request.target_audience}
TIMELINE: {request.timeline}
BUDGET RANGE: {request.budget_range}
RISK TOLERANCE: {request.risk_tolerance}
PRIORITY: {request.priority}
CHANNELS: {", ".join(request.channels)}
SUCCESS METRICS: {", ".join(request.success_metrics)}
CONSTRAINTS: {", ".join(request.constraints)}

"""

        if company_name:
            prompt += f"COMPANY: {company_name}\n"

        if industry:
            prompt += f"INDUSTRY: {industry}\n"

        if brand_voice:
            prompt += f"BRAND VOICE: {brand_voice}\n"

        if context_summary:
            prompt += f"CONTEXT: {context_summary}\n"

        prompt += f"""
TEMPLATE STRUCTURE: {move_template["phases"]}
DEFAULT TIMELINE: {move_template["default_timeline"]} days
TYPICAL CHANNELS: {", ".join(move_template["typical_channels"])}
SUCCESS FOCUS: {objective_template["focus"]}
KEY KPIS: {", ".join(objective_template["kpis"])}

Create a detailed strategy that includes:
1. Move name and description
2. Phased implementation plan with timelines
3. Resource requirements and cost estimates
4. Risk assessment and mitigation strategies
5. Success metrics and KPIs
6. Dependencies and constraints
7. Contingency plans
8. Actionable next steps

The strategy should be practical, executable, and aligned with the specified risk tolerance and budget constraints. Focus on measurable outcomes and clear success criteria.

Format the response as a structured strategy with clear sections and actionable recommendations.
"""

        return prompt

    def _parse_strategy(
        self,
        strategy_text: str,
        request: MoveRequest,
        move_template: Dict[str, Any],
        objective_template: Dict[str, Any],
        risk_profile: Dict[str, Any],
    ) -> MoveStrategy:
        """Parse strategy from generated text."""
        # Extract move name
        move_name = self._extract_section_content(
            strategy_text, ["Move Name", "Strategy Name", "Title"]
        )
        if not move_name:
            move_name = f"{request.move_type.title()} - {request.objective.title()}"

        # Extract description
        description = self._extract_section_content(
            strategy_text, ["Description", "Overview", "Summary"]
        )
        if not description:
            description = (
                f"Strategic {request.move_type} move to achieve {request.objective}"
            )

        # Generate phases
        phases = self._generate_phases(move_template["phases"], request.timeline)

        # Calculate timeline
        timeline_days = self._calculate_timeline(
            move_template["default_timeline"], request.timeline, risk_profile
        )

        # Estimate costs
        estimated_cost = self._estimate_costs(request.budget_range, risk_profile)

        # Calculate success probability
        success_probability = self._calculate_success_probability(
            risk_profile, request.constraints
        )

        # Generate risk assessment
        risk_assessment = self._generate_risk_assessment(
            move_template["risk_factors"], risk_profile
        )

        # Generate KPIs
        kpis = self._generate_kpis(request.success_metrics, objective_template["kpis"])

        # Generate required resources
        required_resources = self._generate_required_resources(
            request.channels, request.move_type
        )

        # Generate dependencies
        dependencies = self._generate_dependencies(request.constraints)

        # Generate contingency plans
        contingency_plans = self._generate_contingency_plans(risk_assessment["risks"])

        # Generate next steps
        next_steps = self._generate_next_steps(phases, request.priority)

        return MoveStrategy(
            move_name=move_name,
            move_type=request.move_type,
            objective=request.objective,
            description=description,
            phases=phases,
            timeline_days=timeline_days,
            estimated_cost=estimated_cost,
            success_probability=success_probability,
            risk_assessment=risk_assessment,
            kpis=kpis,
            required_resources=required_resources,
            dependencies=dependencies,
            contingency_plans=contingency_plans,
            next_steps=next_steps,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "risk_tolerance": request.risk_tolerance,
                "priority": request.priority,
                "channels": request.channels,
                "constraints": request.constraints,
            },
        )

    def _extract_section_content(self, text: str, section_names: List[str]) -> str:
        """Extract content from a section of the strategy text."""
        text_lower = text.lower()

        for section_name in section_names:
            pattern = f"{section_name.lower()}:"
            if pattern in text_lower:
                start_idx = text_lower.find(pattern)
                if start_idx != -1:
                    start_idx += len(pattern)
                    remaining = text[start_idx:].strip()
                    # Get first paragraph or line
                    lines = remaining.split("\n")
                    for line in lines:
                        line = line.strip()
                        if (
                            line
                            and not line.startswith("#")
                            and not line.startswith("*")
                        ):
                            return line
        return ""

    def _generate_phases(
        self, template_phases: List[str], timeline: str
    ) -> List[Dict[str, Any]]:
        """Generate phases for the strategy."""
        timeline_multipliers = {"short_term": 0.5, "medium_term": 1.0, "long_term": 2.0}

        multiplier = timeline_multipliers.get(timeline, 1.0)
        base_duration = 7  # 1 week per phase

        phases = []
        for i, phase_name in enumerate(template_phases):
            phase_duration = int(base_duration * multiplier)
            start_day = i * phase_duration
            end_day = (i + 1) * phase_duration

            phases.append(
                {
                    "name": phase_name.title(),
                    "description": f"Execute {phase_name} phase",
                    "start_day": start_day,
                    "end_day": end_day,
                    "duration_days": phase_duration,
                    "key_activities": self._get_phase_activities(phase_name),
                    "deliverables": self._get_phase_deliverables(phase_name),
                }
            )

        return phases

    def _get_phase_activities(self, phase_name: str) -> List[str]:
        """Get key activities for a phase."""
        activities = {
            "research": ["Market analysis", "Competitor research", "Audience analysis"],
            "planning": [
                "Strategy development",
                "Resource allocation",
                "Timeline creation",
            ],
            "creation": [
                "Content creation",
                "Asset development",
                "Creative production",
            ],
            "launch": ["Campaign activation", "Channel setup", "Monitoring deployment"],
            "optimization": [
                "Performance analysis",
                "A/B testing",
                "Strategy refinement",
            ],
            "development": ["Product development", "Feature implementation", "Testing"],
            "testing": ["User testing", "Quality assurance", "Feedback collection"],
            "localization": ["Market adaptation", "Translation", "Cultural adjustment"],
            "identification": [
                "Partner research",
                "Outreach list creation",
                "Initial contact",
            ],
            "outreach": ["Partner meetings", "Proposal development", "Negotiation"],
            "negotiation": [
                "Contract discussion",
                "Terms agreement",
                "Partnership formalization",
            ],
            "activation": [
                "Joint campaign planning",
                "Co-marketing execution",
                "Cross-promotion",
            ],
            "management": [
                "Relationship management",
                "Performance monitoring",
                "Renewal planning",
            ],
        }

        return activities.get(phase_name, ["Execute phase activities"])

    def _get_phase_deliverables(self, phase_name: str) -> List[str]:
        """Get deliverables for a phase."""
        deliverables = {
            "research": ["Research report", "Market insights", "Competitor analysis"],
            "planning": ["Strategy document", "Timeline", "Budget plan"],
            "creation": ["Creative assets", "Content pieces", "Marketing materials"],
            "launch": ["Live campaign", "Tracking setup", "Initial results"],
            "optimization": [
                "Performance report",
                "Optimization plan",
                "Updated assets",
            ],
            "development": ["Product prototype", "Feature set", "Technical specs"],
            "testing": ["Test results", "User feedback", "Quality report"],
            "localization": [
                "Localized assets",
                "Market adaptation plan",
                "Cultural guide",
            ],
            "identification": ["Partner list", "Research summary", "Outreach strategy"],
            "outreach": ["Partner contacts", "Meeting notes", "Proposal documents"],
            "negotiation": ["Partnership agreement", "Contract terms", "Legal review"],
            "activation": [
                "Joint campaign plan",
                "Co-marketing materials",
                "Launch assets",
            ],
            "management": ["Partnership report", "Performance metrics", "Renewal plan"],
        }

        return deliverables.get(phase_name, ["Phase deliverables"])

    def _calculate_timeline(
        self, default_days: int, timeline: str, risk_profile: Dict[str, Any]
    ) -> int:
        """Calculate timeline based on risk profile."""
        timeline_multipliers = {"short_term": 0.5, "medium_term": 1.0, "long_term": 2.0}

        multiplier = timeline_multipliers.get(timeline, 1.0)
        risk_modifier = risk_profile["timeline_modifier"]

        return int(default_days * multiplier * risk_modifier)

    def _estimate_costs(
        self, budget_range: str, risk_profile: Dict[str, Any]
    ) -> Dict[str, float]:
        """Estimate costs based on budget range and risk profile."""
        budget_info = self.budget_estimates[budget_range]
        risk_modifier = risk_profile["cost_modifier"]

        min_cost = budget_info["min"] * risk_modifier
        max_cost = budget_info["max"] * risk_modifier

        return {
            "min": min_cost,
            "max": max_cost,
            "estimated": (min_cost + max_cost) / 2,
            "unit": budget_info["unit"],
        }

    def _calculate_success_probability(
        self, risk_profile: Dict[str, Any], constraints: List[str]
    ) -> float:
        """Calculate success probability based on risk and constraints."""
        base_probability = 0.7  # 70% base success rate
        risk_modifier = risk_profile["success_modifier"]

        # Adjust for constraints
        constraint_penalty = len(constraints) * 0.05  # 5% penalty per constraint

        probability = base_probability * risk_modifier - constraint_penalty
        return max(0.3, min(0.95, probability))  # Clamp between 30% and 95%

    def _generate_risk_assessment(
        self, risk_factors: List[str], risk_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate risk assessment."""
        risks = []
        for factor in risk_factors:
            risks.append(
                {
                    "risk": factor,
                    "probability": "medium",
                    "impact": "medium",
                    "mitigation": f"Monitor and address {factor} proactively",
                }
            )

        return {
            "overall_risk": risk_profile["risk_tolerance"],
            "risks": risks,
            "mitigation_strategy": f"{risk_profile['risk_tolerance'].title()} risk approach with continuous monitoring",
        }

    def _generate_kpis(
        self, requested_metrics: List[str], objective_kpis: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate KPIs for the strategy."""
        all_kpis = list(set(requested_metrics + objective_kpis))

        kpis = []
        for kpi in all_kpis[:5]:  # Limit to 5 KPIs
            kpis.append(
                {
                    "name": kpi.replace("_", " ").title(),
                    "target": "To be determined",
                    "measurement": "Quantitative",
                    "frequency": "Weekly",
                }
            )

        return kpis

    def _generate_required_resources(
        self, channels: List[str], move_type: str
    ) -> List[str]:
        """Generate required resources."""
        resources = ["Marketing team", "Budget allocation"]

        if "email" in channels:
            resources.append("Email marketing platform")

        if "social" in channels:
            resources.append("Social media management tools")

        if "paid_ads" in channels:
            resources.append("Ad campaign management")

        if "content" in channels:
            resources.append("Content creation resources")

        if move_type == "product":
            resources.extend(["Product development team", "Technical resources"])

        if move_type == "market":
            resources.extend(["Market research team", "Local partners"])

        if move_type == "partnership":
            resources.extend(["Business development team", "Legal support"])

        return resources

    def _generate_dependencies(self, constraints: List[str]) -> List[str]:
        """Generate dependencies based on constraints."""
        dependencies = []

        if "budget" in constraints:
            dependencies.append("Budget approval")

        if "technical" in constraints:
            dependencies.append("Technical infrastructure")

        if "resources" in constraints:
            dependencies.append("Team availability")

        if "regulatory" in constraints:
            dependencies.append("Regulatory compliance")

        if "brand" in constraints:
            dependencies.append("Brand guidelines approval")

        return dependencies or ["Standard business processes"]

    def _generate_contingency_plans(
        self, risks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate contingency plans for identified risks."""
        plans = []

        for risk in risks[:3]:  # Limit to top 3 risks
            plans.append(
                {
                    "trigger": risk["risk"],
                    "response": f"Alternative approach for {risk['risk']}",
                    "timeline": "Immediate",
                    "resources": "Contingency budget",
                }
            )

        return plans

    def _generate_next_steps(
        self, phases: List[Dict[str, Any]], priority: str
    ) -> List[str]:
        """Generate next steps based on priority."""
        next_steps = []

        if priority in ["high", "urgent"]:
            next_steps.append("Immediate stakeholder approval")
            next_steps.append("Resource allocation")

        next_steps.append(f"Begin {phases[0]['name'].lower()} phase")
        next_steps.append("Set up tracking and monitoring")
        next_steps.append("Schedule regular review meetings")

        return next_steps

    async def _store_move_strategy(self, strategy: MoveStrategy, state: AgentState):
        """Store move strategy in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self.get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="moves",
                    workspace_id=state["workspace_id"],
                    data={
                        "name": strategy.move_name,
                        "type": strategy.move_type,
                        "objective": strategy.objective,
                        "description": strategy.description,
                        "phases": strategy.phases,
                        "timeline_days": strategy.timeline_days,
                        "estimated_cost": strategy.estimated_cost,
                        "success_probability": strategy.success_probability,
                        "risk_assessment": strategy.risk_assessment,
                        "kpis": strategy.kpis,
                        "required_resources": strategy.required_resources,
                        "dependencies": strategy.dependencies,
                        "contingency_plans": strategy.contingency_plans,
                        "next_steps": strategy.next_steps,
                        "status": "planned",
                        "created_at": strategy.metadata.get("generated_at"),
                        "updated_at": strategy.metadata.get("generated_at"),
                    },
                )

            # Store in working memory
            working_memory = self.get_tool("working_memory")
            if working_memory:
                session_id = state.get(
                    "session_id", f"move-{datetime.now().timestamp()}"
                )

                await working_memory.set_item(
                    session_id=session_id,
                    workspace_id=state["workspace_id"],
                    user_id=state["user_id"],
                    key=f"move_{strategy.move_type}_{strategy.move_name[:50]}",
                    value=strategy.__dict__,
                    ttl=7200,  # 2 hours
                )

        except Exception as e:
            logger.error(f"Failed to store move strategy: {e}")

    def _format_strategy_response(self, strategy: MoveStrategy) -> str:
        """Format strategy response for user."""
        response = f"Γ£à **{strategy.move_name} Strategy Created**\n\n"
        response += f"**Type:** {strategy.move_type.title()}\n"
        response += f"**Objective:** {strategy.objective.title()}\n"
        response += f"**Timeline:** {strategy.timeline_days} days\n"
        response += f"**Success Probability:** {strategy.success_probability:.1%}\n"
        response += f"**Estimated Cost:** ${strategy.estimated_cost['estimated']:.0f} ({strategy.estimated_cost['unit']})\n\n"

        response += f"**Description:**\n{strategy.description}\n\n"

        response += f"**Phases:**\n"
        for phase in strategy.phases:
            response += (
                f"ΓÇó {phase['name']}: Day {phase['start_day']}-{phase['end_day']}\n"
            )

        response += f"\n**Key KPIs:**\n"
        for kpi in strategy.kpis[:3]:
            response += f"ΓÇó {kpi['name']}\n"

        response += f"\n**Next Steps:**\n"
        for step in strategy.next_steps[:3]:
            response += f"ΓÇó {step}\n"

        return response

    def get_move_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available move templates."""
        return self.move_templates.copy()

    def get_objective_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available objective templates."""
        return self.objective_templates.copy()

    def get_risk_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Get risk assessment matrix."""
        return self.risk_matrix.copy()
