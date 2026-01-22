"""
PhonePe Payment API Endpoints - Latest 2026 Integration
Updated to use Client ID + Client Secret authentication
REST API endpoints for PhonePe Payment Gateway - Current 2026 version
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel, EmailStr
from backend.services.phonepe_gateway import phonepe_gateway

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/payments", tags=["payments"])


# Pydantic models - Current 2026 API
class CustomerInfo(BaseModel):
    id: str
    name: str
    email: EmailStr
    mobile: str


class PaymentInitiateRequest(BaseModel):
    amount: int  # Amount in paise
    merchant_order_id: Optional[str] = None
    redirect_url: str
    callback_url: str
    customer_info: Optional[CustomerInfo] = None
    metadata: Optional[Dict[str, Any]] = None


class PaymentInitiateResponse(BaseModel):
    success: bool
    transaction_id: Optional[str] = None
    merchant_order_id: Optional[str] = None
    checkout_url: Optional[str] = None
    phonepe_transaction_id: Optional[str] = None
    amount: Optional[int] = None
    status: Optional[str] = None
    error: Optional[str] = None


class PaymentStatusResponse(BaseModel):
    success: bool
    status: Optional[str] = None
    merchant_order_id: Optional[str] = None
    amount: Optional[int] = None
    payment_instrument: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class RefundRequest(BaseModel):
    merchant_order_id: str  # Current system uses merchant order ID
    refund_amount: int
    refund_reason: str


class RefundResponse(BaseModel):
    success: bool
    refund_id: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None


@router.post("/initiate", response_model=PaymentInitiateResponse)
async def initiate_payment(
    request: PaymentInitiateRequest, background_tasks: BackgroundTasks
):
    """
    Initiate a new payment transaction using current PhonePe API (2026)
    Updated authentication: Client ID + Client Secret
    """
    try:
        # Generate merchant order ID if not provided
        if not request.merchant_order_id:
            merchant_order_id = (
                f"MO{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"
            )
        else:
            merchant_order_id = request.merchant_order_id

        # Prepare customer info
        customer_info = None
        if request.customer_info:
            customer_info = request.customer_info.dict()

        # Initiate payment using current gateway
        response = phonepe_gateway.initiate_payment(
            amount=request.amount,
            merchant_order_id=merchant_order_id,
            redirect_url=request.redirect_url,
            callback_url=request.callback_url,
            customer_info=customer_info,
            metadata=request.metadata,
        )

        if response["success"]:
            logger.info(
                f"Payment initiated successfully (2026): {response['transaction_id']}"
            )

            # Add background task to log payment event
            background_tasks.add_task(
                log_payment_event,
                "PAYMENT_INITIATED",
                response["transaction_id"],
                response,
            )

            return PaymentInitiateResponse(**response)
        else:
            logger.error(f"Payment initiation failed (2026): {response.get('error')}")
            raise HTTPException(status_code=400, detail=response.get("error"))

    except Exception as e:
        logger.error(f"Error in initiate_payment (2026): {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status/{merchant_order_id}", response_model=PaymentStatusResponse)
async def get_payment_status(merchant_order_id: str):
    """
    Check the status of a payment transaction using merchant order ID
    Current 2026 SDK method
    """
    try:
        response = phonepe_gateway.check_payment_status(merchant_order_id)

        if response["success"]:
            logger.info(
                f"Payment status checked (2026): {merchant_order_id} - {response['status']}"
            )
            return PaymentStatusResponse(**response)
        else:
            logger.error(f"Payment status check failed (2026): {response.get('error')}")
            raise HTTPException(status_code=400, detail=response.get("error"))

    except Exception as e:
        logger.error(f"Error in get_payment_status (2026): {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle webhook callbacks from PhonePe
    Updated for 2026 webhook format
    """
    try:
        # Get authorization header
        authorization_header = request.headers.get("Authorization")
        if not authorization_header:
            raise HTTPException(status_code=401, detail="Missing authorization header")

        # Get raw request body
        response_body = await request.body()
        response_body_str = response_body.decode("utf-8")

        # Validate webhook
        validation_result = phonepe_gateway.validate_webhook(
            authorization_header=authorization_header, response_body=response_body_str
        )

        if validation_result["success"] and validation_result["valid"]:
            logger.info(f"Webhook validated and processed (2026)")

            # Add background task to process webhook
            background_tasks.add_task(process_webhook_event, validation_result)

            return {"status": "success", "message": "Webhook processed"}
        else:
            logger.error(
                f"Webhook validation failed (2026): {validation_result.get('error')}"
            )
            raise HTTPException(status_code=401, detail="Invalid webhook")

    except Exception as e:
        logger.error(f"Error in handle_webhook (2026): {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refund", response_model=RefundResponse)
