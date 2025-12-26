import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Protocol
from uuid import uuid4

from core.config import get_settings

BRIDGE_PATH = Path(__file__).resolve().parents[1] / "phonepe" / "phonepeBridge.js"
FINAL_ORDER_STATES = {"COMPLETED", "SUCCESS"}


class PhonePeCallbackError(RuntimeError):
    """Raised when PhonePe callback validation fails."""


class PhonePeGateway(Protocol):
    def pay(
        self, merchant_order_id: str, amount_paise: int, redirect_url: str
    ) -> Dict[str, Any]:
        ...

    def get_order_status(self, merchant_order_id: str) -> Dict[str, Any]:
        ...

    def validate_callback(
        self,
        username: str,
        password: str,
        authorization: str,
        response_body: str,
    ) -> Dict[str, Any]:
        ...


class PhonePeNodeClient:
    """Bridge that calls the PhonePe Node SDK via a Node.js helper script."""

    def __init__(self, bridge_path: Path = BRIDGE_PATH) -> None:
        self.bridge_path = bridge_path

    def _run(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = subprocess.run(
            ["node", str(self.bridge_path), action],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            error_message = (result.stderr or result.stdout).strip()
            raise RuntimeError(f"PhonePe SDK error: {error_message}")

        if not result.stdout:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("PhonePe SDK returned invalid JSON") from exc

    def pay(
        self, merchant_order_id: str, amount_paise: int, redirect_url: str
    ) -> Dict[str, Any]:
        return self._run(
            "pay",
            {
                "merchantOrderId": merchant_order_id,
                "amount": amount_paise,
                "redirectUrl": redirect_url,
            },
        )

    def get_order_status(self, merchant_order_id: str) -> Dict[str, Any]:
        return self._run("status", {"merchantOrderId": merchant_order_id})

    def validate_callback(
        self,
        username: str,
        password: str,
        authorization: str,
        response_body: str,
    ) -> Dict[str, Any]:
        return self._run(
            "validate",
            {
                "username": username,
                "password": password,
                "authorization": authorization,
                "responseBody": response_body,
            },
        )


class PaymentService:
    """
    PhonePe Standard Checkout v2 integration.
    Handles transaction initiation, status verification, and webhook validation.
    """

    def __init__(self, gateway: Optional[PhonePeGateway] = None):
        self.settings = get_settings()
        self.gateway = gateway or PhonePeNodeClient()
        self.order_states: Dict[str, str] = {}
        self.processed_orders: set[str] = set()
        self.initiated_orders: set[str] = set()
        self._validated = False

    def _validate_phonepe_settings(self) -> None:
        required_fields = [
            "PHONEPE_CLIENT_ID",
            "PHONEPE_CLIENT_SECRET",
            "PHONEPE_CLIENT_VERSION",
            "PHONEPE_ENV",
            "PHONEPE_WEBHOOK_USERNAME",
            "PHONEPE_WEBHOOK_PASSWORD",
        ]

        missing = [
            field
            for field in required_fields
            if not getattr(self.settings, field, None)
        ]
        if missing:
            raise ValueError(
                "Missing PhonePe configuration: " + ", ".join(sorted(missing))
            )

        env_value = str(self.settings.PHONEPE_ENV).upper()
        if env_value not in {"SANDBOX", "PRODUCTION"}:
            raise ValueError(
                "PHONEPE_ENV must be set to SANDBOX or PRODUCTION (case-insensitive)."
            )

    def initiate_payment(
        self, user_id: str, amount: float, transaction_id: str, redirect_url: str
    ) -> Dict[str, Any]:
        """Initiates a payment request with PhonePe."""
        self._ensure_phonepe_ready()
        merchant_order_id = transaction_id or str(uuid4())
        amount_paise = int(round(amount * 100))

        response = self.gateway.pay(merchant_order_id, amount_paise, redirect_url)
        self.initiated_orders.add(merchant_order_id)

        return {
            "url": response.get("redirectUrl"),
            "merchantOrderId": merchant_order_id,
        }

    def get_order_status(self, merchant_order_id: str) -> Dict[str, Any]:
        """Fetch the order status from PhonePe."""
        self._ensure_phonepe_ready()
        return self.gateway.get_order_status(merchant_order_id)

    def _record_order_state(self, merchant_order_id: str, state: Optional[str]) -> bool:
        if not state:
            return False

        if self.order_states.get(merchant_order_id) == state:
            return False

        self.order_states[merchant_order_id] = state

        if state in FINAL_ORDER_STATES:
            self.processed_orders.add(merchant_order_id)

        return True

    def handle_webhook(self, authorization: str, response_body: str) -> Dict[str, str]:
        """Validates webhook callback and updates order state idempotently."""
        self._ensure_phonepe_ready()
        try:
            callback = self.gateway.validate_callback(
                self.settings.PHONEPE_WEBHOOK_USERNAME,
                self.settings.PHONEPE_WEBHOOK_PASSWORD,
                authorization,
                response_body,
            )
        except RuntimeError as exc:
            raise PhonePeCallbackError(str(exc)) from exc

        payload = callback.get("payload") or {}
        merchant_order_id = payload.get("merchantOrderId")
        if not merchant_order_id:
            raise ValueError("Missing merchantOrderId in callback payload.")

        if merchant_order_id in self.processed_orders:
            return {"status": "already_processed"}

        order_status = self.get_order_status(merchant_order_id)
        self._record_order_state(merchant_order_id, order_status.get("state"))

        return {"status": "received"}

    def _ensure_phonepe_ready(self) -> None:
        if not self._validated:
            self._validate_phonepe_settings()
            self._validated = True


payment_service = PaymentService()
