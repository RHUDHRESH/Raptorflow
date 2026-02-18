# Production-Grade Authentication System Deployment Plan
## Raptorflow Auth System - High Concurrency Architecture

**Status**: Research Complete (35 comprehensive searches)  
**Goal**: Transform single-instance auth to production-grade multi-user system  
**Estimated Effort**: Large (Multi-phase implementation)  

---

## Executive Summary

Your current auth system works but is designed for single-instance operation. To handle **many concurrent users**, you need architectural changes across these dimensions:

| Area | Current State | Production Requirement |
|------|--------------|----------------------|
| Rate Limiting | In-memory (per instance) | Distributed Redis-based |
| Sessions | In-memory (lost on restart) | Redis with persistence |
| Database | Direct connections | Connection pooling + Supavisor |
| Deployment | Single instance | Horizontal scaling ready |
| Secrets | .env files | Vault/secrets manager |
| Monitoring | Basic | Full observability stack |

---

## Phase 1: Foundation - Distributed State Management

### 1.1 Redis Infrastructure (CRITICAL FIRST STEP)

**Why**: Your current in-memory rate limiting and sessions won't work across multiple instances.

**Architecture**:
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  FastAPI App 1  │────▶│  Redis Cluster  │◄────│  FastAPI App 2  │
│  (Auth Service) │     │   (Sentinel)    │     │  (Auth Service) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         └───────────────────────┴───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Redis Sentinel │
                    │ (High Available)│
                    └─────────────────┘
```

**Implementation**:

1. **Deploy Redis with Sentinel** (for HA):
```yaml
# docker-compose.redis.yml
version: '3.8'
services:
  redis-master:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    
  redis-replica:
    image: redis:7-alpine
    ports:
      - "6380:6379"
    command: redis-server --replicaof redis-master 6379
    
  sentinel:
    image: redis:7-alpine
    command: >
      redis-sentinel /etc/redis/sentinel.conf
      --sentinel monitor mymaster redis-master 6379 2
      --sentinel down-after-milliseconds mymaster 5000
      --sentinel failover-timeout mymaster 60000
      --sentinel parallel-syncs mymaster 1
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf
```

2. **Update Backend Rate Limiter** to use Redis:
```python
# backend/infrastructure/rate_limiting/redis_rate_limiter.py
import redis
import time
from typing import Optional

class RedisRateLimiter:
    """Distributed rate limiter using Redis with sliding window."""
    
    def __init__(self, redis_url: str):
        self._redis = redis.from_url(redis_url, decode_responses=True)
    
    def is_allowed(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check if request is allowed using sliding window.
        Returns: (is_allowed, remaining_requests)
        """
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Remove old entries
        self._redis.zremrangebyscore(key, 0, window_start)
        
        # Count current requests in window
        current_count = self._redis.zcard(key)
        
        if current_count >= max_requests:
            # Get retry after time
            oldest = self._redis.zrange(key, 0, 0, withscores=True)
            retry_after = int(oldest[0][1] + window_seconds - current_time) if oldest else window_seconds
            return False, retry_after
        
        # Add current request
        self._redis.zadd(key, {str(current_time): current_time})
        self._redis.expire(key, window_seconds)
        
        return True, max_requests - current_count - 1
```

3. **Session Storage in Redis**:
```python
# backend/services/auth/session_store.py
import redis
import json
from typing import Optional, Dict, Any

class RedisSessionStore:
    """Store sessions in Redis for horizontal scaling."""
    
    def __init__(self, redis_client: redis.Redis):
        self._redis = redis_client
        self._prefix = "auth:session:"
    
    def store_session(
        self, 
        session_id: str, 
        data: Dict[str, Any], 
        ttl: int = 3600
    ) -> None:
        """Store session with TTL."""
        key = f"{self._prefix}{session_id}"
        self._redis.setex(key, ttl, json.dumps(data))
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session."""
        key = f"{self._prefix}{session_id}"
        data = self._redis.get(key)
        return json.loads(data) if data else None
    
    def delete_session(self, session_id: str) -> None:
        """Delete session (logout)."""
        key = f"{self._prefix}{session_id}"
        self._redis.delete(key)
    
    def extend_session(self, session_id: str, ttl: int = 3600) -> bool:
        """Extend session TTL."""
        key = f"{self._prefix}{session_id}"
        return self._redis.expire(key, ttl)
```

---

## Phase 2: Database Connection Architecture

### 2.1 Supabase Connection Pooling

**Current Issue**: Each FastAPI instance creates direct connections to Supabase.

**Production Solution**: Use Supavisor (Supabase's connection pooler)

**Configuration**:
```python
# backend/config/settings.py updates

# Use Supavisor for connection pooling
SUPABASE_POOLER_URL = os.getenv(
    "SUPABASE_POOLER_URL", 
    "postgres://postgres.vpwwzsanuyhpkvgorcnc:[password]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
)

# For SQLAlchemy with asyncpg
DATABASE_POOL_SIZE = 10
DATABASE_MAX_OVERFLOW = 20
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 1800  # 30 minutes
```

**SQLAlchemy Configuration**:
```python
# backend/infrastructure/database/engine.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Use NullPool with external pooler (Supavisor)
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Supavisor handles pooling
    echo=False,
    connect_args={
        "statement_cache_size": 0,  # Required for pgbouncer
        "prepared_statement_cache_size": 0,
    }
)

