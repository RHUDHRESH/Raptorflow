#!/usr/bin/env python3
"""
Check Real Sentry DSN
======================

Check the actual Sentry DSN from the .env file.
"""

import os
from pathlib import Path

def check_env_file():
    """Check the actual .env file content."""
    print("Checking actual .env file...")
    print("=" * 50)
    
    env_path = Path(__file__).parent.parent / ".env"
    
    if not env_path.exists():
        print("ERROR: .env file not found")
        return False
    
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    sentry_lines = []
    for line in lines:
        if 'SENTRY_DSN=' in line:
            sentry_lines.append(line.strip())
    
    if not sentry_lines:
        print("ERROR: No SENTRY_DSN found in .env file")
        return False
    
    print("Found SENTRY_DSN entries:")
    for line in sentry_lines:
        print(f"  {line}")
    
    # Extract the DSN value
    for line in sentry_lines:
        if line.startswith('SENTRY_DSN='):
            dsn = line.split('=', 1)[1]
            print(f"\nExtracted DSN: {dsn}")
            
            # Parse the DSN
            from urllib.parse import urlparse
            parsed = urlparse(dsn)
            
            print(f"\nParsed DSN:")
            print(f"  Scheme: {parsed.scheme}")
            print(f"  Username: {parsed.username[:8]}..." if parsed.username else "  Username: None")
            print(f"  Host: {parsed.hostname}")
            print(f"  Path: {parsed.path}")
            
            if parsed.hostname and '.' in parsed.hostname:
                org_id = parsed.hostname.split('.')[0]
                print(f"  Organization ID: {org_id}")
            
            if parsed.path and parsed.path != '/':
                project_id = parsed.path.lstrip('/')
                print(f"  Project ID: {project_id}")
            
            # Check if it's a real DSN
            if 'YOUR_' in dsn or 'placeholder' in dsn.lower():
                print(f"\nERROR: This is still a placeholder DSN!")
                print("Please replace it with your real Sentry DSN")
                return False
            else:
                print(f"\nSUCCESS: This looks like a real Sentry DSN!")
                return True
    
    return False

if __name__ == "__main__":
    success = check_env_file()
    
    if not success:
        print("\nPlease update your .env file with your real Sentry DSN")
        print("Get your DSN from: https://sentry.io -> Your Project -> Settings -> Client Keys (DSN)")
    else:
        print("\nGreat! Your Sentry DSN looks real and ready to use!")
