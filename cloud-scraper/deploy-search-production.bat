@echo off
REM Production Deployment Script for Free Web Search (Windows)
REM Deploys enterprise-grade search service with monitoring

echo 🚀 Deploying Production Free Web Search Service
echo ================================================

REM Configuration
set PROJECT_NAME=free-search
set DOCKER_NETWORK=search-network
set ENVIRONMENT=production

echo 📋 Configuration:
echo   Project: %PROJECT_NAME%
echo   Environment: %ENVIRONMENT%
echo   Network: %DOCKER_NETWORK%

REM Create necessary directories
echo 📁 Creating directories...
if not exist logs\nnginx mkdir logs\nnginx
if not exist data\prometheus mkdir data\prometheus
if not exist data\grafana mkdir data\grafana
if not exist data\redis mkdir data\redis
if not exist data\alertmanager mkdir data\alertmanager
if not exist config mkdir config

REM Create Docker network
echo 🌐 Creating Docker network...
docker network create %DOCKER_NETWORK% 2>nul || echo Network already exists

REM Stop existing services
echo ⏹️  Stopping existing services...
docker-compose -f docker-compose.search.yml down --remove-orphans 2>nul

REM Build images
echo 🔨 Building Docker images...
docker-compose -f docker-compose.search.yml build

REM Start services
echo ▶️  Starting services...
docker-compose -f docker-compose.search.yml up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Health checks
echo 🏥 Checking service health...

REM Check main search service
echo   🔍 Checking search service...
for /l %%i in (1,1,10) do (
    curl -f http://localhost:8084/health >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✅ Search service is healthy
        goto :search_ok
    ) else (
        echo   ⏳ Waiting for search service... (%%i/10)
        timeout /t 5 /nobreak >nul
    )
)
echo   ❌ Search service health check failed
:search_ok

REM Check Nginx
echo   🌐 Checking Nginx...
curl -f http://localhost/health >nul 2>&1
if !errorlevel! equ 0 (
    echo   ✅ Nginx is healthy
) else (
    echo   ❌ Nginx health check failed
)

REM Check Redis
echo   💾 Checking Redis...
docker exec search-redis redis-cli ping >nul 2>&1
if !errorlevel! equ 0 (
    echo   ✅ Redis is healthy
) else (
    echo   ❌ Redis health check failed
)

REM Check Prometheus
echo   📊 Checking Prometheus...
curl -f http://localhost:9090/-/healthy >nul 2>&1
if !errorlevel! equ 0 (
    echo   ✅ Prometheus is healthy
) else (
    echo   ❌ Prometheus health check failed
)

REM Check Grafana
echo   📈 Checking Grafana...
curl -f http://localhost:3000/api/health >nul 2>&1
if !errorlevel! equ 0 (
    echo   ✅ Grafana is healthy
) else (
    echo   ❌ Grafana health check failed
)

REM Test search functionality
echo 🔍 Testing search functionality...
curl -s "http://localhost/search?q=test+query&engines=duckduckgo&max_results=1" | findstr "status" >nul
if !errorlevel! equ 0 (
    echo   ✅ Search API is working
) else (
    echo   ❌ Search API test failed
)

REM Show service status
echo.
echo 📊 Service Status:
echo =================
docker-compose -f docker-compose.search.yml ps

REM Show URLs
echo.
echo 🌐 Service URLs:
echo ================
echo   Search API:     http://localhost/search
echo   Health Check:   http://localhost/health
echo   Metrics:        http://localhost:8084/metrics
echo   Prometheus:     http://localhost:9090
echo   Grafana:        http://localhost:3000 (admin/admin123)
echo   Redis:          localhost:6379

REM Show logs location
echo.
echo 📝 Logs:
echo ========
echo   Search service: docker logs -f search-free-search
echo   Nginx:         docker logs -f search-nginx
echo   Prometheus:    docker logs -f search-prometheus
echo   Grafana:       docker logs -f search-grafana
echo   Redis:         docker logs -f search-redis

REM Show useful commands
echo.
echo 🔧 Useful Commands:
echo ==================
echo   View logs:       docker-compose -f docker-compose.search.yml logs -f
echo   Restart service: docker-compose -f docker-compose.search.yml restart
echo   Stop services:   docker-compose -f docker-compose.search.yml down
echo   Scale service:   docker-compose -f docker-compose.search.yml up -d --scale free-search=3
echo   Update service:  docker-compose -f docker-compose.search.yml pull ^&^& docker-compose -f docker-compose.search.yml up -d

echo.
echo 🎉 Production Free Web Search Service deployed successfully!
echo ==========================================================
echo.
echo 📊 Monitoring Dashboard: http://localhost:3000
echo 🔍 Search API: http://localhost/search
echo 📈 Metrics: http://localhost:9090
echo.
echo 🚀 Your production-grade free search service is ready!
pause
