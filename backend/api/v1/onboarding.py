"""
Onboarding API Routes for RaptorFlow
Handles 23-step onboarding process with AI agents
Enhanced with evidence classification, extraction, contradiction detection
Reddit research, perceptual mapping, neuroscience copywriting, and channel strategy
"""

import asyncio
import logging
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.supabase_mgr import get_supabase_admin
from db.repositories.onboarding import OnboardingRepository
from db.repositories.onboarding_steps import OnboardingStepsRepository
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from integration.bcm_reducer import BCMReducer
from pydantic import BaseModel, Field, validator
from schemas.onboarding_schema import (
    BusinessContext,
    OnboardingFinalizationRequest,
    OnboardingFinalizationResponse,
    extract_business_context_from_steps,
    validate_step_data,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..agents.specialists.category_advisor import CategoryAdvisor
from ..agents.specialists.channel_recommender import ChannelRecommender
from ..agents.specialists.competitor_analyzer import CompetitorAnalyzer
from ..agents.specialists.contradiction_detector import ContradictionDetector

# Specialist Agent imports
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
from ..core.auth import get_current_user
from ..core.models import User

# Redis session management
from ..redis.session_manager import get_onboarding_session_manager

# Core system imports
from ..services.ocr_service import OCRService
from ..services.profile_service import ProfileService
from ..services.search.orchestrator import SOTASearchOrchestrator as NativeSearch
from ..services.storage import get_enhanced_storage_service
from ..services.vertex_ai_service import vertex_ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI Agent configuration
AI_AGENT_TIMEOUT = 30  # 30 seconds max per agent
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1

# Create router
router = APIRouter(prefix="/onboarding", tags=["onboarding"])

# Initialize industrial services
ocr_service = OCRService()
search_service = NativeSearch()
onboarding_repo = OnboardingRepository()
onboarding_steps_repo = OnboardingStepsRepository()

# Initialize Redis session manager
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


# Initialize AI agents
evidence_classifier = EvidenceClassifier()
extraction_orchestrator = ExtractionOrchestrator()
contradiction_detector = ContradictionDetector()
reddit_researcher = RedditResearcher()
perceptual_map_generator = PerceptualMapGenerator()
neuroscience_copywriter = NeuroscienceCopywriter()
channel_recommender = ChannelRecommender()
category_advisor = CategoryAdvisor()
market_size_calculator = MarketSizeCalculator()
competitor_analyzer = CompetitorAnalyzer()
focus_sacrifice_engine = FocusSacrificeEngine()
proof_point_validator = ProofPointValidator()
truth_sheet_generator = TruthSheetGenerator()
messaging_rules_engine = MessagingRulesEngine()
soundbites_generator = SoundbitesGenerator()
icp_deep_generator = ICPDeepGenerator()
positioning_generator = PositioningStatementGenerator()

TOTAL_ONBOARDING_STEPS = 23
STEP_STATUSES = {"pending", "in-progress", "complete", "blocked", "error"}
STEP_NAMES = {
    1: "Evidence Vault",
    2: "Brand Synthesis",
    3: "Strategic Integrity",
    4: "Truth Confirmation",
    5: "The Offer",
    6: "Market Intelligence",
    7: "Competitive Landscape",
    8: "Comparative Angle",
    9: "Market Category",
    10: "Product Capabilities",
    11: "Perceptual Map",
    12: "Position Grid",
    13: "Gap Analysis",
    14: "Positioning Statements",
    15: "Focus & Sacrifice",
    16: "ICP Personas",
    17: "Market Education",
    18: "Messaging Rules",
    19: "Soundbites Library",
    20: "Channel Strategy",
    21: "Market Size",
    22: "Validation Tasks",
    23: "Final Synthesis",
}


def _get_step_name(step_number: int) -> str:
    return STEP_NAMES.get(step_number, f"Step {step_number}")


def _get_phase_number(step_number: int) -> int:
    if step_number <= 4:
        return 1
    if step_number <= 5:
        return 2
    if step_number <= 8:
        return 3
    if step_number <= 13:
        return 4
    if step_number <= 19:
        return 5
    return 6


def _build_next_step_guidance(
    step_number: int, completed: bool = False
) -> Dict[str, Any]:
    if completed or step_number >= TOTAL_ONBOARDING_STEPS:
        return {
            "next_step": None,
            "message": "Onboarding complete. You can move on to the dashboard.",
        }

    next_step = step_number + 1 if step_number >= 1 else 1
    return {
        "next_step": {
            "step_number": next_step,
            "step_name": _get_step_name(next_step),
        },
        "message": f"Continue to step {next_step}: {_get_step_name(next_step)}.",
    }


def _calculate_progress_percentage(completed_steps: int) -> float:
    if TOTAL_ONBOARDING_STEPS <= 0:
        return 0.0
    percentage = (completed_steps / TOTAL_ONBOARDING_STEPS) * 100
    return round(min(max(percentage, 0.0), 100.0), 2)


# Pydantic models with enhanced validation
class StepUpdateRequest(BaseModel):
    data: Dict[str, Any]
    version: int = 1
    workspace_id: Optional[str] = None  # Make optional for decoupled testing

    @validator("data")
    def validate_data_not_empty(cls, v):
        if not v or not isinstance(v, dict):
            raise ValueError("Data must be a non-empty dictionary")
        return v


class SessionCreateRequest(BaseModel):
    workspace_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    client_name: Optional[str] = None


class StepSaveRequest(BaseModel):
    step_number: int = Field(..., ge=1, le=TOTAL_ONBOARDING_STEPS)
    status: str = Field(..., description="pending|in-progress|complete|blocked|error")
    step_data: Dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_required: bool = True

    @validator("status")
    def validate_status(cls, value: str) -> str:
        if value not in STEP_STATUSES:
            raise ValueError(f"Invalid status '{value}'")
        return value

    @validator("completed_at")
    def validate_completion(cls, value: Optional[datetime], values: Dict[str, Any]):
        if value and values.get("status") != "complete":
            raise ValueError("completed_at requires status='complete'")
        return value


class CompletionRequest(BaseModel):
    finalize_context: bool = False


class URLProcessRequest(BaseModel):
    url: str
    item_id: str
    workspace_id: str


# AI Agent wrapper with enhanced exponential-backoff and timeout handling
async def execute_ai_agent_with_timeout(
    agent_name: str, method_name: str, *args, **kwargs
):
    """Execute AI agent method with enhanced exponential-backoff and graceful timeout handling."""
    agent_map = {
        "evidence_classifier": evidence_classifier,
        "extraction_orchestrator": extraction_orchestrator,
        "contradiction_detector": contradiction_detector,
        "reddit_researcher": reddit_researcher,
        "perceptual_map_generator": perceptual_map_generator,
        "neuroscience_copywriter": neuroscience_copywriter,
        "channel_recommender": channel_recommender,
        "category_advisor": category_advisor,
        "market_size_calculator": market_size_calculator,
        "competitor_analyzer": competitor_analyzer,
        "focus_sacrifice_engine": focus_sacrifice_engine,
        "proof_point_validator": proof_point_validator,
        "truth_sheet_generator": truth_sheet_generator,
        "messaging_rules_engine": messaging_rules_engine,
        "soundbites_generator": soundbites_generator,
        "icp_deep_generator": icp_deep_generator,
        "positioning_generator": positioning_generator,
    }

    agent = agent_map.get(agent_name)
    if not agent:
        raise HTTPException(
            status_code=503, detail=f"AI agent '{agent_name}' not available"
        )

    # Enhanced exponential-backoff with jitter
    for attempt in range(MAX_RETRIES):
        try:
            method = getattr(agent, method_name)

            # Add jitter to prevent thundering herd
            jitter = 0.1 * (2**attempt) * (0.5 + (hash(session_id) % 100) / 100)
            wait_time = RETRY_BASE_DELAY * (2**attempt) + jitter

            result = await asyncio.wait_for(
                method(*args, **kwargs), timeout=AI_AGENT_TIMEOUT
            )

            # Log successful retry if applicable
            if attempt > 0:
                logger.info(
                    f"AI agent {agent_name}.{method_name} succeeded on attempt {attempt + 1}"
                )

            return result

        except asyncio.TimeoutError:
            if attempt < MAX_RETRIES - 1:
                logger.warning(
                    f"AI agent {agent_name}.{method_name} timeout (attempt {attempt + 1}/{MAX_RETRIES}), "
                    f"retrying in {wait_time:.2f}s..."
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    f"AI agent {agent_name}.{method_name} failed after {MAX_RETRIES} attempts due to timeout"
                )
                raise HTTPException(
                    status_code=504,
                    detail=f"AI processing timeout after {MAX_RETRIES} attempts (30s each)",
                )

        except Exception as e:
            # Classify error for retry decision
            is_retryable = (
                isinstance(e, (ConnectionError, TimeoutError))
                or "rate limit" in str(e).lower()
                or "temporary" in str(e).lower()
                or "service unavailable" in str(e).lower()
            )

            if attempt < MAX_RETRIES - 1 and is_retryable:
                logger.warning(
                    f"AI agent {agent_name}.{method_name} retryable error (attempt {attempt + 1}/{MAX_RETRIES}): {e}, "
                    f"retrying in {wait_time:.2f}s..."
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"AI agent {agent_name}.{method_name} failed: {e}")
                raise HTTPException(
                    status_code=500, detail=f"AI processing failed: {str(e)}"
                )


# Helper functions
async def scrape_website(url: str) -> Dict[str, Any]:
    """Scrape website content using the real SOTA search service"""
    try:
        # Validate URL
        if not url or not url.startswith(("http://", "https://")):
            return {"status": "error", "error": "Invalid URL format"}

        # Use SOTA search cluster
        results = await search_service.query(f"site:{url}", limit=1)

        if results:
            res = results[0]
            return {
                "status": "success",
                "title": res.get("title", ""),
                "content": res.get("snippet", ""),
                "url": url,
                "source": "sota_search_cluster",
                "search_confidence": res.get("confidence", 0.9),
                "domain": url.split("//")[-1].split("/")[0],
            }
        else:
            return {
                "status": "error",
                "error": f"No content found for URL via SOTA cluster: {url}",
            }

    except Exception as e:
        logger.error(f"SOTA scraping failed for {url}: {e}")
        return {
            "status": "error",
            "error": f"Search cluster unavailable: {str(e)}",
            "url": url,
        }


async def process_ocr(file_path: str, file_content: bytes) -> Dict[str, Any]:
    """Process file with real industrial OCR service"""
    try:
        # Determine file type
        file_extension = os.path.splitext(file_path)[1].lower()
        content_type = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".tiff": "image/tiff",
        }.get(file_extension, "application/octet-stream")

        # Process with real Hybrid OCR Machine
        result = await ocr_service.extract_text_from_bytes(
            file_content=file_content,
            file_type=content_type,
            document_id=os.path.basename(file_path),
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
        }

    except Exception as e:
        logger.error(f"Industrial OCR processing failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "extracted_text": "",
            "page_count": 0,
            "confidence": 0.0,
        }


