"""
Enhanced Onboarding API Routes for RaptorFlow
Handles 23-step onboarding process with Redis session management,
AI agent timeout handling, field validation, and retry logic.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from pydantic import BaseModel, Field, validator
from pydantic.json import pydantic_encoder
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# AI Agent imports with timeout handling
from ..agents.specialists.category_advisor import CategoryAdvisor
from ..agents.specialists.channel_recommender import ChannelRecommender
from ..agents.specialists.competitor_analyzer import CompetitorAnalyzer
from ..agents.specialists.contradiction_detector import ContradictionDetector
from ..agents.specialists.evidence_classifier import EvidenceClassifier
from ..agents.specialists.extraction_orchestrator import ExtractionOrchestrator
from ..agents.specialists.focus_sacrifice_engine import FocusSacrificeEngine
from ..agents.specialists.icp_deep_generator import ICPDeepGenerator
from ..agents.specialists.market_size_calculator import MarketSizeCalculator
from ..agents.specialists.messaging_rules_engine import MessagingRulesEngine
from ..agents.specialists.neuroscience_copywriter import NeuroscienceCopywriter
from ..agents.specialists.perceptual_map_generator import PerceptualMapGenerator
from ..agents.specialists.positioning_statement_generator import (
    PositioningStatementGenerator,
)
from ..agents.specialists.proof_point_validator import ProofPointValidator
from ..agents.specialists.reddit_researcher import RedditResearcher
from ..agents.specialists.soundbites_generator import SoundbitesGenerator
from ..agents.specialists.truth_sheet_generator import TruthSheetGenerator

# Redis session management
from ..redis.session_manager import get_onboarding_session_manager

# Core system imports
from ..services.ocr_service import OCRService
from ..services.search.orchestrator import SOTASearchOrchestrator as NativeSearch
from ..services.storage import get_enhanced_storage_service
from ..services.vertex_ai_service import vertex_ai_service
from fastapi import Query
from ..services.profile_service import ProfileService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/onboarding", tags=["onboarding-enhanced"])

# Initialize services
ocr_service = OCRService()
search_service = NativeSearch()
session_manager = get_onboarding_session_manager()
profile_service = ProfileService()


def _ensure_active_subscription(profile: Dict[str, Any]) -> None:
    subscription_status = profile.get("subscription_status")
    if subscription_status != "active":
        raise HTTPException(
            status_code=402,
            detail={
                "error": "SUBSCRIPTION_REQUIRED",
                "message": "An active subscription is required to start onboarding.",
                "subscription_status": subscription_status,
            },
        )

# Initialize AI agents with timeout configuration
AI_AGENT_TIMEOUT = 30  # 30 seconds max per agent
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1

# AI Agents with error handling
ai_agents = {
    "evidence_classifier": EvidenceClassifier(),
    "extraction_orchestrator": ExtractionOrchestrator(),
    "contradiction_detector": ContradictionDetector(),
    "reddit_researcher": RedditResearcher(),
    "perceptual_map_generator": PerceptualMapGenerator(),
    "neuroscience_copywriter": NeuroscienceCopywriter(),
    "channel_recommender": ChannelRecommender(),
    "category_advisor": CategoryAdvisor(),
    "market_size_calculator": MarketSizeCalculator(),
    "competitor_analyzer": CompetitorAnalyzer(),
    "focus_sacrifice_engine": FocusSacrificeEngine(),
    "proof_point_validator": ProofPointValidator(),
    "truth_sheet_generator": TruthSheetGenerator(),
    "messaging_rules_engine": MessagingRulesEngine(),
    "soundbites_generator": SoundbitesGenerator(),
    "icp_deep_generator": ICPDeepGenerator(),
    "positioning_generator": PositioningStatementGenerator(),
}


# Enhanced Pydantic models with validation
class StepUpdateRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Step data to save")
    version: int = Field(default=1, ge=1, le=10, description="Data version")
    workspace_id: Optional[str] = Field(None, description="Workspace ID for validation")

    @validator("data")
    def validate_data_not_empty(cls, v):
        if not v or not isinstance(v, dict):
            raise ValueError("Data must be a non-empty dictionary")
        return v


class URLProcessRequest(BaseModel):
    url: str = Field(..., description="URL to process")
    item_id: str = Field(
        ..., min_length=1, max_length=100, description="Item identifier"
    )
    workspace_id: str = Field(..., min_length=1, description="Workspace ID")

    @validator("url")
    def validate_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        if len(v) > 2048:
            raise ValueError("URL too long (max 2048 characters)")
        return v


class EvidenceClassificationRequest(BaseModel):
    evidence_data: Dict[str, Any] = Field(..., description="Evidence to classify")
    session_id: str = Field(..., min_length=1, description="Session ID")

    @validator("evidence_data")
    def validate_evidence_data(cls, v):
        required_fields = ["content", "type"]
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Evidence data must contain '{field}' field")
        return v


class FactExtractionRequest(BaseModel):
    evidence_list: List[Dict[str, Any]] = Field(
        ..., min_items=1, max_items=50, description="Evidence list"
    )
    session_id: str = Field(..., min_length=1, description="Session ID")

    @validator("evidence_list")
    def validate_evidence_list(cls, v):
        for i, evidence in enumerate(v):
            if "content" not in evidence:
                raise ValueError(f"Evidence item {i} must contain 'content' field")
        return v


# Helper functions with enhanced error handling
async def scrape_website_with_timeout(url: str, timeout: int = 30) -> Dict[str, Any]:
    """Scrape website content with timeout and retry logic."""
    try:
        # Validate URL
        if not url or not url.startswith(("http://", "https://")):
            return {"status": "error", "error": "Invalid URL format"}

        # Use SOTA search cluster with timeout
        result = await asyncio.wait_for(
            search_service.query(f"site:{url}", limit=1), timeout=timeout
        )

        if result:
            res = result[0]
            return {
                "status": "success",
                "title": res.get("title", ""),
                "content": res.get("snippet", ""),
                "url": url,
                "source": "sota_search_cluster",
                "search_confidence": res.get("confidence", 0.9),
                "domain": url.split("//")[-1].split("/")[0],
                "scraped_at": datetime.utcnow().isoformat(),
            }
        else:
            return {
                "status": "error",
                "error": f"No content found for URL: {url}",
                "url": url,
            }

    except asyncio.TimeoutError:
        logger.error(f"Scraping timeout for URL: {url}")
        return {
            "status": "error",
            "error": f"Scraping timeout after {timeout} seconds",
            "url": url,
        }
    except Exception as e:
        logger.error(f"Scraping failed for {url}: {e}")
        return {"status": "error", "error": f"Scraping error: {str(e)}", "url": url}


async def process_ocr_with_timeout(
    file_path: str, file_content: bytes, timeout: int = 45
) -> Dict[str, Any]:
    """Process file with OCR with timeout and enhanced error handling."""
    try:
        # Determine file type
        file_extension = os.path.splitext(file_path)[1].lower()
        allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".tiff"}

        if file_extension not in allowed_extensions:
            return {
                "status": "error",
                "error": f"Unsupported file type: {file_extension}",
                "supported_types": list(allowed_extensions),
            }

        content_type = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".tiff": "image/tiff",
        }.get(file_extension, "application/octet-stream")

        # Process with timeout
        result = await asyncio.wait_for(
            ocr_service.extract_text_from_bytes(
                file_content=file_content,
                file_type=content_type,
                document_id=os.path.basename(file_path),
            ),
            timeout=timeout,
        )

        return {
            "status": "success",
            "extracted_text": result.extracted_text,
            "page_count": result.page_count,
            "confidence": result.confidence_score,
            "processing_method": result.provider_used,
            "file_type": file_extension,
            "processing_time": result.processing_time,
            "language": result.language,
            "structured_data": result.structured_data,
            "processed_at": datetime.utcnow().isoformat(),
        }

    except asyncio.TimeoutError:
        logger.error(f"OCR processing timeout for file: {file_path}")
        return {
            "status": "error",
            "error": f"OCR processing timeout after {timeout} seconds",
            "file_path": file_path,
        }
    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        return {
            "status": "error",
            "error": f"OCR processing error: {str(e)}",
            "file_path": file_path,
        }


# AI Agent wrapper with timeout and retry logic
async def execute_ai_agent_with_timeout(
    agent_name: str, method_name: str, *args, **kwargs
):
    """Execute AI agent method with timeout and retry logic."""
    agent = ai_agents.get(agent_name)
    if not agent:
        raise HTTPException(
            status_code=503, detail=f"AI agent '{agent_name}' not available"
        )

    for attempt in range(MAX_RETRIES):
        try:
            method = getattr(agent, method_name)
            result = await asyncio.wait_for(
                method(*args, **kwargs), timeout=AI_AGENT_TIMEOUT
            )
            return result

        except asyncio.TimeoutError:
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_BASE_DELAY * (2**attempt)
                logger.warning(
                    f"AI agent {agent_name}.{method_name} timeout (attempt {attempt + 1}), retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    f"AI agent {agent_name}.{method_name} failed after {MAX_RETRIES} attempts"
                )
                raise HTTPException(
                    status_code=504,
                    detail=f"AI processing timeout after {MAX_RETRIES} attempts",
                )

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_BASE_DELAY * (2**attempt)
                logger.warning(
                    f"AI agent {agent_name}.{method_name} error (attempt {attempt + 1}): {e}, retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"AI agent {agent_name}.{method_name} failed: {e}")
                raise HTTPException(
                    status_code=500, detail=f"AI processing failed: {str(e)}"
                )


# Enhanced API Endpoints


@router.post("/session")
async def create_or_get_session_enhanced(
    workspace_id: str,
    user_id: Optional[str] = None,
    auth_user_id: str = Query(..., description="User ID"),
):
    """Create or retrieve onboarding session with enhanced validation"""
    try:
        # Validate inputs
        if not workspace_id or len(workspace_id) < 1:
            raise HTTPException(status_code=400, detail="Invalid workspace ID")

        profile = profile_service.verify_profile(current_user)
        _ensure_active_subscription(profile)

        profile_workspace_id = profile.get("workspace_id")
        if not profile_workspace_id:
            raise HTTPException(status_code=400, detail="Workspace not found for user")
        if workspace_id and workspace_id != profile_workspace_id:
            raise HTTPException(
                status_code=403, detail="Workspace does not match authenticated user"
            )

        workspace_id = profile_workspace_id
        user_id = current_user.id

        # Generate a unique session ID
        import uuid

        session_id = str(uuid.uuid4())

        # Set session metadata in Redis
        if user_id:
            await session_manager.set_metadata(session_id, user_id, workspace_id)
        else:
            await session_manager.set_metadata(session_id, "unknown", workspace_id)

        # Initialize progress
        await session_manager.update_progress(session_id, 0)

        # Return session info
        progress = await session_manager.get_progress(session_id)
        metadata = await session_manager.get_metadata(session_id)

        return {
            "success": True,
            "session_id": session_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "progress": progress,
            "metadata": metadata,
            "created_at": datetime.utcnow().isoformat(),
            "api_version": "enhanced_v2",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating enhanced session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/steps/{step_id}")
async def update_step_data_enhanced(
    session_id: str, step_id: int, request: StepUpdateRequest
):
    """Update step data with enhanced validation and progress tracking"""
    try:
        # Validate step ID
        if step_id < 1 or step_id > 23:
            raise HTTPException(
                status_code=400, detail="Invalid step ID. Must be between 1 and 23."
            )

        # Validate session exists
        metadata = await session_manager.get_metadata(session_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Session not found")

        # Validate workspace if provided
        if (
            request.workspace_id
            and metadata.get("workspace_id") != request.workspace_id
        ):
            raise HTTPException(status_code=403, detail="Workspace ID mismatch")

        # Save step data to Redis
        success = await session_manager.save_step(session_id, step_id, request.data)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to save step data")

        # Get updated progress
        progress = await session_manager.get_progress(session_id)

        logger.info(f"Enhanced step {step_id} saved for session {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "step_id": step_id,
            "version": request.version,
            "progress": progress,
            "updated_at": datetime.utcnow().isoformat(),
            "validation": {
                "data_size": len(str(request.data)),
                "fields_count": len(request.data),
                "workspace_validated": request.workspace_id is not None,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating enhanced step data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/process-url")
async def process_url_enhanced(session_id: str, request: URLProcessRequest):
    """Process URL with enhanced scraping and validation"""
    try:
        # Validate session exists
        metadata = await session_manager.get_metadata(session_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Session not found")

        # Validate workspace
        if metadata.get("workspace_id") != request.workspace_id:
            raise HTTPException(status_code=403, detail="Workspace ID mismatch")

        # Process URL with timeout
        result = await scrape_website_with_timeout(request.url)

        # Store result as step data if successful
        if result["status"] == "success":
            step_data = {
                "url": request.url,
                "item_id": request.item_id,
                "scraping_result": result,
                "processed_at": datetime.utcnow().isoformat(),
            }

            # Save as a temporary step (using step 0 for URL processing)
            await session_manager.save_step(session_id, 0, step_data)

        logger.info(f"URL processed for session {session_id}: {request.url}")

        return {
            "success": result["status"] == "success",
            "session_id": session_id,
            "item_id": request.item_id,
            "result": result,
            "processed_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/upload-file")
async def upload_file_enhanced(
    session_id: str,
    file: UploadFile = File(...),
    item_id: str = Form(...),
    workspace_id: str = Form(...),
):
    """Upload and process file with enhanced OCR and validation"""
    try:
        # Validate session exists
        metadata = await session_manager.get_metadata(session_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Session not found")

        # Validate workspace
        if metadata.get("workspace_id") != workspace_id:
            raise HTTPException(status_code=403, detail="Workspace ID mismatch")

        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Read file content
        file_content = await file.read()

        # Check file size (max 50MB)
        if len(file_content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")

        # Process with OCR
        result = await process_ocr_with_timeout(file.filename, file_content)

        # Store result if successful
        if result["status"] == "success":
            step_data = {
                "filename": file.filename,
                "item_id": item_id,
                "file_size": len(file_content),
                "ocr_result": result,
                "processed_at": datetime.utcnow().isoformat(),
            }

            # Save as a temporary step (using step 0 for file processing)
            await session_manager.save_step(session_id, 0, step_data)

        logger.info(f"File processed for session {session_id}: {file.filename}")

        return {
            "success": result["status"] == "success",
            "session_id": session_id,
            "item_id": item_id,
            "filename": file.filename,
            "file_size": len(file_content),
            "result": result,
            "processed_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Enhanced AI Agent Endpoints


@router.post("/{session_id}/classify-evidence")
async def classify_evidence_enhanced(
    session_id: str, request: EvidenceClassificationRequest
):
    """Classify evidence using AI with timeout and retry logic"""
    try:
        # Validate session exists
        metadata = await session_manager.get_metadata(session_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Session not found")

        # Execute AI agent with timeout
        result = await execute_ai_agent_with_timeout(
            "evidence_classifier", "classify_document", request.evidence_data
        )

        # Store classification in database
        step_data = {
            "classification": result,
            "evidence_data": request.evidence_data,
            "processed_at": datetime.utcnow().isoformat(),
        }
        await session_manager.save_step(session_id, 1, step_data)

        logger.info(f"Evidence classified for session {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "classification": result,
            "processed_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error classifying evidence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/extract-facts")
async def extract_facts_enhanced(session_id: str, request: FactExtractionRequest):
    """Extract facts from evidence using AI with timeout and retry logic"""
    try:
        # Validate session exists
        metadata = await session_manager.get_metadata(session_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Session not found")

        # Execute AI agent with timeout
        result = await execute_ai_agent_with_timeout(
            "extraction_orchestrator",
            "extract_facts_from_evidence",
            request.evidence_list,
        )

        # Store extraction results
        step_data = {
            "extraction_result": result,
            "evidence_count": len(request.evidence_list),
            "processed_at": datetime.utcnow().isoformat(),
        }
        await session_manager.save_step(session_id, 2, step_data)

        logger.info(f"Facts extracted for session {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "extraction_result": result,
            "processed_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting facts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/detect-contradictions")
async def detect_contradictions_enhanced(session_id: str, facts: List[Dict[str, Any]]):
    """Detect contradictions using AI with timeout and retry logic"""
    try:
        # Validate session exists
        metadata = await session_manager.get_metadata(session_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Session not found")

        # Execute AI agent with timeout
        result = await execute_ai_agent_with_timeout(
            "contradiction_detector", "detect_contradictions", facts
        )

        # Store contradiction results
        step_data = {
            "contradiction_result": result,
            "facts_count": len(facts),
            "processed_at": datetime.utcnow().isoformat(),
        }
        await session_manager.save_step(session_id, 3, step_data)

        logger.info(f"Contradictions detected for session {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "contradiction_result": result,
            "processed_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting contradictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Additional enhanced endpoints for other AI agents...
@router.post("/{session_id}/generate-perceptual-map")
async def generate_perceptual_map_enhanced(
    session_id: str,
    company_info: Dict[str, Any],
    competitors: List[Dict[str, Any]] = [],
):
    """Generate AI-powered perceptual map with timeout and retry logic"""
    try:
        # Validate session exists
        metadata = await session_manager.get_metadata(session_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Session not found")

        # Execute AI agent with timeout
        result = await execute_ai_agent_with_timeout(
            "perceptual_map_generator",
            "generate_perceptual_map",
            company_info,
            competitors,
        )

        # Store perceptual map
        step_data = {
            "perceptual_map": result,
            "company_info": company_info,
            "competitors_count": len(competitors),
            "processed_at": datetime.utcnow().isoformat(),
        }
        await session_manager.save_step(session_id, 4, step_data)

        logger.info(f"Perceptual map generated for session {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "perceptual_map": result,
            "processed_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating perceptual map: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/health")
async def session_health_check(session_id: str):
    """Check session health and Redis connectivity"""
    try:
        # Check session exists
        metadata = await session_manager.get_metadata(session_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Session not found")

        # Check Redis health
        redis_health = await session_manager.health_check()

        # Get session summary
        summary = await session_manager.get_session_summary(session_id)

        return {
            "success": True,
            "session_id": session_id,
            "session_health": {
                "exists": True,
                "metadata_valid": metadata is not None,
                "steps_completed": summary.get("stats", {}).get("completed_steps", 0),
                "last_activity": metadata.get("started_at"),
            },
            "redis_health": redis_health,
            "checked_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking session health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/finalize")
async def finalize_session_enhanced(session_id: str, background_tasks: BackgroundTasks):
    """Finalize onboarding session with enhanced processing"""
    try:
        # Get all steps
        all_steps = await session_manager.get_all_steps(session_id)

        if not all_steps:
            raise HTTPException(
                status_code=404, detail="No step data found for session"
            )

        # Get session metadata and progress
        metadata = await session_manager.get_metadata(session_id)
        progress = await session_manager.get_progress(session_id)

        # Build enhanced business context
        business_context = {
            "version": "2.0",
            "generated_at": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "metadata": metadata,
            "progress": progress,
            "steps": all_steps,
            "api_version": "enhanced_v2",
            "processing_summary": {
                "total_steps": len(all_steps),
                "completion_percentage": progress.get("percentage", 0),
                "session_duration": None,  # Would calculate from metadata
            },
        }

        # Add background task for BCM generation (when implemented)
        # background_tasks.add_task(generate_bcm_from_context, business_context)

        logger.info(f"Enhanced session finalized: {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "business_context": business_context,
            "completed_steps": len(all_steps),
            "total_steps": 23,
            "finalized_at": datetime.utcnow().isoformat(),
            "api_version": "enhanced_v2",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finalizing enhanced session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
