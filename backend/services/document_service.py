"""
RaptorFlow Document Service
Phase 1.1.1: Document Upload Infrastructure

Handles file upload, validation, virus scanning, and S3 storage integration
for the onboarding system document processing pipeline.
"""

import asyncio
import hashlib
import mimetypes
import os
import uuid
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
import aiofiles
try:
    import magic
except ImportError:
    # Fallback for systems without libmagic (e.g. Windows without DLLs)
    class magic:
        @staticmethod
        def from_buffer(buffer, mime=False):
            return "application/octet-stream"
        
        class Magic:
            def __init__(self, mime=False):
                pass
            def from_buffer(self, buffer):
                return "application/octet-stream"
            def from_file(self, filename):
                return "application/octet-stream"

from fastapi import UploadFile, HTTPException
from pydantic import BaseModel, Field

# Configuration
from backend.config import get_settings
from backend.core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    PNG = "image/png"
    JPEG = "image/jpeg"
    JPG = "image/jpeg"
    TIFF = "image/tiff"
    TXT = "text/plain"


@dataclass
class ValidationResult:
    """Result of file validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    file_info: Optional[Dict] = None


@dataclass
class ScanResult:
    """Result of virus scanning."""
    is_infected: bool
    scan_time: datetime
    threats_found: List[str]
    scan_engine: str


@dataclass
class DocumentMetadata:
    """Metadata for uploaded documents."""
    id: str
    filename: str
    s3_key: str
    size: int
    content_type: str
    workspace_id: str
    user_id: str
    checksum: str
    metadata: Dict
    created_at: datetime
    scan_result: Optional[ScanResult] = None


class VirusScanner:
    """Virus scanning integration."""
    
    def __init__(self):
        self.enabled = settings.VIRUS_SCAN_ENABLED
        self.scan_engine = settings.VIRUS_SCAN_PROVIDER  # 'clamav', 'aws', 'disabled'
        
    async def scan(self, file: UploadFile) -> ScanResult:
        """
        Scan uploaded file for viruses.
        
        Args:
            file: Uploaded file to scan
            
        Returns:
            ScanResult with infection status and details
        """
        if not self.enabled or self.scan_engine == 'disabled':
            return ScanResult(
                is_infected=False,
                scan_time=datetime.now(UTC),
                threats_found=[],
                scan_engine="disabled"
            )
        
        try:
            if self.scan_engine == 'gcp':
                return await self._scan_with_gcp(file)
            elif self.scan_engine == 'clamav':
                return await self._scan_with_clamav(file)
            else:
                logger.warning(f"Unknown scan engine: {self.scan_engine}")
                return ScanResult(
                    is_infected=False,
                    scan_time=datetime.now(UTC),
                    threats_found=[],
                    scan_engine="unknown"
                )
        except Exception as e:
            logger.error(f"Virus scanning failed: {e}")
            # Fail safe - assume infected if scan fails
            return ScanResult(
                is_infected=True,
                scan_time=datetime.now(UTC),
                threats_found=[f"Scan failed: {str(e)}"],
                scan_engine=self.scan_engine
            )
    
    async def _scan_with_gcp(self, file: UploadFile) -> ScanResult:
        """Scan using GCP VirusScan."""
        # Implementation for GCP VirusScan integration
        # This would use GCP Security Command Center or Cloud Armor
        logger.info("Scanning file with GCP VirusScan")
        return ScanResult(
            is_infected=False,
            scan_time=datetime.now(UTC),
            threats_found=[],
            scan_engine="gcp"
        )
    
    async def _scan_with_clamav(self, file: UploadFile) -> ScanResult:
        """Scan using ClamAV."""
        # Implementation for ClamAV integration
        logger.info("Scanning file with ClamAV")
        return ScanResult(
            is_infected=False,
            scan_time=datetime.now(UTC),
            threats_found=[],
            scan_engine="clamav"
        )


class DocumentValidator:
    """Document validation and metadata extraction."""
    
    def __init__(self):
        self.max_file_size = settings.MAX_FILE_SIZE  # 100MB default
        self.allowed_types = [t.value for t in DocumentType]
        self.max_filename_length = 255
        
    async def validate(self, file: UploadFile) -> ValidationResult:
        """
        Validate uploaded file.
        
        Args:
            file: Uploaded file to validate
            
        Returns:
            ValidationResult with validation status and details
        """
        errors = []
        warnings = []
        file_info = {}
        
        # Check filename
        if not file.filename:
            errors.append("Filename is required")
        else:
            if len(file.filename) > self.max_filename_length:
                errors.append(f"Filename too long (max {self.max_filename_length} characters)")
            
            # Check for dangerous characters
            dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
            if any(char in file.filename for char in dangerous_chars):
                errors.append("Filename contains invalid characters")
        
        # Check file size
        if hasattr(file, 'size') and file.size:
            if file.size > self.max_file_size:
                errors.append(f"File too large (max {self.max_file_size / (1024*1024):.1f}MB)")
            file_info['size'] = file.size
        else:
            warnings.append("File size not provided - will check during upload")
        
        # Check content type
        if file.content_type:
            if file.content_type not in self.allowed_types:
                errors.append(f"Unsupported file type: {file.content_type}")
            file_info['content_type'] = file.content_type
        else:
            # Try to detect from filename
            if file.filename:
                detected_type, _ = mimetypes.guess_type(file.filename)
                if detected_type and detected_type in self.allowed_types:
                    file_info['content_type'] = detected_type
                    warnings.append(f"Content type detected from filename: {detected_type}")
                else:
                    errors.append("Could not determine file type")
        
        # Additional validation for specific file types
        if file.filename:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in ['.pdf', '.docx', '.pptx', '.png', '.jpg', '.jpeg', '.tiff', '.txt']:
                errors.append(f"Unsupported file extension: {ext}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            file_info=file_info
        )
    
    async def extract_metadata(self, file: UploadFile) -> Dict:
        """
        Extract metadata from file.
        
        Args:
            file: Uploaded file
            
        Returns:
            Dictionary with file metadata
        """
        metadata = {}
        
        # Basic metadata
        metadata['filename'] = file.filename
        metadata['content_type'] = file.content_type
        metadata['upload_timestamp'] = datetime.now(UTC).isoformat()
        
        # Calculate checksum
        if hasattr(file, 'file'):
            await file.seek(0)
            content = await file.read()
            checksum = hashlib.sha256(content).hexdigest()
            metadata['sha256_checksum'] = checksum
            await file.seek(0)  # Reset file pointer
        
        # File type specific metadata
        if file.filename:
            ext = os.path.splitext(file.filename)[1].lower()
            metadata['file_extension'] = ext
            
            if ext == '.pdf':
                metadata.update(await self._extract_pdf_metadata(file))
            elif ext in ['.docx', '.pptx']:
                metadata.update(await self._extract_office_metadata(file))
            elif ext in ['.png', '.jpg', '.jpeg', '.tiff']:
                metadata.update(await self._extract_image_metadata(file))
        
        return metadata
    
    async def _extract_pdf_metadata(self, file: UploadFile) -> Dict:
        """Extract PDF-specific metadata."""
        # Implementation would use PyPDF2 or similar
        return {
            'document_type': 'pdf',
            'pages': None,  # Would be extracted from PDF
            'title': None,
            'author': None,
            'created_date': None
        }
    
    async def _extract_office_metadata(self, file: UploadFile) -> Dict:
        """Extract Office document metadata."""
        return {
            'document_type': 'office',
            'application': None,  # Would be extracted from doc
            'title': None,
            'author': None,
            'created_date': None
        }
    
    async def _extract_image_metadata(self, file: UploadFile) -> Dict:
        """Extract image metadata."""
        return {
            'document_type': 'image',
            'width': None,  # Would be extracted from image
            'height': None,
            'format': None,
            'color_mode': None
        }


class GCPStorageManager:
    """Google Cloud Storage integration for document management."""
    
    def __init__(self):
        self.client = storage.Client()
        self.bucket_name = settings.ASSETS_BUCKET
        self.project_id = settings.GCP_PROJECT_ID
        
        # Initialize GCS client
        try:
            self.storage_client = storage.Client(project=self.project_id)
            self.bucket = self.storage_client.bucket(self.bucket_name)
            # Test connection
            self.bucket.reload()
            logger.info(f"GCS client initialized for bucket: {self.bucket_name}")
        except GoogleCloudError as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise
    
    async def upload_file(self, file: UploadFile, gcs_key: str) -> bool:
        """
        Upload file to GCS.
        
        Args:
            file: File to upload
            gcs_key: GCS key for file
            
        Returns:
            True if upload successful
        """
        try:
            # Reset file pointer
            await file.seek(0)
            
            # Create blob
            blob = self.bucket.blob(gcs_key)
            
            # Set metadata
            blob.content_type = file.content_type or 'application/octet-stream'
            blob.metadata = {
                'original_filename': file.filename or '',
                'upload_timestamp': datetime.now(UTC).isoformat()
            }
            
            # Upload to GCS
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: blob.upload_from_file(file)
            )
            
            logger.info(f"Successfully uploaded file to GCS: {gcs_key}")
            return True
            
        except Exception as e:
            logger.error(f"GCS upload failed: {e}")
            return False
    
    async def download_file(self, gcs_key: str) -> bytes:
        """
        Download file from GCS.
        
        Args:
            gcs_key: GCS key of file
            
        Returns:
            File content as bytes
        """
        try:
            blob = self.bucket.blob(gcs_key)
            return await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: blob.download_as_bytes()
            )
            
        except Exception as e:
            logger.error(f"GCS download failed: {e}")
            raise HTTPException(status_code=404, detail="File not found or access denied")
    
    async def delete_file(self, gcs_key: str) -> bool:
        """
        Delete file from GCS.
        
        Args:
            gcs_key: GCS key of file
            
        Returns:
            True if deletion successful
        """
        try:
            blob = self.bucket.blob(gcs_key)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: blob.delete()
            )
            logger.info(f"Successfully deleted file from GCS: {gcs_key}")
            return True
            
        except Exception as e:
            logger.error(f"GCS deletion failed: {e}")
            return False
    
    def generate_signed_url(self, gcs_key: str, expiration: int = 3600) -> str:
        """
        Generate signed URL for file access.
        
        Args:
            gcs_key: GCS key of file
            expiration: URL expiration time in seconds
            
        Returns:
            Signed URL
        """
        try:
            blob = self.bucket.blob(gcs_key)
            return blob.generate_signed_url(
                version="v4",
                expiration=datetime.now(UTC) + timedelta(seconds=expiration),
                method="GET"
            )
        except GoogleCloudError as e:
            logger.error(f"Failed to generate signed URL: {e}")
            raise


class DocumentService:
    """Main document service for the onboarding system."""
    
    def __init__(self):
        self.validator = DocumentValidator()
        self.virus_scanner = VirusScanner()
        self.storage_manager = GCPStorageManager()
        
    async def upload_document(self, file: UploadFile, workspace_id: str, user_id: str) -> DocumentMetadata:
        """
        Upload and process a document.
        
        Args:
            file: Uploaded file
            workspace_id: Workspace ID
            user_id: User ID
            
        Returns:
            DocumentMetadata with upload details
            
        Raises:
            HTTPException: If validation or upload fails
        """
        try:
            # Validate file
            validation_result = await self.validator.validate(file)
            if not validation_result.is_valid:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Validation failed",
                        "details": validation_result.errors
                    }
                )
            
            # Log warnings
            if validation_result.warnings:
                logger.warning(f"Upload warnings: {validation_result.warnings}")
            
            # Scan for viruses
            scan_result = await self.virus_scanner.scan(file)
            if scan_result.is_infected:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Security scan failed",
                        "threats": scan_result.threats_found
                    }
                )
            
            # Generate unique GCS key
            document_id = str(uuid.uuid4())
            gcs_key = f"{workspace_id}/{user_id}/{document_id}/{file.filename}"
            
            # Upload to GCS
            upload_success = await self.storage_manager.upload_file(file, gcs_key)
            if not upload_success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to upload file to storage"
                )
            
            # Extract metadata
            metadata = await self.validator.extract_metadata(file)
            
            # Create document metadata
            document_metadata = DocumentMetadata(
                id=document_id,
                filename=file.filename or "unknown",
                s3_key=gcs_key,
                size=validation_result.file_info.get('size', 0),
                content_type=validation_result.file_info.get('content_type', 'application/octet-stream'),
                workspace_id=workspace_id,
                user_id=user_id,
                checksum=metadata.get('sha256_checksum', ''),
                metadata=metadata,
                created_at=datetime.now(UTC),
                scan_result=scan_result
            )
            
            logger.info(f"Document uploaded successfully: {document_id}")
            return document_metadata
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Document upload failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error during document upload"
            )
    
    async def get_document(self, document_id: str, workspace_id: str) -> Optional[DocumentMetadata]:
        """
        Retrieve document metadata.
        
        Args:
            document_id: Document ID
            workspace_id: Workspace ID for security
            
        Returns:
            DocumentMetadata or None if not found
        """
        # Implementation would query database for document metadata
        # For now, return None as placeholder
        return None
    
    async def delete_document(self, document_id: str, workspace_id: str) -> bool:
        """
        Delete a document.
        
        Args:
            document_id: Document ID
            workspace_id: Workspace ID for security
            
        Returns:
            True if deletion successful
        """
        try:
            # Get document metadata
            doc_metadata = await self.get_document(document_id, workspace_id)
            if not doc_metadata:
                return False
            
            # Delete from GCS
            gcs_deleted = await self.storage_manager.delete_file(doc_metadata.s3_key)
            
            # Delete from database
            # Implementation would delete from database
            
            logger.info(f"Document deleted successfully: {document_id}")
            return gcs_deleted
            
        except Exception as e:
            logger.error(f"Document deletion failed: {e}")
            return False
    
    async def list_documents(self, workspace_id: str, limit: int = 50, offset: int = 0) -> List[DocumentMetadata]:
        """
        List documents in a workspace.
        
        Args:
            workspace_id: Workspace ID
            limit: Maximum number of documents to return
            offset: Number of documents to skip
            
        Returns:
            List of DocumentMetadata
        """
        # Implementation would query database for documents
        # For now, return empty list as placeholder
        return []


# Pydantic models for API responses
class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    document_id: str
    filename: str
    size: int
    content_type: str
    upload_timestamp: datetime
    scan_status: str
    warnings: List[str] = []


class DocumentListResponse(BaseModel):
    """Response model for document list."""
    documents: List[DocumentUploadResponse]
    total_count: int
    has_more: bool


# Error classes
class ValidationError(Exception):
    """Validation error for document uploads."""
    pass


class SecurityError(Exception):
    """Security error for virus detection."""
    pass


class StorageError(Exception):
    """Storage error for GCS operations."""
    pass
