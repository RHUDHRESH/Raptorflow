# Google OAuth Setup Guide

This guide will help you set up Google OAuth authentication for Raptorflow using Supabase.

## Prerequisites

- A Supabase account and project
- A Google Cloud Platform (GCP) account
- Your application URL (e.g., `http://localhost:3000` for development)

## Step 1: Set Up Google OAuth in Google Cloud Console

1. **Go to Google Cloud Console**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Select or create a project

2. **Enable Google+ API**
   - Navigate to **APIs & Services** > **Library**
   - Search for "Google+ API" and enable it
   - Also enable "Google Identity Toolkit API"

3. **Create OAuth 2.0 Credentials**
   - Go to **APIs & Services** > **Credentials**
   - Click **Create Credentials** > **OAuth client ID**
   - If prompted, configure the OAuth consent screen first:
     - Choose **External** (unless you have a Google Workspace)
     - Fill in the required information:
       - App name: "Raptorflow"
       - User support email: Your email
       - Developer contact: Your email
     - Add scopes: `email`, `profile`, `openid`
     - Add test users (if in testing mode)
   - For application type, select **Web application**
   - Add authorized redirect URIs:
     ```
     https://<your-project-ref>.supabase.co/auth/v1/callback
     ```
     Replace `<your-project-ref>` with your Supabase project reference ID
   - Click **Create**
   - Copy the **Client ID** and **Client Secret**

## Step 2: Configure Google OAuth in Supabase

1. **Go to Supabase Dashboard**
   - Visit [Supabase Dashboard](https://app.supabase.com/)
   - Select your project

2. **Navigate to Authentication Settings**
   - Go to **Authentication** > **Providers**
   - Find **Google** in the list and click on it

3. **Enable Google Provider**
   - Toggle **Enable Google provider** to ON
   - Enter your **Client ID** (from Step 1)
   - Enter your **Client Secret** (from Step 1)
   - Click **Save**

## Step 3: Configure Redirect URLs

1. **In Supabase Dashboard**
   - Go to **Authentication** > **URL Configuration**
   - Add your site URL:
     - Development: `http://localhost:3000`
     - Production: `https://yourdomain.com`
   - Add redirect URLs:
     - Development: `http://localhost:3000/**`
     - Production: `https://yourdomain.com/**`

2. **In Google Cloud Console**
   - Make sure your redirect URI matches:
     ```
     https://<your-project-ref>.supabase.co/auth/v1/callback
     ```

## Step 4: Update Environment Variables

Make sure your `.env.local` file includes:

```bash
VITE_SUPABASE_URL=https://<your-project-ref>.supabase.co
VITE_SUPABASE_ANON_KEY=<your-anon-key>
```

You can find these in Supabase Dashboard > Settings > API.

## Step 5: Test the Integration

1. **Start your development server**
   ```bash
   npm run dev
   ```

2. **Navigate to the login page**
   - Go to `http://localhost:3000/login`
   - Click **Continue with Google**
   - You should be redirected to Google's sign-in page
   - After signing in, you'll be redirected back to your app

## Troubleshooting

### "Redirect URI mismatch" Error

- Make sure the redirect URI in Google Cloud Console exactly matches:
  ```
  https://<your-project-ref>.supabase.co/auth/v1/callback
  ```
- Check that there are no trailing slashes or extra characters

### "OAuth client not found" Error

- Verify your Client ID and Client Secret are correct in Supabase
- Make sure you copied them from the correct Google Cloud project

### User Not Redirected After Sign-In

- Check your site URL configuration in Supabase
- Verify redirect URLs are set correctly in both Supabase and Google Cloud Console

### Development vs Production

For production, make sure to:
1. Update the OAuth consent screen to "In Production" (requires verification)
2. Add your production domain to authorized redirect URIs in Google Cloud Console
3. Update site URLs in Supabase to your production domain

## Additional Resources

- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Supabase Google Provider Guide](https://supabase.com/docs/guides/auth/social-login/auth-google)

## Security Notes

- Never commit your Client Secret to version control
- Use environment variables for all sensitive credentials
- Enable 2FA on your Google Cloud account
- Regularly rotate your OAuth credentials
- Monitor OAuth usage in Google Cloud Console

