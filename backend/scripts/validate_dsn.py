#!/usr/bin/env python3
"""
Simple DSN Validation Script
============================

Validates Sentry DSN format without importing custom modules.
"""

import os
import sys
from urllib.parse import urlparse

def validate_dsn():
    """Validate Sentry DSN format."""
    print("Validating Sentry DSN...")
    print("=" * 40)
    
    # Get DSN from environment
    dsn = os.getenv('SENTRY_DSN')
    if not dsn:
        print("ERROR: SENTRY_DSN not found in environment variables")
        print("Please set SENTRY_DSN in your .env file")
        return False
    
    print(f"DSN: {dsn}")
    
    # Parse DSN
    try:
        parsed = urlparse(dsn)
        
        print(f"\nDSN Components:")
        print(f"  Scheme: {parsed.scheme}")
        print(f"  Netloc: {parsed.netloc}")
        print(f"  Path: {parsed.path}")
        print(f"  Username: {parsed.username}")
        print(f"  Host: {parsed.hostname}")
        
        # Extract organization and project
        if parsed.hostname and '.' in parsed.hostname:
            org_id = parsed.hostname.split('.')[0]
            print(f"  Organization ID: {org_id}")
        
        if parsed.path and parsed.path != '/':
            project_id = parsed.path.lstrip('/')
            print(f"  Project ID: {project_id}")
        
        # Validation checks
        issues = []
        
        if parsed.scheme != 'https':
            issues.append("Should use HTTPS")
        
        if not parsed.username:
            issues.append("Missing public key")
        
        if not parsed.hostname:
            issues.append("Missing hostname")
        
        if not parsed.path or parsed.path == '/':
            issues.append("Missing project ID")
        
        if 'ingest.sentry.io' not in parsed.netloc:
            issues.append("Should point to ingest.sentry.io")
        
        if issues:
            print(f"\nValidation Issues:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print(f"\nSUCCESS: DSN format is valid!")
            return True
            
    except Exception as e:
        print(f"ERROR: Failed to parse DSN: {e}")
        return False

def show_dsn_example():
    """Show example of correct DSN format."""
    print("\nCorrect DSN Format:")
    print("=" * 40)
    print("https://PUBLIC_KEY@ORG_ID.ingest.sentry.io/PROJECT_ID")
    print()
    print("Example:")
    print("https://a1b2c3d4e5f6g7h8@1234567890abcdef.ingest.sentry.io/1234567")
    print()
    print("Where:")
    print("- PUBLIC_KEY: Your Sentry public key")
    print("- ORG_ID: Your Sentry organization ID") 
    print("- PROJECT_ID: Your Sentry project ID")

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Note: python-dotenv not installed")
    
    success = validate_dsn()
    
    if not success:
        show_dsn_example()
        sys.exit(1)
    
    print("\nDSN validation passed!")
    print("Next step: Update your .env with a real Sentry DSN from https://sentry.io")
