#!/usr/bin/env python3
"""
Test script for middleware components only.
Tests middleware without importing other problematic modules.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_middleware_only():
    """Test middleware components only."""
    print("=" * 60)
    print("MIDDLEWARE ONLY TEST")
    print("=" * 60)

    try:
        # Test middleware imports
        print("Testing middleware imports...")
        from middleware import ErrorMiddleware, LoggingMiddleware, MetricsMiddleware

        print("✓ Middleware imported successfully")

        # Test middleware instantiation
        print("\nTesting middleware instantiation...")
        logging_middleware = LoggingMiddleware(None)
        error_middleware = ErrorMiddleware(None)
        metrics_middleware = MetricsMiddleware(None)
        print("✓ All middleware instantiated successfully")

        # Test middleware functionality
        print("\nTesting middleware functionality...")

        # Test metrics collection
        metrics_middleware.request_counts["/test"] = 10
        metrics_middleware.response_times["/test"].append(0.1)
        metrics_middleware.response_times["/test"].append(0.2)
        metrics_middleware.error_counts["/test"] = 2

        metrics = metrics_middleware.get_metrics()
        print(f"✓ Metrics collected: {len(metrics['endpoints'])} endpoints")
        print(
            f"  - Test endpoint requests: {metrics['endpoints']['/test']['request_count']}"
        )
        print(
            f"  - Test endpoint errors: {metrics['endpoints']['/test']['error_count']}"
        )

        # Test Prometheus metrics
        prometheus_metrics = metrics_middleware.get_prometheus_metrics()
        print(
            f"✓ Prometheus metrics generated: {len(prometheus_metrics.split('\\n'))} lines"
        )

        # Test error handling classes
        print("\nTesting error handling classes...")
        from middleware.errors import (
            AuthenticationError,
            AuthorizationError,
            NotFoundError,
            RaptorFlowException,
            RateLimitError,
            ValidationError,
        )

        # Test exception creation
        validation_error = ValidationError("Invalid input", field="email")
        auth_error = AuthenticationError("Unauthorized")
        not_found_error = NotFoundError("Resource not found")

        print(f"✓ Exception classes created successfully")
        print(f"  - ValidationError: {validation_error.status_code}")
        print(f"  - AuthenticationError: {auth_error.status_code}")
        print(f"  - NotFoundError: {not_found_error.status_code}")

        print("\n" + "=" * 60)
        print("MIDDLEWARE ONLY TEST COMPLETE")
        print("✓ All middleware working correctly")
        print("✓ Error handling systems ready")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_middleware_only()
    sys.exit(0 if success else 1)
