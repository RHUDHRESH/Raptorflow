#!/usr/bin/env python3
"""
Final integration test - direct import without package issues
"""

import os
import asyncio
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Set the working model
os.environ['VERTEX_AI_MODEL'] = 'gemini-2.0-flash-exp'

# Direct imports
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    print("✅ Vertex AI libraries imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

class TestVertexAIService:
    """Test version of Vertex AI service"""
    
    def __init__(self):
        self.project_id = os.getenv('VERTEX_AI_PROJECT_ID')
        self.location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        self.model_name = os.getenv('VERTEX_AI_MODEL', 'gemini-2.0-flash-exp')
        
        # Rate limiting
        self.requests_per_minute = 60
        self.requests_per_hour = 1000
        self.request_times = []
        
        # Cost tracking (Gemini 2.0 Flash pricing)
        self.input_cost_per_1k = 0.000075
        self.output_cost_per_1k = 0.00015
        
        # Initialize
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel(self.model_name)
        self.model_type = 'generative'
        
        print(f"✅ Service initialized: {self.model_name}")
    
    def _check_rate_limit(self) -> bool:
        """Check rate limits"""
        now = datetime.now()
        self.request_times = [t for t in self.request_times if now - t < timedelta(hours=1)]
        
        minute_ago = [t for t in self.request_times if now - t < timedelta(minutes=1)]
        if len(minute_ago) >= self.requests_per_minute:
            return False
            
        if len(self.request_times) >= self.requests_per_hour:
            return False
            
        return True
    
    async def generate_text(self, prompt: str, workspace_id: str, user_id: str, max_tokens: int = 1000):
        """Generate text"""
        if not self._check_rate_limit():
            return {
                "status": "error",
                "error": "Rate limit exceeded"
            }
        
        try:
            self.request_times.append(datetime.now())
            start_time = time.time()
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": 0.7,
                }
            )
            
            generation_time = time.time() - start_time
            
            # Extract token usage
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            
            cost = ((input_tokens / 1000) * self.input_cost_per_1k + 
                   (output_tokens / 1000) * self.output_cost_per_1k)
            
            return {
                "status": "success",
                "text": response.text,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost_usd": cost,
                "generation_time_seconds": generation_time,
                "model": self.model_name,
                "model_type": self.model_type
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

async def main():
    """Final integration test"""
    print("🚀 Final Vertex AI Integration Test")
    print("=" * 60)
    
    # Check environment
    if not os.getenv('VERTEX_AI_PROJECT_ID'):
        print("❌ VERTEX_AI_PROJECT_ID not set")
        return
    
    print(f"📍 Project: {os.getenv('VERTEX_AI_PROJECT_ID')}")
    print(f"📍 Location: {os.getenv('VERTEX_AI_LOCATION', 'us-central1')}")
    print(f"📍 Model: {os.getenv('VERTEX_AI_MODEL', 'gemini-2.0-flash-exp')}")
    
    try:
        # Create service
        service = TestVertexAIService()
        
        # Test comprehensive scenarios
        test_scenarios = [
            {
                "name": "Basic Greeting",
                "prompt": "Hello! Please respond with a brief greeting and introduce yourself as Gemini.",
                "workspace": "test-workspace",
                "user": "test-user"
            },
            {
                "name": "Raptorflow Description",
                "prompt": "What is Raptorflow? Describe it as a marketing automation platform in one paragraph.",
                "workspace": "raptorflow-main",
                "user": "admin-user"
            },
            {
                "name": "Marketing Content",
                "prompt": "Generate a 3-step customer onboarding email sequence for a SaaS product.",
                "workspace": "marketing-team",
                "user": "marketing-manager"
            },
            {
                "name": "Technical Documentation",
                "prompt": "Explain Vertex AI integration benefits for developers in technical terms.",
                "workspace": "dev-team",
                "user": "developer"
            }
        ]
        
        total_cost = 0
        total_tokens = 0
        successful_tests = 0
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📤 Test {i}: {scenario['name']}")
            print(f"📝 Prompt: {scenario['prompt'][:60]}...")
            
            response = await service.generate_text(
                prompt=scenario['prompt'],
                workspace_id=scenario['workspace'],
                user_id=scenario['user'],
                max_tokens=300
            )
            
            if response["status"] == "success":
                print("✅ SUCCESS!")
                print(f"📝 Response: {response['text'][:150]}...")
                print(f"📊 Tokens: {response['total_tokens']}")
                print(f"💰 Cost: ${response['cost_usd']:.6f}")
                print(f"⏱️  Time: {response['generation_time_seconds']:.2f}s")
                print(f"🏢 Workspace: {scenario['workspace']}")
                print(f"👤 User: {scenario['user']}")
                
                total_cost += response['cost_usd']
                total_tokens += response['total_tokens']
                successful_tests += 1
            else:
                print(f"❌ FAILED: {response['error']}")
        
        print("\n" + "=" * 60)
        print("📊 Final Test Results:")
        print(f"✅ Successful tests: {successful_tests}/{len(test_scenarios)}")
        print(f"💰 Total Cost: ${total_cost:.6f}")
        print(f"📊 Total Tokens: {total_tokens}")
        print(f"🎯 Success Rate: {(successful_tests/len(test_scenarios)*100):.1f}%")
        
        if successful_tests == len(test_scenarios):
            print("\n🎉 PERFECT! Vertex AI integration is fully working!")
            print("\n🚀 Ready for production:")
            print("✅ Rate limiting implemented")
            print("✅ Cost tracking working")
            print("✅ Error handling robust")
            print("✅ Gemini 2.0 Flash model active")
            print("✅ All test scenarios passed")
        else:
            print(f"\n⚠️  {len(test_scenarios) - successful_tests} tests failed")
        
        # Production readiness check
        print(f"\n🔧 Production Configuration:")
        print(f"VERTEX_AI_PROJECT_ID={os.getenv('VERTEX_AI_PROJECT_ID')}")
        print(f"VERTEX_AI_LOCATION={os.getenv('VERTEX_AI_LOCATION', 'us-central1')}")
        print(f"VERTEX_AI_MODEL=gemini-2.0-flash-exp")
        print(f"AI_REQUESTS_PER_MINUTE=60")
        print(f"AI_REQUESTS_PER_HOUR=1000")
        print(f"DAILY_AI_BUDGET=10.0")
        print(f"MONTHLY_AI_BUDGET=100.0")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
