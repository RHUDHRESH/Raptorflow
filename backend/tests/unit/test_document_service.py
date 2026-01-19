"""
Unit tests for Document Service
Tests document upload, validation, and storage functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from fastapi import HTTPException
from datetime import datetime, UTC

from backend.services.document_service import (
    DocumentService, DocumentValidator, VirusScanner, GCPStorageManager,
    DocumentMetadata, ValidationResult, ScanResult
)


class TestDocumentValidator:
    """Test document validation functionality."""
    
    @pytest.mark.asyncio
    async def test_validate_valid_pdf(self):
        """Test validation of valid PDF file."""
        validator = DocumentValidator()
        
        # Mock upload file
        mock_file = MagicMock()
        mock_file.filename = "test.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.size = 1024
        
        result = await validator.validate(mock_file)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.file_info['content_type'] == "application/pdf"
    
    @pytest.mark.asyncio
    async def test_validate_invalid_file_type(self):
        """Test validation rejects unsupported file type."""
        validator = DocumentValidator()
        
        mock_file = MagicMock()
        mock_file.filename = "test.exe"
        mock_file.content_type = "application/exe"
        mock_file.size = 1024
        
        result = await validator.validate(mock_file)
        
        assert not result.is_valid
        assert any("Unsupported file type" in error for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_validate_file_too_large(self):
        """Test validation rejects oversized file."""
        validator = DocumentValidator()
        validator.max_file_size = 100  # 100 bytes limit
        
        mock_file = MagicMock()
        mock_file.filename = "large.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.size = 200  # Over limit
        
        result = await validator.validate(mock_file)
        
        assert not result.is_valid
        assert any("File too large" in error for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_validate_missing_filename(self):
        """Test validation rejects missing filename."""
        validator = DocumentValidator()
        
        mock_file = MagicMock()
        mock_file.filename = None
        mock_file.content_type = "application/pdf"
        mock_file.size = 1024
        
        result = await validator.validate(mock_file)
        
        assert not result.is_valid
        assert any("Filename is required" in error for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_extract_metadata(self):
        """Test metadata extraction."""
        validator = DocumentValidator()
        
        mock_file = AsyncMock()
        mock_file.filename = "test.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.seek = AsyncMock()
        mock_file.read = AsyncMock(return_value=b"test content")
        
        metadata = await validator.extract_metadata(mock_file)
        
        assert 'filename' in metadata
        assert 'content_type' in metadata
        assert 'upload_timestamp' in metadata
        assert 'sha256_checksum' in metadata
        assert metadata['filename'] == "test.pdf"


class TestVirusScanner:
    """Test virus scanning functionality."""
    
    @pytest.mark.asyncio
    async def test_scan_disabled(self):
        """Test scan returns clean when disabled."""
        with patch('backend.services.document_service.settings.VIRUS_SCAN_ENABLED', False):
            scanner = VirusScanner()
            
            mock_file = MagicMock()
            result = await scanner.scan(mock_file)
            
            assert not result.is_infected
            assert result.scan_engine == "disabled"
            assert len(result.threats_found) == 0
    
    @pytest.mark.asyncio
    async def test_scan_gcp_provider(self):
        """Test GCP virus scanning."""
        with patch('backend.services.document_service.settings.VIRUS_SCAN_ENABLED', True):
            with patch('backend.services.document_service.settings.VIRUS_SCAN_PROVIDER', 'gcp'):
                scanner = VirusScanner()
                
                mock_file = MagicMock()
                # Mock the internal scan method
                scanner._scan_with_gcp = AsyncMock(return_value=ScanResult(
                    is_infected=False,
                    scan_time=datetime.now(UTC),
                    threats_found=[],
                    scan_engine="gcp"
                ))
                
                result = await scanner.scan(mock_file)
                
                assert not result.is_infected
                assert result.scan_engine == "gcp"
    
    @pytest.mark.asyncio
    async def test_scan_clamav_provider(self):
        """Test ClamAV virus scanning."""
        with patch('backend.services.document_service.settings.VIRUS_SCAN_ENABLED', True):
            with patch('backend.services.document_service.settings.VIRUS_SCAN_PROVIDER', 'clamav'):
                scanner = VirusScanner()
                
                mock_file = MagicMock()
                # Mock the internal scan method
                scanner._scan_with_clamav = AsyncMock(return_value=ScanResult(
                    is_infected=False,
                    scan_time=datetime.now(UTC),
                    threats_found=[],
                    scan_engine="clamav"
                ))
                
                result = await scanner.scan(mock_file)
                
                assert not result.is_infected
                assert result.scan_engine == "clamav"


class TestGCPStorageManager:
    """Test Google Cloud Storage functionality."""
    
    @pytest.mark.asyncio
    @patch('backend.services.document_service.storage.Client')
    async def test_upload_file_success(self, mock_storage_client):
        """Test successful file upload."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        mock_storage_client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        storage_mgr = GCPStorageManager()
        
        mock_file = AsyncMock()
        mock_file.filename = "test.pdf"
        mock_file.content_type = "application/pdf"
        
        result = await storage_mgr.upload_file(mock_file, "test/key")
        
        assert result is True
        mock_blob.upload_from_file.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('backend.services.document_service.storage.Client')
    async def test_upload_file_failure(self, mock_storage_client):
        """Test file upload failure."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        mock_storage_client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.upload_from_file.side_effect = Exception("Upload failed")
        
        storage_mgr = GCPStorageManager()
        
        mock_file = AsyncMock()
        
        result = await storage_mgr.upload_file(mock_file, "test/key")
        
        assert result is False
    
    @pytest.mark.asyncio
    @patch('backend.services.document_service.storage.Client')
    async def test_download_file(self, mock_storage_client):
        """Test file download."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        mock_storage_client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.download_as_bytes.return_value = b"test content"
        
        storage_mgr = GCPStorageManager()
        result = await storage_mgr.download_file("test/key")
        
        assert result == b"test content"
        mock_blob.download_as_bytes.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('backend.services.document_service.storage.Client')
    async def test_delete_file(self, mock_storage_client):
        """Test file deletion."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        mock_storage_client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        storage_mgr = GCPStorageManager()
        result = await storage_mgr.delete_file("test/key")
        
        assert result is True
        mock_blob.delete.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('backend.services.document_service.storage.Client')
    async def test_generate_signed_url(self, mock_storage_client):
        """Test signed URL generation."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        mock_storage_client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.generate_signed_url.return_value = "https://signed-url.com"
        
        storage_mgr = GCPStorageManager()
        result = storage_mgr.generate_signed_url("test/key")
        
        assert result == "https://signed-url.com"
        mock_blob.generate_signed_url.assert_called_once()


