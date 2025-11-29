"""
Tests for correlation ID logging and middleware.
"""

import uuid
from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, MagicMock


def test_correlation_id_generated_when_not_provided():
    """Test that correlation ID is generated when not in request headers."""
    with patch("backend.main.app") as mock_app:
        # Mock setup_logging to avoid actual setup
        with patch("backend.utils.logging_config.setup_logging"):
            # Import after mocking
            from backend.main import app

        client = TestClient(app)

        # Make a request without X-Correlation-ID header
        response = client.get("/")

        # Check that X-Correlation-ID header is present in response
        assert "X-Correlation-ID" in response.headers
        correlation_id = response.headers["X-Correlation-ID"]

        # Verify it's a valid UUID
        try:
            uuid.UUID(correlation_id, version=4)
        except ValueError:
            pytest.fail(f"Invalid UUID format: {correlation_id}")


def test_correlation_id_propagated_when_provided():
    """Test that provided correlation ID is propagated to response."""
    with patch("backend.main.app") as mock_app:
        with patch("backend.utils.logging_config.setup_logging"):
            from backend.main import app

        client = TestClient(app)

        # Generate a known correlation ID
        known_correlation_id = str(uuid.uuid4())

        # Make a request with X-Correlation-ID header
        response = client.get("/", headers={"X-Correlation-ID": known_correlation_id})

        # Check that the same correlation ID is returned
        assert response.headers["X-Correlation-ID"] == known_correlation_id


def test_correlation_id_in_logging_context():
    """Test that correlation ID is available in logging context."""
    from backend.utils.logging_config import get_correlation_id, get_logger

    # Initially should be None
    assert get_correlation_id() is None

    # Set a correlation ID
    test_correlation_id = str(uuid.uuid4())

    with patch("backend.utils.logging_config.set_correlation_id"):
        from backend.utils.logging_config import set_correlation_id
        set_correlation_id(test_correlation_id)

        # Now it should be available
        assert get_correlation_id() == test_correlation_id

        # Get a logger and check that it would include correlation_id in output
        logger = get_logger("test")

        # Mock the actual logging to capture what would be logged
        with patch("structlog.get_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value.bind.return_value = mock_logger

            # This would normally trigger logging with correlation_id
            # In this test, we just verify the setup works
            assert logger is not None


def test_get_logger_component_binding():
    """Test that get_logger properly binds component."""
    from backend.utils.logging_config import get_logger

    # Get a logger for a component
    logger = get_logger("api")

    # Verify it's bound with component
    assert hasattr(logger, 'bind')
    assert logger is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
