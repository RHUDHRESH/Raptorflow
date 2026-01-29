"""
BCM Semantic Versioning Service

Implements semantic versioning (semver) for Business Context Manifests
following the specification: MAJOR.MINOR.PATCH

- MAJOR: Incompatible API changes
- MINOR: Add functionality in a backwards compatible manner
- PATCH: Backwards compatible bug fixes
"""

import logging
import re
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ..integration.bcm_reducer import BusinessContextManifest


class VersionType(Enum):
    """Type of version change."""

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    HOTFIX = "hotfix"


@dataclass
class Version:
    """Represents a semantic version."""

    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None

    def __str__(self) -> str:
        """Return string representation."""
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version

    def __repr__(self) -> str:
        return f"Version({self.__str__()})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Version):
            return False
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
            and self.build == other.build
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, Version):
            return NotImplemented

        # Compare major, minor, patch
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch

        # Compare prerelease (no prerelease > prerelease)
        if self.prerelease and not other.prerelease:
            return True
        if not self.prerelease and other.prerelease:
            return False
        if self.prerelease and other.prerelease:
            return self.prerelease < other.prerelease

        # Compare build (no build > build)
        if self.build and not other.build:
            return True
        if not self.build and other.build:
            return False
        if self.build and other.build:
            return self.build < other.build

        return False

    def __le__(self, other) -> bool:
        return self < other or self == other

    def __gt__(self, other) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return other < self

    def __ge__(self, other) -> bool:
        return self > other or self == other


