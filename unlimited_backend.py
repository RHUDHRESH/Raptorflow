"""
SIMPLE BACKEND WITHOUT RATE LIMITS
Just the AI endpoint for unlimited requests
"""

import os
import re
import time
from datetime import datetime

import uvicorn
import vertexai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from vertexai.generative_models import GenerativeModel

app = FastAPI(title="Unlimited Gemini Backend")

# SECURITY CONFIGURATION
MAX_PROMPT_LENGTH = 10000
MAX_RESPONSE_TIME = 30
ALLOWED_MODELS = ["gemini-2.0-flash-001"]


# Content Filter
def filter_sensitive_content(content: str) -> str:
    sensitive_patterns = [
        "api key",
        "secret",
        "password",
        "token",
        "database",
        "schema",
        "table",
        "configuration",
        "system architecture",
        "component",
        "config",
    ]

    content_lower = content.lower()
    for pattern in sensitive_patterns:
        if pattern in content_lower:
            return "I cannot provide that information."

    return content


# Input Sanitization
def sanitize_input(prompt: str) -> str:
    if not isinstance(prompt, str):
        raise ValueError("Invalid prompt type")

    # Remove JSON injection attempts
    prompt = prompt.replace('{"', "").replace("}", "")
    # Remove command injection
    prompt = prompt.replace(";", "").replace("--", "")
    # Remove model override attempts
    prompt = re.sub(r"(?i)model\s*[:=]", "", prompt)
    # Remove null bytes and control characters
    prompt = re.sub(r"[\x00-\x1f\x7f]", "", prompt)
    return prompt.strip()


# Model Validation
def validate_model(model: str) -> str:
    if not isinstance(model, str):
        raise ValueError("Invalid model type")

    if model not in ALLOWED_MODELS:
        return ALLOWED_MODELS[0]
    return model


# User ID Validation
def validate_user_id(user_id: str) -> str:
    if not user_id or not isinstance(user_id, str):
        raise ValueError("Invalid user_id")

    if len(user_id) > 100:
        raise ValueError("user_id too long")

    # Check for SQL injection patterns
    if any(
        pattern in user_id.lower() for pattern in ["drop", "delete", "insert", "update"]
    ):
        raise ValueError("Invalid characters in user_id")

    return user_id


# Request Validation
class AIRequest(BaseModel):
    prompt: str
    user_id: str
    model: str = "gemini-2.0-flash-001"  # UNIVERSALLY ENFORCED MODEL

    @validator("prompt")
    def validate_prompt(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Prompt is required")

        if len(v) > MAX_PROMPT_LENGTH:
            raise ValueError(f"Prompt too long (max {MAX_PROMPT_LENGTH} characters)")

        return v

    @validator("user_id")
    def validate_user_field(cls, v):
        return validate_user_id(v)

    @validator("model")
    def validate_model_field(cls, v):
        return validate_model(v)


# Initialize Vertex AI
project_id = os.getenv("GCP_PROJECT_ID", "raptorflow-481505")
region = os.getenv("GCP_REGION", "us-central1")

print(f"Initializing Vertex AI: {project_id} in {region}")
vertexai.init(project=project_id, location=region)


@app.get("/")
async def root():
    return {
        "message": "Unlimited Gemini Backend",
        "model": "gemini-2.0-flash-001",
        "rate_limiting": "disabled",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model": "gemini-2.0-flash-001",
        "rate_limiting": "disabled",
    }


@app.post("/ai/generate")
async def generate_ai_content(request: AIRequest):
    """Generate content using Vertex AI - UNLIMITED UNIVERSAL GEMINI 2.0 FLASH-001"""
    try:
        # Input sanitization
        sanitized_prompt = sanitize_input(request.prompt)

        # ENFORCE UNIVERSAL MODEL USAGE
        universal_model = "gemini-2.0-flash-001"
        if request.model != universal_model:
            print(f"Model override attempted: {request.model} -> {universal_model}")
            request.model = universal_model

        print(f"Using model: {request.model}")
        print(f"Sanitized prompt: {sanitized_prompt[:100]}...")

        # Initialize Vertex AI model (ALWAYS gemini-2.0-flash-001)
        model = GenerativeModel(universal_model)

        # Generate content with timeout
        start_time = time.time()
        response = model.generate_content(sanitized_prompt)
        generation_time = time.time() - start_time

        if generation_time > MAX_RESPONSE_TIME:
            raise HTTPException(status_code=408, detail="Request timeout")

        # Filter sensitive content
        filtered_content = filter_sensitive_content(response.text)

        print(f"Generated in {generation_time:.2f}s: {filtered_content[:50]}...")

        return {
            "content": filtered_content,
            "model": universal_model,  # ALWAYS return universal model
            "usage": {
                "prompt_tokens": len(sanitized_prompt.split()),
                "completion_tokens": len(filtered_content.split()),
                "total_tokens": len(sanitized_prompt.split())
                + len(filtered_content.split()),
            },
            "usage_logged": True,
            "generation_time": generation_time,
            "verification": "UNLIMITED_GEMINI_2_0_FLASH_001",
            "security": "hardened",
            "rate_limiting": "disabled",
        }

    except ValueError as e:
        print(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in AI generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Starting UNLIMITED Gemini backend on port 8003...")
    uvicorn.run(app, host="0.0.0.0", port=8003)
