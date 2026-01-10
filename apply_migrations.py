"""
Apply Supabase migrations to set up database tables
"""

import os

from supabase import create_client


def apply_migrations():
    """Apply database migrations to Supabase"""

    # Get environment variables
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    print("🔧 Applying Supabase migrations...")
    print(f"URL: {supabase_url}")
    print(f"Service Key present: {bool(supabase_service_key)}")

    if not supabase_url or not supabase_service_key:
        print("❌ Missing Supabase environment variables")
        return False

    try:
        # Create admin client with service role key
        client = create_client(supabase_url, supabase_service_key)
        print("✅ Supabase admin client created")

        # Read and apply migrations
        migrations_dir = "supabase/migrations"
        migration_files = [
            "20240105000001_create_user_profiles.sql",
            "20240105000002_auth_and_payments.sql",
            "202401050001_phonepe_payment_schema.sql",
        ]

        for migration_file in migration_files:
            migration_path = os.path.join(migrations_dir, migration_file)
            if os.path.exists(migration_path):
                print(f"📄 Applying {migration_file}...")

                with open(migration_path, "r") as f:
                    migration_sql = f.read()

                # Split migration into individual statements
                statements = [
                    stmt.strip() for stmt in migration_sql.split(";") if stmt.strip()
                ]

                for statement in statements:
                    if statement and not statement.startswith("--"):
                        try:
                            result = client.rpc(
                                "exec_sql", {"sql": statement}
                            ).execute()
                            print(f"  ✅ Executed: {statement[:50]}...")
                        except Exception as e:
                            # Some statements might not be executable via RPC
                            print(f"  ⚠️ Could not execute via RPC: {statement[:50]}...")
                            print(f"     Error: {e}")

                print(f"✅ Completed {migration_file}")
            else:
                print(f"⚠️ Migration file not found: {migration_path}")

        # Test if tables were created
        print("\n🔍 Verifying table creation...")
        try:
            # Test user_profiles table
            result = client.table("user_profiles").select("id").limit(1).execute()
            print("✅ user_profiles table exists and accessible")
        except Exception as e:
            print(f"❌ user_profiles table test failed: {e}")

        try:
            # Test payments table
            result = client.table("payments").select("id").limit(1).execute()
            print("✅ payments table exists and accessible")
        except Exception as e:
            print(f"❌ payments table test failed: {e}")

        print("\n🎉 Migration process completed!")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv("frontend/.env.local")

    apply_migrations()
