#!/usr/bin/env python
"""
Fix Import Paths Script

Systematically fixes all import paths in the backend to use relative imports
instead of 'backend.module' imports.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 'from ' imports
        content = re.sub(r'from backend\.', 'from ', content)
        
        # Fix 'import ' imports
        content = re.sub(r'import backend\.', 'import ', content)
        
        # Fix 'from backend import' to relative imports where possible
        # This is more complex and requires context
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
            return True
        else:
            print(f"No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def find_and_fix_imports(root_dir):
    """Find and fix imports in all Python files."""
    root_path = Path(root_dir)
    fixed_count = 0
    total_count = 0
    
    for py_file in root_path.rglob('*.py'):
        # Skip __pycache__ and other cache directories
        if '__pycache__' in str(py_file) or '.pytest_cache' in str(py_file):
            continue
            
        total_count += 1
        if fix_imports_in_file(py_file):
            fixed_count += 1
    
    print(f"\nSummary: Fixed {fixed_count} out of {total_count} Python files")
    return fixed_count

if __name__ == "__main__":
    backend_dir = Path(__file__).parent
    print(f"Fixing imports in: {backend_dir}")
    
    fixed = find_and_fix_imports(backend_dir)
    
    if fixed > 0:
        print(f"Successfully fixed imports in {fixed} files")
    else:
        print("No imports needed fixing")
