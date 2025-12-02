# Google OAuth Setup Guide

This guide will help you set up Google OAuth authentication for Raptorflow using Supabase.

**IMPORTANT:** If you are seeing `Error 401: deleted_client`, it means your Google Cloud Project credentials have been deleted or are invalid. You must create new credentials and update Supabase.

## Step 1: Set Up Google OAuth in Google Cloud Console

1. **Go to Google Cloud Console**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Select or create a project

2. **Enable APIs**
   - Navigate to **APIs & Services** > **Library**
   - Search for and enable:
     - **Google+ API** (deprecated but sometimes referenced) or **Google People API**
     - **Google Identity Toolkit API** (if applicable, usually just OAuth consent screen setup is enough)

3. **Configure OAuth Consent Screen**
   - Go to **APIs & Services** > **OAuth consent screen**
   - Select **External** (unless you have a Google Workspace)
   - Fill in the required information:
     - App name: "Raptorflow"
     - User support email: Your email
     - Developer contact: Your email
   - Add scopes: `email`, `profile`, `openid`
   - Add test users (e.g., your email) if the app is in Testing mode.

4. **Create OAuth 2.0 Credentials**
   - Go to **APIs & Services** > **Credentials**
   - Click **Create Credentials** > **OAuth client ID**
   - Application type: **Web application**
   - **Authorized redirect URIs**:
     ```
     https://vpwwzsanuyhpkvgorcnc.supabase.co/auth/v1/callback
     ```
     *(Note: This URL is specific to your Supabase project)*
   - Click **Create**
   - Copy the **Client ID** and **Client Secret**

## Step 2: Configure Google OAuth in Supabase

1. **Go to Supabase Dashboard**
   - Visit [Supabase Dashboard](https://supabase.com/dashboard)
   - Select your project (**Raptorflow**)

2. **Navigate to Authentication Settings**
   - Go to **Authentication** > **Providers**
   - Find **Google** in the list and expand it.

3. **Update Credentials**
   - **Client ID**: Paste the NEW Client ID from Google Cloud.
   - **Client Secret**: Paste the NEW Client Secret from Google Cloud.
   - Click **Save**.

## Step 3: Configure Redirect URLs (Supabase)

1. **In Supabase Dashboard**
   - Go to **Authentication** > **URL Configuration**
   - **Site URL**: Set to your production URL (e.g., `https://raptorflow.in`) or `http://localhost:5173` for local dev.
   - **Redirect URLs**: Add the following:
     - `http://localhost:5173/**`
     - `https://raptorflow.in/**`
     - `https://raptorflow.in/onboarding/intro`

## Step 4: Verify

1. Restart your local server if needed (`npm run dev`).
2. Try logging in again.

## Troubleshooting

### "deleted_client" Error
This confirms your Client ID in Supabase is invalid. You **MUST** perform Steps 1 & 2 above to generate a new one.

### "redirect_uri_mismatch" Error
Double check that `https://vpwwzsanuyhpkvgorcnc.supabase.co/auth/v1/callback` is exactly listed in your Google Cloud Console Credentials.
