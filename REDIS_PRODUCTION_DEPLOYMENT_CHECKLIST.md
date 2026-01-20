# ⚡ Redis Production Deployment Checklist

## ✅ **PRE-DEPLOYMENT VERIFICATION**

### Infrastructure & Connectivity
- [ ] **Upstash Database Created** in the correct region (e.g., us-east-1).
- [ ] **REST URL Verified**: Must start with `https://` and point to the instance.
- [ ] **REST Token Active**: Verified in the Upstash console with `Read/Write` permissions.
- [ ] **Environment Variables** configured in production:
  ```bash
  UPSTASH_REDIS_URL=https://your-instance.upstash.io
  UPSTASH_REDIS_TOKEN=your-rest-token
  REDIS_MAX_CONNECTIONS=50
  MOCK_REDIS=false
  ```
- [ ] **Network Egress**: Firewall rules allow outbound HTTPS requests to `upstash.io`.

### Package Dependencies
- [ ] **Backend**: `upstash-redis` v0.15.0+ installed in production environment.
- [ ] **Frontend**: `@upstash/redis` v1.28.0+ integrated into build bundle.
- [ ] **No Conflicting Redis**: Verified that the standard `redis` Python package is not shadowing core modules.

### Security Configuration
- [ ] **REST Tokens Secured**: Secrets stored in GCP Secret Manager/Vercel Environment Variables.
- [ ] **Workspace Isolation**: Verified that all caching/session logic uses `ws:{id}` prefixes.
- [ ] **Input Validation**: All data stored in Redis is properly serialized/sanitized JSON.
- [ ] **HTTPS Enforced**: No non-TLS connections allowed to Upstash.

---

## 🚀 **DEPLOYMENT STEPS**

### 1. Environment Setup
```bash
# Verify credentials connectivity
curl -H "Authorization: Bearer $UPSTASH_REDIS_TOKEN" \
     "$UPSTASH_REDIS_URL/ping"
```

### 2. Service Activation
- [ ] Set `MOCK_REDIS=false` in the production environment.
- [ ] Deploy the backend to Cloud Run/Compute Engine.
- [ ] Restart services to initialize the singleton `RedisClient`.

### 3. Health Verification
```bash
# Verify health endpoint returns 'connected'
curl -f "$NEXT_PUBLIC_APP_URL/api/v1/health/redis"
```

---

## 🔍 **POST-DEPLOYMENT VERIFICATION**

### Core Services Check
- [ ] **Sessions**: Login/Logout flow persists user state correctly.
- [ ] **Caching**: Repeating dashboard requests show `HIT` in performance logs.
- [ ] **Rate Limiting**: Multiple rapid API calls trigger `429` as expected.
- [ ] **Queuing**: Background tasks are successfully added to and removed from lists.

### Admin Dashboard Check
- [ ] `GET /api/v1/admin/redis-metrics` - Returns 200 with full statistics.
- [ ] Admin UI shows the `Redis Performance` chart with live data.

---

## 📊 **PERFORMANCE MONITORING**

### Key Metrics to Monitor
- **Redis PING**: Should remain < 600ms globally.
- **Hit Rate**: Caching should achieve > 60% for frequent modules.
- **Memory Usage**: Monitor Upstash console for quota limits (e.g., 256MB free tier).
- **Fallback Rate**: Monitor logs for `Mock Mode` activation events.

### Monitoring Setup
- [ ] **Alerting**: Configure Slack/Email alerts for Redis PING failures.
- [ ] **Upstash Monitoring**: Enable automated email alerts in the Upstash console.

---

## 🚨 **TROUBLESHOOTING GUIDE**

### Common Issues & Solutions

#### 1. "401 Unauthorized"
- **Cause**: Invalid or expired REST Token.
- **Solution**: Refresh the token in the Upstash console and update environment variables.

#### 2. "Connection Timeout"
- **Cause**: Network egress blocked or region mismatch causing high latency.
- **Solution**: Verify DNS resolution and ensure `UPSTASH_REDIS_URL` is reachable from the server.

#### 3. "MOCK MODE ACTIVE"
- **Cause**: `UPSTASH_REDIS_URL` missing or `MOCK_REDIS` set to true.
- **Solution**: Check the `.env.production` configuration and deployment logs.

---

## ✅ **PRODUCTION READINESS CONFIRMED**

### Final Verification
- [ ] Environment variables verified.
- [ ] Connectivity test passed.
- [ ] Graceful fallback verified.
- [ ] Monitoring dashboard functional.
- [ ] Documentation archived and ready.

---

**Redis infrastructure is production-ready!** ⚡

*Last Updated: January 20, 2026*
