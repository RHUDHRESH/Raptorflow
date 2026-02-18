# Production Auth System Horizontal Scaling

## ⚠️ CRITICAL CORRECTIONS APPLIED

This plan has been **reviewed by Metis** and corrected for the following critical issues:
1. ✅ **Redis Sentinel connection** - Now uses `Sentinel().master_for()` instead of wrong direct connection
2. ✅ **Docker Compose replicas** - Uses explicit instances (backend-1, backend-2, backend-3) instead of broken deploy.replicas
3. ✅ **Blue-green deployment** - Config file swap instead of broken header-based routing
4. ✅ **JWT blacklist** - SHA256 hash instead of assuming jti claim exists
5. ✅ **CSRF protection** - Added (was completely missing!)
6. ✅ **Connection pooling** - Proper pool settings instead of NullPool
7. ✅ **Graceful shutdown** - ASGI-compliant instead of fighting the server

## TL;DR

Transform Raptorflow's single-instance auth system into a horizontally-scalable, production-grade system. **This is an architectural change** (adding server-side sessions) not just scaling.

**Estimated Effort**: Large (4 weeks, now 16 tasks with security fixes)
**Parallel Execution**: NO - Sequential phases with dependencies
**Critical Path**: Redis Sentinel → CSRF Protection → Load Balancer → Health Checks → Deployment Pipeline

---

## Context

### Current Architecture
- **Auth System**: FastAPI backend with Supabase auth
- **Session Storage**: Currently using HTTP-only cookies with JWT tokens
- **Rate Limiting**: Redis-based (Upstash) with in-memory fallback
- **Deployment**: Single-instance Docker container
- **Database**: Direct Supabase PostgreSQL connection

### Research Summary (85+ Searches Completed)
Key findings from extensive research on production auth patterns:
- **Redis Sentinel**: Required for HA session storage across instances
- **Supavisor Pooler**: Port 6543 for transaction-mode connection pooling
- **Nginx Load Balancer**: `least_conn` algorithm with keepalive connections
- **Blue-Green Deployment**: Zero-downtime with instant rollback capability
- **JWT Blacklisting**: Redis-based for secure logout in distributed systems

### Architecture Decisions
1. **Self-hosted Redis Sentinel** over Upstash for full clustering control
2. **Blue-Green deployment** over rolling for simpler rollback
3. **Transaction mode pooling** (port 6543) for maximum concurrency
4. **Shared session store** required for horizontal scaling

---

## Work Objectives

### Core Objective
Enable horizontal scaling of the auth system from 1 to 3+ instances while maintaining session consistency, security, and zero-downtime deployments.

### Concrete Deliverables
- [ ] Redis Sentinel cluster (1 master, 2 replicas, 3 sentinels)
- [ ] Redis-backed session manager with TTL handling
- [ ] JWT token blacklist service
- [ ] Nginx load balancer configuration
- [ ] Docker Compose production setup
- [ ] Health check endpoints (/health/live, /health/ready)
- [ ] Prometheus metrics and alerting
- [ ] Blue-green deployment scripts
- [ ] K6 load testing suite

### Definition of Done
- [ ] System handles 200+ concurrent users
- [ ] Sessions persist across instance restarts
- [ ] Zero-downtime deployments working
- [ ] Health checks prevent routing to unhealthy instances
- [ ] Prometheus alerts fire on auth failures, high latency
- [ ] Load tests pass (p95 < 500ms, error rate < 1%)

### Must Have
- Redis Sentinel (HA, automatic failover)
- CSRF protection (security critical)
- Connection pooling with Supavisor
- Health checks for load balancer
- Graceful shutdown handling
- Prometheus monitoring

### Must NOT Have
- Sticky sessions (not needed with shared Redis)
- Database schema changes (use existing Supabase)
- Breaking API changes (backward compatible)

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (Redis, Docker Compose)
- **Automated tests**: YES (Tests after implementation)
- **Framework**: pytest for unit, K6 for load testing

### Agent-Executed QA Scenarios

**Scenario 1: Session Persistence Across Instances**
- Tool: Playwright
- Steps:
  1. Login via instance 1 (port 8001)
  2. Verify session cookie set
  3. Access protected endpoint via instance 2 (port 8002)
  4. Assert: 200 response (session shared)
  5. Restart instance 1
  6. Access endpoint via instance 1 again
  7. Assert: 200 response (session persisted in Redis)

