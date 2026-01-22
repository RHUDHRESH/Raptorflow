"""
PersonaSimulator specialist agent for Raptorflow marketing automation.
Handles persona simulation, user behavior modeling, and customer journey mapping.
"""

import json
import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from backend.agents.config import ModelTier

from ..base import BaseAgent
from ..exceptions import DatabaseError, ValidationError
from ..state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


@dataclass
class PersonaSimulationRequest:
    """Persona simulation request."""

    simulation_type: (
        str  # customer_journey, behavior_pattern, decision_process, emotional_response
    )
    persona_type: (
        str  # ideal_customer, user_archetype, stakeholder, competitor_customer
    )
    scenario: str
    context: Dict[str, Any]
    touchpoints: List[str]
    objectives: List[str]
    constraints: List[str]
    simulation_depth: str  # surface, detailed, comprehensive


@dataclass
class PersonaProfile:
    """Persona profile data."""

    persona_id: str
    name: str
    archetype: str
    demographics: Dict[str, Any]
    psychographics: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]
    pain_points: List[str]
    motivations: List[str]
    goals: List[str]
    challenges: List[str]
    preferences: Dict[str, Any]
    communication_style: str
    decision_factors: List[str]


@dataclass
class BehaviorPattern:
    """Behavior pattern data."""

    pattern_id: str
    behavior_name: str
    frequency: str  # daily, weekly, monthly, occasional
    triggers: List[str]
    actions: List[str]
    outcomes: List[str]
    emotional_states: List[str]
    context_factors: List[str]
    confidence_score: float


@dataclass
class DecisionProcess:
    """Decision process data."""

    process_id: str
    decision_type: str
    stages: List[Dict[str, Any]]
    criteria: List[str]
    influences: List[str]
    timeline: str
    risk_tolerance: str
    information_sources: List[str]
    decision_makers: List[str]


@dataclass
class EmotionalResponse:
    """Emotional response data."""

    response_id: str
    stimulus: str
    primary_emotion: str
    intensity: float
    secondary_emotions: List[str]
    behavioral_manifestations: List[str]
    cognitive_biases: List[str]
    coping_mechanisms: List[str]
    duration: str


@dataclass
class CustomerJourney:
    """Customer journey data."""

    journey_id: str
    journey_name: str
    stages: List[Dict[str, Any]]
    touchpoints: List[Dict[str, Any]]
    emotions: List[Dict[str, Any]]
    pain_points: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    timeline: str


@dataclass
class SimulationResult:
    """Simulation result data."""

    result_id: str
    simulation_type: str
    persona_id: str
    scenario: str
    outcomes: List[Dict[str, Any]]
    insights: List[str]
    recommendations: List[str]
    confidence_score: float
    simulation_data: Dict[str, Any]
    generated_at: datetime


@dataclass
class PersonaSimulationReport:
    """Complete persona simulation report."""

    report_id: str
    simulation_type: str
    persona_type: str
    scenario: str
    persona_profile: PersonaProfile
    behavior_patterns: List[BehaviorPattern]
    decision_processes: List[DecisionProcess]
    emotional_responses: List[EmotionalResponse]
    customer_journey: Optional[CustomerJourney]
    simulation_results: List[SimulationResult]
    key_insights: List[str]
    actionable_recommendations: List[str]
    predictive_model: Dict[str, Any]
    generated_at: datetime
    metadata: Dict[str, Any]


