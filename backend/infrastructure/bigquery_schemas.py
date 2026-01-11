"""
BigQuery table schemas for Raptorflow analytics.

Defines standardized schemas for all analytics tables
including agent executions, usage events, and user events.
"""

from datetime import datetime
from typing import Any, Dict, List


class BigQuerySchemas:
    """BigQuery table schema definitions."""

    # Agent Executions Schema
    agent_executions_schema = [
        {
            "name": "execution_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Unique identifier for the agent execution",
        },
        {
            "name": "workspace_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Workspace identifier",
        },
        {
            "name": "user_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "User who initiated the execution",
        },
        {
            "name": "agent_type",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Type of agent (e.g., 'muse', 'research', 'analysis')",
        },
        {
            "name": "agent_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Agent identifier",
        },
        {
            "name": "status",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Execution status (e.g., 'started', 'completed', 'failed')",
        },
        {
            "name": "input_tokens",
            "type": "INT64",
            "mode": "NULLABLE",
            "description": "Number of input tokens used",
        },
        {
            "name": "output_tokens",
            "type": "INT64",
            "mode": "NULLABLE",
            "description": "Number of output tokens generated",
        },
        {
            "name": "execution_time_ms",
            "type": "INT64",
            "mode": "NULLABLE",
            "description": "Execution time in milliseconds",
        },
        {
            "name": "cost_usd",
            "type": "FLOAT64",
            "mode": "NULLABLE",
            "description": "Cost in USD",
        },
        {
            "name": "model_used",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "AI model used for execution",
        },
        {
            "name": "error_type",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Type of error if execution failed",
        },
        {
            "name": "error_message",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Error message if execution failed",
        },
        {
            "name": "request_metadata",
            "type": "JSON",
            "mode": "NULLABLE",
            "description": "Additional request metadata",
        },
        {
            "name": "response_metadata",
            "type": "JSON",
            "mode": "NULLABLE",
            "description": "Additional response metadata",
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "mode": "REQUIRED",
            "description": "When the execution was created",
        },
        {
            "name": "started_at",
            "type": "TIMESTAMP",
            "mode": "NULLABLE",
            "description": "When the execution started",
        },
        {
            "name": "completed_at",
            "type": "TIMESTAMP",
            "mode": "NULLABLE",
            "description": "When the execution completed",
        },
    ]

    # Usage Events Schema
    usage_events_schema = [
        {
            "name": "event_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Unique identifier for the usage event",
        },
        {
            "name": "workspace_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Workspace identifier",
        },
        {
            "name": "user_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "User who generated the usage",
        },
        {
            "name": "feature",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Feature being used (e.g., 'muse_generate', 'file_upload')",
        },
        {
            "name": "usage_type",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Type of usage (e.g., 'api_call', 'storage', 'compute')",
        },
        {
            "name": "usage_amount",
            "type": "FLOAT64",
            "mode": "REQUIRED",
            "description": "Amount of usage (e.g., tokens, bytes, seconds)",
        },
        {
            "name": "usage_unit",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Unit of usage (e.g., 'tokens', 'bytes', 'seconds')",
        },
        {
            "name": "cost_usd",
            "type": "FLOAT64",
            "mode": "NULLABLE",
            "description": "Cost in USD for this usage",
        },
        {
            "name": "pricing_tier",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Pricing tier applied",
        },
        {
            "name": "session_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Session identifier",
        },
        {
            "name": "request_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Request identifier",
        },
        {
            "name": "metadata",
            "type": "JSON",
            "mode": "NULLABLE",
            "description": "Additional usage metadata",
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "mode": "REQUIRED",
            "description": "When the usage event occurred",
        },
    ]

    # User Events Schema
    user_events_schema = [
        {
            "name": "event_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Unique identifier for the user event",
        },
        {
            "name": "workspace_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Workspace identifier",
        },
        {
            "name": "user_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "User who performed the action",
        },
        {
            "name": "event_type",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Type of event (e.g., 'login', 'logout', 'create_workspace')",
        },
        {
            "name": "action",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Specific action performed",
        },
        {
            "name": "resource_type",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Type of resource affected",
        },
        {
            "name": "resource_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Identifier of affected resource",
        },
        {
            "name": "ip_address",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "IP address of the user",
        },
        {
            "name": "user_agent",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "User agent string",
        },
        {
            "name": "session_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Session identifier",
        },
        {
            "name": "success",
            "type": "BOOLEAN",
            "mode": "NULLABLE",
            "description": "Whether the action was successful",
        },
        {
            "name": "error_code",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Error code if action failed",
        },
        {
            "name": "error_message",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Error message if action failed",
        },
        {
            "name": "metadata",
            "type": "JSON",
            "mode": "NULLABLE",
            "description": "Additional event metadata",
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "mode": "REQUIRED",
            "description": "When the event occurred",
        },
    ]

    # Workspace Events Schema
    workspace_events_schema = [
        {
            "name": "event_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Unique identifier for the workspace event",
        },
        {
            "name": "workspace_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Workspace identifier",
        },
        {
            "name": "event_type",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Type of workspace event",
        },
        {
            "name": "actor_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "User who performed the action",
        },
        {
            "name": "actor_role",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Role of the actor",
        },
        {
            "name": "target_type",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Type of target affected",
        },
        {
            "name": "target_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Identifier of target affected",
        },
        {
            "name": "old_value",
            "type": "JSON",
            "mode": "NULLABLE",
            "description": "Previous value (for updates)",
        },
        {
            "name": "new_value",
            "type": "JSON",
            "mode": "NULLABLE",
            "description": "New value (for updates)",
        },
        {
            "name": "metadata",
            "type": "JSON",
            "mode": "NULLABLE",
            "description": "Additional event metadata",
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "mode": "REQUIRED",
            "description": "When the event occurred",
        },
    ]

    # Performance Metrics Schema
    performance_metrics_schema = [
        {
            "name": "metric_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Unique identifier for the metric",
        },
        {
            "name": "workspace_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Workspace identifier",
        },
        {
            "name": "metric_name",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Name of the metric",
        },
        {
            "name": "metric_type",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Type of metric (e.g., 'counter', 'gauge', 'histogram')",
        },
        {
            "name": "value",
            "type": "FLOAT64",
            "mode": "REQUIRED",
            "description": "Metric value",
        },
        {
            "name": "unit",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Unit of measurement",
        },
        {
            "name": "tags",
            "type": "JSON",
            "mode": "NULLABLE",
            "description": "Metric tags for filtering",
        },
        {
            "name": "source",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Source of the metric",
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "mode": "REQUIRED",
            "description": "When the metric was recorded",
        },
    ]

    # Error Events Schema
    error_events_schema = [
        {
            "name": "error_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Unique identifier for the error",
        },
        {
            "name": "workspace_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Workspace identifier",
        },
        {
            "name": "user_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "User who encountered the error",
        },
        {
            "name": "error_type",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Type of error",
        },
        {
            "name": "error_code",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Error code",
        },
        {
            "name": "error_message",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Error message",
        },
        {
            "name": "stack_trace",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Stack trace",
        },
        {
            "name": "severity",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Error severity (e.g., 'low', 'medium', 'high', 'critical')",
        },
        {
            "name": "component",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Component where error occurred",
        },
        {
            "name": "request_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Request identifier",
        },
        {
            "name": "session_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Session identifier",
        },
        {
            "name": "context",
            "type": "JSON",
            "mode": "NULLABLE",
            "description": "Additional error context",
        },
        {
            "name": "resolved",
            "type": "BOOLEAN",
            "mode": "NULLABLE",
            "description": "Whether the error has been resolved",
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "mode": "REQUIRED",
            "description": "When the error occurred",
        },
    ]

    # File Operations Schema
    file_operations_schema = [
        {
            "name": "operation_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Unique identifier for the file operation",
        },
        {
            "name": "workspace_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Workspace identifier",
        },
        {
            "name": "user_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "User who performed the operation",
        },
        {
            "name": "operation_type",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Type of operation (e.g., 'upload', 'download', 'delete')",
        },
        {
            "name": "file_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "File identifier",
        },
        {
            "name": "filename",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "File name",
        },
        {
            "name": "file_type",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "File type/MIME type",
        },
        {
            "name": "file_size_bytes",
            "type": "INT64",
            "mode": "NULLABLE",
            "description": "File size in bytes",
        },
        {
            "name": "bucket_name",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Storage bucket name",
        },
        {
            "name": "storage_path",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Storage path",
        },
        {
            "name": "success",
            "type": "BOOLEAN",
            "mode": "NULLABLE",
            "description": "Whether the operation was successful",
        },
        {
            "name": "error_message",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Error message if operation failed",
        },
        {
            "name": "duration_ms",
            "type": "INT64",
            "mode": "NULLABLE",
            "description": "Operation duration in milliseconds",
        },
        {
            "name": "metadata",
            "type": "JSON",
            "mode": "NULLABLE",
            "description": "Additional operation metadata",
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "mode": "REQUIRED",
            "description": "When the operation occurred",
        },
    ]

    # API Requests Schema
    api_requests_schema = [
        {
            "name": "request_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Unique identifier for the API request",
        },
        {
            "name": "workspace_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Workspace identifier",
        },
        {
            "name": "user_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "User who made the request",
        },
        {
            "name": "method",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "HTTP method",
        },
        {
            "name": "endpoint",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "API endpoint",
        },
        {
            "name": "status_code",
            "type": "INT64",
            "mode": "REQUIRED",
            "description": "HTTP status code",
        },
        {
            "name": "response_time_ms",
            "type": "INT64",
            "mode": "NULLABLE",
            "description": "Response time in milliseconds",
        },
        {
            "name": "request_size_bytes",
            "type": "INT64",
            "mode": "NULLABLE",
            "description": "Request size in bytes",
        },
        {
            "name": "response_size_bytes",
            "type": "INT64",
            "mode": "NULLABLE",
            "description": "Response size in bytes",
        },
        {
            "name": "ip_address",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Client IP address",
        },
        {
            "name": "user_agent",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "User agent string",
        },
        {
            "name": "error_code",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Error code if request failed",
        },
        {
            "name": "error_message",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Error message if request failed",
        },
        {
            "name": "metadata",
            "type": "JSON",
            "mode": "NULLABLE",
            "description": "Additional request metadata",
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "mode": "REQUIRED",
            "description": "When the request was made",
        },
    ]

    # Billing Events Schema
    billing_events_schema = [
        {
            "name": "billing_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Unique identifier for the billing event",
        },
        {
            "name": "workspace_id",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Workspace identifier",
        },
        {
            "name": "user_id",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "User who incurred the cost",
        },
        {
            "name": "billing_period",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Billing period (e.g., '2024-01')",
        },
        {
            "name": "service",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Service that incurred the cost",
        },
        {
            "name": "usage_type",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Type of usage",
        },
        {
            "name": "usage_amount",
            "type": "FLOAT64",
            "mode": "REQUIRED",
            "description": "Amount of usage",
        },
        {
            "name": "usage_unit",
            "type": "STRING",
            "mode": "REQUIRED",
            "description": "Unit of usage",
        },
        {
            "name": "unit_price_usd",
            "type": "FLOAT64",
            "mode": "REQUIRED",
            "description": "Price per unit in USD",
        },
        {
            "name": "total_cost_usd",
            "type": "FLOAT64",
            "mode": "REQUIRED",
            "description": "Total cost in USD",
        },
        {
            "name": "currency",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Currency code",
        },
        {
            "name": "pricing_tier",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Pricing tier applied",
        },
        {
            "name": "discount_applied",
            "type": "FLOAT64",
            "mode": "NULLABLE",
            "description": "Discount applied in USD",
        },
        {
            "name": "metadata",
            "type": "JSON",
            "mode": "NULLABLE",
            "description": "Additional billing metadata",
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "mode": "REQUIRED",
            "description": "When the billing event was recorded",
        },
    ]

    @classmethod
    def get_all_schemas(cls) -> Dict[str, List[Dict[str, Any]]]:
        """Get all table schemas."""
        return {
            "agent_executions": cls.agent_executions_schema,
            "usage_events": cls.usage_events_schema,
            "user_events": cls.user_events_schema,
            "workspace_events": cls.workspace_events_schema,
            "performance_metrics": cls.performance_metrics_schema,
            "error_events": cls.error_events_schema,
            "file_operations": cls.file_operations_schema,
            "api_requests": cls.api_requests_schema,
            "billing_events": cls.billing_events_schema,
        }

    @classmethod
    def get_schema(cls, table_name: str) -> Optional[List[Dict[str, Any]]]:
        """Get schema for a specific table."""
        schemas = cls.get_all_schemas()
        return schemas.get(table_name)

    @classmethod
    def validate_schema(cls, schema: List[Dict[str, Any]]) -> List[str]:
        """Validate a schema definition."""
        errors = []

        if not schema:
            errors.append("Schema cannot be empty")
            return errors

        required_fields = ["name", "type", "mode"]

        for i, field in enumerate(schema):
            # Check required fields
            for required_field in required_fields:
                if required_field not in field:
                    errors.append(
                        f"Field {i}: Missing required field '{required_field}'"
                    )

            # Check field types
            if "name" in field and not isinstance(field["name"], str):
                errors.append(f"Field {i}: 'name' must be a string")

            if "type" in field and not isinstance(field["type"], str):
                errors.append(f"Field {i}: 'type' must be a string")

            if "mode" in field and field["mode"] not in [
                "REQUIRED",
                "NULLABLE",
                "REPEATED",
            ]:
                errors.append(
                    f"Field {i}: 'mode' must be 'REQUIRED', 'NULLABLE', or 'REPEATED'"
                )

            # Check nested fields for RECORD type
            if field.get("type") == "RECORD" and "fields" in field:
                nested_errors = cls.validate_schema(field["fields"])
                if nested_errors:
                    errors.extend(
                        [f"Nested field {i}: {error}" for error in nested_errors]
                    )

        return errors

    @classmethod
    def get_partitioning_recommendations(cls, table_name: str) -> Optional[str]:
        """Get partitioning field recommendation for a table."""
        partitioning_map = {
            "agent_executions": "created_at",
            "usage_events": "created_at",
            "user_events": "created_at",
            "workspace_events": "created_at",
            "performance_metrics": "created_at",
            "error_events": "created_at",
            "file_operations": "created_at",
            "api_requests": "created_at",
            "billing_events": "created_at",
        }

        return partitioning_map.get(table_name)

    @classmethod
    def get_clustering_recommendations(cls, table_name: str) -> Optional[List[str]]:
        """Get clustering field recommendations for a table."""
        clustering_map = {
            "agent_executions": ["workspace_id", "agent_type", "status"],
            "usage_events": ["workspace_id", "feature", "usage_type"],
            "user_events": ["workspace_id", "user_id", "event_type"],
            "workspace_events": ["workspace_id", "event_type", "actor_id"],
            "performance_metrics": ["workspace_id", "metric_name", "source"],
            "error_events": ["workspace_id", "error_type", "severity"],
            "file_operations": ["workspace_id", "user_id", "operation_type"],
            "api_requests": ["workspace_id", "method", "endpoint"],
            "billing_events": ["workspace_id", "service", "billing_period"],
        }

        return clustering_map.get(table_name)

    @classmethod
    def get_table_descriptions(cls) -> Dict[str, str]:
        """Get descriptions for all tables."""
        return {
            "agent_executions": "Records of all agent executions with performance metrics",
            "usage_events": "Usage tracking for billing and analytics",
            "user_events": "User activity and interaction events",
            "workspace_events": "Workspace-level events and audit trail",
            "performance_metrics": "System performance and health metrics",
            "error_events": "Error tracking and debugging information",
            "file_operations": "File upload/download/delete operations",
            "api_requests": "API request logging and monitoring",
            "billing_events": "Billing and cost tracking events",
        }

    @classmethod
    def get_sample_queries(cls) -> Dict[str, str]:
        """Get sample queries for common analytics."""
        return {
            "daily_agent_usage": """
                SELECT
                    DATE(created_at) as date,
                    agent_type,
                    COUNT(*) as executions,
                    AVG(execution_time_ms) as avg_execution_time,
                    SUM(cost_usd) as total_cost
                FROM `project.dataset.agent_executions`
                WHERE workspace_id = @workspace_id
                    AND created_at BETWEEN @start_date AND @end_date
                GROUP BY DATE(created_at), agent_type
                ORDER BY date DESC, executions DESC
            """,
            "usage_by_feature": """
                SELECT
                    feature,
                    usage_type,
                    SUM(usage_amount) as total_usage,
                    SUM(cost_usd) as total_cost,
                    COUNT(*) as events
                FROM `project.dataset.usage_events`
                WHERE workspace_id = @workspace_id
                    AND created_at BETWEEN @start_date AND @end_date
                GROUP BY feature, usage_type
                ORDER BY total_cost DESC
            """,
            "user_activity_summary": """
                SELECT
                    user_id,
                    COUNT(*) as total_events,
                    COUNT(DISTINCT event_type) as unique_event_types,
                    MIN(created_at) as first_activity,
                    MAX(created_at) as last_activity
                FROM `project.dataset.user_events`
                WHERE workspace_id = @workspace_id
                    AND created_at BETWEEN @start_date AND @end_date
                GROUP BY user_id
                ORDER BY total_events DESC
            """,
            "error_analysis": """
                SELECT
                    error_type,
                    severity,
                    COUNT(*) as error_count,
                    COUNT(DISTINCT user_id) as affected_users,
                    STRING_AGG(DISTINCT component, ', ') as components
                FROM `project.dataset.error_events`
                WHERE workspace_id = @workspace_id
                    AND created_at BETWEEN @start_date AND @end_date
                GROUP BY error_type, severity
                ORDER BY error_count DESC
            """,
            "performance_trends": """
                SELECT
                    DATE(created_at) as date,
                    metric_name,
                    AVG(value) as avg_value,
                    MIN(value) as min_value,
                    MAX(value) as max_value,
                    COUNT(*) as measurements
                FROM `project.dataset.performance_metrics`
                WHERE workspace_id = @workspace_id
                    AND created_at BETWEEN @start_date AND @end_date
                GROUP BY DATE(created_at), metric_name
                ORDER BY date DESC, avg_value DESC
            """,
        }


# Convenience functions
def get_agent_executions_schema() -> List[Dict[str, Any]]:
    """Get agent executions schema."""
    return BigQuerySchemas.agent_executions_schema


def get_usage_events_schema() -> List[Dict[str, Any]]:
    """Get usage events schema."""
    return BigQuerySchemas.usage_events_schema


def get_user_events_schema() -> List[Dict[str, Any]]:
    """Get user events schema."""
    return BigQuerySchemas.user_events_schema


def get_all_schemas() -> Dict[str, List[Dict[str, Any]]]:
    """Get all table schemas."""
    return BigQuerySchemas.get_all_schemas()


def validate_schema(schema: List[Dict[str, Any]]) -> List[str]:
    """Validate a schema definition."""
    return BigQuerySchemas.validate_schema(schema)


def get_partitioning_recommendation(table_name: str) -> Optional[str]:
    """Get partitioning recommendation for table."""
    return BigQuerySchemas.get_partitioning_recommendations(table_name)


def get_clustering_recommendation(table_name: str) -> Optional[List[str]]:
    """Get clustering recommendation for table."""
    return BigQuerySchemas.get_clustering_recommendations(table_name)
