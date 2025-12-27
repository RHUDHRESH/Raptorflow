import logging
from typing import Any, Dict, List, Optional

from langchain_core.prompts import ChatPromptTemplate

from core.tool_registry import BaseRaptorTool, RaptorRateLimiter
from inference import InferenceProvider

logger = logging.getLogger("raptorflow.tools.product_marketing")


class BenefitToFeatureMapperTool(BaseRaptorTool):
    """
    SOTA Benefit-to-Feature Mapper Tool.
    Maps visceral customer benefits to specific product features using the 'So What?' test.
    """

    def __init__(self, model_tier: str = "driver"):
        self.model_tier = model_tier

    @property
    def name(self) -> str:
        return "benefit_to_feature_mapper"

    @property
    def description(self) -> str:
        return (
            "Maps customer benefits to product features. "
            "Use this to translate 'what the product does' into 'why the customer cares'. "
            "Pass a list of 'features' and it will architect the corresponding 'benefits'."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(
        self, features: List[str], target_persona: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        logger.info(f"Mapping benefits for features: {features}")

        llm = InferenceProvider.get_model(model_tier=self.model_tier)

        system_prompt = (
            "# ROLE: Master Product Marketer\n"
            "# TASK: Perform a surgical 'Benefit-to-Feature' mapping.\n"
            "# METHOD: The 'So What?' Test. Ask 'So what?' until you reach a visceral benefit.\n"
            "# CONSTRAINTS:\n"
            "- Never use jargon.\n"
            "- Focus on outcomes (time saved, money made, status gained).\n"
            "- Tailor to the target persona if provided.\n"
            "Output MUST be a JSON object with a list of 'mappings', each containing 'feature' and 'benefit'."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "user",
                    "Features: {features}\nTarget Persona: {target_persona}\nContext: {context}",
                ),
            ]
        )

        chain = prompt | llm
        try:
            features_str = ", ".join(features)
            response = await chain.ainvoke(
                {
                    "features": features_str,
                    "target_persona": target_persona or "General Audience",
                    "context": kwargs.get("context", "No additional context."),
                }
            )

            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()

            import json

            data = json.loads(content)

            return {
                "success": True,
                "mappings": data.get("mappings", []),
                "target_persona": target_persona,
            }
        except Exception as e:
            logger.error(f"Failed to map benefits: {e}")
            # Fallback mock logic
            mappings = [
                {"feature": f, "benefit": f"Visceral benefit for {f}"} for f in features
            ]
            return {
                "success": True,
                "mappings": mappings,
                "is_mock": True,
                "error": str(e),
            }
