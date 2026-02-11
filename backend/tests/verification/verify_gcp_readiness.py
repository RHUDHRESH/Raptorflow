import os
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./raptorflow-storage-key.json"
project_id = "raptorflow-481505"

def verify_gcp_storage():
    print(f"Connecting to GCP Storage for project {project_id}...")
    try:
        client = storage.Client(project=project_id)
        buckets = list(client.list_buckets(max_results=1))
        print("✅ GCP Storage connection successful!")
        if buckets:
            print(f"First bucket: {buckets[0].name}")
        else:
            print("No buckets found, but connection was successful.")
    except Exception as e:
        print(f"❌ GCP Storage connection failed: {e}")

if __name__ == "__main__":
    verify_gcp_storage()
