"""
BlackboxStrategist specialist agent for Raptorflow marketing automation.
Handles advanced strategic planning, complex problem-solving, and innovative solutions.
"""

import json
import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..base import BaseAgent
from ..config import ModelTier
from ..exceptions import DatabaseError, ValidationError
from ..state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


@dataclass
class StrategicChallenge:
    """Strategic challenge definition."""

    challenge_type: (
        str  # market_entry, competitive_advantage, growth_acceleration, transformation
    )
    complexity: str  # simple, complex, wicked
    scope: str  # tactical, operational, strategic
    urgency: str  # low, medium, high, critical
    volatility: int = 5  # 1-10 scale
    stakeholders: List[str] = None
    constraints: List[str] = None
    objectives: List[str] = None
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.stakeholders is None:
            self.stakeholders = []
        if self.constraints is None:
            self.constraints = []
        if self.objectives is None:
            self.objectives = []
        if self.context is None:
            self.context = {}


@dataclass
class StrategicOption:
    """Strategic option for solving challenge."""

    option_id: str
    name: str
    description: str
    approach: str  # conventional, innovative, disruptive
    feasibility: float  # 0-1
    impact: float  # 0-1
    risk: float  # 0-1
    resources_required: Dict[str, Any]
    timeline_months: int
    success_factors: List[str]
    potential_barriers: List[str]
    confidence_score: float


@dataclass
class StrategicRecommendation:
    """Strategic recommendation with implementation plan."""

    recommendation_id: str
    title: str
    executive_summary: str
    primary_option: StrategicOption
    secondary_options: List[StrategicOption]
    implementation_phases: List[Dict[str, Any]]
    risk_mitigation: Dict[str, Any]
    success_metrics: List[Dict[str, Any]]
    resource_allocation: Dict[str, Any]
    contingency_plans: List[Dict[str, Any]]
    confidence_score: float
    metadata: Dict[str, Any]


