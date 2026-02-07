"""
Security Test Runner for Raptorflow Payment System
Coordinates load testing and penetration testing
"""

import pytest

pytest.skip(
    "Archived manual test script; use explicit run if needed.", allow_module_level=True
)

import asyncio
import json
import sys
from datetime import datetime
from typing import Any, Dict

from load_test import LoadTestRunner
from penetration_test import PaymentPenetrationTester


class SecurityTestRunner:
    """Main security testing coordinator"""

    def __init__(self, base_url: str, auth_token: str = None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.results = {}

    async def run_all_tests(self):
        """Run complete security test suite"""
        print("Starting comprehensive security testing...")

        # Load Testing
        print("\n1. Running Load Tests...")
        load_runner = LoadTestRunner(self.base_url)
        self.results["load_test"] = {
            "standard": load_runner.run_load_test(num_users=10, duration=60),
            "stress": load_runner.run_stress_test(num_users=20, duration=30),
        }

        # Penetration Testing
        print("\n2. Running Penetration Tests...")
        pen_tester = PaymentPenetrationTester(self.base_url, self.auth_token)
        self.results["penetration_test"] = await pen_tester.run_comprehensive_test()

        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate comprehensive security report"""
        report = {
            "test_date": datetime.now().isoformat(),
            "target": self.base_url,
            "load_test_results": self.results["load_test"],
            "penetration_test_results": self.results["penetration_test"],
        }

        with open("security_test_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(
            f"\nSecurity testing completed. Report saved to security_test_report.json"
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python security_test_runner.py <base_url> [auth_token]")
        sys.exit(1)

    runner = SecurityTestRunner(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    asyncio.run(runner.run_all_tests())
