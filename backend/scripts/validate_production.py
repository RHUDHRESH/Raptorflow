#!/usr/bin/env python3
"""
Production validation script for Raptorflow.

Validates that all critical services are configured and working
without any mock data or fallbacks.
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.gcp import GCPClient
from infrastructure.secrets import SecretsManager
from infrastructure.storage import CloudStorage
from monitoring.health import HealthAggregator

from .config.settings import get_settings
from .redis.client import RedisClient
from .redis.config import RedisConfig, validate_redis_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionValidator:
    """Validates production readiness."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []

    def log_error(self, message: str):
        """Log an error."""
        self.errors.append(message)
        logger.error(f"Γ¥î {message}")

    def log_warning(self, message: str):
        """Log a warning."""
        self.warnings.append(message)
        logger.warning(f"ΓÜá∩╕Å {message}")

    def log_success(self, message: str):
        """Log a success."""
        self.successes.append(message)
        logger.info(f"Γ£à {message}")

    def validate_environment_variables(self) -> bool:
        """Validate required environment variables."""
        logger.info("Validating environment variables...")

        required_vars = [
            "UPSTASH_REDIS_URL",
            "UPSTASH_REDIS_TOKEN",
            "SUPABASE_URL",
            "SUPABASE_SERVICE_ROLE_KEY",
            "GCP_PROJECT_ID",
            "GEMINI_API_KEY",
        ]

        all_valid = True

        for var in required_vars:
            value = os.getenv(var)
            if not value:
                self.log_error(f"Required environment variable {var} is not set")
                all_valid = False
            elif value.startswith("your-") or value.startswith("mock://"):
                self.log_error(f"Environment variable {var} has placeholder value")
                all_valid = False
            else:
                self.log_success(f"Environment variable {var} is configured")

        # Check production flags
        if os.getenv("ENVIRONMENT") != "production":
            self.log_warning("ENVIRONMENT is not set to 'production'")

        if os.getenv("MOCK_REDIS", "false").lower() == "true":
            self.log_error("MOCK_REDIS is enabled in production")
            all_valid = False

        return all_valid

    async def validate_redis_connection(self) -> bool:
        """Validate Redis connection."""
        logger.info("Validating Redis connection...")

        try:
            client = RedisClient()

            # Test basic connectivity
            ping_result = await client.ping()
            if not ping_result:
                self.log_error("Redis ping failed")
                return False

            self.log_success("Redis connection established")

            # Test basic operations
            test_key = "raptorflow:validation:test"
            await client.set(test_key, "test_value", ex=60)
            retrieved_value = await client.get(test_key)

            if retrieved_value != "test_value":
                self.log_error("Redis read/write test failed")
                return False

            await client.delete(test_key)
            self.log_success("Redis operations working correctly")

            return True

        except Exception as e:
            self.log_error(f"Redis validation failed: {str(e)}")
            return False

    async def validate_supabase_connection(self) -> bool:
        """Validate Supabase connection."""
        logger.info("Validating Supabase connection...")

        try:
            from supabase import create_client

            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

            if not supabase_url or not supabase_key:
                self.log_error("Supabase credentials not configured")
                return False

            client = create_client(supabase_url, supabase_key)

            # Test basic connectivity with a simple query
            response = client.table("workspaces").select("id").limit(1).execute()

            if response is None:
                self.log_error("Supabase query failed")
                return False

            self.log_success("Supabase connection established")
            return True

        except Exception as e:
            self.log_error(f"Supabase validation failed: {str(e)}")
            return False

    async def validate_gcp_services(self) -> bool:
        """Validate GCP services."""
        logger.info("Validating GCP services...")

        try:
            gcp_client = GCPClient()
            project_id = gcp_client.get_project_id()

            if not project_id:
                self.log_error("GCP project ID not available")
                return False

            self.log_success(f"GCP project {project_id} accessible")

            # Test Cloud Storage
            storage = CloudStorage()
            # Note: We don't test actual upload to avoid costs

            self.log_success("GCP services configured")
            return True

        except Exception as e:
            self.log_error(f"GCP validation failed: {str(e)}")
            return False

    async def validate_health_checks(self) -> bool:
        """Validate health check endpoints."""
        logger.info("Validating health checks...")

        try:
            health_aggregator = HealthAggregator()
            health_report = await health_aggregator.full_health_check()

            if health_report.get("status") != "healthy":
                self.log_warning("Some health checks are not passing")

            self.log_success("Health checks are functional")
            return True

        except Exception as e:
            self.log_error(f"Health check validation failed: {str(e)}")
            return False

    def validate_no_mock_imports(self) -> bool:
        """Validate no mock imports are present."""
        logger.info("Validating no mock imports...")

        redis_client_path = os.path.join(
            os.path.dirname(__file__), "..", "redis", "client.py"
        )

        try:
            with open(redis_client_path, "r") as f:
                content = f.read()

            if "mock_client" in content.lower():
                self.log_error("Mock client imports found in production code")
                return False

            if "UPSTASH_AVAILABLE" in content:
                self.log_error("Fallback logic found in production code")
                return False

            self.log_success("No mock imports found")
            return True

        except Exception as e:
            self.log_error(f"Mock import validation failed: {str(e)}")
            return False

    def validate_configuration(self) -> bool:
        """Validate Redis configuration."""
        logger.info("Validating Redis configuration...")

        try:
            if not validate_redis_config():
                self.log_error("Redis configuration validation failed")
                return False

            config = RedisConfig()

            if config.MOCK_REDIS:
                self.log_error("Mock Redis is enabled")
                return False

            if config.DEBUG_MODE:
                self.log_warning("Debug mode is enabled")

            self.log_success("Redis configuration is valid")
            return True

        except Exception as e:
            self.log_error(f"Configuration validation failed: {str(e)}")
            return False

    async def run_all_validations(self) -> Dict[str, Any]:
        """Run all production validations."""
        logger.info("Starting production validation...")

        results = {
            "environment": self.validate_environment_variables(),
            "configuration": self.validate_configuration(),
            "no_mocks": self.validate_no_mock_imports(),
        }

        # Async validations
        results["redis"] = await self.validate_redis_connection()
        results["supabase"] = await self.validate_supabase_connection()
        results["gcp"] = await self.validate_gcp_services()
        results["health"] = await self.validate_health_checks()

        # Summary
        total_checks = len(results)
        passed_checks = sum(1 for v in results.values() if v)

        logger.info(
            f"Validation complete: {passed_checks}/{total_checks} checks passed"
        )

        return {
            "results": results,
            "summary": {
                "total": total_checks,
                "passed": passed_checks,
                "failed": total_checks - passed_checks,
                "success_rate": (passed_checks / total_checks) * 100,
            },
            "errors": self.errors,
            "warnings": self.warnings,
            "successes": self.successes,
        }

    def print_summary(self, validation_results: Dict[str, Any]):
        """Print validation summary."""
        summary = validation_results["summary"]

        print("\n" + "=" * 60)
        print("PRODUCTION VALIDATION SUMMARY")
        print("=" * 60)

        print(f"\nOverall Result: {summary['passed']}/{summary['total']} checks passed")
        print(f"Success Rate: {summary['success_rate']:.1f}%")

        if self.errors:
            print(f"\nΓ¥î ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\nΓÜá∩╕Å WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        if self.successes:
            print(f"\nΓ£à SUCCESSES ({len(self.successes)}):")
            for success in self.successes:
                print(f"  - {success}")

        print("\n" + "=" * 60)

        # Exit code
        if summary["failed"] > 0:
            print("≡ƒÜ¿ PRODUCTION NOT READY - Fix errors before deploying")
            sys.exit(1)
        else:
            print("≡ƒÄë PRODUCTION READY - All checks passed")
            sys.exit(0)


async def main():
    """Main validation function."""
    validator = ProductionValidator()
    results = await validator.run_all_validations()
    validator.print_summary(results)


if __name__ == "__main__":
    asyncio.run(main())