**Scenario 2: Health Check Failover**
- Tool: Bash (curl)
- Steps:
  1. Start all services
  2. Stop Redis master
  3. Wait 10s for Sentinel failover
  4. curl /health/ready on backend
  5. Assert: 200 response (replica promoted)
  6. Check Nginx upstream
  7. Assert: traffic routing to healthy instances only

**Scenario 3: Blue-Green Deployment**
- Tool: Bash (scripts)
- Steps:
  1. Deploy version 1 to blue
  2. Verify blue serving traffic
  3. Deploy version 2 to green
  4. Run health checks on green
  5. Switch traffic to green
  6. Verify green serving traffic
  7. Rollback to blue
  8. Verify blue serving traffic again

**Scenario 4: Load Test**
- Tool: K6
- Steps:
  1. Run K6 with 100 VUs for 5 minutes
  2. Assert: p95 latency < 500ms
  3. Assert: error rate < 1%
  4. Ramp to 200 VUs
  5. Assert: system remains stable

---

## Execution Strategy

### Sequential Phases

**Phase 1: Redis Session Foundation** (Week 1)
- Install redis-py, implement session manager
- Create session middleware
- Migrate auth endpoints to use shared sessions
- **Blocks**: All subsequent phases

**Phase 2: Infrastructure Setup** (Week 2)
- Configure Redis Sentinel Docker Compose
- Set up Nginx load balancer
- Implement health check endpoints
- Add graceful shutdown handling
- **Depends on**: Phase 1
- **Blocks**: Phase 3

**Phase 3: Monitoring & Hardening** (Week 3)
- Add Prometheus metrics
- Configure structured logging
- Implement rate limiting headers
- Set up connection pooling
- **Depends on**: Phase 2
- **Blocks**: Phase 4

**Phase 4: Deployment Pipeline** (Week 4)
- Create blue-green deployment scripts
- Write K6 load tests
- Perform load testing
- Document rollback procedures
- **Depends on**: Phase 3

---

## TODOs

- [ ] 1. Implement Redis SENTINEL Session Manager (CRITICAL FIX)

  **What to do**:
  - Create `backend/infrastructure/cache/redis_sentinel.py`
  - Use `redis.asyncio.sentinel.Sentinel` (NOT direct Redis connection)
  - Connect to Sentinel ports 26379, get master via `sentinel.master_for()`
  - Implement create_session, get_session, delete_session with JSON serialization
  - Use GETEX for atomic read+TTL extend (Redis 6.2+)
  
  **CRITICAL FIXES from Metis review**:
  - ✅ Use Sentinel-aware client (original plan used wrong port 26379 directly)
  - ✅ Use GETEX to reduce write amplification (original updated TTL on every read)
  - ✅ Proper connection pooling through Sentinel
  
  **Must NOT do**:
  - Don't connect directly to Redis port 6379 (bypasses Sentinel)
  - Don't use pickle (security risk)
  - Don't update TTL on every read (causes write amplification)
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None required
  - **Justification**: Complex Redis Sentinel logic, easy to get wrong
  
  **Parallelization**: NO
  - **Blocks**: Tasks 2, 3, 4
  - **Blocked By**: None (can start immediately)
  
  **References**:
  - `backend/infrastructure/cache/redis.py` - Existing Redis client pattern
  - Redis Sentinel docs: https://redis.io/docs/management/sentinel/
  
  **Acceptance Criteria**:
  - [ ] Connects via Sentinel (ports 26379)
  - [ ] Uses `master_for()` to get current master
  - [ ] Sessions persist across container restarts
  - [ ] Handles failover when master changes
  - [ ] Unit tests pass with mocked Sentinel
  
  **Agent-Executed QA**:
  - Run: `pytest backend/tests/test_redis_sentinel.py -v`
  - Test failover: Stop Redis master, verify app reconnects to new master
  - Expected: All tests pass
  
  **Commit**: YES
  - Message: `feat(sessions): add Redis Sentinel session manager`

