"""
Script to fix all relative imports in the backend codebase.
Converts 'from ..X' to 'from backend.X' for proper package imports.
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
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        return False, 0
    
    original_content = content
    changes = 0
    
    # Pattern to match 'from ..X import' where X is a module name
    # This handles cases like:
    # - from ..config import X
    # - from ..core.X import Y
    # - from ..agents.X import Y
    
    # Get the relative path from backend directory to determine the correct import prefix
    try:
        rel_path = filepath.relative_to(Path(__file__).parent)
        depth = len(rel_path.parts) - 1  # -1 for the filename itself
    except ValueError:
        depth = 2  # Default depth
    
    # Replace 'from ..' patterns based on the file's location
    # Pattern: from ..X where .. goes outside a subpackage
    
    # For files in backend/agents/*, from ..config should become from backend.config
    # For files in backend/agents/specialists/*, from ..config should become from backend.agents.config
    
    # Simple approach: Replace all 'from ..' that would go outside 'backend' package
    
    # Pattern 1: from ..config (goes to backend/config from backend/agents/)
    pattern1 = r'from \.\.config\b'
    replacement1 = 'from backend.config'
    new_content, n = re.subn(pattern1, replacement1, content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ..config' -> 'from backend.config'")
    
    # Pattern 2: from ..core (goes to backend/core from backend/agents/)
    pattern2 = r'from \.\.core\b'
    replacement2 = 'from backend.core'
    new_content, n = re.subn(pattern2, replacement2, content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ..core' -> 'from backend.core'")
    
    # Pattern 3: from ..agents (rare, but handle it)
    pattern3 = r'from \.\.agents\b'
    replacement3 = 'from backend.agents'
    new_content, n = re.subn(pattern3, replacement3, content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ..agents' -> 'from backend.agents'")
    
    # Pattern 4: from ...X (three dots - for api/v1/* files going to backend root)
    # from ...config -> from backend.config
    # from ...core -> from backend.core
    # from ...agents -> from backend.agents
    pattern4a = r'from \.\.\.config\b'
    new_content, n = re.subn(pattern4a, 'from backend.config', content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ...config' -> 'from backend.config'")
    
    pattern4b = r'from \.\.\.core\b'
    new_content, n = re.subn(pattern4b, 'from backend.core', content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ...core' -> 'from backend.core'")
    
    pattern4c = r'from \.\.\.agents\b'
    new_content, n = re.subn(pattern4c, 'from backend.agents', content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ...agents' -> 'from backend.agents'")
    
    pattern4d = r'from \.\.\.services\b'
    new_content, n = re.subn(pattern4d, 'from backend.services', content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ...services' -> 'from backend.services'")
    
    pattern4e = r'from \.\.\.db\b'
    new_content, n = re.subn(pattern4e, 'from backend.db', content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ...db' -> 'from backend.db'")
    
    pattern4f = r'from \.\.\.events\b'
    new_content, n = re.subn(pattern4f, 'from backend.events', content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from ...events' -> 'from backend.events'")
    
    # Pattern 5: Absolute imports without backend. prefix (for main.py and similar files)
    # These are at the start of a line or after newline
    
    # from api. -> from backend.api.
    pattern5a = r'^from api\.'
    new_content, n = re.subn(pattern5a, 'from backend.api.', content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from api.' -> 'from backend.api.'")
    
    # from core. -> from backend.core.
    pattern5b = r'^from core\.'
    new_content, n = re.subn(pattern5b, 'from backend.core.', content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from core.' -> 'from backend.core.'")
    
    # from core (without dot) -> from backend.core
    pattern5m = r'^from core\b'
    new_content, n = re.subn(pattern5m, 'from backend.core', content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from core' -> 'from backend.core'")
    
    # from agents. -> from backend.agents.
    pattern5j = r'^from agents\.'
    new_content, n = re.subn(pattern5j, 'from backend.agents.', content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from agents.' -> 'from backend.agents.'")
    
    # from services. -> from backend.services.
    pattern5k = r'^from services\.'
    new_content, n = re.subn(pattern5k, 'from backend.services.', content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from services.' -> 'from backend.services.'")
    
    # from config. -> from backend.config.
    pattern5l = r'^from config\.'
    new_content, n = re.subn(pattern5l, 'from backend.config.', content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from config.' -> 'from backend.config.'")
    
    # from middleware. -> from backend.middleware.
    pattern5c = r'^from middleware\.'
    new_content, n = re.subn(pattern5c, 'from backend.middleware.', content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from middleware.' -> 'from backend.middleware.'")
    
    # from dependencies -> from backend.dependencies
    pattern5d = r'^from dependencies\b'
    new_content, n = re.subn(pattern5d, 'from backend.dependencies', content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from dependencies' -> 'from backend.dependencies'")
    
    # from startup -> from backend.startup
    pattern5e = r'^from startup\b'
    new_content, n = re.subn(pattern5e, 'from backend.startup', content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from startup' -> 'from backend.startup'")
    
    # from shutdown -> from backend.shutdown
    pattern5f = r'^from shutdown\b'
    new_content, n = re.subn(pattern5f, 'from backend.shutdown', content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from shutdown' -> 'from backend.shutdown'")
    
    # from redis_services_activation -> from backend.redis_services_activation
    pattern5g = r'^from redis_services_activation\b'
    new_content, n = re.subn(pattern5g, 'from backend.redis_services_activation', content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from redis_services_activation' -> 'from backend.redis_services_activation'")
    
    # from backend.config import ModelTier -> from backend.agents.config import ModelTier
    pattern5i = r'from backend\.config import ModelTier'
    new_content, n = re.subn(pattern5i, 'from backend.agents.config import ModelTier', content)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from backend.config import ModelTier' -> 'from backend.agents.config import ModelTier'")
    
    # from .jobs -> from backend.jobs (relative to main.py)
    pattern5h = r'^from \.jobs\b'
    new_content, n = re.subn(pattern5h, 'from backend.jobs', content, flags=re.MULTILINE)
    if n > 0:
        content = new_content
        changes += n
        print(f"  Fixed {n} 'from .jobs' -> 'from backend.jobs'")
    
    if changes > 0:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
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
    print(f"Summary: Modified {total_files_modified} files with {total_changes} total changes")
    print("=" * 60)


if __name__ == "__main__":
    main()
