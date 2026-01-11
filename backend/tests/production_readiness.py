"""
Production readiness test suite for RaptorFlow Backend
Comprehensive testing to ensure production readiness
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock

import httpx
from core.circuit_breaker import get_resilient_client
from core.redis_production import get_redis_production_manager
from core.sentry import get_health_status
from core.supabase_production import get_supabase_production_manager
from fastapi.testclient import TestClient
from main import app

logger = logging.getLogger(__name__)


class ProductionTestResult:
    """Test result container"""

    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category
        self.status = "pending"
        self.message = ""
        self.details = {}
        self.duration_ms = 0
        self.timestamp = datetime.utcnow()
        self.critical = False

    def set_passed(self, message: str = "", details: Optional[Dict] = None):
        """Mark test as passed"""
        self.status = "passed"
        self.message = message
        self.details = details or {}

    def set_failed(self, message: str, details: Optional[Dict] = None):
        """Mark test as failed"""
        self.status = "failed"
        self.message = message
        self.details = details or {}

    def set_critical(self, message: str, details: Optional[Dict] = None):
        """Mark test as critical failure"""
        self.status = "critical"
        self.message = message
        self.details = details or {}
        self.critical = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "category": self.category,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
            "critical": self.critical,
        }


class ProductionTestSuite:
    """Production readiness test suite"""

    def __init__(self):
        self.results: List[ProductionTestResult] = []
        self.test_client = TestClient(app)
        self.http_client = httpx.AsyncClient()

        # Test configuration
        self.base_url = os.getenv("TEST_BASE_URL", "http://localhost:8000")
        self.timeout = int(os.getenv("TEST_TIMEOUT", "30"))

        # Test thresholds
        self.max_response_time_ms = int(os.getenv("MAX_RESPONSE_TIME_MS", "5000"))
        self.max_memory_mb = int(os.getenv("MAX_MEMORY_MB", "512"))
        self.min_uptime_percentage = float(os.getenv("MIN_UPTIME_PERCENTAGE", "99.9"))

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all production readiness tests"""
        logger.info("Starting production readiness test suite")

        start_time = datetime.utcnow()

        # Test categories
        test_categories = [
            ("security", self._run_security_tests),
            ("performance", self._run_performance_tests),
            ("resilience", self._run_resilience_tests),
            ("monitoring", self._run_monitoring_tests),
            ("database", self._run_database_tests),
            ("infrastructure", self._run_infrastructure_tests),
            ("compliance", self._run_compliance_tests),
        ]

        # Run tests by category
        for category, test_func in test_categories:
            logger.info(f"Running {category} tests...")
            await test_func()

        # Calculate results
        end_time = datetime.utcnow()
        total_duration = (end_time - start_time).total_seconds()

        passed = len([r for r in self.results if r.status == "passed"])
        failed = len([r for r in self.results if r.status == "failed"])
        critical = len([r for r in self.results if r.status == "critical"])

        summary = {
            "status": "passed" if critical == 0 and failed == 0 else "failed",
            "total_tests": len(self.results),
            "passed": passed,
            "failed": failed,
            "critical": critical,
            "duration_seconds": total_duration,
            "timestamp": end_time.isoformat(),
            "categories": {},
        }

        # Group results by category
        for result in self.results:
            if result.category not in summary["categories"]:
                summary["categories"][result.category] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "critical": 0,
                }

            cat_summary = summary["categories"][result.category]
            cat_summary["total"] += 1

            if result.status == "passed":
                cat_summary["passed"] += 1
            elif result.status == "failed":
                cat_summary["failed"] += 1
            elif result.status == "critical":
                cat_summary["critical"] += 1

        # Add detailed results
        summary["results"] = [r.to_dict() for r in self.results]

        logger.info(
            f"Test suite completed: {passed}/{len(self.results)} passed, {failed} failed, {critical} critical"
        )

        return summary

    async def _run_security_tests(self) -> None:
        """Run security-related tests"""

        # Test 1: No hardcoded secrets
        test = ProductionTestResult("No hardcoded secrets", "security")
        start_time = time.time()

        try:
            # Check for hardcoded secrets in environment
            sensitive_vars = [
                "API_KEY",
                "SECRET_KEY",
                "PASSWORD",
                "TOKEN",
                "PRIVATE_KEY",
            ]

            hardcoded_found = []
            for var in sensitive_vars:
                value = os.getenv(var)
                if (
                    value
                    and not value.startswith("${")
                    and not value.startswith("your-")
                ):
                    hardcoded_found.append(var)

            if hardcoded_found:
                test.set_failed(
                    f"Found hardcoded environment variables: {hardcoded_found}"
                )
            else:
                test.set_passed("No hardcoded secrets found in environment variables")

        except Exception as e:
            test.set_failed(f"Security check error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

        # Test 2: CORS configuration
        test = ProductionTestResult("CORS configuration", "security")
        start_time = time.time()

        try:
            # Test CORS headers
            response = self.test_client.options("/api/v1/users")

            cors_headers = [
                "access-control-allow-origin",
                "access-control-allow-methods",
                "access-control-allow-headers",
            ]

            missing_headers = []
            for header in cors_headers:
                if header not in response.headers:
                    missing_headers.append(header)

            if missing_headers:
                test.set_failed(f"Missing CORS headers: {missing_headers}")
            else:
                test.set_passed("CORS headers properly configured")

        except Exception as e:
            test.set_failed(f"CORS test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

        # Test 3: Rate limiting
        test = ProductionTestResult("Rate limiting", "security")
        start_time = time.time()

        try:
            # Test rate limiting headers
            response = self.test_client.get("/api/v1/users")

            rate_limit_headers = [
                "x-ratelimit-limit",
                "x-ratelimit-remaining",
                "x-ratelimit-reset",
            ]

            missing_headers = []
            for header in rate_limit_headers:
                if header not in response.headers:
                    missing_headers.append(header)

            if missing_headers:
                test.set_failed(f"Missing rate limit headers: {missing_headers}")
            else:
                test.set_passed("Rate limiting headers present")

        except Exception as e:
            test.set_failed(f"Rate limiting test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

    async def _run_performance_tests(self) -> None:
        """Run performance-related tests"""

        # Test 1: Response time
        test = ProductionTestResult("Response time", "performance")
        start_time = time.time()

        try:
            # Test multiple endpoints
            endpoints = [
                "/api/v1/users",
                "/api/v1/workspaces",
                "/api/v1/icps",
                "/api/v1/health",
            ]

            slow_endpoints = []
            for endpoint in endpoints:
                response_start = time.time()
                response = self.test_client.get(endpoint)
                response_time = (time.time() - response_start) * 1000

                if response_time > self.max_response_time_ms:
                    slow_endpoints.append(f"{endpoint}: {response_time:.2f}ms")

            if slow_endpoints:
                test.set_failed(f"Slow endpoints detected: {slow_endpoints}")
            else:
                test.set_passed("All endpoints within response time limits")

            test.details["slow_endpoints"] = slow_endpoints

        except Exception as e:
            test.set_failed(f"Response time test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

        # Test 2: Memory usage
        test = ProductionTestResult("Memory usage", "performance")
        start_time = time.time()

        try:
            import psutil

            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            if memory_mb > self.max_memory_mb:
                test.set_failed(f"High memory usage: {memory_mb:.2f}MB")
            else:
                test.set_passed(f"Memory usage acceptable: {memory_mb:.2f}MB")

            test.details["memory_mb"] = memory_mb

        except Exception as e:
            test.set_failed(f"Memory usage test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

        # Test 3: Database connection pooling
        test = ProductionTestResult("Database connection pooling", "performance")
        start_time = time.time()

        try:
            manager = get_supabase_production_manager()

            if not manager.client:
                test.set_failed("Database manager not initialized")
            else:
                # Test connection pool stats
                stats = await manager.get_database_stats()
                pool_utilization = stats["connection_pool"]["pool_utilization"]

                if pool_utilization > 0.8:
                    test.set_failed(f"High pool utilization: {pool_utilization:.2%}")
                else:
                    test.set_passed(
                        f"Connection pool utilization acceptable: {pool_utilization:.2%}"
                    )

                test.details.update(stats["connection_pool"])

        except Exception as e:
            test.set_failed(f"Connection pool test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

    async def _run_resilience_tests(self) -> None:
        """Run resilience-related tests"""

        # Test 1: Circuit breaker functionality
        test = ProductionTestResult("Circuit breaker functionality", "resilience")
        start_time = time.time()

        try:
            client = get_resilient_client()

            # Test circuit breaker stats
            stats = client.get_all_stats()

            if not stats:
                test.set_failed("No circuit breakers configured")
            else:
                test.set_passed(f"Circuit breakers active: {list(stats.keys())}")
                test.details["circuit_breakers"] = stats

        except Exception as e:
            test.set_failed(f"Circuit breaker test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

        # Test 2: Error tracking
        test = ProductionTestResult("Error tracking", "resilience")
        start_time = time.time()

        try:
            status = get_health_status()

            if status["status"] == "healthy":
                test.set_passed("Error tracking system healthy")
            else:
                test.set_failed(
                    f"Error tracking issues: {status.get('error', 'Unknown')}"
                )

            test.details.update(status)

        except Exception as e:
            test.set_failed(f"Error tracking test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

        # Test 3: Health check endpoints
        test = ProductionTestResult("Health check endpoints", "resilience")
        start_time = time.time()

        try:
            # Test comprehensive health check
            response = self.test_client.get("/api/v1/health/detailed")

            if response.status_code == 200:
                health_data = response.json()

                if health_data["status"] == "healthy":
                    test.set_passed("Health checks passing")
                else:
                    test.set_failed(
                        f"Health issues detected: {health_data.get('status')}"
                    )

                test.details.update(health_data)
            else:
                test.set_failed(f"Health check returned status {response.status_code}")

        except Exception as e:
            test.set_failed(f"Health check test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

    async def _run_monitoring_tests(self) -> None:
        """Run monitoring-related tests"""

        # Test 1: Metrics availability
        test = ProductionTestResult("Metrics availability", "monitoring")
        start_time = time.time()

        try:
            # Test metrics endpoint
            response = self.test_client.get("/api/v1/health/metrics")

            if response.status_code == 200:
                metrics = response.json()

                required_metrics = [
                    "overall_status",
                    "total_response_time_ms",
                    "check_count",
                ]
                missing_metrics = [m for m in required_metrics if m not in metrics]

                if missing_metrics:
                    test.set_failed(f"Missing metrics: {missing_metrics}")
                else:
                    test.set_passed("All required metrics available")

                test.details.update(metrics)
            else:
                test.set_failed(f"Metrics endpoint returned {response.status_code}")

        except Exception as e:
            test.set_failed(f"Metrics test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

        # Test 2: Logging configuration
        test = ProductionTestResult("Logging configuration", "monitoring")
        start_time = time.time()

        try:
            # Check if structured logging is configured
            import logging

            # Check if we have structured logging configured
            has_structured_logging = any(
                isinstance(handler, logging.StreamHandler)
                for handler in logging.getLogger().handlers
            )

            if has_structured_logging:
                test.set_passed("Logging system configured")
            else:
                test.set_failed("Structured logging not properly configured")

        except Exception as e:
            test.set_failed(f"Logging test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

    async def _run_database_tests(self) -> None:
        """Run database-related tests"""

        # Test 1: Database connectivity
        test = ProductionTestResult("Database connectivity", "database")
        start_time = time.time()

        try:
            manager = get_supabase_production_manager()

            if not manager.client:
                test.set_critical("Database client not initialized")
            else:
                # Test database connection
                health = await manager.test_connection()

                if health["status"] == "healthy":
                    test.set_passed("Database connection healthy")
                else:
                    test.set_critical(
                        f"Database connection issues: {health.get('message')}"
                    )

                test.details.update(health)

        except Exception as e:
            test.set_critical(f"Database test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

        # Test 2: Database performance
        test = ProductionTestResult("Database performance", "database")
        start_time = time.time()

        try:
            manager = get_supabase_production_manager()

            # Test query performance
            start_query = time.time()
            result = manager.client.table("users").select("*").limit(100).execute()
            query_time = (time.time() - start_query) * 1000

            if query_time > 1000:  # 1 second threshold
                test.set_failed(f"Slow query detected: {query_time:.2f}ms")
            else:
                test.set_passed(f"Query performance acceptable: {query_time:.2f}ms")

            test.details["query_time_ms"] = query_time
            test.details["rows_returned"] = len(result.data) if result.data else 0

        except Exception as e:
            test.set_failed(f"Database performance test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

        # Test 3: Row Level Security
        test = ProductionTestResult("Row Level Security", "database")
        start_time = time.time()

        try:
            # Test RLS configuration
            manager = get_supabase_production_manager()

            if manager.config.enable_rls:
                test.set_passed("Row Level Security enabled")
            else:
                test.set_warning("Row Level Security disabled")

            test.details["rls_enabled"] = manager.config.enable_rls

        except Exception as e:
            test.set_failed(f"RLS test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

    async def _run_infrastructure_tests(self) -> None:
        """Run infrastructure-related tests"""

        # Test 1: Redis connectivity
        test = ProductionTestResult("Redis connectivity", "infrastructure")
        start_time = time.time()

        try:
            manager = get_redis_production_manager()

            if not manager.client:
                test.set_critical("Redis client not initialized")
            else:
                # Test Redis connection
                health = await manager.test_connection()

                if health["status"] == "healthy":
                    test.set_passed("Redis connection healthy")
                else:
                    test.set_critical(
                        f"Redis connection issues: {health.get('message')}"
                    )

                test.details.update(health)

        except Exception as e:
            test.set_critical(f"Redis test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

        # Test 2: Environment variables
        test = ProductionTestResult("Environment variables", "infrastructure")
        start_time = time.time()

        try:
            required_vars = [
                "SUPABASE_URL",
                "SUPABASE_SERVICE_ROLE_KEY",
                "UPSTASH_REDIS_URL",
                "UPSTASH_REDIS_TOKEN",
                "ENVIRONMENT",
            ]

            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)

            if missing_vars:
                test.set_critical(
                    f"Missing required environment variables: {missing_vars}"
                )
            else:
                test.set_passed("All required environment variables set")

            test.details["missing_vars"] = missing_vars
            test.details["required_vars"] = required_vars

        except Exception as e:
            test.set_failed(f"Environment variables test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

        # Test 3: Service dependencies
        test = TestResult("Service dependencies", "infrastructure")
        start_time = time.time()

        try:
            # Test external service connectivity
            external_services = [
                ("OpenAI", "https://api.openai.com/v1/models"),
                ("Serper", "https://google.serper.dev/search"),
            ]

            failed_services = []
            for service_name, url in external_services:
                try:
                    response = await self.http_client.get(url, timeout=5)
                    if response.status_code != 200:
                        failed_services.append(
                            f"{service_name}: {response.status_code}"
                        )
                except Exception as e:
                    failed_services.append(f"{service_name}: {str(e)}")

            if failed_services:
                test.set_failed(f"External service issues: {failed_services}")
            else:
                test.set_passed("All external services accessible")

            test.details["failed_services"] = failed_services

        except Exception as e:
            test.set_failed(f"Service dependencies test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

    async def _run_compliance_tests(self) -> None:
        """Run compliance-related tests"""

        # Test 1: Production environment checks
        test = ProductionTestResult("Production environment", "compliance")
        start_time = time.time()

        try:
            env = os.getenv("ENVIRONMENT", "development")

            if env == "production":
                # Check production-specific requirements
                checks = []

                # Check for debug mode
                if os.getenv("DEBUG", "false").lower() == "true":
                    checks.append("Debug mode enabled in production")

                # Check for test mode
                if "test" in os.getenv("APP_NAME", "").lower():
                    checks.append("Test mode detected")

                # Check for mock services
                if os.getenv("MOCK_SERVICES", "false").lower() == "true":
                    checks.append("Mock services enabled")

                if checks:
                    test.set_failed(f"Production compliance issues: {checks}")
                else:
                    test.set_passed("Production environment compliant")

                test.details["environment"] = env
                test.details["compliance_issues"] = checks
            else:
                test.set_passed(f"Environment: {env} (not production)")

        except Exception as e:
            test.set_failed(f"Environment check error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)

        # Test 2: Security headers
        test = ProductionTestResult("Security headers", "compliance")
        start_time = time.time()

        try:
            # Test security headers on API endpoints
            response = self.test_client.get("/api/v1/users")

            security_headers = [
                "x-content-type-options",
                "x-frame-options",
                "x-xss-protection",
                "strict-transport-security",
            ]

            missing_headers = []
            for header in security_headers:
                if header not in response.headers:
                    missing_headers.append(header)

            if missing_headers:
                test.set_warning(f"Missing security headers: {missing_headers}")
            else:
                test.set_passed("Security headers present")

            test.details["missing_headers"] = missing_headers

        except Exception as e:
            test.set_failed(f"Security headers test error: {e}")

        test.duration_ms = (time.time() - start_time) * 1000
        self.results.append(test)


# Test runner function
async def run_production_tests() -> Dict[str, Any]:
    """Run production readiness tests"""
    suite = ProductionTestSuite()
    return await suite.run_all_tests()


# CLI command for running tests
async def main():
    """CLI entry point for production tests"""
    import sys

    command = sys.argv[1] if len(sys.argv) > 1 else "run"

    if command == "run":
        results = await run_production_tests()

        print(f"\n{'='*60}")
        print(f"PRODUCTION READINESS TEST RESULTS")
        print(f"{'='*60}")
        print(f"Status: {results['status'].upper()}")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Critical: {results['critical']}")
        print(f"Duration: {results['duration_seconds']:.2f}s")
        print(f"Timestamp: {results['timestamp']}")

        print(f"\n{'='*60}")
        print("CATEGORY BREAKDOWN:")

        for category, cat_summary in results["categories"].items():
            status = (
                "PASS"
                if cat_summary["critical"] == 0 and cat_summary["failed"] == 0
                else "FAIL"
            )
            print(
                f"{category.upper()}: {status} ({cat_summary['passed']}/{cat_summary['total']})"
            )

        if results["critical"] > 0:
            print(f"\n⚠️  CRITICAL FAILURES:")
            for result in results["results"]:
                if result["critical"]:
                    print(f"  - {result['name']}: {result['message']}")

        if results["failed"] > 0:
            print(f"\n❌ FAILURES:")
            for result in results["results"]:
                if result["status"] == "failed":
                    print(f"  - {result['name']}: {result['message']}")

        print(
            f"\n✅ SUCCESS: {results['passed']}/{results['total_tests']} tests passed"
        )

        # Exit with appropriate code
        if results["critical"] > 0:
            sys.exit(2)  # Critical failures
        elif results["failed"] > 0:
            sys.exit(1)  # Regular failures
        else:
            sys.exit(0)  # All passed

    elif command == "summary":
        results = await run_production_tests()
        print(json.dumps(results, indent=2))

    else:
        print("Usage: python production_tests.py [run|summary]")


if __name__ == "__main__":
    asyncio.run(main())
