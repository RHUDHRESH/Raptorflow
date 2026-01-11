# RaptorFlow Backend Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying RaptorFlow Backend in various environments, from local development to production deployments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [GCP Cloud Run Deployment](#gcp-cloud-run-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Configuration](#security-configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Node.js**: 16.0 or higher (for frontend)
- **Docker**: 20.10 or higher
- **Git**: 2.30 or higher

### Cloud Provider Accounts

- **Google Cloud Platform**: For production deployment
- **GitHub**: For source code management and CI/CD
- **Docker Hub**: For container registry (optional)

### Required Services

- **PostgreSQL**: 15 or higher
- **Redis**: 7.0 or higher
- **Supabase**: For database and authentication (optional)

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/raptorflow-dev/Raptorflow.git
cd Raptorflow/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### 4. Environment Variables

Create environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/raptorflow_dev
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=raptorflow_dev

# Redis
UPSTASH_REDIS_URL=redis://localhost:6379/raptorflow_dev
UPSTASH_REDIS_TOKEN=your-redis-token

# Google Cloud Platform
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1
GCP_ZONE=us-central1-c

# Vertex AI
VERTEX_AI_PROJECT_ID=your-vertex-ai-project-id

# Webhooks
WEBHOOK_SECRET=your-webhook-secret

# Monitoring
LOG_LEVEL=INFO
METRICS_ENABLED=true
```

## Local Development

### 1. Start Database Services

Using Docker Compose:

```bash
docker-compose -f docker-compose.dev.yml up -d postgres redis
```

Or install locally:

```bash
# PostgreSQL
brew install postgresql  # macOS
sudo apt-get install postgresql  # Ubuntu

# Redis
brew install redis  # macOS
sudo apt-get install redis-server  # Ubuntu
```

### 2. Initialize Database

```bash
python apply_migrations.py
python create_tables.py
```

### 3. Start Application

```bash
python main.py
```

The application will be available at `http://localhost:8000`

### 4. Verify Setup

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "memory": {"status": "healthy"},
    "cognitive": {"status": "healthy"}
  }
}
```

## Docker Deployment

### 1. Build Docker Image

```bash
docker build -t raptorflow-backend .
```

### 2. Development Deployment

```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 3. Production Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Docker Compose Configuration

#### Development (`docker-compose.dev.yml`)

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=postgresql://postgres:5432/raptorflow_dev
      - UPSTASH_REDIS_URL=redis://redis:6379/raptorflow_dev
    volumes:
      - .:/app
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=raptorflow_dev
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

#### Production (`docker-compose.prod.yml`)

```yaml
version: '3.8'

services:
  backend:
    image: raptorflow-backend:latest
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - UPSTASH_REDIS_URL=${UPSTASH_REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
    restart_policy:
      condition: on-failure
      delay: 5s
      max_attempts: 3
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart_policy:
      condition: on-failure
      delay: 5s
      max_attempts: 3

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart_policy:
      condition: on-failure
      delay: 5s
      max_attempts: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart_policy:
      condition: on-failure
      delay: 5s
      max_attempts: 3

volumes:
  postgres_data:
  redis_data:
```

## GCP Cloud Run Deployment

### 1. Prerequisites

- Google Cloud SDK installed and configured
- GCP project created
- Required APIs enabled:
  - Cloud Run API
  - Cloud Build API
  - Artifact Registry API
  - Cloud SQL API
  - Secret Manager API

### 2. Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 3. Create Artifact Registry

```bash
gcloud artifacts repositories create raptorflow-backend \
  --repository-format=docker \
  --location=us-central1
```

### 4. Build and Push Image

```bash
# Build image
gcloud builds submit --tag us-central1-docker.pkg.dev/PROJECT_ID/raptorflow-backend/raptorflow-backend:latest

# Or use Docker
docker build -t us-central1-docker.pkg.dev/PROJECT_ID/raptorflow-backend/raptorflow-backend:latest .
docker push us-central1-docker.pkg.dev/PROJECT_ID/raptorflow-backend/raptorflow-backend:latest
```

### 5. Set Up Database

```bash
# Create Cloud SQL instance
gcloud sql instances create raptorflow-db \
  --database-version=POSTGRES_15 \
  --region=us-central1 \
  --tier=db-custom-4 \
  --storage-size=100GB \
  --storage-type=PD_SSD

# Create database
gcloud sql databases create raptorflow_prod \
  --instance=raptorflow-db \
  --region=us-central1
```

### 6. Set Up Secrets

