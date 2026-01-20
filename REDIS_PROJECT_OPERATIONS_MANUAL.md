# ⚡ RaptorFlow Redis Operations Manual

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Environment Configuration](#environment-configuration)
4. [Deployment Procedures](#deployment-procedures)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Security Procedures](#security-procedures)
8. [Failover and Recovery](#failover-and-recovery)
9. [Performance Tuning](#performance-optimization)
10. [Emergency Procedures](#emergency-procedures)

---

## System Overview

### Components
- **Upstash Redis**: Managed serverless Redis hosting (primary).
- **Backend Redis Core**: 35+ Python modules managing sessions, cache, and queues.
- **Frontend Redis Client**: Type-safe TypeScript client for browser-side real-time state.
- **Redis Metrics API**: Dedicated endpoints for real-time performance tracking.
- **Admin Dashboard**: Visual monitoring component for operational oversight.

### Key Features
- **Session Persistence**: User state management with 24h sliding TTL.
- **Multi-Tier Caching**: Workspace-isolated caching for core business objects.
- **Distributed Rate Limiting**: Global API protection using sliding-window counters.
- **Job Queuing**: Reliable asynchronous task processing for AI agents.
- **Real-time Sync**: Simulated Pub/Sub for instant UI updates.

---

## Architecture

### Backend Structure
```
backend/redis_core/
├── client.py              # Singleton client wrapper
├── session.py             # Session management logic
├── cache.py               # Namespace-isolated caching
├── rate_limit.py          # Distributed rate limiting
├── queue.py               # Task queue implementation
└── pubsub.py              # Real-time message bus
```

### API Endpoints
```
/api/v1/health/redis       # Connectivity and PING status
/api/v1/admin/redis-metrics # Full performance report
/api/v1/admin/redis-stats   # High-level key statistics
```

---

## Environment Configuration

### Required Environment Variables

#### Core Redis Settings
```bash
UPSTASH_REDIS_URL=https://your-instance.upstash.io
UPSTASH_REDIS_TOKEN=your-rest-token
MOCK_REDIS=false           # Set to true for local dev without internet
```

#### Optimization Settings
```bash
REDIS_DEFAULT_TTL=3600     # Default cache TTL in seconds
REDIS_SESSION_TTL=86400    # Session TTL (24 hours)
REDIS_MAX_CONNECTIONS=50   # Max concurrent HTTP connections
```

---

## Deployment Procedures

### Production Activation
1. **Provision**: Ensure the Upstash Redis database is created in the same region as the compute (e.g., us-central1).
2. **Secrets**: Add `UPSTASH_REDIS_URL` and `UPSTASH_REDIS_TOKEN` to GCP Secret Manager.
3. **Vercel**: Map environment variables in the Vercel dashboard.
4. **Verification**: Run `./backend/tests/integration/test_redis_integration.py` in the CI/CD pipeline.

---

## Monitoring and Maintenance

### Health Check Command
```bash
curl -X GET "$NEXT_PUBLIC_APP_URL/api/v1/health/redis"
```

### Live Metrics Dashboard
Accessed via the Admin UI at `/admin/performance` or directly via:
```bash
curl -X GET "$NEXT_PUBLIC_APP_URL/api/v1/admin/redis-metrics"
```

### Log Analysis
- **Success Patterns**: Look for `Redis HIT` in backend logs.
- **Error Patterns**: Monitor for `Redis connection failed - falling back to Mock Mode`.

---

## Troubleshooting Guide

### Common Issues

#### 1. "Redis connection failed"
**Symptoms**: 500 errors or slow performance (due to DB fallbacks).
**Solutions**:
- Verify `UPSTASH_REDIS_URL` uses `https://` prefix.
- Check if the token has expired in the Upstash console.
- Ensure the network allows egress to Upstash endpoints.

#### 2. "Rate Limit Exceeded" Errors
**Symptoms**: Legitimate users receiving 429 status codes.
**Solutions**:
- Adjust the sliding window in `backend/redis_core/rate_limit_config.py`.
- Clear the specific user's counter: `redis.del("rate:user_id:endpoint")`.

#### 3. Data Inconsistency
**Symptoms**: Users seeing stale data in the dashboard.
**Solutions**:
- Flush the relevant namespace: `redis.del("cache:workspace_id:*")`.
- Verify the TTL is not set too high for volatile data.

---

## Security Procedures

### Key Rotation
1. Generate a new REST token in the Upstash console.
2. Update GCP Secret Manager and Vercel environment variables.
3. Restart the backend services to pick up the new singleton.

### Data Isolation
- **Rule**: Never store cross-tenant data without a `ws:{id}` prefix.
- **Audit**: Periodically scan keys using `SCAN` (in dev) to ensure naming conventions are followed.

---

## Failover and Recovery

### Automated Fallback
The system is designed with **Graceful Degradation**. If Redis is unreachable:
1. An error is logged.
2. The `MockRedisClient` is automatically instantiated.
3. Operations continue using local in-memory storage (RAM).
4. Performance will decrease, but the system remains functional.

### Manual Recovery
```bash
# Force Redis to bypass if persistent issues occur
echo "MOCK_REDIS=true" >> backend/.env.production
```

---

## Performance Tuning

### Cache TTL Strategy
- **Static Config**: 24h+
- **User Profiles**: 30m
- **Campaign Data**: 15m
- **Live Analytics**: 5m

### Connection Optimization
The synchronous `upstash-redis` client uses a connection pool. Ensure `REDIS_MAX_CONNECTIONS` matches the concurrency limits of your serverless environment.

---

## Emergency Procedures

### Service Blackout
1. **Identify**: Check `/api/v1/health/redis`.
2. **Switch**: Toggle `MOCK_REDIS=true` in environment settings.
3. **Notify**: Contact Upstash support if the dashboard shows downtime.
4. **Restore**: Toggle `MOCK_REDIS=false` once connectivity is verified.

---

**Last Updated**: January 20, 2026  
**Version**: 1.0.0  
**Maintainer**: RaptorFlow Performance Team
