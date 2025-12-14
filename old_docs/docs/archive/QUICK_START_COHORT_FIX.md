# Quick Start Guide - Test Cohort Generation Fix

## Prerequisites Check

Before starting, make sure you have:
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed  
- ✅ Backend dependencies installed
- ✅ Frontend dependencies installed
- ✅ `.env.local` configured with required variables

## Step-by-Step Testing

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Key packages needed:
- `google-cloud-aiplatform>=1.42.1` - Vertex AI SDK
- `anthropic[vertex]>=0.18.0` - Claude via Vertex AI
- `fastapi>=0.109.0` - API framework

### 2. Configure Environment Variables

Create `.env.local` in the project root:

```bash
# Backend API
VITE_API_URL=http://localhost:8000

# Supabase
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Google Maps (optional)
VITE_GOOGLE_MAPS_API_KEY=your-maps-key
```

**Backend Environment Variables** (create `backend/.env` if needed):

```bash
# Google Cloud Project
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Vertex AI Models (already configured in settings.py)
MODEL_CREATIVE=claude-3-7-sonnet-20250219
MODEL_CREATIVE_FAST=claude-3-5-haiku-20241022
MODEL_REASONING=gemini-2.0-flash-thinking-exp-01-21
MODEL_FAST=gemini-2.5-flash-preview-04-17
MODEL_OCR=pixtral-large-2411

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379
```

### 3. Authenticate with Google Cloud

If using Vertex AI, authenticate:

```bash
# Install Google Cloud CLI if not already installed
# https://cloud.google.com/sdk/docs/install

# Login
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### 4. Start the Backend

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Backend should be running at:** `http://localhost:8000`

Check health: `http://localhost:8000/health`

Expected response:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "2.0.0",
  "services": {
    "redis": "healthy",
    "supabase": "connected"
  }
}
```

### 5. Start the Frontend

In a new terminal:

```bash
npm run dev
```

✅ **Frontend should be running at:** `http://localhost:5173`

### 6. Test Cohort Generation

#### Option A: Via UI
1. Open `http://localhost:5173` in your browser
2. Login or complete onboarding
3. Navigate to Cohort Builder
4. Fill in business information:
   - Business description
   - Product description  
   - Target market
   - Value proposition
   - Top customers (optional)
5. Click **"Generate Cohort"**
6. Wait for AI generation (20-30 seconds)
7. Review generated cohort
8. Refine and save

#### Option B: Via API (Direct Test)

Test the API directly with curl:

```bash
curl -X POST http://localhost:8000/api/v1/cohorts/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-token" \
  -d '{
    "businessDescription": "We provide cloud-based project management software for remote teams",
    "productDescription": "SaaS tool with real-time collaboration, task tracking, and analytics",
    "targetMarket": "Small to medium SaaS companies with distributed teams",
    "valueProposition": "Increase team productivity by 40% with seamless remote collaboration",
    "topCustomers": "Tech startups with 20-100 employees, using Slack and Asana currently"
  }'
```

Expected response (sample):
```json
{
  "name": "Mid-Market SaaS Leaders",
  "executiveSummary": "Fast-growing SaaS companies...",
  "demographics": {
    "companySize": "20-100",
    "industry": "SaaS / Technology",
    "revenue": "$1M-$10M",
    "location": "North America, Europe"
  },
  "buyerRole": "VP of Operations / Head of People",
  "psychographics": {
    "values": ["Efficiency", "Innovation", "Collaboration"],
    "decisionStyle": "Data-driven with quick execution",
    "priorities": ["Team productivity", "Cost efficiency", "Scalability"]
  },
  "painPoints": [
    "Scattered tools causing context switching",
    "Difficulty tracking remote team progress",
    "Communication gaps across time zones"
  ],
  "goals": [
    "Improve team alignment by 50%",
    "Reduce tool sprawl and consolidate systems",
    "Scale operations without hiring overhead"
  ],
  ...
}
```

### 7. Verify Backend Processing

Check backend terminal for logs:

```
INFO - Generating cohort from inputs correlation_id=abc-123
INFO - Cohort generated successfully correlation_id=abc-123
```

### 8. View API Documentation

Navigate to: `http://localhost:8000/api/docs`

Interactive Swagger UI with all endpoints:
- POST `/api/v1/cohorts/generate` - Generate cohort
- POST `/api/v1/cohorts/psychographics` - Compute psychographics
- GET `/api/v1/cohorts/` - List cohorts
- POST `/api/v1/cohorts/` - Save cohort
- GET `/api/v1/cohorts/{id}` - Get cohort
- DELETE `/api/v1/cohorts/{id}` - Delete cohort

## Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'google.cloud'`

**Fix:**
```bash
cd backend
pip install google-cloud-aiplatform anthropic[vertex]
```

**Error:** `Could not automatically determine credentials`

**Fix:**
```bash
gcloud auth application-default login
```

### Frontend can't connect to backend

**Error in console:** `Failed to fetch` or `CORS error`

**Fix 1:** Check `VITE_API_URL` in `.env.local`:
```bash
VITE_API_URL=http://localhost:8000
```

**Fix 2:** Verify backend is running:
```bash
curl http://localhost:8000/health
```

**Fix 3:** Check CORS settings in `backend/main.py` allow your frontend origin.

### Cohort generation fails

**Error:** `Failed to generate cohort`

**Check 1:** Backend logs for detailed error:
```bash
# Look for ERROR logs in backend terminal
```

**Check 2:** Vertex AI permissions:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:YOUR_EMAIL" \
  --role="roles/aiplatform.user"
```

**Check 3:** Vertex AI API is enabled:
```bash
gcloud services enable aiplatform.googleapis.com
```

**Check 4:** Google Cloud quota not exceeded (check Cloud Console)

### Authentication errors

**Error:** `401 Unauthorized`

**Development Fix:** Backend uses dummy auth in development mode. Check:
```python
# backend/main.py
if settings.ENVIRONMENT == "development":
    user_id = "00000000-0000-0000-0000-000000000000"
```

**Production Fix:** Implement proper JWT verification with Supabase JWT secret.

## Success Criteria

✅ Backend health check returns "healthy"  
✅ Frontend loads without console errors  
✅ Cohort generation completes in 20-30 seconds  
✅ Generated cohort has all required fields populated  
✅ Psychographics computation works  
✅ Cohorts save to database successfully  

## Next Steps

Once basic testing works:
1. Test with real business data
2. Refine prompts for better cohort quality
3. Add error monitoring (Sentry)
4. Implement rate limiting
5. Add caching for similar requests
6. Deploy to production

## Production Deployment

### Backend (Google Cloud Run)
```bash
cd backend
gcloud run deploy raptorflow-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Frontend (Vercel)
```bash
# Update .env.local
VITE_API_URL=https://your-backend.run.app

# Deploy
vercel --prod
```

## Support

If you encounter issues:
1. Check `COHORT_FIX_SUMMARY.md` for detailed explanations
2. Review backend logs for error details
3. Test API endpoints with curl to isolate frontend/backend issues
4. Check Google Cloud Console for Vertex AI quotas and permissions

**The fix is complete and ready to use!** 🎉

