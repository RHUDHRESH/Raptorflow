# Phase 2A Performance Testing & Load Testing Guide
## Comprehensive Performance Validation & Optimization

**Generated**: November 27, 2024
**Status**: In Progress
**Scope**: API performance, frontend performance, WebSocket latency, load testing

---

## 📊 Performance SLA Definition

### API Response Time SLA

| Tier | Response Time | Target | Percentile |
|---|---|---|---|
| Critical | <50ms | 50ms | 50th |
| High | <100ms | 100ms | 95th |
| Standard | <200ms | 200ms | 99th |
| Async | <500ms | 500ms | 99.9th |

**Current Target**: All lord APIs <100ms at 95th percentile

### Frontend Performance SLA

| Metric | Target | Method |
|---|---|---|
| First Paint | <1s | Lighthouse |
| First Contentful Paint | <1.5s | Chrome DevTools |
| Time to Interactive | <2s | Lighthouse |
| Page Load Complete | <3s | Waterfall |

### WebSocket Performance SLA

| Metric | Target |
|---|---|
| Connection Latency | <500ms |
| Message Delivery | <50ms |
| Reconnection Time | <1s |
| Subscription Confirmation | <100ms |

---

## 🔬 Performance Testing Setup

### Prerequisites

```bash
# Install performance testing tools
pip install locust requests

# Install frontend performance tools
npm install -g lighthouse
npm install -g web-vitals

# Optional: APM tools
# New Relic, DataDog, or self-hosted Prometheus
```

### Baseline Measurement

```python
import time
import requests

BASE_URL = "http://localhost:8000"

def measure_endpoint(endpoint: str, method: str = "GET"):
    """Measure single endpoint response time"""
    start = time.time()

    if method == "GET":
        response = requests.get(f"{BASE_URL}{endpoint}")
    else:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json={"test": "data"}
        )

    duration_ms = (time.time() - start) * 1000
    return {
        "endpoint": endpoint,
        "method": method,
        "status": response.status_code,
        "duration_ms": duration_ms,
        "within_sla": duration_ms < 100
    }

# Measure all endpoints
endpoints = [
    "/lords/architect/initiatives",
    "/lords/cognition/learning",
    "/lords/strategos/plans",
    "/lords/herald/messages",
    # ... etc
]

results = [measure_endpoint(ep) for ep in endpoints]
```

---

## 🎯 Load Testing Scenarios

### Scenario 1: Normal Load (100 concurrent users)

```python
from locust import HttpUser, task, between

class RaptorFlowUser(HttpUser):
    wait_time = between(1, 5)  # Wait 1-5 seconds between requests

    @task(3)
    def view_initiatives(self):
        self.client.get("/lords/architect/initiatives")

    @task(2)
    def create_initiative(self):
        self.client.post(
            "/lords/architect/initiatives/design",
            json={
                "title": "Test Initiative",
                "description": "Test",
                "timeline_weeks": 8,
                "priority": "high"
            }
        )

    @task(2)
    def view_tasks(self):
        self.client.get("/lords/strategos/tasks")

    @task(1)
    def view_messages(self):
        self.client.get("/lords/herald/messages")
```

### Scenario 2: Peak Load (500 concurrent users)

```python
# Same as above but with more aggressive task weights
class PeakUser(HttpUser):
    wait_time = between(0.5, 2)  # More aggressive

    @task(5)  # Higher task weight
    def view_initiatives(self):
        self.client.get("/lords/architect/initiatives")

    # ... other tasks with increased weights
```

### Scenario 3: Stress Testing (1000+ concurrent users)

```python
# Increase wait_time to 0-1 second
class StressUser(HttpUser):
    wait_time = between(0, 1)

    @task(10)  # Maximum task weight
    def view_initiatives(self):
        self.client.get("/lords/architect/initiatives")

    # ... other high-weight tasks
```

### Running Load Tests

```bash
# Basic load test
locust -f locustfile.py --host=http://localhost:8000

# Headless mode with 100 users, ramp-up 10/s
locust -f locustfile.py --host=http://localhost:8000 \
  --headless -u 100 -r 10 -t 5m

# Generate CSV report
locust -f locustfile.py --host=http://localhost:8000 \
  --headless -u 500 -r 50 -t 10m \
  --csv=results
```

