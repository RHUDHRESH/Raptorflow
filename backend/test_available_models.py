#!/usr/bin/env python3
"""
Test different Vertex AI models to find available ones
"""

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

try:
    import vertexai
    from vertexai.preview.language_models import TextGenerationModel, ChatModel
    from vertexai.generative_models import GenerativeModel
    print("✅ Vertex AI libraries imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

# Models to test
models_to_test = [
    # Text models
    'text-bison@001',
    'text-bison@002', 
    'text-bison',
    'text-bison-32k',
    'text-unicorn@001',
    
    # Chat models
    'chat-bison@001',
    'chat-bison',
    'chat-bison-32k',
    
    # Gemini models
    'gemini-pro',
    'gemini-pro-vision',
    'gemini-1.0-pro',
    'gemini-1.0-pro-vision',
    
    # Embedding models
    'textembedding-gecko@001',
    'textembedding-gecko@002',
    'textembedding-gecko@003',
]

async def test_model(model_name):
    """Test a specific model"""
    try:
        if 'gemini' in model_name.lower():
            # Try Gemini model
            model = GenerativeModel(model_name)
            response = model.generate_content("Hello")
            print(f"✅ {model_name} - Gemini model works")
            return True
        elif 'chat' in model_name.lower():
            # Try chat model
            model = ChatModel.from_pretrained(model_name)
            response = model.chat(["Hello"])
            print(f"✅ {model_name} - Chat model works")
            return True
        elif 'textembedding' in model_name.lower():
            # Skip embedding models for text generation test
            print(f"⚠️  {model_name} - Embedding model (skip text test)")
            return False
        else:
            # Try text model
            model = TextGenerationModel.from_pretrained(model_name)
            response = model.predict("Hello", max_output_tokens=10)
            print(f"✅ {model_name} - Text model works")
            return True
            
    except Exception as e:
        print(f"❌ {model_name} - Failed: {str(e)[:100]}...")
        return False

async def main():
    """Test all models"""
    print("🔍 Testing Available Vertex AI Models")
    print("=" * 60)
    
    project_id = os.getenv('VERTEX_AI_PROJECT_ID')
    location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
    
    print(f"📍 Project: {project_id}")
    print(f"📍 Location: {location}")
    
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)
    
    working_models = []
    
    for model_name in models_to_test:
        if await test_model(model_name):
            working_models.append(model_name)
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {len(working_models)} working models found")
    
    if working_models:
        print("✅ Working models:")
        for model in working_models:
            print(f"  - {model}")
            
        # Update environment file with working model
        best_model = working_models[0]
        print(f"\n🎯 Recommended model: {best_model}")
        print(f"Set VERTEX_AI_MODEL={best_model} in your environment")
        
    else:
        print("❌ No working models found")
        print("💡 You may need to enable specific models in the Vertex AI console")

if __name__ == "__main__":
    asyncio.run(main())
