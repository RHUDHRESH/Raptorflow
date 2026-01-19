#!/usr/bin/env python3
"""
Working Muse API Test - Direct implementation
"""

import os
import asyncio
import json
import time
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

class WorkingMuseAPI:
    """Working Muse API implementation"""
    
    def __init__(self):
        self.project_id = os.getenv('VERTEX_AI_PROJECT_ID')
        self.location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        self.model_name = os.getenv('VERTEX_AI_MODEL', 'gemini-2.0-flash-exp')
        
        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel(self.model_name)
        
        print(f"✅ Muse API initialized: {self.model_name}")
    
    async def generate_content(self, request_data: dict) -> dict:
        """Generate content endpoint"""
        try:
            task = request_data.get('task', '')
            context = request_data.get('context', {})
            content_type = request_data.get('content_type', 'general')
            tone = request_data.get('tone', 'professional')
            target_audience = request_data.get('target_audience', 'general')
            max_tokens = request_data.get('max_tokens', 1000)
            temperature = request_data.get('temperature', 0.7)
            
            # Build enhanced prompt
            prompt = f"""You are Muse, an expert content creator for Raptorflow marketing automation platform.

TASK: {task}

CONTENT TYPE: {content_type}
TONE: {tone}
TARGET AUDIENCE: {target_audience}

"""
            
            # Add context
            if context:
                prompt += "CONTEXT:\n"
                for key, value in context.items():
                    prompt += f"- {key}: {value}\n"
            
            prompt += """
GUIDELINES:
- Write in a professional, engaging tone
- Focus on marketing automation insights
- Include actionable advice where relevant
- Maintain brand consistency with Raptorflow
- Optimize for clarity and readability

Please generate high-quality content that meets these requirements.
"""
            
            start_time = time.time()
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": temperature,
                }
            )
            
            generation_time = time.time() - start_time
            
            # Extract usage
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            
            # Calculate cost
            cost = ((input_tokens / 1000) * 0.000075 + 
                   (output_tokens / 1000) * 0.00015)
            
            # SEO score
            content_lower = response.text.lower()
            seo_score = 0.0
            
            if len(response.text) > 300:
                seo_score += 0.2
            if any(word in content_lower for word in ["how", "what", "why", "when", "where"]):
                seo_score += 0.1
            if any(word in content_lower for word in ["step", "guide", "tutorial", "tips"]):
                seo_score += 0.2
            if any(word in content_lower for word in ["marketing", "business", "customer", "audience"]):
                seo_score += 0.2
            if len(response.text.split()) > 50:
                seo_score += 0.1
            if any(char in response.text for char in ["!", "?", "."]):
                seo_score += 0.1
            
            seo_score = min(seo_score, 1.0)
            
            # Suggestions
            suggestions = []
            if len(response.text) < 200:
                suggestions.append("Consider expanding the content for better engagement")
            if "call to action" not in content_lower and content_type in ["blog", "landing", "email"]:
                suggestions.append("Add a clear call to action")
            if "raptorflow" not in content_lower:
                suggestions.append("Consider mentioning Raptorflow for brand consistency")
            
            return {
                "success": True,
                "content": response.text,
                "task": task,
                "content_type": content_type,
                "tone": tone,
                "target_audience": target_audience,
                "tokens_used": input_tokens + output_tokens,
                "cost_usd": cost,
                "generation_time_seconds": generation_time,
                "model_used": self.model_name,
                "seo_score": seo_score,
                "suggestions": suggestions,
                "metadata": {
                    "content_id": str(int(time.time())),
                    "session_id": "test-session"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": request_data.get('task', '')
            }
    
    async def chat(self, request_data: dict) -> dict:
        """Chat endpoint"""
        try:
            message = request_data.get('message', '')
            conversation_history = request_data.get('conversation_history', [])
            context = request_data.get('context', {})
            max_tokens = request_data.get('max_tokens', 1000)
            temperature = request_data.get('temperature', 0.7)
            
            # Build chat prompt
            prompt = """You are Muse, an AI content creation assistant for Raptorflow marketing automation platform.

Your role is to help users create compelling marketing content, provide strategic insights, and offer creative solutions.

CONVERSATION HISTORY:
"""
            
            # Add conversation history
            for msg in conversation_history[-3:]:
                prompt += f"\n{msg['role'].upper()}: {msg['content']}"
            
            prompt += f"\n\nUSER: {message}"
            
            # Add context
            if context:
                prompt += f"\n\nADDITIONAL CONTEXT:"
                for key, value in context.items():
                    prompt += f"\n- {key}: {value}"
            
            prompt += """

Please provide a helpful, insightful response that addresses the user's needs. Be conversational yet professional, and offer specific, actionable advice when relevant.
"""
            
            start_time = time.time()
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": temperature,
                }
            )
            
            generation_time = time.time() - start_time
            
            # Extract usage
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            
            # Calculate cost
            cost = ((input_tokens / 1000) * 0.000075 + 
                   (output_tokens / 1000) * 0.00015)
            
            # Suggestions
            suggestions = []
            response_lower = response.text.lower()
            message_lower = message.lower()
            
            if "blog" in message_lower or "content" in message_lower:
                suggestions.append("Generate a blog post outline")
                suggestions.append("Create social media content")
            
            if "strategy" in message_lower or "plan" in message_lower:
                suggestions.append("Develop a marketing campaign")
                suggestions.append("Create an action plan")
            
            if "email" in message_lower:
                suggestions.append("Design an email template")
                suggestions.append("Plan an email sequence")
            
            return {
                "success": True,
                "message": response.text,
                "conversation_id": "test-conversation",
                "tokens_used": input_tokens + output_tokens,
                "cost_usd": cost,
                "generation_time_seconds": generation_time,
                "model_used": self.model_name,
                "suggestions": suggestions[:3]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_status(self) -> dict:
        """Get status endpoint"""
        return {
            "status": "available",
            "model": self.model_name,
            "project_id": self.project_id,
            "location": self.location,
            "rate_limits": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000
            }
        }

