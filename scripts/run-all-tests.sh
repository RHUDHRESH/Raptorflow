#!/bin/bash

###############################################################################
# RaptorFlow 2.0 - Comprehensive Test Suite Runner
# Runs all backend and frontend tests with coverage reporting
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         RaptorFlow 2.0 - Comprehensive Test Suite          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

###############################################################################
# 1. Backend Tests
###############################################################################

echo -e "${YELLOW}[1/4] Running Backend Unit Tests...${NC}"
cd /home/user/Raptorflow

# Install backend dependencies if needed
if [ ! -d "backend/.venv" ]; then
    echo "Installing backend dependencies..."
    python -m venv backend/.venv
    source backend/.venv/bin/activate
    pip install -q -r backend/requirements.txt
else
    source backend/.venv/bin/activate 2>/dev/null || true
fi

# Run backend tests with coverage
echo "Running pytest with coverage..."
cd backend

if pytest --cov=. --cov-report=term --cov-report=html --cov-report=json -v 2>&1 | tee test-output.log; then
    echo -e "${GREEN}✓ Backend tests passed${NC}"
    BACKEND_COVERAGE=$(python -c "import json; data=json.load(open('coverage.json')); print(f\"{data['totals']['percent_covered']:.1f}\")")
    echo -e "${GREEN}Backend Coverage: ${BACKEND_COVERAGE}%${NC}"
else
    echo -e "${RED}✗ Backend tests failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

cd ..

###############################################################################
# 2. Backend Integration Tests
###############################################################################

echo -e "\n${YELLOW}[2/4] Running Backend Integration Tests...${NC}"
cd backend

if pytest tests/test_integration_e2e.py -v 2>&1 | tee integration-test-output.log; then
    echo -e "${GREEN}✓ Integration tests passed${NC}"
else
    echo -e "${RED}✗ Integration tests failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

cd ..

###############################################################################
# 3. Frontend Unit Tests
###############################################################################

echo -e "\n${YELLOW}[3/4] Running Frontend Unit Tests...${NC}"

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install --silent
fi

# Run frontend tests with coverage
if npm run test:coverage -- --run 2>&1 | tee frontend-test-output.log; then
    echo -e "${GREEN}✓ Frontend tests passed${NC}"
else
    echo -e "${RED}✗ Frontend tests failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

###############################################################################
# 4. Linting & Code Quality
###############################################################################

echo -e "\n${YELLOW}[4/4] Running Code Quality Checks...${NC}"

# Backend linting
echo "Checking backend code quality..."
if command -v black &> /dev/null; then
    black --check backend --quiet && echo -e "${GREEN}✓ Black formatting check passed${NC}" || echo -e "${YELLOW}⚠ Black formatting issues found${NC}"
fi

if command -v ruff &> /dev/null; then
    ruff check backend --quiet && echo -e "${GREEN}✓ Ruff linting passed${NC}" || echo -e "${YELLOW}⚠ Ruff linting issues found${NC}"
fi

# Frontend linting
echo "Checking frontend code quality..."
if npm run lint -- --max-warnings 0 2>&1 | grep -q "0 errors"; then
    echo -e "${GREEN}✓ ESLint check passed${NC}"
else
    echo -e "${YELLOW}⚠ ESLint issues found${NC}"
fi

###############################################################################
# Test Summary
###############################################################################

echo -e "\n${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                      Test Summary                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

if [ -f "backend/coverage.json" ]; then
    echo "Backend Coverage:"
    python3 << 'EOF'
import json
with open('backend/coverage.json') as f:
    data = json.load(f)
    print(f"  Total Coverage: {data['totals']['percent_covered']:.2f}%")
    print(f"  Lines Covered: {data['totals']['covered_lines']}/{data['totals']['num_statements']}")
    print(f"  Missing Lines: {data['totals']['missing_lines']}")
EOF
fi

echo ""
echo "Test Reports Generated:"
echo "  - Backend Coverage: backend/htmlcov/index.html"
echo "  - Backend JSON: backend/coverage.json"
echo "  - Frontend Coverage: coverage/index.html"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════════╗"
    echo "║              ✓ ALL TESTS PASSED SUCCESSFULLY                ║"
    echo "╚══════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "\n${RED}╔══════════════════════════════════════════════════════════════╗"
    echo "║              ✗ SOME TESTS FAILED                            ║"
    echo "╚══════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
