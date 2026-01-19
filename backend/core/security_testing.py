"""
Security Testing Framework and Penetration Testing Tools
Provides comprehensive security testing, vulnerability scanning, and penetration testing capabilities.
"""

import asyncio
import aiohttp
import json
import logging
import re
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from collections import defaultdict
import hashlib
import base64

logger = logging.getLogger(__name__)


class TestType(Enum):
    """Types of security tests."""
    VULNERABILITY_SCAN = "vulnerability_scan"
    PENETRATION_TEST = "penetration_test"
    AUTHENTICATION_TEST = "authentication_test"
    AUTHORIZATION_TEST = "authorization_test"
    INPUT_VALIDATION_TEST = "input_validation_test"
    RATE_LIMITING_TEST = "rate_limiting_test"
    SESSION_MANAGEMENT_TEST = "session_management_test"
    ENCRYPTION_TEST = "encryption_test"
    HEADER_SECURITY_TEST = "header_security_test"
    API_SECURITY_TEST = "api_security_test"


class SeverityLevel(Enum):
    """Severity levels for vulnerabilities."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Vulnerability:
    """Security vulnerability finding."""
    id: str
    title: str
    description: str
    severity: SeverityLevel
    test_type: TestType
    endpoint: str
    method: str
    payload: Optional[str]
    evidence: Dict[str, Any]
    remediation: str
    references: List[str]
    cvss_score: Optional[float]
    discovered_at: datetime
    test_id: str


@dataclass
class SecurityTest:
    """Security test definition."""
    id: str
    name: str
    description: str
    test_type: TestType
    target_endpoints: List[str]
    test_payloads: List[Dict[str, Any]]
    expected_results: Dict[str, Any]
    status: TestStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    vulnerabilities_found: List[str]
    execution_log: List[str]


@dataclass
class PenetrationTestReport:
    """Penetration test report."""
    test_id: str
    target: str
    start_time: datetime
    end_time: datetime
    tester: str
    methodology: str
    scope: List[str]
    vulnerabilities: List[Vulnerability]
    risk_score: float
    recommendations: List[str]
    executive_summary: str


class SecurityTestingFramework:
    """Comprehensive security testing framework."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        
        # Storage
        self.tests: Dict[str, SecurityTest] = {}
        self.vulnerabilities: Dict[str, Vulnerability] = {}
        self.reports: Dict[str, PenetrationTestReport] = {}
        
        # Test configurations
        self.test_payloads = self._initialize_test_payloads()
        self.vulnerability_patterns = self._initialize_vulnerability_patterns()
        
        # HTTP client for testing
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Test results tracking
        self.test_results: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration."""
        return {
            "base_url": "http://localhost:8000",
            "timeout_seconds": 30,
            "max_concurrent_tests": 5,
            "retry_attempts": 3,
            "enable_logging": True,
            "test_user_credentials": {
                "admin": {"email": "admin@test.com", "password": "testpassword123"},
                "user": {"email": "user@test.com", "password": "testpassword123"},
            },
            "test_headers": {
                "User-Agent": "Raptorflow-Security-Tester/1.0",
                "Accept": "application/json",
            },
        }
    
    def _initialize_test_payloads(self) -> Dict[TestType, List[Dict[str, Any]]]:
        """Initialize test payloads for different vulnerability types."""
        return {
            TestType.INPUT_VALIDATION_TEST: [
                {
                    "name": "SQL Injection",
                    "payloads": [
                        "' OR '1'='1",
                        "'; DROP TABLE users; --",
                        "' UNION SELECT * FROM users --",
                        "1' OR '1'='1' #",
                    ],
                    "patterns": [r"SQL syntax", r"mysql_fetch", r"ORA-[0-9]{5}"],
                },
                {
                    "name": "XSS",
                    "payloads": [
                        "<script>alert('XSS')</script>",
                        "javascript:alert('XSS')",
                        "<img src=x onerror=alert('XSS')>",
                        "';alert('XSS');//",
                    ],
                    "patterns": [r"<script", r"javascript:", r"onerror"],
                },
                {
                    "name": "Command Injection",
                    "payloads": [
                        "; ls -la",
                        "| cat /etc/passwd",
                        "`whoami`",
                        "$(id)",
                    ],
                    "patterns": [r"uid=", r"gid=", r"root:", r"bin/"],
                },
                {
                    "name": "Path Traversal",
                    "payloads": [
                        "../../../etc/passwd",
                        "..\\..\\..\\windows\\system32\\config\\sam",
                        "....//....//....//etc/passwd",
                        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                    ],
                    "patterns": [r"root:x", r"daemon:", r"bin:"],
                },
            ],
            TestType.AUTHENTICATION_TEST: [
                {
                    "name": "Weak Passwords",
                    "payloads": [
                        "password", "123456", "admin", "root", "test",
                        "password123", "admin123", "qwerty", "123456789",
                    ],
                    "patterns": [r"success", r"token", r"authenticated"],
                },
                {
                    "name": "SQL Injection in Login",
                    "payloads": [
                        "' OR '1'='1",
                        "admin'--",
                        "' OR '1'='1' #",
                        "admin' OR '1'='1",
                    ],
                    "patterns": [r"success", r"token", r"authenticated"],
                },
            ],
            TestType.RATE_LIMITING_TEST: [
                {
                    "name": "Rapid Requests",
                    "payloads": ["burst"],
                    "patterns": [r"429", r"rate limit", r"too many"],
                },
            ],
        }
    
    def _initialize_vulnerability_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize vulnerability detection patterns."""
        return {
            "sql_injection": {
                "patterns": [
                    r"SQL syntax.*MySQL",
                    r"Warning.*mysql_",
                    r"valid PostgreSQL result",
                    r"ORA-[0-9]{5}",
                    r"Microsoft OLE DB Provider",
                    r"ODBC Microsoft Access",
                    r"PostgreSQL query failed",
                ],
                "severity": SeverityLevel.HIGH,
                "cvss_base": 7.5,
            },
            "xss": {
                "patterns": [
                    r"<script[^>]*>.*?</script>",
                    r"javascript:",
                    r"on\w+\s*=",
                    r"alert\s*\(",
                ],
                "severity": SeverityLevel.MEDIUM,
                "cvss_base": 6.1,
            },
            "command_injection": {
                "patterns": [
                    r"uid=\d+.*gid=\d+",
                    r"root:.*:0:0",
                    r"/bin/",
                    r"/etc/passwd",
                    r"system32",
                ],
                "severity": SeverityLevel.CRITICAL,
                "cvss_base": 9.8,
            },
            "path_traversal": {
                "patterns": [
                    r"root:x:0:0",
                    r"daemon:",
                    r"bin:",
                    r"sys:",
                ],
                "severity": SeverityLevel.HIGH,
                "cvss_base": 7.5,
            },
            "information_disclosure": {
                "patterns": [
                    r"Internal Server Error",
                    r"Stack trace",
                    r"Exception",
                    r"Fatal error",
                    r"Debug mode",
                ],
                "severity": SeverityLevel.LOW,
                "cvss_base": 3.7,
            },
        }
    
    async def initialize(self):
        """Initialize the testing framework."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config["timeout_seconds"]),
            headers=self.config["test_headers"],
        )
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.session:
            await self.session.close()
    
    async def run_vulnerability_scan(self, target_endpoints: List[str]) -> str:
        """Run comprehensive vulnerability scan."""
        test_id = str(uuid.uuid4())
        
        test = SecurityTest(
            id=test_id,
            name="Comprehensive Vulnerability Scan",
            description="Automated vulnerability scanning of target endpoints",
            test_type=TestType.VULNERABILITY_SCAN,
            target_endpoints=target_endpoints,
            test_payloads=[],
            expected_results={},
            status=TestStatus.PENDING,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            vulnerabilities_found=[],
            execution_log=[],
        )
        
        self.tests[test_id] = test
        
        # Run the scan
        asyncio.create_task(self._execute_vulnerability_scan(test_id))
        
        return test_id
    
    async def _execute_vulnerability_scan(self, test_id: str):
        """Execute vulnerability scan."""
        test = self.tests[test_id]
        test.status = TestStatus.RUNNING
        test.started_at = datetime.now()
        
        try:
            for endpoint in test.target_endpoints:
                test.execution_log.append(f"Scanning endpoint: {endpoint}")
                
                # Test different HTTP methods
                for method in ["GET", "POST", "PUT", "DELETE"]:
                    await self._test_endpoint_vulnerabilities(test_id, endpoint, method)
                
                # Test input validation
                await self._test_input_validation(test_id, endpoint)
                
                # Test authentication bypass
                await self._test_authentication_bypass(test_id, endpoint)
            
            test.status = TestStatus.COMPLETED
            test.completed_at = datetime.now()
            
        except Exception as e:
            test.status = TestStatus.FAILED
            test.execution_log.append(f"Test failed: {str(e)}")
            logger.error(f"Vulnerability scan failed: {e}")
    
    async def _test_endpoint_vulnerabilities(self, test_id: str, endpoint: str, method: str):
        """Test endpoint for various vulnerabilities."""
        test = self.tests[test_id]
        
        # Test for information disclosure
        try:
            async with self.session.request(method, f"{self.config['base_url']}{endpoint}") as response:
                content = await response.text()
                
                # Check for information disclosure
                for vuln_type, vuln_info in self.vulnerability_patterns.items():
                    for pattern in vuln_info["patterns"]:
                        if re.search(pattern, content, re.IGNORECASE):
                            vulnerability = Vulnerability(
                                id=str(uuid.uuid4()),
                                title=f"{vuln_type.replace('_', ' ').title()} in {method} {endpoint}",
                                description=f"Detected {vuln_type} vulnerability",
                                severity=vuln_info["severity"],
                                test_type=TestType.VULNERABILITY_SCAN,
                                endpoint=endpoint,
                                method=method,
                                payload=None,
                                evidence={"response_content": content[:500]},
                                remediation=self._get_remediation_advice(vuln_type),
                                references=[],
                                cvss_score=vuln_info["cvss_base"],
                                discovered_at=datetime.now(),
                                test_id=test_id,
                            )
                            
                            self.vulnerabilities[vulnerability.id] = vulnerability
                            test.vulnerabilities_found.append(vulnerability.id)
                            test.execution_log.append(f"Found {vuln_type} in {method} {endpoint}")
        
        except Exception as e:
            test.execution_log.append(f"Error testing {method} {endpoint}: {str(e)}")
    
    async def _test_input_validation(self, test_id: str, endpoint: str):
        """Test input validation vulnerabilities."""
        test = self.tests[test_id]
        
        if TestType.INPUT_VALIDATION_TEST not in self.test_payloads:
            return
        
        for payload_group in self.test_payloads[TestType.INPUT_VALIDATION_TEST]:
            for payload in payload_group["payloads"]:
                try:
                    # Test GET parameter
                    test_url = f"{self.config['base_url']}{endpoint}?input={payload}"
                    async with self.session.get(test_url) as response:
                        content = await response.text()
                        
                        if self._detect_vulnerability(content, payload_group["patterns"]):
                            vulnerability = Vulnerability(
                                id=str(uuid.uuid4()),
                                title=f"{payload_group['name']} in GET {endpoint}",
                                description=f"Input validation vulnerability detected",
                                severity=SeverityLevel.HIGH,
                                test_type=TestType.INPUT_VALIDATION_TEST,
                                endpoint=endpoint,
                                method="GET",
                                payload=payload,
                                evidence={"response_content": content[:500]},
                                remediation="Implement proper input validation and parameterized queries",
                                references=[],
                                cvss_score=7.5,
                                discovered_at=datetime.now(),
                                test_id=test_id,
                            )
                            
                            self.vulnerabilities[vulnerability.id] = vulnerability
                            test.vulnerabilities_found.append(vulnerability.id)
                            test.execution_log.append(f"Found {payload_group['name']} in GET {endpoint}")
                    
                    # Test POST body
                    if endpoint in ["/api/v1/auth/login", "/api/v1/users", "/api/v1/agents"]:
                        test_data = {"input": payload}
                        async with self.session.post(f"{self.config['base_url']}{endpoint}", json=test_data) as response:
                            content = await response.text()
                            
                            if self._detect_vulnerability(content, payload_group["patterns"]):
                                vulnerability = Vulnerability(
                                    id=str(uuid.uuid4()),
                                    title=f"{payload_group['name']} in POST {endpoint}",
                                    description=f"Input validation vulnerability detected",
                                    severity=SeverityLevel.HIGH,
                                    test_type=TestType.INPUT_VALIDATION_TEST,
                                    endpoint=endpoint,
                                    method="POST",
                                    payload=payload,
                                    evidence={"response_content": content[:500]},
                                    remediation="Implement proper input validation and parameterized queries",
                                    references=[],
                                    cvss_score=7.5,
                                    discovered_at=datetime.now(),
                                    test_id=test_id,
                                )
                                
                                self.vulnerabilities[vulnerability.id] = vulnerability
                                test.vulnerabilities_found.append(vulnerability.id)
                                test.execution_log.append(f"Found {payload_group['name']} in POST {endpoint}")
                
                except Exception as e:
                    test.execution_log.append(f"Error testing payload {payload}: {str(e)}")
    
    async def _test_authentication_bypass(self, test_id: str, endpoint: str):
        """Test authentication bypass vulnerabilities."""
        test = self.tests[test_id]
        
        # Test without authentication
        try:
            async with self.session.get(f"{self.config['base_url']}{endpoint}") as response:
                if response.status == 200 and endpoint.startswith("/api/v1/"):
                    # Check if this should be protected
                    if endpoint not in ["/api/v1/health", "/api/v1/auth/login"]:
                        vulnerability = Vulnerability(
                            id=str(uuid.uuid4()),
                            title=f"Authentication Bypass in {endpoint}",
                            description="Endpoint accessible without authentication",
                            severity=SeverityLevel.HIGH,
                            test_type=TestType.AUTHENTICATION_TEST,
                            endpoint=endpoint,
                            method="GET",
                            payload=None,
                            evidence={"status_code": response.status},
                            remediation="Implement proper authentication checks",
                            references=[],
                            cvss_score=7.5,
                            discovered_at=datetime.now(),
                            test_id=test_id,
                        )
                        
                        self.vulnerabilities[vulnerability.id] = vulnerability
                        test.vulnerabilities_found.append(vulnerability.id)
                        test.execution_log.append(f"Authentication bypass found in {endpoint}")
        
        except Exception as e:
            test.execution_log.append(f"Error testing authentication bypass: {str(e)}")
    
    def _detect_vulnerability(self, content: str, patterns: List[str]) -> bool:
        """Detect vulnerability patterns in response content."""
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def _get_remediation_advice(self, vulnerability_type: str) -> str:
        """Get remediation advice for vulnerability type."""
        remediation_map = {
            "sql_injection": "Use parameterized queries or prepared statements. Validate and sanitize all user inputs.",
            "xss": "Implement proper output encoding. Use Content Security Policy headers. Validate and sanitize user inputs.",
            "command_injection": "Avoid executing system commands with user input. Use whitelisting for allowed commands.",
            "path_traversal": "Validate file paths. Use chroot jails. Implement proper access controls.",
            "information_disclosure": "Disable debug mode in production. Implement proper error handling. Use generic error messages.",
        }
        return remediation_map.get(vulnerability_type, "Implement proper security controls and validation.")
    
    async def run_penetration_test(self, target: str, scope: List[str], tester: str = "automated") -> str:
        """Run comprehensive penetration test."""
        test_id = str(uuid.uuid4())
        
        report = PenetrationTestReport(
            test_id=test_id,
            target=target,
            start_time=datetime.now(),
            end_time=datetime.now(),  # Will be updated
            tester=tester,
            methodology="OWASP Testing Guide",
            scope=scope,
            vulnerabilities=[],
            risk_score=0.0,
            recommendations=[],
            executive_summary="",
        )
        
        self.reports[test_id] = report
        
        # Run the penetration test
        asyncio.create_task(self._execute_penetration_test(test_id))
        
        return test_id
    
    async def _execute_penetration_test(self, test_id: str):
        """Execute penetration test."""
        report = self.reports[test_id]
        
        try:
            # Phase 1: Reconnaissance
            await self._reconnaissance_phase(test_id)
            
            # Phase 2: Scanning
            await self._scanning_phase(test_id)
            
            # Phase 3: Gaining Access
            await self._gaining_access_phase(test_id)
            
            # Phase 4: Maintaining Access
            await self._maintaining_access_phase(test_id)
            
            # Phase 5: Covering Tracks
            await self._covering_tracks_phase(test_id)
            
            # Calculate risk score and generate recommendations
            await self._generate_penetration_test_summary(test_id)
            
            report.end_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Penetration test failed: {e}")
    
    async def _reconnaissance_phase(self, test_id: str):
        """Reconnaissance phase of penetration test."""
        report = self.reports[test_id]
        
        # Test for exposed information
        info_endpoints = ["/", "/health", "/status", "/info", "/docs"]
        
        for endpoint in info_endpoints:
            try:
                async with self.session.get(f"{self.config['base_url']}{endpoint}") as response:
                    content = await response.text()
                    
                    # Check for information disclosure
                    if any(keyword in content.lower() for keyword in ["version", "server", "framework", "database"]):
                        vulnerability = Vulnerability(
                            id=str(uuid.uuid4()),
                            title=f"Information Disclosure in {endpoint}",
                            description="Sensitive information exposed",
                            severity=SeverityLevel.LOW,
                            test_type=TestType.PENETRATION_TEST,
                            endpoint=endpoint,
                            method="GET",
                            payload=None,
                            evidence={"response_snippet": content[:200]},
                            remediation="Remove sensitive information from public endpoints",
                            references=[],
                            cvss_score=3.7,
                            discovered_at=datetime.now(),
                            test_id=test_id,
                        )
                        
                        self.vulnerabilities[vulnerability.id] = vulnerability
                        report.vulnerabilities.append(vulnerability)
            
            except Exception as e:
                logger.debug(f"Error during reconnaissance: {e}")
    
    async def _scanning_phase(self, test_id: str):
        """Scanning phase of penetration test."""
        # Run vulnerability scan as part of penetration test
        await self._execute_vulnerability_scan(test_id)
        
        # Add found vulnerabilities to penetration test report
        test = self.tests.get(test_id)
        if test:
            for vuln_id in test.vulnerabilities_found:
                if vuln_id in self.vulnerabilities:
                    report = self.reports[test_id]
                    report.vulnerabilities.append(self.vulnerabilities[vuln_id])
    
    async def _gaining_access_phase(self, test_id: str):
        """Gaining access phase of penetration test."""
        # Test authentication bypass
        auth_endpoints = ["/api/v1/auth/login", "/api/v1/users", "/api/v1/agents"]
        
        for endpoint in auth_endpoints:
            await self._test_authentication_bypass(test_id, endpoint)
    
    async def _maintaining_access_phase(self, test_id: str):
        """Maintaining access phase of penetration test."""
        # Test session management
        await self._test_session_management(test_id)
    
    async def _test_session_management(self, test_id: str):
        """Test session management security."""
        try:
            # Test login to get session
            login_data = {
                "email": self.config["test_user_credentials"]["user"]["email"],
                "password": self.config["test_user_credentials"]["user"]["password"],
            }
            
            async with self.session.post(f"{self.config['base_url']}/api/v1/auth/login", json=login_data) as response:
                if response.status == 200:
                    login_response = await response.json()
                    
                    # Check for session token
                    if "access_token" in login_response:
                        token = login_response["access_token"]
                        
                        # Test session fixation
                        await self._test_session_fixation(test_id, token)
                        
                        # Test session hijacking
                        await self._test_session_hijacking(test_id, token)
        
        except Exception as e:
            logger.debug(f"Error testing session management: {e}")
    
    async def _test_session_fixation(self, test_id: str, token: str):
        """Test for session fixation vulnerabilities."""
        # This is a simplified test - in practice, would test more thoroughly
        pass
    
    async def _test_session_hijacking(self, test_id: str, token: str):
        """Test for session hijacking vulnerabilities."""
        # This is a simplified test - in practice, would test more thoroughly
        pass
    
    async def _covering_tracks_phase(self, test_id: str):
        """Covering tracks phase of penetration test."""
        # Test for logging and monitoring bypass
        await self._test_logging_bypass(test_id)
    
    async def _test_logging_bypass(self, test_id: str):
        """Test for logging and monitoring bypass."""
        # Test if actions are properly logged
        pass
    
    async def _generate_penetration_test_summary(self, test_id: str):
        """Generate penetration test summary and recommendations."""
        report = self.reports[test_id]
        
        # Calculate risk score
        if report.vulnerabilities:
            severity_weights = {
                SeverityLevel.INFO: 0.1,
                SeverityLevel.LOW: 0.3,
                SeverityLevel.MEDIUM: 0.5,
                SeverityLevel.HIGH: 0.8,
                SeverityLevel.CRITICAL: 1.0,
            }
            
            total_score = sum(severity_weights.get(vuln.severity, 0.5) for vuln in report.vulnerabilities)
            report.risk_score = min(total_score / len(report.vulnerabilities), 1.0) if report.vulnerabilities else 0.0
        else:
            report.risk_score = 0.0
        
        # Generate recommendations
        report.recommendations = self._generate_recommendations(report.vulnerabilities)
        
        # Generate executive summary
        report.executive_summary = self._generate_executive_summary(report)
    
    def _generate_recommendations(self, vulnerabilities: List[Vulnerability]) -> List[str]:
        """Generate security recommendations based on findings."""
        recommendations = set()
        
        for vuln in vulnerabilities:
            if vuln.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
                recommendations.add("Immediately address all high and critical severity vulnerabilities")
            
            if "SQL" in vuln.title:
                recommendations.add("Implement parameterized queries and input validation")
            elif "XSS" in vuln.title:
                recommendations.add("Implement proper output encoding and CSP headers")
            elif "Authentication" in vuln.title:
                recommendations.add("Strengthen authentication mechanisms")
            elif "Information" in vuln.title:
                recommendations.add("Review and restrict information disclosure")
        
        return list(recommendations)
    
    def _generate_executive_summary(self, report: PenetrationTestReport) -> str:
        """Generate executive summary for penetration test report."""
        vuln_count = len(report.vulnerabilities)
        critical_count = len([v for v in report.vulnerabilities if v.severity == SeverityLevel.CRITICAL])
        high_count = len([v for v in report.vulnerabilities if v.severity == SeverityLevel.HIGH])
        
        summary = f"""
