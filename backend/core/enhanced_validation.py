"""
RaptorFlow Enhanced Data Validation
Provides robust Pydantic validation with improved error handling and custom validators.
"""

import logging
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union, get_type_hints

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
    validator,
)
from pydantic_core import ErrorDetails

from core.enhanced_exceptions import ValidationError as RaptorValidationError
from core.enhanced_exceptions import handle_validation_error

logger = logging.getLogger("raptorflow.validation")


class ValidationSeverity(Enum):
    """Validation error severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Individual validation issue."""

    field: str
    message: str
    severity: ValidationSeverity
    code: str
    value: Any
    constraint: Optional[str] = None


@dataclass
class ValidationResult:
    """Validation result with issues."""

    is_valid: bool
    issues: List[ValidationIssue]
    data: Optional[Dict[str, Any]] = None
    cleaned_data: Optional[Dict[str, Any]] = None

    def add_issue(
        self,
        field: str,
        message: str,
        severity: ValidationSeverity,
        code: str,
        value: Any,
        constraint: Optional[str] = None,
    ):
        """Add a validation issue."""
        self.issues.append(
            ValidationIssue(
                field=field,
                message=message,
                severity=severity,
                code=code,
                value=value,
                constraint=constraint,
            )
        )

        if severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
            self.is_valid = False

    def get_errors(self) -> List[ValidationIssue]:
        """Get only error-level issues."""
        return [
            issue
            for issue in self.issues
            if issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
        ]

    def get_warnings(self) -> List[ValidationIssue]:
        """Get only warning-level issues."""
        return [
            issue
            for issue in self.issues
            if issue.severity == ValidationSeverity.WARNING
        ]


