import importlib
import os
import sys

# Add project root to sys.path
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

backend_dir = os.path.join(project_root, "backend")

errors = []

for root, dirs, files in os.walk(backend_dir):
    if "__pycache__" in dirs:
        dirs.remove("__pycache__")

    for file in files:
        if file.endswith(".py") and file != "__init__.py":
            relative_path = os.path.relpath(os.path.join(root, file), project_root)
            module_name = relative_path.replace(os.path.sep, ".").replace(".py", "")

            try:
                importlib.import_module(module_name)
                # print(f"Successfully imported {module_name}")
            except Exception as e:
                errors.append(f"Error importing {module_name}: {type(e).__name__}: {e}")

if errors:
    print("\n--- IMPORT ERRORS FOUND ---")
    for err in errors:
        print(err)
else:
    print("All backend modules imported successfully!")
