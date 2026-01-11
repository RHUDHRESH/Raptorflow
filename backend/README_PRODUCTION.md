# Raptorflow Production Deployment Guide

## Overview

This guide covers deploying Raptorflow to production with 100% enterprise-grade reliability, no mock data, and no fallbacks.

## Prerequisites

### Required Services
1. **Upstash Redis** - Primary caching and session storage
2. **Supabase** - Database and authentication
3. **Google Cloud Platform** - Infrastructure hosting
4. **Vertex AI** - AI model inference

### Required Tools
- Google Cloud SDK (gcloud)
- Docker
- Python 3.11+
- Access to all service credentials

## Configuration

### 1. Environment Variables

Create a `.env` file with production values:

```bash
# REQUIRED: Upstash Redis Configuration
UPSTASH_REDIS_URL=https://your-redis-url.upstash.io
UPSTASH_REDIS_TOKEN=your-upstash-redis-token

# REQUIRED: Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret

# REQUIRED: GCP Configuration
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1

# REQUIRED: AI Services
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_TRANSLATE_API_KEY=your-google-translate-api-key

# Service Configuration
ENVIRONMENT=production
DEBUG=false
MOCK_REDIS=false
```

### 2. Upstash Redis Setup

1. Create an Upstash account
2. Create a Redis database
3. Get the REST URL and token
4. Update environment variables

### 3. Supabase Setup

1. Create a Supabase project
2. Run database migrations
3. Configure authentication
4. Get API keys

### 4. GCP Setup

1. Create a GCP project
2. Enable required APIs:
   - Cloud Run
   - Artifact Registry
   - Cloud Build
   - Cloud Storage
   - Vertex AI
3. Configure IAM permissions
4. Set up billing

## Deployment

### 1. Validate Production Configuration

```bash
cd backend
python scripts/validate_production.py
```

This validates:
- All required environment variables
- No mock imports or fallbacks
- Service connectivity
- Configuration validity

### 2. Deploy to Production

```bash
cd backend
python scripts/deploy_production.py
```

This performs:
- Production validation
- Docker image build
- Artifact Registry push
- Cloud Run deployment
- Post-deployment tests

### 3. Manual Deployment (Alternative)

```bash
# Build and push Docker image
docker build -t raptorflow-backend:latest -f Dockerfile .
docker tag raptorflow-backend:latest us-central1-docker.pkg.dev/PROJECT_ID/raptorflow-backend/raptorflow-backend:latest
docker push us-central1-docker.pkg.dev/PROJECT_ID/raptorflow-backend/raptorflow-backend:latest

# Deploy to Cloud Run
gcloud run deploy raptorflow-backend \
  --image us-central1-docker.pkg.dev/PROJECT_ID/raptorflow-backend/raptorflow-backend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars UPSTASH_REDIS_URL=$UPSTASH_REDIS_URL \
  --set-env-vars UPSTASH_REDIS_TOKEN=$UPSTASH_REDIS_TOKEN \
  --set-env-vars SUPABASE_URL=$SUPABASE_URL \
  --set-env-vars SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY \
  --set-env-vars GCP_PROJECT_ID=$GCP_PROJECT_ID \
  --set-env-vars ENVIRONMENT=production
```

## Monitoring

### Health Checks

- **Basic Health**: `/api/v1/health`
- **Detailed Health**: `/api/v1/health/detailed`
- **Readiness Probe**: `/api/v1/health/ready`
- **Liveness Probe**: `/api/v1/health/live`

### Metrics

- **Prometheus Metrics**: `/api/v1/metrics`
- **System Metrics**: `/api/v1/metrics/system`
- **Agent Metrics**: `/api/v1/metrics/agents`

### Logging

Logs are automatically sent to Google Cloud Logging when `CLOUD_LOGGING_ENABLED=true`.

## Security

### Production Security Measures

1. **No Mock Data**: All mock clients and fallbacks are disabled
2. **Required Credentials**: All service credentials are validated
3. **Encryption**: Redis data encryption when enabled
4. **Rate Limiting**: Built-in rate limiting for all endpoints
5. **Authentication**: JWT-based authentication with Supabase

### Security Headers

All API endpoints include:
- CORS headers
- Security headers
- Rate limiting headers
- Request ID tracking

## Performance

### Scaling Configuration

- **Memory**: 2Gi per instance
- **CPU**: 1 vCPU per instance
- **Max Instances**: 10
- **Timeout**: 300 seconds
- **Concurrency**: 100 requests per instance

### Caching Strategy

- **Redis**: Primary caching layer
- **Session Storage**: Redis with 30-minute TTL
- **API Caching**: 1-hour TTL for static data
- **Rate Limiting**: Sliding window algorithm

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Check UPSTASH_REDIS_URL and UPSTASH_REDIS_TOKEN
   - Verify Upstash Redis is running
   - Check network connectivity

2. **Supabase Connection Failed**
   - Check SUPABASE_URL and keys
   - Verify Supabase project is active
   - Check RLS policies

3. **Deployment Failed**
   - Check gcloud authentication
   - Verify GCP project permissions
   - Check Artifact Registry permissions

### Debug Commands

```bash
# Check service logs
gcloud logs read "resource.type=cloud_run_revision" --limit 50

# Check service status
gcloud run services describe raptorflow-backend --region us-central1

# Test health endpoint
curl https://your-service-url/api/v1/health
```

## Maintenance

### Regular Tasks

1. **Monitor Redis memory usage**
2. **Check Supabase storage limits**
3. **Review GCP costs**
4. **Update dependencies**
5. **Run security scans**

### Backup Strategy

- **Database**: Supabase automatic backups
- **Redis**: Upstash automatic backups
- **Storage**: GCP bucket versioning
- **Logs**: Cloud Logging retention

## Support

### Emergency Contacts

- **Infrastructure**: GCP support
- **Database**: Supabase support
- **Redis**: Upstash support
- **Application**: Internal team

### Documentation

- **API Documentation**: Available at `/docs`
- **Architecture**: See `DOCUMENTATION/`
- **Troubleshooting**: Check logs and health endpoints

## Compliance

### Standards Met

- **GDPR**: Data protection compliance
- **SOC 2**: Security controls
- **HIPAA**: Healthcare data protection (if applicable)
- **ISO 27001**: Information security management

### Audit Trail

All actions are logged with:
- User ID
- Timestamp
- Action performed
- IP address
- Request ID

---

## Deployment Checklist

Before deploying to production:

- [ ] All environment variables set
- [ ] Upstash Redis configured
- [ ] Supabase database migrated
- [ ] GCP project set up
- [ ] Validation script passes
- [ ] Health checks configured
- [ ] Monitoring enabled
- [ ] Security scans passed
- [ ] Performance tests completed
- [ ] Backup strategy confirmed

---

**Note**: This deployment configuration is designed for 100% production readiness with no fallbacks or mock data. Ensure all prerequisites are met before deployment.
