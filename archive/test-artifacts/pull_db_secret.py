import subprocess
import os

project_id = "raptorflow-481505"
secret_names = [
    "SUPABASE_DB_PASSWORD",
    "DATABASE_PASSWORD",
    "DB_PASSWORD",
    "postgres-password",
    "SUPABASE_PASSWORD"
]

def access_secret(name):
    print(f"Trying to access secret: {name}...")
    cmd = f"gcloud secrets versions access latest --secret={name} --project={project_id}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ SUCCESS! Secret {name} found.")
            print(f"Value: {result.stdout.strip()}")
            return True
        else:
            # print(f"❌ FAILED for {name}: {result.stderr.strip()[:100]}...")
            pass
    except Exception as e:
        print(f"Error: {e}")
    return False

if __name__ == "__main__":
    # Ensure service account is active
    os.system("gcloud auth activate-service-account --key-file=raptorflow-storage-key.json")
    
    for name in secret_names:
        if access_secret(name):
            # break
            pass
