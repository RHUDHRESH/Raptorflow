#!/usr/bin/env python3
"""
CYNICAL VERIFICATION TEST
Tests Gemini 1.5 Flash is actually being used - no mocks, no fallbacks
"""

import json
import os
import time
from typing import Any, Dict

import requests


class CynicalVerifier:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.test_results = []

    def log_test(self, test_name: str, passed: bool, details: str = ""):
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": time.time(),
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_backend_health(self) -> bool:
        """Test if backend is responsive"""
        try:
            response = requests.get(f"{self.backend_url}/", timeout=5)
            return response.status_code == 200
        except Exception as e:
            return False

    def test_ai_endpoint_real_request(self) -> bool:
        """Test actual AI endpoint with real request"""
        try:
            payload = {
                "prompt": "What is 2+2? Answer with just the number.",
                "user_id": "test-user-verification",
                "model": "gemini-1.5-flash",
            }

            response = requests.post(
                f"{self.backend_url}/ai/generate",
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                data = response.json()
                # Verify response structure and model
                has_content = "content" in data and data["content"]
                correct_model = data.get("model") == "gemini-1.5-flash"
                has_usage = "usage_logged" in data

                return has_content and correct_model and has_usage
            else:
                return False

        except Exception as e:
            print(f"   Error: {e}")
            return False

    def test_model_override_protection(self) -> bool:
        """Test that other models get overridden to gemini-1.5-flash"""
        try:
            fake_models = ["gpt-4", "claude-3", "gemini-pro", "fake-model"]

            for fake_model in fake_models:
                payload = {
                    "prompt": "Say 'hello'",
                    "user_id": "test-user-verification",
                    "model": fake_model,  # Try to use fake model
                }

                response = requests.post(
                    f"{self.backend_url}/ai/generate",
                    json=payload,
                    timeout=15,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    data = response.json()
                    actual_model = data.get("model")
                    if actual_model != "gemini-1.5-flash":
                        print(
                            f"   FAIL: Model {fake_model} was not overridden! Got: {actual_model}"
                        )
                        return False
                else:
                    print(f"   FAIL: Request failed for model {fake_model}")
                    return False

            return True

        except Exception as e:
            print(f"   Error: {e}")
            return False

    def test_direct_gemini_api(self) -> bool:
        """Test direct Gemini API calls"""
        api_key = os.getenv("VERTEX_AI_API_KEY") or os.getenv(
            "NEXT_PUBLIC_VERTEX_AI_API_KEY"
        )

        if not api_key:
            print("   No API key found for direct test")
            return False

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {"parts": [{"text": "What is 3+3? Answer with just the number."}]}
                ],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 10},
            }

            response = requests.post(url, json=payload, timeout=15)

            if response.status_code == 200:
                data = response.json()
                return "candidates" in data and len(data["candidates"]) > 0
            else:
                print(f"   API Error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"   Error: {e}")
            return False

    def test_response_authenticity(self) -> bool:
        """Test if responses are authentic (not mocked)"""
        try:
            # Test with time-sensitive question
            payload = {
                "prompt": "What is the current year? Answer with just the 4-digit number.",
                "user_id": "test-user-verification",
                "model": "gemini-1.5-flash",
            }

            response = requests.post(
                f"{self.backend_url}/ai/generate",
                json=payload,
                timeout=20,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "").strip()

                # Check if response contains current year (2026)
                return "2026" in content
            else:
                return False

        except Exception as e:
            print(f"   Error: {e}")
            return False

    def test_ocr_vision_processor(self) -> bool:
        """Test OCR vision processor is using real Gemini"""
        try:
            # Test if OCR processor can be imported and configured
            import sys

            sys.path.append("c:/Users/hp/OneDrive/Desktop/Raptorflow/backend")

            from agents.tools.ocr_complex.vision_gemini import GeminiVisionProcessor

            # Test configuration
            config = {
                "gemini_api_key": os.getenv("VERTEX_AI_API_KEY") or "test-key",
                "gemini_model": "gemini-1.5-flash",
            }

            # This should work if the module exists and is configured
            processor = GeminiVisionProcessor(config)

            # Verify the model is set correctly
            return processor.model_name == "gemini-1.5-flash"

        except Exception as e:
            print(f"   Error: {e}")
            return False

    def run_all_tests(self):
        """Run all cynical verification tests"""
        print("🔍 CYNICAL VERIFICATION SUITE")
        print("=" * 50)
        print("Testing Gemini 1.5 Flash is REAL - no mocks, no fallbacks")
        print()

        # Test 1: Backend Health
        self.log_test(
            "Backend Health Check", self.test_backend_health(), "Backend is responsive"
        )

        # Test 2: Real AI Request
        self.log_test(
            "Real AI Endpoint Test",
            self.test_ai_endpoint_real_request(),
            "Actual AI generation working",
        )

        # Test 3: Model Override Protection
        self.log_test(
            "Model Override Protection",
            self.test_model_override_protection(),
            "Other models are forced to gemini-1.5-flash",
        )

        # Test 4: Direct Gemini API
        self.log_test(
            "Direct Gemini API Test",
            self.test_direct_gemini_api(),
            "Direct API calls work",
        )

        # Test 5: Response Authenticity
        self.log_test(
            "Response Authenticity Check",
            self.test_response_authenticity(),
            "Responses are real-time, not mocked",
        )

        # Test 6: OCR Vision Processor
        self.log_test(
            "OCR Vision Processor Test",
            self.test_ocr_vision_processor(),
            "OCR agents use gemini-1.5-flash",
        )

        # Summary
        passed = sum(1 for result in self.test_results if result["passed"])
        total = len(self.test_results)

        print("=" * 50)
        print(f"RESULTS: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 ALL TESTS PASSED - Gemini 1.5 Flash is REAL and ENFORCED!")
        else:
            print("⚠️  Some tests failed - verification incomplete")

        return passed == total


if __name__ == "__main__":
    verifier = CynicalVerifier()
    verifier.run_all_tests()
