#!/usr/bin/env python3
"""Comprehensive test of all 32 RaptorFlow API endpoints"""

import urllib.request
import urllib.error
import json
import sys
from typing import Dict, Any, Tuple, Optional

BASE_URL = "http://localhost:8080"
WORKSPACE_ID = "123e4567-e89b-12d3-a456-426614174000"

class EndpointTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def test_endpoint(
        self, 
        method: str, 
        path: str, 
        expected_status: int,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """Test a single endpoint"""
        url = f"{BASE_URL}{path}"
        req_headers = headers or {}
        
        # Add workspace header for API endpoints
        if path.startswith("/api/"):
            req_headers["x-workspace-id"] = WORKSPACE_ID
        
        try:
            req = urllib.request.Request(
                url,
                headers=req_headers,
                method=method,
                data=json.dumps(data).encode() if data else None
            )
            response = urllib.request.urlopen(req, timeout=15)
            actual_status = response.status
            
        except urllib.error.HTTPError as e:
            actual_status = e.code
            # 404 is expected for missing resources, not a failure
            if expected_status == 404 and actual_status == 404:
                return True, "404 as expected"
            if actual_status == expected_status:
                return True, f"HTTP {actual_status}"
            return False, f"HTTP {actual_status} (expected {expected_status})"
            
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
        
        if actual_status == expected_status:
            return True, f"HTTP {actual_status}"
        return False, f"HTTP {actual_status} (expected {expected_status})"
    
    def run_test(self, name: str, method: str, path: str, 
                 expected_status: int, data: Optional[Dict] = None):
        """Run a single test and record result"""
        success, message = self.test_endpoint(method, path, expected_status, data)
        status = "✓" if success else "✗"
        
        self.results.append({
            "name": name,
            "method": method,
            "path": path,
            "status": status,
            "message": message
        })
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
            
        print(f"{status} {method:6} {path:45} {message}")
    
    def run_all_tests(self):
        """Run all 32 endpoint tests"""
        print("=" * 80)
        print("RaptorFlow API Endpoint Testing - All 32 Endpoints")
        print("=" * 80)
        print()
        
        # System Endpoints (2)
        print("--- System Endpoints ---")
        self.run_test("Root", "GET", "/", 200)
        self.run_test("Health", "GET", "/health", 200)
        print()
        
        # Workspaces (3)
        print("--- Workspaces ---")
        self.run_test("Create Workspace", "POST", "/api/workspaces/", 201, {"name": "Test"})
        self.run_test("Get Workspace", "GET", f"/api/workspaces/{WORKSPACE_ID}", 404)  # Expect 404 for fake ID
        self.run_test("Update Workspace", "PATCH", f"/api/workspaces/{WORKSPACE_ID}", 404, {"name": "Updated"})
        print()
        
        # Campaigns (5)
        print("--- Campaigns ---")
        self.run_test("List Campaigns", "GET", "/api/campaigns/", 200)
        self.run_test("Create Campaign", "POST", "/api/campaigns/", 201, {"name": "Test Campaign"})
        self.run_test("Get Campaign", "GET", "/api/campaigns/123e4567-e89b-12d3-a456-426614174001", 404)
        self.run_test("Update Campaign", "PATCH", "/api/campaigns/123e4567-e89b-12d3-a456-426614174001", 404, {"name": "Updated"})
        self.run_test("Delete Campaign", "DELETE", "/api/campaigns/123e4567-e89b-12d3-a456-426614174001", 404)
        print()
        
        # Moves (4)
        print("--- Moves ---")
        self.run_test("List Moves", "GET", "/api/moves/", 200)
        self.run_test("Create Move", "POST", "/api/moves/", 201, {
            "id": "123e4567-e89b-12d3-a456-426614174002",
            "name": "Test Move",
            "category": "ignite",
            "status": "draft",
            "duration": 7,
            "goal": "distribution",
            "tone": "professional",
            "context": "Test context",
            "createdAt": "2026-01-01T00:00:00Z"
        })
        self.run_test("Update Move", "PATCH", "/api/moves/123e4567-e89b-12d3-a456-426614174002", 404, {"name": "Updated"})
        self.run_test("Delete Move", "DELETE", "/api/moves/123e4567-e89b-12d3-a456-426614174002", 404)
        print()
        
        # Foundation (2)
        print("--- Foundation ---")
        self.run_test("Get Foundation", "GET", "/api/foundation/", 200)
        self.run_test("Save Foundation", "PUT", "/api/foundation/", 200, {"mission": "Test mission"})
        print()
        
        # Context/BCM (4)
        print("--- Context/BCM ---")
        self.run_test("Get BCM", "GET", "/api/context/", 404)  # Expect 404 if no data
        self.run_test("Rebuild BCM", "POST", "/api/context/rebuild", 404)  # Expect 404 if no source
        self.run_test("Seed BCM", "POST", "/api/context/seed", 200, {
            "business_context": {"test": "data"}
        })
        self.run_test("List BCM Versions", "GET", "/api/context/versions", 200)
        print()
        
        # Muse (2)
        print("--- Muse ---")
        self.run_test("Muse Health", "GET", "/api/muse/health", 200)
        self.run_test("Muse Generate", "POST", "/api/muse/generate", 200, {
            "task": "Write a test",
            "content_type": "text"
        })
        print()
        
        # Scraper (6) - NEW
        print("--- Scraper (NEW) ---")
        self.run_test("Scraper Health", "GET", "/api/scraper/health", 200)
        self.run_test("Scraper Stats", "GET", "/api/scraper/stats", 200)
        self.run_test("Scraper Strategies", "GET", "/api/scraper/strategies", 200)
        self.run_test("Scraper Analytics", "GET", "/api/scraper/analytics?days=7", 200)
        self.run_test("Scrape URL", "POST", "/api/scraper/", 200, {
            "url": "https://example.com",
            "user_id": "test-user",
            "strategy": "optimized"
        })
        self.run_test("Update Strategy", "POST", "/api/scraper/strategy", 200, {"strategy": "turbo"})
        print()
        
        # Search (4) - NEW
        print("--- Search (NEW) ---")
        self.run_test("Search Health", "GET", "/api/search/health", 200)
        self.run_test("Search Engines", "GET", "/api/search/engines", 200)
        self.run_test("Search Status", "GET", "/api/search/status", 200)
        self.run_test("Web Search", "GET", "/api/search/?q=test&engines=duckduckgo&max_results=5", 200)
        print()
        
        # Summary
        print("=" * 80)
        print(f"Results: {self.passed} passed, {self.failed} failed out of {self.passed + self.failed} tests")
        print("=" * 80)
        
        if self.failed > 0:
            print("\nFailed Tests:")
            for r in self.results:
                if r["status"] == "✗":
                    print(f"  - {r['method']} {r['path']}: {r['message']}")
        
        return self.failed == 0

if __name__ == "__main__":
    tester = EndpointTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
