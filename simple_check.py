#!/usr/bin/env python3
"""
Simple check of what's in the database
"""

import requests

ACCESS_TOKEN = "sbp_23be6405f8c238ea5e6218120f12262ac8d04a74"
PROJECT_ID = "vpwwzsanuyhpkvgorcnc"


def main():
    print("Checking database tables...")

    # Try to query the workspaces table directly
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "apikey": ACCESS_TOKEN,
    }

    # Direct REST API call to see if workspaces table exists
    url = f"https://{PROJECT_ID}.supabase.co/rest/v1/workspaces?select=id&limit=1"

    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")

        if response.status_code == 200:
            print("Workspaces table exists and is accessible")
        elif response.status_code == 404:
            print("Workspaces table does NOT exist")
        elif response.status_code == 400:
            print("Bad request - table might not exist or permissions issue")
        else:
            print(f"Unexpected status: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
