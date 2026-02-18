#!/usr/bin/env python3
"""
Auth Environment Verification Script
Verifies all required environment variables for authentication are properly configured.

Usage: python scripts/verify_auth_env.py
"""

import os
import re
import sys
from pathlib import Path

# Fix Windows encoding issues
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Load .env file if present
from pathlib import Path

env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if key and value and not os.getenv(key):
                    os.environ[key] = value

# Also check .env.local
env_local = Path(__file__).parent.parent / ".env.local"
if env_local.exists():
    with open(env_local) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if key and value and not os.getenv(key):
                    os.environ[key] = value

try:
    import httpx
    import jwt
except ImportError:
    print("Installing required packages...")
    os.system("pip install httpx pyjwt")
    import httpx
    import jwt
except ImportError:
    print("Installing required packages...")
    os.system("pip install httpx pyjwt")
    import httpx
    import jwt


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text: str) -> None:
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_success(text: str) -> None:
    print(f"  {Colors.GREEN}✓{Colors.END} {text}")


def print_error(text: str) -> None:
    print(f"  {Colors.RED}✗{Colors.END} {text}")


def print_warning(text: str) -> None:
    print(f"  {Colors.YELLOW}⚠{Colors.END} {text}")


def print_info(text: str) -> None:
    print(f"  {Colors.BLUE}ℹ{Colors.END} {text}")


def check_required_vars() -> dict:
    """Check if all required environment variables are present."""
    print_header("1. Checking Required Environment Variables")

    required_vars = {
        "SUPABASE_URL": "Supabase project URL",
        "NEXT_PUBLIC_SUPABASE_URL": "Frontend Supabase URL",
        "SUPABASE_ANON_KEY": "Supabase anonymous key",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY": "Frontend anonymous key",
        "SUPABASE_SERVICE_ROLE_KEY": "Supabase service role key (backend only)",
        "AUTH_MODE": "Authentication mode (demo/supabase/disabled)",
    }

    optional_vars = {
        "DATABASE_URL": "Database connection URL",
        "SUPABASE_DB_URL": "Supabase database URL",
        "ACCESS_TOKEN_EXPIRY": "Access token expiry in seconds",
        "REFRESH_TOKEN_EXPIRY": "Refresh token expiry in seconds",
    }

    results = {"required": [], "optional": [], "missing": []}

    # Check required vars
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            results["required"].append((var, True, f"Present - {len(value)} chars"))
        else:
            results["required"].append((var, False, "Missing"))
            results["missing"].append(var)

    # Check optional vars
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            results["optional"].append((var, True, f"Present - {len(value)} chars"))
        else:
            results["optional"].append((var, False, "Not set (optional)"))

    # Print results
    all_passed = True
    for var, passed, msg in results["required"]:
        if passed:
            print_success(f"{var}: {msg}")
        else:
            print_error(f"{var}: {msg}")
            all_passed = False

    for var, passed, msg in results["optional"]:
        if passed:
            print_success(f"{var} (optional): {msg}")
        else:
            print_warning(f"{var} (optional): {msg}")

    return results


def check_supabase_url_format() -> bool:
    """Verify Supabase URL format."""
    print_header("2. Checking Supabase URL Format")

    supabase_url = os.getenv("SUPABASE_URL", "")

    # Check format: https://xxx.supabase.co
    url_pattern = r"^https://[a-z0-9]+\.supabase\.co$"

    if re.match(url_pattern, supabase_url):
        print_success(f"SUPABASE_URL format: {supabase_url}")

        # Extract project ref
        project_ref = supabase_url.replace("https://", "").replace(".supabase.co", "")
        print_info(f"Project ref: {project_ref}")

        return True
    else:
        print_error(f"Invalid SUPABASE_URL format: {supabase_url}")
        print_info("Expected format: https://xxx.supabase.co")
        return False


def check_jwt_keys() -> bool:
    """Verify JWT keys are valid."""
    print_header("3. Checking JWT Keys")

    anon_key = os.getenv("SUPABASE_ANON_KEY", "")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    if not anon_key:
        print_error("SUPABASE_ANON_KEY is missing")
        return False

    if not service_role_key:
        print_error("SUPABASE_SERVICE_ROLE_KEY is missing")
        return False

    all_valid = True

    # Check anon key
    try:
        # Try to decode without verification (just check format)
        decoded = jwt.decode(anon_key, options={"verify_signature": False})
        if decoded.get("role") == "anon":
            print_success("SUPABASE_ANON_KEY: Valid JWT with 'anon' role")
        else:
            print_warning(
                f"SUPABASE_ANON_KEY: JWT role is '{decoded.get('role')}', expected 'anon'"
            )
    except Exception as e:
        print_error(f"SUPABASE_ANON_KEY: Invalid JWT - {str(e)}")
        all_valid = False

    # Check service role key
    try:
        decoded = jwt.decode(service_role_key, options={"verify_signature": False})
        if decoded.get("role") == "service_role":
            print_success(
                "SUPABASE_SERVICE_ROLE_KEY: Valid JWT with 'service_role' role"
            )
        else:
            print_warning(
                f"SUPABASE_SERVICE_ROLE_KEY: JWT role is '{decoded.get('role')}', expected 'service_role'"
            )
    except Exception as e:
        print_error(f"SUPABASE_SERVICE_ROLE_KEY: Invalid JWT - {str(e)}")
        all_valid = False

    # Check if keys match the project
    supabase_url = os.getenv("SUPABASE_URL", "")
    expected_ref = supabase_url.replace("https://", "").replace(".supabase.co", "")

    try:
        decoded = jwt.decode(anon_key, options={"verify_signature": False})
        key_ref = decoded.get("ref", "")

        if key_ref == expected_ref:
            print_success(f"Key project ref matches: {key_ref}")
        else:
            print_error(
                f"Key project ref '{key_ref}' doesn't match URL ref '{expected_ref}'"
            )
            all_valid = False
    except Exception:
        pass  # Already reported above

    return all_valid


