#!/bin/bash

# Production Deployment Script for Free Web Search
# Deploys enterprise-grade search service with monitoring

set -e

echo "🚀 Deploying Production Free Web Search Service"
echo "================================================"

# Configuration
PROJECT_NAME="free-search"
DOCKER_NETWORK="search-network"
ENVIRONMENT=${ENVIRONMENT:-production}

echo "📋 Configuration:"
echo "  Project: $PROJECT_NAME"
echo "  Environment: $ENVIRONMENT"
echo "  Network: $DOCKER_NETWORK"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs/nginx
mkdir -p data/prometheus
mkdir -p data/grafana
mkdir -p data/redis
mkdir -p data/alertmanager
mkdir -p config

# Set permissions
echo "🔐 Setting permissions..."
chmod 755 logs data config
chmod -R 755 data/*
chmod -R 755 logs/*

# Create Docker network
echo "🌐 Creating Docker network..."
docker network create $DOCKER_NETWORK 2>/dev/null || echo "Network already exists"

# Build and deploy services
echo "🐳 Building and deploying services..."

# Stop existing services
echo "⏹️  Stopping existing services..."
docker-compose -f docker-compose.search.yml down --remove-orphans || true

# Build images
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.search.yml build

# Start services
echo "▶️  Starting services..."
docker-compose -f docker-compose.search.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Health checks
echo "🏥 Checking service health..."

# Check main search service
echo "  🔍 Checking search service..."
for i in {1..10}; do
    if curl -f http://localhost:8084/health > /dev/null 2>&1; then
        echo "  ✅ Search service is healthy"
        break
    else
        echo "  ⏳ Waiting for search service... ($i/10)"
        sleep 5
    fi
done

# Check Nginx
echo "  🌐 Checking Nginx..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "  ✅ Nginx is healthy"
else
    echo "  ❌ Nginx health check failed"
fi

# Check Redis
echo "  💾 Checking Redis..."
if docker exec search-redis redis-cli ping > /dev/null 2>&1; then
    echo "  ✅ Redis is healthy"
else
    echo "  ❌ Redis health check failed"
fi

# Check Prometheus
echo "  📊 Checking Prometheus..."
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "  ✅ Prometheus is healthy"
else
    echo "  ❌ Prometheus health check failed"
fi

# Check Grafana
echo "  📈 Checking Grafana..."
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "  ✅ Grafana is healthy"
else
    echo "  ❌ Grafana health check failed"
fi

# Test search functionality
echo "🔍 Testing search functionality..."
SEARCH_RESPONSE=$(curl -s "http://localhost/search?q=test+query&engines=duckduckgo&max_results=1")
if echo "$SEARCH_RESPONSE" | grep -q '"status"'; then
    echo "  ✅ Search API is working"
else
    echo "  ❌ Search API test failed"
fi

# Show service status
echo ""
echo "📊 Service Status:"
echo "=================="
docker-compose -f docker-compose.search.yml ps

# Show URLs
echo ""
echo "🌐 Service URLs:"
echo "================"
echo "  Search API:     http://localhost/search"
echo "  Health Check:   http://localhost/health"
echo "  Metrics:        http://localhost:8084/metrics"
echo "  Prometheus:     http://localhost:9090"
echo "  Grafana:        http://localhost:3000 (admin/admin123)"
echo "  Redis:          localhost:6379"

# Show logs location
echo ""
echo "📝 Logs:"
echo "========"
echo "  Search service: docker logs -f search-free-search"
echo "  Nginx:         docker logs -f search-nginx"
echo "  Prometheus:    docker logs -f search-prometheus"
echo "  Grafana:       docker logs -f search-grafana"
echo "  Redis:         docker logs -f search-redis"

# Show useful commands
echo ""
echo "🔧 Useful Commands:"
echo "=================="
echo "  View logs:       docker-compose -f docker-compose.search.yml logs -f"
echo "  Restart service: docker-compose -f docker-compose.search.yml restart"
echo "  Stop services:   docker-compose -f docker-compose.search.yml down"
echo "  Scale service:   docker-compose -f docker-compose.search.yml up -d --scale free-search=3"
echo "  Update service:  docker-compose -f docker-compose.search.yml pull && docker-compose -f docker-compose.search.yml up -d"

# Performance test
echo ""
echo "⚡ Running performance test..."
for i in {1..5}; do
    START_TIME=$(date +%s.%N)
    curl -s "http://localhost/search?q=python+scraping&engines=duckduckgo&max_results=3" > /dev/null
    END_TIME=$(date +%s.%N)
    DURATION=$(echo "$END_TIME - $START_TIME" | bc)
    echo "  Request $i: ${DURATION}s"
done

echo ""
echo "🎉 Production Free Web Search Service deployed successfully!"
echo "=========================================================="
echo ""
echo "📊 Monitoring Dashboard: http://localhost:3000"
echo "🔍 Search API: http://localhost/search"
echo "📈 Metrics: http://localhost:9090"
echo ""
echo "🚀 Your production-grade free search service is ready!"