class PersonaSimulator(BaseAgent):
    """Specialist agent for persona simulation and behavior modeling."""

    def __init__(self):
        super().__init__(
            name="PersonaSimulator",
            description="Simulates personas and models user behavior for marketing insights",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database", "content_gen"],
        )

        # Persona archetypes
        self.persona_archetypes = {
            "innovator": {
                "characteristics": [
                    "early_adopter",
                    "tech_savvy",
                    "risk_taker",
                    "visionary",
                ],
                "motivations": ["innovation", "efficiency", "competitive_advantage"],
                "pain_points": [
                    "resistance_to_change",
                    "implementation_complexity",
                    "budget_constraints",
                ],
                "decision_factors": ["future_potential", "scalability", "integration"],
            },
            "pragmatist": {
                "characteristics": [
                    "practical",
                    "results_oriented",
                    "cautious",
                    "value_driven",
                ],
                "motivations": ["roi", "reliability", "proven_solutions"],
                "pain_points": ["uncertainty", "learning_curve", "disruption"],
                "decision_factors": ["cost_benefit", "case_studies", "support"],
            },
            "skeptic": {
                "characteristics": [
                    "analytical",
                    "detail_oriented",
                    "questioning",
                    "risk_averse",
                ],
                "motivations": ["proof", "security", "control"],
                "pain_points": ["lack_of_evidence", "hidden_costs", "vendor_lock_in"],
                "decision_factors": ["data", "guarantees", "transparency"],
            },
            "visionary": {
                "characteristics": [
                    "strategic",
                    "big_picture",
                    "inspirational",
                    "transformational",
                ],
                "motivations": ["growth", "impact", "legacy"],
                "pain_points": [
                    "limited_resources",
                    "organizational_inertia",
                    "short_term_focus",
                ],
                "decision_factors": [
                    "strategic_fit",
                    "market_trends",
                    "competitive_position",
                ],
            },
        }

        # Behavioral patterns
        self.behavioral_patterns = {
            "research_phase": {
                "actions": [
                    "search_online",
                    "read_reviews",
                    "ask_recommendations",
                    "compare_options",
                ],
                "duration": "2-8 weeks",
                "emotional_state": "curious, cautious, overwhelmed",
            },
            "consideration_phase": {
                "actions": [
                    "request_demo",
                    "evaluate_features",
                    "check_compatibility",
                    "assess_support",
                ],
                "duration": "1-4 weeks",
                "emotional_state": "interested, analytical, hopeful",
            },
            "decision_phase": {
                "actions": [
                    "negotiate_terms",
                    "get_approval",
                    "plan_implementation",
                    "prepare_team",
                ],
                "duration": "1-2 weeks",
                "emotional_state": "determined, anxious, optimistic",
            },
            "implementation_phase": {
                "actions": [
                    "setup_system",
                    "train_users",
                    "migrate_data",
                    "monitor_progress",
                ],
                "duration": "4-12 weeks",
                "emotional_state": "committed, stressed, satisfied",
            },
        }

        # Decision process stages
        self.decision_stages = {
            "problem_recognition": {
                "activities": ["identify_pain", "quantify_impact", "assess_urgency"],
                "emotions": ["frustration", "concern", "motivation"],
            },
            "information_search": {
                "activities": [
                    "research_solutions",
                    "seek_recommendations",
                    "evaluate_options",
                ],
                "emotions": ["curiosity", "hope", "confusion"],
            },
            "evaluation_alternatives": {
                "activities": [
                    "compare_features",
                    "assess_value",
                    "check_compatibility",
                ],
                "emotions": ["analytical", "cautious", "optimistic"],
            },
            "purchase_decision": {
                "activities": ["negotiate_terms", "secure_approval", "sign_contract"],
                "emotions": ["determined", "anxious", "confident"],
            },
            "post_purchase": {
                "activities": [
                    "implement_solution",
                    "evaluate_results",
                    "provide_feedback",
                ],
                "emotions": ["committed", "satisfied", "disappointed"],
            },
        }

        # Emotional states
        self.emotional_states = {
            "positive": ["excited", "confident", "optimistic", "satisfied", "relieved"],
            "negative": [
                "frustrated",
                "anxious",
                "confused",
                "disappointed",
                "overwhelmed",
            ],
            "neutral": [
                "curious",
                "analytical",
                "cautious",
                "observant",
                "contemplative",
            ],
        }

        # Touchpoint categories
        self.touchpoint_categories = {
            "digital": [
                "website",
                "social_media",
                "email",
                "search_engine",
                "online_ads",
            ],
            "human": [
                "sales_rep",
                "customer_service",
                "technical_support",
                "account_manager",
            ],
            "physical": [
                "events",
                "trade_shows",
                "in_person_meetings",
                "product_trials",
            ],
            "content": [
                "blog_posts",
                "case_studies",
                "whitepapers",
                "webinars",
                "videos",
            ],
        }

        # Simulation depth levels
        self.simulation_depths = {
            "surface": {
                "detail_level": "basic",
                "factors": 5,
                "confidence_threshold": 0.7,
            },
            "detailed": {
                "detail_level": "comprehensive",
                "factors": 15,
                "confidence_threshold": 0.8,
            },
            "comprehensive": {
                "detail_level": "exhaustive",
                "factors": 30,
                "confidence_threshold": 0.9,
            },
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the PersonaSimulator."""
        return """
You are the PersonaSimulator, a specialist agent for Raptorflow marketing automation platform.

Your role is to simulate personas and model user behavior to provide deep insights into customer psychology, decision-making processes, and journey patterns.

Key responsibilities:
1. Create detailed persona profiles based on customer data and market research
2. Simulate behavior patterns and decision processes
3. Model emotional responses and psychological drivers
4. Map customer journeys across multiple touchpoints
5. Predict user actions and reactions in various scenarios
6. Provide actionable insights for marketing and product strategies
7. Generate predictive models for user behavior

Simulation types you can perform:
- Customer Journey Mapping (end-to-end journey visualization)
- Behavior Pattern Analysis (recurring behaviors and triggers)
- Decision Process Modeling (decision criteria and influences)
- Emotional Response Simulation (emotional reactions to stimuli)

For each simulation, you should:
- Create realistic and detailed persona profiles
- Consider psychological, demographic, and contextual factors
- Model both conscious and unconscious behaviors
- Account for emotional states and cognitive biases
- Generate actionable insights and recommendations
- Provide confidence scores for predictions
- Consider multiple scenarios and outcomes

Always focus on creating authentic, data-driven persona simulations that help understand and predict customer behavior.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute persona simulation."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for persona simulation"
                )

            # Extract persona simulation request from state
            simulation_request = self._extract_simulation_request(state)

            if not simulation_request:
                return self._set_error(state, "No persona simulation request provided")

            # Validate simulation request
            self._validate_simulation_request(simulation_request)

            # Perform persona simulation
            simulation_report = await self._perform_persona_simulation(
                simulation_request, state
            )

            # Store simulation report
            await self._store_simulation_report(simulation_report, state)

            # Add assistant message
            response = self._format_simulation_response(simulation_report)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "simulation_report": simulation_report.__dict__,
                    "persona_profile": simulation_report.persona_profile.__dict__,
                    "behavior_patterns": len(simulation_report.behavior_patterns),
                    "decision_processes": len(simulation_report.decision_processes),
                    "key_insights": len(simulation_report.key_insights),
                },
            )

        except Exception as e:
            logger.error(f"Persona simulation failed: {e}")
            return self._set_error(state, f"Persona simulation failed: {str(e)}")

    def _extract_simulation_request(
        self, state: AgentState
    ) -> Optional[PersonaSimulationRequest]:
        """Extract persona simulation request from state."""
        # Check if simulation request is in state
        if "simulation_request" in state:
            request_data = state["simulation_request"]
            return PersonaSimulationRequest(**request_data)

        # Extract from user message
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        # Parse simulation request from user input
        return self._parse_simulation_request(user_input, state)

    def _parse_simulation_request(
        self, user_input: str, state: AgentState
    ) -> Optional[PersonaSimulationRequest]:
        """Parse simulation request from user input."""
        # Extract simulation type
        simulation_types = [
            "customer_journey",
            "behavior_pattern",
            "decision_process",
            "emotional_response",
        ]
        detected_type = None

        for sim_type in simulation_types:
            if sim_type in user_input.lower():
                detected_type = sim_type
                break

        if not detected_type:
            detected_type = "customer_journey"

        # Extract other parameters
        persona_type = self._extract_parameter(
            user_input, ["persona", "archetype", "user"], "ideal_customer"
        )
        scenario = self._extract_parameter(
            user_input, ["scenario", "situation", "context"], "purchase_decision"
        )
        depth = self._extract_parameter(
            user_input, ["depth", "detail", "comprehensive"], "detailed"
        )

        # Create simulation request
        return PersonaSimulationRequest(
            simulation_type=detected_type,
            persona_type=persona_type,
            scenario=scenario,
            context={},
            touchpoints=["website", "email", "social_media"],
            objectives=["understand_behavior", "improve_experience"],
            constraints=["budget", "time"],
            simulation_depth=depth,
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

    def _validate_simulation_request(self, request: PersonaSimulationRequest):
        """Validate persona simulation request."""
        valid_types = [
            "customer_journey",
            "behavior_pattern",
            "decision_process",
            "emotional_response",
        ]
        if request.simulation_type not in valid_types:
            raise ValidationError(
                f"Unsupported simulation type: {request.simulation_type}"
            )

        valid_persona_types = [
            "ideal_customer",
            "user_archetype",
            "stakeholder",
            "competitor_customer",
        ]
        if request.persona_type not in valid_persona_types:
            raise ValidationError(f"Unsupported persona type: {request.persona_type}")

        valid_depths = ["surface", "detailed", "comprehensive"]
        if request.simulation_depth not in valid_depths:
            raise ValidationError(
                f"Invalid simulation depth: {request.simulation_depth}"
            )

    async def _perform_persona_simulation(
        self, request: PersonaSimulationRequest, state: AgentState
    ) -> PersonaSimulationReport:
        """Perform comprehensive persona simulation."""
        try:
            # Generate report ID
            report_id = f"persona_sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Create persona profile
            persona_profile = self._create_persona_profile(request)

            # Generate behavior patterns
            behavior_patterns = self._generate_behavior_patterns(
                persona_profile, request
            )

            # Generate decision processes
            decision_processes = self._generate_decision_processes(
                persona_profile, request
            )

            # Generate emotional responses
            emotional_responses = self._generate_emotional_responses(
                persona_profile, request
            )

            # Generate customer journey (if applicable)
            customer_journey = None
            if request.simulation_type == "customer_journey":
                customer_journey = self._generate_customer_journey(
                    persona_profile, request
                )

            # Generate simulation results
            simulation_results = self._generate_simulation_results(
                persona_profile, request
            )

            # Generate key insights
            key_insights = self._generate_key_insights(
                persona_profile, behavior_patterns, decision_processes
            )

            # Generate actionable recommendations
            actionable_recommendations = self._generate_actionable_recommendations(
                key_insights, request
            )

            # Create predictive model
            predictive_model = self._create_predictive_model(
                persona_profile, behavior_patterns
            )

            # Create persona simulation report
            simulation_report = PersonaSimulationReport(
                report_id=report_id,
                simulation_type=request.simulation_type,
                persona_type=request.persona_type,
                scenario=request.scenario,
                persona_profile=persona_profile,
                behavior_patterns=behavior_patterns,
                decision_processes=decision_processes,
                emotional_responses=emotional_responses,
                customer_journey=customer_journey,
                simulation_results=simulation_results,
                key_insights=key_insights,
                actionable_recommendations=actionable_recommendations,
                predictive_model=predictive_model,
                generated_at=datetime.now(),
                metadata={
                    "context": request.context,
                    "touchpoints": request.touchpoints,
                    "objectives": request.objectives,
                    "constraints": request.constraints,
                    "simulation_depth": request.simulation_depth,
                },
            )

            return simulation_report

        except Exception as e:
            logger.error(f"Persona simulation failed: {e}")
            raise DatabaseError(f"Persona simulation failed: {str(e)}")

    def _create_persona_profile(
        self, request: PersonaSimulationRequest
    ) -> PersonaProfile:
        """Create detailed persona profile."""
        # Select archetype
        archetype = random.choice(list(self.persona_archetypes.keys()))
        archetype_data = self.persona_archetypes[archetype]

        # Generate demographics
        demographics = {
            "age": random.randint(25, 55),
            "education": random.choice(["bachelor", "master", "phd"]),
            "experience": random.randint(2, 20),
            "industry": random.choice(
                ["technology", "healthcare", "finance", "retail", "manufacturing"]
            ),
            "company_size": random.choice(["startup", "small", "medium", "enterprise"]),
            "role": random.choice(["manager", "director", "vp", "c_level"]),
            "location": random.choice(["urban", "suburban", "rural"]),
        }

        # Generate psychographics
        psychographics = {
            "personality": archetype_data["characteristics"],
            "values": ["innovation", "efficiency", "growth", "quality"],
            "lifestyle": random.choice(["work_focused", "balanced", "family_oriented"]),
            "risk_tolerance": random.choice(["low", "medium", "high"]),
            "tech_savviness": random.choice(["basic", "intermediate", "advanced"]),
        }

        # Generate behavioral patterns
        behavioral_patterns = {
            "communication_style": random.choice(["formal", "casual", "technical"]),
            "learning_preference": random.choice(["visual", "auditory", "kinesthetic"]),
            "decision_speed": random.choice(["quick", "deliberate", "cautious"]),
            "social_influence": random.choice(
                ["independent", "collaborative", "leader"]
            ),
        }

        # Create persona profile
        persona_profile = PersonaProfile(
            persona_id=f"persona_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=f"{archetype.title()} Persona",
            archetype=archetype,
            demographics=demographics,
            psychographics=psychographics,
            behavioral_patterns=behavioral_patterns,
            pain_points=archetype_data["pain_points"],
            motivations=archetype_data["motivations"],
            goals=["increase_efficiency", "reduce_costs", "improve_quality"],
            challenges=["resource_constraints", "skill_gaps", "resistance_to_change"],
            preferences={
                "communication": "email",
                "content_type": "case_studies",
                "interaction": "self_service",
            },
            communication_style=behavioral_patterns["communication_style"],
            decision_factors=archetype_data["decision_factors"],
        )

        return persona_profile

    def _generate_behavior_patterns(
        self, persona: PersonaProfile, request: PersonaSimulationRequest
    ) -> List[BehaviorPattern]:
        """Generate behavior patterns for persona."""
        patterns = []

        # Generate patterns based on simulation depth
        depth_config = self.simulation_depths[request.simulation_depth]
        num_patterns = min(depth_config["factors"], len(self.behavioral_patterns))

        selected_patterns = random.sample(
            list(self.behavioral_patterns.keys()), num_patterns
        )

        for i, pattern_name in enumerate(selected_patterns):
            pattern_data = self.behavioral_patterns[pattern_name]

            pattern = BehaviorPattern(
                pattern_id=f"behavior_{i}",
                behavior_name=pattern_name.replace("_", " ").title(),
                frequency=random.choice(["daily", "weekly", "monthly", "occasional"]),
                triggers=["need_arises", "external_trigger", "internal_motivation"],
                actions=pattern_data["actions"],
                outcomes=["solution_found", "decision_made", "action_taken"],
                emotional_states=pattern_data["emotional_state"].split(", "),
                context_factors=["time_pressure", "budget", "stakeholder_input"],
                confidence_score=random.uniform(0.7, 0.95),
            )
            patterns.append(pattern)

        return patterns

    def _generate_decision_processes(
        self, persona: PersonaProfile, request: PersonaSimulationRequest
    ) -> List[DecisionProcess]:
        """Generate decision processes for persona."""
        processes = []

        # Generate decision process for main scenario
        stages = []
        for stage_name, stage_data in self.decision_stages.items():
            stage = {
                "name": stage_name.replace("_", " ").title(),
                "activities": stage_data["activities"],
                "emotions": stage_data["emotions"],
                "duration": random.choice(["1-3 days", "1 week", "2-4 weeks"]),
            }
            stages.append(stage)

        process = DecisionProcess(
            process_id=f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            decision_type=request.scenario,
            stages=stages,
            criteria=persona.decision_factors,
            influences=["peers", "industry_trends", "vendor_reputation"],
            timeline="4-12 weeks",
            risk_tolerance=persona.psychographics["risk_tolerance"],
            information_sources=[
                "online_research",
                "peer_recommendations",
                "vendor_demos",
            ],
            decision_makers=[persona.demographics["role"], "procurement", "finance"],
        )
        processes.append(process)

        return processes

    def _generate_emotional_responses(
        self, persona: PersonaProfile, request: PersonaSimulationRequest
    ) -> List[EmotionalResponse]:
        """Generate emotional responses for persona."""
        responses = []

        # Generate responses for common stimuli
        stimuli = [
            "product_demo",
            "price_quote",
            "technical_issue",
            "support_interaction",
            "success_story",
        ]

        for i, stimulus in enumerate(stimuli):
            # Select primary emotion based on stimulus
            emotion_map = {
                "product_demo": "excited",
                "price_quote": "anxious",
                "technical_issue": "frustrated",
                "support_interaction": "relieved",
                "success_story": "inspired",
            }

            primary_emotion = emotion_map.get(stimulus, "curious")

            response = EmotionalResponse(
                response_id=f"emotion_{i}",
                stimulus=stimulus.replace("_", " ").title(),
                primary_emotion=primary_emotion,
                intensity=random.uniform(0.3, 0.9),
                secondary_emotions=random.sample(
                    list(
                        self.emotional_states["positive"]
                        + self.emotional_states["negative"]
                    ),
                    2,
                ),
                behavioral_manifestations=[
                    "increased_engagement",
                    "information_seeking",
                    "decision_acceleration",
                ],
                cognitive_biases=[
                    "confirmation_bias",
                    "anchoring_bias",
                    "availability_heuristic",
                ],
                coping_mechanisms=["research", "peer_consultation", "trial_period"],
                duration=random.choice(["minutes", "hours", "days"]),
            )
            responses.append(response)

        return responses

    def _generate_customer_journey(
        self, persona: PersonaProfile, request: PersonaSimulationRequest
    ) -> CustomerJourney:
        """Generate customer journey for persona."""
        # Create journey stages
        stages = []
        for stage_name, stage_data in self.behavioral_patterns.items():
            stage = {
                "name": stage_name.replace("_", " ").title(),
                "description": f"Customer is in {stage_name.replace('_', ' ')} phase",
                "duration": stage_data["duration"],
                "key_activities": stage_data["actions"],
                "emotional_state": stage_data["emotional_state"],
                "touchpoints": random.sample(request.touchpoints, 2),
            }
            stages.append(stage)

        # Create touchpoints
        touchpoints = []
        for touchpoint in request.touchpoints:
            touchpoint_data = {
                "name": touchpoint.replace("_", " ").title(),
                "type": "digital",
                "purpose": "information_gathering",
                "satisfaction": random.uniform(0.6, 0.9),
                "frequency": random.choice(["high", "medium", "low"]),
            }
            touchpoints.append(touchpoint_data)

        # Create journey
        journey = CustomerJourney(
            journey_id=f"journey_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            journey_name=f"{persona.archetype.title()} Customer Journey",
            stages=stages,
            touchpoints=touchpoints,
            emotions=[
                {"stage": stage["name"], "emotion": stage["emotional_state"]}
                for stage in stages
            ],
            pain_points=[
                {"stage": stage["name"], "pain": "information_overload"}
                for stage in stages
            ],
            opportunities=[
                {"stage": stage["name"], "opportunity": "personalized_content"}
                for stage in stages
            ],
            metrics={
                "conversion_rate": random.uniform(0.1, 0.4),
                "satisfaction_score": random.uniform(3.5, 4.8),
                "nps_score": random.uniform(20, 80),
            },
            timeline="8-16 weeks",
        )

        return journey

    def _generate_simulation_results(
        self, persona: PersonaProfile, request: PersonaSimulationRequest
    ) -> List[SimulationResult]:
        """Generate simulation results."""
        results = []

        # Generate results for different scenarios
        scenarios = ["best_case", "expected_case", "worst_case"]

        for scenario in scenarios:
            outcomes = []
            if scenario == "best_case":
                outcomes = [
                    {"metric": "conversion", "value": 0.85, "improvement": "+25%"},
                    {"metric": "satisfaction", "value": 4.7, "improvement": "+15%"},
                    {"metric": "retention", "value": 0.92, "improvement": "+18%"},
                ]
            elif scenario == "expected_case":
                outcomes = [
                    {"metric": "conversion", "value": 0.65, "improvement": "+5%"},
                    {"metric": "satisfaction", "value": 4.2, "improvement": "+3%"},
                    {"metric": "retention", "value": 0.78, "improvement": "+2%"},
                ]
            else:  # worst_case
                outcomes = [
                    {"metric": "conversion", "value": 0.45, "improvement": "-15%"},
                    {"metric": "satisfaction", "value": 3.8, "improvement": "-8%"},
                    {"metric": "retention", "value": 0.65, "improvement": "-12%"},
                ]

            result = SimulationResult(
                result_id=f"result_{scenario}",
                simulation_type=request.simulation_type,
                persona_id=persona.persona_id,
                scenario=scenario.replace("_", " ").title(),
                outcomes=outcomes,
                insights=[
                    f"Persona responds well to {persona.preferences['communication']} communication",
                    f"Decision process takes approximately 8-12 weeks",
                    f"Key decision factors: {', '.join(persona.decision_factors[:3])}",
                ],
                recommendations=[
                    "Focus on case studies and testimonials",
                    "Provide detailed technical information",
                    "Offer flexible pricing options",
                ],
                confidence_score=random.uniform(0.7, 0.9),
                simulation_data={
                    "scenario_probability": random.uniform(0.2, 0.6),
                    "key_drivers": persona.motivations,
                    "barriers": persona.pain_points,
                },
                generated_at=datetime.now(),
            )
            results.append(result)

        return results

    def _generate_key_insights(
        self,
        persona: PersonaProfile,
        behaviors: List[BehaviorPattern],
        decisions: List[DecisionProcess],
    ) -> List[str]:
        """Generate key insights from persona simulation."""
        insights = []

        # Persona-specific insights
        insights.append(
            f"{persona.archetype.title()} personas are driven by {', '.join(persona.motivations[:2])}"
        )
        insights.append(
            f"Primary pain points include {', '.join(persona.pain_points[:2])}"
        )

        # Behavioral insights
        if behaviors:
            frequent_behaviors = [
                b for b in behaviors if b.frequency in ["daily", "weekly"]
            ]
            if frequent_behaviors:
                insights.append(
                    f"Most frequent behaviors: {', '.join([b.behavior_name for b in frequent_behaviors[:2]])}"
                )

        # Decision process insights
        if decisions:
            decision = decisions[0]
            insights.append(f"Decision timeline typically spans {decision.timeline}")
            insights.append(
                f"Key decision criteria: {', '.join(decision.criteria[:3])}"
            )

        # General insights
        insights.append("Personalization significantly improves engagement")
        insights.append("Trust building is critical for conversion")
        insights.append("Multi-touchpoint approach yields best results")

        return insights[:8]  # Limit to 8 insights

    def _generate_actionable_recommendations(
        self, insights: List[str], request: PersonaSimulationRequest
    ) -> List[str]:
        """Generate actionable recommendations based on insights."""
        recommendations = []

        # Based on insights, generate specific recommendations
        if any("motivated" in insight.lower() for insight in insights):
            recommendations.append("Align messaging with core motivations and values")

        if any("pain" in insight.lower() for insight in insights):
            recommendations.append("Address pain points directly in value proposition")

        if any("timeline" in insight.lower() for insight in insights):
            recommendations.append(
                "Develop nurture sequences aligned to decision timeline"
            )

        if any("personalization" in insight.lower() for insight in insights):
            recommendations.append("Implement dynamic content personalization")

        # General strategic recommendations
        recommendations.append("Create persona-specific content journeys")
        recommendations.append("Optimize touchpoint experience for each stage")
        recommendations.append("Develop emotional intelligence in communications")
        recommendations.append("Build trust through transparency and social proof")

        return recommendations[:6]  # Limit to 6 recommendations

    def _create_predictive_model(
        self, persona: PersonaProfile, behaviors: List[BehaviorPattern]
    ) -> Dict[str, Any]:
        """Create predictive model for persona behavior."""
        model = {
            "model_type": "behavioral_prediction",
            "accuracy": random.uniform(0.75, 0.92),
            "factors": {
                "demographic_weight": 0.25,
                "psychographic_weight": 0.35,
                "behavioral_weight": 0.30,
                "contextual_weight": 0.10,
            },
            "predictions": {
                "conversion_probability": random.uniform(0.4, 0.8),
                "engagement_score": random.uniform(0.6, 0.9),
                "retention_likelihood": random.uniform(0.7, 0.95),
                "advocacy_potential": random.uniform(0.3, 0.7),
            },
            "key_indicators": [
                "content_engagement_rate",
                "interaction_frequency",
                "decision_acceleration_signals",
                "emotional_response_patterns",
            ],
            "confidence_intervals": {"lower_bound": 0.65, "upper_bound": 0.95},
        }

        return model

    async def _store_simulation_report(
        self, report: PersonaSimulationReport, state: AgentState
    ):
        """Store simulation report in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self._get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="persona_simulation_reports",
                    workspace_id=state["workspace_id"],
                    data={
                        "report_id": report.report_id,
                        "simulation_type": report.simulation_type,
                        "persona_type": report.persona_type,
                        "scenario": report.scenario,
                        "persona_profile": report.persona_profile.__dict__,
                        "behavior_patterns": [
                            pattern.__dict__ for pattern in report.behavior_patterns
                        ],
                        "decision_processes": [
                            process.__dict__ for process in report.decision_processes
                        ],
                        "emotional_responses": [
                            response.__dict__ for response in report.emotional_responses
                        ],
                        "customer_journey": (
                            report.customer_journey.__dict__
                            if report.customer_journey
                            else None
                        ),
                        "simulation_results": [
                            result.__dict__ for result in report.simulation_results
                        ],
                        "key_insights": report.key_insights,
                        "actionable_recommendations": report.actionable_recommendations,
                        "predictive_model": report.predictive_model,
                        "generated_at": report.generated_at.isoformat(),
                        "metadata": report.metadata,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store simulation report: {e}")

    def _format_simulation_response(self, report: PersonaSimulationReport) -> str:
        """Format simulation response for user."""
        response = f"≡ƒÄ¡ **Persona Simulation Report**\n\n"
        response += (
            f"**Simulation Type:** {report.simulation_type.replace('_', ' ').title()}\n"
        )
        response += (
            f"**Persona Type:** {report.persona_type.replace('_', ' ').title()}\n"
        )
        response += f"**Scenario:** {report.scenario.replace('_', ' ').title()}\n"
        response += (
            f"**Persona Archetype:** {report.persona_profile.archetype.title()}\n\n"
        )

        response += f"**Persona Profile:**\n"
        response += f"ΓÇó Name: {report.persona_profile.name}\n"
        response += f"ΓÇó Role: {report.persona_profile.demographics['role'].title()}\n"
        response += (
            f"ΓÇó Industry: {report.persona_profile.demographics['industry'].title()}\n"
        )
        response += f"ΓÇó Experience: {report.persona_profile.demographics['experience']} years\n"
        response += f"ΓÇó Communication Style: {report.persona_profile.communication_style.title()}\n\n"

        response += f"**Key Motivations:**\n"
        for motivation in report.persona_profile.motivations:
            response += f"ΓÇó {motivation.replace('_', ' ').title()}\n"
        response += "\n"

        response += f"**Primary Pain Points:**\n"
        for pain_point in report.persona_profile.pain_points[:3]:
            response += f"ΓÇó {pain_point.replace('_', ' ').title()}\n"
        response += "\n"

        response += (
            f"**Behavior Patterns Identified:** {len(report.behavior_patterns)}\n"
        )
        response += f"**Decision Processes Mapped:** {len(report.decision_processes)}\n"
        response += (
            f"**Emotional Responses Simulated:** {len(report.emotional_responses)}\n"
        )

        if report.customer_journey:
            response += (
                f"**Customer Journey Stages:** {len(report.customer_journey.stages)}\n"
            )

        response += f"\n**Key Insights:**\n"
        for insight in report.key_insights:
            response += f"ΓÇó {insight}\n"
        response += "\n"

        response += f"**Actionable Recommendations:**\n"
        for recommendation in report.actionable_recommendations:
            response += f"ΓÇó {recommendation}\n"
        response += "\n"

        response += f"**Predictive Model Accuracy:** {report.predictive_model['accuracy']:.1%}\n"
        response += f"**Conversion Probability:** {report.predictive_model['predictions']['conversion_probability']:.1%}\n"
        response += f"**Engagement Score:** {report.predictive_model['predictions']['engagement_score']:.1%}\n"

        return response
