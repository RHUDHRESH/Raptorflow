#!/usr/bin/env python3
"""
RaptorFlow Backend Test Script
Production backend health check and validation
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthCheckResult(BaseModel):
    """Health check result model."""
    status: str
    timestamp: datetime
    services: Dict[str, str]
    version: str
    uptime: Optional[float] = None


class BackendTester:
    """Backend testing and health check utility."""

    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:8080")
        self.timeout = 30
        self.max_retries = 3

    async def test_connection(self) -> bool:
        """Test basic connection to backend."""
        logger.info("Testing backend connection...")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(f"{self.base_url}/")
                    if response.status_code == 200:
                        logger.info("✅ Backend connection successful")
                        return True
                except Exception as e:
                    logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2)
            
            logger.error("❌ Backend connection failed")
            return False

    async def test_health_endpoint(self) -> HealthCheckResult:
        """Test comprehensive health endpoint."""
        logger.info("Testing health endpoint...")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    health_data = response.json()
                    logger.info("✅ Health endpoint responding")
                    return HealthCheckResult(**health_data)
                else:
                    logger.error(f"❌ Health endpoint returned {response.status_code}")
                    return HealthCheckResult(
                        status="unhealthy",
                        timestamp=datetime.utcnow(),
                        services={"api": "error"},
                        version="unknown"
                    )
            except Exception as e:
                logger.error(f"❌ Health endpoint error: {e}")
                return HealthCheckResult(
                    status="error",
                    timestamp=datetime.utcnow(),
                    services={"api": "error"},
                    version="unknown"
                )

    async def test_api_endpoints(self) -> Dict[str, bool]:
        """Test critical API endpoints."""
        logger.info("Testing API endpoints...")
        
        endpoints = {
            "/api/v1/health": "Health check",
            "/api/v1/auth/status": "Auth status",
            "/api/v1/users/me": "User profile",
            "/api/v1/workspaces": "Workspaces",
            "/docs": "API documentation"
        }
        
        results = {}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for endpoint, description in endpoints.items():
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    success = response.status_code in [200, 401, 403]  # 401/403 are expected for protected endpoints
                    results[endpoint] = success
                    
                    if success:
                        logger.info(f"✅ {description} - {response.status_code}")
                    else:
                        logger.warning(f"⚠️ {description} - {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"❌ {description} - {e}")
                    results[endpoint] = False
        
        return results

    async def test_database_connection(self) -> bool:
        """Test database connection."""
        logger.info("Testing database connection...")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.base_url}/api/v1/health/database")
                if response.status_code == 200:
                    data = response.json()
                    db_status = data.get("database", "unknown")
                    if db_status == "connected":
                        logger.info("✅ Database connection successful")
                        return True
                    else:
                        logger.warning(f"⚠️ Database status: {db_status}")
                        return False
                else:
                    logger.error(f"❌ Database health check failed: {response.status_code}")
                    return False
            except Exception as e:
                logger.error(f"❌ Database connection error: {e}")
                return False

    async def test_redis_connection(self) -> bool:
        """Test Redis connection."""
        logger.info("Testing Redis connection...")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.base_url}/api/v1/health/redis")
                if response.status_code == 200:
                    data = response.json()
                    redis_status = data.get("redis", "unknown")
                    if redis_status == "connected":
                        logger.info("✅ Redis connection successful")
                        return True
                    else:
                        logger.warning(f"⚠️ Redis status: {redis_status}")
                        return False
                else:
                    logger.error(f"❌ Redis health check failed: {response.status_code}")
                    return False
            except Exception as e:
                logger.error(f"❌ Redis connection error: {e}")
                return False

    async def test_authentication(self) -> bool:
        """Test authentication system."""
        logger.info("Testing authentication system...")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Test login endpoint (should return 401 without credentials)
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json={"email": "test@example.com", "password": "test"}
                )
                
                if response.status_code == 401:
                    logger.info("✅ Authentication system responding (correctly rejects invalid credentials)")
                    return True
                elif response.status_code == 422:
                    logger.info("✅ Authentication system responding (validation working)")
                    return True
                else:
                    logger.warning(f"⚠️ Unexpected auth response: {response.status_code}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Authentication test error: {e}")
                return False

    async def test_rate_limiting(self) -> bool:
        """Test rate limiting."""
        logger.info("Testing rate limiting...")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Make multiple rapid requests
                responses = []
                for i in range(5):
                    response = await client.get(f"{self.base_url}/api/v1/health")
                    responses.append(response.status_code)
                    await asyncio.sleep(0.1)
                
                # Check if any requests were rate limited
                rate_limited = any(status == 429 for status in responses)
                
                if rate_limited:
                    logger.info("✅ Rate limiting is active")
                    return True
                else:
                    logger.warning("⚠️ Rate limiting may not be active")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Rate limiting test error: {e}")
                return False

    async def test_cors_headers(self) -> bool:
        """Test CORS headers."""
        logger.info("Testing CORS headers...")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.options(
                    f"{self.base_url}/api/v1/health",
                    headers={"Origin": "https://raptorflow.com"}
                )
                
                cors_headers = {
                    "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                    "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                    "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                }
                
                if cors_headers["Access-Control-Allow-Origin"]:
                    logger.info("✅ CORS headers present")
                    return True
                else:
                    logger.warning("⚠️ CORS headers missing")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ CORS test error: {e}")
                return False

    async def run_comprehensive_test(self) -> Dict[str, any]:
        """Run comprehensive backend tests."""
        logger.info("🚀 Starting comprehensive backend tests...")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "base_url": self.base_url,
            "tests": {}
        }
        
        # Test basic connection
        results["tests"]["connection"] = await self.test_connection()
        
        if not results["tests"]["connection"]:
            logger.error("❌ Basic connection failed, skipping other tests")
            results["status"] = "failed"
            results["error"] = "Connection failed"
            return results
        
        # Run all tests
        test_functions = [
            ("health_check", self.test_health_endpoint),
            ("database", self.test_database_connection),
            ("redis", self.test_redis_connection),
            ("authentication", self.test_authentication),
            ("rate_limiting", self.test_rate_limiting),
            ("cors_headers", self.test_cors_headers),
            ("api_endpoints", self.test_api_endpoints),
        ]
        
        for test_name, test_func in test_functions:
            try:
                if test_name == "api_endpoints":
                    results["tests"][test_name] = await test_func()
                else:
                    results["tests"][test_name] = await test_func()
            except Exception as e:
                logger.error(f"❌ {test_name} test failed: {e}")
                results["tests"][test_name] = False
        
        # Calculate overall status
        passed_tests = sum(1 for result in results["tests"].values() 
                          if result is True or 
                          (isinstance(result, dict) and all(result.values())))
        total_tests = len(results["tests"])
        
        results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests) * 100
        }
        
        if passed_tests == total_tests:
            results["status"] = "passed"
            logger.info("🎉 All tests passed!")
        elif passed_tests >= total_tests * 0.8:
            results["status"] = "warning"
            logger.warning(f"⚠️ {passed_tests}/{total_tests} tests passed")
        else:
            results["status"] = "failed"
            logger.error(f"❌ Only {passed_tests}/{total_tests} tests passed")
        
        return results

    def print_results(self, results: Dict[str, any]):
        """Print test results in a formatted way."""
        print("\n" + "="*60)
        print("RAPTORFLOW BACKEND TEST RESULTS")
        print("="*60)
        
        print(f"Timestamp: {results['timestamp']}")
        print(f"Base URL: {results['base_url']}")
        print(f"Status: {results['status'].upper()}")
        
        if "summary" in results:
            summary = results["summary"]
            print(f"\nTest Summary:")
            print(f"  Total Tests: {summary['total_tests']}")
            print(f"  Passed: {summary['passed_tests']}")
            print(f"  Failed: {summary['failed_tests']}")
            print(f"  Success Rate: {summary['success_rate']:.1f}%")
        
        print(f"\nDetailed Results:")
        for test_name, result in results["tests"].items():
            if isinstance(result, dict):
                passed = sum(1 for v in result.values() if v)
                total = len(result)
                status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"
                print(f"  {status} {test_name}: {passed}/{total} endpoints")
            else:
                status = "✅" if result else "❌"
                print(f"  {status} {test_name}: {'PASS' if result else 'FAIL'}")
        
        print("="*60)


async def main():
    """Main function to run backend tests."""
    tester = BackendTester()
    
    try:
        results = await tester.run_comprehensive_test()
        tester.print_results(results)
        
        # Exit with appropriate code
        if results["status"] == "passed":
            sys.exit(0)
        elif results["status"] == "warning":
            sys.exit(1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())
