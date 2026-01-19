#!/usr/bin/env python3
"""
Redis Connectivity Test for Raptorflow
Tests Upstash Redis connection and basic operations
"""

import asyncio
import os
import sys
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.redis import get_redis_client
from core.redis_production import get_redis_production_manager, initialize_redis_production


async def test_basic_redis():
    """Test basic Redis connectivity"""
    print("🔍 Testing Basic Redis Connection...")
    
    try:
        # Get Redis client
        redis_client = await get_redis_client()
        client = redis_client.get_client()  # Synchronous
        
        # Test ping
        start_time = datetime.now()
        result = client.ping()  # Synchronous
        ping_time = (datetime.now() - start_time).total_seconds() * 1000
        
        print(f"✅ Redis PING successful: {result} in {ping_time:.2f}ms")
        
        # Test basic operations
        test_key = "raptorflow:test:connectivity"
        test_value = f"test_value_{datetime.now().isoformat()}"
        
        # Set operation
        start_time = datetime.now()
        client.set(test_key, test_value, ex=60)  # Synchronous
        set_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Get operation
        start_time = datetime.now()
        retrieved_value = client.get(test_key)  # Synchronous
        get_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Delete operation
        start_time = datetime.now()
        client.delete(test_key)  # Synchronous
        delete_time = (datetime.now() - start_time).total_seconds() * 1000
        
        print(f"✅ SET operation: {set_time:.2f}ms")
        print(f"✅ GET operation: {get_time:.2f}ms")
        print(f"✅ DELETE operation: {delete_time:.2f}ms")
        print(f"✅ Data integrity: {retrieved_value == test_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic Redis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_production_manager():
    """Test Redis Production Manager"""
    print("\n🏭 Testing Redis Production Manager...")
    
    try:
        # Initialize production manager
        success = await initialize_redis_production()
        if not success:
            print("❌ Failed to initialize Redis production manager")
            return False
        
        manager = get_redis_production_manager()
        
        # Test connection
        result = await manager.test_connection()
        print(f"✅ Production manager test: {result}")
        
        # Get stats
        stats = await manager.get_redis_stats()
        print(f"✅ Redis stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Production manager test failed: {e}")
        return False


async def test_cache_operations():
    """Test caching operations"""
    print("\n💾 Testing Cache Operations...")
    
    try:
        from core.redis_production import redis_cache_with_ttl, redis_get_cached
        
        # Test caching
        test_data = {
            "user_id": "test_user_123",
            "campaign_data": {
                "name": "Test Campaign",
                "budget": 5000,
                "status": "active"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache the data
        success = redis_cache_with_ttl("test:cache:data", test_data, ttl=300)
        print(f"✅ Cache set: {success}")
        
        # Retrieve the data
        cached_data = redis_get_cached("test:cache:data")
        print(f"✅ Cache get: {cached_data is not None}")
        print(f"✅ Data integrity: {cached_data == test_data}")
        
        # Clean up
        manager = get_redis_production_manager()
        if manager.client:
            manager.client.delete("test:cache:data")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("🚀 RAPTORFLOW REDIS CONNECTIVITY TEST")
    print("=" * 50)
    
    # Check environment variables
    print("\n🔧 Environment Configuration:")
    print(f"UPSTASH_REDIS_URL: {os.getenv('UPSTASH_REDIS_URL', 'NOT SET')}")
    print(f"UPSTASH_REDIS_TOKEN: {'SET' if os.getenv('UPSTASH_REDIS_TOKEN') else 'NOT SET'}")
    
    if not os.getenv('UPSTASH_REDIS_URL') or not os.getenv('UPSTASH_REDIS_TOKEN'):
        print("❌ Redis environment variables not properly configured")
        return False
    
    # Run tests
    tests = [
        ("Basic Redis Connection", test_basic_redis),
        ("Production Manager", test_production_manager),
        ("Cache Operations", test_cache_operations),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Redis is ready for production!")
        return True
    else:
        print("⚠️  Some tests failed - Check configuration")
        return False


if __name__ == "__main__":
    asyncio.run(main())
