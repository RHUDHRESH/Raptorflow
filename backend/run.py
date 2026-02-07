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


def main() -> None:
    """Deprecated runner. Use backend.run_simple.main instead."""
    from backend.run_simple import main as run_main

    print("Deprecated: use backend.run_simple.py")
    run_main()


if __name__ == "__main__":
    main()
