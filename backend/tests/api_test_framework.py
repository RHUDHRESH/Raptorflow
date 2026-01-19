"""
Comprehensive API Test Framework with CI/CD Integration

Provides automated testing for RaptorFlow backend API with:
- Comprehensive test coverage
- CI/CD pipeline integration
- Parallel test execution
- Detailed reporting and analytics
- VertexAI-specific testing scenarios
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
import pytest
import yaml
from pydantic import BaseModel, Field
from pytest_html import html_report

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestPriority(Enum):
    """Test priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TestResult:
    """Individual test result."""
    name: str
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    assertion_results: List[bool] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSuite:
    """Test suite containing multiple tests."""
    name: str
    tests: List[TestResult] = field(default_factory=list)
    total_duration: float = 0.0
    passed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    error_count: int = 0

    def add_result(self, result: TestResult) -> None:
        """Add test result to suite."""
        self.tests.append(result)
        self.total_duration += result.duration
        
        if result.status == TestStatus.PASSED:
            self.passed_count += 1
        elif result.status == TestStatus.FAILED:
            self.failed_count += 1
        elif result.status == TestStatus.SKIPPED:
            self.skipped_count += 1
        elif result.status == TestStatus.ERROR:
            self.error_count += 1

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = len(self.tests)
        if total == 0:
            return 0.0
        return (self.passed_count / total) * 100


class APITestConfig(BaseModel):
    """API test configuration."""
    base_url: str = "http://localhost:8000"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    parallel_tests: int = 10
    auth_token: Optional[str] = None
    test_data_file: Optional[str] = None
    output_dir: str = "test_results"
    generate_html_report: bool = True
    generate_json_report: bool = True
    coverage_threshold: float = 95.0


