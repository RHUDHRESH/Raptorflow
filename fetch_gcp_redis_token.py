import os
import logging
from google.cloud import secretmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fetch_secrets")

# Set environment variables for GCP
os.environ["GCP_PROJECT_ID"] = "raptorlite"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./rhudhreshr_json/raptorlite-0ee24b15c8ac.json"

def get_secret(name: str, project_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    # Try with and without prefix
    prefixes = ["", "raptorflow-"]
    for prefix in prefixes:
        path = f"projects/{project_id}/secrets/{prefix}{name}/versions/latest"
        try:
            logger.info(f"Attempting to fetch {path}...")
            response = client.access_secret_version(request={"name": path})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.warning(f"Failed to fetch {prefix}{name}: {e}")
    return None

def main():
    project_id = os.environ["GCP_PROJECT_ID"]
    
    token = get_secret("UPSTASH_REDIS_REST_TOKEN", project_id)
    if token:
        print(f"\n✅ FETCHED UPSTASH_REDIS_REST_TOKEN: [{token}]")
        # Save to a temporary file
        with open("gcp_token.txt", "w") as f:
            f.write(token)
    else:
        # Also try lowercase or common variations
        for var in ["upstash-redis-token", "redis-token", "UPSTASH_REDIS_TOKEN"]:
            token = get_secret(var, project_id)
            if token:
                print(f"\n✅ FETCHED {var}: [{token}]")
                with open("gcp_token.txt", "w") as f:
                    f.write(token)
                break
        else:
            print("\n❌ COULD NOT FIND REDIS TOKEN IN GCP SECRET MANAGER")

if __name__ == "__main__":
    main()
