import base64
import hashlib
import json
from typing import Any, Dict

from backend.core.config import get_settings


class PaymentService:
    """
    SOTA PhonePe Payment Gateway Integration.
    Handles transaction initiation, status verification, and webhook validation.
    """

    def __init__(self):
        self.settings = get_settings()
        self.merchant_id = self.settings.PHONEPE_MERCHANT_ID
        self.salt_key = self.settings.PHONEPE_SALT_KEY
        self.salt_index = self.settings.PHONEPE_SALT_INDEX
        self.base_url = "https://api.phonepe.com/apis/hermes"  # Change for UAT/Prod

    def _generate_checksum(self, payload_base64: str, endpoint: str) -> str:
        """Generates X-VERIFY checksum for PhonePe requests."""
        main_string = payload_base64 + endpoint + self.salt_key
        sha256 = hashlib.sha256(main_string.encode("utf-8")).hexdigest()
        return f"{sha256}###{self.salt_index}"

    def initiate_payment(
        self, user_id: str, amount: float, transaction_id: str, redirect_url: str
    ) -> Dict[str, Any]:
        """Initiates a payment request with PhonePe."""
        payload = {
            "merchantId": self.merchant_id,
            "merchantTransactionId": transaction_id,
            "merchantUserId": user_id,
            "amount": int(amount * 100),  # amount in paise
            "redirectUrl": redirect_url,
            "redirectMode": "POST",
            "callbackUrl": f"{self.settings.NEXT_PUBLIC_API_URL}/v1/payments/webhook",
            "paymentInstrument": {"type": "PAY_PAGE"},
        }

        payload_json = json.dumps(payload)
        payload_base64 = base64.b64encode(payload_json.encode("utf-8")).decode("utf-8")

        checksum = self._generate_checksum(payload_base64, "/pg/v1/pay")

        # For now, return the payload and headers for the frontend to use
        return {
            "url": f"{self.base_url}/pg/v1/pay",
            "payload": payload_base64,
            "checksum": checksum,
        }

    def verify_webhook(self, x_verify: str, response_payload: str) -> bool:
        """Validates the authenticity of the PhonePe webhook callback."""
        # Main string = base64 response + salt key
        main_string = response_payload + self.salt_key
        sha256 = hashlib.sha256(main_string.encode("utf-8")).hexdigest()
        calculated_checksum = f"{sha256}###{self.salt_index}"
        return calculated_checksum == x_verify


payment_service = PaymentService()
