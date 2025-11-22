# RaptorFlow 2.0 - Deployment Guide

Complete guide for deploying RaptorFlow to production environments including Docker and Google Cloud Run.

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Google Cloud Run Deployment](#google-cloud-run-deployment)
5. [Scaling & Performance](#scaling--performance)
6. [Monitoring & Observability](#monitoring--observability)
7. [Troubleshooting](#troubleshooting)

---

## Environment Variables

### Required Variables

Create a `.env` file in the root directory with the following variables:

```bash
# ========== Application Settings ==========
APP_NAME=RaptorFlow
ENVIRONMENT=production  # Options: development, staging, production
DEBUG=false
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32

# ========== Supabase Configuration ==========
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret  # From Supabase project settings

# ========== Google Cloud - Vertex AI ==========
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1  # Or your preferred region
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Vertex AI Model Configuration
VERTEX_AI_MODEL_STANDARD=gemini-2.0-flash-exp  # Fast model for standard tasks
VERTEX_AI_MODEL_CREATIVE=gemini-1.5-pro  # Creative tasks (content generation)
VERTEX_AI_MODEL_REASONING=gemini-2.0-flash-thinking-exp  # Reasoning tasks (analysis)

# ========== Redis Configuration ==========
REDIS_URL=redis://localhost:6379/0  # Or redis://your-redis-host:6379/0
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5

# Cache TTL Settings (in seconds)
CACHE_TTL_RESEARCH=604800  # 7 days
CACHE_TTL_PERSONA=2592000  # 30 days
CACHE_TTL_CONTENT=86400     # 24 hours

# ========== External API Keys ==========
# Perplexity (for research and ambient search)
PERPLEXITY_API_KEY=your-perplexity-api-key

# Tavily (alternative research API)
TAVILY_API_KEY=your-tavily-api-key

# OpenAI (for embeddings, optional)
OPENAI_API_KEY=your-openai-api-key

# Anthropic (alternative LLM provider, optional)
ANTHROPIC_API_KEY=your-anthropic-api-key

# ========== Social Media Integrations ==========
# LinkedIn
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret

# Twitter/X
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
TWITTER_BEARER_TOKEN=your-twitter-bearer-token

# ========== Content Generation Tools ==========
# Canva
CANVA_API_KEY=your-canva-api-key

# Image Generation (Stability AI, Midjourney, etc.)
STABILITY_AI_API_KEY=your-stability-ai-key

# ========== Logging & Monitoring ==========
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
STRUCTURED_LOGGING=true

# Sentry (error tracking, optional)
SENTRY_DSN=your-sentry-dsn

# ========== CORS Settings ==========
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
```

### Environment Variable Validation

RaptorFlow validates all required environment variables at startup. If any are missing, the application will fail to start with a clear error message.

---

## Local Development

### Prerequisites

- Python 3.11+
- Redis (local or remote)
- Google Cloud account with Vertex AI enabled
- Supabase project

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/raptorflow.git
   cd raptorflow
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Start Redis (if running locally):**
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:7-alpine

   # Or using Homebrew (macOS)
   brew services start redis
   ```

6. **Run the application:**
   ```bash
   # Development mode with auto-reload
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

   # Or use the main.py entry point
   python -m backend.main
   ```

7. **Access the API:**
   - API Docs: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc
   - Health Check: http://localhost:8000/health

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest backend/tests/test_integration_e2e.py

# Run concurrency tests
pytest backend/tests/test_concurrency_load.py -v

# Run with markers
pytest -m "not slow"
```

---

## Docker Deployment

### Dockerfile

Create a `Dockerfile` in the root directory:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY config/ ./config/

# Create non-root user
RUN useradd -m -u 1000 raptorflow && chown -R raptorflow:raptorflow /app
USER raptorflow

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### docker-compose.yml

For local development with Redis:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    depends_on:
      - redis
    volumes:
      - ./backend:/app/backend
      - ./config:/app/config

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

### Build and Run

```bash
# Build the image
docker build -t raptorflow:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

---

## Google Cloud Run Deployment

### Prerequisites

- Google Cloud project with billing enabled
- Vertex AI API enabled
- Cloud Run API enabled
- Redis instance (Cloud Memorystore or external)
- Google Cloud SDK installed

### Setup

1. **Authenticate with Google Cloud:**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable required APIs:**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable redis.googleapis.com
   ```

3. **Create Redis instance (Cloud Memorystore):**
   ```bash
   gcloud redis instances create raptorflow-redis \
     --size=1 \
     --region=us-central1 \
     --redis-version=redis_7_0 \
     --tier=basic

   # Get connection info
   gcloud redis instances describe raptorflow-redis --region=us-central1
   ```

4. **Build and push Docker image:**
   ```bash
   # Configure Docker for Google Container Registry
   gcloud auth configure-docker

   # Build and tag image
   docker build -t gcr.io/YOUR_PROJECT_ID/raptorflow:latest .

   # Push to GCR
   docker push gcr.io/YOUR_PROJECT_ID/raptorflow:latest
   ```

5. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy raptorflow \
     --image gcr.io/YOUR_PROJECT_ID/raptorflow:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --timeout 300 \
     --concurrency 80 \
     --min-instances 1 \
     --max-instances 10 \
     --set-env-vars "ENVIRONMENT=production,REDIS_URL=redis://REDIS_IP:6379/0" \
     --set-secrets "SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_SERVICE_KEY=SUPABASE_SERVICE_KEY:latest,VERTEX_AI_PROJECT=VERTEX_AI_PROJECT:latest"
   ```

6. **Set up secrets in Secret Manager:**
   ```bash
   # Create secrets
   echo -n "your-supabase-url" | gcloud secrets create SUPABASE_URL --data-file=-
   echo -n "your-service-key" | gcloud secrets create SUPABASE_SERVICE_KEY --data-file=-

   # Grant access to Cloud Run service
   gcloud secrets add-iam-policy-binding SUPABASE_URL \
     --member=serviceAccount:YOUR_SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com \
     --role=roles/secretmanager.secretAccessor
   ```

### Cloud Run Configuration

**Recommended settings for production:**

- **Memory:** 2-4 GiB (depending on load)
- **CPU:** 2-4 vCPUs
- **Concurrency:** 80-100 requests per instance
- **Timeout:** 300 seconds (5 minutes for long-running workflows)
- **Min instances:** 1 (to avoid cold starts)
- **Max instances:** 10-50 (depending on expected traffic)

### Custom Domain

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service raptorflow \
  --domain api.yourdomain.com \
  --region us-central1
```

---

## Scaling & Performance

### Horizontal Scaling

RaptorFlow is designed to scale horizontally. Use these strategies:

1. **Increase Cloud Run instances:**
   - Adjust `--max-instances` based on traffic
   - Use `--min-instances` to keep warm instances

2. **Use Redis for distributed caching:**
   - All instances share the same Redis cache
   - Prevents duplicate expensive LLM calls

3. **Implement task queuing:**
   - Long-running tasks go to Redis queue
   - Background workers process asynchronously

### Vertical Scaling

For high-throughput scenarios:

- **Memory:** Increase to 4-8 GiB for large LLM responses
- **CPU:** 4+ vCPUs for concurrent request handling
- **Concurrency:** Tune based on Redis and Supabase capacity

### Performance Optimization

#### 1. **Redis Configuration**

```bash
# Increase connection pool
REDIS_MAX_CONNECTIONS=100

# Enable persistence
redis-server --appendonly yes --appendfsync everysec
```

#### 2. **Gunicorn Workers (alternative to uvicorn)**

```bash
# Run with Gunicorn for better production performance
gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300 \
  --keep-alive 5
```

#### 3. **Database Optimization**

- Use Supabase connection pooling
- Add indexes on frequently queried fields
- Use materialized views for analytics

#### 4. **LLM Call Optimization**

- **Cache aggressively:** Set appropriate TTLs for research, personas, content
- **Batch requests:** Group multiple LLM calls when possible
- **Use faster models:** Choose `gemini-flash` for non-creative tasks
- **Streaming:** Enable streaming for long-form content

### Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
cat > locustfile.py <<EOF
from locust import HttpUser, task, between

class RaptorFlowUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def execute_workflow(self):
        self.client.post("/api/v1/orchestration/execute", json={
            "goal": "research_only",
            "research_query": "B2B SaaS"
        }, headers={"Authorization": "Bearer YOUR_TOKEN"})
EOF

# Run load test
locust -f locustfile.py --host=https://your-app.run.app
```

---

## Monitoring & Observability

### Logging

RaptorFlow uses structured logging with `structlog`:

```python
# All logs include:
# - correlation_id: Unique per request
# - workspace_id: For multi-tenancy
# - timestamp: ISO 8601 format
# - level: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Metrics

Key metrics to monitor:

- **Latency:** p50, p95, p99 response times
- **Throughput:** Requests per second
- **Error rate:** 4xx and 5xx responses
- **Graph execution time:** Time per domain graph
- **Redis cache hit rate:** Percentage of cached vs. fresh results
- **LLM token usage:** Track costs

### Google Cloud Monitoring

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=raptorflow" --limit 50

# Create uptime check
gcloud monitoring uptime-check-configs create raptorflow-health \
  --display-name="RaptorFlow Health Check" \
  --http-check-path="/health" \
  --period=60 \
  --resource-type=uptime-url \
  --resource-labels=host=your-app.run.app
```

### Sentry Integration (Optional)

```python
# Add to backend/main.py
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    traces_sample_rate=0.1  # 10% of transactions
)

app.add_middleware(SentryAsgiMiddleware)
```

---

## Troubleshooting

### Common Issues

#### 1. **Redis Connection Errors**

```bash
# Error: "Redis cache connection failed"
# Solution: Check Redis URL and firewall rules

# Test Redis connection
redis-cli -h YOUR_REDIS_HOST ping
# Should return: PONG
```

#### 2. **Vertex AI Authentication Errors**

```bash
# Error: "Could not automatically determine credentials"
# Solution: Set GOOGLE_APPLICATION_CREDENTIALS

export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
gcloud auth application-default login
```

#### 3. **Supabase Connection Issues**

```bash
# Error: "Supabase client not initialized"
# Solution: Verify environment variables

# Check Supabase connection
curl -H "apikey: YOUR_ANON_KEY" https://YOUR_PROJECT.supabase.co/rest/v1/
```

#### 4. **Cold Start Latency**

```bash
# Issue: First request takes 10+ seconds
# Solution: Set min-instances > 0

gcloud run services update raptorflow --min-instances=1
```

#### 5. **Memory Limits**

```bash
# Error: "Container instance exceeded memory limits"
# Solution: Increase memory allocation

gcloud run services update raptorflow --memory=4Gi
```

### Debug Mode

Enable debug logging:

```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG

# Restart application
docker-compose restart app
```

### Health Check Endpoint

```bash
# Check system health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "environment": "production",
  "version": "2.0.0",
  "services": {
    "redis": "healthy",
    "supabase": "connected"
  }
}
```

---

## Security Considerations

1. **API Keys:** Store in Secret Manager, never commit to Git
2. **JWT Validation:** Always verify Supabase JWT tokens
3. **CORS:** Configure allowed origins explicitly
4. **Rate Limiting:** Implement per-user rate limits
5. **Input Validation:** All user inputs are validated with Pydantic
6. **Secrets Rotation:** Rotate keys every 90 days

---

## Support

For issues, questions, or contributions:

- **GitHub Issues:** https://github.com/yourusername/raptorflow/issues
- **Documentation:** https://docs.raptorflow.ai
- **Email:** support@raptorflow.ai

---

**Last Updated:** 2024-01-15
**Version:** 2.0.0
