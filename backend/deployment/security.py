"""
Security configuration for RaptorFlow backend.
Provides security policies, secrets management, and compliance.
"""

import os
from typing import Any, Dict, List


class SecurityConfig:
    """Security configuration management."""

    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "raptorflow-prod")
        self.region = os.getenv("GCP_REGION", "us-central1")
        self.namespace = "raptorflow-prod"
        self.service_name = "raptorflow-backend"

    def get_security_policies(self) -> Dict[str, Any]:
        """Generate security policies configuration."""
        return {
            "authentication": {
                "enabled": True,
                "methods": ["jwt", "oauth2"],
                "jwt": {
                    "secret_key": os.getenv("JWT_SECRET_KEY"),
                    "algorithm": "HS256",
                    "access_token_expire_minutes": 30,
                    "refresh_token_expire_days": 7,
                },
                "oauth2": {
                    "providers": ["google", "github"],
                    "google": {
                        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    },
                    "github": {
                        "client_id": os.getenv("GITHUB_CLIENT_ID"),
                        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
                    },
                },
            },
            "authorization": {
                "enabled": True,
                "rbac": {
                    "roles": ["admin", "user", "viewer"],
                    "permissions": {
                        "admin": ["read", "write", "delete", "manage"],
                        "user": ["read", "write"],
                        "viewer": ["read"],
                    },
                },
            },
            "encryption": {
                "at_rest": {
                    "enabled": True,
                    "algorithm": "AES-256-GCM",
                    "key_rotation_days": 90,
                },
                "in_transit": {
                    "enabled": True,
                    "tls_version": "1.3",
                    "cipher_suites": [
                        "TLS_AES_256_GCM_SHA384",
                        "TLS_CHACHA20_POLY1305_SHA256",
                        "TLS_AES_128_GCM_SHA256",
                    ],
                },
            },
            "network": {
                "firewall": {
                    "enabled": True,
                    "rules": [
                        {
                            "name": "allow-http",
                            "protocol": "tcp",
                            "ports": [80],
                            "source_ranges": ["0.0.0.0/0"],
                        },
                        {
                            "name": "allow-https",
                            "protocol": "tcp",
                            "ports": [443],
                            "source_ranges": ["0.0.0.0/0"],
                        },
                        {
                            "name": "allow-internal",
                            "protocol": "tcp",
                            "ports": [8000],
                            "source_ranges": [
                                "10.0.0.0/8",
                                "172.16.0.0/12",
                                "192.168.0.0/16",
                            ],
                        },
                    ],
                },
                "vpc": {
                    "enabled": True,
                    "private_ip": True,
                    "subnets": [
                        {
                            "name": "raptorflow-subnet",
                            "ip_range": "10.0.0.0/24",
                            "region": self.region,
                        }
                    ],
                },
            },
            "secrets": {
                "manager": "gcp_secret_manager",
                "rotation": {"enabled": True, "interval_days": 90, "automatic": True},
                "access": {
                    "principals": [
                        f"serviceAccount:raptorflow-sa@{self.project_id}.iam.gserviceaccount.com"
                    ],
                    "roles": ["Secret Manager Secret Accessor"],
                },
            },
            "audit": {
                "enabled": True,
                "logging": {
                    "level": "INFO",
                    "retention_days": 365,
                    "fields": [
                        "timestamp",
                        "user_id",
                        "action",
                        "resource",
                        "ip_address",
                        "user_agent",
                    ],
                },
                "alerts": {
                    "suspicious_activity": True,
                    "failed_auth_attempts": True,
                    "privilege_escalation": True,
                },
            },
            "compliance": {
                "standards": ["SOC2", "GDPR", "HIPAA"],
                "data_classification": {
                    "public": {"encryption": False, "access_log": False},
                    "internal": {"encryption": True, "access_log": True},
                    "confidential": {
                        "encryption": True,
                        "access_log": True,
                        "retention_days": 2555,
                    },
                    "restricted": {
                        "encryption": True,
                        "access_log": True,
                        "retention_days": 2555,
                        "additional_controls": True,
                    },
                },
            },
        }

    def get_secrets_config(self) -> Dict[str, Any]:
        """Generate secrets management configuration."""
        return {
            "secret_manager": {
                "project_id": self.project_id,
                "location": self.region,
                "secrets": [
                    {
                        "name": "raptorflow-prod-secrets",
                        "replication": {
                            "automatic": True,
                            "replication_policy": "automatic",
                        },
                        "version": "1",
                        "data": {
                            "SECRET_KEY": os.getenv("SECRET_KEY"),
                            "DATABASE_URL": os.getenv("DATABASE_URL"),
                            "UPSTABASE_REDIS_TOKEN": os.getenv("UPSTABASE_REDIS_TOKEN"),
                            "VERTEX_AI_PROJECT_ID": os.getenv("VERTEX_AI_PROJECT_ID"),
                            "WEBHOOK_SECRET": os.getenv("WEBHOOK_SECRET"),
                            "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY"),
                            "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
                            "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
                            "GITHUB_CLIENT_ID": os.getenv("GITHUB_CLIENT_ID"),
                            "GITHUB_CLIENT_SECRET": os.getenv("GITHUB_CLIENT_SECRET"),
                            "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD"),
                            "SLACK_WEBHOOK_URL": os.getenv("SLACK_WEBHOOK_URL"),
                            "PAGERDUTY_SERVICE_KEY": os.getenv("PAGERDUTY_SERVICE_KEY"),
                            "ERROR_REPORTING_API_KEY": os.getenv(
                                "ERROR_REPORTING_API_KEY"
                            ),
                            "JAEGER_ENDPOINT": os.getenv("JAEGER_ENDPOINT"),
                            "ZIPKIN_ENDPOINT": os.getenv("ZIPKIN_ENDPOINT"),
                        },
                    },
                    {
                        "name": "raptorflow-db-credentials",
                        "replication": {
                            "automatic": True,
                            "replication_policy": "automatic",
                        },
                        "version": "1",
                        "data": {
                            "POSTGRES_USER": os.getenv("POSTGRES_USER"),
                            "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
                            "POSTGRES_DB": os.getenv("POSTGRES_DB", "raptorflow_prod"),
                        },
                    },
                    {
                        "name": "raptorflow-api-keys",
                        "replication": {
                            "automatic": True,
                            "replication_policy": "automatic",
                        },
                        "version": "1",
                        "data": {
                            "VERTEX_AI_API_KEY": os.getenv("VERTEX_AI_API_KEY"),
                            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
                            "GOOGLE_AI_API_KEY": os.getenv("GOOGLE_AI_API_KEY"),
                        },
                    },
                ],
            },
            "rotation": {
                "enabled": True,
                "interval_days": 90,
                "automatic": True,
                "notification_channels": ["email", "slack"],
            },
            "access": {
                "principals": [
                    f"serviceAccount:raptorflow-sa@{self.project_id}.iam.gserviceaccount.com"
                ],
                "roles": ["Secret Manager Secret Accessor"],
                "conditions": {
                    "request.time": {"within": {"duration": "86400s"}}  # 24 hours
                },
            },
        }

    def get_iam_policies(self) -> Dict[str, Any]:
        """Generate IAM policies configuration."""
        return {
            "bindings": [
                {
                    "role": "roles/cloudrun.admin",
                    "members": [
                        f"serviceAccount:raptorflow-sa@{self.project_id}.iam.gserviceaccount.com"
                    ],
                },
                {
                    "role": "roles/cloudsql.admin",
                    "members": [
                        f"serviceAccount:raptorflow-sa@{self.project_id}.iam.gserviceaccount.com"
                    ],
                },
                {
                    "role": "roles/secretmanager.secretAccessor",
                    "members": [
                        f"serviceAccount:raptorflow-sa@{self.project_id}.iam.gserviceaccount.com"
                    ],
                },
                {
                    "role": "roles/logging.logWriter",
                    "members": [
                        f"serviceAccount:raptorflow-sa@{self.project_id}.iam.gserviceaccount.com"
                    ],
                },
                {
                    "role": "roles/monitoring.metricWriter",
                    "members": [
                        f"serviceAccount:raptorflow-sa@{self.project_id}.iam.gserviceaccount.com"
                    ],
                },
                {
                    "role": "roles/aiplatform.user",
                    "members": [
                        f"serviceAccount:raptorflow-sa@{self.project_id}.iam.gserviceaccount.com"
                    ],
                },
                {
                    "role": "roles/bigquery.admin",
                    "members": [
                        f"serviceAccount:raptorflow-sa@{self.project_id}.iam.gserviceaccount.com"
                    ],
                },
            ],
            "audit_configs": [
                {
                    "service": "allServices",
                    "audit_log_configs": [
                        {"log_type": "ADMIN_READ", "exempted_members": []},
                        {"log_type": "DATA_WRITE", "exempted_members": []},
                        {"log_type": "DATA_READ", "exempted_members": []},
                    ],
                }
            ],
        }

    def get_network_security_config(self) -> Dict[str, Any]:
        """Generate network security configuration."""
        return {
            "vpc": {
                "name": "raptorflow-vpc",
                "auto_create_subnetworks": False,
                "routing_mode": "REGIONAL",
                "subnetworks": [
                    {
                        "name": "raptorflow-subnet",
                        "ip_cidr_range": "10.0.0.0/24",
                        "region": self.region,
                        "private_ip_google_access": True,
                        "secondary_ip_ranges": [
                            {
                                "range_name": "raptorflow-pods",
                                "ip_cidr_range": "10.1.0.0/24",
                            },
                            {
                                "range_name": "raptorflow-services",
                                "ip_cidr_range": "10.2.0.0/24",
                            },
                        ],
                    }
                ],
            },
            "firewall": {
                "rules": [
                    {
                        "name": "allow-internal",
                        "network": "raptorflow-vpc",
                        "direction": "INGRESS",
                        "priority": 1000,
                        "source_ranges": [
                            "10.0.0.0/8",
                            "172.16.0.0/12",
                            "192.168.0.0/16",
                        ],
                        "allow": [
                            {"protocol": "tcp", "ports": ["0-65535"]},
                            {"protocol": "udp", "ports": ["0-65535"]},
                            {"protocol": "icmp"},
                        ],
                    },
                    {
                        "name": "allow-ssh",
                        "network": "raptorflow-vpc",
                        "direction": "INGRESS",
                        "priority": 1001,
                        "source_ranges": ["0.0.0.0/0"],
                        "allow": [{"protocol": "tcp", "ports": ["22"]}],
                    },
                    {
                        "name": "deny-all-ingress",
                        "network": "raptorflow-vpc",
                        "direction": "INGRESS",
                        "priority": 65535,
                        "source_ranges": ["0.0.0.0/0"],
                        "deny": [
                            {"protocol": "tcp", "ports": ["0-65535"]},
                            {"protocol": "udp", "ports": ["0-65535"]},
                            {"protocol": "icmp"},
                        ],
                    },
                ]
            },
            "cloud_armor": {
                "policy": {
                    "name": "raptorflow-security-policy",
                    "description": "Security policy for RaptorFlow backend",
                    "rules": [
                        {
                            "name": "allow-internal",
                            "priority": 1000,
                            "match": {
                                "versioned_expr": {
                                    "expr_config": "origin.region_code == 'US'"
                                }
                            },
                            "action": "ALLOW",
                        },
                        {
                            "name": "rate-limit",
                            "priority": 1001,
                            "match": {
                                "versioned_expr": {
                                    "expr_config": "origin.ip != '0.0.0.0'"
                                }
                            },
                            "rate_limit": {
                                "rate_limit": {
                                    "interval": "60s",
                                    "requests_per_interval": 100,
                                }
                            },
                            "action": "ALLOW",
                        },
                        {
                            "name": "block-malicious",
                            "priority": 1002,
                            "match": {
                                "expr": {
                                    "expression": "evaluatePreconfiguredExpr('sqli-stable')"
                                }
                            },
                            "action": "DENY",
                        },
                    ],
                }
            },
        }

    def get_compliance_config(self) -> Dict[str, Any]:
        """Generate compliance configuration."""
        return {
            "standards": {
                "SOC2": {
                    "enabled": True,
                    "controls": [
                        {
                            "id": "CC1.1",
                            "name": "Control Environment",
                            "description": "Maintain and communicate policies",
                            "implemented": True,
                        },
                        {
                            "id": "CC2.1",
                            "name": "Risk Assessment",
                            "description": "Identify and assess risks",
                            "implemented": True,
                        },
                        {
                            "id": "CC3.1",
                            "name": "Control Activities",
                            "description": "Design and implement controls",
                            "implemented": True,
                        },
                        {
                            "id": "CC4.1",
                            "name": "Information and Communication",
                            "description": "Communicate and monitor controls",
                            "implemented": True,
                        },
                        {
                            "id": "CC5.1",
                            "name": "Monitoring Activities",
                            "description": "Monitor and evaluate controls",
                            "implemented": True,
                        },
                    ],
                },
                "GDPR": {
                    "enabled": True,
                    "controls": [
                        {
                            "id": "ART32",
                            "name": "Security of Processing",
                            "description": "Implement appropriate technical measures",
                            "implemented": True,
                        },
                        {
                            "id": "ART33",
                            "name": "Confidentiality and Integrity",
                            "description": "Ensure processing security",
                            "implemented": True,
                        },
                        {
                            "id": "ART34",
                            "name": "Data Protection Impact Assessment",
                            "description": "Conduct DPIA when required",
                            "implemented": True,
                        },
                    ],
                },
                "HIPAA": {
                    "enabled": False,
                    "controls": [
                        {
                            "id": "164.312",
                            "name": "Technical Safeguards",
                            "description": "Implement technical security measures",
                            "implemented": False,
                        }
                    ],
                },
            },
            "data_classification": {
                "public": {
                    "description": "Publicly available information",
                    "encryption": False,
                    "access_log": False,
                    "retention_days": 365,
                },
                "internal": {
                    "description": "Internal company information",
                    "encryption": True,
                    "access_log": True,
                    "retention_days": 1095,
                },
                "confidential": {
                    "description": "Confidential business information",
                    "encryption": True,
                    "access_log": True,
                    "retention_days": 2555,
                },
                "restricted": {
                    "description": "Highly sensitive information",
                    "encryption": True,
                    "access_log": True,
                    "retention_days": 2555,
                    "additional_controls": True,
                },
            },
            "audit": {
                "enabled": True,
                "logging": {
                    "level": "INFO",
                    "retention_days": 365,
                    "fields": [
                        "timestamp",
                        "user_id",
                        "action",
                        "resource",
                        "ip_address",
                        "user_agent",
                        "result",
                        "error",
                    ],
                },
                "alerts": {
                    "suspicious_activity": True,
                    "failed_auth_attempts": True,
                    "privilege_escalation": True,
                    "data_access": True,
                    "configuration_changes": True,
                },
                "reports": {
                    "frequency": "weekly",
                    "recipients": ["security@raptorflow.com"],
                    "include": [
                        "failed_auth_attempts",
                        "suspicious_activity",
                        "privilege_escalation",
                        "data_access",
                    ],
                },
            },
        }

    def get_vulnerability_scanning_config(self) -> Dict[str, Any]:
        """Generate vulnerability scanning configuration."""
        return {
            "enabled": True,
            "scanners": [
                {
                    "name": "dependency_check",
                    "type": "sast",
                    "enabled": True,
                    "schedule": "daily",
                    "tools": ["safety", "bandit", "semgrep"],
                },
                {
                    "name": "container_scan",
                    "type": "container",
                    "enabled": True,
                    "schedule": "on_push",
                    "tools": ["trivy", "clair"],
                },
                {
                    "name": "infrastructure_scan",
                    "type": "iac",
                    "enabled": True,
                    "schedule": "weekly",
                    "tools": ["tfsec", "checkov"],
                },
            ],
            "policies": [
                {
                    "name": "critical_vulnerabilities",
                    "severity": "critical",
                    "action": "block",
                    "threshold": 0,
                },
                {
                    "name": "high_vulnerabilities",
                    "severity": "high",
                    "action": "warn",
                    "threshold": 5,
                },
                {
                    "name": "medium_vulnerabilities",
                    "severity": "medium",
                    "action": "warn",
                    "threshold": 10,
                },
            ],
            "notifications": {
                "channels": ["email", "slack"],
                "recipients": ["security@raptorflow.com"],
                "conditions": [
                    "critical_vulnerabilities > 0",
                    "high_vulnerabilities > 5",
                ],
            },
        }

    def get_penetration_testing_config(self) -> Dict[str, Any]:
        """Generate penetration testing configuration."""
        return {
            "enabled": True,
            "schedule": "quarterly",
            "scope": [
                {
                    "name": "web_application",
                    "url": "https://raptorflow-backend.com",
                    "methods": ["GET", "POST", "PUT", "DELETE"],
                    "exclusions": ["/admin", "/internal"],
                },
                {
                    "name": "api_endpoints",
                    "url": "https://api.raptorflow.com",
                    "methods": ["GET", "POST", "PUT", "DELETE"],
                    "exclusions": ["/admin", "/internal"],
                },
            ],
            "tools": ["burp_suite", "owasp_zap", "nmap", "sqlmap"],
            "reporting": {
                "format": "pdf",
                "recipients": ["security@raptorflow.com", "cto@raptorflow.com"],
                "include": [
                    "executive_summary",
                    "technical_findings",
                    "risk_assessment",
                    "recommendations",
                ],
            },
            "remediation": {
                "timeline": "30_days",
                "tracking": True,
                "verification": True,
            },
        }

    def get_incident_response_config(self) -> Dict[str, Any]:
        """Generate incident response configuration."""
        return {
            "enabled": True,
            "team": {
                "lead": "security@raptorflow.com",
                "members": [
                    "cto@raptorflow.com",
                    "devops@raptorflow.com",
                    "legal@raptorflow.com",
                ],
            },
            "severity_levels": [
                {
                    "level": "critical",
                    "response_time": "15_minutes",
                    "escalation": True,
                    "notification_channels": ["email", "slack", "pagerduty"],
                },
                {
                    "level": "high",
                    "response_time": "1_hour",
                    "escalation": True,
                    "notification_channels": ["email", "slack"],
                },
                {
                    "level": "medium",
                    "response_time": "4_hours",
                    "escalation": False,
                    "notification_channels": ["email"],
                },
                {
                    "level": "low",
                    "response_time": "24_hours",
                    "escalation": False,
                    "notification_channels": ["email"],
                },
            ],
            "procedures": [
                {
                    "name": "data_breach",
                    "steps": [
                        "Identify affected data",
                        "Contain breach",
                        "Notify stakeholders",
                        "Document incident",
                        "Post-incident review",
                    ],
                },
                {
                    "name": "service_outage",
                    "steps": [
                        "Assess impact",
                        "Restore service",
                        "Communicate status",
                        "Investigate root cause",
                        "Implement fixes",
                    ],
                },
                {
                    "name": "security_violation",
                    "steps": [
                        "Investigate violation",
                        "Gather evidence",
                        "Report to authorities",
                        "Implement corrective actions",
                        "Review policies",
                    ],
                },
            ],
            "communication": {
                "templates": {
                    "initial_notification": "security_incident_initial.md",
                    "status_update": "security_incident_update.md",
                    "resolution": "security_incident_resolution.md",
                },
                "channels": ["email", "slack"],
                "stakeholders": ["security@raptorflow.com", "cto@raptorflow.com"],
            },
        }

    def get_backup_and_recovery_config(self) -> Dict[str, Any]:
        """Generate backup and recovery configuration."""
        return {
            "database": {
                "enabled": True,
                "schedule": "daily",
                "retention": "30_days",
                "encryption": True,
                "location": "gcs://raptorflow-backups/database",
                "point_in_time_recovery": True,
            },
            "files": {
                "enabled": True,
                "schedule": "daily",
                "retention": "90_days",
                "encryption": True,
                "location": "gcs://raptorflow-backups/files",
            },
            "secrets": {
                "enabled": True,
                "schedule": "weekly",
                "retention": "365_days",
                "encryption": True,
                "location": "gcs://raptorflow-backups/secrets",
            },
            "recovery": {
                "rto": "4_hours",  # Recovery Time Objective
                "rpo": "1_hour",  # Recovery Point Objective
                "procedures": [
                    "database_restore",
                    "file_restore",
                    "secrets_restore",
                    "service_restart",
                ],
                "testing": {
                    "frequency": "monthly",
                    "scenarios": [
                        "database_corruption",
                        "file_deletion",
                        "secrets_compromise",
                        "service_failure",
                    ],
                },
            },
        }

    def get_disaster_recovery_config(self) -> Dict[str, Any]:
        """Generate disaster recovery configuration."""
        return {
            "enabled": True,
            "regions": [
                {
                    "primary": self.region,
                    "secondary": "us-east1",
                    "failover_time": "30_minutes",
                }
            ],
            "services": [
                {
                    "name": "database",
                    "replication": True,
                    "failover": "automatic",
                    "rto": "1_hour",
                    "rpo": "5_minutes",
                },
                {
                    "name": "application",
                    "replication": True,
                    "failover": "manual",
                    "rto": "4_hours",
                    "rpo": "1_hour",
                },
                {
                    "name": "storage",
                    "replication": True,
                    "failover": "automatic",
                    "rto": "15_minutes",
                    "rpo": "0_minutes",
                },
            ],
            "testing": {
                "frequency": "quarterly",
                "scenarios": [
                    "region_failure",
                    "service_failure",
                    "data_corruption",
                    "security_breach",
                ],
            },
            "documentation": {
                "runbook": "disaster_recovery_runbook.md",
                "contacts": [
                    "security@raptorflow.com",
                    "cto@raptorflow.com",
                    "devops@raptorflow.com",
                ],
            },
        }
