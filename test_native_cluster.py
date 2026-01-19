import asyncio
import os
import sys
import time
import random

# Setup path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend/backend-clean"))

async def test_cluster_concurrency(users: int):
    from core.search_native import NativeSearch
    search = NativeSearch()
    print(f"🚀 Launching Cluster Test: {users} concurrent users")
    
    queries = ["Raptorflow AI", "NextJS 14 Guide", "SaaS Scaling 2026", "Python Async Pattern"]
    
    async def run_query(uid):
        q = random.choice(queries)
        start = time.time()
        results = await search.query(q, limit=2)
        end = time.time()
        if results:
            print(f"[User {uid}] ✅ Found {len(results)} results in {end-start:.2f}s (Engines: {set(r['source'] for r in results)})")
        else:
            print(f"[User {uid}] ⚠️ No results (Blocked or empty)")

    tasks = [run_query(i) for i in range(users)]
    await asyncio.gather(*tasks)
    await search.close()

if __name__ == "__main__":
    # Test 5 users to verify parallel execution and merging
    asyncio.run(test_cluster_concurrency(5))
