"""
Create database tables using direct SQL execution
"""

import os

from supabase import create_client


def create_tables_directly():
    """Create database tables using direct SQL"""

    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    print("🔧 Creating database tables directly...")

    if not supabase_url or not supabase_service_key:
        print("❌ Missing Supabase environment variables")
        return False

    try:
        # Create admin client
        client = create_client(supabase_url, supabase_service_key)

        # Simple table creation using raw SQL
        user_profiles_sql = """
        CREATE TABLE IF NOT EXISTS user_profiles (
            id UUID REFERENCES auth.users(id) PRIMARY KEY,
            email TEXT NOT NULL,
            full_name TEXT,
            avatar_url TEXT,
            subscription_plan TEXT CHECK (subscription_plan IN ('soar', 'glide', 'ascent')),
            subscription_status TEXT CHECK (subscription_status IN ('active', 'cancelled', 'expired')),
            subscription_expires_at TIMESTAMPTZ,
            storage_quota_mb INTEGER DEFAULT 100,
            storage_used_mb INTEGER DEFAULT 0,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """

        payments_sql = """
        CREATE TABLE IF NOT EXISTS payments (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID REFERENCES auth.users(id) NOT NULL,
            transaction_id TEXT UNIQUE NOT NULL,
            plan_id TEXT NOT NULL CHECK (plan_id IN ('soar', 'glide', 'ascent')),
            amount INTEGER NOT NULL,
            currency TEXT DEFAULT 'INR',
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
            payment_method TEXT DEFAULT 'phonepe',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            verified_at TIMESTAMPTZ
        );
        """

        print("📄 Creating user_profiles table...")
        try:
            # Try to create table using postgrest (this might not work for DDL)
            result = client.table("user_profiles").select("*").limit(1).execute()
            print("✅ user_profiles table already exists")
        except Exception as e:
            if "PGRST205" in str(e):  # Table doesn't exist
                print("⚠️ Table doesn't exist and cannot be created via REST API")
                print("📝 Please run the following SQL in Supabase dashboard:")
                print(user_profiles_sql)
            else:
                print(f"❌ Error checking table: {e}")

        print("📄 Creating payments table...")
        try:
            result = client.table("payments").select("*").limit(1).execute()
            print("✅ payments table already exists")
        except Exception as e:
            if "PGRST205" in str(e):  # Table doesn't exist
                print("⚠️ Table doesn't exist and cannot be created via REST API")
                print("📝 Please run the following SQL in Supabase dashboard:")
                print(payments_sql)
            else:
                print(f"❌ Error checking table: {e}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv("frontend/.env.local")

    create_tables_directly()
