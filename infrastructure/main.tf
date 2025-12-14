# =====================================================
# SOTA AWS INFRASTRUCTURE - ECS/FARGATE DEPLOYMENT
# =====================================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Configure S3 backend for state management
  backend "s3" {
    bucket         = "raptorflow-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "raptorflow-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "RaptorFlow"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# =====================================================
# KMS KEY FOR ENCRYPTION
# =====================================================

resource "aws_kms_key" "main" {
  description             = "KMS key for RaptorFlow encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name = "raptorflow-kms-${var.environment}"
  }
}

resource "aws_kms_alias" "main" {
  name          = "alias/raptorflow-${var.environment}"
  target_key_id = aws_kms_key.main.key_id
}

# =====================================================
# VPC & NETWORKING
# =====================================================

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "raptorflow-${var.environment}"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = var.environment == "dev"
  enable_dns_hostnames   = true
  enable_dns_support     = true

  # VPC endpoints for security
  enable_s3_endpoint              = true
  enable_dynamodb_endpoint        = true
  enable_secretsmanager_endpoint  = true
  enable_bedrock_endpoint         = true

  tags = {
    Name = "raptorflow-${var.environment}"
  }
}

# =====================================================
# RDS POSTGRES DATABASE
# =====================================================

module "rds" {
  source = "./modules/rds"

  environment             = var.environment
  vpc_id                  = module.vpc.vpc_id
  private_subnet_ids      = module.vpc.private_subnets
  allowed_security_groups = [aws_security_group.ecs_tasks.id]
  instance_class          = var.rds_instance_class
  allocated_storage       = var.rds_allocated_storage
  max_allocated_storage   = var.rds_max_allocated_storage
  database_name           = var.database_name
  database_username       = var.database_username
  database_password       = var.database_password
  kms_key_arn            = aws_kms_key.main.arn
}

# =====================================================
# ELASTICACHE REDIS
# =====================================================

module "elasticache" {
  source = "./modules/elasticache"

  environment             = var.environment
  vpc_id                  = module.vpc.vpc_id
  private_subnet_ids      = module.vpc.private_subnets
  allowed_security_groups = [aws_security_group.ecs_tasks.id]
  node_type              = var.redis_node_type
  kms_key_arn            = aws_kms_key.main.arn
}

# =====================================================
# S3 ASSETS BUCKET
# =====================================================

module "s3_assets" {
  source = "./modules/s3"

  environment        = var.environment
  kms_key_arn       = aws_kms_key.main.arn
  allowed_origins    = var.s3_allowed_origins
  enable_cloudfront  = var.enable_cloudfront
  ecs_task_role_name = aws_iam_role.ecs_task_role.name
}

# =====================================================
# SQS JOB QUEUE
# =====================================================

resource "aws_sqs_queue" "orchestrator_jobs" {
  name                       = "raptorflow-orchestrator-jobs-${var.environment}"
  delay_seconds             = 0
  max_message_size          = 262144  # 256 KB
  message_retention_seconds = 86400   # 24 hours
  receive_wait_time_seconds = 0
  visibility_timeout_seconds = 300    # 5 minutes

  # Enable encryption
  kms_master_key_id = aws_kms_key.main.key_id
  kms_data_key_reuse_period_seconds = 300

  tags = {
    Name = "raptorflow-orchestrator-jobs-${var.environment}"
  }
}

resource "aws_sqs_queue" "orchestrator_jobs_dlq" {
  name                       = "raptorflow-orchestrator-jobs-dlq-${var.environment}"
  message_retention_seconds = 1209600  # 14 days

  tags = {
    Name = "raptorflow-orchestrator-jobs-dlq-${var.environment}"
  }
}

resource "aws_sqs_queue_redrive_policy" "orchestrator_jobs" {
  queue_url = aws_sqs_queue.orchestrator_jobs.id
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.orchestrator_jobs_dlq.arn
    maxReceiveCount     = 3
  })
}

# =====================================================
# SECURITY GROUPS
# =====================================================

resource "aws_security_group" "ecs_tasks" {
  name_prefix = "raptorflow-ecs-tasks-"
  description = "Security group for ECS tasks"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "Allow inbound traffic from ALB"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "raptorflow-ecs-tasks-${var.environment}"
  }
}

resource "aws_security_group" "alb" {
  name_prefix = "raptorflow-alb-"
  description = "Security group for ALB"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "Allow HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "raptorflow-alb-${var.environment}"
  }
}

# =====================================================
# SECRETS MANAGER
# =====================================================

resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "raptorflow/${var.environment}/app"
  description = "Application secrets for RaptorFlow"

  tags = {
    Name = "raptorflow-app-secrets-${var.environment}"
  }
}

resource "aws_secretsmanager_secret_version" "app_secrets_version" {
  secret_id = aws_secretsmanager_secret.app_secrets.id

  secret_string = jsonencode({
    SUPABASE_URL             = var.supabase_url
    SUPABASE_SERVICE_ROLE_KEY = var.supabase_service_role_key
    GOOGLE_CLOUD_PROJECT_ID  = var.google_cloud_project_id
    AWS_REGION              = var.aws_region
    DATABASE_URL            = "postgresql://${var.database_username}:${var.database_password}@${module.rds.db_endpoint}/${var.database_name}"
    REDIS_URL              = "redis://${module.elasticache.redis_endpoint}:${module.elasticache.redis_port}"
    VERTEX_AI_PROJECT_ID   = var.google_cloud_project_id
    # Add other secrets as needed
  })
}

# =====================================================
# IAM ROLES & POLICIES
# =====================================================

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "raptorflow-ecs-task-execution-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "raptorflow-ecs-task-execution-${var.environment}"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Custom policy for application-specific permissions
resource "aws_iam_role_policy" "ecs_task_execution_custom" {
  name = "raptorflow-ecs-task-execution-custom-${var.environment}"
  role = aws_iam_role.ecs_task_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = [
          aws_secretsmanager_secret.app_secrets.arn,
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/raptorflow/${var.environment}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-3-opus-20240229-v1:0",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/ecs/raptorflow-${var.environment}*"
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters"
        ]
        Resource = module.rds.db_instance_id
      },
      {
        Effect = "Allow"
        Action = [
          "elasticache:DescribeReplicationGroups",
          "elasticache:DescribeCacheClusters"
        ]
        Resource = "arn:aws:elasticache:${var.aws_region}:${data.aws_caller_identity.current.account_id}:replicationgroup:${module.elasticache.redis_replication_group_id}"
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:GetQueueUrl"
        ]
        Resource = [
          aws_sqs_queue.orchestrator_jobs.arn,
          aws_sqs_queue.orchestrator_jobs_dlq.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role" "ecs_task_role" {
  name = "raptorflow-ecs-task-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "raptorflow-ecs-task-${var.environment}"
  }
}

# =====================================================
# ECR REPOSITORY
# =====================================================

resource "aws_ecr_repository" "app" {
  name                 = "raptorflow/backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name = "raptorflow-backend-${var.environment}"
  }
}

resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# =====================================================
# CLOUDWATCH LOGS
# =====================================================

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/raptorflow-${var.environment}"
  retention_in_days = var.environment == "prod" ? 30 : 7

  tags = {
    Name = "raptorflow-ecs-logs-${var.environment}"
  }
}

# =====================================================
# ECS CLUSTER & SERVICE
# =====================================================

resource "aws_ecs_cluster" "main" {
  name = "raptorflow-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "raptorflow-cluster-${var.environment}"
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name       = aws_ecs_cluster.main.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  # Cost-optimized: 70% spot instances, 30% on-demand for reliability
  default_capacity_provider_strategy {
    base              = 1
    weight            = 30
    capacity_provider = "FARGATE"
  }

  default_capacity_provider_strategy {
    base              = 0
    weight            = 70
    capacity_provider = "FARGATE_SPOT"
  }
}

resource "aws_ecs_task_definition" "app" {
  family                   = "raptorflow-backend-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "raptorflow-backend"
      image = "${aws_ecr_repository.app.repository_url}:latest"

      essential = true

      environment = [
        {
          name  = "NODE_ENV"
          value = "production"
        },
        {
          name  = "PORT"
          value = "8080"
        }
      ]

      secrets = [
        {
          name      = "SUPABASE_URL"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:SUPABASE_URL::"
        },
        {
          name      = "SUPABASE_SERVICE_ROLE_KEY"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:SUPABASE_SERVICE_ROLE_KEY::"
        },
        {
          name      = "GOOGLE_CLOUD_PROJECT_ID"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:GOOGLE_CLOUD_PROJECT_ID::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command = [
          "CMD-SHELL",
          "curl -f http://localhost:8080/health || exit 1"
        ]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }

      # Resource limits
      memoryReservation = var.container_memory_reservation
    }
  ])

  tags = {
    Name = "raptorflow-task-${var.environment}"
  }
}

# =====================================================
# APPLICATION LOAD BALANCER
# =====================================================

