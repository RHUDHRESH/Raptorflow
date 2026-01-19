"""
Comprehensive Sentry Integration Testing Framework
=================================================

Complete testing suite for Sentry monitoring integration with
error simulation, performance validation, and end-to-end testing.

Features:
- Error simulation and validation
- Performance monitoring tests
- Session tracking tests
- Alerting system tests
- Dashboard functionality tests
- Integration tests
- Load testing scenarios
- Error recovery testing
"""

import pytest
import asyncio
import time
import uuid
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
import requests
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

# Import Sentry components
from backend.core.sentry_integration import (
    SentryIntegrationManager, 
    SentryConfig, 
    SentryEnvironment,
    get_sentry_manager,
    initialize_sentry,
    shutdown_sentry
)
from backend.core.sentry_error_tracking import (
    SentryErrorTracker,
    ErrorContext,
    ErrorCategory,
    ErrorSeverity,
    get_error_tracker
)
from backend.core.sentry_performance import (
    SentryPerformanceMonitor,
    get_performance_monitor
)
from backend.core.sentry_sessions import (
    SentrySessionManager,
    SessionType,
    get_session_manager
)
from backend.core.sentry_alerting import (
    SentryAlertingManager,
    AlertRule,
    AlertType,
    AlertSeverity,
    get_alerting_manager
)
from backend.core.sentry_dashboards import (
    SentryDashboardManager,
    DashboardType,
    WidgetType,
    get_dashboard_manager
)
from ..middleware.sentry_middleware import SentryMiddleware, add_sentry_middleware


class TestSentryIntegration:
    """Test suite for Sentry integration manager."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock Sentry configuration for testing."""
        return SentryConfig(
            dsn="https://test@test.ingest.sentry.io/123456",
            environment=SentryEnvironment.TESTING,
            release="test-release",
            sample_rate=1.0,
            traces_sample_rate=1.0,
            debug=True
        )
    
    @pytest.fixture
    def sentry_manager(self, mock_config):
        """Create Sentry manager for testing."""
        manager = SentryIntegrationManager(mock_config)
        return manager
    
    def test_sentry_manager_initialization(self, mock_config):
        """Test Sentry manager initialization."""
        manager = SentryIntegrationManager(mock_config)
        
        assert manager.config.dsn == mock_config.dsn
        assert manager.config.environment == SentryEnvironment.TESTING
        assert manager.config.release == mock_config.release
        assert manager.config.sample_rate == 1.0
    
    def test_sentry_manager_health_status(self, sentry_manager):
        """Test Sentry manager health status."""
        health = sentry_manager.get_health_status()
        
        assert health.is_configured is True
        assert health.is_enabled is True  # If Sentry SDK is available
        assert health.last_check is not None
        assert isinstance(health.configuration_issues, list)
    
    def test_sentry_manager_dsn_info(self, sentry_manager):
        """Test DSN information extraction."""
        dsn_info = sentry_manager.get_dsn_info()
        
        assert dsn_info is not None
        assert "host" in dsn_info
        assert "project_id" in dsn_info
        assert dsn_info["project_id"] == "123456"
    
    def test_sentry_manager_transaction_context(self, sentry_manager):
        """Test transaction context manager."""
        with sentry_manager.capture_transaction("test_operation", "test") as transaction:
            assert transaction is not None or not sentry_manager.is_enabled()
    
    def test_sentry_manager_force_flush(self, sentry_manager):
        """Test force flush functionality."""
        result = sentry_manager.force_flush(timeout=1.0)
        assert isinstance(result, bool)
    
    def test_sentry_manager_shutdown(self, sentry_manager):
        """Test Sentry manager shutdown."""
        sentry_manager.shutdown()
        assert sentry_manager.is_initialized is False
        assert sentry_manager.health_status.is_enabled is False


