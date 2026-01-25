"""
PhonePe Payment API - Using Official SDK v2.1.7
Clean, simple API endpoints for real payments
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, EmailStr

from backend.services.phonepe_sdk_gateway_fixed import (
    phonepe_sdk_gateway_fixed,
    PaymentRequest as SDKPaymentRequest,
    RefundRequestData,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments/v2", tags=["payments-v2"])


# Request/Response Models
class InitiatePaymentRequest(BaseModel):
    amount: int  # Amount in paise
    merchant_order_id: Optional[str] = None
    redirect_url: str
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None


class InitiatePaymentResponse(BaseModel):
    success: bool
    checkout_url: Optional[str] = None
    transaction_id: Optional[str] = None
    merchant_order_id: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None


class StatusResponse(BaseModel):
    success: bool
    status: Optional[str] = None
    transaction_id: Optional[str] = None
    amount: Optional[int] = None
    phonepe_transaction_id: Optional[str] = None
    error: Optional[str] = None


class RefundRequest(BaseModel):
    original_merchant_order_id: str
    refund_amount: int
    merchant_refund_id: Optional[str] = None
    refund_reason: Optional[str] = None


class RefundResponse(BaseModel):
    success: bool
    refund_id: Optional[str] = None
    state: Optional[str] = None
    amount: Optional[int] = None
    error: Optional[str] = None


@router.post("/initiate", response_model=InitiatePaymentResponse)
async def initiate_payment(request: InitiatePaymentRequest):
    """
    Initiate a payment using PhonePe Standard Checkout (REAL SDK)
    
    Returns a checkout_url to redirect the user to PhonePe payment page
    """
    try:
        # Generate merchant order ID if not provided
        if not request.merchant_order_id:
            merchant_order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
        else:
            merchant_order_id = request.merchant_order_id
        
        # Validate amount
        if request.amount < 100:
            raise HTTPException(status_code=400, detail="Minimum amount is 100 paise (₹1)")
        
        logger.info(f"Initiating payment via SDK: {merchant_order_id}, Amount: ₹{request.amount/100}")
        
        # Call the SDK gateway (REAL PhonePe API)
        result = await phonepe_sdk_gateway_fixed.initiate_payment(
            SDKPaymentRequest(
                amount=request.amount,
                merchant_order_id=merchant_order_id,
                redirect_url=request.redirect_url,
                callback_url=f"{os.getenv('NEXT_PUBLIC_API_URL', 'http://localhost:8000')}/api/payments/webhook",
                customer_info={
                    "email": request.customer_email,
                    "name": request.customer_name
                },
                user_id=request.user_id,
                metadata=request.metadata
            )
        )
        
        if result.success:
            logger.info(f"Payment initiated successfully: {result.transaction_id}")
            return InitiatePaymentResponse(
                success=True,
                checkout_url=result.checkout_url,
                transaction_id=result.transaction_id,
                merchant_order_id=merchant_order_id,
                status=result.status
            )
        else:
            logger.error(f"Payment initiation failed: {result.error}")
            return InitiatePaymentResponse(
                success=False,
                merchant_order_id=merchant_order_id,
                error=result.error
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment initiation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{merchant_order_id}", response_model=StatusResponse)
async def get_payment_status(merchant_order_id: str):
    """
    Check payment status using PhonePe SDK
    """
    try:
        logger.info(f"Checking payment status via SDK: {merchant_order_id}")
        
        result = await phonepe_sdk_gateway_fixed.check_payment_status(merchant_order_id)
        
        if result.success:
            return StatusResponse(
                success=True,
                status=result.status,
                transaction_id=result.transaction_id,
                amount=result.amount,
                phonepe_transaction_id=result.phonepe_transaction_id
            )
        else:
            return StatusResponse(
                success=False,
                error=result.error
            )
            
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle PhonePe webhook callbacks (using SDK validation)
    """
    try:
        # Get authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        
        # Get raw body
        body = await request.body()
        body_str = body.decode("utf-8")
        
        logger.info("Received PhonePe webhook")
        
        # Validate using SDK
        result = await phonepe_sdk_gateway_fixed.validate_webhook(authorization, body_str)
        
        if result.get("valid"):
            callback_data = result.get("callback")
            
            logger.info(f"Webhook validated - Txn: {callback_data.merchant_transaction_id}, Code: {callback_data.code}")
            
            # Process based on callback type
            if callback_data.code == "PAYMENT_SUCCESS":
                background_tasks.add_task(
                    process_payment_success,
                    callback_data.__dict__
                )
            elif callback_data.code == "PAYMENT_ERROR":
                background_tasks.add_task(
                    process_payment_failure,
                    callback_data.__dict__
                )
            
            return {"status": "success", "message": "Webhook processed"}
        else:
            logger.warning(f"Webhook validation failed: {result.get('error')}")
            raise HTTPException(status_code=401, detail="Invalid webhook")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refund", response_model=RefundResponse)
async def process_refund(request: RefundRequest):
    """
    Process refund using PhonePe SDK
    
    Amount must be <= original transaction amount
    """
    try:
        logger.info(f"Processing refund via SDK: {request.original_merchant_order_id}")
        
        result = await phonepe_sdk_gateway_fixed.process_refund(
            original_merchant_order_id=request.original_merchant_order_id,
            refund_amount=request.refund_amount,
            merchant_refund_id=request.merchant_refund_id,
        )
        
        if result.get("success"):
            return RefundResponse(
                success=True,
                refund_id=result.get("refund_id"),
                state=result.get("state"),
                amount=result.get("amount")
            )
        else:
            return RefundResponse(
                success=False,
                error=result.get("error")
            )
            
    except Exception as e:
        logger.error(f"Refund error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle PhonePe webhook callbacks (using SDK validation)
    """
    try:
        # Get authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        
        # Get raw body
        body = await request.body()
        body_str = body.decode("utf-8")
        
        logger.info("Received PhonePe webhook")
        
        # Validate using SDK
        result = phonepe_sdk_gateway.validate_callback(authorization, body_str)
        
        if result.get("valid"):
            callback_data = result.get("callback_data", {})
            callback_type = result.get("callback_type", "")
            
            logger.info(f"Webhook validated - Type: {callback_type}, State: {callback_data.get('state')}")
            
            # Process based on callback type
            if "COMPLETED" in callback_type:
                background_tasks.add_task(
                    process_payment_success,
                    callback_data
                )
            elif "FAILED" in callback_type:
                background_tasks.add_task(
                    process_payment_failure,
                    callback_data
                )
            
            return {"status": "success", "message": "Webhook processed"}
        else:
            logger.warning(f"Webhook validation failed: {result.get('error')}")
            raise HTTPException(status_code=401, detail="Invalid webhook")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Check PhonePe SDK gateway health
    """
    return phonepe_sdk_gateway_fixed.health_check()


# Background tasks
async def process_payment_success(callback_data: Dict[str, Any]):
    """Process successful payment callback"""
    logger.info(f"Processing payment success: {callback_data}")
    # TODO: Update database, send email, etc.


async def process_payment_failure(callback_data: Dict[str, Any]):
    """Process failed payment callback"""
    logger.info(f"Processing payment failure: {callback_data}")
    # TODO: Update database, notify user, etc.
