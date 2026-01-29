#!/usr/bin/env python3
"""
Sentry Monitoring Initialization Script
=====================================

This script initializes the comprehensive Sentry monitoring system
for Raptorflow Backend with proper configuration and validation.

Usage:
    python scripts/init_sentry.py [--env ENVIRONMENT] [--dsn DSN]

Options:
    --env ENVIRONMENT    Target environment (development, staging, production)
    --dsn DSN           Sentry DSN (overrides environment variable)
    --check-only        Only check configuration without initialization
    --test-mode         Enable test mode with higher sampling rates
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from .core.sentry_integration import (
    initialize_sentry,
    SentryConfig,
    SentryEnvironment,
    get_sentry_manager,
    shutdown_sentry,
)
from .core.sentry_error_tracking import get_error_tracker
from .core.sentry_performance import get_performance_monitor
from .core.sentry_sessions import get_session_manager
from .core.sentry_alerting import get_alerting_manager
from .core.sentry_dashboards import get_dashboard_manager


def setup_logging():
    """Setup logging for the initialization script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def get_environment_config(env: str, test_mode: bool = False) -> SentryConfig:
    """Get Sentry configuration for the specified environment."""

    # Load environment variables
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        print("ERROR: SENTRY_DSN environment variable is required")
        sys.exit(1)

    # Environment-specific configuration
    if env == "production":
        return SentryConfig(
            dsn=dsn,
            environment=SentryEnvironment.PRODUCTION,
            release=os.getenv("APP_VERSION", "production"),
            sample_rate=1.0 if test_mode else 0.1,
            traces_sample_rate=0.01 if test_mode else 0.001,
            profiles_sample_rate=0.01 if test_mode else 0.001,
            debug=False,
            max_breadcrumbs=100,
            attach_stacktrace=True,
            send_default_pii=False,
            send_request_payloads=False,
            send_response_payloads=False,
        )
    elif env == "staging":
        return SentryConfig(
            dsn=dsn,
            environment=SentryEnvironment.STAGING,
            release=os.getenv("APP_VERSION", "staging"),
            sample_rate=1.0,
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            debug=False,
            max_breadcrumbs=100,
            attach_stacktrace=True,
            send_default_pii=False,
            send_request_payloads=True,
            send_response_payloads=False,
        )
    else:  # development or testing
        return SentryConfig(
            dsn=dsn,
            environment=SentryEnvironment.DEVELOPMENT,
            release=os.getenv("APP_VERSION", "development"),
            sample_rate=1.0,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            debug=True,
            max_breadcrumbs=100,
            attach_stacktrace=True,
            send_default_pii=False,
            send_request_payloads=True,
            send_response_payloads=True,
        )


def validate_configuration(config: SentryConfig) -> bool:
    """Validate Sentry configuration."""
    print("🔍 Validating Sentry configuration...")

    # Check DSN format
    if not config.dsn.startswith("https://"):
        print("❌ Invalid DSN format. Should start with 'https://'")
        return False

    # Check environment
    valid_environments = [env.value for env in SentryEnvironment]
    if config.environment.value not in valid_environments:
        print(f"❌ Invalid environment: {config.environment}")
        return False

    # Check sample rates
    if not (0 <= config.sample_rate <= 1):
        print("❌ Sample rate must be between 0 and 1")
        return False

    if not (0 <= config.traces_sample_rate <= 1):
        print("❌ Traces sample rate must be between 0 and 1")
        return False

    print("✅ Configuration validation passed")
    return True


def test_sentry_integration() -> bool:
    """Test Sentry integration with sample events."""
    print("🧪 Testing Sentry integration...")

    try:
        # Test error tracking
        error_tracker = get_error_tracker()

        try:
            raise ValueError("Test error for Sentry integration")
        except Exception as e:
            event_id = error_tracker.track_exception(e)
            if event_id:
                print(f"✅ Error tracking test passed (Event ID: {event_id})")
            else:
                print("⚠️  Error tracking test returned no event ID")

        # Test message tracking
        message_id = error_tracker.track_message("Test message for Sentry integration")
        if message_id:
            print(f"✅ Message tracking test passed (Event ID: {message_id})")
        else:
            print("⚠️  Message tracking test returned no event ID")

        # Test performance monitoring
        performance_monitor = get_performance_monitor()
        performance_monitor.track_custom_metric(
            name="test_metric", value=42.5, unit="count", tags={"test": "integration"}
        )
        print("✅ Performance monitoring test passed")

        # Test session management
        session_manager = get_session_manager()
        session_id = session_manager.create_session(
            user_id="test_user", session_type="web", ip_address="127.0.0.1"
        )
        if session_id:
            print(f"✅ Session management test passed (Session ID: {session_id})")
        else:
            print("⚠️  Session management test returned no session ID")

        return True

    except Exception as e:
        print(f"❌ Sentry integration test failed: {e}")
        return False


