# RaptorFlow Supabase Setup Guide

## Prerequisites

1. Docker Desktop installed and running
2. Supabase CLI installed
3. Google OAuth credentials

## Step 1: Login to Supabase

```bash
npx supabase login
```

You'll need to get your access token from:

- Go to https://supabase.com/dashboard/account/tokens
- Generate a new token (format: sbp_0102...1920)

## Step 2: Create Supabase Project

```bash
npx supabase projects create raptorflow --org-id YOUR_ORG_ID --db-password YourSecurePassword123!
```

## Step 3: Update Project Configuration

Update `supabase/config.toml` with your actual project ID:

```toml
project_id = "your-actual-project-id"
```

## Step 4: Configure Google OAuth

1. Go to your Supabase project dashboard
2. Navigate to Authentication > Providers
3. Enable Google provider
4. Add your Google OAuth credentials:
   - Client ID: Your Google OAuth Client ID
   - Client Secret: Your Google OAuth Client Secret
   - Redirect URL: http://localhost:3000/auth/callback

## Step 5: Start Local Development

```bash
npx supabase start
```

## Step 6: Apply Database Migrations

```bash
npx supabase db reset
```

## Step 7: Update Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## Step 8: Test Google Login

1. Start the app: `npm run dev`
2. Navigate to http://localhost:3000
3. Click "Login with Google"
4. This should create your user account and workspace automatically

## Automatic Account Creation

The system will automatically:

1. Create a user record in `auth.users`
2. Create a workspace for the user
3. Add the user as an 'owner' in `workspace_members`
4. Set up initial foundation state

## Next Steps

Once Docker is running, execute these commands to complete the setup.
