#!/usr/bin/env python3
"""
Windows-compatible unicode character fixer
"""

import os
import re
import sys
import locale

# Ensure UTF-8 encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

def fix_file_encoding(file_path):
    """Fix encoding issues in a Python file"""
    try:
        # Read with error handling
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Replace problematic characters
        content = content.replace('≈', '~')
        content = content.replace('₹', 'INR')
        content = content.replace('\u2248', '~')
        content = content.replace('\u20b9', 'INR')
        
        # Remove any other non-ASCII characters
        content = re.sub(r'[^\x00-\x7F]', '', content)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix encoding issues in all Python files"""
    backend_core_path = os.path.join(os.path.dirname(__file__), 'backend', 'core')
    
    fixed_files = 0
    total_files = 0
    
    for root, dirs, files in os.walk(backend_core_path):
        for file in files:
            if file.endswith('.py'):
                total_files += 1
                file_path = os.path.join(root, file)
                if fix_file_encoding(file_path):
                    fixed_files += 1
                    print(f"Fixed: {file_path}")
    
    print(f"\nFixed encoding issues in {fixed_files}/{total_files} files")

if __name__ == "__main__":
    main()
