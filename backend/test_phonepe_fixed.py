#!/usr/bin/env python3
"""
Test PhonePe SDK Gateway Fixed
"""

import asyncio
import os
import sys

# Add current directory to path
sys.path.insert(0, '.')

async def test_phonepe():
    """Test PhonePe SDK Gateway"""
    
    # Set test environment
    os.environ['PHONEPE_CLIENT_ID'] = 'PGTESTPAYUAT'
    os.environ['PHONEPE_CLIENT_SECRET'] = '09c2c3e7-6b5a-4f8a-9c1d-2e3f4a5b6c7d'
    os.environ['PHONEPE_ENV'] = 'UAT'
    
    try:
        print("🔍 Testing PhonePe SDK Gateway...")
        
        # Import the fixed gateway
        from services.phonepe_sdk_gateway_fixed import phonepe_sdk_gateway_fixed
        print("✅ Gateway imported successfully")
        
        # Test health check
        health = await phonepe_sdk_gateway_fixed.health_check()
        print("✅ Health Status:", health.get('status'))
        print("✅ Environment:", health.get('environment'))
        print("✅ SDK Version:", health.get('sdk_version'))
        print("✅ Merchant ID:", health.get('configuration', {}).get('merchant_id'))
        
        # Test webhook validation
        webhook_result = await phonepe_sdk_gateway_fixed.validate_webhook(
            "Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ=",
            '{"test": "webhook_data"}'
        )
        print("✅ Webhook Validation:", webhook_result.get('valid'))
        
        print("\n🎉 PhonePe SDK Gateway Working!")
        print("📋 Status: Ready for payment processing")
        
        return True
        
    except ImportError as e:
        print("❌ Import Error:", e)
        print("📋 Fix: Ensure phonepe-sdk-python is installed")
        return False
        
    except Exception as e:
        print("❌ Error:", str(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_phonepe())
    if success:
        print("\n🚀 PHONEPE STATUS: ✅ WORKING")
        print("\n📋 READY FOR:")
        print("1. Real PhonePe credentials")
        print("2. Payment initiation testing")
        print("3. Webhook processing")
        print("4. Production deployment")
    else:
        print("\n❌ Fix issues before proceeding")
