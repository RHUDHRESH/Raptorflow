#!/usr/bin/env python3
"""
Test the actual Muse Backend API endpoints
"""

import os
import asyncio
import json
import time
from dotenv import load_dotenv

load_dotenv()

# Set the working model
os.environ['VERTEX_AI_MODEL'] = 'gemini-2.0-flash-exp'

async def test_backend_api():
    """Test the actual backend API endpoints"""
    print("🚀 Testing Muse Backend API")
    print("=" * 60)
    
    try:
        # Import the actual API functions
        import sys
        sys.path.append('.')
        
        # Mock dependencies
        class MockUser:
            id = "test-user"
            email = "test@example.com"
        
        class MockDB:
            async def execute(self, query, *params):
                print(f"📊 DB Query executed")
                return None
        
        # Import the API module
        from api.v1.muse_vertex_ai import (
            ContentRequest, 
            ChatRequest, 
            ChatMessage,
            generate_content_with_vertex_ai,
            chat_with_vertex_ai,
            get_vertex_ai_status
        )
        
        print("✅ API modules imported successfully")
        
        # Test 1: Content Generation
        print("\n📝 Test 1: Content Generation API")
        content_request = ContentRequest(
            task="Create a compelling blog post introduction about AI-powered marketing automation",
            context={
                "platform": "Raptorflow",
                "industry": "Marketing Technology"
            },
            user_id="test-user",
            workspace_id="test-workspace",
            content_type="blog",
            tone="professional",
            target_audience="marketing professionals",
            max_tokens=500
        )
        
        content_response = await generate_content_with_vertex_ai(
            content_request,
            MockUser(),
            MockDB()
        )
        
        print(f"✅ Success: {content_response.success}")
        if content_response.success:
            print(f"📝 Content: {content_response.content[:150]}...")
            print(f"📊 Tokens: {content_response.tokens_used}")
            print(f"💰 Cost: ${content_response.cost_usd:.6f}")
            print(f"⏱️  Time: {content_response.generation_time_seconds:.2f}s")
            print(f"🤖 Model: {content_response.model_used}")
            print(f"📈 SEO Score: {content_response.seo_score:.2f}")
        
        # Test 2: Chat API
        print("\n💬 Test 2: Chat API")
        chat_request = ChatRequest(
            message="How can I improve my email marketing campaigns using AI?",
            conversation_history=[
                ChatMessage(role="user", content="Hi", timestamp="2024-01-01T10:00:00"),
                ChatMessage(role="assistant", content="Hello! I'm here to help.", timestamp="2024-01-01T10:00:01")
            ],
            context={
                "current_campaigns": ["Welcome series", "Product launch"]
            },
            user_id="test-user",
            workspace_id="test-workspace",
            max_tokens=400
        )
        
        chat_response = await chat_with_vertex_ai(
            chat_request,
            MockUser(),
            MockDB()
        )
        
        print(f"✅ Success: {chat_response.success}")
        if chat_response.success:
            print(f"💬 Response: {chat_response.message[:150]}...")
            print(f"📊 Tokens: {chat_response.tokens_used}")
            print(f"💰 Cost: ${chat_response.cost_usd:.6f}")
            print(f"⏱️  Time: {chat_response.generation_time_seconds:.2f}s")
            print(f"🤖 Model: {chat_response.model_used}")
        
        # Test 3: Status API
        print("\n🔍 Test 3: Status API")
        status_response = await get_vertex_ai_status()
        
        print(f"✅ Status: {status_response['status']}")
        if status_response['status'] == 'available':
            print(f"🤖 Model: {status_response['model']}")
            print(f"📍 Project: {status_response['project_id']}")
            print(f"🌍 Location: {status_response['location']}")
        
        print("\n" + "=" * 60)
        print("📊 API Test Summary:")
        
        successful_tests = 0
        if content_response.success:
            successful_tests += 1
        if chat_response.success:
            successful_tests += 1
        if status_response['status'] == 'available':
            successful_tests += 1
        
        print(f"✅ Successful API endpoints: {successful_tests}/3")
        print(f"🎯 Success Rate: {(successful_tests/3)*100:.1f}%")
        
        if successful_tests == 3:
            print(f"\n🎉 PERFECT! All Muse API endpoints are working!")
            print(f"🚀 Ready to connect to frontend!")
        else:
            print(f"\n⚠️  {3 - successful_tests} endpoints need attention")
        
        return successful_tests == 3
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backend_api())
    
    if success:
        print(f"\n🌐 Next: Connect to frontend Muse component")
        print(f"📱 Then test with Playwright in browser")
    else:
        print(f"\n🔧 Fix API issues before proceeding")
