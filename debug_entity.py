#!/usr/bin/env python3
"""
Debug entity extraction for John Doe case
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

import asyncio

from cognitive.perception.entity_extractor import EntityExtractor


async def debug_john_doe():
    extractor = EntityExtractor()
    text = "John Doe from Microsoft Corp invested $1,000,000 in startup XYZ."

    print(f"Testing: {text}")

    # Check person pattern directly
    import re

    person_pattern = r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b"
    common_words = {
        "The",
        "This",
        "That",
        "From",
        "With",
        "And",
        "For",
        "But",
        "Not",
        "All",
        "Any",
        "Can",
        "Will",
        "Just",
        "Out",
        "Get",
        "Got",
        "See",
        "Look",
        "Now",
        "New",
        "Old",
        "Good",
        "Bad",
        "Big",
        "Small",
    }

    matches = list(re.finditer(person_pattern, text))
    print(f"Person pattern matches: {[m.group() for m in matches]}")

    for match in matches:
        words = match.group().split()
        print(f"Words: {words}")
        print(
            f"Words in common_words: {words[0] in common_words or words[1] in common_words}"
        )

        text_before = text[: match.start()].lower()
        text_after = text[match.end() :].lower()
        print(f"Text before: '{text_before[-20:]}'")
        print(f"Text after: '{text_after[:20]}'")

        # Check company indicators
        before_inc = any(
            inc in text_before[-20:] for inc in ["inc", "corp", "llc", "ltd"]
        )
        after_inc = any(inc in text_after[:20] for inc in ["inc", "corp", "llc", "ltd"])
        print(f"Near company indicators: before={before_inc}, after={after_inc}")

    # Test actual extraction
    entities = await extractor.extract(text)
    print(f"\nExtracted entities: {[(e.text, e.type.value) for e in entities]}")


if __name__ == "__main__":
    asyncio.run(debug_john_doe())
