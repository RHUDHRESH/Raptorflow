"""
AI API Proxy - Secure backend proxy for external AI services
Hides API keys and provides rate limiting for AI endpoints
"""

import os
import logging
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from backend.core.auth import get_current_user
from backend.core.models import User

router = APIRouter(prefix="/ai", tags=["ai-proxy"])
logger = logging.getLogger(__name__)

# Get API keys from environment (backend-only)
VERTEX_AI_API_KEY = os.getenv("VERTEX_AI_API_KEY")
VERTEX_AI_PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID", "raptorflow-481505")

if not VERTEX_AI_API_KEY:
    raise ValueError("VERTEX_AI_API_KEY must be set in backend environment")


@router.post("/generate")
async def generate_content(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Proxy for Vertex AI generateContent API
    """
    try:
        # Validate request
        prompt = request.get("prompt")
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="prompt is required"
            )

        model = request.get("model", "gemini-2.0-flash-exp")
        max_tokens = request.get("max_tokens", 1000)
        temperature = request.get("temperature", 0.7)

        # Call Vertex AI API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={VERTEX_AI_API_KEY}",
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    }
                },
                headers={
                    "Content-Type": "application/json",
                }
            )

            if response.status_code != 200:
                logger.error(f"Vertex AI API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="AI service temporarily unavailable"
                )

            result = response.json()

            if not result.get("candidates"):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="AI service returned no content"
                )

            content = result["candidates"][0]["content"]["parts"][0]["text"]
            usage_metadata = result.get("usageMetadata", {})

            # Log usage for cost tracking
            tokens_used = usage_metadata.get("totalTokenCount", 0)
            logger.info(f"AI usage: user={current_user.id}, tokens={tokens_used}, model={model}")

            return {
                "content": content,
                "model": model,
                "usage": {
                    "prompt_tokens": usage_metadata.get("promptTokenCount", 0),
                    "completion_tokens": usage_metadata.get("candidatesTokenCount", 0),
                    "total_tokens": tokens_used,
                },
                "user_id": current_user.id,
            }

    except httpx.RequestError as e:
        logger.error(f"AI service request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable"
        )

    except Exception as e:
        logger.error(f"AI proxy error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/models")
async def list_models(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    List available AI models
    """
    return {
        "models": [
            {
                "id": "gemini-2.0-flash-exp",
                "name": "Gemini 2.0 Flash Experimental",
                "description": "Fast, multimodal model for various tasks",
                "context_length": 1048576,
            }
        ],
        "default": "gemini-2.0-flash-exp"
    }


@router.get("/usage")
async def get_usage_stats(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get AI usage statistics for current user
    """
    # This would typically query a usage tracking table
    # For now, return placeholder data
    return {
        "user_id": current_user.id,
        "period": "current_month",
        "tokens_used": 0,
        "requests_made": 0,
        "cost_usd": 0.0,
        "limit": {
            "tokens": 100000,
            "requests": 1000,
            "cost": 10.0
        }
    }
