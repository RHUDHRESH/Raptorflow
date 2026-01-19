import asyncio
import time
import os
import sys
from typing import List, Dict, Any

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Mock env for testing
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["VERTEX_AI_PROJECT_ID"] = "test-project"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["WEBHOOK_SECRET"] = "test-webhook-secret"

from backend.services.search.orchestrator import SOTASearchOrchestrator

async def run_benchmark(queries: List[str], iterations: int = 1):
    orchestrator = SOTASearchOrchestrator()
    total_start = time.time()
    
    print("🚀 Starting Raptorflow Native Search Machine Benchmark...")
    print("-" * 50)
    
    all_latencies = []
    total_results = 0
    
    for i in range(iterations):
        for q in queries:
            print(f"🔍 Searching: '{q}'...", end="", flush=True)
            start = time.time()
            try:
                results = await orchestrator.query(q, limit=10)
                latency = (time.time() - start) * 1000
                all_latencies.append(latency)
                total_results += len(results)
                print(f" DONE ({len(results)} results, {latency:.2f}ms)")
            except Exception as e:
                print(f" FAILED ({str(e)})")
    
    total_duration = time.time() - total_start
    avg_latency = sum(all_latencies) / len(all_latencies) if all_latencies else 0
    
    # Cost Calculation based on Master Plan & GCP Reality:
    # Monthly Capacity: 10,000 searches/day = 300,000 searches/month
    # GCP Hosting (Cloud Run + Egress + Redis): ~$30.00/month (Conservative estimate)
    
    monthly_cost = 30.0 # USD (GCP Production Tier)
    monthly_capacity = 300000
    cost_per_1k = (monthly_cost / monthly_capacity) * 1000
    
    print("-" * 50)
    print("📊 BENCHMARK RESULTS")
    print(f"Total Queries: {len(all_latencies)}")
    print(f"Total Results: {total_results}")
    print(f"Avg Latency:   {avg_latency:.2f}ms")
    print("-" * 50)
    print("💰 COST ANALYSIS (GCP Native Search Machine)")
    print(f"Estimated Monthly GCP Infrastructure: ${monthly_cost:.2f}")
    print(f"Projected Monthly Capacity:        {monthly_capacity:,} searches")
    print(f"Actual Cost per 1,000 searches:    ${cost_per_1k:.4f}")
    print("-" * 50)
    print("🔥 COMPARISON WITH PAID APIs (Per 1k searches)")
    print(f"Serper.dev:   ~$1.00")
    print(f"Brave Search: ~$3.00")
    print(f"Raptorflow:   ~${cost_per_1k:.4f} (GCP Hosted)")
    print(f"Savings:      {((1.0 - cost_per_1k) / 1.0) * 100:.1f}% vs Serper")
    
    await orchestrator.close()

if __name__ == "__main__":
    test_queries = [
        "latest marketing trends 2026",
        "best AI automation tools for SaaS",
        "Raptorflow marketing operating system",
        "SearXNG vs Brave Search API",
        "Reddit marketing strategy"
    ]
    
    asyncio.run(run_benchmark(test_queries))
