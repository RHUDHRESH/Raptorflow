#!/usr/bin/env python3
"""
Test Gemini models with different naming conventions
"""

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    from google.cloud import aiplatform
    print("✅ Vertex AI libraries imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

# Gemini model variations to test
gemini_models = [
    # Latest Gemini models
    'gemini-1.5-flash',
    'gemini-1.5-flash-001',
    'gemini-1.5-flash-002',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash@001',
    'gemini-1.5-flash@002',
    
    'gemini-1.5-pro',
    'gemini-1.5-pro-001', 
    'gemini-1.5-pro-002',
    'gemini-1.5-pro-latest',
    'gemini-1.5-pro@001',
    'gemini-1.5-pro@002',
    
    # Older Gemini models
    'gemini-pro',
    'gemini-pro-vision',
    'gemini-pro-latest',
    'gemini-pro@001',
    
    # Just in case
    'gemini-2.0-flash-exp',
    'gemini-2.0-flash-exp@001',
]

async def test_gemini_model(model_name):
    """Test a specific Gemini model"""
    try:
        print(f"🧪 Testing: {model_name}")
        
        # Initialize Vertex AI
        project_id = os.getenv('VERTEX_AI_PROJECT_ID')
        location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        vertexai.init(project=project_id, location=location)
        
        # Try to create the model
        model = GenerativeModel(model_name)
        
        # Test with a simple query
        response = model.generate_content("Hello! Please respond with just 'Hi back!'")
        
        print(f"✅ SUCCESS: {model_name}")
        print(f"📝 Response: {response.text}")
        return True, model_name
        
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            print(f"❌ {model_name} - Model not found")
        elif "permission" in error_msg.lower() or "access" in error_msg.lower():
            print(f"🔒 {model_name} - Access denied (may need to enable)")
        else:
            print(f"❌ {model_name} - {error_msg[:80]}...")
        return False, None

async def try_enable_model(model_name):
    """Try to enable a model through API"""
    try:
        from google.api_core import gapic_v1
        from google.cloud import aiplatform_v1
        
        client = aiplatform_v1.ModelServiceClient()
        
        # Try to get model info (this might trigger auto-enable)
        model_path = f"projects/{os.getenv('VERTEX_AI_PROJECT_ID')}/locations/{os.getenv('VERTEX_AI_LOCATION', 'us-central1')}/publishers/google/models/{model_name}"
        
        try:
            model = client.get_model(name=model_path)
            print(f"✅ Model enabled: {model_name}")
            return True
        except Exception as e:
            print(f"❌ Could not enable {model_name}: {e}")
            return False
            
    except ImportError:
        print("⚠️  Advanced client not available")
        return False

async def main():
    """Test all Gemini models"""
    print("🚀 Testing Gemini Models")
    print("=" * 60)
    
    project_id = os.getenv('VERTEX_AI_PROJECT_ID')
    location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
    
    print(f"📍 Project: {project_id}")
    print(f"📍 Location: {location}")
    
    working_model = None
    
    for model_name in gemini_models:
        success, model = await test_gemini_model(model_name)
        if success:
            working_model = model
            break
        
        # Try to enable the model
        await try_enable_model(model_name)
        
        # Test again after trying to enable
        success, model = await test_gemini_model(model_name)
        if success:
            working_model = model
            break
    
    print("\n" + "=" * 60)
    if working_model:
        print(f"🎉 Found working model: {working_model}")
        print(f"\n💡 Set this in your environment:")
        print(f"export VERTEX_AI_MODEL={working_model}")
        print(f"\n🧪 Test with:")
        print(f"python test_vertex_ai_direct.py")
    else:
        print("❌ No working Gemini models found")
        print("\n💡 Manual steps required:")
        print("1. Go to: https://console.cloud.google.com/vertex-ai")
        print("2. Navigate to Model Garden")
        print("3. Search for 'gemini-1.5-flash'")
        print("4. Click 'Enable' on the model")
        print("5. Try this test again")

if __name__ == "__main__":
    asyncio.run(main())
