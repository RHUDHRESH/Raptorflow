# Monitoring & Rollback Procedures
## RaptorFlow Unified Backend Operations

## Observability Stack

### 1. CloudWatch Monitoring

#### Dashboard Overview
The system includes comprehensive CloudWatch dashboards tracking:

**ECS Services Metrics:**
- CPU/Memory utilization per service
- Task count and scaling events
- Container health and restarts
- Network I/O and connections

**API Performance:**
- Response times (avg, p95, p99)
- Request count and throughput
- Error rates (4xx, 5xx)
- Geographic distribution

**Database & Cache:**
- RDS: CPU, storage, connections, query performance
- Redis: Hit rates, memory usage, connections
- Slow query logs and deadlocks

**Infrastructure:**
- ALB: Request routing, target health
- VPC: Network traffic, security groups
- Cost and usage metrics

#### Key Metrics Queries

```sql
-- API Response Time Percentiles
SELECT
  AVG(TargetResponseTime) as avg_response_time,
  APPROXIMATE PERCENTILE_DISC(0.95) WITHIN GROUP (ORDER BY TargetResponseTime) as p95_response_time,
  APPROXIMATE PERCENTILE_DISC(0.99) WITHIN GROUP (ORDER BY TargetResponseTime) as p99_response_time
FROM "AWS/ApplicationELB"
WHERE LoadBalancer = '${alb_arn_suffix}'
  AND TIMESTAMP > ago(1h)

-- Error Rate Calculation
SELECT
  (SUM(HTTPCode_Target_5XX_Count) / SUM(RequestCount)) * 100 as error_rate_percent
FROM "AWS/ApplicationELB"
WHERE LoadBalancer = '${alb_arn_suffix}'
  AND TIMESTAMP > ago(5m)
```

### 2. Application Metrics

#### Custom Business Metrics
```typescript
// Agent Performance Tracking
const agentMetrics = {
  execution_count: 'count of agent executions',
  execution_duration: 'histogram of execution times',
  success_rate: 'percentage of successful executions',
  token_usage: 'total tokens consumed',
  cost_per_execution: 'average cost per agent run'
};

// API Usage Metrics
const apiMetrics = {
  requests_per_endpoint: 'request volume by API endpoint',
  user_sessions: 'active user sessions',
  feature_adoption: 'usage of specific features',
  error_types: 'categorization of API errors'
};
```

#### Performance Baselines
| Metric | Warning | Critical | Description |
|--------|---------|----------|-------------|
| API Response Time | > 2s | > 5s | End-to-end response time |
| Error Rate | > 1% | > 5% | HTTP 5xx error percentage |
| CPU Utilization | > 70% | > 85% | ECS task CPU usage |
| Memory Utilization | > 80% | > 90% | ECS task memory usage |
| Database Connections | > 80% | > 95% | RDS connection pool usage |

### 3. Alerting Strategy

#### Alert Tiers

**🔴 Critical Alerts (Page immediately)**
- Service unavailable (> 5 minutes)
- Data loss or corruption
- Security breach detected
- Database unavailable
- Complete API failure

**🟡 Warning Alerts (Respond within 30 minutes)**
- High error rates (> 5%)
- Performance degradation (> 3s P95)
- Resource exhaustion (> 85% utilization)
- Unusual traffic patterns
- Failed deployments

**ℹ️ Info Alerts (Monitor trends)**
- Usage spikes
- Performance improvements
- Cost anomalies
- Feature adoption changes

#### Alert Configuration

```hcl
# Example CloudWatch Alarm
resource "aws_cloudwatch_metric_alarm" "api_critical_errors" {
  alarm_name          = "prod-api-critical-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "50" # 50+ 5xx errors in 5 minutes

  alarm_actions = [
    aws_sns_topic.critical_alerts.arn,
    aws_sns_topic.pagerduty.arn
  ]

  ok_actions = [
    aws_sns_topic.alerts_recovery.arn
  ]
}
```

## Rollback Procedures

### Automated Rollback

#### 1. GitHub Actions Rollback
```yaml
# Rollback workflow trigger
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to rollback'
        required: true
        default: 'production'
      version:
        description: 'Version to rollback to'
        required: false
        default: 'previous'

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Rollback Deployment
        run: |
          # Get previous stable version
          PREVIOUS_TAG=$(git describe --abbrev=0 --tags 2>/dev/null || echo "v1.0.0")

          # Deploy previous version
          aws ecs update-service \
            --cluster raptorflow-prod \
            --service unified-orchestrator \
            --force-new-deployment \
            --task-definition raptorflow-orchestrator:$PREVIOUS_TAG
```

#### 2. Terraform Rollback
```bash
# Rollback infrastructure changes
cd infrastructure/terraform

# Get previous state
terraform state pull > backup.tfstate
git checkout HEAD~1 -- *.tf

# Plan rollback
terraform plan -state=backup.tfstate

# Apply rollback
terraform apply -state=backup.tfstate
```

### Manual Rollback Procedures

