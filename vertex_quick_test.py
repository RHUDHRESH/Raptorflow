#!/usr/bin/env python3
"""Quick Vertex AI test using backend client."""

import os
import asyncio
import sys
sys.path.insert(0, 'backend')

# Set GCP credentials before importing config
os.environ['GOOGLE_CLOUD_PROJECT'] = 'raptorflow-477017'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'raptorflow-477017-d75059f2c50f.json'

from backend.services.vertex_ai_client import VertexAIClient

async def quick_vertex_test():
    """Test Vertex AI via backend client."""

    print("=== QUICK VERTEX AI TEST ===")
    print("Using backend VertexAIClient...")

    try:
        # Initialize vertex client
        client = VertexAIClient()
        print("[PASS] Vertex AI client initialized successfully")
    except Exception as e:
        print(f"[FAIL] Vertex AI client initialization failed: {e}")
        return

    # Test Gemini models via client
    test_cases = [
        ("fast", "Gemini Flash"),
        ("reasoning", "Gemini Reasoning"),
    ]

    for model_type, description in test_cases:
        try:
            print(f"\nTesting {model_type} ({description})...")

            response = await client.chat_completion(
                messages=[{"role": "user", "content": "Hello! Respond with exactly 'This AI model is working correctly.'"}],
                model_type=model_type
            )

            if response and "working correctly" in response.lower():
                print(f"[PASS] {model_type}: {response[:100]}...")
            else:
                print(f"[FAIL] {model_type}: Unexpected response")

        except Exception as e:
            print(f"[FAIL] {model_type}: {str(e)}")

    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(quick_vertex_test())