---

## 📈 Performance Metrics

### Key Performance Indicators (KPIs)

| KPI | Target | Method |
|---|---|---|
| P50 Response Time | <50ms | percentile analysis |
| P95 Response Time | <100ms | percentile analysis |
| P99 Response Time | <200ms | percentile analysis |
| Error Rate | <0.1% | error_count / total_requests |
| Throughput | 1000+ req/s | requests / duration |
| CPU Usage | <70% | system monitoring |
| Memory Usage | <80% | system monitoring |
| Database Connection Pool | <90% utilization | pool monitoring |

### Collecting Metrics

```python
import time
from statistics import mean, stdev

class PerformanceCollector:
    def __init__(self):
        self.measurements = []

    def record(self, endpoint: str, duration_ms: float):
        self.measurements.append({
            "endpoint": endpoint,
            "duration_ms": duration_ms,
            "timestamp": time.time()
        })

    def get_percentile(self, percentile: int) -> float:
        """Get Nth percentile response time"""
        sorted_times = sorted([m["duration_ms"] for m in self.measurements])
        index = int(len(sorted_times) * percentile / 100)
        return sorted_times[index]

    def get_stats(self):
        durations = [m["duration_ms"] for m in self.measurements]
        return {
            "count": len(durations),
            "mean": mean(durations),
            "stdev": stdev(durations) if len(durations) > 1 else 0,
            "min": min(durations),
            "max": max(durations),
            "p50": self.get_percentile(50),
            "p95": self.get_percentile(95),
            "p99": self.get_percentile(99),
        }
```

---

## 🚀 API Performance Testing

### Test Case 1: Individual Endpoint Performance

```python
import requests
import statistics

def test_endpoint_sla(endpoint: str, iterations: int = 100):
    """Test if endpoint meets <100ms SLA"""
    measurements = []

    for i in range(iterations):
        start = time.time()
        response = requests.get(f"http://localhost:8000{endpoint}")
        duration_ms = (time.time() - start) * 1000

        measurements.append({
            "duration_ms": duration_ms,
            "status": response.status_code,
            "success": response.status_code == 200
        })

    durations = [m["duration_ms"] for m in measurements]
    p95 = sorted(durations)[int(len(durations) * 0.95)]
    success_rate = sum(1 for m in measurements if m["success"]) / len(measurements)

    return {
        "endpoint": endpoint,
        "iterations": iterations,
        "p95_duration_ms": p95,
        "sla_pass": p95 < 100,
        "success_rate": success_rate * 100,
        "stats": {
            "mean": statistics.mean(durations),
            "median": statistics.median(durations),
            "stdev": statistics.stdev(durations),
            "min": min(durations),
            "max": max(durations),
        }
    }

# Test all lord endpoints
lords = ["architect", "cognition", "strategos", "aesthete", "seer", "arbiter", "herald"]
results = []

for lord in lords:
    result = test_endpoint_sla(f"/lords/{lord}/status")
    results.append(result)
    print(f"✅ {lord}: P95={result['p95_duration_ms']:.2f}ms (SLA: {'PASS' if result['sla_pass'] else 'FAIL'})")
```

### Test Case 2: Complex Query Performance

```python
def test_complex_query_sla():
    """Test complex queries with multiple filters"""
    test_cases = [
        {
            "name": "List initiatives with filters",
            "method": "GET",
            "endpoint": "/lords/architect/initiatives?status=active&priority=high"
        },
        {
            "name": "Get decision with full context",
            "method": "GET",
            "endpoint": "/lords/arbiter/decision/decision_001"
        },
        {
            "name": "Generate report",
            "method": "POST",
            "endpoint": "/lords/herald/reporting/communication-report",
            "payload": {"period_days": 30}
        },
    ]

    for test in test_cases:
        measurements = []

        for i in range(50):
            start = time.time()

            if test["method"] == "GET":
                requests.get(f"http://localhost:8000{test['endpoint']}")
            else:
                requests.post(
                    f"http://localhost:8000{test['endpoint']}",
                    json=test.get("payload", {})
                )

            duration_ms = (time.time() - start) * 1000
            measurements.append(duration_ms)

        p95 = sorted(measurements)[int(len(measurements) * 0.95)]
        print(f"✅ {test['name']}: P95={p95:.2f}ms")
```

