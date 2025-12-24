import logging
import os

from langchain_google_vertexai import ChatVertexAI

from backend.core.config import get_settings


def get_vertex_api_key():
    settings = get_settings()
    return settings.VERTEX_AI_API_KEY


logger = logging.getLogger("raptorflow.inference")


class InferenceProvider:
    """
    SOTA Tiered Gemini Factory.
    Routes tasks to the optimal Gemini model based on reasoning complexity.
    """

    @staticmethod
    def get_model(
        model_tier: str = "driver", temperature: float = 0.0, use_fallback: bool = True
    ):
        provider = os.getenv("INFERENCE_PROVIDER", "google").lower()

        if provider == "google":
            # SOTA Tiered Model Mapping (Gemini 2025 Fleet)
            model_map = {
                "ultra": "gemini-3-flash-preview",  # 5% target, strategic
                "strategic": "gemini-3-flash-preview",
                "reasoning": "gemini-2.5-flash",  # 15% target
                "driver": "gemini-2.0-flash",  # 40% target
                "mundane": "gemini-1.5-flash",  # 40% target
            }
            model_name = model_map.get(model_tier, "gemini-2.0-flash")
            logger.info(f"Routing to Gemini Tier: {model_tier} ({model_name})")

            api_key = get_vertex_api_key()

            primary_model = ChatVertexAI(
                model_name=model_name, temperature=temperature, api_key=api_key
            )

            if use_fallback and model_tier in ["ultra", "strategic", "reasoning"]:
                # Cascading Fallback Logic
                fallback_names = []
                if model_tier in ["ultra", "strategic"]:
                    fallback_names = ["gemini-2.5-flash", "gemini-2.0-flash"]
                elif model_tier == "reasoning":
                    fallback_names = ["gemini-2.0-flash"]

                fallbacks = [
                    ChatVertexAI(
                        model_name=name, temperature=temperature, api_key=api_key
                    )
                    for name in fallback_names
                ]
                return primary_model.with_fallbacks(fallbacks)

            return primary_model

        raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def get_embeddings():
        from langchain_google_vertexai import VertexAIEmbeddings

        provider = os.getenv("INFERENCE_PROVIDER", "google").lower()

        if provider == "google":
            return VertexAIEmbeddings(model_name="text-embedding-004")

        return VertexAIEmbeddings(model_name="text-embedding-004")  # Default
