import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent

logger = logging.getLogger("raptorflow.agents.librarian")


class LibrarianAgent(BaseCognitiveAgent):
    """
    The Council Librarian.
    Specializes in extracting heuristics and exploits from ingested knowledge.
    """

    def __init__(self):
        from core.prompts import AssetSpecializations

        super().__init__(
            name="LibrarianAgent",
            role="librarian",
            system_prompt=AssetSpecializations.LIBRARIAN,
            model_tier="driver",
            auto_assign_tools=True,
        )

    async def extract_heuristics(self, text: str) -> Dict[str, Any]:
        """
        Parses raw text and extracts structured heuristics and exploits.
        """
        logger.info("LibrarianAgent extracting heuristics from text...")

        prompt = (
            "Analyze the following text and extract core strategic heuristics.\n\n"
            f"Text: {text[:4000]}\n\n"
            "Output ONLY a JSON object with:\n"
            "- never_rules (list of strings): Constraints to avoid.\n"
            "- always_rules (list of strings): Core principles to follow.\n"
            "- exploits (list of objects): Past wins with 'title', 'description', and 'predicted_roi'.\n"
            "- target_agents (list of strings): Which experts this knowledge most impacts.\n"
        )

        # Use the base call logic but with a specific extraction prompt
        response = await self.llm.ainvoke(
            [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
        )

        content = response.content
        import json

        try:
            start_idx = content.find("{")
            end_idx = content.rfind("}")
            if start_idx != -1 and end_idx != -1:
                return json.loads(content[start_idx : end_idx + 1])
        except Exception as e:
            logger.error(f"Failed to parse Librarian extraction: {e}")

        return {
            "never_rules": [],
            "always_rules": [],
            "exploits": [],
            "target_agents": [],
        }
