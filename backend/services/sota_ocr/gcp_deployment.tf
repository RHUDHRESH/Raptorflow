# GCP Deployment Configuration for SOTA OCR System
# Terraform configuration for infrastructure as code

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_zone
}

# Variables
variable "gcp_project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "raptorflow-ocr-prod"
}

variable "gcp_region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "gcp_zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "production"
}

# VPC Network
resource "google_compute_network" "ocr_network" {
  name                    = "ocr-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "ocr_subnet" {
  name          = "ocr-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.gcp_region
  network       = google_compute_network.ocr_network.id
}

# Firewall Rules
resource "google_compute_firewall" "ocr_firewall" {
  name    = "ocr-firewall"
  network = google_compute_network.ocr_network.id

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "443", "8000"]
  }

  source_ranges = ["0.0.0.0/0"]
}

# Service Account
resource "google_service_account" "ocr_service_account" {
  account_id   = "ocr-service-account"
  display_name = "OCR Service Account"
}

resource "google_project_iam_member" "ocr_service_account_roles" {
  for_each = toset([
    "roles/compute.admin",
    "roles/storage.admin",
    "roles/logging.admin",
    "roles/monitoring.admin",
    "roles/iam.serviceAccountUser"
  ])
  
  project = var.gcp_project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.ocr_service_account.email}"
}

# Storage Bucket
resource "google_storage_bucket" "ocr_storage" {
  name          = "raptorflow-ocr-storage"
  location      = var.gcp_region
  storage_class = "STANDARD"
  
  uniform_bucket_level_access = true
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Compute Instance Template
resource "google_compute_instance_template" "ocr_instance_template" {
  name_prefix  = "ocr-instance-"
  machine_type = "n1-standard-8"
  
  tags = ["ocr-server"]
  
  disk {
    source_image = "ubuntu-os-cloud/ubuntu-2004-lts"
    auto_delete  = true
    boot         = true
    disk_size_gb = 100
    disk_type    = "pd-ssd"
  }
  
  network_interface {
    network    = google_compute_network.ocr_network.id
    subnetwork = google_compute_subnetwork.ocr_subnet.id
    access_config {}
  }
  
  guest_accelerator {
    type  = "nvidia-tesla-a100"
    count = 1
  }
  
  metadata = {
    startup-script = file("startup-script.sh")
    gpu-driver      = "nvidia-tesla-a100"
  }
  
  service_account {
    email  = google_service_account.ocr_service_account.email
    scopes = ["cloud-platform"]
  }
  
  scheduling {
    preemptible = false
    automatic_restart = true
    on_host_maintenance = "TERMINATE"
  }
}

# Managed Instance Group
resource "google_compute_instance_group_manager" "ocr_instance_group" {
  name               = "ocr-instance-group"
  base_instance_name = "ocr-instance"
  zone               = var.gcp_zone
  target_size        = 1
  
  version {
    instance_template = google_compute_instance_template.ocr_instance_template.id
  }
  
  named_port {
    name = "http"
    port = 8000
  }
}

# Autoscaler
resource "google_compute_autoscaler" "ocr_autoscaler" {
  name   = "ocr-autoscaler"
  zone   = var.gcp_zone
  target = google_compute_instance_group_manager.ocr_instance_group.id
  
  autoscaling_policy {
    min_replicas    = 1
    max_replicas    = 5
    cooldown_period = 60
    
    cpu_utilization {
      target = 0.7
    }
  }
}

# HTTP Load Balancer
resource "google_compute_global_forwarding_rule" "ocr_forwarding_rule" {
  name       = "ocr-forwarding-rule"
  target     = google_compute_target_http_proxy.ocr_http_proxy.id
  port_range = "443"
}

resource "google_compute_target_http_proxy" "ocr_http_proxy" {
  name    = "ocr-http-proxy"
  url_map = google_compute_url_map.ocr_url_map.id
}

resource "google_compute_url_map" "ocr_url_map" {
  name            = "ocr-url-map"
  default_service = google_compute_backend_service.ocr_backend_service.id
}

resource "google_compute_backend_service" "ocr_backend_service" {
  name          = "ocr-backend-service"
  port_name     = "http"
  protocol      = "HTTP"
  timeout_sec   = 30
  
  health_checks = [google_compute_http_health_check.ocr_health_check.id]
  
  backend {
    group = google_compute_instance_group_manager.ocr_instance_group.id
  }
}

resource "google_compute_http_health_check" "ocr_health_check" {
  name               = "ocr-health-check"
  request_path       = "/health"
  check_interval_sec = 30
  timeout_sec        = 10
  healthy_threshold  = 2
  unhealthy_threshold = 3
}

# SSL Certificate
resource "google_compute_managed_ssl_certificate" "ocr_ssl_certificate" {
  name        = "ocr-ssl-certificate"
  description = "SSL certificate for OCR service"
  
  managed {
    domains = ["ocr.raptorflow.ai"]
  }
}

# Cloud SQL Database
resource "google_sql_database_instance" "ocr_database" {
  name             = "ocr-monitoring-db"
  database_version = "POSTGRES_14"
  region           = var.gcp_region
  
  settings {
    tier = "db-n1-standard-2"
    
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "ocr-network"
        value = google_compute_subnetwork.ocr_subnet.ip_cidr_range
      }
    }
    
    backup_configuration {
      enabled = true
    }
  }
  
  deletion_protection = false
}

