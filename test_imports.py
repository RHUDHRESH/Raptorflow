
import os
import sys

# Add project root to sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")

try:
    import backend
    print(f"Backend file: {backend.__file__}")
    
    import backend.agents
    print(f"Backend agents file: {backend.agents.__file__}")
    
    import backend.agents.config
    print(f"Backend agents config file: {backend.agents.config.__file__}")
    
    from backend.agents.config import get_config
    config = get_config()
    print("Config loaded successfully")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