### Test Case 3: Concurrent Request Performance

```python
import concurrent.futures

def test_concurrent_performance(endpoint: str, concurrency: int = 10):
    """Test performance under concurrent load"""

    def make_request():
        start = time.time()
        response = requests.get(f"http://localhost:8000{endpoint}")
        return (time.time() - start) * 1000, response.status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(make_request) for _ in range(concurrency)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    durations = [r[0] for r in results]
    success_rate = sum(1 for r in results if r[1] == 200) / len(results)

    return {
        "concurrency": concurrency,
        "p95": sorted(durations)[int(len(durations) * 0.95)],
        "p99": sorted(durations)[int(len(durations) * 0.99)],
        "success_rate": success_rate * 100
    }

# Test with increasing concurrency
for concurrency in [5, 10, 25, 50, 100]:
    result = test_concurrent_performance("/lords/architect/initiatives", concurrency)
    print(f"Concurrency {concurrency}: P95={result['p95']:.2f}ms, Success={result['success_rate']:.1f}%")
```

---

## 🌐 Frontend Performance Testing

### Using Lighthouse

```bash
# Run Lighthouse audit
lighthouse http://localhost:3000/strategy/architect \
  --view

# Generate JSON report
lighthouse http://localhost:3000/strategy/architect \
  --output=json \
  --output-path=report.json

# Performance threshold check
lighthouse http://localhost:3000/strategy/architect \
  --output=json \
  --chrome-flags="--headless" \
  --view
```

### Web Vitals Measurement

```javascript
// Measure Core Web Vitals
import {getCLS, getFID, getFCP, getLCP, getTTFB} from 'web-vitals';

function logWebVitals() {
  getCLS(console.log);  // Cumulative Layout Shift
  getFID(console.log);  // First Input Delay
  getFCP(console.log);  // First Contentful Paint
  getLCP(console.log);  // Largest Contentful Paint
  getTTFB(console.log); // Time to First Byte
}

logWebVitals();
```

### Performance Budget

```javascript
// In src/main.jsx or performance monitoring setup
const performanceBudget = {
  "FCP": 1500,      // First Contentful Paint: 1.5s
  "LCP": 2500,      // Largest Contentful Paint: 2.5s
  "CLS": 0.1,       // Cumulative Layout Shift: 0.1
  "INP": 200,       // Interaction to Next Paint: 200ms
  "TTFB": 500,      // Time to First Byte: 500ms
  "Total": 3000,    // Total load: 3s
};

// Check against budget
function checkPerformanceBudget(metrics) {
  let budgetViolations = [];

  for (const [metric, budget] of Object.entries(performanceBudget)) {
    if (metrics[metric] > budget) {
      budgetViolations.push({
        metric,
        actual: metrics[metric],
        budget,
        exceeded: metrics[metric] - budget
      });
    }
  }

  return budgetViolations;
}
```

---

## ⚡ WebSocket Performance Testing

### Connection Latency Test

```python
import asyncio
import websockets
import time

async def test_websocket_latency():
    """Test WebSocket connection latency"""
    latencies = []

    async with websockets.connect("ws://localhost:8000/ws/lords/architect") as ws:
        for i in range(100):
            start = time.time()

            # Send subscription
            await ws.send('{"type": "ping"}')

            # Wait for pong
            response = await asyncio.wait_for(ws.recv(), timeout=1.0)

            latency_ms = (time.time() - start) * 1000
            latencies.append(latency_ms)

    p95 = sorted(latencies)[int(len(latencies) * 0.95)]
    print(f"WebSocket P95 Latency: {p95:.2f}ms (SLA: {'PASS' if p95 < 50 else 'FAIL'})")

asyncio.run(test_websocket_latency())
```

### Message Throughput Test

