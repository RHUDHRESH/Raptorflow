#!/bin/bash

# Healthcheck script for RaptorFlow infrastructure
# Waits for all services to be ready before proceeding

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MAX_WAIT=300  # 5 minutes max wait time
INTERVAL=2    # Check every 2 seconds

echo -e "${BLUE}🔍 Starting health checks for RaptorFlow infrastructure${NC}"
echo -e "${BLUE}Maximum wait time: ${MAX_WAIT}s${NC}"
echo ""

# Function to check if a command succeeds
check_service() {
    local service_name="$1"
    local command="$2"
    local max_attempts="$3"

    echo -e "${YELLOW}⏳ Waiting for $service_name...${NC}"

    local attempts=0
    while [ $attempts -lt $max_attempts ]; do
        if eval "$command" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is healthy${NC}"
            return 0
        fi

        attempts=$((attempts + 1))
        if [ $attempts -lt $max_attempts ]; then
            echo -e "${YELLOW}⏳ $service_name not ready (attempt $attempts/$max_attempts)${NC}"
            sleep $INTERVAL
        fi
    done

    echo -e "${RED}❌ $service_name failed to become healthy${NC}"
    return 1
}

# Calculate max attempts
max_attempts=$((MAX_WAIT / INTERVAL))

# Check services in dependency order
echo -e "${BLUE}Checking database services...${NC}"

# Postgres
check_service "PostgreSQL" "pg_isready -h localhost -p 5432 -U raptorflow -d raptorflow" $max_attempts

# PgBouncer
check_service "PgBouncer" "nc -z localhost 6432" $max_attempts

echo ""
echo -e "${BLUE}Checking cache and vector services...${NC}"

# Dragonfly (Redis)
check_service "Dragonfly" "redis-cli -h localhost -p 6379 ping | grep -q PONG" $max_attempts

# Qdrant
check_service "Qdrant" "curl -s http://localhost:6333/readyz | grep -q 'true'" $max_attempts

echo ""
echo -e "${GREEN}🎉 All infrastructure services are healthy!${NC}"
echo ""
echo -e "${BLUE}You can now start the API server:${NC}"
echo -e "  cargo run -p raptorflow-api"
echo ""
echo -e "${BLUE}Or run the full stack:${NC}"
echo -e "  pnpm dev"