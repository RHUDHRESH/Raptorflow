"""
BCM Service - Business Context Manifest operations.
"""

from backend.services.bcm.service import BCMService, bcm_service
from backend.services.bcm.reducer import reduce_business_context
from backend.services.bcm.synthesizer import synthesize_business_context
from backend.services.bcm.templates import (
    TemplateType,
    extract_foundation_data,
    get_template,
)
from backend.services.bcm.generation_logger import (
    log_generation,
    get_recent_generations,
    get_rated_generations,
    cleanup_old_generations,
)

__all__ = [
    "BCMService",
    "bcm_service",
    "reduce_business_context",
    "synthesize_business_context",
    "TemplateType",
    "extract_foundation_data",
    "get_template",
    "log_generation",
    "get_recent_generations",
    "get_rated_generations",
    "cleanup_old_generations",
]
