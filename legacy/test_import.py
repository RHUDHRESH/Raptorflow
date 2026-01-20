import traceback

try:
    from backend.main import app
    print("SUCCESS!")
except Exception as e:
    traceback.print_exc()