# API Endpoints


@router.post("/session")
async def create_or_get_session(workspace_id: str, user_id: Optional[str] = None):
    """Create or retrieve onboarding session for workspace using Redis"""
    try:
        # Generate a unique session ID
        import uuid

        session_id = str(uuid.uuid4())

        # Set session metadata in Redis
        if user_id:
            await session_manager.set_metadata(session_id, user_id, workspace_id)
        else:
            # For backward compatibility, create metadata without user_id
            await session_manager.set_metadata(session_id, "unknown", workspace_id)

        # Initialize progress
        await session_manager.update_progress(session_id, 0)

        # Return session info
        progress = await session_manager.get_progress(session_id)
        metadata = await session_manager.get_metadata(session_id)

        return {
            "session_id": session_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "progress": progress,
            "metadata": metadata,
            "created_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error creating Redis session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/create")
async def create_onboarding_session(request: SessionCreateRequest):
    """Create onboarding session persisted in onboarding_sessions/onboarding_steps."""
    try:
        import uuid

        supabase = get_supabase_admin()
        public_session_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        payload = {
            "session_id": public_session_id,
            "user_id": request.user_id,
            "workspace_id": request.workspace_id,
            "client_name": request.client_name,
            "current_step": 1,
            "total_steps": TOTAL_ONBOARDING_STEPS,
            "completion_percentage": 0,
            "status": "active",
            "started_at": now,
            "updated_at": now,
            "metadata": {"client_name": request.client_name},
        }

        result = (
            await supabase.table("onboarding_sessions")
            .insert(payload)
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create session")

        session_row = result.data
        db_session_id = session_row.get("id")
        if not db_session_id:
            raise HTTPException(status_code=500, detail="Missing session identifier")

        onboarding_steps_repo.upsert_step(
            session_id=db_session_id,
            step_number=1,
            step_name=_get_step_name(1),
            phase_number=_get_phase_number(1),
            status="pending",
            step_data={},
            started_at=None,
            completed_at=None,
            is_required=True,
        )

        return {
            "success": True,
            "session_id": db_session_id,
            "public_session_id": public_session_id,
            "workspace_id": request.workspace_id,
            "user_id": request.user_id,
            "current_step": 1,
            "progress_percentage": 0.0,
            "next_step_guidance": _build_next_step_guidance(0),
            "created_at": now,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating onboarding session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/steps")
async def save_onboarding_step(session_id: str, request: StepSaveRequest):
    """Save/update onboarding step data in onboarding_steps with ordering."""
    try:
        supabase = get_supabase_admin()
        session_result = (
            await supabase.table("onboarding_sessions")
            .select("*")
            .eq("id", session_id)
            .maybe_single()
            .execute()
        )
        session_row = session_result.data
        if not session_row:
            session_result = (
                await supabase.table("onboarding_sessions")
                .select("*")
                .eq("session_id", session_id)
                .maybe_single()
                .execute()
            )
            session_row = session_result.data

        if not session_row:
            raise HTTPException(status_code=404, detail="Session not found")

        db_session_id = session_row.get("id", session_id)
        existing_step = onboarding_steps_repo.get_step(
            db_session_id, request.step_number
        )
        current_step = session_row.get("current_step", 1)

        if not existing_step and request.step_number > current_step + 1:
            raise HTTPException(
                status_code=400,
                detail="Step order violation. Complete prior steps before continuing.",
            )

        if existing_step and existing_step.get("status") == "complete":
            if request.status != "complete":
                raise HTTPException(
                    status_code=400, detail="Completed steps cannot be reverted."
                )

        if request.status == "complete":
            is_valid, validation_errors = validate_step_data(
                request.step_number, request.step_data
            )
            if not is_valid:
                raise HTTPException(
                    status_code=400,
                    detail=f"Step validation failed: {'; '.join(validation_errors)}",
                )

        started_at = (
            request.started_at or existing_step.get("started_at")
            if existing_step
            else None
        )
        if not started_at and request.status in {"in-progress", "complete"}:
            started_at = datetime.utcnow()

        completed_at = request.completed_at
        if request.status == "complete" and not completed_at:
            completed_at = datetime.utcnow()
        if request.status != "complete":
            completed_at = None

        saved_step = onboarding_steps_repo.upsert_step(
            session_id=db_session_id,
            step_number=request.step_number,
            step_name=_get_step_name(request.step_number),
            phase_number=_get_phase_number(request.step_number),
            status=request.status,
            step_data=request.step_data,
            started_at=started_at,
            completed_at=completed_at,
            is_required=request.is_required,
        )

        completed_steps = onboarding_steps_repo.count_completed_steps(db_session_id)
        progress_percentage = _calculate_progress_percentage(completed_steps)

        new_current_step = current_step
        if request.status == "complete" and request.step_number >= current_step:
            new_current_step = min(request.step_number + 1, TOTAL_ONBOARDING_STEPS)
        if completed_steps >= TOTAL_ONBOARDING_STEPS:
            new_current_step = TOTAL_ONBOARDING_STEPS

        session_status = (
            "completed" if completed_steps >= TOTAL_ONBOARDING_STEPS else "active"
        )

        await supabase.table("onboarding_sessions").update(
            {
                "current_step": new_current_step,
                "completion_percentage": progress_percentage,
                "status": session_status,
                "updated_at": datetime.utcnow().isoformat(),
            }
        ).eq("id", db_session_id).execute()

        guidance = (
            _build_next_step_guidance(
                request.step_number,
                completed=completed_steps >= TOTAL_ONBOARDING_STEPS,
            )
            if request.status == "complete"
            else _build_next_step_guidance(request.step_number - 1)
        )

        return {
            "success": True,
            "session_id": db_session_id,
            "step": {
                "step_number": request.step_number,
                "step_name": _get_step_name(request.step_number),
                "phase_number": _get_phase_number(request.step_number),
                "status": request.status,
                "saved_at": saved_step.get("updated_at"),
            },
            "completed_steps": completed_steps,
            "progress_percentage": progress_percentage,
            "current_step": new_current_step,
            "next_step_guidance": guidance,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving onboarding step: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/complete")
async def complete_onboarding_session(
    session_id: str, request: Optional[CompletionRequest] = None
):
    """Mark onboarding session as complete and return progress guidance."""
    try:
        _ = request
        supabase = get_supabase_admin()
        session_result = (
            await supabase.table("onboarding_sessions")
            .select("*")
            .eq("id", session_id)
            .maybe_single()
            .execute()
        )
        session_row = session_result.data
        if not session_row:
            session_result = (
                await supabase.table("onboarding_sessions")
                .select("*")
                .eq("session_id", session_id)
                .maybe_single()
                .execute()
            )
            session_row = session_result.data

        if not session_row:
            raise HTTPException(status_code=404, detail="Session not found")

        db_session_id = session_row.get("id", session_id)
        completed_steps = onboarding_steps_repo.count_completed_steps(db_session_id)
        if completed_steps < TOTAL_ONBOARDING_STEPS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot complete session. "
                    f"{completed_steps}/{TOTAL_ONBOARDING_STEPS} steps completed."
                ),
            )

        now = datetime.utcnow().isoformat()
        await supabase.table("onboarding_sessions").update(
            {
                "status": "completed",
                "completion_percentage": 100,
                "current_step": TOTAL_ONBOARDING_STEPS,
                "completed_at": now,
                "updated_at": now,
            }
        ).eq("id", db_session_id).execute()

        return {
            "success": True,
            "session_id": db_session_id,
            "completed_steps": completed_steps,
            "progress_percentage": 100.0,
            "next_step_guidance": _build_next_step_guidance(
                TOTAL_ONBOARDING_STEPS, completed=True
            ),
            "completed_at": now,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing onboarding session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/steps/{step_id}")
async def update_step_data(session_id: str, step_id: int, request: StepUpdateRequest):
    """Update step data using Redis session manager with validation and TTL refresh"""
    try:
        # Validate step ID
        if step_id < 1 or step_id > 23:
            raise HTTPException(
                status_code=400, detail="Invalid step ID. Must be between 1 and 23."
            )

        # Validate payload shape per step
        is_valid, validation_errors = validate_step_data(step_id, request.data)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Step validation failed: {'; '.join(validation_errors)}",
            )

        # Save step data to Redis (this will refresh TTL automatically)
        success = await session_manager.save_step(session_id, step_id, request.data)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to save step data")

        # Explicitly refresh session TTL on each write
        await session_manager.refresh_session_ttl(session_id)

        # Get updated progress
        progress = await session_manager.get_progress(session_id)

        logger.info(f"Validated and updated step {step_id} for session {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "step_id": step_id,
            "progress": progress,
            "validation_passed": True,
            "updated_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating step data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/progress")
async def get_session_progress(session_id: str):
    """Get current session progress"""
    try:
        progress = await session_manager.get_progress(session_id)

        if not progress:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"session_id": session_id, "progress": progress}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/steps/{step_id}")
