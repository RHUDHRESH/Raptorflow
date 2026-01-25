#!/usr/bin/env python3
"""
Complete integration test for Raptorflow with BCM, Tools, and Agents
"""

import json
import time
from datetime import datetime

import requests


class RaptorflowIntegrationTester:
    def __init__(self):
        self.base_url = "http://localhost:3000/api/proxy"
        self.test_results = {}
        self.workspace_id = "test-workspace"
        self.user_id = "test-user"

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    def test_endpoint(
        self, name, method, path, data=None, expected_status=200, show_response=False
    ):
        """Test a single endpoint"""
        try:
            url = f"{self.base_url}{path}"

            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "PUT":
                response = requests.put(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url)

            success = response.status_code == expected_status
            self.test_results[name] = {
                "success": success,
                "status": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "data": response.json() if success and response.content else None,
            }

            status_icon = "✅" if success else "❌"
            self.log(
                f"{status_icon} {name} - {response.status_code} ({response.elapsed.total_seconds():.2f}s)"
            )

            if success and show_response:
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")

            return success

        except Exception as e:
            self.test_results[name] = {"success": False, "error": str(e), "status": 0}
            self.log(f"❌ {name} - Error: {str(e)}")
            return False

    def test_core_systems(self):
        """Test all core Raptorflow systems"""
        self.log("🚀 Testing Core Raptorflow Systems")

        # Moves System
        self.test_endpoint("Moves - List", "GET", "/api/v1/moves/")
        self.test_endpoint(
            "Moves - Create",
            "POST",
            "/api/v1/moves/",
            {
                "name": "Integration Test Move",
                "focusArea": "Testing",
                "desiredOutcome": "Verify integration",
                "volatilityLevel": 3,
                "steps": ["Setup", "Test", "Verify"],
            },
            show_response=True,
        )

        # Campaigns System
        self.test_endpoint("Campaigns - List", "GET", "/api/v1/campaigns/")
        self.test_endpoint(
            "Campaigns - Create",
            "POST",
            "/api/v1/campaigns/",
            {
                "name": "Integration Test Campaign",
                "description": "Testing full integration",
                "target_icps": ["test-icp"],
            },
            show_response=True,
        )

        # Daily Wins System
        self.test_endpoint("Daily Wins - List", "GET", "/api/v1/daily_wins/")
        self.test_endpoint(
            "Daily Wins - Generate",
            "POST",
            "/api/v1/daily_wins/generate",
            {
                "workspace_id": self.workspace_id,
                "user_id": self.user_id,
                "platform": "LinkedIn",
            },
            show_response=True,
        )

        # Blackbox System
        self.test_endpoint(
            "Blackbox - List Strategies", "GET", "/api/v1/blackbox/strategies"
        )
        self.test_endpoint(
            "Blackbox - Generate Strategy",
            "POST",
            "/api/v1/blackbox/generate-strategy",
            {
                "focus_area": "integration_testing",
                "business_context": "Testing complete system integration",
                "workspace_id": self.workspace_id,
                "user_id": self.user_id,
            },
            show_response=True,
        )

        # Muse System
        self.test_endpoint("Muse - List Assets", "GET", "/api/v1/muse/assets")
        self.test_endpoint(
            "Muse - Generate Content",
            "POST",
            "/api/v1/muse/generate",
            {
                "prompt": "Create content about system integration",
                "platform": "blog",
                "workspace_id": self.workspace_id,
                "user_id": self.user_id,
            },
            show_response=True,
        )
        self.test_endpoint(
            "Muse - Chat",
            "POST",
            "/api/v1/muse/chat",
            {
                "message": "Help me understand system integration",
                "workspace_id": self.workspace_id,
                "user_id": self.user_id,
            },
        )

    def test_bcm_system(self):
        """Test Business Context Management"""
        self.log("🧠 Testing BCM (Business Context Management)")

        self.test_endpoint("BCM - Get Context", "GET", "/api/v1/bcm/context")
        self.test_endpoint("BCM - Get Evolution", "GET", "/api/v1/bcm/evolution")
        self.test_endpoint(
            "BCM - Record Interaction",
            "POST",
            "/api/v1/bcm/record-interaction",
            {
                "agent": "integration_tester",
                "action": "complete_system_test",
                "context": {
                    "test_timestamp": datetime.now().isoformat(),
                    "systems_tested": [
                        "moves",
                        "campaigns",
                        "daily_wins",
                        "blackbox",
                        "muse",
                    ],
                },
            },
            show_response=True,
        )

    def test_tools_and_services(self):
        """Test tools and services"""
        self.log("🔧 Testing Tools and Services")

        self.test_endpoint("Tools - Available", "GET", "/api/v1/tools/available")
        self.test_endpoint("Services - Status", "GET", "/api/v1/services/status")

    def test_agents_system(self):
        """Test agent system"""
        self.log("🤖 Testing Agent System")

        self.test_endpoint("Agents - Available", "GET", "/api/v1/agents/available")
        self.test_endpoint(
            "Agents - Execute Muse",
            "POST",
            "/api/v1/agents/muse/execute",
            {
                "task": "Generate integration summary",
                "context": {
                    "bcm_context": "integration_testing",
                    "user_request": "Complete system verification",
                },
            },
            show_response=True,
        )
        self.test_endpoint(
            "Agents - Execute Blackbox",
            "POST",
            "/api/v1/agents/blackbox/execute",
            {
                "task": "Analyze integration results",
                "context": {"test_results": self.test_results, "bcm_stage": "growth"},
            },
            show_response=True,
        )

    def test_analytics_system(self):
        """Test analytics system"""
        self.log("📊 Testing Analytics System")

        self.test_endpoint(
            "Analytics - Dashboard", "GET", "/api/v1/analytics/dashboard"
        )

    def test_cross_system_integration(self):
        """Test cross-system integration"""
        self.log("🔗 Testing Cross-System Integration")

        # Test creating a move from Blackbox strategy
        self.test_endpoint(
            "Integration - Move from Strategy",
            "POST",
            "/api/v1/blackbox/test-strategy/create-move",
        )

        # Test completing a daily win
        self.test_endpoint(
            "Integration - Complete Daily Win",
            "POST",
            "/api/v1/daily_wins/test-win/complete",
        )

        # Test saving a Muse asset
        self.test_endpoint(
            "Integration - Save Muse Asset",
            "POST",
            "/api/v1/muse/assets",
            {
                "title": "Integration Test Asset",
                "content": "This asset was created during integration testing",
                "platform": "blog",
            },
        )

    def run_comprehensive_test(self):
        """Run the complete integration test suite"""
        self.log("🎯 Starting Comprehensive Raptorflow Integration Test")
        self.log("=" * 60)

        start_time = time.time()

        # Test all systems
        self.test_core_systems()
        self.test_bcm_system()
        self.test_tools_and_services()
        self.test_agents_system()
        self.test_analytics_system()
        self.test_cross_system_integration()

        end_time = time.time()
        total_time = end_time - start_time

        # Generate summary
        self.log("=" * 60)
        self.log("🎯 INTEGRATION TEST SUMMARY")
        self.log("=" * 60)

        total_tests = len(self.test_results)
        successful_tests = sum(
            1 for result in self.test_results.values() if result["success"]
        )
        failed_tests = total_tests - successful_tests

        self.log(f"Total Tests: {total_tests}")
        self.log(f"Successful: {successful_tests} ✅")
        self.log(f"Failed: {failed_tests} ❌")
        self.log(f"Success Rate: {(successful_tests/total_tests*100):.1f}%")
        self.log(f"Total Time: {total_time:.2f} seconds")

        # Show failed tests if any
        if failed_tests > 0:
            self.log("\n❌ Failed Tests:")
            for name, result in self.test_results.items():
                if not result["success"]:
                    self.log(f"   {name}: {result.get('error', 'Unknown error')}")

        # Show system health
        self.log("\n🏥 System Health:")
        systems = {
            "Core Systems": [
                "Moves - List",
                "Moves - Create",
                "Campaigns - List",
                "Campaigns - Create",
                "Daily Wins - List",
                "Daily Wins - Generate",
                "Blackbox - List Strategies",
                "Blackbox - Generate Strategy",
                "Muse - List Assets",
                "Muse - Generate Content",
            ],
            "BCM System": [
                "BCM - Get Context",
                "BCM - Get Evolution",
                "BCM - Record Interaction",
            ],
            "Tools & Services": ["Tools - Available", "Services - Status"],
            "Agent System": [
                "Agents - Available",
                "Agents - Execute Muse",
                "Agents - Execute Blackbox",
            ],
            "Analytics": ["Analytics - Dashboard"],
            "Cross-Integration": [
                "Integration - Move from Strategy",
                "Integration - Complete Daily Win",
                "Integration - Save Muse Asset",
            ],
        }

        for system_name, test_names in systems.items():
            system_success = sum(
                1
                for name in test_names
                if self.test_results.get(name, {}).get("success")
            )
            system_total = len(test_names)
            status = (
                "✅ HEALTHY"
                if system_success == system_total
                else "⚠️  DEGRADED" if system_success > 0 else "❌ FAILED"
            )
            self.log(f"   {system_name}: {status} ({system_success}/{system_total})")

        # Final verdict
        self.log("=" * 60)
        if successful_tests == total_tests:
            self.log("🎉 ALL SYSTEMS INTEGRATED SUCCESSFULLY!")
            self.log("🚀 Raptorflow is ready for production with full BCM integration!")
            self.log("\n📋 What's Working:")
            self.log(
                "   ✅ All core systems (Moves, Campaigns, Daily Wins, Blackbox, Muse)"
            )
            self.log("   ✅ Business Context Management (BCM)")
            self.log("   ✅ Tools and Services integration")
            self.log("   ✅ Agent system with BCM context")
            self.log("   ✅ Analytics and insights")
            self.log("   ✅ Cross-system data flow")
            self.log("\n🔗 Architecture:")
            self.log("   Frontend (localhost:3000) → Proxy → Backend (localhost:8000)")
            self.log("   All systems connected with BCM context awareness")
        else:
            self.log("⚠️  INTEGRATION COMPLETE WITH ISSUES")
            self.log("🔧 Some systems need attention - see failed tests above")

        self.log(f"\n⏱️  Test completed in {total_time:.2f} seconds")

        return successful_tests == total_tests


if __name__ == "__main__":
    tester = RaptorflowIntegrationTester()
    success = tester.run_comprehensive_test()

    # Exit with appropriate code
    exit(0 if success else 1)
