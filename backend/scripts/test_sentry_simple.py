#!/usr/bin/env python3
"""
Simple Sentry Connection Test
============================

Tests Sentry connection without unicode characters.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

def test_sentry_connection():
    """Test Sentry connection and diagnose issues."""
    print("Testing Sentry Connection...")
    print("=" * 50)
    
    # Check environment variable
    dsn = os.getenv('SENTRY_DSN')
    if not dsn:
        print("ERROR: SENTRY_DSN environment variable not found")
        print("Please set SENTRY_DSN in your .env file")
        return False
    
    print(f"DSN found: {dsn[:50]}...")
    
    # Parse DSN components
    try:
        from urllib.parse import urlparse
        parsed = urlparse(dsn)
        
        org_part = parsed.netloc.split('.')[0] if '.' in parsed.netloc else 'Unknown'
        print(f"Organization: {org_part}")
        print(f"Public Key: {parsed.username[:8]}..." if parsed.username else "ERROR: No public key")
        print(f"Project ID: {parsed.path.lstrip('/')}" if parsed.path else "ERROR: No project ID")
        
        # Check DSN format
        if not all([parsed.scheme, parsed.netloc, parsed.path]):
            print("ERROR: Invalid DSN format")
            return False
            
        if parsed.scheme != 'https':
            print("WARNING: Using HTTP instead of HTTPS")
        
    except Exception as e:
        print(f"ERROR: Failed to parse DSN: {e}")
        return False
    
    # Try to initialize Sentry
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from core.sentry_integration import get_sentry_manager
        
        manager = get_sentry_manager()
        health = manager.get_health_status()
        
        print(f"Sentry Manager Status: {'Healthy' if health.is_healthy else 'Unhealthy'}")
        print(f"Configured: {'Yes' if health.is_configured else 'No'}")
        print(f"Enabled: {'Yes' if health.is_enabled else 'No'}")
        
        if health.configuration_issues:
            print("Configuration Issues:")
            for issue in health.configuration_issues:
                print(f"   - {issue}")
        
        # Get DSN info
        dsn_info = manager.get_dsn_info()
        if 'error' not in dsn_info:
            print("SUCCESS: DSN is valid and properly formatted")
            print(f"Host: {dsn_info.get('host', 'Unknown')}")
            print(f"Project: {dsn_info.get('project_id', 'Unknown')}")
        else:
            print(f"ERROR: DSN Error: {dsn_info['error']}")
            return False
        
    except Exception as e:
        print(f"ERROR: Failed to initialize Sentry: {e}")
        return False
    
    # Test event sending
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from core.sentry_error_tracking import get_error_tracker
        
        tracker = get_error_tracker()
        
        # Send a test message
        message_id = tracker.track_message("Sentry connection test", level="info")
        
        if message_id:
            print(f"SUCCESS: Test message sent (ID: {message_id})")
        else:
            print("WARNING: Test message sent but no event ID returned")
        
        # Send a test error
        try:
            raise ValueError("Test error for Sentry connection validation")
        except Exception as e:
            error_id = tracker.track_exception(e)
            
            if error_id:
                print(f"SUCCESS: Test error sent (ID: {error_id})")
            else:
                print("WARNING: Test error sent but no event ID returned")
        
    except Exception as e:
        print(f"ERROR: Failed to send test events: {e}")
        return False
    
    print("\nSentry connection test completed!")
    print("Next Steps:")
    print("1. Check your Sentry dashboard for the test events")
    print("2. If you see events, your integration is working")
    print("3. If you don't see events, check your organization/project setup")
    
    return True

def show_sentry_setup_guide():
    """Show Sentry setup guide."""
    print("\nSentry Setup Guide")
    print("=" * 50)
    print("1. Go to https://sentry.io")
    print("2. Sign up or log in")
    print("3. Create a new organization (or use existing)")
    print("4. Create a new project:")
    print("   - Platform: Python")
    print("   - Framework: FastAPI (if available)")
    print("5. Copy the DSN from project settings")
    print("6. Update your .env file:")
    print("   SENTRY_DSN=https://YOUR_PUBLIC_KEY@YOUR_ORG.ingest.sentry.io/YOUR_PROJECT_ID")
    print("7. Run this test script again")
    print("\nUseful Links:")
    print("- Sentry Dashboard: https://sentry.io")
    print("- Python SDK Docs: https://docs.sentry.io/platforms/python/")
    print("- FastAPI Integration: https://docs.sentry.io/platforms/python/integrations/fastapi/")

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("WARNING: python-dotenv not installed, environment variables may not be loaded")
    
    success = test_sentry_connection()
    
    if not success:
        show_sentry_setup_guide()
        sys.exit(1)
    
    print("\nSUCCESS: All tests passed! Your Sentry integration is working.")
