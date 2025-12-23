import logging
import os


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
        # Move imports inside to allow surgical mocking and avoid Python 3.14 crashes
        from langchain_google_vertexai import ChatVertexAI

        provider = os.getenv("INFERENCE_PROVIDER", "google").lower()

        if provider == "google":
            model_map = {
                "ultra": "gemini-1.5-pro",  # SOTA Reasoning
                "reasoning": "gemini-1.5-pro",
                "driver": "gemini-1.5-flash",  # High-speed reliable
                "mundane": "gemini-1.5-flash",
            }
            model_name = model_map.get(model_tier, "gemini-1.5-flash")
            logger.info(f"Routing to Gemini Tier: {model_tier} ({model_name})")

            api_key = get_vertex_api_key()

            primary_model = ChatVertexAI(
                model_name=model_name, temperature=temperature, api_key=api_key
            )

            if use_fallback and model_tier in ["ultra", "reasoning"]:
                # Fallback to Flash if Pro fails (e.g. quota, latency)
                fallback_model = ChatVertexAI(
                    model_name="gemini-1.5-flash",
                    temperature=temperature,
                    api_key=api_key,
                )
                return primary_model.with_fallbacks([fallback_model])

            return primary_model

        raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def get_embeddings():
        from langchain_google_vertexai import VertexAIEmbeddings

        provider = os.getenv("INFERENCE_PROVIDER", "google").lower()

        if provider == "google":
            return VertexAIEmbeddings(model_name="text-embedding-004")

        return VertexAIEmbeddings(model_name="text-embedding-004")  # Default
