"""
Comprehensive PhonePe Payment Status Service
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from phonepe_sdk_gateway import PhonePeSDKGateway


class PaymentStatusService:
    """Monitors and verifies payment statuses"""

    def __init__(self):
        self.gateway = PhonePeSDKGateway()
        self.check_interval = timedelta(minutes=5)

    async def check_payment_statuses(
        self, transaction_ids: List[str]
    ) -> Dict[str, Dict]:
        """Check status of multiple payments"""
        results = {}
        for tx_id in transaction_ids:
            results[tx_id] = await self.check_payment_status(tx_id)
        return results

    async def check_payment_status(
        self, transaction_id: str
    ) -> Dict[str, Optional[str]]:
        """Comprehensive payment status check"""
        try:
            # Check with PhonePe
            response = await self.gateway.check_payment_status(transaction_id)

            if not response.success:
                return {"status": "error", "details": response.error}

            # Additional verification logic can be added here
            return {
                "status": response.status,
                "last_checked": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"status": "check_failed", "error": str(e)}

    async def monitor_payments(self):
        """Periodic monitoring task"""
        while True:
            # Get pending transactions from database
            # pending_txs = await get_pending_transactions()
            # statuses = await self.check_payment_statuses(pending_txs)

            # Temporary implementation for testing
            print(f"Running status checks at {datetime.now()}")
            await asyncio.sleep(self.check_interval.total_seconds())
