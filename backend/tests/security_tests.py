import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytest

logger = logging.getLogger("raptorflow.testing.security")


@dataclass
class SecurityTestConfig:
    """Security test configuration."""

    base_url: str = "http://localhost:8000"
    timeout: int = 30
    test_sql_injection: bool = True
    test_xss: bool = True
    test_authentication_bypass: bool = True
    test_rate_limiting: bool = True
    test_input_validation: bool = True
    test_authorization: bool = True


@dataclass
class SecurityVulnerability:
    """Security vulnerability finding."""

    vulnerability_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    endpoint: str
    description: str
    evidence: str
    recommendation: str
    timestamp: datetime


class SecurityTestRunner:
    """Security test runner for vulnerability scanning."""

    def __init__(self, config: SecurityTestConfig):
        self.config = config
        self.vulnerabilities: List[SecurityVulnerability] = []

    async def run_security_tests(self) -> List[SecurityVulnerability]:
        """Run comprehensive security tests."""
        logger.info("Starting security vulnerability scanning")

        if self.config.test_sql_injection:
            await self._test_sql_injection()

        if self.config.test_xss:
            await self._test_xss()

        if self.config.test_authentication_bypass:
            await self._test_authentication_bypass()

        if self.config.test_rate_limiting:
            await self._test_rate_limiting()

        if self.config.test_input_validation:
            await self._test_input_validation()

        if self.config.test_authorization:
            await self._test_authorization()

        logger.info(
            f"Security scan complete: {len(self.vulnerabilities)} vulnerabilities found"
        )
        return self.vulnerabilities

    async def _test_sql_injection(self):
        """Test for SQL injection vulnerabilities."""
        from httpx import AsyncClient

        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; SELECT * FROM information_schema.tables --",
            "' OR 1=1 --",
            "admin'--",
            "' OR 'x'='x",
        ]

        endpoints = ["/api/v1/users", "/api/v1/campaigns", "/api/v1/moves"]

        async with AsyncClient(
            base_url=self.config.base_url, timeout=self.config.timeout
        ) as client:
            for endpoint in endpoints:
                for payload in sql_payloads:
                    try:
                        # Test in query parameters
                        response = await client.get(f"{endpoint}?search={payload}")

                        # Check for SQL error messages or unusual behavior
                        response_text = response.text.lower()
                        sql_errors = [
                            "sql",
                            "mysql",
                            "postgresql",
                            "sqlite",
                            "ora-",
                            "syntax error",
                        ]

                        if (
                            any(error in response_text for error in sql_errors)
                            and response.status_code != 404
                        ):
                            self.vulnerabilities.append(
                                SecurityVulnerability(
                                    vulnerability_type="SQL Injection",
                                    severity="HIGH",
                                    endpoint=endpoint,
                                    description=f"Potential SQL injection vulnerability detected",
                                    evidence=f"Payload: {payload}, Response: {response.status_code}",
                                    recommendation="Use parameterized queries and input validation",
                                )
                            )

                        # Test in POST data
                        response = await client.post(endpoint, json={"search": payload})

                        if (
                            any(error in response.text.lower() for error in sql_errors)
                            and response.status_code != 404
                        ):
                            self.vulnerabilities.append(
                                SecurityVulnerability(
                                    vulnerability_type="SQL Injection",
                                    severity="HIGH",
                                    endpoint=endpoint,
                                    description=f"Potential SQL injection in POST data",
                                    evidence=f"Payload: {payload}, Response: {response.status_code}",
                                    recommendation="Use parameterized queries and input validation",
                                )
                            )

                    except Exception as e:
                        logger.debug(f"SQL injection test error: {e}")

    async def _test_xss(self):
        """Test for XSS vulnerabilities."""
        from httpx import AsyncClient

        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>",
            "'\"><script>alert('XSS')</script>",
        ]

        endpoints = ["/api/v1/users", "/api/v1/campaigns", "/api/v1/moves"]

        async with AsyncClient(
            base_url=self.config.base_url, timeout=self.config.timeout
        ) as client:
            for endpoint in endpoints:
                for payload in xss_payloads:
                    try:
                        # Test in query parameters
                        response = await client.get(f"{endpoint}?search={payload}")

                        # Check if payload is reflected in response without sanitization
                        if payload in response.text and response.status_code == 200:
                            self.vulnerabilities.append(
                                SecurityVulnerability(
                                    vulnerability_type="Cross-Site Scripting (XSS)",
                                    severity="MEDIUM",
                                    endpoint=endpoint,
                                    description="XSS payload reflected in response without sanitization",
                                    evidence=f"Payload: {payload} found in response",
                                    recommendation="Implement proper output encoding and CSP headers",
                                )
                            )

                        # Test in POST data
                        response = await client.post(endpoint, json={"name": payload})

                        if payload in response.text and response.status_code == 200:
                            self.vulnerabilities.append(
                                SecurityVulnerability(
                                    vulnerability_type="Cross-Site Scripting (XSS)",
                                    severity="MEDIUM",
                                    endpoint=endpoint,
                                    description="XSS payload in POST data reflected without sanitization",
                                    evidence=f"Payload: {payload} found in response",
                                    recommendation="Implement proper output encoding and CSP headers",
                                )
                            )

                    except Exception as e:
                        logger.debug(f"XSS test error: {e}")

    async def _test_authentication_bypass(self):
        """Test for authentication bypass vulnerabilities."""
        from httpx import AsyncClient

        # Test accessing protected endpoints without authentication
        protected_endpoints = [
            "/api/v1/users/profile",
            "/api/v1/campaigns/create",
            "/api/v1/admin/dashboard",
        ]

        async with AsyncClient(
            base_url=self.config.base_url, timeout=self.config.timeout
        ) as client:
            for endpoint in protected_endpoints:
                try:
                    # Test without any authentication
                    response = await client.get(endpoint)

                    if response.status_code == 200:
                        self.vulnerabilities.append(
                            SecurityVulnerability(
                                vulnerability_type="Authentication Bypass",
                                severity="HIGH",
                                endpoint=endpoint,
                                description="Protected endpoint accessible without authentication",
                                evidence=f"Status: {response.status_code}",
                                recommendation="Implement proper authentication middleware",
                            )
                        )

                    # Test with invalid token
                    response = await client.get(
                        endpoint, headers={"Authorization": "Bearer invalid_token"}
                    )

                    if response.status_code == 200:
                        self.vulnerabilities.append(
                            SecurityVulnerability(
                                vulnerability_type="Authentication Bypass",
                                severity="HIGH",
                                endpoint=endpoint,
                                description="Protected endpoint accessible with invalid token",
                                evidence=f"Status: {response.status_code}",
                                recommendation="Implement proper token validation",
                            )
                        )

                    # Test with manipulated token
                    response = await client.get(
                        endpoint, headers={"Authorization": "Bearer admin_token"}
                    )

                    if response.status_code == 200:
                        self.vulnerabilities.append(
                            SecurityVulnerability(
                                vulnerability_type="Authentication Bypass",
                                severity="HIGH",
                                endpoint=endpoint,
                                description="Protected endpoint accessible with manipulated token",
                                evidence=f"Status: {response.status_code}",
                                recommendation="Implement proper token validation and role checking",
                            )
                        )

                except Exception as e:
                    logger.debug(f"Authentication bypass test error: {e}")

    async def _test_rate_limiting(self):
        """Test rate limiting effectiveness."""
        import time

        from httpx import AsyncClient

        endpoint = "/api/v1/users"

        async with AsyncClient(
            base_url=self.config.base_url, timeout=self.config.timeout
        ) as client:
            # Send rapid requests to test rate limiting
            responses = []
            start_time = time.time()

            for i in range(100):  # Send 100 requests rapidly
                try:
                    response = await client.get(endpoint)
                    responses.append(response.status_code)

                    # If we get rate limited, break
                    if response.status_code == 429:
                        break

                except Exception as e:
                    logger.debug(f"Rate limiting test error: {e}")
                    break

            end_time = time.time()
            duration = end_time - start_time

            # Check if rate limiting is working
            if 429 not in responses and duration < 10:  # No rate limiting in 10 seconds
                self.vulnerabilities.append(
                    SecurityVulnerability(
                        vulnerability_type="Missing Rate Limiting",
                        severity="MEDIUM",
                        endpoint=endpoint,
                        description="No rate limiting detected on endpoint",
                        evidence=f"100 requests in {duration:.1f}s without 429 status",
                        recommendation="Implement rate limiting to prevent abuse",
                    )
                )

    async def _test_input_validation(self):
        """Test input validation effectiveness."""
        from httpx import AsyncClient

        # Test various malformed inputs
        test_cases = [
            {"field": "email", "value": "invalid-email", "expected_status": 422},
            {"field": "age", "value": -5, "expected_status": 422},
            {"field": "name", "value": "", "expected_status": 422},
            {"field": "id", "value": "not-a-number", "expected_status": 422},
            {"field": "date", "value": "invalid-date", "expected_status": 422},
        ]

        endpoints = ["/api/v1/users", "/api/v1/campaigns"]

        async with AsyncClient(
            base_url=self.config.base_url, timeout=self.config.timeout
        ) as client:
            for endpoint in endpoints:
                for test_case in test_cases:
                    try:
                        response = await client.post(
                            endpoint, json={test_case["field"]: test_case["value"]}
                        )

                        # If server accepts invalid input, it's a vulnerability
                        if response.status_code != test_case["expected_status"]:
                            self.vulnerabilities.append(
                                SecurityVulnerability(
                                    vulnerability_type="Input Validation Bypass",
                                    severity="MEDIUM",
                                    endpoint=endpoint,
                                    description=f"Invalid input accepted for field: {test_case['field']}",
                                    evidence=f"Input: {test_case['value']}, Status: {response.status_code}",
                                    recommendation="Implement proper input validation",
                                )
                            )

                    except Exception as e:
                        logger.debug(f"Input validation test error: {e}")

    async def _test_authorization(self):
        """Test authorization controls."""
        from httpx import AsyncClient

        # Test accessing admin endpoints as regular user
        admin_endpoints = [
            "/api/v1/admin/users",
            "/api/v1/admin/settings",
            "/api/v1/admin/metrics",
        ]

        # Simulate regular user token (this would be a real token in production)
        user_token = "Bearer regular_user_token"

        async with AsyncClient(
            base_url=self.config.base_url, timeout=self.config.timeout
        ) as client:
            for endpoint in admin_endpoints:
                try:
                    response = await client.get(
                        endpoint, headers={"Authorization": user_token}
                    )

                    # If regular user can access admin endpoint, it's a vulnerability
                    if response.status_code == 200:
                        self.vulnerabilities.append(
                            SecurityVulnerability(
                                vulnerability_type="Authorization Bypass",
                                severity="HIGH",
                                endpoint=endpoint,
                                description="Regular user can access admin endpoint",
                                evidence=f"Status: {response.status_code}",
                                recommendation="Implement proper role-based access control",
                            )
                        )

                except Exception as e:
                    logger.debug(f"Authorization test error: {e}")

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate security vulnerability report."""
        if not self.vulnerabilities:
            return {
                "status": "SECURE",
                "vulnerabilities_found": 0,
                "recommendations": ["No security vulnerabilities detected"],
                "generated_at": datetime.utcnow().isoformat(),
            }

        # Group vulnerabilities by severity
        severity_counts = {}
        for vuln in self.vulnerabilities:
            severity = vuln.severity
            if severity not in severity_counts:
                severity_counts[severity] = 0
            severity_counts[severity] += 1

        # Calculate risk score
        risk_score = (
            severity_counts.get("CRITICAL", 0) * 10
            + severity_counts.get("HIGH", 0) * 5
            + severity_counts.get("MEDIUM", 0) * 2
            + severity_counts.get("LOW", 0) * 1
        )

        # Determine overall security status
        if severity_counts.get("CRITICAL", 0) > 0:
            status = "CRITICAL"
        elif severity_counts.get("HIGH", 0) > 2:
            status = "HIGH_RISK"
        elif severity_counts.get("HIGH", 0) > 0 or severity_counts.get("MEDIUM", 0) > 5:
            status = "MEDIUM_RISK"
        elif severity_counts.get("MEDIUM", 0) > 0:
            status = "LOW_RISK"
        else:
            status = "SECURE"

        return {
            "status": status,
            "risk_score": risk_score,
            "vulnerabilities_found": len(self.vulnerabilities),
            "severity_breakdown": severity_counts,
            "vulnerabilities": [
                {
                    "type": v.vulnerability_type,
                    "severity": v.severity,
                    "endpoint": v.endpoint,
                    "description": v.description,
                    "evidence": v.evidence,
                    "recommendation": v.recommendation,
                    "timestamp": v.timestamp.isoformat(),
                }
                for v in self.vulnerabilities
            ],
            "recommendations": self._generate_security_recommendations(),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _generate_security_recommendations(self) -> List[str]:
        """Generate security recommendations based on findings."""
        recommendations = []

        vuln_types = set(v.vulnerability_type for v in self.vulnerabilities)

        if "SQL Injection" in vuln_types:
            recommendations.append(
                "Implement parameterized queries and input validation to prevent SQL injection"
            )

        if "Cross-Site Scripting (XSS)" in vuln_types:
            recommendations.append(
                "Implement Content Security Policy (CSP) headers and output encoding to prevent XSS"
            )

        if "Authentication Bypass" in vuln_types:
            recommendations.append(
                "Strengthen authentication mechanisms and implement proper token validation"
            )

        if "Authorization Bypass" in vuln_types:
            recommendations.append(
                "Implement role-based access control (RBAC) and regular authorization audits"
            )

        if "Missing Rate Limiting" in vuln_types:
            recommendations.append(
                "Implement rate limiting to prevent abuse and DoS attacks"
            )

        if "Input Validation Bypass" in vuln_types:
            recommendations.append(
                "Implement comprehensive input validation and sanitization"
            )

        if not recommendations:
            recommendations.append(
                "Continue following security best practices and regular security audits"
            )

        return recommendations


# Pytest fixtures and test functions
@pytest.fixture
def security_test_config():
    """Pytest fixture for security test configuration."""
    return SecurityTestConfig()


@pytest.mark.asyncio
async def test_security_vulnerabilities(security_test_config):
    """Test for security vulnerabilities."""
    runner = SecurityTestRunner(security_test_config)
    vulnerabilities = await runner.run_security_tests()

    # Assert no critical or high vulnerabilities
    critical_high_vulns = [
        v for v in vulnerabilities if v.severity in ["CRITICAL", "HIGH"]
    ]
    assert (
        len(critical_high_vulns) == 0
    ), f"Critical/High vulnerabilities found: {[v.vulnerability_type for v in critical_high_vulns]}"


if __name__ == "__main__":
    # Run security tests when executed directly
    async def main():
        config = SecurityTestConfig()
        runner = SecurityTestRunner(config)
        vulnerabilities = await runner.run_security_tests()
        report = runner.generate_security_report()

        print(f"\nSecurity Scan Results:")
        print(f"Status: {report['status']}")
        print(f"Risk Score: {report['risk_score']}")
        print(f"Vulnerabilities Found: {report['vulnerabilities_found']}")

        if report["vulnerabilities_found"] > 0:
            print(f"\nSeverity Breakdown:")
            for severity, count in report["severity_breakdown"].items():
                print(f"- {severity}: {count}")

            print(f"\nTop Vulnerabilities:")
            for vuln in report["vulnerabilities"][:5]:  # Show top 5
                print(f"- {vuln['type']} ({vuln['severity']}) on {vuln['endpoint']}")

        print(f"\nRecommendations:")
        for rec in report["recommendations"]:
            print(f"- {rec}")

    asyncio.run(main())