class BlackboxStrategist(BaseAgent):
    """Specialist agent for advanced strategic planning and complex problem-solving."""

    def __init__(self):
        super().__init__(
            name="BlackboxStrategist",
            description="Handles complex strategic challenges and innovative solutions",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database"],
        )

        # Strategic challenge templates
        self.challenge_templates = {
            "market_entry": {
                "focus": "entering new markets or segments",
                "key_factors": ["market_size", "competition", "barriers", "timing"],
                "approaches": [
                    "direct_entry",
                    "partnership",
                    "acquisition",
                    "digital_first",
                ],
                "complexity_drivers": [
                    "regulatory",
                    "cultural",
                    "competitive",
                    "infrastructure",
                ],
            },
            "competitive_advantage": {
                "focus": "developing sustainable competitive advantages",
                "key_factors": [
                    "differentiation",
                    "cost_leadership",
                    "innovation",
                    "customer_experience",
                ],
                "approaches": [
                    "product_innovation",
                    "service_excellence",
                    "operational_efficiency",
                    "ecosystem_build",
                ],
                "complexity_drivers": [
                    "market_dynamics",
                    "technology_disruption",
                    "customer_evolution",
                    "competitive_response",
                ],
            },
            "growth_acceleration": {
                "focus": "accelerating business growth and scaling",
                "key_factors": [
                    "market_penetration",
                    "product_expansion",
                    "channel_optimization",
                    "operational_scale",
                ],
                "approaches": [
                    "aggressive_expansion",
                    "strategic_partnerships",
                    "digital_transformation",
                    "market_consolidation",
                ],
                "complexity_drivers": [
                    "resource_constraints",
                    "market_saturation",
                    "operational_complexity",
                    "organizational_capacity",
                ],
            },
            "transformation": {
                "focus": "business model and organizational transformation",
                "key_factors": [
                    "business_model",
                    "organizational_structure",
                    "technology_stack",
                    "culture",
                ],
                "approaches": [
                    "digital_transformation",
                    "business_model_reinvention",
                    "organizational_redesign",
                    "ecosystem_integration",
                ],
                "complexity_drivers": [
                    "cultural_resistance",
                    "technical_debt",
                    "market_disruption",
                    "resource_reallocation",
                ],
            },
        }

        # Strategic approach frameworks
        self.strategic_frameworks = {
            "conventional": {
                "risk_profile": "low",
                "innovation_level": "incremental",
                "time_horizon": "short_to_medium",
                "resource_intensity": "low",
                "success_probability": 0.7,
            },
            "innovative": {
                "risk_profile": "medium",
                "innovation_level": "breakthrough",
                "time_horizon": "medium",
                "resource_intensity": "medium",
                "success_probability": 0.5,
            },
            "disruptive": {
                "risk_profile": "high",
                "innovation_level": "transformative",
                "time_horizon": "long",
                "resource_intensity": "high",
                "success_probability": 0.3,
            },
        }

        # Complexity assessment matrix
        self.complexity_matrix = {
            "simple": {
                "factors": 3,
                "interdependencies": "low",
                "uncertainty": "low",
                "stakeholders": 5,
                "analysis_depth": "surface",
            },
            "complex": {
                "factors": 7,
                "interdependencies": "medium",
                "uncertainty": "medium",
                "stakeholders": 15,
                "analysis_depth": "detailed",
            },
            "wicked": {
                "factors": 12,
                "interdependencies": "high",
                "uncertainty": "high",
                "stakeholders": 30,
                "analysis_depth": "comprehensive",
            },
        }

        # Strategic thinking models
        self.thinking_models = [
            "systems_thinking",
            "design_thinking",
            "blue_ocean_strategy",
            "jobs_to_be_done",
            "scenario_planning",
            "real_options",
            "game_theory",
            "complexity_theory",
        ]

    def get_system_prompt(self) -> str:
        """Get the system prompt for the BlackboxStrategist."""
        return """
You are the BlackboxStrategist, a specialist agent for Raptorflow marketing automation platform.

Your role is to tackle complex strategic challenges using advanced strategic thinking frameworks and innovative problem-solving approaches.

Key responsibilities:
1. Analyze complex strategic challenges across multiple dimensions
2. Generate innovative and unconventional strategic options
3. Apply multiple strategic thinking models and frameworks
4. Assess feasibility, impact, and risk of strategic options
5. Develop comprehensive implementation plans
6. Provide strategic recommendations with confidence assessments

Strategic challenges you can address:
- Market Entry (new markets, segments, geographies)
- Competitive Advantage (sustainable differentiation, positioning)
- Growth Acceleration (scaling, expansion, optimization)
- Business Transformation (digital, business model, organizational)

Strategic approaches you can employ:
- Conventional (proven, low-risk, incremental)
- Innovative (breakthrough, medium-risk, transformative)
- Disruptive (game-changing, high-risk, revolutionary)

Strategic thinking models you can apply:
- Systems Thinking (holistic perspective, interdependencies)
- Design Thinking (user-centric, iterative prototyping)
- Blue Ocean Strategy (value innovation, market creation)
- Jobs to be Done (customer needs, outcomes)
- Scenario Planning (future scenarios, contingency planning)
- Real Options (flexibility, staged investments)
- Game Theory (competitive dynamics, strategic moves)
- Complexity Theory (emergence, adaptation, self-organization)

Volatility Management (1-10 Scale):
- 1-3 (Low): Focus on incremental improvements, proven tactics, and high feasibility.
- 4-6 (Medium): Balance innovation with reliability. Introduce some unconventional elements.
- 7-8 (High): Aggressive expansion, "Black Moves", and high-reward/high-risk tactical plays.
- 9-10 (Extreme): Maximum disruption, radical departures from conventional marketing, and experimental maneuvers.

For each strategic challenge, you should:
- Define the problem space and key dimensions
- Apply appropriate strategic thinking models
- Generate multiple strategic options with different approaches
- Assess feasibility, impact, and risk for each option
- Develop implementation plans with clear phases
- Identify success factors and potential barriers
- Provide confidence assessments and contingency plans

Always think systemically, consider multiple perspectives, and challenge conventional assumptions. Focus on creating sustainable strategic advantages and innovative solutions.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute strategic analysis."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for strategic analysis"
                )

            # Extract strategic challenge from state
            strategic_challenge = self._extract_strategic_challenge(state)

            if not strategic_challenge:
                return self._set_error(state, "No strategic challenge provided")

            # Validate strategic challenge
            self._validate_strategic_challenge(strategic_challenge)

            # Generate strategic recommendation
            recommendation = await self._generate_strategic_recommendation(
                strategic_challenge, state
            )

            # Store strategic recommendation
            await self._store_strategic_recommendation(recommendation, state)

            # Add assistant message
            response = self._format_strategic_response(recommendation)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "strategic_recommendation": recommendation.__dict__,
                    "challenge_type": strategic_challenge.challenge_type,
                    "complexity": strategic_challenge.complexity,
                    "confidence_score": recommendation.confidence_score,
                    "primary_approach": recommendation.primary_option.approach,
                    "implementation_phases": len(recommendation.implementation_phases),
                },
            )

        except Exception as e:
            logger.error(f"Strategic analysis failed: {e}")
            return self._set_error(state, f"Strategic analysis failed: {str(e)}")

    def _extract_strategic_challenge(
        self, state: AgentState
    ) -> Optional[StrategicChallenge]:
        """Extract strategic challenge from state."""
        # Check if strategic challenge is in state
        if "strategic_challenge" in state:
            challenge_data = state["strategic_challenge"]
            return StrategicChallenge(**challenge_data)

        # Extract from user message
        user_input = self._extract_user_input(state)

        # Check for volatility in state (passed from API)
        volatility = state.get("risk_tolerance") or state.get("volatility_level")
        if not volatility and "memory_context" in state:
            volatility = state["memory_context"].get("risk_tolerance")

        if not volatility:
            volatility = 5

        if not user_input:
            # If no message, try to build from context if available
            return None

        # Parse strategic challenge from user input
        challenge = self._parse_strategic_challenge(user_input, state)
        if challenge:
            challenge.volatility = int(volatility)
        return challenge

    def _parse_strategic_challenge(
        self, user_input: str, state: AgentState
    ) -> Optional[StrategicChallenge]:
        """Parse strategic challenge from user input."""
        # Check for explicit challenge type mention
        challenge_types = list(self.challenge_templates.keys())
        detected_type = None

        for challenge_type in challenge_types:
            if challenge_type.lower() in user_input.lower():
                detected_type = challenge_type
                break

        if not detected_type:
            # Default to competitive advantage
            detected_type = "competitive_advantage"

        # Extract other parameters
        complexity = self._extract_parameter(
            user_input, ["complexity", "difficulty", "level"], "complex"
        )
        scope = self._extract_parameter(
            user_input, ["scope", "level", "scale"], "strategic"
        )
        urgency = self._extract_parameter(
            user_input, ["urgency", "priority", "timeline"], "medium"
        )

        # Extract stakeholders
        stakeholders = self._extract_stakeholders(user_input)

        # Extract constraints
        constraints = self._extract_constraints(user_input)

        # Extract objectives
        objectives = self._extract_objectives(user_input)

        # Get context from state
        context = {
            "company_name": state.get("company_name", ""),
            "industry": state.get("industry", ""),
            "context_summary": state.get("context_summary", ""),
        }

        # Create strategic challenge
        return StrategicChallenge(
            challenge_type=detected_type,
            complexity=complexity,
            scope=scope,
            urgency=urgency,
            stakeholders=stakeholders,
            constraints=constraints,
            objectives=objectives,
            context=context,
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

    def _extract_stakeholders(self, text: str) -> List[str]:
        """Extract stakeholders from text."""
        stakeholder_keywords = {
            "customers": ["customer", "client", "user"],
            "employees": ["employee", "staff", "team"],
            "investors": ["investor", "shareholder", "stakeholder"],
            "partners": ["partner", "supplier", "vendor"],
            "regulators": ["regulator", "government", "compliance"],
            "competitors": ["competitor", "competition", "rival"],
        }

        stakeholders = []
        text_lower = text.lower()

        for stakeholder, keywords in stakeholder_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    stakeholders.append(stakeholder)
                    break

        return stakeholders or ["customers", "employees"]  # Default stakeholders

    def _extract_constraints(self, text: str) -> List[str]:
        """Extract constraints from text."""
        constraint_keywords = {
            "budget": ["budget", "cost", "financial"],
            "time": ["time", "deadline", "timeline"],
            "resources": ["resources", "team", "staff"],
            "technology": ["technology", "technical", "infrastructure"],
            "regulatory": ["regulatory", "compliance", "legal"],
            "market": ["market", "competition", "demand"],
            "organizational": ["organizational", "culture", "structure"],
        }

        constraints = []
        text_lower = text.lower()

        for constraint, keywords in constraint_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    constraints.append(constraint)
                    break

        return constraints or ["budget", "time"]  # Default constraints

    def _extract_objectives(self, text: str) -> List[str]:
        """Extract objectives from text."""
        objective_keywords = {
            "growth": ["grow", "growth", "expand", "scale"],
            "profitability": ["profit", "margin", "profitability"],
            "market_share": ["market", "share", "position"],
            "innovation": ["innovate", "innovation", "new"],
            "efficiency": ["efficient", "optimize", "improve"],
            "customer_satisfaction": ["satisfaction", "experience", "loyalty"],
            "competitive_advantage": ["advantage", "differentiate", "unique"],
            "transformation": ["transform", "change", "evolve"],
        }

        objectives = []
        text_lower = text.lower()

        for objective, keywords in objective_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    objectives.append(objective)
                    break

        return objectives or ["growth", "competitive_advantage"]  # Default objectives

    def _validate_strategic_challenge(self, challenge: StrategicChallenge):
        """Validate strategic challenge."""
        if challenge.challenge_type not in self.challenge_templates:
            raise ValidationError(
                f"Unsupported challenge type: {challenge.challenge_type}"
            )

        if challenge.complexity not in self.complexity_matrix:
            raise ValidationError(f"Invalid complexity: {challenge.complexity}")

        if challenge.scope not in ["tactical", "operational", "strategic"]:
            raise ValidationError(f"Invalid scope: {challenge.scope}")

        if challenge.urgency not in ["low", "medium", "high", "critical"]:
            raise ValidationError(f"Invalid urgency: {challenge.urgency}")

        if not challenge.objectives:
            raise ValidationError("At least one objective is required")

    async def _generate_strategic_recommendation(
        self, challenge: StrategicChallenge, state: AgentState
    ) -> StrategicRecommendation:
        """Generate strategic recommendation based on challenge."""
        try:
            # Get template and configurations
            template = self.challenge_templates[challenge.challenge_type]
            complexity_config = self.complexity_matrix[challenge.complexity]

            # Gather enhanced intelligence using Swarm Skills
            intelligence = await self._gather_intelligence(challenge)

            # Add intelligence to context
            challenge.context["swarm_intelligence"] = intelligence

            # Build strategic analysis prompt
            prompt = self._build_strategic_prompt(
                challenge, template, complexity_config, state
            )

            # Generate strategic insights
            strategic_text = await self.llm.generate(prompt)

            # Parse strategic recommendation
            recommendation = await self._parse_strategic_recommendation(
                strategic_text, challenge, template, complexity_config
            )

            return recommendation

        except Exception as e:
            logger.error(f"Strategic recommendation generation failed: {e}")
            raise DatabaseError(f"Strategic recommendation generation failed: {str(e)}")

    async def _gather_intelligence(
        self, challenge: StrategicChallenge
    ) -> Dict[str, Any]:
        """Gather intelligence using Swarm Skills."""
        intelligence = {}

        # 1. Trend Spotting (if industry/market context exists)
        market_context = challenge.context.get("market") or challenge.context.get(
            "industry"
        )
        if market_context:
            trend_skill = self.skills_registry.get_skill("trend_spotter")
            if trend_skill:
                try:
                    logger.info("Swarm: Deploying TrendSpotter...")
                    trends = await trend_skill.execute(
                        {"agent": self, "industry": market_context}
                    )
                    intelligence["trends"] = trends
                except Exception as e:
                    logger.warning(f"TrendSpotter failed: {e}")

        # 2. Competitor Analysis (if competitors mentioned)
        competitors = challenge.context.get("competitors", [])
        if competitors and isinstance(competitors, list):
            comp_skill = self.skills_registry.get_skill("competitor_scout")
            if comp_skill:
                comp_data = []
                for comp in competitors[:2]:  # Limit to 2 for speed
                    try:
                        logger.info(f"Swarm: Deploying CompetitorScout for {comp}...")
                        res = await comp_skill.execute(
                            {
                                "agent": self,
                                "competitor_name": comp,
                                "competitor_url": "unknown",  # simplified
                            }
                        )
                        comp_data.append(res)
                    except Exception:
                        pass
                if comp_data:
                    intelligence["competitor_intel"] = comp_data

        return intelligence

    def _build_strategic_prompt(
        self,
        challenge: StrategicChallenge,
        template: Dict[str, Any],
        complexity_config: Dict[str, Any],
        state: AgentState,
    ) -> str:
        """Build strategic analysis prompt."""
        # Build prompt
        prompt = f"""
