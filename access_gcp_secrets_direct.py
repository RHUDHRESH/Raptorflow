import subprocess
import os

project_id = "raptorflow-481505"
secret_names = [
    "UPSTASH_REDIS_REST_TOKEN",
    "UPSTASH_REDIS_TOKEN",
    "REDIS_TOKEN",
    "upstash-redis-token",
    "raptorflow-UPSTASH_REDIS_REST_TOKEN",
    "raptorflow-redis-token"
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
            print(f"❌ FAILED for {name}: {result.stderr.strip()[:100]}...")
    except Exception as e:
        print(f"Error: {e}")
    return False

if __name__ == "__main__":
    # Ensure service account is active
    os.system("gcloud auth activate-service-account --key-file=raptorflow-storage-key.json")
    
    for name in secret_names:
        if access_secret(name):
            break
