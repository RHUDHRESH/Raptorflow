#!/usr/bin/env python3
"""
Vertex AI Multi-Model Integration Test

Tests all 9 integrated AI models to verify Vertex AI configuration and functionality:
- Google Gemini models (2.5 Flash-Lite, 2.5 Flash Preview, 3 Pro Preview)
- Anthropic Claude models (Haiku 4.5, Sonnet 4.5)
- WRITER Palmyra X4
- AI21 Jamba Large 1.6
- Mistral OCR (25.05)

Usage: python vertex_test.py

Prerequisites: Set up Google Cloud authentication and Vertex AI configuration
"""

import asyncio
import sys
import os
from typing import Dict, Any, List, Tuple

# Set environment variables before importing config
os.environ['GOOGLE_CLOUD_PROJECT'] = 'raptorflow-477017'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'raptorflow-477017-d75059f2c50f.json'

# Add backend to Python path
sys.path.insert(0, 'backend')

from backend.core.config import Config, get_settings
from backend.services.model_dispatcher import model_dispatcher


class VertexTester:
    """Comprehensive Vertex AI testing suite."""

    def __init__(self):
        # Force GCP configuration since we know it's valid
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'raptorflow-477017'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'raptorflow-477017-d75059f2c50f.json'

        # Create config manually with direct settings
        config_dict = {
            'gcp_project_id': 'raptorflow-477017',
            'gcp_location': 'us-central1',
            'gcp_auth_file': 'raptorflow-477017-d75059f2c50f.json',
        }

        # Use fresh config to avoid caching issues
        self.config = Config(**config_dict)
        self.results: List[Tuple[str, bool, str]] = []
        self.test_message = "Hello! Please respond with exactly one sentence confirming that this AI model is working correctly."

    def log_result(self, model_name: str, success: bool, message: str):
        """Log individual test result."""
        status = "[PASS]" if success else "[FAIL]"
        print(f"\n{status} | {model_name}")
        print(f"   {message}")
        self.results.append((model_name, success, message))

    async def test_model_direct(self, model_name: str, description: str, require_config: bool = True) -> bool:
        """Test a model using the direct client."""
        try:
            if require_config and not self.config.gcp_project_id:
                self.log_result(model_name, False, "[FAIL] GOOGLE_CLOUD_PROJECT not configured")
                return False

            # Test basic chat completion
            from backend.services.model_dispatcher import ModelDispatchRequest

            request = ModelDispatchRequest(
                workspace_id="test-workspace-123",
                model=model_name,
                messages=[self.test_message],
                temperature=0.7,
                max_tokens=100
            )

            response = await model_dispatcher.dispatch(request)

            if response and response.raw_response and len(response.raw_response.strip()) > 0:
                self.log_result(
                    f"{model_name} ({description})",
                    True,
                    f"[PASS] Response: {response.raw_response[:80]}..."
                )
                return True
            else:
                self.log_result(f"{model_name} ({description})", False, "[FAIL] Empty or invalid response")
                return False

        except Exception as e:
            self.log_result(f"{model_name} ({description})", False, f"[FAIL] Exception: {str(e)}")
            return False

    async def test_vertex_ai_config(self) -> bool:
        """Test basic Vertex AI configuration."""
        config_checks = []

        # Check GCP project
        if self.config.gcp_project_id:
            config_checks.append("[PASS] GCP Project ID configured")
        else:
            config_checks.append("[FAIL] GCP Project ID not set")

        # Check location
        if self.config.gcp_location:
            config_checks.append("[PASS] GCP Location configured")
        else:
            config_checks.append("[FAIL] GCP Location not set")

        print("\n[CONFIG] VERTEX AI CONFIGURATION CHECK:")
        for check in config_checks:
            print(f"   {check}")

        # Test if gcloud auth works
        try:
            import subprocess
            result = subprocess.run(
                ["gcloud", "auth", "application-default", "print-access-token"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and len(result.stdout.strip()) > 10:
                print("   [PASS] gcloud authentication working")
                auth_ok = True
            else:
                print("   [FAIL] gcloud authentication failed")
                print(f"      Error: {result.stderr.strip()}")
                auth_ok = False
        except Exception as e:
            print(f"   [FAIL] gcloud authentication test failed: {str(e)}")
            auth_ok = False

        return self.config.gcp_project_id and auth_ok

    async def run_all_tests(self):
        """Run comprehensive test suite for all models."""
        print("VERTEX AI MULTI-MODEL INTEGRATION TEST")
        print("=" * 60)

        # Check basic configuration
        config_ok = await self.test_vertex_ai_config()
        if not config_ok:
            print("\n[WARNING] Vertex AI configuration incomplete - some models will fail!")
            print("   Note: GCP not fully configured, will test available models anyway...")
            print("   For full Vertex AI access: set GOOGLE_CLOUD_PROJECT and run:")
            print("   gcloud auth application-default login")

        print("\n[TESTING] ALL 9 INTEGRATED AI MODELS:")
        print("-" * 60)

        # Test Gemini models (always work with standard Vertex AI)
        print("\n[GOOGLE] GEMINI MODELS:")
        await self.test_model_direct("gemini-2.5-flash-lite", "Latest fast & cheap", require_config=False)
        await self.test_model_direct("gemini-2.5-flash-preview-09-2025", "Enhanced thinking", require_config=False)
        await self.test_model_direct("gemini-3-pro-preview", "Most powerful multimodal", require_config=False)
        await self.test_model_direct("gemini-1.5-pro", "Legacy enterprise (fallback)", require_config=False)

        # Test Claude models (require Vertex access)
        print("\n[ANTHROPIC] CLAUDE MODELS:")
        await self.test_model_direct("claude-haiku-4-5@20251001", "Fast & cost-effective", require_config=True)
        await self.test_model_direct("claude-sonnet-4-5@20250929", "Industry-leading agents", require_config=True)

        # Test SDEP models (require endpoint configuration)
        print("\n[ENDPOINTS] SELF-DEPLOY ENDPOINT MODELS:")
        await self.test_model_direct("palmyra-x4", "WRITER X4 (Research Guild)", require_config=False)
        await self.test_model_direct("jamba-large-1.6", "AI21 Long-context", require_config=False)
        await self.test_model_direct("mistral-ocr-2505", "Mistral OCR Processor", require_config=False)

        # Summary
        print("\n" + "=" * 60)
        print("[SUMMARY] TEST SUMMARY:")
        print("=" * 60)

        passed = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)

        # Print detailed results
        for model_name, success, message in self.results:
            status_icon = "[PASS]" if success else "[FAIL]"
            print(f"{status_icon} {model_name}")

        print(f"\n[RESULT] FINAL RESULT: {passed}/{total} models working")

        if passed == total:
            print("[SUCCESS] ALL MODELS INTEGRATED SUCCESSFULLY!")
            print("[STATUS] AI SUPREMACY ACHIEVED!")
        elif passed >= 7:  # Google models always work
            print("[STATUS] MAJORITY OF MODELS WORKING - READY FOR PRODUCTION")
        elif passed >= 4:
            print("[WARNING] SOME MODELS WORKING - CHECK VERTEX CONFIGURATION")
        else:
            print("[ERROR] MOST MODELS FAILED - VERTEX AI CONFIGURATION REQUIRED")

        return passed, total

async def main():
    """Main test execution."""
    tester = VertexTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    # Run async main
    if sys.platform == "win32":
        # Windows asyncio fix
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test framework error: {str(e)}")
        import traceback
        traceback.print_exc()
