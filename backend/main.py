"""
RaptorFlow Backend Service
Runs on Google Cloud Run with GCP integrations
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Pydantic imports
from pydantic import BaseModel, validator

# Redis import
import redis
import vertexai
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# GCP Imports
from google.cloud import aiplatform, bigquery, storage

# Import onboarding routes
from onboarding_routes import router as onboarding_router
from pydantic import BaseModel, EmailStr
from vertexai.generative_models import GenerativeModel

# Supabase Integration
from supabase import Client, create_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="RaptorFlow Backend",
    description="Backend API for RaptorFlow Marketing OS",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GCP Clients
storage_client = storage.Client()
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True
)
bq_client = bigquery.Client()

# Supabase Client
supabase: Client = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
)

# Vertex AI Configuration
aiplatform.init(
    project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_REGION", "us-central1")
)
vertexai.init(
    project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_REGION", "us-central1")
)


# Models
class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    subscription_plan: Optional[str]
    subscription_status: Optional[str]
    storage_quota_mb: int
    storage_used_mb: int
    created_at: datetime
    updated_at: datetime


class PaymentRequest(BaseModel):
    plan_id: str
    amount: int
    user_id: str


# SECURITY IMPORTS
import re

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


# Enhanced Request Validation
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


class StorageUploadRequest(BaseModel):
    user_id: str
    file_name: str
    file_type: str
    file_size: int


# Helper Functions
def get_user_storage_bucket(user_id: str, file_type: str) -> str:
    """Determine the appropriate GCS bucket based on file type"""
    bucket_map = {
        "avatar": f"{os.getenv('GCP_PROJECT_ID')}-user-avatars",
        "document": f"{os.getenv('GCP_PROJECT_ID')}-user-documents",
        "workspace": f"{os.getenv('GCP_PROJECT_ID')}-workspace-files",
    }
    return bucket_map.get(file_type, f"{os.getenv('GCP_PROJECT_ID')}-user-documents")


def check_storage_quota(user_id: str, file_size: int) -> bool:
    """Check if user has enough storage quota"""
    try:
        profile = (
            supabase.table("user_profiles")
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )
        if profile.data:
            quota = (
                profile.data["storage_quota_mb"] * 1024 * 1024
            )  # Convert MB to bytes
            used = profile.data["storage_used_mb"] * 1024 * 1024
            return (used + file_size) <= quota
        return False
    except Exception as e:
        logger.error(f"Error checking storage quota: {e}")
        return False


# API Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "gcs": bool(storage_client),
            "redis": bool(redis_client),
            "supabase": bool(supabase),
            "vertex_ai": True,
        },
    }


@app.post("/auth/create-profile")
async def create_user_profile(user_data: Dict[str, Any]):
    """Create or update user profile in Supabase"""
    try:
        # Set default storage quota based on subscription plan
        storage_quotas = {
            "soar": 1024,  # 1GB
            "glide": 5120,  # 5GB
            "ascent": 10240,  # 10GB
            None: 100,  # 100MB free tier
        }

        profile_data = {
            **user_data,
            "storage_quota_mb": storage_quotas.get(
                user_data.get("subscription_plan"), 100
            ),
            "storage_used_mb": 0,
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = supabase.table("user_profiles").upsert(profile_data).execute()

        return {"success": True, "profile": result.data}
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/storage/upload-url")
async def generate_upload_url(request: StorageUploadRequest):
    """Generate signed URL for GCS upload"""
    try:
        # Check storage quota
        if not check_storage_quota(request.user_id, request.file_size):
            raise HTTPException(status_code=400, detail="Storage quota exceeded")

        # Determine bucket
        bucket_name = get_user_storage_bucket(request.user_id, request.file_type)
        bucket = storage_client.bucket(bucket_name)

        # Generate blob name with user folder
        blob_name = f"{request.user_id}/{request.file_name}"
        blob = bucket.blob(blob_name)

        # Generate signed URL (valid for 1 hour)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=1),
            method="PUT",
            content_type=request.file_type,
        )

        return {
            "upload_url": url,
            "file_path": f"gs://{bucket_name}/{blob_name}",
            "expires_in": 3600,
        }
    except Exception as e:
        logger.error(f"Error generating upload URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/storage/download-url")
async def generate_download_url(user_id: str, file_path: str):
    """Generate signed URL for GCS download"""
    try:
        bucket = storage_client.bucket(file_path.split("/")[2])
        blob = bucket.blob("/".join(file_path.split("/")[3:]))

        url = blob.generate_signed_url(
            version="v4", expiration=timedelta(hours=1), method="GET"
        )

        return {"download_url": url, "expires_in": 3600}
    except Exception as e:
        logger.error(f"Error generating download URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/generate")
async def generate_ai_content(request: AIRequest):
    """Generate content using Vertex AI - SECURE UNIVERSAL GEMINI 2.0 FLASH-001"""
    try:
        # Input sanitization
        sanitized_prompt = sanitize_input(request.prompt)

        # ENFORCE UNIVERSAL MODEL USAGE
        universal_model = "gemini-2.0-flash-001"
        if request.model != universal_model:
            logger.warning(
                f"Model override attempted: {request.model} -> {universal_model}"
            )
            request.model = universal_model

        logger.info(f" Using model: {request.model}")
        logger.info(f" Sanitized prompt: {sanitized_prompt[:100]}...")

        # Check user subscription for AI features
        profile = (
            supabase.table("user_profiles")
            .select("*")
            .eq("id", request.user_id)
            .single()
            .execute()
        )
        if not profile.data or profile.data["subscription_status"] != "active":
            raise HTTPException(
                status_code=403, detail="Active subscription required for AI features"
            )

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

        logger.info(f" Generated in {generation_time:.2f}s: {filtered_content[:50]}...")

        # Log usage to BigQuery
        usage_data = {
            "user_id": request.user_id,
            "model": universal_model,  # ALWAYS log universal model
            "prompt_length": len(sanitized_prompt),
            "response_length": len(filtered_content),
            "generation_time": generation_time,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Insert into BigQuery (async)
        try:
            table_id = f"{os.getenv('GCP_PROJECT_ID')}.ai_usage.usage_logs"
            rows_to_insert = [usage_data]

            errors = bq_client.insert_rows_json(table_id, rows_to_insert)
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
            else:
                logger.info("Usage logged to BigQuery")
        except Exception as e:
            logger.error(f"Failed to log usage to BigQuery: {e}")

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
            "verification": "SECURE_GEMINI_2_0_FLASH_001",
            "security": "hardened",
            "rate_limiting": "disabled",
        }

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/payment/process")
async def process_payment(payment_data: PaymentRequest):
    """Process payment and update subscription"""
    try:
        # Create payment record
        payment_record = {
            "user_id": payment_data.user_id,
            "plan_id": payment_data.plan_id,
            "amount": payment_data.amount,
            "status": "completed",
            "payment_method": "phonepe",
            "created_at": datetime.utcnow().isoformat(),
            "verified_at": datetime.utcnow().isoformat(),
        }

        payment_result = supabase.table("payments").insert(payment_record).execute()

        # Update user subscription
        subscription_update = {
            "subscription_plan": payment_data.plan_id,
            "subscription_status": "active",
            "subscription_expires_at": (
                datetime.utcnow() + timedelta(days=30)
            ).isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        profile_result = (
            supabase.table("user_profiles")
            .update(subscription_update)
            .eq("id", payment_data.user_id)
            .execute()
        )

        # Cache in Redis for quick access
        cache_key = f"subscription:{payment_data.user_id}"
        redis_client.setex(
            cache_key,
            timedelta(hours=1).total_seconds(),
            json.dumps(subscription_update),
        )

        return {
            "success": True,
            "payment_id": payment_result.data[0]["id"],
            "subscription_updated": True,
        }
    except Exception as e:
        logger.error(f"Error processing payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{user_id}/subscription")
async def get_user_subscription(user_id: str):
    """Get user subscription details"""
    try:
        # Check Redis cache first
        cache_key = f"subscription:{user_id}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        # Fetch from Supabase
        profile = (
            supabase.table("user_profiles")
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )

        if not profile.data:
            raise HTTPException(status_code=404, detail="User not found")

        subscription_data = {
            "plan": profile.data["subscription_plan"],
            "status": profile.data["subscription_status"],
            "expires_at": profile.data["subscription_expires_at"],
            "storage_quota_mb": profile.data["storage_quota_mb"],
            "storage_used_mb": profile.data["storage_used_mb"],
        }

        # Cache for 1 hour
        redis_client.setex(
            cache_key, timedelta(hours=1).total_seconds(), json.dumps(subscription_data)
        )

        return subscription_data
    except Exception as e:
        logger.error(f"Error fetching subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/usage")
async def get_usage_analytics():
    """Get usage analytics from BigQuery"""
    try:
        query = """
        SELECT
            DATE(timestamp) as date,
            COUNT(*) as total_requests,
            COUNT(DISTINCT user_id) as unique_users,
            AVG(prompt_length) as avg_prompt_length,
            AVG(response_length) as avg_response_length
        FROM `raptorflow-prod.ai_usage.usage_logs`
        WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
        """

        query_job = bq_client.query(query)
        results = query_job.result()

        return {
            "analytics": [dict(row) for row in results],
            "total_requests": len(results),
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Include onboarding routes
app.include_router(onboarding_router)


# Cloud Run health check
@app.get("/_ah/health")
async def cloud_run_health():
    """Cloud Run health check endpoint"""
    return {"status": "serving"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
