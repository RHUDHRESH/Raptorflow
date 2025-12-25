from fastapi import APIRouter, Depends, HTTPException, Request

from backend.core.auth import get_current_user
from backend.services.payment_service import PhonePeCallbackError, payment_service

router = APIRouter(prefix="/v1/payments", tags=["Payments"])


@router.post("/initiate")
async def initiate_payment(
    user_id: str,
    amount: float,
    transaction_id: str,
    redirect_url: str,
    _current_user: dict = Depends(get_current_user),
):
    """Initiates a PhonePe payment session."""
    return payment_service.initiate_payment(
        user_id, amount, transaction_id, redirect_url
    )


@router.get("/status/{merchant_order_id}")
async def get_payment_status(
    merchant_order_id: str, _current_user: dict = Depends(get_current_user)
):
    """Fetch the latest order status from PhonePe."""
    return payment_service.get_order_status(merchant_order_id)


@router.post("/webhook")
async def payment_webhook(request: Request):
    """
    PhonePe Webhook Handler.
    Validates callback authenticity using the SDK and updates transaction state.
    """
    authorization = request.headers.get("authorization")
    if not authorization:
        raise HTTPException(status_code=400, detail="Missing Authorization header")

    response_body = (await request.body()).decode("utf-8")

    try:
        return payment_service.handle_webhook(authorization, response_body)
    except PhonePeCallbackError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
