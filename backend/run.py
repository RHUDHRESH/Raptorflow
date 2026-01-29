"""
RaptorFlow Backend Startup Script
Properly configures Python path for relative imports
"""

import os
import sys

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Also add parent directory for any cross-module imports
parent_dir = os.path.dirname(backend_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Load environment variables from env file
from dotenv import load_dotenv

load_dotenv(os.path.join(backend_dir, ".env"))

# Now import and run the app
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    reload_enabled = os.environ.get("ENVIRONMENT", "dev").lower() in (
        "dev",
        "development",
    )

    print(f"🚀 Starting RaptorFlow Backend on {host}:{port}")
    print(f"   Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    print(f"   Auto-reload: {reload_enabled}")
    print(f"   Python path: {backend_dir}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload_enabled,
        reload_dirs=[backend_dir] if reload_enabled else None,
    )
