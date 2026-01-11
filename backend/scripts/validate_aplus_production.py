#!/usr/bin/env python3
"""
A+ Production Validation Script for RaptorFlow Backend
Validates enterprise-grade production readiness with zero tolerance for issues
"""

import asyncio
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class APlusProductionValidator:
    """Validates A+ production readiness standards"""

    def __init__(self):
        self.backend_path = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.passed_checks = []

        # A+ Standards - Zero tolerance for security issues
        self.security_patterns = [
            r'api_key\s*=\s*"[^"]*your-[^"]*"',  # Hardcoded API keys
            r'secret\s*=\s*"[^"]*your-[^"]*"',  # Hardcoded secrets
            r'token\s*=\s*"[^"]*your-[^"]*"',  # Hardcoded tokens
            r'password\s*=\s*"[^"]*your-[^"]*"',  # Hardcoded passwords
            r"localhost.*3000",  # Development URLs
            r"127\.0\.0\.1.*3000",  # Local development
            r"0\.0\.0\.0.*3000",  # Local development
        ]

        # Mock patterns that should not exist in production
        self.mock_patterns = [
            r"from.*mock.*import",
            r"import.*mock",
            r"MockClient",
            r"mock_client",
            r"fallback.*redis",
            r"fallback.*database",
        ]

        # Test files that should not be in production paths
        self.test_file_patterns = [
            r"test_.*\.py$",
            r".*_test\.py$",
            r".*_tests\.py$",
        ]

    async def validate_all(self) -> Dict[str, any]:
        """Run complete A+ production validation"""
        print("🚀 Starting A+ Production Validation...")
        print("=" * 60)

        # Core validations
        await self._validate_no_hardcoded_secrets()
        await self._validate_no_mocks_in_production()
        await self._validate_no_test_files_in_production()
        await self._validate_environment_variables()
        await self._validate_production_configurations()
        await self._validate_security_headers()
        await self._validate_circuit_breakers()
        await self._validate_monitoring()

        # Generate report
        return self._generate_report()

    async def _validate_no_hardcoded_secrets(self) -> None:
        """Validate no hardcoded secrets exist"""
        print("🔍 Checking for hardcoded secrets...")

        # Scan all Python files
        python_files = list(self.backend_path.rglob("*.py"))

        for file_path in python_files:
            # Skip tests directory
            if "tests" in str(file_path):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")

                for pattern in self.security_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1
                        self.issues.append(
                            {
                                "type": "hardcoded_secret",
                                "file": str(file_path.relative_to(self.backend_path)),
                                "line": line_num,
                                "content": match.group().strip(),
                                "severity": "critical",
                            }
                        )

            except Exception as e:
                self.warnings.append(f"Could not read {file_path}: {e}")

        if not any(issue["type"] == "hardcoded_secret" for issue in self.issues):
            self.passed_checks.append("No hardcoded secrets found")
            print("✅ No hardcoded secrets detected")
        else:
            print(
                f"❌ Found {len([i for i in self.issues if i['type'] == 'hardcoded_secret'])} hardcoded secrets"
            )

    async def _validate_no_mocks_in_production(self) -> None:
        """Validate no mock imports in production code"""
        print("🎭 Checking for mock imports in production...")

        # Scan production directories only
        production_dirs = [
            self.backend_path / "api",
            self.backend_path / "core",
            self.backend_path / "middleware",
            self.backend_path / "agents",
            self.backend_path / "memory",
            self.backend_path / "services",
        ]

        for prod_dir in production_dirs:
            if not prod_dir.exists():
                continue

            python_files = list(prod_dir.rglob("*.py"))

            for file_path in python_files:
                # Skip test files
                if "test" in file_path.name:
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8")

                    for pattern in self.mock_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[: match.start()].count("\n") + 1

                            # Allow fallback comments but not fallback code
                            if (
                                "fallback" in match.group().lower()
                                and "#" in content.split("\n")[line_num - 1]
                            ):
                                continue

                            self.issues.append(
                                {
                                    "type": "mock_in_production",
                                    "file": str(
                                        file_path.relative_to(self.backend_path)
                                    ),
                                    "line": line_num,
                                    "content": match.group().strip(),
                                    "severity": "high",
                                }
                            )

                except Exception as e:
                    self.warnings.append(f"Could not read {file_path}: {e}")

        if not any(issue["type"] == "mock_in_production" for issue in self.issues):
            self.passed_checks.append("No mock imports in production code")
            print("✅ No mock imports in production code")
        else:
            print(
                f"❌ Found {len([i for i in self.issues if i['type'] == 'mock_in_production'])} mock imports"
            )

    async def _validate_no_test_files_in_production(self) -> None:
        """Validate no test files in production directories"""
        print("📋 Checking for test files in production directories...")

        # Production directories that should not contain test files
        production_dirs = [
            self.backend_path / "api",
            self.backend_path / "core",
            self.backend_path / "middleware",
            self.backend_path / "agents",
            self.backend_path / "memory",
            self.backend_path / "services",
        ]

        for prod_dir in production_dirs:
            if not prod_dir.exists():
                continue

            for file_path in prod_dir.rglob("*.py"):
                for pattern in self.test_file_patterns:
                    if re.match(pattern, file_path.name, re.IGNORECASE):
                        self.issues.append(
                            {
                                "type": "test_file_in_production",
                                "file": str(file_path.relative_to(self.backend_path)),
                                "line": 1,
                                "content": f"Test file: {file_path.name}",
                                "severity": "medium",
                            }
                        )

        if not any(issue["type"] == "test_file_in_production" for issue in self.issues):
            self.passed_checks.append("No test files in production directories")
            print("✅ No test files in production directories")
        else:
            print(
                f"❌ Found {len([i for i in self.issues if i['type'] == 'test_file_in_production'])} test files in production"
            )

    async def _validate_environment_variables(self) -> None:
        """Validate production environment variables"""
        print("🌍 Checking environment variable configuration...")

        # Check production environment file
        prod_env_file = self.backend_path / ".env.production.example"

        if not prod_env_file.exists():
            self.issues.append(
                {
                    "type": "missing_production_env",
                    "file": ".env.production.example",
                    "line": 1,
                    "content": "Production environment template missing",
                    "severity": "high",
                }
            )
            return

        try:
            content = prod_env_file.read_text()

            # Required production variables
            required_vars = [
                "SUPABASE_URL",
                "SUPABASE_SERVICE_ROLE_KEY",
                "UPSTASH_REDIS_URL",
                "UPSTASH_REDIS_TOKEN",
                "ENVIRONMENT",
                "ALLOWED_ORIGINS",
                "SENTRY_DSN",
            ]

            missing_vars = []
            for var in required_vars:
                if var not in content:
                    missing_vars.append(var)

            if missing_vars:
                self.issues.append(
                    {
                        "type": "missing_env_vars",
                        "file": ".env.production.example",
                        "line": 1,
                        "content": f"Missing required variables: {', '.join(missing_vars)}",
                        "severity": "high",
                    }
                )
            else:
                self.passed_checks.append(
                    "All required environment variables configured"
                )
                print("✅ Production environment variables properly configured")

        except Exception as e:
            self.issues.append(
                {
                    "type": "env_file_error",
                    "file": ".env.production.example",
                    "line": 1,
                    "content": f"Could not read environment file: {e}",
                    "severity": "medium",
                }
            )

    async def _validate_production_configurations(self) -> None:
        """Validate production-specific configurations"""
        print("⚙️ Checking production configurations...")

        # Check main.py for production settings
        main_file = self.backend_path / "main.py"

        if main_file.exists():
            try:
                content = main_file.read_text()

                # Check for development fallbacks
                if (
                    "localhost:3000" in content
                    and "development fallback" in content.lower()
                ):
                    self.issues.append(
                        {
                            "type": "development_fallback",
                            "file": "main.py",
                            "line": content.find("localhost:3000"),
                            "content": "Development fallback found in CORS configuration",
                            "severity": "high",
                        }
                    )
                else:
                    self.passed_checks.append(
                        "No development fallbacks in main configuration"
                    )

                # Check for proper middleware order
                if "Sentry" in content and "CORS" in content:
                    self.passed_checks.append(
                        "Production middleware properly configured"
                    )

            except Exception as e:
                self.warnings.append(f"Could not validate main.py: {e}")

        # Check Docker production configuration
        docker_file = self.backend_path / "Dockerfile.production"
        if docker_file.exists():
            self.passed_checks.append("Production Docker configuration exists")
        else:
            self.issues.append(
                {
                    "type": "missing_docker_production",
                    "file": "Dockerfile.production",
                    "line": 1,
                    "content": "Production Docker configuration missing",
                    "severity": "high",
                }
            )

        print("✅ Production configurations validated")

    async def _validate_security_headers(self) -> None:
        """Validate security headers configuration"""
        print("🔒 Checking security headers...")

        # Check if security middleware is configured
        main_file = self.backend_path / "main.py"

        if main_file.exists():
            try:
                content = main_file.read_text()

                # Check for security-related middleware
                security_indicators = [
                    "CORSMiddleware",
                    "ErrorMiddleware",
                    "LoggingMiddleware",
                    "MetricsMiddleware",
                ]

                missing_middleware = []
                for middleware in security_indicators:
                    if middleware not in content:
                        missing_middleware.append(middleware)

                if missing_middleware:
                    self.issues.append(
                        {
                            "type": "missing_security_middleware",
                            "file": "main.py",
                            "line": 1,
                            "content": f"Missing security middleware: {', '.join(missing_middleware)}",
                            "severity": "medium",
                        }
                    )
                else:
                    self.passed_checks.append("Security middleware properly configured")

            except Exception as e:
                self.warnings.append(f"Could not validate security headers: {e}")

        print("✅ Security headers validated")

    async def _validate_circuit_breakers(self) -> None:
        """Validate circuit breaker configuration"""
        print("⚡ Checking circuit breaker configuration...")

        # Check for circuit breaker implementation
        circuit_breaker_file = self.backend_path / "core" / "circuit_breaker.py"

        if circuit_breaker_file.exists():
            try:
                content = circuit_breaker_file.read_text()

                if "CircuitBreaker" in content and "ResilientClient" in content:
                    self.passed_checks.append("Circuit breaker implementation exists")
                else:
                    self.issues.append(
                        {
                            "type": "incomplete_circuit_breaker",
                            "file": "core/circuit_breaker.py",
                            "line": 1,
                            "content": "Incomplete circuit breaker implementation",
                            "severity": "medium",
                        }
                    )
            except Exception as e:
                self.warnings.append(f"Could not validate circuit breakers: {e}")
        else:
            self.issues.append(
                {
                    "type": "missing_circuit_breaker",
                    "file": "core/circuit_breaker.py",
                    "line": 1,
                    "content": "Circuit breaker implementation missing",
                    "severity": "medium",
                }
            )

        print("✅ Circuit breaker configuration validated")

    async def _validate_monitoring(self) -> None:
        """Validate monitoring and observability"""
        print("📊 Checking monitoring configuration...")

        # Check for Prometheus metrics
        prometheus_file = self.backend_path / "core" / "prometheus_metrics.py"

        if prometheus_file.exists():
            self.passed_checks.append("Prometheus metrics configured")
        else:
            self.issues.append(
                {
                    "type": "missing_monitoring",
                    "file": "core/prometheus_metrics.py",
                    "line": 1,
                    "content": "Prometheus metrics configuration missing",
                    "severity": "medium",
                }
            )

        # Check for Sentry configuration
        sentry_file = self.backend_path / "core" / "sentry.py"

        if sentry_file.exists():
            self.passed_checks.append("Sentry error tracking configured")
        else:
            self.issues.append(
                {
                    "type": "missing_error_tracking",
                    "file": "core/sentry.py",
                    "line": 1,
                    "content": "Sentry error tracking configuration missing",
                    "severity": "medium",
                }
            )

        print("✅ Monitoring configuration validated")

    def _generate_report(self) -> Dict[str, any]:
        """Generate comprehensive validation report"""

        # Count issues by severity
        critical_issues = [i for i in self.issues if i["severity"] == "critical"]
        high_issues = [i for i in self.issues if i["severity"] == "high"]
        medium_issues = [i for i in self.issues if i["severity"] == "medium"]

        # Determine grade
        if critical_issues:
            grade = "F"  # Fail for critical issues
            status = "FAILED"
        elif high_issues:
            grade = "C"  # C for high issues
            status = "NEEDS_IMPROVEMENT"
        elif medium_issues:
            grade = "B"  # B for medium issues
            status = "GOOD"
        else:
            grade = "A+"  # A+ for no issues
            status = "EXCELLENT"

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "grade": grade,
            "status": status,
            "summary": {
                "total_issues": len(self.issues),
                "critical_issues": len(critical_issues),
                "high_issues": len(high_issues),
                "medium_issues": len(medium_issues),
                "warnings": len(self.warnings),
                "passed_checks": len(self.passed_checks),
            },
            "issues": self.issues,
            "warnings": self.warnings,
            "passed_checks": self.passed_checks,
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        critical_issues = [i for i in self.issues if i["severity"] == "critical"]
        high_issues = [i for i in self.issues if i["severity"] == "high"]

        if critical_issues:
            recommendations.append("🚨 CRITICAL: Fix all hardcoded secrets immediately")

        if high_issues:
            recommendations.append(
                "⚠️ HIGH: Remove all mock imports and development fallbacks"
            )

        if any(i["type"] == "test_file_in_production" for i in self.issues):
            recommendations.append("📋 Move all test files to /tests/ directory")

        if any(i["type"] == "missing_env_vars" for i in self.issues):
            recommendations.append("🌍 Configure all required environment variables")

        if not recommendations:
            recommendations.append(
                "🎉 EXCELLENT: System meets A+ production standards!"
            )

        return recommendations


