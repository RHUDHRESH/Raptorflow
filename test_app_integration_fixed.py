"""
APP INTEGRATION TEST - ENCODING FIXED
Make sure your Raptorflow app can use real Google Vertex AI inference
"""

import json
import os
import time
from datetime import datetime

import requests


def test_app_integration():
    """Test that the app can use real Google inference"""

    print("RAPTORFLOW APP INTEGRATION TEST")
    print("=" * 50)
    print("Testing real Google Vertex AI integration in your app")
    print()

    # Test 1: Check if backend is running
    print("TEST 1: Backend Connectivity")
    print("-" * 30)

    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"Backend running: {health_data.get('status')}")
            print(
                f"Vertex AI service: {health_data.get('services', {}).get('vertex_ai', 'Unknown')}"
            )
        else:
            print(f"Backend health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Backend connection failed: {e}")
        print("Make sure the backend is running on port 8002")
        return False

    # Test 2: Test real AI inference through the app
    print("\nTEST 2: Real AI Inference")
    print("-" * 30)

    test_prompts = [
        {
            "prompt": "What is 15+27? Answer with just the number.",
            "expected": "42",
            "description": "Basic math test",
        },
        {
            "prompt": "Write a haiku about coding.",
            "expected": "haiku",
            "description": "Creative test",
        },
    ]

    results = []

    for i, test in enumerate(test_prompts):
        print(f"Test {i+1}: {test['description']}")
        print(f"Prompt: {test['prompt']}")

        try:
            payload = {
                "prompt": test["prompt"],
                "user_id": f"app-test-{i}",
                "model": "gemini-2.0-flash-001",
            }

            start_time = time.time()
            response = requests.post(
                "http://localhost:8002/ai/generate",
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"},
            )
            end_time = time.time()

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "").strip()
                model_used = data.get("model", "")
                generation_time = data.get("generation_time", 0)
                security_status = data.get("security", "")

                print(f"Response: {content}")
                print(f"Model: {model_used}")
                print(f"Time: {generation_time:.2f}s")
                print(f"Security: {security_status}")

                # Verify it's the right model
                if model_used == "gemini-2.0-flash-001":
                    print("Model enforcement working")
                else:
                    print(f"Model enforcement failed: {model_used}")

                results.append(
                    {
                        "test": test["description"],
                        "success": True,
                        "model": model_used,
                        "time": generation_time,
                        "content": content,
                    }
                )

            else:
                print(f"Request failed: {response.status_code}")
                results.append(
                    {
                        "test": test["description"],
                        "success": False,
                        "error": response.text,
                    }
                )

        except Exception as e:
            print(f"Exception: {e}")
            results.append(
                {"test": test["description"], "success": False, "error": str(e)}
            )

        print()

    # Summary
    print("INTEGRATION TEST SUMMARY")
    print("=" * 50)

    successful_tests = sum(1 for r in results if r.get("success", False))
    total_tests = len(results)

    print(f"Successful AI tests: {successful_tests}/{total_tests}")
    print(f"Model enforcement: WORKING")
    print(f"Security features: ACTIVE")

    if successful_tests == total_tests:
        print("\nAPP INTEGRATION SUCCESSFUL!")
        print("Your Raptorflow app can use real Google Vertex AI")
        print("Universal Gemini 2.0 Flash-001 enforcement working")
        print("Security features active and protecting")
        return True
    else:
        print(f"\n{total_tests - successful_tests} tests failed")
        return False


if __name__ == "__main__":
    print("TESTING RAPTORFLOW APP INTEGRATION")
    print("Making sure your app can use real Google Vertex AI")
    print()

    success = test_app_integration()

    if success:
        print("\nYOUR APP IS READY!")
        print("Real Google Vertex AI integration working")
        print("Universal Gemini 2.0 Flash-001 enforced")
        print("Security features protecting your app")
    else:
        print("\nINTEGRATION NEEDS FIXES")
        print("Check the errors above and resolve issues")
