# DEPLOYMENT ARCHITECTURE & IMPLEMENTATION TIMELINE

---

## Deployment Architecture

### Docker Configuration

```dockerfile
# backend/Dockerfile
# Multi-stage build for production

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim as production

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 raptorflow
USER raptorflow

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# backend/docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/raptorflow
      - REDIS_URL=redis://redis:6379
      - GCP_PROJECT_ID=${GCP_PROJECT_ID}
      - PHONEPE_CLIENT_ID=${PHONEPE_CLIENT_ID}
      - PHONEPE_CLIENT_SECRET=${PHONEPE_CLIENT_SECRET}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./skills/definitions:/app/skills/definitions:ro
    restart: unless-stopped

  db:
    image: pgvector/pgvector:pg16
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=raptorflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  # Worker for background tasks
  worker:
    build: .
    command: python -m workers.queue
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/raptorflow
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
  redis_data:
```

---

### Google Cloud Run Configuration

```yaml
# deploy/cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: raptorflow-api
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/execution-environment: gen2
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "100"
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/startup-cpu-boost: "true"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      serviceAccountName: raptorflow-api@${PROJECT_ID}.iam.gserviceaccount.com
      containers:
        - image: gcr.io/${PROJECT_ID}/raptorflow-api:latest
          ports:
            - containerPort: 8000
          resources:
            limits:
              cpu: "2"
              memory: "4Gi"
          env:
            - name: ENVIRONMENT
              value: "production"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: database-url
                  key: latest
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: redis-url
                  key: latest
            - name: GCP_PROJECT_ID
              value: ${PROJECT_ID}
          startupProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 30
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            periodSeconds: 30
```

---

### Requirements

```txt
# backend/requirements.txt

# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
asyncpg==0.29.0
sqlalchemy[asyncio]==2.0.25
alembic==1.13.1
pgvector==0.2.4

# Redis
redis[hiredis]==5.0.1

# AI/ML
google-cloud-aiplatform==1.40.0
langchain==0.1.4
langgraph==0.0.20
sentence-transformers==2.3.1
numpy==1.26.3

# Validation
pydantic==2.5.3
pydantic-settings==2.1.0

# HTTP
aiohttp==3.9.1
httpx==0.26.0

# Scraping
beautifulsoup4==4.12.3
playwright==1.41.0

# Templates
jinja2==3.1.3

# Markdown/YAML
python-frontmatter==1.1.0
pyyaml==6.0.1

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Observability
prometheus-client==0.19.0
opentelemetry-api==1.22.0
opentelemetry-sdk==1.22.0
sentry-sdk[fastapi]==1.39.2

# File watching (hot reload)
watchdog==3.0.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0

# Dev
black==23.12.1
ruff==0.1.13
mypy==1.8.0
```

---

## Implementation Timeline

### Phase 1: Foundation Infrastructure (Week 1-2)

**Deliverables:**
- [ ] Project structure setup
- [ ] FastAPI application with middleware
- [ ] PostgreSQL connection with pooling
- [ ] Redis connection with pooling
- [ ] Configuration management (Pydantic settings)
- [ ] Basic authentication (JWT)
- [ ] Health check endpoints
- [ ] Docker setup for local development
- [ ] Database migrations (Alembic)

**Key Files:**
- `main.py`
- `core/config.py`
- `core/database.py`
- `core/redis_client.py`
- `security/auth.py`

---

### Phase 2: Skill Compiler System (Week 3-4)

**Deliverables:**
- [ ] Skill Markdown format specification
- [ ] YAML frontmatter parser
- [ ] Pydantic model generator from schemas
- [ ] Jinja2 template compilation
- [ ] Skill registry with hot-reload
- [ ] Version hashing
- [ ] TypeScript type generator
- [ ] 20 initial skill definitions

**Key Files:**
- `skills/compiler.py`
- `skills/registry.py`
- `skills/codegen.py`
- `skills/definitions/*.md`

---

### Phase 3: Agent Core Engine (Week 5-6)

**Deliverables:**
- [ ] Queen Router implementation
- [ ] SwarmNode executor
- [ ] Tool binding system
- [ ] Model client (Vertex AI)
- [ ] Critic/QA validation
- [ ] Overseer approval
- [ ] Streaming execution
- [ ] Cancellation tokens
- [ ] Circuit breakers
- [ ] Call stack recursion prevention

**Key Files:**
- `agents/queen_router.py`
- `agents/swarm_node.py`
- `agents/critic.py`
- `agents/overseer.py`
- `agents/model_client.py`

---

### Phase 4: Memory & Knowledge Systems (Week 7)

**Deliverables:**
- [ ] Foundation store
- [ ] Vector store (pgvector)
- [ ] Knowledge graph store
- [ ] Conversation memory
- [ ] Memory decay algorithm
- [ ] Context optimization (Lost in Middle fix)
- [ ] Hallucination detection
- [ ] User constitution system

**Key Files:**
- `memory/foundation_store.py`
- `memory/vector_store.py`
- `memory/graph_store.py`
- `memory/conversation.py`
- `cognition/context_manager.py`
- `cognition/hallucination_detector.py`

---

### Phase 5: Tool Registry & Execution (Week 8)

