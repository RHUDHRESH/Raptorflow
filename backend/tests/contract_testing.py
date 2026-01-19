"""
Contract Test Framework with Backward Compatibility Validation

Provides API contract testing for RaptorFlow backend:
- OpenAPI specification validation
- Response schema validation
- Backward compatibility checking
- API versioning support
- Breaking change detection
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
import jsonschema
import yaml
from pydantic import BaseModel, Field
from deepdiff import DeepDiff

logger = logging.getLogger(__name__)


class ContractTestType(Enum):
    """Contract test types."""
    SCHEMA_VALIDATION = "schema_validation"
    RESPONSE_VALIDATION = "response_validation"
    BACKWARD_COMPATIBILITY = "backward_compatibility"
    VERSION_COMPARISON = "version_comparison"
    BREAKING_CHANGE_DETECTION = "breaking_change_detection"


class ChangeType(Enum):
    """Types of changes detected."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    TYPE_CHANGED = "type_changed"


@dataclass
class ContractViolation:
    """Contract violation details."""
    test_type: ContractTestType
    severity: str
    endpoint: str
    method: str
    field_path: str
    expected: Any
    actual: Any
    message: str
    change_type: Optional[ChangeType] = None


@dataclass
class ContractTestResult:
    """Contract test result."""
    test_name: str
    test_type: ContractTestType
    passed: bool
    violations: List[ContractViolation] = field(default_factory=list)
    execution_time: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


class ContractTestConfig(BaseModel):
    """Contract test configuration."""
    base_url: str = "http://localhost:8000"
    output_dir: str = "contract_results"
    openapi_spec_path: str = "docs/openapi_comprehensive.yaml"
    previous_spec_path: Optional[str] = None
    auth_token: Optional[str] = None
    strict_mode: bool = True
    generate_diff_report: bool = True


