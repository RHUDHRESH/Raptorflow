#!/usr/bin/env python3
"""
Debug intent detection full flow
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

    # Test the full _detect_with_llm method
    intent = await detector._detect_with_llm(text)
    print(f"Intent from _detect_with_llm: {intent}")
    print(f"Parameters: {intent.parameters}")
    print(f"Sub-intents: {intent.sub_intents}")

    # Test the main detect method
    intent2 = await detector.detect(text)
    print(f"\nIntent from main detect: {intent2}")
    print(f"Parameters: {intent2.parameters}")
    print(f"Sub-intents: {intent2.sub_intents}")


if __name__ == "__main__":
    asyncio.run(debug_intent())