def check_auth_mode() -> bool:
    """Verify AUTH_MODE is valid."""
    print_header("4. Checking Authentication Mode")

    auth_mode = os.getenv("AUTH_MODE", "demo")

    valid_modes = ["demo", "supabase", "disabled"]

    if auth_mode.lower() in valid_modes:
        print_success(f"AUTH_MODE: {auth_mode}")

        if auth_mode.lower() == "demo":
            print_warning("Demo mode is enabled - NOT SECURE for production")
            print_info("Set AUTH_MODE=supabase for production")
        elif auth_mode.lower() == "disabled":
            print_warning("Auth is DISABLED - NOT SECURE for production")
        else:
            print_success("Supabase auth mode is enabled - READY for production")

        return True
    else:
        print_error(f"Invalid AUTH_MODE: {auth_mode}")
        print_info(f"Valid options: {', '.join(valid_modes)}")
        return False


def check_url_consistency() -> bool:
    """Check if URLs are consistent across env vars."""
    print_header("5. Checking URL Consistency")

    supabase_url = os.getenv("SUPABASE_URL", "")
    next_public_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")

    all_consistent = True

    if supabase_url == next_public_url:
        print_success("SUPABASE_URL and NEXT_PUBLIC_SUPABASE_URL match")
    else:
        print_error("URLs don't match:")
        print_error(f"  SUPABASE_URL: {supabase_url}")
        print_error(f"  NEXT_PUBLIC_SUPABASE_URL: {next_public_url}")
        all_consistent = False

    return all_consistent


async def check_supabase_connection() -> bool:
    """Test connection to Supabase API."""
    print_header("6. Testing Supabase Connection")

    supabase_url = os.getenv("SUPABASE_URL", "")
    anon_key = os.getenv("SUPABASE_ANON_KEY", "")

    if not supabase_url or not anon_key:
        print_error("Missing SUPABASE_URL or SUPABASE_ANON_KEY")
        return False

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try to get auth settings
            response = await client.get(
                f"{supabase_url}/auth/v1/settings", headers={"apikey": anon_key}
            )

            if response.status_code == 200:
                print_success(f"Supabase API accessible: {response.status_code}")

                # Try to get project info
                project_response = await client.get(
                    f"{supabase_url}/rest/v1/", headers={"apikey": anon_key}
                )

                if project_response.status_code in [200, 401, 404]:
                    print_success("Supabase REST API accessible")
                    return True
                else:
                    print_warning(f"REST API returned: {project_response.status_code}")
                    return False
            else:
                print_error(f"Supabase API returned: {response.status_code}")
                print_error(response.text[:200])
                return False

    except httpx.ConnectError:
        print_error("Cannot connect to Supabase - check URL and network")
        return False
    except Exception as e:
        print_error(f"Connection test failed: {str(e)}")
        return False


async def check_database_connection() -> bool:
    """Test connection to Supabase database."""
    print_header("7. Testing Database Connection")

    db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")

    if not db_url:
        print_warning("DATABASE_URL not set - skipping database test")
        return True

    try:
        import psycopg2

        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        cursor.execute("SELECT version()")
        version = cursor.fetchone()

        print_success(f"Database connected: {version[0].split(',')[0]}")

        # Check tables
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
            LIMIT 10
        """)
        tables = [row[0] for row in cursor.fetchall()]

        print_success(
            f"Found {len(tables)} tables: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}"
        )

        cursor.close()
        conn.close()

        return True

    except ImportError:
        print_warning("psycopg2 not installed - skipping database test")
        print_info("Install with: pip install psycopg2-binary")
        return True
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        return False


def main():
    print("\n" + "=" * 60)
    print("  RAPTORFLOW AUTH ENVIRONMENT VERIFICATION SCRIPT")
    print("=" * 60 + "\n")

    # Run all checks
    results = {}

    # 1. Required vars
    var_results = check_required_vars()
    results["required_vars"] = len(var_results["missing"]) == 0

    # 2. URL format
    results["url_format"] = check_supabase_url_format()

    # 3. JWT keys
    results["jwt_keys"] = check_jwt_keys()

    # 4. Auth mode
    results["auth_mode"] = check_auth_mode()

    # 5. URL consistency
    results["url_consistency"] = check_url_consistency()

    # 6. Supabase connection (async)
    import asyncio

    results["supabase_connection"] = asyncio.run(check_supabase_connection())

    # 7. Database connection (async)
    results["database_connection"] = asyncio.run(check_database_connection())

    # Summary
    print_header("VERIFICATION SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for check, result in results.items():
        name = check.replace("_", " ").title()
        if result:
            print_success(name)
        else:
            print_error(name)

    print(f"\n{Colors.BOLD}Score: {passed}/{total} checks passed{Colors.END}\n")

    if passed == total:
        print(
            f"{Colors.GREEN}{Colors.BOLD}✓ All checks passed! Auth is ready.{Colors.END}\n"
        )
        return 0
    elif passed >= total - 1:
        print(
            f"{Colors.YELLOW}{Colors.BOLD}⚠ Most checks passed. Review warnings above.{Colors.END}\n"
        )
        return 0
    else:
        print(
            f"{Colors.RED}{Colors.BOLD}✗ Multiple checks failed. Please fix the issues above.{Colors.END}\n"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
