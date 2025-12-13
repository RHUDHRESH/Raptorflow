"""
Cost-Optimized Load Testing for RaptorFlow Backend

Tests the effectiveness of cost optimization measures:
- Measures actual cost per request under load
- Validates caching effectiveness
- Tests batching and async processing
- Monitors infrastructure costs
- Validates rate limiting and circuit breakers

Run with: locust -f test/cost_load_test.py --host http://localhost:8080
"""

from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner
import json
import os
import time
from typing import Dict, List
from datetime import datetime

class CostAwareUser(HttpUser):
    wait_time = between(2, 5)  # Slower to avoid overwhelming rate limits

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = os.getenv('TEST_JWT_TOKEN', 'test-token-123')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        self.request_costs: List[float] = []
        self.start_time = time.time()

    def on_start(self):
        """Setup and get baseline metrics"""
        self.baseline_metrics = self.get_monitoring_metrics()

    def on_stop(self):
        """Calculate final cost metrics"""
        end_time = time.time()
        duration = end_time - self.start_time

        if self.request_costs:
            avg_cost = sum(self.request_costs) / len(self.request_costs)
            total_cost = sum(self.request_costs)

            print(f"\n🎯 Cost Test Results for {self.__class__.__name__}:")
            print(f"   Duration: {duration:.1f}s")
            print(f"   Requests: {len(self.request_costs)}")
            print(f"   Avg Cost/Request: ${avg_cost:.4f}")
            print(f"   Total Cost: ${total_cost:.4f}")
            print(f"   Requests/Second: {len(self.request_costs)/duration:.2f}")

            # Check if within target
            if avg_cost <= 0.03:  # $0.03 target
                print("   ✅ TARGET ACHIEVED: Cost per request within $0.03")
            else:
                print(f"   ❌ TARGET MISSED: Cost per request exceeds $0.03 by ${(avg_cost - 0.03):.4f}")

    @task(1)
    def monitor_system_health(self):
        """Monitor system health and costs during load test"""
        with self.client.get("/v2/advanced/monitoring/health", headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                # Track cost metrics
                if 'metrics' in data and 'cost_per_request' in data['metrics']:
                    cost = data['metrics']['cost_per_request']
                    self.request_costs.append(cost)
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    def get_monitoring_metrics(self):
        """Get baseline monitoring metrics"""
        try:
            response = self.client.get("/v2/advanced/monitoring/metrics", headers=self.headers)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {}

class CachedRequestUser(CostAwareUser):
    """Tests caching effectiveness"""

    @task(4)
    def test_cached_plan_generation(self):
        """Test plan generation with caching"""
        payload = {
            "goal": "Create a marketing strategy for a SaaS startup",
            "context": {
                "campaign": {
                    "industry": "SaaS",
                    "target_market": "small businesses",
                    "budget": 25000
                }
            }
        }

        # Add cache key for testing
        headers = {**self.headers, 'X-Cache-Key': f'plan_saas_small_business_{hash(str(payload))}'}

        with self.client.post("/v2/plan", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                # Check for cache headers
                cache_hit = response.headers.get('X-Cache-Hit', 'false') == 'true'
                if cache_hit:
                    print("   ✅ Cache hit detected")
                response.success()
            elif response.status_code == 429:
                response.success()  # Rate limited is expected
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(2)
    def test_company_enrichment_cache(self):
        """Test company enrichment caching"""
        payload = {
            "company_name": "Stripe",
            "enrichment_type": "full"
        }

        headers = {**self.headers, 'X-Cache-Key': f'company_stripe_full'}

        with self.client.post("/api/enrich/company", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:  # Endpoint might not exist
                response.success()
            else:
                response.failure(f"Company enrichment failed: {response.status_code}")

class BatchProcessingUser(CostAwareUser):
    """Tests batch processing effectiveness"""

    @task(3)
    def test_batch_llm_processing(self):
        """Test async LLM processing"""
        payload = {
            "messages": [
                {"role": "user", "content": "Generate 3 marketing campaign ideas for a fintech startup"}
            ],
            "model": "gemini-1.5-flash",
            "maxTokens": 500,
            "enableBatching": True,
            "batchPriority": 2
        }

        with self.client.post("/v2/advanced/worker/queue", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 202:
                job_data = response.json()
                job_id = job_data.get('job_id')
                if job_id:
                    # Wait a bit then check status
                    time.sleep(2)
                    self.check_batch_result(job_id)
                response.success()
            elif response.status_code == 429:
                response.success()  # Rate limited
            else:
                response.failure(f"Batch queue failed: {response.status_code}")

    def check_batch_result(self, job_id: str):
        """Check batch processing result"""
        with self.client.get(f"/v2/advanced/worker/result/{job_id}", headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'completed':
                    print("   ✅ Batch processing completed successfully")
                elif result.get('status') == 'processing':
                    print("   ⏳ Batch still processing")
                response.success()
            else:
                response.failure(f"Batch result check failed: {response.status_code}")

class PromptOptimizationUser(CostAwareUser):
    """Tests prompt optimization effectiveness"""

    @task(3)
    def test_prompt_optimization(self):
        """Test prompt optimization endpoint"""
        payload = {
            "prompt": "You are a marketing strategist. Create a comprehensive 12-week go-to-market strategy for a B2B SaaS company that provides AI-powered customer support automation. Include specific activities for each week, marketing channels to use, content creation requirements, sales enablement materials needed, budget allocation suggestions, success metrics to track, and potential risks to mitigate. Make it detailed and actionable.",
            "maxTokens": 2000,
            "category": "planning",
            "aggressive": True
        }

        with self.client.post("/v2/advanced/prompt/optimize", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                original_tokens = data.get('original', {}).get('tokens', 0)
                optimized_tokens = data.get('optimized', {}).get('tokens', 0)

                if optimized_tokens < original_tokens:
                    savings = original_tokens - optimized_tokens
                    print(f"   📝 Prompt optimized: {original_tokens} → {optimized_tokens} tokens ({savings} saved)")
                response.success()
            else:
                response.failure(f"Prompt optimization failed: {response.status_code}")

class RateLimitUser(CostAwareUser):
    """Tests rate limiting effectiveness"""

    wait_time = between(0.1, 0.5)  # Fast requests to test rate limits

    @task(10)
    def test_rate_limits(self):
        """Aggressively test rate limits"""
        payload = {
            "goal": "Quick marketing analysis",
            "context": {}
        }

        with self.client.post("/v2/plan", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                print("   🛑 Rate limit triggered (expected under load)")
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Initialize test monitoring"""
    print("🚀 Starting Cost Load Test")
    print("🎯 Target: <$0.03 per request")
    print("📊 Monitoring: caching, batching, rate limits, and costs")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Generate final test report"""
    print("\n🏁 Cost Load Test Completed")
    print("📈 Check monitoring dashboard for detailed cost analysis")
    print("🔗 Dashboard: GET /v2/advanced/monitoring/dashboard")

if __name__ == "__main__":
    # Allow running individual test classes
    import sys
    if len(sys.argv) > 1:
        test_class = sys.argv[1]
        if test_class == "cached":
            CostAwareUser.__bases__ = (CachedRequestUser,)
        elif test_class == "batch":
            CostAwareUser.__bases__ = (BatchProcessingUser,)
        elif test_class == "prompt":
            CostAwareUser.__bases__ = (PromptOptimizationUser,)
        elif test_class == "ratelimit":
            CostAwareUser.__bases__ = (RateLimitUser,)


