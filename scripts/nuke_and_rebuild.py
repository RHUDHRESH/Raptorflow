"""
Scorched earth: nuke all public tables, then push canonical schema.

Usage:
    python scripts/nuke_and_rebuild.py
    python scripts/nuke_and_rebuild.py --nuke-only
    python scripts/nuke_and_rebuild.py --schema-only
"""

import argparse
import os
import sys
import pathlib

# Add project root to path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / "backend" / ".env.test")
load_dotenv(PROJECT_ROOT / "backend" / ".env")
load_dotenv(PROJECT_ROOT / ".env")

SUPABASE_URL = (
    os.getenv("SUPABASE_URL")
    or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    or "https://vpwwzsanuyhpkvgorcnc.supabase.co"
)
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SERVICE_ROLE_KEY")
    or ""
)

NUKE_SQL_PATH = PROJECT_ROOT / "scripts" / "nuke_db.sql"
SCHEMA_SQL_PATH = PROJECT_ROOT / "supabase" / "migrations" / "20260208000000_canonical_schema.sql"


def execute_sql(sql: str, description: str) -> bool:
    """Execute SQL via Supabase REST RPC (pg_execute) or direct HTTP."""
    import urllib.request
    import json

    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    # Try the RPC approach first — if exec_sql function doesn't exist, fall back
    payload = json.dumps({"query": sql}).encode()
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(f"  ✓ {description} (status {resp.status})")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if "404" in str(e.code) or "does not exist" in body.lower():
            # exec_sql RPC doesn't exist, try creating it first
            return False
        print(f"  ✗ {description} failed: {e.code} — {body[:200]}")
        return False


def ensure_exec_sql_function() -> bool:
    """Create the exec_sql helper function if it doesn't exist."""
    import urllib.request
    import json

    create_fn_sql = """
    CREATE OR REPLACE FUNCTION exec_sql(query text)
    RETURNS void AS $$
    BEGIN
        EXECUTE query;
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    """

    # We need to use the Supabase Management API or SQL Editor for this.
    # Since we can't run DDL via REST easily, let's use the /pg endpoint if available.
    # Fallback: use supabase-py if installed.
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        client.rpc("exec_sql", {"query": "SELECT 1"}).execute()
        return True
    except Exception:
        pass

    # Try creating via REST RPC — this is a chicken-and-egg problem.
    # We'll use the management API approach.
    print("  → Creating exec_sql function via Management API...")

    mgmt_url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    # If the function doesn't exist yet, we need another way.
    # Let's try using supabase-py's postgrest or the SQL endpoint.
    return False


def execute_sql_via_supabase_py(sql: str, description: str) -> bool:
    """Execute SQL using supabase-py client."""
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Split SQL into statements and execute via RPC
        # First ensure the exec_sql function exists
        try:
            client.rpc("exec_sql", {"query": "SELECT 1"}).execute()
        except Exception:
            # Function doesn't exist — create it using postgrest
            # This won't work for DDL. We need to use the SQL editor approach.
            print(f"  ⚠ exec_sql function not available. Creating it...")
            # Use the Supabase Management API
            return execute_sql_via_management_api(sql, description)

        # Execute the full SQL
        result = client.rpc("exec_sql", {"query": sql}).execute()
        print(f"  ✓ {description}")
        return True
    except ImportError:
        print("  ⚠ supabase-py not installed. Install with: pip install supabase")
        return False
    except Exception as e:
        print(f"  ✗ {description} failed: {e}")
        return False


def execute_sql_via_management_api(sql: str, description: str) -> bool:
    """Execute SQL via Supabase Management API (requires access token)."""
    import urllib.request
    import json

    access_token = os.getenv("SUPABASE_ACCESS_TOKEN", "sbp_23be6405f8c238ea5e6218120f12262ac8d04a74")
    project_ref = "vpwwzsanuyhpkvgorcnc"

    url = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({"query": sql}).encode()
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode()
            print(f"  ✓ {description}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ✗ {description} failed: {e.code} — {body[:300]}")
        return False


def nuke_db():
    """Drop all public tables."""
    print("\n🔥 NUKING DATABASE...")
    sql = NUKE_SQL_PATH.read_text(encoding="utf-8")
    if not execute_sql_via_management_api(sql, "Nuke all public tables"):
        print("  ⚠ Nuke failed. Try running scripts/nuke_db.sql manually in Supabase SQL Editor.")
        return False
    return True


def push_schema():
    """Push canonical schema."""
    print("\n🏗️  PUSHING CANONICAL SCHEMA...")
    sql = SCHEMA_SQL_PATH.read_text(encoding="utf-8")
    if not execute_sql_via_management_api(sql, "Push canonical schema"):
        print("  ⚠ Schema push failed. Try running the migration SQL manually in Supabase SQL Editor.")
        return False
    return True


def verify():
    """Verify tables exist."""
    print("\n🔍 VERIFYING...")
    import urllib.request
    import json

    headers_dict = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    url = f"{SUPABASE_URL}/rest/v1/"
    req = urllib.request.Request(url, headers=headers_dict, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            tables = list(data.get("definitions", {}).keys())
            print(f"  Tables found: {len(tables)}")
            for t in sorted(tables):
                print(f"    • {t}")
            return True
    except Exception as e:
        print(f"  ✗ Verification failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Nuke and rebuild Supabase DB")
    parser.add_argument("--nuke-only", action="store_true", help="Only nuke, don't rebuild")
    parser.add_argument("--schema-only", action="store_true", help="Only push schema, don't nuke")
    parser.add_argument("--verify-only", action="store_true", help="Only verify current state")
    args = parser.parse_args()

    if not SUPABASE_KEY:
        print("✗ SUPABASE_SERVICE_ROLE_KEY not set. Check your .env files.")
        sys.exit(1)

    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"Service key: ...{SUPABASE_KEY[-8:]}")

    if args.verify_only:
        verify()
        return

    if not args.schema_only:
        if not nuke_db():
            print("\n⚠ Nuke step had issues. Continuing anyway...")

    if not args.nuke_only:
        if not push_schema():
            print("\n✗ Schema push failed.")
            sys.exit(1)

    verify()
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
