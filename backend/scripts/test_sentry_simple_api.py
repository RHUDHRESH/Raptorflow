#!/usr/bin/env python3
"""
Simple Sentry API Test
=====================

Test Sentry API with different approaches.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sentry_with_dsn():
    """Test Sentry connection using DSN directly."""
    print("Testing Sentry with DSN...")
    print("=" * 40)
    
    dsn = os.getenv('SENTRY_DSN')
    if not dsn:
        print("ERROR: SENTRY_DSN not found")
        return False
    
    print(f"DSN: {dsn[:50]}...")
    
    # Parse DSN to get org and project info
    from urllib.parse import urlparse
    parsed = urlparse(dsn)
    
    print(f"Host: {parsed.hostname}")
    print(f"Username: {parsed.username}")
    print(f"Path: {parsed.path}")
    
    # Extract org and project
    if parsed.hostname and parsed.path:
        org_id = parsed.hostname.split('.')[0] if '.' in parsed.hostname else parsed.hostname
        project_id = parsed.path.lstrip('/')
        
        print(f"Organization ID: {org_id}")
        print(f"Project ID: {project_id}")
        
        # Test by sending a simple event to the ingest endpoint
        print(f"\nTesting ingest endpoint...")
        
        # Create a simple event payload
        event = {
            "event_id": "test-event-123",
            "timestamp": "2026-01-15T11:39:00Z",
            "platform": "python",
            "level": "info",
            "message": "Test message from Raptorflow",
            "environment": os.getenv('SENTRY_ENVIRONMENT', 'development'),
            "sdk": {
                "name": "sentry.python",
                "version": "2.49.0"
            },
            "tags": {
                "test": "true",
                "source": "raptorflow"
            }
        }
        
        # Send to ingest endpoint
        ingest_url = f"https://{parsed.hostname}{parsed.path}/api/envelope/"
        headers = {
            'Content-Type': 'application/json',
            'X-Sentry-Auth': f'Sentry sentry_version=7, sentry_client=sentry.python/2.49.0, sentry_key={parsed.username}'
        }
        
        try:
            response = requests.post(ingest_url, json={"event": event}, headers=headers, timeout=10)
            
            print(f"Response status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code in [200, 201, 202]:
                print("SUCCESS: Event sent to Sentry!")
                return True
            else:
                print("ERROR: Failed to send event")
                return False
                
        except Exception as e:
            print(f"ERROR: Failed to send event: {e}")
            return False
    
    return False

def test_sentry_webhook():
    """Test Sentry webhook connection."""
    print("\nTesting Sentry Webhook...")
    print("=" * 40)
    
    # Try to access Sentry web API with different approaches
    auth_token = os.getenv('SENTRY_AUTH_TOKEN')
    if not auth_token:
        print("ERROR: SENTRY_AUTH_TOKEN not found")
        return False
    
    print(f"Auth token: {auth_token[:20]}...")
    
    # Try different API endpoints
    endpoints = [
        "https://sentry.io/api/0/",
        "https://sentry.io/api/0/projects/",
        "https://api.sentry.io/api/0/",
        "https://app.sentry.io/api/0/"
    ]
    
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    
    for endpoint in endpoints:
        try:
            print(f"\nTrying endpoint: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("SUCCESS: Found working endpoint!")
                return True
            elif response.status_code == 401:
                print("ERROR: Invalid auth token")
                return False
            else:
                print(f"Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"ERROR: Failed to connect: {e}")
    
    return False

def show_sentry_info():
    """Show Sentry connection information."""
    print("\nSentry Connection Information:")
    print("=" * 40)
    
    dsn = os.getenv('SENTRY_DSN')
    auth_token = os.getenv('SENTRY_AUTH_TOKEN')
    
    if dsn:
        from urllib.parse import urlparse
        parsed = urlparse(dsn)
        
        print(f"DSN Host: {parsed.hostname}")
        print(f"Organization: {parsed.hostname.split('.')[0] if '.' in parsed.hostname else 'Unknown'}")
        print(f"Project: {parsed.path.lstrip('/') if parsed.path else 'Unknown'}")
        print(f"Environment: {os.getenv('SENTRY_ENVIRONMENT', 'development')}")
    
    if auth_token:
        print(f"Auth Token: {auth_token[:20]}...")
    
    print(f"\nDashboard: https://sentry.io")
    print(f"Direct Project: https://sentry.io/issues/?project={parsed.path.lstrip('/') if dsn and parsed.path else 'unknown'}")

if __name__ == "__main__":
    print("Sentry Connection Test")
    print("=" * 50)
    
    # Test with DSN
    dsn_success = test_sentry_with_dsn()
    
    # Test with webhook
    webhook_success = test_sentry_webhook()
    
    # Show info
    show_sentry_info()
    
    if dsn_success or webhook_success:
        print(f"\nSUCCESS: Sentry connection is working!")
        print("Your comprehensive monitoring system is ready to use!")
        print("\nNext steps:")
        print("1. Start your Raptorflow backend")
        print("2. Monitor your Sentry dashboard")
        print("3. Check for real-time errors and performance data")
    else:
        print(f"\nFAILED: Sentry connection test failed")
        print("Please check:")
        print("1. Your DSN is correct")
        print("2. Your auth token is valid")
        print("3. Your organization and project exist")
