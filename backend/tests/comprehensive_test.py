import pytest

pytest.skip(
    "Archived manual test script; use explicit run if needed.", allow_module_level=True
)

#!/usr/bin/env python3
"""
Comprehensive Test Suite for Raptorflow Onboarding Backend
Tests web scraping, file processing, and API functionality
"""

import asyncio
import json
import os
import tempfile
from datetime import datetime

import httpx


class RaptorflowTestSuite:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"test-session-{int(datetime.now().timestamp())}"
        self.results = []

    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}: {details}"
        print(result)
        self.results.append(
            {
                "test": test_name,
                "success": success,
                "details": details,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    async def test_health_check(self):
        """Test backend health endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                data = response.json()

                success = (
                    response.status_code == 200
                    and data.get("status") == "healthy"
                    and "web_scraping" in data.get("services", {})
                )

                self.log_result(
                    "Health Check",
                    success,
                    f"Status: {data.get('status')}, Services: {list(data.get('services', {}).keys())}",
                )
                return success
        except Exception as e:
            self.log_result("Health Check", False, f"Exception: {str(e)}")
            return False

    async def test_web_scraping(self):
        """Test web scraping functionality"""
        test_urls = [
            "https://example.com",
            "https://httpbin.org/html",
            "https://jsonplaceholder.typicode.com",
        ]

        for url in test_urls:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    payload = {
                        "url": url,
                        "item_id": f"test-{url.replace('https://', '').replace('/', '-')}",
                    }
                    response = await client.post(
                        f"{self.base_url}/api/onboarding/{self.session_id}/vault/url",
                        json=payload,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        success = data.get("scraped", False) and data.get("title", "")

                        self.log_result(
                            f"Web Scraping - {url}",
                            success,
                            f"Title: '{data.get('title', '')[:50]}...', Content length: {len(data.get('content', ''))}",
                        )
                    else:
                        self.log_result(
                            f"Web Scraping - {url}",
                            False,
                            f"HTTP {response.status_code}",
                        )

            except Exception as e:
                self.log_result(f"Web Scraping - {url}", False, f"Exception: {str(e)}")

    async def test_file_processing(self):
        """Test file upload and processing"""
        # Test different file types
        test_files = [
            ("test.txt", b"This is a test document for OCR processing.", "text/plain"),
            (
                "test.html",
                b"<html><head><title>Test HTML</title></head><body><p>Test paragraph</p></body></html>",
                "text/html",
            ),
            ("test.json", b'{"test": "data", "number": 123}', "application/json"),
        ]

        for filename, content, content_type in test_files:
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(
                    mode="wb", delete=False, suffix=f"_{filename}"
                ) as f:
                    f.write(content)
                    temp_path = f.name

                # Upload file
                async with httpx.AsyncClient(timeout=15.0) as client:
                    with open(temp_path, "rb") as f:
                        files = {"file": (filename, f, content_type)}
                        data = {"item_id": f"file-{filename}"}

                        response = await client.post(
                            f"{self.base_url}/api/onboarding/{self.session_id}/vault/upload",
                            files=files,
                            data=data,
                        )

                # Clean up
                os.unlink(temp_path)

                if response.status_code == 200:
                    result = response.json()
                    success = result.get("success", False) and result.get(
                        "ocr_processed", False
                    )

                    self.log_result(
                        f"File Processing - {filename}",
                        success,
                        f"Size: {result.get('size', 0)} bytes, OCR: {result.get('ocr_processed', False)}",
                    )
                else:
                    self.log_result(
                        f"File Processing - {filename}",
                        False,
                        f"HTTP {response.status_code}",
                    )

            except Exception as e:
                self.log_result(
                    f"File Processing - {filename}", False, f"Exception: {str(e)}"
                )

    async def test_step_management(self):
        """Test step data management"""
        try:
            async with httpx.AsyncClient() as client:
                # Update step data
                payload = {
                    "data": {
                        "test_field": "test_value",
                        "timestamp": datetime.utcnow().isoformat(),
                        "evidence_count": 3,
                    },
                    "version": 1,
                }

                response = await client.post(
                    f"{self.base_url}/api/onboarding/{self.session_id}/steps/1",
                    json=payload,
                )

                if response.status_code == 200:
                    # Retrieve step data
                    response2 = await client.get(
                        f"{self.base_url}/api/onboarding/{self.session_id}/steps/1"
                    )

                    if response2.status_code == 200:
                        data = response2.json()
                        stored_data = data.get("data", {})
                        success = stored_data.get("test_field") == "test_value"

                        self.log_result(
                            "Step Management",
                            success,
                            f"Stored and retrieved: {list(stored_data.keys())}",
                        )
                    else:
                        self.log_result(
                            "Step Management", False, "Failed to retrieve step data"
                        )
                else:
                    self.log_result(
                        "Step Management", False, f"HTTP {response.status_code}"
                    )

        except Exception as e:
            self.log_result("Step Management", False, f"Exception: {str(e)}")

    async def test_vault_operations(self):
        """Test vault CRUD operations"""
        try:
            async with httpx.AsyncClient() as client:
                # Get vault contents
                response = await client.get(
                    f"{self.base_url}/api/onboarding/{self.session_id}/vault"
                )

                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", {})

                    self.log_result(
                        "Vault Operations",
                        True,
                        f"Total items: {data.get('total_items', 0)}, Keys: {list(items.keys())}",
                    )
                else:
                    self.log_result(
                        "Vault Operations", False, f"HTTP {response.status_code}"
                    )

        except Exception as e:
            self.log_result("Vault Operations", False, f"Exception: {str(e)}")

    async def test_cross_validation(self):
        """Cross-validate web scraping with external search"""
        # Test the same URL that we tested in the frontend
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "url": "https://example.com",
                    "item_id": os.getenv("ITEM_ID"),
                }
                response = await client.post(
                    f"{self.base_url}/api/onboarding/{self.session_id}/vault/url",
                    json=payload,
                )

                if response.status_code == 200:
                    data = response.json()
                    title = data.get("title", "")
                    content = data.get("content", "")

                    # Cross-validation checks
                    has_correct_title = "Example Domain" in title
                    has_documentation_mention = (
                        "documentation" in content.lower()
                        or "examples" in content.lower()
                    )
                    has_permission_mention = "permission" in content.lower()

                    success = has_correct_title and (
                        has_documentation_mention or has_permission_mention
                    )

                    self.log_result(
                        "Cross-Validation",
                        success,
                        f"Title match: {has_correct_title}, Content validation: {has_documentation_mention or has_permission_mention}",
                    )

                    # Print actual content for verification
                    print(f"    📄 Scraped title: '{title}'")
                    print(f"    📄 Scraped content: '{content[:100]}...'")

                else:
                    self.log_result(
                        "Cross-Validation", False, f"HTTP {response.status_code}"
                    )

        except Exception as e:
            self.log_result("Cross-Validation", False, f"Exception: {str(e)}")

    async def run_all_tests(self):
        """Run all test suites"""
        print(f"🚀 Starting Raptorflow Backend Test Suite")
        print(f"📅 Session ID: {self.session_id}")
        print(f"🌐 Backend URL: {self.base_url}")
        print("=" * 60)

        # Run tests
        await self.test_health_check()
        await self.test_web_scraping()
        await self.test_file_processing()
        await self.test_step_management()
        await self.test_vault_operations()
        await self.test_cross_validation()

        # Summary
        print("=" * 60)
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests

        print(f"📊 Test Summary: {passed_tests}/{total_tests} passed")

        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")

        # Save results
        with open(f"test_results_{self.session_id}.json", "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results saved to: test_results_{self.session_id}.json")
        print(f"🎯 Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        return passed_tests == total_tests


if __name__ == "__main__":
    suite = RaptorflowTestSuite()
    success = asyncio.run(suite.run_all_tests())
    exit(0 if success else 1)
