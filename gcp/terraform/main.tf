terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.40.0"
    }
    supabase = {
      source  = "supabase/supabase"
      version = ">= 1.0.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# GCP Project Configuration
resource "google_project" "raptorflow" {
  name            = var.project_id
  project_id      = var.project_id
  org_id          = var.org_id
  billing_account = var.billing_account_id
}

# Enable Required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "compute.googleapis.com",
    "storage.googleapis.com",
    "sql-component.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "redis.googleapis.com",
    "aiplatform.googleapis.com",
    "iam.googleapis.com",
    "resourcemanager.googleapis.com"
  ])

  project = var.project_id
  service = each.key
}

# GCS Buckets for Storage
resource "google_storage_bucket" "user_avatars" {
  name          = "${var.project_id}-user-avatars"
  project_id    = var.project_id
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  cors {
    origin          = ["*"]
    method          = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

resource "google_storage_bucket" "user_documents" {
  name          = "${var.project_id}-user-documents"
  project_id    = var.project_id
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  cors {
    origin          = ["*"]
    method          = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

resource "google_storage_bucket" "workspace_files" {
  name          = "${var.project_id}-workspace-files"
  project_id    = var.project_id
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  cors {
    origin          = ["*"]
    method          = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

# Cloud Run for Backend Services
resource "google_cloud_run_service" "backend" {
  name     = "raptorflow-backend"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/raptorflow-backend:latest"

        env_vars {
          name  = "UPSTASH_REDIS_URL"
          value = var.upstash_redis_url
        }
        env_vars {
          name  = "UPSTASH_REDIS_TOKEN"
          value = var.upstash_redis_token
        }
        env_vars {
          name  = "SUPABASE_URL"
          value = var.supabase_url
        }
        env_vars {
          name  = "SUPABASE_SERVICE_ROLE_KEY"
          value = var.supabase_service_role_key
        }
        env_vars {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
        env_vars {
          name  = "VERTEX_AI_ENDPOINT"
          value = "https://${var.region}-aiplatform.googleapis.com"
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "2Gi"
          }
        }
      }

      container_concurrency = 100
      timeout_seconds       = 300
    }
  }

  traffic {
    percent = 100
  }

  autogenerate_revision_name = true
}

# Upstash Redis Configuration (External Service)
# Note: Upstash Redis is managed externally, not via Terraform
# Update these variables with your Upstash configuration

variable "upstash_redis_url" {
  description = "Upstash Redis URL"
  type        = string
  sensitive   = true
  default     = ""
}

variable "upstash_redis_token" {
  description = "Upstash Redis REST token"
  type        = string
  sensitive   = true
  default     = ""
}

# Vertex AI Endpoints for Inference
resource "google_ai_platform_notebook_runtime_template" "inference" {
  name        = "raptorflow-inference"
  location    = var.region
  project_id  = var.project_id

  machine_type = "e2-standard-4"
  container_image {
    image_uri = "us-docker.pkg.dev/vertexai/vertex-notebook:latest"
  }

  install_gpu_drivers = true
  boot_disk {
    auto_delete = true
    machine_type = "PD_STANDARD"
    source_image = "projects/deeplearning-platform-release/global/images/deeplearning-platform-release-notebook-image-v20231106"
  }
}

# Artifact Registry for Container Storage
resource "google_artifact_registry_repository" "backend" {
  location      = var.region
  repository_id = "raptorflow-backend"
  description    = "Container repository for RaptorFlow backend services"
  format        = "DOCKER"
}

# Cloud Build for CI/CD
resource "google_cloudbuild_trigger" "backend" {
  name        = "raptorflow-backend-trigger"
  description = "Trigger for backend builds"
  project_id  = var.project_id

  github {
    owner = var.github_owner
    name  = var.github_repo
    push {
      branch = "^main$"
    }
  }

  build_config {
    step {
      name = "Build and Push"
      args = ["build", "-t", "gcr.io/${var.project_id}/raptorflow-backend:$COMMIT_SHA", "."]
    }
    step {
      name = "Push to Artifact Registry"
      args = ["push", "gcr.io/${var.project_id}/raptorflow-backend:$COMMIT_SHA"]
    }
    step {
      name = "Deploy to Cloud Run"
      args = ["run", "deploy", "--image", "gcr.io/${var.project_id}/raptorflow-backend:$COMMIT_SHA", "--region", var.region, "raptorflow-backend"]
    }
  }
}

# Service Accounts and IAM
resource "google_service_account" "raptorflow_backend" {
  account_id   = "raptorflow-backend"
  display_name = "RaptorFlow Backend Service Account"
}

resource "google_project_iam_member" "backend_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.raptorflow_backend.email}"
}

resource "google_project_iam_member" "backend_vertex_ai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.raptorflow_backend.email}"
}

resource "google_project_iam_member" "backend_cloud_run" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.raptorflow_backend.email}"
}

# Supabase Integration
resource "supabase_project" "raptorflow" {
  name        = "RaptorFlow"
  database_password = var.supabase_db_password
  region      = var.supabase_region
  plan_id    = "free" # Change to "pro" for production
}

# Outputs
output "project_id" {
  value = google_project.raptorflow.project_id
}

output "backend_url" {
  value = google_cloud_run_service.backend.status[0].url
}

output "redis_config" {
  value = {
    url   = var.upstash_redis_url
    token = var.upstash_redis_token
  }
  sensitive = true
}

output "storage_buckets" {
  value = {
    avatars    = google_storage_bucket.user_avatars.name
    documents  = google_storage_bucket.user_documents.name
    workspace  = google_storage_bucket.workspace_files.name
  }
}

output "supabase_url" {
  value = supabase_project.raptorflow.url
}

output "supabase_anon_key" {
  value = supabase_project.raptorflow.anon_key
}

output "supabase_service_role_key" {
  value = supabase_project.raptorflow.service_role_key
}
