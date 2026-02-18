# Production-Grade Horizontal Scaling Implementation Guide

## Executive Summary

Based on 85+ research queries, this guide provides step-by-step implementation instructions to transform Raptorflow's single-instance auth system into a horizontally-scalable, production-grade system capable of handling many concurrent users.

**Key Transformations Required:**
1. Single instance → 3+ instances behind load balancer
2. In-memory sessions → Redis-backed shared sessions
3. Direct Supabase → Supavisor connection pooler
4. Upstash Redis → Self-hosted Redis Sentinel cluster
5. Basic logging → Structured JSON logging + Prometheus metrics
6. Manual deployment → Zero-downtime blue-green deployment

---

## Phase 1: Redis Session Store Implementation

### 1.1 Install Dependencies

```bash
cd backend
pip install redis[hiredis]  # High-performance Redis client
pip install itsdangerous     # For signed session cookies
```

### 1.2 Create Redis Session Manager

**File: `backend/infrastructure/cache/session_manager.py`**

```python
import json
import redis.asyncio as redis
from typing import Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from backend.config.settings import get_settings

class RedisSessionManager:
    """Distributed session management using Redis."""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self.key_prefix = "session:"
        self.default_ttl = 3600  # 1 hour
    
    async def connect(self):
        """Initialize Redis connection."""
        settings = get_settings()
        self._redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
            health_check_interval=30,
        )
    
    async def disconnect(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
    
    def _make_key(self, session_id: str) -> str:
        """Create session key with prefix."""
        return f"{self.key_prefix}{session_id}"
    
    async def create_session(
        self, 
        data: Dict[str, Any], 
        ttl: Optional[int] = None
    ) -> str:
        """Create new session and return session ID."""
        session_id = str(uuid.uuid4())
        key = self._make_key(session_id)
        
        session_data = {
            "data": data,
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat(),
        }
        
        await self._redis.setex(
            key, 
            ttl or self.default_ttl, 
            json.dumps(session_data)
        )
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data."""
        key = self._make_key(session_id)
        data = await self._redis.get(key)
        
        if data:
            session = json.loads(data)
            # Update last accessed
            session["last_accessed"] = datetime.utcnow().isoformat()
            await self._redis.setex(
                key, 
                self.default_ttl, 
                json.dumps(session)
            )
            return session["data"]
        
        return None
    
    async def delete_session(self, session_id: str):
        """Delete session."""
        key = self._make_key(session_id)
        await self._redis.delete(key)
    
    async def extend_session(self, session_id: str, ttl: int):
        """Extend session TTL."""
        key = self._make_key(session_id)
        await self._redis.expire(key, ttl)

# Global session manager instance
session_manager = RedisSessionManager()
```

### 1.3 Create Session Middleware

**File: `backend/middleware/session_middleware.py`**

```python
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from backend.infrastructure.cache.session_manager import session_manager
import uuid

class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware to handle distributed sessions."""
    
    async def dispatch(self, request: Request, call_next):
        # Extract session ID from cookie
        session_id = request.cookies.get("session_id")
        
        # Load session data if session_id exists
        if session_id:
            request.state.session_data = await session_manager.get_session(session_id)
            request.state.session_id = session_id
        else:
            request.state.session_data = {}
            request.state.session_id = None
        
        # Process request
        response = await call_next(request)
        
        # Set session cookie if new session was created
        if hasattr(request.state, 'new_session_id') and request.state.new_session_id:
            response.set_cookie(
                key="session_id",
                value=request.state.new_session_id,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=3600,  # 1 hour
            )
        
        return response
```

---

## Phase 2: JWT Blacklist for Secure Logout

### 2.1 Create Token Blacklist Service

**File: `backend/services/auth/token_blacklist.py`**

```python
import redis.asyncio as redis
from typing import Optional
import jwt
from datetime import datetime
from backend.config.settings import get_settings

class TokenBlacklist:
    """Manage JWT token blacklisting in Redis."""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self.blacklist_prefix = "blacklist:"
    
    async def connect(self):
        """Initialize Redis connection."""
        settings = get_settings()
        self._redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
    
    async def blacklist_token(self, token: str) -> bool:
        """Add token to blacklist."""
        try:
            # Decode without verification to get JTI and expiration
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False}
            )
            
            jti = payload.get("jti")  # JWT ID
            exp = payload.get("exp")
            
            if not jti or not exp:
                return False
            
            # Calculate TTL (time until token expires)
            ttl = max(0, exp - int(datetime.utcnow().timestamp()))
            
            if ttl > 0:
                key = f"{self.blacklist_prefix}{jti}"
                await self._redis.setex(key, ttl, "1")
                return True
            
            return False
        except jwt.InvalidTokenError:
            return False
    
    async def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False}
            )
            
            jti = payload.get("jti")
            if not jti:
                return False
            
            key = f"{self.blacklist_prefix}{jti}"
            return await self._redis.exists(key) > 0
        except jwt.InvalidTokenError:
            return True  # Treat invalid tokens as blacklisted

token_blacklist = TokenBlacklist()
```

