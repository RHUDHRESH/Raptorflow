"""
Production Readiness Verification Report
"""

import json
from datetime import datetime
from pathlib import Path


class ProductionReadinessChecker:
    """Comprehensive production readiness verification"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues = []
        self.warnings = []
        self.successes = []
        self.score = 0
        self.max_score = 100

    def check_database_migrations(self):
        """Check database migrations completeness"""
        print("🔍 Checking database migrations...")

        migrations_dir = self.project_root / "supabase" / "migrations"
        if not migrations_dir.exists():
            self.issues.append("❌ Supabase migrations directory not found")
            return

        migration_files = list(migrations_dir.glob("*.sql"))
        required_migrations = [
            "20240101_users_workspaces.sql",
            "20240120_billing.sql",
            "20240121_api_keys.sql",
            "20240122_audit_logs.sql",
            "20240116_indexes.sql",
            "20240117_functions.sql",
            "20240118_triggers.sql",
            "20240119_views.sql",
        ]

        missing_migrations = []
        found_migrations = []
        for required in required_migrations:
            found = any(migration.name == required for migration in migration_files)
            if found:
                found_migrations.append(required)
            else:
                missing_migrations.append(required)

        if missing_migrations:
            self.issues.append(
                f"❌ Missing migrations: {', '.join(missing_migrations)}"
            )
            self.score += len(found_migrations) * 2  # Partial credit
        else:
            self.successes.append("✅ All required database migrations present")
            self.score += 10

    def check_authentication_system(self):
        """Check authentication system completeness"""
        print("🔍 Checking authentication system...")

        auth_files = [
            "backend/core/auth.py",
            "backend/core/models.py",
            "backend/core/jwt.py",
        ]

        missing_auth_files = []
        found_auth_files = []
        for auth_file in auth_files:
            if (self.project_root / auth_file).exists():
                found_auth_files.append(auth_file)
            else:
                missing_auth_files.append(auth_file)

        if missing_auth_files:
            self.issues.append(
                f"❌ Missing auth files: {', '.join(missing_auth_files)}"
            )
            self.score += len(found_auth_files) * 3  # Partial credit
        else:
            self.successes.append("✅ Authentication system files present")
            self.score += 10

        # Check auth endpoints
        auth_endpoint = self.project_root / "backend/api/v1/auth.py"
        if auth_endpoint.exists():
            self.successes.append("✅ Authentication API endpoints present")
            self.score += 5
        else:
            self.issues.append("❌ Authentication API endpoints missing")

    def check_database_repositories(self):
        """Check database repositories completeness"""
        print("🔍 Checking database repositories...")

        repo_files = [
            "backend/db/base.py",
            "backend/db/pagination.py",
            "backend/db/filters.py",
            "backend/db/foundations.py",
            "backend/db/icps.py",
            "backend/db/moves.py",
            "backend/db/campaigns.py",
            "backend/db/muse_assets.py",
            "backend/db/blackbox.py",
            "backend/db/daily_wins.py",
            "backend/db/agent_executions.py",
        ]

        missing_repos = []
        found_repos = []
        for repo_file in repo_files:
            if (self.project_root / repo_file).exists():
                found_repos.append(repo_file)
            else:
                missing_repos.append(repo_file)

        if missing_repos:
            self.issues.append(
                f"❌ Missing repository files: {', '.join(missing_repos)}"
            )
            self.score += len(found_repos)  # Partial credit
        else:
            self.successes.append("✅ All database repositories present")
            self.score += 15

    def check_api_endpoints(self):
        """Check API endpoints completeness"""
        print("🔍 Checking API endpoints...")

        api_files = [
            "backend/api/v1/auth.py",
            "backend/api/v1/workspaces.py",
            "backend/api/v1/users.py",
            "backend/api/v1/campaigns.py",
            "backend/api/v1/muse.py",
            "backend/api/v1/blackbox.py",
            "backend/api/v1/daily_wins.py",
        ]

        missing_apis = []
        found_apis = []
        for api_file in api_files:
            if (self.project_root / api_file).exists():
                found_apis.append(api_file)
            else:
                missing_apis.append(api_file)

        if missing_apis:
            self.issues.append(f"❌ Missing API files: {', '.join(missing_apis)}")
            self.score += len(found_apis) * 2  # Partial credit
        else:
            self.successes.append("✅ All API endpoints present")
            self.score += 15

    def check_test_suite(self):
        """Check test suite completeness"""
        print("🔍 Checking test suite...")

        test_files = [
            "tests/conftest.py",
            "tests/db/conftest.py",
            "tests/db/test_repositories.py",
            "tests/auth/test_authentication.py",
            "tests/api/test_endpoints.py",
            "tests/run_tests.py",
            "pytest.ini",
        ]

        missing_tests = []
        found_tests = []
        for test_file in test_files:
            if (self.project_root / test_file).exists():
                found_tests.append(test_file)
            else:
                missing_tests.append(test_file)

        if missing_tests:
            self.issues.append(f"❌ Missing test files: {', '.join(missing_tests)}")
            self.score += len(found_tests) * 2  # Partial credit
        else:
            self.successes.append("✅ Comprehensive test suite present")
            self.score += 15

    def check_configuration_files(self):
        """Check configuration files"""
        print("🔍 Checking configuration files...")

        config_files = [".env.example", "docker-compose.yml", "Dockerfile", "README.md"]

        missing_configs = []
        for config_file in config_files:
            if not (self.project_root / config_file).exists():
                missing_configs.append(config_file)

        if missing_configs:
            self.warnings.append(
                f"⚠️ Missing config files: {', '.join(missing_configs)}"
            )
        else:
            self.successes.append("✅ Configuration files present")
            self.score += 5

    def check_documentation(self):
        """Check documentation completeness"""
        print("🔍 Checking documentation...")

        doc_files = ["README.md", "DOCUMENTATION/SWARM/TASKS/STREAM_4_DATABASE_AUTH.md"]

        missing_docs = []
        for doc_file in doc_files:
            if not (self.project_root / doc_file).exists():
                missing_docs.append(doc_file)

        if missing_docs:
            self.warnings.append(f"⚠️ Missing documentation: {', '.join(missing_docs)}")
        else:
            self.successes.append("✅ Documentation present")
            self.score += 5

    def check_security_measures(self):
        """Check security measures"""
        print("🔍 Checking security measures...")

        # Check for RLS policies in migrations
        migrations_dir = self.project_root / "supabase" / "migrations"
        rls_found = False

        if migrations_dir.exists():
            for migration in migrations_dir.glob("*.sql"):
                content = migration.read_text()
                if "ROW LEVEL SECURITY" in content or "RLS" in content:
                    rls_found = True
                    break

        if rls_found:
            self.successes.append("✅ Row Level Security policies found")
            self.score += 5
        else:
            self.issues.append("❌ No Row Level Security policies found")

        # Check for audit logging
        audit_migration = migrations_dir / "20240122_audit_logs.sql"
        if audit_migration.exists():
            self.successes.append("✅ Audit logging system present")
            self.score += 5
        else:
            self.issues.append("❌ Audit logging system missing")

    def check_performance_optimizations(self):
        """Check performance optimizations"""
        print("🔍 Checking performance optimizations...")

        migrations_dir = self.project_root / "supabase" / "migrations"

        # Check for indexes
        indexes_migration = migrations_dir / "20240116_indexes.sql"
        if indexes_migration.exists():
            self.successes.append("✅ Database indexes present")
            self.score += 5
        else:
            self.issues.append("❌ Database indexes missing")

        # Check for database functions
        functions_migration = migrations_dir / "20240117_functions.sql"
        if functions_migration.exists():
            self.successes.append("✅ Database functions present")
            self.score += 5
        else:
            self.issues.append("❌ Database functions missing")

    def check_error_handling(self):
        """Check error handling"""
        print("🔍 Checking error handling...")

        # Check API endpoints for proper error handling
        api_dir = self.project_root / "backend/api/v1"
        error_handling_found = False

        if api_dir.exists():
            for api_file in api_dir.glob("*.py"):
                try:
                    content = api_file.read_text(encoding="utf-8")
                    if "HTTPException" in content and "status_code" in content:
                        error_handling_found = True
                        break
                except UnicodeDecodeError:
                    # Skip files with encoding issues
                    continue

        if error_handling_found:
            self.successes.append("✅ Proper error handling in API endpoints")
            self.score += 5
        else:
            self.warnings.append("⚠️ Limited error handling detected")

    def check_monitoring_setup(self):
        """Check monitoring and logging setup"""
        print("🔍 Checking monitoring setup...")

        # Check for logging configuration
        backend_dir = self.project_root / "backend"
        logging_found = False

        if backend_dir.exists():
            for py_file in backend_dir.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8")
                    if "import logging" in content or "from logging" in content:
                        logging_found = True
                        break
                except UnicodeDecodeError:
                    # Skip files with encoding issues
                    continue

        if logging_found:
            self.successes.append("✅ Logging configuration found")
            self.score += 5
        else:
            self.warnings.append("⚠️ Limited logging configuration detected")

    def generate_report(self):
        """Generate comprehensive production readiness report"""
        print("\n" + "=" * 80)
        print("🚀 RAPTORFLOW PRODUCTION READINESS REPORT")
        print("=" * 80)
        print(f"Generated: {datetime.now().isoformat()}")
        print(f"Project: {self.project_root}")
        print()

        # Run all checks
        self.check_database_migrations()
        self.check_authentication_system()
        self.check_database_repositories()
        self.check_api_endpoints()
        self.check_test_suite()
        self.check_configuration_files()
        self.check_documentation()
        self.check_security_measures()
        self.check_performance_optimizations()
        self.check_error_handling()
        self.check_monitoring_setup()

        # Calculate final score
        total_checks = len(self.successes) + len(self.issues) + len(self.warnings)
        success_rate = (
            (len(self.successes) / total_checks * 100) if total_checks > 0 else 0
        )

        # Display results
        print(
            f"📊 OVERALL SCORE: {self.score}/{self.max_score} ({success_rate:.1f}% success rate)"
        )
        print()

        if self.successes:
            print("✅ SUCCESSFUL CHECKS:")
            for success in self.successes:
                print(f"  {success}")
            print()

        if self.warnings:
            print("⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
            print()

        if self.issues:
            print("❌ ISSUES:")
            for issue in self.issues:
                print(f"  {issue}")
            print()

        # Production readiness assessment
        print("🎯 PRODUCTION READINESS ASSESSMENT:")
        if self.score >= 90:
            print("  🟢 EXCELLENT - Ready for production deployment")
        elif self.score >= 80:
            print("  🟡 GOOD - Mostly ready, address minor issues")
        elif self.score >= 70:
            print("  🟠 FAIR - Needs significant improvements")
        else:
            print("  🔴 NOT READY - Major issues must be addressed")

        print()

        # Recommendations
        print("📋 RECOMMENDATIONS:")
        if self.issues:
            print("  1. Address all critical issues before production deployment")
        if self.warnings:
            print("  2. Review and address warnings for optimal performance")
        if len(self.successes) < 10:
            print("  3. Complete missing components to improve readiness")
        print("  4. Run comprehensive tests before deployment")
        print("  5. Set up monitoring and alerting")
        print("  6. Document deployment procedures")
        print("  7. Plan rollback strategy")
        print()

        # Generate JSON report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_root),
            "score": self.score,
            "max_score": self.max_score,
            "success_rate": success_rate,
            "successes": self.successes,
            "warnings": self.warnings,
            "issues": self.issues,
            "readiness_level": self._get_readiness_level(),
        }

        report_file = self.project_root / "production_readiness_report.json"
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"📄 Detailed report saved to: {report_file}")
        print()

        return report_data

    def _get_readiness_level(self):
        """Get readiness level based on score"""
        if self.score >= 90:
            return "EXCELLENT"
        elif self.score >= 80:
            return "GOOD"
        elif self.score >= 70:
            return "FAIR"
        else:
            return "NOT_READY"


def main():
    """Main function to run production readiness check"""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    checker = ProductionReadinessChecker(script_dir)
    report = checker.generate_report()

    return report


if __name__ == "__main__":
    main()
