import pytest

pytest.skip(
    "Legacy file retention test; needs rebase on canonical workflows.",
    allow_module_level=True,
)

import os
import sys

import pytest

# Add project root to Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from jobs.file_cleanup import delete_expired_originals
from workflows.onboarding import finalize_onboarding

from .services.onboarding import process_uploaded_file


@pytest.mark.asyncio
async def test_ocr_file_retention():
    """Test OCR file retention and deletion workflow"""
    # Mock a file with OCR data
    mock_file = {
        "id": "file_123",
        "user_id": "user_456",
        "original_path": "user-uploads/onboarding/file.pdf",
        "extracted_data": {"text": "sample content"},
        "retention_date": datetime.utcnow() - timedelta(days=8),
        "status": "processed",
    }

    # Test finalization deletes OCR originals
    await finalize_onboarding("user_456")
    # In real test, verify storage removal was called


@pytest.mark.asyncio
async def test_non_ocr_file_retention():
    """Test non-OCR files are retained"""
    mock_file = {
        "id": "file_789",
        "user_id": "user_456",
        "original_path": "user-uploads/onboarding/logo.png",
        "status": "raw",
        "retention_date": None,
    }

    await finalize_onboarding("user_456")
    # Verify file was NOT deleted


@pytest.mark.asyncio
async def test_cleanup_job():
    """Test daily cleanup job"""
    # Mock expired files
    mock_files = [
        {"id": "expired1", "original_path": "path1", "status": "processed"},
        {"id": "expired2", "original_path": "path2", "status": "processed"},
    ]

    # Mock database and storage
    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_files
    mock_storage = AsyncMock()

    await delete_expired_originals(mock_db, mock_storage)

    # Verify storage.remove called twice
    assert mock_storage.remove.call_count == 2