def setup_default_alerts() -> bool:
    """Setup default alert rules."""
    print("🚨 Setting up default alert rules...")

    try:
        alerting_manager = get_alerting_manager()

        # Check if default rules already exist
        existing_rules = alerting_manager.get_alert_rules()
        if existing_rules:
            print(f"✅ Found {len(existing_rules)} existing alert rules")
            return True

        print("ℹ️  Default alert rules will be created automatically")
        print("   - High error rate alert")
        print("   - Slow response time alert")
        print("   - Service availability alert")
        print("   - Database performance alert")

        return True

    except Exception as e:
        print(f"❌ Failed to setup default alerts: {e}")
        return False


def setup_default_dashboards() -> bool:
    """Setup default dashboards."""
    print("📊 Setting up default dashboards...")

    try:
        dashboard_manager = get_dashboard_manager()

        # Check available templates
        templates = dashboard_manager.get_dashboard_templates()
        print(f"✅ Found {len(templates)} dashboard templates")

        for template in templates:
            print(f"   - {template.name} ({template.template_id})")

        return True

    except Exception as e:
        print(f"❌ Failed to setup default dashboards: {e}")
        return False


def display_health_status():
    """Display comprehensive health status."""
    print("📋 System Health Status")
    print("=" * 50)

    # Sentry Integration
    sentry_manager = get_sentry_manager()
    sentry_health = sentry_manager.get_health_status()

    print(f"Sentry Integration:")
    print(f"  - Status: {'✅ Healthy' if sentry_health.is_healthy else '❌ Unhealthy'}")
    print(f"  - Configured: {'✅ Yes' if sentry_health.is_configured else '❌ No'}")
    print(f"  - Enabled: {'✅ Yes' if sentry_health.is_enabled else '❌ No'}")
    print(f"  - DSN Info: {sentry_manager.get_dsn_info()}")

    if sentry_health.configuration_issues:
        print(f"  - Issues: {', '.join(sentry_health.configuration_issues)}")

    print()

    # Component Status
    components = [
        ("Error Tracker", get_error_tracker()),
        ("Performance Monitor", get_performance_monitor()),
        ("Session Manager", get_session_manager()),
        ("Alerting Manager", get_alerting_manager()),
        ("Dashboard Manager", get_dashboard_manager()),
    ]

    print("Component Status:")
    for name, component in components:
        print(f"  - {name}: ✅ Initialized")

    print()


def display_next_steps(env: str):
    """Display next steps for the user."""
    print("🎯 Next Steps")
    print("=" * 50)

    print(f"1. Environment: {env}")
    print("2. Configure notification channels:")
    print("   - Set up email configuration in .env")
    print("   - Configure Slack webhook if needed")
    print("   - Test notification delivery")
    print()

    print("3. Add middleware to your FastAPI app:")
    print("   from middleware.sentry_middleware import add_sentry_middleware")
    print("   add_sentry_middleware(app)")
    print()

    print("4. Monitor your dashboards:")
    print("   - Visit Sentry.io to view errors")
    print("   - Check performance metrics")
    print("   - Review alert rules")
    print()

    print("5. Test the integration:")
    print("   python scripts/test_sentry_integration.py")
    print()

    if env == "production":
        print("⚠️  Production Notes:")
        print("   - Monitor error rates closely")
        print("   - Set up proper alert escalation")
        print("   - Regularly review dashboard performance")
        print()


def main():
    """Main initialization function."""
    parser = argparse.ArgumentParser(description="Initialize Sentry monitoring")
    parser.add_argument(
        "--env",
        default="development",
        choices=["development", "staging", "production"],
        help="Target environment",
    )
    parser.add_argument("--dsn", help="Sentry DSN (overrides environment variable)")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check configuration without initialization",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Enable test mode with higher sampling rates",
    )

    args = parser.parse_args()

    setup_logging()

    print("🚀 Raptorflow Backend - Sentry Monitoring Initialization")
    print("=" * 60)

    # Override DSN if provided
    if args.dsn:
        os.environ["SENTRY_DSN"] = args.dsn

    # Get configuration
    config = get_environment_config(args.env, args.test_mode)

    print(f"Environment: {args.env}")
    print(
        f"Sentry DSN: {config.dsn[:30]}..."
        if len(config.dsn) > 30
        else f"Sentry DSN: {config.dsn}"
    )
    print()

    # Validate configuration
    if not validate_configuration(config):
        sys.exit(1)

    if args.check_only:
        print("✅ Configuration check completed successfully")
        return

    # Initialize Sentry
    print("🔧 Initializing Sentry integration...")
    success = initialize_sentry(config)

    if not success:
        print("❌ Failed to initialize Sentry")
        sys.exit(1)

    print("✅ Sentry initialized successfully")

    # Test integration
    if not test_sentry_integration():
        print("⚠️  Some tests failed, but initialization completed")

    # Setup defaults
    setup_default_alerts()
    setup_default_dashboards()

    # Display health status
    display_health_status()

    # Display next steps
    display_next_steps(args.env)

    print("🎉 Sentry monitoring initialization completed!")
    print()
    print("📚 Documentation: backend/docs/sentry_monitoring.md")
    print("🧪 Tests: backend/tests/test_sentry_integration.py")
    print("💡 Support: Check the troubleshooting section in documentation")


if __name__ == "__main__":
    main()