#### Emergency Rollback (< 5 minutes)
```bash
#!/bin/bash
# emergency_rollback.sh

ENVIRONMENT=$1
SERVICE_NAME="unified-orchestrator"

echo "🚨 EMERGENCY ROLLBACK INITIATED"
echo "Environment: $ENVIRONMENT"
echo "Service: $SERVICE_NAME"

# 1. Scale down problematic service
aws ecs update-service \
  --cluster "raptorflow-$ENVIRONMENT" \
  --service "$SERVICE_NAME" \
  --desired-count 0

# 2. Scale up backup service
aws ecs update-service \
  --cluster "raptorflow-$ENVIRONMENT" \
  --service "v1-agents-backup" \
  --desired-count 3

# 3. Update ALB to route to backup
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions '[{
    "Type": "forward",
    "ForwardConfig": {
      "TargetGroups": [{"TargetGroupArn": "'$BACKUP_TG_ARN'"}]
    }
  }]'

echo "✅ Emergency rollback completed"
echo "Traffic routed to backup service"
```

#### Database Rollback
```bash
#!/bin/bash
# database_rollback.sh

BACKUP_TIMESTAMP=$1

# 1. Stop application traffic
aws ecs update-service --cluster raptorflow-prod --service unified-orchestrator --desired-count 0

# 2. Restore from backup
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier raptorflow-prod-rollback \
  --db-snapshot-identifier $BACKUP_TIMESTAMP \
  --db-instance-class db.t3.medium

# 3. Switch DNS/connection strings
# Update parameter store with new endpoint
aws ssm put-parameter \
  --name "/raptorflow/prod/database/endpoint" \
  --value $NEW_ENDPOINT \
  --overwrite

# 4. Restart services
aws ecs update-service --cluster raptorflow-prod --service unified-orchestrator --desired-count 3
```

### Service-Specific Rollbacks

#### ECS Service Rollback
```bash
# Roll back to specific task definition
TASK_DEFINITION_ARN=$(aws ecs list-task-definitions \
  --family-prefix raptorflow-orchestrator \
  --sort DESC \
  --max-items 10 \
  | jq -r '.taskDefinitionArns[1]') # Get second most recent

aws ecs update-service \
  --cluster raptorflow-prod \
  --service unified-orchestrator \
  --task-definition $TASK_DEFINITION_ARN \
  --force-new-deployment
```

#### Lambda Function Rollback
```bash
# Roll back Lambda function
aws lambda update-function-code \
  --function-name raptorflow-webhook-processor \
  --s3-bucket raptorflow-deployments \
  --s3-key lambda/previous-version.zip
```

## Incident Response

### Incident Severity Levels

| Level | Description | Response Time | Communication |
|-------|-------------|---------------|---------------|
| **SEV-1** | System down, data loss | < 15 minutes | Immediate page + customer notification |
| **SEV-2** | Major feature broken | < 1 hour | Slack alerts + status page |
| **SEV-3** | Minor issue, workaround available | < 4 hours | Internal monitoring |
| **SEV-4** | Cosmetic or minor issues | < 24 hours | Ticket tracking |

### Incident Response Process

#### 1. Detection
- **Automated**: CloudWatch alarms trigger PagerDuty
- **Manual**: User reports or monitoring dashboard alerts
- **Proactive**: Regular health checks identify issues

#### 2. Assessment (First 15 minutes)
```bash
# Quick health check
curl -f https://api.raptorflow.in/health
curl -f https://api.raptorflow.in/v3/agents

# Check service status
aws ecs describe-services --cluster raptorflow-prod --services unified-orchestrator

# Database connectivity
aws rds describe-db-instances --db-instance-identifier raptorflow-prod-db

# Recent deployments
aws ecs list-tasks --cluster raptorflow-prod --family raptorflow-orchestrator
```

#### 3. Containment (Next 30 minutes)
- **Isolate affected components**
- **Scale up/down resources as needed**
- **Enable circuit breakers if available**
- **Notify stakeholders**

#### 4. Recovery (Next 1-4 hours)
- **Execute rollback procedures**
- **Restore from backups if needed**
- **Verify system stability**
- **Gradually restore traffic**

#### 5. Post-Mortem (Within 24 hours)
```markdown
# Incident Report Template

## Incident Summary
- **Date/Time**: [Timestamp]
- **Duration**: [Duration]
- **Impact**: [Users/Services affected]
- **Severity**: [SEV-1/2/3/4]

## Root Cause
[Detailed analysis of what caused the incident]

## Resolution
[Steps taken to resolve the issue]

## Prevention
[Actions to prevent similar incidents]

## Timeline
- [Time] Incident detected
- [Time] Initial assessment
- [Time] Containment started
- [Time] Recovery completed
- [Time] Full service restored

## Metrics
- MTTR: [Mean Time To Recovery]
- Impact: [Number of users affected]
- Cost: [Financial impact if any]
```

## Health Checks & Maintenance

### Automated Health Checks

