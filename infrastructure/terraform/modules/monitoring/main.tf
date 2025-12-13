# CloudWatch Monitoring Module for RaptorFlow Backend

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.environment}-raptorflow-unified"

  dashboard_body = jsonencode({
    widgets = [
      # ECS Services Health
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", var.ecs_orchestrator_service, "ClusterName", var.ecs_cluster_name, { "label": "Orchestrator CPU" }],
            [".", ".", ".", var.ecs_v1_service, ".", ".", { "label": "V1 Agents CPU" }],
            [".", ".", ".", var.ecs_v2_service, ".", ".", { "label": "V2 Agents CPU" }],
            [".", ".", ".", var.ecs_api_service, ".", ".", { "label": "API Gateway CPU" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "ECS Services CPU Utilization"
          period  = 300
        }
      },

      # Memory Usage
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ECS", "MemoryUtilization", "ServiceName", var.ecs_orchestrator_service, "ClusterName", var.ecs_cluster_name, { "label": "Orchestrator Memory" }],
            [".", ".", ".", var.ecs_v1_service, ".", ".", { "label": "V1 Agents Memory" }],
            [".", ".", ".", var.ecs_v2_service, ".", ".", { { "label": "V2 Agents Memory" }],
            [".", ".", ".", var.ecs_api_service, ".", ".", { "label": "API Gateway Memory" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "ECS Services Memory Utilization"
          period  = 300
        }
      },

      # API Response Times
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", var.alb_arn_suffix, { "label": "Avg Response Time", "stat": "Average" }],
            [".", ".", ".", ".", { "label": "P95 Response Time", "stat": "p95" }],
            [".", ".", ".", ".", { "label": "P99 Response Time", "stat": "p99" }]
          ]
          view   = "timeSeries"
          region = var.region
          title  = "API Response Times"
          period = 300
        }
      },

      # Error Rates
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", var.alb_arn_suffix, { "label": "5XX Errors" }],
            [".", "HTTPCode_Target_4XX_Count", ".", ".", { "label": "4XX Errors" }],
            [".", "RequestCount", ".", ".", { "label": "Total Requests" }]
          ]
          view   = "timeSeries"
          region = var.region
          title  = "Error Rates & Request Volume"
          period = 300
        }
      },

      # Database Performance
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.rds_instance_id, { "label": "RDS CPU" }],
            [".", "FreeStorageSpace", ".", ".", { "label": "Free Storage (MB)" }],
            [".", "DatabaseConnections", ".", ".", { "label": "Active Connections" }]
          ]
          view   = "timeSeries"
          region = var.region
          title  = "Database Performance"
          period = 300
        }
      },

      # Cache Performance
      {
        type   = "metric"
        x      = 12
        y      = 12
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ElastiCache", "CPUUtilization", "CacheClusterId", var.elasticache_id, { "label": "Redis CPU" }],
            [".", "CurrConnections", ".", ".", { "label": "Active Connections" }],
            [".", "CacheHits", ".", ".", { "label": "Cache Hits" }],
            [".", "CacheMisses", ".", ".", { "label": "Cache Misses" }]
          ]
          view   = "timeSeries"
          region = var.region
          title  = "Cache Performance"
          period = 300
        }
      }
    ]
  })
}

# CloudWatch Alarms

# High CPU Utilization
resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  for_each = toset([
    var.ecs_orchestrator_service,
    var.ecs_v1_service,
    var.ecs_v2_service,
    var.ecs_api_service
  ])

  alarm_name          = "${var.environment}-ecs-${each.value}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "ECS service ${each.value} CPU utilization is too high"
  alarm_actions       = var.enable_alarms ? [aws_sns_topic.alerts[0].arn] : []

  dimensions = {
    ServiceName  = each.value
    ClusterName  = var.ecs_cluster_name
  }

  tags = {
    Name = "${var.environment}-ecs-${each.value}-cpu-alarm"
  }
}

# High Memory Utilization
resource "aws_cloudwatch_metric_alarm" "ecs_memory_high" {
  for_each = toset([
    var.ecs_orchestrator_service,
    var.ecs_v1_service,
    var.ecs_v2_service,
    var.ecs_api_service
  ])

  alarm_name          = "${var.environment}-ecs-${each.value}-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "ECS service ${each.value} memory utilization is too high"
  alarm_actions       = var.enable_alarms ? [aws_sns_topic.alerts[0].arn] : []

  dimensions = {
    ServiceName  = each.value
    ClusterName  = var.ecs_cluster_name
  }

  tags = {
    Name = "${var.environment}-ecs-${each.value}-memory-alarm"
  }
}

# API High Error Rate
resource "aws_cloudwatch_metric_alarm" "api_5xx_errors" {
  alarm_name          = "${var.environment}-api-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "API returning too many 5XX errors"
  alarm_actions       = var.enable_alarms ? [aws_sns_topic.alerts[0].arn] : []

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }

  tags = {
    Name = "${var.environment}-api-5xx-alarm"
  }
}

# API High Response Time
resource "aws_cloudwatch_metric_alarm" "api_response_time" {
  alarm_name          = "${var.environment}-api-response-time"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = "5"
  alarm_description   = "API response time is too high"
  alarm_actions       = var.enable_alarms ? [aws_sns_topic.alerts[0].arn] : []

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }

  tags = {
    Name = "${var.environment}-api-response-time-alarm"
  }
}

# RDS High CPU
resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  alarm_name          = "${var.environment}-rds-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "RDS CPU utilization is too high"
  alarm_actions       = var.enable_alarms ? [aws_sns_topic.alerts[0].arn] : []

  dimensions = {
    DBInstanceIdentifier = var.rds_instance_id
  }

  tags = {
    Name = "${var.environment}-rds-cpu-alarm"
  }
}

# RDS Low Storage
resource "aws_cloudwatch_metric_alarm" "rds_storage_low" {
  alarm_name          = "${var.environment}-rds-storage-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "2000000000" # 2GB
  alarm_description   = "RDS free storage space is low"
  alarm_actions       = var.enable_alarms ? [aws_sns_topic.alerts[0].arn] : []

  dimensions = {
    DBInstanceIdentifier = var.rds_instance_id
  }

  tags = {
    Name = "${var.environment}-rds-storage-alarm"
  }
}

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  count = var.enable_alarms ? 1 : 0
  name  = "${var.environment}-raptorflow-alerts"

  tags = {
    Name = "${var.environment}-alerts-topic"
  }
}

resource "aws_sns_topic_subscription" "email" {
  count     = var.enable_alarms && var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts[0].arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# Outputs
output "dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://${var.region}.console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "alerts_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = var.enable_alarms ? aws_sns_topic.alerts[0].arn : null
}


