#!/usr/bin/env python3
"""
Standalone PhonePe Payment Test Server
No dependencies on complex backend imports
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PhonePe Payment Test API",
    description="Standalone API for PhonePe integration testing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PhonePe Payment Test API",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "running",
            "phonepe": "configured"
        }
    }

@app.get("/api/payments/v2/health")
async def payments_health():
    """Payment API health check"""
    try:
        # Test PhonePe SDK import
        from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
        from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
        from phonepe.sdk.pg.env import Env
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "phonepe_sdk": {
                "imported": True,
                "client_class": "StandardCheckoutClient",
                "request_class": "StandardCheckoutPayRequest",
                "environment": "PRODUCTION" if hasattr(Env, 'PRODUCTION') else "SANDBOX"
            },
            "environment": os.getenv("PHONEPE_ENV", "UAT"),
            "client_id": os.getenv("PHONEPE_CLIENT_ID", "PGTESTPAYUAT")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@app.post("/api/payments/v2/initiate")
async def initiate_payment(payment_data: Dict[str, Any]):
    """Initiate payment endpoint"""
    try:
        # Validate required fields
        required_fields = ["amount", "merchant_order_id", "redirect_url"]
        for field in required_fields:
            if field not in payment_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Test PhonePe SDK
        from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
        from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
        from phonepe.sdk.pg.env import Env
        
        # Create client (test mode with official UAT credentials)
        client = StandardCheckoutClient(
            client_id=os.getenv("PHONEPE_CLIENT_ID", "PGTESTPAYUAT86"),
            client_version=1,
            client_secret=os.getenv("PHONEPE_CLIENT_SECRET", "96434309-7796-489d-8924-ab56988a6076"),
            env=Env.PRODUCTION,
            should_publish_events=True
        )
        
        # Create payment request
        request = StandardCheckoutPayRequest.build_request(
            merchant_order_id=payment_data["merchant_order_id"],
            amount=payment_data["amount"],
            redirect_url=payment_data["redirect_url"]
        )
        
        # For testing, return a mock checkout URL
        checkout_url = f"https://phonepe.com/payment/test?order_id={payment_data['merchant_order_id']}&amount={payment_data['amount']}"
        
        return {
            "success": True,
            "merchant_order_id": payment_data["merchant_order_id"],
            "checkout_url": checkout_url,
            "amount": payment_data["amount"],
            "timestamp": datetime.utcnow().isoformat(),
            "test_mode": True
        }
        
    except Exception as e:
        logger.error(f"Payment initiation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment initiation failed: {str(e)}")

@app.get("/api/payments/v2/status/{merchant_order_id}")
async def check_payment_status(merchant_order_id: str):
    """Check payment status endpoint"""
    try:
        # For testing, return mock status
        return {
            "success": True,
            "merchant_order_id": merchant_order_id,
            "status": "SUCCESS",
            "amount": 500000,  # ₹5,000 in paise
            "transaction_id": f"TXN_{merchant_order_id}",
            "timestamp": datetime.utcnow().isoformat(),
            "test_mode": True
        }
        
    except Exception as e:
        logger.error(f"Payment status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.post("/api/payments/v2/webhook")
async def handle_webhook(webhook_data: Dict[str, Any]):
    """Handle PhonePe webhook endpoint"""
    try:
        logger.info(f"Received webhook: {webhook_data}")
        
        # For testing, always return success
        return {
            "success": True,
            "message": "Webhook processed successfully",
            "test_mode": True
        }
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 Starting PhonePe Payment Test API")
    logger.info(f"📊 Environment: {os.getenv('PHONEPE_ENV', 'UAT')}")
    logger.info(f"💳 Client ID: {os.getenv('PHONEPE_CLIENT_ID', 'PGTESTPAYUAT')}")
    logger.info("✅ Payment API ready for testing")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🌐 Starting PhonePe test server on port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
