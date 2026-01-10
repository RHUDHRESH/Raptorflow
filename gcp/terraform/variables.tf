variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "raptorflow-prod"
}

variable "org_id" {
  description = "GCP Organization ID"
  type        = string
}

variable "billing_account_id" {
  description = "GCP Billing Account ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "supabase_url" {
  description = "Supabase Project URL"
  type        = string
}

variable "supabase_service_role_key" {
  description = "Supabase Service Role Key"
  type        = string
  sensitive   = true
}

variable "supabase_db_password" {
  description = "Supabase Database Password"
  type        = string
  sensitive   = true
  default     = "raptorflow-db-2024"
}

variable "supabase_region" {
  description = "Supabase Region"
  type        = string
  default     = "us-east-1"
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = "your-username"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "raptorflow"
}
