# CI/CD Setup Guide

This document outlines the comprehensive CI/CD pipeline for the RaptorFlow Muse system.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Actions │    │   AWS Services   │    │  Monitoring     │
│                 │    │                 │    │                 │
│ • CI Pipeline   │───▶│ • ECS/Fargate   │───▶│ • CloudWatch    │
│ • CD Pipeline   │    │ • RDS Postgres  │    │ • X-Ray         │
│ • Security      │    │ • ElastiCache    │    │ • Alarms        │
│ • Testing       │    │ • S3 Assets     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 CI Pipeline

### Triggers
- **Push to main/develop**: Full CI pipeline
- **Pull requests**: Full validation without deployment
- **Manual dispatch**: Custom deployments

### Stages

#### 1. Code Quality (`quality-check`)
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting validation
- **TypeScript**: Type checking for both frontend and backend
- **Terraform**: Infrastructure code validation

#### 2. Unit Tests (`unit-tests`)
- **Frontend**: Vitest with coverage
- **Backend**: Vitest with coverage
- **Database**: PostgreSQL test instance
- **Redis**: Redis test instance

#### 3. Integration Tests (`integration-tests`)
- **API Tests**: End-to-end orchestrator flows
- **Database Integration**: Supabase migrations
- **External Services**: S3, Redis, PostgreSQL

#### 4. Build (`build`)
- **Frontend**: Vite production build
- **Backend**: TypeScript compilation
- **Docker Images**: Multi-stage builds
- **Artifact Storage**: GitHub artifact uploads

#### 5. Security Scan (`security-scan`)
- **NPM Audit**: Dependency vulnerability scanning
- **CodeQL**: Static application security testing (SAST)
- **Checkov**: Infrastructure as Code security scanning
- **Snyk**: Container and dependency scanning

#### 6. Infrastructure Validation (`terraform-validate`)
- **Terraform Format**: Code formatting
- **Terraform Validate**: Syntax and logic validation
- **Terraform Plan**: Change preview (PRs only)

#### 7. Performance Testing (`performance-test`)
- **Lighthouse CI**: Frontend performance metrics
- **Load Testing**: API response time validation
- **Bundle Analysis**: JavaScript bundle size monitoring

## 🚢 CD Pipelines

### Staging Deployment (`deploy-staging.yml`)

**Trigger**: Push to `develop` branch

**Stages**:
1. **Infrastructure Deployment**
   - Terraform apply to staging environment
   - Database migration with backup
   - Service discovery updates

2. **Application Deployment**
   - Backend: ECS blue-green deployment
   - Frontend: Vercel preview deployment
   - Health checks and validation

3. **Post-Deployment Testing**
   - Smoke tests against staging URLs
   - API functionality validation
   - Performance regression checks

### Production Deployment (`deploy-production.yml`)

**Trigger**: Push to `main` branch or manual dispatch

**Enhanced Features**:
- **Pre-flight checks**: Environment validation
- **Database backups**: Automatic backup before migrations
- **Rollback planning**: Automated rollback documentation
- **Production smoke tests**: Critical path validation
- **Security headers**: Production security validation
- **Performance monitoring**: Response time validation

## 🔧 Configuration

### Required Secrets

```bash
# AWS
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
TF_STATE_BUCKET

# Database
DB_PASSWORD_STAGING
DB_PASSWORD_PRODUCTION
REDIS_AUTH_TOKEN_STAGING
REDIS_AUTH_TOKEN_PRODUCTION

# Supabase
SUPABASE_ACCESS_TOKEN
SUPABASE_PROJECT_REF_STAGING
SUPABASE_PROJECT_REF_PRODUCTION

# Vercel
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID_STAGING
VERCEL_PROJECT_ID_PRODUCTION

# Slack Notifications
SLACK_WEBHOOK_URL

# Health Checks
HEALTH_CHECK_TOKEN
```

### Environment Variables

