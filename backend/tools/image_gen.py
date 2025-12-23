import logging
from typing import Any, Dict

from backend.core.base_tool import RaptorRateLimiter
from backend.core.config import get_settings

logger = logging.getLogger("raptorflow.tools.image_gen")


class ImageGenerator:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.OPENAI_API_KEY

    @property
    def name(self) -> str:
        return "image_gen_dalle"

    @property
    def description(self) -> str:
        return (
            "Generates a high-quality marketing image using DALL-E 3. "
            "Input is a highly detailed visual prompt. Returns the image URL."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(
        self, prompt: str, size: str = "1024x1024", quality: str = "standard"
    ) -> Dict[str, Any]:
        """Executes DALL-E 3 generation."""
        from openai import AsyncOpenAI

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY missing from environment.")

        logger.info(f"Generating DALL-E 3 image for prompt: {prompt[:50]}...")
        client = AsyncOpenAI(api_key=self.api_key)

        response = await client.images.generate(
            model="dall-e-3", prompt=prompt, size=size, quality=quality, n=1
        )

        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt

        return {
            "image_url": image_url,
            "revised_prompt": revised_prompt,
            "model": "dall-e-3",
        }