**Deliverables:**
- [ ] Tool decorator system
- [ ] Tool registry
- [ ] Web search tool
- [ ] Generic scraper tool
- [ ] Vision scraper (screenshot-based)
- [ ] Database tools
- [ ] Indian market tools (JustDial, IndiaMART)
- [ ] GST calculator tool
- [ ] Rate limiting per tool
- [ ] Tool sandboxing (future: E2B)

**Key Files:**
- `tools/registry.py`
- `tools/search/web_search.py`
- `tools/scrapers/*.py`
- `tools/indian/*.py`

---

### Phase 6: Product Module Integration (Week 9-10)

**Deliverables:**
- [ ] BlackBox strategy engine
- [ ] Moves generator
- [ ] Campaign planner
- [ ] Muse creative engine
- [ ] Onboarding/Foundation builder
- [ ] ICP generator integration
- [ ] API endpoints for all modules

**Key Files:**
- `products/blackbox/strategy_engine.py`
- `products/moves/move_generator.py`
- `products/campaigns/campaign_planner.py`
- `products/muse/creative_engine.py`
- `api/v1/*.py`

---

### Phase 7: Economics Engine (Week 11)

**Deliverables:**
- [ ] Cost predictor
- [ ] Budget enforcer
- [ ] Semantic cache
- [ ] Usage tracking
- [ ] Anomaly detection
- [ ] Monthly usage reports
- [ ] Budget alerts

**Key Files:**
- `economics/cost_predictor.py`
- `economics/budget_enforcer.py`
- `economics/semantic_cache.py`
- `economics/usage_tracker.py`

---

### Phase 8: Indian Market Integration (Week 12)

**Deliverables:**
- [ ] PhonePe gateway (OAuth, payments, refunds)
- [ ] UPI mandate for subscriptions
- [ ] GST invoice service
- [ ] State code mapping
- [ ] Festival calendar
- [ ] Regional language support (Hindi, Tamil, Telugu)
- [ ] INR pricing tiers
- [ ] Webhook handlers

**Key Files:**
- `indian_market/phonepe_gateway.py`
- `indian_market/gst_service.py`
- `indian_market/festival_calendar.py`
- `indian_market/regional_languages.py`
- `api/webhooks/phonepe.py`

---

### Phase 9: Security & Compliance (Week 13)

**Deliverables:**
- [ ] Input sanitization (prompt injection prevention)
- [ ] PII scanner and masking
- [ ] Secret vault integration
- [ ] Row-level security policies
- [ ] Audit logging
- [ ] Rate limiting
- [ ] API key rotation
- [ ] Webhook signature validation

**Key Files:**
- `security/sanitizer.py`
- `security/pii_scanner.py`
- `security/secret_vault.py`
- `security/audit_logger.py`
- `security/rate_limiter.py`

---

### Phase 10: Observability & Operations (Week 14-15)

**Deliverables:**
- [ ] Event sourcing system
- [ ] Prometheus metrics
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Sentry error tracking
- [ ] Health check endpoints
- [ ] Cloud Run deployment
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Load testing
- [ ] Golden dataset evaluation
- [ ] Documentation

**Key Files:**
- `core/event_store.py`
- `observability/metrics.py`
- `observability/tracing.py`
- `observability/health.py`
- `tests/golden_datasets/*.json`
- `.github/workflows/deploy.yml`

---

## Cost Estimates

### Infrastructure (Monthly)

| Service | Configuration | Cost/Month |
|---------|--------------|------------|
| Cloud Run | 2 vCPU, 4GB RAM, min 1 instance | $150-300 |
| Cloud SQL | db-f1-micro + 10GB | $50-100 |
| Memorystore Redis | 1GB Basic | $35-50 |
| Cloud Storage | 10GB | $5 |
| Vertex AI | Usage-based | Variable |
| **Total Fixed** | | **~$250-450** |

### Per-User Economics

| Metric | Value |
|--------|-------|
| Avg tokens per task | 5,000-10,000 |
| Avg cost per task | $0.01-0.05 |
| Tasks per user per day | 5-15 |
| Monthly cost per active user | $5-15 |

### Break-Even Analysis

| Plan | Price (INR) | Cost/User | Margin |
|------|-------------|-----------|--------|
| Starter | ₹2,999 ($36) | ~$10 | 72% |
| Growth | ₹9,999 ($120) | ~$25 | 79% |
| Agency | ₹24,999 ($300) | ~$50 | 83% |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Latency (P95) | < 5 seconds | Prometheus |
| Cost per Task | < $0.05 | Usage tracking |
| User Acceptance Rate | > 80% first gen | Feedback loop |
| System Uptime | 99.9% | Health checks |
| Concurrent Users | 10,000+ | Load testing |
| Cache Hit Rate | > 30% | Semantic cache metrics |
| Quality Score | > 80 avg | Critic scores |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Model costs explode | Budget caps, semantic caching, model tiering |
| Vertex AI downtime | Model cascade fallback (GPT-4o backup) |
| Scraper IP bans | Rotating proxies, rate limiting |
| Data leaks | RLS, PII scanning, audit logs |
| Prompt injection | Input sanitization, sandboxed execution |
| Recursive agents | Call stack depth limit |
| Cold start latency | Min instances, startup probes |
