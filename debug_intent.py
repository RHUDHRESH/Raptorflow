#!/usr/bin/env python3
"""
Debug intent detection parameter extraction
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

import asyncio

from cognitive.perception.intent_detector import IntentDetector


async def debug_intent():
    detector = IntentDetector()
    text = "Create a new blog post about AI trends"

    print(f"Testing: {text}")

    # Test the parameter extraction directly
    params = detector._extract_create_parameters(text)
    print(f"Direct parameter extraction: {params}")

    # Test full intent detection
    intent = await detector.detect(text)
    print(f"Full detection result: {intent.parameters}")
    print(f"Sub-intents: {intent.sub_intents}")


if __name__ == "__main__":
    asyncio.run(debug_intent())
