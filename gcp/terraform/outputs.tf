# Terraform outputs for Raptorflow GCP infrastructure

output "project_id" {
  description = "GCP project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP region"
  value       = var.region
}

output "environment" {
  description = "Deployment environment"
  value       = var.environment
}

# Cloud Run outputs
output "cloud_run_service_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_service.raptorflow.status[0].url
}

output "cloud_run_service_name" {
  description = "Cloud Run service name"
  value       = google_cloud_run_service.raptorflow.name
}

output "cloud_run_service_id" {
  description = "Cloud Run service ID"
  value       = google_cloud_run_service.raptorflow.id
}

# Redis (Memorystore) outputs
output "redis_host" {
  description = "Redis instance host"
  value       = google_redis_instance.raptorflow_redis.host
}

output "redis_port" {
  description = "Redis instance port"
  value       = google_redis_instance.raptorflow_redis.port
}

output "redis_auth_string" {
  description = "Redis auth string"
  value       = google_redis_instance.raptorflow_redis.auth_string
  sensitive   = true
}

output "redis_instance_id" {
  description = "Redis instance ID"
  value       = google_redis_instance.raptorflow_redis.id
}

# Cloud Storage outputs
output "evidence_bucket_name" {
  description = "Evidence storage bucket name"
  value       = google_storage_bucket.evidence_bucket.name
}

output "evidence_bucket_url" {
  description = "Evidence storage bucket URL"
  value       = google_storage_bucket.evidence_bucket.url
}

output "exports_bucket_name" {
  description = "Exports storage bucket name"
  value       = google_storage_bucket.exports_bucket.name
}

output "exports_bucket_url" {
  description = "Exports storage bucket URL"
  value       = google_storage_bucket.exports_bucket.url
}

output "assets_bucket_name" {
  description = "Assets storage bucket name"
  value       = google_storage_bucket.assets_bucket.name
}

output "assets_bucket_url" {
  description = "Assets storage bucket URL"
  value       = google_storage_bucket.assets_bucket.url
}

# BigQuery outputs
output "bigquery_dataset_id" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.raptorflow_analytics.dataset_id
}

output "bigquery_dataset_location" {
  description = "BigQuery dataset location"
  value       = google_bigquery_dataset.raptorflow_analytics.location
}

output "bigquery_project" {
  description = "BigQuery project"
  value       = google_bigquery_dataset.raptorflow_analytics.project
}

# Cloud SQL outputs (if enabled)
output "cloud_sql_instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.raptorflow_db.name
}

output "cloud_sql_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.raptorflow_db.connection_name
}

output "cloud_sql_database_name" {
  description = "Cloud SQL database name"
  value       = google_sql_database.raptorflow_database.name
}

# VPC Connector outputs
output "vpc_connector_name" {
  description = "VPC connector name"
  value       = google_vpc_access_connector.connector.name
}

output "vpc_connector_id" {
  description = "VPC connector ID"
  value       = google_vpc_access_connector.connector.id
}

# Service Account outputs
output "service_account_email" {
  description = "Cloud Run service account email"
  value       = google_service_account.raptorflow_sa.email
}

output "service_account_name" {
  description = "Cloud Run service account name"
  value       = google_service_account.raptorflow_sa.name
}

# IAM outputs
output "service_account_iam_roles" {
  description = "IAM roles assigned to service account"
  value = [
    "roles/cloudrun.admin",
    "roles/redis.user",
    "roles/storage.admin",
    "roles/bigquery.admin",
    "roles/secretmanager.secretAccessor",
  ]
}

# Cloud Tasks outputs
output "cloud_tasks_queue_name" {
  description = "Cloud Tasks queue name"
  value       = google_cloud_tasks_queue.raptorflow_tasks.name
}

output "cloud_tasks_queue_id" {
  description = "Cloud Tasks queue ID"
  value       = google_cloud_tasks_queue.raptorflow_tasks.id
}

# Pub/Sub outputs
output "pubsub_topic_name" {
  description = "Pub/Sub topic name"
  value       = google_pubsub_topic.raptorflow_events.name
}

output "pubsub_subscription_name" {
  description = "Pub/Sub subscription name"
  value       = google_pubsub_subscription.raptorflow_events_sub.name
}

# Secret Manager outputs
output "secret_manager_secrets" {
  description = "Secret Manager secret names"
  value = {
    database_url = google_secret_manager_secret.database_url.secret_id
    jwt_secret   = google_secret_manager_secret.jwt_secret.secret_id
    webhook_secret = google_secret_manager_secret.webhook_secret.secret_id
  }
}

