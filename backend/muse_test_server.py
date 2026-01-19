#!/usr/bin/env python3
"""
Simple Muse Vertex AI Test Server
Demonstrates the integration without complex dependencies
"""

import os
import asyncio
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

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

# FastAPI app
app = FastAPI(title="Muse Vertex AI Test Server")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ContentRequest(BaseModel):
    task: str
    context: Dict[str, Any] = {}
    user_id: str
    workspace_id: str
    content_type: str = "general"
    tone: str = "professional"
    target_audience: str = "general"
    max_tokens: int = 1000
    temperature: float = 0.7

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}
    user_id: str
    workspace_id: str
    max_tokens: int = 1000
    temperature: float = 0.7

# Muse Vertex AI Service
class MuseVertexAIService:
    def __init__(self):
        self.project_id = os.getenv('VERTEX_AI_PROJECT_ID')
        self.location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        self.model_name = os.getenv('VERTEX_AI_MODEL', 'gemini-2.0-flash-exp')
        
        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel(self.model_name)
        
        print(f"✅ Muse Vertex AI initialized: {self.model_name}")
    
    async def generate_content(self, request: ContentRequest) -> Dict[str, Any]:
        """Generate content using Vertex AI"""
        try:
            # Build enhanced prompt
            prompt = f"""You are Muse, an expert content creator for Raptorflow marketing automation platform.

TASK: {request.task}

CONTENT TYPE: {request.content_type}
TONE: {request.tone}
TARGET AUDIENCE: {request.target_audience}

"""
            
            # Add context
            if request.context:
                prompt += "CONTEXT:\n"
                for key, value in request.context.items():
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
                    "max_output_tokens": request.max_tokens,
                    "temperature": request.temperature,
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
            if "call to action" not in content_lower and request.content_type in ["blog", "landing", "email"]:
                suggestions.append("Add a clear call to action")
            if "raptorflow" not in content_lower:
                suggestions.append("Consider mentioning Raptorflow for brand consistency")
            
            return {
                "success": True,
                "content": response.text,
                "task": request.task,
                "content_type": request.content_type,
                "tone": request.tone,
                "target_audience": request.target_audience,
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
                "task": request.task
            }
    
    async def chat(self, request: ChatRequest) -> Dict[str, Any]:
        """Chat with Muse AI"""
        try:
            # Build chat prompt
            prompt = """You are Muse, an AI content creation assistant for Raptorflow marketing automation platform.

Your role is to help users create compelling marketing content, provide strategic insights, and offer creative solutions.

CONVERSATION HISTORY:
"""
            
            # Add conversation history
            for msg in request.conversation_history[-3:]:
                prompt += f"\n{msg['role'].upper()}: {msg['content']}"
            
            prompt += f"\n\nUSER: {request.message}"
            
            # Add context
            if request.context:
                prompt += f"\n\nADDITIONAL CONTEXT:"
                for key, value in request.context.items():
                    prompt += f"\n- {key}: {value}"
            
            prompt += """

Please provide a helpful, insightful response that addresses the user's needs. Be conversational yet professional, and offer specific, actionable advice when relevant.
"""
            
            start_time = time.time()
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": request.max_tokens,
                    "temperature": request.temperature,
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
            message_lower = request.message.lower()
            
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
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
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

# Initialize service
muse_service = MuseVertexAIService()

# API Endpoints
@app.get("/api/v1/muse/status")
async def get_status():
    """Get Muse Vertex AI status"""
    return muse_service.get_status()

@app.post("/api/v1/muse/generate")
async def generate_content(request: ContentRequest):
    """Generate content endpoint"""
    result = await muse_service.generate_content(request)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.post("/api/v1/muse/chat")
async def chat(request: ChatRequest):
    """Chat endpoint"""
    result = await muse_service.chat(request)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Muse Vertex AI Test Server",
        "status": "running",
        "endpoints": {
            "status": "/api/v1/muse/status",
            "generate": "/api/v1/muse/generate",
            "chat": "/api/v1/muse/chat"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Muse Vertex AI Test Server...")
    print("📊 Available endpoints:")
    print("  - GET  /api/v1/muse/status")
    print("  - POST /api/v1/muse/generate")
    print("  - POST /api/v1/muse/chat")
    print("🌐 Frontend should be available at: http://localhost:3001/muse-vertex-ai")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