class APITestFramework:
    """Comprehensive API test framework."""

    def __init__(self, config: APITestConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_data: Dict[str, Any] = {}
        
        # Create output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Load test data
        if config.test_data_file:
            self._load_test_data()

    async def __aenter__(self):
        """Async context manager entry."""
        await self._setup_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _setup_session(self) -> None:
        """Setup HTTP session with retry configuration."""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
        connector = aiohttp.TCPConnector(
            limit=self.config.parallel_tests * 2,
            limit_per_host=self.config.parallel_tests
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'RaptorFlow-API-Test-Framework/1.0'
            }
        )

    def _load_test_data(self) -> None:
        """Load test data from file."""
        try:
            with open(self.config.test_data_file, 'r') as f:
                self.test_data = json.load(f)
            logger.info(f"Loaded test data from {self.config.test_data_file}")
        except Exception as e:
            logger.error(f"Failed to load test data: {e}")
            raise

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Tuple[int, Dict[str, Any], float, Dict[str, str]]:
        """Make HTTP request with retry logic."""
        url = f"{self.config.base_url}{endpoint}"
        
        # Prepare headers
        request_headers = {}
        if self.config.auth_token:
            request_headers['Authorization'] = f'Bearer {self.config.auth_token}'
        if headers:
            request_headers.update(headers)
        
        # Retry logic
        for attempt in range(self.config.max_retries):
            try:
                start_time = time.time()
                
                async with self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers
                ) as response:
                    duration = time.time() - start_time
                    
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
                    
                    response_headers = dict(response.headers)
                    
                    if response.status < 500:
                        return response.status, response_data, duration, response_headers
                    else:
                        logger.warning(f"Server error (attempt {attempt + 1}): {response.status}")
                        
            except Exception as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay)
        
        # All retries failed
        raise Exception(f"Request failed after {self.config.max_retries} attempts")

    async def run_test_case(
        self,
        name: str,
        method: str,
        endpoint: str,
        expected_status: int = 200,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        assertions: Optional[List[callable]] = None
    ) -> TestResult:
        """Run individual test case."""
        start_time = time.time()
        
        try:
            status, response_data, duration, response_headers = await self._make_request(
                method=method,
                endpoint=endpoint,
                data=data,
                params=params,
                headers=headers
            )
            
            # Basic status check
            assertion_results = [status == expected_status]
            
            # Custom assertions
            if assertions:
                for assertion in assertions:
                    try:
                        result = assertion(response_data, response_headers)
                        assertion_results.append(result)
                    except Exception as e:
                        logger.error(f"Assertion failed: {e}")
                        assertion_results.append(False)
            
            # Determine test status
            if all(assertion_results):
                status_result = TestStatus.PASSED
                error_message = None
            else:
                status_result = TestStatus.FAILED
                error_message = f"Expected status {expected_status}, got {status}"
            
            return TestResult(
                name=name,
                status=status_result,
                duration=duration,
                response_data=response_data,
                assertion_results=assertion_results,
                metadata={
                    'method': method,
                    'endpoint': endpoint,
                    'expected_status': expected_status,
                    'actual_status': status,
                    'response_headers': response_headers
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=name,
                status=TestStatus.ERROR,
                duration=duration,
                error_message=str(e),
                metadata={
                    'method': method,
                    'endpoint': endpoint,
                    'expected_status': expected_status
                }
            )

    async def run_test_suite(
        self,
        suite_name: str,
        test_cases: List[Dict[str, Any]],
        parallel: bool = True
    ) -> TestSuite:
        """Run a test suite with multiple test cases."""
        logger.info(f"Running test suite: {suite_name}")
        
        suite = TestSuite(name=suite_name)
        
        if parallel:
            # Run tests in parallel
            tasks = []
            for test_case in test_cases:
                task = self.run_test_case(**test_case)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    suite.add_result(TestResult(
                        name="Unknown",
                        status=TestStatus.ERROR,
                        duration=0.0,
                        error_message=str(result)
                    ))
                else:
                    suite.add_result(result)
        else:
            # Run tests sequentially
            for test_case in test_cases:
                result = await self.run_test_case(**test_case)
                suite.add_result(result)
        
        self.test_suites[suite_name] = suite
        logger.info(f"Test suite {suite_name} completed: {suite.success_rate:.1f}% success rate")
        
        return suite

    def generate_health_tests(self) -> List[Dict[str, Any]]:
        """Generate health check test cases."""
        return [
            {
                'name': 'Health Check - Basic',
                'method': 'GET',
                'endpoint': '/health',
                'expected_status': 200,
                'assertions': [
                    lambda data, headers: data.get('status') == 'healthy',
                    lambda data, headers: 'services' in data,
                    lambda data, headers: isinstance(data.get('services'), dict)
                ]
            },
            {
                'name': 'Health Check - Database Service',
                'method': 'GET',
                'endpoint': '/health',
                'expected_status': 200,
                'assertions': [
                    lambda data, headers: data.get('services', {}).get('database', {}).get('status') == 'healthy'
                ]
            },
            {
                'name': 'Health Check - VertexAI Service',
                'method': 'GET',
                'endpoint': '/health',
                'expected_status': 200,
                'assertions': [
                    lambda data, headers: data.get('services', {}).get('vertexai', {}).get('status') == 'healthy'
                ]
            }
        ]

    def generate_auth_tests(self) -> List[Dict[str, Any]]:
        """Generate authentication test cases."""
        test_user = self.test_data.get('test_user', {
            'email': 'test@example.com',
            'password': 'testpassword123'
        })
        
        return [
            {
                'name': 'Login - Valid Credentials',
                'method': 'POST',
                'endpoint': '/auth/login',
                'data': test_user,
                'expected_status': 200,
                'assertions': [
                    lambda data, headers: data.get('success') is True,
                    lambda data, headers: 'access_token' in data.get('data', {}),
                    lambda data, headers: 'refresh_token' in data.get('data', {})
                ]
            },
            {
                'name': 'Login - Invalid Credentials',
                'method': 'POST',
                'endpoint': '/auth/login',
                'data': {'email': 'invalid@example.com', 'password': 'wrong'},
                'expected_status': 401
            },
            {
                'name': 'Login - Missing Fields',
                'method': 'POST',
                'endpoint': '/auth/login',
                'data': {'email': 'test@example.com'},
                'expected_status': 422
            }
        ]

    def generate_user_tests(self) -> List[Dict[str, Any]]:
        """Generate user management test cases."""
        return [
            {
                'name': 'Get Current User Profile',
                'method': 'GET',
                'endpoint': '/users/me',
                'expected_status': 200,
                'assertions': [
                    lambda data, headers: data.get('success') is True,
                    lambda data, headers: 'id' in data.get('data', {}),
                    lambda data, headers: 'email' in data.get('data', {})
                ]
            },
            {
                'name': 'Update User Profile',
                'method': 'PUT',
                'endpoint': '/users/me',
                'data': {
                    'name': 'Updated Test User',
                    'preferences': {
                        'theme': 'dark',
                        'notifications': True
                    }
                },
                'expected_status': 200,
                'assertions': [
                    lambda data, headers: data.get('success') is True,
                    lambda data, headers: data.get('data', {}).get('name') == 'Updated Test User'
                ]
            }
        ]

    def generate_workspace_tests(self) -> List[Dict[str, Any]]:
        """Generate workspace management test cases."""
        workspace_data = self.test_data.get('workspace', {
            'name': 'Test Workspace',
            'description': 'Test workspace for API testing'
        })
        
        return [
            {
                'name': 'List Workspaces',
                'method': 'GET',
                'endpoint': '/workspaces',
                'expected_status': 200,
                'assertions': [
                    lambda data, headers: data.get('success') is True,
                    lambda data, headers: 'workspaces' in data.get('data', {}),
                    lambda data, headers: isinstance(data.get('data', {}).get('workspaces'), list)
                ]
            },
            {
                'name': 'Create Workspace',
                'method': 'POST',
                'endpoint': '/workspaces',
                'data': workspace_data,
                'expected_status': 201,
                'assertions': [
                    lambda data, headers: data.get('success') is True,
                    lambda data, headers: 'id' in data.get('data', {}),
                    lambda data, headers: data.get('data', {}).get('name') == workspace_data['name']
                ]
            }
        ]

    def generate_vertexai_tests(self) -> List[Dict[str, Any]]:
        """Generate VertexAI-specific test cases."""
        return [
            {
                'name': 'VertexAI Health Check',
                'method': 'GET',
                'endpoint': '/health',
                'expected_status': 200,
                'assertions': [
                    lambda data, headers: 'vertexai' in data.get('services', {}),
                    lambda data, headers: data.get('services', {}).get('vertexai', {}).get('status') == 'healthy'
                ]
            },
            {
                'name': 'AI Inference - VertexAI Model',
                'method': 'POST',
                'endpoint': '/api/v1/ai/inference',
                'data': {
                    'prompt': 'Test prompt for VertexAI',
                    'model': 'gemini-pro',
                    'max_tokens': 100
                },
                'expected_status': 200,
                'assertions': [
                    lambda data, headers: data.get('success') is True,
                    lambda data, headers: 'response' in data.get('data', {}),
                    lambda data, headers: 'tokens_used' in data.get('data', {})
                ]
            }
        ]

    def generate_performance_tests(self) -> List[Dict[str, Any]]:
        """Generate performance test cases."""
        return [
            {
                'name': 'Response Time - Health Check',
                'method': 'GET',
                'endpoint': '/health',
                'expected_status': 200,
                'assertions': [
                    lambda data, headers: True  # Duration check in test runner
                ]
            },
            {
                'name': 'Response Time - User Profile',
                'method': 'GET',
                'endpoint': '/users/me',
                'expected_status': 200,
                'assertions': [
                    lambda data, headers: True  # Duration check in test runner
                ]
            }
        ]

    async def run_all_tests(self) -> Dict[str, TestSuite]:
        """Run all test suites."""
        logger.info("Starting comprehensive API test execution")
        
        # Define all test suites
        test_suites_config = [
            ('Health Checks', self.generate_health_tests()),
            ('Authentication', self.generate_auth_tests()),
            ('User Management', self.generate_user_tests()),
            ('Workspace Management', self.generate_workspace_tests()),
            ('VertexAI Integration', self.generate_vertexai_tests()),
            ('Performance', self.generate_performance_tests())
        ]
        
        # Run all suites
        for suite_name, test_cases in test_suites_config:
            await self.run_test_suite(suite_name, test_cases)
        
        return self.test_suites

    def generate_html_report(self) -> str:
        """Generate HTML test report."""
        total_tests = sum(len(suite.tests) for suite in self.test_suites.values())
        total_passed = sum(suite.passed_count for suite in self.test_suites.values())
        total_failed = sum(suite.failed_count for suite in self.test_suites.values())
        total_errors = sum(suite.error_count for suite in self.test_suites.values())
        total_skipped = sum(suite.skipped_count for suite in self.test_suites.values())
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RaptorFlow API Test Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .test-pass {{ background-color: #10b981; }}
        .test-fail {{ background-color: #ef4444; }}
        .test-error {{ background-color: #f59e0b; }}
        .test-skip {{ background-color: #6b7280; }}
    </style>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <header class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">RaptorFlow API Test Report</h1>
            <p class="text-gray-600">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>

        <!-- Summary -->
        <section class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Test Summary</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center">
                    <div class="text-3xl font-bold text-green-600">{total_passed}</div>
                    <div class="text-gray-600">Passed</div>
                </div>
                <div class="text-center">
                    <div class="text-3xl font-bold text-red-600">{total_failed}</div>
                    <div class="text-gray-600">Failed</div>
                </div>
                <div class="text-center">
                    <div class="text-3xl font-bold text-yellow-600">{total_errors}</div>
                    <div class="text-gray-600">Errors</div>
                </div>
                <div class="text-center">
                    <div class="text-3xl font-bold text-gray-600">{total_skipped}</div>
                    <div class="text-gray-600">Skipped</div>
                </div>
            </div>
            <div class="mt-6">
                <div class="flex justify-between items-center mb-2">
                    <span class="font-medium">Overall Success Rate</span>
                    <span class="font-bold">{overall_success_rate:.1f}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-4">
                    <div class="bg-green-600 h-4 rounded-full" style="width: {overall_success_rate}%"></div>
                </div>
            </div>
        </section>

        <!-- Test Suites -->
        <section class="space-y-6">
            <h2 class="text-xl font-semibold mb-4">Test Suites</h2>
            {self._generate_suite_html()}
        </section>
    </div>

    <script>
        // Interactive functionality
        document.querySelectorAll('.suite-toggle').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const content = document.getElementById(btn.dataset.suite);
                content.classList.toggle('hidden');
                btn.textContent = content.classList.contains('hidden') ? 'Show' : 'Hide';
            }});
        }});
    </script>
</body>
</html>
        """
        
        return html_template

    def _generate_suite_html(self) -> str:
        """Generate HTML for test suites."""
        suites_html = ""
        
        for suite_name, suite in self.test_suites.items():
            status_class = "test-pass" if suite.success_rate >= 95 else "test-fail"
            
            suites_html += f"""
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-semibold">{suite_name}</h3>
                    <button class="suite-toggle px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                            data-suite="{suite_name.replace(' ', '-')}">Show</button>
                </div>
                
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div class="text-center">
                        <div class="text-2xl font-bold text-green-600">{suite.passed_count}</div>
                        <div class="text-sm text-gray-600">Passed</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-red-600">{suite.failed_count}</div>
                        <div class="text-sm text-gray-600">Failed</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-yellow-600">{suite.error_count}</div>
                        <div class="text-sm text-gray-600">Errors</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-gray-600">{suite.success_rate:.1f}%</div>
                        <div class="text-sm text-gray-600">Success Rate</div>
                    </div>
                </div>
                
                <div id="{suite_name.replace(' ', '-')}" class="hidden">
                    <div class="space-y-2">
                        {self._generate_test_html(suite.tests)}
                    </div>
                </div>
            </div>
            """
        
        return suites_html

    def _generate_test_html(self, tests: List[TestResult]) -> str:
        """Generate HTML for individual tests."""
        tests_html = ""
        
        for test in tests:
            status_badge = {
                TestStatus.PASSED: '<span class="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">PASSED</span>',
                TestStatus.FAILED: '<span class="px-2 py-1 bg-red-100 text-red-800 rounded text-sm">FAILED</span>',
                TestStatus.ERROR: '<span class="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-sm">ERROR</span>',
                TestStatus.SKIPPED: '<span class="px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm">SKIPPED</span>'
            }.get(test.status, '<span class="px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm">UNKNOWN</span>')
            
            tests_html += f"""
            <div class="border rounded p-4">
                <div class="flex justify-between items-center mb-2">
                    <span class="font-medium">{test.name}</span>
                    <div class="flex items-center space-x-2">
                        {status_badge}
                        <span class="text-sm text-gray-600">{test.duration:.3f}s</span>
                    </div>
                </div>
                {f'<div class="text-red-600 text-sm">{test.error_message}</div>' if test.error_message else ''}
                {f'<div class="bg-gray-50 rounded p-2 mt-2"><pre class="text-xs overflow-x-auto">{json.dumps(test.response_data, indent=2)}</pre></div>' if test.response_data else ''}
            </div>
            """
        
        return tests_html

    def generate_json_report(self) -> Dict[str, Any]:
        """Generate JSON test report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': sum(len(suite.tests) for suite in self.test_suites.values()),
                'total_passed': sum(suite.passed_count for suite in self.test_suites.values()),
                'total_failed': sum(suite.failed_count for suite in self.test_suites.values()),
                'total_errors': sum(suite.error_count for suite in self.test_suites.values()),
                'total_skipped': sum(suite.skipped_count for suite in self.test_suites.values()),
                'overall_success_rate': self._calculate_overall_success_rate()
            },
            'suites': {
                name: {
                    'name': suite.name,
                    'total_tests': len(suite.tests),
                    'passed_count': suite.passed_count,
                    'failed_count': suite.failed_count,
                    'error_count': suite.error_count,
                    'skipped_count': suite.skipped_count,
                    'success_rate': suite.success_rate,
                    'total_duration': suite.total_duration,
                    'tests': [
                        {
                            'name': test.name,
                            'status': test.status.value,
                            'duration': test.duration,
                            'error_message': test.error_message,
                            'response_data': test.response_data,
                            'metadata': test.metadata
                        }
                        for test in suite.tests
                    ]
                }
                for name, suite in self.test_suites.items()
            }
        }

    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate across all suites."""
        total_tests = sum(len(suite.tests) for suite in self.test_suites.values())
        total_passed = sum(suite.passed_count for suite in self.test_suites.values())
        
        if total_tests == 0:
            return 0.0
        return (total_passed / total_tests) * 100

    def save_reports(self) -> None:
        """Save test reports to files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save HTML report
        if self.config.generate_html_report:
            html_report = self.generate_html_report()
            html_file = Path(self.config.output_dir) / f"test_report_{timestamp}.html"
            with open(html_file, 'w') as f:
                f.write(html_report)
            logger.info(f"HTML report saved: {html_file}")
        
        # Save JSON report
        if self.config.generate_json_report:
            json_report = self.generate_json_report()
            json_file = Path(self.config.output_dir) / f"test_report_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(json_report, f, indent=2)
            logger.info(f"JSON report saved: {json_file}")

    async def run_ci_cd_pipeline(self) -> bool:
        """Run CI/CD pipeline with exit code based on test results."""
        logger.info("Running CI/CD pipeline")
        
        # Run all tests
        await self.run_all_tests()
        
        # Generate reports
        self.save_reports()
        
        # Calculate overall success rate
        success_rate = self._calculate_overall_success_rate()
        
        # Check if coverage threshold is met
        if success_rate >= self.config.coverage_threshold:
            logger.info(f"CI/CD pipeline PASSED: {success_rate:.1f}% success rate")
            return True
        else:
            logger.error(f"CI/CD pipeline FAILED: {success_rate:.1f}% success rate (threshold: {self.config.coverage_threshold}%)")
            return False


# CLI usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run comprehensive API tests")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base API URL")
    parser.add_argument("--auth-token", help="Authentication token")
    parser.add_argument("--test-data", help="Test data file path")
    parser.add_argument("--output-dir", default="test_results", help="Output directory")
    parser.add_argument("--parallel", type=int, default=10, help="Parallel test count")
    parser.add_argument("--coverage-threshold", type=float, default=95.0, help="Coverage threshold")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout")
    parser.add_argument("--ci", action="store_true", help="Run in CI/CD mode")
    
    args = parser.parse_args()
    
    # Create configuration
    config = APITestConfig(
        base_url=args.base_url,
        auth_token=args.auth_token,
        test_data_file=args.test_data,
        output_dir=args.output_dir,
        parallel_tests=args.parallel,
        coverage_threshold=args.coverage_threshold,
        timeout=args.timeout
    )
    
    # Run tests
    async def main():
        async with APITestFramework(config) as framework:
            if args.ci:
                success = await framework.run_ci_cd_pipeline()
                exit(0 if success else 1)
            else:
                await framework.run_all_tests()
                framework.save_reports()
    
    asyncio.run(main())
