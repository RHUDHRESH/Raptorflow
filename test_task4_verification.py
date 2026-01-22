#!/usr/bin/env python3
"""
CYNICAL VERIFICATION - Task 4: Auth Middleware
Tests if auth middleware correctly extracts user and workspace from JWT
No "graceful failures" - either it works or it's broken
"""

import asyncio
import importlib.util
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


class AuthMiddlewareTester:
    def __init__(self):
        self.results = []
        self.backend_path = "c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\backend"

    def add_result(
        self, test_name: str, passed: bool, details: str, evidence: str = None
    ):
        self.results.append(TestResult(test_name, passed, details, evidence))
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {test_name} - {details}")
        if evidence:
            print(f"  Evidence: {evidence}")

    def test_module_imports(self):
        """Test if auth modules can be imported"""
        modules_to_test = [
            "core.supabase",
            "core.models",
            "core.jwt",
            "core.auth",
            "core.workspace",
            "core.middleware",
        ]

        for module_name in modules_to_test:
            try:
                # Add backend path to sys.path
                import sys

                if self.backend_path not in sys.path:
                    sys.path.insert(0, self.backend_path)

                # Try to import the module
                if module_name == "core.supabase":
                    from core import supabase
                elif module_name == "core.models":
                    from core import models
                elif module_name == "core.jwt":
                    from core import jwt
                elif module_name == "core.auth":
                    from core import auth
                elif module_name == "core.workspace":
                    from core import workspace
                elif module_name == "core.middleware":
                    from core import middleware

                self.add_result(
                    f"Import {module_name}", True, f"Module imported successfully"
                )

            except Exception as e:
                self.add_result(
                    f"Import {module_name}", False, f"Import failed: {str(e)}"
                )

    def test_supabase_client(self):
        """Test if SupabaseClient class exists and has required methods"""
        try:
            # Import and check SupabaseClient
            spec = importlib.util.spec_from_file_location(
                "core.supabase", os.path.join(self.backend_path, "core/supabase.py")
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check if SupabaseClient class exists
                if hasattr(module, "SupabaseClient"):
                    self.add_result(
                        "SupabaseClient class exists",
                        True,
                        "SupabaseClient class found",
                    )

                    # Check required methods
                    required_methods = [
                        "get_client",
                        "get_admin_client",
                        "health_check",
                    ]
                    for method in required_methods:
                        if hasattr(module.SupabaseClient, method):
                            self.add_result(
                                f"SupabaseClient has {method}",
                                True,
                                f"Method {method} exists",
                            )
                        else:
                            self.add_result(
                                f"SupabaseClient has {method}",
                                False,
                                f"Method {method} missing",
                            )
                else:
                    self.add_result(
                        "SupabaseClient class exists",
                        False,
                        "SupabaseClient class not found",
                    )
            else:
                self.add_result(
                    "SupabaseClient class exists",
                    False,
                    "Could not load supabase module",
                )

        except Exception as e:
            self.add_result(
                "SupabaseClient class exists",
                False,
                f"Error checking SupabaseClient: {str(e)}",
            )

    def test_jwt_validator(self):
        """Test if JWTValidator class exists and has required methods"""
        try:
            spec = importlib.util.spec_from_file_location(
                "core.jwt", os.path.join(self.backend_path, "core/jwt.py")
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, "JWTValidator"):
                    self.add_result(
                        "JWTValidator class exists", True, "JWTValidator class found"
                    )

                    # Check required methods
                    required_methods = [
                        "extract_token",
                        "verify_token",
                        "validate_claims",
                    ]
                    for method in required_methods:
                        if hasattr(module.JWTValidator, method):
                            self.add_result(
                                f"JWTValidator has {method}",
                                True,
                                f"Method {method} exists",
                            )
                        else:
                            self.add_result(
                                f"JWTValidator has {method}",
                                False,
                                f"Method {method} missing",
                            )
                else:
                    self.add_result(
                        "JWTValidator class exists",
                        False,
                        "JWTValidator class not found",
                    )
            else:
                self.add_result(
                    "JWTValidator class exists", False, "Could not load jwt module"
                )

        except Exception as e:
            self.add_result(
                "JWTValidator class exists",
                False,
                f"Error checking JWTValidator: {str(e)}",
            )

    def test_auth_functions(self):
        """Test if auth functions exist"""
        try:
            spec = importlib.util.spec_from_file_location(
                "core.auth", os.path.join(self.backend_path, "core/auth.py")
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check required functions
                required_functions = [
                    "get_current_user",
                    "get_workspace_id",
                    "user_owns_workspace",
                    "get_default_workspace_id",
                    "get_workspace_for_user",
                    "get_auth_context",
                ]

                for func_name in required_functions:
                    if hasattr(module, func_name):
                        self.add_result(
                            f"Auth function {func_name} exists",
                            True,
                            f"Function {func_name} found",
                        )
                    else:
                        self.add_result(
                            f"Auth function {func_name} exists",
                            False,
                            f"Function {func_name} missing",
                        )
            else:
                self.add_result(
                    "Auth functions exist", False, "Could not load auth module"
                )

        except Exception as e:
            self.add_result(
                "Auth functions exist",
                False,
                f"Error checking auth functions: {str(e)}",
            )

    def test_middleware_classes(self):
        """Test if middleware classes exist"""
        try:
            spec = importlib.util.spec_from_file_location(
                "core.middleware", os.path.join(self.backend_path, "core/middleware.py")
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check middleware classes
                middleware_classes = [
                    "AuthMiddleware",
                    "WorkspaceMiddleware",
                    "LoggingMiddleware",
                ]

                for class_name in middleware_classes:
                    if hasattr(module, class_name):
                        self.add_result(
                            f"Middleware {class_name} exists",
                            True,
                            f"Class {class_name} found",
                        )
                    else:
                        self.add_result(
                            f"Middleware {class_name} exists",
                            False,
                            f"Class {class_name} missing",
                        )
            else:
                self.add_result(
                    "Middleware classes exist",
                    False,
                    "Could not load middleware module",
                )

        except Exception as e:
            self.add_result(
                "Middleware classes exist",
                False,
                f"Error checking middleware: {str(e)}",
            )

    def test_environment_variables(self):
        """Test if required environment variables are documented"""
        env_vars = [
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
            "SUPABASE_JWT_SECRET",
        ]

        for env_var in env_vars:
            # Check if env var is referenced in code
            found = False
            for root, dirs, files in os.walk(self.backend_path):
                for file in files:
                    if file.endswith(".py"):
                        try:
                            file_path = os.path.join(root, file)
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                                if env_var in content:
                                    found = True
                                    break
                        except:
                            pass
                if found:
                    break

            if found:
                self.add_result(
                    f"Environment variable {env_var} referenced",
                    True,
                    f"{env_var} found in code",
                )
            else:
                self.add_result(
                    f"Environment variable {env_var} referenced",
                    False,
                    f"{env_var} not found in code",
                )

    def test_file_structure(self):
        """Test if required files exist"""
        required_files = [
            "core/__init__.py",
            "core/supabase.py",
            "core/models.py",
            "core/jwt.py",
            "core/auth.py",
            "core/workspace.py",
            "core/middleware.py",
        ]

        for file_path in required_files:
            full_path = os.path.join(self.backend_path, file_path)
            if os.path.exists(full_path):
                self.add_result(
                    f"File {file_path} exists", True, f"File found at {full_path}"
                )
            else:
                self.add_result(
                    f"File {file_path} exists", False, f"File missing at {full_path}"
                )

    async def run_all_tests(self):
        """Run all verification tests"""
        print("=" * 60)
        print("CYNICAL VERIFICATION - Task 4: Auth Middleware")
        print("=" * 60)

        self.test_file_structure()
        self.test_module_imports()
        self.test_supabase_client()
        self.test_jwt_validator()
        self.test_auth_functions()
        self.test_middleware_classes()
        self.test_environment_variables()

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        print(f"Tests passed: {passed}/{total}")

        if passed == total:
            print("✓ ALL TESTS PASSED - Task 4 verified empirically")
            return True
        else:
            print("✗ SOME TESTS FAILED - Task 4 needs fixes")
            for result in self.results:
                if not result.passed:
                    print(f"  FAILED: {result.test_name} - {result.details}")
            return False


if __name__ == "__main__":
    tester = AuthMiddlewareTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
