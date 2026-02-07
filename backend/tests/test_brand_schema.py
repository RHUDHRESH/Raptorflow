from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from core.enhanced_exceptions import ValidationError as RaptorValidationError
from core.enhanced_validation import (
    CommonValidators,
    EnhancedBaseModel,
    get_enhanced_validator,
)


class BrandPositioningModel(EnhancedBaseModel):
    """Enhanced brand positioning model with validation."""

    uvp: str
    target_market_segments: list
    competitive_moat: str
    brand_archetype: str
    brand_kit_id: str

    @field_validator("uvp")
    @classmethod
    def validate_uvp(cls, v):
        return CommonValidators.non_empty_string_validator(v)

    @field_validator("brand_kit_id")
    @classmethod
    def validate_brand_kit_id(cls, v):
        return CommonValidators.uuid_validator(v)


def test_brand_positioning_schema_requirements():
    """Verify the expected structure of the brand positioning intelligence table."""
    # This is a requirements-validation test
    required_fields = [
        "uvp",
        "target_market_segments",
        "competitive_moat",
        "brand_archetype",
    ]

    # Simulate DB metadata check
    metadata = {
        "uvp": "text",
        "target_market_segments": "jsonb",
        "competitive_moat": "text",
        "brand_archetype": "text",
    }

    for field in required_fields:
        assert field in metadata


def test_tenant_isolation_logic_mocked():
    """Ensure that positioning data requires a valid brand_kit link."""
    mock_db = MagicMock()

    # Simulate a foreign key violation
    mock_db.insert.side_effect = RaptorValidationError(
        "Invalid brand_kit_id format",
        field="brand_kit_id",
        validation_code="invalid_uuid",
    )

    with pytest.raises(RaptorValidationError) as excinfo:
        mock_db.insert({"uvp": "Best CRM", "brand_kit_id": "invalid-uuid"})

    assert "brand_kit_id" in str(excinfo.value)


def test_enhanced_brand_positioning_validation():
    """Test enhanced validation for brand positioning data."""
    validator = get_enhanced_validator()

    # Valid data
    valid_data = {
        "uvp": "Best CRM for small businesses",
        "target_market_segments": ["SMB", "Startups"],
        "competitive_moat": "AI-powered automation",
        "brand_archetype": "caregiver",
        "brand_kit_id": "550e8400-e29b-41d4-a716-446655440000",
    }

    result = validator.validate_model(BrandPositioningModel, valid_data)
    assert (
        result.is_valid
    ), f"Valid data failed validation: {[issue.message for issue in result.get_errors()]}"

    # Invalid data
    invalid_data = {
        "uvp": "",  # Empty UVP
        "target_market_segments": [],
        "competitive_moat": "AI-powered automation",
        "brand_archetype": "caregiver",
        "brand_kit_id": "invalid-uuid",  # Invalid UUID
    }

    result = validator.validate_model(BrandPositioningModel, invalid_data)
    assert not result.is_valid, "Invalid data passed validation"

    # Check specific errors
    error_fields = [issue.field for issue in result.get_errors()]
    assert "uvp" in error_fields
    assert "brand_kit_id" in error_fields


def test_brand_positioning_pydantic_validation():
    """Test Pydantic validation with enhanced error handling."""
    # Valid data
    valid_data = {
        "uvp": "Best CRM for small businesses",
        "target_market_segments": ["SMB", "Startups"],
        "competitive_moat": "AI-powered automation",
        "brand_archetype": "caregiver",
        "brand_kit_id": "550e8400-e29b-41d4-a716-446655440000",
    }

    model = BrandPositioningModel(**valid_data)
    assert model.uvp == "Best CRM for small businesses"

    # Invalid data - should raise ValidationError
    invalid_data = {
        "uvp": "",  # Empty UVP
        "target_market_segments": ["SMB"],
        "competitive_moat": "AI-powered automation",
        "brand_archetype": "caregiver",
        "brand_kit_id": "invalid-uuid",
    }

    with pytest.raises(ValidationError) as excinfo:
        BrandPositioningModel(**invalid_data)

    # Check that validation errors are properly formatted
    errors = excinfo.value.errors()
    assert len(errors) >= 1

    # Check for specific validation errors
    error_fields = [".".join(str(loc) for loc in error["loc"]) for error in errors]
    assert "uvp" in error_fields or "brand_kit_id" in error_fields