class ContractTestFramework:
    """Comprehensive contract test framework."""

    def __init__(self, config: ContractTestConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.current_spec: Dict[str, Any] = {}
        self.previous_spec: Dict[str, Any] = {}
        
        # Create output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Load OpenAPI specifications
        self._load_specifications()

    async def __aenter__(self):
        """Async context manager entry."""
        await self._setup_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _setup_session(self) -> None:
        """Setup HTTP session."""
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=50)
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'RaptorFlow-Contract-Test/1.0'
        }
        
        if self.config.auth_token:
            headers['Authorization'] = f'Bearer {self.config.auth_token}'
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=headers
        )

    def _load_specifications(self) -> None:
        """Load OpenAPI specifications."""
        try:
            # Load current specification
            with open(self.config.openapi_spec_path, 'r') as f:
                self.current_spec = yaml.safe_load(f)
            logger.info(f"Loaded current OpenAPI spec: {self.config.openapi_spec_path}")
            
            # Load previous specification if available
            if self.config.previous_spec_path and Path(self.config.previous_spec_path).exists():
                with open(self.config.previous_spec_path, 'r') as f:
                    self.previous_spec = yaml.safe_load(f)
                logger.info(f"Loaded previous OpenAPI spec: {self.config.previous_spec_path}")
            else:
                logger.info("No previous specification found, skipping compatibility tests")
                
        except Exception as e:
            logger.error(f"Failed to load specifications: {e}")
            raise

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
        """Make HTTP request."""
        url = f"{self.config.base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                response_data = await response.json()
                return response.status, response_data, dict(response.headers)
        except Exception as e:
            return 0, {"error": str(e)}, {}

    def _validate_response_schema(
        self,
        response_data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> List[ContractViolation]:
        """Validate response against OpenAPI schema."""
        violations = []
        
        try:
            jsonschema.validate(response_data, schema)
        except jsonschema.ValidationError as e:
            violations.append(ContractViolation(
                test_type=ContractTestType.SCHEMA_VALIDATION,
                severity="error",
                endpoint="",
                method="",
                field_path=e.absolute_path,
                expected=schema,
                actual=response_data,
                message=str(e)
            ))
        except Exception as e:
            violations.append(ContractViolation(
                test_type=ContractTestType.SCHEMA_VALIDATION,
                severity="error",
                endpoint="",
                method="",
                field_path="",
                expected=schema,
                actual=response_data,
                message=f"Schema validation error: {str(e)}"
            ))
        
        return violations

    def _detect_schema_changes(
        self,
        current_schema: Dict[str, Any],
        previous_schema: Dict[str, Any],
        path: str = ""
    ) -> List[ContractViolation]:
        """Detect changes between schemas."""
        violations = []
        
        diff = DeepDiff(previous_schema, current_schema, ignore_order=True)
        
        # Handle added fields
        if 'dictionary_item_added' in diff:
            for item in diff['dictionary_item_added']:
                violations.append(ContractViolation(
                    test_type=ContractTestType.BREAKING_CHANGE_DETECTION,
                    severity="warning",
                    endpoint="",
                    method="",
                    field_path=f"{path}{item}",
                    expected=None,
                    actual="added",
                    message=f"Field added: {item}",
                    change_type=ChangeType.ADDED
                ))
        
        # Handle removed fields
        if 'dictionary_item_removed' in diff:
            for item in diff['dictionary_item_removed']:
                violations.append(ContractViolation(
                    test_type=ContractTestType.BREAKING_CHANGE_DETECTION,
                    severity="error",
                    endpoint="",
                    method="",
                    field_path=f"{path}{item}",
                    expected="present",
                    actual="removed",
                    message=f"Field removed: {item} (BREAKING CHANGE)",
                    change_type=ChangeType.REMOVED
                ))
        
        # Handle changed values
        if 'values_changed' in diff:
            for item in diff['values_changed']:
                violations.append(ContractViolation(
                    test_type=ContractTestType.BREAKING_CHANGE_DETECTION,
                    severity="warning",
                    endpoint="",
                    method="",
                    field_path=f"{path}{item}",
                    expected=item['old_value'],
                    actual=item['new_value'],
                    message=f"Field changed: {item}",
                    change_type=ChangeType.MODIFIED
                ))
        
        # Handle type changes
        if 'type_changes' in diff:
            for item in diff['type_changes']:
                violations.append(ContractViolation(
                    test_type=ContractTestType.BREAKING_CHANGE_DETECTION,
                    severity="error",
                    endpoint="",
                    method="",
                    field_path=f"{path}{item}",
                    expected=item['old_type'],
                    actual=item['new_type'],
                    message=f"Type changed: {item} (BREAKING CHANGE)",
                    change_type=ChangeType.TYPE_CHANGED
                ))
        
        return violations

    async def test_openapi_spec_validation(self) -> ContractTestResult:
        """Test OpenAPI specification validation."""
        logger.info("Testing OpenAPI specification validation")
        start_time = time.time()
        
        violations = []
        
        # Check required OpenAPI fields
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in self.current_spec:
                violations.append(ContractViolation(
                    test_type=ContractTestType.SCHEMA_VALIDATION,
                    severity="error",
                    endpoint="spec",
                    method="validation",
                    field_path=field,
                    expected="present",
                    actual="missing",
                    message=f"Required OpenAPI field missing: {field}"
                ))
        
        # Check info section
        if 'info' in self.current_spec:
            info_required = ['title', 'version']
            for field in info_required:
                if field not in self.current_spec['info']:
                    violations.append(ContractViolation(
                        test_type=ContractTestType.SCHEMA_VALIDATION,
                        severity="error",
                        endpoint="spec.info",
                        method="validation",
                        field_path=field,
                        expected="present",
                        actual="missing",
                        message=f"Required info field missing: {field}"
                    ))
        
        # Validate paths
        if 'paths' in self.current_spec:
            for path, methods in self.current_spec['paths'].items():
                for method, details in methods.items():
                    # Check for required fields in each endpoint
                    if 'summary' not in details:
                        violations.append(ContractViolation(
                            test_type=ContractTestType.SCHEMA_VALIDATION,
                            severity="warning",
                            endpoint=path,
                            method=method.upper(),
                            field_path="summary",
                            expected="present",
                            actual="missing",
                            message=f"Missing summary for {method.upper()} {path}"
                        ))
                    
                    # Check responses
                    if 'responses' not in details:
                        violations.append(ContractViolation(
                            test_type=ContractTestType.SCHEMA_VALIDATION,
                            severity="error",
                            endpoint=path,
                            method=method.upper(),
                            field_path="responses",
                            expected="present",
                            actual="missing",
                            message=f"Missing responses for {method.upper()} {path}"
                        ))
        
        return ContractTestResult(
            test_name="OpenAPI Specification Validation",
            test_type=ContractTestType.SCHEMA_VALIDATION,
            passed=len(violations) == 0,
            violations=violations,
            execution_time=time.time() - start_time
        )

    async def test_response_schema_validation(self) -> ContractTestResult:
        """Test response schema validation."""
        logger.info("Testing response schema validation")
        start_time = time.time()
        
        violations = []
        
        if 'paths' not in self.current_spec:
            return ContractTestResult(
                test_name="Response Schema Validation",
                test_type=ContractTestType.RESPONSE_VALIDATION,
                passed=False,
                violations=[ContractViolation(
                    test_type=ContractTestType.RESPONSE_VALIDATION,
                    severity="error",
                    endpoint="",
                    method="",
                    field_path="paths",
                    expected="present",
                    actual="missing",
                    message="No paths found in OpenAPI spec"
                )],
                execution_time=time.time() - start_time
            )
        
        # Test each endpoint
        for path, methods in self.current_spec['paths'].items():
            for method, details in methods.items():
                if 'responses' not in details:
                    continue
                
                # Test successful response
                for status_code, response_details in details['responses'].items():
                    if status_code.startswith('2') and 'content' in response_details:
                        if 'application/json' in response_details['content']:
                            schema = response_details['content']['application/json'].get('schema')
                            if schema:
                                # Make request to validate response
                                status, response_data, headers = await self._make_request(method.upper(), path)
                                
                                if status == int(status_code):
                                    schema_violations = self._validate_response_schema(response_data, schema)
                                    for violation in schema_violations:
                                        violation.endpoint = path
                                        violation.method = method.upper()
                                    violations.extend(schema_violations)
        
        return ContractTestResult(
            test_name="Response Schema Validation",
            test_type=ContractTestType.RESPONSE_VALIDATION,
            passed=len(violations) == 0,
            violations=violations,
            execution_time=time.time() - start_time
        )

    async def test_backward_compatibility(self) -> ContractTestResult:
        """Test backward compatibility."""
        logger.info("Testing backward compatibility")
        start_time = time.time()
        
        violations = []
        
        if not self.previous_spec:
            return ContractTestResult(
                test_name="Backward Compatibility",
                test_type=ContractTestType.BACKWARD_COMPATIBILITY,
                passed=True,
                violations=[],
                execution_time=time.time() - start_time,
                details={"message": "No previous specification to compare"}
            )
        
        # Compare paths
        current_paths = set(self.current_spec.get('paths', {}).keys())
        previous_paths = set(self.previous_spec.get('paths', {}).keys())
        
        # Check for removed endpoints
        removed_paths = previous_paths - current_paths
        for path in removed_paths:
            violations.append(ContractViolation(
                test_type=ContractTestType.BREAKING_CHANGE_DETECTION,
                severity="error",
                endpoint=path,
                method="*",
                field_path="",
                expected="present",
                actual="removed",
                message=f"Endpoint removed: {path} (BREAKING CHANGE)",
                change_type=ChangeType.REMOVED
            ))
        
        # Check for modified endpoints
        common_paths = current_paths & previous_paths
        for path in common_paths:
            current_methods = set(self.current_spec['paths'][path].keys())
            previous_methods = set(self.previous_spec['paths'][path].keys())
            
            # Check for removed methods
            removed_methods = previous_methods - current_methods
            for method in removed_methods:
                violations.append(ContractViolation(
                    test_type=ContractTestType.BREAKING_CHANGE_DETECTION,
                    severity="error",
                    endpoint=path,
                    method=method.upper(),
                    field_path="",
                    expected="present",
                    actual="removed",
                    message=f"Method removed: {method.upper()} {path} (BREAKING CHANGE)",
                    change_type=ChangeType.REMOVED
                ))
            
            # Check for schema changes in common methods
            common_methods = current_methods & previous_methods
            for method in common_methods:
                current_details = self.current_spec['paths'][path][method]
                previous_details = self.previous_spec['paths'][path][method]
                
                # Compare response schemas
                current_responses = current_details.get('responses', {})
                previous_responses = previous_details.get('responses', {})
                
                for status_code in current_responses:
                    if status_code in previous_responses:
                        current_schema = current_responses[status_code].get('content', {}).get('application/json', {}).get('schema')
                        previous_schema = previous_responses[status_code].get('content', {}).get('application/json', {}).get('schema')
                        
                        if current_schema and previous_schema:
                            schema_violations = self._detect_schema_changes(
                                current_schema, 
                                previous_schema, 
                                f"{path}.{method}.{status_code}"
                            )
                            for violation in schema_violations:
                                violation.endpoint = path
                                violation.method = method.upper()
                            violations.extend(schema_violations)
        
        return ContractTestResult(
            test_name="Backward Compatibility",
            test_type=ContractTestType.BACKWARD_COMPATIBILITY,
            passed=len([v for v in violations if v.severity == "error"]) == 0,
            violations=violations,
            execution_time=time.time() - start_time
        )

    async def test_version_comparison(self) -> ContractTestResult:
        """Test API versioning."""
        logger.info("Testing API versioning")
        start_time = time.time()
        
        violations = []
        
        # Check for version in info
        if 'info' not in self.current_spec or 'version' not in self.current_spec['info']:
            violations.append(ContractViolation(
                test_type=ContractTestType.VERSION_COMPARISON,
                severity="warning",
                endpoint="spec",
                method="validation",
                field_path="info.version",
                expected="present",
                actual="missing",
                message="API version not specified in OpenAPI spec"
            ))
        
        # Check for version in paths
        versioned_paths = []
        for path in self.current_spec.get('paths', {}):
            if any(path.startswith(f"/v{i}/") for i in range(1, 10)):
                versioned_paths.append(path)
        
        if not versioned_paths:
            violations.append(ContractViolation(
                test_type=ContractTestType.VERSION_COMPARISON,
                severity="info",
                endpoint="paths",
                method="validation",
                field_path="",
                expected="versioned",
                actual="unversioned",
                message="No versioned paths found in API"
            ))
        
        # Check for deprecated endpoints
        deprecated_endpoints = []
        for path, methods in self.current_spec.get('paths', {}).items():
            for method, details in methods.items():
                if details.get('deprecated', False):
                    deprecated_endpoints.append(f"{method.upper()} {path}")
        
        details = {
            "deprecated_endpoints": deprecated_endpoints,
            "versioned_paths": versioned_paths
        }
        
        return ContractTestResult(
            test_name="API Versioning",
            test_type=ContractTestType.VERSION_COMPARISON,
            passed=len(violations) == 0,
            violations=violations,
            execution_time=time.time() - start_time,
            details=details
        )

    async def run_contract_tests(self) -> List[ContractTestResult]:
        """Run all contract tests."""
        logger.info("Starting comprehensive contract testing")
        
        tests = [
            self.test_openapi_spec_validation(),
            self.test_response_schema_validation(),
            self.test_backward_compatibility(),
            self.test_version_comparison()
        ]
        
        results = await asyncio.gather(*tests)
        
        logger.info(f"Contract testing completed: {len(results)} tests executed")
        return results

    def generate_contract_report(self, results: List[ContractTestResult]) -> Dict[str, Any]:
        """Generate comprehensive contract test report."""
        all_violations = []
        for result in results:
            all_violations.extend(result.violations)
        
        # Count by severity
        severity_counts = {}
        for violation in all_violations:
            severity = violation.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count by test type
        type_counts = {}
        for result in results:
            test_type = result.test_type.value
            type_counts[test_type] = {
                'violations': len(result.violations),
                'passed': result.passed
            }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': len(results),
                'tests_passed': sum(1 for r in results if r.passed),
                'tests_failed': sum(1 for r in results if not r.passed),
                'total_violations': len(all_violations),
                'error_violations': severity_counts.get('error', 0),
                'warning_violations': severity_counts.get('warning', 0),
                'info_violations': severity_counts.get('info', 0)
            },
            'test_results': [
                {
                    'test_name': result.test_name,
                    'test_type': result.test_type.value,
                    'passed': result.passed,
                    'execution_time': result.execution_time,
                    'violations_found': len(result.violations),
                    'details': result.details
                }
                for result in results
            ],
            'violations': [
                {
                    'test_type': violation.test_type.value,
                    'severity': violation.severity,
                    'endpoint': violation.endpoint,
                    'method': violation.method,
                    'field_path': violation.field_path,
                    'expected': violation.expected,
                    'actual': violation.actual,
                    'message': violation.message,
                    'change_type': violation.change_type.value if violation.change_type else None
                }
                for violation in all_violations
            ],
            'type_breakdown': type_counts
        }

    def save_report(self, results: List[ContractTestResult]) -> None:
        """Save contract test report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate report
        report_data = self.generate_contract_report(results)
        
        # Save JSON report
        json_file = Path(self.config.output_dir) / f"contract_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Contract test report saved: {json_file}")
        
        # Generate diff report if enabled
        if self.config.generate_diff_report and self.previous_spec:
            diff_file = Path(self.config.output_dir) / f"spec_diff_{timestamp}.json"
            diff_data = DeepDiff(self.previous_spec, self.current_spec, ignore_order=True)
            with open(diff_file, 'w') as f:
                json.dump(diff_data.to_dict(), f, indent=2)
            logger.info(f"Specification diff saved: {diff_file}")
        
        # Print summary
        summary = report_data['summary']
        print(f"\nContract Testing Summary:")
        print(f"Tests Passed: {summary['tests_passed']}/{summary['total_tests']}")
        print(f"Total Violations: {summary['total_violations']}")
        print(f"Errors: {summary['error_violations']}")
        print(f"Warnings: {summary['warning_violations']}")
        print(f"Info: {summary['info_violations']}")


# CLI usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run contract tests")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base API URL")
    parser.add_argument("--openapi-spec", default="docs/openapi_comprehensive.yaml", help="OpenAPI spec path")
    parser.add_argument("--previous-spec", help="Previous OpenAPI spec for comparison")
    parser.add_argument("--auth-token", help="Authentication token")
    parser.add_argument("--output-dir", default="contract_results", help="Output directory")
    parser.add_argument("--no-diff", action="store_true", help="Disable diff report generation")
    
    args = parser.parse_args()
    
    # Create configuration
    config = ContractTestConfig(
        base_url=args.base_url,
        openapi_spec_path=args.openapi_spec,
        previous_spec_path=args.previous_spec,
        auth_token=args.auth_token,
        output_dir=args.output_dir,
        generate_diff_report=not args.no_diff
    )
    
    # Run contract tests
    async def main():
        async with ContractTestFramework(config) as framework:
            results = await framework.run_contract_tests()
            framework.save_report(results)
    
    asyncio.run(main())
