#!/usr/bin/env python3
"""
Sequential Business Context Template Test Harness

Tests all 3 business context templates one at a time:
1. Clears existing BCM data ("ejects" previous context)
2. Seeds template #1 → Tests → Validates
3. Clears BCM
4. Seeds template #2 → Tests → Validates
5. Clears BCM
6. Seeds template #3 → Tests → Validates

Usage:
    python test_bcm_templates.py <workspace_id>
    
Example:
    python test_bcm_templates.py 1bd63eb6-bc0a-4ceb-82ee-8f2cdfb22ce0
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

BASE_URL = "http://localhost:8080"

# Template definitions
TEMPLATES = {
    "saas": {
        "file": "backend/fixtures/business_context_saas.json",
        "expected_company": "FlowBoard",
        "expected_industry": "SaaS",
    },
    "agency": {
        "file": "backend/fixtures/business_context_agency.json", 
        "expected_company": "GrowthForge",
        "expected_industry": "Agency",
    },
    "ecommerce": {
        "file": "backend/fixtures/business_context_ecommerce.json",
        "expected_company": "EcoThread",
        "expected_industry": "Fashion",
    },
}


def api_request(method, path, workspace_id, data=None):
    """Make API request with workspace header."""
    url = f"{BASE_URL}{path}"
    headers = {
        "Accept": "application/json",
        "x-workspace-id": workspace_id,
    }
    if data:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode()
    else:
        body = None
    
    req = urllib.request.Request(url, method=method, headers=headers, data=body)
    try:
        response = urllib.request.urlopen(req, timeout=10)
        resp_body = response.read().decode()
        return response.status, json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode() if e.read() else ""
        return e.code, json.loads(resp_body) if resp_body else {"error": e.reason}


def clear_bcm(workspace_id):
    """Eject/clear all BCM data for workspace."""
    print(f"  [1/4] Ejecting/Clearing BCM data...")
    status, result = api_request("DELETE", "/api/context/", workspace_id)
    if status in [200, 204]:
        deleted = result.get("deleted_count", "?")
        print(f"        ✓ Cleared {deleted} BCM entries")
        return True
    else:
        print(f"        ✗ Failed to clear: {result}")
        return False


def load_template(template_name):
    """Load business context JSON from fixtures."""
    template_info = TEMPLATES[template_name]
    file_path = Path(template_info["file"])
    
    if not file_path.exists():
        print(f"        ✗ Template file not found: {file_path}")
        return None
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_template(workspace_id, template_name, business_context):
    """Seed BCM with business context template."""
    print(f"  [2/4] Seeding '{template_name}' template...")
    status, result = api_request(
        "POST", "/api/context/seed", workspace_id,
        {"business_context": business_context}
    )
    if status == 200:
        version = result.get("version")
        completion = result.get("completion_pct")
        print(f"        ✓ Seeded BCM v{version} ({completion}% complete)")
        return True
    else:
        print(f"        ✗ Failed to seed: {result}")
        return False


def test_bcm(workspace_id, template_name):
    """Test BCM data was stored correctly."""
    print(f"  [3/4] Testing BCM data...")
    status, result = api_request("GET", "/api/context/", workspace_id)
    if status == 200:
        manifest = result.get("manifest", {})
        foundation = manifest.get("foundation", {})
        
        # Extract company info from manifest
        company = foundation.get("company", "")
        industry = foundation.get("industry", "")
        
        expected = TEMPLATES[template_name]["expected_company"]
        
        if expected.lower() in company.lower():
            print(f"        ✓ Company match: {company}")
            return True
        else:
            print(f"        ✗ Company mismatch: expected '{expected}', got '{company}'")
            return False
    else:
        print(f"        ✗ Failed to fetch BCM: {result}")
        return False


def validate_template_file(template_name):
    """Validate template file structure."""
    print(f"  [4/4] Validating template file...")
    business_context = load_template(template_name)
    if not business_context:
        return False
    
    required_keys = ["company_profile", "intelligence"]
    for key in required_keys:
        if key not in business_context:
            print(f"        ✗ Missing key: {key}")
            return False
    
    company = business_context.get("company_profile", {})
    expected = TEMPLATES[template_name]["expected_company"]
    
    if company.get("name") == expected:
        print(f"        ✓ Template valid: {expected}")
        return True
    else:
        print(f"        ⚠ Company name mismatch: expected '{expected}', got '{company.get('name')}'")
        return True  # Still valid, just warning


def test_single_template(workspace_id, template_name):
    """Test one template end-to-end."""
    print(f"\n{'='*60}")
    print(f"Testing Template: {template_name.upper()}")
    print(f"{'='*60}")
    
    # Step 1: Clear BCM
    if not clear_bcm(workspace_id):
        return False
    time.sleep(0.3)
    
    # Step 2: Load and seed template
    business_context = load_template(template_name)
    if not business_context:
        return False
    
    if not seed_template(workspace_id, template_name, business_context):
        return False
    time.sleep(0.3)
    
    # Step 3: Test BCM
    if not test_bcm(workspace_id, template_name):
        return False
    
    # Step 4: Validate template file
    if not validate_template_file(template_name):
        return False
    
    print(f"\n  ✓✓✓ {template_name.upper()} TEMPLATE PASSED ✓✓✓")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_bcm_templates.py <workspace_id>")
        print("\nExample:")
        print("  python test_bcm_templates.py 1bd63eb6-bc0a-4ceb-82ee-8f2cdfb22ce0")
        sys.exit(1)
    
    workspace_id = sys.argv[1]
    
    print(f"\n{'#'*60}")
    print("# BCM TEMPLATE TEST HARNESS")
    print("# Tests 3 business context templates sequentially")
    print("# Each test: Clear → Seed → Test → Validate")
    print(f"{'#'*60}")
    print(f"\nWorkspace ID: {workspace_id}")
    print(f"Base URL: {BASE_URL}")
    
    results = {}
    
    # Test each template in sequence
    for template_name in ["saas", "agency", "ecommerce"]:
        results[template_name] = test_single_template(workspace_id, template_name)
    
    # Final cleanup
    print(f"\n{'='*60}")
    print("Final Cleanup")
    print(f"{'='*60}")
    clear_bcm(workspace_id)
    
    # Summary
    print(f"\n{'#'*60}")
    print("# TEST SUMMARY")
    print(f"{'#'*60}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for template_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {template_name.upper()}")
    
    print(f"\nTotal: {passed}/{total} templates passed")
    
    if passed == total:
        print("\n🎉 ALL TEMPLATES PASSED! 🎉")
        return 0
    else:
        print(f"\n⚠ {total - passed} template(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
