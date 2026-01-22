"""
MINIMAL BACKEND TEST - Test Gemini 1.5 Flash without full backend dependencies
"""

import json
import os
import sys

import vertexai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from vertexai.generative_models import GenerativeModel

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize FastAPI
app = FastAPI(title="Gemini Test Backend")

# Model configuration
UNIVERSAL_MODEL = "gemini-1.5-flash"


class AIRequest(BaseModel):
    prompt: str
    user_id: str
    model: str = UNIVERSAL_MODEL


# Initialize Vertex AI
try:
    project_id = os.getenv("GCP_PROJECT_ID", "raptorflow-481505")
    region = os.getenv("GCP_REGION", "us-central1")

    print(f"Initializing Vertex AI with project: {project_id}, region: {region}")
    vertexai.init(project=project_id, location=region)

    # Test model initialization
    test_model = GenerativeModel(UNIVERSAL_MODEL)
    print(f"✅ Successfully initialized {UNIVERSAL_MODEL}")

except Exception as e:
    print(f"❌ Vertex AI initialization failed: {e}")
    sys.exit(1)


@app.get("/health")
async def health():
    return {"status": "healthy", "model": UNIVERSAL_MODEL}


@app.post("/ai/generate")
async def generate_ai_content(request: AIRequest):
    """Generate content using Vertex AI - UNIVERSALLY ENFORCED GEMINI 1.5 FLASH"""
    try:
        # ENFORCE UNIVERSAL MODEL USAGE
        if request.model != UNIVERSAL_MODEL:
            print(f"⚠️  Model override attempted: {request.model} -> {UNIVERSAL_MODEL}")
            request.model = UNIVERSAL_MODEL

        print(f"🔥 Using REAL Gemini model: {request.model}")
        print(f"📝 Prompt: {request.prompt}")

        # Initialize Vertex AI model (ALWAYS gemini-1.5-flash)
        model = GenerativeModel(UNIVERSAL_MODEL)

        # Generate content
        response = model.generate_content(request.prompt)

        print(f"✅ Generated response: {response.text[:100]}...")

        return {
            "content": response.text,
            "model": UNIVERSAL_MODEL,  # ALWAYS return universal model
            "usage_logged": True,
            "verification": "REAL_GEMINI_1_5_FLASH",
        }

    except Exception as e:
        print(f"❌ Error in AI generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting minimal Gemini test backend on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
