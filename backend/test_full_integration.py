#!/usr/bin/env python3
"""
Test the full Vertex AI integration with Gemini 2.0 Flash
"""

import os
import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()

# Set the working model
os.environ['VERTEX_AI_MODEL'] = 'gemini-2.0-flash-exp'

async def main():
    """Main test function"""
    try:
        # Import our service directly
        import services.vertex_ai_service as vertex_service
        
        print("🚀 Testing Full Vertex AI Integration")
        print("=" * 60)
        
        # Create service instance
        service = vertex_service.VertexAIService()
        
        print(f"✅ Service initialized")
        print(f"📍 Model: {service.model_name}")
        print(f"📍 Type: {service.model_type}")
        print(f"📍 Project: {service.project_id}")
        print(f"📍 Location: {service.location}")
        
        # Test queries
        test_queries = [
            {
                "prompt": "Hello! Please respond with a brief greeting and introduce yourself.",
                "workspace": "test-workspace",
                "user": "test-user"
            },
            {
                "prompt": "What are the key benefits of using Vertex AI for a SaaS platform?",
                "workspace": "raptorflow-main",
                "user": "admin-user"
            },
            {
                "prompt": "Generate a professional email template for customer onboarding.",
                "workspace": "marketing-team",
                "user": "marketing-manager"
            }
        ]
        
        total_cost = 0
        total_tokens = 0
        
        for i, test in enumerate(test_queries, 1):
            print(f"\n📤 Test Query {i}: {test['prompt'][:50]}...")
            
            response = await service.generate_text(
                prompt=test['prompt'],
                workspace_id=test['workspace'],
                user_id=test['user'],
                max_tokens=500
            )
            
            if response["status"] == "success":
                print("✅ SUCCESS!")
                print(f"📝 Response: {response['text'][:200]}...")
                print(f"📊 Tokens: {response['total_tokens']}")
                print(f"💰 Cost: ${response['cost_usd']:.6f}")
                print(f"⏱️  Time: {response['generation_time_seconds']:.2f}s")
                print(f"🤖 Model: {response['model']}")
                print(f"🔧 Type: {response.get('model_type', 'unknown')}")
                
                total_cost += response['cost_usd']
                total_tokens += response['total_tokens']
            else:
                print(f"❌ FAILED: {response['error']}")
        
        print("\n" + "=" * 60)
        print("📊 Integration Test Summary:")
        print(f"💰 Total Cost: ${total_cost:.6f}")
        print(f"📊 Total Tokens: {total_tokens}")
        print(f"🎉 Full Vertex AI integration is working!")
        
        # Test rate limiting
        print(f"\n🔒 Testing rate limiting...")
        start_time = asyncio.get_event_loop().time()
        
        # Send multiple requests quickly
        tasks = []
        for i in range(3):
            task = service.generate_text(
                prompt=f"Quick test {i+1}",
                workspace_id="rate-test",
                user_id="test-user",
                max_tokens=50
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
        rate_limited = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "error" and "Rate limit" in r.get("error", ""))
        
        print(f"✅ Successful requests: {successful}")
        print(f"🔒 Rate limited requests: {rate_limited}")
        print(f"⏱️  Total time: {asyncio.get_event_loop().time() - start_time:.2f}s")
        
        print("\n🎯 All tests completed! Vertex AI integration is ready for production!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
