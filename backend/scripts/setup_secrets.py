import os
from google.cloud import secretmanager
from backend.core.config import get_settings

def create_secret(project_id: str, secret_id: str):
    """
    Create a new secret in the specified project.
    """
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project_id}"

    try:
        response = client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            }
        )
        print(f"Created secret: {response.name}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"Secret {secret_id} already exists.")
        else:
            print(f"Error creating secret {secret_id}: {e}")

def main():
    settings = get_settings()
    project_id = settings.GCP_PROJECT_ID
    
    secrets = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "FIRECRAWL_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "UPSTASH_REDIS_REST_URL",
        "UPSTASH_REDIS_REST_TOKEN"
    ]

    print(f"Initializing secrets for project: {project_id}")
    for secret in secrets:
        create_secret(project_id, secret)

if __name__ == "__main__":
    main()