```bash
# Create secrets
gcloud secrets create raptorflow-prod-secrets \
  --replication-policy=automatic

# Add secret values
echo -n "your-secret-key" | gcloud secrets versions add raptorflow-prod-secrets --data-file=-

# Add other secrets
gcloud secrets versions add raptorflow-prod-secrets --data-file=database_url.txt
gcloud secrets versions add raptorflow-prod-secrets --data-file=redis_token.txt
```

### 7. Deploy to Cloud Run

```bash
gcloud run deploy raptorflow-backend \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/raptorflow-backend/raptorflow-backend:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --port=8000 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=3 \
  --set-env-vars \
    ENVIRONMENT=production \
    SECRET_KEY=raptorflow-prod-secrets \
    DATABASE_URL=raptorflow-prod-secrets \
    UPSTASH_REDIS_URL=raptorflow-prod-secrets \
    UPSTASH_REDIS_TOKEN=raptorflow-prod-secrets \
    VERTEX_AI_PROJECT_ID=PROJECT_ID \
    GCP_PROJECT_ID=PROJECT_ID \
    WEBHOOK_SECRET=raptorflow-prod-secrets \
    ALLOWED_ORIGINS=* \
  --set-cloudsql-instances=PROJECT_ID:us-central1:raptorflow-db \
  --set-secrets=raptorflow-prod-secrets
```

### 8. Configure Traffic Management

```bash
# Set up traffic splitting
gcloud run services update-traffic raptorflow-backend \
  --to-revisions=raptorflow-backend-00001-abc \
  --to-percentages=100

# Add custom domain (optional)
gcloud run domain mappings create \
  --service=raptorflow-backend \
  --domain=api.raptorflow.com
```

### 9. Set Up Monitoring

```bash
# Create monitoring dashboard
gcloud monitoring dashboards create --config-from-file=monitoring/dashboard.json

# Set up alerts
gcloud monitoring policies create --config-from-file=monitoring/alerts.yaml
```

## Kubernetes Deployment

### 1. Prerequisites

- Kubernetes cluster (GKE, EKS, or AKS)
- kubectl configured
- Container registry access

### 2. Create Namespace

```bash
kubectl create namespace raptorflow-prod
kubectl config set-context --current=raptorflow-prod
```

### 3. Create Secrets

```bash
# Create secrets from environment variables
kubectl create secret generic raptorflow-secrets \
  --from-literal=secret-key="$SECRET_KEY" \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=redis-token="$REDIS_TOKEN" \
  --namespace=raptorflow-prod
```

### 4. Deploy Database

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: raptorflow-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: raptorflow_prod
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: raptorflow-prod
spec:
  selector:
    matchLabels:
      app: postgres
  ports:
  - port: 5432
    targetPort: 5432
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: raptorflow-prod
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
```

```bash
kubectl apply -f postgres-deployment.yaml
```

### 5. Deploy Redis

```yaml
# redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: raptorflow-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-storage
          mountPath: /data
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: raptorflow-prod
spec:
  selector:
    matchLabels:
      app: redis
  ports:
  - port: 6379
    targetPort: 6379
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: raptorflow-prod
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

```bash
kubectl apply -f redis-deployment.yaml
```

### 6. Deploy Application

```yaml
# app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: raptorflow-backend
  namespace: raptorflow-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: raptorflow-backend
  template:
    metadata:
      labels:
        app: raptorflow-backend
    spec:
      containers:
      - name: raptorflow-backend
        image: raptorflow-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: raptorflow-secrets
              key: secret-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: raptorflow-secrets
              key: database-url
        - name: UPSTASH_REDIS_URL
          valueFrom:
            secretKeyRef:
              name: raptorflow-secrets
              key: redis-url
        - name: UPSTASH_REDIS_TOKEN
          valueFrom:
            secretKeyRef:
              name: raptorflow-secrets
              key: redis-token
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: raptorflow-backend
  namespace: raptorflow-prod
spec:
  selector:
    matchLabels:
      app: raptorflow-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: raptorflow-backend-hpa
  namespace: raptorflow-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: raptorflow-backend
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

```bash
kubectl apply -f app-deployment.yaml
```

### 7. Configure Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: raptorflow-ingress
  namespace: raptorflow-prod
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.raptorflow.com
    secretName: raptorflow-tls
  rules:
  - host: api.raptorflow.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: raptorflow-backend
            port:
              number: 8000
```

```bash
kubectl apply -f ingress.yaml
```

## CI/CD Pipeline

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=backend --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v4

    - name: Configure gcloud
      uses: google-github-actions/setup-gcloud@v2
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ secrets.GCP_PROJECT_ID }}

    - name: Build and push Docker image
      run: |
        gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/raptorflow-backend:${{ github.sha }}

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy raptorflow-backend \
          --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/raptorflow-backend:${{ github.sha }} \
          --region us-central1 \
          --set-env-vars ENVIRONMENT=production \
          --set-secrets raptorflow-prod-secrets
