import logging
import sys

logging.basicConfig(level=logging.INFO)

try:
    print("Attempting to import PhonePe SDK v2 components...")
    # Based on the file system audit
    from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
    from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
    from phonepe.sdk.pg.env import Env
    
    print("✅ Success: PhonePe SDK v2 components imported successfully.")
    
except ImportError as e:
    print(f"❌ Error: Could not import PhonePe SDK v2 components. {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
    sys.exit(1)