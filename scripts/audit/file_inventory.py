#!/usr/bin/env python3
"""
STEP 1: FILE INVENTORY GENERATOR
Generates a complete inventory of all Python files with size and line counts.
"""

import os
import csv
from pathlib import Path


def get_file_inventory(directory: str, output_path: str):
    """Generate inventory of all Python files."""
    inventory = []
    directory_path = Path(directory)
    
    for py_file in sorted(directory_path.rglob('*.py')):
        try:
            stat = py_file.stat()
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                line_count = len(lines)
            
            rel_path = str(py_file.relative_to(directory_path.parent))
            size_bytes = stat.st_size
            
            inventory.append({
                'relative_path': rel_path,
                'absolute_path': str(py_file),
                'size_bytes': size_bytes,
                'line_count': line_count,
                'extension': '.py'
            })
        except Exception as e:
            print(f"Warning: Could not process {py_file}: {e}")
    
    # Save to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['relative_path', 'absolute_path', 'size_bytes', 'line_count', 'extension'])
        writer.writeheader()
        writer.writerows(inventory)
    
    print(f"File inventory saved to {output_path}")
    print(f"Total files: {len(inventory)}")
    print(f"Total lines: {sum(item['line_count'] for item in inventory)}")
    
    return inventory


if __name__ == '__main__':
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else 'backend'
    output = sys.argv[2] if len(sys.argv) > 2 else 'docs/file_inventory.csv'
    get_file_inventory(directory, output)
"""
STEP 1: FILE INVENTORY GENERATOR
Generates a complete inventory of all Python files with size and line counts.
"""

import os
import csv
from pathlib import Path


def get_file_inventory(directory: str, output_path: str):
    """Generate inventory of all Python files."""
    inventory = []
    directory_path = Path(directory)
    
    for py_file in sorted(directory_path.rglob('*.py')):
        try:
            stat = py_file.stat()
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                line_count = len(lines)
            
            rel_path = str(py_file.relative_to(directory_path.parent))
            size_bytes = stat.st_size
            
            inventory.append({
                'relative_path': rel_path,
                'absolute_path': str(py_file),
                'size_bytes': size_bytes,
                'line_count': line_count,
                'extension': '.py'
            })
        except Exception as e:
            print(f"Warning: Could not process {py_file}: {e}")
    
    # Save to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['relative_path', 'absolute_path', 'size_bytes', 'line_count', 'extension'])
        writer.writeheader()
        writer.writerows(inventory)
    
    print(f"File inventory saved to {output_path}")
    print(f"Total files: {len(inventory)}")
    print(f"Total lines: {sum(item['line_count'] for item in inventory)}")
    
    return inventory


if __name__ == '__main__':
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else 'backend'
    output = sys.argv[2] if len(sys.argv) > 2 else 'docs/file_inventory.csv'
    get_file_inventory(directory, output)

