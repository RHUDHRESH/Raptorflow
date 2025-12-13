# RaptorFlow AWS Infrastructure

This directory contains the Terraform infrastructure code for deploying RaptorFlow to AWS using ECS/Fargate.

## Architecture

- **ECS/Fargate**: Serverless container orchestration
- **Application Load Balancer**: Traffic distribution and SSL termination
- **Secrets Manager**: Secure credential storage
- **CloudWatch**: Monitoring, logging, and alerting
- **ECR**: Container registry
- **VPC**: Isolated network with private subnets

## Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **Terraform 1.0+** installed
3. **Docker** for building container images
4. **AWS account** with necessary permissions

### Required AWS Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:*",
        "ecr:*",
        "iam:*",
        "secretsmanager:*",
        "ssm:*",
        "logs:*",
        "elasticloadbalancing:*",
        "ec2:*",
        "application-autoscaling:*",
        "cloudwatch:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## Quick Start

### 1. Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Plan Deployment

```bash
terraform plan
```

### 4. Deploy Infrastructure

```bash
terraform apply
```

### 5. Build and Push Container Image

```bash
# Get ECR repository URL
ECR_URL=$(terraform output -raw ecr_repository_url)

# Build and push image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URL
docker build -t raptorflow-backend ../backend
docker tag raptorflow-backend:latest $ECR_URL:latest
docker push $ECR_URL:latest
```

### 6. Update ECS Service

```bash
# Force deployment with new image
aws ecs update-service \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service raptorflow-backend-dev \
  --force-new-deployment
```

## Configuration

### Environment Variables

Store sensitive configuration in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name raptorflow/dev/app \
  --secret-string '{
    "SUPABASE_URL": "https://your-project.supabase.co",
    "SUPABASE_SERVICE_ROLE_KEY": "your-key",
    "GOOGLE_CLOUD_PROJECT_ID": "your-gcp-project"
  }'
```

### Scaling Configuration

```hcl
# Example autoscaling based on CPU/memory
resource "aws_appautoscaling_policy" "cpu_scaling" {
  policy_type = "TargetTrackingScaling"

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
```

## Monitoring

### CloudWatch Metrics

- **ECS Metrics**: CPU/Memory utilization, task count
- **ALB Metrics**: Request count, latency, error rates
- **Custom Metrics**: Agent performance, token usage, cache hits

### Logs

- **ECS Logs**: Application logs in CloudWatch Logs
- **ALB Logs**: Access logs for request analysis
- **VPC Flow Logs**: Network traffic monitoring

## Cost Optimization

### Strategies

1. **Fargate Spot**: Use spot instances for dev/staging
2. **Right-sizing**: Monitor and adjust CPU/memory allocation
3. **Auto-scaling**: Scale based on actual load
4. **Log retention**: Shorter retention for dev environments

### Cost Monitoring

```bash
# Get cost allocation tags
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --metrics "BlendedCost" \
  --group-by Type=TAG,Key=Project
```

## Security

### Network Security

- **VPC Isolation**: Private subnets for ECS tasks
- **Security Groups**: Minimal required access
- **Secrets Manager**: Encrypted credential storage
- **IAM Roles**: Least privilege access

### Compliance

- **Encryption**: Data encrypted at rest and in transit
- **Access Control**: IAM policies and resource policies
- **Audit Logging**: CloudTrail for API activity
- **Vulnerability Scanning**: ECR image scanning enabled

## Troubleshooting

### Common Issues

1. **Task fails to start**: Check CloudWatch logs for application errors
2. **Health check fails**: Verify `/health` endpoint implementation
3. **Secrets access denied**: Ensure IAM permissions for Secrets Manager
4. **Image pull fails**: Check ECR permissions and image existence

### Debugging Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster raptorflow-dev --services raptorflow-backend-dev

# View task logs
aws logs tail /ecs/raptorflow-dev --follow

# Check ALB target health
aws elbv2 describe-target-health --target-group-arn $TARGET_GROUP_ARN
```

## CI/CD Integration

Use GitHub Actions for automated deployments:

```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2
      - name: Terraform Apply
        run: terraform apply -auto-approve
```

## Backup and Recovery

- **State Management**: S3 backend with DynamoDB locking
- **Container Images**: ECR with lifecycle policies
- **Logs**: CloudWatch retention policies
- **Secrets**: Secrets Manager automatic backup

## Support

For issues with this infrastructure:

1. Check CloudWatch logs
2. Review Terraform state: `terraform show`
3. Validate AWS permissions
4. Check AWS service limits


