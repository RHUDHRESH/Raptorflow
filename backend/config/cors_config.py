"""
CORS configuration for Raptorflow backend.
"""

from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings import get_settings


def get_cors_config() -> Dict[str, Any]:
    """Get CORS configuration based on environment."""
    settings = get_settings()

    return {
        "allow_origins": settings.get_cors_origins(),
        "allow_credentials": settings.CORS_ALLOW_CREDENTIALS,
        "allow_methods": settings.CORS_ALLOW_METHODS,
        "allow_headers": settings.CORS_ALLOW_HEADERS,
    }


def configure_cors(app: FastAPI) -> None:
    """Configure CORS middleware for FastAPI app."""
    cors_config = get_cors_config()

    app.add_middleware(CORSMiddleware, **cors_config)


class CORSConfig:
    """CORS configuration management."""

    def __init__(self):
        self.settings = get_settings()

    def get_allowed_origins(self) -> List[str]:
        """Get allowed origins based on environment."""
        if self.settings.is_development:
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://localhost:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
            ]
        elif self.settings.is_staging:
            return [
                "https://staging.raptorflow.app",
                "https://staging-admin.raptorflow.app",
            ]
        else:
            return [
                "https://app.raptorflow.app",
                "https://admin.raptorflow.app",
                "https://raptorflow.app",
            ]

    def get_allowed_methods(self) -> List[str]:
        """Get allowed HTTP methods."""
        return [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "OPTIONS",
            "HEAD",
        ]

    def get_allowed_headers(self) -> List[str]:
        """Get allowed headers."""
        return [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID",
            "X-Workspace-ID",
            "X-User-ID",
            "Origin",
            "Cache-Control",
            "Pragma",
        ]

    def get_exposed_headers(self) -> List[str]:
        """Get exposed headers."""
        return [
            "X-Request-ID",
            "X-Total-Count",
            "X-Page-Count",
            "X-Rate-Limit-Limit",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset",
        ]

    def get_max_age(self) -> int:
        """Get max age for preflight requests."""
        return 86400  # 24 hours

    def get_cors_middleware_config(self) -> Dict[str, Any]:
        """Get complete CORS middleware configuration."""
        return {
            "allow_origins": self.get_allowed_origins(),
            "allow_credentials": True,
            "allow_methods": self.get_allowed_methods(),
            "allow_headers": self.get_allowed_headers(),
            "expose_headers": self.get_exposed_headers(),
            "max_age": self.get_max_age(),
        }

    def is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed."""
        allowed_origins = self.get_allowed_origins()

        # Exact match
        if origin in allowed_origins:
            return True

        # Wildcard subdomains for production
        if self.settings.is_production:
            if origin.endswith(".raptorflow.app"):
                return True

        return False

    def add_cors_headers(
        self, headers: Dict[str, str], origin: str = None
    ) -> Dict[str, str]:
        """Add CORS headers to response."""
        if origin and self.is_origin_allowed(origin):
            headers["Access-Control-Allow-Origin"] = origin

        headers["Access-Control-Allow-Credentials"] = "true"
        headers["Access-Control-Allow-Methods"] = ", ".join(self.get_allowed_methods())
        headers["Access-Control-Allow-Headers"] = ", ".join(self.get_allowed_headers())
        headers["Access-Control-Expose-Headers"] = ", ".join(self.get_exposed_headers())
        headers["Access-Control-Max-Age"] = str(self.get_max_age())

        return headers


# Global CORS config instance
_cors_config: CORSConfig = None


def get_cors_config_instance() -> CORSConfig:
    """Get the global CORS config instance."""
    global _cors_config
    if _cors_config is None:
        _cors_config = CORSConfig()
    return _cors_config
