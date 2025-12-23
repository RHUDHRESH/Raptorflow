import os


def get_embedding_client():
    """
    Returns an initialized Vertex AI Embeddings client.
    Uses lazy import to avoid numpy/pandas crashes on certain systems.
    """
    from langchain_google_vertexai import VertexAIEmbeddings
    
    model_name = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
    return VertexAIEmbeddings(model_name=model_name)


class VertexManager:
    """
    Centralized manager for Vertex AI client lifecycle.
    """
    def __init__(self):
        self._embedding_client = None

    def get_embeddings(self):
        if not self._embedding_client:
            self._embedding_client = get_embedding_client()
        return self._embedding_client
