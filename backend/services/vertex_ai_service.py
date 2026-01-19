"""
Vertex AI Service for Raptorflow
Handles AI model interactions with rate limiting and cost tracking
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import vertexai
try:
    from vertexai.generative_models import GenerativeModel
    GENERATIVE_MODEL_AVAILABLE = True
except ImportError:
    GENERATIVE_MODEL_AVAILABLE = False

try:
    from vertexai.preview.language_models import TextGenerationModel
    TEXT_MODEL_AVAILABLE = True
except ImportError:
    TEXT_MODEL_AVAILABLE = False

import google.cloud.aiplatform as aiplatform
from google.api_core import exceptions as gcp_exceptions

from backend.config.settings import get_settings
try:
    from core.logging_config import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)
settings = get_settings()

@dataclass
class AIRequest:
    """Track AI requests for cost calculation"""
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: datetime
    workspace_id: str
    user_id: str

class VertexAIService:
    """Vertex AI integration with rate limiting and cost tracking"""
    
    def __init__(self):
        self.project_id = settings.VERTEX_AI_PROJECT_ID
        self.location = settings.VERTEX_AI_LOCATION
        self.model_name = getattr(settings, 'VERTEX_AI_MODEL', 'gemini-2.0-flash-exp')
        
        # Rate limiting
        self.requests_per_minute = getattr(settings, 'AI_REQUESTS_PER_MINUTE', 60)
        self.requests_per_hour = getattr(settings, 'AI_REQUESTS_PER_HOUR', 1000)
        self.request_times = []
        
        # Cost tracking (approximate pricing)
        self.input_cost_per_1k = 0.000075  # $0.000075 per 1K input tokens (Gemini 2.0 Flash)
        self.output_cost_per_1k = 0.00015   # $0.00015 per 1K output tokens (Gemini 2.0 Flash)
        
        # Initialize Vertex AI
        try:
            vertexai.init(project=self.project_id, location=self.location)
            
            # Try to initialize the appropriate model
            if 'gemini' in self.model_name.lower() and GENERATIVE_MODEL_AVAILABLE:
                self.model = GenerativeModel(self.model_name)
                self.model_type = 'generative'
            elif 'text-bison' in self.model_name.lower() and TEXT_MODEL_AVAILABLE:
                self.model = TextGenerationModel.from_pretrained(self.model_name)
                self.model_type = 'text'
            else:
                # Fallback to text model
                self.model = TextGenerationModel.from_pretrained('text-bison@002')
                self.model_type = 'text'
                self.model_name = 'text-bison@002'
                
            logger.info(f"Vertex AI initialized: {self.model_name} (type: {self.model_type}) in {self.location}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        now = datetime.now()
        
        # Clean old requests (older than 1 hour)
        self.request_times = [t for t in self.request_times if now - t < timedelta(hours=1)]
        
        # Check per-minute limit
        minute_ago = [t for t in self.request_times if now - t < timedelta(minutes=1)]
        if len(minute_ago) >= self.requests_per_minute:
            return False
            
        # Check per-hour limit
        if len(self.request_times) >= self.requests_per_hour:
            return False
            
        return True
    
    async def _track_cost(self, input_tokens: int, output_tokens: int, workspace_id: str, user_id: str):
        """Track AI usage costs"""
        cost = (input_tokens / 1000) * self.input_cost_per_1k + \
                (output_tokens / 1000) * self.output_cost_per_1k
        
        request = AIRequest(
            model=self.model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            timestamp=datetime.now(),
            workspace_id=workspace_id,
            user_id=user_id
        )
        
        # Store cost tracking (implement in database later)
        logger.info(f"AI Request tracked: {request}")
        
        # Check budget alerts
        await self._check_budget_alerts(workspace_id, cost)
    
    async def _check_budget_alerts(self, workspace_id: str, current_cost: float):
        """Check if workspace is approaching budget limits"""
        # TODO: Implement budget checking from database
        daily_budget = getattr(settings, 'DAILY_AI_BUDGET', 10.0)  # $10 per day default
        monthly_budget = getattr(settings, 'MONTHLY_AI_BUDGET', 100.0)  # $100 per month default
        
        # For now, just log if approaching limits
        if current_cost > daily_budget * 0.8:
            logger.warning(f"Workspace {workspace_id} approaching daily budget: ${current_cost:.4f}")
    
    async def generate_text(
        self, 
        prompt: str, 
        workspace_id: str, 
        user_id: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate text using Vertex AI with rate limiting and cost tracking"""
        
        # Check rate limits
        if not self._check_rate_limit():
            return {
                "status": "error",
                "error": "Rate limit exceeded. Please try again later.",
                "retry_after": 60
            }
        
        try:
            # Track request time
            self.request_times.append(datetime.now())
            
            # Generate content based on model type
            start_time = time.time()
            
            if self.model_type == 'generative':
                # Use Gemini-style API
                response = await self.model.generate_content_async(
                    prompt,
                    generation_config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature,
                    }
                )
                
                # Extract token usage
                usage = response.usage_metadata
                input_tokens = usage.prompt_token_count if usage else 0
                output_tokens = usage.candidates_token_count if usage else 0
                text = response.text
                
            else:
                # Use text-bison style API
                response = self.model.predict(
                    prompt,
                    max_output_tokens=max_tokens,
                    temperature=temperature
                )
                
                # Extract token usage (text-bison provides different metadata)
                input_tokens = getattr(response, 'token_count', {}).get('input_tokens', 0)
                output_tokens = getattr(response, 'token_count', {}).get('output_tokens', 0)
                text = response.text
            
            # Track cost
            await self._track_cost(input_tokens, output_tokens, workspace_id, user_id)
            
            generation_time = time.time() - start_time
            
            return {
                "status": "success",
                "text": text,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost_usd": ((input_tokens / 1000) * self.input_cost_per_1k + 
                           (output_tokens / 1000) * self.output_cost_per_1k),
                "generation_time_seconds": generation_time,
                "model": self.model_name,
                "model_type": self.model_type
            }
            
        except gcp_exceptions.GoogleAPICallError as e:
            logger.error(f"Vertex AI API error: {e}")
            return {
                "status": "error", 
                "error": f"Vertex AI API error: {str(e)}",
                "error_type": "api_error"
            }
        except Exception as e:
            logger.error(f"Unexpected error in Vertex AI: {e}")
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "error_type": "system_error"
            }

# Global service instance
try:
    vertex_ai_service = VertexAIService()
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI service: {e}")
    vertex_ai_service = None
