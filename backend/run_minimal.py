"""
Minimal RaptorFlow Backend Startup
Bypasses GCP/storage issues for basic functionality
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv

load_dotenv(os.path.join(backend_dir, ".env"))

# Set environment variables to bypass GCP issues
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
os.environ["STORAGE_DISABLED"] = "true"
os.environ["GCS_DISABLED"] = "true"

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")

    print(f"🚀 Starting Minimal RaptorFlow Backend on {host}:{port}")
    print(f"   Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    print(f"   GCP Storage: DISABLED (bypassing credentials)")

    uvicorn.run(
        "main_minimal:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=[str(backend_dir)],
    )
