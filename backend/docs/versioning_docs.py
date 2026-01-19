"""
Versioning Documentation with Migration Guides and Deprecation Notices

Comprehensive API versioning documentation for RaptorFlow backend:
- API versioning strategy and policies
- Migration guides between versions
- Deprecation notices and timelines
- Breaking change documentation
- Version comparison tools
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import yaml
from deepdiff import DeepDiff
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DeprecationStatus(Enum):
    """Deprecation status levels."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"
    REMOVED = "removed"


class ChangeType(Enum):
    """Types of API changes."""
    BREAKING = "breaking"
    NON_BREAKING = "non_breaking"
    FEATURE = "feature"
    BUG_FIX = "bug_fix"
    SECURITY = "security"
    DEPRECATION = "deprecation"


@dataclass
class APIVersion:
    """API version information."""
    version: str
    status: DeprecationStatus
    release_date: datetime
    deprecation_date: Optional[datetime] = None
    sunset_date: Optional[datetime] = None
    removal_date: Optional[datetime] = None
    description: str = ""
    migration_guide: Optional[str] = None


@dataclass
class APIChange:
    """API change details."""
    version: str
    change_type: ChangeType
    endpoint: str
    method: str
    description: str
    breaking: bool = False
    migration_required: bool = False
    old_behavior: Optional[str] = None
    new_behavior: Optional[str] = None
    code_example: Optional[str] = None


@dataclass
class MigrationStep:
    """Migration step instructions."""
    step_number: int
    title: str
    description: str
    code_changes: Optional[str] = None
    testing_instructions: Optional[str] = None
    estimated_time: Optional[str] = None


class VersioningConfig(BaseModel):
    """Versioning documentation configuration."""
    output_dir: str = "versioning_docs"
    current_version: str = "1.0.0"
    supported_versions: List[str] = Field(default=["1.0.0"])
    deprecation_timeline_months: int = 6
    sunset_timeline_months: int = 12
    openapi_specs_dir: str = "docs"
    generate_migration_guides: bool = True
    generate_changelog: bool = True