class SemanticVersioning:
    """
    Semantic versioning service for BCM management.

    Handles version increment logic, conflict detection, and version history tracking.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_version(self, version_string: str) -> Version:
        """
        Parse a version string into a Version object.

        Args:
            version_string: Version string (e.g., "1.2.3", "2.0.0-alpha.1")

        Returns:
            Version object

        Raises:
            ValueError: If version string is invalid
        """
        try:
            # Parse semantic version pattern
            # https://semver.org/spec/v2.0.0.html
            semver_pattern = r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>[0-9A-Za-z\-\.]+))?(?:\+(?P<build>[0-9A-Za-z\-\.]+))?$"

            match = re.match(semver_pattern, version_string)
            if not match:
                raise ValueError(f"Invalid version string: {version_string}")

            return Version(
                major=int(match.group("major")),
                minor=int(match.group("minor")),
                patch=int(match.group("patch")),
                prerelease=match.group("prerelease"),
                build=match.group("build"),
            )

        except Exception as e:
            raise ValueError(f"Error parsing version '{version_string}': {e}")

    def get_current_version(self, bcm: BusinessContextManifest) -> Version:
        """
        Extract current version from BCM.

        Args:
            bcm: Business Context Manifest

        Returns:
            Current version
        """
        try:
            # Try to get version from links metadata first
            if bcm.links and "version" in bcm.links:
                return self.parse_version(bcm.links["version"])

            # Fallback to default version
            return self.parse_version("1.0.0")

        except Exception as e:
            self.logger.error(f"Error extracting version from BCM: {e}")
            return self.parse_version("1.0.0")

    def determine_version_change(
        self, old_bcm: BusinessContextManifest, new_bcm: BusinessContextManifest
    ) -> Tuple[VersionType, str]:
        """
        Determine the type of version change needed.

        Args:
            old_bcm: Previous BCM
            new_bcm: New BCM

        Returns:
            Tuple of (version_type, reason)
        """
        reasons = []

        # Check for major version changes (breaking changes)
        if self._has_breaking_changes(old_bcm, new_bcm):
            return (VersionType.MAJOR, "Breaking changes detected")

        # Check for minor version changes (new features)
        if self._has_new_features(old_bcm, new_bcm):
            return (VersionType.MINOR, "New features added")

        # Check for patch version changes (bug fixes)
        if self._has_bug_fixes(old_bcm, new_bcm):
            return (VersionType.PATCH, "Bug fixes applied")

        # No significant changes
        return (VersionType.PATCH, "Minor update")

    def _has_breaking_changes(
        self, old_bcm: BusinessContextManifest, new_bcm: BusinessContextManifest
    ) -> bool:
        """
        Check if there are breaking changes between BCNs.

        Args:
            old_bcm: Previous BCM
            new_bcm: New BCM

        Returns:
            True if breaking changes detected
        """
        # Check for structural changes that would break compatibility
        breaking_indicators = [
            # Company structure changes
            old_bcm.company.name != new_bcm.company.name,
            # ICP count changes (affects integrations)
            len(old_bcm.icps) != len(new_bcm.icps),
            # Major messaging changes
            (
                old_bcm.value_prop.primary != new_bcm.value_prop.primary
                and old_bcm.value_prop.primary
                and new_bcm.value_prop.primary
            ),
            # Market positioning changes
            (old_bcm.market and not new_bcm.market)
            or (not old_bcm.market and new_bcm.market),
        ]

        return any(breaking_indicators)

    def _has_new_features(
        self, old_bcm: BusinessContextManifest, new_bcm: BusinessContextManifest
    ) -> bool:
        """
        Check if there are new features added.

        Args:
            old_bcm: Previous BCM
            new_bcm: New BCM

        Returns:
            True if new features detected
        """
        new_feature_indicators = [
            # New ICPs added
            len(new_bcm.icps) > len(old_bcm.icps),
            # New key messages
            len(new_bcm.key_messages) > len(old_bcm.key_messages),
            # New taglines
            len(new_bcm.taglines) > len(old_bcm.taglines),
            # New goals or KPIs
            len(new_bcm.short_term_goals) > len(old_bcm.short_term_goals),
            len(new_bcm.kpis) > len(old_bcm.kpis),
            # New channels
            len(new_bcm.primary_channels) > len(old_bcm.primary_channels),
        ]

        return any(new_feature_indicators)

    def _has_bug_fixes(
        self, old_bcm: BusinessContextManifest, new_bcm: BusinessContextManifest
    ) -> bool:
        """
        Check if there are bug fixes applied.

        Args:
            old_bcm: Previous BCM
            new_bcm: New BCM

        Returns:
            True if bug fixes detected
        """
        # For now, any change that's not a breaking change or new feature
        # is considered a patch/bug fix
        return not (
            self._has_breaking_changes(old_bcm, new_bcm)
            or self._has_new_features(old_bcm, new_bcm)
        )

    def increment_version(
        self, current_version: Version, version_type: VersionType
    ) -> Version:
        """
        Increment version based on change type.

        Args:
            current_version: Current version
            version_type: Type of version change

        Returns:
            New version
        """
        if version_type == VersionType.MAJOR:
            return Version(
                major=current_version.major + 1,
                minor=0,
                patch=0,
                prerelease=None,
                build=None,
            )
        elif version_type == VersionType.MINOR:
            return Version(
                major=current_version.major,
                minor=current_version.minor + 1,
                patch=0,
                prerelease=None,
                build=None,
            )
        elif version_type == VersionType.PATCH:
            return Version(
                major=current_version.major,
                minor=current_version.minor,
                patch=current_version.patch + 1,
                prerelease=None,
                build=None,
            )
        else:
            # Default to patch for unknown types
            return Version(
                major=current_version.major,
                minor=current_version.minor,
                patch=current_version.patch + 1,
                prerelease=None,
                build=None,
            )

    def create_version_with_metadata(
        self, version: Version, metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create version information with metadata.

        Args:
            version: Version object
            metadata: Additional metadata

        Returns:
            Version information dictionary
        """
        version_info = {
            "version_string": str(version),
            "version_major": version.major,
            "version_minor": version.minor,
            "version_patch": version.patch,
            "prerelease": version.prerelease,
            "build": version.build,
            "created_at": datetime.utcnow().isoformat(),
        }

        if metadata:
            version_info.update(metadata)

        return version_info

    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        try:
            v1 = self.parse_version(version1)
            v2 = self.parse_version(version2)

            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            else:
                return 0

        except Exception as e:
            self.logger.error(
                f"Error comparing versions {version1} and {version2}: {e}"
            )
            return 0

    def is_version_compatible(
        self, required_version: str, current_version: str
    ) -> bool:
        """
        Check if current version meets required version compatibility.

        Args:
            required_version: Minimum required version
            current_version: Current version to check

        Returns:
            True if compatible, False otherwise
        """
        try:
            required = self.parse_version(required_version)
            current = self.parse_version(current_version)

            # Major version must match exactly
            if required.major != current.major:
                return False

            # Current minor must be >= required minor
            if current.minor < required.minor:
                return False

            # If major and minor match, patch must be >= required patch
            if current.minor == required.minor and current.patch < required.patch:
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking version compatibility: {e}")
            return False

    def get_version_range(self, min_version: str, max_version: str) -> Dict[str, Any]:
        """
        Get information about a version range.

        Args:
            min_version: Minimum version
            max_version: Maximum version

        Returns:
            Version range information
        """
        try:
            min_v = self.parse_version(min_version)
            max_v = self.parse_version(max_version)

            return {
                "min_version": str(min_v),
                "max_version": str(max_v),
                "range_size": self._calculate_range_size(min_v, max_v),
                "is_valid_range": min_v <= max_v,
            }

        except Exception as e:
            self.logger.error(f"Error creating version range: {e}")
            return {}

    def _calculate_range_size(self, min_version: Version, max_version: Version) -> int:
        """
        Calculate the number of versions in a range.

        Args:
            min_version: Minimum version
            max_version: Maximum version

        Returns:
            Number of versions in range
        """
        if min_version > max_version:
            return 0

        # Simple calculation - in a real implementation, this would be more complex
        major_diff = max_version.major - min_version.major
        minor_diff = max_version.minor - min_version.minor
        patch_diff = max_version.patch - min_version.patch

        return (major_diff * 10000) + (minor_diff * 100) + patch_diff

    def validate_version_string(self, version_string: str) -> bool:
        """
        Validate if a string is a valid semantic version.

        Args:
            version_string: Version string to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            self.parse_version(version_string)
            return True
        except ValueError:
            return False

    def get_latest_version(self, versions: list[str]) -> Optional[str]:
        """
        Get the latest version from a list of version strings.

        Args:
            versions: List of version strings

        Returns:
            Latest version string or None if list is empty
        """
        if not versions:
            return None

        try:
            # Parse all versions and find the maximum
            parsed_versions = []
            for version_str in versions:
                if self.validate_version_string(version_str):
                    parsed_versions.append(
                        (self.parse_version(version_str), version_str)
                    )

            if parsed_versions:
                # Sort by version and return the latest
                latest = max(parsed_versions, key=lambda x: x[0])
                return latest[1]

        except Exception as e:
            self.logger.error(f"Error finding latest version: {e}")

        return None

    def format_version_for_display(self, version: Version) -> str:
        """
        Format version for human-readable display.

        Args:
            version: Version object

        Returns:
            Formatted version string
        """
        formatted = f"v{version.major}.{version.minor}.{version.patch}"

        if version.prerelease:
            formatted += f"-{version.prerelease}"

        if version.build:
            formatted += f" (build {version.build})"

        return formatted
