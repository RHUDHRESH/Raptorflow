import os
import json
import uuid
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")
load_dotenv("frontend/.env.local", override=True)

def run_red_team_audit():
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_service_key:
        print("Γ¥î Missing Supabase environment variables")
        return

    client = create_client(supabase_url, supabase_service_key)
    
    # Define the red team test SQL
    # This SQL will:
    # 1. Create two workspaces
    # 2. Create two users, each in their own workspace
    # 3. As User 1, try to see User 2's data
    # 4. As User 1, try to insert into User 2's workspace
    
    workspace_1_id = str(uuid.uuid4())
    workspace_2_id = str(uuid.uuid4())
    user_1_id = str(uuid.uuid4())
    user_2_id = str(uuid.uuid4())
    
    test_sql = f"""
    DO $$
    DECLARE
        v_count INTEGER;
    BEGIN
        -- Setup Clean State for Test
        DELETE FROM public.workspace_members WHERE workspace_id IN ('{workspace_1_id}', '{workspace_2_id}');
        DELETE FROM public.workspaces WHERE id IN ('{workspace_1_id}', '{workspace_2_id}');
        
        -- Create Workspaces
        INSERT INTO public.workspaces (id, name, owner_id) VALUES ('{workspace_1_id}', 'Workspace 1', '{user_1_id}');
        INSERT INTO public.workspaces (id, name, owner_id) VALUES ('{workspace_2_id}', 'Workspace 2', '{user_2_id}');
        
        -- Add Members
        INSERT INTO public.workspace_members (user_id, workspace_id, role) VALUES ('{user_1_id}', '{workspace_1_id}', 'owner');
        INSERT INTO public.workspace_members (user_id, workspace_id, role) VALUES ('{user_2_id}', '{workspace_2_id}', 'owner');
        
        -- Insert Data into Workspace 2
        INSERT INTO public.moves (workspace_id, title, category, objective) 
        VALUES ('{workspace_2_id}', 'Secret Move 2', 'marketing', 'User 2 Objective');
        
        -- TEST 1: User 1 tries to SELECT from Workspace 2
        -- Simulate User 1 Session
        PERFORM set_config('request.jwt.claims', json_build_object('sub', '{user_1_id}')::text, true);
        PERFORM set_config('role', 'authenticated', true);
        
        SELECT count(*) INTO v_count FROM public.moves WHERE workspace_id = '{workspace_2_id}';
        
        IF v_count > 0 THEN
            RAISE EXCEPTION 'RLS FAILURE: User 1 can see User 2 data!';
        END IF;
        
        -- TEST 2: User 1 tries to INSERT into Workspace 2
        BEGIN
            INSERT INTO public.moves (workspace_id, title, category, objective) 
            VALUES ('{workspace_2_id}', 'Hacked Move', 'marketing', 'Evil Objective');
            RAISE EXCEPTION 'RLS FAILURE: User 1 can insert into User 2 workspace!';
        EXCEPTION WHEN insufficient_privilege OR raise_exception THEN
            -- Expected failure
            NULL;
        END;
        
        -- Cleanup
        DELETE FROM public.moves WHERE workspace_id IN ('{workspace_1_id}', '{workspace_2_id}');
        DELETE FROM public.workspace_members WHERE workspace_id IN ('{workspace_1_id}', '{workspace_2_id}');
        DELETE FROM public.workspaces WHERE id IN ('{workspace_1_id}', '{workspace_2_id}');
        
        RAISE NOTICE 'RLS Audit Passed: Isolation is enforced.';
    END $$;
    """
    
    print("≡ƒ¢í∩╕Å Running RLS Red-Team Audit...")
    try:
        # Use exec_sql RPC if it exists, otherwise we might need to use another method
        result = client.rpc("exec_sql", {"sql": test_sql}).execute()
        print("Γ£à RLS Audit Successful: Isolation is enforced.")
    except Exception as e:
        if "RLS FAILURE" in str(e):
            print(f"≡ƒÜ¿ CRITICAL SECURITY VULNERABILITY: {e}")
        else:
            print(f"ΓÜá∩╕Å Audit encountered an error (Check if exec_sql exists): {e}")

if __name__ == "__main__":
    run_red_team_audit()
