
import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

# Load .env
load_dotenv()

print(f"GCP_PROJECT_ID: {os.getenv('GCP_PROJECT_ID')}")

try:
    from backend.agents.config import get_config
    config = get_config()
    print("Config loaded successfully")
    print(f"GCP_PROJECT_ID in config: {config.GCP_PROJECT_ID}")
except Exception as e:
    print(f"Failed to load config: {e}")
    import traceback
    traceback.print_exc()
