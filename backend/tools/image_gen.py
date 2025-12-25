import logging
from typing import Any, Dict

from backend.core.tool_registry import RaptorRateLimiter
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


class NanoBananaImageTool:
    """
    SOTA Gemini Nano Banana Image Generation Tool.
    Optimized for RaptorFlow's multimodal marketing workflow.
    """

    def __init__(self, model_tier: str = "nano"):
        from backend.core.usage_tracker import usage_tracker
        from backend.inference import InferenceProvider

        self.model = InferenceProvider.get_image_model(model_tier=model_tier)
        self.usage_tracker = usage_tracker

    @property
    def name(self) -> str:
        return "nano_banana_gen"

    async def run(
        self, tenant_id: str, prompt: str, aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """Executes Nano Banana generation and GCS upload."""
        from google.genai import types

        from backend.utils.storage import pil_to_bytes, upload_image_to_gcs

        # Check Quota
        if not await self.usage_tracker.check_quota(tenant_id, "image"):
            return {"success": False, "error": "Quota exceeded"}

        logger.info(f"Nano Banana: Generating image (Ratio: {aspect_ratio})...")

        config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
        )

        response = await self.model.ainvoke(prompt, config=config)

        if not response.images:
            return {"success": False, "error": "No images generated"}

        # Process first image
        img = response.images[0]
        img_bytes = pil_to_bytes(img)
        url = await upload_image_to_gcs(img_bytes)

        # Track Usage
        await self.usage_tracker.track_usage(tenant_id, amount=1, service_type="image")

        return {
            "success": True,
            "image_url": url,
            "model": self.model.model_name,
            "aspect_ratio": aspect_ratio,
        }
