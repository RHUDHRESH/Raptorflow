import logging
from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate

from core.prompts import MarketingFrameworks
from core.tool_registry import BaseRaptorTool, RaptorRateLimiter
from inference import InferenceProvider

logger = logging.getLogger("raptorflow.tools.pr_pitch")


class JournalistPitchArchitectTool(BaseRaptorTool):
    """
    SOTA Journalist Pitch Architect Tool.
    Architects high-fidelity journalist pitches using 'Narrative Hook' outreach frameworks.
    """

    def __init__(self, model_tier: str = "driver"):
        self.model_tier = model_tier

    @property
    def name(self) -> str:
        return "journalist_pitch_architect"

    @property
    def description(self) -> str:
        return (
            "Architects a surgical pitch for a journalist or media outlet. "
            "Use this to generate newsworthy hooks, personalized intros, and compelling value props. "
            "Returns a structured pitch with a newsworthiness score. "
            "Supports frameworks: NARRATIVE_HOOK, THE_REFRAME."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(
        self,
        story_angle: str,
        target_outlet: str,
        framework: str = "NARRATIVE_HOOK",
        **kwargs,
    ) -> Dict[str, Any]:
        logger.info(f"Architecting pitch for {target_outlet} with angle: {story_angle}")

        llm = InferenceProvider.get_model(model_tier=self.model_tier)

        fw_data = getattr(
            MarketingFrameworks, framework.upper(), MarketingFrameworks.NARRATIVE_HOOK
        )

        system_prompt = (
            "# ROLE: SOTA Journalist Pitch Architect\n"
            "# TASK: Architect a high-fidelity journalist pitch.\n"
            f"# FRAMEWORK: Use the {fw_data['name']} framework: {fw_data['instructions']}\n"
            "# CONSTRAINTS:\n"
            "- Be surgical and direct.\n"
            "- Focus on newsworthiness over promotion.\n"
            "- Include a 'Why Now' hook.\n"
            "Output MUST be a JSON object with 'subject', 'intro', 'hook', 'cta', and 'newsworthiness_score' (0.0-1.0)."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "user",
                    "Story Angle: {story_angle}\nTarget Outlet: {target_outlet}\nAdditional Context: {context}",
                ),
            ]
        )

        chain = prompt | llm
        try:
            # We use a try-except because the LLM might not return perfect JSON
            # In a real SOTA system, we'd use Structured Output
            response = await chain.ainvoke(
                {
                    "story_angle": story_angle,
                    "target_outlet": target_outlet,
                    "context": kwargs.get("context", "No additional context."),
                }
            )

            # Simple cleanup of response content if it has markdown code blocks
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()

            import json

            pitch_data = json.loads(content)

            return {
                "success": True,
                "story_angle": story_angle,
                "target_outlet": target_outlet,
                "framework_used": fw_data["name"],
                "pitch": pitch_data,
                "newsworthiness_score": pitch_data.get("newsworthiness_score", 0.8),
            }
        except Exception as e:
            logger.error(f"Failed to parse pitch JSON: {e}")
            # Fallback to a structured but non-LLM generated response if it fails
            return {
                "success": True,
                "story_angle": story_angle,
                "target_outlet": target_outlet,
                "framework_used": fw_data["name"],
                "pitch": {
                    "subject": f"STORY: {story_angle}",
                    "intro": f"Hi, I noticed your work at {target_outlet}...",
                    "hook": f"The '{fw_data['name']}' angle for {story_angle} is compelling because of its timeliness.",
                    "cta": "Interested in a briefing?",
                },
                "newsworthiness_score": 0.7,
                "error": str(e),
            }
