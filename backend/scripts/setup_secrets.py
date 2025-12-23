import argparse
from google.cloud import secretmanager


def setup_secret(project_id: str, secret_id: str, secret_value: str):
    """
    Creates or updates a secret in GCP Secret Manager.
    """
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project_id}"

    # 1. Create the secret if it doesn't exist
    try:
        client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            }
        )
        print(f"Created secret {secret_id}")
    except Exception:
        print(f"Secret {secret_id} already exists")

    # 2. Add a new version
    secret_path = f"projects/{project_id}/secrets/{secret_id}"
    client.add_secret_version(
        request={"parent": secret_path, "payload": {"data": secret_value.encode("UTF-8")}}
    )
    print(f"Added new version to {secret_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup GCP Secrets for Blackbox")
    parser.add_argument("--project", help="GCP Project ID", required=True)
    parser.add_argument("--search_key", help="Search API Key", required=True)
    parser.add_argument("--scrape_key", help="Scrape API Key", required=True)

    args = parser.parse_args()

    setup_secret(args.project, "blackbox_search_key", args.search_key)
    setup_secret(args.project, "blackbox_scrape_key", args.scrape_key)
