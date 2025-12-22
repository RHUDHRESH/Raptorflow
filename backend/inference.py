import os
from typing import Union
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
# Potential future imports (pre-configured for easy swap)
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_anthropic import ChatAnthropic

class InferenceProvider:
    """
    Central factory to swap inference providers (Vertex, OpenAI, Anthropic, etc.)
    Configuration is driven by INFERENCE_PROVIDER env var.
    """
    
    @staticmethod
    def get_model(model_tier: str = "fast", temperature: float = 0.0):
        provider = os.getenv("INFERENCE_PROVIDER", "google").lower()
        
        if provider == "google":
            model_map = {
                "fast": "gemini-1.5-flash-002",
                "smart": "gemini-1.5-pro-002",
                "ultra": "gemini-2.0-flash-exp"
            }
            return ChatVertexAI(
                model_name=model_map.get(model_tier, "gemini-1.5-flash-002"),
                temperature=temperature
            )
            
        # Example: Easy swap to OpenAI
        # elif provider == "openai":
        #     model_map = {"fast": "gpt-4o-mini", "smart": "gpt-4o"}
        #     return ChatOpenAI(model=model_map[model_tier], temperature=temperature)
            
        raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def get_embeddings():
        provider = os.getenv("INFERENCE_PROVIDER", "google").lower()
        
        if provider == "google":
            return VertexAIEmbeddings(model_name="text-embedding-004")
            
        # elif provider == "openai":
        #     return OpenAIEmbeddings(model="text-embedding-3-small")
            
        return VertexAIEmbeddings(model_name="text-embedding-004") # Default