resource "aws_lb" "main" {
  name               = "raptorflow-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets

  enable_deletion_protection = var.environment == "prod"

  tags = {
    Name = "raptorflow-alb-${var.environment}"
  }
}

resource "aws_lb_target_group" "app" {
  name        = "raptorflow-tg-${var.environment}"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name = "raptorflow-tg-${var.environment}"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# =====================================================
# ECS SERVICE
# =====================================================

resource "aws_ecs_service" "app" {
  name            = "raptorflow-backend-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = module.vpc.private_subnets
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "raptorflow-backend"
    container_port   = 8080
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight           = 100
  }

  deployment_controller {
    type = "ECS"
  }

  depends_on = [aws_lb_listener.http]

  tags = {
    Name = "raptorflow-service-${var.environment}"
  }
}

# =====================================================
# AUTO SCALING
# =====================================================

resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_cpu_policy" {
  name               = "raptorflow-cpu-autoscaling-${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 60.0  # Reduced from 70% for cost optimization
  }
}

resource "aws_appautoscaling_policy" "ecs_memory_policy" {
  name               = "raptorflow-memory-autoscaling-${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = 70.0  # Reduced from 80% for cost optimization
  }
}

# Cost-aware scaling policy - scale down during low-cost periods
resource "aws_appautoscaling_policy" "cost_optimized_scaling" {
  name               = "raptorflow-cost-autoscaling-${var.environment}"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown               = 300  # 5 minutes
    metric_aggregation_type = "Average"

    # Scale down when CPU is consistently low (cost saving)
    step_adjustment {
      metric_interval_upper_bound = 30
      scaling_adjustment          = -1
    }

    # Scale up only when absolutely necessary
    step_adjustment {
      metric_interval_lower_bound = 80
      metric_interval_upper_bound = 0
      scaling_adjustment          = 1
    }
  }
}

# =====================================================
# CLOUDWATCH ALARMS & MONITORING
# =====================================================

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "raptorflow-high-cpu-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "75"  # Reduced from 80 for cost optimization
  alarm_description   = "This metric monitors ECS CPU utilization"
  alarm_actions       = []

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.app.name
  }
}

# Cost monitoring alarm
resource "aws_cloudwatch_metric_alarm" "high_cost" {
  alarm_name          = "raptorflow-high-daily-cost-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "21600"  # 6 hours
  statistic           = "Maximum"
  threshold           = "25"     # $25/day cost threshold
  alarm_description   = "Daily cost threshold exceeded - review usage"
  alarm_actions       = []

  dimensions = {
    Currency    = "USD"
    ServiceName = "AmazonEC2"  # Primary cost driver
  }
}

# =====================================================
# DATA SOURCES
# =====================================================

data "aws_caller_identity" "current" {}

# =====================================================
# OUTPUTS
# =====================================================

output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "ecr_repository_url" {
  description = "ECR repository URL for pushing images"
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "secrets_manager_arn" {
  description = "Secrets Manager ARN"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

# =====================================================
# DATABASE OUTPUTS
# =====================================================

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = module.rds.db_endpoint
}

output "rds_port" {
  description = "RDS PostgreSQL port"
  value       = module.rds.db_port
}

output "rds_database_name" {
  description = "RDS database name"
  value       = module.rds.db_name
}

# =====================================================
# REDIS OUTPUTS
# =====================================================

output "redis_endpoint" {
  description = "Redis primary endpoint"
  value       = module.elasticache.redis_endpoint
}

output "redis_port" {
  description = "Redis port"
  value       = module.elasticache.redis_port
}

# =====================================================
# S3 OUTPUTS
# =====================================================

output "s3_assets_bucket_name" {
  description = "S3 assets bucket name"
  value       = module.s3_assets.bucket_name
}

output "s3_assets_bucket_arn" {
  description = "S3 assets bucket ARN"
  value       = module.s3_assets.bucket_arn
}

output "s3_assets_cloudfront_domain" {
  description = "CloudFront domain for S3 assets (if enabled)"
  value       = module.s3_assets.cloudfront_domain_name
}

# =====================================================
# SQS OUTPUTS
# =====================================================

output "sqs_queue_url" {
  description = "SQS queue URL for orchestrator jobs"
  value       = aws_sqs_queue.orchestrator_jobs.url
}

output "sqs_queue_arn" {
  description = "SQS queue ARN for orchestrator jobs"
  value       = aws_sqs_queue.orchestrator_jobs.arn
}

output "sqs_dlq_url" {
  description = "SQS DLQ URL for failed orchestrator jobs"
  value       = aws_sqs_queue.orchestrator_jobs_dlq.url
}
