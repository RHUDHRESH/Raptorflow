import base64
import json

from backend.services.payment_service import PaymentService


def test_generate_checksum():
    """Verify X-VERIFY checksum generation logic."""
    service = PaymentService()
    service.salt_key = "test_salt"
    service.salt_index = 1

    payload = "test_payload"
    endpoint = "/test"

    # Manually calculate expected checksum
    import hashlib

    main_string = payload + endpoint + "test_salt"
    sha256 = hashlib.sha256(main_string.encode("utf-8")).hexdigest()
    expected = f"{sha256}###1"

    assert service._generate_checksum(payload, endpoint) == expected


def test_initiate_payment():
    """Verify payment initiation payload structure."""
    service = PaymentService()
    service.merchant_id = "MID123"

    res = service.initiate_payment("user1", 100.0, "tx123", "http://redirect")

    assert "url" in res
    assert "payload" in res
    assert "checksum" in res

    # Decode payload
    decoded = base64.b64decode(res["payload"]).decode("utf-8")
    data = json.loads(decoded)

    assert data["merchantId"] == "MID123"
    assert data["amount"] == 10000  # 100 * 100 paise
    assert data["merchantTransactionId"] == "tx123"


def test_verify_webhook_success():
    """Verify webhook validation with correct checksum."""
    service = PaymentService()
    service.salt_key = "test_salt"
    service.salt_index = 1

    response_payload = "test_response"

    import hashlib

    main_string = response_payload + "test_salt"
    sha256 = hashlib.sha256(main_string.encode("utf-8")).hexdigest()
    x_verify = f"{sha256}###1"

    assert service.verify_webhook(x_verify, response_payload) is True


def test_verify_webhook_failure():
    """Verify webhook validation fails with incorrect checksum."""
    service = PaymentService()
    assert service.verify_webhook("wrong", "payload") is False
