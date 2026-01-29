#!/usr/bin/env python3
"""Test script to verify payment service imports work correctly"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing imports...")

    # Test email service
    from services.email_service import email_service

    print("✅ Email service import: OK")

    # Test payment service
    from services.payment_service import payment_service

    print("✅ Payment service import: OK")

    # Test core auth
    from core.auth import get_current_user, get_auth_context

    print("✅ Core auth import: OK")

    # Test supabase manager
    from core.supabase_mgr import get_supabase_admin

    print("✅ Supabase manager import: OK")

    # Test models
    from core.models import User, AuthContext

    print("✅ Core models import: OK")

    print("\n🎉 All critical imports working correctly!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
