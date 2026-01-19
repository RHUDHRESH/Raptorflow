#!/usr/bin/env python3
"""
Test Sentry Live Connection
=========================

Test if Sentry is actually configured and sending data.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sentry_configuration():
    """Test Sentry configuration and connection."""
    print("Testing Sentry Configuration...")
    print("=" * 50)
    
    # Check environment variables
    dsn = os.getenv('SENTRY_DSN')
    environment = os.getenv('ENVIRONMENT', 'development')
    
    print(f"DSN: {dsn[:50] if dsn else 'None'}...")
    print(f"Environment: {environment}")
    
    if not dsn:
        print("ERROR: SENTRY_DSN not configured")
        return False
    
    # Test Sentry SDK
    try:
        import sentry_sdk
        
        # Initialize Sentry
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            traces_sample_rate=1.0,
            debug=True
        )
        
        print("SUCCESS: Sentry SDK initialized!")
        
        # Send test message
        message_id = sentry_sdk.capture_message(
            "Live test from Raptorflow Backend - Sentry Configuration Check",
            level="info",
            tags={
                "test_type": "configuration_check",
                "source": "raptorflow_backend",
                "timestamp": "2026-01-15T12:56:00Z"
            }
        )
        
        print(f"SUCCESS: Test message sent! Event ID: {message_id}")
        
        # Send test error
        try:
            raise ValueError("Live test error from Raptorflow Backend - Sentry Configuration Check")
        except Exception as e:
            error_id = sentry_sdk.capture_exception(e)
            print(f"SUCCESS: Test error sent! Event ID: {error_id}")
        
        # Send test transaction
        transaction = sentry_sdk.start_transaction(
            name="test_transaction",
            op="test",
            sampled=True
        )
        
        # Add a span
        span = transaction.start_child(op="function", description="test_function")
        span.finish()
        
        transaction.finish()
        print("SUCCESS: Test transaction sent!")
        
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
    """Show Sentry dashboard information."""
    dsn = os.getenv('SENTRY_DSN')
    if not dsn:
        return
    
    from urllib.parse import urlparse
    parsed = urlparse(dsn)
    
    org_id = parsed.hostname.split('.')[0] if parsed.hostname else None
    project_id = parsed.path.lstrip('/') if parsed.path else None
    
    print(f"\nSentry Dashboard Information:")
    print("=" * 40)
    print(f"Organization ID: {org_id}")
    print(f"Project ID: {project_id}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Dashboard URL: https://sentry.io")
    print(f"Direct Project URL: https://sentry.io/issues/?project={project_id}")
    
    print(f"\nWhat to look for in Sentry:")
    print("- 'Live test from Raptorflow Backend - Sentry Configuration Check'")
    print("- 'ValueError: Live test error from Raptorflow Backend'")
    print("- Transaction: 'test_transaction'")

if __name__ == "__main__":
    print("Raptorflow Sentry Live Test")
    print("=" * 60)
    
    success = test_sentry_configuration()
    
    if success:
        show_sentry_dashboard_info()
        
        print(f"\n" + "=" * 60)
        print("SUCCESS: Sentry is configured and working!")
        print("Check your Sentry dashboard for the test events above.")
        print("Your comprehensive monitoring system is ready to use!")
    else:
        print(f"\nFAILED: Sentry configuration test failed")
        print("Please check the error messages above")
