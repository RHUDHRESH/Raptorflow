# Redis Configuration Quick Reference

## URLs by Environment

### Development (Localhost)
```
REDIS_URL=redis://localhost:6379/0
REDIS_SSL=false
```

### Production (Upstash)
```
REDIS_URL=redis://default:PASSWORD@HOST.upstash.io:PORT
REDIS_SSL=true
```

## Getting Upstash Redis URL

1. Go to https://console.upstash.com
2. Click your database
3. Copy the **Redis URL** (full line including password)
4. Example format:
   ```
   redis://default:AXaU...example...P9@us1-fine-cougar-12345.upstash.io:34567
   ```

## Environment Variables

| Variable | Dev | Prod | Purpose |
|----------|-----|------|---------|
| `REDIS_URL` | `localhost:6379` | Upstash URL | Connection string |
| `REDIS_SSL` | `false` | `true` | Enable SSL for security |
| `REDIS_MAX_CONNECTIONS` | 50 | 100 | Connection pool size |
| `REDIS_SOCKET_TIMEOUT` | 5 | 10 | Connection timeout (seconds) |
| `REDIS_RETRIES` | 3 | 3 | Retry failed connections |
| `REDIS_RETRY_DELAY` | 1 | 2 | Delay between retries (seconds) |

## What Redis Does

| Feature | Status | Purpose |
|---------|--------|---------|
| **Rate Limiting** | ✅ Active | Limit API requests |
| **Distributed Locks** | ✅ Active | Prevent race conditions in payments |
| **Token Blacklist** | ✅ Active | Admin token revocation |
| **Session Management** | ✅ Active | User sessions & refresh tokens |
| **Queue Management** | ✅ Active | Job processing & webhook retries |
| **Pub/Sub** | ⏳ Coming | Real-time updates |

## Testing Connection

```bash
# From Cloud Run logs
gcloud run logs read raptorflow-backend --limit 50 | grep "Redis connected"

# Should see:
# ✓ Redis cache connected (url: host.upstash.io:port, attempt: 1)
```

## Upstash Console Links

- **Dashboard**: https://console.upstash.com
- **Database Details**: Select db → click name
- **Stats**: Select db → Stats tab
- **API Keys**: Account Settings

## Cost Estimation

- **Free Tier**: 10,000 commands/day
- **Typical Usage**:
  - Rate limiting: 50-100 commands/day
  - Cache hits: 100-500 commands/day
  - Locks: 10-50 commands/day
  - **Total**: ~200-500 commands/day = Free! ✅

## Common Redis Keys (Auto-generated)

```
raptorflow:lock:webhook:MT123456...           # Distributed lock
raptorflow:webhook:phonepe:192.168.1.1       # Rate limit counter
raptorflow:token_blacklist:uuid               # Revoked tokens
raptorflow:session:session-uuid               # User session data
raptorflow:user_sessions:user-uuid            # Set of user's session IDs
raptorflow:queue:payment_reconciliation       # Payment reconciliation queue
raptorflow:queue:webhook_retry_payment        # Webhook retry queue
raptorflow:research:query                     # Research cache
raptorflow:persona:icp-id                     # Persona cache
raptorflow:content:content-id                 # Content cache
```

## Debugging Commands

If you have Redis CLI:

```bash
# Connect to Upstash
redis-cli -u redis://default:PASSWORD@HOST.upstash.io:PORT

# Check keys
> KEYS raptorflow:*

# View lock
> GET raptorflow:lock:webhook:MT123

# Check counter
> GET raptorflow:webhook:phonepe:192.168.1.1

# Check queue length
> LLEN raptorflow:queue:payment_reconciliation

# Peek at first 5 queue items (newest first)
> LRANGE raptorflow:queue:payment_reconciliation 0 4

# Peek at all queue items
> LRANGE raptorflow:queue:payment_reconciliation 0 -1

# Monitor in real-time
> MONITOR
```
