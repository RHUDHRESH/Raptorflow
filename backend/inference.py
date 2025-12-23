import os
import logging
from typing import Union
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings

logger = logging.getLogger("raptorflow.inference")
# Potential future imports (pre-configured for easy swap)
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_anthropic import ChatAnthropic

class InferenceProvider:
    """
    SOTA Tiered Gemini Factory.
    Routes tasks to the optimal Gemini model based on reasoning complexity.
    """
    
    @staticmethod
    def get_model(model_tier: str = "driver", temperature: float = 0.0):
        provider = os.getenv("INFERENCE_PROVIDER", "google").lower()
        
        if provider == "google":
            model_map = {
                "ultra": "gemini-3-pro-preview",      # Ultra Reasoning
                "reasoning": "gemini-3-flash-preview", # High Reasoning
                "driver": "gemini-2.5-flash",         # Daily Driver
                "kinda_mundane": "gemini-2.0-flash",  # Mundane Tasks
                "mundane": "gemini-1.5-flash"         # Simple Tasks
            }
            model_name = model_map.get(model_tier, "gemini-2.5-flash")
            logger.info(f"Routing to Gemini Tier: {model_tier} ({model_name})")
            
            return ChatVertexAI(
                model_name=model_name,
                temperature=temperature
            )
            
        raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def get_embeddings():
        provider = os.getenv("INFERENCE_PROVIDER", "google").lower()
        
        if provider == "google":
            return VertexAIEmbeddings(model_name="text-embedding-004")
            
        # elif provider == "openai":
        #     return OpenAIEmbeddings(model="text-embedding-3-small")
            
        return VertexAIEmbeddings(model_name="text-embedding-004") # Default
