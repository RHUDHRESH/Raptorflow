# AWS Infrastructure for RaptorFlow Backend (V1-V2 Unified)
# Terraform Configuration

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "raptorflow-terraform-state"
    key    = "unified-backend.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "RaptorFlow"
      Environment = var.environment
      ManagedBy   = "Terraform"
      System      = "Unified-Backend"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# VPC and Networking
module "vpc" {
  source = "./modules/vpc"

  environment = var.environment
  project     = "raptorflow"
}

# RDS PostgreSQL Database
module "rds" {
  source = "./modules/rds"

  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  database_name       = var.database_name
  database_username   = var.database_username
  database_password   = var.database_password
  allowed_cidr_blocks = [module.vpc.vpc_cidr_block]
}

# ElastiCache Redis
module "elasticache" {
  source = "./modules/elasticache"

  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
}

# ECS Cluster and Services
module "ecs" {
  source = "./modules/ecs"

  environment              = var.environment
  vpc_id                   = module.vpc.vpc_id
  private_subnet_ids       = module.vpc.private_subnet_ids
  public_subnet_ids        = module.vpc.public_subnet_ids
  database_endpoint        = module.rds.endpoint
  database_username        = var.database_username
  database_password        = var.database_password
  redis_endpoint           = module.elasticache.endpoint
  alb_security_group_id    = module.alb.security_group_id
  alb_target_group_arn     = module.alb.target_group_arn

  # Service configurations
  orchestrator_desired_count = var.orchestrator_desired_count
  v1_agents_desired_count    = var.v1_agents_desired_count
  v2_agents_desired_count    = var.v2_agents_desired_count
  api_gateway_desired_count  = var.api_gateway_desired_count
}

# Application Load Balancer
module "alb" {
  source = "./modules/alb"

  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  certificate_arn    = var.certificate_arn
}

# CloudWatch Monitoring
module "monitoring" {
  source = "./modules/monitoring"

  environment = var.environment
  region      = var.aws_region

  # Resource ARNs for monitoring
  ecs_cluster_name     = module.ecs.cluster_name
  rds_instance_id      = module.rds.instance_id
  elasticache_id       = module.elasticache.id
  alb_arn_suffix       = module.alb.arn_suffix

  # Alert configurations
  alert_email = var.alert_email
}

# S3 Buckets
module "s3" {
  source = "./modules/s3"

  environment = var.environment
}

# IAM Roles and Policies
module "iam" {
  source = "./modules/iam"

  environment = var.environment
  region      = var.aws_region

  # Resource ARNs
  s3_bucket_arn         = module.s3.assets_bucket_arn
  ecs_task_execution_arn = module.ecs.task_execution_role_arn
}

# Secrets Manager
module "secrets" {
  source = "./modules/secrets"

  environment = var.environment

  # Secrets
  database_password     = var.database_password
  jwt_secret           = var.jwt_secret
  supabase_url         = var.supabase_url
  supabase_service_key = var.supabase_service_role_key
  supabase_anon_key    = var.supabase_anon_key
  google_cloud_project = var.google_cloud_project_id
  vertex_api_key       = var.vertex_api_key
  openai_api_key       = var.openai_api_key
}

# WAF (Web Application Firewall)
module "waf" {
  source = "./modules/waf"

  environment = var.environment
}

# Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.elasticache.endpoint
  sensitive   = true
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.alb.dns_name
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "cloudwatch_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = module.monitoring.dashboard_url
}


