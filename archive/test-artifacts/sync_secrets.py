import logging
import os

from dotenv import load_dotenv
from google.cloud import secretmanager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sync_secrets")


def get_secret(name: str, project_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    path = f"projects/{project_id}/secrets/{name}/versions/latest"
    try:
        response = client.access_secret_version(request={"name": path})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Failed to fetch {name}: {e}")
        return None


def main():
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        logger.error("GCP_PROJECT_ID not set")
        return

    keys_to_fetch = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "UPSTASH_REDIS_REST_URL",
        "UPSTASH_REDIS_REST_TOKEN",
    ]

    for key in keys_to_fetch:
        val = get_secret(key, project_id)
        if val:
            logger.info(f"Fetched {key} from GCP. Length: {len(val)}")
            current = os.getenv(key)
            if val != current:
                logger.warning(f"SECRET MISMATCH for {key}!")
                logger.info(f"  Local: {current[:10]}...")
                logger.info(f"  GCP:   {val[:10]}...")
            else:
                logger.info(f"{key} matches GCP version.")
        else:
            logger.warning(f"Could not find {key} in GCP Secret Manager.")


if __name__ == "__main__":
    main()
