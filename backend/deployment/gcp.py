"""
GCP configuration for RaptorFlow backend.
Provides Cloud Run, Cloud SQL, and monitoring setup.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List


class GCPConfig:
    """GCP configuration management."""

    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "raptorflow-prod")
        self.region = os.getenv("GCP_REGION", "us-central1")
        self.zone = os.getenv("GCP_ZONE", "us-central1-c")
        self.service_account_key = os.getenv("GCP_SERVICE_ACCOUNT_KEY")
        self.artifact_registry = f"{self.project_id}.pkg.dev"
        self.cloud_run_service = "raptorflow-backend"

    def get_cloudbuild_config(self) -> Dict[str, Any]:
        """Generate Cloud Build configuration."""
        return {
            "steps": [
                {
                    "name": "Build Docker image",
                    "args": [
                        "build",
                        "-t",
                        f"gcr.io/{self.artifact_registry}/{self.cloud_run_service}:latest",
                        "."
                    ]
                },
                {
                    "name": "Push to Artifact Registry",
                    "args": [
                        "docker",
                        "push",
                        f"gcr.io/{self.artifact_registry}/{self.cloud_run_service}:latest"
                    ]
                }
            ],
            "images": [
                f"gcr.io/{self.artifact_registry}/{self.cloud_run_service}:latest"
            ],
            "timeout": "1200s"
        }

    def get_cloud_run_deployment(self) -> Dict[str, Any]:
        """Generate Cloud Run deployment configuration."""
        return {
            "name": self.cloud_run_service,
            "image": f"gcr.io/{self.artifact_registry}/{self.cloud_run_service}:latest",
            "region": self.region,
            "platform": "managed",
            "allowUnauthenticated": False,
            "port": 8000,
            "memory": "512Mi",
            "cpu": "1",
            "timeout": "300s",
            "minInstances": "1",
            "maxInstances": "3",
            "concurrency": 100,
            "env": [
                {
                    "name": "ENVIRONMENT",
                    "value": "production"
                },
                {
                    "name": "SECRET_KEY",
                    "value": os.getenv("SECRET_KEY", "")
                },
                {
                    "name": "DATABASE_URL",
                    "value": os.getenv("DATABASE_URL", "")
                },
                {
                    "name": "UPSTABASE_REDIS_URL",
                    "value": os.getenv("UPSTABASE_REDIS_URL", "")
                },
                {
                    "name": "UPSTABASE_REDIS_TOKEN",
                    "value": os.getenv("UPSTASE_REDIS_TOKEN", "")
                },
                {
                    "name": "VERTEX_AI_PROJECT_ID",
                    "value": os.getenv("VERTEX_AI_PROJECT_ID", "")
                },
                {
                    "name": "GCP_PROJECT_ID",
                    "value": self.project_id
                },
                {
                    "name": "WEBHOOK_SECRET",
                    "value": os.getenv("WEBHOOK_SECRET", "")
                },
                {
                    "name": "ALLOWED_ORIGINS",
                    "value": os.getenv("ALLOWED_ORIGINS", "*")
                }
            ],
            "volumes": [
                {
                    "name": "cloudsql",
                    "mountPath": "/cloudsql"
                }
            ],
            "cloudSqlInstances": [
                f"projects/{self.project_id}/instances/{self.project_id}:us-central1:raptorflow-db"
            ],
            "cloudSqlDatabases": [
                "raptorflow_prod"
            ],
            "secrets": [
                f"projects/{self.project_id}/secrets/raptorflow-prod-secrets"
            ],
            "traffic": {
                "maxConcurrency": 100
            }
        }

    def get_cloudsql_config(self) -> Dict[str, Any]:
        """Generate Cloud SQL configuration."""
        return {
            "instance": {
                "name": f"{self.project_id}:raptorflow-db",
                "databaseVersion": "POSTGRES_15",
                "region": self.region,
                "zone": self.zone,
                "settings": {
                    "tier": "db-custom-4",
                    "diskSize": "100GB",
                    "diskType": "PD_SSD",
                    "ipType": "PRIVATE"
                },
                "deletionPolicy": {
                    "type": "Automatic",
                    "retentionPeriod": "7d"
                }
            },
            "database": {
                "name": "raptorflow_prod",
                "instance": f"{self.project_id}:raptorflow-db",
                "charset": "UTF8",
                "collation": "en_US",
                "settings": {
                    "max_connections": 100,
                    "shared_buffers": "256MB",
                    "effective_cache_size": "256MB",
                    "maintenance_work_mem": "64MB",
                    "checkpoint_completion_target": "0.7"
                }
            },
            "backup": {
                "enabled": True,
                "startTime": "02:00",
                "location": "us-central1",
                "retentionPeriod": "30d"
            }
        }

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Generate monitoring configuration."""
        return {
            "metrics": {
                "prometheus": {
                    "enabled": True,
                    "namespace": "raptorflow-prod",
                    "service": "raptorflow-backend",
                    "port": 8000,
                    "path": "/metrics"
                },
                "logging": {
                    "enabled": True,
                    "namespace": "raptorflow-prod",
                    "service": "raptorflow-backend",
                    "logName": "raptorflow-backend",
                    "destination": "bigquery",
                    "dataset": "raptorflow_logs",
                    "table": "application_logs"
                },
                "tracing": {
                    "enabled": True,
                    "namespace": "raptorflow-prod",
                    "service": "raptorflow-backend",
                    "sampleRate": 0.1
                },
                "error_reporting": {
                    "enabled": True,
                    "namespace": "raptorflow-prod",
                    "service": "raptorflow-backend",
                    "policy_name": "raptorflow-error-policy"
                }
            },
            "alerts": {
                "prometheus": {
                    "enabled": True,
                    "channels": ["email", "slack"],
                    "rules": [
                        {
                            "name": "high_error_rate",
                            "condition": "error_rate > 0.05",
                            "duration": "5m",
                            "severity": "warning"
                        },
                        {
                            "name": "high_response_time",
                            "condition": "p95_response_time > 2s",
                            "duration": "5m",
                            "severity": "warning"
                        },
                        {
                            "name": "service_down",
                            "condition": "up == 0",
                            "duration": "1m",
                            "severity": "critical"
                        }
                    ]
                },
                "logging": {
                    "enabled": True,
                    "channels": ["email"],
                    "rules": [
                        {
                            "name": "critical_errors",
                            "condition": "level >= ERROR",
                            "duration": "1m",
                            "severity": "critical"
                        },
                        {
                            "name": "database_errors",
                            "condition": "message =~ 'database'",
                            "duration": "5m",
                            "severity": "warning"
                        }
                    ]
                }
            }
        }

    def get_service_account_config(self) -> Dict[str, Any]:
        """Generate service account configuration."""
        return {
            "type": "service_account",
            "project_id": self.project_id,
            "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
            "private_key": os.getenv("GCP_PRIVATE_KEY"),
            "client_email": os.getenv("GCP_CLIENT_EMAIL"),
            "client_id": os.getenv("GCP_CLIENT_ID"),
            "client_x509_cert_url": os.getenv("GCP_CLIENT_X509_CERT_URL"),
            "auth_uri": os.getenv("GCP_AUTH_URI"),
            "token_uri": os.getenv("GCP_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("GCP_AUTH_PROVIDER_X509_CERT_URL"),
            "client_secret": os.getenv("GCP_CLIENT_SECRET"),
            "redirect_uris": os.getenv("GCP_REDIRECT_URIS"),
            "javascript_origins": os.getenv("GCP_JAVASCRIPT_ORIGINS"),
            "scopes": [
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/devstorage.read_write"
            ]
        }

    def get_terraform_config(self) -> Dict[str, Any]:
        """Generate Terraform configuration."""
        return {
            "terraform": {
                "required_version": ">= 1.0",
                "backend": "gcs"
            },
            "provider": {
                "google": {
                    "project": self.project_id,
                    "region": self.region,
                    "zone": self.zone,
                    "credentials": self.service_account_key
                }
            },
            "resource": {
                "google_cloud_run_service": {
                    "project": self.project_id,
                    "location": self.region,
                    "name": self.cloud_run_service,
                    "image": f"gcr.io/{self.artifact_registry}/{self.cloud_run_service}:latest",
                    "template": "cloud_run"
                },
                "google_cloud_sql_database": {
                    "project": self.project_id,
                    "name": f"{self.project_id}:raptorflow-db",
                    "database_version": "POSTGRES_15",
                    "region": self.region,
                    "zone": self.zone,
                    "settings": {
                        "tier": "db-custom-4",
                        "disk_size": "100GB",
                        "disk_type": "PD_SSD",
                        "ip_type": "PRIVATE"
                    }
                },
                "google_cloud_sql_database_instance": {
                    "project": self.project_id,
                    "name": f"{self.project_id}:raptorflow-db",
                    "database_version": "POSTGRES_15",
                    "region": self.region,
                    "zone": self.zone,
                    "settings": {
                        "tier": "db-custom-4",
                        "disk_size": "100GB",
                        "disk_type": "gke-raptorflow-db",
                        "ip_type": "PRIVATE"
                    }
                },
                "google_cloud_sql_database": {
                    "project": self.project_id,
                    "name": "raptorflow_prod",
                    "instance": f"{self.project_id}:raptorflow-db",
                    "charset": "UTF8",
                    "collation": "en_US"
                },
                "google_secret_manager_secret": {
                    "project": self.project_id,
                    "secret_id": f"{self.project_id}-secrets",
                    "replication": {
                        "automatic": True,
                        "replication_policy": "automatic"
                    },
                    "version": "1"
                },
                "google_secret_manager_secret_version": {
                    "project": self.project_id,
                    "secret": f"{self.project_id}-secrets",
                    "version": "1"
                },
                "google_secret_manager_secret_data": {
                    "project": self.project_id,
                    "secret": f"{self.project_id}-secrets",
                    "data": {
                        "SECRET_KEY": os.getenv("SECRET_KEY"),
                        "DATABASE_URL": os.getenv("database_url"),
                        "UPSTABASE_REDIS_TOKEN": os.getenv("UPSTABASE_REDIS_TOKEN"),
                        "VERTEX_AI_PROJECT_ID": os.getenv("VERTEX_AI_PROJECT_ID"),
                        "WEBHOOK_SECRET": os.getenv("WEBHOOK_SECRET")
                    }
                }
            }
        }

    def get_main_terraform(self) -> str:
        """Generate main Terraform configuration."""
        return f"""# RaptorFlow Backend GCP Infrastructure
# Generated by RaptorFlow deployment system

terraform {{
  required_version = ">= 1.0"

  backend "gcs" {{
    project = "{self.project_id}"
    region  = "{self.region}"
  }}

  provider "google" {{
    project = "{self.project_id}"
    region  = "{self.region}"
    zone    = "{self.zone}"
    credentials = file("{self.service_account_key}")
  }}

  # Artifact Registry
  resource "google_artifact_registry" "raptorflow_registry" {{
    project     = "{self.project_id}"
    location   = "{self.region}"
    repository = "{self.artifact_registry}"
    description = "RaptorFlow Backend Container Registry"
    format      = "DOCKER"
    }}

  # Cloud Run Service
  resource "google_cloud_run_service" "raptorflow_backend" {{
    project     = "{self.project_id}"
    location   = "{self.region}"
    name        = "{self.cloud_run_service}"
    description = "RaptorFlow Backend API Service"

    template {{
      spec {{
        container {{
          image = "gcr.io/{self.artifact_registry}/{self.cloud_run_service}:latest"
          ports = [{{
            containerPort = 8000
          }}]
          env = [
            {{
              name  = "ENVIRONMENT"
              value = "production"
            }},
            {{
              name  = "SECRET_KEY"
              value = "${{os.getenv('SECRET_KEY')}}"
            }},
            {{
              name  = "DATABASE_URL"
              value = "${{os.getenv('DATABASE_URL')}}"
            }},
            {{
              name  = "UPSTABASE_REDIS_URL"
              value = "${{os.getenv('UPSTABASE_REDIS_URL')}}"
            }},
            {{
              name  = "UPSTABASE_REDIS_TOKEN"
              value = "{{{os.getenv('UPSTABASE_REDIS_TOKEN')}}"
            }},
            {{
              name  = "VERTEX_AI_PROJECT_ID"
              value = "${{os.getenv('VERTEX_AI_PROJECT_ID')}}"
            }},
            {{
              name  = "GCP_PROJECT_ID"
              value = "{self.project_id}"
            }},
            {{
              name  = "WEBHOOK_SECRET"
              value = "${{os.getenv('WEBHOOK_SECRET')}}"
            }},
            {{
              name  = "ALLOWED_ORIGINS"
              value = "${{os.getenv('ALLOWED_ORIGINS', '*')}}"
            }}]
          resources {{
            requests_memory = "256Mi"
            requests_cpu    = "250m"
            limits_memory    = "512Mi"
            limits_cpu      = "500m"
          }}
        }}

        traffic {{
          max_concurrency = 100
        }}

        timeout = "300s"

        revision = "latest"

        depends_on = [
          "google_cloudsql_database_instance.raptorflow_db",
          "google_secret_manager_secret.raptorflow-prod-secrets"
        ]
      }}
    }}

  # Cloud SQL Instance
  resource "google_sql_database_instance" "raptorflow_db" {{
    project     = "{self.project_id}"
    name        = "raptorflow-db"
    database_version = "POSTGRES_15"
    region      = "{self.region}"
    zone        = "{self.zone}"
    settings {{
      tier          = "db-custom-4"
      disk_size      = "100GB"
      disk_type      = "PD_SSD"
      ip_type        = "PRIVATE"
      deletion_policy = {{
        type = "Automatic"
        retention_period = "7d"
      }}
    }}

  # Cloud SQL Database
  resource "google_sql_database" "raptorflow_prod" {{
    project     = "{self.project_id}"
    name        = "raptorflow_prod"
    instance    = "raptorflow-db"
    charset     = "UTF8"
    collation   = "en_US"
    }}

  # Secrets
  resource "google_secret_manager_secret" "raptorflow-prod-secrets" {{
    project     = "{self.project_id}"
    secret_id   = "raptorflow-prod-secrets"
    replication {{
      automatic = true
      replication_policy = "automatic"
    }}
  }}

  resource "google_secret_manager_secret_version" "raptorflow-prod-secrets" {{
    project     = "{self.project_id}"
    secret_id   = "raptorflow-prod-secrets"
    version    = "1"
  }}

  resource "google_secret_manager_secret_data" "raptorflow-prod-secrets" {{
    project     = "{self.project_id}"
    secret_id   = "raptorflow-prod-secrets"
    secret_data = {{
        SECRET_KEY     = "${{os.getenv('SECRET_KEY')}}"
        DATABASE_URL   = "${{os.getenv('DATABASE_URL')}}"
        UPSTABASE_REDIS_TOKEN = "${{os.getenv('UPSTABASE_REDIS_TOKEN')}}"
        VERTEX_AI_PROJECT_ID = "${{os.getenv('VERTEX_AI_PROJECT_ID')}}"
        WEBHOOK_SECRET = "${{os.getenv('WEBHOOK_SECRET')}}"
    }}

  # IAM Service Account
  resource "google_service_account" "raptorflow-sa" {{
    account_id   = "{os.getenv('GCP_CLIENT_ID')}"
    display_name = "RaptorFlow Service Account"
    description = "Service account for RaptorFlow backend"
  }}

  # IAM Roles
  resource "google_project_iam_policy" "raptorflow-cloud-run-deployer" {{
    policy_id    = "roles/cloudrun.deployer"
    role        = "roles/cloudrun.deployer"
    members      = [
        "serviceAccount:{os.getenv('GCP_CLIENT_ID')}"
    ]
    binding      = [
        "projects/{self.project_id}/roles/cloudrun.deployer",
        "projects/{self.project_id}/roles/cloudrun.invoker"
      ]
  }}

  resource "google_project_iam_policy" "raptorflow-cloud-run-invoker" {{
    policy_id    = "roles/cloudrun.invoker"
    role        = "roles/cloudrun.invoker"
    members      = [
        "serviceAccount:{os.getenv('GCP_CLIENT_ID')}"
    ]
    binding      = [
        "projects/{self.project_id}/roles/cloudrun.invoker",
        "projects/{self.project_id}/roles/cloudrun.viewer"
    ]
  }}

  resource "google_project_iam_policy" "raptorflow-cloudrun-viewer" {{
    policy_id    = "roles/cloudrun.viewer"
    role        = "roles/cloudrun.viewer"
    members      = [
        "serviceAccount:{os.getenv('GCP_CLIENT_ID')}"
    ]
    binding      = [
        "projects/{self.project_id}/roles/cloudrun.viewer"
    ]
  }}

  # Monitoring
  resource "google_monitoring_dashboard" "raptorflow-dashboard" {{
    project     = "{self.project_id}"
    dashboard_id = "raptorflow-backend"
    display_name = "RaptorFlow Backend Dashboard"
    charts = [
        "google_monitoring_chart.raptorflow-backend"
    ]
  }}

  # Logging
  resource "google_logging_project_sink "raptorflow-logs" {{
    project     = "{self.project_id}"
    name        = "raptorflow-backend"
        description = "Logs from RaptorFlow backend service"
        destination = "bigquery"
        filter     = "resource.type = \"cloud_run_revision\" AND resource.labels.service_name = \"{self.cloud_run_service}\""
        log_name    = "raptorflow-backend"
        version     = "1"
    }}

  # Error Reporting
  resource "google_error_reporting_policy" "raptorflow-error-policy" {{
    project     = "{self.project_id}"
    policy_id    = "raptorflow-error-policy"
    condition    = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"{self.cloud_run_service}\""
    enabled     = true
    notification_channels = ["email", "slack"]
    alerting_strategy = "new"
    error_reporting_service = "raptorflow-error-service"
  }}

  resource "google_error_reporting_service" "raptorflow-error-service" {{
    project     = "{self.project_id}"
    service_name = "raptorflow-error-service"
    config_path  = "error_reporting_policy.json"
    api_key     = os.getenv("ERROR_REPORTING_API_KEY")
  }}

  # Custom Metrics
  resource "google_monitoring_metric_descriptor" "raptorflow_request_count" {{
    project     = "{self.project_id}"
    type        = "external"
    metric      = "raptorflow_request_count"
    display_name = "RaptorFlow Request Count"
    description = "Total number of requests to RaptorFlow backend"
    metric_labels = {{
        service_name = "{self.cloud_run_service}"
        environment = "production"
    }}

  resource "google_monitoring_metric_descriptor" "raptorflow_response_time" {{
    project     = "{self.project_id}"
    type        = "external"
    metric      = "raptorflow_response_time"
    display_name = "RaptorFlow Response Time"
    description = "Response time for RaptorFlow backend requests"
    metric_labels = {{
        service_name = "{self.cloud_run_service}"
        environment = "production"
    }}
}}
"""

    def get_service_account_key_content(self) -> str:
        """Generate service account key content."""
        return os.getenv("GCP_PRIVATE_KEY", "")

    def get_startup_script(self) -> str:
        """Generate startup script for GCP deployment."""
        return f"""#!/bin/bash
# RaptorFlow Backend GCP Startup Script

set -e

# Configuration
PROJECT_ID="{self.project_id}"
REGION="{self.region}"
SERVICE_NAME="{self.cloud_run_service}"
IMAGE="gcr.io/{self.artifact_registry}/{self.cloud_run_service}:latest"

echo "Starting RaptorFlow backend deployment..."

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudb.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable sqladmin.googleapis.com

# Create service account and set up permissions
echo "Setting up service account..."
gcloud iam service-accounts create raptorflow-sa \\
    --display-name="RaptorFlow Service Account" \\
    --description="Service account for RaptorFlow backend" \\
    --project=$PROJECT_ID \\
    --quiet

# Get service account credentials
echo "Getting service account credentials..."
gcloud iam service-accounts keys list raptorflow-sa --key=JSON > service-account-key.json

# Create IAM policies
echo "Creating IAM policies..."
gcloud iam policies create raptorflow-cloud-run-deployer \\
    --project=$PROJECT_ID \\
    --file=deployment/gcp/iam/cloud-run-deployer.yaml

gcloud iam policies create raptorflow-cloud-run-invoker \\
    --project=$PROJECT_ID \\
    --file=deployment/gcp/iam/cloud-run-invoker.yaml

gcloud iam policies create raptorflow-cloudrun-viewer \\
    --project=$PROJECT_ID \\
    --file=deployment/gcp/iam/cloud-run-viewer.yaml

# Enable Cloud Run Admin API
gcloud services enable run.googleapis.com

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \\
    --image=$IMAGE \\
    --region=$REGION \\
    --platform=managed \\
    --allow-unauthenticated \\
    --port=8000 \\
    --memory=512Mi \\
    --cpu=1 \\
    --min-instances=1 \\
    --max-instances=3 \\
    --set-env-vars \\
        ENVIRONMENT=production \\
        SECRET_KEY="${{os.getenv('SECRET_KEY')}}" \\
        DATABASE_URL="${{os.getenv('DATABASE_URL')}}" \\
        UPSTABASE_REDIS_URL="${{os.getenv('UPSTABASE_REDIS_URL')}}" \\
        UPSTABASE_REDIS_TOKEN="${{os.getenv('UPSTABASE_REDIS_TOKEN')}}" \\
        VERTEX_AI_PROJECT_ID="${{os.getenv('VERTEX_AI_PROJECT_ID')}}" \\
        GCP_PROJECT_ID="$PROJECT_ID" \\
        WEBHOOK_SECRET="${{os.getenv('WEBHOOK_SECRET')}}" \\
        ALLOWED_ORIGINS="${{os.getenv('ALLOWED_ORIGINS', '*')}}" \\
    --set-cloudsql-instances raptorflow-db \\
    --set-secrets raptorflow-prod-secrets \\
    --set-traffic-rules deployment/gcp/traffic-rules.yaml

# Set up traffic routing
echo "Setting up traffic routing..."
gcloud run services update-traffic $SERVICE_NAME \\
    --to-revisions=latest \\
    --to-min-revisions=1

echo "Deployment completed successfully!"
echo "Service URL: https://$SERVICE_NAME-$RANDOM_HASH.a.run.app"
echo "Health check: https://$SERVICE_NAME-$RANDOM_HASH.a.run.app/health"
"""

    def get_traffic_rules_config(self) -> str:
        """Generate traffic routing rules."""
        return """# RaptorFlow Traffic Routing Rules
# Generated by RaptorFlow deployment system

rules:
- name: raptorflow-backend
  match: request.path.startsWith("/api/")
  priority: 100
  action: use
    service: raptorflow-backend
"""

    def get_monitoring_dashboard_config(self) -> str:
        """Generate monitoring dashboard configuration."""
        return f"""# RaptorFlow Monitoring Dashboard
# Generated by RaptorFlow deployment system

apiVersion: v1
kind: Dashboard
metadata:
  name: raptorflow-backend
  labels:
    app: raptorflow
    environment: production
spec:
  display_name: RaptorFlow Backend Dashboard
  charts:
  - name: raptorflow-backend
    type: google_monitoring_chart
    title: Request Rate
    targets:
      - request_count
    - response_time
  annotations:
    display_name: Request Rate
    - display_name: Response Time
  - display_name: Error Rate
  - display_name: Uptime
  - display_name: Memory Usage
    - display_name: CPU Usage
  - display_name: Database Connections
    - display_name: Redis Connections
    - display_name: Agent Executions
    display_name: Cognitive Processing Time
    - display_name: Memory Storage Size
    display_name: Cache Hit Rate
"""

    def get_logging_config(self) -> str:
        """Generate logging configuration."""
        return f"""# RaptorFlow Logging Configuration
# Generated by RaptorFlow deployment system

apiVersion: v2
kind: LogSink
metadata:
  name: raptorflow-backend
  labels:
    app: raptorflow
    environment: production
spec:
  name: raptorflow-backend
  description: Logs from RaptorFlow backend service
  destination: bigquery:raptorflow-prod.logs.application_logs
  filter: resource.type = "cloud_run_revision" AND resource.labels.service_name = "raptorflow-backend"
  logName: raptorflow-backend
  version: 1
  resource: projects/{self.project_id}/logs/raptorflow-backend
"""

    def get_error_reporting_config(self) -> str:
        """Generate error reporting configuration."""
        return f"""# RaptorFlow Error Reporting Configuration
# Generated by RaptorFlow deployment system

apiVersion: v1
kind: ErrorReportingPolicy
metadata:
  name: raptorflow-error-policy
  description: Error reporting policy for RaptorFlow backend
spec:
  condition: resource.type="cloud_run_revision" AND resource.labels.service_name="raptorflow"
  enabled: true
  notification_channels:
    - email
    - slack
  alerting_strategy: new
  error_reporting_service: raptorflow-error-service
  logging:
    severity: ERROR
  notification_channels:
      - email
      - slack
      pubsub_topic: projects/{self.project_id}/logs/errors
"""

    def get_error_reporting_service_config(self) -> str:
        """Generate error reporting service configuration."""
        return f"""# RaptorFlow Error Reporting Service Configuration
# Generated by Raptorflow deployment system

apiVersion: v1
kind: ErrorReportingService
metadata:
  name: raptorflow-error-service
  description: Error reporting service for RaptorFlow backend
spec:
  config_path: error_reporting_policy.json
  api_key: {os.getenv("ERROR_REPORTING_API_KEY")}
"""

    def get_deployment_script(self) -> str:
        """Generate deployment script for production."""
        return f"""#!/bin/bash
# RaptorFlow Production Deployment Script

set -e

# Configuration
PROJECT_ID="{self.project_id}"
REGION="{self.region}"
SERVICE_NAME="{self.cloud_run_service}"
IMAGE="gcr.io/{self.artifact_registry}/{self.cloud_run_service}:latest"

echo "🚀 Starting RaptorFlow production deployment..."

# Pre-deployment checks
echo "Running pre-deployment checks..."

# Check if service exists
if gcloud run services describe $SERVICE_NAME --format="json" | jq -r '.status.status == "RUNNING"' > /dev/null; then
    echo "⚠️  Service already running, scaling down..."
    gcloud run services update $SERVICE_NAME --max-instances=1
fi

# Backup current version
CURRENT_VERSION=$(gcloud run services describe $SERVICE_NAME --format="json" | jq -r '.spec.template.spec[0].containers[0].image.split(":")[1]')
echo "Current version: $CURRENT_VERSION"

# Deploy new version
echo "📦 Deploying new version..."
gcloud run deploy $SERVICE_NAME \\
    --image=$IMAGE \\
    --region=$REGION \\
    --platform=managed \\
    --allow-unauthenticated \\
    --port=8000 \\
    --memory=512Mi \\
    --cpu=1 \\
    --min-instances=1 \\
    --max-instances=3 \\
    --set-env-vars \\
        ENVIRONMENT=production \\
        SECRET_KEY="${{os.getenv('SECRET_KEY')}}" \\
        DATABASE_URL="${{os.getenv('DATABASE_URL')}}" \\
        UPSTABASE_REDIS_URL="${{os.getenv('UPSTABASE_REDIS_URL')}}" \\
        UPSTABASE_REDIS_TOKEN="${{os.getenv('UPSTABASE_REDIS_TOKEN')}}" \\
        VERTEX_AI_PROJECT_ID="${os.getenv('VERTEX_AI_PROJECT_ID')}}" \\
        GCP_PROJECT_ID="$PROJECT_ID" \\
        WEBHOOK_SECRET="${{os.getenv('WEBHOOK_SECRET')}}" \\
        ALLOWED_ORIGINS="${{os.getenv('ALLOWED_ORIGINS', '*')}}" \\
    --set-cloudsql-instances raptorflow-db \\
    --set-secrets raptorflow-prod-secrets \\
    --timeout=300s

# Wait for deployment to complete
echo "Waiting for deployment to complete..."
sleep 30

# Verify deployment
if gcloud run services describe $SERVICE_NAME --format="json" | jq -r '.status.status == "RUNNING"' > /dev/null; then
    echo "✅ Deployment successful!"
    echo "Service URL: https://$SERVICE_NAME-$RANDOM_HASH.a.run.app"
    echo "Health check: https://$SERVICE_NAME-$RANDOM_HASH.a.run.app/health"
else
    echo "❌ Deployment failed!"
    echo "Checking logs..."
    gcloud logs read --limit=50 $SERVICE_NAME
    exit 1
fi

# Scale up if needed
echo "Scaling to optimal configuration..."
gcloud run services update $SERVICE_NAME \\
    --max-instances=3

echo "🎯 Production deployment completed!"
echo "Service URL: https://$SERVICE_NAME-$RANDOM_HASH.a.run.app"
echo "Health check: https://SERVICE_NAME-$RANDOM_HASH.a.run.app/health"
echo "Metrics: https://$SERVICE_NAME-$RANDOM_HASH.a.run.app/metrics"
"""
