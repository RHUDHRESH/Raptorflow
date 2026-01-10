"""
Test Supabase database connection
"""

import os

from supabase import create_client


def test_supabase_connection():
    """Test Supabase database connection"""

    # Get environment variables
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_anon_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

    print(f"Testing Supabase connection...")
    print(f"URL: {supabase_url}")
    print(f"Key present: {bool(supabase_anon_key)}")

    if not supabase_url or not supabase_anon_key:
        print("❌ Missing Supabase environment variables")
        return False

    try:
        # Create client
        client = create_client(supabase_url, supabase_anon_key)
        print("✅ Supabase client created successfully")

        # Test connection by checking if user_profiles table exists
        try:
            result = client.table("user_profiles").select("id").limit(1).execute()
            print("✅ Database connection successful - user_profiles table exists")
            return True
        except Exception as e:
            if "does not exist" in str(e) or "PGRST116" in str(e):
                print("⚠️ Database connected but user_profiles table missing")
                print("This is expected for new installations")
                return True
            else:
                print(f"❌ Database query failed: {e}")
                return False

    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False


if __name__ == "__main__":
    # Load environment variables from .env.local if available
    from dotenv import load_dotenv

    load_dotenv("frontend/.env.local")

    test_supabase_connection()