async def refund_payment(request: RefundRequest, background_tasks: BackgroundTasks):
    """
    Process a refund for a transaction using current SDK (2026)
    Updated to use merchant order ID
    """
    try:
        response = phonepe_gateway.process_refund(
            merchant_order_id=request.merchant_order_id,
            refund_amount=request.refund_amount,
            refund_reason=request.refund_reason,
        )

        if response["success"]:
            logger.info(f"Refund initiated (2026): {response['refund_id']}")

            # Add background task to log refund
            background_tasks.add_task(
                log_payment_event, "REFUND_INITIATED", response["refund_id"], response
            )

            return RefundResponse(**response)
        else:
            logger.error(f"Refund failed (2026): {response.get('error')}")
            raise HTTPException(status_code=400, detail=response.get("error"))

    except Exception as e:
        logger.error(f"Error in refund_payment (2026): {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for payment service
    Updated for 2026 authentication system
    """
    try:
        # Check if PhonePe gateway is configured with current credentials
        if not phonepe_gateway.client_id or not phonepe_gateway.client_secret:
            return {
                "status": "unhealthy",
                "message": "PhonePe gateway not configured - missing Client ID or Client Secret",
                "year": "2026",
            }

        return {
            "status": "healthy",
            "message": "PhonePe payment service is operational - Current 2026 version",
            "environment": (
                "production" if phonepe_gateway.env.value == "PRODUCTION" else "UAT"
            ),
            "auth_system": "Client ID + Client Secret (2026)",
            "year": "2026",
        }

    except Exception as e:
        logger.error(f"Error in health_check (2026): {str(e)}")
        return {"status": "unhealthy", "message": str(e), "year": "2026"}


# Background task functions
async def log_payment_event(event_type: str, transaction_id: str, data: Dict[str, Any]):
    """
    Log payment events to database or logging service (2026)
    """
    try:
        logger.info(f"Payment event (2026): {event_type} - {transaction_id} - {data}")
        # TODO: Add database logging here

    except Exception as e:
        logger.error(f"Error logging payment event (2026): {str(e)}")


async def process_webhook_event(webhook_data: Dict[str, Any]):
    """
    Process webhook events in background
    Updated for 2026 webhook format
    """
    try:
        webhook_payload = webhook_data["webhook_data"]
        logger.info(
            f"Processing webhook (2026): {webhook_payload.get('type', 'unknown')}"
        )

        # Handle different webhook types based on current format
        webhook_type = webhook_payload.get("type", "")

        if webhook_type == "PAYMENT_SUCCESS":
            await handle_payment_success(webhook_payload)
        elif webhook_type == "PAYMENT_FAILED":
            await handle_payment_failure(webhook_payload)
        elif webhook_type == "REFUND_SUCCESS":
            await handle_refund_success(webhook_payload)
        else:
            logger.warning(f"Unknown webhook type (2026): {webhook_type}")

    except Exception as e:
        logger.error(f"Error processing webhook event (2026): {str(e)}")


async def handle_payment_success(webhook_payload: Dict[str, Any]):
    """
    Handle successful payment webhook (2026)
    """
    try:
        # Extract payment details from current webhook format
        transaction_id = webhook_payload.get("transactionId")
        logger.info(f"Payment success (2026): {transaction_id}")
        # TODO: Update database with payment success

    except Exception as e:
        logger.error(f"Error handling payment success (2026): {str(e)}")


async def handle_payment_failure(webhook_payload: Dict[str, Any]):
    """
    Handle payment failure webhook (2026)
    """
    try:
        transaction_id = webhook_payload.get("transactionId")
        error_code = webhook_payload.get("code")
        logger.info(f"Payment failed (2026): {transaction_id} - Error: {error_code}")
        # TODO: Update database with payment failure

    except Exception as e:
        logger.error(f"Error handling payment failure (2026): {str(e)}")


async def handle_refund_success(webhook_payload: Dict[str, Any]):
    """
    Handle refund success webhook (2026)
    """
    try:
        refund_id = webhook_payload.get("refundId")
        logger.info(f"Refund success (2026): {refund_id}")
        # TODO: Update database with refund success

    except Exception as e:
        logger.error(f"Error handling refund success (2026): {str(e)}")
