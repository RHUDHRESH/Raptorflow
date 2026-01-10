"""
Local testing configuration for Raptorflow Cloud Scraper
This file contains local overrides and mock services for testing without Google Cloud
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from unittest.mock import Mock, patch

# Configure logging for local testing
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Local configuration
LOCAL_CONFIG = {
    "GOOGLE_CLOUD_PROJECT": "raptorflow-local-test",
    "BUCKET_NAME": "local-test-bucket",
    "TOPIC_NAME": "local-test-topic",
    "PORT": 8080,
    "MAX_CONTENT_LENGTH": 10000000,
    "LOCAL_MODE": True,
}

# Set environment variables for local testing
for key, value in LOCAL_CONFIG.items():
    os.environ[key] = str(value)


class MockStorageClient:
    """Mock Cloud Storage client for local testing"""

    def __init__(self):
        self.local_storage = {}
        self.bucket_name = LOCAL_CONFIG["BUCKET_NAME"]

    def bucket(self, name):
        return MockBucket(name, self.local_storage)

    class bucket:
        def __init__(self, name):
            self.name = name


class MockBucket:
    """Mock Cloud Storage bucket"""

    def __init__(self, name, storage_dict):
        self.name = name
        self.storage = storage_dict

    def blob(self, filename):
        return MockBlob(filename, self.name, self.storage)

    def list_blobs(self, prefix=None):
        # Return mock blobs for testing
        return []


class MockBlob:
    """Mock Cloud Storage blob"""

    def __init__(self, filename, bucket_name, storage_dict):
        self.filename = filename
        self.bucket_name = bucket_name
        self.storage = storage_dict
        self.public_url = f"http://localhost:8080/mock-storage/{filename}"

    def upload_from_string(self, content, content_type=None):
        key = f"{self.bucket_name}/{self.filename}"
        self.storage[key] = {
            "content": content,
            "content_type": content_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(f"📁 Mock storage: Saved {key} ({len(content)} bytes)")

    def download_as_text(self):
        key = f"{self.bucket_name}/{self.filename}"
        if key in self.storage:
            return self.storage[key]["content"]
        raise FileNotFoundError(f"File {self.filename} not found in mock storage")

    def exists(self):
        key = f"{self.bucket_name}/{self.filename}"
        return key in self.storage

    def make_public(self):
        pass


class MockPubSubClient:
    """Mock Pub/Sub client for local testing"""

    def __init__(self):
        self.messages = []

    def topic_path(self, project_id, topic_name):
        return f"projects/{project_id}/topics/{topic_name}"

    def publish(self, topic_path, data):
        message_id = f"msg-{len(self.messages)}"
        self.messages.append(
            {
                "id": message_id,
                "topic": topic_path,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        print(f"📨 Mock Pub/Sub: Published message to {topic_path}")

        class MockFuture:
            def result(self):
                return message_id

        return MockFuture()


class MockLoggingClient:
    """Mock Cloud Logging client"""

    def setup_logging(self):
        print("📝 Mock logging: Setup complete")


def setup_local_mocks():
    """Setup all mock services for local testing"""

    # Patch Google Cloud clients
    storage_patch = patch("scraper_service.storage_client", MockStorageClient())
    pubsub_patch = patch("scraper_service.publisher", MockPubSubClient())
    logging_patch = patch("scraper_service.logging_client", MockLoggingClient())

    # Start patches
    storage_patch.start()
    pubsub_patch.start()
    logging_patch.start()

    print("🔧 Mock services initialized for local testing")
    print("📁 Storage: Local file system")
    print("📨 Pub/Sub: Local message queue")
    print("📝 Logging: Console output")

    return storage_patch, pubsub_patch, logging_patch


def create_local_test_data():
    """Create test data for local testing"""

    test_urls = [
        "https://www.pepsico.com/en/",
        "https://www.coca-cola.com/",
        "https://www.nestle.com/",
        "https://example.com/",
        "https://httpbin.org/html",
    ]

    test_users = ["test-user-1", "test-user-2", "admin-user"]

    return test_urls, test_users


def run_local_tests(base_url="http://localhost:8080"):
    """Run local tests against the scraper service"""

    import httpx

    print(f"🧪 Running local tests against {base_url}")

    test_urls, test_users = create_local_test_data()

    with httpx.Client() as client:
        # Test health endpoint
        try:
            response = client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

        # Test scraping endpoint
        for i, (url, user_id) in enumerate(zip(test_urls[:2], test_users[:2])):
            try:
                print(f"🕷️ Testing scrape {i+1}: {url}")

                response = client.post(
                    f"{base_url}/scrape",
                    json={"url": url, "user_id": user_id, "legal_basis": "testing"},
                    timeout=60.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Scrape {i+1} successful")
                    print(f"   Title: {result.get('title', 'N/A')}")
                    print(f"   Content length: {result.get('content_length', 0)}")
                    print(
                        f"   Processing time: {result.get('processing_time', 0):.2f}s"
                    )
                    print(f"   Status: {result.get('status', 'unknown')}")
                else:
                    print(f"❌ Scrape {i+1} failed: {response.status_code}")
                    print(f"   Error: {response.text}")

            except Exception as e:
                print(f"❌ Scrape {i+1} error: {e}")

        # Test stats endpoint
        try:
            response = client.get(f"{base_url}/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"📊 Stats: {stats}")
            else:
                print(f"❌ Stats failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Stats error: {e}")

    print("🎉 Local tests completed!")
    return True


if __name__ == "__main__":
    # Setup local environment
    setup_local_mocks()

    # Print configuration
    print("🔧 Local Configuration:")
    for key, value in LOCAL_CONFIG.items():
        print(f"   {key}: {value}")
    print()

    # Run tests if service is running
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_local_tests()