# Monitoring outputs
output "monitoring_workspace_id" {
  description = "Monitoring workspace ID"
  value       = google_monitoring_workspace.raptorflow_monitoring.id
}

output "logging_sink_name" {
  description = "Logging sink name"
  value       = google_logging_sink.raptorflow_logs.name
}

# Networking outputs
output "serverless_vpc_connector_network" {
  description = "Serverless VPC connector network"
  value       = google_compute_network.vpc_network.name
}

output "serverless_vpc_connector_subnet" {
  description = "Serverless VPC connector subnet"
  value       = google_compute_subnetwork.vpc_subnet.name
}

# Security outputs
output "firewall_rules" {
  description = "Firewall rules"
  value = {
    allow_redis = google_compute_firewall.allow_redis.name
    allow_sql   = google_compute_firewall.allow_sql.name
  }
}

# Cost Management outputs
output "budget_name" {
  description = "Budget name"
  value       = google_billing_budget.raptorflow_budget.name
}

output "budget_amount" {
  description = "Budget amount"
  value       = google_billing_budget.raptorflow_budget.budget_amount[0].specified_amount[0].units
}

# Environment-specific outputs
locals {
  environment_outputs = {
    development = {
      cloud_run_url = "https://raptorflow-dev-${random_id.suffix.value}.run.app"
      redis_host    = google_redis_instance.raptorflow_redis.host
      environment   = "development"
    }
    staging = {
      cloud_run_url = "https://raptorflow-staging-${random_id.suffix.value}.run.app"
      redis_host    = google_redis_instance.raptorflow_redis.host
      environment   = "staging"
    }
    production = {
      cloud_run_url = "https://raptorflow-prod-${random_id.suffix.value}.run.app"
      redis_host    = google_redis_instance.raptorflow_redis.host
      environment   = "production"
    }
  }
}

output "environment_config" {
  description = "Environment-specific configuration"
  value       = local.environment_outputs[var.environment]
}

# Application Configuration outputs
output "app_environment_variables" {
  description = "Application environment variables"
  value = {
    ENVIRONMENT                = var.environment
    PROJECT_ID                = var.project_id
    REGION                    = var.region
    REDIS_HOST               = google_redis_instance.raptorflow_redis.host
    REDIS_PORT               = tostring(google_redis_instance.raptorflow_redis.port)
    EVIDENCE_BUCKET          = google_storage_bucket.evidence_bucket.name
    EXPORTS_BUCKET           = google_storage_bucket.exports_bucket.name
    ASSETS_BUCKET            = google_storage_bucket.assets_bucket.name
    BIGQUERY_DATASET         = google_bigquery_dataset.raptorflow_analytics.dataset_id
    CLOUD_TASKS_QUEUE       = google_cloud_tasks_queue.raptorflow_tasks.name
    PUBSUB_TOPIC             = google_pubsub_topic.raptorflow_events.name
  }
  sensitive = true
}

# CI/CD outputs
output "cicd_config" {
  description = "CI/CD configuration"
  value = {
    service_account_email = google_service_account.raptorflow_sa.email
    project_id            = var.project_id
    region                = var.region
    cloud_run_service     = google_cloud_run_service.raptorflow.name
  }
}

# Backup and Disaster Recovery outputs
output "backup_config" {
  description = "Backup configuration"
  value = {
    backup_bucket = google_storage_bucket.backup_bucket.name
    backup_schedule = "0 2 * * *"  # Daily at 2 AM
    retention_days = 30
  }
}

# Compliance and Security outputs
output "security_config" {
  description = "Security configuration"
  value = {
    vpc_connector_cidr_range = google_vpc_access_connector.connector.ip_cidr_range
    enable_private_google_access = true
    force_destroy_on_delete = var.environment != "production"
  }
}

# Performance and Scaling outputs
output "performance_config" {
  description = "Performance configuration"
  value = {
    cloud_run_min_instances = google_cloud_run_service.raptorflow.template[0].spec[0].container_concurrency
    cloud_run_max_instances = google_cloud_run_service.raptorflow.template[0].spec[0].scaling[0].max_instance_count
    redis_memory_size       = google_redis_instance.raptorflow_redis.memory_size_gb
    redis_tier              = google_redis_instance.raptorflow_redis.tier
  }
}
