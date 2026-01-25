#!/usr/bin/env python3
"""
Simple integration test for Raptorflow systems
"""

import requests
import json

def test_backend_endpoints():
    """Test that all backend endpoints are working"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/api/v1/moves/",
        "/api/v1/campaigns/",
        "/api/v1/daily_wins/",
        "/api/v1/blackbox/strategies",
        "/api/v1/muse/assets",
        "/health"
    ]
    
    print("🔍 Testing Backend Endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {endpoint} - Working")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def test_create_operations():
    """Test creating new resources"""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Testing Create Operations...")
    
    # Test creating a move
    try:
        move_data = {
            "name": "Test Move from Integration",
            "focusArea": "Testing",
            "desiredOutcome": "Verify integration works",
            "volatilityLevel": 2,
            "steps": ["Step 1", "Step 2"]
        }
        response = requests.post(f"{base_url}/api/v1/moves/", json=move_data)
        if response.status_code == 200:
            print("✅ Create Move - Working")
            result = response.json()
            print(f"   Created move: {result.get('id')}")
        else:
            print(f"❌ Create Move - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Create Move - Error: {e}")
    
    # Test creating a campaign
    try:
        campaign_data = {
            "name": "Test Campaign",
            "description": "Integration test campaign",
            "target_icps": ["test-icp"]
        }
        response = requests.post(f"{base_url}/api/v1/campaigns/", json=campaign_data)
        if response.status_code == 200:
            print("✅ Create Campaign - Working")
            result = response.json()
            print(f"   Created campaign: {result.get('id')}")
        else:
            print(f"❌ Create Campaign - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Create Campaign - Error: {e}")

def test_ai_endpoints():
    """Test AI-powered endpoints"""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Testing AI Endpoints...")
    
    # Test Daily Wins generation
    try:
        win_data = {
            "workspace_id": "test-workspace",
            "user_id": "test-user",
            "platform": "LinkedIn"
        }
        response = requests.post(f"{base_url}/api/v1/daily_wins/generate", json=win_data)
        if response.status_code == 200:
            print("✅ Daily Wins Generation - Working")
            result = response.json()
            print(f"   Generated win: {result.get('win', {}).get('id')}")
        else:
            print(f"❌ Daily Wins Generation - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Daily Wins Generation - Error: {e}")
    
    # Test Blackbox strategy generation
    try:
        strategy_data = {
            "focus_area": "growth",
            "business_context": "Test integration",
            "workspace_id": "test-workspace",
            "user_id": "test-user"
        }
        response = requests.post(f"{base_url}/api/v1/blackbox/generate-strategy", json=strategy_data)
        if response.status_code == 200:
            print("✅ Blackbox Strategy Generation - Working")
            result = response.json()
            print(f"   Generated strategy: {result.get('strategy', {}).get('id')}")
        else:
            print(f"❌ Blackbox Strategy Generation - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Blackbox Strategy Generation - Error: {e}")
    
    # Test Muse content generation
    try:
        muse_data = {
            "prompt": "Write a marketing email",
            "platform": "email",
            "workspace_id": "test-workspace",
            "user_id": "test-user"
        }
        response = requests.post(f"{base_url}/api/v1/muse/generate", json=muse_data)
        if response.status_code == 200:
            print("✅ Muse Content Generation - Working")
            result = response.json()
            print(f"   Generated asset: {result.get('asset', {}).get('id')}")
        else:
            print(f"❌ Muse Content Generation - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Muse Content Generation - Error: {e}")

if __name__ == "__main__":
    print("🚀 RAPTORFLOW INTEGRATION VERIFICATION")
    print("=" * 50)
    
    test_backend_endpoints()
    test_create_operations()
    test_ai_endpoints()
    
    print("\n🎯 INTEGRATION TEST COMPLETE")
    print("If all tests show ✅, the integration is working!")
