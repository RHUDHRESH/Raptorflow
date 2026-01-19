#!/usr/bin/env python3
"""
Fix unicode characters in Python files
"""

import os
import re
import sys

def fix_unicode_in_file(file_path):
    """Fix unicode characters in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace unicode characters with ASCII equivalents
        content = content.replace('ℹ️', '[INFO]')
        content = content.replace('⚠️', '[WARNING]')
        content = content.replace('❌', '[ERROR]')
        content = content.replace('🚨', '[CRITICAL]')
        content = content.replace('📢', '[INFO]')
        content = content.replace('🔥', '[INFO]')
        content = content.replace('📊', '[INFO]')
        content = content.replace('✅', '[SUCCESS]')
        content = content.replace('❌', '[FAIL]')
        content = content.replace('⚠️', '[WARNING]')
        content = content.replace('🎯', '[EXCELLENT]')
        content = content.replace('🚀', '[WORKING]')
        
        # Write back with fixed encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed unicode characters in {file_path}")
        return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix unicode characters in all backend core files"""
    print("Fixing unicode characters in backend core files...")
    
    backend_core_path = os.path.join(os.path.dirname(__file__), 'backend', 'core')
    
    fixed_files = 0
    total_files = 0
    
    for root, dirs, files in os.walk(backend_core_path):
        for file in files:
            if file.endswith('.py'):
                total_files += 1
                file_path = os.path.join(root, file)
                if fix_unicode_in_file(file_path):
                    fixed_files += 1
    
    print(f"Fixed unicode characters in {fixed_files}/{total_files} files")
    
    if fixed_files > 0:
        print("\nUnicode characters fixed successfully!")
        print("All optimization components should now import without encoding issues.")
    else:
        print("\nNo unicode characters found or all issues resolved.")

if __name__ == "__main__":
    main()
