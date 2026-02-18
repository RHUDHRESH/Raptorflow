#!/bin/bash
set -e

VERSION=${1:-latest}

if [ -z "$VERSION" ]; then
    echo "Usage: ./deploy.sh <version_tag>"
    echo "Example: ./deploy.sh v1.2.3"
    exit 1
fi

echo "Starting deployment for version $VERSION"

echo "Building new images..."
docker-compose -f docker-compose.prod.yml build

echo "Starting new containers..."
docker-compose -f docker-compose.prod.yml up -d

echo "Running health checks..."
for i in {1..30}; do
    if curl -fsS http://localhost:8000/health/ready > /dev/null 2>&1; then
        echo "Health check passed"
        break
    fi
    echo "Waiting for health check... ($i/30)"
    sleep 2
done

if ! curl -fsS http://localhost:8000/health/ready > /dev/null 2>&1; then
    echo "Health check failed!"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

echo "Reloading Nginx..."
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo "Deployment complete!"
