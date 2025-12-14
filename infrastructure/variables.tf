# =====================================================
# TERRAFORM VARIABLES
# =====================================================

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod"
  }
}

# =====================================================
# APPLICATION CONFIGURATION
# =====================================================

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

variable "google_cloud_project_id" {
  description = "Google Cloud Project ID for Vertex AI"
  type        = string
}

# =====================================================
# DATABASE CONFIGURATION
# =====================================================

variable "database_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "raptorflow"
}

variable "database_username" {
  description = "PostgreSQL database username"
  type        = string
  default     = "raptorflow"
}

variable "database_password" {
  description = "PostgreSQL database password"
  type        = string
  sensitive   = true
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"  # More cost-effective than t3.micro
}

variable "rds_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "rds_max_allocated_storage" {
  description = "RDS maximum allocated storage in GB"
  type        = number
  default     = 50  # Reduced from 100 for cost optimization
}

# =====================================================
# REDIS CONFIGURATION
# =====================================================

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t4g.micro"  # More cost-effective than t3.micro
}

# =====================================================
# S3 CONFIGURATION
# =====================================================

variable "s3_allowed_origins" {
  description = "List of allowed origins for S3 CORS"
  type        = list(string)
  default     = ["*"]
}

variable "enable_cloudfront" {
  description = "Enable CloudFront CDN for S3 assets"
  type        = bool
  default     = false
}

# =====================================================
# ECS CONFIGURATION
# =====================================================

variable "task_cpu" {
  description = "CPU units for ECS task (256, 512, 1024, 2048, 4096)"
  type        = string
  default     = "256"  # Optimized for cost - reduced from 512

  validation {
    condition = contains([
      "256", "512", "1024", "2048", "4096"
    ], var.task_cpu)
    error_message = "Task CPU must be one of: 256, 512, 1024, 2048, 4096"
  }
}

variable "task_memory" {
  description = "Memory for ECS task in MB"
  type        = string
  default     = "512"  # Optimized for cost - reduced from 1024

  validation {
    condition = contains([
      "512", "1024", "2048", "3072", "4096", "5120", "6144", "7168", "8192"
    ], var.task_memory)
    error_message = "Task memory must be a valid Fargate memory value"
  }
}

variable "container_memory_reservation" {
  description = "Soft memory limit for container in MB"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1
}

variable "min_capacity" {
  description = "Minimum number of tasks for autoscaling"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of tasks for autoscaling"
  type        = number
  default     = 10
}

# =====================================================
# MONITORING & LOGGING
# =====================================================

variable "enable_cloudwatch_alarms" {
  description = "Enable CloudWatch alarms"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30

  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653
    ], var.log_retention_days)
    error_message = "Log retention must be a valid CloudWatch retention value"
  }
}

# =====================================================
# NETWORKING
# =====================================================

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = []
}

# =====================================================
# COST OPTIMIZATION
# =====================================================

variable "enable_spot_instances" {
  description = "Enable Fargate Spot for cost optimization"
  type        = bool
  default     = false
}

variable "backup_retention_days" {
  description = "Database backup retention in days"
  type        = number
  default     = 7
}

# =====================================================
# TAGS
# =====================================================

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
