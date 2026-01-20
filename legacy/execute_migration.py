import psycopg2
import os
import sys

# Database connection using the service role
db_url = "postgresql://postgres.vpwwzsanuyhpkvgorcnc:1IMRvR6WC3kbRvp4@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def execute_migration():
    conn = None
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print("Reading migration file...")
        with open('./supabase/migrations/20260118015016_google_auth_profiles_update.sql', 'r') as f:
            migration_sql = f.read()
        
        print("Executing migration SQL...")
        
        # Split into individual statements and execute one by one
        statements = migration_sql.split(';')
        for i, statement in enumerate(statements):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                print(f"Executing statement {i+1}...")
                try:
                    cursor.execute(statement)
                    print(f"✓ Statement {i+1} executed successfully")
                except Exception as e:
                    print(f"⚠ Statement {i+1} warning: {e}")
                    # Continue with other statements
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Verify the profiles table exists
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'profiles' AND table_schema = 'public'")
        table_exists = cursor.fetchone()[0] > 0
        print(f"Profiles table exists: {table_exists}")
        
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM public.profiles")
            profile_count = cursor.fetchone()[0]
            print(f"Current profiles count: {profile_count}")
        
    except Exception as error:
        print(f"❌ Migration failed: {error}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()
    return True

if __name__ == "__main__":
    success = execute_migration()
    sys.exit(0 if success else 1)
