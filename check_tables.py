#!/usr/bin/env python3
"""
Check what tables exist in Supabase
"""

import requests
import json

# Your Supabase access token
ACCESS_TOKEN = "sbp_23be6405f8c238ea5e6218120f12262ac8d04a74"
PROJECT_ID = "vpwwzsanuyhpkvgorcnc"


def check_tables():
    """Check what tables exist"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "apikey": ACCESS_TOKEN,
    }

    # Get project info to get REST URL
    try:
        response = requests.get(
            f"https://api.supabase.io/v1/projects/{PROJECT_ID}", headers=headers
        )
        if response.status_code == 200:
            project_data = response.json()
            rest_url = project_data["restUrl"]

            # Query information_schema to see what tables exist
            sql = """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name IN ('users', 'workspaces', 'workspace_members', 'payment_transactions')
            ORDER BY table_name, ordinal_position;
            """

            sql_endpoint = f"{rest_url}/rest/v1/rpc/execute_sql"
            payload = {"sql": sql}

            response = requests.post(sql_endpoint, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                print("Current database schema:")
                print("=" * 50)
                if result:
                    for row in result:
                        print(
                            f"Table: {row['table_name']}, Column: {row['column_name']}, Type: {row['data_type']}"
                        )
                else:
                    print("No tables found or query failed")
            else:
                print(f"Query failed: {response.status_code}")
                print(response.text)

        else:
            print(f"Failed to get project info: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_tables()
