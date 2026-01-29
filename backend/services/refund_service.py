"""
Refund Service for RaptorFlow Payment System
Implements comprehensive refund tracking, validation, and processing
Addresses critical refund system vulnerabilities identified in red team audit
"""

import logging
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

import httpx
from phonepe.sdk.pg.payments import PhonePePayments
from phonepe.sdk.pg.common.models import PhonePeConfig, Environment

from core.supabase_mgr import get_supabase_admin
from .email_service import EmailService, EmailRecipient


class RefundStatus(Enum):
    """Refund status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RefundEligibility(Enum):
    """Refund eligibility status"""

    ELIGIBLE = "eligible"
    NOT_ELIGIBLE = "not_eligible"
    TIME_EXPIRED = "time_expired"
    ALREADY_REFUNDED = "already_refunded"
    USAGE_LIMIT_EXCEEDED = "usage_limit_exceeded"
    AMOUNT_EXCEEDED = "amount_exceeded"


@dataclass
class RefundRequest:
    """Refund request data structure"""

    original_order_id: str
    refund_amount: int  # Amount in paise
    reason: str
    refund_idempotency_key: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class RefundResponse:
    """Refund response data structure"""

    success: bool
    refund_id: str
    original_order_id: str
    refund_amount: int
    status: RefundStatus
    phonepe_refund_id: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class RefundEligibilityResponse:
    """Refund eligibility response"""

    eligible: bool
    status: RefundEligibility
    max_refund_amount: int
    reason: str
    time_remaining: Optional[timedelta] = None


class RefundError(Exception):
    """Refund processing error"""

    def __init__(
        self, message: str, error_type: str, context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_type = error_type
        self.context = context or {}
        super().__init__(message)


class RefundService:
    """
    Comprehensive Refund Service
    Implements secure refund processing with validation and tracking
    """

    def __init__(self):
        """Initialize refund service"""
        self.logger = logging.getLogger(__name__)
        self.supabase = get_supabase_admin()
        self.email_service = EmailService()

        # Initialize PhonePe SDK for refunds
        self.merchant_id = os.getenv("PHONEPE_MERCHANT_ID")
        self.salt_key = os.getenv("PHONEPE_SALT_KEY")
        self.salt_index = os.getenv("PHONEPE_SALT_INDEX", "1")
        self.environment = os.getenv("PHONEPE_ENVIRONMENT", "sandbox")

        if not all([self.merchant_id, self.salt_key]):
            raise RefundError(
                "PhonePe credentials not configured", "MISSING_CREDENTIALS"
            )

        # Configure PhonePe SDK
        config = PhonePeConfig(
            merchant_id=self.merchant_id,
            salt_key=self.salt_key,
            salt_index=int(self.salt_index),
            environment=(
                Environment.SANDBOX
                if self.environment == "sandbox"
                else Environment.PRODUCTION
            ),
        )

        self.phonepe = PhonePePayments(config)

        # Refund policies
        self.REFUND_TIME_LIMIT = timedelta(days=30)  # 30 days refund window
        self.MAX_REFUND_PERCENTAGE = 0.8  # Max 80% of original amount

        self.logger.info("Refund service initialized")

    async def process_refund(self, request: RefundRequest) -> RefundResponse:
        """
        Process refund request with comprehensive validation
        """
        try:
            # Validate refund request
            await self._validate_refund_request(request)

            # Check idempotency
            if request.refund_idempotency_key:
                existing_refund = await self._check_refund_idempotency(
                    request.refund_idempotency_key
                )
                if existing_refund:
                    self.logger.info(
                        f"Returning existing refund for idempotency key: {request.refund_idempotency_key}"
                    )
                    return existing_refund

            # Get original transaction
            original_transaction = await self._get_original_transaction(
                request.original_order_id
            )
            if not original_transaction:
                raise RefundError(
                    "Original transaction not found", "TRANSACTION_NOT_FOUND"
                )

            # Check refund eligibility
            eligibility = await self.check_refund_eligibility(
                request.original_order_id, request.refund_amount
            )
            if not eligibility.eligible:
                raise RefundError(
                    f"Refund not eligible: {eligibility.reason}",
                    "REFUND_NOT_ELIGIBLE",
                    {"eligibility_status": eligibility.status.value},
                )

            # Generate unique refund ID
            refund_id = self._generate_refund_id()

            # Create refund record
            refund_data = {
                "id": refund_id,
                "original_order_id": request.original_order_id,
                "refund_amount": request.refund_amount,
                "reason": request.reason,
                "status": RefundStatus.PENDING.value,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "metadata": request.metadata or {},
            }

            # Store refund in database
            result = (
                self.supabase.table("refunds")
                .insert(refund_data)
                .select()
                .single()
                .execute()
            )

            if not result.data:
                raise RefundError("Failed to create refund record", "DATABASE_ERROR")

            refund_record = result.data

            # Process refund with PhonePe
            try:
                # Update status to processing
                await self._update_refund_status(refund_id, RefundStatus.PROCESSING)

                # Prepare PhonePe refund request
                phonepe_refund_request = {
                    "merchantTransactionId": refund_id,
                    "originalTransactionId": original_transaction[
                        "phonepe_transaction_id"
                    ],
                    "amount": request.refund_amount,
                }

                # Call PhonePe SDK for refund
                phonepe_response = self.phonepe.refund(phonepe_refund_request)

                if not phonepe_response.success:
                    raise RefundError(
                        f"PhonePe refund error: {phonepe_response.message}",
                        "PHONEPE_REFUND_ERROR",
                    )

                # Update refund record with PhonePe details
                await self._update_refund_with_phonepe_response(
                    refund_id,
                    phonepe_response.data.merchantTransactionId,
                    RefundStatus.PROCESSING,
                )

                response = RefundResponse(
                    success=True,
                    refund_id=refund_id,
                    original_order_id=request.original_order_id,
                    refund_amount=request.refund_amount,
                    status=RefundStatus.PROCESSING,
                    phonepe_refund_id=phonepe_response.data.merchantTransactionId,
                    created_at=datetime.now(timezone.utc),
                )

                # Store idempotency response if key provided
                if request.refund_idempotency_key:
                    await self._store_refund_idempotency(
                        request.refund_idempotency_key, response
                    )

                self.logger.info(f"Refund initiated successfully: {refund_id}")
                return response

            except Exception as e:
                # Update refund status to failed
                await self._update_refund_status(refund_id, RefundStatus.FAILED, str(e))

                raise RefundError(
                    f"Refund processing failed: {str(e)}", "REFUND_PROCESSING_FAILED"
                )

        except RefundError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in refund processing: {str(e)}")
            raise RefundError(
                "Refund processing failed due to internal error",
                "INTERNAL_ERROR",
                {"original_error": str(e)},
            )

    async def check_refund_status(self, refund_id: str) -> RefundResponse:
        """
        Check refund status from PhonePe and update local records
        """
        try:
            # Get refund record
            result = (
                self.supabase.table("refunds")
                .select("*")
                .eq("id", refund_id)
                .single()
                .execute()
            )

            if not result.data:
                raise RefundError("Refund not found", "REFUND_NOT_FOUND")

            refund_record = result.data

            # If already completed or failed, return cached status
            if refund_record["status"] in [
                RefundStatus.COMPLETED.value,
                RefundStatus.FAILED.value,
            ]:
                return RefundResponse(
                    success=True,
                    refund_id=refund_id,
                    original_order_id=refund_record["original_order_id"],
                    refund_amount=refund_record["refund_amount"],
                    status=RefundStatus(refund_record["status"]),
                    phonepe_refund_id=refund_record.get("phonepe_refund_id"),
                    created_at=datetime.fromisoformat(refund_record["created_at"]),
                    completed_at=(
                        datetime.fromisoformat(refund_record["completed_at"])
                        if refund_record.get("completed_at")
                        else None
                    ),
                )

            # Check status with PhonePe SDK
            try:
                phonepe_response = self.phonepe.get_transaction_status(refund_id)

                if not phonepe_response.success:
                    raise RefundError(
                        f"PhonePe refund status check error: {phonepe_response.message}",
                        "PHONEPE_STATUS_ERROR",
                    )

                phonepe_data = phonepe_response.data
                new_status = self._map_phonepe_refund_status(phonepe_data.state)

                # Update refund record
                update_data = {
                    "status": new_status.value,
                    "phonepe_refund_id": phonepe_data.transactionId,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }

                if new_status == RefundStatus.COMPLETED:
                    update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                    # Send refund confirmation email
                    await self._send_refund_confirmation_email(refund_record)

                elif new_status == RefundStatus.FAILED:
                    update_data["failed_at"] = datetime.now(timezone.utc).isoformat()
                    update_data["error_message"] = phonepe_data.responseMessage
                    # Send refund failure email
                    await self._send_refund_failure_email(refund_record)

                self.supabase.table("refunds").update(update_data).eq(
                    "id", refund_id
                ).execute()

                return RefundResponse(
                    success=True,
                    refund_id=refund_id,
                    original_order_id=refund_record["original_order_id"],
                    refund_amount=refund_record["refund_amount"],
                    status=new_status,
                    phonepe_refund_id=phonepe_data.transactionId,
                    created_at=datetime.fromisoformat(refund_record["created_at"]),
                    completed_at=(
                        datetime.now(timezone.utc)
                        if new_status == RefundStatus.COMPLETED
                        else None
                    ),
                )

            except Exception as e:
                self.logger.error(f"PhonePe refund status check failed: {str(e)}")
                raise RefundError(
                    f"Refund status check failed: {str(e)}", "STATUS_CHECK_FAILED"
                )

        except RefundError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in refund status check: {str(e)}")
            raise RefundError(
                "Refund status check failed due to internal error",
                "INTERNAL_ERROR",
                {"original_error": str(e)},
            )

    async def check_refund_eligibility(
        self, original_order_id: str, refund_amount: int
    ) -> RefundEligibilityResponse:
        """
        Check if a transaction is eligible for refund
        """
        try:
            # Get original transaction
            original_transaction = await self._get_original_transaction(
                original_order_id
            )
            if not original_transaction:
                return RefundEligibilityResponse(
                    eligible=False,
                    status=RefundEligibility.NOT_ELIGIBLE,
                    max_refund_amount=0,
                    reason="Original transaction not found",
                )

            # Check if transaction is completed
            if original_transaction["status"] != "completed":
                return RefundEligibilityResponse(
                    eligible=False,
                    status=RefundEligibility.NOT_ELIGIBLE,
                    max_refund_amount=0,
                    reason="Transaction not completed",
                )

            # Check time limit
            completed_at = datetime.fromisoformat(original_transaction["completed_at"])
            time_since_completion = datetime.now(timezone.utc) - completed_at

            if time_since_completion > self.REFUND_TIME_LIMIT:
                return RefundEligibilityResponse(
                    eligible=False,
                    status=RefundEligibility.TIME_EXPIRED,
                    max_refund_amount=0,
                    reason="Refund time limit exceeded",
                    time_remaining=timedelta(0),
                )

            # Check existing refunds
            existing_refunds = await self._get_existing_refunds(original_order_id)
            total_refunded = sum(
                refund["refund_amount"]
                for refund in existing_refunds
                if refund["status"] == RefundStatus.COMPLETED.value
            )

            # Calculate maximum refundable amount
            max_refund_amount = int(
                original_transaction["amount"] * self.MAX_REFUND_PERCENTAGE
            )
            remaining_refundable = max_refund_amount - total_refunded

            if remaining_refundable <= 0:
                return RefundEligibilityResponse(
                    eligible=False,
                    status=RefundEligibility.ALREADY_REFUNDED,
                    max_refund_amount=0,
                    reason="Maximum refund amount already reached",
                )

            # Check if requested amount exceeds remaining refundable amount
            if refund_amount > remaining_refundable:
                return RefundEligibilityResponse(
                    eligible=False,
                    status=RefundEligibility.AMOUNT_EXCEEDED,
                    max_refund_amount=remaining_refundable,
                    reason=f"Requested amount exceeds maximum refundable amount of ₹{remaining_refundable // 100}",
                )

            # Check business rules (e.g., usage limits)
            if len(existing_refunds) >= 3:  # Max 3 refunds per transaction
                return RefundEligibilityResponse(
                    eligible=False,
                    status=RefundEligibility.USAGE_LIMIT_EXCEEDED,
                    max_refund_amount=remaining_refundable,
                    reason="Maximum refund attempts exceeded",
                )

            return RefundEligibilityResponse(
                eligible=True,
                status=RefundEligibility.ELIGIBLE,
                max_refund_amount=remaining_refundable,
                reason="Refund eligible",
                time_remaining=self.REFUND_TIME_LIMIT - time_since_completion,
            )

        except Exception as e:
            self.logger.error(f"Error checking refund eligibility: {str(e)}")
            raise RefundError(
                "Refund eligibility check failed",
                "ELIGIBILITY_CHECK_FAILED",
                {"original_error": str(e)},
            )

    async def get_refund_history(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        Get refund history for a workspace
        """
        try:
            result = (
                self.supabase.table("refunds")
                .select("*", count="exact")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc=True)
                .execute()
            )

            return result.data or []

        except Exception as e:
            self.logger.error(f"Error getting refund history: {str(e)}")
            raise RefundError(
                "Failed to get refund history",
                "HISTORY_FETCH_FAILED",
                {"original_error": str(e)},
            )

    async def _validate_refund_request(self, request: RefundRequest):
        """Validate refund request"""
        if not request.original_order_id:
            raise RefundError("Original order ID is required", "MISSING_ORDER_ID")

        if request.refund_amount < 100:  # Minimum ₹1
            raise RefundError("Refund amount must be at least ₹1", "AMOUNT_TOO_LOW")

        if request.refund_amount > 10000000:  # Maximum ₹1,00,000
            raise RefundError("Refund amount exceeds maximum limit", "AMOUNT_TOO_HIGH")

        if not request.reason:
            raise RefundError("Refund reason is required", "MISSING_REASON")

    async def _get_original_transaction(
        self, order_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get original transaction by order ID"""
        try:
            result = (
                self.supabase.table("payment_transactions")
                .select("*")
                .eq("merchant_order_id", order_id)
                .single()
                .execute()
            )
            return result.data if result.data else None
        except Exception as e:
            self.logger.error(f"Error getting original transaction: {str(e)}")
            return None

    async def _get_existing_refunds(
        self, original_order_id: str
    ) -> List[Dict[str, Any]]:
        """Get existing refunds for a transaction"""
        try:
            result = (
                self.supabase.table("refunds")
                .select("*")
                .eq("original_order_id", original_order_id)
                .execute()
            )
            return result.data or []
        except Exception as e:
            self.logger.error(f"Error getting existing refunds: {str(e)}")
            return []

    def _generate_refund_id(self) -> str:
        """Generate unique refund ID"""
        timestamp = int(datetime.now(timezone.utc).timestamp())
        random_str = uuid.uuid4().hex[:8].upper()
        return f"REF{timestamp}{random_str}"

    def _map_phonepe_refund_status(self, phonepe_status: str) -> RefundStatus:
        """Map PhonePe refund status to internal status"""
        status_mapping = {
            "COMPLETED": RefundStatus.COMPLETED,
            "FAILED": RefundStatus.FAILED,
            "PENDING": RefundStatus.PENDING,
            "PROCESSING": RefundStatus.PROCESSING,
        }
        return status_mapping.get(phonepe_status, RefundStatus.PENDING)

    async def _update_refund_status(
        self, refund_id: str, status: RefundStatus, error_message: Optional[str] = None
    ):
        """Update refund status in database"""
        update_data = {
            "status": status.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if error_message:
            update_data["error_message"] = error_message

        if status == RefundStatus.COMPLETED:
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        elif status == RefundStatus.FAILED:
            update_data["failed_at"] = datetime.now(timezone.utc).isoformat()

        self.supabase.table("refunds").update(update_data).eq("id", refund_id).execute()

    async def _update_refund_with_phonepe_response(
        self, refund_id: str, phonepe_refund_id: str, status: RefundStatus
    ):
        """Update refund record with PhonePe response"""
        update_data = {
            "phonepe_refund_id": phonepe_refund_id,
            "status": status.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        self.supabase.table("refunds").update(update_data).eq("id", refund_id).execute()

    async def _check_refund_idempotency(
        self, idempotency_key: str
    ) -> Optional[RefundResponse]:
        """Check for existing refund using idempotency key"""
        # This would check Redis or database for cached refund response
        # For now, return None (should be implemented properly)
        return None

    async def _store_refund_idempotency(
        self, idempotency_key: str, response: RefundResponse
    ):
        """Store refund response for idempotency"""
        # This would store response in Redis with TTL
        # For now, do nothing (should be implemented properly)
        pass

    async def _send_refund_confirmation_email(self, refund_record: Dict[str, Any]):
        """Send refund confirmation email"""
        try:
            # Get user details from workspace
            workspace_result = (
                self.supabase.table("workspaces")
                .select("owner_id")
                .eq("id", refund_record["workspace_id"])
                .single()
                .execute()
            )

            if workspace_result.data:
                user_result = (
                    self.supabase.table("users")
                    .select("email, full_name")
                    .eq("id", workspace_result.data["owner_id"])
                    .single()
                    .execute()
                )

                if user_result.data:
                    recipient = EmailRecipient(
                        email=user_result.data["email"],
                        name=user_result.data["full_name"],
                        template="refund_confirmation",
                        data={
                            "refund_id": refund_record["id"],
                            "refund_amount": f"₹{refund_record['refund_amount'] // 100}",
                            "original_order_id": refund_record["original_order_id"],
                            "reason": refund_record["reason"],
                        },
                    )

                    self.email_service.send_email(recipient)

        except Exception as e:
            self.logger.error(f"Failed to send refund confirmation email: {str(e)}")

    async def _send_refund_failure_email(self, refund_record: Dict[str, Any]):
        """Send refund failure email"""
        try:
            # Get user details from workspace
            workspace_result = (
                self.supabase.table("workspaces")
                .select("owner_id")
                .eq("id", refund_record["workspace_id"])
                .single()
                .execute()
            )

            if workspace_result.data:
                user_result = (
                    self.supabase.table("users")
                    .select("email, full_name")
                    .eq("id", workspace_result.data["owner_id"])
                    .single()
                    .execute()
                )

                if user_result.data:
                    recipient = EmailRecipient(
                        email=user_result.data["email"],
                        name=user_result.data["full_name"],
                        template="refund_failure",
                        data={
                            "refund_id": refund_record["id"],
                            "original_order_id": refund_record["original_order_id"],
                            "error_message": refund_record.get(
                                "error_message", "Refund failed"
                            ),
                        },
                    )

                    self.email_service.send_email(recipient)

        except Exception as e:
            self.logger.error(f"Failed to send refund failure email: {str(e)}")


# Global instance
refund_service = RefundService()
