"""
Response compression middleware
Implements gzip compression for API responses
"""

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
import logging

logger = logging.getLogger(__name__)


def add_compression_middleware(app: FastAPI) -> None:
    """
    Add compression middleware to FastAPI app.
    
    Compresses responses larger than 1KB with gzip.
    """
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,  # Only compress responses > 1KB
        compresslevel=6,    # Balanced compression (1-9, 6 is default)
    )
    logger.info("Compression middleware configured (gzip, min_size=1KB)")
