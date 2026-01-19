import psycopg2
import os

# Database connection
db_url = "postgresql://postgres.vpwwzsanuyhpkvgorcnc:1IMRvR6WC3kbRvp4@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def run_migration():
    conn = None
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print("Reading migration file...")
        with open('./supabase/migrations/20260118_google_auth_profiles.sql', 'r') as f:
            migration_sql = f.read()
        
        print("Executing migration...")
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        
    except Exception as error:
        print(f"❌ Migration failed: {error}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    run_migration()
