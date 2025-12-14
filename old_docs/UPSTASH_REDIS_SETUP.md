# Upstash Redis Setup Guide 🚀

Complete guide to set up Upstash Redis for production on Cloud Run.

## Step 1: Create Upstash Account & Database

1. Go to **https://console.upstash.com**
2. Sign up (free account, no credit card needed initially)
3. Click **Create Database**
   - **Name**: `raptorflow-prod`
   - **Region**: Select closest to India
     - **Singapore** (ap-southeast-1) - RECOMMENDED for India
     - Or **us-east-1** (US East)
   - **Type**: Redis
   - Click **Create**

## Step 2: Get Connection Details

Once database is created:

1. Click on your database name
2. In the **Details** tab, copy:
   - **Redis URL**: `redis://default:xxxxxxxxxxxx@xxxxx.upstash.io:xxxxx`
   - Keep this secret! It contains password.

## Step 3: Set Up Cloud Run Environment Variables

### Option A: Using Google Cloud Console (Easiest)

1. Go to **Cloud Run** > Select your service
2. Click **Edit & Deploy New Revision**
3. In **Environment Variables** section, add:

```
REDIS_URL = redis://default:PASSWORD@HOST.upstash.io:PORT
REDIS_SSL = true
ENVIRONMENT = production
```

4. Click **Deploy**

### Option B: Using gcloud CLI

```bash
gcloud run deploy raptorflow-backend \
  --set-env-vars REDIS_URL="redis://default:PASSWORD@HOST.upstash.io:PORT" \
  --set-env-vars REDIS_SSL="true" \
  --set-env-vars ENVIRONMENT="production" \
  --region us-central1 \
  --project YOUR_GCP_PROJECT
```

### Option C: Using GitHub Actions (Recommended)

Add to your `.github/workflows/deploy.yml`:

```yaml
env:
  REDIS_URL: ${{ secrets.UPSTASH_REDIS_URL }}
  REDIS_SSL: "true"
```

Then set GitHub secret:
1. Go to **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret**
3. Name: `UPSTASH_REDIS_URL`
4. Value: `redis://default:PASSWORD@HOST.upstash.io:PORT`

## Step 4: Verify Connection

Once deployed, check logs:

```bash
gcloud run logs read raptorflow-backend --limit 50
```

Look for:
```
✓ Redis cache connected (Upstash)
```

## Step 5: Monitor Usage

Go to **https://console.upstash.com**:
- Click your database
- View **Stats** tab
- See commands/day usage
- Free tier: 10,000 commands/day (usually enough for small projects)

## Pricing

- **Free Tier**: 10,000 commands/day, 1GB storage
- **Pay as you go**: $0.2 per 100k commands
- Typical app: 1,000-5,000 commands/day = $0.02-0.10/month

## Troubleshooting

### ❌ "SSL: CERTIFICATE_VERIFY_FAILED"

**Solution**: Already handled! Our code auto-detects Upstash URL and enables SSL.

### ❌ "Connection timeout"

**Check**:
1. Upstash database is running (check console)
2. Redis URL is correct (copy-paste from Upstash console)
3. Cloud Run has internet access (it does by default)

### ❌ "Max connections exceeded"

Increase `REDIS_MAX_CONNECTIONS` in env vars:
```
REDIS_MAX_CONNECTIONS = 100
```

## Development (Localhost)

For local development, keep using localhost Redis:

```bash
# Install Redis locally
brew install redis  # macOS
# or docker
docker run -d -p 6379:6379 redis:7

# Then in .env
REDIS_URL=redis://localhost:6379/0
REDIS_SSL=false
```

## Security Best Practices

1. ✅ **Never commit Redis URL** to Git
2. ✅ **Use Google Cloud Secrets Manager** for production
3. ✅ **Rotate password** monthly in Upstash console
4. ✅ **Enable SSL** (automatic for Upstash)
5. ✅ **Monitor usage** for unusual activity

## API Endpoints That Use Redis

- Rate limiting on `/api/v1/payments/webhook`
- Rate limiting on `/api/v1/autopay/webhook`
- Session management (future)
- Token blacklist (admin revocation)
- Distributed locks (payment processing)
- Cache (research, personas, content)

---

**Questions?** Check Upstash docs: https://upstash.com/docs