async def get_step_data(session_id: str, step_id: int):
    """Get specific step data"""
    try:
        if step_id < 1 or step_id > 23:
            raise HTTPException(
                status_code=400, detail="Invalid step ID. Must be between 1 and 23."
            )

        step_data = await session_manager.get_step(session_id, step_id)

        if not step_data:
            raise HTTPException(status_code=404, detail="Step data not found")

        return {"session_id": session_id, "step_id": step_id, "data": step_data}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting step data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/summary")
async def get_session_summary(session_id: str):
    """Get complete session summary"""
    try:
        summary = await session_manager.get_session_summary(session_id)

        if not summary or "error" in summary:
            raise HTTPException(status_code=404, detail="Session not found")

        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/finalize")
async def finalize_session(session_id: str, force_finalize: bool = False):
    """Finalize onboarding session with comprehensive validation and BCM generation"""
    try:
        # Pull all 23 steps from Redis
        all_steps = await session_manager.get_all_steps(session_id)

        if not all_steps:
            raise HTTPException(
                status_code=404, detail="No step data found for session"
            )

        # Get session metadata and progress
        metadata = await session_manager.get_metadata(session_id)
        progress = await session_manager.get_progress(session_id)

        # Enforce completion threshold (require at least 20/23 steps unless forced)
        completed_steps = len(all_steps)
        if completed_steps < 20 and not force_finalize:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient steps completed: {completed_steps}/23 (minimum 20 required). Use force_finalize=true to override.",
            )

        # Build business context from all steps
        business_context_data = {
            "version": "2.0",
            "generated_at": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "metadata": metadata,
            "progress": progress,
            "steps": all_steps,
        }

        # Run schema validation
        try:
            business_context = extract_business_context_from_steps(
                business_context_data
            )
        except Exception as validation_error:
            if not force_finalize:
                raise HTTPException(
                    status_code=400,
                    detail=f"Business context validation failed: {str(validation_error)}. Use force_finalize=true to override.",
                )
            logger.warning(
                f"Business context validation failed but proceeding with force finalize: {validation_error}"
            )
            business_context = None

        # Call BCM reducer to generate Business Context Manifest
        try:
            bcm_reducer = BCMReducer()
            bcm_result = await bcm_reducer.reduce(business_context_data)
            logger.info(f"BCM generated successfully for session {session_id}")
        except Exception as bcm_error:
            logger.error(f"BCM generation failed for session {session_id}: {bcm_error}")
            bcm_result = None
            if not force_finalize:
                raise HTTPException(
                    status_code=500,
                    detail=f"BCM generation failed: {str(bcm_error)}. Use force_finalize=true to override.",
                )

        # Persist onboarding status to database
        supabase = get_supabase_admin()
        if metadata and "user_id" in metadata:
            try:
                await supabase.table("users").update(
                    {
                        "onboarding_status": "completed",
                        "onboarding_completed_at": datetime.utcnow().isoformat(),
                    }
                ).eq("id", metadata["user_id"]).execute()

                logger.info(
                    f"Updated user {metadata['user_id']} onboarding status to completed"
                )
            except Exception as e:
                logger.error(f"Failed to update user onboarding status: {e}")
                # Don't fail the request if status update fails

        # Store BCM in database if available
        if bcm_result:
            try:
                # Import BCM service for storage
                from ..services.bcm_service import BCMService

                bcm_service = BCMService(db_client=supabase)

                # Store the generated BCM
                await bcm_service.store_manifest(
                    workspace_id=metadata.get("workspace_id", "unknown"),
                    manifest=bcm_result.dict(),
                    user_id=metadata.get("user_id"),
                )
                logger.info(
                    f"BCM stored in database for workspace {metadata.get('workspace_id')}"
                )
            except Exception as storage_error:
                logger.error(f"Failed to store BCM in database: {storage_error}")
                # Don't fail the request if BCM storage fails

        # Clear Redis session after successful finalization
        await session_manager.clear_session(session_id)

        logger.info(
            f"Finalized session {session_id} with {completed_steps} steps and generated BCM"
        )

        return {
            "success": True,
            "session_id": session_id,
            "business_context": business_context.dict() if business_context else None,
            "bcm": bcm_result.dict() if bcm_result else None,
            "completed_steps": completed_steps,
            "total_steps": 23,
            "completion_percentage": (completed_steps / 23) * 100,
            "finalized_at": datetime.utcnow().isoformat(),
            "validation_passed": business_context is not None,
            "bcm_generated": bcm_result is not None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finalizing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete session and all associated data"""
    try:
        success = await session_manager.delete_session(session_id)

        if not success:
            raise HTTPException(
                status_code=404, detail="Session not found or already deleted"
            )

        return {
            "success": True,
            "session_id": session_id,
            "message": "Session deleted successfully",
            "deleted_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# New AI Agent Endpoints for 23-Step Onboarding


@router.post("/{session_id}/classify-evidence")
async def classify_evidence(session_id: str, evidence_data: Dict[str, Any]):
    """Classify evidence using AI with timeout and retry logic"""
    try:
        # Validate session exists
        metadata = await session_manager.get_metadata(session_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Session not found")

        # Execute AI agent with timeout
        result = await execute_ai_agent_with_timeout(
            "evidence_classifier", "classify_document", evidence_data
        )

        # Store classification in database
        await onboarding_repo.store_evidence_classification(session_id, result)

        logger.info(f"Evidence classified for session {session_id}")

        return {"success": True, "classification": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error classifying evidence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/extract-facts")
async def extract_facts(session_id: str, evidence_list: List[Dict[str, Any]]):
    """Extract facts from evidence using AI with timeout and retry logic"""
    try:
        # Validate session exists
        metadata = await session_manager.get_metadata(session_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Session not found")

        # Execute AI agent with timeout
        result = await execute_ai_agent_with_timeout(
            "extraction_orchestrator", "extract_facts_from_evidence", evidence_list
        )

        # Store extracted facts in database
        await onboarding_repo.store_extracted_facts(session_id, result.facts)

        return {"success": True, "extraction_result": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting facts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/detect-contradictions")
async def detect_contradictions(session_id: str, facts: List[Dict[str, Any]]):
    """Detect contradictions in extracted facts using AI with timeout and retry logic"""
    try:
        # Validate session exists
        metadata = await session_manager.get_metadata(session_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Session not found")

        # Execute AI agent with timeout
        result = await execute_ai_agent_with_timeout(
            "contradiction_detector", "detect_contradictions", facts
        )

        # Store contradictions in database
        await onboarding_repo.store_contradictions(session_id, result.contradictions)

        return {"success": True, "contradiction_result": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting contradictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/reddit-research")
async def reddit_research(session_id: str, company_info: Dict[str, Any]):
    """Perform Reddit market research"""
    try:
        if not reddit_researcher:
            raise HTTPException(
                status_code=503, detail="Reddit researcher not available"
            )

        result = await reddit_researcher.analyze_reddit_market(company_info)

        # Store research data in database
        await onboarding_repo.store_reddit_research(session_id, result)

        return {"success": True, "research_result": result}
    except Exception as e:
        logger.error(f"Error performing Reddit research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/generate-perceptual-map")
async def generate_perceptual_map(
    session_id: str, company_info: Dict[str, Any], competitors: List[Dict[str, Any]]
):
    """Generate AI-powered perceptual map"""
    try:
        if not perceptual_map_generator:
            raise HTTPException(
                status_code=503, detail="Perceptual map generator not available"
            )

        result = await perceptual_map_generator.generate_perceptual_map(
            company_info, competitors
        )

        # Store perceptual map in database
        await onboarding_repo.store_perceptual_map(session_id, result)

        return {"success": True, "perceptual_map": result}
    except Exception as e:
        logger.error(f"Error generating perceptual map: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/generate-copy")
async def generate_neuroscience_copy(session_id: str, product_info: Dict[str, Any]):
    """Generate neuroscience-based copywriting"""
    try:
        if not neuroscience_copywriter:
            raise HTTPException(
                status_code=503, detail="Neuroscience copywriter not available"
            )

        result = await neuroscience_copywriter.generate_copywriting_campaign(
            product_info
        )

        # Store copy variants in database
        await onboarding_repo.store_copy_variants(session_id, result.variants)

        return {"success": True, "copywriting_result": result}
    except Exception as e:
        logger.error(f"Error generating copy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/channel-strategy")
async def generate_channel_strategy(
    session_id: str,
    company_info: Dict[str, Any],
    competitors: List[Dict[str, Any]] = None,
):
    """Generate AI-powered channel strategy"""
    try:
        if not channel_recommender:
            raise HTTPException(
                status_code=503, detail="Channel recommender not available"
            )

        result = await channel_recommender.analyze_channels(company_info, competitors)

        # Store channel strategy in database
        await onboarding_repo.store_channel_strategy(session_id, result.strategy)

        return {"success": True, "channel_strategy": result}
    except Exception as e:
        logger.error(f"Error generating channel strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/category-paths")
async def analyze_category_paths(
    session_id: str,
    company_info: Dict[str, Any],
    competitors: List[Dict[str, Any]] = None,
):
    """Generate Safe/Clever/Bold category path recommendations"""
    try:
        if not category_advisor:
            raise HTTPException(
                status_code=503, detail="Category advisor not available"
            )

        result = await category_advisor.analyze_category_paths(
            company_info, competitors
        )

        # Store category paths in database
        await onboarding_repo.store_category_paths(
            session_id,
            {
                "safe_path": result.safe_path.__dict__,
                "clever_path": result.clever_path.__dict__,
                "bold_path": result.bold_path.__dict__,
                "recommended": result.recommended_path.value,
                "rationale": result.recommendation_rationale,
            },
        )

        return {
            "success": True,
            "category_paths": {
                "safe": result.safe_path.__dict__,
                "clever": result.clever_path.__dict__,
                "bold": result.bold_path.__dict__,
                "recommended": result.recommended_path.value,
                "rationale": result.recommendation_rationale,
                "decision_factors": result.decision_factors,
            },
        }
    except Exception as e:
        logger.error(f"Error analyzing category paths: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/market-size")
async def calculate_market_size(session_id: str, company_info: Dict[str, Any]):
    """Calculate TAM/SAM/SOM with beautiful visualization data"""
    try:
        if not market_size_calculator:
            raise HTTPException(
                status_code=503, detail="Market size calculator not available"
            )

        result = await market_size_calculator.calculate_market_size(company_info)

        # Get visualization config
        viz_config = market_size_calculator.get_visualization_config(result)

        # Store market size in database
        await onboarding_repo.store_market_size(
            session_id,
            {
                "tam": result.tam.__dict__,
                "sam": result.sam.__dict__,
                "som": result.som.__dict__,
                "summary": result.market_summary,
            },
        )

        return {
            "success": True,
            "market_size": {
                "tam": {
                    "value": result.tam.value,
                    "formatted": result.tam.value_formatted,
                    "description": result.tam.description,
                    "confidence": result.tam.confidence_level,
                    "growth_rate": result.tam.growth_rate,
                    "projected_5y": result.tam.projected_value_5y,
                },
                "sam": {
                    "value": result.sam.value,
                    "formatted": result.sam.value_formatted,
                    "percentage_of_tam": result.sam.percentage_of_tam,
                    "description": result.sam.description,
                    "confidence": result.sam.confidence_level,
                },
                "som": {
                    "value": result.som.value,
                    "formatted": result.som.value_formatted,
                    "percentage_of_tam": result.som.percentage_of_tam,
                    "description": result.som.description,
                    "confidence": result.som.confidence_level,
                },
                "summary": result.market_summary,
                "recommendations": result.recommendations,
                "methodology": result.methodology_notes,
                "visualization": viz_config,
            },
        }
    except Exception as e:
        logger.error(f"Error calculating market size: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/competitor-analysis")
async def analyze_competitors(
    session_id: str,
    company_info: Dict[str, Any],
    discovered_competitors: List[Dict[str, Any]] = None,
):
    """Perform comprehensive competitor analysis"""
    try:
        if not competitor_analyzer:
            raise HTTPException(
                status_code=503, detail="Competitor analyzer not available"
            )

        result = await competitor_analyzer.analyze_competitors(
            company_info, discovered_competitors
        )

        # Store competitor analysis
        await onboarding_repo.store_competitor_analysis(
            session_id,
            {
                "competitors": [c.__dict__ for c in result.competitors],
                "advantages": [a.__dict__ for a in result.competitive_advantages],
                "gaps": result.market_gaps,
                "threat_assessment": result.threat_assessment,
            },
        )

        return {
            "success": True,
            "competitor_analysis": {
                "competitor_count": len(result.competitors),
                "competitors": [
                    {
                        "name": c.name,
                        "type": c.competitor_type.value,
                        "threat": c.threat_level.value,
                    }
                    for c in result.competitors
                ],
                "advantages": [
                    {"description": a.description, "category": a.category}
                    for a in result.competitive_advantages
                ],
                "market_gaps": result.market_gaps,
                "threat_assessment": result.threat_assessment,
                "recommendations": result.recommendations,
                "summary": result.analysis_summary,
            },
        }
    except Exception as e:
        logger.error(f"Error analyzing competitors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/focus-sacrifice")
async def analyze_focus_sacrifice(
    session_id: str,
    company_info: Dict[str, Any],
    icp_data: Dict[str, Any] = None,
    capabilities: List[Dict[str, Any]] = None,
    positioning: Dict[str, Any] = None,
):
    """Analyze strategic focus and sacrifice tradeoffs"""
    try:
        if not focus_sacrifice_engine:
            raise HTTPException(
                status_code=503, detail="Focus/sacrifice engine not available"
            )

        result = await focus_sacrifice_engine.analyze_focus_sacrifice(
            company_info, icp_data, capabilities, positioning
        )

        # Store focus/sacrifice analysis
        await onboarding_repo.store_focus_sacrifice(
            session_id,
            {
                "focus_items": [f.__dict__ for f in result.focus_items],
                "sacrifice_items": [s.__dict__ for s in result.sacrifice_items],
                "positioning_statement": result.positioning_statement,
            },
        )

        return {
            "success": True,
            "focus_sacrifice": {
                "focus_items": [
                    {
                        "description": f.description,
                        "category": f.category.value,
                        "impact": f.impact_score,
                    }
                    for f in result.focus_items
                ],
                "sacrifice_items": [
                    {
                        "description": s.description,
                        "impact": s.impact.value,
                        "alternative_message": s.alternative_message,
                    }
                    for s in result.sacrifice_items
                ],
                "tradeoff_pairs": len(result.tradeoff_pairs),
                "positioning_statement": result.positioning_statement,
                "lightbulb_insights": result.lightbulb_insights,
                "recommendations": result.recommendations,
                "summary": result.constraint_summary,
            },
        }
    except Exception as e:
        logger.error(f"Error analyzing focus/sacrifice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/truth-sheet")
async def generate_truth_sheet(
    session_id: str,
    evidence_list: List[Dict[str, Any]],
    existing_entries: List[Dict[str, Any]] = None,
):
    """Generate truth sheet from evidence"""
    try:
        if not truth_sheet_generator:
            raise HTTPException(
                status_code=503, detail="Truth sheet generator not available"
            )

        result = await truth_sheet_generator.generate_truth_sheet(
            evidence_list, existing_entries
        )

        # Store truth sheet
        await onboarding_repo.store_truth_sheet(
            session_id,
            {
                "entries": [e.__dict__ for e in result.entries],
                "completeness": result.completeness_score,
                "categories": result.categories_covered,
            },
        )

        return {
            "success": True,
            "truth_sheet": {
                "entries": [
                    {
                        "id": e.id,
                        "category": e.category.value,
                        "field_name": e.field_name,
                        "value": e.value,
                        "confidence": e.confidence.value,
                        "verified": e.verified,
                    }
                    for e in result.entries
                ],
                "completeness_score": result.completeness_score,
                "categories_covered": result.categories_covered,
                "missing_fields": result.missing_fields,
                "recommendations": result.recommendations,
                "summary": result.summary,
            },
        }
    except Exception as e:
        logger.error(f"Error generating truth sheet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/proof-points")
async def validate_proof_points(
    session_id: str, claims: List[str], evidence: List[Dict[str, Any]] = None
):
    """Validate claims with proof points"""
    try:
        if not proof_point_validator:
            raise HTTPException(
                status_code=503, detail="Proof point validator not available"
            )

        result = await proof_point_validator.validate_claims(claims, evidence)

        # Store validation results
        await onboarding_repo.store_proof_points(
            session_id,
            {
                "validations": [v.__dict__ for v in result.validations],
                "overall_score": result.overall_score,
                "strong_claims": result.strong_claims,
                "weak_claims": result.weak_claims,
            },
        )

        return {
            "success": True,
            "validation": {
                "validations": [
                    {
                        "claim_id": v.claim_id,
                        "claim_text": v.claim_text,
                        "status": v.status.value,
                        "strength": v.strength.value,
                        "confidence_score": v.confidence_score,
                        "recommendations": v.recommendations,
                    }
                    for v in result.validations
                ],
                "overall_score": result.overall_score,
                "strong_claims": result.strong_claims,
                "weak_claims": result.weak_claims,
                "needs_evidence": result.needs_evidence,
                "recommendations": result.recommendations,
                "summary": result.summary,
            },
        }
    except Exception as e:
        logger.error(f"Error validating proof points: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/messaging-rules")
async def generate_messaging_rules(
    session_id: str, company_info: Dict[str, Any], positioning: Dict[str, Any] = None
):
    """Generate messaging rules and guardrails"""
    try:
        if not messaging_rules_engine:
            raise HTTPException(
                status_code=503, detail="Messaging rules engine not available"
            )

        result = await messaging_rules_engine.generate_messaging_rules(
            company_info, positioning
        )

        await onboarding_repo.store_messaging_rules(
            session_id,
            {
                "rules": [
                    {
                        "id": r.id,
                        "category": r.category.value,
                        "name": r.name,
                        "severity": r.severity.value,
                    }
                    for r in result.rules
                ],
                "rule_count": result.rule_count,
            },
        )

        return {
            "success": True,
            "messaging_rules": {
                "rules": [
                    {
                        "id": r.id,
                        "category": r.category.value,
                        "name": r.name,
                        "description": r.description,
                        "severity": r.severity.value,
                        "status": r.status.value,
                    }
                    for r in result.rules
                ],
                "rule_count": result.rule_count,
                "categories_covered": result.categories_covered,
                "recommendations": result.recommendations,
                "summary": result.summary,
            },
        }
    except Exception as e:
        logger.error(f"Error generating messaging rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/soundbites")
async def generate_soundbites(
    session_id: str,
    company_info: Dict[str, Any],
    positioning: Dict[str, Any] = None,
    icp_data: Dict[str, Any] = None,
):
    """Generate soundbites library"""
    try:
        if not soundbites_generator:
            raise HTTPException(
                status_code=503, detail="Soundbites generator not available"
            )

        result = await soundbites_generator.generate_soundbites(
            company_info, positioning, icp_data
        )

        await onboarding_repo.store_soundbites(
            session_id,
            {
                "soundbites": [
                    {
                        "id": s.id,
                        "type": s.type.value,
                        "content": s.content,
                        "score": s.score,
                    }
                    for s in result.soundbites
                ],
                "count": len(result.soundbites),
            },
        )

        return {
            "success": True,
            "soundbites": {
                "library": [
                    {
                        "id": s.id,
                        "type": s.type.value,
                        "content": s.content,
                        "audience": s.audience.value,
                        "tone": s.tone.value,
                        "score": s.score,
                        "use_cases": s.use_cases,
                    }
                    for s in result.soundbites
                ],
                "by_type": {k: len(v) for k, v in result.by_type.items()},
                "recommendations": result.recommendations,
                "summary": result.summary,
            },
        }
    except Exception as e:
        logger.error(f"Error generating soundbites: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/icp-deep")
async def generate_icp_deep(
    session_id: str,
    company_info: Dict[str, Any],
    positioning: Dict[str, Any] = None,
    count: int = 3,
):
    """Generate comprehensive ICP profiles"""
    try:
        if not icp_deep_generator:
            raise HTTPException(
                status_code=503, detail="ICP deep generator not available"
            )

        result = await icp_deep_generator.generate_icp_profiles(
            company_info, positioning, count
        )

        await onboarding_repo.store_icp_deep(
            session_id,
            {
                "profiles": [
                    icp_deep_generator.profile_to_dict(p) for p in result.profiles
                ],
                "primary_icp": result.primary_icp.name if result.primary_icp else None,
            },
        )

        return {
            "success": True,
            "icp_profiles": {
                "profiles": [
                    icp_deep_generator.profile_to_dict(p) for p in result.profiles
                ],
                "primary_icp": result.primary_icp.name if result.primary_icp else None,
                "recommendations": result.recommendations,
                "summary": result.summary,
            },
        }
    except Exception as e:
        logger.error(f"Error generating ICP deep: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/positioning")
async def generate_positioning(
    session_id: str,
    company_info: Dict[str, Any],
    positioning: Dict[str, Any] = None,
    icp_data: Dict[str, Any] = None,
):
    """Generate positioning statements"""
    try:
        if not positioning_generator:
            raise HTTPException(
                status_code=503, detail="Positioning generator not available"
            )

        result = await positioning_generator.generate_positioning(
            company_info, positioning, icp_data
        )

        await onboarding_repo.store_positioning(
            session_id,
            {
                "statements": [
                    {
                        "id": s.id,
                        "type": s.type.value,
                        "framework": s.framework.value,
                        "statement": s.statement,
                        "score": s.score,
                    }
                    for s in result.statements
                ],
                "primary_statement": (
                    result.primary_statement.statement
                    if result.primary_statement
                    else None
                ),
                "only_we_claims": result.only_we_claims,
            },
        )

        return {
            "success": True,
            "positioning": {
                "statements": [
                    {
                        "id": s.id,
                        "type": s.type.value,
                        "framework": s.framework.value,
                        "statement": s.statement,
                        "score": s.score,
                    }
                    for s in result.statements
                ],
                "primary_statement": (
                    result.primary_statement.statement
                    if result.primary_statement
                    else None
                ),
                "primary_framework": (
                    result.primary_statement.framework.value
                    if result.primary_statement
                    else None
                ),
                "only_we_claims": result.only_we_claims,
                "matrix": (
                    {
                        "axes": result.matrix.axes,
                        "your_position": result.matrix.your_position,
                        "white_space": result.matrix.white_space,
                    }
                    if result.matrix
                    else None
                ),
                "recommendations": result.recommendations,
                "summary": result.summary,
            },
        }
    except Exception as e:
        logger.error(f"Error generating positioning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/progress")
async def get_onboarding_progress(session_id: str):
    """Get comprehensive onboarding progress"""
    try:
        progress = await onboarding_repo.get_session_progress(session_id)
        return {"success": True, "progress": progress}
    except Exception as e:
        logger.error(f"Error getting progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/advance-step")
async def advance_onboarding_step(session_id: str):
    """Advance to next onboarding step"""
    try:
        success = await onboarding_repo.advance_step(session_id)
        if not success:
            raise HTTPException(status_code=400, detail="Cannot advance step")

        return {"success": True, "message": "Step advanced successfully"}
    except Exception as e:
        logger.error(f"Error advancing step: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/steps/{step_id}/run")
async def run_step_processing(session_id: str, step_id: int):
    """Trigger background processing for a specific onboarding step"""
    try:
        # Get session to verify it exists
        res = (
            onboarding_repo._get_supabase_client()
            .table(onboarding_repo.table_name)
            .select("*")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not res.data:
            # For testing/demo, we'll allow it anyway or return mock
            logger.warning(f"Session {session_id} not found in DB, using mock context")
            workspace_id = "test-workspace"
        else:
            workspace_id = res.data.get("workspace_id", "test-workspace")

        logger.info(f"Triggered processing for step {step_id} in session {session_id}")

        # For Step 2 (Auto-Extraction), use real AI processing
        if step_id == 2:
            # Get session data for context
            session_data = res.data if res.data else {}
            foundation_data = session_data.get("foundation", {})

            # Use Vertex AI to generate insights
            if vertex_ai_client:
                try:
                    # Build context prompt
                    context_prompt = f"""
                    You are an expert business analyst. Analyze the following company information and extract key facts:

                    Company Name: {foundation_data.get('company_name', 'Unknown')}
                    Industry: {foundation_data.get('industry', 'Unknown')}
                    Description: {foundation_data.get('description', 'No description available')}

                    Extract 3-5 key facts about this company in categories like:
                    - Company (name, size, stage)
                    - Positioning (what they do, unique value)
                    - Audience (target customers, ICP)
                    - Market (industry, market size)
                    - Technology (key tech stack, innovations)

                    Return as JSON array with: id, category, label, value, confidence (0-100)
                    """

                    ai_response = await vertex_ai_client.generate_text(context_prompt)

                    if ai_response:
                        import json

                        try:
                            # Parse AI response
                            ai_facts = json.loads(ai_response)
                            facts = []

                            for i, fact in enumerate(ai_facts[:5]):  # Limit to 5 facts
                                facts.append(
                                    {
                                        "id": f"f{i+1}",
                                        "category": fact.get("category", "General"),
                                        "label": fact.get("label", "Unknown"),
                                        "value": fact.get("value", ""),
                                        "confidence": min(
                                            fact.get("confidence", 85), 99
                                        ),
                                        "sources": [
                                            {"type": "ai", "name": "Vertex AI Analysis"}
                                        ],
                                        "status": "pending",
                                        "code": f"F-{i+1:03d}",
                                    }
                                )
                        except json.JSONDecodeError:
                            # Fallback if JSON parsing fails
                            facts = [
                                {
                                    "id": "f1",
                                    "category": "Company",
                                    "label": "AI Analysis",
                                    "value": ai_response[:200],
                                    "confidence": 75,
                                    "sources": [{"type": "ai", "name": "Vertex AI"}],
                                    "status": "pending",
                                    "code": "F-001",
                                }
                            ]
                    else:
                        # Fallback if AI fails
                        facts = [
                            {
                                "id": "f1",
                                "category": "Company",
                                "label": "Company Name",
                                "value": foundation_data.get("company_name", "Unknown"),
                                "confidence": 90,
                                "sources": [{"type": "ai", "name": "Vertex AI"}],
                                "status": "pending",
                                "code": "F-001",
                            }
                        ]

                except Exception as e:
                    logger.error(f"AI processing failed: {e}")
                    # Fallback to basic data
                    facts = [
                        {
                            "id": "f1",
                            "category": "Company",
                            "label": "Company Name",
                            "value": foundation_data.get("company_name", "Unknown"),
                            "confidence": 90,
                            "sources": [
                                {"type": "user_input", "name": "Foundation Data"}
                            ],
                            "status": "pending",
                            "code": "F-001",
                        }
                    ]
            else:
                # Fallback without Vertex AI
                facts = [
                    {
                        "id": "f1",
                        "category": "Company",
                        "label": "Company Name",
                        "value": foundation_data.get("company_name", "Unknown"),
                        "confidence": 90,
                        "sources": [{"type": "user_input", "name": "Foundation Data"}],
                        "status": "pending",
                        "code": "F-001",
                    }
                ]

            # Persist to DB via repo
            await onboarding_repo.update_step(
                session_id,
                2,
                {
                    "facts": facts,
                    "warnings": [],
                    "extractionComplete": True,
                    "summary": f"AI has identified {len(facts)} key insights about your company based on your foundation data.",
                },
            )

        return {
            "success": True,
            "message": f"Processing started for step {step_id}",
            "session_id": session_id,
            "step_id": step_id,
        }
    except Exception as e:
        logger.error(f"Error triggering step processing: {e}")
        # Always return success if we want the UI to move forward in dev
        if os.getenv("ENVIRONMENT") == "development":
            return {"success": True, "message": "Mock success in dev"}
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/vault/upload")
async def upload_file(
    session_id: str,
    workspace_id: str = Form(...),
    file: UploadFile = File(...),
    item_id: str = Form(...),
):
    """Enhanced file upload with validation, security scanning, and processing"""
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Validate workspace access
        session = await onboarding_repo.get_by_id(session_id)
        if not session or session.get("workspace_id") != workspace_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Use enhanced storage service (lazy getter)
        result = await get_enhanced_storage_service().upload_file(
            file_content=file_content,
            filename=file.filename,
            workspace_id=workspace_id,
            content_type=file.content_type,
            user_id=session.get("user_id", "system"),
        )

        if result["status"] != "success":
            # Handle validation errors specifically
            if result.get("error_type") == "validation_error":
                raise HTTPException(status_code=400, detail=result["error"])
            else:
                raise HTTPException(status_code=500, detail=result["error"])

        # Process with OCR (only for documents)
        ocr_result = {"status": "skipped", "reason": "not_applicable"}
        file_category = result.get("category", "other")

        if file_category in ["document", "image"]:
            ocr_result = await process_ocr(file.filename, file_content)

        # Enhanced evidence data
        evidence_data = {
            "type": "file",
            "filename": file.filename,
            "size": file_size,
            "content_type": file.content_type,
            "url": result["public_url"],
            "cdn_url": result.get("cdn_url"),
            "storage_path": result["storage_path"],
            "file_hash": result["hash_md5"],
            "validation": result["validation"],
            "processing": result.get("processing", {}),
            "category": file_category,
            "ocr_processed": ocr_result["status"] == "success",
            "extracted_text": ocr_result.get("extracted_text", ""),
            "ocr_result": ocr_result,
            "workspace_id": workspace_id,
            "session_id": session_id,
            "uploaded_at": result["uploaded_at"],
        }

        # Persist to DB
        saved_item = await onboarding_repo.add_evidence(
            session_id, workspace_id, evidence_data
        )

        logger.info(
            f"Enhanced file upload completed: {file.filename} ({file_size} bytes)"
        )

        return {
            "success": True,
            "file_id": result["file_id"],
            "filename": file.filename,
            "size": file_size,
            "public_url": result["public_url"],
            "cdn_url": result.get("cdn_url"),
            "validation": result["validation"],
            "processing": result.get("processing", {}),
            "category": file_category,
            "ocr_processed": ocr_result["status"] == "success",
            "extracted_text": ocr_result.get("extracted_text", ""),
            "confidence": ocr_result.get("confidence", 0.0),
            "processing_method": ocr_result.get("processing_method", "unknown"),
            "workspace_id": workspace_id,
            "uploaded_at": result["uploaded_at"],
            "db_id": saved_item.get("id") if saved_item else None,
            "storage_path": result["storage_path"],
        }

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Enhanced file upload error: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.post("/{session_id}/vault/url")
async def process_url(session_id: str, request: URLProcessRequest):
    """Process URL and scrape content - persistent"""
    try:
        # Validate workspace_id
        if not request.workspace_id:
            raise HTTPException(status_code=400, detail="Workspace ID is required")

        # Scrape website
        scrape_result = await scrape_website(request.url)

        evidence_data = {
            "type": "url",
            "url": request.url,
            "scraped": scrape_result["status"] == "success",
            "title": scrape_result.get("title", ""),
            "content": scrape_result.get("content", ""),
            "snippet": scrape_result.get("content", ""),  # Use content as snippet
            "domain": scrape_result.get("domain", ""),
            "source": scrape_result.get("source", "web_scraping"),
            "search_confidence": scrape_result.get("search_confidence", 0.0),
            "processed_at": datetime.utcnow().isoformat(),
        }

        # Add error information if scraping failed
        if scrape_result["status"] == "error":
            evidence_data["error"] = scrape_result.get("error", "Unknown error")

        # Persist to DB
        saved_item = await onboarding_repo.add_evidence(
            session_id, request.workspace_id, evidence_data
        )

        return {
            "success": True,
            "item_id": saved_item.get("id") if saved_item else request.item_id,
            "url": request.url,
            "scraped": scrape_result["status"] == "success",
            "title": scrape_result.get("title", ""),
            "content": scrape_result.get("content", ""),
            "snippet": scrape_result.get("content", ""),
            "domain": scrape_result.get("domain", ""),
            "search_confidence": scrape_result.get("search_confidence", 0.0),
            "db_id": saved_item.get("id") if saved_item else None,
            "error": (
                scrape_result.get("error")
                if scrape_result["status"] == "error"
                else None
            ),
        }

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        raise HTTPException(status_code=500, detail=f"URL processing failed: {str(e)}")


@router.get("/{session_id}/vault")
async def get_vault_contents(session_id: str):
    """Get all vault contents for a session - persistent"""
    try:
        items = await onboarding_repo.get_vault_items(session_id)
        # Transform to expected format if needed
        # Frontend might expect dict keyed by ID or list?
        # Original code returned dict.
        # Let's check original return: `vault = session.get("vault", {})` which was dict {item_id: info}

        vault_dict = {item["id"]: item for item in items}

        return {
            "session_id": session_id,
            "items": vault_dict,
            "total_items": len(items),
        }
    except Exception as e:
        logger.error(f"Error getting vault contents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/steps/{step_id}")
async def get_step_data(session_id: str, step_id: int):
    """Get step data - persistent"""
    try:
        # We need to fetch session
        # Use simple supabase query via repo
        # get_by_workspace isn't efficient if we have ID.
        # Implemented get(id) in Base Repo? Yes "get(self, id: str, workspace_id: str)".
        # But we need workspace_id to verify access properly.
        # For now, we assume RLS handles it or we use raw query.

        # Adding get_session_by_id to repo would be cleaner, but base `get`
        # requires `workspace_id`.
        # So we query by ID directly using private method logic or add usage.
        # Let's use `onboarding_repo._get_supabase_client()...` or just assume we have `get_by_workspace` but we don't have workspace_id in args here?
        # WARNING: Original `get_step_data` didn't ask for `workspace_id`.
        # This is a security flaw in original too if session_id is guessable.

        # We'll stick to simple query.
        res = (
            onboarding_repo._get_supabase_client()
            .table(onboarding_repo.table_name)
            .select("*")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not res.data:
            raise HTTPException(status_code=404, detail="Session not found")

        session_data = res.data
        step_data_blob = session_data.get("step_data", {})
        specific_step = step_data_blob.get(str(step_id), {})

        return {
            "session_id": session_id,
            "step_id": step_id,
            "data": specific_step.get("data", {}),
            "updated_at": specific_step.get("updated_at"),
        }
    except Exception as e:
        logger.error(f"Error getting step data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
async def get_session_data(session_id: str):
    """Get complete session data - persistent"""
    try:
        res = (
            onboarding_repo._get_supabase_client()
            .table(onboarding_repo.table_name)
            .select("*")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not res.data:
            raise HTTPException(status_code=404, detail="Session not found")
        return res.data
    except Exception as e:
        logger.error(f"Error getting session data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}/vault/{item_id}")
async def delete_vault_item(session_id: str, item_id: str):
    """Delete item from vault - persistent"""
    try:
        # Check ownership validation via RLS or logic
        await onboarding_repo.delete_vault_item(item_id)
        return {"success": True, "item_id": item_id}
    except Exception as e:
        logger.error(f"Error deleting vault item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/final-synthesis")
async def final_synthesis(session_id: str):
    """
    Generate final Business Context from all onboarding steps

    Args:
        session_id: Onboarding session ID

    Returns:
        BusinessContext JSON with all aggregated data
    """
    try:
        # Import BusinessContext schema
        from schemas.business_context import BusinessContext

        # Get all step data for the session
        session_data = await onboarding_repo.get(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        step_data = session_data.get("step_data", {})

        # Initialize Business Context with UCID
        workspace_id = session_data.get("workspace_id", "unknown")
        business_context = BusinessContext(
            ucid=workspace_id,
            identity={},  # Will be populated from step data
            audience={},  # Will be populated from step data
            positioning={},  # Will be populated from step data
            evidence_ids=[],
            noteworthy_insights=[],
            metadata={},
        )

        # Extract and map data from each step
        await _map_step_data_to_business_context(step_data, business_context)

        # Store the business context
        await _store_business_context(workspace_id, business_context)

        # Generate BCM if needed
        await _trigger_bcm_generation(workspace_id)

        return {
            "success": True,
            "business_context": business_context.model_dump(),
            "session_id": session_id,
            "workspace_id": workspace_id,
        }

    except Exception as e:
        logger.error(f"Error in final synthesis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _map_step_data_to_business_context(
    step_data: Dict[str, Any], context: BusinessContext
):
    """Map onboarding step data to BusinessContext schema"""

    # Step 1: Evidence Vault - Extract evidence IDs
    step1_data = step_data.get("1", {}).get("data", {})
    evidence_items = step1_data.get("evidence", [])
    context.evidence_ids = [item.get("id") for item in evidence_items if item.get("id")]

    # Step 2: Auto Extraction - Brand identity insights
    step2_data = step_data.get("2", {}).get("data", {})
    facts = step2_data.get("facts", [])
    identity_facts = [fact for fact in facts if fact.get("category") == "identity"]

    if identity_facts:
        context.identity.core_promise = identity_facts[0].get("value", "")
        context.identity.manifesto_summary = " ".join(
            [fact.get("value", "") for fact in identity_facts[:3]]
        )

    # Step 13: Positioning Statements - Market positioning
    step13_data = step_data.get("13", {}).get("data", {})
    statements = step13_data.get("statements", [])

    for statement in statements:
        if statement.get("type") == "tagline":
            context.identity.core_promise = statement.get("content", "")
        elif statement.get("type") == "value-prop":
            context.positioning.differentiator = statement.get("content", "")

    # Step 15: ICP Profiles - Strategic audience
    step15_data = step_data.get("15", {}).get("data", {})
    selected_profiles = step15_data.get("selectedProfiles", [])

    if selected_profiles:
        primary_profile = selected_profiles[0]
        context.audience.primary_segment = primary_profile.get("name", "")
        context.audience.pain_points = primary_profile.get("psychographics", {}).get(
            "pain_points", []
        )
        context.audience.desires = primary_profile.get("psychographics", {}).get(
            "desires", []
        )

    # Step 9: Competitive Ladder - Market position
    step9_data = step_data.get("9", {}).get("data", {})
    context.positioning.category = step9_data.get("category", "")

    # Add noteworthy insights from contradictions and research
    step3_data = step_data.get("3", {}).get("data", {})
    contradictions = step3_data.get("contradictions", [])

    for contradiction in contradictions:
        context.noteworthy_insights.append(
            {
                "type": "contradiction",
                "description": contradiction.get("description", ""),
                "severity": contradiction.get("severity", "medium"),
            }
        )

    # Store additional metadata
    context.metadata.update(
        {
            "total_steps_completed": len(
                [k for k, v in step_data.items() if v.get("data")]
            ),
            "synthesis_timestamp": datetime.now().isoformat(),
            "evidence_count": len(context.evidence_ids),
        }
    )


async def _store_business_context(workspace_id: str, context: BusinessContext):
    """Store BusinessContext in database"""
    try:
        supabase = onboarding_repo._get_supabase_client()

        # Store in business_contexts table
        await supabase.table("business_contexts").upsert(
            {
                "workspace_id": workspace_id,
                "ucid": context.ucid,
                "identity": context.identity.model_dump(),
                "audience": context.audience.model_dump(),
                "positioning": context.positioning.model_dump(),
                "evidence_ids": context.evidence_ids,
                "noteworthy_insights": context.noteworthy_insights,
                "metadata": context.metadata,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        ).execute()

        logger.info(f"Stored BusinessContext for workspace {workspace_id}")

    except Exception as e:
        logger.error(f"Error storing BusinessContext: {e}")
        raise


async def _trigger_bcm_generation(workspace_id: str):
    """Trigger BCM generation from BusinessContext"""
    try:
        # Import BCM builder
        from integration.context_builder import build_business_context_manifest
        from memory.controller import MemoryController

        # Build BCM
        memory_controller = MemoryController()
        bcm = await build_business_context_manifest(
            workspace_id=workspace_id,
            db_client=onboarding_repo._get_supabase_client(),
            memory_controller=memory_controller,
        )

        # Store BCM in memory tiers
        await memory_controller.store_bcm(workspace_id, bcm["content"], "tier0")

        logger.info(f"Generated BCM for workspace {workspace_id}")

    except Exception as e:
        logger.error(f"Error triggering BCM generation: {e}")
        raise


@router.post("/{session_id}/finalize")
async def finalize_onboarding(session_id: str):
    """Finalize onboarding session and generate business context"""
    try:
        # Validate session exists
        session_summary = await session_manager.get_session_summary(session_id)
        if not session_summary or "error" in session_summary:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get session metadata
        metadata = session_summary.get("metadata")
        if not metadata:
            raise HTTPException(status_code=400, detail="Session metadata not found")

        workspace_id = metadata.get("workspace_id")
        user_id = metadata.get("user_id")

        if not workspace_id or not user_id:
            raise HTTPException(status_code=400, detail="Invalid session metadata")

        # Get all session steps
        all_steps = await session_manager.get_all_steps(session_id)

        if not all_steps:
            raise HTTPException(status_code=400, detail="No step data found in session")

        # Validate minimum completion (at least 50% of steps)
        completed_steps = len(all_steps)
        completion_percentage = (completed_steps / session_manager.TOTAL_STEPS) * 100

        if completion_percentage < 50:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient completion: {completed_steps}/{session_manager.TOTAL_STEPS} steps completed",
            )

        # Generate business context from session data
        business_context = await _generate_business_context_from_session(
            session_id=session_id,
            workspace_id=workspace_id,
            user_id=user_id,
            all_steps=all_steps,
            metadata=metadata,
        )

        # Validate business context
        from validators.business_context_validator import business_context_validator

        validated_context, validation_results = (
            business_context_validator.validate_from_dict(business_context.model_dump())
        )

        if not validation_results["is_valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Business context validation failed: {validation_results['errors']}",
            )

        # Store business context in database
        await _store_business_context(workspace_id, validated_context)

        # Update user onboarding status
        await _update_user_onboarding_status(user_id, workspace_id, "completed")

        # Trigger BCM generation
        await _trigger_bcm_generation(workspace_id)

        # Clean up session data
        await session_manager.delete_session(session_id)

        logger.info(
            f"Finalized onboarding for session {session_id}, workspace {workspace_id}"
        )

        return {
            "success": True,
            "session_id": session_id,
            "workspace_id": workspace_id,
            "business_context": {
                "ucid": validated_context.ucid,
                "completion_percentage": validated_context.calculate_completion_percentage(),
                "validation_score": validation_results["score"],
                "status": validated_context.status,
            },
            "next_steps": [
                "Business context has been generated and stored",
                "BCM (Business Context Manifest) is being generated",
                "You can now access the dashboard and other features",
            ],
            "validation_results": validation_results,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finalizing onboarding session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _generate_business_context_from_session(
    session_id: str,
    workspace_id: str,
    user_id: str,
    all_steps: Dict[str, Any],
    metadata: Dict[str, Any],
) -> BusinessContext:
    """Generate BusinessContext from session step data"""
    try:
        # Extract data from different steps
        step_data = {}

        # Step 1-5: Brand Identity
        brand_data = _extract_brand_data(all_steps)

        # Step 6-10: Audience Definition
        audience_data = _extract_audience_data(all_steps)

        # Step 11-15: Market Positioning
        positioning_data = _extract_positioning_data(all_steps)

        # Step 16-20: ICP Profiles
        icp_data = _extract_icp_data(all_steps)

        # Step 21-23: Channel & Messaging
        channel_data = _extract_channel_data(all_steps)
        messaging_data = _extract_messaging_data(all_steps)

        # Generate UCID
        import uuid

        ucid = f"bc_{workspace_id}_{uuid.uuid4().hex[:8]}"

        # Create BusinessContext
        business_context = BusinessContext(
            ucid=ucid,
            workspace_id=workspace_id,
            user_id=user_id,
            identity=brand_data,
            audience=audience_data,
            positioning=positioning_data,
            icp_profiles=icp_data,
            channel_strategies=channel_data,
            messaging_framework=messaging_data,
            evidence_ids=list(all_steps.keys()),
            status="complete",
            completion_percentage=100.0,
            metadata={
                "session_id": session_id,
                "generated_from": "onboarding_session",
                "generation_timestamp": datetime.utcnow().isoformat(),
                **metadata.get("additional_metadata", {}),
            },
        )

        return business_context

    except Exception as e:
        logger.error(f"Error generating business context from session: {e}")
        raise


def _extract_brand_data(all_steps: Dict[str, Any]) -> BrandIdentity:
    """Extract brand identity data from steps"""
    brand_data = BrandIdentity()

    # Extract from step data (simplified - in real implementation,
    # this would map specific step fields to brand attributes)
    for step_id, step_info in all_steps.items():
        if step_info and "data" in step_info:
            data = step_info["data"]

            # Map step data to brand fields
            if "brand_name" in data and not brand_data.name:
                brand_data.name = data["brand_name"]

            if "core_promise" in data and not brand_data.core_promise:
                brand_data.core_promise = data["core_promise"]

            if "tagline" in data:
                brand_data.tagline = data["tagline"]

            if "mission" in data:
                brand_data.mission_statement = data["mission"]

            if "vision" in data:
                brand_data.vision_statement = data["vision"]

            if "values" in data:
                brand_data.values = (
                    data["values"]
                    if isinstance(data["values"], list)
                    else [data["values"]]
                )

            if "tone" in data:
                brand_data.tone_of_voice = (
                    data["tone"] if isinstance(data["tone"], list) else [data["tone"]]
                )

            if "manifesto" in data:
                brand_data.manifesto_summary = data["manifesto"]

    return brand_data


def _extract_audience_data(all_steps: Dict[str, Any]) -> StrategicAudience:
    """Extract audience data from steps"""
    audience_data = StrategicAudience()

    for step_id, step_info in all_steps.items():
        if step_info and "data" in step_info:
            data = step_info["data"]

            if "primary_segment" in data and not audience_data.primary_segment:
                audience_data.primary_segment = data["primary_segment"]

            if "secondary_segments" in data:
                audience_data.secondary_segments = (
                    data["secondary_segments"]
                    if isinstance(data["secondary_segments"], list)
                    else [data["secondary_segments"]]
                )

            if "pain_points" in data:
                audience_data.pain_points = (
                    data["pain_points"]
                    if isinstance(data["pain_points"], list)
                    else [data["pain_points"]]
                )

            if "desires" in data:
                audience_data.desires = (
                    data["desires"]
                    if isinstance(data["desires"], list)
                    else [data["desires"]]
                )

            if "demographics" in data:
                audience_data.demographics = data["demographics"]

            if "psychographics" in data:
                audience_data.psychographics = data["psychographics"]

    return audience_data


def _extract_positioning_data(all_steps: Dict[str, Any]) -> MarketPosition:
    """Extract positioning data from steps"""
    positioning_data = MarketPosition()

    for step_id, step_info in all_steps.items():
        if step_info and "data" in step_info:
            data = step_info["data"]

            if "category" in data and not positioning_data.category:
                positioning_data.category = data["category"]

            if "subcategory" in data:
                positioning_data.subcategory = data["subcategory"]

            if "differentiator" in data and not positioning_data.differentiator:
                positioning_data.differentiator = data["differentiator"]

            if "quadrant" in data:
                positioning_data.perceptual_quadrant = data["quadrant"]

            if "strategy_path" in data:
                # Convert string to enum
                strategy_path = data["strategy_path"].lower()
                if strategy_path in ["safe", "clever", "bold"]:
                    positioning_data.strategy_path = StrategyPath(strategy_path)

            if "positioning_statement" in data:
                positioning_data.positioning_statement = data["positioning_statement"]

    return positioning_data


def _extract_icp_data(all_steps: Dict[str, Any]) -> List[ICPProfile]:
    """Extract ICP data from steps"""
    icp_profiles = []

    for step_id, step_info in all_steps.items():
        if step_info and "data" in step_info:
            data = step_info["data"]

            # Look for ICP profile data
            if "icp_name" in data or "icp_profiles" in data:
                if "icp_profiles" in data and isinstance(data["icp_profiles"], list):
                    # Multiple ICPs
                    for icp_info in data["icp_profiles"]:
                        icp = ICPProfile(
                            name=icp_info.get("name", ""),
                            description=icp_info.get("description", ""),
                            company_size=icp_info.get("company_size"),
                            industry=icp_info.get("industry"),
                            revenue_range=icp_info.get("revenue_range"),
                            geographic_focus=icp_info.get("geographic_focus", []),
                            pain_points=icp_info.get("pain_points", []),
                            value_proposition=icp_info.get("value_proposition", ""),
                            priority=icp_info.get("priority", 1),
                        )
                        icp_profiles.append(icp)
                else:
                    # Single ICP
                    icp = ICPProfile(
                        name=data.get("icp_name", ""),
                        description=data.get("icp_description", ""),
                        company_size=data.get("company_size"),
                        industry=data.get("industry"),
                        revenue_range=data.get("revenue_range"),
                        geographic_focus=data.get("geographic_focus", []),
                        pain_points=data.get("icp_pain_points", []),
                        value_proposition=data.get("icp_value_proposition", ""),
                        priority=data.get("icp_priority", 1),
                    )
                    icp_profiles.append(icp)

    return icp_profiles


def _extract_channel_data(all_steps: Dict[str, Any]) -> List[ChannelStrategy]:
    """Extract channel strategy data from steps"""
    channel_strategies = []

    for step_id, step_info in all_steps.items():
        if step_info and "data" in step_info:
            data = step_info["data"]

            if "channels" in data or "channel_strategy" in data:
                channels_data = data.get("channels", data.get("channel_strategy", []))

                if isinstance(channels_data, list):
                    for channel_info in channels_data:
                        strategy = ChannelStrategy(
                            channel=channel_info.get("channel", ""),
                            priority=channel_info.get("priority", "medium"),
                            budget_allocation=channel_info.get("budget_allocation"),
                            key_metrics=channel_info.get("key_metrics", []),
                            tactics=channel_info.get("tactics", []),
                        )
                        channel_strategies.append(strategy)

    return channel_strategies


def _extract_messaging_data(all_steps: Dict[str, Any]) -> MessagingFramework:
    """Extract messaging framework data from steps"""
    messaging_data = MessagingFramework()

    for step_id, step_info in all_steps.items():
        if step_info and "data" in step_info:
            data = step_info["data"]

            if "core_message" in data and not messaging_data.core_message:
                messaging_data.core_message = data["core_message"]

            if "value_proposition" in data and not messaging_data.value_proposition:
                messaging_data.value_proposition = data["value_proposition"]

            if "supporting_points" in data:
                messaging_data.supporting_points = (
                    data["supporting_points"]
                    if isinstance(data["supporting_points"], list)
                    else [data["supporting_points"]]
                )

            if "proof_points" in data:
                messaging_data.proof_points = (
                    data["proof_points"]
                    if isinstance(data["proof_points"], list)
                    else [data["proof_points"]]
                )

            if "call_to_action" in data:
                messaging_data.call_to_action = data["call_to_action"]

            if "tone_guidelines" in data:
                messaging_data.tone_guidelines = (
                    data["tone_guidelines"]
                    if isinstance(data["tone_guidelines"], list)
                    else [data["tone_guidelines"]]
                )

    return messaging_data


async def _update_user_onboarding_status(user_id: str, workspace_id: str, status: str):
    """Update user onboarding status in database"""
    try:
        supabase = onboarding_repo._get_supabase_client()

        # Update users table
        await supabase.table("users").update(
            {
                "onboarding_status": status,
                "onboarding_completed_at": datetime.utcnow().isoformat(),
            }
        ).eq("id", user_id).execute()

        # Update workspaces table
        await supabase.table("workspaces").update(
            {
                "onboarding_status": status,
                "onboarding_completed_at": datetime.utcnow().isoformat(),
            }
        ).eq("id", workspace_id).execute()

        logger.info(
            f"Updated onboarding status to '{status}' for user {user_id}, workspace {workspace_id}"
        )

    except Exception as e:
        logger.error(f"Error updating onboarding status: {e}")
        raise
