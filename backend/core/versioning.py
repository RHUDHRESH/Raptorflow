import logging
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.routing import APIRoute

logger = logging.getLogger("raptorflow.versioning")


class APIVersion(Enum):
    """Supported API versions."""

    V1 = "v1"
    V2 = "v2"


class VersionedAPIRoute(APIRoute):
    """Custom route that handles API versioning."""

    def __init__(
        self,
        *args,
        deprecated_versions: Optional[List[str]] = None,
        removed_versions: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.deprecated_versions = deprecated_versions or []
        self.removed_versions = removed_versions or []


class APIVersionManager:
    """
    Production-grade API versioning system with deprecation and removal support.
    """

    def __init__(self):
        self.versions: Dict[str, Dict[str, Any]] = {}
        self.deprecation_warnings: Dict[str, str] = {}
        self.removal_errors: Dict[str, str] = {}

    def register_version(
        self,
        version: str,
        description: str,
        deprecated: bool = False,
        removal_date: Optional[str] = None,
        migration_guide: Optional[str] = None,
    ):
        """Register an API version."""
        self.versions[version] = {
            "description": description,
            "deprecated": deprecated,
            "removal_date": removal_date,
            "migration_guide": migration_guide,
            "endpoints": [],
        }

        if deprecated:
            self.deprecation_warnings[version] = (
                f"API version {version} is deprecated. "
                f"Please migrate to the latest version. "
                f"{'Removal date: ' + removal_date if removal_date else ''}"
                f"{'Migration guide: ' + migration_guide if migration_guide else ''}"
            )

    def add_endpoint_to_version(self, version: str, endpoint: str, method: str):
        """Add an endpoint to a version."""
        if version in self.versions:
            self.versions[version]["endpoints"].append(f"{method} {endpoint}")

    def is_version_supported(self, version: str) -> bool:
        """Check if a version is supported."""
        return version in self.versions and not self.versions[version].get(
            "removed", False
        )

    def is_version_deprecated(self, version: str) -> bool:
        """Check if a version is deprecated."""
        return version in self.versions and self.versions[version].get(
            "deprecated", False
        )

    def get_latest_version(self) -> str:
        """Get the latest supported version."""
        supported_versions = [
            v for v in self.versions.keys() if self.is_version_supported(v)
        ]
        return max(supported_versions) if supported_versions else None

    def get_version_info(self, version: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific version."""
        return self.versions.get(version)


# Global version manager
_version_manager: Optional[APIVersionManager] = None


def get_version_manager() -> APIVersionManager:
    """Get the global version manager instance."""
    global _version_manager
    if _version_manager is None:
        _version_manager = APIVersionManager()
        _setup_default_versions()
    return _version_manager


def _setup_default_versions():
    """Setup default API versions."""
    manager = get_version_manager()

    # Register v1 (current stable version)
    manager.register_version(
        version="v1", description="Current stable API version", deprecated=False
    )

    # Register v2 (future version, not yet implemented)
    manager.register_version(
        version="v2",
        description="Next generation API with enhanced features",
        deprecated=False,
    )


class VersionMiddleware:
    """Middleware to handle API versioning."""

    def __init__(self, app, version_manager: APIVersionManager):
        self.app = app
        self.version_manager = version_manager

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Extract version from request
            version = self._extract_version(scope)

            # Validate version
            if not self.version_manager.is_version_supported(version):
                await self._send_version_error(send, version)
                return

            # Add deprecation warning if needed
            if self.version_manager.is_version_deprecated(version):
                await self._add_deprecation_header(send, version)

            # Add version to scope for downstream use
            scope["api_version"] = version

        await self.app(scope, receive, send)

    def _extract_version(self, scope: Dict[str, Any]) -> str:
        """Extract API version from request."""
        # Method 1: From URL path
        path = scope.get("path", "")
        if path.startswith("/v1/"):
            return "v1"
        elif path.startswith("/v2/"):
            return "v2"

        # Method 2: From Accept header
        headers = dict(scope.get("headers", []))
        accept = headers.get(b"accept", b"").decode()
        if "application/vnd.raptorflow.v1+json" in accept:
            return "v1"
        elif "application/vnd.raptorflow.v2+json" in accept:
            return "v2"

        # Method 3: From custom header
        api_version = headers.get(b"x-api-version", b"").decode()
        if api_version in ["v1", "v2"]:
            return api_version

        # Default to latest version
        return self.version_manager.get_latest_version() or "v1"

    async def _send_version_error(self, send, requested_version: str):
        """Send version not supported error."""
        latest_version = self.version_manager.get_latest_version()

        response = Response(
            content={
                "error": "API version not supported",
                "message": f"Version '{requested_version}' is not supported",
                "supported_versions": list(self.version_manager.versions.keys()),
                "latest_version": latest_version,
            },
            status_code=400,
        )

        await response(scope, receive, send)

    async def _add_deprecation_header(self, send, version: str):
        """Add deprecation warning header."""
        warning = self.version_manager.deprecation_warnings.get(version, "")
        # Add deprecation header to response
        pass


def create_versioned_router(
    version: str, prefix: str, tags: List[str] = None, deprecated: bool = False
) -> APIRouter:
    """Create a versioned API router."""
    manager = get_version_manager()

    if not manager.is_version_supported(version):
        raise ValueError(f"API version {version} is not supported")

    # Add deprecation warning to tags if needed
    if deprecated or manager.is_version_deprecated(version):
        if tags:
            tags = [f"{tag} (deprecated)" for tag in tags]
        else:
            tags = ["deprecated"]

    router = APIRouter(prefix=f"/{version}{prefix}", tags=tags)

    # Add version info endpoint
    @router.get("/version", include_in_schema=False)
    async def get_version_info():
        """Get API version information."""
        version_info = manager.get_version_info(version)
        return {
            "version": version,
            "description": version_info.get("description"),
            "deprecated": version_info.get("deprecated", False),
            "removal_date": version_info.get("removal_date"),
            "migration_guide": version_info.get("migration_guide"),
            "endpoints": version_info.get("endpoints", []),
        }

    return router


def version_endpoint(
    version: str,
    deprecated: bool = False,
    removal_date: Optional[str] = None,
    migration_guide: Optional[str] = None,
):
    """Decorator to mark endpoints with version information."""

    def decorator(func: Callable):
        # Add version metadata to function
        func._api_version = version
        func._deprecated = deprecated
        func._removal_date = removal_date
        func._migration_guide = migration_guide

        # Add deprecation warning to docstring if needed
        if deprecated:
            original_doc = func.__doc__ or ""
            deprecation_notice = (
                f"\n\nDEPRECATED: This endpoint is deprecated. "
                f"{'Removal date: ' + removal_date if removal_date else ''}"
                f"{'Migration guide: ' + migration_guide if migration_guide else ''}"
            )
            func.__doc__ = original_doc + deprecation_notice

        return func

    return decorator


class VersionCompatibilityChecker:
    """Check compatibility between API versions."""

    def __init__(self, version_manager: APIVersionManager):
        self.version_manager = version_manager

    def check_backward_compatibility(
        self, from_version: str, to_version: str
    ) -> Dict[str, Any]:
        """Check backward compatibility between versions."""
        compatibility = {
            "compatible": True,
            "breaking_changes": [],
            "deprecated_fields": [],
            "new_fields": [],
            "recommendations": [],
        }

        # Example compatibility checks (would be expanded based on actual API changes)
        if from_version == "v1" and to_version == "v2":
            compatibility["breaking_changes"] = [
                "Field 'old_field' removed from Campaign model",
                "Endpoint /old-endpoint removed",
            ]
            compatibility["deprecated_fields"] = [
                "Field 'legacy_field' in Campaign model"
            ]
            compatibility["new_fields"] = [
                "Field 'enhanced_metadata' in Campaign model",
                "New endpoint /v2/campaigns/analytics",
            ]
            compatibility["recommendations"] = [
                "Update client to use new field names",
                "Migrate to new endpoints before v1 removal",
            ]
            compatibility["compatible"] = False

        return compatibility

    def get_migration_path(self, from_version: str, to_version: str) -> List[str]:
        """Get migration path between versions."""
        # For now, assume direct migration is possible
        # In reality, this might involve intermediate versions
        return [from_version, to_version]


# Version validation middleware
async def validate_api_version(request: Request) -> Dict[str, Any]:
    """Validate API version in request."""
    version_manager = get_version_manager()

    # Extract version from request
    version = request.headers.get("X-API-Version")
    if not version:
        # Extract from path
        path = request.url.path
        if path.startswith("/v1/"):
            version = "v1"
        elif path.startswith("/v2/"):
            version = "v2"
        else:
            version = version_manager.get_latest_version() or "v1"

    # Validate version
    if not version_manager.is_version_supported(version):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unsupported API version",
                "requested_version": version,
                "supported_versions": list(version_manager.versions.keys()),
                "latest_version": version_manager.get_latest_version(),
            },
        )

    return {
        "version": version,
        "deprecated": version_manager.is_version_deprecated(version),
        "version_info": version_manager.get_version_info(version),
    }
