#!/usr/bin/env python3
"""
Direct Upstash Redis Test
Tests Upstash Redis connection using their Python client
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_upstash_redis():
    """Test Upstash Redis directly"""
    print("🔍 Testing Upstash Redis Direct Connection...")
    
    try:
        # Import Upstash Redis client
        from upstash_redis import Redis
        
        url = os.getenv('UPSTASH_REDIS_URL')
        token = os.getenv('UPSTASH_REDIS_TOKEN')
        
        print(f"URL: {url}")
        print(f"Token: {token[:10]}..." if token else "No token")
        
        # Create client
        redis = Redis(url=url, token=token)
        
        # Test ping
        start_time = asyncio.get_event_loop().time()
        result = redis.ping()  # Synchronous call
        ping_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        print(f"✅ PING successful: {result} in {ping_time:.2f}ms")
        
        # Test set/get
        test_key = "raptorflow:test:upstash"
        test_value = "test_value_12345"
        
        start_time = asyncio.get_event_loop().time()
        redis.set(test_key, test_value, ex=60)  # Synchronous
        set_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        start_time = asyncio.get_event_loop().time()
        retrieved = redis.get(test_key)  # Synchronous
        get_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        print(f"✅ SET: {set_time:.2f}ms")
        print(f"✅ GET: {get_time:.2f}ms")
        print(f"✅ Data integrity: {retrieved == test_value}")
        
        # Clean up
        redis.delete(test_key)  # Synchronous
        
        return True
        
    except Exception as e:
        print(f"❌ Upstash Redis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_upstash_redis())
