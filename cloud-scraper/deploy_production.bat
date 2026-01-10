@echo off
REM Production Deployment Script for Windows
REM Usage: deploy_production.bat [command] [environment]

setlocal enabledelayedexpansion

set "ENVIRONMENT=%~2"
if "%ENVIRONMENT%"=="" set "ENVIRONMENT=production"
set "PROJECT_NAME=raptorflow-scraper"
set "REGION=us-central1"
set "SERVICE_NAME=ultra-fast-scraper"

echo [INFO] Starting deployment to %ENVIRONMENT%...

REM Check prerequisites
echo [INFO] Checking prerequisites...

where gcloud >nul 2>&1
if errorlevel 1 (
    echo [ERROR] gcloud CLI is not installed. Please install it first.
    exit /b 1
)

where docker >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install it first.
    exit /b 1
)

echo [SUCCESS] Prerequisites check passed

REM Build Docker image
echo [INFO] Building Docker image...
docker build -f Dockerfile.production -t gcr.io/$(gcloud config get-value project)/%PROJECT_NAME%:latest .
if errorlevel 1 (
    echo [ERROR] Docker build failed
    exit /b 1
)
echo [SUCCESS] Docker image built successfully

REM Push to Google Container Registry
echo [INFO] Pushing image to Google Container Registry...
for /f "delims=" %%i in ('gcloud config get-value project') do set "PROJECT_ID=%%i"
set "IMAGE_TAG=gcr.io/%PROJECT_ID%/%PROJECT_NAME%:latest"

docker push %IMAGE_TAG%
if errorlevel 1 (
    echo [ERROR] Docker push failed
    exit /b 1
)
echo [SUCCESS] Image pushed to GCR

REM Deploy to Cloud Run
echo [INFO] Deploying to Cloud Run...
gcloud run deploy %SERVICE_NAME% ^
    --image=%IMAGE_TAG% ^
    --region=%REGION% ^
    --platform=managed ^
    --allow-unauthenticated ^
    --memory=1Gi ^
    --cpu=1 ^
    --timeout=300 ^
    --concurrency=100 ^
    --max-instances=10 ^
    --min-instances=0 ^
    --set-env-vars="ENVIRONMENT=%ENVIRONMENT%" ^
    --set-env-vars="LOG_LEVEL=info" ^
    --set-env-vars="MAX_WORKERS=8" ^
    --set-env-vars="CONNECTION_POOL_SIZE=100" ^
    --set-env-vars="REQUEST_TIMEOUT=10" ^
    --set-env-vars="COST_TRACKING=true" ^
    --set-env-vars="BUDGET_ALERTS=true" ^
    --set-env-vars="MAX_COST_PER_HOUR=10.0" ^
    --set-env-vars="COMPLIANCE_CHECKING=true" ^
    --set-env-vars="ROBOTS_TXT_RESPECT=true" ^
    --set-env-vars="RATE_LIMITING=true"

if errorlevel 1 (
    echo [ERROR] Cloud Run deployment failed
    exit /b 1
)
echo [SUCCESS] Deployed to Cloud Run

REM Get service URL
echo [INFO] Getting service URL...
for /f "delims=" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)"') do set "SERVICE_URL=%%i"
echo [SUCCESS] Service deployed at: %SERVICE_URL%

REM Health check
echo [INFO] Running health check...
timeout /t 10 /nobreak >nul

curl -f "%SERVICE_URL%/health" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Health check failed
    exit /b 1
)
echo [SUCCESS] Health check passed

echo.
echo [SUCCESS] Deployment completed successfully!
echo.
echo 🚀 Ultra-Fast Scraper is now live!
echo 📊 Dashboard: %SERVICE_URL%
echo 🔍 Health: %SERVICE_URL%/health
echo 📈 Analytics: %SERVICE_URL%/performance/analytics
echo 💰 Cost Tracking: %SERVICE_URL%/cost/analytics

endlocal
