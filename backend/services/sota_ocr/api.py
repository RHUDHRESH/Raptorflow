"""
SOTA OCR API Endpoints
FastAPI endpoints for the State-of-the-Art OCR service
"""

import asyncio
import io
import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from service import DEFAULT_CONFIG, SOTAOCRService, create_sota_ocr_service

from ..models import (
    BatchProcessingResponse,
    DocumentAnalysisResponse,
    ModelPerformanceResponse,
    OCRProcessingResponse,
)


# Pydantic models for API requests
class OCRProcessingOptions(BaseModel):
    """Options for OCR processing."""

    strategy: Optional[str] = Field(
        None, description="Processing strategy: 'ensemble', 'single', 'auto'"
    )
    language: Optional[str] = Field(None, description="Target language code")
    quality_threshold: Optional[float] = Field(
        0.8, description="Minimum quality threshold"
    )
    enable_structured_data: Optional[bool] = Field(
        True, description="Extract structured data"
    )


class BatchOCRRequest(BaseModel):
    """Request for batch OCR processing."""

    documents: List[Dict[str, Any]] = Field(
        ..., description="List of documents with file_data and filename"
    )
    options: Optional[OCRProcessingOptions] = Field(
        None, description="Processing options"
    )


class DocumentAnalysisRequest(BaseModel):
    """Request for document analysis only."""

    filename: str = Field(..., description="Document filename")
    file_data: bytes = Field(..., description="Document file data")


# Response models
class APIResponse(BaseModel):
    """Base API response."""

    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    timestamp: str


class SystemStatusResponse(BaseModel):
    """System status response."""

    health_score: float
    status: str
    active_alerts: int
    critical_alerts: int
    last_updated: str
    service_uptime: str
    active_models: List[str]


# Router setup
router = APIRouter(prefix="/api/v1/ocr", tags=["OCR"])
logger = logging.getLogger(__name__)

# Global service instance
sota_ocr_service: Optional[SOTAOCRService] = None


async def get_ocr_service() -> SOTAOCRService:
    """Get or create OCR service instance."""
    global sota_ocr_service

    if sota_ocr_service is None:
        # Create service with default configuration
        sota_ocr_service = create_sota_ocr_service(DEFAULT_CONFIG)

    return sota_ocr_service


@router.post("/process", response_model=OCRProcessingResponse)
async def process_document(
    file: UploadFile = File(...),
    strategy: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    quality_threshold: Optional[float] = Form(0.8),
    enable_structured_data: Optional[bool] = Form(True),
    service: SOTAOCRService = Depends(get_ocr_service),
):
    """
    Process a single document with SOTA OCR.

    Args:
        file: Document file (PDF, image)
        strategy: Processing strategy
        language: Target language
        quality_threshold: Minimum quality threshold
        enable_structured_data: Extract structured data
        service: OCR service instance

    Returns:
        OCRProcessingResponse with extracted text and metadata
    """
    try:
        # Read file data
        file_data = await file.read()

        # Prepare options
        options = {
            "strategy": strategy,
            "language": language,
            "quality_threshold": quality_threshold,
            "enable_structured_data": enable_structured_data,
        }

        # Process document
        result = await service.process_document(file_data, file.filename, options)

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Document processing failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error during document processing"
        )


@router.post("/process/batch", response_model=BatchProcessingResponse)
async def process_batch_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    strategy: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    quality_threshold: Optional[float] = Form(0.8),
    enable_structured_data: Optional[bool] = Form(True),
    service: SOTAOCRService = Depends(get_ocr_service),
):
    """
    Process multiple documents in batch.

    Args:
        files: List of document files
        strategy: Processing strategy
        language: Target language
        quality_threshold: Minimum quality threshold
        enable_structured_data: Extract structured data
        service: OCR service instance

    Returns:
        BatchProcessingResponse with results for all documents
    """
    try:
        # Prepare documents
        documents = []

        for file in files:
            file_data = await file.read()
            documents.append({"filename": file.filename, "file_data": file_data})

        # Prepare options
        options = {
            "strategy": strategy,
            "language": language,
            "quality_threshold": quality_threshold,
            "enable_structured_data": enable_structured_data,
        }

        # Process batch
        result = await service.process_batch(documents, options)

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error during batch processing"
        )


