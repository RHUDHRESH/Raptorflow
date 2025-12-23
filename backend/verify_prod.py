import asyncio
import os
from backend.db import get_pool, get_cache

async def verify_infrastructure():
    print("--- RaptorFlow Infrastructure Diagnostic ---")
    
    # 1. DB Verification
    print("\n[1/2] Verifying Supabase Connectivity...")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("FAIL: DATABASE_URL not set in environment.")
    else:
        try:
            pool = get_pool()
            await pool.open()
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    result = await cur.fetchone()
                    if result[0] == 1:
                        print("PASS: Successfully connected to Supabase.")
                    else:
                        print(f"FAIL: Unexpected DB result: {result}")
        except Exception as e:
            print(f"FAIL: Could not connect to Supabase: {e}")

    # 2. Cache Verification
    print("\n[2/2] Verifying Upstash Redis Connectivity...")
    upstash_url = os.getenv("UPSTASH_REDIS_REST_URL")
    upstash_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    
    if not upstash_url or not upstash_token:
        print("FAIL: UPSTASH_REDIS_REST_URL or TOKEN not set.")
    else:
        try:
            cache = get_cache()
            await cache.set("rf_diag", "ok", ex=60)
            val = await cache.get("rf_diag")
            if val == "ok":
                print("PASS: Successfully connected to Upstash Redis.")
            else:
                print(f"FAIL: Unexpected Cache result: {val}")
        except Exception as e:
            print(f"FAIL: Could not connect to Upstash: {e}")

    print("\n--- Diagnostic Complete ---")

if __name__ == "__main__":
    asyncio.run(verify_infrastructure())