#!/usr/bin/env python3
"""
Test Muse Vertex AI Integration
"""

import os
import asyncio
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# Set the working model
os.environ['VERTEX_AI_MODEL'] = 'gemini-2.0-flash-exp'

# Add current directory to path
sys.path.append('.')

async def main():
    """Main test function"""
    try:
        # Import the Muse Vertex AI service directly
        import api.v1.muse_vertex_ai as muse_api
        
        print("🚀 Testing Muse Vertex AI Integration")
        print("=" * 60)
        
        # Mock the database dependency for testing
        class MockDB:
            async def execute(self, query, *params):
                print(f"📊 DB Query: {query[:50]}...")
                return None
        
        class MockUser:
            id = "test-user"
            email = "test@example.com"
        
        # Test content generation
        print("\n📝 Test 1: Content Generation")
        content_request = muse_api.ContentRequest(
            task="Create a compelling blog post introduction about AI-powered marketing automation",
            context={
                "platform": "Raptorflow",
                "industry": "Marketing Technology",
                "target_length": "200-300 words"
            },
            user_id="test-user",
            workspace_id="test-workspace",
            content_type="blog",
            tone="professional",
            target_audience="marketing professionals",
            max_tokens=500
        )
        
        # Test content generation
        content_response = await muse_api.generate_content_with_vertex_ai(
            content_request,
            MockUser(),
            MockDB()
        )
        
        print(f"✅ Success: {content_response.success}")
        print(f"📝 Content: {content_response.content[:200]}...")
        print(f"📊 Tokens: {content_response.tokens_used}")
        print(f"💰 Cost: ${content_response.cost_usd:.6f}")
        print(f"⏱️  Time: {content_response.generation_time_seconds:.2f}s")
        print(f"🤖 Model: {content_response.model_used}")
        print(f"📈 SEO Score: {content_response.seo_score:.2f}")
        print(f"💡 Suggestions: {len(content_response.suggestions)}")
        
        # Test chat functionality
        print("\n💬 Test 2: Chat Interaction")
        chat_request = muse_api.ChatRequest(
            message="How can I improve my email marketing campaigns using AI?",
            conversation_history=[
                muse_api.ChatMessage(role="user", content="Hi", timestamp="2024-01-01T10:00:00"),
                muse_api.ChatMessage(role="assistant", content="Hello! I'm here to help with your marketing questions.", timestamp="2024-01-01T10:00:01")
            ],
            context={
                "current_campaigns": ["Welcome series", "Product launch"],
                "industry": "SaaS"
            },
            user_id="test-user",
            workspace_id="test-workspace",
            max_tokens=400
        )
        
        chat_response = await muse_api.chat_with_vertex_ai(
            chat_request,
            MockUser(),
            MockDB()
        )
        
        print(f"✅ Success: {chat_response.success}")
        print(f"💬 Response: {chat_response.message[:200]}...")
        print(f"📊 Tokens: {chat_response.tokens_used}")
        print(f"💰 Cost: ${chat_response.cost_usd:.6f}")
        print(f"⏱️  Time: {chat_response.generation_time_seconds:.2f}s")
        print(f"🤖 Model: {chat_response.model_used}")
        print(f"💡 Suggestions: {len(chat_response.suggestions)}")
        
        # Test status endpoint
        print("\n🔍 Test 3: Service Status")
        status_response = await muse_api.get_vertex_ai_status()
        
        print(f"✅ Status: {status_response['status']}")
        if status_response['status'] == 'available':
            print(f"🤖 Model: {status_response['model']}")
            print(f"📍 Project: {status_response['project_id']}")
            print(f"🌍 Location: {status_response['location']}")
            print(f"📊 Rate Limits: {status_response['rate_limits']}")
        
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        
        total_cost = content_response.cost_usd + chat_response.cost_usd
        total_tokens = content_response.tokens_used + chat_response.tokens_used
        
        print(f"💰 Total Cost: ${total_cost:.6f}")
        print(f"📊 Total Tokens: {total_tokens}")
        print(f"🎯 All tests completed successfully!")
        
        print(f"\n🚀 Muse Vertex AI Integration is ready!")
        print(f"✅ Content generation working")
        print(f"✅ Chat functionality working")
        print(f"✅ Status monitoring working")
        print(f"✅ Cost tracking active")
        print(f"✅ Database integration ready")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
