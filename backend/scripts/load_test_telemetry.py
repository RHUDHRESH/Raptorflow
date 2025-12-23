import asyncio
import httpx
import time
from uuid import uuid4
import statistics

BASE_URL = "http://localhost:8000/v1/blackbox/telemetry"
CONCURRENT_REQUESTS = 100
TOTAL_REQUESTS = 1000

async def send_telemetry(client, request_id):
    payload = {
        "move_id": str(uuid4()),
        "agent_id": f"test_agent_{request_id % 5}",
        "trace": {"data": "load_test", "index": request_id},
        "tokens": 100,
        "latency": 0.5
    }
    
    start_time = time.time()
    try:
        response = await client.post("", json=payload)
        end_time = time.time()
        return end_time - start_time, response.status_code
    except Exception as e:
        print(f"Request {request_id} failed: {e}")
        return None, 500

async def run_load_test():
    print(f"Starting load test: {TOTAL_REQUESTS} requests, {CONCURRENT_REQUESTS} concurrency...")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        tasks = []
        latencies = []
        status_codes = []
        
        start_test = time.time()
        
        # Run in batches to respect concurrency
        for i in range(0, TOTAL_REQUESTS, CONCURRENT_REQUESTS):
            batch = [send_telemetry(client, j) for j in range(i, min(i + CONCURRENT_REQUESTS, TOTAL_REQUESTS))]
            results = await asyncio.gather(*batch)
            
            for lat, status in results:
                if lat: latencies.append(lat)
                status_codes.append(status)
        
        end_test = time.time()
        
    duration = end_test - start_test
    print("\n--- Load Test Results ---")
    print(f"Total Duration: {duration:.2f}s")
    print(f"Requests per second: {TOTAL_REQUESTS / duration:.2f}")
    print(f"Success Rate: {(status_codes.count(201) / TOTAL_REQUESTS) * 100:.1f}%")
    
    if latencies:
        print(f"Average Latency: {statistics.mean(latencies)*1000:.2f}ms")
        print(f"P95 Latency: {statistics.quantiles(latencies, n=20)[18]*1000:.2f}ms")
        print(f"Max Latency: {max(latencies)*1000:.2f}ms")

if __name__ == "__main__":
    try:
        asyncio.run(run_load_test())
    except KeyboardInterrupt:
        pass
