import logging
from datetime import datetime
from typing import Set
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from core.auth import get_current_user, get_tenant_id
from core.config import get_settings
from db import get_db_connection
from services.payment_service import PhonePeCallbackError, payment_service

logger = logging.getLogger("raptorflow.payments")
router = APIRouter(prefix="/v1/payments", tags=["Payments"])


class PaymentInitiateRequest(BaseModel):
    amount: float = Field(..., gt=0)
    transaction_id: str
    redirect_url: str


class PaymentCreateRequest(BaseModel):
    plan_id: str = Field(..., description="Plan ID to subscribe to")
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="INR", description="Currency code")
    return_url: str = Field(default=None, description="URL to redirect after payment")
    callback_url: str = Field(
        default=None, description="Callback URL for payment notifications"
    )
    promo_code: str | None = Field(default=None, description="Optional promo code")


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


@router.post("/create")
async def create_payment(
    payload: PaymentCreateRequest,
    current_user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_tenant_id),
):
    """Create a PhonePe payment session for subscription."""
    try:
        # Validate plan exists and is active
        promo_code = payload.promo_code.strip() if payload.promo_code else None
        discount_amount = 0.0
        final_amount = payload.amount
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, name, price, currency FROM plans
                    WHERE id = %s AND is_active = true
                """,
                    (payload.plan_id,),
                )
                plan = await cur.fetchone()

                if not plan:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Plan {payload.plan_id} not found or inactive",
                    )

                plan_price = float(plan[2])
                final_amount = plan_price

                if promo_code:
                    await cur.execute(
                        """
                        SELECT percent_off, amount_off, currency, max_redemptions,
                               redemption_count, active, starts_at, expires_at
                        FROM promo_codes
                        WHERE LOWER(code) = LOWER(%s)
                    """,
                        (promo_code,),
                    )
                    promo = await cur.fetchone()
                    if not promo:
                        raise HTTPException(
                            status_code=404, detail="Promo code not found."
                        )

                    (
                        percent_off,
                        amount_off,
                        promo_currency,
                        max_redemptions,
                        redemption_count,
                        active,
                        starts_at,
                        expires_at,
                    ) = promo

                    if not active:
                        raise HTTPException(
                            status_code=400, detail="Promo code is inactive."
                        )
                    if promo_currency and promo_currency != payload.currency:
                        raise HTTPException(
                            status_code=400,
                            detail="Promo code currency mismatch.",
                        )
                    if starts_at and starts_at > datetime.utcnow():
                        raise HTTPException(
                            status_code=400, detail="Promo code not active yet."
                        )
                    if expires_at and expires_at < datetime.utcnow():
                        raise HTTPException(
                            status_code=400, detail="Promo code has expired."
                        )
                    if max_redemptions is not None and redemption_count is not None:
                        if redemption_count >= max_redemptions:
                            raise HTTPException(
                                status_code=400,
                                detail="Promo code redemption limit reached.",
                            )

                    if percent_off:
                        discount_amount = plan_price * (float(percent_off) / 100.0)
                    elif amount_off:
                        discount_amount = float(amount_off)

                    discount_amount = min(discount_amount, plan_price)
                    final_amount = round(plan_price - discount_amount, 2)

                if abs(payload.amount - final_amount) > 0.01:
                    logger.warning(
                        "Payment amount mismatch: requested %.2f, computed %.2f",
                        payload.amount,
                        final_amount,
                    )

        result = await payment_service.create_payment_session(
            workspace_id=workspace_id,
            plan_id=payload.plan_id,
            amount=final_amount,
            currency=payload.currency,
            return_url=payload.return_url,
            callback_url=payload.callback_url,
            promo_code=promo_code,
            discount_amount=discount_amount if discount_amount else None,
        )

        return {
            "status": "success",
            "payment_url": result["payment_url"],
            "order_id": result["merchant_order_id"],
            "transaction_id": result["transaction_id"],
            "amount": final_amount,
            "discount_amount": discount_amount if discount_amount else 0,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create payment session: {str(e)}"
        )


@router.get("/plans")
async def list_plans():
    """Return active subscription plans for pricing page."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, name, description, price, currency, billing_interval, features,
                       max_campaigns, max_users, max_icp_profiles
                FROM plans
                WHERE is_active = true
                ORDER BY price ASC
                """
            )
            rows = await cur.fetchall()

    plans = [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": float(row[3]) if row[3] is not None else 0.0,
            "currency": row[4] or "INR",
            "billing_interval": row[5] or "monthly",
            "features": row[6] or {},
            "max_campaigns": row[7],
            "max_users": row[8],
            "max_icp_profiles": row[9],
        }
        for row in rows
    ]

    return {"status": "success", "data": {"plans": plans}}


@router.post("/confirm/{merchant_order_id}")
async def confirm_payment(
    merchant_order_id: str,
    _current_user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_tenant_id),
):
    """Confirm payment after redirect if webhook auth is not configured."""
    try:
        result = await payment_service.confirm_payment_session(
            workspace_id, merchant_order_id
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Payment confirmation failed: {str(exc)}"
        ) from exc


@router.get("/callback")
async def payment_callback(request: Request):
    """Handle PhonePe payment callback."""
    authorization = request.headers.get("authorization")
    if not authorization:
        raise HTTPException(status_code=400, detail="Missing Authorization header")

    response_body = (await request.body()).decode("utf-8")

    try:
        result = await payment_service.handle_payment_callback(
            authorization, response_body
        )
        return result
    except PhonePeCallbackError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Callback processing failed: {str(e)}"
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
    PhonePe Webhook Handler for asynchronous payment notifications.
    Validates callback authenticity using the SDK and updates transaction state.
    """
    authorization = request.headers.get("authorization")
    if not authorization:
        raise HTTPException(status_code=400, detail="Missing Authorization header")

    response_body = (await request.body()).decode("utf-8")

    try:
        result = await payment_service.handle_payment_callback(
            authorization, response_body
        )

        # Log webhook processing for monitoring
        logger.info(f"Webhook processed: {result}")

        return result
    except PhonePeCallbackError as exc:
        logger.error(f"Webhook validation failed: {exc}")
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ValueError as exc:
        logger.error(f"Webhook data validation failed: {exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Webhook processing failed: {str(e)}"
        )


@router.post("/webhook/test")
async def test_webhook():
    """Test endpoint for webhook configuration validation."""
    return {"status": "webhook endpoint is active"}
