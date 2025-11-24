"""
Payment Reconciliation Service
Periodically reconciles payment status between local database and PhonePe.
Handles webhooks that may have failed or been lost.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from backend.services.supabase_client import supabase_client
from backend.services.phonepe_service import phonepe_service
from backend.services.phonepe_autopay_service import phonepe_autopay_service

logger = logging.getLogger(__name__)


class PaymentReconciliationService:
    """Service to reconcile payment status with PhonePe."""

    # Only reconcile payments older than this to avoid immediate rechecks
    MIN_AGE_MINUTES = 5

    async def reconcile_pending_payments(self) -> Dict[str, Any]:
        """
        Find payments in 'pending' status and check actual status with PhonePe.
        Updates database and logs discrepancies.

        Returns:
            Dict with reconciliation results
        """
        logger.info("Starting payment reconciliation...")

        try:
            # Fetch pending payments older than MIN_AGE_MINUTES
            cutoff_time = (datetime.now(timezone.utc) - timedelta(minutes=self.MIN_AGE_MINUTES)).isoformat()

            pending_payments = await supabase_client.fetch_all(
                "billing_history",
                {"status": "pending"}
            )

            if not pending_payments:
                logger.info("No pending payments to reconcile")
                return {"status": "success", "checked": 0, "updated": 0, "failed": 0}

            # Filter for payments older than MIN_AGE_MINUTES
            pending_payments = [
                p for p in pending_payments
                if p.get("created_at", cutoff_time) < cutoff_time
            ]

            if not pending_payments:
                logger.info("No old enough pending payments to reconcile")
                return {"status": "success", "checked": 0, "updated": 0, "failed": 0}

            logger.info(f"Found {len(pending_payments)} pending payments to reconcile")

            updated_count = 0
            failed_count = 0

            for payment in pending_payments:
                merchant_transaction_id = payment.get("merchant_transaction_id")

                if not merchant_transaction_id:
                    logger.warning(f"Payment {payment.get('id')} missing merchant_transaction_id")
                    failed_count += 1
                    continue

                try:
                    # Check status with PhonePe
                    status, error = await phonepe_service.check_payment_status(merchant_transaction_id)

                    if error or not status:
                        logger.warning(f"Failed to check status for {merchant_transaction_id}: {error}")
                        failed_count += 1
                        continue

                    # Map PhonePe status to local status
                    if status.status == "success":
                        # Payment completed but webhook didn't arrive
                        logger.info(f"Found completed payment {merchant_transaction_id}, marking as active")

                        user_id = payment.get("user_id")

                        # SECURITY: Check if subscription already exists to prevent orphaned subscriptions
                        existing_subscription = await supabase_client.fetch_one(
                            "subscriptions",
                            {"user_id": user_id}
                        )

                        if existing_subscription and existing_subscription.get("status") == "active":
                            logger.info(f"Active subscription already exists for user {user_id}, skipping upsert")
                            # Just mark the payment as reconciled without creating duplicate subscription
                            await supabase_client.update(
                                "billing_history",
                                {"merchant_transaction_id": merchant_transaction_id},
                                {"status": "active", "reconciled_at": datetime.now(timezone.utc).isoformat()}
                            )
                        else:
                            # No active subscription exists, safe to create
                            await supabase_client.execute_transaction([
                                {
                                    "type": "update",
                                    "table": "billing_history",
                                    "filters": {"merchant_transaction_id": merchant_transaction_id},
                                    "data": {"status": "active", "reconciled_at": datetime.now(timezone.utc).isoformat()}
                                },
                                {
                                    "type": "upsert",
                                    "table": "subscriptions",
                                    "data": {
                                        "user_id": user_id,
                                        "status": "active",
                                        "phonepe_transaction_id": status.transaction_id,
                                        "current_period_start": datetime.now(timezone.utc).isoformat(),
                                        "current_period_end": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
                                    },
                                    "match_columns": ["user_id"]
                                }
                            ])

                        updated_count += 1

                    elif status.status == "failed":
                        # Payment failed
                        logger.info(f"Found failed payment {merchant_transaction_id}, marking as failed")

                        await supabase_client.update(
                            "billing_history",
                            {"merchant_transaction_id": merchant_transaction_id},
                            {
                                "status": "failed",
                                "reconciled_at": datetime.now(timezone.utc).isoformat()
                            }
                        )
                        updated_count += 1

                    elif status.status == "pending":
                        # Still pending, leave as is
                        logger.debug(f"Payment {merchant_transaction_id} still pending")

                    else:
                        logger.warning(f"Unexpected status for {merchant_transaction_id}: {status.status}")

                except Exception as e:
                    logger.error(f"Error reconciling payment {merchant_transaction_id}: {str(e)}", exc_info=True)
                    failed_count += 1

            logger.info(
                f"Payment reconciliation complete: checked={len(pending_payments)}, "
                f"updated={updated_count}, failed={failed_count}"
            )

            return {
                "status": "success",
                "checked": len(pending_payments),
                "updated": updated_count,
                "failed": failed_count
            }

        except Exception as e:
            logger.error(f"Payment reconciliation failed: {str(e)}", exc_info=True)
            return {"status": "failed", "error": str(e)}

    async def reconcile_pending_subscriptions(self) -> Dict[str, Any]:
        """
        Find subscriptions in 'pending' status and check actual status with PhonePe.
        Updates database and logs discrepancies.

        Returns:
            Dict with reconciliation results
        """
        logger.info("Starting subscription reconciliation...")

        try:
            # Fetch pending subscriptions
            pending_subs = await supabase_client.fetch_all(
                "autopay_subscriptions",
                {"status": "pending"}
            )

            if not pending_subs:
                logger.info("No pending subscriptions to reconcile")
                return {"status": "success", "checked": 0, "updated": 0, "failed": 0}

            logger.info(f"Found {len(pending_subs)} pending subscriptions to reconcile")

            updated_count = 0
            failed_count = 0

            for sub in pending_subs:
                merchant_subscription_id = sub.get("merchant_subscription_id")

                if not merchant_subscription_id:
                    logger.warning(f"Subscription {sub.get('id')} missing merchant_subscription_id")
                    failed_count += 1
                    continue

                try:
                    # Check status with PhonePe
                    status, error = await phonepe_autopay_service.check_subscription_status(
                        merchant_subscription_id
                    )

                    if error or not status:
                        logger.warning(f"Failed to check subscription {merchant_subscription_id}: {error}")
                        failed_count += 1
                        continue

                    # Update if status changed
                    if status.status in ["active", "failed", "cancelled", "paused", "expired"]:
                        logger.info(f"Found subscription {merchant_subscription_id} with status={status.status}")

                        # SECURITY: Verify subscription record still exists before updating
                        # This prevents race conditions where subscription was deleted
                        sub_record = await supabase_client.fetch_one(
                            "autopay_subscriptions",
                            {"merchant_subscription_id": merchant_subscription_id}
                        )

                        if not sub_record:
                            logger.warning(f"SECURITY: Subscription {merchant_subscription_id} no longer exists, skipping update")
                            failed_count += 1
                            continue

                        # Verify user still exists
                        user_id = sub_record.get("user_id")
                        if user_id:
                            user_exists = await supabase_client.fetch_one(
                                "users",
                                {"id": user_id}
                            )
                            if not user_exists:
                                logger.warning(f"SECURITY: User {user_id} for subscription {merchant_subscription_id} no longer exists")
                                failed_count += 1
                                continue

                        await supabase_client.update(
                            "autopay_subscriptions",
                            {"merchant_subscription_id": merchant_subscription_id},
                            {
                                "status": status.status,
                                "next_billing_date": status.next_billing_date.isoformat() if status.next_billing_date else None,
                                "reconciled_at": datetime.now(timezone.utc).isoformat()
                            }
                        )
                        updated_count += 1

                except Exception as e:
                    logger.error(f"Error reconciling subscription {merchant_subscription_id}: {str(e)}", exc_info=True)
                    failed_count += 1

            logger.info(
                f"Subscription reconciliation complete: checked={len(pending_subs)}, "
                f"updated={updated_count}, failed={failed_count}"
            )

            return {
                "status": "success",
                "checked": len(pending_subs),
                "updated": updated_count,
                "failed": failed_count
            }

        except Exception as e:
            logger.error(f"Subscription reconciliation failed: {str(e)}", exc_info=True)
            return {"status": "failed", "error": str(e)}

    async def run_full_reconciliation(self) -> Dict[str, Any]:
        """
        Run complete reconciliation for both payments and subscriptions.

        Returns:
            Dict with combined results
        """
        payment_results = await self.reconcile_pending_payments()
        subscription_results = await self.reconcile_pending_subscriptions()

        return {
            "status": "success" if payment_results.get("status") == "success" and subscription_results.get("status") == "success" else "partial_failure",
            "payments": payment_results,
            "subscriptions": subscription_results
        }


# Global instance
payment_reconciliation_service = PaymentReconciliationService()
