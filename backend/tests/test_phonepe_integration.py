import os
from unittest.mock import Mock

from services.payment_service import PaymentService


def _set_phonepe_env() -> None:
    os.environ.setdefault("PHONEPE_CLIENT_ID", "client-id")
    os.environ.setdefault("PHONEPE_CLIENT_SECRET", "client-secret")
    os.environ.setdefault("PHONEPE_CLIENT_VERSION", "1")
    os.environ.setdefault("PHONEPE_ENV", "SANDBOX")
    os.environ.setdefault("PHONEPE_WEBHOOK_USERNAME", "webhook-user")
    os.environ.setdefault("PHONEPE_WEBHOOK_PASSWORD", "webhook-pass")


def test_initiate_payment_calls_sdk_with_expected_payload():
    _set_phonepe_env()
    gateway = Mock()
    gateway.pay.return_value = {"redirectUrl": "https://phonepe.com/checkout"}

    service = PaymentService(gateway=gateway)
    result = service.initiate_payment(
        "user1", 100.0, "order-123", "http://redirect"
    )

    gateway.pay.assert_called_once_with("order-123", 10000, "http://redirect")
    assert result["url"] == "https://phonepe.com/checkout"
    assert result["merchantOrderId"] == "order-123"


def test_webhook_validation_is_idempotent():
    _set_phonepe_env()
    gateway = Mock()
    gateway.validate_callback.return_value = {
        "payload": {"merchantOrderId": "order-123"}
    }
    gateway.get_order_status.return_value = {"state": "COMPLETED"}

    service = PaymentService(gateway=gateway)

    first = service.handle_webhook("auth", "payload")
    second = service.handle_webhook("auth", "payload")

    assert first["status"] == "received"
    assert second["status"] == "already_processed"
    gateway.validate_callback.assert_called()
    gateway.get_order_status.assert_called_once_with("order-123")
