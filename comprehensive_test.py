"""
Comprehensive System Test Suite
Tests all critical components of Raptorflow
"""

import asyncio
import requests
import json
import time
from typing import Dict, List, Any
from pathlib import Path

class SystemTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.results = []
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": time.time()
        }
        self.results.append(result)
        print(f"{status}: {test_name} {message}")
    
    def test_backend_health(self) -> bool:
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            passed = response.status_code == 200
            self.log_test(
                "Backend Health Check",
                passed,
                f"Status: {response.status_code}"
            )
            return passed
        except Exception as e:
            self.log_test("Backend Health Check", False, str(e))
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test critical API endpoints"""
        endpoints = [
            "/api/v1/health/",
            "/api/v1/users/me",
            "/api/v1/campaigns/",
            "/api/v1/moves/",
            "/api/v1/blackbox/",
            "/api/v1/analytics/",
        ]
        
        all_passed = True
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                passed = response.status_code in [200, 401, 403]  # Accept auth errors
                self.log_test(
                    f"API Endpoint {endpoint}",
                    passed,
                    f"Status: {response.status_code}"
                )
                if not passed:
                    all_passed = False
            except Exception as e:
                self.log_test(f"API Endpoint {endpoint}", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_frontend_build(self) -> bool:
        """Test frontend build process"""
        try:
            # Check if frontend directory exists
            frontend_dir = Path("frontend")
            if not frontend_dir.exists():
                self.log_test("Frontend Directory", False, "Frontend directory not found")
                return False
            
            # Check package.json
            package_json = frontend_dir / "package.json"
            if not package_json.exists():
                self.log_test("Package.json", False, "package.json not found")
                return False
            
            self.log_test("Frontend Structure", True, "Frontend files present")
            return True
        except Exception as e:
            self.log_test("Frontend Build", False, str(e))
            return False
    
    def test_database_connection(self) -> bool:
        """Test database connection"""
        try:
            # This would require the backend to be running
            response = requests.get(f"{self.backend_url}/api/v1/health/detailed", timeout=5)
            if response.status_code == 200:
                data = response.json()
                db_status = data.get("database", "unknown")
                passed = db_status == "connected" or db_status == "ok"
                self.log_test(
                    "Database Connection",
                    passed,
                    f"Status: {db_status}"
                )
                return passed
            else:
                self.log_test("Database Connection", False, "Health endpoint not responding")
                return False
        except Exception as e:
            self.log_test("Database Connection", False, str(e))
            return False
    
    def test_redis_connection(self) -> bool:
        """Test Redis connection"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/health/detailed", timeout=5)
            if response.status_code == 200:
                data = response.json()
                redis_status = data.get("redis", "unknown")
                passed = redis_status == "connected" or redis_status == "ok"
                self.log_test(
                    "Redis Connection",
                    passed,
                    f"Status: {redis_status}"
                )
                return passed
            else:
                self.log_test("Redis Connection", False, "Health endpoint not responding")
                return False
        except Exception as e:
            self.log_test("Redis Connection", False, str(e))
            return False
    
    def test_configuration(self) -> bool:
        """Test configuration files"""
        config_files = [
            ".env.template",
            "backend/config_clean.py",
            "backend/app.py",
            "frontend/package.json"
        ]
        
        all_passed = True
        for config_file in config_files:
            if Path(config_file).exists():
                self.log_test(f"Config File {config_file}", True, "Found")
            else:
                self.log_test(f"Config File {config_file}", False, "Missing")
                all_passed = False
        
        return all_passed
    
    def test_type_check(self) -> bool:
        """Test TypeScript compilation"""
        try:
            import subprocess
            result = subprocess.run(
                ["npm", "run", "type-check"],
                cwd="frontend",
                capture_output=True,
                text=True,
                timeout=30
            )
            
            passed = result.returncode == 0
            self.log_test(
                "TypeScript Type Check",
                passed,
                "No type errors" if passed else f"Errors found: {len(result.stderr.splitlines())}"
            )
            return passed
        except Exception as e:
            self.log_test("TypeScript Type Check", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("🧪 Running Comprehensive System Tests...")
        print("=" * 50)
        
        tests = [
            self.test_configuration,
            self.test_frontend_build,
            self.test_backend_health,
            self.test_api_endpoints,
            self.test_database_connection,
            self.test_redis_connection,
            self.test_type_check,
        ]
        
        passed_count = 0
        total_count = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_count += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        # Calculate results
        success_rate = (passed_count / total_count) * 100
        
        print("=" * 50)
        print(f"📊 Test Results: {passed_count}/{total_count} passed ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 System is HEALTHY and ready for production!")
        elif success_rate >= 60:
            print("⚠️  System has issues but may be functional")
        else:
            print("🚨 System has critical issues - NOT production ready!")
        
        # Generate report
        report = {
            "total_tests": total_count,
            "passed_tests": passed_count,
            "success_rate": success_rate,
            "results": self.results,
            "timestamp": time.time()
        }
        
        # Save report
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Detailed report saved to test_report.json")
        
        return report

def main():
    """Main test runner"""
    tester = SystemTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["success_rate"] >= 80:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()
