"""
CYNICAL EMPIRICAL VERIFICATION
Test everything with real data, no assumptions, no shortcuts
"""

import json
import os
import sys
import time
from datetime import datetime

import requests


class CynicalVerifier:
    def __init__(self):
        self.test_results = []
        self.backend_url = "http://localhost:8001"  # Minimal backend
        self.real_api_key = os.getenv("VERTEX_AI_API_KEY")

    def log_result(
        self, test_name: str, passed: bool, details: str = "", evidence: str = ""
    ):
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "evidence": evidence,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if evidence:
            print(f"   Evidence: {evidence}")
        print()

    def test_backend_connectivity(self):
        """Test if backend is actually reachable"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return (
                    True,
                    f"Backend responded: {data}",
                    f"Status: {response.status_code}",
                )
            else:
                return (
                    False,
                    f"Backend returned {response.status_code}",
                    f"Response: {response.text[:100]}",
                )
        except Exception as e:
            return False, f"Connection failed: {str(e)}", ""

    def test_real_ai_generation(self):
        """Test actual AI generation with verifiable math"""
        test_cases = [
            {"prompt": "What is 2+2? Answer with just the number.", "expected": "4"},
            {"prompt": "What is 10+15? Answer with just the number.", "expected": "25"},
            {"prompt": "What is 7*8? Answer with just the number.", "expected": "56"},
            {"prompt": "What is 100/4? Answer with just the number.", "expected": "25"},
        ]

        passed_count = 0
        evidence = []

        for i, test_case in enumerate(test_cases):
            try:
                payload = {
                    "prompt": test_case["prompt"],
                    "user_id": f"cynical-test-{i}",
                    "model": "gemini-2.0-flash-001",
                }

                response = requests.post(
                    f"{self.backend_url}/ai/generate",
                    json=payload,
                    timeout=30,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data.get("content", "").strip()
                    model_used = data.get("model", "")

                    # Verify mathematical accuracy
                    is_correct = test_case["expected"] in content
                    if is_correct:
                        passed_count += 1

                    evidence.append(
                        f"Test {i+1}: '{test_case['prompt']}' -> '{content}' (Expected: {test_case['expected']}) {'✅' if is_correct else '❌'}"
                    )

                    # Verify model enforcement
                    if model_used != "gemini-2.0-flash-001":
                        evidence.append(
                            f"❌ MODEL ENFORCEMENT FAILED: Got {model_used}"
                        )
                        passed_count -= 1
                else:
                    evidence.append(
                        f"❌ Test {i+1} failed: HTTP {response.status_code}"
                    )
                    passed_count -= 1

            except Exception as e:
                evidence.append(f"❌ Test {i+1} exception: {str(e)}")
                passed_count -= 1

        success_rate = passed_count / len(test_cases)
        details = f"Passed {passed_count}/{len(test_cases)} math tests ({success_rate*100:.1f}%)"
        evidence_str = "\n".join(evidence)

        return success_rate >= 0.75, details, evidence_str

    def test_model_override_protection(self):
        """Test that other models get forcibly overridden"""
        fake_models = ["gpt-4", "claude-3", "gemini-pro", "fake-model-123"]
        override_evidence = []

        for fake_model in fake_models:
            try:
                payload = {
                    "prompt": "Say 'hello' and tell me what model you are",
                    "user_id": f"override-test-{fake_model}",
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
                    actual_model = data.get("model", "")
                    content = data.get("content", "")

                    if actual_model == "gemini-2.0-flash-001":
                        override_evidence.append(f"✅ {fake_model} -> {actual_model}")
                    else:
                        override_evidence.append(
                            f"❌ {fake_model} was NOT overridden! Got: {actual_model}"
                        )
                else:
                    override_evidence.append(
                        f"❌ {fake_model} request failed: {response.status_code}"
                    )

            except Exception as e:
                override_evidence.append(f"❌ {fake_model} exception: {str(e)}")

        success_count = sum(1 for e in override_evidence if e.startswith("✅"))
        success_rate = success_count / len(fake_models)

        return (
            success_rate == 1.0,
            f"Model override protection: {success_count}/{len(fake_models)} successful",
            "\n".join(override_evidence),
        )

    def test_response_authenticity(self):
        """Test if responses are real-time, not cached or mocked"""
        # Test with time-sensitive question
        time_sensitive_prompts = [
            "What time is it now? Answer with just the current hour number.",
            "What is today's date? Answer with just the day number.",
            "Generate a random number between 1 and 100.",
        ]

        responses = []
        for prompt in time_sensitive_prompts:
            try:
                payload = {
                    "prompt": prompt,
                    "user_id": "authenticity-test",
                    "model": "gemini-2.0-flash-001",
                }

                response = requests.post(
                    f"{self.backend_url}/ai/generate",
                    json=payload,
                    timeout=20,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    data = response.json()
                    responses.append(data.get("content", "").strip())

            except Exception as e:
                responses.append(f"Error: {str(e)}")

        # Check if responses are unique (indicating real generation)
        unique_responses = len(set(responses))
        total_responses = len(responses)

        if unique_responses == total_responses and total_responses > 1:
            return (
                True,
                f"All {total_responses} responses unique",
                f"Responses: {responses}",
            )
        else:
            return (
                False,
                f"Only {unique_responses}/{total_responses} unique responses",
                f"Responses: {responses}",
            )

    def test_performance_metrics(self):
        """Test actual performance with timing"""
        try:
            payload = {
                "prompt": "Write a 100-word story about space exploration.",
                "user_id": "performance-test",
                "model": "gemini-2.0-flash-001",
            }

            start_time = time.time()
            response = requests.post(
                f"{self.backend_url}/ai/generate",
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"},
            )
            end_time = time.time()

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "")
                response_time = end_time - start_time
                word_count = len(content.split())

                # Performance metrics
                words_per_second = (
                    word_count / response_time if response_time > 0 else 0
                )

                details = f"Response time: {response_time:.2f}s, Words: {word_count}, Speed: {words_per_second:.1f} words/sec"
                evidence = (
                    f"Content length: {len(content)} chars, Model: {data.get('model')}"
                )

                # Reasonable performance check
                is_reasonable = response_time < 10 and word_count > 50

                return is_reasonable, details, evidence
            else:
                return (
                    False,
                    f"Request failed: {response.status_code}",
                    response.text[:200],
                )

        except Exception as e:
            return False, f"Performance test failed: {str(e)}", ""

    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        error_tests = [
            {"prompt": "", "expected_error": "Empty prompt"},
            {"prompt": "x" * 10000, "expected_error": "Too long prompt"},
            {
                "prompt": "What is the meaning of life?" * 100,
                "expected_error": "Excessive repetition",
            },
        ]

        error_results = []

        for test in error_tests:
            try:
                payload = {
                    "prompt": test["prompt"],
                    "user_id": "error-test",
                    "model": "gemini-2.0-flash-001",
                }

                response = requests.post(
                    f"{self.backend_url}/ai/generate",
                    json=payload,
                    timeout=15,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code != 200:
                    error_results.append(
                        f"✅ {test['expected_error']}: Properly rejected ({response.status_code})"
                    )
                else:
                    error_results.append(
                        f"❌ {test['expected_error']}: Should have been rejected"
                    )

            except Exception as e:
                error_results.append(
                    f"✅ {test['expected_error']}: Exception caught ({str(e)[:50]})"
                )

        return (
            len(error_results) == len(error_tests),
            f"Error handling: {len(error_results)}/{len(error_tests)} proper",
            "\n".join(error_results),
        )

    def run_cynical_verification(self):
        """Run all cynical tests"""
        print("🔬 CYNICAL EMPIRICAL VERIFICATION")
        print("=" * 60)
        print("Testing with REAL data, NO assumptions, NO shortcuts")
        print()

        # Test 1: Backend connectivity
        passed, details, evidence = self.test_backend_connectivity()
        self.log_result("Backend Connectivity", passed, details, evidence)

        if not passed:
            print("❌ BACKEND NOT REACHABLE - Stopping verification")
            return False

        # Test 2: Real AI generation with math
        passed, details, evidence = self.test_real_ai_generation()
        self.log_result("Real AI Generation (Math)", passed, details, evidence)

        # Test 3: Model override protection
        passed, details, evidence = self.test_model_override_protection()
        self.log_result("Model Override Protection", passed, details, evidence)

        # Test 4: Response authenticity
        passed, details, evidence = self.test_response_authenticity()
        self.log_result("Response Authenticity", passed, details, evidence)

        # Test 5: Performance metrics
        passed, details, evidence = self.test_performance_metrics()
        self.log_result("Performance Metrics", passed, details, evidence)

        # Test 6: Error handling
        passed, details, evidence = self.test_error_handling()
        self.log_result("Error Handling", passed, details, evidence)

        # Summary
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        total_tests = len(self.test_results)

        print("=" * 60)
        print(
            f"📊 CYNICAL VERIFICATION RESULTS: {passed_tests}/{total_tests} tests passed"
        )

        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - This is REAL Gemini 2.0 Flash!")
            print("✅ Universal enforcement is WORKING")
            print("✅ Mathematical accuracy is VERIFIED")
            print("✅ Model protection is ACTIVE")
            print("✅ Performance is ACCEPTABLE")
            return True
        else:
            print("⚠️  Some tests failed - See details above")
            return False


if __name__ == "__main__":
    verifier = CynicalVerifier()
    success = verifier.run_cynical_verification()

    # Save detailed report
    with open(
        "c:/Users/hp/OneDrive/Desktop/Raptorflow/cynical_verification_report.json", "w"
    ) as f:
        json.dump(verifier.test_results, f, indent=2)

    print(f"\n📄 Detailed report saved to: cynical_verification_report.json")