async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)
```

**Connection String Strategy**:
- **Transaction Mode** (port 6543): For short-lived requests, auto-scaling
- **Session Mode** (port 5432): For long-running transactions, admin operations

---

## Phase 3: Horizontal Scaling Architecture

### 3.1 Load Balancer Configuration

**Architecture**:
```
                    ┌─────────────────┐
                    │   Nginx / ALB   │
                    │  (Load Balancer)│
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐
     │ FastAPI App 1 │ │FastAPI App2│ │FastAPI   │
     │  (Docker)     │ │  (Docker)  │ │  App 3   │
     └───────┬───────┘ └─────┬──────┘ └────┬─────┘
             │               │             │
             └───────────────┼─────────────┘
                             │
                    ┌────────▼────────┐
                    │   Redis Cluster │
                    │ (Sessions/Cache)│
                    └─────────────────┘
```

**Nginx Configuration**:
```nginx
# nginx.conf
upstream auth_backend {
    least_conn;  # Load balancing method
    server fastapi1:8000 max_fails=3 fail_timeout=30s;
    server fastapi2:8000 max_fails=3 fail_timeout=30s;
    server fastapi3:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;  # Connection pooling
}

server {
    listen 80;
    server_name api.raptorflow.in;
    
    location /api/auth/ {
        proxy_pass http://auth_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # Health check
        health_check interval=5s fails=3 passes=2;
    }
}
```

### 3.2 Docker Compose Production Setup

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - auth1
      - auth2
      - auth3
    restart: unless-stopped
  
  auth1:
    build: .
    environment:
      - AUTH_MODE=supabase
      - REDIS_URL=redis://redis:6379
      - SUPABASE_POOLER_URL=${SUPABASE_POOLER_URL}
    depends_on:
      - redis
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
  
  auth2:
    build: .
    environment:
      - AUTH_MODE=supabase
      - REDIS_URL=redis://redis:6379
      - SUPABASE_POOLER_URL=${SUPABASE_POOLER_URL}
    depends_on:
      - redis
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
  
  auth3:
    build: .
    environment:
      - AUTH_MODE=supabase
      - REDIS_URL=redis://redis:6379
      - SUPABASE_POOLER_URL=${SUPABASE_POOLER_URL}
    depends_on:
      - redis
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
  
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    restart: unless-stopped
  
  redis-sentinel:
    image: redis:7-alpine
    command: >
      redis-sentinel
      --sentinel monitor mymaster redis 6379 2
      --sentinel down-after-milliseconds mymaster 5000
      --sentinel failover-timeout mymaster 60000
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  redis-data:
```

---

## Phase 4: Security & Secrets Management

### 4.1 HashiCorp Vault Integration

**Why**: Environment variables in .env files are not production-grade.

**Architecture**:
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  FastAPI    │────▶│Vault Agent  │────▶│  Vault      │
│  (App)      │     │  (Sidecar)  │     │  (Server)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────▼──────┐
                    │  Env vars   │
                    │  injected   │
                    └─────────────┘
```

**Implementation**:

1. **Vault Setup**:
```bash
# Initialize Vault (one-time)
vault operator init

# Enable KV secrets engine
vault secrets enable -path=secret kv-v2

# Store auth secrets
vault kv put secret/raptorflow/auth \
  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIs..." \
  JWT_SECRET="your-jwt-secret" \
  REDIS_PASSWORD="redis-password"
```

2. **Vault Agent Configuration**:
```hcl
# vault-agent-config.hcl
auto_auth {
  method "kubernetes" {
    mount_path = "auth/kubernetes"
    config = {
      role = "raptorflow-auth"
    }
  }
  sink "file" {
    config = {
      path = "/vault/.vault-token"
    }
  }
}

template {
  destination = "/app/.env"
  contents = <<EOT
{{ with secret "secret/raptorflow/auth" }}
SUPABASE_SERVICE_ROLE_KEY={{ .Data.SUPABASE_SERVICE_ROLE_KEY }}
JWT_SECRET={{ .Data.JWT_SECRET }}
REDIS_PASSWORD={{ .Data.REDIS_PASSWORD }}
{{ end }}
EOT
}
```

3. **Application Integration**:
```python
# backend/config/vault_loader.py
import os
from pathlib import Path

