#!/usr/bin/env python3
"""
Debug intent detection mock response
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

import asyncio
import json

from cognitive.perception.intent_detector import IntentDetector


async def debug_intent():
    detector = IntentDetector()
    text = "Create a new blog post about AI trends"

    print(f"Testing: {text}")

    # Test the mock response directly
    mock_response = detector._generate_mock_llm_response(text)
    print(f"Mock response: {mock_response}")

    try:
        data = json.loads(mock_response)
        print(f"Parsed data: {data}")
        print(f"Parameters in data: {data.get('parameters', {})}")
    except Exception as e:
        print(f"JSON parse error: {e}")


if __name__ == "__main__":
    asyncio.run(debug_intent())