class TestDocumentService:
    """Test main document service functionality."""
    
    @pytest.mark.asyncio
    @patch('backend.services.document_service.GCPStorageManager')
    @patch('backend.services.document_service.VirusScanner')
    @patch('backend.services.document_service.DocumentValidator')
    async def test_upload_document_success(self, mock_validator_cls, mock_scanner_cls, mock_storage_cls):
        """Test successful document upload."""
        # Setup mocks
        mock_validator = mock_validator_cls.return_value
        mock_validator.validate = AsyncMock(return_value=ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            file_info={'content_type': 'application/pdf', 'size': 1024}
        ))
        mock_validator.extract_metadata = AsyncMock(return_value={})
        
        mock_scanner = mock_scanner_cls.return_value
        mock_scanner.scan = AsyncMock(return_value=ScanResult(
            is_infected=False,
            scan_time=datetime.now(UTC),
            threats_found=[],
            scan_engine="gcp"
        ))
        
        mock_storage = mock_storage_cls.return_value
        mock_storage.upload_file = AsyncMock(return_value=True)
        
        service = DocumentService()
        
        mock_file = MagicMock()
        mock_file.filename = "test.pdf"
        mock_file.content_type = "application/pdf"
        
        result = await service.upload_document(mock_file, "workspace-123", "user-123")
        
        assert isinstance(result, DocumentMetadata)
        assert result.filename == "test.pdf"
        assert result.content_type == "application/pdf"
        assert result.workspace_id == "workspace-123"
        assert result.user_id == "user-123"
        assert result.scan_result.is_infected is False
    
    @pytest.mark.asyncio
    @patch('backend.services.document_service.GCPStorageManager')
    @patch('backend.services.document_service.VirusScanner')
    @patch('backend.services.document_service.DocumentValidator')
    async def test_upload_document_validation_failure(self, mock_validator_cls, mock_scanner_cls, mock_storage_cls):
        """Test document upload with validation failure."""
        mock_validator = mock_validator_cls.return_value
        mock_validator.validate = AsyncMock(return_value=ValidationResult(
            is_valid=False,
            errors=["File too large"],
            warnings=[],
            file_info=None
        ))
        
        service = DocumentService()
        
        mock_file = MagicMock()
        mock_file.filename = "large.pdf"
        
        with pytest.raises(HTTPException) as exc_info:
            await service.upload_document(mock_file, "workspace-123", "user-123")
        
        assert exc_info.value.status_code == 400
        assert "Validation failed" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    @patch('backend.services.document_service.GCPStorageManager')
    @patch('backend.services.document_service.VirusScanner')
    @patch('backend.services.document_service.DocumentValidator')
    async def test_upload_document_virus_detected(self, mock_validator_cls, mock_scanner_cls, mock_storage_cls):
        """Test document upload with virus detected."""
        mock_validator = mock_validator_cls.return_value
        mock_validator.validate = AsyncMock(return_value=ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            file_info={'content_type': 'application/pdf'}
        ))
        
        mock_scanner = mock_scanner_cls.return_value
        mock_scanner.scan = AsyncMock(return_value=ScanResult(
            is_infected=True,
            scan_time=datetime.now(UTC),
            threats_found=["Trojan.Generic"],
            scan_engine="clamav"
        ))
        
        service = DocumentService()
        
        mock_file = MagicMock()
        mock_file.filename = "infected.pdf"
        
        with pytest.raises(HTTPException) as exc_info:
            await service.upload_document(mock_file, "workspace-123", "user-123")
        
        assert exc_info.value.status_code == 400
        assert "Security scan failed" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    @patch('backend.services.document_service.GCPStorageManager')
    @patch('backend.services.document_service.VirusScanner')
    async def test_get_document(self, mock_scanner, mock_storage):
        """Test getting document metadata."""
        # This would test database retrieval
        service = DocumentService()
        
        result = await service.get_document("doc-123", "workspace-123")
        
        # For now, returns None as placeholder
        assert result is None
    
    @pytest.mark.asyncio
    @patch('backend.services.document_service.GCPStorageManager')
    @patch('backend.services.document_service.VirusScanner')
    async def test_delete_document(self, mock_scanner, mock_storage_cls):
        """Test document deletion."""
        mock_storage = mock_storage_cls.return_value
        mock_storage.delete_file = AsyncMock(return_value=True)
        
        service = DocumentService()
        
        # Mock get_document to return something
        service.get_document = AsyncMock(return_value=DocumentMetadata(
            id="doc-123",
            filename="test.pdf",
            s3_key="test/key",
            size=1024,
            content_type="application/pdf",
            workspace_id="ws-123",
            user_id="user-123",
            checksum="abc",
            metadata={},
            created_at=datetime.now(UTC)
        ))
        
        result = await service.delete_document("doc-123", "workspace-123")
        
        assert result is True
        mock_storage.delete_file.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('backend.services.document_service.GCPStorageManager')
    @patch('backend.services.document_service.VirusScanner')
    async def test_list_documents(self, mock_scanner, mock_storage):
        """Test listing documents."""
        service = DocumentService()
        
        result = await service.list_documents("workspace-123")
        
        # For now, returns empty list as placeholder
        assert result == []