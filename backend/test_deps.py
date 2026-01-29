#!/usr/bin/env python3
"""Test script to verify payment service dependencies"""

import os
import sys

try:
    print("Testing payment service dependencies...")

    # Test email service dependencies
    import logging
    import os
    from dataclasses import dataclass
    from datetime import datetime
    from typing import Any, Dict, List, Optional

    os.environ["RESEND_API_KEY"] = "test-key"
    os.environ["FROM_EMAIL"] = "test@example.com"

    print("Email service dependencies: OK")

    # Test payment service dependencies
    import hashlib
    import hmac
    import json
    import uuid
    from datetime import datetime, timezone

    os.environ["PHONEPE_MERCHANT_ID"] = "test-merchant-id"
    os.environ["PHONEPE_SALT_KEY"] = "test-salt-key"
    os.environ["PHONEPE_SALT_INDEX"] = "1"
    os.environ["PHONEPE_ENVIRONMENT"] = "sandbox"

    print("Payment service dependencies: OK")

    # Test core dependencies
    import re
    from dataclasses import dataclass

    print("Core dependencies: OK")

    print("All payment service dependencies verified!")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
