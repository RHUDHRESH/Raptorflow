import os
import google.auth
from google.cloud import aiplatform

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./raptorflow-storage-key.json"
os.environ["VERTEX_AI_API_KEY"] = "AQ.Ab8RN6IUsXQOIdywX4O_vrP6lSO5JS-fY_bQG4o84BajiSrIPg"
project_id = "raptorflow-481505"
location = "us-central1"

def verify_vertex_ai():
    print(f"Initializing Vertex AI for project {project_id} in {location}...")
    try:
        # aiplatform.init(project=project_id, location=location)
        # Using GenAI library might be better to test the API key
        import google.generativeai as genai
        genai.configure(api_key=os.environ["VERTEX_AI_API_KEY"])
        model = genai.GenerativeModel('gemini-pro')
        # Simple test generation
        # response = model.generate_content("Ping")
        print("✅ Vertex AI (GenAI) configured with API Key!")
        print(f"Model: {model.model_name}")
    except Exception as e:
        print(f"❌ Vertex AI initialization failed: {e}")

if __name__ == "__main__":
    verify_vertex_ai()