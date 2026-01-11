"""
Versioning for Protocol Standardization

Version control and compatibility management for cognitive components.
Implements PROMPT 76 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import semver
from packaging import version


class VersionType(Enum):
    """Types of version changes."""

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRE_RELEASE = "pre_release"
    BUILD = "build"


class CompatibilityLevel(Enum):
    """Compatibility levels between versions."""

    COMPATIBLE = "compatible"
    BACKWARD_COMPATIBLE = "backward_compatible"
    FORWARD_COMPATIBLE = "forward_compatible"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """Types of cognitive components."""

    PERCEPTION = "perception"
    PLANNING = "planning"
    REFLECTION = "reflection"
    CRITIC = "critic"
    INTEGRATION = "integration"
    PROTOCOL = "protocol"
    AGENT = "agent"
    WORKFLOW = "workflow"


@dataclass
class ComponentVersion:
    """Version information for a cognitive component."""

    component_id: str
    component_type: ComponentType
    version: str
    build_number: str
    release_date: datetime
    changelog: List[str]
    dependencies: Dict[str, str]  # component_id -> version
    compatibility_matrix: Dict[str, CompatibilityLevel]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize version if not provided."""
        if not self.version:
            self.version = "1.0.0"
        if not self.build_number:
            self.build_number = "1"
        if not self.release_date:
            self.release_date = datetime.now()

    def get_semver(self) -> version.Version:
        """Get semantic version object."""
        return version.Version(self.version)

    def is_compatible_with(self, other_version: str) -> CompatibilityLevel:
        """Check compatibility with another version."""
        try:
            current = self.get_semver()
            other = version.Version(other_version)

            # Same version - fully compatible
            if current == other:
                return CompatibilityLevel.COMPATIBLE

            # Major version difference - incompatible
            if current.major != other.major:
                return CompatibilityLevel.INCOMPATIBLE

            # Minor version difference - backward compatible
            if current.minor != other.minor:
                if current.minor > other.minor:
                    return CompatibilityLevel.BACKWARD_COMPATIBLE
                else:
                    return CompatibilityLevel.FORWARD_COMPATIBLE

            # Patch version difference - fully compatible
            return CompatibilityLevel.COMPATIBLE

        except Exception:
            return CompatibilityLevel.UNKNOWN

    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary."""
        return {
            "component_id": self.component_id,
            "component_type": self.component_type.value,
            "version": self.version,
            "build_number": self.build_number,
            "release_date": self.release_date.isoformat(),
            "changelog": self.changelog,
            "dependencies": self.dependencies,
            "compatibility_matrix": {
                version: level.value
                for version, level in self.compatibility_matrix.items()
            },
            "metadata": self.metadata,
        }


@dataclass
class VersionConstraint:
    """Version constraint for dependencies."""

    component_id: str
    constraint: str  # semver constraint string
    required: bool = True
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def satisfies(self, version: str) -> bool:
        """Check if a version satisfies the constraint."""
        try:
            return version.Version(version) in version.SpecifierSet(self.constraint)
        except Exception:
            return False


@dataclass
class VersionUpdate:
    """Information about a version update."""

    component_id: str
    from_version: str
    to_version: str
    update_type: VersionType
    description: str
    breaking_changes: List[str]
    new_features: List[str]
    bug_fixes: List[str]
    dependencies_added: Dict[str, str]
    dependencies_removed: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class VersionManager:
    """
    Version control and compatibility management for cognitive components.

    Manages component versions, dependencies, and compatibility.
    """

    def __init__(self):
        """Initialize the version manager."""
        self.components: Dict[str, ComponentVersion] = {}
        self.version_history: List[VersionUpdate] = []
        self.constraints: Dict[str, List[VersionConstraint]] = {}
        self.compatibility_cache: Dict[Tuple[str, str], CompatibilityLevel] = {}

        # Statistics
        self.stats = {
            "total_components": 0,
            "versions_by_type": {},
            "total_updates": 0,
            "breaking_changes": 0,
            "compatibility_checks": 0,
            "compatibility_cache_hits": 0,
        }

        # Setup default components
        self._setup_default_components()

    def register_component(self, component: ComponentVersion) -> None:
        """Register a component version."""
        self.components[component.component_id] = component
        self.stats["total_components"] += 1

        # Update type statistics
        component_type = component.component_type.value
        self.stats["versions_by_type"][component_type] = (
            self.stats["versions_by_type"].get(component_type, 0) + 1
        )

    def get_component(self, component_id: str) -> Optional[ComponentVersion]:
        """Get a component by ID."""
        return self.components.get(component_id)

    def update_component(
        self,
        component_id: str,
        new_version: str,
        update_type: VersionType,
        description: str,
        changelog: List[str] = None,
        breaking_changes: List[str] = None,
        new_features: List[str] = None,
        bug_fixes: List[str] = None,
    ) -> ComponentVersion:
        """Update a component to a new version."""
        current_component = self.components.get(component_id)
        if not current_component:
            raise ValueError(f"Component {component_id} not found")

        old_version = current_component.version

        # Create version update record
        update = VersionUpdate(
            component_id=component_id,
            from_version=old_version,
            to_version=new_version,
            update_type=update_type,
            description=description,
            breaking_changes=breaking_changes or [],
            new_features=new_features or [],
            bug_fixes=bug_fixes or [],
            dependencies_added={},
            dependencies_removed=[],
            metadata={"updated_at": datetime.now().isoformat()},
        )

        # Update component
        updated_component = ComponentVersion(
            component_id=component_id,
            component_type=current_component.component_type,
            version=new_version,
            build_number=str(int(current_component.build_number) + 1),
            release_date=datetime.now(),
            changelog=changelog or [],
            dependencies=current_component.dependencies.copy(),
            compatibility_matrix=current_component.compatibility_matrix.copy(),
            metadata=current_component.metadata.copy(),
        )

        # Update compatibility matrix
        updated_component.compatibility_matrix[old_version] = (
            updated_component.is_compatible_with(old_version)
        )

        # Register updated component
        self.register_component(updated_component)

        # Record update
        self.version_history.append(update)
        self.stats["total_updates"] += 1

        if update_type == VersionType.MAJOR:
            self.stats["breaking_changes"] += 1

        return updated_component

    def check_compatibility(
        self, component_id: str, version: str
    ) -> CompatibilityLevel:
        """Check compatibility between component versions."""
        cache_key = (component_id, version)

        # Check cache first
        if cache_key in self.compatibility_cache:
            self.stats["compatibility_cache_hits"] += 1
            return self.compatibility_cache[cache_key]

        component = self.get_component(component_id)
        if not component:
            return CompatibilityLevel.UNKNOWN

        compatibility = component.is_compatible_with(version)

        # Cache result
        self.compatibility_cache[cache_key] = compatibility
        self.stats["compatibility_checks"] += 1

        return compatibility

    def add_constraint(self, component_id: str, constraint: VersionConstraint) -> None:
        """Add a version constraint for a component."""
        if component_id not in self.constraints:
            self.constraints[component_id] = []

        self.constraints[component_id].append(constraint)

    def remove_constraint(self, component_id: str, constraint_index: int) -> bool:
        """Remove a version constraint."""
        if component_id in self.constraints:
            constraints = self.constraints[component_id]
            if 0 <= constraint_index < len(constraints):
                constraints.pop(constraint_index)
                return True
        return False

    def get_constraints(self, component_id: str) -> List[VersionConstraint]:
        """Get constraints for a component."""
        return self.constraints.get(component_id, [])

    def validate_dependencies(self, component_id: str) -> Dict[str, Any]:
        """Validate dependencies for a component."""
        component = self.get_component(component_id)
        if not component:
            return {"valid": False, "error": "Component not found"}

        validation_result = {
            "valid": True,
            "dependencies": {},
            "violations": [],
            "warnings": [],
        }

        # Check each dependency
        for dep_id, required_version in component.dependencies.items():
            dep_component = self.get_component(dep_id)

            if not dep_component:
                validation_result["violations"].append(f"Dependency {dep_id} not found")
                validation_result["valid"] = False
                continue

            # Check version compatibility
            compatibility = self.check_compatibility(dep_id, required_version)

            validation_result["dependencies"][dep_id] = {
                "required_version": required_version,
                "available_version": dep_component.version,
                "compatibility": compatibility.value,
            }

            if compatibility == CompatibilityLevel.INCOMPATIBLE:
                validation_result["violations"].append(
                    f"Incompatible version for {dep_id}: required {required_version}, available {dep_component.version}"
                )
                validation_result["valid"] = False
            elif compatibility == CompatibilityLevel.UNKNOWN:
                validation_result["warnings"].append(
                    f"Unknown compatibility for {dep_id}: required {required_version}, available {dep_component.version}"
                )

        # Check constraints
        for constraint in self.get_constraints(component_id):
            if not constraint.satisfies(component.version):
                validation_result["violations"].append(
                    f"Version constraint violated: {component.version} does not satisfy {constraint.constraint}"
                )
                validation_result["valid"] = False

        return validation_result

    def get_compatible_versions(self, component_id: str) -> List[str]:
        """Get all compatible versions for a component."""
        component = self.get_component(component_id)
        if not component:
            return []

        compatible_versions = []

        for version_str, compatibility in component.compatibility_matrix.items():
            if compatibility in [
                CompatibilityLevel.COMPATIBLE,
                CompatibilityLevel.BACKWARD_COMPATIBLE,
            ]:
                compatible_versions.append(version_str)

        return compatible_versions

    def find_latest_compatible(
        self, component_id: str, required_version: str
    ) -> Optional[str]:
        """Find the latest compatible version for a component."""
        component = self.get_component(component_id)
        if not component:
            return None

        # Get all versions (this would typically come from a version registry)
        all_versions = [component.version]  # Simplified

        # Filter compatible versions
        compatible_versions = []
        for version in all_versions:
            if self.check_compatibility(component_id, version) in [
                CompatibilityLevel.COMPATIBLE,
                CompatibilityLevel.BACKWARD_COMPATIBLE,
            ]:
                try:
                    if version.Version(version) >= version.Version(required_version):
                        compatible_versions.append(version)
                except:
                    pass

        # Return latest compatible version
        if compatible_versions:
            return max(compatible_versions, key=lambda v: version.Version(v))

        return None

    def get_version_history(self, component_id: str = None) -> List[VersionUpdate]:
        """Get version history for a component or all components."""
        if component_id:
            return [
                update
                for update in self.version_history
                if update.component_id == component_id
            ]
        else:
            return self.version_history

    def get_component_stats(self) -> Dict[str, Any]:
        """Get component version statistics."""
        return self.stats

    def export_versions(self, format: str = "json") -> str:
        """Export version information."""
        export_data = {
            "components": {
                component_id: component.to_dict()
                for component_id, component in self.components.items()
            },
            "constraints": {
                component_id: [
                    {
                        "constraint": constraint.constraint,
                        "required": constraint.required,
                        "reason": constraint.reason,
                    }
                    for constraint in constraints
                ]
                for component_id, constraints in self.constraints.items()
            },
            "version_history": [
                {
                    "component_id": update.component_id,
                    "from_version": update.from_version,
                    "to_version": update.to_version,
                    "update_type": update.update_type.value,
                    "description": update.description,
                    "breaking_changes": update.breaking_changes,
                    "new_features": update.new_features,
                    "bug_fixes": update.bug_fixes,
                    "metadata": update.metadata,
                }
                for update in self.version_history
            ],
            "statistics": self.stats,
            "exported_at": datetime.now().isoformat(),
        }

        if format.lower() == "json":
            return json.dumps(export_data, indent=2)
        else:
            raise ValueError(f"Format {format} not supported")

    def _setup_default_components(self) -> None:
        """Setup default cognitive components."""
        # Perception module
        perception = ComponentVersion(
            component_id="perception_module",
            component_type=ComponentType.PERCEPTION,
            version="1.0.0",
            build_number="1",
            release_date=datetime.now(),
            changelog=["Initial release"],
            dependencies={},
            compatibility_matrix={},
            metadata={"description": "Cognitive perception module"},
        )

        # Planning module
        planning = ComponentVersion(
            component_id="planning_module",
            component_type=ComponentType.PLANNING,
            version="1.0.0",
            build_number="1",
            release_date=datetime.now(),
            changelog=["Initial release"],
            dependencies={"perception_module": "1.0.0"},
            compatibility_matrix={},
            metadata={"description": "Cognitive planning module"},
        )

        # Reflection module
        reflection = ComponentVersion(
            component_id="reflection_module",
            component_type=ComponentType.REFLECTION,
            version="1.0.0",
            build_number="1",
            release_date=datetime.now(),
            changelog=["Initial release"],
            dependencies={"perception_module": "1.0.0"},
            compatibility_matrix={},
            metadata={"description": "Cognitive reflection module"},
        )

        # Critic module
        critic = ComponentVersion(
            component_id="critic_module",
            component_type=ComponentType.CRITIC,
            version="1.0.0",
            build_number="1",
            release_date=datetime.now(),
            changelog=["Initial release"],
            dependencies={"perception_module": "1.0.0"},
            compatibility_matrix={},
            metadata={"description": "Cognitive adversarial critic module"},
        )

        # Integration module
        integration = ComponentVersion(
            component_id="integration_module",
            component_type=ComponentType.INTEGRATION,
            version="1.0.0",
            build_number="1",
            release_date=datetime.now(),
            changelog=["Initial release"],
            dependencies={
                "perception_module": "1.0.0",
                "planning_module": "1.0.0",
                "reflection_module": "1.0.0",
                "critic_module": "1.0.0",
            },
            compatibility_matrix={},
            metadata={"description": "Cognitive integration module"},
        )

        # Register components
        self.register_component(perception)
        self.register_component(planning)
        self.register_component(reflection)
        self.register_component(critic)
        self.register_component(integration)

        # Setup compatibility matrices
        planning.compatibility_matrix["1.0.0"] = CompatibilityLevel.COMPATIBLE
        reflection.compatibility_matrix["1.0.0"] = CompatibilityLevel.COMPATIBLE
        critic.compatibility_matrix["1.0.0"] = CompatibilityLevel.COMPATIBLE
        integration.compatibility_matrix["1.0.0"] = CompatibilityLevel.COMPATIBLE

        # Add default constraints
        self.add_constraint(
            "planning_module",
            VersionConstraint(
                component_id="perception_module",
                constraint="^1.0.0",
                required=True,
                reason="Planning module requires perception module v1.0.0",
            ),
        )

        self.add_constraint(
            "reflection_module",
            VersionConstraint(
                component_id="perception_module",
                constraint="^1.0.0",
                required=True,
                reason="Reflection module requires perception module v1.0.0",
            ),
        )

        self.add_constraint(
            "critic_module",
            VersionConstraint(
                component_id="perception_module",
                constraint="^1.0.0",
                required=True,
                reason="Critic module requires perception module v1.0.0",
            ),
        )

        self.add_constraint(
            "integration_module",
            VersionConstraint(
                component_id="perception_module",
                constraint="^1.0.0",
                required=True,
                reason="Integration module requires perception module v1.0.0",
            ),
        )

        self.add_constraint(
            "integration_module",
            VersionConstraint(
                component_id="planning_module",
                constraint="^1.0.0",
                required=True,
                reason="Integration module requires planning module v1.0.0",
            ),
        )


class VersionComparator:
    """Comparator for semantic version comparison."""

    @staticmethod
    def compare(version1: str, version2: str) -> int:
        """
        Compare two semantic versions.

        Returns:
            -1 if version1 < version2
             0 if version1 == version2
             1 if version1 > version2
        """
        try:
            v1 = version.Version(version1)
            v2 = version.Version(version2)

            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            else:
                return 0

        except Exception:
            # Fallback to string comparison
            if version1 < version2:
                return -1
            elif version1 > version2:
                return 1
            else:
                return 0

    @staticmethod
    def is_greater(version1: str, version2: str) -> bool:
        """Check if version1 is greater than version2."""
        return VersionComparator.compare(version1, version2) > 0

    @staticmethod
    def is_less(version1: str, version2: str) -> bool:
        """Check if version1 is less than version2."""
        return VersionComparator.compare(version1, version2) < 0

    @staticmethod
    def is_equal(version1: str, version2: str) -> bool:
        """Check if version1 equals version2."""
        return VersionComparator.compare(version1, version2) == 0

    @staticmethod
    def get_latest_version(versions: List[str]) -> Optional[str]:
        """Get the latest version from a list."""
        if not versions:
            return None

        latest = versions[0]
        for version in versions[1:]:
            if VersionComparator.is_greater(version, latest):
                latest = version

        return latest

    @staticmethod
    def sort_versions(versions: List[str]) -> List[str]:
        """Sort versions in ascending order."""
        return sorted(versions, key=cmp_to_key(VersionComparator.compare))


def cmp_to_key(mycmp):
    """Convert cmp function to key function for sorting."""

    class K:
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0

    return K
