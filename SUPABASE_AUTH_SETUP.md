# RaptorFlow Authentication Setup Guide

## Overview

This guide covers the complete authentication setup for RaptorFlow, including Supabase configuration, environment variables, and troubleshooting common redirect issues.

## Quick Setup Checklist

- [ ] Add redirect URLs to Supabase
- [ ] Configure environment variables
- [ ] Test OAuth flow
- [ ] Verify database tables exist
- [ ] Check logs for redirect issues

## Supabase Configuration

### 1. Required Redirect URLs

Add these URLs to your Supabase project **Authentication > Settings > Redirect URLs**:

#### Development Environment
```
http://localhost:3000/auth/callback
http://localhost:3000/auth/reset-password
```

#### Production Environment
```
https://raptorflow.in/auth/callback
https://raptorflow.in/auth/reset-password
```

#### Vercel Preview (add your specific preview domains)
```
https://<your-preview-app>.vercel.app/auth/callback
https://<your-preview-app>.vercel.app/auth/reset-password
```

### 2. Required Database Tables

Ensure these tables exist in your Supabase database:

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  onboarding_status TEXT DEFAULT 'pending',
  default_workspace_id UUID,
  is_active BOOLEAN DEFAULT true,
  is_banned BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User subscriptions table
CREATE TABLE user_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  plan_id TEXT NOT NULL,
  status TEXT DEFAULT 'inactive',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Environment Variables

### Required Variables
```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Optional Variables (for custom domains/preview)
```env
# Custom App URL (overrides automatic detection)
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Vercel (auto-set on Vercel deployments)
VERCEL_URL=your-vercel-app.vercel.app
VERCEL_ENV=preview

# Environment Detection
NEXT_PUBLIC_APP_ENV=development
NODE_ENV=development
```

### OAuth Provider Variables
```env
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# GitHub OAuth (optional)
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Microsoft OAuth (optional)
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret

# Apple OAuth (optional)
APPLE_CLIENT_ID=your_apple_client_id
APPLE_CLIENT_SECRET=your_apple_client_secret
```

## How Authentication Works

### 1. Base URL Resolution
The system uses this priority order for determining the base URL:
1. `NEXT_PUBLIC_APP_URL` (explicit override)
2. `VERCEL_URL` (Vercel preview/production)
3. Environment-based fallbacks (localhost vs raptorflow.in)

### 2. OAuth Redirect Flow
1. User clicks "Continue with Google"
2. System generates OAuth URL with `getAuthCallbackUrl()`
3. Google redirects to `{baseUrl}/auth/callback`
4. Callback route exchanges code for session
5. System checks user data and redirects appropriately

### 3. Post-Login Redirect Logic
- **No subscription** → `/pricing`
- **No onboarding** → `/onboarding`
- **Complete setup** → `/dashboard` or requested page

## Testing Your Setup

### 1. Environment Validation
```bash
# Check current environment
npm run dev

# Look for these logs:
# ✅ Environment validation passed
# 🔐 Auth Configuration Summary:
```

### 2. OAuth Flow Testing
1. Open browser dev tools Network tab
2. Go to login page and click "Continue with Google"
3. Verify the redirect URL matches your expected domain
4. Complete Google OAuth flow
5. Check you land on the correct page

### 3. Database Verification
```sql
-- Check if user was created
SELECT * FROM users WHERE email = 'your-email@example.com';

-- Check subscription status
SELECT * FROM user_subscriptions WHERE user_id = [user_id];
```

## Common Issues & Solutions

### Issue: Redirect to raptorflow.in in development
**Cause**: Environment variables forcing production mode
**Solution**: Set `NEXT_PUBLIC_APP_ENV=development` or `NEXT_PUBLIC_APP_URL=http://localhost:3000`

### Issue: OAuth provider error
**Cause**: Redirect URL not in Supabase allowlist
**Solution**: Add your local/preview URL to Supabase Authentication > Settings > Redirect URLs

### Issue: Stuck on pricing page after login
**Cause**: Missing subscription record or user record
**Solution**: 
1. Check `users` table has row for your auth user
2. Check `user_subscriptions` table has active subscription
3. Look at auth callback logs for details

### Issue: Infinite redirect loops
**Cause**: Missing data or incorrect redirect logic
**Solution**: Check browser console for auth callback logs showing redirect decisions

### Issue: Domain mismatch errors
**Cause**: Request origin doesn't match expected base URL
**Solution**: Ensure environment variables match your actual domain

## Debugging Tools

### 1. Environment Summary
```javascript
// In any component
import { getEnvironmentSummary } from '@/lib/env-validation'
console.log(getEnvironmentSummary())
```

### 2. Auth Configuration
```javascript
// Check auth configuration
import { validateAndLogAuthConfig } from '@/lib/auth-config'
validateAndLogAuthConfig()
```

### 3. Required Redirect URLs
```javascript
// Get all required URLs for Supabase
import { getSupabaseRedirectUrls } from '@/lib/auth-config'
console.log('Required redirect URLs:', getSupabaseRedirectUrls())
```

## Production Deployment

### 1. Vercel Deployment
- Set `NEXT_PUBLIC_APP_ENV=production`
- Add production URLs to Supabase redirect list
- Verify all OAuth providers have production credentials

### 2. Environment Variable Validation
The system automatically validates required variables on startup and will:
- Log warnings in development
- Throw errors in production if critical variables are missing

### 3. Security Considerations
- Use HTTPS in production
- Ensure OAuth redirect URLs use HTTPS
- Review Supabase RLS policies
- Monitor auth callback logs for suspicious activity

## Support

If you encounter issues:
1. Check browser console for errors
2. Review auth callback logs in server logs
3. Verify environment variables
4. Ensure Supabase tables exist
5. Check redirect URL configuration in Supabase

For additional help, refer to the auth callback logs which provide detailed information about:
- User data found/created
- Subscription status
- Redirect decisions
- Final redirect URL
