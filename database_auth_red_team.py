#!/usr/bin/env python3
"""
RED TEAM ASSESSMENT: Database & Authentication Implementation
Cynical verification of multi-tenant isolation and security
"""

import os
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class TestResult:
    test_name: str
    passed: bool
    details: str
    evidence: Optional[str] = None
    severity: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW


class DatabaseAuthRedTeam:
    def __init__(self):
        self.results = []
        self.supabase_path = (
            "c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\supabase\\migrations"
        )
        self.backend_path = "c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\backend"

    def add_result(
        self,
        test_name: str,
        passed: bool,
        details: str,
        evidence: str = None,
        severity: str = "HIGH",
    ):
        self.results.append(TestResult(test_name, passed, details, evidence, severity))
        status = "PASS" if passed else "FAIL"
        severity_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
        print(f"{severity_emoji[severity]} {status}: {test_name} - {details}")
        if evidence:
            print(f"  Evidence: {evidence}")

    def test_rls_policy_completeness(self):
        """Test if RLS policies cover all necessary operations"""

        rls_files = [
            "20240101_users_rls.sql",
            "20240101_workspaces_rls.sql",
            "20240102_foundations_rls.sql",
            "20240103_icp_rls.sql",
        ]

        for rls_file in rls_files:
            file_path = os.path.join(self.supabase_path, rls_file)
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                # Check for missing CRUD operations
                required_operations = ["SELECT", "INSERT", "UPDATE", "DELETE"]
                missing_ops = []

                for op in required_operations:
                    if f"FOR {op}" not in content:
                        missing_ops.append(op)

                if missing_ops:
                    self.add_result(
                        f"RLS policy completeness in {rls_file}",
                        False,
                        f"Missing operations: {', '.join(missing_ops)}",
                        f"File has: {[op for op in required_operations if f'FOR {op}' in content]}",
                        "HIGH",
                    )
                else:
                    self.add_result(
                        f"RLS policy completeness in {rls_file}",
                        True,
                        "All CRUD operations covered",
                        "SELECT, INSERT, UPDATE, DELETE policies found",
                        "LOW",
                    )

            except Exception as e:
                self.add_result(
                    f"RLS policy completeness in {rls_file}",
                    False,
                    f"Error reading file: {str(e)}",
                    "CRITICAL",
                )

    def test_workspace_isolation_gaps(self):
        """Test for potential gaps in workspace isolation"""

        critical_files = ["20240102_foundations.sql", "20240103_icp_profiles.sql"]

        for file_name in critical_files:
            file_path = os.path.join(self.supabase_path, file_name)
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                # Check for workspace_id in all constraints
                if "workspace_id" not in content:
                    self.add_result(
                        f"Workspace isolation in {file_name}",
                        False,
                        "workspace_id column missing",
                        "No workspace_id column found",
                        "CRITICAL",
                    )

                # Check for missing workspace_id in indexes
                if "CREATE INDEX" in content and "workspace_id" not in content:
                    self.add_result(
                        f"Workspace indexing in {file_name}",
                        False,
                        "Missing workspace_id in indexes",
                        "Indexes don't include workspace_id",
                        "HIGH",
                    )

                # Check for potential data leakage vectors
                if "public." in content and "workspace_id" not in content:
                    self.add_result(
                        f"Public access risk in {file_name}",
                        False,
                        "Public table without workspace isolation",
                        "Public table without workspace_id filter",
                        "CRITICAL",
                    )

            except Exception as e:
                self.add_result(
                    f"Workspace isolation in {file_name}",
                    False,
                    f"Error reading file: {str(e)}",
                    "CRITICAL",
                )

    def test_authentication_edge_cases(self):
        """Test for authentication edge cases that could bypass isolation"""

        auth_files = ["core/auth.py", "core/middleware.py"]

        for file_name in auth_files:
            file_path = os.path.join(self.backend_path, file_name)
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                # Check for missing workspace validation
                if "get_workspace_id" not in content:
                    self.add_result(
                        f"Authentication validation in {file_name}",
                        False,
                        "Missing workspace validation",
                        "get_workspace_id function not found",
                        "HIGH",
                    )

                # Check for potential bypass patterns
                bypass_patterns = [
                    ("admin", "Admin bypass potential"),
                    ("root", "Root bypass potential"),
                    ("super", "Super user bypass potential"),
                    ("override", "Override bypass potential"),
                ]

                for pattern, description in bypass_patterns:
                    if pattern in content.lower():
                        self.add_result(
                            f"Authentication bypass risk in {file_name}",
                            False,
                            description,
                            f"Pattern '{pattern}' found",
                            "MEDIUM",
                        )

                # Check for hardcoded workspace IDs
                if "workspace_id" in content and any(
                    char.isdigit() for char in content
                ):
                    self.add_result(
                        f"Hardcoded workspace risk in {file_name}",
                        False,
                        "Potential hardcoded workspace ID",
                        "Digits found in workspace_id context",
                        "MEDIUM",
                    )

            except Exception as e:
                self.add_result(
                    f"Authentication edge cases in {file_name}",
                    False,
                    f"Error reading file: {str(e)}",
                    "CRITICAL",
                )

    def test_repository_isolation_completeness(self):
        """Test if repository base class has complete isolation"""

        base_file = os.path.join(self.backend_path, "db/base.py")
        try:
            with open(base_file, "r") as f:
                content = f.read()

            # Check all repository methods for workspace filtering
            methods_to_check = [
                ("get", "workspace_filter(workspace_id)"),
                ("list", "workspace_filter(workspace_id)"),
                ("create", 'data["workspace_id"] = workspace_id'),
                ("update", "workspace_filter(workspace_id)"),
                ("delete", "workspace_filter(workspace_id)"),
                ("count", "workspace_filter(workspace_id)"),
            ]

            missing_methods = []
            for method_name, pattern in methods_to_check:
                if pattern not in content:
                    missing_methods.append(method_name)

            if missing_methods:
                self.add_result(
                    "Repository isolation completeness",
                    False,
                    f"Missing workspace filtering in: {', '.join(missing_methods)}",
                    f"Methods missing workspace_filter",
                    "CRITICAL",
                )
            else:
                self.add_result(
                    "Repository isolation completeness",
                    True,
                    "All methods enforce workspace filtering",
                    "6 methods with workspace_filter found",
                    "LOW",
                )

        except Exception as e:
            self.add_result(
                "Repository isolation completeness",
                False,
                f"Error reading base.py: {str(e)}",
                "CRITICAL",
            )

    def test_database_trigger_security(self):
        """Test if database triggers have security implications"""

        trigger_file = os.path.join(self.supabase_path, "20240101_users_workspaces.sql")
        try:
            with open(trigger_file, "r") as f:
                content = f.read()

            # Check for SQL injection risks in triggers
            if "EXECUTE" in content or "dynamic" in content:
                self.add_result(
                    "Database trigger security",
                    False,
                    "Potential SQL injection in triggers",
                    "EXECUTE or dynamic SQL found",
                    "HIGH",
                )

            # Check for privilege escalation
            if "SECURITY DEFINER" in content:
                self.add_result(
                    "Database trigger security",
                    False,
                    "High privilege triggers",
                    "SECURITY DEFINER found - potential privilege escalation",
                    "MEDIUM",
                )

            # Check for proper error handling
            if "EXCEPTION" not in content and "RAISE" not in content:
                self.add_result(
                    "Database trigger security",
                    False,
                    "Missing error handling in triggers",
                    "No error handling found",
                    "MEDIUM",
                )
            else:
                self.add_result(
                    "Database trigger security",
                    True,
                    "Triggers have error handling",
                    "EXCEPTION or RAISE found",
                    "LOW",
                )

        except Exception as e:
            self.add_result(
                "Database trigger security",
                False,
                f"Error reading trigger file: {str(e)}",
                "CRITICAL",
            )

    def test_cross_workspace_data_leak_vectors(self):
        """Test for potential cross-workspace data leak vectors"""

        # Check for any files that might leak data across workspaces
        leak_vectors = [
            ("db/base.py", "Repository base"),
            ("core/auth.py", "Authentication"),
            ("core/middleware.py", "Middleware"),
            ("core/supabase.py", "Supabase client"),
        ]

        for file_name, description in leak_vectors:
            file_path = os.path.join(self.backend_path, file_name)
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                # Check for missing workspace context
                if "workspace_id" not in content:
                    self.add_result(
                        f"Data leak vector in {description}",
                        False,
                        "Missing workspace context",
                        f"{file_name} doesn't reference workspace_id",
                        "CRITICAL",
                    )

                # Check for potential cross-workspace queries
                if "SELECT *" in content and "WHERE workspace_id" not in content:
                    self.add_result(
                        f"Data leak vector in {description}",
                        False,
                        "Potential cross-workspace query",
                        "SELECT * without WHERE workspace_id",
                        "HIGH",
                    )

                # Check for admin bypass patterns
                if "admin" in content.lower() and "workspace_id" not in content:
                    self.add_result(
                        f"Data leak vector in {description}",
                        False,
                        "Admin bypass potential",
                        "Admin access without workspace filtering",
                        "HIGH",
                    )

            except Exception as e:
                self.add_result(
                    f"Data leak vector in {description}",
                    False,
                    f"Error reading file: {str(e)}",
                    "CRITICAL",
                )

    def test_environment_variable_security(self):
        """Test for environment variable security issues"""

        # Check for hardcoded secrets in code
        secret_patterns = [
            ("password", "Hardcoded password"),
            ("secret", "Hardcoded secret"),
            ("key", "Hardcoded key"),
            ("token", "Hardcoded token"),
            ("api_key", "Hardcoded API key"),
        ]

        for root, dirs, files in os.walk(self.backend_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        for pattern, description in secret_patterns:
                            if pattern in content.lower():
                                self.add_result(
                                    f"Secret security in {file_path}",
                                    False,
                                    description,
                                    f"Pattern '{pattern}' found in code",
                                    "HIGH",
                                )
                    except:
                        pass

    def test_sql_injection_prevention(self):
        """Test if SQL injection prevention is implemented"""

        sql_injection_patterns = [
            ("DROP TABLE", "DROP TABLE injection"),
            ("DELETE FROM", "DELETE FROM injection"),
            ("INSERT INTO", "INSERT INTO injection"),
            ("UPDATE SET", "UPDATE SET injection"),
            ("UNION SELECT", "UNION SELECT injection"),
            ("';", "SQL injection with comment"),
            ("--", "SQL comment injection"),
        ]

        # Check in authentication and repository files
        files_to_check = ["core/auth.py", "db/base.py"]

        for file_name in files_to_check:
            file_path = os.path.join(self.backend_path, file_name)
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                for pattern, description in sql_injection_patterns:
                    if pattern in content:
                        self.add_result(
                            f"SQL injection prevention in {file_name}",
                            False,
                            description,
                            f"SQL pattern '{pattern}' found",
                            "HIGH",
                        )

            except Exception as e:
                self.add_result(
                    f"SQL injection prevention in {file_name}",
                    False,
                    f"Error reading file: {str(e)}",
                    "CRITICAL",
                )

    def run_red_team_assessment(self):
        """Run complete red team assessment of database and auth"""

        print("🔴 RED TEAM ASSESSMENT: Database & Authentication")
        print("=" * 60)
        print("Cynical verification of multi-tenant isolation security")
        print()

        # Run all tests
        self.test_rls_policy_completeness()
        self.test_workspace_isolation_gaps()
        self.test_authentication_edge_cases()
        self.test_repository_isolation_completeness()
        self.test_database_trigger_security()
        self.test_cross_workspace_data_leak_vectors()
        self.test_environment_variable_security()
        self.test_sql_injection_prevention()

        # Generate summary
        critical_count = sum(1 for r in self.results if r.severity == "CRITICAL")
        high_count = sum(1 for r in self.results if r.severity == "HIGH")
        medium_count = sum(1 for r in self.results if r.severity == "MEDIUM")
        low_count = sum(1 for r in self.results if r.severity == "LOW")

        print("=" * 60)
        print("📊 RED TEAM ASSESSMENT SUMMARY")
        print(f"🔴 Critical: {critical_count}")
        print(f"🟠 High: {high_count}")
        print(f"🟡 Medium: {medium_count}")
        print(f"🟢 Low: {low_count}")
        print(f"Total: {len(self.results)} issues found")

        # Critical vulnerabilities first
        critical_issues = [r for r in self.results if r.severity == "CRITICAL"]
        if critical_issues:
            print("\n🚨 CRITICAL ISSUES (must fix immediately):")
            for issue in critical_issues:
                print(f"  - {issue.test_name}: {issue.details}")

        # High severity issues
        high_issues = [r for r in self.results if r.severity == "HIGH"]
        if high_issues:
            print("\n⚠️ HIGH SEVERITY ISSUES:")
            for issue in high_issues:
                print(f"  - {issue.test_name}: {issue.details}")

        # Overall assessment
        total_issues = len(self.results)
        if total_issues == 0:
            print(
                "\n🎉 NO SECURITY ISSUES FOUND - Database & Auth implementation is secure!"
            )
            return True
        elif critical_count == 0:
            print(f"\n⚠️  {total_issues} non-critical issues found - Review recommended")
            return False
        else:
            print(f"\n🚨  {total_issues} issues found - IMMEDIATE ACTION REQUIRED")
            return False


if __name__ == "__main__":
    red_team = DatabaseAuthRedTeam()
    success = red_team.run_red_team_assessment()

    if not success:
        print("\n" + "=" * 60)
        print("🔧 RECOMMENDED ACTIONS:")
        print("1. Fix all CRITICAL issues immediately")
        print("2. Review and fix HIGH severity issues")
        print("3. Test fixes with real data")
        print("4. Implement additional security measures")
        print("5. Run assessment again to verify fixes")
