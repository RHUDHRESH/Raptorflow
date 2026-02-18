"""
Backward compatibility shim for bcm_generation_logger.

This module provides the legacy import path for generation logging functions,
redirecting to the new modular location.
"""

from backend.services.bcm.generation_logger import (
    cleanup_old_generations,
    get_rated_generations,
    get_recent_generations,
    log_generation,
)

__all__ = [
    "log_generation",
    "get_recent_generations",
    "get_rated_generations",
    "cleanup_old_generations",
]
