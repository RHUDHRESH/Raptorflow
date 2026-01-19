#!/usr/bin/env python3
"""
Simple test script for Vertex AI integration
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_vertex_ai():
    """Test Vertex AI integration"""
    print("🧪 Testing Vertex AI Integration...")
    print("=" * 50)
    
    # Test 1: Check environment variables
    print("1. Checking environment variables...")
    required_vars = [
        'VERTEX_AI_PROJECT_ID',
        'VERTEX_AI_LOCATION', 
        'VERTEX_AI_MODEL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {missing_vars}")
        return False
    
    # Test 2: Check Vertex AI library
    print("\n2. Checking Vertex AI library...")
    try:
        import vertexai
        print("   ✅ Vertex AI library imported successfully")
    except ImportError as e:
        print(f"   ❌ Vertex AI library not available: {e}")
        return False
    
    # Test 3: Test basic configuration
    print("\n3. Testing configuration...")
    try:
        project_id = os.getenv('VERTEX_AI_PROJECT_ID')
        location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        model_name = os.getenv('VERTEX_AI_MODEL', 'gemini-1.5-flash')
        
        vertexai.init(project=project_id, location=location)
        print(f"   ✅ Vertex AI initialized")
        print(f"   📍 Project: {project_id}")
        print(f"   📍 Location: {location}")
        print(f"   📍 Model: {model_name}")
        
    except Exception as e:
        print(f"   ❌ Vertex AI initialization failed: {e}")
        return False
    
    # Test 4: Test model loading
    print("\n4. Testing model loading...")
    try:
        from vertexai.generative_models import GenerativeModel
        model = GenerativeModel(model_name)
        print(f"   ✅ Model {model_name} loaded successfully")
    except Exception as e:
        print(f"   ❌ Model loading failed: {e}")
        return False
    
    # Test 5: Test simple generation (if credentials are available)
    print("\n5. Testing text generation...")
    try:
        response = model.generate_content("Hello, this is a test.")
        print(f"   ✅ Text generation successful")
        print(f"   📝 Response: {response.text[:100]}...")
    except Exception as e:
        print(f"   ⚠️  Text generation failed (may need credentials): {e}")
        print("   💡 This is expected if GCP credentials are not configured")
    
    print("\n" + "=" * 50)
    print("🎉 Vertex AI integration test completed!")
    print("💡 Next steps:")
    print("   1. Set up GCP credentials")
    print("   2. Configure environment variables")
    print("   3. Test with actual API calls")
    
    return True

if __name__ == "__main__":
    test_vertex_ai()
