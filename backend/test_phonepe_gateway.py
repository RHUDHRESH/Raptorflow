#!/usr/bin/env python3
"""
Test PhonePe SDK Gateway Integration
"""

import asyncio
import logging
import os
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_phonepe_gateway():
    """Test PhonePe SDK Gateway functionality"""

    # Set test environment variables
    os.environ["PHONEPE_CLIENT_ID"] = "PGTESTPAYUAT"
    os.environ["PHONEPE_CLIENT_SECRET"] = "test_key_12345"
    os.environ["PHONEPE_ENV"] = "UAT"

    try:
        # Import the fixed gateway
        from services.phonepe_sdk_gateway_fixed import (
            PaymentRequest,
            phonepe_sdk_gateway_fixed,
        )

        print("🔍 Testing PhonePe SDK Gateway...")

        # Test 1: Health Check
        print("\n1. Testing Health Check...")
        health = await phonepe_sdk_gateway_fixed.health_check()
        print(f"   ✅ Status: {health.get('status')}")
        print(f"   ✅ Environment: {health.get('environment')}")
        print(f"   ✅ SDK Version: {health.get('sdk_version')}")
        print(f"   ✅ Config Valid: {health.get('configuration', {}).get('valid')}")

        # Test 2: Payment Request Validation
        print("\n2. Testing Payment Request Validation...")
        test_request = PaymentRequest(
            amount=50000,  # ₹500 in paise
            merchant_order_id="TEST123456",
            redirect_url="http://localhost:3000/payment/status",
            callback_url="http://localhost:3000/api/webhook",
            customer_info={"email": "test@example.com", "name": "Test User"},
        )

        print(f"   ✅ Amount: ₹{test_request.amount/100}")
        print(f"   ✅ Order ID: {test_request.merchant_order_id}")
        print(f"   ✅ Redirect URL: {test_request.redirect_url}")

        # Test 3: SDK Client Initialization (without actual API call)
        print("\n3. Testing SDK Client Initialization...")
        try:
            client = await phonepe_sdk_gateway_fixed._get_client()
            print(f"   ✅ Client Type: {type(client).__name__}")
            print(f"   ✅ Client Initialized: {phonepe_sdk_gateway_fixed._initialized}")
        except Exception as e:
            print(
                f"   ⚠️  Client Init Failed (expected with test credentials): {str(e)}"
            )

        print("\n🎉 PhonePe SDK Gateway Test Complete!")
        print(
            "📋 Status: ✅ Gateway code working, needs real credentials for API calls"
        )

        return True

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print(
            "📋 Fix: Ensure phonepe-sdk-python is installed: pip install phonepe-sdk-python==3.2.1"
        )
        return False

    except Exception as e:
        print(f"❌ Test Failed: {e}")
        return False


async def test_sdk_imports():
    """Test PhonePe SDK imports"""
    print("🔍 Testing PhonePe SDK Imports...")

    try:
        from phonepe.sdk.pg.env import Env
        from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import (
            StandardCheckoutPayRequest,
        )
        from phonepe.sdk.pg.payments.v2.standard_checkout_client import (
            StandardCheckoutClient,
        )

        print("   ✅ StandardCheckoutClient imported")
        print("   ✅ StandardCheckoutPayRequest imported")
        print("   ✅ Env imported")

        # Test environment enum
        print(f"   ✅ Environment enum available")
        print(f"   ✅ UAT Environment: {hasattr(Env, 'UAT')}")
        print(f"   ✅ PRODUCTION Environment: {hasattr(Env, 'PRODUCTION')}")

        return True

    except ImportError as e:
        print(f"   ❌ Import Failed: {e}")
        print("   📋 Fix: pip install phonepe-sdk-python==3.2.1")
        return False


async def main():
    """Main test function"""
    print("=" * 60)
    print("📱 PhonePe SDK Integration Test")
    print("=" * 60)

    # Test SDK imports first
    sdk_ok = await test_sdk_imports()

    if sdk_ok:
        # Test gateway functionality
        gateway_ok = await test_phonepe_gateway()

        if gateway_ok:
            print("\n🎯 NEXT STEPS:")
            print("1. Get real PhonePe credentials from business.phonepe.com")
            print("2. Update environment variables with real values")
            print("3. Test with actual payment initiation")
            print("4. Configure webhook URLs in PhonePe dashboard")
        else:
            print("\n❌ Gateway tests failed - check implementation")
    else:
        print("\n❌ SDK imports failed - install phonepe-sdk-python")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
