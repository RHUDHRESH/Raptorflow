"""
Payments Domain - Router
API routes for payments and subscriptions
"""

from typing import Any, Dict, List

from dependencies import PaymentService, get_payments, require_workspace_id
from fastapi import APIRouter, Depends, HTTPException, Request
from infrastructure.database import get_supabase
from pydantic import BaseModel

router = APIRouter()


# Request/Response schemas
class CreatePaymentRequest(BaseModel):
    plan: str
    amount: int
    customer_email: str
    customer_name: str = None
    redirect_url: str = None


class PaymentResponse(BaseModel):
    id: str
    merchant_order_id: str
    status: str
    amount: int
    currency: str
    payment_url: str = None


# Payment routes
@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    data: CreatePaymentRequest,
    workspace_id: str = Depends(require_workspace_id),
    service: PaymentService = Depends(get_payments),
):
    """Create a new payment"""
    payment = await service.create_payment(
        workspace_id=workspace_id,
        plan=data.plan,
        amount=data.amount,
        customer_email=data.customer_email,
        customer_name=data.customer_name,
        redirect_url=data.redirect_url,
    )

    if not payment:
        raise HTTPException(status_code=400, detail="Failed to create payment")

    return PaymentResponse(
        id=payment.id,
        merchant_order_id=payment.merchant_order_id,
        status=payment.status,
        amount=payment.amount,
        currency=payment.currency,
        payment_url=payment.payment_url,
    )


@router.get("/status/{merchant_order_id}")
async def check_payment_status(
    merchant_order_id: str, service: PaymentService = Depends(get_payments)
):
    """Check payment status"""
    payment = await service.verify_payment(merchant_order_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return {
        "id": payment.id,
        "status": payment.status,
        "amount": payment.amount,
        "plan": payment.plan,
    }


@router.post("/webhook")
async def payment_webhook(
    request: Request, service: PaymentService = Depends(get_payments)
):
    """Handle PhonePe webhook"""
    payload = await request.json()

    success = await service.handle_webhook(payload)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to process webhook")

    return {"success": True}


@router.get("/history")
async def get_payment_history(
    workspace_id: str = Depends(require_workspace_id),
):
    """Get payment history for workspace"""
    db = get_supabase()
    result = await db.select("payments", {"workspace_id": workspace_id})

    return result.data or []


@router.get("/subscription")
async def get_subscription(
    workspace_id: str = Depends(require_workspace_id),
):
    """Get current subscription"""
    db = get_supabase()
    result = await db.select(
        "subscriptions", {"workspace_id": workspace_id, "status": "active"}, limit=1
    )

    if result.data:
        return result.data[0]
    return None
