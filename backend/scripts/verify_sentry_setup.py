#!/usr/bin/env python3
"""
Verify Sentry Setup
==================

Verify Sentry connection and show how to get API access.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_sentry_sdk():
    """Verify Sentry SDK connection."""
    print("Verifying Sentry SDK Connection...")
    print("=" * 50)
    
    dsn = os.getenv('SENTRY_DSN')
    if not dsn:
        print("ERROR: SENTRY_DSN not found")
        return False
    
    try:
        import sentry_sdk
        
        # Initialize Sentry
        sentry_sdk.init(
            dsn=dsn,
            environment=os.getenv('SENTRY_ENVIRONMENT', 'development'),
            traces_sample_rate=1.0,
            debug=True
        )
        
        print("SUCCESS: Sentry SDK initialized!")
        
        # Send test events
        sentry_sdk.capture_message("Test message from Raptorflow Backend - SDK Verification", level="info")
        print("SUCCESS: Test message sent!")
        
        try:
            raise ValueError("Test error from Raptorflow Backend - SDK Verification")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print("SUCCESS: Test error sent!")
        
        # Flush events
        sentry_sdk.flush()
        print("SUCCESS: Events flushed to Sentry!")
        
        return True
        
    except ImportError:
        print("ERROR: sentry-sdk not installed")
        return False
    except Exception as e:
        print(f"ERROR: Failed to initialize Sentry: {e}")
        return False

def show_sentry_dashboard_info():
    """Show how to access Sentry dashboard."""
    dsn = os.getenv('SENTRY_DSN')
    if not dsn:
        return
    
    from urllib.parse import urlparse
    parsed = urlparse(dsn)
    
    org_id = parsed.hostname.split('.')[0] if parsed.hostname else None
    project_id = parsed.path.lstrip('/') if parsed.path else None
    
    print("\nSentry Dashboard Access:")
    print("=" * 40)
    print(f"1. Go to: https://sentry.io")
    print(f"2. Login to your account")
    print(f"3. Navigate to your organization")
    print(f"4. Select your project")
    print(f"5. Check for recent events")
    print(f"\nDirect Project URL: https://sentry.io/issues/?project={project_id}")
    print(f"Organization ID: {org_id}")
    print(f"Project ID: {project_id}")

def show_api_access_instructions():
    """Show how to get API access."""
    print("\nHow to Get Sentry API Access:")
    print("=" * 50)
    print("1. Go to: https://sentry.io")
    print("2. Click on your profile (top right)")
    print("3. Go to 'User Settings'")
    print("4. Click on 'API Tokens' in the left sidebar")
    print("5. Click 'Create New Token'")
    print("6. Give it a name (e.g., 'Raptorflow API')")
    print("7. Select permissions:")
    print("   - Organization: read")
    print("   - Project: read")
    print("   - Releases: read")
    print("   - Issues: read")
    print("8. Copy the token")
    print("9. Add it to your .env file as:")
    print("   SENTRY_API_TOKEN=your_new_token_here")
    print("\nNote: The token should start with 'sntrys_' followed by hex characters")

def create_simple_test():
    """Create a simple test to verify monitoring works."""
    print("\nCreating Simple Test...")
    print("=" * 40)
    
    try:
        import sentry_sdk
        
        # Re-initialize with debug mode
        sentry_sdk.init(
            dsn=os.getenv('SENTRY_DSN'),
            environment='test',
            debug=True,
            traces_sample_rate=1.0
        )
        
        # Create a transaction
        with sentry_sdk.start_transaction(name="test_transaction", op="test"):
            # Add some spans
            with sentry_sdk.start_span(op="function", description="test_function"):
                pass
            
            with sentry_sdk.start_span(op="database", description="test_query"):
                pass
        
        # Send a message
        sentry_sdk.capture_message("This is a test message from Raptorflow - you should see this in Sentry!", level="info")
        
        # Send an error
        try:
            raise RuntimeError("This is a test error from Raptorflow - you should see this in Sentry!")
        except Exception:
            sentry_sdk.capture_exception()
        
        # Flush
        sentry_sdk.flush()
        
        print("SUCCESS: Test events sent to Sentry!")
        print("Check your Sentry dashboard for these events:")
        print("- 'This is a test message from Raptorflow'")
        print("- 'RuntimeError: This is a test error from Raptorflow'")
        print("- Transaction: 'test_transaction'")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create test: {e}")
        return False

if __name__ == "__main__":
    print("Raptorflow Sentry Setup Verification")
    print("=" * 60)
    
    # Verify SDK connection
    sdk_success = verify_sentry_sdk()
    
    # Show dashboard info
    show_sentry_dashboard_info()
    
    # Show API access instructions
    show_api_access_instructions()
    
    # Create test
    test_success = create_simple_test()
    
    if sdk_success and test_success:
        print("\n" + "=" * 60)
        print("SUCCESS: Sentry monitoring is working!")
        print("Your comprehensive monitoring system is ready to use!")
        print("\nWhat you should see in Sentry:")
        print("1. Test messages and errors")
        print("2. Performance traces")
        print("3. Real-time monitoring data")
        print("\nNext steps:")
        print("1. Start your Raptorflow backend")
        print("2. Monitor your Sentry dashboard")
        print("3. Set up alerts and notifications")
        print("4. Configure custom dashboards")
    else:
        print("\nFAILED: Sentry setup verification failed")
        print("Please check the error messages above")
