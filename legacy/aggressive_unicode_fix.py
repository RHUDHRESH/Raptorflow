#!/usr/bin/env python3
"""
Aggressive unicode character finder and fixer
"""

import os
import re
import sys

def find_problematic_chars(file_path):
    """Find any non-ASCII characters in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find any character outside ASCII range
        non_ascii = re.findall(r'[^\x00-\x7F]', content)
        if non_ascii:
            unique_chars = set(non_ascii)
            print(f"File: {file_path}")
            print(f"Non-ASCII characters found: {len(unique_chars)} unique")
            for char in sorted(unique_chars):
                print(f"  '{char}' (U+{ord(char):04X})")
            return True
        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def aggressive_unicode_fix(file_path):
    """Aggressively replace all non-ASCII characters"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace ALL non-ASCII characters with ASCII equivalents
        # Common replacements
        replacements = {
            '''': "'",
            ''': "'",
            '"': '"',
            '"': '"',
            '–': '-',
            '—': '--',
            '…': '...',
            '•': '*',
            '©': '(c)',
            '®': '(r)',
            '™': '(tm)',
            '°': ' degrees ',
            '±': '+/-',
            '×': 'x',
            '÷': '/',
            '≤': '<=',
            '≥': '>=',
            '≠': '!=',
            '∞': 'inf',
            '∑': 'sum',
            '∏': 'prod',
            '∫': 'int',
            '√': 'sqrt',
            '∂': 'partial',
            '∇': 'grad',
            '∈': 'in',
            '∉': 'not in',
            '⊂': 'subset',
            '⊃': 'superset',
            '∪': 'union',
            '∩': 'intersection',
            '∅': 'empty',
            '∀': 'forall',
            '∃': 'exists',
            '¬': 'not',
            '∧': 'and',
            '∨': 'or',
            '→': '->',
            '←': '<-',
            '↑': 'up',
            '↓': 'down',
            '⇒': '=>',
            '⇐': '<=',
            '⇑': '=>',
            '⇓': '<=',
        }
        
        # Apply replacements
        for unicode_char, ascii_replace in replacements.items():
            content = content.replace(unicode_char, ascii_replace)
        
        # Replace any remaining non-ASCII with generic ASCII
        content = re.sub(r'[^\x00-\x7F]', '?', content)
        
        # Only write if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed non-ASCII characters in {file_path}")
            return True
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Find and fix all non-ASCII characters in backend core"""
    print("Aggressively finding and fixing non-ASCII characters...")
    
    backend_core_path = os.path.join(os.path.dirname(__file__), 'backend', 'core')
    
    problematic_files = []
    fixed_files = 0
    total_files = 0
    
    # First pass: find problematic files
    for root, dirs, files in os.walk(backend_core_path):
        for file in files:
            if file.endswith('.py'):
                total_files += 1
                file_path = os.path.join(root, file)
                if find_problematic_chars(file_path):
                    problematic_files.append(file_path)
    
    print(f"\nFound {len(problematic_files)} files with non-ASCII characters out of {total_files} total files")
    
    # Second pass: fix them
    for file_path in problematic_files:
        if aggressive_unicode_fix(file_path):
            fixed_files += 1
    
    print(f"\nFixed non-ASCII characters in {fixed_files} files")
    
    if fixed_files > 0:
        print("\nAggressive unicode fix completed!")
        print("All non-ASCII characters have been replaced with ASCII equivalents.")
    else:
        print("\nNo non-ASCII characters found or all issues resolved.")

if __name__ == "__main__":
    main()
