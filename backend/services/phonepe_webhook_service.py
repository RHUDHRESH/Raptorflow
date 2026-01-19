"""
Consolidated PhonePe Webhook Service
Handles all PhonePe webhook events with standardized processing
"""
import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

from fastapi import HTTPException

from .phonepe_auth import PhonePeAuthClient
from .redis_client import upstash_redis

class PhonePeWebhookService:
    """Unified webhook handler for PhonePe events"""
    
    def __init__(self, webhook_secret: str):
        self.auth_client = PhonePeAuthClient()
        self.webhook_secret = webhook_secret
        self.event_handlers = {
            "payment.success": self._handle_payment_success,
            "payment.failed": self._handle_payment_failed,
            "refund.processed": self._handle_refund_processed
        }
    
    async def verify_and_process(self, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point - verifies and processes webhook"""
        try:
            # Verify signature
            if not await self._verify_signature(payload, headers):
                raise HTTPException(status_code=401, detail="Invalid signature")
            
            # Check for replay attack
            if await self._check_replay_attack(payload):
                raise HTTPException(status_code=400, detail="Replay attack detected")
            
            # Process event
            event_type = payload.get("event")
            if event_type not in self.event_handlers:
                raise HTTPException(status_code=400, detail="Unsupported event type")
            
            return await self.event_handlers[event_type](payload)
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            raise
    
    async def process_webhook(self, payload: Dict, headers: Dict):
        """Process webhook with replay and signature checks"""
        # Check for replay attack
        if await self._check_replay_attack(payload):
            raise ValueError("Possible replay attack detected")
            
        # Verify signature
        if not await self._verify_signature(payload, headers):
            raise ValueError("Invalid signature")
            
        # Process event based on type
        event_type = payload.get("type")
        if event_type == "PAYMENT_SUCCESS":
            return await self._handle_payment_success(payload)
        elif event_type == "PAYMENT_FAILURE":
            return await self._handle_payment_failed(payload)
        # ... other event types
        
        return {"status": "unknown_event"}
    
    async def _verify_signature(self, payload: Dict, headers: Dict) -> bool:
        """Verify HMAC SHA256 signature using X-VERIFY header"""
        try:
            # Get the X-VERIFY header
            signature = headers.get("X-VERIFY")
            if not signature:
                return False
                
            # Create the payload string
            payload_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
            
            # Create HMAC SHA256 signature
            generated_signature = hmac.new(
                self.webhook_secret.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(generated_signature, signature)
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    async def _check_replay_attack(self, payload: Dict) -> bool:
        """Check for replay attacks using payload nonce"""
        nonce = payload.get("nonce")
        if not nonce:
            return False
            
        # Check if nonce already processed
        if await upstash_redis.exists(f"phonepe_nonce:{nonce}"):
            return True
            
        # Store nonce with 5-minute TTL
        await upstash_redis.set(f"phonepe_nonce:{nonce}", "1", ex=300)
        return False
    
    async def _handle_payment_success(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment success event"""
        # Unified processing logic
        return {"status": "success"}
    
    async def _handle_payment_failed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment failure event"""
        # Unified processing logic
        return {"status": "failed"}
    
    async def _handle_refund_processed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process refund event"""
        # Unified processing logic
        return {"status": "processed"}
