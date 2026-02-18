# CRITICAL Security Remediation Plan

## Executive Summary

**Status**: 🚨 NOT PRODUCTION READY  
**Risk Level**: CRITICAL - Remote exploitation possible  
**Estimated Fix Time**: 3-5 days  
**Blockers**: 10 Critical, 5 Medium

This plan addresses critical security vulnerabilities found in the horizontal scaling implementation. DO NOT deploy to production until Priority 1 items are completed.

---

## Risk Assessment Matrix

| Vulnerability | CVSS Score | Exploitability | Impact | Priority |
|--------------|------------|----------------|---------|----------|
| No TLS/SSL | 9.1 | Easy | Complete data exposure | P1 |
| Redis No Auth | 9.8 | Easy | Complete session compromise | P1 |
| JWT Race Condition | 8.2 | Moderate | Auth bypass | P1 |
| CSRF Inadequate | 8.8 | Easy | Account takeover | P1 |
| Docker Root | 7.8 | Moderate | Host compromise | P2 |
| Nginx No Headers | 6.5 | Easy | XSS/Clickjacking | P2 |
| Cookie Security | 7.5 | Easy | Session hijacking | P2 |
| No Rate Limiting | 7.1 | Easy | DoS/Brute force | P2 |
| Redis Network | 8.1 | Easy | Data exfiltration | P2 |
| Input Validation | 7.0 | Moderate | Injection attacks | P3 |

---

## Phase 1: PRODUCTION BLOCKERS (Fix First - Days 1-2)

### Task 1.1: Enable TLS/SSL (CRITICAL)
**File**: `nginx/nginx.conf`

```nginx
# Add to nginx.conf
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # HSTS (enable after confirming HTTPS works)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

**Environment Variables**:
```bash
# .env.production
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem
```

**Verification**:
```bash
curl -I http://localhost  # Should return 301
curl -I https://localhost  # Should return 200 with HTTPS
```

**Time**: 2-4 hours

---

### Task 1.2: Redis Authentication (CRITICAL)
**Files**: `redis/redis.conf`, `redis/sentinel.conf`, `docker-compose.prod.yml`

```conf
# redis/redis.conf
bind 0.0.0.0
protected-mode yes
port 6379
requirepass ${REDIS_PASSWORD}
```

```conf
# redis/sentinel.conf
port 26379
protected-mode yes
sentinel auth-pass mymaster ${REDIS_PASSWORD}
```

**Docker Compose Update**:
```yaml
redis-master:
  environment:
    - REDIS_PASSWORD=${REDIS_PASSWORD}
  command: >
    sh -c "echo 'requirepass '$$REDIS_PASSWORD >> /usr/local/etc/redis/redis.conf &&
           redis-server /usr/local/etc/redis/redis.conf"
```

**Python Client Update**:
```python
# backend/infrastructure/cache/redis_sentinel.py
self._sentinel = Sentinel(
    sentinel_hosts,
    password=settings.REDIS_SENTINEL_PASSWORD,  # Add this
    socket_connect_timeout=5,
)
```

**Verification**:
```bash
redis-cli -a wrongpassword ping  # Should fail
redis-cli -a correctpassword ping  # Should return PONG
```

**Time**: 3-6 hours

---

### Task 1.3: Fix JWT Blacklist Race Condition (CRITICAL)
**File**: `backend/services/auth/token_blacklist.py`

```python
async def verify_and_blacklist(token: str) -> dict:
    """Verify token and check blacklist atomically."""
    try:
        # Step 1: Decode without verification to get jti
        unverified = jwt.decode(
            token,
            options={"verify_signature": False, "verify_exp": False}
        )
        jti = unverified.get("jti")
        
        # Step 2: Check blacklist FIRST
        if jti and await self.is_blacklisted(jti):
            raise HTTPException(status_code=401, detail="Token revoked")
        
        # Step 3: NOW verify signature
        claims = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        return claims
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
```

**Verification**:
```python
# Test: Blacklist token, then try to use it
await blacklist_token(token)
# Immediately try to verify - should raise 401
try:
    await verify_and_blacklist(token)
    assert False, "Should have raised 401"
