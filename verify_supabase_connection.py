import os

from supabase import Client, create_client


def _get_supabase_url() -> str:
    return os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL") or ""


def _get_supabase_service_role_key() -> str:
    return (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_SERVICE_KEY")
        or os.getenv("SERVICE_ROLE_KEY")
        or ""
    )


def verify_supabase() -> None:
    url = _get_supabase_url()
    key = _get_supabase_service_role_key()

    if not url or not key:
        raise SystemExit(
            "Supabase credentials not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
        )

    print(f"Connecting to Supabase at {url}...")

    supabase: Client = create_client(url, key)
    response = supabase.table("workspaces").select("id", count="exact").limit(1).execute()

    print("Supabase connection OK.")
    if getattr(response, "count", None) is not None:
        print(f"workspaces count (exact): {response.count}")


if __name__ == "__main__":
    verify_supabase()
