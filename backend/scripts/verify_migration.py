import os
import sys

def verify_migration_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: Migration file {file_path} not found.")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    required_tables = [
        "foundation_brand_kit",
        "foundation_positioning",
        "foundation_voice_tone",
        "campaigns",
        "moves",
        "blackbox_telemetry",
        "ml_feature_store"
    ]
    
    missing = [t for t in required_tables if t not in content]
    
    if missing:
        print(f"Error: Missing tables in migration: {missing}")
        return False
    
    print(f"Migration file {file_path} verified successfully.")
    return True

if __name__ == "__main__":
    path = "raptorflow-app/supabase/migrations/20251223_industrial_core.sql"
    if verify_migration_file(path):
        sys.exit(0)
    else:
        sys.exit(1)
