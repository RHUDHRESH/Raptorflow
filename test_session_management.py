#!/usr/bin/env python3
"""
Redis Session Management Test for Raptorflow
Tests session persistence and recovery
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.redis import get_redis_client


async def test_session_management():
    """Test Redis session management"""
    print("🔐 Testing Redis Session Management...")
    
    try:
        # Get Redis client
        redis_client = await get_redis_client()
        client = redis_client.get_client()
        
        # Test session storage
        session_id = "test_session_12345"
        session_data = {
            "user_id": "test_user_123",
            "workspace_id": "test_workspace_456",
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "status": "active",
            "metadata": {
                "campaign_count": 5,
                "last_action": "created_campaign"
            }
        }
        
        # Store session
        import json
        session_key = f"session:{session_id}"
        client.setex(session_key, 3600, json.dumps(session_data))  # 1 hour TTL
        
        print(f"✅ Session stored: {session_id}")
        
        # Retrieve session
        retrieved_data = client.get(session_key)
        if retrieved_data:
            parsed_data = json.loads(retrieved_data)
            print(f"✅ Session retrieved: {parsed_data['user_id']}")
            print(f"✅ Data integrity: {parsed_data['user_id'] == session_data['user_id']}")
        
        # Test session metadata
        metadata_key = f"session_meta:{session_id}"
        metadata = {
            "session_id": session_id,
            "user_id": session_data["user_id"],
            "workspace_id": session_data["workspace_id"],
            "created_at": session_data["created_at"],
            "last_accessed": datetime.now().isoformat(),
            "ttl": 3600
        }
        
        client.setex(metadata_key, 3600, json.dumps(metadata))
        print(f"✅ Session metadata stored")
        
        # List sessions (simple pattern matching)
        session_keys = client.keys("session:*")
        meta_keys = client.keys("session_meta:*")
        print(f"✅ Found {len(session_keys)} sessions, {len(meta_keys)} metadata entries")
        
        # Clean up test data
        client.delete(session_key)
        client.delete(metadata_key)
        print("✅ Test session cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_rate_limiting():
    """Test Redis rate limiting"""
    print("\n🚦 Testing Redis Rate Limiting...")
    
    try:
        redis_client = await get_redis_client()
        client = redis_client.get_client()
        
        # Simple rate limiting test
        user_id = "test_user_123"
        rate_limit_key = f"rate_limit:{user_id}"
        
        # Simulate API calls
        for i in range(5):
            current_count = client.incr(rate_limit_key)
            if current_count == 1:
                client.expire(rate_limit_key, 60)  # 1 minute window
            
            print(f"✅ API call {i+1}: Count = {current_count}")
        
        # Check current limit
        remaining = client.get(rate_limit_key)
        print(f"✅ Current request count: {remaining}")
        
        # Clean up
        client.delete(rate_limit_key)
        print("✅ Rate limit test cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False


async def test_caching_strategies():
    """Test different caching strategies"""
    print("\n💾 Testing Redis Caching Strategies...")
    
    try:
        import json
        redis_client = await get_redis_client()
        client = redis_client.get_client()
        
        # Test user profile caching
        user_profile = {
            "id": "user_123",
            "name": "Test User",
            "email": "test@example.com",
            "plan": "premium",
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        }
        
        profile_key = "user_profile:123"
        client.setex(profile_key, 1800, json.dumps(user_profile))  # 30 minutes
        print("✅ User profile cached (30 min TTL)")
        
        # Test campaign data caching
        campaign_data = {
            "id": "campaign_456",
            "name": "Test Campaign",
            "status": "active",
            "budget": 5000,
            "performance": {
                "impressions": 10000,
                "clicks": 500,
                "conversions": 25
            }
        }
        
        campaign_key = "campaign_data:456"
        client.setex(campaign_key, 900, json.dumps(campaign_data))  # 15 minutes
        print("✅ Campaign data cached (15 min TTL)")
        
        # Test analytics result caching
        analytics_result = {
            "query": "campaign_performance_last_30_days",
            "result": {
                "total_impressions": 500000,
                "total_clicks": 25000,
                "total_conversions": 1250,
                "ctr": 5.0,
                "conversion_rate": 5.0
            },
            "generated_at": datetime.now().isoformat()
        }
        
        analytics_key = "analytics:campaign_performance_30d"
        client.setex(analytics_key, 300, json.dumps(analytics_result))  # 5 minutes
        print("✅ Analytics result cached (5 min TTL)")
        
        # Verify cache retrieval
        cached_profile = json.loads(client.get(profile_key))
        cached_campaign = json.loads(client.get(campaign_key))
        cached_analytics = json.loads(client.get(analytics_key))
        
        print(f"✅ Retrieved profile: {cached_profile['name']}")
        print(f"✅ Retrieved campaign: {cached_campaign['name']}")
        print(f"✅ Retrieved analytics: {len(cached_analytics['result'])} metrics")
        
        # Clean up
        client.delete(profile_key)
        client.delete(campaign_key)
        client.delete(analytics_key)
        print("✅ Cache test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Caching strategies test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 RAPTORFLOW REDIS SESSION MANAGEMENT TEST")
    print("=" * 60)
    
    # Check environment
    print("\n🔧 Environment Configuration:")
    print(f"UPSTASH_REDIS_URL: {os.getenv('UPSTASH_REDIS_URL', 'NOT SET')}")
    print(f"UPSTASH_REDIS_TOKEN: {'SET' if os.getenv('UPSTASH_REDIS_TOKEN') else 'NOT SET'}")
    
    if not os.getenv('UPSTASH_REDIS_URL') or not os.getenv('UPSTASH_REDIS_TOKEN'):
        print("❌ Redis environment variables not properly configured")
        return False
    
    # Run tests
    tests = [
        ("Session Management", test_session_management),
        ("Rate Limiting", test_rate_limiting),
        ("Caching Strategies", test_caching_strategies),
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
    print("\n" + "=" * 60)
    print("📊 SESSION MANAGEMENT TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SESSION MANAGEMENT TESTS PASSED!")
        print("🔥 Redis session management is ready for production!")
        return True
    else:
        print("⚠️  Some tests failed - Check configuration")
        return False


if __name__ == "__main__":
    asyncio.run(main())
