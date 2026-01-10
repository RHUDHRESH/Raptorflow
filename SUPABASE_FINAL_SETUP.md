# RaptorFlow Supabase Final Setup Guide

## ✅ Current Status
- Supabase CLI installed
- Config file properly configured for production (raptorflow.in)
- Migrations ready
- Environment variables configured
- Service role key needs updating

## 🚀 Quick Setup Steps

### 1. Get Your Supabase Access Token
1. Go to https://supabase.com/dashboard/account/tokens
2. Generate a new access token
3. Copy the token (starts with `sbp_`)

### 2. Login and Link Project
```bash
# In the supabase directory
supabase login
# Paste your access token when prompted

# Link to your project
supabase link --project-ref vpwwzsanuyhpkvgorcnc
```

### 3. Push Migrations
```bash
# Apply database schema
supabase db push
```

### 4. Update Service Role Key
1. Go to https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc/settings/api
2. Find the `service_role` key
3. Update `SUPABASE_SERVICE_ROLE_KEY` in `frontend/.env.local`

### 5. Configure Google OAuth (Optional)
1. Go to https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc/auth/providers
2. Enable Google provider
3. Get OAuth credentials from Google Cloud Console
4. Add redirect URI: `https://vpwwzsanuyhpkvgorcnc.supabase.co/auth/v1/callback`

### 6. Test the Flow
1. Start your frontend: `npm run dev`
2. Go to http://localhost:3000
3. Click "Get Started"
4. Sign up with email (works immediately)
5. Select a plan and complete payment
6. Access workspace

## 🔧 Configuration Summary

### Auth Settings
- Site URL: `https://raptorflow.in`
- Redirect URLs: `https://raptorflow.in/auth/callback`
- Email confirmations: Disabled (for easier testing)

### Database Tables
- `user_profiles` - User data and subscriptions
- `payments` - Payment transactions
- Automatic profile creation on signup
- RLS policies enabled

### Payment Integration
- PhonePe test mode
- Test merchant ID: `PGTESTPAYUAT`
- Test salt key configured

## 🐛 Common Issues

### "Deployment temporarily paused"
- Check project status at https://supabase.com/dashboard
- Resume project if paused

### OAuth redirect errors
- Ensure exact URL match in redirect settings
- Check Google OAuth configuration

### Migration errors
- Run `supabase db reset` to start fresh
- Check for syntax errors in migration files

## 📝 Notes
- Email authentication works without any additional setup
- Google OAuth requires configuration but provides better UX
- All new users need to purchase a subscription to access workspace
- PhonePe is in test mode - no real charges

## ✨ Next Steps
1. Complete the setup above
2. Test the complete user flow
3. Configure production PhonePe credentials
4. Set up monitoring and analytics
5. Add more payment methods if needed
