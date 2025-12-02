#!/usr/bin/env python3
"""Debug configuration loading."""

import os
from dotenv import load_dotenv

# Load backend .env file specifically
load_dotenv("backend/.env")

print("Loaded backend/.env")
print(f"GOOGLE_CLOUD_PROJECT env var: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
print(f"GOOGLE_APPLICATION_CREDENTIALS env var: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")

from backend.core.config import Config

# Create fresh config instance (not cached)
config = Config()
print(f"GCP Project ID: {config.gcp_project_id}")
print(f"GCP Location: {config.gcp_location}")
print(f"Environment: {config.environment}")

# Also test the cached version
from backend.core.config import get_settings
cached_config = get_settings()
print(f"Cached GCP Project ID: {cached_config.gcp_project_id}")
