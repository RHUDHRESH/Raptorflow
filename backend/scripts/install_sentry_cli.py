#!/usr/bin/env python3
"""
Install Sentry CLI
==================

Install and configure Sentry CLI for API access.
"""

import subprocess
import sys
import os

def install_sentry_cli():
    """Install Sentry CLI."""
    print("Installing Sentry CLI...")
    print("=" * 40)
    
    try:
        # Check if sentry-cli is already installed
        result = subprocess.run(['sentry-cli', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Sentry CLI already installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    # Install sentry-cli
    print("Installing sentry-cli...")
    try:
        result = subprocess.run(['pip', 'install', 'sentry-cli'], capture_output=True, text=True)
        if result.returncode == 0:
            print("SUCCESS: Sentry CLI installed!")
            return True
        else:
            print(f"ERROR: Failed to install sentry-cli: {result.stderr}")
            return False
    except Exception as e:
        print(f"ERROR: Failed to install sentry-cli: {e}")
        return False

def configure_sentry_cli():
    """Configure Sentry CLI with auth token."""
    print("\nConfiguring Sentry CLI...")
    print("=" * 40)
    
    auth_token = os.getenv('SENTRY_AUTH_TOKEN')
    if not auth_token:
        print("ERROR: SENTRY_AUTH_TOKEN not found")
        return False
    
    try:
        # Set auth token
        result = subprocess.run(['sentry-cli', 'login', '--auth-token', auth_token], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCESS: Sentry CLI configured!")
            return True
        else:
            print(f"ERROR: Failed to configure Sentry CLI: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to configure Sentry CLI: {e}")
        return False

def list_organizations():
    """List Sentry organizations."""
    print("\nListing Sentry Organizations...")
    print("=" * 40)
    
    try:
        result = subprocess.run(['sentry-cli', 'organizations', 'list'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCESS: Organizations found!")
            print(result.stdout)
            return True
        else:
            print(f"ERROR: Failed to list organizations: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to list organizations: {e}")
        return False

def list_projects():
    """List Sentry projects."""
    print("\nListing Sentry Projects...")
    print("=" * 40)
    
    try:
        result = subprocess.run(['sentry-cli', 'projects', 'list'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCESS: Projects found!")
            print(result.stdout)
            return True
        else:
            print(f"ERROR: Failed to list projects: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to list projects: {e}")
        return False

def create_test_issue():
    """Create a test issue using CLI."""
    print("\nCreating Test Issue using CLI...")
    print("=" * 40)
    
    try:
        # Create a simple test issue
        result = subprocess.run(['sentry-cli', 'issues', 'new', 
                               '--title', 'Test Issue from Raptorflow CLI',
                               '--message', 'This is a test issue created via Sentry CLI to verify the connection is working properly.',
                               '--level', 'info',
                               '--tags', 'test,raptorflow,cli'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCESS: Test issue created!")
            print(result.stdout)
            return True
        else:
            print(f"ERROR: Failed to create issue: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to create issue: {e}")
        return False

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Note: python-dotenv not installed")
    
    # Install CLI
    if not install_sentry_cli():
        sys.exit(1)
    
    # Configure CLI
    if not configure_sentry_cli():
        sys.exit(1)
    
    # List organizations
    if not list_organizations():
        sys.exit(1)
    
    # List projects
    if not list_projects():
        sys.exit(1)
    
    # Ask if user wants to create a test issue
    try:
        user_input = input("\nDo you want to create a test issue? (y/n): ").strip().lower()
        if user_input == 'y':
            create_test_issue()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    
    print("\nSUCCESS: Sentry CLI setup complete!")
    print("You can now use sentry-cli commands to manage your Sentry projects.")
    print("Your comprehensive monitoring system is ready to use!")
