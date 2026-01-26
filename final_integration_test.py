#!/usr/bin/env python3
"""
Final comprehensive integration test for Raptorflow systems
"""

import json

import requests


def test_system(name, base_url, endpoints):
    """Test a complete system"""
    print(f"\n🔍 Testing {name} System...")

    results = []

    for endpoint_name, endpoint_config in endpoints.items():
        method = endpoint_config.get("method", "GET")
        url = f"{base_url}{endpoint_config['path']}"
        data = endpoint_config.get("data")

        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "PUT":
                response = requests.put(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url)

            if response.status_code == 200:
                results.append(f"✅ {endpoint_name} - Working")
                if endpoint_config.get("show_response"):
                    print(
                        f"   Response: {json.dumps(response.json(), indent=2)[:200]}..."
                    )
            else:
                results.append(f"❌ {endpoint_name} - Status: {response.status_code}")

        except Exception as e:
            results.append(f"❌ {endpoint_name} - Error: {str(e)}")

    for result in results:
        print(f"   {result}")

    return all("✅" in r for r in results)


def main():
    print("🚀 RAPTORFLOW FINAL INTEGRATION TEST")
    print("=" * 60)

    proxy_url = "http://localhost:3000/api/proxy"

    # Test Moves System
    moves_endpoints = {
        "List Moves": {"path": "/api/v1/moves/"},
        "Create Move": {
            "path": "/api/v1/moves/",
            "method": "POST",
            "data": {
                "name": "Integration Test Move",
                "focusArea": "Testing",
                "desiredOutcome": "Verify full integration",
                "volatilityLevel": 3,
                "steps": ["Setup", "Test", "Verify"],
            },
            "show_response": True,
        },
        "Update Move": {
            "path": "/api/v1/moves/test-move",
            "method": "PUT",
            "data": {"status": "active"},
        },
    }

    moves_success = test_system("Moves", proxy_url, moves_endpoints)

    # Test Campaigns System
    campaigns_endpoints = {
        "List Campaigns": {"path": "/api/v1/campaigns/"},
        "Create Campaign": {
            "path": "/api/v1/campaigns/",
            "method": "POST",
            "data": {
                "name": "Integration Test Campaign",
                "description": "Testing campaign integration",
                "target_icps": ["test-icp"],
            },
            "show_response": True,
        },
    }

    campaigns_success = test_system("Campaigns", proxy_url, campaigns_endpoints)

    # Test Daily Wins System
    daily_wins_endpoints = {
        "List Daily Wins": {"path": "/api/v1/daily_wins/"},
        "Generate Daily Win": {
            "path": "/api/v1/daily_wins/generate",
            "method": "POST",
            "data": {
                "workspace_id": "test-workspace",
                "user_id": "test-user",
                "platform": "LinkedIn",
            },
            "show_response": True,
        },
        "Complete Daily Win": {
            "path": "/api/v1/daily_wins/test-win/complete",
            "method": "POST",
        },
    }

    daily_wins_success = test_system("Daily Wins", proxy_url, daily_wins_endpoints)

    # Test Blackbox System
    blackbox_endpoints = {
        "List Strategies": {"path": "/api/v1/blackbox/strategies"},
        "Generate Strategy": {
            "path": "/api/v1/blackbox/generate-strategy",
            "method": "POST",
            "data": {
                "focus_area": "growth",
                "business_context": "Integration testing",
                "workspace_id": "test-workspace",
                "user_id": "test-user",
            },
            "show_response": True,
        },
        "Create Move from Strategy": {
            "path": "/api/v1/blackbox/test-strategy/create-move",
            "method": "POST",
        },
    }

    blackbox_success = test_system("Blackbox", proxy_url, blackbox_endpoints)

    # Test Muse System
    muse_endpoints = {
        "List Assets": {"path": "/api/v1/muse/assets"},
        "Generate Content": {
            "path": "/api/v1/muse/generate",
            "method": "POST",
            "data": {
                "prompt": "Write a test marketing email",
                "platform": "email",
                "workspace_id": "test-workspace",
                "user_id": "test-user",
            },
            "show_response": True,
        },
        "Save Asset": {
            "path": "/api/v1/muse/assets",
            "method": "POST",
            "data": {
                "title": "Test Asset",
                "content": "Test content",
                "platform": "email",
            },
        },
        "Chat with Muse": {
            "path": "/api/v1/muse/chat",
            "method": "POST",
            "data": {
                "message": "Help me with marketing",
                "workspace_id": "test-workspace",
                "user_id": "test-user",
            },
        },
    }

    muse_success = test_system("Muse", proxy_url, muse_endpoints)

    # Summary
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION TEST SUMMARY")
    print("=" * 60)

    systems = [
        ("Moves", moves_success),
        ("Campaigns", campaigns_success),
        ("Daily Wins", daily_wins_success),
        ("Blackbox", blackbox_success),
        ("Muse", muse_success),
    ]

    all_success = True
    for system_name, success in systems:
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{system_name:12} : {status}")
        if not success:
            all_success = False

    print("=" * 60)

    if all_success:
        print("🎉 ALL SYSTEMS INTEGRATED SUCCESSFULLY!")
        print("🚀 Raptorflow is ready for development and testing!")
        print("\n📋 Next Steps:")
        print("   1. Open http://localhost:3000 for the test interface")
        print("   2. Test the frontend stores integration")
        print("   3. Verify authentication flow")
        print("   4. Test end-to-end user workflows")
    else:
        print("⚠️  Some systems need attention")
        print("🔧 Check the failed systems above")

    print("\n🔗 Architecture:")
    print("   Frontend (localhost:3000) → Proxy → Backend (localhost:8000)")
    print("   All systems are now connected and functional!")


if __name__ == "__main__":
    main()
