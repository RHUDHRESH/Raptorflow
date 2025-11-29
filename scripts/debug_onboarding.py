import sys
import os
from psycopg2.extras import RealDictCursor

# Add scripts directory to path to allow importing from sibling
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_client import get_db_connection

def debug_user_onboarding(email=None):
    """
    Queries user_profiles to check onboarding status.
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            print("\n--- Checking User Profiles (Public Schema) ---")
            
            query = """
                SELECT id, email, full_name, onboarding_completed, onboarding_skipped, created_at 
                FROM public.user_profiles
            """
            
            params = []
            if email:
                query += " WHERE email = %s"
                params.append(email)
            
            query += " ORDER BY created_at DESC LIMIT 10;"
            
            cur.execute(query, params)
            profiles = cur.fetchall()

            if not profiles:
                print("No profiles found.")
            else:
                print(f"{'ID':<38} | {'Email':<30} | {'Onboarding':<10} | {'Skipped':<8} | {'Name'}")
                print("-" * 110)
                for p in profiles:
                    o_completed = str(p.get('onboarding_completed'))
                    o_skipped = str(p.get('onboarding_skipped'))
                    print(f"{str(p.get('id')):<38} | {str(p.get('email')):<30} | {o_completed:<10} | {o_skipped:<8} | {p.get('full_name')}")

            # Also check auth.users if we have permission (often postgres user does)
            # This helps verify if the user exists in Auth but not in public profile
            print("\n--- Checking Auth Users (Auth Schema - Last 5) ---")
            try:
                auth_query = "SELECT id, email, created_at FROM auth.users ORDER BY created_at DESC LIMIT 5;"
                cur.execute(auth_query)
                users = cur.fetchall()
                if users:
                    print(f"{'ID':<38} | {'Email':<30} | {'Created At'}")
                    print("-" * 90)
                    for u in users:
                        print(f"{str(u.get('id')):<38} | {str(u.get('email')):<30} | {str(u.get('created_at'))}")
                else:
                    print("No auth users found or no permission.")
            except Exception as e:
                print(f"Could not query auth.users: {e}")
                conn.rollback()

    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    target_email = sys.argv[1] if len(sys.argv) > 1 else None
    debug_user_onboarding(target_email)
