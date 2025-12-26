from core.config import get_settings


def get_embedding_client():
    """
    Returns an initialized Vertex AI Embeddings client.
    Uses lazy import to avoid numpy/pandas crashes on certain systems.
    """
    # Lazy import to prevent startup crashes
    from langchain_google_vertexai import VertexAIEmbeddings

    settings = get_settings()
    model_name = settings.EMBEDDING_MODEL
    kwargs = {"model_name": model_name}
    fields_set = getattr(settings, "model_fields_set", set())
    if "GCP_PROJECT_ID" in fields_set:
        kwargs["project"] = settings.GCP_PROJECT_ID
    if "GCP_REGION" in fields_set:
        kwargs["location"] = settings.GCP_REGION
    return VertexAIEmbeddings(**kwargs)


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
