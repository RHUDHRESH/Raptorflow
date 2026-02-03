"""
Backend Restructure Verification Script
Tests that all new modules import correctly
"""

import sys

def test_import(module_name, description):
    """Test importing a module"""
    try:
        __import__(module_name)
        print(f"✓ {description}")
        return True
    except Exception as e:
        print(f"✗ {description}: {e}")
        return False

def main():
    print("=" * 60)
    print("Backend Restructure Verification")
    print("=" * 60)
    print()
    
    results = []
    
    # Test Infrastructure
    print("Infrastructure Layer:")
    results.append(test_import("infrastructure.database", "Database client"))
    results.append(test_import("infrastructure.cache", "Cache client"))
    results.append(test_import("infrastructure.llm", "LLM client"))
    results.append(test_import("infrastructure.email", "Email client"))
    results.append(test_import("infrastructure", "Infrastructure package"))
    print()
    
    # Test Domains
    print("Domain Modules:")
    results.append(test_import("domains.auth", "Auth domain"))
    results.append(test_import("domains.auth.models", "Auth models"))
    results.append(test_import("domains.auth.service", "Auth service"))
    results.append(test_import("domains.auth.router", "Auth router"))
    
    results.append(test_import("domains.payments", "Payments domain"))
    results.append(test_import("domains.payments.models", "Payments models"))
    results.append(test_import("domains.payments.service", "Payments service"))
    results.append(test_import("domains.payments.router", "Payments router"))
    
    results.append(test_import("domains.onboarding", "Onboarding domain"))
    results.append(test_import("domains.onboarding.models", "Onboarding models"))
    results.append(test_import("domains.onboarding.service", "Onboarding service"))
    results.append(test_import("domains.onboarding.router", "Onboarding router"))
    
    results.append(test_import("domains.agents", "Agents domain"))
    results.append(test_import("domains.agents.models", "Agents models"))
    results.append(test_import("domains.agents.service", "Agents service"))
    results.append(test_import("domains.agents.router", "Agents router"))
    print()
    
    # Test App
    print("Application Layer:")
    results.append(test_import("app.lifespan", "Lifespan manager"))
    results.append(test_import("app.middleware", "Middleware"))
    results.append(test_import("app", "App package"))
    print()
    
    # Test Dependencies
    print("Dependencies:")
    results.append(test_import("dependencies", "Dependencies module"))
    print()
    
    # Test Main
    print("Main Entry Point:")
    results.append(test_import("main", "Main module"))
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All imports successful! Backend restructure is solid.")
        return 0
    else:
        print(f"✗ {total - passed} import(s) failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
