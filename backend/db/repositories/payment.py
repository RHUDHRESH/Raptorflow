"""
Payment Repository for PhonePe transactions and logs
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from backend.core.supabase_mgr import get_supabase_client

from .base import BaseModel, Repository
from .filters import Filter, build_query
from .pagination import PaginatedResult, Pagination


@dataclass
class PaymentTransaction(BaseModel):
    transaction_id: str
    merchant_order_id: str
    amount: int
    status: str
    currency: str = "INR"
    customer_id: Optional[str] = None
    customer_email: Optional[str] = None
    payment_mode: Optional[str] = None
    metadata: Optional[Dict] = None


class PaymentRepository(Repository[PaymentTransaction]):
    """Repository for payment transactions and logs"""

    def __init__(self):
        super().__init__("payment_transactions")
        self.refunds_table = "payment_refunds"
        self.webhooks_table = "payment_webhook_logs"
        self.events_table = "payment_events_log"

    def _map_to_model(self, data: Dict[str, Any]) -> PaymentTransaction:
        return PaymentTransaction(
            id=data.get("id"),
            workspace_id=data.get(
                "workspace_id", ""
            ),  # Note: Payment schema might not have workspace_id, check schema
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            transaction_id=data.get("transaction_id"),
            merchant_order_id=data.get("merchant_order_id"),
            amount=data.get("amount"),
            status=data.get("status"),
            currency=data.get("currency", "INR"),
            customer_id=data.get("customer_id"),
            customer_email=data.get("customer_email"),
            payment_mode=data.get("payment_mode"),
            metadata=data.get("metadata"),
        )

    async def create_transaction(
        self, transaction_data: Dict[str, Any], user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new payment transaction"""
        # Ensure ID is generated if not present (DB handles it but good to be explicit/consistent)
        # Note: 'id' is uuid default gen in DB. transaction_id is required.

        # We might need to handle user_id -> customer_id mapping if applicable
        if user_id and "customer_id" not in transaction_data:
            transaction_data["customer_id"] = user_id

        try:
            result = (
                self._get_supabase_client()
                .table(self.table_name)
                .insert(transaction_data)
                .single()
                .execute()
            )
            return result.data
        except Exception as e:
            # Handle duplicates or other errors
            print(f"Error creating transaction: {e}")
            return None

    async def get_by_merchant_order_id(
        self, merchant_order_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get transaction by merchant order ID"""
        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .select("*")
            .eq("merchant_order_id", merchant_order_id)
            .single()
            .execute()
        )
        return result.data if result.data else None

    async def update_status(
        self,
        transaction_id: str,
        status: str,
        payment_mode: Optional[str] = None,
        phonepe_transaction_id: Optional[str] = None,
        payment_instrument: Optional[Dict] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update transaction status"""
        update_data = {"status": status, "updated_at": datetime.utcnow().isoformat()}
        if payment_mode:
            update_data["payment_mode"] = payment_mode
        if phonepe_transaction_id:
            update_data["phonepe_transaction_id"] = phonepe_transaction_id
        if payment_instrument:
            update_data["payment_instrument"] = payment_instrument

        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .update(update_data)
            .eq("transaction_id", transaction_id)
            .execute()
        )
        return result.data[0] if result.data else None

    async def log_event(
        self,
        event_type: str,
        transaction_id: str,
        event_data: Dict[str, Any],
        refund_id: Optional[str] = None,
    ):
        """Log a payment event"""
        log_entry = {
            "event_type": event_type,
            "transaction_id": transaction_id,
            "refund_id": refund_id,
            "event_data": event_data,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._get_supabase_client().table(self.events_table).insert(log_entry).execute()

    async def log_webhook(
        self,
        webhook_id: str,
        callback_type: str,
        payload: Dict[str, Any],
        auth_header: str,
    ):
        """Log a webhook receipt"""
        log_entry = {
            "webhook_id": webhook_id,
            # We assume transaction_id is extracted from payload elsewhere or we store it null initially
            # If payload has transactionId, we might link it, but usually we just dump raw first.
            "callback_type": callback_type,
            "request_body": payload,
            "authorization_header": auth_header,
            "processed": False,
            "received_at": datetime.utcnow().isoformat(),
        }
        # Try to extract transaction_id if possible
        if isinstance(payload, dict) and "data" in payload:
            data = payload.get("data", {})
            if "transactionId" in data:
                log_entry["transaction_id"] = data["transactionId"]

        self._get_supabase_client().table(self.webhooks_table).insert(
            log_entry
        ).execute()

    async def create_refund(
        self, refund_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a refund record"""
        result = (
            self._get_supabase_client()
            .table(self.refunds_table)
            .insert(refund_data)
            .single()
            .execute()
        )
        return result.data
