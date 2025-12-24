import logging
from typing import Any, Dict, Optional

from langchain_core.prompts import ChatPromptTemplate

from backend.core.base_tool import BaseRaptorTool, RaptorRateLimiter
from backend.core.prompts import MarketingFrameworks, MusePrompts
from backend.inference import InferenceProvider

logger = logging.getLogger("raptorflow.tools.muse")


class AssetGenTool(BaseRaptorTool):
    """
    SOTA Asset Generation Tool (Muse Integration).
    Generates high-quality marketing copy and creative briefs.
    """

    def __init__(self, model_tier: str = "driver"):
        self.model_tier = model_tier

    @property
    def name(self) -> str:
        return "asset_gen"

    @property
    def description(self) -> str:
        return (
            "A SOTA asset generation tool. Use this to create marketing copy, "
            "email sequences, social posts, and image generation prompts. "
            "Input should include the 'topic', 'format', and optional 'framework' (PAS, AIDA, BAB)."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(
        self,
        topic: str,
        format: str,
        framework: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes asset generation using the Muse Spine logic.
        """
        logger.info(f"Generating {format} asset for topic: {topic}")
        llm = InferenceProvider.get_model(model_tier=self.model_tier)

        framework_instr = ""
        if framework:
            fw_data = getattr(MarketingFrameworks, framework.upper(), {})
            if fw_data:
                framework_instr = (
                    f"\nUse the {fw_data['name']} framework: {fw_data['instructions']}"
                )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", MusePrompts.ASSET_GEN_SYSTEM + framework_instr),
                (
                    "user",
                    "Topic: {topic}\nFormat: {format}\nAdditional Context: {context}",
                ),
            ]
        )

        chain = prompt | llm
        response = await chain.ainvoke(
            {
                "topic": topic,
                "format": format,
                "context": context or "No additional context.",
            }
        )

        return {
            "content": response.content,
            "format": format,
            "framework_used": framework,
        }