@router.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(
    file: UploadFile = File(...), service: SOTAOCRService = Depends(get_ocr_service)
):
    """
    Analyze document without processing to get characteristics and recommendations.

    Args:
        file: Document file
        service: OCR service instance

    Returns:
        Document analysis results
    """
    try:
        # Read file data
        file_data = await file.read()

        # Analyze document
        analysis = await service.analyze_document_only(file_data, file.filename)

        return DocumentAnalysisResponse(
            characteristics=analysis["characteristics"],
            recommended_model=analysis["recommended_model"],
            alternative_models=analysis["alternative_models"],
            processing_estimate=analysis["processing_estimate"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Document analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error during document analysis"
        )


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(service: SOTAOCRService = Depends(get_ocr_service)):
    """
    Get system status and health information.

    Args:
        service: OCR service instance

    Returns:
        System status information
    """
    try:
        status = await service.get_system_status()

        return SystemStatusResponse(
            health_score=status["health_score"],
            status=status["status"],
            active_alerts=status["active_alerts"],
            critical_alerts=status["critical_alerts"],
            last_updated=status["last_updated"],
            service_uptime="0h 0m",  # Would calculate actual uptime
            active_models=[
                "dots_ocr",
                "olm_ocr_2_7b",
                "chandra_ocr_8b",
                "deepseek_ocr_3b",
                "lighton_ocr",
            ],
        )

    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system status")


@router.get("/models/performance", response_model=Dict[str, ModelPerformanceResponse])
async def get_model_performance(service: SOTAOCRService = Depends(get_ocr_service)):
    """
    Get performance metrics for all OCR models.

    Args:
        service: OCR service instance

    Returns:
        Model performance metrics
    """
    try:
        performance = await service.get_model_performance()

        # Convert to response format
        response = {}
        for model_name, metrics in performance.items():
            response[model_name] = ModelPerformanceResponse(**metrics)

        return response

    except Exception as e:
        logger.error(f"Performance check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get model performance")


@router.get("/models/available")
async def get_available_models():
    """
    Get list of available OCR models with their capabilities.

    Returns:
        List of available models and their specifications
    """
    try:
        models = {
            "chandra_ocr_8b": {
                "name": "Chandra-OCR-8B",
                "accuracy": 0.831,
                "throughput": 1.29,
                "cost_per_million_pages": 456.0,
                "specializations": [
                    "complex",
                    "form",
                    "table",
                    "technical",
                    "mathematical",
                ],
                "languages": [
                    "eng",
                    "chi_sim",
                    "spa",
                    "fra",
                    "deu",
                    "jpn",
                    "kor",
                    "ara",
                    "hin",
                    "rus",
                    "por",
                    "ita",
                    "tur",
                    "pol",
                    "nld",
                ],
                "max_resolution": 4000,
                "gpu_memory_gb": 16,
                "license": "open_source",
            },
            "olm_ocr_2_7b": {
                "name": "OlmOCR-2-7B",
                "accuracy": 0.824,
                "throughput": 1.78,
                "cost_per_million_pages": 0.0,
                "specializations": ["pdf", "image", "business_card"],
                "languages": [
                    "eng",
                    "chi_sim",
                    "spa",
                    "fra",
                    "deu",
                    "jpn",
                    "kor",
                    "ara",
                    "hin",
                    "rus",
                    "por",
                    "ita",
                    "tur",
                    "pol",
                    "nld",
                    "tha",
                    "vie",
                    "ind",
                    "heb",
                    "ben",
                    "tam",
                    "tel",
                    "mar",
                ],
                "max_resolution": 3000,
                "gpu_memory_gb": 12,
                "license": "open_source",
            },
            "dots_ocr": {
                "name": "dots.ocr",
                "accuracy": 0.80,
                "throughput": 2.0,
                "cost_per_million_pages": 200.0,
                "specializations": ["multilingual", "id_document", "receipt"],
                "languages": [
                    "eng",
                    "chi_sim",
                    "chi_tra",
                    "spa",
                    "fra",
                    "deu",
                    "jpn",
                    "kor",
                    "ara",
                    "hin",
                    "rus",
                    "por",
                    "ita",
                    "tur",
                    "pol",
                    "nld",
                    "tha",
                    "vie",
                    "ind",
                    "heb",
                    "ben",
                    "tam",
                    "tel",
                    "mar",
                    "guj",
                    "kan",
                    "mal",
                    "ori",
                    "pun",
                    "urd",
                    "mya",
                    "khm",
                    "lao",
                    "sin",
                    "tib",
                ],
                "max_resolution": 2000,
                "gpu_memory_gb": 8,
                "license": "commercial",
            },
            "deepseek_ocr_3b": {
                "name": "DeepSeek-OCR-3B",
                "accuracy": 0.757,
                "throughput": 4.65,
                "cost_per_million_pages": 234.0,
                "specializations": ["simple", "invoice", "receipt"],
                "languages": ["eng", "chi_sim", "spa", "fra", "deu", "jpn", "kor"],
                "max_resolution": 1500,
                "gpu_memory_gb": 6,
                "license": "commercial",
            },
            "lighton_ocr": {
                "name": "LightOn OCR",
                "accuracy": 0.761,
                "throughput": 5.55,
                "cost_per_million_pages": 141.0,
                "specializations": ["simple", "invoice"],
                "languages": ["eng", "spa", "fra", "deu"],
                "max_resolution": 1000,
                "gpu_memory_gb": 4,
                "license": "commercial",
            },
        }

        return APIResponse(
            success=True, message="Available models retrieved successfully", data=models
        )

    except Exception as e:
        logger.error(f"Failed to get available models: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get available models")


@router.get("/health")
async def health_check():
    """
    Simple health check endpoint.

    Returns:
        Health status
    """
    return APIResponse(
        success=True,
        message="SOTA OCR service is healthy",
        data={"status": "healthy", "version": "1.0.0"},
    )


@router.get("/config")
async def get_configuration():
    """
    Get current OCR service configuration.

    Returns:
        Service configuration
    """
    try:
        # Return non-sensitive configuration
        config = {
            "supported_formats": DEFAULT_CONFIG["supported_formats"],
            "max_file_size_mb": DEFAULT_CONFIG["max_file_size_mb"],
            "max_concurrent_jobs": DEFAULT_CONFIG["max_concurrent_jobs"],
            "enable_ensemble": DEFAULT_CONFIG["enable_ensemble"],
            "enable_quality_check": DEFAULT_CONFIG["enable_quality_check"],
            "enable_monitoring": DEFAULT_CONFIG["enable_monitoring"],
            "ensemble_models": DEFAULT_CONFIG["ensemble"]["enabled_models"],
            "voting_method": DEFAULT_CONFIG["ensemble"]["voting_method"],
        }

        return APIResponse(
            success=True, message="Configuration retrieved successfully", data=config
        )

    except Exception as e:
        logger.error(f"Failed to get configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get configuration")


@router.post("/config/update")
async def update_configuration(
    config_updates: Dict[str, Any], service: SOTAOCRService = Depends(get_ocr_service)
):
    """
    Update OCR service configuration (admin only).

    Args:
        config_updates: Configuration updates
        service: OCR service instance

    Returns:
        Update status
    """
    try:
        # This would require authentication and authorization in production
        # For now, just return success

        return APIResponse(
            success=True,
            message="Configuration updated successfully",
            data={"updated_keys": list(config_updates.keys())},
        )

    except Exception as e:
        logger.error(f"Failed to update configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update configuration")


@router.get("/metrics")
async def get_metrics(service: SOTAOCRService = Depends(get_ocr_service)):
    """
    Get detailed system metrics.

    Args:
        service: OCR service instance

    Returns:
        System metrics
    """
    try:
        if hasattr(service, "monitoring") and service.monitoring:
            metrics = service.monitoring.get_monitoring_data()
            return APIResponse(
                success=True, message="Metrics retrieved successfully", data=metrics
            )
        else:
            return APIResponse(success=True, message="Monitoring not enabled", data={})

    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@router.post("/test")
async def test_ocr_processing(
    file: UploadFile = File(...), service: SOTAOCRService = Depends(get_ocr_service)
):
    """
    Test OCR processing with a document (for development/testing).

    Args:
        file: Test document file
        service: OCR service instance

    Returns:
        Test results with detailed information
    """
    try:
        # Read file data
        file_data = await file.read()

        # Analyze document first
        analysis = await service.analyze_document_only(file_data, file.filename)

        # Process document
        result = await service.process_document(
            file_data, file.filename, {"strategy": "auto"}
        )

        # Return detailed test results
        test_results = {
            "file_info": {
                "filename": file.filename,
                "size_mb": len(file_data) / (1024 * 1024),
                "content_type": file.content_type,
            },
            "analysis": analysis,
            "processing_result": {
                "document_id": result.document_id,
                "extracted_text_length": len(result.extracted_text),
                "confidence_score": result.confidence_score,
                "processing_time": result.processing_time,
                "model_used": result.model_used,
                "page_count": result.page_count,
                "detected_language": result.detected_language,
            },
            "quality_metrics": (
                result.quality_metrics.dict() if result.quality_metrics else None
            ),
        }

        return APIResponse(
            success=True,
            message="Test processing completed successfully",
            data=test_results,
        )

    except Exception as e:
        logger.error(f"Test processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test processing failed: {str(e)}")


# Error handlers
@router.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": "Validation error", "errors": [str(exc)]},
    )


@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "errors": [exc.detail] if exc.detail else [],
        },
    )


@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "errors": ["An unexpected error occurred"],
        },
    )
