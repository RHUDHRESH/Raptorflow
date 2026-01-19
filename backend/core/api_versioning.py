"""
API Versioning and Backward Compatibility System
Provides comprehensive API versioning with migration support and backward compatibility.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import json

class APIVersion(Enum):
    """Supported API versions."""
    V1 = "v1"
    V2 = "v2"

class VersionStatus(Enum):
    """Version lifecycle status."""
    DEVELOPMENT = "development"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"

@dataclass
class VersionInfo:
    """API version information."""
    version: APIVersion
    status: VersionStatus
    released_at: datetime
    deprecated_at: Optional[datetime]
    sunset_at: Optional[datetime]
    migration_guide: Optional[str]
    breaking_changes: List[str]
    supported_until: Optional[datetime]

class APIVersionManager:
    """Manages API versions and compatibility."""
    
    def __init__(self):
        self.versions: Dict[APIVersion, VersionInfo] = {}
        self.request_transformers: Dict[str, callable] = {}
        self.response_transformers: Dict[str, callable] = {}
        self._initialize_versions()
    
    def _initialize_versions(self):
        """Initialize API versions."""
        self.versions[APIVersion.V1] = VersionInfo(
            version=APIVersion.V1,
            status=VersionStatus.STABLE,
            released_at=datetime(2024, 1, 1),
            deprecated_at=None,
            sunset_at=None,
            migration_guide="/docs/migration/v1-to-v2",
            breaking_changes=[],
            supported_until=datetime(2025, 12, 31)
        )
        
        self.versions[APIVersion.V2] = VersionInfo(
            version=APIVersion.V2,
            status=VersionStatus.DEVELOPMENT,
            released_at=datetime(2024, 6, 1),
            deprecated_at=None,
            sunset_at=None,
            migration_guide="/docs/migration/v1-to-v2",
            breaking_changes=[
                "User endpoint response format changed",
                "Authentication header format updated"
            ],
            supported_until=datetime(2026, 12, 31)
        )
    
    def get_version(self, version: APIVersion) -> Optional[VersionInfo]:
        """Get version information."""
        return self.versions.get(version)
    
    def is_version_supported(self, version: APIVersion) -> bool:
        """Check if version is supported."""
        if version not in self.versions:
            return False
        
        version_info = self.versions[version]
        if version_info.status == VersionStatus.SUNSET:
            return False
        
        if version_info.supported_until and datetime.now() > version_info.supported_until:
            return False
        
        return True
    
    def transform_request(self, from_version: APIVersion, to_version: APIVersion, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform request data between versions."""
        transformer_key = f"{from_version.value}_to_{to_version.value}"
        if transformer_key in self.request_transformers:
            return self.request_transformers[transformer_key](data)
        return data
    
    def transform_response(self, from_version: APIVersion, to_version: APIVersion, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform response data between versions."""
        transformer_key = f"{from_version.value}_to_{to_version.value}"
        if transformer_key in self.response_transformers:
            return self.response_transformers[transformer_key](data)
        return data

# Global instance
_api_version_manager = APIVersionManager()

def get_api_version_manager() -> APIVersionManager:
    return _api_version_manager
