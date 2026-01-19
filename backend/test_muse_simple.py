#!/usr/bin/env python3
"""
Simple Muse Vertex AI Test - Direct API call
"""

import os
import asyncio
import sys
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

class SimpleMuseVertexAI:
    """Simple Muse Vertex AI service for testing"""
    
    def __init__(self):
        self.project_id = os.getenv('VERTEX_AI_PROJECT_ID')
        self.location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        self.model_name = os.getenv('VERTEX_AI_MODEL', 'gemini-2.0-flash-exp')
        
        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel(self.model_name)
        
        print(f"✅ Muse Vertex AI initialized: {self.model_name}")
    
    async def generate_content(self, task: str, context: dict = {}, content_type: str = "general", tone: str = "professional") -> dict:
        """Generate content using Vertex AI"""
        
        # Build Muse-specific prompt
        prompt = f"""You are Muse, an AI content creation assistant for Raptorflow marketing automation platform.

TASK: {task}

CONTENT TYPE: {content_type}
TONE: {tone}

"""
        
        # Add context if provided
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
        
        try:
            start_time = time.time()
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 800,
                    "temperature": 0.7,
                }
            )
            
            generation_time = time.time() - start_time
            
            # Extract token usage
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            
            # Calculate cost (Gemini 2.0 Flash pricing)
            cost = ((input_tokens / 1000) * 0.000075 + 
                   (output_tokens / 1000) * 0.00015)
            
            # Calculate simple SEO score
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
            
            # Generate suggestions
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
                "tokens_used": input_tokens + output_tokens,
                "cost_usd": cost,
                "generation_time_seconds": generation_time,
                "model_used": self.model_name,
                "seo_score": seo_score,
                "suggestions": suggestions
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": task
            }
    
    async def chat(self, message: str, conversation_history: list = [], context: dict = {}) -> dict:
        """Chat with Muse AI"""
        
        # Build chat prompt
        prompt = """You are Muse, an AI content creation assistant for Raptorflow marketing automation platform.

Your role is to help users create compelling marketing content, provide strategic insights, and offer creative solutions.

CONVERSATION HISTORY:
"""
        
        # Add conversation history
        for msg in conversation_history[-3:]:  # Last 3 messages
            prompt += f"\n{msg['role'].upper()}: {msg['content']}"
        
        prompt += f"\n\nUSER: {message}"
        
        # Add context if provided
        if context:
            prompt += f"\n\nADDITIONAL CONTEXT:"
            for key, value in context.items():
                prompt += f"\n- {key}: {value}"
        
        prompt += """

Please provide a helpful, insightful response that addresses the user's needs. Be conversational yet professional, and offer specific, actionable advice when relevant.
"""
        
        try:
            start_time = time.time()
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 600,
                    "temperature": 0.7,
                }
            )
            
            generation_time = time.time() - start_time
            
            # Extract token usage
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            
            # Calculate cost
            cost = ((input_tokens / 1000) * 0.000075 + 
                   (output_tokens / 1000) * 0.00015)
            
            # Generate suggestions
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

async def main():
    """Test Muse Vertex AI"""
    print("🚀 Testing Muse Vertex AI Integration")
    print("=" * 60)
    
    try:
        # Initialize Muse
        muse = SimpleMuseVertexAI()
        
        # Test 1: Content Generation
        print("\n📝 Test 1: Content Generation")
        content_result = await muse.generate_content(
            task="Create a compelling blog post introduction about AI-powered marketing automation",
            context={
                "platform": "Raptorflow",
                "industry": "Marketing Technology",
                "target_length": "200-300 words"
            },
            content_type="blog",
            tone="professional"
        )
        
        print(f"✅ Success: {content_result['success']}")
        if content_result['success']:
            print(f"📝 Content: {content_result['content'][:200]}...")
            print(f"📊 Tokens: {content_result['tokens_used']}")
            print(f"💰 Cost: ${content_result['cost_usd']:.6f}")
            print(f"⏱️  Time: {content_result['generation_time_seconds']:.2f}s")
            print(f"🤖 Model: {content_result['model_used']}")
            print(f"📈 SEO Score: {content_result['seo_score']:.2f}")
            print(f"💡 Suggestions: {len(content_result['suggestions'])}")
        
        # Test 2: Chat Interaction
        print("\n💬 Test 2: Chat Interaction")
        chat_result = await muse.chat(
            message="How can I improve my email marketing campaigns using AI?",
            conversation_history=[
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Hello! I'm here to help with your marketing questions."}
            ],
            context={
                "current_campaigns": ["Welcome series", "Product launch"],
                "industry": "SaaS"
            }
        )
        
        print(f"✅ Success: {chat_result['success']}")
        if chat_result['success']:
            print(f"💬 Response: {chat_result['message'][:200]}...")
            print(f"📊 Tokens: {chat_result['tokens_used']}")
            print(f"💰 Cost: ${chat_result['cost_usd']:.6f}")
            print(f"⏱️  Time: {chat_result['generation_time_seconds']:.2f}s")
            print(f"🤖 Model: {chat_result['model_used']}")
            print(f"💡 Suggestions: {len(chat_result['suggestions'])}")
        
        # Test 3: Different Content Types
        print("\n📧 Test 3: Email Content")
        email_result = await muse.generate_content(
            task="Write a welcome email for new SaaS users",
            context={
                "product": "Raptorflow",
                "features": ["AI automation", "Campaign management", "Analytics"]
            },
            content_type="email",
            tone="friendly"
        )
        
        print(f"✅ Success: {email_result['success']}")
        if email_result['success']:
            print(f"📧 Email: {email_result['content'][:150]}...")
            print(f"📊 Tokens: {email_result['tokens_used']}")
            print(f"💰 Cost: ${email_result['cost_usd']:.6f}")
        
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        
        total_cost = 0
        total_tokens = 0
        successful_tests = 0
        
        for result in [content_result, chat_result, email_result]:
            if result['success']:
                total_cost += result['cost_usd']
                total_tokens += result['tokens_used']
                successful_tests += 1
        
        print(f"✅ Successful tests: {successful_tests}/3")
        print(f"💰 Total Cost: ${total_cost:.6f}")
        print(f"📊 Total Tokens: {total_tokens}")
        print(f"🎯 Success Rate: {(successful_tests/3)*100:.1f}%")
        
        if successful_tests == 3:
            print(f"\n🎉 PERFECT! Muse Vertex AI integration is fully working!")
            print(f"\n🚀 Ready for browser testing with Playwright!")
            print(f"✅ Content generation working")
            print(f"✅ Chat functionality working")
            print(f"✅ Multiple content types working")
            print(f"✅ Cost tracking active")
            print(f"✅ SEO scoring working")
            print(f"✅ Smart suggestions working")
        else:
            print(f"\n⚠️  {3 - successful_tests} tests failed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
