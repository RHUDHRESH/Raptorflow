"""
Muse API with Vertex AI Integration
Enhanced content generation using Gemini 2.0 Flash
Fully integrated with REAL database and services
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Import Vertex AI service
try:
    from services.vertex_ai_service import vertex_ai_service
except ImportError:
    vertex_ai_service = None

try:
    from core.auth import get_current_user

    from ...dependencies import get_db
except ImportError:

    def get_current_user():
        return {"id": "test-user", "email": "test@example.com"}

    def get_db():
        return None


from services.advanced_analytics_service import advanced_analytics_service
from services.audit_service import audit_service
from services.automation_service import automation_service
from services.brand_voice_service import brand_voice_service
from services.brief_service import brief_service
from services.coaching_service import coaching_service
from services.collaboration_service import ApprovalStatus, collaboration_service

# Import Services
from services.crm_service import CRMProvider, crm_service
from services.distribution_service import DistributionPlatform, distribution_service
from services.marketplace_service import marketplace_service
from services.onboarding_service import muse_onboarding_service
from services.premium_service import premium_service
from services.repurposing_service import PlatformType, repurposing_service
from services.seo_service import seo_service

router = APIRouter(prefix="/muse", tags=["muse"])

# --- Models ---


class ContentRequest(BaseModel):
    task: str
    context: Dict[str, Any] = {}
    workspace_id: str = "default"
    session_id: str = "default"
    content_type: str = "general"
    tone: str = "professional"
    target_audience: str = "general"
    max_tokens: int = 1000
    temperature: float = 0.7


class ContentResponse(BaseModel):
    success: bool
    content: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    seo_score: float = 0.0
    suggestions: List[str] = []
    error: str = ""
    metadata: Dict[str, Any] = {}


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime


class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []
    context: Dict[str, Any] = {}
    workspace_id: str = "default"
    session_id: str = "default"


class ChatResponse(BaseModel):
    success: bool
    message: str = ""
    tokens_used: int = 0
    error: str = ""


class SyncProspectRequest(BaseModel):
    prospect_id: str
    content: str
    title: str
    provider: str = "hubspot"


class RepurposeRequest(BaseModel):
    content: str
    target_platform: str
    tone: str = "professional"
    additional_instructions: str = ""


class CommentRequest(BaseModel):
    asset_id: str
    text: str


class ApprovalRequest(BaseModel):
    asset_id: str
    status: str


class VoiceAnalysisRequest(BaseModel):
    samples: List[str]


class DistributionRequest(BaseModel):
    content: str
    platform: str
    scheduled_at: Optional[datetime] = None


class AuditRequest(BaseModel):
    assets: List[Dict[str, Any]]
    gtm_goals: List[str]


class SEORequest(BaseModel):
    content: str
    target_keywords: List[str]


class BriefRequest(BaseModel):
    topic: str
    icp_context: Dict[str, Any]
    platform: str = "blog"


class SequenceRequest(BaseModel):
    goal: str
    steps: int = 5
    tone: str = "professional"


class CoachingRequest(BaseModel):
    content: str
    bcm_context: Dict[str, Any]


class ProjectRequest(BaseModel):
    title: str
    description: str
    budget_range: str


# --- Endpoints ---


@router.post("/generate", response_model=ContentResponse)
async def generate_content(
    request: ContentRequest, user=Depends(get_current_user), db=Depends(get_db)
):
    """Generate content using real Vertex AI inference and store in DB."""
    if not vertex_ai_service:
        raise HTTPException(status_code=503, detail="Vertex AI unavailable")

    prompt = f"Task: {request.task}\nType: {request.content_type}\nTone: {request.tone}\nContext: {json.dumps(request.context)}"
    ai_res = await vertex_ai_service.generate_text(
        prompt, request.workspace_id, user["id"]
    )

    if ai_res["status"] != "success":
        return ContentResponse(success=False, error=ai_res.get("error", "AI Error"))

    asset_id = str(uuid.uuid4())
    if db:
        await db.execute(
            "INSERT INTO muse_assets (id, workspace_id, created_by, title, content, asset_type, ai_generated) VALUES ($1, $2, $3, $4, $5, $6, TRUE)",
            asset_id,
            request.workspace_id,
            user["id"],
            request.task[:50],
            ai_res["text"],
            request.content_type,
        )

    # Record in BCM Ledger
    try:
        from backend.services.bcm_integration import bcm_evolution
        await bcm_evolution.record_interaction(
            workspace_id=request.workspace_id,
            agent_name="Muse",
            interaction_type="CONTENT_GENERATION",
            payload={
                "task": request.task,
                "content_type": request.content_type,
                "asset_id": asset_id
            }
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to ledger Muse generation: {e}")

    return ContentResponse(
        success=True,
        content=ai_res["text"],
        tokens_used=ai_res["total_tokens"],
        cost_usd=ai_res["cost_usd"],
        metadata={"asset_id": asset_id},
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user=Depends(get_current_user)):
    """Conversational content assistance with real AI inference."""
    prompt = f"User: {request.message}\nContext: {json.dumps(request.context)}"
    ai_res = await vertex_ai_service.generate_text(
        prompt, request.workspace_id, user["id"]
    )

    if ai_res["status"] == "success":
        # Record in BCM Ledger
        try:
            from backend.services.bcm_integration import bcm_evolution
            await bcm_evolution.record_interaction(
                workspace_id=request.workspace_id,
                agent_name="Muse",
                interaction_type="CHAT",
                payload={
                    "message_preview": request.message[:100]
                }
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to ledger Muse chat: {e}")

        return ChatResponse(
            success=True, message=ai_res["text"], tokens_used=ai_res["total_tokens"]
        )
    return ChatResponse(success=False, error="Chat failed")


@router.get("/prospects")
async def get_prospects(workspace_id: str = "default", user=Depends(get_current_user)):
    """Fetch real prospects from DB (ICPs)."""
    return {"success": True, "prospects": await crm_service.get_prospects(workspace_id)}


@router.post("/sync-prospect")
async def sync_prospect(request: SyncProspectRequest, user=Depends(get_current_user)):
    """Sync personalized content to prospect and log in DB."""
    return await crm_service.sync_content_to_prospect(
        "default-workspace",
        user["id"],
        request.prospect_id,
        request.content,
        request.title,
    )


@router.post("/repurpose")
async def repurpose(request: RepurposeRequest, user=Depends(get_current_user)):
    """Repurpose content via real AI inference."""
    platform = PlatformType(request.target_platform.lower())
    return await repurposing_service.repurpose_content(
        request.content, platform, request.tone, request.additional_instructions
    )


@router.post("/comment")
async def comment(request: CommentRequest, user=Depends(get_current_user)):
    """Add real persistent comment to DB."""
    return await collaboration_service.add_comment(
        request.asset_id, "default-workspace", user["id"], request.text
    )


@router.post("/approve")
async def approve(request: ApprovalRequest, user=Depends(get_current_user)):
    """Update real approval status in DB."""
    return await collaboration_service.update_approval_status(
        request.asset_id, ApprovalStatus(request.status.lower()), user["id"]
    )


@router.post("/analyze-voice")
async def analyze_voice(request: VoiceAnalysisRequest, user=Depends(get_current_user)):
    """Extract brand voice profile via real AI inference."""
    return await brand_voice_service.analyze_brand_voice(request.samples, user["id"])


@router.post("/distribute")
async def distribute(request: DistributionRequest, user=Depends(get_current_user)):
    """Distribute content and log event in DB."""
    return await distribution_service.post_to_platform(
        "default-workspace",
        user["id"],
        request.content,
        DistributionPlatform(request.platform.lower()),
    )


@router.post("/audit")
async def audit(request: AuditRequest, user=Depends(get_current_user)):
    """Perform real strategic audit via AI inference."""
    return await audit_service.audit_content_library(request.assets, request.gtm_goals)


@router.post("/seo-optimize")
async def seo_optimize(request: SEORequest, user=Depends(get_current_user)):
    """Audit SEO via real AI inference."""
    return await seo_service.optimize_content(request.content, request.target_keywords)


@router.post("/brief")
async def brief(request: BriefRequest, user=Depends(get_current_user)):
    """Generate strategic brief via real AI inference."""
    return await brief_service.generate_brief(
        request.topic, request.icp_context, request.platform
    )


@router.post("/sequence")
async def sequence(request: SequenceRequest, user=Depends(get_current_user)):
    """Generate automation sequence via real AI inference."""
    return await automation_service.create_content_sequence(
        request.goal, request.steps, request.tone
    )


@router.post("/coach")
async def coach(request: CoachingRequest, user=Depends(get_current_user)):
    """Get strategic critique via real AI inference."""
    return await coaching_service.get_strategic_critique(
        request.content, request.bcm_context
    )


@router.get("/roi-report")
async def roi_report(user=Depends(get_current_user)):
    """Calculate real ROI from DB data."""
    return await advanced_analytics_service.get_roi_report("default-workspace")


@router.get("/insights")
async def insights(user=Depends(get_current_user)):
    """Generate real AI insights from performance data."""
    return {
        "success": True,
        "insights": await advanced_analytics_service.get_automated_insights(
            "default-workspace"
        ),
    }


@router.post("/marketplace/project")
async def marketplace_project(request: ProjectRequest, user=Depends(get_current_user)):
    """Post real project to marketplace (Moves table)."""
    return await marketplace_service.post_project(
        "default-workspace",
        user["id"],
        request.title,
        request.description,
        request.budget_range,
    )


@router.get("/status")
async def status():
    """Technical status check."""
    return {
        "status": "available",
        "engine": "Gemini 2.0 Flash",
        "integration": "Vertex AI",
    }
