# Deployment Guide

## Prerequisites
1.  **Install Missing Tools:**
    - **Docker:** Not found. Install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop).
    - **Google Cloud SDK:** Not found. Install from [cloud.google.com/sdk](https://cloud.google.com/sdk/docs/install).

2.  **Google Cloud Login:**
    ```shell
    gcloud auth login
    gcloud config set project raptorflow-479706
    ```
3.  **Vercel Login:**
    ```shell
    vercel login
    ```

## Step 1: Deploy Backend (Cloud Run)
This step builds the Docker container and deploys the backend API to Google Cloud Run.

1.  Run the deployment script:
    ```shell
    deploy-backend.cmd
    ```
2.  Wait for the deployment to finish.
3.  **Copy the Service URL** output at the end (e.g., `https://raptorflow-backend-xyz-uc.a.run.app`). You will need this for the frontend.

**Note:** If the script fails due to missing `backend\.env.prod`, ensure I have created it (I did!). If it fails on Docker/Gcloud, check your local installation and authentication.

## Step 2: Deploy Frontend (Vercel)
This step deploys the React frontend to Vercel.

1.  Run the deployment script:
    ```shell
    deploy-frontend.cmd
    ```
2.  **Vercel Link:** If prompted to link the project, follow the interactive prompts (select your scope, project name `raptorflow`, etc.).
3.  **Environment Variables:** The script will ask for environment variables.
    *   `VITE_SUPABASE_URL`: Enter `https://vpwwzsanuyhpkvgorcnc.supabase.co`
    *   `VITE_SUPABASE_ANON_KEY`: Enter the key from your `.env.local` file.
    *   `VITE_BACKEND_API_URL`: **Paste the Cloud Run Service URL** from Step 1 (append `/api/v1` if needed, check backend routes). usually `https://.../api/v1`.
    *   `VITE_POSTHOG_KEY`: Press Enter to skip or provide if you have one.

## Step 3: Final Verification
1.  Open the deployed Vercel URL.
2.  Check console logs for any connection errors.
3.  Verify that `onboarding_requests` table exists (via Supabase Dashboard) so the app works correctly.

## Important: Vertex AI
I have updated `backend/.env` and `backend/.env.prod` with your Vertex AI API Key. Ensure `backend/.env.prod` is used during deployment (handled by the script).
