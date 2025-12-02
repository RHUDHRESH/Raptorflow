# Raptorflow Setup Guide

Complete guide to setting up Google OAuth, Supabase, and all required services for Raptorflow.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Supabase Setup](#supabase-setup)
3. [Google OAuth Setup](#google-oauth-setup)
4. [Database Migration](#database-migration)
5. [Environment Variables](#environment-variables)
6. [Testing the Setup](#testing-the-setup)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, make sure you have:

- **Node.js** (v18 or higher)
- **npm** or **yarn**
- A **Supabase account** (free tier works)
- A **Google Cloud Platform account** (free tier works)
- A **code editor** (VS Code recommended)

---

## Supabase Setup

### Step 1: Create a Supabase Project

1. Go to [https://app.supabase.com/](https://app.supabase.com/)
2. Click **"New project"**
3. Fill in the details:
   - **Name**: Raptorflow (or your preferred name)
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Select the closest region to your users
   - **Pricing Plan**: Free (or choose a paid plan)
4. Click **"Create new project"**
5. Wait for the project to finish setting up (~2 minutes)

### Step 2: Get Your Supabase Credentials

1. In your Supabase dashboard, go to **Settings** (gear icon) → **API**
2. Copy the following values:
   - **Project URL**: `https://your-project-id.supabase.co`
   - **anon public key**: A long string starting with `eyJ...`
3. Save these for the environment variables section

---

## Google OAuth Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** dropdown → **"New Project"**
3. Enter project name: **Raptorflow**
4. Click **"Create"**
5. Wait for the project to be created

### Step 2: Configure OAuth Consent Screen

1. In Google Cloud Console, navigate to **APIs & Services** → **OAuth consent screen**
2. Select **External** (unless you have Google Workspace)
3. Click **"Create"**
4. Fill in the required information:
   - **App name**: Raptorflow
   - **User support email**: Your email address
   - **App logo**: (Optional) Upload your logo
   - **App domain**: Leave blank for now
   - **Authorized domains**: Add your domain if you have one
   - **Developer contact information**: Your email address
5. Click **"Save and Continue"**
6. **Scopes**: Click **"Add or Remove Scopes"**
   - Add: `email`
   - Add: `profile`
   - Add: `openid`
7. Click **"Save and Continue"**
8. **Test users** (if app is in Testing mode):
   - Add your email and any test user emails
9. Click **"Save and Continue"**
10. Review and click **"Back to Dashboard"**

### Step 3: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Select **Application type**: **Web application**
4. **Name**: Raptorflow Web Client
5. **Authorized JavaScript origins**: (Optional)
   - For development: `http://localhost:3000`
   - For production: `https://yourdomain.com`
6. **Authorized redirect URIs**: ⚠️ **IMPORTANT**
   ```
   https://your-project-ref.supabase.co/auth/v1/callback
   ```
   Replace `your-project-ref` with your actual Supabase project reference ID (found in your Supabase project URL)
7. Click **"Create"**
8. **Copy the Client ID and Client Secret** (you'll need these!)

### Step 4: Enable Google+ API (Required)

1. In Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for **"Google+ API"**
3. Click on it and click **"Enable"**
4. Also search for and enable **"Google Identity Toolkit API"**

### Step 5: Configure Google OAuth in Supabase

1. Go to your Supabase Dashboard
2. Navigate to **Authentication** → **Providers**
3. Find **Google** in the list
4. Toggle **Enable Google provider** to **ON**
5. Enter your **Client ID** (from Step 3)
6. Enter your **Client Secret** (from Step 3)
7. **Redirect URL**: This should be automatically filled:
   ```
   https://your-project-ref.supabase.co/auth/v1/callback
   ```
8. Click **"Save"**

### Step 6: Configure Supabase URL Settings

1. In Supabase Dashboard, go to **Authentication** → **URL Configuration**
2. **Site URL**: 
   - Development: `http://localhost:3000`
   - Production: `https://yourdomain.com`
3. **Redirect URLs**: Add these patterns:
   - `http://localhost:3000/**`
   - `https://yourdomain.com/**` (if you have production)
4. Click **"Save"**

---

## Database Migration

### Step 1: Run Migrations

You need to run the SQL migrations in your Supabase database:

1. In Supabase Dashboard, go to **SQL Editor**
2. Click **"New query"**
3. Copy and paste the contents of each migration file in order:

   **Migration 1**: `database/migrations/001_move_system_schema.sql`
   - Click **"Run"**
   - Wait for success message

   **Migration 2**: `database/migrations/002_assets_table.sql`
   - Click **"New query"** → paste → **"Run"**

   **Migration 3**: `database/migrations/003_quests_table.sql`
   - Click **"New query"** → paste → **"Run"**

   **Migration 4**: `database/migrations/004_core_missing_tables.sql`
   - Click **"New query"** → paste → **"Run"**

   **Migration 5**: `database/migrations/005_subscriptions_and_onboarding.sql`
   - Click **"New query"** → paste → **"Run"**

### Step 2: Verify Migrations

1. In Supabase Dashboard, go to **Table Editor**
2. You should see these tables:
   - `subscriptions`
   - `onboarding_responses`
   - `user_profiles`
   - `workspaces`
   - `cohorts`
   - And many more...

---

## Environment Variables

### Step 1: Create .env.local File

In your project root, create a file called `.env.local`:

```bash
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here

# Google Maps (Optional - for location features)
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-key

# OpenAI (Required for AI features)
VITE_OPENAI_API_KEY=your-openai-api-key

# Google Cloud Vertex AI (Optional - alternative to OpenAI)
VITE_GOOGLE_CLOUD_PROJECT_ID=your-project-id
VITE_GOOGLE_CLOUD_REGION=us-central1

# PostHog Analytics (Optional)
VITE_PUBLIC_POSTHOG_KEY=your-posthog-key
VITE_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

### Step 2: Get API Keys

#### Supabase Keys (Required)
- Already obtained in [Supabase Setup](#step-2-get-your-supabase-credentials)

#### OpenAI API Key (Required for AI features)
1. Go to [https://platform.openai.com/](https://platform.openai.com/)
2. Sign up or log in
3. Go to **API Keys** → **Create new secret key**
4. Copy the key (it starts with `sk-...`)
5. Add to `.env.local` as `VITE_OPENAI_API_KEY`

#### Google Maps API Key (Optional)
1. In Google Cloud Console, go to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"API key"**
3. Copy the API key
4. Click **"Edit API key"** to restrict it:
   - **Application restrictions**: HTTP referrers
   - **API restrictions**: 
     - Maps JavaScript API
     - Places API
     - Geocoding API
5. Add to `.env.local` as `VITE_GOOGLE_MAPS_API_KEY`

### Step 3: Restart Dev Server

After adding environment variables:

```bash
npm run dev
```

---

## Testing the Setup

### Test 1: Google OAuth Login

1. Start your dev server: `npm run dev`
2. Navigate to `http://localhost:3000/login`
3. Click **"Continue with Google"**
4. You should be redirected to Google's sign-in page
5. Sign in with your Google account
6. You should be redirected back to your app

**Expected Result**: 
- You're logged in
- You see the onboarding screen
- No errors in the browser console

### Test 2: Database Tables

1. In Supabase Dashboard, go to **Table Editor**
2. Click on **user_profiles** table
3. You should see a row with your user data
4. Click on **subscriptions** table
5. You should see a subscription (plan: 'free', status: 'active')

### Test 3: Onboarding Flow

1. Complete the onboarding questions
2. Click through all steps
3. Complete the final step
4. Check Supabase **onboarding_responses** table
5. You should see your answers saved

**Expected Result**:
- All data is saved in Supabase
- `user_profiles.onboarding_completed` is set to `true`
- You're redirected to the dashboard

### Test 4: Protected Routes

1. Log out
2. Try to visit `http://localhost:3000/dashboard`
3. You should be redirected to `/login`
4. Log back in
5. You should be redirected back to `/dashboard`

---

## Troubleshooting

### Issue: "Google OAuth is not enabled"

**Solution**: 
1. Go to Supabase Dashboard → Authentication → Providers
2. Make sure Google is **enabled**
3. Verify Client ID and Client Secret are correct
4. Make sure you saved the configuration

### Issue: "Redirect URI mismatch"

**Solution**:
1. Check that the redirect URI in Google Cloud Console **exactly matches**:
   ```
   https://your-project-ref.supabase.co/auth/v1/callback
   ```
2. No trailing slashes
3. Use `https://` not `http://`
4. Check for typos in your project reference ID

### Issue: "User is created but not redirected"

**Solution**:
1. Check Site URL in Supabase: Authentication → URL Configuration
2. Make sure it matches your dev server: `http://localhost:3000`
3. Check Redirect URLs includes: `http://localhost:3000/**`

### Issue: "Migration failed"

**Solution**:
1. Check if you have the required permissions
2. Run migrations in order (001, 002, 003, 004, 005)
3. Check for syntax errors in the SQL
4. Look at the error message in Supabase SQL Editor

### Issue: "Onboarding doesn't redirect"

**Solution**:
1. Check browser console for errors
2. Verify `onboarding_responses` table exists
3. Verify `user_profiles` table has `onboarding_completed` column
4. Check that the user is authenticated

### Issue: "AI features not working"

**Solution**:
1. Verify OpenAI API key is set in `.env.local`
2. Check that the key starts with `sk-`
3. Make sure you have credits in your OpenAI account
4. Check browser console for API errors
5. Restart dev server after adding env variables

---

## Next Steps

After setup is complete:

1. **Customize Onboarding**: Edit `src/components/Onboarding.jsx`
2. **Add Subscription Plans**: Integrate Stripe for paid plans
3. **Deploy to Production**: 
   - Update Google OAuth redirect URIs
   - Update Supabase Site URL
   - Set production environment variables
4. **Enable Email Auth**: Configure email in Supabase
5. **Add More Providers**: GitHub, Twitter, etc.

---

## Support

If you run into issues:

1. Check the [Supabase Documentation](https://supabase.com/docs)
2. Check the [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
3. Open an issue on GitHub
4. Contact support

---

## Security Checklist

Before going to production:

- [ ] Enable Row Level Security (RLS) on all tables
- [ ] Set up proper RLS policies
- [ ] Use environment variables for all secrets
- [ ] Never commit `.env.local` to git
- [ ] Enable 2FA on Google Cloud account
- [ ] Enable 2FA on Supabase account
- [ ] Set up Supabase database backups
- [ ] Configure CORS properly
- [ ] Review and limit API key permissions
- [ ] Set up monitoring and alerts

---

**Last Updated**: 2025-11-22
**Version**: 1.0.0