#### Application Health
```bash
# Health endpoint checks
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://api.raptorflow.in/health)
if [ "$HEALTH_CHECK" != "200" ]; then
  echo "❌ Health check failed: $HEALTH_CHECK"
  exit 1
fi
```

#### Dependency Checks
```bash
# Database connectivity
DB_STATUS=$(aws rds describe-db-instances --db-instance-identifier raptorflow-prod-db --query 'DBInstances[0].DBInstanceStatus')
if [ "$DB_STATUS" != "\"available\"" ]; then
  echo "❌ Database unavailable: $DB_STATUS"
  exit 1
fi

# Redis connectivity
REDIS_STATUS=$(aws elasticache describe-cache-clusters --cache-cluster-id raptorflow-prod-redis --query 'CacheClusters[0].CacheClusterStatus')
if [ "$REDIS_STATUS" != "\"available\"" ]; then
  echo "❌ Redis unavailable: $REDIS_STATUS"
  exit 1
fi
```

### Maintenance Windows

#### Weekly Maintenance
- **Monday 2-4 AM UTC**: Security patching and updates
- **Wednesday 2-4 AM UTC**: Performance optimization
- **Friday 2-4 AM UTC**: Backup verification

#### Monthly Maintenance
- **First Monday**: Infrastructure updates
- **Third Monday**: Database maintenance
- **Last Friday**: Full system backup and DR testing

### Backup Verification

```bash
#!/bin/bash
# backup_verification.sh

# 1. List recent backups
aws rds describe-db-snapshots \
  --db-instance-identifier raptorflow-prod-db \
  --snapshot-type automated \
  --max-records 7

# 2. Test backup restoration (in staging)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier raptorflow-staging-restore-test \
  --db-snapshot-identifier $LATEST_SNAPSHOT \
  --db-instance-class db.t3.micro

# 3. Run integrity checks
# (Connect to restored instance and run validation queries)

# 4. Cleanup test instance
aws rds delete-db-instance \
  --db-instance-identifier raptorflow-staging-restore-test \
  --skip-final-snapshot
```

## Performance Optimization

### Automated Scaling

#### ECS Auto-Scaling
```hcl
resource "aws_appautoscaling_target" "orchestrator" {
  max_capacity       = 20
  min_capacity       = 2
  resource_id        = "service/raptorflow-prod/unified-orchestrator"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu_scaling" {
  name               = "cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.orchestrator.resource_id
  scalable_dimension = aws_appautoscaling_target.orchestrator.scalable_dimension
  service_namespace  = aws_appautoscaling_target.orchestrator.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
```

#### Database Optimization
```bash
# RDS Performance Insights
aws rds describe-db-instance-automated-backups \
  --db-instance-identifier raptorflow-prod-db

# Query performance analysis
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ReadLatency \
  --dimensions Name=DBInstanceIdentifier,Value=raptorflow-prod-db \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

### Cost Monitoring

#### Budget Alerts
```hcl
resource "aws_budgets_budget" "monthly" {
  name         = "raptorflow-monthly-budget"
  budget_type  = "COST"
  limit_amount = "2000"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name   = "Service"
    values = ["Amazon Elastic Compute Cloud - Compute"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = ["alerts@raptorflow.in"]
  }
}
```

#### Cost Optimization Actions
- **Rightsizing**: Monitor and adjust instance sizes
- **Reserved Instances**: Purchase for predictable workloads
- **Spot Instances**: Use for development and batch jobs
- **Storage Optimization**: Use appropriate storage classes

## Communication Templates

### Status Page Updates

```
🚨 **System Incident** - Investigating
**Started**: [Timestamp]
**Impact**: [Description of affected services]
**Status**: Investigating root cause
**ETA**: [Estimated resolution time]

**Affected Services**:
- API Gateway: Degraded
- Agent Orchestration: Normal
- Database: Normal

**Workaround**: [If available]
**Updates**: Every 30 minutes
```

### Customer Notifications

```
Subject: RaptorFlow Service Update

Dear Valued Customer,

We are currently experiencing a temporary service issue affecting [specific features].
Our team is working diligently to resolve this.

**Current Status**: Investigating
**Estimated Resolution**: [Time estimate]
**Impact**: [Description of impact]

We apologize for any inconvenience this may cause. For urgent matters, please contact support@raptorflow.in.

Best regards,
RaptorFlow Team
```

## Documentation & Training

### Runbook Locations
- **Incident Response**: `/docs/incident-response.md`
- **Rollback Procedures**: `/docs/rollback-procedures.md`
- **Monitoring Setup**: `/docs/monitoring-setup.md`
- **Deployment Guide**: `/docs/deployment-guide.md`

### Team Training
- **Monthly Drills**: Incident response simulations
- **Quarterly Reviews**: Post-mortem analysis and improvements
- **Certification**: AWS and cloud security training
- **Documentation**: Regular updates and reviews

---

**Last Updated**: December 2025
**Version**: 1.0
**Review Cycle**: Quarterly


