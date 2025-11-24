@echo off
REM Deploy RaptorFlow Backend to Google Cloud Run (Windows)

setlocal enabledelayedexpansion

echo.
echo 🚀 RaptorFlow Backend Deployment to Cloud Run
echo ==============================================

REM Configuration
set PROJECT_ID=raptorflow-477017
set SERVICE_NAME=raptorflow-backend
set REGION=us-central1
set IMAGE_NAME=gcr.io/%PROJECT_ID%/%SERVICE_NAME%

REM Check if gcloud is installed
where gcloud >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Google Cloud SDK not found. Install from: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker not found. Install from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Get project directory
cd /d "%~dp0"

echo 📝 Authenticating with Google Cloud...
call gcloud auth login
call gcloud config set project %PROJECT_ID%

echo ⚙️  Enabling required APIs...
call gcloud services enable run.googleapis.com
call gcloud services enable containerregistry.googleapis.com
call gcloud services enable cloudbuild.googleapis.com

REM Configure environment variables
echo 🔐 Setting up environment variables...
echo.
echo Create backend\.env.prod with your production secrets:
echo.
echo ENVIRONMENT=production
echo DEBUG=False
echo LOG_LEVEL=WARNING
echo GOOGLE_CLOUD_PROJECT=%PROJECT_ID%
echo SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
echo SUPABASE_SERVICE_KEY=your_service_key_here
echo SECRET_KEY=your-strong-random-string-here
echo.
pause

if not exist "backend\.env.prod" (
    echo ❌ backend\.env.prod not found!
    pause
    exit /b 1
)

echo 🐳 Building Docker image...
call docker build -f Dockerfile.cloudrun -t %IMAGE_NAME%:latest .
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker build failed!
    pause
    exit /b 1
)

echo 🔼 Pushing image to Google Container Registry...
call docker push %IMAGE_NAME%:latest
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker push failed!
    pause
    exit /b 1
)

echo ☁️  Deploying to Cloud Run...
call gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_NAME%:latest ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --memory 1Gi ^
    --cpu 1 ^
    --timeout 3600 ^
    --max-instances 10 ^
    --env-vars-file backend\.env.prod

echo.
echo ✅ Backend deployed successfully!
echo.
echo 📊 Service URL:
call gcloud run services describe %SERVICE_NAME% --region %REGION% --format="value(status.url)"
echo.
echo 📋 View logs:
echo gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --limit 50
echo.
pause
