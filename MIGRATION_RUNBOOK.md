# RaptorFlow Backend Migration Runbook
## V1-V2 Unified System Deployment

## Overview

This runbook outlines the staged migration from separate V1/V2 systems to a unified backend deployed on AWS. The migration ensures zero downtime and maintains backward compatibility throughout the process.

## Pre-Migration Checklist

### ✅ Infrastructure Prerequisites
- [ ] AWS account configured with proper IAM permissions
- [ ] Domain and SSL certificates ready
- [ ] Terraform state bucket created
- [ ] ECR repository initialized
- [ ] Secrets Manager configured

### ✅ Application Prerequisites
- [ ] All V2 system prompts implemented
- [ ] LangChain compatibility issues resolved
- [ ] Unified adapter layer functional
- [ ] Integration tests passing
- [ ] Performance benchmarks established

### ✅ Operational Prerequisites
- [ ] Monitoring and alerting configured
- [ ] Rollback procedures documented
- [ ] Communication plan ready
- [ ] Support team on standby

## Migration Phases

### Phase 1: Infrastructure Setup (Day 1)

#### 1.1 Environment Preparation
```bash
# Create Terraform workspace
cd infrastructure/terraform
terraform workspace select -or-create dev

# Initialize infrastructure
terraform init
terraform plan -var-file="dev.tfvars"
terraform apply -var-file="dev.tfvars"
```

#### 1.2 Initial Deployment
```bash
# Deploy to development environment
git tag v1.0.0-dev
git push origin v1.0.0-dev

# Monitor deployment
watch kubectl get pods -n raptorflow-dev
```

#### 1.3 Smoke Tests
```bash
# Health checks
curl -f https://dev-api.raptorflow.in/health
curl -f https://dev-api.raptorflow.in/v3/agents

# Basic functionality tests
curl -X POST https://dev-api.raptorflow.in/api/icps \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -d '{"goal": "test icp creation"}'
```

### Phase 2: Traffic Migration (Day 2-3)

#### 2.1 Blue-Green Deployment Strategy

**Stage 1: 10% Traffic (2 hours)**
```bash
# Update ALB weights
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions '[
    {"Type": "forward", "Order": 1, "ForwardConfig": {
      "TargetGroups": [
        {"TargetGroupArn": "'$V1_TG'", "Weight": 90},
        {"TargetGroupArn": "'$UNIFIED_TG'", "Weight": 10}
      ]
    }}
  ]'
```

**Monitoring Commands:**
```bash
# Error rates
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name HTTPCode_Target_5XX_Count \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Response times
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

**Stage 2: 50% Traffic (4 hours)**
```bash
# Increase unified system traffic
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions '[...weight 50/50...]'
```

**Stage 3: 100% Traffic (Immediate)**
```bash
# Full cutover
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions '[...weight 0/100...]'
```

#### 2.2 Rollback Procedures

**Immediate Rollback (< 5 minutes):**
```bash
# Switch all traffic back to V1
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions '[...weight 100/0...]'
```

**Full Rollback (< 15 minutes):**
```bash
# Scale down unified system
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service unified-orchestrator \
  --desired-count 0

# Scale up V1 system
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service v1-agents \
  --desired-count 5
```

### Phase 3: Validation & Optimization (Day 4-5)

#### 3.1 Performance Validation
```bash
# Load testing
ab -n 1000 -c 10 https://api.raptorflow.in/v3/execute

# Compare metrics
# Response time: < 2s P95
# Error rate: < 1%
# CPU usage: < 70%
# Memory usage: < 80%
```

#### 3.2 Feature Parity Check
- [ ] All V1 APIs functional through unified system
- [ ] V2 advanced features accessible
- [ ] Cross-system orchestration working
- [ ] Context sharing operational

#### 3.3 Cost Optimization
```bash
# Enable auto-scaling
aws application-autoscaling put-scaling-policy \
  --policy-name "cpu-scaling" \
  --resource-id service/$CLUSTER_NAME/$SERVICE_NAME \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    }
  }'
```

### Phase 4: Production Stabilization (Week 2)

#### 4.1 Monitoring Setup
```bash
# Create CloudWatch dashboards
aws cloudwatch put-dashboard \
  --dashboard-name "RaptorFlow-Unified" \
  --dashboard-body file://monitoring/dashboard.json

# Set up alerts
aws cloudwatch put-metric-alarm \
  --alarm-name "HighErrorRate" \
  --alarm-description "Error rate above 5%" \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

#### 4.2 Documentation Update
- [ ] API documentation updated
- [ ] Developer onboarding guides
- [ ] Operational runbooks
- [ ] Troubleshooting guides

## Success Criteria

### Technical Metrics
- ✅ **Availability**: 99.9% uptime
- ✅ **Performance**: P95 response time < 2 seconds
- ✅ **Reliability**: Error rate < 1%
- ✅ **Scalability**: Auto-scaling working
- ✅ **Security**: No security incidents

### Business Metrics
- ✅ **Functionality**: All features working
- ✅ **Compatibility**: V1 APIs still functional
- ✅ **Innovation**: V2 features accessible
- ✅ **Cost**: Within budget projections

## Emergency Procedures

### Critical Incident Response
1. **Assess Impact**: Determine scope and severity
2. **Notify Stakeholders**: Alert relevant teams
3. **Initiate Rollback**: Use automated rollback procedures
4. **Investigate Root Cause**: Post-mortem analysis
5. **Implement Fixes**: Apply permanent solutions

### Communication Templates

**Internal Alert:**
```
🚨 CRITICAL: RaptorFlow Migration Issue
Status: Investigating
Impact: [High/Medium/Low]
ETA: [Time estimate]
Next Update: [Time]
```

**Customer Communication:**
```
📢 Service Update: We're experiencing temporary issues with some features.
Status: Investigating
ETA: [Time estimate]
We're working to resolve this quickly.
```

## Post-Migration Activities

### Week 3: Optimization
- [ ] Performance tuning
- [ ] Cost optimization
- [ ] Feature enhancements
- [ ] Documentation completion

### Week 4: Handover
- [ ] Team training completed
- [ ] Runbooks finalized
- [ ] Support procedures documented
- [ ] Knowledge transfer complete

## Risk Assessment

### High Risk Items
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data corruption | Critical | Low | Comprehensive testing, backups |
| Performance degradation | High | Medium | Load testing, monitoring |
| Security vulnerabilities | Critical | Low | Security reviews, scanning |
| Feature regressions | High | Medium | Automated testing, manual QA |

### Contingency Plans
- **Full Rollback**: Complete reversion to V1 system
- **Partial Rollback**: Selective feature disablement
- **Traffic Shaping**: Gradual traffic adjustments
- **Circuit Breakers**: Automatic failure isolation

## Contact Information

### Technical Leads
- **Infrastructure**: [Name] - [Contact]
- **Backend**: [Name] - [Contact]
- **DevOps**: [Name] - [Contact]

### Support Teams
- **24/7 On-call**: [Phone] - [Email]
- **Development**: [Slack Channel]
- **Infrastructure**: [Slack Channel]

---

**Migration Commander**: [Name]
**Date**: [Date]
**Version**: 1.0


