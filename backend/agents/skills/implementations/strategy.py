"""
Strategy-related executable skills.
"""

import json
import logging
from typing import Any, Dict, List

from ...base import Skill, SkillCategory, SkillLevel

logger = logging.getLogger(__name__)


class StrategyEvaluationSkill(Skill):
    """Skill for critically evaluating strategic options."""

    def __init__(self):
        super().__init__(
            name="strategy_evaluation",
            category=SkillCategory.STRATEGY,
            level=SkillLevel.ADVANCED,
            description="Critically evaluate strategic options for feasibility, impact, and risk",
            tools_required=[],  # Uses Agent's LLM
            capabilities=[
                "Feasibility analysis",
                "Impact assessment",
                "Risk evaluation",
                "Strategic reasoning",
            ],
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute strategy evaluation.

        Context requires:
        - option: Dict - The strategic option to evaluate
        - challenge_context: Dict - The context of the strategic challenge
        - agent: BaseAgent - The calling agent
        """
        agent = context.get("agent")
        option = context.get("option")
        challenge_context = context.get("challenge_context", {})

        if not agent or not option:
            raise ValueError("Agent and option are required for strategy evaluation")

        logger.info(
            f"Executing StrategyEvaluationSkill for option: {option.get('name', 'Unknown')}"
        )

        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(option, challenge_context)
        system_prompt = "You are a Chief Strategy Officer. Evaluate the proposed strategy critically and objectively. Provide numerical scores (0.0-1.0) and reasoning."

        # Call LLM
        try:
            # We request structured output to get clean scores
            response_text = await agent._call_llm(prompt, system_prompt=system_prompt)

            # Parse the response (assuming JSON-like structure requested in prompt)
            return self._parse_evaluation(response_text)

        except Exception as e:
            logger.error(f"Strategy evaluation failed: {e}")
            # Fallback to a neutral score with error note
            return {
                "feasibility": 0.5,
                "impact": 0.5,
                "risk": 0.5,
                "confidence": 0.1,
                "reasoning": f"Evaluation failed due to error: {str(e)}",
            }

    def _build_evaluation_prompt(
        self, option: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        return f"""
EVALUATE THE FOLLOWING STRATEGIC OPTION:

NAME: {option.get('name')}
APPROACH: {option.get('approach')}
DESCRIPTION: {option.get('description')}

CONTEXT OF CHALLENGE:
{json.dumps(context, indent=2)}

CRITERIA:
1. Feasibility: Can this realistically be done given the constraints? (0.0 = Impossible, 1.0 = Easy)
2. Impact: How much will this move the needle on objectives? (0.0 = Negligible, 1.0 = Transformative)
3. Risk: What is the probability of failure or negative side effects? (0.0 = Safe, 1.0 = Dangerous)

OUTPUT FORMAT:
Return a valid JSON object ONLY:
{{
    "feasibility": <float 0.0-1.0>,
    "impact": <float 0.0-1.0>,
    "risk": <float 0.0-1.0>,
    "reasoning": "<short explanation of the scores>"
}}
"""

    def _parse_evaluation(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM JSON response."""
        try:
            # Strip potential markdown fences
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON evaluation: {response_text[:100]}...")
            # Simple heuristic callback or error
            return {
                "feasibility": 0.5,
                "impact": 0.5,
                "risk": 0.5,
                "reasoning": "Could not parse AI evaluation. Defaulting to neutral.",
            }


class PersonaBuilderSkill(Skill):
    def __init__(self):
        super().__init__(
            name="persona_builder",
            category=SkillCategory.STRATEGY,
            level=SkillLevel.INTERMEDIATE,
            description="Create complete buyer personas including demographics, psychographics, and pain points.",
            capabilities=["Persona creation", "Customer profiling", "Empathy mapping"],
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        base_profile = context.get("base_profile", {})
        personality_trait = context.get("personality_trait", "analytical")
        target_audience = context.get("target_audience", "professional")

        # Build comprehensive persona prompt
        system_prompt = """You are a Chief Marketing Officer and expert in buyer persona development.
Create a detailed, structured buyer persona that includes specific demographic, psychographic, and behavioral data.

Return your response as a valid JSON object with the following structure:
{
    "persona": {
        "name": "Specific persona name",
        "role_description": "Brief tagline describing their role",
        "demographics": {
            "age_range": [min_age, max_age],
            "title": "Job title",
            "income_level": "income_range_description",
            "education": "education_level",
            "location": "geographic_location"
        },
        "motivations": ["motivation1", "motivation2", "motivation3"],
        "frustrations": ["frustration1", "frustration2", "frustration3"],
        "goals": ["goal1", "goal2", "goal3"],
        "personality_traits": ["trait1", "trait2", "trait3"],
        "decision_factors": ["factor1", "factor2", "factor3"],
        "preferred_channels": ["channel1", "channel2", "channel3"]
    }
}"""

        # Build detailed prompt with business context and personality
        prompt = f"""Create a detailed buyer persona with the following specifications:

BUSINESS CONTEXT:
- Industry: {base_profile.get('industry', 'Technology')}
- Company Size: {base_profile.get('company_size', 'Medium')}
- Target Market: {base_profile.get('target_market', 'B2B')}
- ICP Type: {base_profile.get('icp_type', 'b2b_smb')}

PERSONALITY TYPE: {personality_trait}
TARGET AUDIENCE: {target_audience}

Please create a realistic, detailed persona that reflects this personality type and business context.
Ensure the JSON is properly formatted and contains all required fields."""

        try:
            result = await agent._call_llm(prompt, system_prompt=system_prompt)

            # Parse the JSON response
            import json

            try:
                # Clean up the response and parse JSON
                clean_result = result.replace("```json", "").replace("```", "").strip()
                persona_data = json.loads(clean_result)

                # Validate required structure
                if "persona" not in persona_data:
                    raise ValueError("Missing 'persona' key in response")

                persona = persona_data["persona"]

                # Ensure required fields exist
                required_fields = [
                    "name",
                    "role_description",
                    "demographics",
                    "motivations",
                    "frustrations",
                    "goals",
                ]
                for field in required_fields:
                    if field not in persona:
                        persona[field] = self._get_default_field(
                            field, personality_trait, base_profile
                        )

                logger.info(
                    f"Successfully generated persona: {persona.get('name', 'Unknown')}"
                )
                return persona_data

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse persona JSON: {e}")
                # Fallback to structured generation
                return self._generate_fallback_persona(
                    base_profile, personality_trait, target_audience
                )

        except Exception as e:
            logger.error(f"Persona generation failed: {e}")
            # Return fallback persona
            return self._generate_fallback_persona(
                base_profile, personality_trait, target_audience
            )

    def _get_default_field(
        self, field: str, personality: str, context: Dict[str, Any]
    ) -> Any:
        """Get default values for missing fields."""
        defaults = {
            "name": f"{context.get('industry', 'Professional')} {personality.title()} Persona",
            "role_description": f"{personality.title()} professional in {context.get('industry', 'technology')}",
            "demographics": {
                "age_range": [30, 50],
                "title": "Professional",
                "income_level": "Mid-range",
                "education": "Bachelor's Degree",
                "location": "United States",
            },
            "motivations": ["career growth", "efficiency", "success"],
            "frustrations": ["inefficiency", "lack of control", "slow progress"],
            "goals": [
                "professional success",
                "efficiency improvements",
                "skill development",
            ],
        }
        return defaults.get(field, None)

    def _generate_fallback_persona(
        self, base_profile: Dict[str, Any], personality: str, target_audience: str
    ) -> Dict[str, Any]:
        """Generate a basic persona when LLM fails."""
        industry = base_profile.get("industry", "Technology")

        fallback_persona = {
            "persona": {
                "name": f"{industry} {personality.title()} Professional",
                "role_description": f"{personality.title()} decision-maker in the {industry} sector",
                "demographics": {
                    "age_range": [35, 55],
                    "title": (
                        "Senior Manager"
                        if "b2b" in str(base_profile.get("icp_type", "")).lower()
                        else "Professional"
                    ),
                    "income_level": "$80,000 - $150,000",
                    "education": "Bachelor's Degree or higher",
                    "location": "United States",
                },
                "motivations": ["efficiency", "growth", "innovation"],
                "frustrations": ["bottlenecks", "outdated systems", "lack of insights"],
                "goals": ["business growth", "process optimization", "team success"],
                "personality_traits": [personality, "professional", "goal-oriented"],
                "decision_factors": ["ROI", "efficiency", "reliability"],
                "preferred_channels": [
                    "email",
                    "professional networks",
                    "industry publications",
                ],
            }
        }

        return fallback_persona


class GapAnalysisSkill(Skill):
    def __init__(self):
        super().__init__(
            name="gap_analysis",
            category=SkillCategory.STRATEGY,
            level=SkillLevel.ADVANCED,
            description="Compare current state vs desired state to identify strategic gaps.",
            capabilities=["Gap analysis", "Strategic planning", "Needs assessment"],
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        current_state = context.get("current_state")
        desired_state = context.get("desired_state")

        system_prompt = "You are a Business Consultant. Perform a Gap Analysis. Identify the specific deficiencies (Process, Technology, Skills) preventing the move from Current State to Desired State. Propose an Action Plan."
        prompt = f"Current State: {current_state}\nDesired State: {desired_state}"
        result = await agent._call_llm(prompt, system_prompt=system_prompt)
        return {"gap_analysis": result}


class PricingArchitectSkill(Skill):
    def __init__(self):
        super().__init__(
            name="pricing_architect",
            category=SkillCategory.STRATEGY,
            level=SkillLevel.ADVANCED,
            description="Design pricing strategies, tiers, and psychological pricing models.",
            capabilities=[
                "Pricing strategy",
                "Monetization modeling",
                "Value proposition analysis",
            ],
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        product_details = context.get("product_details")
        market_position = context.get("market_position", "mid-market")

        system_prompt = "You are a Pricing Strategist. Design a 3-tier pricing model (Good/Better/Best) for the product. Include price points, feature differentiation, and psychological anchoring rationale."
        prompt = f"Product: {product_details}\nPositioning: {market_position}"
        result = await agent._call_llm(prompt, system_prompt=system_prompt)
        return {"pricing_strategy": result}


class FunnelBlueprintSkill(Skill):
    def __init__(self):
        super().__init__(
            name="funnel_blueprint",
            category=SkillCategory.STRATEGY,
            level=SkillLevel.ADVANCED,
            description="Design comprehensive marketing funnel stages (TOFU/MOFU/BOFU).",
            capabilities=[
                "Funnel design",
                "Customer journey mapping",
                "Conversion optimization",
            ],
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        goal = context.get("conversion_goal")

        system_prompt = "You are a Growth Hacker. Design a full conversion funnel (Awareness -> Interest -> Desire -> Action). Specify content types and key messages for each stage."
        result = await agent._call_llm(
            f"Funnel Goal: {goal}", system_prompt=system_prompt
        )
        return {"funnel_blueprint": result}


class BrandVoiceGuardSkill(Skill):
    def __init__(self):
        super().__init__(
            name="brand_voice_guard",
            category=SkillCategory.STRATEGY,
            level=SkillLevel.INTERMEDIATE,
            description="Critique and rewrite content to ensure adherence to brand guidelines.",
            capabilities=["Brand consistency check", "Voice analysis", "Copy editing"],
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        content = context.get("content")
        brand_guidelines = context.get("brand_guidelines")

        system_prompt = "You are a Brand Manager. Review the content against the guidelines. 1. Identify violations. 2. Rewrite the content to perfectly match the brand voice."
        prompt = f"Guidelines: {brand_guidelines}\n\nContent: {content}"
        result = await agent._call_llm(prompt, system_prompt=system_prompt)
        return {"brand_voice_review": result}
