#!/usr/bin/env python3
"""
Simple backend starter - bypasses import issues
"""
import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("=== Starting Raptorflow Backend ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {current_dir}")

try:
    # Set environment variables
    os.environ['DATABASE_URL'] = 'sqlite:///./raptorflow.db'
    os.environ['ENVIRONMENT'] = 'development'
    os.environ['DEBUG'] = 'true'
    os.environ['MOCK_REDIS'] = 'true'
    os.environ['GEMINI_API_KEY'] = 'mock_key_for_testing'
    
    print("✅ Environment variables set")
    
    # Import and start main
    from main import app
    import uvicorn
    
    print("✅ Main app imported")
    
    # Start server
    print("🚀 Starting server on http://localhost:8000")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    
except Exception as e:
    print(f"❌ Failed to start: {e}")
    import traceback
    traceback.print_exc()
