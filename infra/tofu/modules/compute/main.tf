data "aws_subnet" "selected" {
  id = var.private_subnet_ids[0]
}

data "aws_caller_identity" "current" {}

locals {
  service_discovery_namespace = "${var.name}.internal"
  qdrant_endpoint             = "http://qdrant.${local.service_discovery_namespace}:6333"
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.name}/api"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "qdrant" {
  name              = "/ecs/${var.name}/qdrant"
  retention_in_days = 30
}

resource "aws_s3_bucket" "alb_logs" {
  bucket = "${var.name}-alb-logs"
  tags   = var.tags
}

resource "aws_s3_bucket_public_access_block" "alb_logs" {
  bucket                  = aws_s3_bucket.alb_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_versioning" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  rule {
    id     = "expire-access-logs"
    status = "Enabled"

    expiration {
      days = 90
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "primary_logs" {
  bucket = aws_s3_bucket.primary_logs.id

  rule {
    id     = "expire-s3-server-access-logs"
    status = "Enabled"

    expiration {
      days = 90
    }
  }
}

resource "aws_s3_bucket_policy" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSLogDeliveryWrite"
        Effect = "Allow"
        Principal = {
          Service = "logdelivery.elasticloadbalancing.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.alb_logs.arn}/${var.name}/alb/AWSLogs/${data.aws_caller_identity.current.account_id}/*"
        Condition = {
          ArnLike = {
            "aws:SourceArn" = aws_lb.api.arn
          }
        }
      },
      {
        Sid    = "AWSLogDeliveryAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "logdelivery.elasticloadbalancing.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.alb_logs.arn
      }
    ]
  })
}

resource "aws_ecs_cluster" "this" {
  name = "${var.name}-cluster"
}

resource "aws_service_discovery_private_dns_namespace" "this" {
  name        = local.service_discovery_namespace
  description = "Private service discovery namespace for ${var.name}"
  vpc         = data.aws_subnet.selected.vpc_id
}

resource "aws_service_discovery_service" "qdrant" {
  name = "qdrant"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.this.id

    dns_records {
      ttl  = 10
      type = "A"
    }
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

resource "aws_lb" "api" {
  name                             = "${var.name}-alb"
  load_balancer_type               = "application"
  internal                         = false
  security_groups                  = [var.alb_security_group_id]
  subnets                          = var.public_subnet_ids
  idle_timeout                     = var.alb_idle_timeout_seconds
  drop_invalid_header_fields       = true
  enable_deletion_protection       = false
  enable_http2                     = true

  access_logs {
    bucket  = aws_s3_bucket.alb_logs.bucket
    prefix  = "${var.name}/alb"
    enabled = true
  }
}

resource "aws_lb_target_group" "api" {
  name                       = "${var.name}-api"
  port                       = 8080
  protocol                   = "HTTP"
  target_type                = "ip"
  vpc_id                     = data.aws_subnet.selected.vpc_id
  deregistration_delay       = var.api_deregistration_delay_seconds

  health_check {
    path                = "/health/ready"
    matcher             = "200-399"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 30
    timeout             = 5
  }

  stickiness {
    enabled         = true
    type            = "lb_cookie"
    cookie_duration = 86400
  }
}

resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.api.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.api.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${var.name}-api"
  cpu                      = 2048
  memory                   = 4096
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = var.image_uri
      essential = true
      portMappings = [
        { containerPort = 8080, hostPort = 8080 }
      ]
      environment = [
        { name = "AWS_REGION", value = var.aws_region },
        { name = "PORT", value = "8080" },
        { name = "RUST_LOG", value = "info" },
        { name = "QDRANT_URL", value = local.qdrant_endpoint }
      ]
      secrets = [
        { name = "DATABASE_APP_SECRET", valueFrom = var.database_app_secret_arn },
        { name = "DATABASE_DIRECT_SECRET", valueFrom = var.database_direct_secret_arn },
        { name = "CLERK_JWT_SECRET", valueFrom = var.clerk_jwt_secret_arn },
        { name = "GCP_API_KEY", valueFrom = var.gcp_api_key_secret_arn },
        { name = "RAZORPAY_API_KEY", valueFrom = var.razorpay_api_secret_arn },
        { name = "RESEND_API_KEY", valueFrom = var.resend_api_key_secret_arn }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.api.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_s3_bucket_policy" "primary_logs" {
  bucket = aws_s3_bucket.primary_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowS3ServerAccessLoggingWrite"
        Effect = "Allow"
        Principal = {
          Service = "logging.s3.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.primary_logs.arn}/primary/*"
        Condition = {
          ArnLike = {
            "aws:SourceArn" = aws_s3_bucket.primary.arn
          }
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

resource "aws_ecs_service" "api" {
  name                               = "${var.name}-api"
  cluster                            = aws_ecs_cluster.this.id
  task_definition                    = aws_ecs_task_definition.api.arn
  desired_count                      = var.api_desired_count
  launch_type                        = "FARGATE"
  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200
  health_check_grace_period_seconds  = 60

  network_configuration {
    assign_public_ip = false
    subnets          = var.private_subnet_ids
    security_groups  = [var.api_security_group_id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8080
  }
}

resource "aws_appautoscaling_target" "api" {
  max_capacity       = var.api_max_capacity
  min_capacity       = var.api_min_capacity
  resource_id        = "service/${aws_ecs_cluster.this.name}/${aws_ecs_service.api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "api_cpu" {
  name               = "${var.name}-api-cpu"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = var.api_cpu_target_value
    scale_in_cooldown  = 60
    scale_out_cooldown = 60

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}

resource "aws_ecs_task_definition" "qdrant" {
  family                   = "${var.name}-qdrant"
  cpu                      = var.qdrant_cpu
  memory                   = var.qdrant_memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  volume {
    name = "qdrant-storage"

    efs_volume_configuration {
      file_system_id     = var.qdrant_efs_id
      root_directory     = "/"
      transit_encryption = "ENABLED"
    }
  }

  container_definitions = jsonencode([
    {
      name      = "qdrant"
      image     = var.qdrant_image_uri
      essential = true
      portMappings = [
        { containerPort = 6333, hostPort = 6333 },
        { containerPort = 6334, hostPort = 6334 }
      ]
      environment = [
        { name = "QDRANT__SERVICE__HTTP_PORT", value = "6333" },
        { name = "QDRANT__SERVICE__GRPC_PORT", value = tostring(var.qdrant_grpc_port) },
        { name = "QDRANT__STORAGE__STORAGE_PATH", value = "/qdrant/storage" }
      ]
      mountPoints = [
        {
          sourceVolume  = "qdrant-storage"
          containerPath = "/qdrant/storage"
          readOnly      = false
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.qdrant.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "qdrant" {
  name                              = "${var.name}-qdrant"
  cluster                           = aws_ecs_cluster.this.id
  task_definition                   = aws_ecs_task_definition.qdrant.arn
  desired_count                     = var.qdrant_desired_count
  launch_type                       = "FARGATE"
  health_check_grace_period_seconds = 90

  network_configuration {
    assign_public_ip = false
    subnets          = var.private_subnet_ids
    security_groups  = [var.qdrant_security_group_id]
  }

  service_registries {
    registry_arn   = aws_service_discovery_service.qdrant.arn
    container_name  = "qdrant"
    container_port  = 6333
  }
}