class VersioningDocumentation:
    """Comprehensive versioning documentation generator."""

    def __init__(self, config: VersioningConfig):
        self.config = config
        self.versions: Dict[str, APIVersion] = {}
        self.changes: List[APIChange] = []
        
        # Create output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize version information
        self._initialize_versions()

    def _initialize_versions(self) -> None:
        """Initialize API version information."""
        current_date = datetime.now()
        
        # Current version
        self.versions[self.config.current_version] = APIVersion(
            version=self.config.current_version,
            status=DeprecationStatus.ACTIVE,
            release_date=current_date,
            description="Current stable version with VertexAI integration"
        )
        
        # Add historical versions if they exist
        historical_versions = ["0.9.0", "0.8.0"]
        for i, version in enumerate(historical_versions):
            release_date = current_date - timedelta(days=90 * (i + 1))
            self.versions[version] = APIVersion(
                version=version,
                status=DeprecationStatus.DEPRECATED,
                release_date=release_date,
                deprecation_date=release_date + timedelta(days=30),
                sunset_date=release_date + timedelta(days=90),
                description="Legacy version with limited support"
            )

    def add_change(self, change: APIChange) -> None:
        """Add an API change to the changelog."""
        self.changes.append(change)

    def generate_migration_guide(self, from_version: str, to_version: str) -> Dict[str, Any]:
        """Generate migration guide between versions."""
        if from_version not in self.versions or to_version not in self.versions:
            raise ValueError("Invalid version specified")
        
        # Get changes between versions
        relevant_changes = [
            change for change in self.changes
            if self._is_version_between(change.version, from_version, to_version)
        ]
        
        # Separate breaking and non-breaking changes
        breaking_changes = [c for c in relevant_changes if c.breaking]
        non_breaking_changes = [c for c in relevant_changes if not c.breaking]
        
        # Generate migration steps
        migration_steps = self._generate_migration_steps(breaking_changes)
        
        return {
            'from_version': from_version,
            'to_version': to_version,
            'overview': f"Migration guide from {from_version} to {to_version}",
            'breaking_changes_count': len(breaking_changes),
            'non_breaking_changes_count': len(non_breaking_changes),
            'estimated_migration_time': self._estimate_migration_time(breaking_changes),
            'migration_steps': migration_steps,
            'breaking_changes': [
                {
                    'endpoint': change.endpoint,
                    'method': change.method,
                    'description': change.description,
                    'old_behavior': change.old_behavior,
                    'new_behavior': change.new_behavior,
                    'code_example': change.code_example
                }
                for change in breaking_changes
            ],
            'non_breaking_changes': [
                {
                    'endpoint': change.endpoint,
                    'method': change.method,
                    'description': change.description
                }
                for change in non_breaking_changes
            ],
            'testing_checklist': self._generate_testing_checklist(breaking_changes),
            'rollback_plan': self._generate_rollback_plan(from_version)
        }

    def _is_version_between(self, change_version: str, from_version: str, to_version: str) -> bool:
        """Check if a change version is between two versions."""
        # Simplified version comparison
        def version_key(v):
            return tuple(map(int, v.split('.')))
        
        return (version_key(from_version) < version_key(change_version) <= version_key(to_version))

    def _generate_migration_steps(self, breaking_changes: List[APIChange]) -> List[MigrationStep]:
        """Generate step-by-step migration instructions."""
        steps = []
        
        # Step 1: Preparation
        steps.append(MigrationStep(
            step_number=1,
            title="Preparation and Backup",
            description="""
            Before starting the migration, ensure you have:
            - A complete backup of your current implementation
            - Test environment with the new API version
            - Updated dependencies and SDKs
            - Monitoring and logging in place
            """,
            testing_instructions="""
            1. Test current implementation works with backup
            2. Verify test environment is accessible
            3. Confirm monitoring tools are configured
            """
        ))
        
        # Step 2: Update Authentication
        steps.append(MigrationStep(
            step_number=2,
            title="Update Authentication and Headers",
            description="""
            Update your authentication mechanism to work with the new API version.
            """,
            code_changes='''
# Old authentication
headers = {
    'Authorization': 'Bearer OLD_TOKEN',
    'Content-Type': 'application/json'
}

# New authentication
headers = {
    'Authorization': 'Bearer NEW_TOKEN',
    'Content-Type': 'application/json',
    'API-Version': '1.0.0'
}
            ''',
            estimated_time="30 minutes"
        ))
        
        # Step 3: Update Endpoint Calls
        for i, change in enumerate(breaking_changes):
            steps.append(MigrationStep(
                step_number=3 + i,
                title=f"Update {change.method} {change.endpoint}",
                description=change.description,
                code_changes=change.code_example,
                testing_instructions=f"""
                1. Test the updated {change.method} {change.endpoint} call
                2. Verify response format matches expectations
                3. Check error handling for new response codes
                """,
                estimated_time="15 minutes"
            ))
        
        # Step 4: Testing and Validation
        steps.append(MigrationStep(
            step_number=len(breaking_changes) + 4,
            title="Comprehensive Testing",
            description="""
            Run comprehensive tests to ensure all functionality works with the new API version.
            """,
            testing_instructions="""
            1. Run all existing test suites
            2. Test new features and endpoints
            3. Verify error handling and edge cases
            4. Load test critical endpoints
            5. Security testing for authentication changes
            """,
            estimated_time="2-4 hours"
        ))
        
        # Step 5: Deployment
        steps.append(MigrationStep(
            step_number=len(breaking_changes) + 5,
            title="Deployment and Monitoring",
            description="""
            Deploy the updated implementation and monitor for issues.
            """,
            testing_instructions="""
            1. Deploy to staging environment first
            2. Monitor error rates and response times
            3. Check logs for any issues
            4. Gradual rollout to production
            5. Monitor for 24-48 hours post-deployment
            """,
            estimated_time="1-2 hours"
        ))
        
        return steps

    def _estimate_migration_time(self, breaking_changes: List[APIChange]) -> str:
        """Estimate migration time based on breaking changes."""
        base_time = 2  # Base hours for preparation and deployment
        change_time = len(breaking_changes) * 0.5  # 30 minutes per breaking change
        
        total_hours = base_time + change_time
        
        if total_hours < 4:
            return "2-4 hours"
        elif total_hours < 8:
            return "4-8 hours"
        elif total_hours < 16:
            return "1-2 days"
        else:
            return f"{total_hours/8:.1f} days"

    def _generate_testing_checklist(self, breaking_changes: List[APIChange]) -> List[str]:
        """Generate testing checklist for migration."""
        checklist = [
            "Verify authentication still works",
            "Test all updated endpoints",
            "Check response format changes",
            "Validate error handling",
            "Test rate limiting still works",
            "Verify security headers",
            "Test VertexAI integration",
            "Check WebSocket connections",
            "Validate webhook endpoints",
            "Test file upload functionality"
        ]
        
        # Add specific tests for breaking changes
        for change in breaking_changes:
            checklist.append(f"Test {change.method} {change.endpoint} with new format")
        
        return checklist

    def _generate_rollback_plan(self, from_version: str) -> Dict[str, Any]:
        """Generate rollback plan."""
        return {
            'rollback_version': from_version,
            'rollback_triggers': [
                "Error rate increases by >50%",
                "Response time increases by >100%",
                "Critical functionality fails",
                "Security vulnerabilities detected",
                "VertexAI integration issues"
            ],
            'rollback_steps': [
                "Switch API version back to " + from_version,
                "Restore previous authentication method",
                "Revert endpoint changes",
                "Update configuration files",
                "Restart services",
                "Verify functionality",
                "Monitor for 1 hour"
            ],
            'rollback_time': "15-30 minutes"
        }

    def generate_changelog(self) -> Dict[str, Any]:
        """Generate comprehensive changelog."""
        # Group changes by version
        changes_by_version = {}
        for change in self.changes:
            if change.version not in changes_by_version:
                changes_by_version[change.version] = []
            changes_by_version[change.version].append(change)
        
        # Generate changelog structure
        changelog = {
            'current_version': self.config.current_version,
            'supported_versions': self.config.supported_versions,
            'versions': []
        }
        
        for version in sorted(changes_by_version.keys(), reverse=True):
            version_changes = changes_by_version[version]
            version_info = self.versions.get(version)
            
            # Group changes by type
            changes_by_type = {}
            for change in version_changes:
                change_type = change.change_type.value
                if change_type not in changes_by_type:
                    changes_by_type[change_type] = []
                changes_by_type[change_type].append(change)
            
            changelog['versions'].append({
                'version': version,
                'release_date': version_info.release_date.isoformat() if version_info else None,
                'status': version_info.status.value if version_info else None,
                'description': version_info.description if version_info else "",
                'changes': {
                    change_type: [
                        {
                            'endpoint': change.endpoint,
                            'method': change.method,
                            'description': change.description,
                            'breaking': change.breaking
                        }
                        for change in changes
                    ]
                    for change_type, changes in changes_by_type.items()
                },
                'breaking_changes_count': len([c for c in version_changes if c.breaking]),
                'total_changes_count': len(version_changes)
            })
        
        return changelog

    def generate_deprecation_notices(self) -> Dict[str, Any]:
        """Generate deprecation notices for all versions."""
        notices = []
        current_date = datetime.now()
        
        for version, version_info in self.versions.items():
            if version_info.status == DeprecationStatus.ACTIVE:
                continue
            
            notice = {
                'version': version,
                'status': version_info.status.value,
                'message': self._generate_deprecation_message(version_info, current_date),
                'action_required': self._get_deprecation_action(version_info.status),
                'timeline': self._generate_deprecation_timeline(version_info, current_date)
            }
            
            notices.append(notice)
        
        return {
            'notices': notices,
            'current_date': current_date.isoformat(),
            'deprecation_policy': {
                'deprecation_period_months': self.config.deprecation_timeline_months,
                'sunset_period_months': self.config.sunset_timeline_months,
                'support_levels': {
                    'active': 'Full support including new features and bug fixes',
                    'deprecated': 'Security updates and critical bug fixes only',
                    'sunset': 'Security updates only',
                    'removed': 'No support available'
                }
            }
        }

    def _generate_deprecation_message(self, version_info: APIVersion, current_date: datetime) -> str:
        """Generate deprecation message for a version."""
        if version_info.status == DeprecationStatus.DEPRECATED:
            days_until_sunset = (version_info.sunset_date - current_date).days if version_info.sunset_date else 0
            return f"Version {version_info.version} is deprecated and will be sunset in {days_until_sunset} days. Please upgrade to {self.config.current_version}."
        elif version_info.status == DeprecationStatus.SUNSET:
            return f"Version {version_info.version} is sunset and no longer receives updates. Please upgrade to {self.config.current_version} immediately."
        elif version_info.status == DeprecationStatus.REMOVED:
            return f"Version {version_info.version} has been removed and is no longer available. Use {self.config.current_version} instead."
        return ""

    def _get_deprecation_action(self, status: DeprecationStatus) -> str:
        """Get required action for deprecation status."""
        actions = {
            DeprecationStatus.DEPRECATED: "Plan migration to latest version",
            DeprecationStatus.SUNSET: "Migrate immediately to avoid service disruption",
            DeprecationStatus.REMOVED: "Update to latest version - this version is no longer available"
        }
        return actions.get(status, "")

    def _generate_deprecation_timeline(self, version_info: APIVersion, current_date: datetime) -> Dict[str, Any]:
        """Generate deprecation timeline."""
        timeline = {}
        
        if version_info.release_date:
            timeline['released'] = version_info.release_date.isoformat()
        
        if version_info.deprecation_date:
            timeline['deprecated'] = version_info.deprecation_date.isoformat()
            days_since_deprecation = (current_date - version_info.deprecation_date).days
            timeline['days_since_deprecation'] = days_since_deprecation
        
        if version_info.sunset_date:
            timeline['sunset'] = version_info.sunset_date.isoformat()
            days_until_sunset = (version_info.sunset_date - current_date).days
            timeline['days_until_sunset'] = days_until_sunset
        
        if version_info.removal_date:
            timeline['removed'] = version_info.removal_date.isoformat()
        
        return timeline

    def generate_version_comparison(self, version1: str, version2: str) -> Dict[str, Any]:
        """Generate comparison between two versions."""
        if version1 not in self.versions or version2 not in self.versions:
            raise ValueError("Invalid version specified")
        
        # Load OpenAPI specs for comparison
        spec1 = self._load_openapi_spec(version1)
        spec2 = self._load_openapi_spec(version2)
        
        # Compare specifications
        diff = DeepDiff(spec1, spec2, ignore_order=True)
        
        # Analyze changes
        added_endpoints = []
        removed_endpoints = []
        modified_endpoints = []
        
        if 'dictionary_item_added' in diff:
            for item in diff['dictionary_item_added']:
                if 'paths' in item:
                    added_endpoints.append(item)
        
        if 'dictionary_item_removed' in diff:
            for item in diff['dictionary_item_removed']:
                if 'paths' in item:
                    removed_endpoints.append(item)
        
        if 'values_changed' in diff:
            for item in diff['values_changed']:
                if 'paths' in item:
                    modified_endpoints.append(item)
        
        return {
            'version1': version1,
            'version2': version2,
            'comparison_date': datetime.now().isoformat(),
            'summary': {
                'added_endpoints': len(added_endpoints),
                'removed_endpoints': len(removed_endpoints),
                'modified_endpoints': len(modified_endpoints),
                'total_changes': len(added_endpoints) + len(removed_endpoints) + len(modified_endpoints)
            },
            'changes': {
                'added': added_endpoints,
                'removed': removed_endpoints,
                'modified': modified_endpoints
            },
            'compatibility': self._assess_compatibility(version1, version2),
            'migration_complexity': self._assess_migration_complexity(removed_endpoints, modified_endpoints)
        }

    def _load_openapi_spec(self, version: str) -> Dict[str, Any]:
        """Load OpenAPI specification for a version."""
        spec_path = Path(self.config.openapi_specs_dir) / f"openapi_v{version}.yaml"
        
        if spec_path.exists():
            with open(spec_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Return current spec if version-specific spec doesn't exist
            current_spec_path = Path(self.config.openapi_specs_dir) / "openapi_comprehensive.yaml"
            if current_spec_path.exists():
                with open(current_spec_path, 'r') as f:
                    return yaml.safe_load(f)
        
        return {}

    def _assess_compatibility(self, version1: str, version2: str) -> str:
        """Assess compatibility between versions."""
        v1_parts = tuple(map(int, version1.split('.')))
        v2_parts = tuple(map(int, version2.split('.')))
        
        # Major version change - breaking changes expected
        if v1_parts[0] != v2_parts[0]:
            return "breaking"
        # Minor version change - possible breaking changes
        elif v1_parts[1] != v2_parts[1]:
            return "possible_breaking"
        # Patch version change - should be compatible
        else:
            return "compatible"

    def _assess_migration_complexity(self, removed_endpoints: List, modified_endpoints: List) -> str:
        """Assess migration complexity based on changes."""
        total_changes = len(removed_endpoints) + len(modified_endpoints)
        
        if total_changes == 0:
            return "none"
        elif total_changes <= 5:
            return "low"
        elif total_changes <= 15:
            return "medium"
        else:
            return "high"

    def save_documentation(self) -> None:
        """Save all versioning documentation."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save migration guides
        if self.config.generate_migration_guides:
            migration_guide = self.generate_migration_guide("0.9.0", "1.0.0")
            migration_file = Path(self.config.output_dir) / f"migration_0.9.0_to_1.0.0_{timestamp}.json"
            with open(migration_file, 'w') as f:
                json.dump(migration_guide, f, indent=2)
            logger.info(f"Migration guide saved: {migration_file}")
        
        # Save changelog
        if self.config.generate_changelog:
            changelog = self.generate_changelog()
            changelog_file = Path(self.config.output_dir) / f"changelog_{timestamp}.json"
            with open(changelog_file, 'w') as f:
                json.dump(changelog, f, indent=2)
            logger.info(f"Changelog saved: {changelog_file}")
        
        # Save deprecation notices
        deprecation_notices = self.generate_deprecation_notices()
        deprecation_file = Path(self.config.output_dir) / f"deprecation_notices_{timestamp}.json"
        with open(deprecation_file, 'w') as f:
            json.dump(deprecation_notices, f, indent=2)
        logger.info(f"Deprecation notices saved: {deprecation_file}")
        
        # Save version comparison
        if len(self.versions) > 1:
            version_comparison = self.generate_version_comparison("0.9.0", "1.0.0")
            comparison_file = Path(self.config.output_dir) / f"version_comparison_0.9.0_to_1.0.0_{timestamp}.json"
            with open(comparison_file, 'w') as f:
                json.dump(version_comparison, f, indent=2)
            logger.info(f"Version comparison saved: {comparison_file}")


# CLI usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate versioning documentation")
    parser.add_argument("--output-dir", default="versioning_docs", help="Output directory")
    parser.add_argument("--current-version", default="1.0.0", help="Current API version")
    parser.add_argument("--supported-versions", nargs="+", default=["1.0.0"], help="Supported versions")
    parser.add_argument("--no-migration", action="store_true", help="Skip migration guides")
    parser.add_argument("--no-changelog", action="store_true", help="Skip changelog generation")
    
    args = parser.parse_args()
    
    # Create configuration
    config = VersioningConfig(
        output_dir=args.output_dir,
        current_version=args.current_version,
        supported_versions=args.supported_versions,
        generate_migration_guides=not args.no_migration,
        generate_changelog=not args.no_changelog
    )
    
    # Generate documentation
    versioning = VersioningDocumentation(config)
    
    # Add some example changes
    versioning.add_change(APIChange(
        version="1.0.0",
        change_type=ChangeType.BREAKING,
        endpoint="/auth/login",
        method="POST",
        description="Updated authentication response format",
        breaking=True,
        migration_required=True,
        old_behavior="Returns 'token' field",
        new_behavior="Returns 'access_token' and 'refresh_token' fields",
        code_example='''
# Old way
response = requests.post('/auth/login', json=credentials)
token = response.json()['token']

# New way
response = requests.post('/auth/login', json=credentials)
access_token = response.json()['data']['access_token']
refresh_token = response.json()['data']['refresh_token']
        '''
    ))
    
    versioning.add_change(APIChange(
        version="1.0.0",
        change_type=ChangeType.FEATURE,
        endpoint="/api/v1/ai/inference",
        method="POST",
        description="Added VertexAI model selection",
        breaking=False,
        migration_required=False
    ))
    
    # Save documentation
    versioning.save_documentation()
    
    print(f"Versioning documentation generated in {args.output_dir}")
    print(f"Current version: {args.current_version}")
    print(f"Supported versions: {args.supported_versions}")
