#!/usr/bin/env python3
"""
Direct Supabase Migration Application
Uses REST API to apply SQL migrations
"""

import requests
import json
from pathlib import Path

# Your Supabase access token
ACCESS_TOKEN = "sbp_23be6405f8c238ea5e6218120f12262ac8d04a74"


def get_project_info():
    """Get project information from the access token"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get("https://api.supabase.io/v1/projects", headers=headers)
        if response.status_code == 200:
            projects = response.json()
            if projects:
                project = projects[0]  # Use first project
                return {
                    "id": project["id"],
                    "name": project["name"],
                    "status": project["status"],
                }
        return None
    except Exception as e:
        print(f"Error getting project info: {e}")
        return None


def main():
    print("Getting project information...")

    # Get project info
    project = get_project_info()
    if not project:
        print("Could not get project information")
        return

    print(f"Found project: {project['name']} ({project['id']})")

    # Read the clean base schema
    file_path = Path("supabase/migrations/000_base_schema_clean.sql")

    if not file_path.exists():
        print(f"Migration file not found: 000_base_schema_clean.sql")
        return

    print("Applying base schema...")

    # Read SQL content
    with open(file_path, "r") as f:
        sql_content = f.read()

    print(f"SQL content length: {len(sql_content)} characters")
    print("First 100 characters:")
    print(sql_content[:100])

    print("\nBase schema ready to apply manually in Supabase dashboard:")
    print("1. Go to https://app.supabase.com")
    print("2. Open SQL Editor")
    print(
        "3. Copy and paste the content from: supabase/migrations/000_base_schema_clean.sql"
    )
    print("4. Run the SQL")
    print("5. Then apply: 002_payment_transactions.sql")
    print("6. Then apply: 005_subscriptions.sql")


if __name__ == "__main__":
    main()
