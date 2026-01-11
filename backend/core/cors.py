"""
Production-ready CORS configuration for RaptorFlow
Configures cross-origin resource sharing policies
"""

import logging
import os
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


class CORSConfig:
    """CORS configuration settings"""

    def __init__(self):
        # Load allowed origins from environment
        self.allowed_origins = self._parse_allowed_origins()
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        self.allowed_headers = [
            "Authorization",
            "Content-Type",
            "X-Workspace-ID",
            "X-Requested-With",
            "Accept",
            "Origin",
        ]
        self.exposed_headers = ["X-Process-Time", "X-Total-Count"]
        self.allow_credentials = True
        self.max_age = 86400  # 24 hours

    def _parse_allowed_origins(self) -> List[str]:
        """Parse allowed origins from environment variable"""
        origins_str = os.getenv("ALLOWED_ORIGINS", "")

        if not origins_str:
            # Default for development
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
            ]

        # Parse comma-separated origins
        origins = [
            origin.strip() for origin in origins_str.split(",") if origin.strip()
        ]

        # Validate origins
        valid_origins = []
        for origin in origins:
            if self._is_valid_origin(origin):
                valid_origins.append(origin)
            else:
                logger.warning(f"Invalid origin format: {origin}")

        return valid_origins

    def _is_valid_origin(self, origin: str) -> bool:
        """Validate origin format"""
        if not origin:
            return False

        # Allow localhost for development
        if origin.startswith(
            (
                "http://localhost:",
                "https://localhost:",
                "http://127.0.0.1:",
                "https://127.0.0.1:",
            )
        ):
            return True

        # Basic URL validation
        if origin.startswith(("http://", "https://")):
            return True

        return False

    def get_cors_middleware(self, app: FastAPI) -> CORSMiddleware:
        """Get configured CORS middleware"""
        logger.info(f"Configuring CORS for origins: {self.allowed_origins}")

        return CORSMiddleware(
            app=app,
            allow_origins=self.allowed_origins,
            allow_credentials=self.allow_credentials,
            allow_methods=self.allowed_methods,
            allow_headers=self.allowed_headers,
            expose_headers=self.exposed_headers,
            max_age=self.max_age,
        )


def add_cors_middleware(app: FastAPI) -> None:
    """
    Add CORS middleware to FastAPI application

    Args:
        app: FastAPI application instance
    """
    cors_config = CORSConfig()
    app.add_middleware(cors_config.get_cors_middleware(app))


# Global CORS config instance
_cors_config: Optional[CORSConfig] = None


def get_cors_config() -> CORSConfig:
    """Get global CORS configuration"""
    global _cors_config
    if _cors_config is None:
        _cors_config = CORSConfig()
    return _cors_config
