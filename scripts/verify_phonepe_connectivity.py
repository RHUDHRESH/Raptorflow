import os
import uuid
import logging
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.env import Env
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_connectivity():
    merchant_id = os.getenv("PHONEPE_MERCHANT_ID") or os.getenv("PHONEPE_CLIENT_ID")
    salt_key = os.getenv("PHONEPE_SALT_KEY")
    salt_index = int(os.getenv("PHONEPE_SALT_INDEX", "1"))
    
    if not merchant_id or not salt_key:
        print("❌ Error: Missing credentials in .env")
        return

    print(f"Testing connectivity for Merchant ID: {merchant_id}")
    
    try:
        # Initialize Client
        client = StandardCheckoutClient(
            client_id=merchant_id,
            client_version=int(os.getenv("PHONEPE_CLIENT_VERSION", "1")),
            client_secret=salt_key,
            env=Env.SANDBOX,
            should_publish_events=True
        )
        
        # Create a dummy payment request
        txn_id = f"TEST_{uuid.uuid4().hex[:10]}"
        pay_request = StandardCheckoutPayRequest.build_request(
            merchant_order_id=txn_id,
            amount=100, # 1 INR
            redirect_url="https://raptorflow.in/payment/status"
        )
        
        print(f"Initiating test payment {txn_id}...")
        response = client.pay(pay_request)
        
        print(f"Success!")
        print(f"State: {response.state}")
        print(f"Order ID: {response.order_id}")
        print(f"Checkout URL: {response.redirect_url}")
            
    except Exception as e:
        print(f"Connectivity test failed: {e}")
        # Log full traceback for debugging if needed
        # logger.exception(e)

if __name__ == "__main__":
    verify_connectivity()
