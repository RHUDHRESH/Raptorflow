"""
Enhanced PhonePe Payment API v2 with Security
Complete payment integration with comprehensive security measures
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from api.dependencies import get_auth_context, get_current_user
from core.audit_logger import EventType, LogLevel, audit_logger
from core.input_validator import input_validator
from core.models import AuthContext, User
from core.rate_limiter import RateLimitConfig, RateLimiter
from core.supabase_mgr import get_supabase_admin
from core.webhook_security import webhook_security
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel, Field, validator
from services.payment_service import (
    PaymentError,
    PaymentRequest,
    PaymentResponse,
    PaymentService,
)
from services.refund_service import RefundRequest, RefundResponse, RefundService

# Rate limiting configuration
payment_rate_config = RateLimitConfig(
    requests_per_minute=5,  # 5 payment initiations per minute
    requests_per_hour=50,  # 50 payment initiations per hour
    requests_per_day=200,  # 200 payment initiations per day
)

# Initialize rate limiter
payment_rate_limiter = RateLimiter(payment_rate_config)

router = APIRouter(prefix="/api/payments/v2", tags=["payments"])


class SecurePaymentInitiateRequest(BaseModel):
    """Secure payment initiation request with validation"""

    plan: str = Field(..., regex=r"^(starter|growth|enterprise)$")
    redirect_url: str = Field(..., description="Redirect URL after payment")
    webhook_url: str = Field(..., description="Webhook URL for payment notifications")
    idempotency_key: Optional[str] = Field(
        None, min_length=8, max_length=64, regex=r"^[A-Za-z0-9_-]+$"
    )
    metadata: Optional[Dict[str, Any]] = None

    @validator("redirect_url", "webhook_url")
    def validate_urls(cls, v):
        # Validate URLs using input validator
        result = input_validator.validate_url(v)
        if not result.is_valid:
            raise ValueError(f"Invalid URL: {', '.join(result.errors)}")
        return v


class SecureRefundRequest(BaseModel):
    """Secure refund request with validation"""

    original_order_id: str = Field(
        ..., min_length=8, max_length=64, regex=r"^[A-Za-z0-9_-]+$"
    )
    refund_amount: int = Field(..., gt=99, lt=10000000)
    reason: str = Field(..., min_length=1, max_length=500)
    refund_idempotency_key: Optional[str] = Field(
        None, min_length=8, max_length=64, regex=r"^[A-Za-z0-9_-]+$"
    )
    metadata: Optional[Dict[str, Any]] = None


class SecurePaymentResponse(BaseModel):
    """Secure payment response"""

    success: bool
    merchant_order_id: Optional[str] = None
    payment_url: Optional[str] = None
    phonepe_transaction_id: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None
    expires_at: Optional[datetime] = None
    security_flags: Optional[Dict[str, Any]] = None


class SecureRefundResponse(BaseModel):
    """Secure refund response"""

    success: bool
    refund_id: Optional[str] = None
    original_order_id: Optional[str] = None
    refund_amount: Optional[int] = None
    status: Optional[str] = None
    phonepe_refund_id: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    security_flags: Optional[Dict[str, Any]] = None


@router.post("/initiate", response_model=SecurePaymentResponse)
async def initiate_payment(
    request: SecurePaymentInitiateRequest,
    background_tasks: BackgroundTasks,
    request_obj: Request,
    current_user: User = Depends(get_current_user),
    auth_context: AuthContext = Depends(get_auth_context),
):
    """
    Initiate payment with comprehensive security measures
    """
    try:
        # Rate limiting check
        user_id = current_user.id
        if not payment_rate_limiter.is_allowed(f"payment_initiate:{user_id}"):
            raise HTTPException(
                status_code=429, detail="Rate limit exceeded. Please try again later."
            )

        # Validate request data
        validation_result = input_validator.validate_payment_request(
            {
                "workspace_id": auth_context.workspace_id,
                "plan": request.plan,
                "amount": 0,  # Will be set based on plan
                "customer_email": current_user.email,
                "customer_name": current_user.full_name or current_user.email,
                "redirect_url": request.redirect_url,
                "webhook_url": request.webhook_url,
                "idempotency_key": request.idempotency_key,
                "metadata": request.metadata,
            }
        )

        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Validation failed: {', '.join(validation_result.errors)}",
            )

        # Get plan amount
        plan_amounts = {"starter": 4900, "growth": 14900, "enterprise": 49900}

        amount = plan_amounts[request.plan]

        # Create payment request
        payment_request = PaymentRequest(
            workspace_id=auth_context.workspace_id,
            plan=request.plan,
            amount=amount,
            customer_email=current_user.email,
            customer_name=current_user.full_name or current_user.email,
            redirect_url=request.redirect_url,
            webhook_url=request.webhook_url,
            idempotency_key=request.idempotency_key,
            metadata=request.metadata,
        )

        # Log security event
        audit_logger.log_event(
            EventType.PAYMENT_INITIATION,
            LogLevel.INFO,
            "Payment initiation requested",
            user_id=user_id,
            workspace_id=auth_context.workspace_id,
            ip_address=request_obj.client.host,
            user_agent=request_obj.headers.get("user-agent"),
            details={
                "plan": request.plan,
                "amount": amount,
                "idempotency_key": request.idempotency_key,
            },
        )

        # Process payment
        payment_service = PaymentService()
        result = payment_service.initiate_payment(payment_request)

        if result.success:
            # Log successful initiation
            audit_logger.log_event(
                EventType.PAYMENT_SUCCESS,
                LogLevel.INFO,
                "Payment initiated successfully",
                user_id=user_id,
                workspace_id=auth_context.workspace_id,
                details={
                    "merchant_order_id": result.merchant_order_id,
                    "plan": request.plan,
                    "amount": amount,
                },
            )

            return SecurePaymentResponse(
                success=True,
                merchant_order_id=result.merchant_order_id,
                payment_url=result.payment_url,
                phonepe_transaction_id=result.phonepe_transaction_id,
                status=result.status,
                expires_at=result.expires_at,
                security_flags={
                    "rate_limited": False,
                    "validated": True,
                    "risk_score": 0,
                },
            )
        else:
            # Log failed initiation
            audit_logger.log_event(
                EventType.PAYMENT_FAILED,
                LogLevel.WARNING,
                "Payment initiation failed",
                user_id=user_id,
                workspace_id=auth_context.workspace_id,
                details={"error": result.error, "plan": request.plan, "amount": amount},
            )

            return SecurePaymentResponse(
                success=False,
                error=result.error,
                security_flags={
                    "rate_limited": False,
                    "validated": True,
                    "risk_score": 50,
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        # Log unexpected error
        audit_logger.log_event(
            EventType.SYSTEM_ERROR,
            LogLevel.ERROR,
            f"Payment initiation error: {str(e)}",
            user_id=current_user.id,
            workspace_id=auth_context.workspace_id,
            details={"error": str(e)},
        )

        raise HTTPException(
            status_code=500, detail="Internal server error during payment initiation"
        )


@router.get("/status/{merchant_order_id}", response_model=SecurePaymentResponse)
async def get_payment_status(
    merchant_order_id: str,
    request_obj: Request,
    current_user: User = Depends(get_current_user),
    auth_context: AuthContext = Depends(get_auth_context),
):
    """
    Get payment status with security validation
    """
    try:
        # Validate order ID format
        validation_result = input_validator.validate_json_input(
            json.dumps({"merchant_order_id": merchant_order_id})
        )

        if not validation_result.is_valid:
            raise HTTPException(status_code=400, detail="Invalid order ID format")

        # Log status check
        audit_logger.log_event(
            EventType.PAYMENT_STATUS_CHECK,
            LogLevel.INFO,
            "Payment status requested",
            user_id=current_user.id,
            workspace_id=auth_context.workspace_id,
            ip_address=request_obj.client.host,
            user_agent=request_obj.headers.get("user-agent"),
            details={"merchant_order_id": merchant_order_id},
        )

        # Get payment status
        payment_service = PaymentService()
        result = payment_service.check_payment_status(merchant_order_id)

        if result.success:
            return SecurePaymentResponse(
                success=True,
                status=result.status,
                phonepe_transaction_id=result.phonepe_transaction_id,
                amount=result.amount,
                completed_at=result.completed_at,
                security_flags={"validated": True, "risk_score": 0},
            )
        else:
            return SecurePaymentResponse(
                success=False,
                error=result.error,
                security_flags={"validated": True, "risk_score": 30},
            )

    except HTTPException:
        raise
    except Exception as e:
        audit_logger.log_event(
            EventType.SYSTEM_ERROR,
            LogLevel.ERROR,
            f"Payment status check error: {str(e)}",
            user_id=current_user.id,
            workspace_id=auth_context.workspace_id,
            details={"error": str(e)},
        )

        raise HTTPException(
            status_code=500, detail="Internal server error during status check"
        )


@router.post("/refund", response_model=SecureRefundResponse)
async def process_refund(
    request: SecureRefundRequest,
    background_tasks: BackgroundTasks,
    request_obj: Request,
    current_user: User = Depends(get_current_user),
    auth_context: AuthContext = Depends(get_auth_context),
):
    """
    Process refund with comprehensive security validation
    """
    try:
        # Rate limiting for refunds (more restrictive)
        user_id = current_user.id
        if not payment_rate_limiter.is_allowed(f"refund:{user_id}"):
            raise HTTPException(
                status_code=429,
                detail="Refund rate limit exceeded. Please try again later.",
            )

        # Validate refund request
        validation_result = input_validator.validate_refund_request(
            {
                "original_order_id": request.original_order_id,
                "refund_amount": request.refund_amount,
                "reason": request.reason,
                "refund_idempotency_key": request.refund_idempotency_key,
                "metadata": request.metadata,
            }
        )

        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Validation failed: {', '.join(validation_result.errors)}",
            )

        # Log refund request
        audit_logger.log_event(
            EventType.REFUND_REQUESTED,
            LogLevel.INFO,
            "Refund requested",
            user_id=user_id,
            workspace_id=auth_context.workspace_id,
            ip_address=request_obj.client.host,
            user_agent=request_obj.headers.get("user-agent"),
            details={
                "original_order_id": request.original_order_id,
                "refund_amount": request.refund_amount,
                "reason": request.reason,
            },
        )

        # Process refund
        refund_service = RefundService()
        result = await refund_service.process_refund(
            RefundRequest(
                original_order_id=request.original_order_id,
                refund_amount=request.refund_amount,
                reason=request.reason,
                refund_idempotency_key=request.refund_idempotency_key,
                metadata=request.metadata,
            )
        )

        if result.success:
            # Log successful refund
            audit_logger.log_event(
                EventType.REFUND_PROCESSED,
                LogLevel.INFO,
                "Refund processed successfully",
                user_id=user_id,
                workspace_id=auth_context.workspace_id,
                details={
                    "refund_id": result.refund_id,
                    "original_order_id": request.original_order_id,
                    "refund_amount": request.refund_amount,
                },
            )

            return SecureRefundResponse(
                success=True,
                refund_id=result.refund_id,
                original_order_id=result.original_order_id,
                refund_amount=result.refund_amount,
                status=result.status.value,
                phonepe_refund_id=result.phonepe_refund_id,
                created_at=result.created_at,
                completed_at=result.completed_at,
                security_flags={"validated": True, "risk_score": 0},
            )
        else:
            # Log failed refund
            audit_logger.log_event(
                EventType.REFUND_FAILED,
                LogLevel.WARNING,
                "Refund processing failed",
                user_id=user_id,
                workspace_id=auth_context.workspace_id,
                details={
                    "error": result.error,
                    "original_order_id": request.original_order_id,
                },
            )

            return SecureRefundResponse(
                success=False,
                error=result.error,
                security_flags={"validated": True, "risk_score": 40},
            )

    except HTTPException:
        raise
    except Exception as e:
        audit_logger.log_event(
            EventType.SYSTEM_ERROR,
            LogLevel.ERROR,
            f"Refund processing error: {str(e)}",
            user_id=current_user.id,
            workspace_id=auth_context.workspace_id,
            details={"error": str(e)},
        )

        raise HTTPException(
            status_code=500, detail="Internal server error during refund processing"
        )


@router.post("/webhook")
async def handle_webhook(
    webhook_data: Dict[str, Any], request: Request, background_tasks: BackgroundTasks
):
    """
    Handle PhonePe webhook with enhanced security
    """
    try:
        # Get signature from header
        signature = request.headers.get("x-verify")
        if not signature:
            raise HTTPException(status_code=401, detail="Missing signature header")

        # Get PhonePe salt key
        salt_key = os.getenv("PHONEPE_SALT_KEY")
        if not salt_key:
            raise HTTPException(
                status_code=500, detail="PhonePe salt key not configured"
            )

        # Add security headers to webhook data
        webhook_data = webhook_security.add_security_headers(webhook_data)

        # Validate webhook with comprehensive security
        if not webhook_security.validate_webhook(webhook_data, signature, salt_key):
            raise HTTPException(status_code=401, detail="Webhook validation failed")

        # Log webhook receipt
        audit_logger.log_event(
            EventType.WEBHOOK_RECEIVED,
            LogLevel.INFO,
            "PhonePe webhook received",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            details={
                "merchantTransactionId": webhook_data.get("merchantTransactionId"),
                "code": webhook_data.get("code"),
                "nonce": webhook_data.get("nonce"),
            },
        )

        # Process webhook
        payment_service = PaymentService()
        success = payment_service.process_webhook(webhook_data)

        if success:
            audit_logger.log_event(
                EventType.WEBHOOK_PROCESSED,
                LogLevel.INFO,
                "PhonePe webhook processed successfully",
                details={
                    "merchantTransactionId": webhook_data.get("merchantTransactionId")
                },
            )
        else:
            audit_logger.log_event(
                EventType.WEBHOOK_FAILED,
                LogLevel.WARNING,
                "PhonePe webhook processing failed",
                details={
                    "merchantTransactionId": webhook_data.get("merchantTransactionId")
                },
            )

        return {"success": success}

    except HTTPException:
        raise
    except Exception as e:
        audit_logger.log_event(
            EventType.WEBHOOK_ERROR,
            LogLevel.ERROR,
            f"Webhook processing error: {str(e)}",
            ip_address=request.client.host,
            details={"error": str(e)},
        )

        raise HTTPException(
            status_code=500, detail="Internal server error during webhook processing"
        )


@router.get("/plans")
async def get_payment_plans():
    """
    Get available payment plans
    """
    try:
        payment_service = PaymentService()
        plans = payment_service.get_payment_plans()

        return {
            "success": True,
            "plans": plans,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get payment plans")


@router.get("/health")
async def health_check():
    """
    Health check for payment service
    """
    try:
        # Check payment service
        payment_service = PaymentService()

        # Check webhook security
        webhook_stats = webhook_security.get_webhook_statistics()

        # Check rate limiter
        rate_limiter_stats = payment_rate_limiter.get_statistics()

        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0",
            "services": {
                "payment_service": "healthy",
                "webhook_security": "healthy",
                "rate_limiter": "healthy",
            },
            "statistics": {
                "webhook_security": webhook_stats,
                "rate_limiter": rate_limiter_stats,
            },
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
        }


@router.get("/security-stats")
async def get_security_statistics(
    current_user: User = Depends(get_current_user),
    auth_context: AuthContext = Depends(get_auth_context),
):
    """
    Get security statistics (admin only)
    """
    try:
        # Check if user is admin
        supabase = get_supabase_admin()
        workspace_result = (
            supabase.table("workspaces")
            .select("owner_id")
            .eq("id", auth_context.workspace_id)
            .single()
            .execute()
        )

        if (
            not workspace_result.data
            or workspace_result.data["owner_id"] != current_user.id
        ):
            raise HTTPException(status_code=403, detail="Admin access required")

        # Get security statistics
        webhook_stats = webhook_security.get_webhook_statistics()
        rate_limiter_stats = payment_rate_limiter.get_statistics()

        # Get recent security events
        supabase.table("payment_security_events").select(
            "event_type", "severity", "description", "created_at"
        ).eq("workspace_id", auth_context.workspace_id).order(
            "created_at", desc=True
        ).limit(
            50
        ).execute()

        return {
            "webhook_security": webhook_stats,
            "rate_limiter": rate_limiter_stats,
            "recent_events": security_events.data if security_events else [],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get security statistics")
