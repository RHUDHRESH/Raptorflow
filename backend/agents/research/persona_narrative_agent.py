"""
Persona Narrative Agent - Generates human-readable persona stories.

Creates engaging 1-2 paragraph narratives that bring ICP data to life.
Includes persona name, day-in-the-life scenarios, pain points, and goals.

Uses Vertex AI Gemini with higher temperature for creative narratives.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from pydantic import ValidationError

from backend.agents.base_agent import BaseAgent
from backend.models.persona import PersonaNarrative
from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id


logger = logging.getLogger(__name__)


# System prompt for narrative generation
PERSONA_NARRATIVE_SYSTEM_PROMPT = """You are an expert storyteller and copywriter specializing in persona narratives.

Your role:
- Transform dry ICP data into compelling human stories
- Create memorable, empathetic personas that marketing teams can relate to
- Use vivid details to bring personas to life
- Make personas feel like real people with real challenges and aspirations

Write in an engaging, professional tone that builds empathy and understanding.
Focus on showing, not just telling - use scenarios and examples."""


class PersonaNarrativeAgent(BaseAgent):
    """
    Generates persona narratives from ICP data.

    Creates:
    - Memorable persona name (e.g., "Scaling Sarah", "Technical Tom")
    - Engaging narrative (1-2 paragraphs)
    - Day-in-the-life details
    - Pain points in narrative form
    - Goals and aspirations

    Returns PersonaNarrative schema with all fields.
    """

    def __init__(self):
        super().__init__(name="PersonaNarrativeAgent")

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate persona narrative from ICP data.

        Args:
            payload: Dict containing:
                - icp_name: str (ICP profile name)
                - demographics: Dict (optional)
                - psychographics: Dict (optional)
                - pain_points: List[str] (optional)
                - goals: List[str] (optional)

        Returns:
            Dict with:
                - agent: str (agent name)
                - output: Dict (PersonaNarrative data)
        """
        correlation_id = get_correlation_id()
        self.log("Generating persona narrative")

        # Extract inputs
        icp_name = payload.get("icp_name", "Customer Persona")
        demographics = payload.get("demographics", {})
        psychographics = payload.get("psychographics", {})
        pain_points = payload.get("pain_points", [])
        goals = payload.get("goals", [])

        # Build prompt
        prompt = self._build_prompt(
            icp_name=icp_name,
            demographics=demographics,
            psychographics=psychographics,
            pain_points=pain_points,
            goals=goals,
        )

        try:
            # Call Vertex AI with higher temperature for creativity
            self.log("Calling Vertex AI Gemini for narrative generation")
            response_json = await vertex_ai_client.generate_json(
                prompt=prompt,
                system_prompt=PERSONA_NARRATIVE_SYSTEM_PROMPT,
                model="creative_fast",  # Use creative model for storytelling
                temperature=0.8,  # Higher temperature for more creative output
                max_tokens=2048,
            )

            self.log("Received persona narrative response")

            # Validate and transform
            narrative_data = self._validate_and_transform(response_json)

            self.log("Persona narrative generated successfully")

            return {
                "agent": self.name,
                "output": narrative_data,
            }

        except Exception as e:
            error_msg = f"Persona narrative generation failed: {str(e)}"
            self.log(error_msg, level="error", exc_info=True)
            raise

    def _build_prompt(
        self,
        icp_name: str,
        demographics: Dict[str, Any],
        psychographics: Dict[str, Any],
        pain_points: List[str],
        goals: List[str],
    ) -> str:
        """
        Build XML-structured prompt for narrative generation.

        Args:
            icp_name: Name of ICP
            demographics: Demographic attributes
            psychographics: Psychographic attributes
            pain_points: List of pain points
            goals: List of goals

        Returns:
            XML-formatted prompt
        """
        # Format demographics
        demo_text = "\n".join([
            f"- {key}: {value}"
            for key, value in demographics.items()
            if value
        ]) if demographics else "Not specified"

        # Format psychographics
        psycho_items = []
        if psychographics:
            for key, value in psychographics.items():
                if value and not isinstance(value, (list, dict)):
                    psycho_items.append(f"- {key}: {value}")

            # Add lists
            for key in ["motivations", "values"]:
                if key in psychographics and psychographics[key]:
                    values = psychographics[key]
                    if isinstance(values, list):
                        psycho_items.append(f"- {key}: {', '.join(values)}")

        psycho_text = "\n".join(psycho_items) if psycho_items else "Not specified"

        # Format pain points
        pain_text = "\n".join([f"- {pp}" for pp in pain_points]) if pain_points else "Not specified"

        # Format goals
        goals_text = "\n".join([f"- {g}" for g in goals]) if goals else "Not specified"

        prompt = f"""
<context>
You are creating a persona narrative for: {icp_name}

ICP Data:

Demographics:
{demo_text}

Psychographics:
{psycho_text}

Pain Points:
{pain_text}

Goals:
{goals_text}
</context>

<task>
Create a compelling persona narrative that brings this ICP to life as a real person.

The narrative should:
1. Start with an attention-grabbing hook (1 sentence)
2. Introduce the persona with a memorable, alliterative name (e.g., "Scaling Sarah", "Technical Tom")
3. Paint a day-in-the-life picture (1-2 paragraphs)
4. Weave in their pain points and frustrations naturally
5. Show their goals and aspirations
6. Make them feel like someone you'd meet in real life
7. Build empathy and understanding

Tone: Professional but engaging, empathetic, human
Length: 2-3 concise paragraphs (150-250 words total)
Style: Narrative storytelling, not bullet points
</task>

<output_format>
Return a JSON object with this structure:

{{
  "persona_name": "Alliterative memorable name (e.g., 'Scaling Sarah', 'Marketing Mike')",
  "hook": "One-sentence attention-grabber about this persona",
  "narrative": "2-3 paragraph narrative bringing the persona to life. Use vivid details, scenarios, and emotions. Make it feel like a real person's story. Include their daily challenges, what keeps them up at night, and what they're striving to achieve.",
  "day_in_life": [
    "Morning: Brief day-in-life detail",
    "Midday: Brief day-in-life detail",
    "Afternoon: Brief day-in-life detail",
    "Evening: Brief day-in-life detail"
  ],
  "goals": [
    "Specific goal 1",
    "Specific goal 2",
    "Specific goal 3"
  ],
  "pain_points": [
    "Specific pain point 1",
    "Specific pain point 2",
    "Specific pain point 3"
  ],
  "preferred_channels": [
    "Channel 1",
    "Channel 2",
    "Channel 3"
  ]
}}

IMPORTANT:
- The persona_name should be alliterative and memorable
- The narrative should read like a story, not a data dump
- Use specific, concrete details
- Make it emotionally engaging
- Keep it concise (2-3 paragraphs max)
- Return ONLY valid JSON
</output_format>
"""
        return prompt

    def _validate_and_transform(
        self,
        response_json: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate and transform response into PersonaNarrative schema.

        Args:
            response_json: Raw JSON from LLM

        Returns:
            Validated PersonaNarrative dict

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Validate against PersonaNarrative schema
            persona_narrative = PersonaNarrative(
                persona_name=response_json.get("persona_name", "Customer Persona"),
                hook=response_json.get("hook", ""),
                narrative=response_json.get("narrative", ""),
                day_in_life=response_json.get("day_in_life", []),
                goals=response_json.get("goals", []),
                pain_points=response_json.get("pain_points", []),
                preferred_channels=response_json.get("preferred_channels", []),
            )

            return persona_narrative.model_dump()

        except ValidationError as e:
            self.log(f"Narrative validation failed: {e}", level="error")
            # Return fallback narrative
            return self._fallback_narrative(response_json)

    def _fallback_narrative(
        self,
        raw_response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create fallback narrative if validation fails.

        Args:
            raw_response: Original LLM response

        Returns:
            Minimal valid PersonaNarrative dict
        """
        self.log("Using fallback narrative due to validation failure", level="warning")

        # Extract whatever we can from the response
        persona_name = raw_response.get("persona_name", "Customer Persona")
        narrative = raw_response.get("narrative", "")

        # Provide minimal fallback if narrative is missing
        if not narrative:
            narrative = f"""
{persona_name} represents a typical customer in this segment. They face various
challenges in their role and are looking for solutions that can help them achieve
their goals more effectively.

They prefer direct, value-driven communication and appreciate tools that save time
and reduce complexity. Understanding their needs is key to crafting effective
marketing messages.
"""

        fallback = PersonaNarrative(
            persona_name=persona_name,
            hook=raw_response.get("hook", f"Meet {persona_name}"),
            narrative=narrative.strip(),
            day_in_life=raw_response.get("day_in_life", [
                "Morning: Checks priorities and plans the day",
                "Midday: Focuses on core responsibilities",
                "Afternoon: Collaborates with team",
                "Evening: Reviews progress and plans ahead",
            ]),
            goals=raw_response.get("goals", ["Achieve better results", "Save time", "Reduce costs"]),
            pain_points=raw_response.get("pain_points", ["Limited resources", "Time constraints", "Process inefficiencies"]),
            preferred_channels=raw_response.get("preferred_channels", ["Email", "LinkedIn", "Industry blogs"]),
        )

        return fallback.model_dump()


# Global instance
persona_narrative_agent = PersonaNarrativeAgent()
