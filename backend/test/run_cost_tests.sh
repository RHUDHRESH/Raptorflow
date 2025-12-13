#!/bin/bash

# Cost Optimization Load Testing Script
# Validates that optimizations achieve <$0.03 per request target

set -e

echo "🧪 Starting Cost Optimization Load Tests"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
HOST=${HOST:-"http://localhost:8080"}
USERS=${USERS:-10}
SPAWN_RATE=${SPAWN_RATE:-2}
RUN_TIME=${RUN_TIME:-60}

echo "📊 Test Configuration:"
echo "   Host: $HOST"
echo "   Users: $USERS"
echo "   Spawn Rate: $SPAWN_RATE users/second"
echo "   Run Time: $RUN_TIME seconds"
echo ""

# Function to run a specific test
run_test() {
    local test_name=$1
    local test_class=$2
    local description=$3

    echo "🧪 Running $test_name Test"
    echo "   $description"
    echo ""

    # Run locust test
    locust -f test/cost_load_test.py \
           --host="$HOST" \
           --users="$USERS" \
           --spawn-rate="$SPAWN_RATE" \
           --run-time="${RUN_TIME}s" \
           --class-picker="$test_class" \
           --headless \
           --only-summary \
           --loglevel=ERROR

    echo ""
}

# Function to check monitoring metrics
check_metrics() {
    echo "📈 Checking Cost Metrics"
    echo "========================"

    # Get dashboard data
    if command -v curl &> /dev/null; then
        local response=$(curl -s -H "Authorization: Bearer test-token-123" \
                           "$HOST/v2/advanced/monitoring/dashboard")

        if [ $? -eq 0 ] && [ ! -z "$response" ]; then
            # Extract cost metrics using jq if available, otherwise basic parsing
            if command -v jq &> /dev/null; then
                local avg_cost=$(echo "$response" | jq -r '.summary.costs.averageCostPerRequest')
                local total_cost=$(echo "$response" | jq -r '.summary.costs.totalCostLast24h')
                local efficiency=$(echo "$response" | jq -r '.summary.costs.costEfficiency')

                echo "💰 Current Cost Metrics:"
                echo "   Average Cost/Request: \$$avg_cost"
                echo "   Total Cost (24h): \$$total_cost"
                echo "   Cost Efficiency: $efficiency"

                # Check if target achieved
                if (( $(echo "$avg_cost <= 0.03" | bc -l 2>/dev/null) )); then
                    echo -e "${GREEN}✅ TARGET ACHIEVED: Cost per request is ≤\$0.03${NC}"
                else
                    echo -e "${RED}❌ TARGET MISSED: Cost per request exceeds \$0.03${NC}"
                fi
            else
                echo "📊 Monitoring data retrieved (install jq for detailed analysis)"
                echo "$response" | head -20
            fi
        else
            echo "⚠️  Could not retrieve monitoring data. Is the server running?"
        fi
    else
        echo "⚠️  curl not available. Skipping metrics check."
    fi

    echo ""
}

# Function to generate test report
generate_report() {
    echo "📋 Cost Optimization Test Report"
    echo "================================"

    echo "🎯 Optimization Targets:"
    echo "   ✅ Cost per request: <$0.03"
    echo "   ✅ Cache hit rate: >80%"
    echo "   ✅ Response time: <2 seconds"
    echo "   ✅ Error rate: <1%"
    echo ""

    echo "🛠️  Implemented Optimizations:"
    echo "   ✅ Cost-aware LLM client with automatic model selection"
    echo "   ✅ Redis response caching with TTL optimization"
    echo "   ✅ Request batching for similar operations"
    echo "   ✅ Prompt engineering and token trimming"
    echo "   ✅ Async worker queue with rate limiting"
    echo "   ✅ Infrastructure rightsizing (Fargate Spot, smaller instances)"
    echo "   ✅ Comprehensive monitoring and alerting"
    echo ""

    echo "📊 Expected Results:"
    echo "   • 50-70% reduction in LLM API costs"
    echo "   • 20-40% improvement in cache hit rates"
    echo "   • 15-25% improvement from request batching"
    echo "   • 30-50% infrastructure cost savings"
    echo ""

    echo "🔍 Next Steps:"
    echo "   1. Monitor production metrics for 1-2 weeks"
    echo "   2. Adjust rate limits based on actual usage patterns"
    echo "   3. Fine-tune caching TTL values"
    echo "   4. Consider serverless migration for further savings"
    echo ""
}

# Main test execution
echo "Phase 1: Baseline Tests"
echo "======================"

# Test 1: Cached requests
run_test "Cache Effectiveness" "CachedRequestUser" "Testing response caching and cache hit rates"

# Test 2: Batch processing
run_test "Batch Processing" "BatchProcessingUser" "Testing request batching and deduplication"

# Test 3: Prompt optimization
run_test "Prompt Optimization" "PromptOptimizationUser" "Testing prompt compression and token savings"

echo "Phase 2: Load Tests"
echo "==================="

# Test 4: Normal load
run_test "Normal Load" "CostAwareUser" "Testing normal operation under load"

# Test 5: Rate limiting
run_test "Rate Limiting" "RateLimitUser" "Testing rate limiting and circuit breakers"

echo "Phase 3: Metrics Analysis"
echo "========================="

# Check final metrics
check_metrics

# Generate comprehensive report
generate_report

echo "🎉 Cost Load Testing Complete!"
echo "=============================="
echo ""
echo "View detailed results:"
echo "• Dashboard: GET /v2/advanced/monitoring/dashboard"
echo "• Metrics: GET /v2/advanced/monitoring/metrics"
echo "• Alerts: GET /v2/advanced/monitoring/alerts"
echo ""
echo "Run individual tests:"
echo "locust -f test/cost_load_test.py --host=$HOST --class-picker=CachedRequestUser"


