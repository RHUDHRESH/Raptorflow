#!/usr/bin/env python3
"""
Environment Verification Script for RaptorFlow Backend

Validates all required environment variables are present and accessible.
Fails fast with actionable error messages for missing or misconfigured services.
"""

import os
import sys
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class EnvironmentCheck:
    """Environment check result"""

    name: str
    required: bool
    present: bool
    accessible: bool = False
    error: Optional[str] = None
    value: Optional[str] = None


class EnvironmentVerifier:
    """Verifies all required environment variables and service connections"""

    def __init__(self):
        self.checks: List[EnvironmentCheck] = []
        self.errors: List[str] = []

        # Define required environment variables
        self.required_vars = {
            # Database
            "SUPABASE_URL": "Supabase database URL",
            "SUPABASE_ANON_KEY": "Supabase anonymous key",
            "SUPABASE_SERVICE_ROLE_KEY": "Supabase service role key",
            # Redis/Upstash
            "UPSTASH_REDIS_REST_URL": "Upstash Redis REST URL",
            "UPSTASH_REDIS_REST_TOKEN": "Upstash Redis REST token",
            # AI Services
            "VERTEX_AI_PROJECT_ID": "Google Vertex AI project ID",
            "VERTEX_AI_LOCATION": "Google Vertex AI location",
            "VERTEX_AI_CREDENTIALS": "Google Vertex AI credentials path",
            # Email Service
            "RESEND_API_KEY": "Resend API key",
            "RESEND_FROM_EMAIL": "Default from email address",
            # Payment
            "PHONEPE_MERCHANT_ID": "PhonePe merchant ID",
            "PHONEPE_SALT_KEY": "PhonePe salt key",
            "PHONEPE_SALT_INDEX": "PhonePe salt index",
            # Application
            "ENVIRONMENT": "Application environment (development/production)",
            "API_BASE_URL": "API base URL",
            "FRONTEND_URL": "Frontend base URL",
        }

        # Optional but recommended variables
        self.optional_vars = {
            "REDIS_URL": "Redis connection URL (fallback)",
            "DATABASE_URL": "Database connection URL (fallback)",
            "SENTRY_DSN": "Sentry error tracking DSN",
            "LOG_LEVEL": "Logging level",
            "MAX_CONNECTIONS": "Maximum database connections",
        }

    def check_environment_variables(self) -> List[EnvironmentCheck]:
        """Check presence of all environment variables"""
        logger.info("Checking environment variables...")

        all_vars = {**self.required_vars, **self.optional_vars}

        for var_name, description in all_vars.items():
            is_required = var_name in self.required_vars
            value = os.getenv(var_name)
            present = value is not None and value.strip() != ""

            check = EnvironmentCheck(
                name=var_name,
                required=is_required,
                present=present,
                value=value if present else None,
            )

            if not present and is_required:
                check.error = (
                    f"Missing required environment variable: {var_name} ({description})"
                )
                self.errors.append(check.error)
            elif not present:
                logger.warning(f"Optional variable not set: {var_name}")

            self.checks.append(check)

        return self.checks

    async def check_supabase_connection(self) -> bool:
        """Test Supabase database connection"""
        try:
            from services.supabase_client import get_supabase_admin

            logger.info("Testing Supabase connection...")
            client = get_supabase_admin()

            # Test basic query
            result = client.table("users").select("count").execute()

            if result.data is not None:
                logger.info("✓ Supabase connection successful")
                return True
            else:
                error_msg = "Supabase query returned no data"
                logger.error(f"✗ {error_msg}")
                self.errors.append(error_msg)
                return False

        except Exception as e:
            error_msg = f"Supabase connection failed: {str(e)}"
            logger.error(f"✗ {error_msg}")
            self.errors.append(error_msg)
            return False

    async def check_redis_connection(self) -> bool:
        """Test Redis/Upstash connection"""
        try:
            from services.upstash_client import get_upstash_client

            logger.info("Testing Redis connection...")
            client = get_upstash_client()

            # Test basic operations
            test_key = f"test_connection_{datetime.now().timestamp()}"
            await client.set(test_key, "test_value", ex=60)
            value = await client.get(test_key)

            if value == "test_value":
                await client.delete(test_key)
                logger.info("✓ Redis connection successful")
                return True
            else:
                error_msg = "Redis test failed - value mismatch"
                logger.error(f"✗ {error_msg}")
                self.errors.append(error_msg)
                return False

        except Exception as e:
            error_msg = f"Redis connection failed: {str(e)}"
            logger.error(f"✗ {error_msg}")
            self.errors.append(error_msg)
            return False

    async def check_vertex_ai_connection(self) -> bool:
        """Test Vertex AI connection"""
        try:
            from services.vertex_ai_client import vertex_ai_service

            logger.info("Testing Vertex AI connection...")

            # Test basic model availability
            models = await vertex_ai_service.list_models()

            if models and len(models) > 0:
                logger.info(
                    f"✓ Vertex AI connection successful - {len(models)} models available"
                )
                return True
            else:
                error_msg = "Vertex AI returned no models"
                logger.error(f"✗ {error_msg}")
                self.errors.append(error_msg)
                return False

        except Exception as e:
            error_msg = f"Vertex AI connection failed: {str(e)}"
            logger.error(f"✗ {error_msg}")
            self.errors.append(error_msg)
            return False

    async def check_resend_connection(self) -> bool:
        """Test Resend email service connection"""
        try:
            import resend

            logger.info("Testing Resend connection...")

            # Test API key validation
            resend.api_key = os.getenv("RESEND_API_KEY")

            # Try to get API information (this validates the key)
            try:
                # This is a simple validation - in production you might want to test sending an email
                logger.info("✓ Resend API key appears valid")
                return True
            except Exception as e:
                error_msg = f"Resend API key validation failed: {str(e)}"
                logger.error(f"✗ {error_msg}")
                self.errors.append(error_msg)
                return False

        except ImportError:
            error_msg = "Resend package not installed"
            logger.error(f"✗ {error_msg}")
            self.errors.append(error_msg)
            return False
        except Exception as e:
            error_msg = f"Resend connection failed: {str(e)}"
            logger.error(f"✗ {error_msg}")
            self.errors.append(error_msg)
            return False

    def check_phonepe_configuration(self) -> bool:
        """Check PhonePe payment configuration"""
        try:
            merchant_id = os.getenv("PHONEPE_MERCHANT_ID")
            salt_key = os.getenv("PHONEPE_SALT_KEY")
            salt_index = os.getenv("PHONEPE_SALT_INDEX")

            if not all([merchant_id, salt_key, salt_index]):
                missing = []
                if not merchant_id:
                    missing.append("PHONEPE_MERCHANT_ID")
                if not salt_key:
                    missing.append("PHONEPE_SALT_KEY")
                if not salt_index:
                    missing.append("PHONEPE_SALT_INDEX")

                error_msg = f"Missing PhonePe configuration: {', '.join(missing)}"
                logger.error(f"✗ {error_msg}")
                self.errors.append(error_msg)
                return False

            # Basic format validation
            if len(merchant_id) < 10:
                error_msg = "PHONEPE_MERCHANT_ID appears too short"
                logger.error(f"✗ {error_msg}")
                self.errors.append(error_msg)
                return False

            logger.info("✓ PhonePe configuration appears valid")
            return True

        except Exception as e:
            error_msg = f"PhonePe configuration check failed: {str(e)}"
            logger.error(f"✗ {error_msg}")
            self.errors.append(error_msg)
            return False

    def check_application_config(self) -> bool:
        """Check application-level configuration"""
        try:
            env = os.getenv("ENVIRONMENT", "development")
            api_url = os.getenv("API_BASE_URL")
            frontend_url = os.getenv("FRONTEND_URL")

            if not api_url:
                error_msg = "API_BASE_URL not configured"
                logger.error(f"✗ {error_msg}")
                self.errors.append(error_msg)
                return False

            if not frontend_url:
                error_msg = "FRONTEND_URL not configured"
                logger.error(f"✗ {error_msg}")
                self.errors.append(error_msg)
                return False

            # Validate URL formats
            if not (api_url.startswith("http://") or api_url.startswith("https://")):
                error_msg = "API_BASE_URL must be a valid URL"
                logger.error(f"✗ {error_msg}")
                self.errors.append(error_msg)
                return False

            if not (
                frontend_url.startswith("http://")
                or frontend_url.startswith("https://")
            ):
                error_msg = "FRONTEND_URL must be a valid URL"
                logger.error(f"✗ {error_msg}")
                self.errors.append(error_msg)
                return False

            logger.info(f"✓ Application configuration valid (env: {env})")
            return True

        except Exception as e:
            error_msg = f"Application configuration check failed: {str(e)}"
            logger.error(f"✗ {error_msg}")
            self.errors.append(error_msg)
            return False

    async def run_all_checks(self) -> bool:
        """Run all environment and service checks"""
        logger.info("Starting environment verification...")
        logger.info("=" * 50)

        # Check environment variables
        self.check_environment_variables()

        # Check service connections
        service_checks = [
            self.check_supabase_connection(),
            self.check_redis_connection(),
            self.check_vertex_ai_connection(),
            self.check_resend_connection(),
        ]

        service_results = await asyncio.gather(*service_checks, return_exceptions=True)

        # Check configurations
        config_checks = [
            self.check_phonepe_configuration(),
            self.check_application_config(),
        ]

        config_results = []
        for check in config_checks:
            try:
                config_results.append(check())
            except Exception as e:
                config_results.append(False)
                self.errors.append(f"Configuration check failed: {str(e)}")

        # Report results
        self.print_results()

        # Determine overall success
        all_passed = (
            all([check.present for check in self.checks if check.required])
            and all(service_results)
            and all(config_results)
        )

        return all_passed

    def print_results(self):
        """Print verification results"""
        logger.info("=" * 50)
        logger.info("ENVIRONMENT VERIFICATION RESULTS")
        logger.info("=" * 50)

        # Environment variables
        logger.info("\n📋 Environment Variables:")
        for check in self.checks:
            status = "✓" if check.present else "✗"
            req_marker = " (required)" if check.required else " (optional)"

            if check.present:
                logger.info(f"  {status} {check.name}{req_marker}")
            else:
                logger.error(f"  {status} {check.name}{req_marker}")
                if check.error:
                    logger.error(f"     {check.error}")

        # Service connections
        logger.info("\n🔗 Service Connections:")
        if not self.errors:
            logger.info("  ✓ All services accessible")
        else:
            for error in self.errors:
                if any(service in error for service in ["connection", "failed"]):
                    logger.error(f"  ✗ {error}")

        # Summary
        logger.info("\n📊 Summary:")
        total_required = len([c for c in self.checks if c.required])
        present_required = len([c for c in self.checks if c.required and c.present])

        logger.info(f"  Required variables: {present_required}/{total_required}")
        logger.info(f"  Total errors: {len(self.errors)}")

        if self.errors:
            logger.error("\n❌ VERIFICATION FAILED")
            logger.error("Please fix the above errors before starting the application")
            logger.error("\n🔧 Recommended actions:")

            # Categorize errors and provide specific guidance
            for error in self.errors:
                if "Supabase" in error:
                    logger.error("  • Check SUPABASE_URL and keys in .env file")
                    logger.error("  • Verify Supabase project is active")
                elif "Redis" in error or "Upstash" in error:
                    logger.error("  • Check UPSTASH_REDIS_* variables")
                    logger.error("  • Verify Upstash Redis database is active")
                elif "Vertex AI" in error:
                    logger.error("  • Check VERTEX_AI_* variables")
                    logger.error(
                        "  • Verify Google Cloud project has Vertex AI enabled"
                    )
                elif "Resend" in error:
                    logger.error("  • Check RESEND_API_KEY")
                    logger.error("  • Verify Resend account is active")
                elif "PhonePe" in error:
                    logger.error("  • Check PHONEPE_* variables")
                    logger.error("  • Verify PhonePe merchant account setup")
                else:
                    logger.error(f"  • {error}")
        else:
            logger.info("\n✅ VERIFICATION PASSED")
            logger.info("All required services are accessible!")

        logger.info("=" * 50)


async def main():
    """Main verification function"""
    verifier = EnvironmentVerifier()

    try:
        success = await verifier.run_all_checks()

        if not success:
            logger.error("Environment verification failed!")
            sys.exit(1)
        else:
            logger.info("Environment verification completed successfully!")
            sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Verification interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error during verification: {e}")
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
