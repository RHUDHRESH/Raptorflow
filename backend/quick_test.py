#!/usr/bin/env python3
"""
Quick test to bypass Python environment issues
"""
import os
import sys

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("=== Python Environment Test ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path[:3]}")

try:
    print("\n=== Testing Imports ===")
    from ..base import BaseAgent

    print("✅ BaseAgent imported successfully")

    from ..agents.specialists.content_creator import ContentCreator

    print("✅ ContentCreator imported successfully")

    from ..agents.skills.registry import get_skills_registry

    print("✅ Skills registry imported successfully")

    print("\n=== Testing Agent Creation ===")
    agent = ContentCreator()
    print(f"✅ Agent created: {agent.name}")

    print("\n=== Testing Skills Registry ===")
    registry = get_skills_registry()
    skills = registry.list_skills()
    print(f"✅ Registry loaded with {len(skills)} skills")

    print("\n=== SUCCESS: All Core Components Working ===")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback

    traceback.print_exc()

print("\n=== Test Complete ===")
