variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "kms_key_arn" {
  description = "KMS key ARN for S3 bucket encryption"
  type        = string
}

variable "allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "enable_cloudfront" {
  description = "Enable CloudFront CDN for the S3 bucket"
  type        = bool
  default     = false
}

variable "ecs_task_role_name" {
  description = "Name of the ECS task IAM role to attach S3 permissions"
  type        = string
}

