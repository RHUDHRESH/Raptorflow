#!/usr/bin/env python3
"""
Test runner for RaptorFlow backend tests.
Provides comprehensive test execution and reporting.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


class TestRunner:
    """Comprehensive test runner for RaptorFlow backend."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / "backend" / "tests"
        self.pytest_config = self.tests_dir / "pytest.ini"

    def run_all_tests(
        self, coverage: bool = True, html_report: bool = True
    ) -> Dict[str, Any]:
        """Run all tests with comprehensive reporting."""
        print("🚀 Running all RaptorFlow backend tests...")

        cmd = ["python", "-m", "pytest"]

        # Add coverage if requested
        if coverage:
            cmd.extend(
                [
                    "--cov=backend",
                    "--cov-report=term-missing",
                    "--cov-report=html",
                    "--cov-report=xml",
                    "--cov-fail-under=80",
                ]
            )

        # Add HTML report if requested
        if html_report:
            cmd.extend(["--html=reports/html", "--self-contained-html"])

        # Add pytest config
        if self.pytest_config.exists():
            cmd.extend(["-c", str(self.pytest_config)])

        # Add test directory
        cmd.append(str(self.tests_dir))

        # Run tests
        result = subprocess.run(
            cmd, cwd=self.project_root, capture_output=True, text=True
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests only."""
        print("🧪 Running unit tests...")

        cmd = [
            "python",
            "-m",
            "pytest",
            "-m",
            "unit",
            str(self.tests_dir / "test_unit.py"),
            "-v",
        ]

        result = subprocess.run(
            cmd, cwd=self.project_root, capture_output=True, text=True
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests only."""
        print("🔗 Running integration tests...")

        cmd = [
            "python",
            "-m",
            "pytest",
            "-m",
            "integration",
            str(self.tests_dir / "test_integration.py"),
            "-v",
        ]

        result = subprocess.run(
            cmd, cwd=self.project_root, capture_output=True, text=True
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests only."""
        print("⚡ Running performance tests...")

        cmd = [
            "python",
            "-m",
            "pytest",
            "-m",
            "performance",
            str(self.tests_dir / "test_performance.py"),
            "-v",
            "--durations=10",
        ]

        result = subprocess.run(
            cmd, cwd=self.project_root, capture_output=True, text=True
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

    def run_e2e_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests only."""
        print("🎯 Running end-to-end tests...")

        cmd = [
            "python",
            "-m",
            "pytest",
            "-m",
            "e2e",
            str(self.tests_dir / "test_e2e.py"),
            "-v",
            "--durations=30",
        ]

        result = subprocess.run(
            cmd, cwd=self.project_root, capture_output=True, text=True
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

    def run_smoke_tests(self) -> Dict[str, Any]:
        """Run smoke tests for quick validation."""
        print("💨 Running smoke tests...")

        cmd = [
            "python",
            "-m",
            "pytest",
            "-m",
            "smoke",
            "-k",
            "test_smoke",
            str(self.tests_dir),
            "-v",
            "--maxfail=5",
        ]

        result = subprocess.run(
            cmd, cwd=self.project_root, capture_output=True, text=True
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

    def run_specific_test(self, test_path: str) -> Dict[str, Any]:
        """Run a specific test file or test function."""
        print(f"🎯 Running specific test: {test_path}")

        cmd = ["python", "-m", "pytest", "-v", test_path]

        result = subprocess.run(
            cmd, cwd=self.project_root, capture_output=True, text=True
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

    def generate_coverage_report(self) -> Dict[str, Any]:
        """Generate coverage report."""
        print("📊 Generating coverage report...")

        cmd = ["python", "-m", "coverage", "report", "-m", "html", "-d", "backend"]

        result = subprocess.run(
            cmd, cwd=self.project_root, capture_output=True, text=True
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

    def check_test_dependencies(self) -> Dict[str, Any]:
        """Check if all test dependencies are available."""
        print("🔍 Checking test dependencies...")

        dependencies = [
            ("pytest", "pytest --version"),
            ("pytest-asyncio", "pytest-asyncio --version"),
            ("pytest-cov", "pytest-cov --version"),
            ("coverage", "coverage --version"),
        ]

        missing_deps = []

        for dep, check_cmd in dependencies:
            try:
                result = subprocess.run(check_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    missing_deps.append(dep)
            except FileNotFoundError:
                missing_deps.append(dep)

        return {
            "all_available": len(missing_deps) == 0,
            "missing": missing_deps,
            "installed": [dep for dep, _ in dependencies if dep not in missing_deps],
        }

    def cleanup_test_artifacts(self) -> Dict[str, Any]:
        """Clean up test artifacts and temporary files."""
        print("🧹 Cleaning up test artifacts...")

        artifacts = [
            ".coverage",
            ".pytest_cache",
            "htmlcov",
            "reports",
            "*.pyc",
            "__pycache__",
        ]

        cleaned = []

        for artifact in artifacts:
            artifact_path = self.project_root / artifact
            if artifact_path.exists():
                if artifact_path.is_dir():
                    import shutil

                    shutil.rmtree(artifact_path)
                else:
                    artifact_path.unlink()
                cleaned.append(str(artifact_path))

        return {"cleaned": cleaned, "success": True}


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description="RaptorFlow Backend Test Runner")

    parser.add_argument("--all", action="store_true", help="Run all tests")

    parser.add_argument("--unit", action="store_true", help="Run unit tests only")

    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests only"
    )

    parser.add_argument(
        "--performance", action="store_true", help="Run performance tests only"
    )

    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests only")

    parser.add_argument("--smoke", action="store_true", help="Run smoke tests only")

    parser.add_argument(
        "--coverage", action="store_true", default=True, help="Generate coverage report"
    )

    parser.add_argument(
        "--no-coverage", action="store_true", help="Skip coverage report"
    )

    parser.add_argument("--clean", action="store_true", help="Clean up test artifacts")

    parser.add_argument(
        "--check-deps", action="store_true", help="Check test dependencies"
    )

    parser.add_argument("--test", type=str, help="Run specific test file or function")

    parser.add_argument(
        "--report", action="store_true", help="Generate coverage report only"
    )

    args = parser.parse_args()

    # Initialize test runner
    runner = TestRunner()

    # Check dependencies if requested
    if args.check_deps:
        deps_result = runner.check_test_dependencies()
        if not deps_result["all_available"]:
            print("❌ Missing dependencies:")
            for dep in deps_result["missing"]:
                print(f"  - {dep}")
            print("\nInstall missing dependencies:")
            print("pip install " + " ".join(deps_result["missing"]))
            sys.exit(1)
        else:
            print("✅ All test dependencies are installed")

    # Clean artifacts if requested
    if args.clean:
        runner.cleanup_test_artifacts()
        return

    # Generate coverage report only if requested
    if args.report:
        coverage_result = runner.generate_coverage_report()
        if coverage_result["success"]:
            print("✅ Coverage report generated successfully")
        else:
            print("❌ Failed to generate coverage report")
        return

    # Run specific test if requested
    if args.test:
        result = runner.run_specific_test(args.test)
        print(result["stdout"])
        if result["stderr"]:
            print(result["stderr"])
        sys.exit(result["exit_code"])

    # Determine which tests to run
    coverage = args.coverage and not args.no_coverage

    if args.all:
        result = runner.run_all_tests(coverage=coverage)
    elif args.unit:
        result = runner.run_unit_tests()
    elif args.integration:
        result = runner.run_integration_tests()
    elif args.performance:
        result = runner.run_performance_tests()
    elif args.e2e:
        result = runner.run_e2e_tests()
    elif args.smoke:
        result = runner.run_smoke_tests()
    else:
        # Default: run smoke tests
        print("No test type specified. Running smoke tests...")
        result = runner.run_smoke_tests()

    # Print results
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(result["stdout"])

    if result["stderr"]:
        print("\nSTDERR:")
        print(result["stderr"])

    print(f"\nExit code: {result['exit_code']}")

    if result["success"]:
        print("✅ Tests completed successfully!")
    else:
        print("❌ Tests failed!")

    # Generate coverage report if coverage was enabled
    if coverage and result["success"]:
        print("\n📊 Generating coverage report...")
        coverage_result = runner.generate_coverage_report()
        if coverage_result["success"]:
            print("✅ Coverage report generated successfully")
        else:
            print("❌ Failed to generate coverage report")

    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()