#### Staging
```bash
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=xxx
VITE_API_URL=https://api-staging.raptorflow.dev
AWS_S3_BUCKET=raptorflow-staging-assets
```

#### Production
```bash
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=xxx
VITE_API_URL=https://api.raptorflow.dev
AWS_S3_BUCKET=raptorflow-production-assets
```

## 🏃‍♂️ Local Development

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Run tests
docker-compose exec backend npm test

# Stop services
docker-compose down
```

### Health Checks

```bash
# Run comprehensive health check
npm run health-check

# JSON output for CI/CD
npm run health-check:json
```

## 📊 Monitoring & Alerting

### CloudWatch Dashboards

- **API Performance**: Response times, error rates, throughput
- **Infrastructure**: CPU, memory, disk usage
- **Database**: Connections, query performance
- **Queues**: SQS depth, processing rates

### Alerts

- **API Errors**: 5XX errors > 5 in 5 minutes
- **High CPU**: ECS CPU > 80% for 10 minutes
- **Database Issues**: High connection count
- **Queue Backlog**: SQS messages > 100

### X-Ray Tracing

- **API Gateway**: Request tracing
- **ECS Services**: Application performance
- **Database Calls**: Query performance
- **External APIs**: Third-party service calls

## 🔄 Rollback Procedures

### Automatic Rollback

```bash
# ECS rollback
aws ecs update-service \
  --cluster production-cluster \
  --service raptorflow-backend \
  --task-definition previous-task-definition-arn \
  --force-new-deployment
```

### Database Rollback

```bash
# Supabase rollback
supabase db reset --project-ref xxx
# Restore from backup if needed
```

### Frontend Rollback

```bash
# Vercel rollback
vercel --prod --yes
```

## 🧪 Testing Strategy

### Unit Tests
```bash
# Frontend
npm run test:unit

# Backend
cd backend && npm run test
```

### Integration Tests
```bash
# Full integration suite
cd backend && npm run test:orchestrator
```

### End-to-End Tests
```bash
# Playwright E2E
npm run test:e2e

# Production smoke tests
npm run test:production
```

### Performance Tests
```bash
# Lighthouse CI
npm run lighthouse
```

## 🔐 Security

### Code Security
- **SAST**: CodeQL static analysis
- **Dependency Scanning**: Snyk and NPM audit
- **Container Security**: Trivy image scanning

### Infrastructure Security
- **Checkov**: Terraform security validation
- **AWS Config**: Resource compliance
- **VPC Security**: Network isolation

### Runtime Security
- **AWS WAF**: Web application firewall
- **AWS Shield**: DDoS protection
- **AWS GuardDuty**: Threat detection

## 📈 Metrics & KPIs

### Deployment Metrics
- **Deployment Frequency**: Daily deployments to staging
- **Lead Time**: < 15 minutes from commit to production
- **Change Failure Rate**: < 5%
- **MTTR**: < 30 minutes

### Application Metrics
- **Availability**: 99.9% uptime
- **Performance**: < 2s API response time
- **Error Rate**: < 0.1% 5XX errors
- **User Satisfaction**: > 95% based on feedback

## 🔄 Maintenance

### Regular Tasks
- **Dependency Updates**: Weekly via Dependabot
- **Security Patches**: Immediate via automated PRs
- **Infrastructure Updates**: Monthly Terraform updates
- **Performance Reviews**: Bi-weekly Lighthouse audits

### Emergency Procedures
1. **Alert Response**: Slack notifications to on-call team
2. **Incident Response**: Follow defined runbooks
3. **Communication**: Status page updates
4. **Post-mortem**: Retrospective and improvements

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS ECS Deployment Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment.html)
- [Terraform Best Practices](https://www.terraform.io/docs/language/modules/develop/index.html)
- [Supabase Deployment](https://supabase.com/docs/guides/cli)
- [Vercel Deployment](https://vercel.com/docs/deployments/overview)

