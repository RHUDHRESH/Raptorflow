import os
import sys

import psycopg2


def _resolve_db_url() -> str:
    db_url = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("Set SUPABASE_DB_URL or DATABASE_URL before running this check.")
    return db_url


def test_conn() -> None:
    try:
        conn = psycopg2.connect(_resolve_db_url())
        print("Connection successful")
        cur = conn.cursor()
        cur.execute("SELECT current_user, current_database();")
        res = cur.fetchone()
        print(f"User: {res[0]}, DB: {res[1]}")
        cur.close()
        conn.close()
    except Exception as exc:
        print(f"Connection failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    test_conn()
