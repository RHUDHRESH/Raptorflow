
import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Load environment variables
load_dotenv()

try:
    print("Attempting to import backend.main:app...")
    from backend.main import app
    print("✅ Successfully imported FastAPI app")
    
    print("Checking routes...")
    for route in app.routes:
        print(f"Route: {route.path}")
except Exception as e:
    print(f"❌ Failed to start backend: {e}")
    import traceback
    traceback.print_exc()
