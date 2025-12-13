# =====================================================
# ELASTICACHE REDIS MODULE
# =====================================================

resource "aws_elasticache_subnet_group" "main" {
  name       = "raptorflow-redis-${var.environment}"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "raptorflow-redis-subnet-group-${var.environment}"
  }
}

resource "aws_security_group" "redis" {
  name_prefix = "raptorflow-redis-"
  description = "Security group for ElastiCache Redis"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow Redis access from ECS tasks"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = var.allowed_security_groups
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "raptorflow-redis-sg-${var.environment}"
  }
}

resource "aws_elasticache_parameter_group" "main" {
  family = "redis7"
  name   = "raptorflow-redis-${var.environment}"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  parameter {
    name  = "tcp-keepalive"
    value = "300"
  }

  parameter {
    name  = "maxclients"
    value = "65000"
  }

  tags = {
    Name = "raptorflow-redis-params-${var.environment}"
  }
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "raptorflow-redis-${var.environment}"
  description               = "Redis cluster for RaptorFlow orchestrator"
  node_type                 = var.node_type
  port                      = 6379
  parameter_group_name      = aws_elasticache_parameter_group.main.name
  subnet_group_name         = aws_elasticache_subnet_group.main.name
  security_group_ids        = [aws_security_group.redis.id]

  # Cluster configuration
  num_cache_clusters = var.environment == "prod" ? 2 : 1

  # Engine configuration
  engine         = "redis"
  engine_version = "7.1"

  # Maintenance & backup
  maintenance_window       = "sun:04:00-sun:05:00"
  snapshot_window         = "03:00-04:00"
  snapshot_retention_limit = var.environment == "prod" ? 7 : 1
  final_snapshot_identifier = var.environment == "prod" ? "raptorflow-redis-final-${var.environment}" : null

  # Security
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  kms_key_id                = var.kms_key_arn

  # Monitoring
  notification_topic_arn = var.environment == "prod" ? var.sns_topic_arn : null

  tags = {
    Name = "raptorflow-redis-${var.environment}"
  }
}

# CloudWatch alarms for Redis
resource "aws_cloudwatch_metric_alarm" "redis_cpu" {
  alarm_name          = "raptorflow-redis-cpu-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Redis CPU utilization is too high"

  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.main.id
  }
}

resource "aws_cloudwatch_metric_alarm" "redis_memory" {
  alarm_name          = "raptorflow-redis-memory-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "90"
  alarm_description   = "Redis memory usage is too high"

  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.main.id
  }
}

