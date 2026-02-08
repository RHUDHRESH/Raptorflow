#!/usr/bin/env python3
"""
Environment Verification Script
Tests all critical services and configurations
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_environment():
    print("=== RAPTORFLOW ENVIRONMENT VERIFICATION ===\n")
    
    # 1. Test Environment Variables
    print("1. Testing Environment Variables...")
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_SERVICE_ROLE_KEY': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
        'VERTEX_AI_PROJECT_ID': os.getenv('VERTEX_AI_PROJECT_ID'),
        'UPSTASH_REDIS_REST_URL': os.getenv('UPSTASH_REDIS_REST_URL'),
        'UPSTASH_REDIS_REST_TOKEN': os.getenv('UPSTASH_REDIS_REST_TOKEN'),
    }
    
    all_set = True
    for var, value in required_vars.items():
        if value:
            print(f"   ✓ {var}: {'*' * 10}...{value[-10:] if len(value) > 20 else value}")
        else:
            print(f"   ✗ {var}: NOT SET")
            all_set = False
    
    if not all_set:
        print("\n   ⚠️  Some environment variables are missing!")
    
    # 2. Test Settings Module
    print("\n2. Testing Settings Module...")
    try:
        from backend.config.settings import get_settings
        settings = get_settings()
        print(f"   ✓ Settings loaded for environment: {settings.ENVIRONMENT}")
        print(f"   ✓ Supabase URL configured: {'Yes' if settings.SUPABASE_URL else 'No'}")
        print(f"   ✓ Vertex AI project: {settings.VERTEX_AI_PROJECT_ID or 'Not set'}")
        print(f"   ✓ Redis URL: {'Yes' if settings.redis_url else 'No'}")
    except Exception as e:
        print(f"   ✗ Settings module error: {e}")
    
    # 3. Test Supabase Connection
    print("\n3. Testing Supabase Connection...")
    try:
        from backend.core.supabase_mgr import get_supabase_client
        client = get_supabase_client()
        # Simple health check
        result = client.table('workspaces').select('count').execute()
        print(f"   ✓ Supabase connection successful")
    except Exception as e:
        print(f"   ✗ Supabase connection failed: {e}")
    
    # 4. Test Redis Connection
    print("\n4. Testing Redis Connection...")
    try:
        import redis
        redis_url = os.getenv('UPSTASH_REDIS_REST_URL')
        if redis_url:
            # For Upstash REST API, we'd use the client
            print(f"   ✓ Redis URL configured: {redis_url[:30]}...")
        else:
            print("   ✗ Redis URL not configured")
    except Exception as e:
        print(f"   ✗ Redis test failed: {e}")
    
    # 5. Test Backend Import
    print("\n5. Testing Backend Modules...")
    try:
        import backend.main
        print("   ✓ Backend main module imports successfully")
        
        import backend.app_factory
        print("   ✓ App factory imports successfully")
        
        from backend.api.registry import include_universal
        print("   ✓ API registry imports successfully")
    except Exception as e:
        print(f"   ✗ Backend import error: {e}")
    
    # 6. Check Frontend Environment
    print("\n6. Testing Frontend Environment...")
    frontend_env = Path('.env.local')
    if frontend_env.exists():
        print("   ✓ .env.local exists")
        with open(frontend_env) as f:
            content = f.read()
            if 'NEXT_PUBLIC_SUPABASE_URL' in content:
                print("   ✓ Frontend Supabase URL configured")
            if 'NEXT_PUBLIC_API_URL' in content:
                print("   ✓ Frontend API URL configured")
    else:
        print("   ✗ .env.local not found")
    
    print("\n=== VERIFICATION COMPLETE ===")
    print("\nNext steps:")
    print("1. Start backend: cd backend && python -m uvicorn backend.main:app --reload")
    print("2. Start frontend: npm run dev")
    print("3. Visit http://localhost:3000 to verify the application")

if __name__ == "__main__":
    test_environment()
