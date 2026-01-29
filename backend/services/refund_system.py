"""
Enhanced Refund System for PhonePe SDK Gateway
Implements proper refund request/response models with comprehensive validation
Addresses critical refund vulnerabilities identified in red team audit
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import json

# PhonePe SDK imports
from phonepe.sdk.pg.common.models.request.refund_request import (
    RefundRequest as SDKRefundRequest,
)
from phonepe.sdk.pg.common.models.response.refund_response import (
    RefundResponse as SDKRefundResponse,
)
from phonepe.sdk.pg.common.models.response.refund_status_response import (
    RefundStatusResponse as SDKRefundStatusResponse,
)
from phonepe.sdk.pg.common.exceptions import PhonePeException

# Internal imports
from .core.audit_logger import audit_logger, EventType, LogLevel
from .core.idempotency_manager import idempotency_manager
from .core.payment_fraud_detection import fraud_detector
from .core.payment_compliance import compliance_manager
from db.repositories.payment import PaymentRepository

logger = logging.getLogger(__name__)


class RefundState(Enum):
    """Refund states matching PhonePe SDK"""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class RefundReason(Enum):
    """Standardized refund reasons"""

    CUSTOMER_REQUEST = "CUSTOMER_REQUEST"
    SERVICE_ISSUE = "SERVICE_ISSUE"
    DUPLICATE_PAYMENT = "DUPLICATE_PAYMENT"
    FRAUDULENT_TRANSACTION = "FRAUDULENT_TRANSACTION"
    TECHNICAL_ERROR = "TECHNICAL_ERROR"
    CHARGEBACK = "CHARGEBACK"
    OTHER = "OTHER"


@dataclass
class RefundRequestData:
    """Enhanced refund request with comprehensive validation"""

    merchant_order_id: str
    refund_amount: int  # Amount in paise
    refund_reason: str
    reason_code: Optional[RefundReason] = RefundReason.OTHER
    user_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    customer_notes: Optional[str] = None
    internal_notes: Optional[str] = None
    priority: Optional[str] = "NORMAL"  # NORMAL, HIGH, URGENT


@dataclass
class RefundResponseData:
    """Enhanced refund response with full context"""

    success: bool
    refund_id: Optional[str] = None
    merchant_refund_id: Optional[str] = None
    phonepe_refund_id: Optional[str] = None
    original_merchant_order_id: Optional[str] = None
    refund_amount: Optional[int] = None
    status: Optional[RefundState] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    processing_time_ms: Optional[int] = None
    estimated_completion_time: Optional[datetime] = None
    security_metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    audit_metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class RefundStatusData:
    """Refund status information with detailed tracking"""

    refund_id: str
    merchant_refund_id: str
    phonepe_refund_id: Optional[str] = None
    original_merchant_order_id: str
    refund_amount: int
    current_status: RefundState
    previous_statuses: List[RefundState] = field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    completion_time: Optional[datetime] = None
    failure_reason: Optional[str] = None
    payment_details: Optional[List[Dict[str, Any]]] = field(default_factory=list)
    compliance_info: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class RefundEligibilityResult:
    """Refund eligibility check result"""

    eligible: bool
    reason: Optional[str] = None
    max_refundable_amount: Optional[int] = None
    time_restrictions: Optional[Dict[str, Any]] = None
    compliance_notes: Optional[List[str]] = field(default_factory=list)


class RefundManager:
    """
    Production-Ready Refund Management System
    Handles all refund operations with comprehensive security and validation
    """

    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repo = payment_repository
        self._refund_cache = {}  # Simple cache for status tracking

    async def validate_refund_eligibility(
        self, merchant_order_id: str, refund_amount: int, user_id: Optional[str] = None
    ) -> RefundEligibilityResult:
        """
        Comprehensive refund eligibility validation
        """
        try:
            # Check if original transaction exists and is successful
            original_transaction = await self.payment_repo.get_by_merchant_order_id(
                merchant_order_id
            )

            if not original_transaction:
                return RefundEligibilityResult(
                    eligible=False, reason="Original transaction not found"
                )

            if original_transaction.get("status") != "COMPLETED":
                return RefundEligibilityResult(
                    eligible=False, reason="Original transaction not completed"
                )

            # Check if refund amount exceeds original amount
            original_amount = original_transaction.get("amount", 0)
            if refund_amount > original_amount:
                return RefundEligibilityResult(
                    eligible=False,
                    reason=f"Refund amount ({refund_amount}) exceeds original transaction amount ({original_amount})",
                    max_refundable_amount=original_amount,
                )

            # Check time restrictions (e.g., refund within 30 days)
            transaction_date = original_transaction.get("created_at")
            if transaction_date:
                if isinstance(transaction_date, str):
                    transaction_date = datetime.fromisoformat(
                        transaction_date.replace("Z", "+00:00")
                    )

                days_since_transaction = (datetime.now() - transaction_date).days
                if days_since_transaction > 30:
                    return RefundEligibilityResult(
                        eligible=False,
                        reason="Refund period expired (30 days limit exceeded)",
                        time_restrictions={
                            "max_days": 30,
                            "days_elapsed": days_since_transaction,
                        },
                    )

            # Check for existing refunds
            existing_refunds = await self.payment_repo.get_refunds_for_order(
                merchant_order_id
            )
            total_refunded = sum(refund.get("amount", 0) for refund in existing_refunds)

            if total_refunded >= original_amount:
                return RefundEligibilityResult(
                    eligible=False,
                    reason="Full amount already refunded",
                    max_refundable_amount=max(0, original_amount - total_refunded),
                )

            # Compliance checks
            compliance_result = await compliance_manager.validate_refund_eligibility(
                merchant_order_id=merchant_order_id,
                refund_amount=refund_amount,
                user_id=user_id,
                original_transaction=original_transaction,
            )

            if not compliance_result.is_compliant:
                return RefundEligibilityResult(
                    eligible=False,
                    reason=f"Compliance check failed: {compliance_result.reason}",
                    compliance_notes=compliance_result.violations,
                )

            # Calculate maximum refundable amount
            max_refundable = original_amount - total_refunded

            return RefundEligibilityResult(
                eligible=True,
                max_refundable_amount=max_refundable,
                compliance_notes=["All checks passed"],
            )

        except Exception as e:
            logger.error(f"Refund eligibility validation error: {e}")
            return RefundEligibilityResult(
                eligible=False, reason=f"Validation error: {str(e)}"
            )

    async def create_refund_request(
        self, request: RefundRequestData
    ) -> RefundResponseData:
        """
        Create and process refund request with comprehensive validation
        """
        start_time = datetime.now()

        try:
            # Validate request structure
            await self._validate_refund_request(request)

            # Check idempotency
            if request.idempotency_key:
                existing_response = await idempotency_manager.get_response(
                    "refund_creation", request.idempotency_key
                )
                if existing_response:
                    await audit_logger.log_event(
                        event_type=EventType.IDEMPOTENT_REQUEST_DETECTED,
                        level=LogLevel.INFO,
                        request_data={"idempotency_key": request.idempotency_key},
                    )
                    return RefundResponseData(**existing_response)

            # Check refund eligibility
            eligibility = await self.validate_refund_eligibility(
                request.merchant_order_id, request.refund_amount, request.user_id
            )

            if not eligibility.eligible:
                await audit_logger.log_security_violation(
                    violation_type="refund_eligibility_failed",
                    request_data={
                        "merchant_order_id": request.merchant_order_id,
                        "refund_amount": request.refund_amount,
                        "reason": eligibility.reason,
                    },
                )
                return RefundResponseData(
                    success=False,
                    error=f"Refund not eligible: {eligibility.reason}",
                    original_merchant_order_id=request.merchant_order_id,
                    refund_amount=request.refund_amount,
                )

            # Fraud detection check
            fraud_score = await fraud_detector.assess_refund_risk(
                user_id=request.user_id,
                refund_amount=request.refund_amount,
                original_order_id=request.merchant_order_id,
                reason=request.refund_reason,
            )

            if fraud_score.risk_level == "CRITICAL":
                await audit_logger.log_security_violation(
                    violation_type="critical_refund_fraud_risk",
                    request_data={
                        "fraud_score": fraud_score.__dict__,
                        "merchant_order_id": request.merchant_order_id,
                    },
                )
                return RefundResponseData(
                    success=False,
                    error="Refund blocked due to high fraud risk",
                    original_merchant_order_id=request.merchant_order_id,
                    refund_amount=request.refund_amount,
                )

            # Generate unique refund ID
            merchant_refund_id = (
                f"RF{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"
            )

            # Create refund record in database
            refund_record = {
                "refund_id": merchant_refund_id,
                "merchant_refund_id": merchant_refund_id,
                "original_merchant_order_id": request.merchant_order_id,
                "refund_amount": request.refund_amount,
                "refund_reason": request.refund_reason,
                "reason_code": (
                    request.reason_code.value if request.reason_code else "OTHER"
                ),
                "user_id": request.user_id,
                "status": RefundState.PENDING.value,
                "fraud_score": fraud_score.__dict__,
                "metadata": request.metadata,
                "customer_notes": request.customer_notes,
                "internal_notes": request.internal_notes,
                "priority": request.priority,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            await self.payment_repo.create_refund(refund_record)

            # Store idempotency response
            if request.idempotency_key:
                await idempotency_manager.store_response(
                    "refund_creation", request.idempotency_key, refund_record
                )

            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

            # Build response
            response = RefundResponseData(
                success=True,
                refund_id=merchant_refund_id,
                merchant_refund_id=merchant_refund_id,
                original_merchant_order_id=request.merchant_order_id,
                refund_amount=request.refund_amount,
                status=RefundState.PENDING,
                processing_time_ms=processing_time,
                estimated_completion_time=datetime.now()
                + timedelta(hours=24),  # Estimate
                security_metadata={
                    "fraud_score": fraud_score.__dict__,
                    "eligibility_check": "PASSED",
                    "request_id": str(uuid.uuid4()),
                },
                audit_metadata={
                    "validation_checks": ["ELIGIBILITY", "FRAUD", "COMPLIANCE"],
                    "risk_level": fraud_score.risk_level,
                },
            )

            # Log refund creation
            await audit_logger.log_event(
                event_type=EventType.REFUND_INITIATED,
                level=LogLevel.INFO,
                user_id=request.user_id,
                transaction_id=merchant_refund_id,
                request_data={
                    "original_order_id": request.merchant_order_id,
                    "refund_amount": request.refund_amount,
                    "reason": request.refund_reason,
                    "fraud_score": fraud_score.__dict__,
                },
            )

            logger.info(f"Refund request created successfully: {merchant_refund_id}")
            return response

        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

            await audit_logger.log_event(
                event_type=EventType.REFUND_CREATION_FAILED,
                level=LogLevel.ERROR,
                user_id=request.user_id,
                error_message=f"Refund creation error: {str(e)}",
            )

            logger.error(f"Refund creation failed: {e}")
            return RefundResponseData(
                success=False,
                error="Internal server error during refund creation",
                processing_time_ms=processing_time,
            )

    async def process_refund_with_phonepe(
        self, merchant_refund_id: str
    ) -> RefundResponseData:
        """
        Process refund through PhonePe SDK
        """
        start_time = datetime.now()

        try:
            # Get refund record
            refund_record = await self.payment_repo.get_refund_by_merchant_id(
                merchant_refund_id
            )

            if not refund_record:
                return RefundResponseData(
                    success=False, error="Refund record not found"
                )

            if refund_record.get("status") != RefundState.PENDING.value:
                return RefundResponseData(
                    success=False,
                    error=f"Refund already processed: {refund_record.get('status')}",
                )

            # Update status to processing
            await self.payment_repo.update_refund_status(
                merchant_refund_id, RefundState.PROCESSING.value
            )

            # Import here to avoid circular imports
            from services.phonepe_sdk_gateway import phonepe_sdk_gateway

            # Create SDK refund request
            sdk_request = RefundRequestData(
                merchant_order_id=refund_record["original_merchant_order_id"],
                refund_amount=refund_record["refund_amount"],
                refund_reason=refund_record["refund_reason"],
                user_id=refund_record.get("user_id"),
            )

            # Process through SDK
            sdk_response = await phonepe_sdk_gateway.process_refund(sdk_request)

            if sdk_response.success:
                # Update refund record with PhonePe details
                update_data = {
                    "phonepe_refund_id": sdk_response.phonepe_refund_id,
                    "status": (
                        sdk_response.status.value
                        if isinstance(sdk_response.status, RefundState)
                        else sdk_response.status
                    ),
                    "updated_at": datetime.now(),
                }

                await self.payment_repo.update_refund(merchant_refund_id, update_data)

                processing_time = int(
                    (datetime.now() - start_time).total_seconds() * 1000
                )

                response = RefundResponseData(
                    success=True,
                    refund_id=merchant_refund_id,
                    merchant_refund_id=merchant_refund_id,
                    phonepe_refund_id=sdk_response.phonepe_refund_id,
                    original_merchant_order_id=refund_record[
                        "original_merchant_order_id"
                    ],
                    refund_amount=refund_record["refund_amount"],
                    status=sdk_response.status,
                    processing_time_ms=processing_time,
                    security_metadata={
                        "sdk_processed": True,
                        "phonepe_refund_id": sdk_response.phonepe_refund_id,
                    },
                )

                # Log successful processing
                await audit_logger.log_event(
                    event_type=EventType.REFUND_PROCESSED,
                    level=LogLevel.INFO,
                    transaction_id=merchant_refund_id,
                    request_data={
                        "phonepe_refund_id": sdk_response.phonepe_refund_id,
                        "status": sdk_response.status,
                    },
                )

                return response
            else:
                # Update refund record with error
                update_data = {
                    "status": RefundState.FAILED.value,
                    "failure_reason": sdk_response.error,
                    "updated_at": datetime.now(),
                }

                await self.payment_repo.update_refund(merchant_refund_id, update_data)

                return RefundResponseData(
                    success=False,
                    error=f"PhonePe processing failed: {sdk_response.error}",
                    refund_id=merchant_refund_id,
                    status=RefundState.FAILED,
                )

        except Exception as e:
            # Update refund record with error
            try:
                update_data = {
                    "status": RefundState.FAILED.value,
                    "failure_reason": str(e),
                    "updated_at": datetime.now(),
                }
                await self.payment_repo.update_refund(merchant_refund_id, update_data)
            except:
                pass  # Don't fail error logging if DB update fails

            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

            await audit_logger.log_event(
                event_type=EventType.REFUND_PROCESSING_FAILED,
                level=LogLevel.ERROR,
                transaction_id=merchant_refund_id,
                error_message=f"Refund processing error: {str(e)}",
            )

            return RefundResponseData(
                success=False,
                error="Internal server error during refund processing",
                refund_id=merchant_refund_id,
                status=RefundState.FAILED,
                processing_time_ms=processing_time,
            )

    async def get_refund_status(self, merchant_refund_id: str) -> RefundStatusData:
        """
        Get comprehensive refund status
        """
        try:
            # Get refund record
            refund_record = await self.payment_repo.get_refund_by_merchant_id(
                merchant_refund_id
            )

            if not refund_record:
                raise ValueError("Refund record not found")

            # Get status history
            status_history = await self.payment_repo.get_refund_status_history(
                merchant_refund_id
            )

            # Build status data
            status_data = RefundStatusData(
                refund_id=refund_record["refund_id"],
                merchant_refund_id=refund_record["merchant_refund_id"],
                phonepe_refund_id=refund_record.get("phonepe_refund_id"),
                original_merchant_order_id=refund_record["original_merchant_order_id"],
                refund_amount=refund_record["refund_amount"],
                current_status=RefundState(refund_record["status"]),
                previous_statuses=[
                    RefundState(status["status"]) for status in status_history
                ],
                created_at=refund_record["created_at"],
                updated_at=refund_record["updated_at"],
                completion_time=refund_record.get("completion_time"),
                failure_reason=refund_record.get("failure_reason"),
                payment_details=refund_record.get("payment_details", []),
                compliance_info={
                    "fraud_score": refund_record.get("fraud_score"),
                    "eligibility_check": refund_record.get("eligibility_check"),
                },
            )

            # Log status check
            await audit_logger.log_event(
                event_type=EventType.REFUND_STATUS_CHECK,
                level=LogLevel.INFO,
                transaction_id=merchant_refund_id,
                request_data={"current_status": refund_record["status"]},
            )

            return status_data

        except Exception as e:
            logger.error(f"Refund status check error: {e}")
            raise

    async def update_refund_from_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Update refund status from PhonePe webhook
        """
        try:
            # Extract refund information from webhook
            refund_id = webhook_data.get("refundId") or webhook_data.get("refund_id")
            status = webhook_data.get("state") or webhook_data.get("status")

            if not refund_id or not status:
                logger.warning("Invalid refund webhook data")
                return False

            # Get refund record
            refund_record = await self.payment_repo.get_refund_by_phonepe_id(refund_id)

            if not refund_record:
                logger.warning(
                    f"Refund record not found for PhonePe refund ID: {refund_id}"
                )
                return False

            merchant_refund_id = refund_record["merchant_refund_id"]

            # Update status
            update_data = {
                "status": status,
                "updated_at": datetime.now(),
                "payment_details": webhook_data,
            }

            if status == RefundState.COMPLETED.value:
                update_data["completion_time"] = datetime.now()

            await self.payment_repo.update_refund(merchant_refund_id, update_data)

            # Log webhook processing
            await audit_logger.log_event(
                event_type=EventType.REFUND_UPDATED_FROM_WEBHOOK,
                level=LogLevel.INFO,
                transaction_id=merchant_refund_id,
                request_data={
                    "phonepe_refund_id": refund_id,
                    "new_status": status,
                    "webhook_data": webhook_data,
                },
            )

            logger.info(
                f"Refund updated from webhook: {merchant_refund_id} -> {status}"
            )
            return True

        except Exception as e:
            logger.error(f"Refund webhook processing error: {e}")
            return False

    async def _validate_refund_request(self, request: RefundRequestData):
        """Comprehensive refund request validation"""
        if not request.merchant_order_id:
            raise ValueError("Merchant order ID is required")

        if not request.refund_amount or request.refund_amount <= 0:
            raise ValueError("Refund amount must be greater than 0")

        if not request.refund_reason:
            raise ValueError("Refund reason is required")

        if len(request.refund_reason) > 500:
            raise ValueError("Refund reason too long (max 500 chars)")

        if request.customer_notes and len(request.customer_notes) > 1000:
            raise ValueError("Customer notes too long (max 1000 chars)")

        if request.internal_notes and len(request.internal_notes) > 2000:
            raise ValueError("Internal notes too long (max 2000 chars)")

        # Validate refund amount limits
        if request.refund_amount > 500000:  # ₹5,000 in paise
            raise ValueError("Refund amount exceeds maximum limit")

        # Validate priority
        valid_priorities = ["NORMAL", "HIGH", "URGENT"]
        if request.priority and request.priority not in valid_priorities:
            raise ValueError(f"Invalid priority. Must be one of: {valid_priorities}")


# Global refund manager instance
refund_manager = None


def get_refund_manager(payment_repository: PaymentRepository) -> RefundManager:
    """Get or create refund manager instance"""
    global refund_manager
    if refund_manager is None:
        refund_manager = RefundManager(payment_repository)
    return refund_manager