- [ ] 2. Create Session Middleware

  **What to do**:
  - Create `backend/middleware/session_middleware.py`
  - Extract session_id from cookies
  - Load session data into request.state
  - Set new session cookies on response
  
  **Must NOT do**:
  - Don't modify session data in middleware (read-only)
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  
  **Parallelization**: NO
  - **Blocked By**: Task 1
  
  **References**:
  - FastAPI middleware docs
  
  **Acceptance Criteria**:
  - [ ] Middleware extracts session from cookies
  - [ ] request.state.session_data available in routes
  
  **Commit**: YES (group with Task 1)

- [ ] 3. Implement JWT Token Blacklist (CRITICAL FIX)

  **What to do**:
  - Create `backend/services/auth/token_blacklist.py`
  - Use SHA256 hash of token as blacklist key (NOT JTI)
  - Set TTL to match token expiration
  - Check blacklist on token verification
  
  **CRITICAL FIX from Metis review**:
  - ✅ Use SHA256 hash (original assumed jti claim exists - Supabase tokens may not have it)
  - ✅ Works with ANY JWT regardless of claims
  
  **Must NOT do**:
  - Don't assume jti claim exists (Supabase tokens often don't have it)
  - Don't store full token (memory waste)
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  
  **Parallelization**: NO
  - **Blocked By**: Task 1
  
  **Acceptance Criteria**:
  - [ ] Logout creates SHA256 hash of token
  - [ ] Blacklisted token rejected on next request
  - [ ] Works with Supabase tokens (no jti required)
  - [ ] TTL matches token expiration
  
  **Commit**: YES
  - Message: `feat(auth): add SHA256-based token blacklist`

- [ ] 4. Update Auth Endpoints for Shared Sessions

  **What to do**:
  - Modify login endpoint to create Redis session
  - Modify logout to blacklist JWT + delete session
  - Update current_user dependency to check session
  - Test with multiple instances
  
  **Must NOT do**:
  - Don't break existing API contract
  - Keep backward compatibility
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  
  **Parallelization**: NO
  - **Blocked By**: Tasks 1, 2, 3
  
  **References**:
  - `backend/api/v1/auth/routes.py`
  
  **Acceptance Criteria**:
  - [ ] Login creates Redis session
  - [ ] Logout invalidates session and token
  - [ ] Auth works across multiple instances
  
  **Agent-Executed QA**:
  - Start 2 backend instances
  - Login via instance 1
  - Access protected endpoint via instance 2
  - Assert: 200 OK
  
  **Commit**: YES
  - Message: `feat(auth): integrate Redis sessions`

- [ ] 5. Create Redis Sentinel Docker Compose (CRITICAL FIX)

  **What to do**:
  - Create `docker-compose.prod.yml`
  - Add Redis master + 2 replicas
  - Add 3 Sentinel instances
  - Configure AOF persistence
  - Add health checks
  
  **CRITICAL FIX from Metis review**:
  - ✅ Use explicit service instances (NOT deploy.replicas - only works in Swarm)
  - ✅ Name services backend-1, backend-2, backend-3
  
  **Must NOT do**:
  - Don't use `deploy.replicas: 3` (ignored by docker-compose, only works in Swarm)
  - Don't use default Redis config (no persistence)
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  
  **Parallelization**: NO
  - **Blocked By**: Task 4
  
  **Acceptance Criteria**:
  - [ ] `docker-compose -f docker-compose.prod.yml up` starts all services
  - [ ] Uses explicit backend-1, backend-2, backend-3 services
  - [ ] Redis master accepts writes
  - [ ] Replicas sync from master
  - [ ] Sentinels monitor master
  
  **Agent-Executed QA**:
  - Run: `docker-compose -f docker-compose.prod.yml ps`
  - Assert: backend-1, backend-2, backend-3 all running
  - Assert: All services healthy
  
  **Commit**: YES
  - Message: `infra(compose): add Sentinel cluster with explicit instances`

