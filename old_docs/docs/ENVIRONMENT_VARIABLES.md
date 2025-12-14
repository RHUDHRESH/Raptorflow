# Environment Variables Reference

This document describes all environment variables needed for Raptorflow.

## Required Environment Variables

Create a `.env.local` file in your project root with these variables:

### Backend API Configuration (Required)

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000
```

For production, set this to your deployed backend URL (e.g., `https://api.raptorflow.com`)

### Supabase Configuration (Required)

```bash
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

Get these from: https://app.supabase.com/ → Your Project → Settings → API

### AI Services (Required for AI features)

```bash
# OpenAI API Key (Primary AI provider)
VITE_OPENAI_API_KEY=sk-your-openai-key-here
```

Get from: https://platform.openai.com/api-keys

## Optional Environment Variables

### Google Services

```bash
# Google Maps API Key (For location-based features)
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here

# Google Cloud Vertex AI (Alternative to OpenAI)
VITE_GOOGLE_CLOUD_PROJECT_ID=your-gcp-project-id
VITE_GOOGLE_CLOUD_REGION=us-central1
```

### Analytics & Monitoring

```bash
# PostHog Analytics
VITE_PUBLIC_POSTHOG_KEY=your-posthog-key-here
VITE_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

### Social Media Integrations

```bash
# Instagram Graph API
VITE_INSTAGRAM_CLIENT_ID=your-instagram-client-id
VITE_INSTAGRAM_CLIENT_SECRET=your-instagram-client-secret

# LinkedIn API
VITE_LINKEDIN_CLIENT_ID=your-linkedin-client-id
VITE_LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret

# Twitter/X API
VITE_TWITTER_API_KEY=your-twitter-api-key
VITE_TWITTER_API_SECRET=your-twitter-api-secret

# YouTube Data API
VITE_YOUTUBE_API_KEY=your-youtube-api-key
```

### Payment Processing

```bash
# PhonePe (Primary Payment Gateway for India)
PHONEPE_MERCHANT_ID=your-phonepe-merchant-id
PHONEPE_SALT_KEY=your-phonepe-salt-key
PHONEPE_SALT_INDEX=1
PHONEPE_ENABLED=True

# Stripe (Alternative)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
```

Get PhonePe credentials from: https://business.phonepe.com/

## Setup Instructions

1. **Copy the template**:
   ```bash
   # Create your local environment file
   touch .env.local
   ```

2. **Add required variables**:
   - `VITE_API_URL` (e.g., `http://localhost:8000` for development)
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
   - `VITE_OPENAI_API_KEY` (optional, for legacy direct AI calls)

3. **Restart dev server**:
   ```bash
   npm run dev
   ```

## Security Notes

- ⚠️ **NEVER commit `.env.local` to version control**
- `.env.local` is already in `.gitignore`
- Use different keys for development/staging/production
- Rotate keys regularly
- Enable 2FA on all service accounts

## Testing Your Setup

1. Start dev server: `npm run dev`
2. Navigate to: `http://localhost:3000/login`
3. Try Google OAuth login
4. Complete onboarding
5. Check browser console for errors

## Troubleshooting

### Variables not loading?
- Restart your dev server after changing `.env.local`
- Check that variable names start with `VITE_`
- Check for syntax errors in `.env.local`

### Google OAuth not working?
- Verify `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` are correct
- Check Google OAuth setup in Supabase Dashboard
- See `SETUP_GUIDE.md` for detailed OAuth setup

### AI features not working?
- Verify backend API is running at `VITE_API_URL`
- Check backend logs for Vertex AI errors
- Verify Google Cloud credentials are configured on the backend
- Check browser console for API errors

### Backend connection errors?
- Verify `VITE_API_URL` points to the correct backend URL
- Ensure backend server is running (`cd backend && python -m uvicorn main:app --reload`)
- Check CORS configuration in backend (`backend/main.py`)
- Verify authentication tokens are being sent correctly