Analyze the following strategic challenge and develop comprehensive recommendations:

CHALLENGE TYPE: {challenge.challenge_type}
COMPLEXITY: {challenge.complexity}
SCOPE: {challenge.scope}
URGENCY: {challenge.urgency}
VOLATILITY: {challenge.volatility} (1-10 scale, where 10 is most disruptive/risky)
STAKEHOLDERS: {", ".join(challenge.stakeholders)}
CONSTRAINTS: {", ".join(challenge.constraints)}
OBJECTIVES: {", ".join(challenge.objectives)}

CONTEXT:
{json.dumps(challenge.context, indent=2)}

"""

        prompt += f"""
FOCUS AREA: {template["focus"]}
KEY FACTORS: {", ".join(template["key_factors"])}
APPROACHES: {", ".join(template["approaches"])}
COMPLEXITY DRIVERS: {", ".join(template["complexity_drivers"])}

ANALYSIS REQUIREMENTS:
- Factors to consider: {complexity_config["factors"]}
- Interdependency level: {complexity_config["interdependencies"]}
- Uncertainty level: {complexity_config["uncertainty"]}
- Stakeholder count: {complexity_config["stakeholders"]}
- Analysis depth: {complexity_config["analysis_depth"]}

STRATEGIC THINKING MODELS TO APPLY:
{", ".join(self.thinking_models[:4])}