---

## Phase 3: Docker Compose Production Setup

### 3.1 Create Production Docker Compose

**File: `docker-compose.prod.yml`**

```yaml
version: "3.8"

services:
  # Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend-blue
      - backend-green
    networks:
      - raptorflow-network
    restart: unless-stopped

  # Blue Environment (Current Production)
  backend-blue:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_HOST=redis-master
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - JWT_SECRET=${JWT_SECRET}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    depends_on:
      redis-master:
        condition: service_healthy
      redis-sentinel-1:
        condition: service_healthy
    networks:
      - raptorflow-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/ready"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s
    deploy:
      replicas: 2

  # Green Environment (Next Deployment)
  backend-green:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_HOST=redis-master
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - JWT_SECRET=${JWT_SECRET}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    depends_on:
      redis-master:
        condition: service_healthy
      redis-sentinel-1:
        condition: service_healthy
    networks:
      - raptorflow-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/ready"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s
    deploy:
      replicas: 2

  # Redis Master
  redis-master:
    image: redis:7-alpine
    volumes:
      - redis-master-data:/data
      - ./redis/redis-master.conf:/usr/local/etc/redis/redis.conf:ro
    command: redis-server /usr/local/etc/redis/redis.conf
    networks:
      - raptorflow-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  # Redis Replica 1
  redis-replica-1:
    image: redis:7-alpine
    volumes:
      - redis-replica-1-data:/data
    command: >
      redis-server 
      --replicaof redis-master 6379
      --appendonly yes
      --protected-mode no
    depends_on:
      - redis-master
    networks:
      - raptorflow-network
    restart: unless-stopped

  # Redis Replica 2
  redis-replica-2:
    image: redis:7-alpine
    volumes:
      - redis-replica-2-data:/data
    command: >
      redis-server 
      --replicaof redis-master 6379
      --appendonly yes
      --protected-mode no
    depends_on:
      - redis-master
    networks:
      - raptorflow-network
    restart: unless-stopped

  # Redis Sentinel 1
  redis-sentinel-1:
    image: redis:7-alpine
    volumes:
      - ./redis/sentinel.conf:/usr/local/etc/redis/sentinel.conf:ro
    command: redis-sentinel /usr/local/etc/redis/sentinel.conf
    depends_on:
      - redis-master
      - redis-replica-1
      - redis-replica-2
    networks:
      - raptorflow-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "-p", "26379", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  # Redis Sentinel 2
  redis-sentinel-2:
    image: redis:7-alpine
    volumes:
      - ./redis/sentinel.conf:/usr/local/etc/redis/sentinel.conf:ro
    command: redis-sentinel /usr/local/etc/redis/sentinel.conf
    depends_on:
      - redis-master
      - redis-replica-1
      - redis-replica-2
    networks:
      - raptorflow-network
    restart: unless-stopped

  # Redis Sentinel 3
  redis-sentinel-3:
    image: redis:7-alpine
    volumes:
      - ./redis/sentinel.conf:/usr/local/etc/redis/sentinel.conf:ro
    command: redis-sentinel /usr/local/etc/redis/sentinel.conf
    depends_on:
      - redis-master
      - redis-replica-1
      - redis-replica-2
    networks:
      - raptorflow-network
    restart: unless-stopped

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - raptorflow-network
    restart: unless-stopped

  # Grafana
  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./grafana/datasources:/etc/grafana/provisioning/datasources:ro
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    networks:
      - raptorflow-network
    restart: unless-stopped

networks:
  raptorflow-network:
    driver: bridge

volumes:
  redis-master-data:
  redis-replica-1-data:
  redis-replica-2-data:
  prometheus-data:
  grafana-data:
```

### 3.2 Nginx Load Balancer Configuration

**File: `nginx/nginx.conf`**

