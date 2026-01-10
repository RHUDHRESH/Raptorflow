@echo off
REM Local Deployment Script for Windows
REM Usage: deploy_local.bat

echo [INFO] Starting local deployment...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    exit /b 1
)

echo [SUCCESS] Docker is running

REM Build and run with Docker Compose
echo [INFO] Building and starting containers...
docker-compose -f docker-compose.production.yml up -d --build

if errorlevel 1 (
    echo [ERROR] Docker Compose deployment failed
    exit /b 1
)

echo [SUCCESS] Local deployment completed!
echo.
echo 🚀 Ultra-Fast Scraper is now running locally!
echo 📊 Dashboard: http://localhost:8082
echo 🔍 Health: http://localhost:8082/health
echo 📈 Analytics: http://localhost:8082/performance/analytics
echo 💰 Cost Tracking: http://localhost:8080/cost/analytics
echo 📊 Grafana: http://localhost:3000 (admin/admin123)
echo 📈 Prometheus: http://localhost:9090
echo.
echo [INFO] Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check health
echo [INFO] Checking service health...
curl -f "http://localhost:8082/health" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ultra-fast scraper health check failed, but containers are running
) else (
    echo [SUCCESS] Ultra-fast scraper is healthy
)

echo.
echo [INFO] To stop services, run: docker-compose -f docker-compose.production.yml down
echo [INFO] To view logs, run: docker-compose -f docker-compose.production.yml logs -f

endlocal
