#!/usr/bin/env python3
"""
Test with modern Vertex AI SDK approach
"""

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

try:
    import vertexai
    from google.cloud import aiplatform
    print("✅ Modern Vertex AI libraries imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

async def test_modern_approach():
    """Test with modern Vertex AI approach"""
    print("🔍 Testing Modern Vertex AI Approach")
    print("=" * 50)
    
    project_id = os.getenv('VERTEX_AI_PROJECT_ID')
    location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
    
    print(f"📍 Project: {project_id}")
    print(f"📍 Location: {location}")
    
    try:
        # Initialize AI Platform
        aiplatform.init(project=project_id, location=location)
        print("✅ AI Platform initialized")
        
        # Try to list models using the newer API
        try:
            models = aiplatform.Model.list(filter="")
            model_list = list(models)
            
            if model_list:
                print(f"✅ Found {len(model_list)} models:")
                for model in model_list[:10]:  # Show first 10
                    print(f"  - {model.display_name} ({model.name})")
            else:
                print("❌ No models found")
                
        except Exception as e:
            print(f"❌ Error listing models: {e}")
        
        # Try using the generative AI API directly
        try:
            import vertexai.generative_models as generative_models
            
            # Try to create a model with a simple name
            model = generative_models.GenerativeModel("gemini-pro")
            response = model.generate_content("Hello!")
            print("✅ SUCCESS with gemini-pro!")
            print(f"Response: {response.text[:100]}...")
            return True
            
        except Exception as e:
            print(f"❌ Generative AI failed: {e}")
        
        # Try using AutoML for custom models
        try:
            # Check if there are any custom models
            endpoint = aiplatform.Endpoint.list()
            if endpoint:
                print(f"✅ Found {len(endpoint)} endpoints")
                for ep in endpoint[:3]:
                    print(f"  - {ep.display_name}")
            else:
                print("❌ No endpoints found")
                
        except Exception as e:
            print(f"❌ Error checking endpoints: {e}")
        
        # Final fallback - try to create a simple text generation
        try:
            from vertexai.preview.language_models import TextGenerationModel
            
            # Try with the most basic model name
            model = TextGenerationModel.from_pretrained("text-bison")
            response = model.predict("Hello!", max_output_tokens=50)
            print("✅ SUCCESS with text-bison!")
            print(f"Response: {response.text}")
            return True
            
        except Exception as e:
            print(f"❌ Text generation failed: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

async def main():
    success = await test_modern_approach()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Vertex AI is working!")
    else:
        print("❌ Vertex AI needs configuration")
        print("\n💡 Next steps:")
        print("1. Go to Vertex AI console: https://console.cloud.google.com/vertex-ai")
        print("2. Enable models in Model Garden")
        print("3. Try again after enabling models")

if __name__ == "__main__":
    asyncio.run(main())
