import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent

logger = logging.getLogger("raptorflow.agents.image_gen_director")


class ImageGenDirectorAgent(BaseCognitiveAgent):
    """
    The Image Generation Director.
    Architects high-fidelity visual prompts for Muse and other engines.
    """

    def __init__(self):
        director_prompt = """
        # ROLE: World-Class Visual Creative Director
        # TASK: Convert abstract marketing concepts into surgical image generation prompts.

        # HEURISTICS:
        1. LIGHTING: Specify cinematic, volumetric, or studio lighting.
        2. COMPOSITION: Use 'Rule of Thirds', 'Golden Ratio', or 'Central Symmetry'.
        3. STYLE: Focus on 'Quiet Luxury' - muted tones, high-quality textures, minimalist background.
        4. CAMERA: Specify lens (e.g., 35mm, 85mm), aperture (f/1.8), and focus.

        # OUTPUT: Return a JSON object with:
        - primary_prompt: The detailed string for the engine.
        - negative_prompt: What to avoid.
        - aspect_ratio: '1:1', '16:9', or '9:16'.
        - reasoning: Why this visual style fits the brand.
        """

        super().__init__(
            name="ImageGenDirectorAgent",
            role="image_director",
            system_prompt=director_prompt,
            model_tier="driver",
            auto_assign_tools=False,
        )

    async def architect_visual(self, concept: str) -> Dict[str, Any]:
        """
        Generates a surgical image prompt from a concept.
        """
        logger.info(f"ImageGenDirectorAgent architecting visual for: {concept}")

        prompt = (
            f"Architect a surgical image prompt for the following concept: {concept}"
        )

        response = await self.llm.ainvoke(prompt)
        content = response.content

        import json

        try:
            start_idx = content.find("{")
            end_idx = content.rfind("}")
            if start_idx != -1 and end_idx != -1:
                return json.loads(content[start_idx : end_idx + 1])
        except Exception as e:
            logger.error(f"Failed to parse Image Director output: {e}")

        return {
            "primary_prompt": concept,
            "negative_prompt": "",
            "aspect_ratio": "16:9",
        }
