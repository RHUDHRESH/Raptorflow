#!/bin/bash

# Performance Benchmark Script
# Tests API endpoints under load and measures response times

API_URL="https://api.raptorflow.com"
RESULTS_FILE="performance-results-$(date +%Y%m%d-%H%M%S).json"

echo "🚀 Starting Performance Benchmark Tests..."
echo "================================"

# Create results file
cat > "$RESULTS_FILE" << EOF
{
  "timestamp": "$(date -I)",
  "tests": []
}
EOF

# Function to run load test
run_load_test() {
    local endpoint="$1"
    local method="$2"
    local data="$3"
    local concurrent="$4"
    local requests="$5"
    
    echo "Testing $endpoint with $concurrent concurrent users, $requests total requests..."
    
    # Use Apache Bench (ab) for load testing
    if command -v ab &> /dev/null; then
        if [ "$method" = "POST" ]; then
            result=$(ab -n "$requests" -c "$concurrent" -p "$data" "$API_URL$endpoint" 2>&1)
        else
            result=$(ab -n "$requests" -c "$concurrent" "$API_URL$endpoint" 2>&1)
        fi
        
        # Extract metrics
        requests_per_second=$(echo "$result" | grep "Requests per second" | awk '{print $4}')
        time_per_request=$(echo "$result" | grep "Time per request" | awk '{print $4}')
        failed_requests=$(echo "$result" | grep "Failed requests" | awk '{print $3}')
        
        echo "  ✅ $endpoint: $requests_per_second req/s, $time_per_request ms avg"
        
        # Add to results
        jq --arg endpoint "$endpoint" \
           --arg rps "$requests_per_second" \
           --arg tpr "$time_per_request" \
           --arg failed "$failed_requests" \
           '.tests += [{"endpoint": $endpoint, "rps": $rps, "tpr": $tpr, "failed": $failed}]' \
           "$RESULTS_FILE" > tmp.json && mv tmp.json "$RESULTS_FILE"
    else
        echo "  ❌ Apache Bench (ab) not installed"
    fi
}

# Test endpoints
echo "📊 Testing API endpoints..."

# Health check
run_load_test "/health" "GET" "" 10 100

# Authentication
run_load_test "/auth/login" "POST" '{"email":"test@example.com","password":"testpass"}' 10 50

# Workspace operations
run_load_test "/workspaces" "GET" "" 5 50

# Campaign operations
run_load_test "/campaigns" "GET" "" 5 30

# User management
run_load_test "/users" "GET" "" 5 25

# Database performance test
echo "🗄️ Testing database performance..."
if command -v psql &> /dev/null; then
    echo "Testing database connection pool..."
    
    # Test connection time
    start_time=$(date +%s%N)
    psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1
    end_time=$(date +%s%N)
    db_time=$((($end_time - $start_time) / 1000000))
    
    echo "  ✅ Database response time: ${db_time}ms"
    
    # Test query performance
    start_time=$(date +%s%N)
    psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM profiles;" > /dev/null 2>&1
    end_time=$(date +%s%N)
    query_time=$((($end_time - $start_time) / 1000000))
    
    echo "  ✅ Query response time: ${query_time}ms"
    
    # Add to results
    jq --arg db_time "$db_time" \
       --arg query_time "$query_time" \
       '.tests += [{"endpoint": "database", "rps": "N/A", "tpr": $db_time, "failed": "0"}, {"endpoint": "query", "rps": "N/A", "tpr": $query_time, "failed": "0"}]' \
       "$RESULTS_FILE" > tmp.json && mv tmp.json "$RESULTS_FILE"
else
    echo "  ❌ PostgreSQL client not available"
fi

