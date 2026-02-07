from typing import Set
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from core.auth import get_current_user
from core.config import get_settings
from services.payment_service import PhonePeCallbackError, payment_service

router = APIRouter(prefix="/v1/payments", tags=["Payments"])


class PaymentInitiateRequest(BaseModel):
    amount: float = Field(..., gt=0)
    transaction_id: str
    redirect_url: str


def _normalize_origin(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("redirect_url must be a valid absolute URL.")
    return f"{parsed.scheme}://{parsed.netloc}"


def _get_allowed_redirect_origins() -> Set[str]:
    settings = get_settings()
    raw_allowlist = settings.PAYMENT_REDIRECT_ALLOWLIST
    allowed = {
        _normalize_origin(entry.strip())
        for entry in raw_allowlist.split(",")
        if entry.strip()
    }
    return allowed


@router.post("/initiate")
async def initiate_payment(
    payload: PaymentInitiateRequest,
    _current_user: dict = Depends(get_current_user),
):
    """Initiates a PhonePe payment session."""
    try:
        redirect_origin = _normalize_origin(payload.redirect_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        allowed_origins = _get_allowed_redirect_origins()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    if not allowed_origins:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Redirect allowlist is not configured.",
        )

    if redirect_origin not in allowed_origins:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="redirect_url is not in the allowlist.",
        )

    # RBI compliance: Autopay only allowed for amounts ≤ ₹5,000
    if payload.amount > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount exceeds ₹5,000 limit for autopay payments per RBI regulations.",
        )

    if (
        payload.transaction_id in payment_service.initiated_orders
        or payload.transaction_id in payment_service.processed_orders
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="transaction_id has already been used.",
        )

    user_id = _current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user is missing an id.",
        )

    return payment_service.initiate_payment(
        user_id, payload.amount, payload.transaction_id, payload.redirect_url
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
