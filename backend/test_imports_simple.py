#!/usr/bin/env python3
"""Test script to verify payment service imports work correctly"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing imports...")

    # Test email service directly
    import services.email_service

    print("✅ Email service import: OK")

    # Test payment service directly
    import services.payment_service

    print("✅ Payment service import: OK")

    # Test core auth directly
    import core.auth

    print("✅ Core auth import: OK")

    # Test supabase manager directly
    import core.supabase_mgr

    print("✅ Supabase manager import: OK")

    # Test models directly
    import core.models

    print("✅ Core models import: OK")

    print("\nAll critical imports working correctly!")

except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
