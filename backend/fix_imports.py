"""
Script to fix all relative imports in the backend codebase.
Converts 'from X' to 'from X' for proper package imports.
"""

import os
import re
from pathlib import Path


def fix_imports_in_file(filepath: Path) -> tuple[bool, int]:
    """Fix relative imports in a single file.

    Returns:
        tuple: (was_modified, number_of_changes)
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        return False, 0

    original_content = content
    changes = 0

    # Pattern to match 'from X import' where X is a module name
    # This handles cases like:
    # - from config import X
    # - from core.X import Y
    # - from agents.X import Y

    # Get the relative path from backend directory to determine the correct import prefix
    try:
        rel_path = filepath.relative_to(Path(__file__).parent)
        depth = len(rel_path.parts) - 1  # -1 for the filename itself
    except ValueError:
        depth = 2  # Default depth

    # Replace 'from ..' patterns based on the file's location
    # Pattern: from X where .. goes outside a subpackage

    # For files in backend/agents/*, from config should become from config
    # For files in backend/agents/specialists/*, from config should become from agents.config

    # Simple approach: Replace all 'from ..' that would go outside 'backend' package

    # Pattern 1: from config (goes to backend/config from backend/agents/)
    pattern1 = r"from \.\.config\b"
    replacement1 = "from config"
    new_content, n = re.subn(pattern1, replacement1, content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from config' -> 'from config'")

    # Pattern 2: from core (goes to backend/core from backend/agents/)
    pattern2 = r"from \.\.core\b"
    replacement2 = "from core"
    new_content, n = re.subn(pattern2, replacement2, content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from core' -> 'from core'")

    # Pattern 3: from agents (rare, but handle it)
    pattern3 = r"from \.\.agents\b"
    replacement3 = "from agents"
    new_content, n = re.subn(pattern3, replacement3, content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from agents' -> 'from agents'")

    # Pattern 4: from ...X (three dots - for api/v1/* files going to backend root)
    # from ...config -> from config
    # from ...core -> from core
    # from ...agents -> from agents
    pattern4a = r"from \.\.\.config\b"
    new_content, n = re.subn(pattern4a, "from config", content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ...config' -> 'from config'")

    pattern4b = r"from \.\.\.core\b"
    new_content, n = re.subn(pattern4b, "from core", content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ...core' -> 'from core'")

    pattern4c = r"from \.\.\.agents\b"
    new_content, n = re.subn(pattern4c, "from agents", content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ...agents' -> 'from agents'")

    pattern4d = r"from \.\.\.services\b"
    new_content, n = re.subn(pattern4d, "from services", content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ...services' -> 'from services'")

    pattern4e = r"from \.\.\.db\b"
    new_content, n = re.subn(pattern4e, "from db", content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ...db' -> 'from db'")

    pattern4f = r"from \.\.\.events\b"
    new_content, n = re.subn(pattern4f, "from events", content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ...events' -> 'from events'")

    # Pattern 5: Absolute imports without backend. prefix (for main.py and similar files)
    # These are at the start of a line or after newline

    # from api. -> from api.
    pattern5a = r"^from api\."
    new_content, n = re.subn(pattern5a, "from api.", content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from api.' -> 'from api.'")

    # from core. -> from core.
    pattern5b = r"^from core\."
    new_content, n = re.subn(pattern5b, "from core.", content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from core.' -> 'from core.'")

    # from core (without dot) -> from core
    pattern5m = r"^from core\b"
    new_content, n = re.subn(pattern5m, "from core", content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from core' -> 'from core'")

    # from agents. -> from agents.
    pattern5j = r"^from agents\."
    new_content, n = re.subn(pattern5j, "from agents.", content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from agents.' -> 'from agents.'")

    # from services. -> from services.
    pattern5k = r"^from services\."
    new_content, n = re.subn(pattern5k, "from services.", content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from services.' -> 'from services.'")

    # from config. -> from config.
    pattern5l = r"^from config\."
    new_content, n = re.subn(pattern5l, "from config.", content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from config.' -> 'from config.'")

    # from middleware. -> from middleware.
    pattern5c = r"^from middleware\."
    new_content, n = re.subn(pattern5c, "from middleware.", content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from middleware.' -> 'from middleware.'")

    # from dependencies -> from dependencies
    pattern5d = r"^from dependencies\b"
    new_content, n = re.subn(
        pattern5d, "from dependencies", content, flags=re.MULTILINE
    )
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from dependencies' -> 'from dependencies'")

    # from startup -> from startup
    pattern5e = r"^from startup\b"
    new_content, n = re.subn(pattern5e, "from startup", content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from startup' -> 'from startup'")

    # from shutdown -> from shutdown
    pattern5f = r"^from shutdown\b"
    new_content, n = re.subn(pattern5f, "from shutdown", content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from shutdown' -> 'from shutdown'")

    # from redis_services_activation -> from redis_services_activation
    pattern5g = r"^from redis_services_activation\b"
    new_content, n = re.subn(
        pattern5g, "from redis_services_activation", content, flags=re.MULTILINE
    )
    if n > 0:
        content = new_content
        changes += n
        print(
            f"  Fixed {n} 'from redis_services_activation' -> 'from redis_services_activation'"
        )

    # from config import ModelTier -> from agents.config import ModelTier
    pattern5i = r"from backend\.config import ModelTier"
    new_content, n = re.subn(pattern5i, "from agents.config import ModelTier", content)
    if n > 0:
        content = new_content
        changes += n
        print(
            f"  Fixed {n} 'from config import ModelTier' -> 'from agents.config import ModelTier'"
        )

    # from jobs -> from jobs (relative to main.py)
    pattern5h = r"^from \.jobs\b"
    new_content, n = re.subn(pattern5h, "from jobs", content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from jobs' -> 'from jobs'")

    if changes > 0:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True, changes
        except Exception as e:
            print(f"  Error writing {filepath}: {e}")
            return False, 0

    return False, 0


def main():
    backend_dir = Path(__file__).parent

    print(f"Fixing imports in: {backend_dir}")
    print("=" * 60)

    total_files_modified = 0
    total_changes = 0

    # Find all Python files
    for py_file in backend_dir.rglob("*.py"):
        # Skip this script itself
        if py_file.name == "fix_imports.py":
            continue

        # Skip __pycache__ directories
        if "__pycache__" in str(py_file):
            continue

        print(f"\nProcessing: {py_file.relative_to(backend_dir)}")
        modified, changes = fix_imports_in_file(py_file)
        if modified:
            total_files_modified += 1
            total_changes += changes

    print("\n" + "=" * 60)
    print(
        f"Summary: Modified {total_files_modified} files with {total_changes} total changes"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
