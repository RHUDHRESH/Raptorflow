"""
Monitoring configuration for RaptorFlow backend.
Provides Prometheus, Grafana, and logging setup.
"""

import os
from typing import Any, Dict, List


class MonitoringConfig:
    """Monitoring configuration management."""

    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "raptorflow-prod")
        self.region = os.getenv("GCP_REGION", "us-central1")
        self.namespace = "raptorflow-prod"
        self.service_name = "raptorflow-backend"

    def get_prometheus_config(self) -> Dict[str, Any]:
        """Generate Prometheus configuration."""
        return {
            "global": {"scrape_interval": "15s", "evaluation_interval": "15s"},
            "scrape_configs": [
                {
                    "job_name": "raptorflow-backend",
                    "static_configs": [
                        {
                            "targets": ["raptorflow-backend:8000"],
                            "labels": {
                                "service": "raptorflow-backend",
                                "environment": "production",
                            },
                        }
                    ],
                    "metrics_path": "/metrics",
                    "scrape_interval": "10s",
                    "scrape_timeout": "5s",
                },
                {
                    "job_name": "postgres",
                    "static_configs": [
                        {
                            "targets": ["postgres-exporter:9187"],
                            "labels": {
                                "service": "postgres",
                                "environment": "production",
                            },
                        }
                    ],
                    "metrics_path": "/metrics",
                    "scrape_interval": "30s",
                },
                {
                    "job_name": "redis",
                    "static_configs": [
                        {
                            "targets": ["redis-exporter:9121"],
                            "labels": {"service": "redis", "environment": "production"},
                        }
                    ],
                    "metrics_path": "/metrics",
                    "scrape_interval": "30s",
                },
            ],
            "rule_files": ["raptorflow-rules.yml"],
            "alerting": {
                "alertmanagers": [
                    {"static_configs": [{"targets": ["alertmanager:9093"]}]}
                ]
            },
        }

    def get_grafana_dashboard_config(self) -> Dict[str, Any]:
        """Generate Grafana dashboard configuration."""
        return {
            "dashboard": {
                "id": None,
                "title": "RaptorFlow Backend Dashboard",
                "tags": ["raptorflow", "backend", "production"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Request Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(raptorflow_requests_total[5m])",
                                "legendFormat": "{{method}} {{endpoint}}",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                    },
                    {
                        "id": 2,
                        "title": "Response Time",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(raptorflow_request_duration_seconds_bucket[5m]))",
                                "legendFormat": "95th percentile",
                            },
                            {
                                "expr": "histogram_quantile(0.50, rate(raptorflow_request_duration_seconds_bucket[5m]))",
                                "legendFormat": "50th percentile",
                            },
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                    },
                    {
                        "id": 3,
                        "title": "Error Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": 'rate(raptorflow_requests_total{status=~"5.."}[5m]) / rate(raptorflow_requests_total[5m])',
                                "legendFormat": "Error Rate",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                    },
                    {
                        "id": 4,
                        "title": "Memory Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "process_resident_memory_bytes / 1024 / 1024",
                                "legendFormat": "Memory (MB)",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                    },
                    {
                        "id": 5,
                        "title": "CPU Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(process_cpu_seconds_total[5m]) * 100",
                                "legendFormat": "CPU (%)",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16},
                    },
                    {
                        "id": 6,
                        "title": "Database Connections",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "pg_stat_database_numbackends",
                                "legendFormat": "Active Connections",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16},
                    },
                    {
                        "id": 7,
                        "title": "Redis Connections",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "redis_connected_clients",
                                "legendFormat": "Connected Clients",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 24},
                    },
                    {
                        "id": 8,
                        "title": "Agent Executions",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(raptorflow_agent_executions_total[5m])",
                                "legendFormat": "Executions/sec",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 24},
                    },
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "5s",
            }
        }

    def get_alertmanager_config(self) -> Dict[str, Any]:
        """Generate Alertmanager configuration."""
        return {
            "global": {
                "smtp_smarthost": "smtp.gmail.com:587",
                "smtp_from": "alerts@raptorflow.com",
                "smtp_auth_username": "alerts@raptorflow.com",
                "smtp_auth_password": os.getenv("SMTP_PASSWORD"),
            },
            "route": {
                "group_by": ["alertname", "cluster", "service"],
                "group_wait": "10s",
                "group_interval": "10s",
                "repeat_interval": "1h",
                "receiver": "web.hook",
                "routes": [
                    {"match": {"severity": "critical"}, "receiver": "critical-alerts"},
                    {"match": {"severity": "warning"}, "receiver": "warning-alerts"},
                ],
            },
            "receivers": [
                {
                    "name": "web.hook",
                    "webhook_configs": [
                        {
                            "url": os.getenv(
                                "WEBHOOK_URL", "https://hooks.slack.com/services/xxx"
                            )
                        }
                    ],
                },
                {
                    "name": "critical-alerts",
                    "email_configs": [
                        {
                            "to": "team@raptorflow.com",
                            "subject": "Critical Alert: {{ .GroupLabels.alertname }}",
                            "body": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}",
                        }
                    ],
                    "webhook_configs": [
                        {
                            "url": os.getenv(
                                "WEBHOOK_URL", "https://hooks.slack.com/services/xxx"
                            ),
                            "send_resolved": True,
                        }
                    ],
                },
                {
                    "name": "warning-alerts",
                    "email_configs": [
                        {
                            "to": "team@raptorflow.com",
                            "subject": "Warning: {{ .GroupLabels.alertname }}",
                            "body": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}",
                        }
                    ],
                },
            ],
            "inhibit_rules": [
                {
                    "source_match": {"severity": "critical"},
                    "target_match": {"severity": "warning"},
                    "equal": ["alertname", "cluster", "service"],
                }
            ],
        }

    def get_prometheus_rules(self) -> Dict[str, Any]:
        """Generate Prometheus alerting rules."""
        return {
            "groups": [
                {
                    "name": "raptorflow.rules",
                    "rules": [
                        {
                            "alert": "HighErrorRate",
                            "expr": 'rate(raptorflow_requests_total{status=~"5.."}[5m]) / rate(raptorflow_requests_total[5m]) > 0.05',
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High error rate detected",
                                "description": "Error rate is {{ $value | humanizePercentage }} for the last 5 minutes",
                            },
                        },
                        {
                            "alert": "HighResponseTime",
                            "expr": "histogram_quantile(0.95, rate(raptorflow_request_duration_seconds_bucket[5m])) > 2",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High response time detected",
                                "description": "95th percentile response time is {{ $value }}s for the last 5 minutes",
                            },
                        },
                        {
                            "alert": "ServiceDown",
                            "expr": 'up{job="raptorflow-backend"} == 0',
                            "for": "1m",
                            "labels": {"severity": "critical"},
                            "annotations": {
                                "summary": "RaptorFlow backend service is down",
                                "description": "RaptorFlow backend service has been down for more than 1 minute",
                            },
                        },
                        {
                            "alert": "HighMemoryUsage",
                            "expr": "process_resident_memory_bytes / 1024 / 1024 > 400",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High memory usage detected",
                                "description": "Memory usage is {{ $value }}MB for the last 5 minutes",
                            },
                        },
                        {
                            "alert": "HighCPUUsage",
                            "expr": "rate(process_cpu_seconds_total[5m]) * 100 > 80",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High CPU usage detected",
                                "description": "CPU usage is {{ $value }}% for the last 5 minutes",
                            },
                        },
                        {
                            "alert": "DatabaseConnectionsHigh",
                            "expr": "pg_stat_database_numbackends > 80",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High database connections",
                                "description": "Database has {{ $value }} active connections",
                            },
                        },
                        {
                            "alert": "RedisConnectionsHigh",
                            "expr": "redis_connected_clients > 100",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High Redis connections",
                                "description": "Redis has {{ $value }} connected clients",
                            },
                        },
                    ],
                }
            ]
        }

    def get_logging_config(self) -> Dict[str, Any]:
        """Generate logging configuration."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                },
                "json": {
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                },
            },
            "handlers": {
                "console": {
                    "level": "INFO",
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                },
                "file": {
                    "level": "INFO",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "/app/logs/raptorflow.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "formatter": "json",
                },
                "cloud_logging": {
                    "level": "INFO",
                    "class": "google.cloud.logging.handlers.CloudLoggingHandler",
                    "formatter": "json",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["console", "file", "cloud_logging"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["console", "file", "cloud_logging"],
                    "level": "INFO",
                    "propagate": False,
                },
                "sqlalchemy": {
                    "handlers": ["console", "file", "cloud_logging"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "redis": {
                    "handlers": ["console", "file", "cloud_logging"],
                    "level": "WARNING",
                    "propagate": False,
                },
            },
        }

    def get_tracing_config(self) -> Dict[str, Any]:
        """Generate distributed tracing configuration."""
        return {
            "service_name": "raptorflow-backend",
            "sampling": {"type": "probabilistic", "param": 0.1},
            "exporter": {
                "jaeger": {
                    "endpoint": os.getenv(
                        "JAEGER_ENDPOINT", "http://jaeger:14268/api/traces"
                    ),
                    "auth": {"type": "none"},
                },
                "zipkin": {
                    "endpoint": os.getenv(
                        "ZIPKIN_ENDPOINT", "http://zipkin:9411/api/v2/spans"
                    ),
                    "auth": {"type": "none"},
                },
            },
            "instrumentation": {
                "http": {
                    "enabled": True,
                    "trace_requests": True,
                    "trace_responses": True,
                },
                "sqlalchemy": {
                    "enabled": True,
                    "trace_execute": True,
                    "trace_commit": True,
                },
                "redis": {"enabled": True, "trace_commands": True},
            },
        }

    def get_health_check_config(self) -> Dict[str, Any]:
        """Generate health check configuration."""
        return {
            "checks": [
                {
                    "name": "database",
                    "type": "sql",
                    "connection_string": os.getenv("DATABASE_URL"),
                    "query": "SELECT 1",
                    "timeout": 5,
                },
                {
                    "name": "redis",
                    "type": "redis",
                    "connection_string": os.getenv("UPSTABASE_REDIS_URL"),
                    "command": "PING",
                    "timeout": 5,
                },
                {"name": "memory", "type": "memory", "threshold_mb": 400, "timeout": 5},
                {"name": "cpu", "type": "cpu", "threshold_percent": 80, "timeout": 5},
            ],
            "endpoint": "/health",
            "method": "GET",
            "response_format": "json",
        }

    def get_metrics_config(self) -> Dict[str, Any]:
        """Generate metrics configuration."""
        return {
            "prometheus": {
                "enabled": True,
                "port": 8000,
                "path": "/metrics",
                "registry": "default",
            },
            "custom_metrics": [
                {
                    "name": "raptorflow_requests_total",
                    "type": "counter",
                    "description": "Total number of requests",
                    "labels": ["method", "endpoint", "status"],
                },
                {
                    "name": "raptorflow_request_duration_seconds",
                    "type": "histogram",
                    "description": "Request duration in seconds",
                    "labels": ["method", "endpoint"],
                    "buckets": [0.1, 0.5, 1.0, 2.0, 5.0],
                },
                {
                    "name": "raptorflow_agent_executions_total",
                    "type": "counter",
                    "description": "Total number of agent executions",
                    "labels": ["agent_name", "status"],
                },
                {
                    "name": "raptorflow_cognitive_processing_time",
                    "type": "histogram",
                    "description": "Cognitive processing time in seconds",
                    "labels": ["module", "operation"],
                    "buckets": [0.1, 0.5, 1.0, 2.0, 5.0],
                },
                {
                    "name": "raptorflow_memory_storage_size",
                    "type": "gauge",
                    "description": "Memory storage size in bytes",
                    "labels": ["memory_type"],
                },
                {
                    "name": "raptorflow_cache_hit_rate",
                    "type": "gauge",
                    "description": "Cache hit rate",
                    "labels": ["cache_type"],
                },
            ],
        }

    def get_error_reporting_config(self) -> Dict[str, Any]:
        """Generate error reporting configuration."""
        return {
            "enabled": True,
            "service_name": "raptorflow-backend",
            "environment": "production",
            "api_key": os.getenv("ERROR_REPORTING_API_KEY"),
            "project_id": self.project_id,
            "service_version": os.getenv("APP_VERSION", "1.0.0"),
            "report_uncaught_exceptions": True,
            "report_unhandled_rejections": True,
            "ignore_exceptions": ["KeyboardInterrupt", "SystemExit", "GeneratorExit"],
            "context": {
                "runtime": "python",
                "framework": "fastapi",
                "database": "postgresql",
                "cache": "redis",
            },
        }

    def get_performance_monitoring_config(self) -> Dict[str, Any]:
        """Generate performance monitoring configuration."""
        return {
            "enabled": True,
            "sampling_rate": 0.1,
            "profiling": {"enabled": True, "duration": 60, "interval": 300},
            "metrics": [
                {"name": "response_time", "type": "histogram", "threshold": 2.0},
                {"name": "throughput", "type": "counter", "threshold": 100},
                {"name": "error_rate", "type": "gauge", "threshold": 0.05},
            ],
            "alerts": [
                {
                    "name": "slow_requests",
                    "condition": "response_time > 2.0",
                    "duration": "5m",
                    "severity": "warning",
                },
                {
                    "name": "low_throughput",
                    "condition": "throughput < 10",
                    "duration": "5m",
                    "severity": "warning",
                },
                {
                    "name": "high_error_rate",
                    "condition": "error_rate > 0.05",
                    "duration": "5m",
                    "severity": "critical",
                },
            ],
        }

    def get_log_analytics_config(self) -> Dict[str, Any]:
        """Generate log analytics configuration."""
        return {
            "enabled": True,
            "destination": "bigquery",
            "dataset": "raptorflow_logs",
            "table": "application_logs",
            "schema": [
                {"name": "timestamp", "type": "TIMESTAMP"},
                {"name": "level", "type": "STRING"},
                {"name": "logger", "type": "STRING"},
                {"name": "message", "type": "STRING"},
                {"name": "request_id", "type": "STRING"},
                {"name": "user_id", "type": "STRING"},
                {"name": "workspace_id", "type": "STRING"},
                {"name": "method", "type": "STRING"},
                {"name": "endpoint", "type": "STRING"},
                {"name": "status_code", "type": "INTEGER"},
                {"name": "duration", "type": "FLOAT"},
                {"name": "error", "type": "STRING"},
                {"name": "stack_trace", "type": "STRING"},
            ],
            "retention": "30d",
            "partitioning": "timestamp",
            "clustering": "timestamp",
            "compression": "GZIP",
        }

    def get_alerting_config(self) -> Dict[str, Any]:
        """Generate alerting configuration."""
        return {
            "enabled": True,
            "channels": [
                {
                    "name": "email",
                    "type": "email",
                    "enabled": True,
                    "config": {
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587,
                        "username": "alerts@raptorflow.com",
                        "password": os.getenv("SMTP_PASSWORD"),
                        "recipients": ["team@raptorflow.com"],
                    },
                },
                {
                    "name": "slack",
                    "type": "slack",
                    "enabled": True,
                    "config": {
                        "webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
                        "channel": "#alerts",
                        "username": "RaptorFlow Alerts",
                    },
                },
                {
                    "name": "pagerduty",
                    "type": "pagerduty",
                    "enabled": False,
                    "config": {
                        "service_key": os.getenv("PAGERDUTY_SERVICE_KEY"),
                        "severity": "critical",
                    },
                },
            ],
            "rules": [
                {
                    "name": "service_down",
                    "condition": "up == 0",
                    "duration": "1m",
                    "severity": "critical",
                    "channels": ["email", "slack", "pagerduty"],
                },
                {
                    "name": "high_error_rate",
                    "condition": "error_rate > 0.05",
                    "duration": "5m",
                    "severity": "warning",
                    "channels": ["email", "slack"],
                },
                {
                    "name": "slow_response_time",
                    "condition": "p95_response_time > 2.0",
                    "duration": "5m",
                    "severity": "warning",
                    "channels": ["email", "slack"],
                },
                {
                    "name": "high_memory_usage",
                    "condition": "memory_usage > 400",
                    "duration": "5m",
                    "severity": "warning",
                    "channels": ["email", "slack"],
                },
                {
                    "name": "high_cpu_usage",
                    "condition": "cpu_usage > 80",
                    "duration": "5m",
                    "severity": "warning",
                    "channels": ["email", "slack"],
                },
            ],
        }

    def get_dashboard_config(self) -> Dict[str, Any]:
        """Generate dashboard configuration."""
        return {
            "title": "RaptorFlow Backend Dashboard",
            "description": "Comprehensive monitoring dashboard for RaptorFlow backend",
            "panels": [
                {
                    "title": "Service Health",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": 'up{job="raptorflow-backend"}',
                            "legendFormat": "{{instance}}",
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [
                                {
                                    "options": {
                                        "0": {"text": "DOWN", "color": "red"},
                                        "1": {"text": "UP", "color": "green"},
                                    },
                                    "type": "value",
                                }
                            ]
                        }
                    },
                },
                {
                    "title": "Request Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(raptorflow_requests_total[5m])",
                            "legendFormat": "{{method}} {{endpoint}}",
                        }
                    ],
                    "yAxes": [{"label": "Requests/sec", "min": 0}],
                },
                {
                    "title": "Response Time",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.95, rate(raptorflow_request_duration_seconds_bucket[5m]))",
                            "legendFormat": "95th percentile",
                        },
                        {
                            "expr": "histogram_quantile(0.50, rate(raptorflow_request_duration_seconds_bucket[5m]))",
                            "legendFormat": "50th percentile",
                        },
                    ],
                    "yAxes": [{"label": "Seconds", "min": 0}],
                },
                {
                    "title": "Error Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(raptorflow_requests_total{status=~"5.."}[5m]) / rate(raptorflow_requests_total[5m])',
                            "legendFormat": "Error Rate",
                        }
                    ],
                    "yAxes": [
                        {"label": "Error Rate", "min": 0, "max": 1, "format": "percent"}
                    ],
                },
                {
                    "title": "Memory Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "process_resident_memory_bytes / 1024 / 1024",
                            "legendFormat": "Memory (MB)",
                        }
                    ],
                    "yAxes": [{"label": "Memory (MB)", "min": 0}],
                },
                {
                    "title": "CPU Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(process_cpu_seconds_total[5m]) * 100",
                            "legendFormat": "CPU (%)",
                        }
                    ],
                    "yAxes": [{"label": "CPU (%)", "min": 0, "max": 100}],
                },
                {
                    "title": "Database Connections",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "pg_stat_database_numbackends",
                            "legendFormat": "Active Connections",
                        }
                    ],
                    "yAxes": [{"label": "Connections", "min": 0}],
                },
                {
                    "title": "Redis Connections",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "redis_connected_clients",
                            "legendFormat": "Connected Clients",
                        }
                    ],
                    "yAxes": [{"label": "Clients", "min": 0}],
                },
                {
                    "title": "Agent Executions",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(raptorflow_agent_executions_total[5m])",
                            "legendFormat": "Executions/sec",
                        }
                    ],
                    "yAxes": [{"label": "Executions/sec", "min": 0}],
                },
                {
                    "title": "Cognitive Processing Time",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.95, rate(raptorflow_cognitive_processing_time_bucket[5m]))",
                            "legendFormat": "95th percentile",
                        }
                    ],
                    "yAxes": [{"label": "Seconds", "min": 0}],
                },
                {
                    "title": "Memory Storage Size",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "raptorflow_memory_storage_size / 1024 / 1024",
                            "legendFormat": "{{memory_type}} (MB)",
                        }
                    ],
                    "yAxes": [{"label": "Size (MB)", "min": 0}],
                },
                {
                    "title": "Cache Hit Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "raptorflow_cache_hit_rate",
                            "legendFormat": "{{cache_type}}",
                        }
                    ],
                    "yAxes": [
                        {"label": "Hit Rate", "min": 0, "max": 1, "format": "percent"}
                    ],
                },
            ],
            "time": {"from": "now-1h", "to": "now"},
            "refresh": "5s",
        }