Penetration test completed on {report.target} from {report.start_time} to {report.end_time}.
Found {vuln_count} vulnerabilities: {critical_count} critical, {high_count} high.
Overall risk score: {report.risk_score:.2f}/1.0.
"""
        
        if report.risk_score > 0.7:
            summary += "Immediate action required to address security vulnerabilities."
        elif report.risk_score > 0.4:
            summary += "Security improvements recommended to mitigate identified risks."
        else:
            summary += "Security posture is generally good with minor improvements needed."
        
        return summary.strip()
    
    def get_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get test results."""
        if test_id in self.tests:
            test = self.tests[test_id]
            return {
                "test": asdict(test),
                "vulnerabilities": [
                    asdict(self.vulnerabilities[vuln_id])
                    for vuln_id in test.vulnerabilities_found
                    if vuln_id in self.vulnerabilities
                ],
            }
        elif test_id in self.reports:
            report = self.reports[test_id]
            return {
                "report": asdict(report),
                "vulnerabilities": [asdict(vuln) for vuln in report.vulnerabilities],
            }
        
        return None
    
    def get_vulnerability_summary(self) -> Dict[str, Any]:
        """Get vulnerability summary."""
        if not self.vulnerabilities:
            return {"total": 0, "by_severity": {}, "by_type": {}}
        
        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)
        
        for vuln in self.vulnerabilities.values():
            severity_counts[vuln.severity.value] += 1
            type_counts[vuln.test_type.value] += 1
        
        return {
            "total": len(self.vulnerabilities),
            "by_severity": dict(severity_counts),
            "by_type": dict(type_counts),
            "average_cvss": statistics.mean([v.cvss_score for v in self.vulnerabilities.values() if v.cvss_score]),
        }
    
    def export_test_report(self, test_id: str, format: str = "json") -> str:
        """Export test report in specified format."""
        results = self.get_test_results(test_id)
        if not results:
            return ""
        
        if format.lower() == "json":
            return json.dumps(results, indent=2, default=str)
        elif format.lower() == "csv":
            return self._export_to_csv(results)
        elif format.lower() == "html":
            return self._export_to_html(results)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_to_csv(self, results: Dict[str, Any]) -> str:
        """Export results to CSV format."""
        import csv
        import io
        
        output = io.StringIO()
        
        if "vulnerabilities" in results and results["vulnerabilities"]:
            fieldnames = ["id", "title", "severity", "endpoint", "method", "cvss_score", "discovered_at"]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for vuln in results["vulnerabilities"]:
                writer.writerow({
                    "id": vuln["id"],
                    "title": vuln["title"],
                    "severity": vuln["severity"],
                    "endpoint": vuln["endpoint"],
                    "method": vuln["method"],
                    "cvss_score": vuln["cvss_score"],
                    "discovered_at": vuln["discovered_at"],
                })
        
        return output.getvalue()
    
    def _export_to_html(self, results: Dict[str, Any]) -> str:
        """Export results to HTML format."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .vulnerability { border: 1px solid #ddd; margin: 10px 0; padding: 15px; }
                .critical { border-left: 5px solid #d32f2f; }
                .high { border-left: 5px solid #f57c00; }
                .medium { border-left: 5px solid #fbc02d; }
                .low { border-left: 5px solid #388e3c; }
                .info { border-left: 5px solid #1976d2; }
            </style>
        </head>
        <body>
            <h1>Security Test Report</h1>
        """
        
        if "vulnerabilities" in results and results["vulnerabilities"]:
            for vuln in results["vulnerabilities"]:
                severity_class = vuln["severity"].lower()
                html += f"""
                <div class="vulnerability {severity_class}">
                    <h3>{vuln['title']}</h3>
                    <p><strong>Severity:</strong> {vuln['severity']}</p>
                    <p><strong>Endpoint:</strong> {vuln['method']} {vuln['endpoint']}</p>
                    <p><strong>CVSS Score:</strong> {vuln['cvss_score']}</p>
                    <p><strong>Description:</strong> {vuln['description']}</p>
                    <p><strong>Remediation:</strong> {vuln['remediation']}</p>
                </div>
                """
        
        html += "</body></html>"
        return html


# Global security testing framework instance
_security_testing_framework: Optional[SecurityTestingFramework] = None


def get_security_testing_framework() -> SecurityTestingFramework:
    """Get the global security testing framework instance."""
    global _security_testing_framework
    if _security_testing_framework is None:
        _security_testing_framework = SecurityTestingFramework()
    return _security_testing_framework
