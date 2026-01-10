"""
MINIMAL BACKEND TEST FOR GEMINI-2.0-FLASH-001
Simple test to verify the backend works with the new model
"""

import os

import uvicorn
import vertexai
from fastapi import FastAPI
from pydantic import BaseModel
from vertexai.generative_models import GenerativeModel

app = FastAPI(title="Gemini 2.0 Flash Test")


class AIRequest(BaseModel):
    prompt: str
    user_id: str
    model: str = "gemini-2.0-flash-001"


# Initialize Vertex AI
project_id = os.getenv("GCP_PROJECT_ID", "raptorflow-481505")
region = os.getenv("GCP_REGION", "us-central1")

print(f"🚀 Initializing Vertex AI: {project_id} in {region}")
vertexai.init(project=project_id, location=region)


@app.get("/")
async def root():
    return {"message": "Gemini 2.0 Flash Test Backend", "model": "gemini-2.0-flash-001"}


@app.get("/health")
async def health():
    return {"status": "healthy", "model": "gemini-2.0-flash-001"}


@app.post("/ai/generate")
async def generate_ai_content(request: AIRequest):
    """Generate content using Vertex AI - GEMINI-2.0-FLASH-001"""
    try:
        # ENFORCE UNIVERSAL MODEL USAGE
        universal_model = "gemini-2.0-flash-001"
        if request.model != universal_model:
            print(f"⚠️  Model override attempted: {request.model} -> {universal_model}")
            request.model = universal_model

        print(f"🔥 Using model: {request.model}")
        print(f"📝 Prompt: {request.prompt}")

        # Initialize Vertex AI model
        model = GenerativeModel(universal_model)

        # Generate content
        response = model.generate_content(request.prompt)

        print(f"✅ Generated: {response.text[:50]}...")

        return {
            "content": response.text,
            "model": universal_model,
            "usage_logged": True,
            "verification": "REAL_GEMINI_2_0_FLASH_001",
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    print("🌐 Starting minimal Gemini backend on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