class TestSentryErrorTracking:
    """Test suite for Sentry error tracking."""
    
    @pytest.fixture
    def error_tracker(self):
        """Create error tracker for testing."""
        return SentryErrorTracker()
    
    def test_error_categorization(self, error_tracker):
        """Test error categorization logic."""
        # Test authentication error
        auth_error = ValueError("Invalid authentication credentials")
        category = error_tracker.categorize_error(auth_error)
        assert category == ErrorCategory.AUTHENTICATION
        
        # Test validation error
        validation_error = ValueError("Missing required field")
        category = error_tracker.categorize_error(validation_error)
        assert category == ErrorCategory.VALIDATION
        
        # Test database error
        db_error = ConnectionError("Database connection failed")
        category = error_tracker.categorize_error(db_error)
        assert category in [ErrorCategory.DATABASE, ErrorCategory.NETWORK]
    
    def test_error_severity_determination(self, error_tracker):
        """Test error severity determination."""
        # Test critical error
        critical_error = MemoryError("Out of memory")
        context = ErrorContext(user_id="test_user")
        severity = error_tracker.determine_severity(
            critical_error, 
            ErrorCategory.MEMORY, 
            context
        )
        assert severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]
        
        # Test low severity error
        low_error = ValueError("Invalid input format")
        severity = error_tracker.determine_severity(
            low_error, 
            ErrorCategory.VALIDATION, 
            context
        )
        assert severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM]
    
    def test_error_fingerprinting(self, error_tracker):
        """Test error fingerprinting."""
        error = ValueError("Test error message")
        category = ErrorCategory.VALIDATION
        context = ErrorContext(function_name="test_function")
        
        fingerprint1 = error_tracker.create_error_fingerprint(error, category, context)
        fingerprint2 = error_tracker.create_error_fingerprint(error, category, context)
        
        assert fingerprint1 == fingerprint2  # Same error should have same fingerprint
        assert len(fingerprint1) == 16  # Should be 16 characters
    
    def test_error_context_enrichment(self, error_tracker):
        """Test error context enrichment."""
        error = ValueError("Test error")
        base_context = ErrorContext(user_id="test_user")
        
        enriched_context = error_tracker.enrich_error_context(error, base_context)
        
        assert enriched_context.user_id == "test_user"
        assert enriched_context.system_context is not None
        assert "python_version" in enriched_context.system_context
        assert enriched_context.business_context is not None
        assert "environment" in enriched_context.business_context
    
    def test_exception_tracking(self, error_tracker):
        """Test exception tracking."""
        error = ValueError("Test exception for tracking")
        context = ErrorContext(
            user_id="test_user",
            endpoint="/api/test",
            component="test_component"
        )
        
        event_id = error_tracker.track_exception(error, context)
        
        # Should return an event ID if Sentry is enabled
        assert isinstance(event_id, str)
        
        # Check error analytics
        analytics = error_tracker.get_error_analytics()
        assert "total_errors" in analytics
        assert "unique_errors" in analytics
        assert "category_distribution" in analytics
    
    def test_message_tracking(self, error_tracker):
        """Test message tracking."""
        message = "Test message for tracking"
        event_id = error_tracker.track_message(message)
        
        assert isinstance(event_id, str)
    
    def test_breadcrumb_management(self, error_tracker):
        """Test breadcrumb management."""
        from backend.core.sentry_error_tracking import BreadcrumbData, BreadcrumbLevel
        
        breadcrumb = BreadcrumbData(
            message="Test breadcrumb",
            level=BreadcrumbLevel.INFO,
            category="test",
            data={"test_key": "test_value"}
        )
        
        error_tracker.add_breadcrumb(breadcrumb)
        
        # Should not raise any exceptions
        assert True
    
    def test_error_analytics(self, error_tracker):
        """Test error analytics functionality."""
        analytics = error_tracker.get_error_analytics()
        
        required_keys = [
            "total_errors", "unique_errors", "recent_errors",
            "category_distribution", "severity_distribution", "top_errors"
        ]
        
        for key in required_keys:
            assert key in analytics
            assert isinstance(analytics[key], (int, dict, list))