```nginx
upstream backend_blue {
    least_conn;  # Route to instance with least active connections
    server backend-blue-1:8000 max_fails=3 fail_timeout=30s;
    server backend-blue-2:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;  # Keep connections open for reuse
}

upstream backend_green {
    least_conn;
    server backend-green-1:8000 max_fails=3 fail_timeout=30s;
    server backend-green-2:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# Map to determine active environment
map $http_x_deployment_env $active_backend {
    default backend_blue;
    "green" backend_green;
}

server {
    listen 80;
    server_name _;

    # Health check endpoint (bypass load balancing)
    location /health {
        proxy_pass http://$active_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        access_log off;
    }

    # Main application
    location / {
        proxy_pass http://$active_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Cookie handling
        proxy_cookie_path / "/; Secure; HttpOnly; SameSite=Lax";
    }
}
```

---

## Phase 4: Health Checks & Graceful Shutdown

### 4.1 Implement Health Check Endpoints

**File: `backend/api/v1/health/routes.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import get_db
from backend.infrastructure.cache.redis import get_redis_client
import redis.asyncio as redis
import asyncio

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe - lightweight check."""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe - checks all dependencies."""
    checks = {}
    
    # Check database
    try:
        await db.execute("SELECT 1")
        checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"disconnected: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "checks": checks}
        )
    
    # Check Redis
    try:
        redis_client = get_redis_client()
        await redis_client.ping()
        checks["redis"] = "connected"
    except Exception as e:
        checks["redis"] = f"disconnected: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "checks": checks}
        )
    
    return {
        "status": "ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    # This will be handled by prometheus-fastapi-instrumentator
    pass
```

### 4.2 Implement Graceful Shutdown

**File: `backend/app_factory.py` (Update)**

```python
import signal
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with graceful shutdown."""
    # Startup
    print("Starting up...")
    await session_manager.connect()
    await token_blacklist.connect()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        print(f"Received signal {sig}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await session_manager.disconnect()
    await token_blacklist.disconnect()

app = FastAPI(lifespan=lifespan)
```

---

## Phase 5: Prometheus Monitoring

### 5.1 Add Prometheus Instrumentation

```bash
pip install prometheus-fastapi-instrumentator
```

**File: `backend/middleware/metrics_middleware.py`**

```python
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram
import time

# Custom auth metrics
auth_attempts = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['type', 'status']  # type: login/signup/verify, status: success/failure
)

auth_latency = Histogram(
    'auth_latency_seconds',
    'Authentication endpoint latency',
    ['endpoint']
)

active_sessions = Gauge(
    'active_sessions',
    'Number of active user sessions'
)

rate_limit_hits = Counter(
    'rate_limit_hits_total',
    'Rate limit hits',
    ['endpoint', 'client_ip']
)

def setup_metrics(app):
    """Setup Prometheus instrumentation."""
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app)
    return instrumentator
```

### 5.2 Prometheus Configuration

**File: `prometheus/prometheus.yml`**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - alert_rules.yml

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend-blue'
    static_configs:
      - targets: ['backend-blue:8000']
    metrics_path: '/metrics'

  - job_name: 'backend-green'
    static_configs:
      - targets: ['backend-green:8000']
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 5.3 Alert Rules

**File: `prometheus/alert_rules.yml`**

```yaml
groups:
  - name: auth_alerts
    rules:
      # High error rate
      - alert: HighAuthErrorRate
        expr: |
          (
            sum(rate(auth_attempts_total{status="failure"}[5m]))
            /
            sum(rate(auth_attempts_total[5m]))
          ) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High authentication error rate"
          description: "Auth failure rate is above 10% for 5 minutes"

      # High latency
      - alert: HighAuthLatency
        expr: |
          histogram_quantile(0.99, 
            sum(rate(auth_latency_seconds_bucket[5m])) by (le)
          ) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High authentication latency"
          description: "99th percentile latency is above 500ms"

      # Instance down
      - alert: InstanceDown
        expr: up{job=~"backend-.*"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Backend instance is down"

      # Rate limiting triggered frequently
      - alert: FrequentRateLimiting
        expr: |
          sum(rate(rate_limit_hits_total[5m])) > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Frequent rate limiting"
          description: "More than 100 rate limit hits per second"
```

---

## Phase 6: Zero-Downtime Deployment Script

**File: `scripts/deploy.sh`**