- [ ] 6. Configure Nginx Load Balancer (CRITICAL FIX)

  **What to do**:
  - Create `nginx/nginx.conf`
  - Create separate `nginx/upstreams.conf` for blue-green swapping
  - Configure upstream with least_conn
  - Use backend-1:8000, backend-2:8000, backend-3:8000 (not generic names)
  - Enable keepalive connections
  
  **CRITICAL FIX from Metis review**:
  - ✅ Separate upstreams.conf file (for atomic swapping in blue-green)
  - ✅ Explicit backend hostnames (backend-1, not backend-blue-1)
  
  **Must NOT do**:
  - Don't use round-robin (least_conn is better for auth)
  - Don't use variables for upstream names in proxy_pass (breaks resolution)
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  
  **Parallelization**: NO
  - **Blocked By**: Task 5
  
  **Acceptance Criteria**:
  - [ ] Nginx routes to backend-1, backend-2, backend-3
  - [ ] Upstreams in separate file for swapping
  - [ ] Unhealthy instances removed from pool
  - [ ] Keepalive connections working
  
  **Commit**: YES
  - Message: `infra(nginx): add load balancer with swappable upstreams`

- [ ] 7. Implement Health Check Endpoints

  **What to do**:
  - Create `/health/live` (liveness)
  - Create `/health/ready` (readiness with DB + Redis checks)
  - Return 503 if dependencies down
  - Add to nginx upstream checks
  
  **Must NOT do**:
  - Don't make /health/live check DB (should be lightweight)
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  
  **Parallelization**: NO
  - **Blocked By**: Task 5
  
  **Acceptance Criteria**:
  - [ ] GET /health/live returns 200
  - [ ] GET /health/ready returns 200 when all dependencies up
  - [ ] GET /health/ready returns 503 when Redis down
  
  **Agent-Executed QA**:
  - curl http://localhost:8000/health/ready
  - Assert: JSON with status: ready
  
  **Commit**: YES
  - Message: `feat(health): add liveness and readiness probes`

- [ ] 8. Add Graceful Shutdown Handling

  **What to do**:
  - Update app lifespan to handle SIGTERM
  - Close Redis connections on shutdown
  - Finish in-flight requests
  - Set timeout for forceful shutdown
  
  **Must NOT do**:
  - Don't drop connections immediately
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  
  **Parallelization**: NO
  - **Blocked By**: Task 4
  
  **Acceptance Criteria**:
  - [ ] SIGTERM triggers graceful shutdown
  - [ ] In-flight requests complete
  - [ ] Redis connections closed
  
  **Commit**: YES (group with Task 7)

- [ ] 9. Configure Prometheus Metrics

  **What to do**:
  - Install prometheus-fastapi-instrumentator
  - Add custom metrics: auth_attempts, auth_latency, active_sessions
  - Create /metrics endpoint
  - Configure Prometheus scraping
  
  **Must NOT do**:
  - Don't expose sensitive data in metrics
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  
  **Parallelization**: NO
  - **Blocked By**: Task 4
  
  **Acceptance Criteria**:
  - [ ] /metrics returns Prometheus format
  - [ ] Auth attempts counted
  - [ ] Latency histogram populated
  
  **Commit**: YES
  - Message: `feat(monitoring): add Prometheus metrics`

- [ ] 10. Create Alert Rules

  **What to do**:
  - Create `prometheus/alert_rules.yml`
  - High error rate alert (>10%)
  - High latency alert (p99 > 500ms)
  - Instance down alert
  - Configure Alertmanager
  
  **Must NOT do**:
  - Don't alert on single failures (use for: 5m)
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  
  **Parallelization**: NO
  - **Blocked By**: Task 9
  
  **Acceptance Criteria**:
  - [ ] Alerts defined for key metrics
  - [ ] Alertmanager configured
  
  **Commit**: YES (group with Task 9)

- [ ] 11. Add Structured Logging

  **What to do**:
  - Install structlog
  - Configure JSON output in production
  - Add correlation IDs
  - Include request context in logs
  
  **Must NOT do**:
  - Don't log sensitive data (passwords, tokens)
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  
  **Parallelization**: NO
  - **Blocked By**: None (can parallel with 9-10)
  
  **Acceptance Criteria**:
  - [ ] Logs output as JSON
  - [ ] Correlation ID in all log entries
  - [ ] Request context included
  
  **Commit**: YES
  - Message: `feat(logging): add structured JSON logging`