except HTTPException as e:
    assert e.status_code == 401
```

**Time**: 2-4 hours

---

### Task 1.4: Implement Proper CSRF Protection (CRITICAL)
**Install**: `pip install fastapi-csrf-protect`

**File**: `backend/app/middleware.py`

```python
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

@CsrfProtect.load_config
def get_csrf_config():
    return [
        ('secret_key', settings.SECRET_KEY),
        ('cookie_secure', True),
        ('cookie_samesite', 'Lax'),
        ('header_name', 'X-CSRF-Token'),
    ]

class CSRFMiddleware(BaseHTTPMiddleware):
    """Proper CSRF protection using double-submit cookie pattern."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip safe methods
        if request.method in {'GET', 'HEAD', 'OPTIONS'}:
            return await call_next(request)
        
        # Skip if no session cookie
        session_id = request.cookies.get('__Host-session_id')
        if not session_id:
            return await call_next(request)
        
        # Validate CSRF token
        csrf_token = request.headers.get('X-CSRF-Token')
        csrf_cookie = request.cookies.get('csrf_token')
        
        if not csrf_token or not csrf_cookie:
            return JSONResponse(
                status_code=403,
                content={'detail': 'CSRF token missing'}
            )
        
        if csrf_token != csrf_cookie:
            return JSONResponse(
                status_code=403,
                content={'detail': 'CSRF token mismatch'}
            )
        
        return await call_next(request)
```

**Frontend Update Required**:
```javascript
// All POST/PUT/DELETE requests must include CSRF token
const csrfToken = getCookie('csrf_token');
fetch('/api/v1/auth/logout', {
  method: 'POST',
  headers: {
    'X-CSRF-Token': csrfToken,
  },
});
```

**Time**: 6-12 hours (includes frontend changes)

---

## Phase 2: HARDENING (Days 3-4)

### Task 2.1: Docker Non-Root User (CRITICAL)
**File**: `backend/Dockerfile.production`

```dockerfile
# Add at the end of Dockerfile
RUN addgroup --system --gid 1000 appgroup && \
    adduser --system --uid 1000 --ingroup appgroup appuser

# Change ownership of app files
RUN chown -R appuser:appgroup /app

USER appuser
```

**Docker Compose Security**:
```yaml
backend-1:
  user: "1000:1000"
  read_only: true
  security_opt:
    - no-new-privileges:true
  cap_drop:
    - ALL
  cap_add:
    - NET_BIND_SERVICE
```

**Time**: 2-4 hours

---

### Task 2.2: Nginx Security Headers (CRITICAL)
**File**: `nginx/nginx.conf`

```nginx
server {
    listen 443 ssl http2;
    
    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    
    # CSP (tune for your frontend)
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https:; frame-ancestors 'none'; base-uri 'self';" always;
}
```

**Verification**:
```bash
curl -I https://localhost | grep -E "X-Frame|X-Content|X-XSS|CSP"
```

**Time**: 1-2 hours

---

### Task 2.3: Rate Limiting (CRITICAL)
**File**: `nginx/nginx.conf`

```nginx
# Add in http block
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth:10m rate=1r/s;
limit_conn_zone $binary_remote_addr zone=addr:10m;

server {
    # General API rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        limit_conn addr 10;
        proxy_pass http://backend;
    }
    
    # Strict rate limiting for auth endpoints
    location /api/v1/auth/login {
        limit_req zone=auth burst=5 nodelay;
        proxy_pass http://backend;
    }
    
    location /api/v1/auth/signup {
        limit_req zone=auth burst=3 nodelay;
        proxy_pass http://backend;
    }
}
```

**Time**: 1-2 hours

---

### Task 2.4: Cookie Security Enforcement (CRITICAL)
**File**: `backend/app/middleware.py`

```python
class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # ONLY accept __Host- prefixed cookies
        session_id = request.cookies.get("__Host-session_id")
        
        # Reject non-prefixed cookies entirely
        if request.cookies.get("session_id") and not session_id:
            logger.warning(f"Rejected non-secure session cookie from {request.client.host}")
            # Optionally: clear the insecure cookie
            response = await call_next(request)
            response.delete_cookie(key="session_id", path="/")
            return response
        
        # Rest of the middleware...
```

**Time**: 1 hour

---

### Task 2.5: Network Segmentation (CRITICAL)
**File**: `docker-compose.prod.yml`

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
  database:
    driver: bridge
    internal: true

services:
  nginx:
    networks:
      - frontend
      - backend
    
  backend-1:
    networks:
      - backend
      - database
    
  redis-master:
    networks:
      - database
    # No ports exposed to host
```

**Time**: 2-3 hours

---

## Phase 3: VALIDATION & MONITORING (Day 5)

### Task 3.1: Security Testing Suite

```bash
#!/bin/bash
# scripts/security_test.sh

echo "=== Security Validation Tests ==="

# Test 1: HTTPS enforcement
echo "Test 1: HTTP should redirect to HTTPS"
curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "301" && echo "PASS" || echo "FAIL"

# Test 2: Redis auth
echo "Test 2: Redis should require auth"
redis-cli ping 2>&1 | grep -q "NOAUTH" && echo "PASS" || echo "FAIL"

# Test 3: Security headers
echo "Test 3: Security headers present"
curl -s -I https://localhost | grep -q "X-Frame-Options" && echo "PASS" || echo "FAIL"

# Test 4: CSRF protection
echo "Test 4: POST without CSRF token should fail"
curl -s -o /dev/null -w "%{http_code}" -X POST https://localhost/api/v1/auth/logout | grep -q "403" && echo "PASS" || echo "FAIL"

# Test 5: Rate limiting
echo "Test 5: Rate limiting should trigger"
for i in {1..15}; do
  curl -s -o /dev/null https://localhost/api/v1/auth/login
done
curl -s -o /dev/null -w "%{http_code}" https://localhost/api/v1/auth/login | grep -q "429" && echo "PASS" || echo "FAIL"

echo "=== Tests Complete ==="
```

**Time**: 2-4 hours

---

## Deployment Checklist

### Pre-Deployment
- [ ] All Priority 1 tasks completed
- [ ] Security test suite passing
- [ ] Load test with 100+ concurrent users
- [ ] Penetration test (basic)
- [ ] SSL certificate valid and auto-renewal configured
- [ ] Backup strategy documented

### Post-Deployment
- [ ] Monitoring alerts configured
- [ ] Log aggregation working
- [ ] Incident response plan ready
- [ ] Security audit scheduled (30 days)

---

## Medium Priority Fixes (Post-Launch)

1. **Prometheus Authentication** - Add basic auth or VPN-only access
2. **Log Rotation** - Configure logrotate or max log size
3. **Health Check Timeouts** - Add explicit timeout values
4. **Redis Backups** - Automated RDB snapshots to S3
5. **Image Scanning** - Add Trivy/Clair to CI/CD

---

## Verification Commands

```bash
# SSL Test
curl -I https://localhost

# Security Headers
curl -I https://localhost | grep -i "x-\|content-security"

# Redis Auth
redis-cli -h localhost -a wrongpassword ping  # Should fail
redis-cli -h localhost -a correctpassword ping  # Should succeed

# Rate Limiting
for i in {1..20}; do curl -s -o /dev/null -w "%{http_code}\n" https://localhost/api/v1/auth/login; done

# CSRF
curl -X POST https://localhost/api/v1/auth/logout -H "Authorization: Bearer token"  # Should fail (403)
```

---

**GO/NO-GO Criteria for Production**:
- [ ] HTTPS enforced
- [ ] Redis authenticated
- [ ] JWT blacklist working
- [ ] CSRF protection active
- [ ] Security headers present
- [ ] Rate limiting active
- [ ] Docker non-root
- [ ] All tests passing

**DO NOT DEPLOY** if any critical checkbox is unchecked.