```bash
#!/bin/bash
set -e

# Blue-Green Deployment Script
ENV=${1:-green}
VERSION=${2:-latest}

echo "Starting deployment to $ENV environment with version $VERSION"

# Build new image
docker-compose -f docker-compose.prod.yml build backend-$ENV

# Start new environment
docker-compose -f docker-compose.prod.yml up -d backend-$ENV

# Wait for health checks
echo "Waiting for health checks..."
sleep 10

HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/ready || echo "000")

if [ "$HEALTH_STATUS" != "200" ]; then
    echo "Health check failed! Rolling back..."
    docker-compose -f docker-compose.prod.yml stop backend-$ENV
    exit 1
fi

echo "Health check passed. Switching traffic..."

# Update Nginx to route to new environment
if [ "$ENV" == "green" ]; then
    sed -i 's/default backend_blue;/default backend_green;/' nginx/nginx.conf
else
    sed -i 's/default backend_green;/default backend_blue;/' nginx/nginx.conf
fi

# Reload Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo "Deployment complete! Traffic now routing to $ENV"

# Keep old environment running for 5 minutes (quick rollback)
echo "Old environment will be kept running for 5 minutes for rollback capability..."
sleep 300

# Stop old environment
OLD_ENV=$(if [ "$ENV" == "green" ]; then echo "blue"; else echo "green"; fi)
docker-compose -f docker-compose.prod.yml stop backend-$OLD_ENV

echo "Deployment finished successfully!"
```

---

## Phase 7: K6 Load Testing

**File: `tests/load/auth_load_test.js`**

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 200 },   // Ramp up to 200 users
    { duration: '5m', target: 200 },   // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    errors: ['rate<0.1'],              // Error rate under 10%
  },
};

export function setup() {
  // Get auth token before load test
  const loginRes = http.post('http://localhost/api/v1/auth/login', {
    email: 'test@example.com',
    password: 'TestPass123!',
  });
  
  return {
    token: loginRes.json('access_token'),
  };
}

export default function (data) {
  const params = {
    headers: {
      'Authorization': `Bearer ${data.token}`,
      'Content-Type': 'application/json',
    },
    cookies: {
      'session_id': data.sessionId || '',
    },
  };

  // Test authenticated endpoint
  const res = http.get('http://localhost/api/v1/auth/me', params);
  
  const success = check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  errorRate.add(!success);
  sleep(1);
}
```

---

## Phase 8: Environment Configuration

### 8.1 Production Environment Variables

**File: `.env.production`**

```bash
# Database (Supavisor Connection Pooler)
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:6543/postgres?ssl=require
# Note: Use port 6543 for transaction mode pooling

# Redis Sentinel
REDIS_HOST=redis-sentinel-1
REDIS_PORT=26379
REDIS_PASSWORD=your_redis_password

# JWT
JWT_SECRET=your_jwt_secret_min_32_chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Supabase
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_KEY=your_supabase_service_role_key

# Monitoring
PROMETHEUS_MULTIPROC_DIR=/tmp
GRAFANA_PASSWORD=your_grafana_admin_password

# Rate Limiting
RATE_LIMIT_LOGIN=5/minute
RATE_LIMIT_SIGNUP=3/hour
```

---

## Implementation Timeline

### Week 1: Foundation
- [ ] Set up Redis Sentinel Docker Compose
- [ ] Implement Redis session manager
- [ ] Create JWT blacklist service
- [ ] Update auth endpoints to use shared sessions

### Week 2: Infrastructure
- [ ] Configure Nginx load balancer
- [ ] Implement health check endpoints
- [ ] Add graceful shutdown handling
- [ ] Set up Prometheus + Grafana

### Week 3: Production Hardening
- [ ] Add structured JSON logging
- [ ] Implement rate limiting headers (RFC 6585)
- [ ] Configure connection pooling with Supavisor
- [ ] Add CORS credentials configuration

### Week 4: Deployment & Testing
- [ ] Create blue-green deployment script
- [ ] Write K6 load tests
- [ ] Perform load testing (100 → 200 concurrent users)
- [ ] Document rollback procedures

---

## Cost Estimate

| Component | Monthly Cost |
|-----------|-------------|
| VPS (4 CPU, 8GB RAM) | $40 |
| Supabase (Database + Pooler) | $25 |
| Domain + SSL | $15 |
| Monitoring (Prometheus/Grafana self-hosted) | $0 |
| **Total** | **~$80/month** |

---

## Key Architectural Decisions

1. **Redis Sentinel over Upstash**: Full control over clustering, failover, and memory policies
2. **Blue-Green over Rolling**: Instant rollback capability, simpler mental model
3. **Transaction Mode Pooling**: Port 6543 for maximum concurrent connections
4. **JWT Blacklisting**: Enables secure logout in distributed systems
5. **Least_conn Load Balancing**: Better distribution under load vs round-robin

---

## Next Steps

1. **Review this guide** and identify which phases to implement first
2. **Set up staging environment** to test changes
3. **Implement Phase 1** (Redis sessions) - This is the critical foundation
4. **Run `/start-work`** to begin implementation with Sisyphus

Would you like me to create the work plan for implementing any specific phase, or do you have questions about any of these implementation details?