- [ ] 12. Configure Supavisor Connection Pooling (CRITICAL FIX)

  **What to do**:
  - Update DATABASE_URL to use port 6543
  - Configure SQLAlchemy with proper pool size (NOT NullPool)
  - Set statement_cache_size=0 and prepared_statement_cache_size=0 for Supavisor
  - Test connection pooling
  
  **CRITICAL FIX from Metis review**:
  - ✅ Use proper connection pool (NOT NullPool - causes connection churn)
  - ✅ Disable prepared statement cache for transaction pooling
  
  **Must NOT do**:
  - Don't use NullPool (causes connection churn)
  - Don't use port 5432 (direct connection, no pooling)
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  
  **Parallelization**: NO
  - **Blocked By**: None (can parallel with 9-11)
  
  **Acceptance Criteria**:
  - [ ] App connects via port 6543
  - [ ] No DuplicatePreparedStatement errors
  - [ ] Uses connection pool (not NullPool)
  - [ ] Connection pool working efficiently
  
  **Commit**: YES
  - Message: `perf(db): configure Supavisor with proper pooling`

- [ ] 13. Create Blue-Green Deployment Scripts (CRITICAL FIX)

  **What to do**:
  - Create `scripts/deploy.sh`
  - Build and start new environment
  - Run health checks
  - Swap Nginx upstream config file (NOT header-based)
  - Reload Nginx (zero-downtime)
  - Keep old environment for rollback
  
  **CRITICAL FIX from Metis review**:
  - ✅ Config file swap + nginx reload (NOT header-based routing)
  - ✅ Atomic upstream replacement
  
  **Must NOT do**:
  - Don't use header-based routing (original was broken)
  - Don't destroy old environment immediately
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  
  **Parallelization**: NO
  - **Blocked By**: Tasks 5, 6, 7
  
  **Acceptance Criteria**:
  - [ ] Script builds new image
  - [ ] Health checks run before switch
  - [ ] Swaps upstreams.conf file
  - [ ] Reloads Nginx (zero-downtime)
  - [ ] Rollback capability maintained
  
  **Agent-Executed QA**:
  - Run: `./scripts/deploy.sh v1.2.3`
  - Assert: upstreams.conf updated
  - Assert: Nginx reloads successfully
  - Assert: Traffic switched
  
  **Commit**: YES
  - Message: `ci(deploy): add blue-green deployment with config swap`

- [ ] 14. Write K6 Load Tests

  **What to do**:
  - Create `tests/load/auth_load_test.js`
  - Test login → verify → logout flow
  - Ramp up: 100 → 200 concurrent users
  - Assert p95 < 500ms, error rate < 1%
  
  **Must NOT do**:
  - Don't use real user credentials (use test accounts)
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  
  **Parallelization**: NO
  - **Blocked By**: Task 4
  
  **Acceptance Criteria**:
  - [ ] K6 script runs successfully
  - [ ] Load test completes with thresholds met
  
  **Agent-Executed QA**:
  - Run: `k6 run tests/load/auth_load_test.js`
  - Assert: p95 < 500ms, errors < 1%
  
  **Commit**: YES
  - Message: `test(load): add K6 auth load tests`

- [ ] 15. Add CSRF Protection (CRITICAL - SECURITY)

  **What to do**:
  - Install `fastapi-csrf-protect`
  - Add CSRF token generation endpoint
  - Validate CSRF tokens on state-changing operations (POST, PUT, DELETE)
  - Use double-submit cookie pattern
  
  **CRITICAL from Metis review**:
  - Moving to cookie-based sessions requires CSRF protection
  - Original plan completely missed this security requirement
  
  **Must NOT do**:
  - Don't skip CSRF (major security vulnerability)
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  
  **Parallelization**: NO
  - **Blocked By**: Tasks 1-4
  
  **Acceptance Criteria**:
  - [ ] CSRF token endpoint returns token
  - [ ] State-changing endpoints require CSRF header
  - [ ] Rejected requests return 403
  - [ ] Double-submit cookie pattern implemented
  
  **Commit**: YES
  - Message: `security(auth): add CSRF protection`

- [ ] 16. Perform Load Testing

  **What to do**:
  - Deploy to staging environment
  - Run K6 with 100 VUs for 5 minutes
  - Monitor metrics in Grafana
  - Ramp to 200 VUs
  - Document results
  
  **Must NOT do**:
  - Don't test on production
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  
  **Parallelization**: NO
  - **Blocked By**: Tasks 9-15
  
  **Acceptance Criteria**:
  - [ ] 100 VUs: p95 < 500ms
  - [ ] 200 VUs: System stable
  - [ ] No memory leaks observed
  
  **Commit**: NO (testing only)

