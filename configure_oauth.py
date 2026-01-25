#!/usr/bin/env python3
"""
Configure Google OAuth for Supabase
"""

import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()


def configure_google_oauth():
    """Configure Google OAuth in Supabase"""

    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not all([supabase_url, service_key, google_client_id, google_client_secret]):
        print("❌ Missing required environment variables")
        return False

    # Update OAuth config via Supabase REST API
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }

    # Enable Google OAuth provider
    oauth_config = {
        "external": {
            "google": {
                "enabled": True,
                "client_id": google_client_id,
                "client_secret": google_client_secret,
                "redirect_uri": f"http://localhost:3000/auth/callback",
            }
        }
    }

    try:
        # Try to update the auth configuration
        response = requests.patch(
            f"{supabase_url}/rest/v1/config", headers=headers, json=oauth_config
        )

        if response.status_code == 200:
            print("✅ Google OAuth configured successfully")
            return True
        else:
            print(f"❌ Failed to configure OAuth: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error configuring OAuth: {str(e)}")
        return False


def test_oauth_connection():
    """Test if OAuth is properly configured"""

    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")

    headers = {"apikey": anon_key, "Content-Type": "application/json"}

    try:
        # Get OAuth configuration
        response = requests.get(f"{supabase_url}/auth/v1/settings", headers=headers)

        if response.status_code == 200:
            settings = response.json()
            print("✅ OAuth settings retrieved")
            print(f"External providers: {settings.get('external', {})}")
            return True
        else:
            print(f"❌ Failed to get OAuth settings: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error getting OAuth settings: {str(e)}")
        return False


if __name__ == "__main__":
    print("🔧 Configuring Google OAuth for Supabase...")

    # Test current settings
    test_oauth_connection()

    # Configure OAuth
    configure_google_oauth()

    # Test again
    test_oauth_connection()
