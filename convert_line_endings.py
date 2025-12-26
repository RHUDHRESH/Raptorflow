#!/usr/bin/env python3
"""
Line ending converter for Windows/Unix compatibility.
Usage: python convert_line_endings.py <file_path> [to_unix|to_dos]
"""

import sys
import os
from pathlib import Path

def convert_line_endings(file_path, to_unix=True):
    """Convert line endings in a file."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        if to_unix:
            # Convert Windows CRLF to Unix LF
            converted = content.replace(b'\r\n', b'\n')
            print(f"Converted {file_path} to Unix (LF) format")
        else:
            # Convert Unix LF to Windows CRLF
            converted = content.replace(b'\n', b'\r\n')
            print(f"Converted {file_path} to DOS (CRLF) format")
        
        with open(file_path, 'wb') as f:
            f.write(converted)
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_line_endings.py <file_path> [to_unix|to_dos]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    conversion_type = sys.argv[2] if len(sys.argv) > 2 else "to_unix"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    to_unix = conversion_type != "to_dos"
    success = convert_line_endings(file_path, to_unix)
    
    sys.exit(0 if success else 1)
