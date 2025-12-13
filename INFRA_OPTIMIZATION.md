# Infrastructure Cost Optimization Analysis

## Current Infrastructure Setup

### ECS Fargate
- **Current**: 512 CPU / 1024 MB RAM ($0.04048/hour ≈ $29.15/month)
- **Load**: Based on LLM inference workload
- **Cost Impact**: High - Fargate is expensive for consistent workloads

### RDS PostgreSQL
- **Current**: t3.micro ($0.018/hour ≈ $13/month)
- **Storage**: 20GB allocated
- **Load**: Light to moderate DB queries

### ElastiCache Redis
- **Current**: t3.micro ($0.018/hour ≈ $13/month)
- **Usage**: Caching, session storage, job queues

### SQS
- **Current**: Standard queues
- **Usage**: Job queuing for async processing

## Optimization Recommendations

### 1. Container Rightsizing

**Current Load Analysis:**
- LLM inference: CPU-intensive during token processing
- Memory usage: ~200-400MB for Node.js + dependencies
- Network I/O: Moderate for API calls

**Recommended Configuration:**
```terraform
# infrastructure/variables.tf
variable "task_cpu" {
  default = "256"  # Down from 512
}

variable "task_memory" {
  default = "512"  # Down from 1024
}
```

**Cost Savings**: ~$15/month (50% reduction)

### 2. Spot Instance Strategy

**Fargate Spot Implementation:**
```terraform
# Add to infrastructure/main.tf
resource "aws_ecs_capacity_provider" "spot" {
  name = "raptorflow-spot"

  fargate_spot {
    target_capacity = 70  # 70% spot, 30% on-demand
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight           = 70
  }

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight           = 30
  }
}
```

**Cost Savings**: 50-70% on compute costs

### 3. Intelligent Autoscaling

**Current**: Basic CPU/memory autoscaling
**Optimized**: Cost-aware autoscaling

```terraform
# Replace basic autoscaling with intelligent rules
resource "aws_appautoscaling_policy" "cost_optimized_cpu" {
  policy_type = "TargetTrackingScaling"

  target_tracking_scaling_policy_configuration {
    customized_metric_specification {
      metric_name = "CPUUtilization"
      namespace   = "AWS/ECS"
      statistic   = "Average"

      dimensions {
        name  = "ClusterName"
        value = aws_ecs_cluster.main.name
      }
      dimensions {
        name  = "ServiceName"
        value = aws_ecs_service.app.name
      }
    }

    target_value = 60.0  # Lower threshold = fewer instances
  }
}

# Cost-based scaling policy
resource "aws_appautoscaling_policy" "cost_based_scaling" {
  policy_type = "StepScaling"

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown               = 300
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_lower_bound = 0
      scaling_adjustment          = -1  # Scale down when cost is low
    }
  }
}
```

### 4. Database Optimization

**RDS Rightsizing:**
- **Current**: t3.micro (2 vCPU, 1GB RAM)
- **Analysis**: Most queries are simple SELECT/INSERT
- **Recommendation**: db.t4g.micro (better price/performance for burstable workloads)

**Storage Optimization:**
```terraform
# infrastructure/modules/rds/main.tf
resource "aws_db_instance" "main" {
  instance_class = "db.t4g.micro"  # Better price/perf

  allocated_storage     = 20  # Current
  max_allocated_storage = 50  # Reduced from 100

  # Enable performance insights for monitoring
  performance_insights_enabled = true
  monitoring_interval         = 60
}
```

**Cost Savings**: ~$5/month with better performance

### 5. Redis Optimization

**ElastiCache Rightsizing:**
- **Current**: t3.micro cache.t3.micro
- **Usage**: ~100-200MB memory usage
- **Recommendation**: cache.t4g.micro (better for burstable workloads)

**Persistence Strategy:**
```terraform
resource "aws_elasticache_cluster" "redis" {
  cluster_id      = "raptorflow-cache"
  engine         = "redis"
  node_type      = "cache.t4g.micro"
  num_cache_nodes = 1

  # Enable backup for critical data only
  snapshot_retention_limit = 3  # Reduced from default
}
```

### 6. Serverless Migration Path

**Long-term Recommendation: AWS Lambda**

**Lambda Configuration:**
```terraform
# Potential Lambda implementation for API endpoints
resource "aws_lambda_function" "api" {
  function_name = "raptorflow-api"
  runtime      = "nodejs20.x"
  memory_size  = 512  # 512MB
  timeout      = 30   # 30 seconds

  # Provisioned concurrency for consistent performance
  reserved_concurrent_executions = 5
}

# API Gateway integration
resource "aws_apigatewayv2_integration" "lambda" {
  integration_type = "AWS_PROXY"
  connection_type  = "INTERNET"
  integration_method = "POST"
  integration_uri  = aws_lambda_function.api.invoke_arn
}
```

**Migration Benefits:**
- Pay only for actual usage
- Automatic scaling to zero
- No server management
- Better cost granularity

## Implementation Phases

### Phase 1: Quick Wins (Week 1)
1. Right-size containers (256 CPU / 512 MB)
2. Enable Fargate Spot with 70/30 split
3. Reduce RDS storage limits
4. Optimize autoscaling thresholds

**Cost Savings**: ~$20-25/month (40% reduction)

### Phase 2: Advanced Optimization (Week 2)
1. Implement cost-based autoscaling
2. Add performance monitoring
3. Optimize Redis configuration
4. Set up automated cost alerts

**Cost Savings**: Additional ~$10-15/month

### Phase 3: Serverless Migration (Month 2)
1. Migrate read-heavy endpoints to Lambda
2. Implement API Gateway with caching
3. Set up CloudFront for static assets
4. Monitor and optimize cold starts

**Cost Savings**: 60-80% on compute costs

## Monitoring & Alerts

**CloudWatch Alarms for Cost Control:**
```terraform
resource "aws_cloudwatch_metric_alarm" "high_cost" {
  alarm_name          = "raptorflow-high-cost"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "21600"  # 6 hours
  statistic           = "Maximum"
  threshold           = "50"     # $50/day threshold
  alarm_description   = "Cost threshold exceeded"

  dimensions = {
    Currency = "USD"
    ServiceName = "AmazonEC2"  # Adjust for actual services
  }
}
```

## Success Metrics

- **Cost per request**: Target <$0.03
- **Infrastructure cost**: Reduce by 50-70%
- **Performance**: Maintain <2s average response time
- **Availability**: Maintain 99.9% uptime

## Total Projected Savings

**Current Monthly Cost**: ~$60 (infrastructure only)
**Optimized Monthly Cost**: ~$15-25
**Annual Savings**: $420-4200

**Note**: Actual savings depend on traffic patterns and usage. Monitor closely during initial optimization period.