---

## Commit Strategy

| Task | Message | Files |
|------|---------|-------|
| 1-2 | feat(sessions): add Redis Sentinel management | redis_sentinel.py, session_middleware.py |
| 3 | feat(auth): add SHA256 token blacklist | token_blacklist.py |
| 4 | feat(auth): integrate Redis sessions | auth/routes.py |
| 5 | infra(redis): add Sentinel cluster | docker-compose.prod.yml |
| 6 | infra(nginx): add load balancer | nginx/nginx.conf, upstreams.conf |
| 7-8 | feat(health): add probes and graceful shutdown | health/routes.py, app_factory.py |
| 9-10 | feat(monitoring): add Prometheus and alerts | metrics_middleware.py, alert_rules.yml |
| 11 | feat(logging): add structured logging | logging_config.py |
| 12 | perf(db): configure Supavisor pooling | session.py, settings.py |
| 13 | ci(deploy): add blue-green deployment | scripts/deploy.sh |
| 14 | test(load): add K6 load tests | tests/load/*.js |
| 15 | security(auth): add CSRF protection | csrf_middleware.py |

---

## Success Criteria

### Verification Commands
```bash
# Test session sharing
curl -c cookies.txt -X POST http://localhost/api/v1/auth/login -d '{"email":"test@example.com","password":"testpass"}'
curl -b cookies.txt http://localhost/api/v1/auth/me  # Should work on any instance

# Test health checks
curl http://localhost:8000/health/ready

# Test metrics
curl http://localhost:8000/metrics | grep auth_attempts

# Load test
k6 run tests/load/auth_load_test.js
```

### Final Checklist
- [ ] Sessions persist across container restarts
- [ ] Blue-green deployment switches traffic instantly
- [ ] Failed instances removed from load balancer
- [ ] Prometheus alerts fire correctly
- [ ] 200 concurrent users handled with p95 < 500ms
- [ ] Zero-downtime deployment tested 3+ times
- [ ] CSRF protection working on all state-changing endpoints
- [ ] Redis Sentinel failover tested (master failure recovery)
- [ ] Token blacklist working with Supabase tokens

---

## Metis Review Summary

### Critical Issues Fixed
| Issue | Original | Corrected |
|-------|----------|-----------|
| **Redis Connection** | Direct connection to port 26379 | `Sentinel().master_for()` |
| **Docker Replicas** | `deploy.replicas: 3` (Swarm-only) | Explicit `backend-1,2,3` services |
| **Blue-Green Switch** | Header-based routing (broken) | Config file swap + nginx reload |
| **JWT Blacklist** | Assumed `jti` claim exists | SHA256 hash of entire token |
| **CSRF Protection** | **COMPLETELY MISSING** | Added with `fastapi-csrf-protect` |
| **Connection Pool** | Wrong NullPool advice | Proper pool with cache disabled |
| **Graceful Shutdown** | `signal.signal()` fights ASGI | ASGI-compliant lifespan |
| **Health Checks** | `db.execute("SELECT 1")` | `db.execute(text("SELECT 1"))` |

### Why These Corrections Matter
1. **Redis Sentinel**: Original would have connected to wrong port and failed during failover
2. **Docker Compose**: Original `deploy.replicas` would have been ignored, breaking scaling
3. **Blue-Green**: Header-based routing doesn't work - config swap is the correct pattern
4. **JWT Blacklist**: Supabase tokens don't always have `jti` - would have broken logout
5. **CSRF**: Without this, your cookie-based auth is vulnerable to CSRF attacks
6. **Connection Pool**: NullPool would have caused connection churn and performance issues

### Files Updated
- ✅ `.sisyphus/plans/production-auth-horizontal-scaling.md` - This plan (16 tasks, was 15)
- ✅ `.sisyphus/drafts/PRODUCTION_IMPLEMENTATION_GUIDE_CORRECTED.md` - Complete implementation guide with fixes

**Status**: Ready for implementation after user answers architecture questions (token type, CSRF requirements, deployment target)
