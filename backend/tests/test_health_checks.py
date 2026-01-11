"""
Test file to verify health checks detect issues correctly.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Import health check components
from monitoring.health_checks import (
    CheckType,
    HealthCheck,
    HealthChecker,
    HealthCheckResult,
    HealthStatus,
    get_health_checker,
)

logger = logging.getLogger(__name__)


class TestHealthChecks:
    """Test suite for health check functionality."""

    def __init__(self):
        self.test_results = {}
        self.health_checker = None
        self.test_checks = []

    async def run_all_tests(self):
        """Run all health check tests."""
        logger.info("Starting health check tests")

        # Initialize health checker
        await self._initialize_health_checker()

        # Test health check registration
        await self._test_health_check_registration()

        # Test healthy checks
        await self._test_healthy_checks()

        # Test warning checks
        await self._test_warning_checks()

        # Test critical checks
        await self._test_critical_checks()

        # Test check execution
        await self._test_check_execution()

        # Test health report generation
        await self._test_health_report()

        # Test check dependencies
        await self._test_check_dependencies()

        # Test monitoring service
        await self._test_monitoring_service()

        # Test error handling
        await self._test_error_handling()

        # Test cleanup
        await self._test_cleanup()

        # Print results
        self.print_test_results()

        return self.test_results

    async def _initialize_health_checker(self):
        """Initialize health checker."""
        try:
            self.health_checker = get_health_checker()

            # Verify initialization
            is_initialized = self.health_checker is not None
            is_enabled = self.health_checker.is_enabled()
            has_default_checks = len(self.health_checker.checks) > 0

            self.test_results["initialization"] = {
                "status": (
                    "PASS"
                    if is_initialized and is_enabled and has_default_checks
                    else "FAIL"
                ),
                "message": f"Health checker initialization {'successful' if is_initialized and is_enabled and has_default_checks else 'failed'}",
                "is_initialized": is_initialized,
                "is_enabled": is_enabled,
                "default_checks_count": len(self.health_checker.checks),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Health checker initialization {'successful' if is_initialized and is_enabled and has_default_checks else 'failed'}"
            )

        except Exception as e:
            self.test_results["initialization"] = {
                "status": "FAIL",
                "message": f"Health checker initialization failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Health checker initialization failed: {e}")

    async def _test_health_check_registration(self):
        """Test health check registration."""
        try:
            # Register test health checks
            test_checks = [
                HealthCheck(
                    name="test_healthy",
                    check_type=CheckType.SYSTEM,
                    description="Test healthy check",
                    check_function=self._test_healthy_check_function,
                    timeout=5,
                    interval=30,
                ),
                HealthCheck(
                    name="test_warning",
                    check_type=CheckType.SYSTEM,
                    description="Test warning check",
                    check_function=self._test_warning_check_function,
                    timeout=5,
                    interval=30,
                ),
                HealthCheck(
                    name="test_critical",
                    check_type=CheckType.SYSTEM,
                    description="Test critical check",
                    check_function=self._test_critical_check_function,
                    timeout=5,
                    interval=30,
                ),
                HealthCheck(
                    name="test_timeout",
                    check_type=CheckType.SYSTEM,
                    description="Test timeout check",
                    check_function=self._test_timeout_check_function,
                    timeout=1,  # Very short timeout
                    interval=30,
                ),
                HealthCheck(
                    name="test_error",
                    check_type=CheckType.SYSTEM,
                    description="Test error check",
                    check_function=self._test_error_check_function,
                    timeout=5,
                    interval=30,
                ),
            ]

            for check in test_checks:
                self.health_checker.register_check(check)
                self.test_checks.append(check.name)

            # Verify registration
            registered_count = len(
                [c for c in self.health_checker.checks.keys() if c.startswith("test_")]
            )
            expected_count = len(test_checks)

            registration_success = registered_count == expected_count

            self.test_results["health_check_registration"] = {
                "status": "PASS" if registration_success else "FAIL",
                "message": f"Health check registration {'successful' if registration_success else 'failed'}",
                "registered_count": registered_count,
                "expected_count": expected_count,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Health check registration {'successful' if registration_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["health_check_registration"] = {
                "status": "FAIL",
                "message": f"Health check registration failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Health check registration failed: {e}")

    async def _test_healthy_checks(self):
        """Test healthy health checks."""
        try:
            # Run healthy check
            result = await self.health_checker.run_check("test_healthy")

            # Verify result
            healthy_success = result.status == HealthStatus.HEALTHY
            message_success = "Test healthy check" in result.message
            has_details = len(result.details) > 0
            has_timestamp = result.timestamp is not None

            self.test_results["healthy_checks"] = {
                "status": (
                    "PASS"
                    if healthy_success
                    and message_success
                    and has_details
                    and has_timestamp
                    else "FAIL"
                ),
                "message": f"Healthy checks {'successful' if healthy_success and message_success and has_details and has_timestamp else 'failed'}",
                "healthy_success": healthy_success,
                "message_success": message_success,
                "has_details": has_details,
                "has_timestamp": has_timestamp,
                "result_status": result.status.value,
                "result_message": result.message,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Healthy checks {'successful' if healthy_success and message_success and has_details and has_timestamp else 'failed'}"
            )

        except Exception as e:
            self.test_results["healthy_checks"] = {
                "status": "FAIL",
                "message": f"Healthy checks test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Healthy checks test failed: {e}")

    async def _test_warning_checks(self):
        """Test warning health checks."""
        try:
            # Run warning check
            result = await self.health_checker.run_check("test_warning")

            # Verify result
            warning_success = result.status == HealthStatus.WARNING
            message_success = "Test warning check" in result.message
            has_details = len(result.details) > 0
            has_timestamp = result.timestamp is not None

            self.test_results["warning_checks"] = {
                "status": (
                    "PASS"
                    if warning_success
                    and message_success
                    and has_details
                    and has_timestamp
                    else "FAIL"
                ),
                "message": f"Warning checks {'successful' if warning_success and message_success and has_details and has_timestamp else 'failed'}",
                "warning_success": warning_success,
                "message_success": message_success,
                "has_details": has_details,
                "has_timestamp": has_timestamp,
                "result_status": result.status.value,
                "result_message": result.message,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Warning checks {'successful' if warning_success and message_success and has_details and has_timestamp else 'failed'}"
            )

        except Exception as e:
            self.test_results["warning_checks"] = {
                "status": "FAIL",
                "message": f"Warning checks test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Warning checks test failed: {e}")

    async def _test_critical_checks(self):
        """Test critical health checks."""
        try:
            # Run critical check
            result = await self.health_checker.run_check("test_critical")

            # Verify result
            critical_success = result.status == HealthStatus.CRITICAL
            message_success = "Test critical check" in result.message
            has_details = len(result.details) > 0
            has_timestamp = result.timestamp is not None
            has_error = result.error is not None

            self.test_results["critical_checks"] = {
                "status": (
                    "PASS"
                    if critical_success
                    and message_success
                    and has_details
                    and has_timestamp
                    else "FAIL"
                ),
                "message": f"Critical checks {'successful' if critical_success and message_success and has_details and has_timestamp else 'failed'}",
                "critical_success": critical_success,
                "message_success": message_success,
                "has_details": has_details,
                "has_timestamp": has_timestamp,
                "has_error": has_error,
                "result_status": result.status.value,
                "result_message": result.message,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Critical checks {'successful' if critical_success and message_success and has_details and has_timestamp else 'failed'}"
            )

        except Exception as e:
            self.test_results["critical_checks"] = {
                "status": "FAIL",
                "message": f"Critical checks test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Critical checks test failed: {e}")

    async def _test_check_execution(self):
        """Test check execution."""
        try:
            # Run multiple checks concurrently
            tasks = []
            for check_name in ["test_healthy", "test_warning", "test_critical"]:
                task = self.health_checker.run_check(check_name)
                tasks.append(task)

            # Wait for all checks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Analyze results
            successful_count = 0
            failed_count = 0
            execution_results = {}

            for i, result in enumerate(results):
                check_name = ["test_healthy", "test_warning", "test_critical"][i]

                if isinstance(result, Exception):
                    failed_count += 1
                    execution_results[check_name] = {
                        "success": False,
                        "error": str(result),
                    }
                else:
                    health_result = result
                    success = health_result.status in [
                        HealthStatus.HEALTHY,
                        HealthStatus.WARNING,
                        HealthStatus.CRITICAL,
                    ]

                    if success:
                        successful_count += 1
                    else:
                        failed_count += 1

                    execution_results[check_name] = {
                        "success": success,
                        "status": health_result.status.value,
                        "message": health_result.message,
                        "duration": health_result.duration,
                    }

            execution_success = failed_count == 0

            self.test_results["check_execution"] = {
                "status": "PASS" if execution_success else "FAIL",
                "message": f"Check execution {'successful' if execution_success else 'failed'}",
                "total_checks": len(tasks),
                "successful_count": successful_count,
                "failed_count": failed_count,
                "execution_results": execution_results,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Check execution {'successful' if execution_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["check_execution"] = {
                "status": "FAIL",
                "message": f"Check execution test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Check execution test failed: {e}")

    async def _test_health_report(self):
        """Test health report generation."""
        try:
            # Generate health report
            report = await self.health_checker.run_all_checks()

            # Verify report
            has_timestamp = report.timestamp is not None
            has_checks = len(report.checks) > 0
            has_summary = len(report.summary) > 0
            has_recommendations = len(report.recommendations) > 0

            # Verify overall status calculation
            critical_count = len(
                [c for c in report.checks if c.status == HealthStatus.CRITICAL]
            )
            warning_count = len(
                [c for c in report.checks if c.status == HealthStatus.WARNING]
            )
            healthy_count = len(
                [c for c in report.checks if c.status == HealthStatus.HEALTHY]
            )

            expected_status = (
                HealthStatus.CRITICAL
                if critical_count > 0
                else HealthStatus.WARNING if warning_count > 0 else HealthStatus.HEALTHY
            )
            status_correct = report.overall_status == expected_status

            self.test_results["health_report"] = {
                "status": (
                    "PASS"
                    if has_timestamp and has_checks and has_summary and status_correct
                    else "FAIL"
                ),
                "message": f"Health report generation {'successful' if has_timestamp and has_checks and has_summary and status_correct else 'failed'}",
                "has_timestamp": has_timestamp,
                "has_checks": has_checks,
                "has_summary": has_summary,
                "has_recommendations": has_recommendations,
                "status_correct": status_correct,
                "overall_status": report.overall_status.value,
                "expected_status": expected_status.value,
                "critical_count": critical_count,
                "warning_count": warning_count,
                "healthy_count": healthy_count,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Health report generation {'successful' if has_timestamp and has_checks and has_summary and status_correct else 'failed'}"
            )

        except Exception as e:
            self.test_results["health_report"] = {
                "status": "FAIL",
                "message": f"Health report generation failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Health report generation failed: {e}")

    async def _test_check_dependencies(self):
        """Test check dependencies."""
        try:
            # Create a check with dependencies
            dependent_check = HealthCheck(
                name="test_dependent",
                check_type=CheckType.SYSTEM,
                description="Test dependent check",
                check_function=self._test_dependent_check_function,
                dependencies=["test_healthy"],
                timeout=5,
                interval=30,
            )

            self.health_checker.register_check(dependent_check)

            # Run dependent check
            result = await self.health_checker.run_check("test_dependent")

            # Verify result
            dependency_success = result.status == HealthStatus.HEALTHY

            # Test check without dependencies
            independent_check = HealthCheck(
                name="test_independent",
                check_type=CheckType.SYSTEM,
                description="Test independent check",
                check_function=self._test_independent_check_function,
                timeout=5,
                interval=30,
            )

            self.health_checker.register_check(independent_check)

            # Run independent check
            independent_result = await self.health_checker.run_check("test_independent")

            independent_success = independent_result.status == HealthStatus.HEALTHY

            self.test_results["check_dependencies"] = {
                "status": (
                    "PASS" if dependency_success and independent_success else "FAIL"
                ),
                "message": f"Check dependencies {'successful' if dependency_success and independent_success else 'failed'}",
                "dependency_success": dependency_success,
                "independent_success": independent_success,
                "dependency_status": result.status.value,
                "independent_status": independent_result.status.value,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Check dependencies {'successful' if dependency_success and independent_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["check_dependencies"] = {
                "status": "FAIL",
                "message": f"Check dependencies test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Check dependencies test failed: {e}")

    async def _test_monitoring_service(self):
        """Test monitoring service."""
        try:
            # Start monitoring service
            await self.health_checker.start_monitoring()

            # Verify service is running
            is_monitoring = self.health_checker.is_monitoring()

            # Wait a moment for monitoring to start
            await asyncio.sleep(0.1)

            # Stop monitoring service
            await self.health_checker.stop_monitoring()

            # Verify service is stopped
            is_stopped = not self.health_checker.is_monitoring()

            monitoring_success = is_monitoring and is_stopped

            self.test_results["monitoring_service"] = {
                "status": "PASS" if monitoring_success else "FAIL",
                "message": f"Monitoring service {'successful' if monitoring_success else 'failed'}",
                "is_monitoring": is_monitoring,
                "is_stopped": is_stopped,
                "monitoring_success": monitoring_success,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Monitoring service {'successful' if monitoring_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["monitoring_service"] = {
                "status": "FAIL",
                "message": f"Monitoring service test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Monitoring service test failed: {e}")

    async def _test_error_handling(self):
        """Test error handling."""
        try:
            # Test timeout error
            timeout_result = await self.health_checker.run_check("test_timeout")
            timeout_success = (
                timeout_result.status == HealthStatus.CRITICAL
                and "timed out" in timeout_result.message.lower()
            )

            # Test execution error
            error_result = await self.health_checker.run_check("test_error")
            error_success = (
                error_result.status == HealthStatus.CRITICAL
                and "failed" in error_result.message.lower()
            )

            # Test unknown check
            unknown_result = await self.health_checker.run_check("nonexistent_check")
            unknown_success = (
                unknown_result.status == HealthStatus.UNKNOWN
                and "not found" in unknown_result.message.lower()
            )

            error_handling_success = (
                timeout_success and error_success and unknown_success
            )

            self.test_results["error_handling"] = {
                "status": "PASS" if error_handling_success else "FAIL",
                "message": f"Error handling {'successful' if error_handling_success else 'failed'}",
                "timeout_success": timeout_success,
                "error_success": error_success,
                "unknown_success": unknown_success,
                "error_handling_success": error_handling_success,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Error handling {'successful' if error_handling_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["error_handling"] = {
                "status": "FAIL",
                "message": f"Error handling test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Error handling test failed: {e}")

    async def _test_cleanup(self):
        """Test cleanup functionality."""
        try:
            # Unregister test checks
            for check_name in self.test_checks:
                self.health_checker.unregister_check(check_name)

            # Verify unregistration
            remaining_test_checks = len(
                [c for c in self.health_checker.checks.keys() if c.startswith("test_")]
            )
            cleanup_success = remaining_test_checks == 0

            # Test enable/disable
            self.health_checker.disable()
            disabled = not self.health_checker.is_enabled()

            self.health_checker.enable()
            enabled = self.health_checker.is_enabled()

            cleanup_success = cleanup_success and disabled and enabled

            self.test_results["cleanup"] = {
                "status": "PASS" if cleanup_success else "FAIL",
                "message": f"Cleanup {'successful' if cleanup_success else 'failed'}",
                "cleanup_success": cleanup_success,
                "remaining_test_checks": remaining_test_checks,
                "disabled": disabled,
                "enabled": enabled,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ Cleanup {'successful' if cleanup_success else 'failed'}")

        except Exception as e:
            self.test_results["cleanup"] = {
                "status": "FAIL",
                "message": f"Cleanup test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Cleanup test failed: {e}")

    # Test check functions
    async def _test_healthy_check_function(self):
        """Test healthy check function."""
        return HealthCheckResult(
            name="test_healthy",
            status=HealthStatus.HEALTHY,
            message="Test healthy check",
            timestamp=datetime.now(),
            duration=0.1,
            details={"test": "healthy"},
        )

    async def _test_warning_check_function(self):
        """Test warning check function."""
        return HealthCheckResult(
            name="test_warning",
            status=HealthStatus.WARNING,
            message="Test warning check",
            timestamp=datetime.now(),
            duration=0.1,
            details={"test": "warning"},
        )

    async def _test_critical_check_function(self):
        """Test critical check function."""
        return HealthCheckResult(
            name="test_critical",
            status=HealthStatus.CRITICAL,
            message="Test critical check",
            timestamp=datetime.now(),
            duration=0.1,
            details={"test": "critical"},
        )

    async def _test_timeout_check_function(self):
        """Test timeout check function."""
        # Simulate timeout by sleeping longer than the check timeout
        await asyncio.sleep(2)  # Longer than 1 second timeout
        return HealthCheckResult(
            name="test_timeout",
            status=HealthStatus.HEALTHY,
            message="Test timeout check",
            timestamp=datetime.now(),
            duration=2.1,
            details={"test": "timeout"},
        )

    async def _test_error_check_function(self):
        """Test error check function."""
        raise Exception("Test error")

    async def _test_dependent_check_function(self):
        """Test dependent check function."""
        # This check depends on test_healthy check being healthy
        healthy_result = self.health_checker.get_check_result("test_healthy")

        if healthy_result and healthy_result.status == HealthStatus.HEALTHY:
            return HealthCheckResult(
                name="test_dependent",
                status=HealthStatus.HEALTHY,
                message="Test dependent check",
                timestamp=datetime.now(),
                duration=0.1,
                details={"test": "dependent", "dependency": "healthy"},
            )
        else:
            return HealthCheckResult(
                name="test_dependent",
                status=HealthStatus.WARNING,
                message="Test dependent check - dependency failed",
                timestamp=datetime.now(),
                duration=0.1,
                details={"test": "dependent", "dependency": "failed"},
            )

    async def _test_independent_check_function(self):
        """Test independent check function."""
        return HealthCheckResult(
            name="test_independent",
            status=HealthStatus.HEALTHY,
            message="Test independent check",
            timestamp=datetime.now(),
            duration=0.1,
            details={"test": "independent"},
        )

    def print_test_results(self):
        """Print test results summary."""
        logger.info("\n" + "=" * 50)
        logger.info("HEALTH CHECK TEST RESULTS")
        logger.info("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = len(
            [r for r in self.test_results.values() if r["status"] == "PASS"]
        )
        failed_tests = total_tests - passed_tests

        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        logger.info("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            logger.info(f"{status_icon} {test_name}: {result['message']}")

        if failed_tests > 0:
            logger.info(
                f"\n⚠️  {failed_tests} tests failed. Please review the errors above."
            )
        else:
            logger.info("\n🎉 All tests passed! Health checks are working correctly.")

        logger.info("=" * 50)


async def main():
    """Main function to run tests."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run tests
    tester = TestHealthChecks()
    results = await tester.run_all_tests()

    return results


if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())

    # Exit with appropriate code
    failed_count = len([r for r in results.values() if r["status"] == "FAIL"])
    exit(1 if failed_count > 0 else 0)