# Redis Instance
resource "google_redis_instance" "ocr_cache" {
  name           = "ocr-cache"
  tier           = "STANDARD_HA"
  memory_size_gb = 4
  
  location_id = "${var.gcp_region}-a"
  
  authorized_network = google_compute_subnetwork.ocr_subnet.name
  
  redis_version = "REDIS_6_X"
  
  display_name = "OCR Cache Instance"
}

# Monitoring Workspace
resource "google_monitoring_workspace" "ocr_monitoring" {
  display_name = "OCR Monitoring Workspace"
}

# Alert Policies
resource "google_monitoring_alert_policy" "ocr_high_cpu" {
  display_name = "OCR High CPU Usage"
  combiner     = "OR"
  
  conditions {
    display_name = "CPU usage > 80%"
    
    condition_threshold {
      filter          = "metric.type=\"compute.googleapis.com/instance/cpu/utilization\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8
    }
  }
  
  notification_channels = []
}

# Cloud Logging
resource "google_logging_metric" "ocr_processing_time" {
  name   = "ocr_processing_time"
  filter = "resource.type=\"gce_instance\" AND logName=\"projects/${var.gcp_project_id}/logs/ocr-service\""
  
  metric_descriptor {
    metric_name = "ocr_processing_time"
    display_name = "OCR Processing Time"
    type = "DOUBLE"
    unit = "s"
  }
}

# Artifact Registry
resource "google_artifact_registry_repository" "ocr_container_registry" {
  location      = var.gcp_region
  repository_id = "ocr-container"
  description   = "OCR container registry"
  format        = "DOCKER"
}

# Cloud Scheduler for backups
resource "google_cloud_scheduler_job" "ocr_backup_job" {
  name             = "ocr-backup-job"
  description      = "Daily backup job for OCR data"
  schedule         = "0 2 * * *"  # Daily at 2 AM
  time_zone        = "America/New_York"
  
  http_target {
    http_method = "POST"
    uri         = "https://ocr.raptorflow.ai/api/v1/backup"
    body        = base64encode("{\"action\":\"backup\"}")
  }
}

# Budget Alert
resource "google_billing_budget" "ocr_budget" {
  billing_account = "123456-789012-345678"
  display_name   = "OCR Monthly Budget"
  
  budget_filter {
    projects = ["projects/${var.gcp_project_id}"]
  }
  
  amount {
    specified_amount {
      currency_code = "USD"
      units         = "5000"
    }
  }
  
  threshold_rules {
    threshold_percent = 50.0
    spend_basis       = "CURRENT_SPEND"
  }
  
  threshold_rules {
    threshold_percent = 90.0
    spend_basis       = "CURRENT_SPEND"
  }
}

# Outputs
output "instance_group_url" {
  value = google_compute_instance_group_manager.ocr_instance_group.instance_group
}

output "load_balancer_ip" {
  value = google_compute_global_forwarding_rule.ocr_forwarding_rule.ip_address
}

output "storage_bucket_name" {
  value = google_storage_bucket.ocr_storage.name
}

output "database_connection_name" {
  value = google_sql_database_instance.ocr_database.connection_name
}

output "redis_host" {
  value = google_redis_instance.ocr_cache.host
}
