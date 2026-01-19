#!/usr/bin/env python3
"""
Red Team Test 2: LLM Integration Test
Tests if LLM integration works with actual API calls
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from agents.llm import get_llm
from agents.config import ModelTier

async def test_llm_integration():
    """Test LLM integration with actual API calls."""
    print("🔴 RED TEAM TEST 2: LLM Integration Test")
    print("=" * 50)
    
    try:
        # Test LLM instantiation
        print("🚀 Initializing LLM...")
        llm = get_llm(ModelTier.FLASH_LITE)
        print(f"✅ LLM created: {llm.model_name}")
        
        # Test basic generation
        print("📤 Testing basic generation...")
        response1 = await llm.generate("What is 2+2?", "You are a helpful assistant.")
        print(f"✅ Basic response: {response1[:100]}...")
        
        # Test structured generation
        print("📊 Testing structured generation...")
        from pydantic import BaseModel
        
        class MathResult(BaseModel):
            answer: int
            explanation: str
        
        response2 = await llm.generate_structured(
            "What is 5*3? Provide answer and explanation.",
            MathResult,
            "You are a math tutor."
        )
        print(f"✅ Structured response: {response2}")
        
        # Test error handling
        print("⚠️ Testing error handling...")
        try:
            # This should fail gracefully
            await llm.generate("", "Invalid prompt")
            print("❌ Should have failed but didn't")
        except Exception as e:
            print(f"✅ Error handling works: {str(e)[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_llm_integration())
    print(f"\n🎯 RESULT: {'PASS' if result else 'FAIL'}")
    sys.exit(0 if result else 1)
