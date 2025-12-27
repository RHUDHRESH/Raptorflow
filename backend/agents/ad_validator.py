import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent

logger = logging.getLogger("raptorflow.agents.ad_validator")


class AdCopyValidatorAgent(BaseCognitiveAgent):
    """
    The Ad Copy Validator.
    Checks copy against common Facebook and Google ad policies.
    """

    def __init__(self):
        policy_prompt = """
        # ROLE: Ad Policy Compliance Officer (Facebook & Google Ads)
        # TASK: Audit ad copy for policy violations.

        # POLICIES:
        1. NO Personal Attributes: Do not imply knowledge of user's personal attributes (e.g. 'Are you a founder?').
           Use 'For founders' instead.
        2. NO Sensationalism: No excessive punctuation (!!!), no all-caps words, no misleading claims.
        3. NO Forbidden Content: No weight loss, financial 'get rich quick', or discriminatory language.
        4. CLEAR CTA: Must have a clear, non-deceptive Call to Action.
        5. LANDING PAGE ALIGNMENT: Copy must match the expected landing page experience.

        # OUTPUT: Return a JSON object with:
        - status: 'passed' | 'flagged' | 'failed'
        - violations: list of specific policy breaches
        - refined_copy: a corrected version of the copy
        - confidence: 0-1 score
        """

        super().__init__(
            name="AdCopyValidatorAgent",
            role="ad_validator",
            system_prompt=policy_prompt,
            model_tier="Mundane",  # Mundane is enough for policy checks
            auto_assign_tools=False,
        )

    async def validate_copy(self, copy: str) -> Dict[str, Any]:
        """
        Audits ad copy and returns validation results.
        """
        logger.info("AdCopyValidatorAgent auditing copy...")

        prompt = f"Audit the following ad copy for compliance:\n\n{copy}"

        # Use simple call pattern
        response = await self.llm.ainvoke(prompt)
        content = response.content

        import json

        try:
            start_idx = content.find("{")
            end_idx = content.rfind("}")
            if start_idx != -1 and end_idx != -1:
                return json.loads(content[start_idx : end_idx + 1])
        except Exception as e:
            logger.error(f"Failed to parse Ad Validator output: {e}")

        return {
            "status": "error",
            "violations": ["Parsing failed"],
            "refined_copy": copy,
        }
