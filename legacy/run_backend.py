
import os
import sys
from dotenv import load_dotenv
import uvicorn

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Ensure port is 8000 to match frontend expectations
    port = 8000
    
    print(f"🚀 Starting RaptorFlow Backend on http://localhost:{port}")
    
    # Run the application
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