Generate a comprehensive strategic recommendation that includes:
1. Executive summary of the challenge and recommended approach
2. Multiple strategic options (conventional, innovative, disruptive)
3. Feasibility, impact, and risk assessment for each option
4. Detailed implementation plan with phases and timelines
5. Risk mitigation strategies and contingency plans
6. Success metrics and monitoring framework
7. Resource allocation and requirements
8. Confidence assessment for the recommendation

Apply multiple strategic thinking models to ensure comprehensive analysis. Consider system dynamics, competitive forces, and future scenarios. Provide actionable recommendations with clear implementation paths.

Format the response as a structured strategic recommendation with clear sections and supporting analysis.
"""

        return prompt

    async def _parse_strategic_recommendation(
        self,
        strategic_text: str,
        challenge: StrategicChallenge,
        template: Dict[str, Any],
        complexity_config: Dict[str, Any],
    ) -> StrategicRecommendation:
        """Parse strategic recommendation from generated text."""
        # Generate recommendation ID
        recommendation_id = f"strategy_{challenge.challenge_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Generate title
        title = f"Strategic Recommendation: {challenge.challenge_type.replace('_', ' ').title()}"

        # Extract executive summary
        executive_summary = self._extract_section_content(
            strategic_text, ["Executive Summary", "Summary", "Overview"]
        )
        if not executive_summary:
            executive_summary = f"Comprehensive strategic approach to address {challenge.challenge_type} challenges"

        # Generate strategic options (Dynamic Evaluation)
        primary_option, secondary_options = await self._generate_strategic_options(
            challenge, template
        )

        # Generate implementation phases
        implementation_phases = self._generate_implementation_phases(
            challenge, primary_option
        )

        # Generate risk mitigation
        risk_mitigation = self._generate_risk_mitigation(challenge, primary_option)

        # Generate success metrics
        success_metrics = self._generate_success_metrics(challenge.objectives)

        # Generate resource allocation
        resource_allocation = self._generate_resource_allocation(primary_option)

        # Generate contingency plans
        contingency_plans = self._generate_contingency_plans(
            primary_option, challenge.constraints
        )

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            challenge, complexity_config
        )

        return StrategicRecommendation(
            recommendation_id=recommendation_id,
            title=title,
            executive_summary=executive_summary,
            primary_option=primary_option,
            secondary_options=secondary_options,
            implementation_phases=implementation_phases,
            risk_mitigation=risk_mitigation,
            success_metrics=success_metrics,
            resource_allocation=resource_allocation,
            contingency_plans=contingency_plans,
            confidence_score=confidence_score,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "challenge_complexity": challenge.complexity,
                "thinking_models_applied": self.thinking_models[:4],
                "stakeholder_count": len(challenge.stakeholders),
                "constraint_count": len(challenge.constraints),
            },
        )

    def _extract_section_content(self, text: str, section_names: List[str]) -> str:
        """Extract content from a section of the strategic text."""
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

    async def _generate_strategic_options(
        self, challenge: StrategicChallenge, template: Dict[str, Any]
    ) -> Tuple[StrategicOption, List[StrategicOption]]:
        """Generate strategic options using dynamic evaluation."""
        approaches = ["conventional", "innovative", "disruptive"]
        options = []

        # Get the evaluation skill
        eval_skill = self.skills_registry.get_skill("strategy_evaluation")

        for i, approach in enumerate(approaches):
            framework = self.strategic_frameworks[approach]

            # Create preliminary option dict for evaluation
            option_desc = f"Strategic option using {approach} approach"
            temp_option = {
                "name": f"{approach.title()} Approach",
                "approach": approach,
                "description": option_desc,
            }

            # Evaluate using skill (Critic Agent)
            evaluation = {
                "feasibility": 0.5,
                "impact": 0.5,
                "risk": 0.5,
                "confidence": 0.5,
            }
            if eval_skill and hasattr(eval_skill, "execute"):
                try:
                    evaluation = await eval_skill.execute(
                        {
                            "option": temp_option,
                            "challenge_context": {
                                "type": challenge.challenge_type,
                                "complexity": challenge.complexity,
                                "urgency": challenge.urgency,
                                "constraints": challenge.constraints,
                            },
                            "agent": self,
                        }
                    )
                except Exception as e:
                    logger.warning(f"Evaluation skill failed for {approach}: {e}")
                    # Fallback to defaults

            # Map risk score to low/medium/high for profile?
            # Or keep framework profile but use dynamic score?
            # We'll use the dynamic score for mathematical "risk" field.

            option = StrategicOption(
                option_id=f"option_{approach}_{i}",
                name=f"{approach.title()} Approach",
                description=option_desc,
                approach=approach,
                feasibility=evaluation.get("feasibility", 0.5),
                impact=evaluation.get("impact", 0.5),
                risk=evaluation.get("risk", 0.5),
                resources_required=self._generate_resource_requirements(approach),
                timeline_months=self._calculate_timeline(approach, challenge.scope),
                success_factors=self._generate_success_factors(
                    approach, template["key_factors"]
                ),
                potential_barriers=self._generate_potential_barriers(
                    approach, challenge.constraints
                ),
                confidence_score=framework[
                    "success_probability"
                ],  # Could also be dynamic
            )
            options.append(option)

        # Primary option is the one with best balance of feasibility and impact
        primary_option = max(options, key=lambda x: (x.feasibility + x.impact) / 2)
        secondary_options = [opt for opt in options if opt != primary_option]

        return primary_option, secondary_options

    # Deprecated hardcoded methods removed

    def _generate_resource_requirements(self, approach: str) -> Dict[str, Any]:
        """Generate resource requirements."""
        base_requirements = {
            "conventional": {
                "budget": "medium",
                "team_size": 5,
                "expertise": "standard",
            },
            "innovative": {
                "budget": "high",
                "team_size": 8,
                "expertise": "specialized",
            },
            "disruptive": {
                "budget": "very_high",
                "team_size": 12,
                "expertise": "cutting_edge",
            },
        }

        return base_requirements[approach]

    def _calculate_timeline(self, approach: str, scope: str) -> int:
        """Calculate timeline in months."""
        base_timeline = {"conventional": 6, "innovative": 12, "disruptive": 24}

        scope_modifier = {"tactical": 0.5, "operational": 1.0, "strategic": 2.0}

        return int(base_timeline[approach] * scope_modifier[scope])

    def _generate_success_factors(
        self, approach: str, key_factors: List[str]
    ) -> List[str]:
        """Generate success factors."""
        factors = []

        # Add approach-specific factors
        approach_factors = {
            "conventional": [
                "execution_excellence",
                "resource_optimization",
                "stakeholder_buy_in",
            ],
            "innovative": [
                "innovation_capability",
                "market_acceptance",
                "adaptive_execution",
            ],
            "disruptive": [
                "visionary_leadership",
                "market_creation",
                "ecosystem_development",
            ],
        }

        factors.extend(approach_factors[approach])
        factors.extend(key_factors[:2])  # Add first 2 key factors

        return factors[:5]  # Limit to 5 factors

    def _generate_potential_barriers(
        self, approach: str, constraints: List[str]
    ) -> List[str]:
        """Generate potential barriers."""
        barriers = []

        # Add approach-specific barriers
        approach_barriers = {
            "conventional": [
                "resource_constraints",
                "market_conditions",
                "competitive_pressure",
            ],
            "innovative": [
                "adoption_resistance",
                "technical_challenges",
                "market_uncertainty",
            ],
            "disruptive": [
                "market_resistance",
                "regulatory_hurdles",
                "ecosystem_challenges",
            ],
        }

        barriers.extend(approach_barriers[approach])
        barriers.extend(constraints[:2])  # Add first 2 constraints

        return barriers[:4]  # Limit to 4 barriers

    def _generate_implementation_phases(
        self, challenge: StrategicChallenge, option: StrategicOption
    ) -> List[Dict[str, Any]]:
        """Generate implementation phases."""
        phases = []
        total_months = option.timeline_months

        phase_configs = [
            {
                "name": "Planning",
                "duration": 0.1,
                "activities": [
                    "strategy_development",
                    "resource_planning",
                    "team_formation",
                ],
            },
            {
                "name": "Preparation",
                "duration": 0.2,
                "activities": [
                    "stakeholder_alignment",
                    "capability_building",
                    "pilot_testing",
                ],
            },
            {
                "name": "Execution",
                "duration": 0.5,
                "activities": ["full_implementation", "monitoring", "optimization"],
            },
            {
                "name": "Scaling",
                "duration": 0.2,
                "activities": ["expansion", "refinement", "institutionalization"],
            },
        ]

        cumulative_months = 0
        for config in phase_configs:
            phase_duration = int(total_months * config["duration"])
            start_month = cumulative_months
            end_month = cumulative_months + phase_duration

            phase = {
                "name": config["name"],
                "start_month": start_month,
                "end_month": end_month,
                "duration_months": phase_duration,
                "key_activities": config["activities"],
                "deliverables": [
                    f"{config['name']}_deliverable_1",
                    f"{config['name']}_deliverable_2",
                ],
                "success_criteria": [
                    f"{config['name']}_criteria_1",
                    f"{config['name']}_criteria_2",
                ],
                "risks": [f"{config['name']}_risk_1", f"{config['name']}_risk_2"],
            }

            phases.append(phase)
            cumulative_months = end_month

        return phases

    def _generate_risk_mitigation(
        self, challenge: StrategicChallenge, option: StrategicOption
    ) -> Dict[str, Any]:
        """Generate risk mitigation strategies."""
        return {
            "high_priority_risks": [
                {
                    "risk": "execution_risk",
                    "probability": "medium",
                    "impact": "high",
                    "mitigation": "robust_planning_and_monitoring",
                    "contingency": "alternative_implementation_approach",
                },
                {
                    "risk": "market_risk",
                    "probability": "medium",
                    "impact": "medium",
                    "mitigation": "continuous_market_intelligence",
                    "contingency": "strategy_pivot",
                },
            ],
            "monitoring_framework": {
                "frequency": "monthly",
                "key_indicators": [
                    "progress_metrics",
                    "risk_indicators",
                    "performance_metrics",
                ],
                "escalation_triggers": [
                    "schedule_deviation",
                    "budget_overrun",
                    "stakeholder_concerns",
                ],
            },
            "risk_governance": {
                "risk_committee": "strategic_leadership_team",
                "review_frequency": "quarterly",
                "decision_authority": "executive_sponsor",
            },
        }

    def _generate_success_metrics(self, objectives: List[str]) -> List[Dict[str, Any]]:
        """Generate success metrics."""
        metrics = []

        for objective in objectives[:3]:  # Limit to 3 objectives
            metric = {
                "name": f"{objective}_metric",
                "description": f"Measure of {objective} achievement",
                "target": "to_be_determined",
                "measurement": "quantitative",
                "frequency": "monthly",
                "owner": "strategy_team",
            }
            metrics.append(metric)

        return metrics

    def _generate_resource_allocation(self, option: StrategicOption) -> Dict[str, Any]:
        """Generate resource allocation plan."""
        return {
            "human_resources": {
                "team_size": option.resources_required["team_size"],
                "expertise_required": option.resources_required["expertise"],
                "key_roles": [
                    "strategy_lead",
                    "implementation_manager",
                    "subject_matter_experts",
                ],
            },
            "financial_resources": {
                "total_budget": option.resources_required["budget"],
                "allocation_phases": ["planning", "execution", "scaling"],
                "contingency_reserve": "15%",
            },
            "technology_resources": {
                "tools_required": ["project_management", "analytics", "collaboration"],
                "infrastructure_needs": "based_on_approach",
                "data_requirements": "performance_and_tracking",
            },
            "external_resources": {
                "consultants": "as_needed",
                "partners": "strategic_partnerships",
                "vendors": "specialized_services",
            },
        }

    def _generate_contingency_plans(
        self, option: StrategicOption, constraints: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate contingency plans."""
        return [
            {
                "trigger": "budget_constraints",
                "response": "phased_implementation_with_minimum_viable_scope",
                "timeline_impact": "+3_months",
                "resource_impact": "reduce_team_by_30%",
            },
            {
                "trigger": "market_resistance",
                "response": "pivot_to_alternative_approach",
                "timeline_impact": "+6_months",
                "resource_impact": "additional_market_research_budget",
            },
            {
                "trigger": "execution_challenges",
                "response": "external_expert_engagement",
                "timeline_impact": "+2_months",
                "resource_impact": "consulting_fees",
            },
        ]

    def _calculate_confidence_score(
        self, challenge: StrategicChallenge, complexity_config: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence score."""
        # Base confidence from complexity
        complexity_scores = {"simple": 0.9, "complex": 0.7, "wicked": 0.5}

        base_confidence = complexity_scores[challenge.complexity]

        # Adjust for constraints (more constraints = lower confidence)
        constraint_penalty = min(0.2, len(challenge.constraints) * 0.05)

        # Adjust for stakeholders (more stakeholders = lower confidence)
        stakeholder_penalty = min(0.1, len(challenge.stakeholders) * 0.01)

        # Calculate final confidence
        confidence = base_confidence - constraint_penalty - stakeholder_penalty
        return max(0.3, min(0.95, confidence))  # Clamp between 30% and 95%

    async def _store_strategic_recommendation(
        self, recommendation: StrategicRecommendation, state: AgentState
    ):
        """Store strategic recommendation in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self.get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="strategic_recommendations",
                    workspace_id=state["workspace_id"],
                    data={
                        "recommendation_id": recommendation.recommendation_id,
                        "title": recommendation.title,
                        "executive_summary": recommendation.executive_summary,
                        "primary_option": recommendation.primary_option.__dict__,
                        "secondary_options": [
                            opt.__dict__ for opt in recommendation.secondary_options
                        ],
                        "implementation_phases": recommendation.implementation_phases,
                        "risk_mitigation": recommendation.risk_mitigation,
                        "success_metrics": recommendation.success_metrics,
                        "resource_allocation": recommendation.resource_allocation,
                        "contingency_plans": recommendation.contingency_plans,
                        "confidence_score": recommendation.confidence_score,
                        "status": "recommended",
                        "created_at": recommendation.metadata.get("generated_at"),
                        "updated_at": recommendation.metadata.get("generated_at"),
                    },
                )

            # Store in working memory
            working_memory = self.get_tool("working_memory")
            if working_memory:
                session_id = state.get(
                    "session_id", f"strategy-{datetime.now().timestamp()}"
                )

                await working_memory.set_item(
                    session_id=session_id,
                    workspace_id=state["workspace_id"],
                    user_id=state["user_id"],
                    key=f"strategy_{recommendation.recommendation_id}",
                    value=recommendation.__dict__,
                    ttl=14400,  # 4 hours
                )

        except Exception as e:
            logger.error(f"Failed to store strategic recommendation: {e}")

    def _format_strategic_response(
        self, recommendation: StrategicRecommendation
    ) -> str:
        """Format strategic response for user."""
        response = f"Γ£à **{recommendation.title}**\n\n"
        response += (
            f"**Primary Approach:** {recommendation.primary_option.approach.title()}\n"
        )
        response += (
            f"**Timeline:** {recommendation.primary_option.timeline_months} months\n"
        )
        response += f"**Confidence Score:** {recommendation.confidence_score:.1%}\n\n"

        response += f"**Executive Summary:**\n{recommendation.executive_summary}\n\n"

        response += f"**Primary Option:** {recommendation.primary_option.name}\n"
        response += (
            f"ΓÇó Feasibility: {recommendation.primary_option.feasibility:.1%}\n"
        )
        response += f"ΓÇó Impact: {recommendation.primary_option.impact:.1%}\n"
        response += f"ΓÇó Risk: {recommendation.primary_option.risk:.1%}\n\n"

        response += f"**Implementation Phases:**\n"
        for phase in recommendation.implementation_phases:
            response += f"ΓÇó {phase['name']}: Month {phase['start_month']}-{phase['end_month']}\n"

        response += f"\n**Key Success Factors:**\n"
        for factor in recommendation.primary_option.success_factors[:3]:
            response += f"ΓÇó {factor}\n"

        response += f"\n**Next Steps:**\n"
        response += f"ΓÇó Review and approve strategic recommendation\n"
        response += f"ΓÇó Form implementation team\n"
        response += f"ΓÇó Begin planning phase\n"

        return response

    def get_challenge_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available challenge templates."""
        return self.challenge_templates.copy()

    def get_strategic_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Get strategic frameworks."""
        return self.strategic_frameworks.copy()

    def get_thinking_models(self) -> List[str]:
        """Get strategic thinking models."""
        return self.thinking_models.copy()
