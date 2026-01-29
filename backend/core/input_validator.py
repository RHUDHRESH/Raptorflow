"""
Comprehensive Input Validation for Payment System
Implements strict validation for all payment-related inputs
Addresses critical input validation vulnerabilities identified in red team audit
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import bleach
from pydantic import BaseModel, Field, HttpUrl, validator


class ValidationError(Exception):
    """Input validation error"""

    def __init__(self, message: str, field: str, value: Any):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(message)


class PaymentPlan(str, Enum):
    """Valid payment plans"""

    STARTER = "starter"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


class PaymentStatus(str, Enum):
    """Valid payment statuses"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ValidationResult:
    """Validation result"""

    is_valid: bool
    errors: List[str]
    sanitized_data: Optional[Dict[str, Any]] = None


class PaymentRequestValidator(BaseModel):
    """Payment request validation model"""

    workspace_id: str = Field(..., min_length=1, max_length=100)
    plan: PaymentPlan
    amount: int = Field(..., gt=99, lt=10000000)  # ₹1 to ₹1,00,000
    customer_email: str = Field(
        ..., regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    customer_name: str = Field(..., min_length=1, max_length=100)
    redirect_url: Optional[HttpUrl] = None
    webhook_url: Optional[HttpUrl] = None
    idempotency_key: Optional[str] = Field(
        None, min_length=8, max_length=64, regex=r"^[A-Za-z0-9_-]+$"
    )
    metadata: Optional[Dict[str, Any]] = None

    @validator("amount")
    def validate_amount(cls, v):
        if v % 100 != 0:  # Must be whole rupees
            raise ValueError("Amount must be in whole rupees (no paise)")
        return v

    @validator("customer_name")
    def validate_customer_name(cls, v):
        # Remove potentially dangerous characters
        sanitized = bleach.clean(v, tags=[], strip=True)
        if len(sanitized.strip()) == 0:
            raise ValueError("Customer name cannot be empty after sanitization")
        return sanitized.strip()

    @validator("metadata")
    def validate_metadata(cls, v):
        if v is None:
            return v

        # Limit metadata size
        if len(str(v)) > 10000:  # 10KB limit
            raise ValueError("Metadata too large")

        # Sanitize metadata values
        sanitized = {}
        for key, value in v.items():
            if isinstance(key, str):
                sanitized_key = bleach.clean(key, tags=[], strip=True)[:100]
            else:
                sanitized_key = str(key)[:100]

            if isinstance(value, str):
                sanitized_value = bleach.clean(value, tags=[], strip=True)[:1000]
            else:
                sanitized_value = str(value)[:1000]

            sanitized[sanitized_key] = sanitized_value

        return sanitized


class RefundRequestValidator(BaseModel):
    """Refund request validation model"""

    original_order_id: str = Field(
        ..., min_length=8, max_length=64, regex=r"^[A-Za-z0-9_-]+$"
    )
    refund_amount: int = Field(..., gt=99, lt=10000000)  # ₹1 to ₹1,00,000
    reason: str = Field(..., min_length=1, max_length=500)
    refund_idempotency_key: Optional[str] = Field(
        None, min_length=8, max_length=64, regex=r"^[A-Za-z0-9_-]+$"
    )
    metadata: Optional[Dict[str, Any]] = None

    @validator("refund_amount")
    def validate_refund_amount(cls, v):
        if v % 100 != 0:  # Must be whole rupees
            raise ValueError("Refund amount must be in whole rupees (no paise)")
        return v

    @validator("reason")
    def validate_reason(cls, v):
        # Remove potentially dangerous characters
        sanitized = bleach.clean(v, tags=[], strip=True)
        if len(sanitized.strip()) == 0:
            raise ValueError("Reason cannot be empty after sanitization")
        return sanitized.strip()


class WebhookValidator(BaseModel):
    """Webhook validation model"""

    merchantTransactionId: str = Field(..., min_length=8, max_length=64)
    code: str = Field(..., regex=r"^(PAYMENT_SUCCESS|PAYMENT_FAILED|PAYMENT_PENDING)$")
    data: Dict[str, Any]
    timestamp: Optional[int] = None
    nonce: Optional[str] = None

    @validator("merchantTransactionId")
    def validate_transaction_id(cls, v):
        if not re.match(r"^[A-Za-z0-9_-]+$", v):
            raise ValueError("Invalid transaction ID format")
        return v

    @validator("data")
    def validate_webhook_data(cls, v):
        # Limit webhook data size
        if len(str(v)) > 1024 * 1024:  # 1MB limit
            raise ValueError("Webhook data too large")
        return v


class InputValidator:
    """
    Comprehensive input validator for payment system
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Validation patterns
        self.EMAIL_PATTERN = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        self.PHONEPE_TRANSACTION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
        self.ORDER_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")

        # Allowed domains for URLs
        self.ALLOWED_URL_DOMAINS = [
            "raptorflow.com",
            "phonepe.com",
            "localhost",
            "127.0.0.1",
        ]

    def validate_payment_request(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate payment request data"""
        try:
            # Use Pydantic for validation
            validated_data = PaymentRequestValidator(**data)

            # Additional business logic validation
            self._validate_payment_business_rules(validated_data.dict())

            return ValidationResult(
                is_valid=True, errors=[], sanitized_data=validated_data.dict()
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False, errors=[str(e)], sanitized_data=None
            )

    def validate_refund_request(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate refund request data"""
        try:
            validated_data = RefundRequestValidator(**data)

            # Additional business logic validation
            self._validate_refund_business_rules(validated_data.dict())

            return ValidationResult(
                is_valid=True, errors=[], sanitized_data=validated_data.dict()
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False, errors=[str(e)], sanitized_data=None
            )

    def validate_webhook(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate webhook data"""
        try:
            validated_data = WebhookValidator(**data)

            # Additional webhook validation
            self._validate_webhook_business_rules(validated_data.dict())

            return ValidationResult(
                is_valid=True, errors=[], sanitized_data=validated_data.dict()
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False, errors=[str(e)], sanitized_data=None
            )

    def validate_email(self, email: str) -> ValidationResult:
        """Validate email address"""
        try:
            if not self.EMAIL_PATTERN.match(email):
                raise ValueError("Invalid email format")

            # Additional email validation
            email = email.lower().strip()

            # Check for suspicious patterns
            suspicious_patterns = [
                r"..",  # Double dots
                r"\.com\.com",  # Double .com
                r"\.con\.con",  # Double .con
            ]

            for pattern in suspicious_patterns:
                if re.search(pattern, email):
                    raise ValueError("Suspicious email pattern detected")

            return ValidationResult(
                is_valid=True, errors=[], sanitized_data={"email": email}
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False, errors=[str(e)], sanitized_data=None
            )

    def validate_url(
        self, url: str, allowed_domains: Optional[List[str]] = None
    ) -> ValidationResult:
        """Validate URL"""
        try:
            parsed_url = urlparse(url)

            # Basic URL validation
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL format")

            if parsed_url.scheme not in ["http", "https"]:
                raise ValueError("Only HTTP and HTTPS URLs are allowed")

            # Domain validation
            domains = allowed_domains or self.ALLOWED_URL_DOMAINS
            if not any(domain in parsed_url.netloc for domain in domains):
                raise ValueError(f"URL domain not in allowed list: {domains}")

            # Path validation
            if len(parsed_url.path) > 2048:  # URL length limit
                raise ValueError("URL path too long")

            return ValidationResult(
                is_valid=True, errors=[], sanitized_data={"url": url}
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False, errors=[str(e)], sanitized_data=None
            )

    def validate_amount(self, amount: Union[int, str]) -> ValidationResult:
        """Validate payment amount"""
        try:
            # Convert to integer if string
            if isinstance(amount, str):
                if not amount.isdigit():
                    raise ValueError("Amount must be a number")
                amount = int(amount)

            # Amount validation
            if amount < 100:  # Minimum ₹1
                raise ValueError("Amount must be at least ₹1")

            if amount > 10000000:  # Maximum ₹1,00,000
                raise ValueError("Amount exceeds maximum limit")

            if amount % 100 != 0:  # Must be whole rupees
                raise ValueError("Amount must be in whole rupees")

            return ValidationResult(
                is_valid=True, errors=[], sanitized_data={"amount": amount}
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False, errors=[str(e)], sanitized_data=None
            )

    def validate_plan(self, plan: str) -> ValidationResult:
        """Validate payment plan"""
        try:
            valid_plans = [p.value for p in PaymentPlan]

            if plan not in valid_plans:
                raise ValueError(f"Invalid plan. Valid plans: {valid_plans}")

            return ValidationResult(
                is_valid=True, errors=[], sanitized_data={"plan": plan}
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False, errors=[str(e)], sanitized_data=None
            )

    def _validate_payment_business_rules(self, data: Dict[str, Any]):
        """Validate payment business rules"""
        # Plan-amount mapping validation
        plan_amounts = {"starter": 4900, "growth": 14900, "enterprise": 49900}

        expected_amount = plan_amounts.get(data["plan"])
        if expected_amount and data["amount"] != expected_amount:
            raise ValueError(
                f"Amount mismatch for plan {data['plan']}. Expected: ₹{expected_amount//100}"
            )

    def _validate_refund_business_rules(self, data: Dict[str, Any]):
        """Validate refund business rules"""
        # Refund amount cannot exceed original amount (would be checked in service)
        # Refund reason validation
        forbidden_reasons = ["test", "testing", "debug"]
        if data["reason"].lower() in forbidden_reasons:
            raise ValueError("Invalid refund reason")

    def _validate_webhook_business_rules(self, data: Dict[str, Any]):
        """Validate webhook business rules"""
        # Validate webhook code
        valid_codes = ["PAYMENT_SUCCESS", "PAYMENT_FAILED", "PAYMENT_PENDING"]
        if data["code"] not in valid_codes:
            raise ValueError(f"Invalid webhook code: {data['code']}")

        # Validate transaction ID format
        if not self.PHONEPE_TRANSACTION_ID_PATTERN.match(data["merchantTransactionId"]):
            raise ValueError("Invalid transaction ID format")

    def sanitize_input(self, input_data: str, max_length: int = 1000) -> str:
        """Sanitize user input"""
        if not isinstance(input_data, str):
            input_data = str(input_data)

        # Remove HTML tags and scripts
        sanitized = bleach.clean(input_data, tags=[], strip=True)

        # Limit length
        sanitized = sanitized[:max_length]

        # Remove potentially dangerous characters
        dangerous_chars = ["<", ">", '"', "'", "&", "\x00"]
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")

        return sanitized.strip()

    def validate_json_input(
        self, json_data: str, max_size: int = 1024 * 1024
    ) -> ValidationResult:
        """Validate JSON input"""
        try:
            # Size validation
            if len(json_data.encode("utf-8")) > max_size:
                raise ValueError("JSON data too large")

            # Parse JSON
            parsed_data = json.loads(json_data)

            # Recursively validate JSON structure
            self._validate_json_structure(parsed_data)

            return ValidationResult(
                is_valid=True, errors=[], sanitized_data={"data": parsed_data}
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False, errors=[str(e)], sanitized_data=None
            )

    def _validate_json_structure(self, data: Any, max_depth: int = 10):
        """Recursively validate JSON structure"""
        if max_depth <= 0:
            raise ValueError("JSON structure too deep")

        if isinstance(data, dict):
            for key, value in data.items():
                if not isinstance(key, str):
                    raise ValueError("JSON keys must be strings")
                if len(key) > 100:
                    raise ValueError("JSON key too long")
                self._validate_json_structure(value, max_depth - 1)
        elif isinstance(data, list):
            if len(data) > 1000:
                raise ValueError("JSON array too large")
            for item in data:
                self._validate_json_structure(item, max_depth - 1)
        elif isinstance(data, str):
            if len(data) > 1000:
                raise ValueError("JSON string value too long")


# Global instance
input_validator = InputValidator()
