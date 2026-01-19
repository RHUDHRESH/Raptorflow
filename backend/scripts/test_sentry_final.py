#!/usr/bin/env python3
"""
Final Sentry Test
================

Test Sentry connection without unicode characters.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sentry_direct():
    """Test Sentry directly with the SDK."""
    print("Testing Sentry Direct Connection...")
    print("=" * 50)
    
    # Get DSN
    dsn = os.getenv('SENTRY_DSN')
    if not dsn:
        print("ERROR: SENTRY_DSN not found")
        return False
    
    print(f"Using DSN: {dsn[:50]}...")
    
    # Try to import and initialize Sentry
    try:
        import sentry_sdk
        
        # Initialize Sentry
        sentry_sdk.init(
            dsn=dsn,
            environment=os.getenv('SENTRY_ENVIRONMENT', 'development'),
            traces_sample_rate=1.0,
            debug=True
        )
        
        print("SUCCESS: Sentry initialized!")
        
        # Test message
        sentry_sdk.capture_message("Test message from Raptorflow Backend", level="info")
        print("SUCCESS: Test message sent!")
        
        # Test error
        try:
            raise ValueError("Test error from Raptorflow Backend")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print("SUCCESS: Test error sent!")
        
        # Flush events
        sentry_sdk.flush()
        print("SUCCESS: Events flushed to Sentry!")
        
        return True
        
    except ImportError:
        print("ERROR: sentry-sdk not installed")
        print("Install with: pip install sentry-sdk")
        return False
    except Exception as e:
        print(f"ERROR: Failed to initialize Sentry: {e}")
        return False

def show_sentry_info():
    """Show Sentry connection info."""
    dsn = os.getenv('SENTRY_DSN')
    if not dsn:
        return
    
    from urllib.parse import urlparse
    parsed = urlparse(dsn)
    
    print("\nSentry Connection Info:")
    print("=" * 30)
    print(f"Organization: {parsed.hostname.split('.')[0] if parsed.hostname else 'Unknown'}")
    print(f"Project ID: {parsed.path.lstrip('/') if parsed.path else 'Unknown'}")
    print(f"Environment: {os.getenv('SENTRY_ENVIRONMENT', 'development')}")
    
    print(f"\nCheck your Sentry dashboard:")
    print(f"https://sentry.io")
    print(f"You should see the test events there!")

if __name__ == "__main__":
    success = test_sentry_direct()
    
    if success:
        show_sentry_info()
        print("\nSUCCESS: Sentry integration is working!")
        print("Your comprehensive monitoring system is ready to use!")
    else:
        print("\nFAILED: Sentry integration test failed")
        print("Please check the error messages above")