```

### Environment-Specific Deployments

#### Staging Environment

```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to staging
      run: |
        gcloud run deploy raptorflow-backend-staging \
          --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/raptorflow-backend:latest \
          --region us-central1 \
          --set-env-vars ENVIRONMENT=staging
```

#### Production Environment

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    tags: ['v*']

jobs:
  deploy-production:
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to production
      run: |
        gcloud run deploy raptorflow-backend \
          --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/raptorflow-backend:${{ github.ref_name }} \
          --region us-central1 \
          --set-env-vars ENVIRONMENT=production
```

## Monitoring and Logging

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'raptorflow-backend'
    static_configs:
      - targets: ['raptorflow-backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "RaptorFlow Backend",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(raptorflow_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(raptorflow_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration

```python
# logging_config.py
import logging
import google.cloud.logging
from pythonjsonlogger import jsonlogger

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        google.cloud.logging.handlers.CloudLoggingHandler()
    ]
)

# Configure JSON logging for production
if os.getenv("ENVIRONMENT") == "production":
    logger = logging.getLogger()
    logger.handlers = [
        jsonlogger.JsonFormatter()
    ]
```

## Security Configuration

### SSL/TLS Configuration

#### Nginx Configuration

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name api.raptorflow.com;

    ssl_certificate /etc/nginx/ssl/api.raptorflow.com.crt;
    ssl_certificate_key /etc/nginx/ssl/api.raptorflow.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://raptorflow-backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Security Headers

```python
# security_headers.py
from fastapi import Response

def add_security_headers(response: Response) -> Response:
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

### Rate Limiting

```python
# rate_limiting.py
from slowapi import Limiter, _rate

# Apply rate limiting
@limiter(_rate("100/minute"))
async def protected_endpoint():
    return {"message": "This endpoint is rate limited"}
```

## Troubleshooting

### Common Issues

#### Database Connection Issues

**Problem**: Connection refused or timeout

**Solution**:
1. Check database service status
2. Verify connection string
3. Check firewall rules
4. Validate credentials

```bash
# Check PostgreSQL status
kubectl get pods -l app=postgres
kubectl logs postgres-pod-name

# Test connection
psql -h localhost -U postgres -d raptorflow_prod
```

#### Redis Connection Issues

**Problem**: Redis connection failed

**Solution**:
1. Check Redis service status
2. Verify Redis URL format
3. Check network connectivity

```bash
# Check Redis status
kubectl get pods -l app=redis
kubectl logs redis-pod-name

# Test connection
redis-cli ping
```

#### Memory Issues

**Problem**: High memory usage or OOM errors

**Solution**:
1. Check memory usage
2. Increase memory limits
3. Optimize memory usage
4. Check for memory leaks

```bash
# Check memory usage
kubectl top pods -l app=raptorflow-backend

# Check memory limits
kubectl describe pod pod-name
```

#### Performance Issues

**Problem**: Slow response times

**Solution**:
1. Check resource utilization
2. Analyze slow queries
3. Review agent performance
4. Check network latency

```bash
# Check resource usage
kubectl top pods -l app=raptorflow-backend

# Check database queries
kubectl logs postgres-pod-name | grep "slow query"
```

### Debugging Commands

#### Health Check

```bash
curl http://localhost:8000/health
```

#### Logs

```bash
# Application logs
kubectl logs -f deployment/raptorflow-backend

# Database logs
kubectl logs -f postgres-pod-name

# Redis logs
kubectl logs -f redis-pod-name
```

#### Metrics

```bash
# Check metrics endpoint
curl http://localhost:8000/metrics

# Prometheus metrics
curl http://prometheus:9090/metrics
```

#### Debug Mode

```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG
python main.py
```

### Support Resources

- **Documentation**: https://docs.raptorflow.com
- **GitHub Issues**: https://github.com/raptorflow-dev/Raptorflow/issues
- **Community**: https://discord.gg/raptorflow
- **Email**: support@raptorflow.com

### Getting Help

For deployment issues, please provide:

1. **Environment**: Development, staging, or production
2. **Platform**: Docker, GCP, Kubernetes, etc.
3. **Error Messages**: Full error logs and stack traces
4. **Configuration**: Relevant environment variables
5. **Steps Taken**: What you've already tried

---

This deployment guide covers the most common deployment scenarios for RaptorFlow Backend. For specific use cases or advanced configurations, please refer to the detailed documentation or contact our support team.