class EnhancedValidator:
    """
    Enhanced validator with custom rules and improved error handling.
    """

    def __init__(self):
        self.custom_validators = {}
        self.global_constraints = {}

    def add_validator(self, name: str, validator_func):
        """Add a custom validator function."""
        self.custom_validators[name] = validator_func

    def add_constraint(self, field: str, constraint: Dict[str, Any]):
        """Add a global constraint for a field."""
        self.global_constraints[field] = constraint

    def validate_email(self, value: str) -> bool:
        """Validate email format."""
        if not value:
            return True

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, value))

    def validate_phone(self, value: str) -> bool:
        """Validate phone number format."""
        if not value:
            return True

        # Remove common formatting characters
        cleaned = re.sub(r"[^\d+]", "", value)

        # Check if it's a valid phone number (10-15 digits, optional +)
        pattern = r"^\+?[1-9]\d{9,14}$"
        return bool(re.match(pattern, cleaned))

    def validate_url(self, value: str) -> bool:
        """Validate URL format."""
        if not value:
            return True

        pattern = r"^https?:\/\/(?:[-\w.])+(?:\:[0-9]+)?(?:\/(?:[\w\/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$"
        return bool(re.match(pattern, value))

    def validate_uuid(self, value: str) -> bool:
        """Validate UUID format."""
        if not value:
            return True

        pattern = (
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )
        return bool(re.match(pattern, value.lower()))

    def validate_date_range(
        self,
        value: date,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
    ) -> bool:
        """Validate date is within range."""
        if min_date and value < min_date:
            return False
        if max_date and value > max_date:
            return False
        return True

    def validate_string_length(
        self,
        value: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> bool:
        """Validate string length."""
        if min_length and len(value) < min_length:
            return False
        if max_length and len(value) > max_length:
            return False
        return True

    def validate_numeric_range(
        self,
        value: Union[int, float],
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
    ) -> bool:
        """Validate numeric range."""
        if min_value is not None and value < min_value:
            return False
        if max_value is not None and value > max_value:
            return False
        return True

    def sanitize_string(self, value: str) -> str:
        """Sanitize string input."""
        if not value:
            return value

        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>"\']', "", value)

        # Trim whitespace
        sanitized = sanitized.strip()

        return sanitized

    def validate_model(
        self, model_class: Type[BaseModel], data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate data against a Pydantic model with enhanced error handling."""
        result = ValidationResult(is_valid=True, issues=[], data=data)

        try:
            # Validate with Pydantic
            instance = model_class(**data)
            result.cleaned_data = instance.model_dump()

            # Run custom validators
            self._run_custom_validators(model_class, data, result)

            # Run global constraints
            self._run_global_constraints(model_class, data, result)

        except ValidationError as e:
            # Convert Pydantic errors to ValidationIssues
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                message = error["msg"]
                code = error["type"]
                value = error.get("input")

                severity = ValidationSeverity.ERROR
                if code in ["missing", "forbidden"]:
                    severity = ValidationSeverity.CRITICAL
                elif code in [
                    "string_too_short",
                    "string_too_long",
                    "greater_than",
                    "less_than",
                ]:
                    severity = ValidationSeverity.WARNING

                result.add_issue(field, message, severity, code, value)

        except Exception as e:
            result.add_issue(
                "model",
                f"Unexpected validation error: {str(e)}",
                ValidationSeverity.CRITICAL,
                "validation_error",
                data,
            )

        return result

    def _run_custom_validators(
        self,
        model_class: Type[BaseModel],
        data: Dict[str, Any],
        result: ValidationResult,
    ):
        """Run custom validators on the data."""
        for field_name, validator_func in self.custom_validators.items():
            if field_name in data:
                try:
                    value = data[field_name]
                    validation_result = validator_func(value)

                    if isinstance(validation_result, bool):
                        if not validation_result:
                            result.add_issue(
                                field_name,
                                f"Custom validation failed for field '{field_name}'",
                                ValidationSeverity.ERROR,
                                "custom_validation_failed",
                                value,
                            )
                    elif isinstance(validation_result, str):
                        result.add_issue(
                            field_name,
                            validation_result,
                            ValidationSeverity.ERROR,
                            "custom_validation_failed",
                            value,
                        )

                except Exception as e:
                    result.add_issue(
                        field_name,
                        f"Custom validator error: {str(e)}",
                        ValidationSeverity.WARNING,
                        "custom_validator_error",
                        data[field_name],
                    )

    def _run_global_constraints(
        self,
        model_class: Type[BaseModel],
        data: Dict[str, Any],
        result: ValidationResult,
    ):
        """Run global constraints on the data."""
        for field_name, constraint in self.global_constraints.items():
            if field_name in data:
                value = data[field_name]

                # Check type constraint
                if "type" in constraint:
                    expected_type = constraint["type"]
                    if not isinstance(value, expected_type):
                        result.add_issue(
                            field_name,
                            f"Expected type {expected_type.__name__}, got {type(value).__name__}",
                            ValidationSeverity.ERROR,
                            "type_mismatch",
                            value,
                        )

                # Check length constraint
                if "min_length" in constraint or "max_length" in constraint:
                    if isinstance(value, str):
                        min_len = constraint.get("min_length")
                        max_len = constraint.get("max_length")

                        if not self.validate_string_length(value, min_len, max_len):
                            result.add_issue(
                                field_name,
                                f"String length constraint violated",
                                ValidationSeverity.WARNING,
                                "length_constraint_violated",
                                value,
                            )

                # Check range constraint
                if "min_value" in constraint or "max_value" in constraint:
                    if isinstance(value, (int, float)):
                        min_val = constraint.get("min_value")
                        max_val = constraint.get("max_value")

                        if not self.validate_numeric_range(value, min_val, max_val):
                            result.add_issue(
                                field_name,
                                f"Numeric range constraint violated",
                                ValidationSeverity.WARNING,
                                "range_constraint_violated",
                                value,
                            )


# Base model with enhanced validation
class EnhancedBaseModel(BaseModel):
    """
    Base Pydantic model with enhanced validation capabilities.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    def validate_with_enhanced_validator(
        self, validator: EnhancedValidator
    ) -> ValidationResult:
        """Validate model with enhanced validator."""
        return validator.validate_model(self.__class__, self.model_dump())

    @classmethod
    def validate_data(
        cls, data: Dict[str, Any], validator: Optional[EnhancedValidator] = None
    ) -> ValidationResult:
        """Validate data dictionary against this model."""
        if validator is None:
            validator = EnhancedValidator()
        return validator.validate_model(cls, data)


# Custom field validators
class CommonValidators:
    """Common validation functions."""

    @staticmethod
    def email_validator(value: str) -> str:
        """Validate and normalize email."""
        validator = EnhancedValidator()
        if not validator.validate_email(value):
            raise RaptorValidationError("Invalid email format", field="email")
        return value.lower().strip()

    @staticmethod
    def phone_validator(value: str) -> str:
        """Validate and normalize phone number."""
        validator = EnhancedValidator()
        if not validator.validate_phone(value):
            raise RaptorValidationError("Invalid phone number format", field="phone")
        # Remove formatting characters
        return re.sub(r"[^\d+]", "", value)

    @staticmethod
    def url_validator(value: str) -> str:
        """Validate and normalize URL."""
        validator = EnhancedValidator()
        if not validator.validate_url(value):
            raise RaptorValidationError("Invalid URL format", field="url")
        return value

    @staticmethod
    def uuid_validator(value: str) -> str:
        """Validate and normalize UUID."""
        validator = EnhancedValidator()
        if not validator.validate_uuid(value):
            raise RaptorValidationError("Invalid UUID format", field="uuid")
        return value.lower()

    @staticmethod
    def future_date_validator(value: date) -> date:
        """Validate date is in the future."""
        if value <= date.today():
            raise RaptorValidationError("Date must be in the future", field="date")
        return value

    @staticmethod
    def past_date_validator(value: date) -> date:
        """Validate date is in the past."""
        if value >= date.today():
            raise RaptorValidationError("Date must be in the past", field="date")
        return value

    @staticmethod
    def positive_number_validator(value: Union[int, float]) -> Union[int, float]:
        """Validate number is positive."""
        if value <= 0:
            raise RaptorValidationError("Value must be positive", field="value")
        return value

    @staticmethod
    def non_empty_string_validator(value: str) -> str:
        """Validate string is not empty."""
        if not value or not value.strip():
            raise RaptorValidationError("String cannot be empty", field="value")
        return value.strip()


# Global validator instance
_enhanced_validator: Optional[EnhancedValidator] = None


def get_enhanced_validator() -> EnhancedValidator:
    """Get the global enhanced validator instance."""
    global _enhanced_validator
    if _enhanced_validator is None:
        _enhanced_validator = EnhancedValidator()

        # Register common validators
        _enhanced_validator.add_validator("email", CommonValidators.email_validator)
        _enhanced_validator.add_validator("phone", CommonValidators.phone_validator)
        _enhanced_validator.add_validator("url", CommonValidators.url_validator)
        _enhanced_validator.add_validator("uuid", CommonValidators.uuid_validator)
        _enhanced_validator.add_validator(
            "future_date", CommonValidators.future_date_validator
        )
        _enhanced_validator.add_validator(
            "past_date", CommonValidators.past_date_validator
        )
        _enhanced_validator.add_validator(
            "positive_number", CommonValidators.positive_number_validator
        )
        _enhanced_validator.add_validator(
            "non_empty_string", CommonValidators.non_empty_string_validator
        )

    return _enhanced_validator


# Utility functions
def validate_with_enhanced_validator(
    model_class: Type[EnhancedBaseModel],
    data: Dict[str, Any],
    validator: Optional[EnhancedValidator] = None,
) -> ValidationResult:
    """Validate data with enhanced validator."""
    if validator is None:
        validator = get_enhanced_validator()
    return validator.validate_model(model_class, data)


def handle_pydantic_validation_error(
    error: ValidationError, context: Optional[str] = None
) -> RaptorValidationError:
    """Convert Pydantic ValidationError to RaptorValidationError."""
    error_details = []

    for err in error.errors():
        field = ".".join(str(loc) for loc in err["loc"])
        message = f"{field}: {err['msg']}"
        error_details.append(message)

    full_message = "; ".join(error_details)

    return handle_validation_error(
        f"Validation failed: {full_message}",
        context=context,
        validation_errors=error.errors(),
    )


if __name__ == "__main__":
    # Test enhanced validation
    validator = get_enhanced_validator()

    # Test data
    test_data = {
        "email": "invalid-email",
        "phone": "123",
        "url": "not-a-url",
        "value": -10,
    }

    # Define a simple model
    class TestModel(EnhancedBaseModel):
        email: str
        phone: Optional[str] = None
        url: Optional[str] = None
        value: int

    # Validate
    result = validator.validate_model(TestModel, test_data)

    print(f"Validation result: {result.is_valid}")
    for issue in result.issues:
        print(f"  {issue.severity.value}: {issue.field} - {issue.message}")
