#!/usr/bin/env python3
"""
Direct Supabase Migration Application
Uses REST API to apply SQL migrations
"""

import os
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


def apply_sql_to_supabase(project_id, sql_content):
    """Apply SQL to Supabase project"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "apikey": ACCESS_TOKEN,
    }

    # Get project details to get the REST URL
    project_url = f"https://api.supabase.io/v1/projects/{project_id}"

    try:
        response = requests.get(project_url, headers=headers)
        if response.status_code == 200:
            project_data = response.json()
            rest_url = project_data["restUrl"]

            # Apply SQL using the REST API
            sql_endpoint = f"{rest_url}/rest/v1/rpc/execute_sql"

            payload = {"sql": sql_content}

            response = requests.post(sql_endpoint, headers=headers, json=payload)
            return response.status_code == 200, response.text
        else:
            return False, f"Failed to get project info: {response.status_code}"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    print("🚀 Applying RaptorFlow Migrations...")

    # Get project info
    project = get_project_info()
    if not project:
        print("❌ Could not get project information")
        return

    print(f"✅ Found project: {project['name']} ({project['id']})")

    # Migration files in order
    migrations = [
        "000_base_schema_clean.sql",
        "001_auth_triggers.sql",
        "002_payment_transactions.sql",
        "005_subscriptions.sql",
    ]

    # Apply each migration
    for migration_file in migrations:
        file_path = Path(f"supabase/migrations/{migration_file}")

        if not file_path.exists():
            print(f"❌ Migration file not found: {migration_file}")
            continue

        print(f"\n📋 Applying: {migration_file}")

        # Read SQL content
        with open(file_path, "r") as f:
            sql_content = f.read()

        # Apply migration
        success, result = apply_sql_to_supabase(project["id"], sql_content)

        if success:
            print(f"✅ {migration_file} applied successfully")
        else:
            print(f"❌ {migration_file} failed: {result}")
            break

    print("\n🎉 Migration process completed!")


if __name__ == "__main__":
    main()
