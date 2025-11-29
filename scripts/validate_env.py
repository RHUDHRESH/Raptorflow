#!/usr/bin/env python3
"""
Environment Validation Script for Production Deployment.
Checks for required environment variables and configuration validity.
"""

import os
import sys
from urllib.parse import urlparse

REQUIRED_VARS = [
    "GOOGLE_CLOUD_PROJECT",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_KEY",
    "REDIS_URL",
    "SECRET_KEY",
    "ENVIRONMENT"
]

OPTIONAL_VARS = [
    "VERTEX_AI_LOCATION",
    "SUPABASE_JWT_SECRET",
    "SENTRY_DSN"
]

def validate_url(url: str, name: str) -> bool:
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            print(f"❌ {name} is not a valid URL: {url}")
            return False
        return True
    except Exception:
        print(f"❌ {name} is invalid")
        return False

def main():
    print("🔍 Validating environment configuration...")
    
    missing = []
    for var in REQUIRED_VARS:
        value = os.environ.get(var)
        if not value:
            missing.append(var)
        else:
            # Mask secrets
            if "KEY" in var or "SECRET" in var:
                print(f"✅ {var} is set (***)")
            else:
                print(f"✅ {var} = {value}")

    if missing:
        print(f"\n❌ Missing required environment variables:\n" + "\n".join(missing))
        sys.exit(1)

    # Validate URLs
    valid_config = True
    if not validate_url(os.environ["SUPABASE_URL"], "SUPABASE_URL"):
        valid_config = False
    
    redis_url = os.environ["REDIS_URL"]
    if not redis_url.startswith("redis://") and not redis_url.startswith("rediss://"):
        print(f"❌ REDIS_URL must start with redis:// or rediss://")
        valid_config = False

    if not valid_config:
        print("\n❌ Configuration validation failed.")
        sys.exit(1)

    print("\n✅ Environment validation passed! Ready for deployment.")

if __name__ == "__main__":
    main()
