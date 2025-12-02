# Supabase Configuration for GCP and Vercel

This guide explains how to configure your RaptorFlow application to connect to Supabase when running on Google Cloud Platform (GCP) or Vercel.

## Prerequisites

1.  **Supabase Project**: Ensure you have a Supabase project created.
2.  **Credentials**: Retrieve the following from your Supabase Project Settings (API section):
    *   `Project URL` (SUPABASE_URL)
    *   `anon public` key (SUPABASE_ANON_KEY)
    *   `service_role` key (SUPABASE_SERVICE_KEY) - **Keep this secret!**

---

## 1. Google Cloud Platform (GCP) Configuration

The backend is designed to run on Google Cloud Run. You can deploy manually using the `deploy-backend.sh` script or automatically via Cloud Build.

### Option A: Manual Deployment via `deploy-backend.sh`

1.  Navigate to the `backend` directory.
2.  Create a file named `.env.prod` based on `.env.example` (or just create it fresh).
3.  Add your Supabase credentials:
    ```env
    ENVIRONMENT=production
    DEBUG=False
    LOG_LEVEL=INFO
    GOOGLE_CLOUD_PROJECT=your-project-id
    SUPABASE_URL=https://your-project.supabase.co
    SUPABASE_SERVICE_KEY=your-service-role-key
    SECRET_KEY=your-secure-random-string
    ```
4.  Run the deployment script:
    ```bash
    ./deploy-backend.sh
    ```
    This script will build the Docker container, push it to GCR, and deploy to Cloud Run with the environment variables from `.env.prod`.

### Option B: Automated Deployment via Cloud Build

If you are using the `cloudbuild.yaml` pipeline:

1.  Go to **Cloud Build > Triggers** in the Google Cloud Console.
2.  Create or Edit your build trigger.
3.  Under **Substitution variables**, add the following:
    *   `_SUPABASE_URL`: Your Supabase Project URL
    *   `_SUPABASE_ANON_KEY`: Your Supabase Anon Key
    *   `_SUPABASE_SERVICE_KEY`: Your Supabase Service Role Key
    *   `_REGION`: `us-central1` (or your preferred region)
4.  Save the trigger.
5.  Pushing to your repository (or manually running the trigger) will now deploy the backend with these variables set in the Cloud Run service.

---

## 2. Vercel Configuration (Frontend)

The frontend is built with Vite and deployed to Vercel. It needs to connect to Supabase directly for authentication and data fetching.

1.  Go to your project settings in the **Vercel Dashboard**.
2.  Navigate to **Settings > Environment Variables**.
3.  Add the following variables:
    *   `VITE_SUPABASE_URL`: Your Supabase Project URL
    *   `VITE_SUPABASE_ANON_KEY`: Your Supabase Anon Key
    *   `VITE_ENVIRONMENT`: `production`
4.  (Optional) If you use PostHog or Google Maps:
    *   `VITE_POSTHOG_KEY`: Your PostHog Key
    *   `VITE_POSTHOG_HOST`: Your PostHog Host
    *   `VITE_GOOGLE_MAPS_API_KEY`: Your Google Maps API Key
5.  Redeploy your application for the changes to take effect.

---

## 3. Running Database Migrations

Since Supabase is a managed PostgreSQL service, you typically apply migrations via the Supabase Dashboard or CLI.

### Option A: Supabase Dashboard (Recommended for Quick Fixes)

1.  Go to the **SQL Editor** in your Supabase Dashboard.
2.  Open the migration file (e.g., `database/migrations/025_fix_missing_rls_policies.sql`) locally.
3.  Copy the content.
4.  Paste it into the SQL Editor.
5.  Click **Run**.

### Option B: Supabase CLI

If you have the Supabase CLI installed and linked to your project:

```bash
supabase db push
```
(Note: This requires your local migrations directory to be in sync with the remote).

Alternatively, to run a specific file:
```bash
psql -h aws-0-us-east-1.pooler.supabase.com -p 6543 -U postgres.[your-project-ref] -d postgres -f database/migrations/025_fix_missing_rls_policies.sql
```
(You will need the database password).

### Option C: Automated Migration (Advanced)

For automated migrations during deployment, you would typically:
1.  Create a Cloud Build step that runs a script using a Python or Node.js Supabase client to execute the SQL.
2.  Or use a tool like `prisma migrate deploy` if you were using Prisma.
3.  Currently, the project is set up for manual migration application via SQL files.

---

## 4. Verification

After configuration:

1.  **Frontend**: Open your Vercel URL. Open the browser console. Verify there are no errors connecting to Supabase (e.g., 401 Unauthorized).
2.  **Backend**: Check Cloud Run logs. Look for "Supabase client connected" messages.
3.  **Database**: Check the Supabase Dashboard > Table Editor. Verify that RLS is enabled on tables (lock icon) and that you can access data according to your policies.
