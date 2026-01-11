"""
Test file to verify alerting triggers correctly.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Import alerting components
from monitoring.alerting import (
    Alert,
    AlertManager,
    AlertRule,
    AlertSeverity,
    AlertStatus,
    AlertType,
    NotificationChannel,
    get_alert_manager,
)
from monitoring.health_checks import HealthStatus, get_health_checker
from monitoring.metrics import get_metrics_collector

logger = logging.getLogger(__name__)


class TestAlertingSystem:
    """Test suite for alerting system functionality."""

    def __init__(self):
        self.test_results = {}
        self.alert_manager = None
        self.test_rules = []
        self.test_channels = []
        self.test_alerts = []

    async def run_all_tests(self):
        """Run all alerting system tests."""
        logger.info("Starting alerting system tests")

        # Initialize alert manager
        await self._initialize_alert_manager()

        # Test alert rule registration
        await self._test_alert_rule_registration()

        # Test metric threshold alerts
        await self._test_metric_threshold_alerts()

        # Test health check alerts
        await self._test_health_check_alerts()

        # Test system error alerts
        await self._test_system_error_alerts()

        # Test alert creation and management
        await self._test_alert_management()

        # Test alert escalation
        await self._test_alert_escalation()

        # Test notification channels
        await self._test_notification_channels()

        # Test alert statistics
        await self._test_alert_statistics()

        # Test alert cleanup
        await self._test_alert_cleanup()

        # Print results
        self.print_test_results()

        return self.test_results

    async def _initialize_alert_manager(self):
        """Initialize alert manager."""
        try:
            self.alert_manager = get_alert_manager()

            # Verify initialization
            is_initialized = self.alert_manager is not None
            is_enabled = self.alert_manager.is_enabled()
            has_default_rules = len(self.alert_manager.rules) > 0
            has_default_channels = len(self.alert_manager.channels) > 0

            self.test_results["initialization"] = {
                "status": (
                    "PASS"
                    if is_initialized
                    and is_enabled
                    and has_default_rules
                    and has_default_channels
                    else "FAIL"
                ),
                "message": f"Alert manager initialization {'successful' if is_initialized and is_enabled and has_default_rules and has_default_channels else 'failed'}",
                "is_initialized": is_initialized,
                "is_enabled": is_enabled,
                "default_rules_count": len(self.alert_manager.rules),
                "default_channels_count": len(self.alert_manager.channels),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Alert manager initialization {'successful' if is_initialized and is_enabled and has_default_rules and has_default_channels else 'failed'}"
            )

        except Exception as e:
            self.test_results["initialization"] = {
                "status": "FAIL",
                "message": f"Alert manager initialization failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Alert manager initialization failed: {e}")

    async def _test_alert_rule_registration(self):
        """Test alert rule registration."""
        try:
            # Register test alert rules
            test_rules = [
                AlertRule(
                    name="test_metric_rule",
                    alert_type=AlertType.METRIC_THRESHOLD,
                    description="Test metric threshold rule",
                    severity=AlertSeverity.HIGH,
                    metric_name="test_metric",
                    threshold=80.0,
                    condition=">=",
                    notification_channels=["email"],
                    cooldown=60,
                ),
                AlertRule(
                    name="test_health_rule",
                    alert_type=AlertType.HEALTH_CHECK,
                    description="Test health check rule",
                    severity=AlertSeverity.MEDIUM,
                    health_check_name="test_health_check",
                    notification_channels=["slack"],
                    cooldown=120,
                ),
                AlertRule(
                    name="test_error_rule",
                    alert_type=AlertType.SYSTEM_ERROR,
                    description="Test system error rule",
                    severity=AlertSeverity.CRITICAL,
                    notification_channels=["email", "slack", "webhook"],
                    cooldown=30,
                ),
                AlertRule(
                    name="test_custom_rule",
                    alert_type=AlertType.CUSTOM,
                    description="Test custom rule",
                    severity=AlertSeverity.LOW,
                    notification_channels=["email"],
                    cooldown=300,
                ),
            ]

            for rule in test_rules:
                self.alert_manager.register_rule(rule)
                self.test_rules.append(rule.name)

            # Verify registration
            registered_count = len(
                [r for r in self.alert_manager.rules.keys() if r.startswith("test_")]
            )
            expected_count = len(test_rules)

            registration_success = registered_count == expected_count

            self.test_results["alert_rule_registration"] = {
                "status": "PASS" if registration_success else "FAIL",
                "message": f"Alert rule registration {'successful' if registration_success else 'failed'}",
                "registered_count": registered_count,
                "expected_count": expected_count,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Alert rule registration {'successful' if registration_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["alert_rule_registration"] = {
                "status": "FAIL",
                "message": f"Alert rule registration failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Alert rule registration failed: {e}")

    async def _test_metric_threshold_alerts(self):
        """Test metric threshold alerts."""
        try:
            # Set up metrics collector
            metrics_collector = get_metrics_collector()

            # Set metric value to trigger alert
            metrics_collector.set_gauge("test_metric", 85.0)

            # Check for alert
            await self.alert_manager.check_rules()

            # Verify alert was created
            alerts = self.alert_manager.get_alerts(status=AlertStatus.ACTIVE)
            metric_alerts = [
                a for a in alerts if a.alert_type == AlertType.METRIC_THRESHOLD
            ]

            metric_success = len(metric_alerts) > 0
            alert_details = metric_alerts[0].details if metric_alerts else {}

            # Verify alert details
            has_metric_value = "metric_value" in alert_details
            has_threshold = "threshold" in alert_details
            metric_value_correct = alert_details.get("metric_value") == 85.0
            threshold_correct = alert_details.get("threshold") == 80.0

            self.test_results["metric_threshold_alerts"] = {
                "status": (
                    "PASS"
                    if metric_success
                    and has_metric_value
                    and has_threshold
                    and metric_value_correct
                    and threshold_correct
                    else "FAIL"
                ),
                "message": f"Metric threshold alerts {'successful' if metric_success and has_metric_value and has_threshold and metric_value_correct and threshold_correct else 'failed'}",
                "metric_success": metric_success,
                "has_metric_value": has_metric_value,
                "has_threshold": has_threshold,
                "metric_value_correct": metric_value_correct,
                "threshold_correct": threshold_correct,
                "alert_count": len(metric_alerts),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Metric threshold alerts {'successful' if metric_success and has_metric_value and has_threshold and metric_value_correct and threshold_correct else 'failed'}"
            )

        except Exception as e:
            self.test_results["metric_threshold_alerts"] = {
                "status": "FAIL",
                "message": f"Metric threshold alerts test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Metric threshold alerts test failed: {e}")

    async def _test_health_check_alerts(self):
        """Test health check alerts."""
        try:
            # Set up health checker
            health_checker = get_health_checker()

            # Simulate critical health check result
            critical_result = health_checker.results.get("database_connection")
            if critical_result:
                critical_result.status = HealthStatus.CRITICAL
                critical_result.message = "Database connection failed"

            # Check for alert
            await self.alert_manager.check_rules()

            # Verify alert was created
            alerts = self.alert_manager.get_alerts(status=AlertStatus.ACTIVE)
            health_alerts = [
                a for a in alerts if a.alert_type == AlertType.HEALTH_CHECK
            ]

            health_success = len(health_alerts) > 0
            alert_details = health_alerts[0].details if health_alerts else {}

            # Verify alert details
            has_health_status = "health_status" in alert_details
            health_status_critical = alert_details.get("health_status") == "critical"

            self.test_results["health_check_alerts"] = {
                "status": (
                    "PASS"
                    if health_success and has_health_status and health_status_critical
                    else "FAIL"
                ),
                "message": f"Health check alerts {'successful' if health_success and has_health_status and health_status_critical else 'failed'}",
                "health_success": health_success,
                "has_health_status": has_health_status,
                "health_status_critical": health_status_critical,
                "alert_count": len(health_alerts),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Health check alerts {'successful' if health_success and has_health_status and health_status_critical else 'failed'}"
            )

        except Exception as e:
            self.test_results["health_check_alerts"] = {
                "status": "FAIL",
                "message": f"Health check alerts test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Health check alerts test failed: {e}")

    async def _test_system_error_alerts(self):
        """Test system error alerts."""
        try:
            # Set up metrics collector
            metrics_collector = get_metrics_collector()

            # Increment error count to trigger alert
            metrics_collector.increment_counter("error_total", 1)

            # Check for alert
            await self.alert_manager.check_rules()

            # Verify alert was created
            alerts = self.alert_manager.get_alerts(status=AlertStatus.ACTIVE)
            error_alerts = [a for a in alerts if a.alert_type == AlertType.SYSTEM_ERROR]

            error_success = len(error_alerts) > 0
            alert_details = error_alerts[0].details if error_alerts else {}

            # Verify alert details
            has_error_count = "error_count" in alert_details
            error_count_correct = alert_details.get("error_count") == 1

            self.test_results["system_error_alerts"] = {
                "status": (
                    "PASS"
                    if error_success and has_error_count and error_count_correct
                    else "FAIL"
                ),
                "message": f"System error alerts {'successful' if error_success and has_error_count and error_count_correct else 'failed'}",
                "error_success": error_success,
                "has_error_count": has_error_count,
                "error_count_correct": error_count_correct,
                "alert_count": len(error_alerts),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ System error alerts {'successful' if error_success and has_error_count and error_count_correct else 'failed'}"
            )

        except Exception as e:
            self.test_results["system_error_alerts"] = {
                "status": "FAIL",
                "message": f"System error alerts test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ System error alerts test failed: {e}")

    async def _test_alert_management(self):
        """Test alert management operations."""
        try:
            # Create a test alert
            test_alert = Alert(
                id="test_alert_1",
                rule_name="test_metric_rule",
                alert_type=AlertType.METRIC_THRESHOLD,
                severity=AlertSeverity.HIGH,
                status=AlertStatus.ACTIVE,
                title="Test Alert",
                message="Test alert message",
                details={"test": "data"},
            )

            # Add alert to manager
            self.alert_manager.alerts[test_alert.id] = test_alert
            self.test_alerts.append(test_alert.id)

            # Test acknowledgment
            ack_success = await self.alert_manager.acknowledge_alert(
                test_alert.id, "test_user"
            )

            # Verify acknowledgment
            acknowledged_alert = self.alert_manager.get_alert(test_alert.id)
            ack_verified = acknowledged_alert.status == AlertStatus.ACKNOWLEDGED
            ack_user_correct = acknowledged_alert.acknowledged_by == "test_user"

            # Test resolution
            resolve_success = await self.alert_manager.resolve_alert(
                test_alert.id, "test_user"
            )

            # Verify resolution
            resolved_alert = self.alert_manager.get_alert(test_alert.id)
            resolved_verified = resolved_alert.status == AlertStatus.RESOLVED
            resolved_by_correct = resolved_alert.resolved_by == "test_user"

            # Test suppression
            suppress_success = await self.alert_manager.suppress_alert(test_alert.id)

            # Verify suppression
            suppressed_alert = self.alert_manager.get_alert(test_alert.id)
            suppressed_verified = suppressed_alert.status == AlertStatus.SUPPRESSED

            management_success = (
                ack_success
                and ack_verified
                and resolve_success
                and resolved_verified
                and resolved_by_correct
                and suppress_success
                and suppressed_verified
            )

            self.test_results["alert_management"] = {
                "status": "PASS" if management_success else "FAIL",
                "message": f"Alert management {'successful' if management_success else 'failed'}",
                "ack_success": ack_success,
                "ack_verified": ack_verified,
                "resolve_success": resolve_success,
                "resolved_verified": resolved_verified,
                "resolved_by_correct": resolved_by_correct,
                "suppress_success": suppress_success,
                "suppressed_verified": suppressed_verified,
                "management_success": management_success,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Alert management {'successful' if management_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["alert_management"] = {
                "status": "FAIL",
                "message": f"Alert management test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Alert management test failed: {e}")

    async def _test_alert_escalation(self):
        """Test alert escalation."""
        try:
            # Test high severity alert
            high_severity_alert = Alert(
                id="test_high_severity",
                rule_name="test_error_rule",
                alert_type=AlertType.SYSTEM_ERROR,
                severity=AlertSeverity.HIGH,
                status=AlertStatus.ACTIVE,
                title="High Severity Alert",
                message="High severity test alert",
                details={"test": "data"},
            )

            # Test critical severity alert
            critical_severity_alert = Alert(
                id="test_critical_severity",
                rule_name="test_error_rule",
                alert_type=AlertType.SYSTEM_ERROR,
                severity=AlertSeverity.CRITICAL,
                status=AlertStatus.ACTIVE,
                title="Critical Severity Alert",
                message="Critical severity test alert",
                details={"test": "data"},
            )

            # Add alerts to manager
            self.alert_manager.alerts[high_severity_alert.id] = high_severity_alert
            self.alert_manager.alerts[critical_severity_alert.id] = (
                critical_severity_alert
            )

            # Verify severity levels
            high_severity_correct = high_severity_alert.severity == AlertSeverity.HIGH
            critical_severity_correct = (
                critical_severity_alert.severity == AlertSeverity.CRITICAL
            )

            # Test escalation policy
            escalation_success = high_severity_correct and critical_severity_correct

            self.test_results["alert_escalation"] = {
                "status": "PASS" if escalation_success else "FAIL",
                "message": f"Alert escalation {'successful' if escalation_success else 'failed'}",
                "high_severity_correct": high_severity_correct,
                "critical_severity_correct": critical_severity_correct,
                "escalation_success": escalation_success,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Alert escalation {'successful' if escalation_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["alert_escalation"] = {
                "status": "FAIL",
                "message": f"Alert escalation test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Alert escalation test failed: {e}")

    async def _test_notification_channels(self):
        """Test notification channels."""
        try:
            # Register test notification channel
            test_channel = NotificationChannel(
                name="test_channel",
                type="test",
                enabled=True,
                config={"test": "config"},
                rate_limit=10,
                retry_attempts=2,
                retry_delay=30,
            )

            self.alert_manager.register_channel(test_channel)
            self.test_channels.append(test_channel.name)

            # Verify registration
            registered_count = len(
                [c for c in self.alert_manager.channels.keys() if c.startswith("test_")]
            )
            expected_count = 1

            registration_success = registered_count == expected_count

            # Test channel enable/disable
            self.alert_manager.disable_channel("test_channel")
            disabled = not self.alert_manager.channels["test_channel"].enabled

            self.alert_manager.enable_channel("test_channel")
            enabled = self.alert_manager.channels["test_channel"].enabled

            channel_success = registration_success and disabled and enabled

            self.test_results["notification_channels"] = {
                "status": "PASS" if channel_success else "FAIL",
                "message": f"Notification channels {'successful' if channel_success else 'failed'}",
                "registration_success": registration_success,
                "disabled": disabled,
                "enabled": enabled,
                "channel_success": channel_success,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Notification channels {'successful' if channel_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["notification_channels"] = {
                "status": "FAIL",
                "message": f"Notification channels test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Notification channels test failed: {e}")

    async def _test_alert_statistics(self):
        """Test alert statistics."""
        try:
            # Create some test alerts
            for i in range(5):
                alert = Alert(
                    id=f"test_alert_{i}",
                    rule_name="test_metric_rule",
                    alert_type=AlertType.METRIC_THRESHOLD,
                    severity=AlertSeverity.MEDIUM,
                    status=AlertStatus.ACTIVE,
                    title=f"Test Alert {i}",
                    message=f"Test alert message {i}",
                    details={"test": f"data_{i}"},
                )
                self.alert_manager.alerts[alert.id] = alert
                self.test_alerts.append(alert.id)

            # Get statistics
            stats = self.alert_manager.get_alert_statistics()

            # Verify statistics
            has_total_alerts = "total_alerts" in stats
            has_active_alerts = "active_alerts" in stats
            has_resolved_alerts = "resolved_alerts" in stats
            has_alerts_by_severity = "alerts_by_severity" in stats
            has_alerts_by_type = "alerts_by_type" in stats
            has_alerts_by_rule = "alerts_by_rule" in stats

            stats_success = (
                has_total_alerts
                and has_active_alerts
                and has_resolved_alerts
                and has_alerts_by_severity
                and has_alerts_by_type
                and has_alerts_by_rule
            )

            # Verify counts
            total_correct = stats["total_alerts"] == len(self.test_alerts)
            active_correct = stats["active_alerts"] == len(self.test_alerts)

            self.test_results["alert_statistics"] = {
                "status": (
                    "PASS"
                    if stats_success and total_correct and active_correct
                    else "FAIL"
                ),
                "message": f"Alert statistics {'successful' if stats_success and total_correct and active_correct else 'failed'}",
                "stats_success": stats_success,
                "has_total_alerts": has_total_alerts,
                "has_active_alerts": has_active_alerts,
                "has_resolved_alerts": has_resolved_alerts,
                "has_alerts_by_severity": has_alerts_by_severity,
                "has_alerts_by_type": has_alerts_by_type,
                "has_alerts_by_rule": has_alerts_by_rule,
                "total_correct": total_correct,
                "active_correct": active_correct,
                "total_alerts": stats["total_alerts"],
                "active_alerts": stats["active_alerts"],
                "resolved_alerts": stats["resolved_alerts"],
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Alert statistics {'successful' if stats_success and total_correct and active_correct else 'failed'}"
            )

        except Exception as e:
            self.test_results["alert_statistics"] = {
                "status": "FAIL",
                "message": f"Alert statistics test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Alert statistics test failed: {e}")

    async def _test_alert_cleanup(self):
        """Test alert cleanup functionality."""
        try:
            # Unregister test rules
            for rule_name in self.test_rules:
                self.alert_manager.unregister_rule(rule_name)

            # Unregister test channels
            for channel_name in self.test_channels:
                self.alert_manager.unregister_channel(channel_name)

            # Clear test alerts
            self.alert_manager.alerts.clear()
            self.test_alerts.clear()

            # Verify cleanup
            remaining_rules = len(
                [r for r in self.alert_manager.rules.keys() if r.startswith("test_")]
            )
            remaining_channels = len(
                [c for c in self.alert_manager.channels.keys() if c.startswith("test_")]
            )
            remaining_alerts = len(self.alert_manager.alerts)

            cleanup_success = (
                remaining_rules == 0
                and remaining_channels == 0
                and remaining_alerts == 0
            )

            # Test enable/disable
            self.alert_manager.disable()
            disabled = not self.alert_manager.is_enabled()

            self.alert_manager.enable()
            enabled = self.alert_manager.is_enabled()

            cleanup_success = cleanup_success and disabled and enabled

            self.test_results["alert_cleanup"] = {
                "status": "PASS" if cleanup_success else "FAIL",
                "message": f"Alert cleanup {'successful' if cleanup_success else 'failed'}",
                "cleanup_success": cleanup_success,
                "remaining_rules": remaining_rules,
                "remaining_channels": remaining_channels,
                "remaining_alerts": remaining_alerts,
                "disabled": disabled,
                "enabled": enabled,
                "cleanup_success": cleanup_success,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Alert cleanup {'successful' if cleanup_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["alert_cleanup"] = {
                "status": "FAIL",
                "message": f"Alert cleanup test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Alert cleanup test failed: {e}")

    def print_test_results(self):
        """Print test results summary."""
        logger.info("\n" + "=" * 50)
        logger.info("ALERTING SYSTEM TEST RESULTS")
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
            logger.info("\n🎉 All tests passed! Alerting system is working correctly.")

        logger.info("=" * 50)


async def main():
    """Main function to run tests."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run tests
    tester = TestAlertingSystem()
    results = await tester.run_all_tests()

    return results


if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())

    # Exit with appropriate code
    failed_count = len([r for r in results.values() if r["status"] == "FAIL"])
    exit(1 if failed_count > 0 else 0)
