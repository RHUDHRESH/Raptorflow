# Monitoring Module Variables

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "enable_alarms" {
  description = "Enable CloudWatch alarms"
  type        = bool
  default     = true
}

variable "alert_email" {
  description = "Email address for alerts"
  type        = string
  default     = ""
}

variable "ecs_cluster_name" {
  description = "ECS cluster name"
  type        = string
}

variable "ecs_orchestrator_service" {
  description = "ECS orchestrator service name"
  type        = string
}

variable "ecs_v1_service" {
  description = "ECS V1 service name"
  type        = string
}

variable "ecs_v2_service" {
  description = "ECS V2 service name"
  type        = string
}

variable "ecs_api_service" {
  description = "ECS API service name"
  type        = string
}

variable "rds_instance_id" {
  description = "RDS instance ID"
  type        = string
}

variable "elasticache_id" {
  description = "ElastiCache cluster ID"
  type        = string
}

variable "alb_arn_suffix" {
  description = "ALB ARN suffix"
  type        = string
}


