#!/usr/bin/env python3
"""
Find unicode characters in Python files
"""

import os
import re

def find_unicode_chars_in_file(file_path):
    """Find unicode characters in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for unicode characters
            unicode_chars = re.findall(r'[\U0001f000-\U0001F7FF]', content)
            if unicode_chars:
                print(f"File: {file_path}")
                print(f"Unicode characters found: {len(unicode_chars)}")
                # Show specific lines
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if re.search(r'[\U0001f000-\U0001F7FF]', line):
                        print(f"  Line {i+1}: {line.strip()[:80]}...")
                return True
            return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def search_backend_core():
    """Search all Python files in backend/core for unicode characters"""
    backend_core_path = os.path.join(os.path.dirname(__file__), 'backend', 'core')
    
    unicode_files = []
    
    for root, dirs, files in os.walk(backend_core_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if find_unicode_chars_in_file(file_path):
                    unicode_files.append(file_path)
    
    print(f"Found unicode characters in {len(unicode_files)} files:")
    for file_path in unicode_files:
        print(f"  {file_path}")
    
    return unicode_files

if __name__ == "__main__":
    unicode_files = search_backend_core()
    print(f"Total files with unicode: {len(unicode_files)}")
    
    if unicode_files:
        print("\nRECOMMENDATION:")
        print("1. Replace unicode characters with ASCII equivalents")
        print("2. Use ASCII characters in logging messages")
        print("3. Set proper encoding in Python scripts")

if __name__ == "__main__":
    search_backend_core()