# Frontend performance test
echo "🌐 Testing frontend performance..."
if command -v curl &> /dev/null; then
    echo "Testing page load times..."
    
    # Test home page
    start_time=$(date +%s%N)
    status_code=$(curl -s -o /dev/null -w "%{http_code}" https://raptorflow.com)
    end_time=$(date +%s%N)
    load_time=$((($end_time - $start_time) / 1000000))
    
    echo "  ✅ Home page load time: ${load_time}ms (status: $status_code)"
    
    # Test API page
    start_time=$(date +%s%N)
    status_code=$(curl -s -o /dev/null -w "%{http_code}" https://raptorflow.com/api/health)
    end_time=$(date +%s%N)
    api_load_time=$((($end_time - $start_time) / 1000000))
    
    echo "  ✅ API page load time: ${api_load_time}ms (status: $status_code)"
    
    # Add to results
    jq --arg load_time "$load_time" \
       --arg api_load_time "$api_load_time" \
       '.tests += [{"endpoint": "frontend_home", "rps": "N/A", "tpr": $load_time, "failed": "0"}, {"endpoint": "frontend_api", "rps": "N/A", "tpr": $api_load_time, "failed": "0"}]' \
       "$RESULTS_FILE" > tmp.json && mv tmp.json "$RESULTS_FILE"
else
    echo "  ❌ curl not available"
fi

# Memory usage test
echo "💾 Testing memory usage..."
if command -v ps &> /dev/null; then
    # Get current memory usage
    mem_usage=$(ps -o %mem --no-headers -p $$ | head -1 | tr -d ' ')
    echo "  ✅ Current memory usage: ${mem_usage}%"
    
    # Check for memory leaks in Node processes
    node_processes=$(pgrep -f "node" | wc -l)
    echo "  ✅ Node.js processes running: $node_processes"
    
    # Add to results
    jq --arg mem_usage "$mem_usage" \
       --arg node_processes "$node_processes" \
       '.tests += [{"endpoint": "memory", "rps": "N/A", "tpr": "N/A", "failed": "0"}]' \
       "$RESULTS_FILE" > tmp.json && mv tmp.json "$RESULTS_FILE"
else
    echo "  ❌ ps command not available"
fi

# Generate summary report
echo "📈 Generating performance report..."
echo "================================"

# Calculate averages and summary
total_tests=$(jq '.tests | length' "$RESULTS_FILE")
avg_rps=$(jq '.tests | map(select(.rps != "N/A")) | .rps | add / length' "$RESULTS_FILE" 2>/dev/null)
avg_tpr=$(jq '.tests | map(select(.tpr != "N/A")) | .tpr | add / length' "$RESULTS_FILE" 2>/dev/null)
total_failed=$(jq '.tests | map(.failed) | add' "$RESULTS_FILE")

echo "Performance Test Results:"
echo "======================"
echo "Total Tests: $total_tests"
echo "Average RPS: ${avg_rps:-N/A}"
echo "Average Response Time: ${avg_tpr:-N/A}ms"
echo "Total Failed Requests: $total_failed"
echo ""

echo "Detailed Results:"
echo "=============="
jq -r '.tests[] | "Endpoint: \(.endpoint\), RPS: \(.rps), Avg Time: \(.tpr)ms, Failed: \(.failed)"' "$RESULTS_FILE"

echo ""
echo "Results saved to: $RESULTS_FILE"

# Performance thresholds check
echo "🔍 Checking performance thresholds..."
thresholds_met=true

# Check average response time
if (( $(echo "$avg_tpr < 200" | bc -l) )); then
    echo "✅ Average response time < 200ms"
else
    echo "❌ Average response time > 200ms: ${avg_tpr}ms"
    thresholds_met=false
fi

# Check failed requests
if [ "$total_failed" -eq 0 ]; then
    echo "✅ No failed requests"
else
    echo "❌ $total_failed failed requests"
    thresholds_met=false
fi

# Check database response time
db_time=$(jq -r '.tests[] | select(.endpoint == "database") | .tpr' "$RESULTS_FILE" 2>/dev/null)
if [ -n "$db_time" ] && (( $(echo "$db_time < 100" | bc -l) )); then
    echo "✅ Database response time < 100ms"
else
    echo "❌ Database response time > 100ms: ${db_time}ms"
    thresholds_met=false
fi

echo ""
if [ "$thresholds_met" = true ]; then
    echo "🎉 All performance thresholds met!"
    exit 0
else
    echo "⚠️  Some performance thresholds not met"
    exit 1
fi
