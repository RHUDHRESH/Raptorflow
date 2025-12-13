# ECS Module for RaptorFlow Backend Services

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.environment}-raptorflow-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${var.environment}-ecs-cluster"
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name       = aws_ecs_cluster.main.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "orchestrator" {
  name              = "/ecs/${var.environment}/orchestrator"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.environment}-orchestrator-logs"
  }
}

resource "aws_cloudwatch_log_group" "v1_agents" {
  name              = "/ecs/${var.environment}/v1-agents"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.environment}-v1-agents-logs"
  }
}

resource "aws_cloudwatch_log_group" "v2_agents" {
  name              = "/ecs/${var.environment}/v2-agents"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.environment}-v2-agents-logs"
  }
}

resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/ecs/${var.environment}/api-gateway"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.environment}-api-gateway-logs"
  }
}

# ECS Task Definitions
resource "aws_ecs_task_definition" "orchestrator" {
  family                   = "${var.environment}-orchestrator"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.orchestrator_cpu
  memory                   = var.orchestrator_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn           = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "orchestrator"
      image = var.container_image

      environment = [
        {
          name  = "NODE_ENV"
          value = var.environment
        },
        {
          name  = "PORT"
          value = "3000"
        },
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.database_username}:${var.database_password}@${var.database_endpoint}/${var.database_name}"
        },
        {
          name  = "REDIS_URL"
          value = "redis://${var.redis_endpoint}"
        }
      ]

      secrets = [
        {
          name      = "SUPABASE_URL"
          valueFrom = "${var.secrets_arn}:supabase_url::"
        },
        {
          name      = "SUPABASE_SERVICE_ROLE_KEY"
          valueFrom = "${var.secrets_arn}:supabase_service_role_key::"
        },
        {
          name      = "JWT_SECRET"
          valueFrom = "${var.secrets_arn}:jwt_secret::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.orchestrator.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command = ["CMD-SHELL", "curl -f http://localhost:3000/health || exit 1"]
        interval = 30
        timeout  = 5
        retries  = 3
      }

      essential = true
    }
  ])

  tags = {
    Name = "${var.environment}-orchestrator-task"
  }
}

resource "aws_ecs_task_definition" "v1_agents" {
  family                   = "${var.environment}-v1-agents"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.agent_cpu
  memory                   = var.agent_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn           = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "v1-agents"
      image = var.container_image

      environment = [
        {
          name  = "NODE_ENV"
          value = var.environment
        },
        {
          name  = "SERVICE_TYPE"
          value = "v1_agents"
        },
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.database_username}:${var.database_password}@${var.database_endpoint}/${var.database_name}"
        },
        {
          name  = "REDIS_URL"
          value = "redis://${var.redis_endpoint}"
        }
      ]

      secrets = [
        {
          name      = "SUPABASE_URL"
          valueFrom = "${var.secrets_arn}:supabase_url::"
        },
        {
          name      = "SUPABASE_SERVICE_ROLE_KEY"
          valueFrom = "${var.secrets_arn}:supabase_service_role_key::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.v1_agents.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name = "${var.environment}-v1-agents-task"
  }
}

resource "aws_ecs_task_definition" "v2_agents" {
  family                   = "${var.environment}-v2-agents"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.agent_cpu
  memory                   = var.agent_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn           = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "v2-agents"
      image = var.container_image

      environment = [
        {
          name  = "NODE_ENV"
          value = var.environment
        },
        {
          name  = "SERVICE_TYPE"
          value = "v2_agents"
        },
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.database_username}:${var.database_password}@${var.database_endpoint}/${var.database_name}"
        },
        {
          name  = "REDIS_URL"
          value = "redis://${var.redis_endpoint}"
        }
      ]

      secrets = [
        {
          name      = "SUPABASE_URL"
          valueFrom = "${var.secrets_arn}:supabase_url::"
        },
        {
          name      = "SUPABASE_SERVICE_ROLE_KEY"
          valueFrom = "${var.secrets_arn}:supabase_service_role_key::"
        },
        {
          name      = "GOOGLE_CLOUD_PROJECT_ID"
          valueFrom = "${var.secrets_arn}:google_cloud_project_id::"
        },
        {
          name      = "VERTEX_API_KEY"
          valueFrom = "${var.secrets_arn}:vertex_api_key::"
        },
        {
          name      = "OPENAI_API_KEY"
          valueFrom = "${var.secrets_arn}:openai_api_key::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.v2_agents.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name = "${var.environment}-v2-agents-task"
  }
}

