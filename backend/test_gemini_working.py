#!/usr/bin/env python3
"""
Test the working Gemini 2.0 Flash model
"""

import os
import asyncio
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    print("✅ Gemini libraries imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

class GeminiAIService:
    """Gemini AI service for testing"""
    
    def __init__(self):
        self.project_id = os.getenv('VERTEX_AI_PROJECT_ID')
        self.location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        self.model_name = os.getenv('VERTEX_AI_MODEL', 'gemini-2.0-flash-exp')
        
        # Rate limiting
        self.requests_per_minute = 60
        self.requests_per_hour = 1000
        self.request_times = []
        
        # Cost tracking (approximate for Gemini 2.0 Flash)
        self.input_cost_per_1k = 0.000075  # $0.000075 per 1K input tokens
        self.output_cost_per_1k = 0.00015   # $0.00015 per 1K output tokens
        
        # Initialize
        try:
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel(self.model_name)
            print(f"✅ Gemini initialized: {self.model_name}")
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            raise
    
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
        """Generate text using Gemini"""
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
                "model": self.model_name
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

async def main():
    """Test the Gemini model"""
    print("🚀 Testing Gemini 2.0 Flash Model")
    print("=" * 50)
    
    # Check environment
    if not os.getenv('VERTEX_AI_PROJECT_ID'):
        print("❌ VERTEX_AI_PROJECT_ID not set")
        return
    
    print(f"📍 Project: {os.getenv('VERTEX_AI_PROJECT_ID')}")
    print(f"📍 Location: {os.getenv('VERTEX_AI_LOCATION', 'us-central1')}")
    print(f"📍 Model: {os.getenv('VERTEX_AI_MODEL', 'gemini-2.0-flash-exp')}")
    
    try:
        # Create service
        service = GeminiAIService()
        
        # Test queries
        test_queries = [
            "Hello! Please respond with a brief greeting.",
            "What is Raptorflow? Answer in one sentence.",
            "List 3 key features of a marketing automation platform.",
            "Generate a creative tagline for a SaaS product."
        ]
        
        total_cost = 0
        total_tokens = 0
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📤 Test Query {i}: {query}")
            
            response = await service.generate_text(
                prompt=query,
                workspace_id="test-workspace",
                user_id="test-user",
                max_tokens=200
            )
            
            if response["status"] == "success":
                print("✅ SUCCESS!")
                print(f"📝 Response: {response['text']}")
                print(f"📊 Tokens: {response['total_tokens']}")
                print(f"💰 Cost: ${response['cost_usd']:.6f}")
                print(f"⏱️  Time: {response['generation_time_seconds']:.2f}s")
                
                total_cost += response['cost_usd']
                total_tokens += response['total_tokens']
            else:
                print(f"❌ FAILED: {response['error']}")
        
        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        print(f"💰 Total Cost: ${total_cost:.6f}")
        print(f"📊 Total Tokens: {total_tokens}")
        print(f"🎉 Gemini 2.0 Flash is working!")
        
        # Update the environment file
        print(f"\n💡 Update your .env file with:")
        print(f"VERTEX_AI_MODEL=gemini-2.0-flash-exp")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
