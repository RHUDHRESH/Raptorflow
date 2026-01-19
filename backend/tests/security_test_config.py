"""
Security Testing Configuration
Configuration settings for load testing and penetration testing
"""

from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class LoadTestConfig:
    """Load testing configuration"""
    # Standard Load Test
    standard_users: int = 10
    standard_spawn_rate: int = 2
    standard_duration: int = 300  # 5 minutes
    
    # Stress Test
    stress_users: int = 50
    stress_spawn_rate: int = 10
    stress_duration: int = 600  # 10 minutes
    
    # Spike Test
    spike_users: int = 100
    spike_spawn_rate: int = 50
    spike_duration: int = 120  # 2 minutes
    
    # Performance Thresholds
    max_response_time_ms: int = 2000
    max_error_rate_percent: float = 1.0
    min_throughput_rps: float = 10.0

@dataclass
class PenetrationTestConfig:
    """Penetration testing configuration"""
    # Test Targets
    target_endpoints: List[str] = None
    exclude_endpoints: List[str] = None
    
    # Rate Limiting Test
    rate_test_requests: int = 50
    rate_test_success_threshold: int = 10
    
    # Authentication
    test_auth_bypass: bool = True
    test_invalid_tokens: bool = True
    
    # Webhook Security
    test_webhook_validation: bool = True
    webhook_payloads: List[str] = None
    
    # Data Exposure
    test_error_disclosure: bool = True
    sensitive_patterns: List[str] = None
    
    def __post_init__(self):
        if self.target_endpoints is None:
            self.target_endpoints = [
                "/api/v1/payments/initiate",
                "/api/v1/payments/status",
                "/api/v1/payments/refund",
                "/api/v1/payments/history",
                "/api/v1/webhooks/phonepe"
            ]
        
        if self.exclude_endpoints is None:
            self.exclude_endpoints = [
                "/health",
                "/metrics",
                "/docs"
            ]
        
        if self.webhook_payloads is None:
            self.webhook_payloads = [
                "PAYMENT_SUCCESS",
                "PAYMENT_FAILED",
                "REFUND_SUCCESS",
                "REFUND_FAILED"
            ]
        
        if self.sensitive_patterns is None:
            self.sensitive_patterns = [
                r"password",
                r"secret",
                r"key",
                r"token",
                r"database",
                r"internal",
                r"admin",
                r"config",
                r"env",
                r"sql",
                r"stack trace",
                r"exception"
            ]

@dataclass
class SecurityTestConfig:
    """Main security testing configuration"""
    load_test: LoadTestConfig
    penetration_test: PenetrationTestConfig
    
    # General Settings
    base_url: str
    auth_token: str = None
    output_directory: str = "./test_results"
    
    # Alerting
    alert_threshold_vulnerabilities: int = 5
    alert_threshold_errors: float = 5.0  # percentage
    
    # Reporting
    generate_html_report: bool = True
    generate_json_report: bool = True
    email_report: bool = False
    
    def __post_init__(self):
        if not self.output_directory.endswith('/'):
            self.output_directory += '/'

# Default configurations
DEFAULT_LOAD_CONFIG = LoadTestConfig()
DEFAULT_PENETRATION_CONFIG = PenetrationTestConfig()

# Environment-specific configurations
PRODUCTION_CONFIG = SecurityTestConfig(
    load_test=LoadTestConfig(
        standard_users=20,
        stress_users=100,
        spike_users=200
    ),
    penetration_test=DEFAULT_PENETRATION_CONFIG,
    base_url="https://api.raptorflow.com"
)

STAGING_CONFIG = SecurityTestConfig(
    load_test=LoadTestConfig(
        standard_users=10,
        stress_users=50,
        spike_users=100
    ),
    penetration_test=DEFAULT_PENETRATION_CONFIG,
    base_url="https://staging-api.raptorflow.com"
)

DEVELOPMENT_CONFIG = SecurityTestConfig(
    load_test=LoadTestConfig(
        standard_users=5,
        stress_users=20,
        spike_users=50
    ),
    penetration_test=DEFAULT_PENETRATION_CONFIG,
    base_url="http://localhost:8000"
)

# Test Scenarios
TEST_SCENARIOS = {
    "smoke": {
        "load_users": 5,
        "load_duration": 60,
        "penetration_tests": ["authentication", "rate_limiting"]
    },
    "integration": {
        "load_users": 10,
        "load_duration": 300,
        "penetration_tests": ["all"]
    },
    "production": {
        "load_users": 50,
        "load_duration": 1800,
        "penetration_tests": ["all"]
    }
}

# Vulnerability Severity Mappings
SEVERITY_COLORS = {
    "CRITICAL": "#FF0000",
    "HIGH": "#FF6600",
    "MEDIUM": "#FFAA00",
    "LOW": "#0066CC"
}

CWE_MAPPINGS = {
    "SQL Injection": "CWE-89",
    "XSS": "CWE-79",
    "Authentication Bypass": "CWE-287",
    "Rate Limiting Bypass": "CWE-770",
    "Idempotency Bypass": "CWE-668",
    "Webhook Signature Bypass": "CWE-345",
    "Sensitive Data Exposure": "CWE-209"
}

# Performance Benchmarks
PERFORMANCE_BENCHMARKS = {
    "payment_initiation": {
        "max_response_time_ms": 1500,
        "min_throughput_rps": 20.0
    },
    "payment_status": {
        "max_response_time_ms": 500,
        "min_throughput_rps": 50.0
    },
    "refund_processing": {
        "max_response_time_ms": 2000,
        "min_throughput_rps": 10.0
    },
    "webhook_processing": {
        "max_response_time_ms": 1000,
        "min_throughput_rps": 100.0
    }
}