def load_vault_secrets():
    """Load secrets from Vault agent-injected files."""
    vault_env_path = Path("/vault/secrets/.env")
    
    if vault_env_path.exists():
        with open(vault_env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ.setdefault(key, value)
    
    # Fallback to regular env vars for local dev
    return os.environ
```

---

## Phase 5: Observability & Monitoring

### 5.1 Metrics to Track

**Critical Auth Metrics**:
1. **Authentication Success/Failure Rates**
2. **Token Validation Latency (p50, p95, p99)**
3. **Session Duration**
4. **Concurrent Active Sessions**
5. **Rate Limit Hits**
6. **Token Refresh Rate**

**Implementation with Prometheus**:
```python
# backend/infrastructure/metrics/auth_metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Auth metrics
auth_attempts = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['method', 'status']
)

auth_latency = Histogram(
    'auth_latency_seconds',
    'Authentication latency',
    ['method'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

active_sessions = Gauge(
    'auth_active_sessions',
    'Number of active sessions'
)

rate_limit_hits = Counter(
    'auth_rate_limit_hits_total',
    'Total rate limit hits',
    ['endpoint', 'client_ip']
)

# Usage in auth routes
@router.post("/login")
async def login(credentials: LoginRequest):
    with auth_latency.labels(method="login").time():
        result = await authenticate(credentials)
        
        auth_attempts.labels(
            method="login",
            status="success" if result.success else "failure"
        ).inc()
        
        return result
```

### 5.2 Health Checks

**Liveness vs Readiness**:
```python
# backend/api/health/routes.py
from fastapi import APIRouter, Depends, HTTPException
import redis
import httpx

router = APIRouter()

@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe - is the app running?"""
    return {"status": "alive"}

@router.get("/health/ready")
async def readiness_check(
    redis_client: redis.Redis = Depends(get_redis)
):
    """Kubernetes readiness probe - is the app ready to serve traffic?"""
    checks = {
        "redis": False,
        "supabase": False
    }
    
    # Check Redis
    try:
        redis_client.ping()
        checks["redis"] = True
    except Exception:
        pass
    
    # Check Supabase
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/health"
            )
            checks["supabase"] = response.status_code == 200
    except Exception:
        pass
    
    if not all(checks.values()):
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "checks": checks}
        )
    
    return {"status": "ready", "checks": checks}
```

---

## Phase 6: Zero-Downtime Deployment

### 6.1 Blue-Green Deployment Strategy

```
Phase 1: Blue Active          Phase 2: Both Running        Phase 3: Green Active
┌─────────────┐              ┌─────────────┐              ┌─────────────┐
│   LB        │              │   LB        │              │   LB        │
│   (Blue)    │              │ (Split 90/10│              │   (Green)   │
└──────┬──────┘              └──────┬──────┘              └──────┬──────┘
       │                            │                            │
┌──────▼──────┐              ┌──────▼──────┐              ┌──────▼──────┐
│ Blue Stack  │              │ Blue Stack  │              │ Green Stack │
│  (v1.0)     │              │  (v1.0)     │              │  (v1.1)     │
└─────────────┘              └─────────────┘              └─────────────┘
                             ┌─────────────┐              
                             │ Green Stack │              
                             │  (v1.1)     │              
                             └─────────────┘              
```

**Implementation Script**:
```bash
#!/bin/bash
# blue-green-deploy.sh

# Deploy green stack
docker-compose -f docker-compose.green.yml up -d

# Run health checks
until curl -f http://green:8000/health/ready; do
    echo "Waiting for green to be ready..."
    sleep 5
done

# Gradually shift traffic
for split in 10 25 50 75 90 100; do
    echo "Shifting $split% traffic to green"
    update-nginx-config $split
    sleep 60
    
    # Check error rates
    error_rate=$(get_error_rate)
    if (( $(echo "$error_rate > 0.01" | bc -l) )); then
        echo "Error rate too high! Rolling back..."
        update-nginx-config 0
        exit 1
    fi
done

# Decommission blue
docker-compose -f docker-compose.blue.yml down
```

### 6.2 Database Migration Strategy

**Zero-Downtime Migrations**:
1. **Expand Phase**: Add new columns/tables without breaking existing code
2. **Migrate Phase**: Backfill data in background
3. **Contract Phase**: Remove old columns after verification

```python
# Example: Adding a column safely
# Migration 1: Add nullable column
"ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP NULL"

# Migration 2: Backfill data (run in batches)
"UPDATE users SET last_login_at = created_at WHERE last_login_at IS NULL"

# Migration 3: Make non-nullable (after all data migrated)
"ALTER TABLE users ALTER COLUMN last_login_at SET NOT NULL"
```

---

## Phase 7: Testing & Load Testing

### 7.1 Load Testing with K6

```javascript
// load-tests/auth-load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up
    { duration: '5m', target: 100 },   // Steady state
    { duration: '2m', target: 200 },   // Increase load
    { duration: '5m', target: 200 },   // Steady state
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],   // 95% under 500ms
    errors: ['rate<0.01'],               // Error rate < 1%
  },
};

export default function () {
  // Login request
  const loginRes = http.post('http://api.raptorflow.in/api/auth/login', {
    email: 'test@example.com',
    password: 'testpass123',
  });
  
  const loginSuccess = check(loginRes, {
    'login status is 200': (r) => r.status === 200,
    'has access token': (r) => r.json('access_token') !== undefined,
  });
  
  errorRate.add(!loginSuccess);
  
  if (loginSuccess) {
    const token = loginRes.json('access_token');
    
    // Verify token
    const verifyRes = http.post('http://api.raptorflow.in/api/auth/verify', null, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    
    check(verifyRes, {
      'verify status is 200': (r) => r.status === 200,
      'token is valid': (r) => r.json('valid') === true,
    });
  }
  
  sleep(1);
}
```

**Run Load Test**:
```bash
# Install k6
brew install k6

# Run test
k6 run --out influxdb=http://localhost:8086/k6 auth-load-test.js
```

---

## Phase 8: Disaster Recovery

### 8.1 RPO/RTO Targets

| Service | RPO | RTO | Strategy |
|---------|-----|-----|----------|
| Auth Service | 0 (stateless) | 5 min | Auto-scaling groups |
| Redis Sessions | 5 min | 10 min | AOF + RDB persistence |
| Supabase | 1 hour | 4 hours | Point-in-time recovery |
| Secrets | 0 | 15 min | Vault HA cluster |

### 8.2 Backup Strategy

```bash
#!/bin/bash
# backup-auth-data.sh

# Backup Redis sessions
redis-cli BGSAVE
aws s3 cp /data/redis/dump.rdb s3://raptorflow-backups/redis/$(date +%Y%m%d-%H%M%S).rdb

# Export Supabase schema
pg_dump $SUPABASE_DB_URL --schema-only > schema-$(date +%Y%m%d).sql
aws s3 cp schema-*.sql s3://raptorflow-backups/database/

# Backup Vault secrets
vault operator raft snapshot save vault-$(date +%Y%m%d-%H%M%S).snap
aws s3 cp vault-*.snap s3://raptorflow-backups/vault/
```

---

## Implementation Roadmap

### Week 1: Foundation
- [ ] Deploy Redis with Sentinel
- [ ] Implement Redis-based rate limiter
- [ ] Migrate sessions to Redis
- [ ] Test locally with Docker Compose

### Week 2: Database & Pooling
- [ ] Configure Supavisor connection pooling
- [ ] Update SQLAlchemy settings
- [ ] Load test connection pooling
- [ ] Performance benchmarks

### Week 3: Scaling
- [ ] Set up Nginx load balancer
- [ ] Deploy 3 FastAPI instances
- [ ] Configure health checks
- [ ] Implement blue-green deployment

### Week 4: Security & Monitoring
- [ ] Integrate Vault for secrets
- [ ] Set up Prometheus metrics
- [ ] Configure Sentry for errors
- [ ] Create dashboards (Grafana)

### Week 5: Testing & Hardening
- [ ] Run load tests (K6)
- [ ] Penetration testing
- [ ] Disaster recovery drills
- [ ] Documentation

---

## Cost Estimation (Monthly)

| Component | Specs | Cost |
|-----------|-------|------|
| VPS (3x) | 2 vCPU, 4GB RAM | $60 |
| Redis Cluster | 3 nodes | $45 |
| Load Balancer | Nginx (self-hosted) | $0 |
| Supabase | Pro plan | $25 |
| Vault | Self-hosted | $0 |
| Monitoring | Prometheus/Grafana | $0 |
| Backups | S3 storage | $10 |
| **Total** | | **~$140/month** |

---

## Key Takeaways

1. **Redis is Critical**: Without distributed state, you can't scale horizontally
2. **Connection Pooling**: Use Supavisor to handle thousands of connections
3. **Secrets Management**: Move away from .env files to Vault
4. **Health Checks**: Essential for load balancer to know which instances are healthy
5. **Observability**: You can't optimize what you don't measure
6. **Zero-Downtime**: Blue-green deployment prevents user disruption
7. **Load Testing**: Prove your system can handle load before going live

---

## Next Steps

1. Start with **Phase 1** (Redis infrastructure)
2. Run both old and new systems in parallel
3. Gradually migrate traffic
4. Monitor metrics closely
5. Roll back if issues arise

**Need help implementing?** Each phase can be implemented independently. Start with Phase 1 and build incrementally.
