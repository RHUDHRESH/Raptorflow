"""
SHOW ACTUAL AI RESPONSES
Display the real content from unlimited requests test
"""

import json

import requests


def show_actual_responses():
    """Show real AI responses from unlimited test"""

    print("SHOWING ACTUAL AI RESPONSES")
    print("=" * 40)
    print("Real Google Gemini 2.0 Flash-001 responses:")
    print()

    # Test a few requests and show actual content
    test_prompts = [
        "What is 10+10? Answer with just the number.",
        "Write a haiku about programming.",
        "Explain quantum computing in one sentence.",
        "What is the capital of France?",
        "Calculate 25*4 and show the work.",
    ]

    for i, prompt in enumerate(test_prompts):
        try:
            payload = {
                "prompt": prompt,
                "user_id": "response-test",
                "model": "gemini-2.0-flash-001",
            }

            response = requests.post(
                "http://localhost:8003/ai/generate",
                json=payload,
                timeout=15,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "").strip()
                model = data.get("model", "")
                rate_limiting = data.get("rate_limiting", "unknown")

                print(f"Request {i+1}: {prompt}")
                print(f"Response: {content}")
                print(f"Model: {model}")
                print(f"Rate Limiting: {rate_limiting}")
                print(f"Status: REAL AI RESPONSE")
                print()

            else:
                print(f"Request {i+1} failed: {response.status_code}")
                print()

        except Exception as e:
            print(f"Request {i+1} error: {e}")
            print()


if __name__ == "__main__":
    show_actual_responses()
