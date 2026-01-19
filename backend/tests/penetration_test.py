"""
Penetration Testing Framework for Raptorflow Payment System
Security testing suite for identifying vulnerabilities in payment endpoints
"""

import asyncio
import json
import uuid
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
from dataclasses import dataclass
import requests
from concurrent.futures import ThreadPoolExecutor
import re

logger = logging.getLogger(__name__)

@dataclass
class VulnerabilityReport:
    """Structure for reporting security vulnerabilities"""
    vulnerability_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    endpoint: str
    payload: str
    response: str
    recommendation: str
    cwe_id: Optional[str] = None

class PaymentPenetrationTester:
    """
    Comprehensive penetration testing suite for payment endpoints
    Tests for OWASP Top 10 and payment-specific vulnerabilities
    """
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = requests.Session()
        self.vulnerabilities: List[VulnerabilityReport] = []
        
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            })
    
    def add_vulnerability(self, vuln: VulnerabilityReport):
        """Add a vulnerability to the report"""
        self.vulnerabilities.append(vuln)
        logger.warning(f"Vulnerability found: {vuln.vulnerability_type} - {vuln.description}")
    
    async def test_sql_injection(self) -> List[VulnerabilityReport]:
        """Test for SQL injection vulnerabilities"""
        logger.info("Testing for SQL injection vulnerabilities...")
        
        sql_payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "'; DROP TABLE payments; --",
            "' UNION SELECT * FROM users --",
            "1' AND (SELECT COUNT(*) FROM users) > 0 --",
            "' AND 1=CONVERT(int, (SELECT @@version)) --"
        ]
        
        vulnerabilities = []
        
        for payload in sql_payloads:
            # Test payment initiation endpoint
            payment_data = {
                "amount": 100,
                "merchant_order_id": payload,
                "redirect_url": "https://example.com/success",
                "callback_url": "https://example.com/callback"
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/payments/initiate",
                    json=payment_data,
                    timeout=10
                )
                
                # Check for SQL error messages
                sql_errors = [
                    "syntax error", "mysql_fetch", "ora-", "microsoft odbc",
                    "postgresql", "sqlite_", "sql syntax", "warning: mysql"
                ]
                
                if any(error in response.text.lower() for error in sql_errors):
                    vuln = VulnerabilityReport(
                        vulnerability_type="SQL Injection",
                        severity="CRITICAL",
                        description=f"SQL injection vulnerability detected with payload: {payload}",
                        endpoint="/api/v1/payments/initiate",
                        payload=json.dumps(payment_data),
                        response=response.text[:500],
                        recommendation="Implement parameterized queries and input validation",
                        cwe_id="CWE-89"
                    )
                    vulnerabilities.append(vuln)
                    self.add_vulnerability(vuln)
                    
            except Exception as e:
                logger.error(f"Error testing SQL injection: {e}")
        
        return vulnerabilities
    
    async def test_xss_vulnerabilities(self) -> List[VulnerabilityReport]:
        """Test for Cross-Site Scripting (XSS) vulnerabilities"""
        logger.info("Testing for XSS vulnerabilities...")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>",
            "'\"><script>alert('XSS')</script>"
        ]
        
        vulnerabilities = []
        
        for payload in xss_payloads:
            # Test customer info field
            payment_data = {
                "amount": 100,
                "merchant_order_id": f"MO{int(time.time())}",
                "redirect_url": "https://example.com/success",
                "callback_url": "https://example.com/callback",
                "customer_info": {
                    "name": payload,
                    "email": f"test_{uuid.uuid4().hex[:8]}@example.com"
                }
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/payments/initiate",
                    json=payment_data,
                    timeout=10
                )
                
                # Check if payload is reflected in response
                if payload in response.text:
                    vuln = VulnerabilityReport(
                        vulnerability_type="Cross-Site Scripting (XSS)",
                        severity="HIGH",
                        description=f"XSS vulnerability detected with payload: {payload}",
                        endpoint="/api/v1/payments/initiate",
                        payload=json.dumps(payment_data),
                        response=response.text[:500],
                        recommendation="Implement output encoding and input sanitization",
                        cwe_id="CWE-79"
                    )
                    vulnerabilities.append(vuln)
                    self.add_vulnerability(vuln)
                    
            except Exception as e:
                logger.error(f"Error testing XSS: {e}")
        
        return vulnerabilities
    
    async def test_authentication_bypass(self) -> List[VulnerabilityReport]:
        """Test for authentication bypass vulnerabilities"""
        logger.info("Testing for authentication bypass...")
        
        vulnerabilities = []
        
        # Test without authentication
        unauth_session = requests.Session()
        unauth_session.headers.update({'Content-Type': 'application/json'})
        
        protected_endpoints = [
            "/api/v1/payments/history",
            "/api/v1/payments/refund",
            "/api/v1/admin/users"
        ]
        
        for endpoint in protected_endpoints:
            try:
                response = unauth_session.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code != 401 and response.status_code != 403:
                    vuln = VulnerabilityReport(
                        vulnerability_type="Authentication Bypass",
                        severity="CRITICAL",
                        description=f"Protected endpoint accessible without authentication",
                        endpoint=endpoint,
                        payload="No authentication",
                        response=response.text[:200],
                        recommendation="Implement proper authentication middleware",
                        cwe_id="CWE-287"
                    )
                    vulnerabilities.append(vuln)
                    self.add_vulnerability(vuln)
                    
            except Exception as e:
                logger.error(f"Error testing authentication bypass: {e}")
        
        # Test with invalid token
        invalid_session = requests.Session()
        invalid_session.headers.update({
            'Authorization': 'Bearer invalid_token_123',
            'Content-Type': 'application/json'
        })
        
        for endpoint in protected_endpoints:
            try:
                response = invalid_session.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code != 401 and response.status_code != 403:
                    vuln = VulnerabilityReport(
                        vulnerability_type="Authentication Bypass",
                        severity="HIGH",
                        description=f"Protected endpoint accessible with invalid token",
                        endpoint=endpoint,
                        payload="Bearer invalid_token_123",
                        response=response.text[:200],
                        recommendation="Validate JWT tokens properly",
                        cwe_id="CWE-287"
                    )
                    vulnerabilities.append(vuln)
                    self.add_vulnerability(vuln)
                    
            except Exception as e:
                logger.error(f"Error testing invalid token: {e}")
        
        return vulnerabilities
    
    async def test_rate_limiting_bypass(self) -> List[VulnerabilityReport]:
        """Test for rate limiting bypass"""
        logger.info("Testing rate limiting bypass...")
        
        vulnerabilities = []
        
        # Test rapid requests to payment initiation
        payment_data = {
            "amount": 100,
            "merchant_order_id": f"MO{int(time.time())}",
            "redirect_url": "https://example.com/success",
            "callback_url": "https://example.com/callback"
        }
        
        success_count = 0
        total_requests = 50
        
        for i in range(total_requests):
            try:
                # Change merchant order ID for each request
                payment_data["merchant_order_id"] = f"MO{int(time.time())}{i}"
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/payments/initiate",
                    json=payment_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"Error in rate limiting test: {e}")
        
        # If more than 10 requests succeeded in rapid succession, rate limiting might be insufficient
        if success_count > 10:
            vuln = VulnerabilityReport(
                vulnerability_type="Rate Limiting Bypass",
                severity="MEDIUM",
                description=f"Rate limiting insufficient - {success_count}/{total_requests} requests succeeded",
                endpoint="/api/v1/payments/initiate",
                payload=f"Rapid requests: {total_requests}",
                response=f"Success count: {success_count}",
                recommendation="Implement stricter rate limiting with proper throttling",
                cwe_id="CWE-770"
            )
            vulnerabilities.append(vuln)
            self.add_vulnerability(vuln)
        
        return vulnerabilities
    
    async def test_idempotency_bypass(self) -> List[VulnerabilityReport]:
        """Test for idempotency bypass vulnerabilities"""
        logger.info("Testing idempotency bypass...")
        
        vulnerabilities = []
        
        # Test duplicate requests with same idempotency key
        payment_data = {
            "amount": 100,
            "merchant_order_id": f"MO{int(time.time())}",
            "redirect_url": "https://example.com/success",
            "callback_url": "https://example.com/callback",
            "idempotency_key": "test_key_12345"
        }
        
        try:
            # Send first request
            response1 = self.session.post(
                f"{self.base_url}/api/v1/payments/initiate",
                json=payment_data,
                timeout=10
            )
            
            # Send duplicate request
            response2 = self.session.post(
                f"{self.base_url}/api/v1/payments/initiate",
                json=payment_data,
                timeout=10
            )
            
            # Check if different transaction IDs are returned (idempotency violation)
            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                
                if data1.get("transaction_id") != data2.get("transaction_id"):
                    vuln = VulnerabilityReport(
                        vulnerability_type="Idempotency Bypass",
                        severity="HIGH",
                        description="Duplicate requests with same idempotency key created different transactions",
                        endpoint="/api/v1/payments/initiate",
                        payload=json.dumps(payment_data),
                        response=f"Response1: {data1.get('transaction_id')}, Response2: {data2.get('transaction_id')}",
                        recommendation="Implement proper idempotency handling with key-based deduplication",
                        cwe_id="CWE-668"
                    )
                    vulnerabilities.append(vuln)
                    self.add_vulnerability(vuln)
                    
        except Exception as e:
            logger.error(f"Error testing idempotency: {e}")
        
        return vulnerabilities
    
    async def test_webhook_signature_bypass(self) -> List[VulnerabilityReport]:
        """Test webhook signature validation bypass"""
        logger.info("Testing webhook signature bypass...")
        
        vulnerabilities = []
        
        # Test webhook with invalid signature
        webhook_payload = {
            "event": "PAYMENT_SUCCESS",
            "data": {
                "transaction_id": f"txn_{uuid.uuid4().hex}",
                "merchant_order_id": f"MO{int(time.time())}",
                "amount": 100,
                "status": "SUCCESS"
            }
        }
        
        # Test without signature
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/webhooks/phonepe",
                json=webhook_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                vuln = VulnerabilityReport(
                    vulnerability_type="Webhook Signature Bypass",
                    severity="CRITICAL",
                    description="Webhook accepted without signature validation",
                    endpoint="/api/v1/webhooks/phonepe",
                    payload=json.dumps(webhook_payload),
                    response=response.text[:200],
                    recommendation="Implement mandatory webhook signature validation",
                    cwe_id="CWE-345"
                )
                vulnerabilities.append(vuln)
                self.add_vulnerability(vuln)
                
        except Exception as e:
            logger.error(f"Error testing webhook without signature: {e}")
        
        # Test with invalid signature
        try:
            headers = {"X-VERIFY": "invalid_signature_123"}
            response = self.session.post(
                f"{self.base_url}/api/v1/webhooks/phonepe",
                json=webhook_payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                vuln = VulnerabilityReport(
                    vulnerability_type="Webhook Signature Bypass",
                    severity="CRITICAL",
                    description="Webhook accepted with invalid signature",
                    endpoint="/api/v1/webhooks/phonepe",
                    payload=json.dumps(webhook_payload),
                    response=response.text[:200],
                    recommendation="Validate webhook signatures using proper cryptographic verification",
                    cwe_id="CWE-345"
                )
                vulnerabilities.append(vuln)
                self.add_vulnerability(vuln)
                
        except Exception as e:
            logger.error(f"Error testing webhook with invalid signature: {e}")
        
        return vulnerabilities
    
    async def test_data_exposure(self) -> List[VulnerabilityReport]:
        """Test for sensitive data exposure"""
        logger.info("Testing for sensitive data exposure...")
        
        vulnerabilities = []
        
        # Test for information disclosure in error messages
        invalid_payment_data = {
            "amount": -100,  # Invalid amount
            "merchant_order_id": "test_order",
            "redirect_url": "invalid_url",
            "callback_url": "invalid_url"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/payments/initiate",
                json=invalid_payment_data,
                timeout=10
            )
            
            # Check for sensitive information in error response
            sensitive_patterns = [
                r"password", r"secret", r"key", r"token", r"database",
                r"internal", r"admin", r"config", r"env", r"sql"
            ]
            
            for pattern in sensitive_patterns:
                if re.search(pattern, response.text, re.IGNORECASE):
                    vuln = VulnerabilityReport(
                        vulnerability_type="Sensitive Data Exposure",
                        severity="MEDIUM",
                        description=f"Sensitive information pattern '{pattern}' found in error response",
                        endpoint="/api/v1/payments/initiate",
                        payload=json.dumps(invalid_payment_data),
                        response=response.text[:500],
                        recommendation="Sanitize error messages and avoid exposing internal details",
                        cwe_id="CWE-209"
                    )
                    vulnerabilities.append(vuln)
                    self.add_vulnerability(vuln)
                    break
                    
        except Exception as e:
            logger.error(f"Error testing data exposure: {e}")
        
        return vulnerabilities
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all penetration tests and generate comprehensive report"""
        logger.info("Starting comprehensive penetration testing...")
        
        start_time = time.time()
        
        # Run all tests
        sql_vulns = await self.test_sql_injection()
        xss_vulns = await self.test_xss_vulnerabilities()
        auth_vulns = await self.test_authentication_bypass()
        rate_vulns = await self.test_rate_limiting_bypass()
        idemp_vulns = await self.test_idempotency_bypass()
        webhook_vulns = await self.test_webhook_signature_bypass()
        data_vulns = await self.test_data_exposure()
        
        end_time = time.time()
        
        # Generate summary
        total_vulns = len(self.vulnerabilities)
        critical_vulns = len([v for v in self.vulnerabilities if v.severity == "CRITICAL"])
        high_vulns = len([v for v in self.vulnerabilities if v.severity == "HIGH"])
        medium_vulns = len([v for v in self.vulnerabilities if v.severity == "MEDIUM"])
        low_vulns = len([v for v in self.vulnerabilities if v.severity == "LOW"])
        
        report = {
            "test_summary": {
                "total_vulnerabilities": total_vulns,
                "critical": critical_vulns,
                "high": high_vulns,
                "medium": medium_vulns,
                "low": low_vulns,
                "test_duration": end_time - start_time,
                "timestamp": datetime.now().isoformat()
            },
            "vulnerabilities_by_type": {
                "sql_injection": len(sql_vulns),
                "xss": len(xss_vulns),
                "authentication_bypass": len(auth_vulns),
                "rate_limiting_bypass": len(rate_vulns),
                "idempotency_bypass": len(idemp_vulns),
                "webhook_signature_bypass": len(webhook_vulns),
                "data_exposure": len(data_vulns)
            },
            "detailed_vulnerabilities": [
                {
                    "type": v.vulnerability_type,
                    "severity": v.severity,
                    "description": v.description,
                    "endpoint": v.endpoint,
                    "payload": v.payload,
                    "response": v.response,
                    "recommendation": v.recommendation,
                    "cwe_id": v.cwe_id
                }
                for v in self.vulnerabilities
            ]
        }
        
        logger.info(f"Penetration testing completed. Found {total_vulns} vulnerabilities.")
        return report
    
    def generate_report(self, report: Dict[str, Any], output_file: str = "penetration_test_report.json"):
        """Generate detailed penetration test report"""
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Penetration test report saved to {output_file}")
        
        # Print summary
        print("\n" + "="*50)
        print("PENETRATION TEST SUMMARY")
        print("="*50)
        print(f"Total Vulnerabilities: {report['test_summary']['total_vulnerabilities']}")
        print(f"Critical: {report['test_summary']['critical']}")
        print(f"High: {report['test_summary']['high']}")
        print(f"Medium: {report['test_summary']['medium']}")
        print(f"Low: {report['test_summary']['low']}")
        print(f"Test Duration: {report['test_summary']['test_duration']:.2f} seconds")
        print("="*50)


class AutomatedSecurityScanner:
    """
    Automated security scanner for continuous security monitoring
    """
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.tester = PaymentPenetrationTester(base_url, auth_token)
    
    async def scan_and_alert(self, alert_threshold: int = 5):
        """
        Run security scan and alert if vulnerabilities exceed threshold
        """
        report = await self.tester.run_comprehensive_test()
        
        if report['test_summary']['total_vulnerabilities'] > alert_threshold:
            logger.critical(f"SECURITY ALERT: {report['test_summary']['total_vulnerabilities']} vulnerabilities found!")
            # Here you could integrate with alerting systems
            # send_slack_alert(report)
            # send_email_alert(report)
        
        return report


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python penetration_test.py <base_url> [auth_token]")
        sys.exit(1)
    
    base_url = sys.argv[1]
    auth_token = sys.argv[2] if len(sys.argv) > 2 else None
    
    async def main():
        tester = PaymentPenetrationTester(base_url, auth_token)
        report = await tester.run_comprehensive_test()
        tester.generate_report(report)
    
    asyncio.run(main())
