# Terraform Variables for RaptorFlow Unified Backend

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "raptorflow"
}

# Database Configuration
variable "database_name" {
  description = "RDS database name"
  type        = string
  default     = "raptorflow"
}

variable "database_username" {
  description = "RDS database username"
  type        = string
  default     = "raptorflow_admin"
}

variable "database_password" {
  description = "RDS database password"
  type        = string
  sensitive   = true
}

# ECS Service Configuration
variable "orchestrator_desired_count" {
  description = "Desired count of orchestrator service tasks"
  type        = number
  default     = 2
}

variable "v1_agents_desired_count" {
  description = "Desired count of V1 agents service tasks"
  type        = number
  default     = 1
}

variable "v2_agents_desired_count" {
  description = "Desired count of V2 agents service tasks"
  type        = number
  default     = 3
}

variable "api_gateway_desired_count" {
  description = "Desired count of API gateway service tasks"
  type        = number
  default     = 2
}

# SSL/TLS Configuration
variable "certificate_arn" {
  description = "ARN of ACM certificate for ALB"
  type        = string
  default     = ""
}

# Monitoring Configuration
variable "alert_email" {
  description = "Email address for CloudWatch alerts"
  type        = string
  default     = ""
}

# Secrets (sensitive)
variable "jwt_secret" {
  description = "JWT secret for authentication"
  type        = string
  sensitive   = true
}

variable "supabase_url" {
  description = "Supabase project URL"
  type        = string
  sensitive   = true
}

variable "supabase_service_role_key" {
  description = "Supabase service role key"
  type        = string
  sensitive   = true
}

variable "supabase_anon_key" {
  description = "Supabase anonymous key"
  type        = string
  sensitive   = true
}

variable "google_cloud_project_id" {
  description = "Google Cloud Project ID"
  type        = string
  sensitive   = true
}

variable "vertex_api_key" {
  description = "Google Vertex AI API key"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

# ECS Configuration
variable "container_cpu_orchestrator" {
  description = "CPU units for orchestrator container"
  type        = number
  default     = 1024
}

variable "container_memory_orchestrator" {
  description = "Memory for orchestrator container (MB)"
  type        = number
  default     = 2048
}

variable "container_cpu_agents" {
  description = "CPU units for agent containers"
  type        = number
  default     = 512
}

variable "container_memory_agents" {
  description = "Memory for agent containers (MB)"
  type        = number
  default     = 1024
}

variable "container_cpu_api" {
  description = "CPU units for API gateway container"
  type        = number
  default     = 512
}

variable "container_memory_api" {
  description = "Memory for API gateway container (MB)"
  type        = number
  default     = 1024
}

# RDS Configuration
variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "rds_allocated_storage" {
  description = "RDS allocated storage (GB)"
  type        = number
  default     = 20
}

variable "rds_engine_version" {
  description = "RDS PostgreSQL engine version"
  type        = string
  default     = "15.4"
}

# ElastiCache Configuration
variable "elasticache_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "elasticache_num_cache_nodes" {
  description = "Number of ElastiCache nodes"
  type        = number
  default     = 1
}

# Network Configuration
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnets" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24", "10.0.12.0/24"]
}

# Monitoring Configuration
variable "enable_cloudwatch_alarms" {
  description = "Enable CloudWatch alarms"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

# Backup Configuration
variable "backup_retention_period" {
  description = "RDS backup retention period in days"
  type        = number
  default     = 7
}

variable "enable_rds_multi_az" {
  description = "Enable RDS Multi-AZ deployment"
  type        = bool
  default     = false
}

# Cost Optimization
variable "enable_cost_allocation_tags" {
  description = "Enable cost allocation tags"
  type        = bool
  default     = true
}


