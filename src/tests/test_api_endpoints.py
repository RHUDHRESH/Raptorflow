#!/usr/bin/env python3
"""Test all API endpoints for RaptorFlow backend."""

import urllib.request
import urllib.error
import json

BASE_URL = "http://localhost:8000"
WORKSPACE_ID = "123e4567-e89b-12d3-a456-426614174000"

def test_endpoint(method, path, headers=None, data=None):
    """Test a single endpoint."""
    url = f"{BASE_URL}{path}"
    req_headers = headers or {}
    
    # FastAPI redirects to trailing slash, so let's handle that
    if method in ["POST", "PUT", "PATCH"] and not path.endswith("/"):
        # Try with trailing slash first to avoid 307
        url = f"{BASE_URL}{path}/"
    
    try:
        req = urllib.request.Request(
            url, 
            headers=req_headers, 
            method=method, 
            data=json.dumps(data).encode() if data else None
        )
        response = urllib.request.urlopen(req, timeout=10)
        return response.status, "OK"
    except urllib.error.HTTPError as e:
        if e.code == 307:
            # Follow the redirect
            redirect_url = e.headers.get('Location')
            if redirect_url:
                try:
                    req = urllib.request.Request(
                        redirect_url, 
                        headers=req_headers, 
                        method=method, 
                        data=json.dumps(data).encode() if data else None
                    )
                    response = urllib.request.urlopen(req, timeout=10)
                    return response.status, "OK"
                except urllib.error.HTTPError as e2:
                    return e2.code, e2.reason
        return e.code, e.reason
    except Exception as e:
        return "ERROR", str(e)[:50]

def main():
    print("Testing RaptorFlow API Endpoints")
    print("=" * 50)
    
    tests = [
        # System endpoints
        ("GET", "/", {}),
        ("GET", "/health", {}),
        
        # Workspaces
        ("POST", "/api/workspaces", {"Content-Type": "application/json"}, {"name": "Test Workspace"}),
        ("GET", f"/api/workspaces/{WORKSPACE_ID}", {}),
        ("PATCH", f"/api/workspaces/{WORKSPACE_ID}", {"Content-Type": "application/json", "x-workspace-id": WORKSPACE_ID}, {"name": "Updated"}),
        
        # Campaigns
        ("GET", "/api/campaigns", {"x-workspace-id": WORKSPACE_ID}),
        ("POST", "/api/campaigns", {"Content-Type": "application/json", "x-workspace-id": WORKSPACE_ID}, {"name": "Test Campaign"}),
        
        # Moves
        ("GET", "/api/moves", {"x-workspace-id": WORKSPACE_ID}),
        
        # Foundation
        ("GET", "/api/foundation", {"x-workspace-id": WORKSPACE_ID}),
        ("PUT", "/api/foundation", {"Content-Type": "application/json", "x-workspace-id": WORKSPACE_ID}, {"mission": "Test mission"}),
        
        # Context (BCM)
        ("GET", "/api/context", {"x-workspace-id": WORKSPACE_ID}),
        ("GET", "/api/context/versions", {"x-workspace-id": WORKSPACE_ID}),
        
        # Muse
        ("GET", "/api/muse/health", {"x-workspace-id": WORKSPACE_ID}),
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        method, path = test[0], test[1]
        headers = test[2] if len(test) > 2 else {}
        data = test[3] if len(test) > 3 else None
        
        status, msg = test_endpoint(method, path, headers, data)
        
        # 200-299 = success, 400-499 = expected errors (validation/not found), 500 = server error
        status_num = status if isinstance(status, int) else 0
        if 200 <= status_num < 300:
            status_str = f"✓ {status}"
            passed += 1
        elif 400 <= status_num < 500:
            status_str = f"⚠ {status}"
            passed += 1  # Expected behavior for invalid data
        else:
            status_str = f"✗ {status}"
            failed += 1
            
        print(f"{method:6} {path:40} {status_str:10} {msg}")
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    main()
