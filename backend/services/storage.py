"""
Enhanced Supabase Storage Service
Handles file uploads, validation, CDN, security scanning, and image processing
"""

import hashlib
import io
import logging
import mimetypes
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union

import magic

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - image processing disabled")

from ..infrastructure.supabase_storage import FileCategory, get_supabase_storage

# No longer importing from .storage to avoid circular dependency
# basic_storage_service will be initialized using get_supabase_storage()

logger = logging.getLogger(__name__)


@dataclass
class FileMetadata:
    """Enhanced metadata for uploaded files"""

    original_name: str
    storage_path: str
    public_url: str
    size_bytes: int
    content_type: str
    mime_type: str
    hash_md5: str
    workspace_id: str
    uploaded_at: datetime
    is_scanned: bool = False
    scan_result: Optional[str] = None
    is_processed: bool = False
    processing_info: Optional[Dict[str, Any]] = None
    cdn_url: Optional[str] = None
    file_category: str = "general"
    validation_status: str = "pending"
    security_flags: List[str] = None

    def __post_init__(self):
        if self.security_flags is None:
            self.security_flags = []


class EnhancedStorageService:
    """Enhanced Supabase storage with validation, security scanning, and image processing"""

    def __init__(self):
        # Use existing storage service as base
        self.basic_storage = get_supabase_storage()
        self.supabase_storage = get_supabase_storage()

        # CDN configuration (Supabase doesn't have CDN by default, but we can use public URLs)
        self.cdn_base_url = os.getenv("SUPABASE_CDN_URL")

        # File limits and validation
        self.max_file_size = (
            int(os.getenv("MAX_FILE_SIZE_MB", "100")) * 1024 * 1024
        )  # Convert to bytes
        self.enable_security_scanning = (
            os.getenv("ENABLE_FILE_SCANNING", "true").lower() == "true"
        )
        self.enable_image_processing = (
            os.getenv("ENABLE_IMAGE_PROCESSING", "true").lower() == "true"
        )

        # Allowed file types
        self.allowed_extensions = {
            "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"],
            "document": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
            "spreadsheet": [".xls", ".xlsx", ".csv"],
            "presentation": [".ppt", ".pptx"],
            "archive": [".zip", ".rar", ".7z"],
            "media": [".mp4", ".avi", ".mov", ".mp3", ".wav"],
        }

        # Suspicious content signatures
        self.suspicious_signatures = [
            b"eval(",
            b"exec(",
            b"system(",
            b"shell_exec",
            b"powershell",
            b"cmd.exe",
            b"/bin/sh",
            b"bash -c",
            b"subprocess",
            b"os.system",
            b"__import__",
            b"compile",
        ]

        logger.info(
            f"Enhanced storage service initialized - CDN: {self.cdn_base_url}, Security scanning: {self.enable_security_scanning}, Image processing: {self.enable_image_processing}"
        )

    def _validate_file(
        self, file_content: bytes, filename: str
    ) -> Tuple[bool, str, List[str]]:
        """Enhanced file validation for security and size"""
        errors = []
        warnings = []

        # Check file size
        if len(file_content) > self.max_file_size:
            errors.append(
                f"File size exceeds limit of {self.max_file_size // (1024 * 1024)}MB"
            )

        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        allowed_exts = []
        for ext_list in self.allowed_extensions.values():
            allowed_exts.extend(ext_list)

        if file_ext not in allowed_exts:
            errors.append(f"File type {file_ext} not allowed")

        # Check MIME type with python-magic
        try:
            mime_type = magic.from_buffer(file_content, mime=True)

            # Block executables and scripts
            if mime_type.startswith("application/x-executable") or mime_type.startswith(
                "application/x-msdownload"
            ):
                errors.append(f"Executable files not allowed: {mime_type}")

            # Block script files
            if mime_type in [
                "application/x-sh",
                "application/x-bat",
                "application/x-python",
            ]:
                errors.append(f"Script files not allowed: {mime_type}")

        except Exception as e:
            logger.warning(f"MIME type detection failed: {e}")
            warnings.append("Could not verify file type")

        # Security scanning
        if self.enable_security_scanning:
            security_result = self._security_scan(file_content)
            if security_result["suspicious"]:
                errors.append(
                    f"File contains suspicious content: {', '.join(security_result['flags'])}"
                )
            warnings.extend(security_result["warnings"])

        is_valid = len(errors) == 0
        status = "passed" if is_valid else "failed"
        message = "Validation passed" if is_valid else "; ".join(errors)

        return is_valid, message, warnings

    def _security_scan(self, content: bytes) -> Dict[str, Any]:
        """Enhanced security scanning for malicious content"""
        result = {"suspicious": False, "flags": [], "warnings": []}

        try:
            content_lower = content.lower()

            # Check for suspicious signatures
            for sig in self.suspicious_signatures:
                if sig in content_lower:
                    result["suspicious"] = True
                    result["flags"].append(
                        f"Suspicious pattern: {sig.decode('utf-8', errors='ignore')}"
                    )

            # Check for embedded scripts
            if b"<script" in content_lower and b"javascript:" in content_lower:
                result["suspicious"] = True
                result["flags"].append("Embedded JavaScript detected")

            # Check for suspicious file headers
            if content.startswith(b"MZ"):  # PE executable
                result["suspicious"] = True
                result["flags"].append("Windows executable detected")

            # Check for common malware patterns
            malware_patterns = [
                b"CreateProcess",
                b"VirtualAlloc",
                b"WriteProcessMemory",
                b"SetWindowsHookEx",
                b"keylogger",
                b"backdoor",
            ]

            for pattern in malware_patterns:
                if pattern in content_lower:
                    result["warnings"].append(
                        f"Potentially suspicious pattern: {pattern.decode('utf-8', errors='ignore')}"
                    )

        except Exception as e:
            logger.error(f"Security scan error: {e}")
            result["warnings"].append("Security scan incomplete")

        return result

    def _process_image_if_needed(
        self, content: bytes, filename: str
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Enhanced image processing with optimization and metadata"""
        processing_info = {
            "processed": False,
            "original_size": len(content),
            "final_size": len(content),
            "compression_ratio": 0.0,
            "format": "unknown",
            "dimensions": None,
        }

        if not self.enable_image_processing or not PIL_AVAILABLE:
            return content, processing_info

        try:
            # Check if it's an image
            mime_type = magic.from_buffer(content, mime=True)
            if not mime_type.startswith("image/"):
                return content, processing_info

            # Open image
            img = Image.open(io.BytesIO(content))
            processing_info["format"] = img.format
            processing_info["dimensions"] = f"{img.width}x{img.height}"

            # Convert to RGB if necessary (removes alpha channel)
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
                processing_info["format_conversion"] = f"{img.mode} -> RGB"

            # Resize if too large (max 2048x2048)
            max_size = 2048
            if img.width > max_size or img.height > max_size:
                original_size = (img.width, img.height)
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                processing_info["resize"] = (
                    f"{original_size} -> {img.width}x{img.height}"
                )

            # Optimize and save
            output = io.BytesIO()

            # Determine best format and quality
            if img.format in ["JPEG", "JPG"]:
                img.save(output, format="JPEG", quality=85, optimize=True)
            elif img.format == "PNG":
                img.save(
                    output, format="JPEG", quality=85, optimize=True
                )  # Convert to JPEG for better compression
                processing_info["format_conversion"] = "PNG -> JPEG"
            else:
                img.save(output, format="JPEG", quality=85, optimize=True)

            processed_content = output.getvalue()

            # Calculate compression
            processing_info["processed"] = True
            processing_info["final_size"] = len(processed_content)
            processing_info["compression_ratio"] = round(
                (1 - len(processed_content) / len(content)) * 100, 2
            )

            logger.info(
                f"Image processed: {filename}, compression: {processing_info['compression_ratio']}%"
            )
            return processed_content, processing_info

        except Exception as e:
            logger.warning(f"Image processing failed for {filename}: {e}")
            processing_info["error"] = str(e)
            return content, processing_info

    def _get_file_category(self, filename: str) -> str:
        """Categorize file by extension"""
        file_ext = os.path.splitext(filename)[1].lower()

        for category, extensions in self.allowed_extensions.items():
            if file_ext in extensions:
                return category
        return "other"

    def _calculate_file_hash(self, content: bytes) -> str:
        """Calculate SHA256 hash for deduplication"""
        return hashlib.sha256(content).hexdigest()

    def _generate_storage_path(self, workspace_id: str, filename: str) -> str:
        """Generate unique storage path for file"""
        file_ext = os.path.splitext(filename)[1]
        unique_id = str(uuid.uuid4())
        date_path = datetime.now().strftime("%Y/%m/%d")
        category = self._get_file_category(filename)

        return f"{workspace_id}/{category}/{date_path}/{unique_id}{file_ext}"

    def _generate_cdn_url(self, storage_path: str) -> Optional[str]:
        """Generate CDN URL if configured"""
        if self.cdn_base_url:
            return f"{self.cdn_base_url}/{storage_path}"
        return None

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        workspace_id: str,
        content_type: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enhanced file upload with validation, processing, and security scanning"""

        try:
            # Enhanced validation
            is_valid, validation_message, warnings = self._validate_file(
                file_content, filename
            )

            if not is_valid:
                return {
                    "status": "error",
                    "error": validation_message,
                    "error_type": "validation_error",
                    "validation_status": "failed",
                }

            # Process content (image optimization, etc.)
            processed_content, processing_info = self._process_image_if_needed(
                file_content, filename
            )

            # Generate metadata
            storage_path = self._generate_storage_path(workspace_id, filename)
            file_hash = self._calculate_file_hash(processed_content)
            mime_type = content_type or magic.from_buffer(processed_content, mime=True)
            file_category = self._get_file_category(filename)

            # Security scan results
            security_result = {"suspicious": False, "flags": [], "warnings": []}
            if self.enable_security_scanning:
                security_result = self._security_scan(processed_content)

            # Use enhanced Supabase storage service
            upload_result = await self.supabase_storage.upload_file(
                content=processed_content,
                filename=filename,
                workspace_id=workspace_id,
                user_id=user_id or "system",
                category=(
                    FileCategory(file_category)
                    if file_category in [c.value for c in FileCategory]
                    else FileCategory.UPLOADS
                ),
                content_type=mime_type,
                is_public=True,  # Make publicly accessible for CDN
                custom_metadata={
                    "original_hash": hashlib.sha256(file_content).hexdigest(),
                    "processing_info": str(processing_info),
                    "security_flags": (
                        ",".join(security_result["flags"])
                        if security_result["flags"]
                        else ""
                    ),
                    "validation_warnings": ",".join(warnings) if warnings else "",
                },
            )

            if not upload_result.success:
                return {
                    "status": "error",
                    "error": upload_result.error_message,
                    "error_type": "upload_error",
                }

            # Generate URLs
            public_url = upload_result.download_url
            cdn_url = self._generate_cdn_url(storage_path)

            # Create enhanced metadata
            metadata = FileMetadata(
                original_name=filename,
                storage_path=storage_path,
                public_url=public_url,
                size_bytes=len(processed_content),
                content_type=mime_type,
                mime_type=mime_type,
                hash_md5=file_hash,
                workspace_id=workspace_id,
                uploaded_at=datetime.now(),
                is_scanned=True,
                scan_result=(
                    "clean" if not security_result["suspicious"] else "suspicious"
                ),
                is_processed=processing_info["processed"],
                processing_info=processing_info,
                cdn_url=cdn_url,
                file_category=file_category,
                validation_status="passed",
                security_flags=security_result["flags"],
            )

            # Log successful upload
            logger.info(
                f"Enhanced file upload: {filename} -> {storage_path} ({len(processed_content)} bytes)"
            )

            return {
                "status": "success",
                "file_id": upload_result.file_id,
                "storage_path": storage_path,
                "public_url": public_url,
                "cdn_url": cdn_url,
                "size_bytes": len(processed_content),
                "content_type": mime_type,
                "hash_md5": file_hash,
                "workspace_id": workspace_id,
                "uploaded_at": metadata.uploaded_at.isoformat(),
                "validation": {
                    "status": "passed",
                    "warnings": warnings,
                    "scanned": True,
                    "scan_result": metadata.scan_result,
                    "security_flags": security_result["flags"],
                },
                "processing": processing_info,
                "category": file_category,
                "metadata": metadata.to_dict() if hasattr(metadata, "to_dict") else {},
            }

        except Exception as e:
            logger.error(f"Enhanced file upload failed: {e}")
            return {
                "status": "error",
                "error": f"Upload failed: {str(e)}",
                "error_type": "upload_error",
            }

    def delete_file(self, storage_path: str) -> Dict[str, Any]:
        """Delete file from storage"""
        try:
            # Extract file_id from storage path
            file_id = storage_path.split("/")[-1].split(".")[0]

            # Use Supabase storage to delete
            import asyncio

            success = asyncio.run(self.supabase_storage.delete_file(file_id))

            if success:
                logger.info(f"File deleted: {storage_path}")
                return {
                    "status": "success",
                    "message": f"File {storage_path} deleted successfully",
                }
            else:
                return {"status": "error", "error": "File not found or deletion failed"}

        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return {"status": "error", "error": f"Deletion failed: {str(e)}"}

    async def cleanup_old_files(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up files older than specified days"""
        try:
            # Use Supabase storage cleanup
            cleaned_count = await self.supabase_storage.cleanup_expired_files()

            logger.info(f"Cleanup completed: {cleaned_count} files")

            return {
                "status": "success",
                "files_deleted": cleaned_count,
                "cleanup_date": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {"status": "error", "error": f"Cleanup failed: {str(e)}"}

    def get_workspace_usage(self, workspace_id: str) -> Dict[str, Any]:
        """Get storage usage for workspace"""
        try:
            import asyncio

            usage = asyncio.run(self.supabase_storage.get_workspace_usage(workspace_id))

            return usage

        except Exception as e:
            logger.error(f"Usage calculation failed: {e}")
            return {"status": "error", "error": str(e)}


# Enhanced service instance - lazy initialization
enhanced_storage_service = None


def get_enhanced_storage_service():
    """Get enhanced storage service instance with lazy initialization."""
    global enhanced_storage_service
    if enhanced_storage_service is None:
        enhanced_storage_service = EnhancedStorageService()
    return enhanced_storage_service


# Keep backward compatibility
storage_service = None


def get_storage_service():
    """Get storage service instance with lazy initialization."""
    global storage_service
    if storage_service is None:
        storage_service = get_supabase_storage()
    return storage_service
