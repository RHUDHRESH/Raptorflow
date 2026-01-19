#!/usr/bin/env python3
"""
Direct test of Vertex AI integration without package dependencies
"""

import os
import sys
import asyncio
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Direct imports to avoid package issues
try:
    import vertexai
    from vertexai.preview.language_models import TextGenerationModel
    from google.api_core import exceptions as gcp_exceptions
    print("✅ Vertex AI libraries imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

class SimpleVertexAIService:
    """Simplified Vertex AI service for testing"""
    
    def __init__(self):
        self.project_id = os.getenv('VERTEX_AI_PROJECT_ID')
        self.location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        self.model_name = os.getenv('VERTEX_AI_MODEL', 'text-bison@002')
        
        # Rate limiting
        self.requests_per_minute = 60
        self.requests_per_hour = 1000
        self.request_times = []
        
        # Cost tracking
        self.input_cost_per_1k = 0.0004
        self.output_cost_per_1k = 0.0008
        
        # Initialize
        try:
            vertexai.init(project=self.project_id, location=self.location)
            self.model = TextGenerationModel.from_pretrained(self.model_name)
            print(f"✅ Vertex AI initialized: {self.model_name}")
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
        """Generate text"""
        if not self._check_rate_limit():
            return {
                "status": "error",
                "error": "Rate limit exceeded"
            }
        
        try:
            self.request_times.append(datetime.now())
            start_time = time.time()
            
            response = self.model.predict(
                prompt,
                max_output_tokens=max_tokens,
                temperature=0.7
            )
            
            generation_time = time.time() - start_time
            
            # Extract token info
            input_tokens = getattr(response, 'token_count', {}).get('input_tokens', 0)
            output_tokens = getattr(response, 'token_count', {}).get('output_tokens', 0)
            
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
    """Main test function"""
    print("🧪 Direct Vertex AI Test")
    print("=" * 50)
    
    # Check environment
    if not os.getenv('VERTEX_AI_PROJECT_ID'):
        print("❌ VERTEX_AI_PROJECT_ID not set")
        return
    
    print(f"📍 Project: {os.getenv('VERTEX_AI_PROJECT_ID')}")
    print(f"📍 Location: {os.getenv('VERTEX_AI_LOCATION', 'us-central1')}")
    print(f"📍 Model: {os.getenv('VERTEX_AI_MODEL', 'text-bison@002')}")
    
    try:
        # Create service
        service = SimpleVertexAIService()
        
        # Test queries
        test_queries = [
            "Hello! Please respond with a brief greeting.",
            "What is Raptorflow? Answer in one sentence.",
            "List 3 key features of a marketing automation platform."
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📤 Test Query {i}: {query}")
            
            response = await service.generate_text(
                prompt=query,
                workspace_id="test-workspace",
                user_id="test-user",
                max_tokens=150
            )
            
            if response["status"] == "success":
                print("✅ SUCCESS!")
                print(f"📝 Response: {response['text']}")
                print(f"📊 Tokens: {response['total_tokens']}")
                print(f"💰 Cost: ${response['cost_usd']:.6f}")
                print(f"⏱️  Time: {response['generation_time_seconds']:.2f}s")
            else:
                print(f"❌ FAILED: {response['error']}")
        
        print("\n" + "=" * 50)
        print("🎉 Vertex AI integration test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