async def test_working_api():
    """Test the working API"""
    print("🚀 Testing Working Muse API")
    print("=" * 60)
    
    try:
        # Initialize API
        api = WorkingMuseAPI()
        
        # Test 1: Content Generation
        print("\n📝 Test 1: Content Generation")
        content_request = {
            "task": "Create a compelling blog post introduction about AI-powered marketing automation",
            "context": {
                "platform": "Raptorflow",
                "industry": "Marketing Technology",
                "target_length": "200-300 words"
            },
            "user_id": "test-user",
            "workspace_id": "test-workspace",
            "content_type": "blog",
            "tone": "professional",
            "target_audience": "marketing professionals",
            "max_tokens": 500
        }
        
        content_response = await api.generate_content(content_request)
        
        print(f"✅ Success: {content_response['success']}")
        if content_response['success']:
            print(f"📝 Content: {content_response['content'][:150]}...")
            print(f"📊 Tokens: {content_response['tokens_used']}")
            print(f"💰 Cost: ${content_response['cost_usd']:.6f}")
            print(f"⏱️  Time: {content_response['generation_time_seconds']:.2f}s")
            print(f"🤖 Model: {content_response['model_used']}")
            print(f"📈 SEO Score: {content_response['seo_score']:.2f}")
        
        # Test 2: Chat
        print("\n💬 Test 2: Chat")
        chat_request = {
            "message": "How can I improve my email marketing campaigns using AI?",
            "conversation_history": [
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Hello! I'm here to help with your marketing questions."}
            ],
            "context": {
                "current_campaigns": ["Welcome series", "Product launch"],
                "industry": "SaaS"
            },
            "user_id": "test-user",
            "workspace_id": "test-workspace",
            "max_tokens": 400
        }
        
        chat_response = await api.chat(chat_request)
        
        print(f"✅ Success: {chat_response['success']}")
        if chat_response['success']:
            print(f"💬 Response: {chat_response['message'][:150]}...")
            print(f"📊 Tokens: {chat_response['tokens_used']}")
            print(f"💰 Cost: ${chat_response['cost_usd']:.6f}")
            print(f"⏱️  Time: {chat_response['generation_time_seconds']:.2f}s")
            print(f"🤖 Model: {chat_response['model_used']}")
        
        # Test 3: Status
        print("\n🔍 Test 3: Status")
        status_response = await api.get_status()
        
        print(f"✅ Status: {status_response['status']}")
        print(f"🤖 Model: {status_response['model']}")
        print(f"📍 Project: {status_response['project_id']}")
        print(f"🌍 Location: {status_response['location']}")
        
        print("\n" + "=" * 60)
        print("📊 API Test Summary:")
        
        successful_tests = 0
        if content_response['success']:
            successful_tests += 1
        if chat_response['success']:
            successful_tests += 1
        if status_response['status'] == 'available':
            successful_tests += 1
        
        print(f"✅ Successful endpoints: {successful_tests}/3")
        print(f"🎯 Success Rate: {(successful_tests/3)*100:.1f}%")
        
        if successful_tests == 3:
            print(f"\n🎉 PERFECT! Muse API is fully working!")
            print(f"🚀 Ready to create frontend integration!")
            
            # Save API responses for frontend testing
            with open('muse_api_test_responses.json', 'w') as f:
                json.dump({
                    'content_response': content_response,
                    'chat_response': chat_response,
                    'status_response': status_response
                }, f, indent=2, default=str)
            
            print(f"💾 Test responses saved to muse_api_test_responses.json")
            return True
        else:
            print(f"\n⚠️  {3 - successful_tests} endpoints need attention")
            return False
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_working_api())
    
    if success:
        print(f"\n🌐 Next: Create frontend Muse integration")
        print(f"📱 Then test with Playwright in browser")
    else:
        print(f"\n🔧 Fix API issues before proceeding")