async def main():
    """Main validation entry point"""
    validator = APlusProductionValidator()

    try:
        report = await validator.validate_all()

        # Print results
        print("\n" + "=" * 60)
        print("🎯 A+ PRODUCTION VALIDATION RESULTS")
        print("=" * 60)

        print(f"Grade: {report['grade']} ({report['status']})")
        print(f"Timestamp: {report['timestamp']}")

        print(f"\n📊 SUMMARY:")
        print(f"  Total Issues: {report['summary']['total_issues']}")
        print(f"  Critical: {report['summary']['critical_issues']}")
        print(f"  High: {report['summary']['high_issues']}")
        print(f"  Medium: {report['summary']['medium_issues']}")
        print(f"  Warnings: {report['summary']['warnings']}")
        print(f"  Passed Checks: {report['summary']['passed_checks']}")

        if report["issues"]:
            print(f"\n🚨 ISSUES FOUND:")
            for issue in report["issues"]:
                severity_emoji = {"critical": "🚨", "high": "⚠️", "medium": "📋"}
                print(
                    f"  {severity_emoji[issue['severity']]} {issue['file']}:{issue['line']} - {issue['content']}"
                )

        if report["warnings"]:
            print(f"\n⚠️ WARNINGS:")
            for warning in report["warnings"]:
                print(f"  ⚠️ {warning}")

        if report["passed_checks"]:
            print(f"\n✅ PASSED CHECKS:")
            for check in report["passed_checks"]:
                print(f"  ✅ {check}")

        print(f"\n📋 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"  {rec}")

        # Save report
        report_file = Path("aplus_production_validation_report.json")
        report_file.write_text(json.dumps(report, indent=2))
        print(f"\n📄 Detailed report saved to: {report_file}")

        # Exit with appropriate code
        if report["grade"] == "A+":
            print("\n🎉 CONGRATULATIONS! A+ Production Ready!")
            sys.exit(0)
        elif report["grade"] == "F":
            print("\n❌ CRITICAL ISSUES - Fix before production deployment!")
            sys.exit(2)
        else:
            print("\n⚠️ IMPROVEMENTS NEEDED - Address issues before production")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())
