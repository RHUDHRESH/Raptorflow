"""
RaptorFlow OCR Service (Modernized)
Handles text extraction using the Hybrid Cognitive OCR Machine.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import HTTPException
from pydantic import BaseModel

from backend.services.document_service import DocumentMetadata
from backend.services.ocr.universal_extractor import UniversalExtractor as HybridOCRExtractor

logger = logging.getLogger(__name__)


class OCRResult(BaseModel):
    """Complete OCR result for a document."""
    document_id: str
    extracted_text: str
    confidence_score: float
    structured_data: Optional[Dict]
    processing_time: float
    provider_used: str
    page_count: int
    language: str
    created_at: datetime


class OCRService:
    """Main OCR service for document processing using Hybrid OCR Machine."""
    
    def __init__(self):
        self.hybrid_extractor = HybridOCRExtractor()
        
        async def extract_text(self, document: DocumentMetadata) -> OCRResult:
        
            """
        
            Extract text from a document using the Hybrid OCR Machine.
        
            """
        
            try:
        
                # Download document from GCS
        
                from backend.services.document_service import GCPStorageManager
        
                storage_manager = GCPStorageManager()
        
                document_data = await storage_manager.download_file(document.s3_key)
        
                
        
                return await self.extract_text_from_bytes(
        
                    file_content=document_data,
        
                    file_type=document.content_type,
        
                    document_id=document.id
        
                )
        
                
        
            except Exception as e:
        
                logger.error(f"OCR extraction failed for document {document.id}: {e}")
        
                raise HTTPException(
        
                    status_code=500,
        
                    detail=f"Failed to extract text: {str(e)}"
        
                )
        
    
        
        async def extract_text_from_bytes(self, file_content: bytes, file_type: str, document_id: str = "temp") -> OCRResult:
        
            """
        
            Extract text from raw bytes using the Hybrid OCR Machine.
        
            """
        
            try:
        
                start_time = datetime.utcnow()
        
                
        
                # Use Hybrid Machine
        
                result = await self.hybrid_extractor.extract(
        
                    file_content=file_content,
        
                    file_type=file_type,
        
                    context={"document_id": document_id}
        
                )
        
                
        
                processing_time = (datetime.utcnow() - start_time).total_seconds()
        
                
        
                # Create OCR result
        
                return OCRResult(
        
                    document_id=document_id,
        
                    extracted_text=result.text,
        
                    confidence_score=result.confidence,
        
                    structured_data=result.raw_data,
        
                    processing_time=processing_time,
        
                    provider_used="hybrid_ocr_machine",
        
                    page_count=result.pages,
        
                    language=result.metadata.get("detected_languages", ["unknown"])[0],
        
                    created_at=datetime.utcnow()
        
                )
        
                
        
            except Exception as e:
        
                logger.error(f"OCR extraction from bytes failed: {e}")
        
                raise HTTPException(
        
                    status_code=500,
        
                    detail=f"Failed to extract text from bytes: {str(e)}"
        
                )
        
    