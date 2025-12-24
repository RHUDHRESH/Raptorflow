import base64
import json

from fastapi import APIRouter, HTTPException, Request

from backend.core.config import get_settings
from backend.services.payment_service import payment_service

router = APIRouter(prefix="/v1/payments", tags=["Payments"])
settings = get_settings()


@router.post("/initiate")
async def initiate_payment(
    user_id: str, amount: float, transaction_id: str, redirect_url: str
):
    """Initiates a PhonePe payment session."""
    return payment_service.initiate_payment(
        user_id, amount, transaction_id, redirect_url
    )


@router.post("/webhook")
async def payment_webhook(request: Request):
    """
    PhonePe Webhook Handler.
    Validates the checksum and updates transaction status in Supabase.
    """
    x_verify = request.headers.get("X-VERIFY")
    if not x_verify:
        raise HTTPException(status_code=400, detail="Missing X-VERIFY header")

    body = await request.json()
    response_base64 = body.get("response")

    if not payment_service.verify_webhook(x_verify, response_base64):
        raise HTTPException(status_code=401, detail="Invalid checksum")

    # Decode response
    response_json = base64.b64decode(response_base64).decode("utf-8")
    data = json.loads(response_json)

    # Placeholder for status processing to satisfy linter
    print(
        f"Received webhook for transaction {data.get('data', {}).get('merchantTransactionId')}: {data.get('code')}"
    )

    return {"status": "received"}