class TestSentryPerformanceMonitoring:
    """Test suite for Sentry performance monitoring."""
    
    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor for testing."""
        return SentryPerformanceMonitor()
    
    def test_api_request_tracking(self, performance_monitor):
        """Test API request tracking."""
        performance_monitor.track_api_request(
            method="GET",
            endpoint="/api/test",
            status_code=200,
            response_time_ms=150.5,
            request_size_bytes=100,
            response_size_bytes=500,
            user_id="test_user",
            ip_address="127.0.0.1"
        )
        
        # Get performance summary
        summary = performance_monitor.get_performance_summary(time_window_minutes=60)
        
        assert "api_metrics" in summary
        assert "performance_health" in summary
    
    def test_database_query_tracking(self, performance_monitor):
        """Test database query tracking."""
        performance_monitor.track_database_query(
            query_type="SELECT",
            execution_time_ms=25.5,
            table="users",
            rows_affected=10,
            success=True
        )
        
        summary = performance_monitor.get_performance_summary(time_window_minutes=60)
        
        assert "database_metrics" in summary
    
    def test_custom_metric_tracking(self, performance_monitor):
        """Test custom metric tracking."""
        performance_monitor.track_custom_metric(
            name="test_metric",
            value=42.5,
            unit="count",
            tags={"component": "test"}
        )
        
        # Should not raise any exceptions
        assert True
    
    def test_operation_tracking(self, performance_monitor):
        """Test operation tracking with context manager."""
        with performance_monitor.track_operation("test_operation", "test_function"):
            time.sleep(0.01)  # Simulate some work
        
        # Should not raise any exceptions
        assert True
    
    def test_performance_summary(self, performance_monitor):
        """Test performance summary generation."""
        # Add some test data
        performance_monitor.track_api_request(
            method="GET", endpoint="/api/test", status_code=200,
            response_time_ms=100.0
        )
        
        summary = performance_monitor.get_performance_summary(time_window_minutes=60)
        
        required_keys = [
            "time_window_minutes", "api_metrics", "database_metrics",
            "custom_metrics", "slow_operations", "performance_health"
        ]
        
        for key in required_keys:
            assert key in summary
    
    def test_performance_health_evaluation(self, performance_monitor):
        """Test performance health evaluation."""
        health = performance_monitor._evaluate_overall_health({}, {})
        assert health in ["excellent", "good", "acceptable", "poor", "critical"]


class TestSentrySessionManagement:
    """Test suite for Sentry session management."""
    
    @pytest.fixture
    def session_manager(self):
        """Create session manager for testing."""
        return SentrySessionManager(default_session_ttl_minutes=60)
    
    def test_session_creation(self, session_manager):
        """Test session creation."""
        session_id = session_manager.create_session(
            user_id="test_user",
            session_type=SessionType.API,
            ip_address="127.0.0.1",
            user_agent="TestAgent/1.0"
        )
        
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        
        # Verify session was created
        session = session_manager.get_session_info(session_id)
        assert session is not None
        assert session.user_id == "test_user"
        assert session.session_type == SessionType.API
    
    def test_session_update(self, session_manager):
        """Test session update."""
        session_id = session_manager.create_session(user_id="test_user")
        
        success = session_manager.update_session(
            session_id=session_id,
            endpoint="/api/new_endpoint",
            metadata={"test": "value"}
        )
        
        assert success is True
        
        # Verify update
        session = session_manager.get_session_info(session_id)
        assert session.endpoint == "/api/new_endpoint"
        assert session.metadata["test"] == "value"
    
    def test_session_error_tracking(self, session_manager):
        """Test session error tracking."""
        session_id = session_manager.create_session(user_id="test_user")
        
        success = session_manager.track_session_error(
            error_id="test_error_id",
            session_id=session_id,
            error_type="ValueError",
            error_message="Test error",
            severity="medium",
            user_impacted=True
        )
        
        assert success is True
        
        # Verify error was tracked
        errors = session_manager.get_session_errors(session_id)
        assert len(errors) > 0
        assert errors[0].error_id == "test_error_id"
    
    def test_session_request_tracking(self, session_manager):
        """Test session request tracking."""
        session_id = session_manager.create_session(user_id="test_user")
        
        success = session_manager.track_session_request(
            session_id=session_id,
            endpoint="/api/test",
            method="GET",
            status_code=200,
            response_time_ms=150.0,
            success=True
        )
        
        assert success is True
        
        # Verify metrics were updated
        metrics = session_manager.get_session_metrics(session_id)
        assert metrics is not None
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
    
    def test_session_termination(self, session_manager):
        """Test session termination."""
        session_id = session_manager.create_session(user_id="test_user")
        
        success = session_manager.terminate_session(session_id, "test_reason")
        
        assert success is True
        
        # Verify session was terminated
        session = session_manager.get_session_info(session_id)
        assert session.status.value == "terminated"
    
    def test_session_analytics(self, session_manager):
        """Test session analytics."""
        # Create some test sessions
        session_manager.create_session(user_id="user1")
        session_manager.create_session(user_id="user2")
        
        analytics = session_manager.get_session_analytics(time_window_hours=24)
        
        required_keys = [
            "time_window_hours", "total_sessions", "active_sessions",
            "session_type_distribution", "avg_session_duration_minutes",
            "total_errors", "conversion_rate"
        ]
        
        for key in required_keys:
            assert key in analytics
    
    def test_active_sessions_retrieval(self, session_manager):
        """Test active sessions retrieval."""
        session_id = session_manager.create_session(user_id="test_user")
        
        active_sessions = session_manager.get_active_sessions()
        
        assert isinstance(active_sessions, list)
        # Should contain our created session
        session_ids = [s.session_id for s in active_sessions]
        assert session_id in session_ids


class TestSentryAlerting:
    """Test suite for Sentry alerting system."""
    
    @pytest.fixture
    def alerting_manager(self):
        """Create alerting manager for testing."""
        return SentryAlertingManager()
    
    def test_alert_rule_creation(self, alerting_manager):
        """Test alert rule creation."""
        rule = AlertRule(
            rule_id="test_rule",
            name="Test Alert Rule",
            description="Test alert rule description",
            alert_type=AlertType.ERROR_RATE,
            severity=AlertSeverity.WARNING,
            conditions={"metric": "error_rate", "operator": ">"},
            thresholds={"error_rate": 0.05}
        )
        
        success = alerting_manager.add_alert_rule(rule)
        
        assert success is True
        
        # Verify rule was added
        rules = alerting_manager.get_alert_rules()
        assert len(rules) > 0
        assert any(r.rule_id == "test_rule" for r in rules)
    
    def test_alert_rule_update(self, alerting_manager):
        """Test alert rule update."""
        # First create a rule
        rule = AlertRule(
            rule_id="test_update_rule",
            name="Test Update Rule",
            alert_type=AlertType.ERROR_RATE,
            severity=AlertSeverity.WARNING
        )
        alerting_manager.add_alert_rule(rule)
        
        # Update the rule
        success = alerting_manager.update_alert_rule(
            "test_update_rule",
            {"name": "Updated Rule Name", "severity": AlertSeverity.ERROR}
        )
        
        assert success is True
        
        # Verify update
        rules = alerting_manager.get_alert_rules()
        updated_rule = next(r for r in rules if r.rule_id == "test_update_rule")
        assert updated_rule.name == "Updated Rule Name"
        assert updated_rule.severity == AlertSeverity.ERROR
    
    def test_alert_rule_deletion(self, alerting_manager):
        """Test alert rule deletion."""
        # First create a rule
        rule = AlertRule(
            rule_id="test_delete_rule",
            name="Test Delete Rule",
            alert_type=AlertType.ERROR_RATE
        )
        alerting_manager.add_alert_rule(rule)
        
        # Delete the rule
        success = alerting_manager.delete_alert_rule("test_delete_rule")
        
        assert success is True
        
        # Verify deletion
        rules = alerting_manager.get_alert_rules()
        assert not any(r.rule_id == "test_delete_rule" for r in rules)
    
    def test_alert_acknowledgment(self, alerting_manager):
        """Test alert acknowledgment."""
        # This would require creating an actual alert first
        # For now, test the method exists and handles gracefully
        success = alerting_manager.acknowledge_alert("non_existent_alert_id")
        assert success is False
    
    def test_alert_suppression(self, alerting_manager):
        """Test alert suppression."""
        success = alerting_manager.suppress_alert("non_existent_alert_id", 30)
        assert success is False
    
    def test_alert_statistics(self, alerting_manager):
        """Test alert statistics."""
        stats = alerting_manager.get_alert_statistics()
        
        required_keys = [
            "total_alerts", "active_alerts", "recent_alerts_24h",
            "severity_distribution", "type_distribution",
            "total_rules", "enabled_rules"
        ]
        
        for key in required_keys:
            assert key in stats
            assert isinstance(stats[key], (int, dict))


class TestSentryDashboards:
    """Test suite for Sentry dashboard management."""
    
    @pytest.fixture
    def dashboard_manager(self):
        """Create dashboard manager for testing."""
        return SentryDashboardManager()
    
    def test_dashboard_creation(self, dashboard_manager):
        """Test dashboard creation."""
        dashboard_id = dashboard_manager.create_dashboard(
            name="Test Dashboard",
            description="Test dashboard description",
            dashboard_type=DashboardType.CUSTOM,
            created_by="test_user"
        )
        
        assert isinstance(dashboard_id, str)
        assert len(dashboard_id) > 0
        
        # Verify dashboard was created
        dashboard = dashboard_manager.get_dashboard(dashboard_id)
        assert dashboard is not None
        assert dashboard.name == "Test Dashboard"
        assert dashboard.created_by == "test_user"
    
    def test_dashboard_from_template(self, dashboard_manager):
        """Test dashboard creation from template."""
        dashboard_id = dashboard_manager.create_dashboard_from_template(
            template_id="system_overview",
            name="System Overview Test",
            created_by="test_user"
        )
        
        assert dashboard_id is not None
        
        # Verify dashboard was created with widgets
        dashboard = dashboard_manager.get_dashboard(dashboard_id)
        assert dashboard is not None
        assert len(dashboard.widgets) > 0
    
    def test_dashboard_update(self, dashboard_manager):
        """Test dashboard update."""
        # First create a dashboard
        dashboard_id = dashboard_manager.create_dashboard(
            name="Test Update Dashboard",
            dashboard_type=DashboardType.CUSTOM
        )
        
        # Update the dashboard
        success = dashboard_manager.update_dashboard(
            dashboard_id,
            {"name": "Updated Dashboard Name", "description": "Updated description"}
        )
        
        assert success is True
        
        # Verify update
        dashboard = dashboard_manager.get_dashboard(dashboard_id)
        assert dashboard.name == "Updated Dashboard Name"
        assert dashboard.description == "Updated description"
    
    def test_dashboard_deletion(self, dashboard_manager):
        """Test dashboard deletion."""
        # First create a dashboard
        dashboard_id = dashboard_manager.create_dashboard(
            name="Test Delete Dashboard",
            dashboard_type=DashboardType.CUSTOM
        )
        
        # Delete the dashboard
        success = dashboard_manager.delete_dashboard(dashboard_id)
        
        assert success is True
        
        # Verify deletion
        dashboard = dashboard_manager.get_dashboard(dashboard_id)
        assert dashboard is None
    
    def test_widget_management(self, dashboard_manager):
        """Test widget management."""
        # Create dashboard
        dashboard_id = dashboard_manager.create_dashboard(
            name="Test Widget Dashboard",
            dashboard_type=DashboardType.CUSTOM
        )
        
        # Add widget
        from backend.core.sentry_dashboards import WidgetConfig, WidgetType, AggregationType
        
        widget = WidgetConfig(
            name="Test Widget",
            widget_type=WidgetType.METRIC_CARD,
            position={"x": 0, "y": 0, "width": 3, "height": 2},
            data_source="performance",
            metrics=["avg_response_time_ms"],
            aggregation=AggregationType.AVERAGE
        )
        
        success = dashboard_manager.add_widget(dashboard_id, widget)
        assert success is True
        
        # Update widget
        success = dashboard_manager.update_widget(
            dashboard_id, widget.widget_id,
            {"name": "Updated Widget Name"}
        )
        assert success is True
        
        # Delete widget
        success = dashboard_manager.delete_widget(dashboard_id, widget.widget_id)
        assert success is True
    
    def test_dashboard_export_import(self, dashboard_manager):
        """Test dashboard export and import."""
        # Create dashboard with widgets
        dashboard_id = dashboard_manager.create_dashboard_from_template(
            template_id="system_overview",
            name="Export Test Dashboard"
        )
        
        # Export dashboard
        exported_config = dashboard_manager.export_dashboard(dashboard_id)
        assert exported_config is not None
        assert "name" in exported_config
        assert "widgets" in exported_config
        
        # Import dashboard
        imported_id = dashboard_manager.import_dashboard(
            exported_config,
            created_by="test_user"
        )
        assert imported_id is not None
        assert imported_id != dashboard_id  # Should be a new dashboard
        
        # Verify imported dashboard
        imported_dashboard = dashboard_manager.get_dashboard(imported_id)
        assert imported_dashboard is not None
        assert imported_dashboard.name == "Export Test Dashboard"
    
    def test_dashboard_templates(self, dashboard_manager):
        """Test dashboard templates."""
        templates = dashboard_manager.get_dashboard_templates()
        
        assert len(templates) > 0
        
        # Verify required templates exist
        template_ids = [t.template_id for t in templates]
        required_templates = [
            "system_overview",
            "performance_monitoring",
            "error_monitoring",
            "user_analytics"
        ]
        
        for template_id in required_templates:
            assert template_id in template_ids
    
    def test_widget_data_retrieval(self, dashboard_manager):
        """Test widget data retrieval."""
        # Create dashboard from template
        dashboard_id = dashboard_manager.create_dashboard_from_template(
            template_id="system_overview",
            name="Data Test Dashboard"
        )
        
        # Get dashboard data
        dashboard_data = dashboard_manager.get_dashboard_data(dashboard_id)
        
        assert "dashboard" in dashboard_data
        assert "widget_data" in dashboard_data
        assert "timestamp" in dashboard_data


class TestSentryMiddleware:
    """Test suite for Sentry middleware."""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        # Add Sentry middleware
        add_sentry_middleware(
            app,
            capture_request_body=True,
            capture_response_body=True,
            session_tracking=True,
            performance_tracking=True,
            error_tracking=True
        )
        
        return TestClient(app)
    
    def test_middleware_successful_request(self, client):
        """Test middleware with successful request."""
        response = client.get("/test")
        
        assert response.status_code == 200
        assert response.json() == {"message": "test"}
    
    def test_middleware_error_request(self, client):
        """Test middleware with error request."""
        response = client.get("/error")
        
        assert response.status_code == 500
    
    def test_middleware_request_headers(self, client):
        """Test middleware request header handling."""
        headers = {
            "x-user-id": "test_user",
            "x-session-id": "test_session",
            "user-agent": "TestAgent/1.0"
        }
        
        response = client.get("/test", headers=headers)
        
        assert response.status_code == 200
    
    def test_middleware_request_body(self, client):
        """Test middleware request body handling."""
        # Add POST endpoint for testing
        app = client.app
        
        @app.post("/test-post")
        async def test_post_endpoint(data: dict):
            return {"received": data}
        
        test_data = {"key": "value", "number": 42}
        response = client.post("/test-post", json=test_data)
        
        assert response.status_code == 200
        assert response.json()["received"] == test_data


class TestIntegration:
    """Integration tests for the complete Sentry system."""
    
    @pytest.fixture
    def integrated_system(self):
        """Set up integrated Sentry system."""
        # Initialize all components
        sentry_manager = get_sentry_manager()
        error_tracker = get_error_tracker()
        performance_monitor = get_performance_monitor()
        session_manager = get_session_manager()
        alerting_manager = get_alerting_manager()
        dashboard_manager = get_dashboard_manager()
        
        return {
            "sentry_manager": sentry_manager,
            "error_tracker": error_tracker,
            "performance_monitor": performance_monitor,
            "session_manager": session_manager,
            "alerting_manager": alerting_manager,
            "dashboard_manager": dashboard_manager
        }
    
    def test_end_to_end_error_flow(self, integrated_system):
        """Test end-to-end error flow."""
        session_manager = integrated_system["session_manager"]
        error_tracker = integrated_system["error_tracker"]
        performance_monitor = integrated_system["performance_monitor"]
        
        # Create session
        session_id = session_manager.create_session(user_id="test_user")
        
        # Track error
        error = ValueError("Test integration error")
        context = ErrorContext(
            user_id="test_user",
            session_id=session_id,
            endpoint="/api/integration_test"
        )
        
        event_id = error_tracker.track_exception(error, context)
        
        # Track session error
        session_manager.track_session_error(
            error_id=event_id,
            session_id=session_id,
            error_type="ValueError",
            error_message=str(error),
            user_impacted=True
        )
        
        # Track failed request
        performance_monitor.track_api_request(
            method="POST",
            endpoint="/api/integration_test",
            status_code=500,
            response_time_ms=250.0,
            success=False
        )
        
        # Verify data was captured
        session_errors = session_manager.get_session_errors(session_id)
        assert len(session_errors) > 0
        
        error_analytics = error_tracker.get_error_analytics()
        assert error_analytics["total_errors"] > 0
    
    def test_end_to_end_performance_flow(self, integrated_system):
        """Test end-to-end performance flow."""
        session_manager = integrated_system["session_manager"]
        performance_monitor = integrated_system["performance_monitor"]
        dashboard_manager = integrated_system["dashboard_manager"]
        
        # Create session
        session_id = session_manager.create_session(user_id="test_user")
        
        # Track multiple requests
        for i in range(5):
            performance_monitor.track_api_request(
                method="GET",
                endpoint=f"/api/test_{i}",
                status_code=200,
                response_time_ms=100.0 + (i * 10),
                success=True
            )
            
            session_manager.track_session_request(
                session_id=session_id,
                endpoint=f"/api/test_{i}",
                method="GET",
                status_code=200,
                response_time_ms=100.0 + (i * 10),
                success=True
            )
        
        # Track database queries
        for i in range(3):
            performance_monitor.track_database_query(
                query_type="SELECT",
                execution_time_ms=25.0 + (i * 5),
                table="users",
                success=True
            )
        
        # Create performance dashboard
        dashboard_id = dashboard_manager.create_dashboard_from_template(
            template_id="performance_monitoring",
            name="Integration Test Dashboard"
        )
        
        # Verify dashboard data
        dashboard_data = dashboard_manager.get_dashboard_data(dashboard_id)
        assert "dashboard" in dashboard_data
        assert "widget_data" in dashboard_data
        
        # Verify session metrics
        session_metrics = session_manager.get_session_metrics(session_id)
        assert session_metrics.total_requests == 5
        assert session_metrics.successful_requests == 5
    
    def test_system_health_monitoring(self, integrated_system):
        """Test system health monitoring."""
        sentry_manager = integrated_system["sentry_manager"]
        performance_monitor = integrated_system["performance_monitor"]
        
        # Check Sentry health
        sentry_health = sentry_manager.get_health_status()
        assert sentry_health.is_configured is True
        
        # Get performance summary
        perf_summary = performance_monitor.get_performance_summary()
        assert "performance_health" in perf_summary
        
        # Health should be one of the expected values
        health_status = perf_summary["performance_health"]
        assert health_status in ["excellent", "good", "acceptable", "poor", "critical"]


# Performance and load testing
class TestPerformanceAndLoad:
    """Performance and load testing for Sentry integration."""
    
    def test_high_volume_error_tracking(self):
        """Test tracking high volume of errors."""
        error_tracker = get_error_tracker()
        
        # Track many errors
        start_time = time.time()
        
        for i in range(100):
            error = ValueError(f"Test error {i}")
            context = ErrorContext(
                user_id=f"user_{i % 10}",
                endpoint=f"/api/endpoint_{i % 5}"
            )
            error_tracker.track_exception(error, context)
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time
        assert duration < 5.0  # 5 seconds
        
        # Verify analytics
        analytics = error_tracker.get_error_analytics()
        assert analytics["total_errors"] >= 100
    
    def test_high_volume_performance_tracking(self):
        """Test tracking high volume of performance data."""
        performance_monitor = get_performance_monitor()
        
        # Track many API requests
        start_time = time.time()
        
        for i in range(1000):
            performance_monitor.track_api_request(
                method="GET",
                endpoint=f"/api/test_{i % 20}",
                status_code=200 if i % 10 != 0 else 500,
                response_time_ms=100.0 + (i % 200),
                success=i % 10 != 0
            )
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time
        assert duration < 3.0  # 3 seconds
        
        # Verify performance summary
        summary = performance_monitor.get_performance_summary()
        assert "api_metrics" in summary
        assert summary["api_metrics"]["total_requests"] >= 1000
    
    def test_concurrent_session_tracking(self):
        """Test concurrent session tracking."""
        session_manager = get_session_manager()
        
        def create_and_track_session(user_id: str):
            session_id = session_manager.create_session(user_id=user_id)
            
            # Track some activity
            for i in range(5):
                session_manager.track_session_request(
                    session_id=session_id,
                    endpoint=f"/api/test_{i}",
                    method="GET",
                    status_code=200,
                    response_time_ms=100.0,
                    success=True
                )
            
            return session_id
        
        # Create sessions concurrently
        import threading
        
        threads = []
        session_ids = []
        
        def worker(user_id: str):
            session_id = create_and_track_session(user_id)
            session_ids.append(session_id)
        
        start_time = time.time()
        
        # Create 50 concurrent sessions
        for i in range(50):
            thread = threading.Thread(target=worker, args=(f"user_{i}",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time
        assert duration < 5.0  # 5 seconds
        
        # Verify sessions were created
        assert len(session_ids) == 50
        
        # Verify session analytics
        analytics = session_manager.get_session_analytics()
        assert analytics["total_sessions"] >= 50


# Test configuration and utilities
@pytest.fixture(scope="session")
def test_logging():
    """Configure test logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@pytest.fixture(autouse=True)
def cleanup_sentry():
    """Clean up Sentry after each test."""
    yield
    
    # Clean up any test data
    try:
        shutdown_sentry()
    except Exception:
        pass


# Mock Sentry SDK for testing
@pytest.fixture(autouse=True)
def mock_sentry_sdk():
    """Mock Sentry SDK for testing."""
    mock_modules = {
        'sentry_sdk': Mock(),
        'sentry_sdk.integrations': Mock(),
        'sentry_sdk.tracing': Mock(),
    }
    
    with patch.dict('sys.modules', mock_modules):
        yield


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
