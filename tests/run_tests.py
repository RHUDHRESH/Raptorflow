"""
Main test runner and test discovery
"""

import os
import sys
from pathlib import Path

import pytest

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Run the test suite"""
    # Define test directories
    test_dirs = [
        "tests/db",
        "tests/auth",
        "tests/api",
        "tests/services",
        "tests/integration",
    ]

    # Check if test directories exist
    existing_test_dirs = []
    for test_dir in test_dirs:
        if (project_root / test_dir).exists():
            existing_test_dirs.append(test_dir)

    if not existing_test_dirs:
        print("No test directories found!")
        return

    print(f"Running tests in: {', '.join(existing_test_dirs)}")

    # Configure pytest arguments
    pytest_args = [
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker enforcement
        "--disable-warnings",  # Disable warnings
        "--cov=backend",  # Coverage for backend module
        "--cov-report=html",  # HTML coverage report
        "--cov-report=term-missing",  # Coverage summary
        "--cov-fail-under=80",  # Fail if coverage below 80%
    ]

    # Add test directories
    for test_dir in existing_test_dirs:
        pytest_args.append(test_dir)

    # Run pytest
    exit_code = pytest.main(pytest_args)

    return exit_code


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
