#!/usr/bin/env python3
"""
Sentry API Connection Check
===========================

Use Sentry API to verify organization and project setup.
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sentry_api():
    """Test Sentry API connection."""
    print("Testing Sentry API Connection...")
    print("=" * 50)
    
    # Get auth token
    auth_token = os.getenv('SENTRY_AUTH_TOKEN')
    if not auth_token:
        print("ERROR: SENTRY_AUTH_TOKEN not found")
        print("Please set SENTRY_AUTH_TOKEN in your .env file")
        return False
    
    print(f"Using auth token: {auth_token[:20]}...")
    
    # Get organization info from DSN
    dsn = os.getenv('SENTRY_DSN')
    if not dsn:
        print("ERROR: SENTRY_DSN not found")
        return False
    
    from urllib.parse import urlparse
    parsed = urlparse(dsn)
    org_id = parsed.hostname.split('.')[0] if parsed.hostname else None
    
    if not org_id:
        print("ERROR: Could not extract organization ID from DSN")
        return False
    
    print(f"Organization ID: {org_id}")
    
    # Test API calls
    try:
        # 1. Get organization info
        org_url = f"https://sentry.io/api/0/organizations/{org_id}/"
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
        
        print(f"\n1. Testing organization API...")
        response = requests.get(org_url, headers=headers)
        
        if response.status_code == 200:
            org_data = response.json()
            print(f"SUCCESS: Organization found!")
            print(f"  Name: {org_data.get('name', 'Unknown')}")
            print(f"  Slug: {org_data.get('slug', 'Unknown')}")
            print(f"  Status: {org_data.get('status', 'Unknown')}")
        else:
            print(f"ERROR: Organization API failed ({response.status_code})")
            print(f"Response: {response.text}")
            return False
        
        # 2. Get projects
        projects_url = f"https://sentry.io/api/0/organizations/{org_id}/projects/"
        
        print(f"\n2. Testing projects API...")
        response = requests.get(projects_url, headers=headers)
        
        if response.status_code == 200:
            projects = response.json()
            print(f"SUCCESS: Found {len(projects)} projects")
            
            for project in projects:
                project_id = project.get('id')
                project_name = project.get('name', 'Unknown')
                project_slug = project.get('slug', 'Unknown')
                print(f"  - {project_name} (ID: {project_id}, Slug: {project_slug})")
                
                # Check if this matches our project ID from DSN
                project_id_from_dsn = parsed.path.lstrip('/')
                if str(project_id) == project_id_from_dsn:
                    print(f"    ^^^ This matches our DSN project!")
                    
                    # Get project details
                    project_detail_url = f"https://sentry.io/api/0/projects/{project_id}/"
                    detail_response = requests.get(project_detail_url, headers=headers)
                    
                    if detail_response.status_code == 200:
                        project_detail = detail_response.json()
                        print(f"    Platform: {project_detail.get('platform', 'Unknown')}")
                        print(f"    Created: {project_detail.get('dateCreated', 'Unknown')}")
                        
                        # Get recent issues
                        issues_url = f"https://sentry.io/api/0/projects/{project_id}/issues/"
                        issues_response = requests.get(issues_url, headers=headers, params={'limit': 5})
                        
                        if issues_response.status_code == 200:
                            issues = issues_response.json()
                            print(f"    Recent issues: {len(issues)}")
                            
                            for issue in issues[:3]:  # Show last 3 issues
                                issue_id = issue.get('id', 'Unknown')
                                issue_title = issue.get('title', 'Unknown')
                                issue_level = issue.get('level', 'Unknown')
                                print(f"      - {issue_title} ({issue_level})")
                        
                        print(f"    Project URL: https://sentry.io/{org_data['slug']}/{project_slug}/")
                        return True
        else:
            print(f"ERROR: Projects API failed ({response.status_code})")
            print(f"Response: {response.text}")
            return False
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network request failed: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
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
    print(f"Dashboard URL: https://sentry.io")
    print(f"Direct Project URL: https://sentry.io/{org_id}/issues/?project={project_id}")

def create_test_issue():
    """Create a test issue via API."""
    print("\nCreating Test Issue via API...")
    print("=" * 40)
    
    auth_token = os.getenv('SENTRY_AUTH_TOKEN')
    dsn = os.getenv('SENTRY_DSN')
    
    if not auth_token or not dsn:
        print("ERROR: Missing auth token or DSN")
        return False
    
    from urllib.parse import urlparse
    parsed = urlparse(dsn)
    org_id = parsed.hostname.split('.')[0] if parsed.hostname else None
    project_id = parsed.path.lstrip('/') if parsed.path else None
    
    # Create test issue
    issue_data = {
        "title": "Test Issue from Raptorflow Backend API",
        "message": "This is a test issue created via the Sentry API to verify the connection is working properly.",
        "level": "info",
        "platform": "python",
        "environment": os.getenv('SENTRY_ENVIRONMENT', 'development'),
        "tags": ["test", "raptorflow", "api"]
    }
    
    issue_url = f"https://sentry.io/api/0/projects/{project_id}/issues/"
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(issue_url, json=issue_data, headers=headers)
        
        if response.status_code == 201:
            issue = response.json()
            print("SUCCESS: Test issue created!")
            print(f"  Issue ID: {issue.get('id')}")
            print(f"  Title: {issue.get('title')}")
            print(f"  Level: {issue.get('level')}")
            print(f"  URL: {issue.get('permalink')}")
            return True
        else:
            print(f"ERROR: Failed to create issue ({response.status_code})")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to create issue: {e}")
        return False

if __name__ == "__main__":
    success = test_sentry_api()
    
    if success:
        show_sentry_dashboard_info()
        
        # Ask if user wants to create a test issue
        try:
            user_input = input("\nDo you want to create a test issue? (y/n): ").strip().lower()
            if user_input == 'y':
                create_test_issue()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
        
        print("\nSUCCESS: Sentry API connection is working!")
        print("Your comprehensive monitoring system is ready to use!")
        print("You can now:")
        print("1. Check your Sentry dashboard")
        print("2. Start your Raptorflow backend")
        print("3. Monitor real-time errors and performance")
    else:
        print("\nFAILED: Sentry API connection test failed")
        print("Please check:")
        print("1. Your SENTRY_AUTH_TOKEN is correct")
        print("2. Your organization exists in Sentry")
        print("3. Your project exists in Sentry")