resource "aws_ecs_task_definition" "api_gateway" {
  family                   = "${var.environment}-api-gateway"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.api_cpu
  memory                   = var.api_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn           = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "api-gateway"
      image = var.container_image

      environment = [
        {
          name  = "NODE_ENV"
          value = var.environment
        },
        {
          name  = "SERVICE_TYPE"
          value = "api_gateway"
        },
        {
          name  = "PORT"
          value = "3000"
        }
      ]

      secrets = [
        {
          name      = "SUPABASE_URL"
          valueFrom = "${var.secrets_arn}:supabase_url::"
        },
        {
          name      = "SUPABASE_ANON_KEY"
          valueFrom = "${var.secrets_arn}:supabase_anon_key::"
        },
        {
          name      = "JWT_SECRET"
          valueFrom = "${var.secrets_arn}:jwt_secret::"
        }
      ]

      portMappings = [
        {
          containerPort = 3000
          hostPort      = 3000
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.api_gateway.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name = "${var.environment}-api-gateway-task"
  }
}

# ECS Services
resource "aws_ecs_service" "orchestrator" {
  name            = "${var.environment}-orchestrator"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.orchestrator.arn
  desired_count   = var.orchestrator_desired_count

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  load_balancer {
    target_group_arn = var.alb_target_group_arn
    container_name   = "orchestrator"
    container_port   = 3000
  }

  depends_on = [var.alb_listener_arn]

  tags = {
    Name = "${var.environment}-orchestrator-service"
  }
}

resource "aws_ecs_service" "v1_agents" {
  name            = "${var.environment}-v1-agents"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.v1_agents.arn
  desired_count   = var.v1_agents_desired_count

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  tags = {
    Name = "${var.environment}-v1-agents-service"
  }
}

resource "aws_ecs_service" "v2_agents" {
  name            = "${var.environment}-v2-agents"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.v2_agents.arn
  desired_count   = var.v2_agents_desired_count

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  tags = {
    Name = "${var.environment}-v2-agents-service"
  }
}

resource "aws_ecs_service" "api_gateway" {
  name            = "${var.environment}-api-gateway"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api_gateway.arn
  desired_count   = var.api_gateway_desired_count

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  load_balancer {
    target_group_arn = var.alb_target_group_arn
    container_name   = "api-gateway"
    container_port   = 3000
  }

  depends_on = [var.alb_listener_arn]

  tags = {
    Name = "${var.environment}-api-gateway-service"
  }
}

# Security Groups
resource "aws_security_group" "ecs_tasks" {
  name_prefix = "${var.environment}-ecs-tasks-"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.environment}-ecs-tasks-sg"
  }
}

# IAM Roles
resource "aws_iam_role" "ecs_execution" {
  name = "${var.environment}-ecs-execution-role"

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
    Name = "${var.environment}-ecs-execution-role"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name = "${var.environment}-ecs-task-role"

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
    Name = "${var.environment}-ecs-task-role"
  }
}

# Outputs
output "cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "orchestrator_service_name" {
  description = "Orchestrator service name"
  value       = aws_ecs_service.orchestrator.name
}

output "v1_agents_service_name" {
  description = "V1 agents service name"
  value       = aws_ecs_service.v1_agents.name
}

output "v2_agents_service_name" {
  description = "V2 agents service name"
  value       = aws_ecs_service.v2_agents.name
}

output "api_gateway_service_name" {
  description = "API gateway service name"
  value       = aws_ecs_service.api_gateway.name
}

output "task_execution_role_arn" {
  description = "ECS task execution role ARN"
  value       = aws_iam_role.ecs_execution.arn
}


