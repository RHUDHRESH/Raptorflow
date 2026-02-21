import os

backend_dir = r"c:\Users\hp\OneDrive\Desktop\Raptorflow\backend"

replacements = [
    ("backend.app.", "backend.core."),
    ("backend.infrastructure.", "backend.core."),
    ("backend.features.", "backend.services."),
    ("backend.src.raptorflow.", "backend.services."),
    ("from features.", "from services."),
    ("import features.", "import services."),
    ("from app.", "from core."),
    ("import app.", "import core."),
    ("from infrastructure.", "from core."),
    ("import infrastructure.", "import core.")
]

files_updated = 0
for root, _, files in os.walk(backend_dir):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                
                original_content = content
                
                for old, new in replacements:
                    content = content.replace(old, new)
                
                if content != original_content:
                    with open(path, "w", encoding="utf-8") as file:
                        file.write(content)
                    files_updated += 1
                    print(f"Updated {f}")
            except Exception as e:
                print(f"Failed to process {f}: {e}")

print(f"Successfully updated {files_updated} files.")
