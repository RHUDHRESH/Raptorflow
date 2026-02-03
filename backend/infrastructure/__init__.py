"""
Infrastructure module for Raptorflow backend.

Provides database, cache, LLM, storage, and email services.
"""

from .database import SupabaseClient, get_supabase, get_service_supabase
from .cache import CacheClient, get_cache
from .llm import LLMClient, get_llm
from .email import EmailClient, get_email

try:
    from .storage import CloudStorage, get_cloud_storage
except ImportError:  # pragma: no cover
    CloudStorage = None  # type: ignore
    get_cloud_storage = None  # type: ignore

# Legacy GCP imports (for backward compatibility)
try:
    from .bigquery import BigQueryClient
    from .cloud_tasks import CloudTasksClient
    from .pubsub_client import PubSubClient
    from .gcp import GCPClient
    
    __all__ = [
        "SupabaseClient",
        "get_supabase",
        "get_service_supabase",
        "CacheClient",
        "get_cache",
        "LLMClient",
        "get_llm",
        "CloudStorage",
        "get_cloud_storage",
        "EmailClient",
        "get_email",
        # Legacy
        "GCPClient",
        "BigQueryClient",
        "PubSubClient",
        "CloudTasksClient",
    ]
except ImportError:
    __all__ = [
        "SupabaseClient",
        "get_supabase",
        "get_service_supabase",
        "CacheClient",
        "get_cache",
        "LLMClient",
        "get_llm",
        "CloudStorage",
        "get_cloud_storage",
        "EmailClient",
        "get_email",
    ]