```python
async def test_websocket_throughput():
    """Test WebSocket message throughput"""
    message_count = 0
    start_time = time.time()

    async with websockets.connect("ws://localhost:8000/ws/lords/architect") as ws:
        await ws.send('{"type": "subscribe"}')

        # Receive messages for 30 seconds
        while time.time() - start_time < 30:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                message_count += 1
            except asyncio.TimeoutError:
                break

    duration = time.time() - start_time
    throughput = message_count / duration
    print(f"WebSocket Throughput: {throughput:.2f} messages/second")

asyncio.run(test_websocket_throughput())
```

---

## 💾 Database Performance

### Query Performance Monitoring

```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 0.1;  -- 100ms

-- Monitor query execution
EXPLAIN ANALYZE
SELECT * FROM initiatives
WHERE status = 'active' AND workspace_id = $1
ORDER BY created_at DESC;

-- Check index usage
SELECT * FROM pg_stat_user_indexes
WHERE idx_scan < 1;  -- Unused indexes

-- Monitor query stats
SELECT query, calls, mean_time, max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Connection Pool Performance

```python
# Monitor connection pool utilization
from sqlalchemy import event, pool

@event.listens_for(pool.Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    print(f"Pool size: {dbapi_conn.get_backend_pid()}")

@event.listens_for(pool.Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    print("Connection checked out from pool")
```

---

## 📊 Performance Testing Report Template

### Summary

| Metric | Value | Status |
|--------|-------|--------|
| Test Duration | XXX seconds | ✅ |
| Total Requests | XXX | ✅ |
| Failed Requests | X (X.X%) | ✅ |
| Average Response Time | XXms | ✅ |
| P95 Response Time | XXms | ✅ |
| P99 Response Time | XXms | ✅ |
| Max Response Time | XXms | ✅ |
| Throughput | XXX req/s | ✅ |

### By Endpoint

| Endpoint | Count | Avg (ms) | P95 (ms) | P99 (ms) | Error Rate | Status |
|---|---|---|---|---|---|---|
| GET /lords/architect/initiatives | 500 | 45 | 78 | 95 | 0% | ✅ |
| POST /lords/architect/initiatives/design | 250 | 52 | 85 | 110 | 0% | ✅ |
| GET /lords/cognition/learning | 450 | 38 | 65 | 82 | 0% | ✅ |
| ... | ... | ... | ... | ... | ... | ... |

### Load Test Results

| Concurrency | P95 (ms) | P99 (ms) | Error Rate | Status |
|---|---|---|---|---|
| 10 users | 45 | 78 | 0% | ✅ |
| 50 users | 62 | 95 | 0% | ✅ |
| 100 users | 85 | 120 | 0.05% | ✅ |
| 500 users | 150 | 250 | 0.2% | ⚠️ |

### Bottleneck Analysis

- Database query time: 30% of total
- API processing time: 50% of total
- Network latency: 10% of total
- Other: 10% of total

### Recommendations

1. Optimize slow database queries (identified in slow log)
2. Add caching for frequently accessed data
3. Implement connection pooling optimization
4. Consider read replicas for query-heavy endpoints

---

## ✅ Performance Checklist

### Pre-Load Testing

- [ ] Baseline measurements taken for all endpoints
- [ ] Load testing environment matches production
- [ ] Database has production-like data volume
- [ ] Monitoring/APM tools configured
- [ ] Performance budgets defined
- [ ] Acceptance criteria agreed

### Load Testing

- [ ] Normal load test (100 concurrent users) passed
- [ ] Peak load test (500 concurrent users) passed
- [ ] Stress test (1000+ concurrent users) passed
- [ ] Soak test (sustained load) passed
- [ ] Error rate <0.1%
- [ ] P95 response time <100ms

### Frontend Performance

- [ ] Lighthouse score ≥90
- [ ] FCP <1.5s
- [ ] LCP <2.5s
- [ ] CLS <0.1
- [ ] TTI <2s
- [ ] WebSocket latency <50ms

### Database Performance

- [ ] Query response time <50ms (95th percentile)
- [ ] Connection pool efficiency >90%
- [ ] No slow queries in logs
- [ ] Indexes are being used
- [ ] Replication lag <100ms

---

**Status**: In Progress
**Last Updated**: November 27, 2024
**Next Steps**: Execute performance tests and optimize as needed
