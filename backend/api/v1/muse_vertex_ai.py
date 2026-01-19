"""
Muse API with Vertex AI Integration
Enhanced content generation using Gemini 2.0 Flash
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

# Import Vertex AI service
try:
    from services.vertex_ai_service import vertex_ai_service
except ImportError:
    # Fallback for testing without full dependencies
    vertex_ai_service = None

try:
    from core.auth import get_current_user
    from ...dependencies import get_db
except ImportError:
    # Fallback for testing
    def get_current_user():
        return {"id": "test-user", "email": "test@example.com"}
    
    def get_db():
        return None

router = APIRouter(prefix="/muse", tags=["muse"])

class ContentRequest(BaseModel):
    """Request model for content generation"""
    task: str
    context: Dict[str, Any] = {}
    user_id: str
    workspace_id: str
    session_id: str = "default"
    content_type: str = "general"
    tone: str = "professional"
    target_audience: str = "general"
    max_tokens: int = 1000
    temperature: float = 0.7

class ContentResponse(BaseModel):
    """Response model for content generation"""
    success: bool
    content: str = ""
    task: str = ""
    content_type: str = ""
    tone: str = ""
    target_audience: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    generation_time_seconds: float = 0.0
    model_used: str = ""
    seo_score: float = 0.0
    suggestions: List[str] = []
    error: str = ""
    metadata: Dict[str, Any] = {}

class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    tokens_used: int = 0

class ChatRequest(BaseModel):
    """Request model for chat interaction"""
    message: str
    conversation_history: List[ChatMessage] = []
    context: Dict[str, Any] = {}
    user_id: str
    workspace_id: str
    session_id: str = "default"
    max_tokens: int = 1000
    temperature: float = 0.7

class ChatResponse(BaseModel):
    """Response model for chat interaction"""
    success: bool
    message: str = ""
    conversation_id: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    generation_time_seconds: float = 0.0
    model_used: str = ""
    suggestions: List[str] = []
    error: str = ""

def build_enhanced_prompt(request: ContentRequest) -> str:
    """Build an enhanced prompt with context and constraints"""
    
    base_prompt = f"""You are an expert content creator for Raptorflow, a marketing automation platform.

TASK: {request.task}

CONTENT TYPE: {request.content_type}
TONE: {request.tone}
TARGET AUDIENCE: {request.target_audience}

"""
    
    # Add context if provided
    if request.context:
        context_str = "\nCONTEXT:\n"
        for key, value in request.context.items():
            context_str += f"- {key}: {value}\n"
        base_prompt += context_str
    
    # Add constraints and guidelines
    base_prompt += f"""

GUIDELINES:
- Write in a {request.tone} tone
- Target the content for {request.target_audience}
- Keep it engaging and actionable
- Include relevant marketing insights where appropriate
- Maintain brand consistency with Raptorflow's values
- Optimize for clarity and readability

Please generate high-quality content that meets these requirements.
"""
    
    return base_prompt

def build_chat_prompt(request: ChatRequest, history: List[ChatMessage]) -> str:
    """Build a chat prompt with conversation history"""
    
    prompt = """You are Muse, an AI content creation assistant for Raptorflow marketing automation platform.

Your role is to help users create compelling marketing content, provide strategic insights, and offer creative solutions.

CONVERSATION HISTORY:
"""
    
    # Add conversation history
    for msg in history[-5:]:  # Last 5 messages for context
        prompt += f"\n{msg.role.upper()}: {msg.content}"
    
    prompt += f"\n\nUSER: {request.message}"
    
    # Add context if provided
    if request.context:
        prompt += f"\n\nADDITIONAL CONTEXT:"
        for key, value in request.context.items():
            prompt += f"\n- {key}: {value}"
    
    prompt += """

Please provide a helpful, insightful response that addresses the user's needs. Be conversational yet professional, and offer specific, actionable advice when relevant.
"""
    
    return prompt

@router.post("/generate", response_model=ContentResponse)
async def generate_content_with_vertex_ai(
    request: ContentRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Generate content using Vertex AI (Gemini 2.0 Flash)"""
    
    if not vertex_ai_service:
        return ContentResponse(
            success=False,
            error="Vertex AI service not available"
        )
    
    try:
        # Build enhanced prompt
        enhanced_prompt = build_enhanced_prompt(request)
        
        # Generate content using Vertex AI
        ai_response = await vertex_ai_service.generate_text(
            prompt=enhanced_prompt,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        if ai_response["status"] != "success":
            return ContentResponse(
                success=False,
                error=ai_response.get("error", "Unknown AI error"),
                task=request.task
            )
        
        # Store content in database (async background)
        content_id = str(uuid.uuid4())
        
        # Simple database insertion (you can enhance this)
        try:
            await db.execute(
                """
                INSERT INTO muse_assets (
                    id, workspace_id, user_id, content_type, topic, tone,
                    target_audience, content, draft_content, content_status,
                    tokens_used, cost_usd, model_used, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, NOW(), NOW())
                """,
                content_id,
                request.workspace_id,
                request.user_id,
                request.content_type,
                request.task,
                request.tone,
                request.target_audience,
                ai_response["text"],
                ai_response["text"],  # Store as both draft and final initially
                "generated",
                ai_response["total_tokens"],
                ai_response["cost_usd"],
                ai_response.get("model", "gemini-2.0-flash-exp"),
            )
        except Exception as db_error:
            # Log database error but don't fail the request
            print(f"Database error (non-blocking): {db_error}")
        
        # Calculate simple SEO score based on content
        seo_score = calculate_seo_score(ai_response["text"])
        suggestions = generate_content_suggestions(ai_response["text"], request.content_type)
        
        return ContentResponse(
            success=True,
            content=ai_response["text"],
            task=request.task,
            content_type=request.content_type,
            tone=request.tone,
            target_audience=request.target_audience,
            tokens_used=ai_response["total_tokens"],
            cost_usd=ai_response["cost_usd"],
            generation_time_seconds=ai_response["generation_time_seconds"],
            model_used=ai_response.get("model", "gemini-2.0-flash-exp"),
            seo_score=seo_score,
            suggestions=suggestions,
            metadata={
                "content_id": content_id,
                "session_id": request.session_id,
                "enhanced_prompt_length": len(enhanced_prompt)
            }
        )
        
    except Exception as e:
        return ContentResponse(
            success=False,
            error=f"Content generation failed: {str(e)}",
            task=request.task
        )

@router.post("/chat", response_model=ChatResponse)
async def chat_with_vertex_ai(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Chat with Vertex AI for conversational content assistance"""
    
    if not vertex_ai_service:
        return ChatResponse(
            success=False,
            error="Vertex AI service not available"
        )
    
    try:
        # Build chat prompt with history
        chat_prompt = build_chat_prompt(request, request.conversation_history)
        
        # Generate response using Vertex AI
        ai_response = await vertex_ai_service.generate_text(
            prompt=chat_prompt,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        if ai_response["status"] != "success":
            return ChatResponse(
                success=False,
                error=ai_response.get("error", "Unknown AI error")
            )
        
        # Generate conversation ID
        conversation_id = request.session_id or str(uuid.uuid4())
        
        # Store chat message in database
        try:
            await db.execute(
                """
                INSERT INTO muse_chat_messages (
                    id, conversation_id, workspace_id, user_id, role,
                    content, tokens_used, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                """,
                str(uuid.uuid4()),
                conversation_id,
                request.workspace_id,
                request.user_id,
                "user",
                request.message,
                0,  # User message tokens not tracked
            )
            
            # Store AI response
            await db.execute(
                """
                INSERT INTO muse_chat_messages (
                    id, conversation_id, workspace_id, user_id, role,
                    content, tokens_used, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                """,
                str(uuid.uuid4()),
                conversation_id,
                request.workspace_id,
                request.user_id,
                "assistant",
                ai_response["text"],
                ai_response["total_tokens"],
            )
        except Exception as db_error:
            print(f"Chat database error (non-blocking): {db_error}")
        
        # Generate suggestions based on conversation
        suggestions = generate_chat_suggestions(ai_response["text"], request.message)
        
        return ChatResponse(
            success=True,
            message=ai_response["text"],
            conversation_id=conversation_id,
            tokens_used=ai_response["total_tokens"],
            cost_usd=ai_response["cost_usd"],
            generation_time_seconds=ai_response["generation_time_seconds"],
            model_used=ai_response.get("model", "gemini-2.0-flash-exp"),
            suggestions=suggestions
        )
        
    except Exception as e:
        return ChatResponse(
            success=False,
            error=f"Chat failed: {str(e)}"
        )

@router.get("/status")
async def get_vertex_ai_status():
    """Get Vertex AI service status"""
    if not vertex_ai_service:
        return {
            "status": "unavailable",
            "error": "Vertex AI service not initialized"
        }
    
    return {
        "status": "available",
        "model": vertex_ai_service.model_name,
        "project_id": vertex_ai_service.project_id,
        "location": vertex_ai_service.location,
        "rate_limits": {
            "requests_per_minute": vertex_ai_service.requests_per_minute,
            "requests_per_hour": vertex_ai_service.requests_per_hour
        }
    }

# Helper functions
def calculate_seo_score(content: str) -> float:
    """Simple SEO score calculation"""
    score = 0.0
    content_lower = content.lower()
    
    # Check for SEO elements
    if len(content) > 300:
        score += 0.2  # Good length
    if any(word in content_lower for word in ["how", "what", "why", "when", "where"]):
        score += 0.1  # Question words
    if any(word in content_lower for word in ["step", "guide", "tutorial", "tips"]):
        score += 0.2  # Action-oriented
    if any(word in content_lower for word in ["marketing", "business", "customer", "audience"]):
        score += 0.2  # Business relevance
    if len(content.split()) > 50:
        score += 0.1  # Good word count
    if any(char in content for char in ["!", "?", "."]):
        score += 0.1  # Proper punctuation
    
    return min(score, 1.0)

def generate_content_suggestions(content: str, content_type: str) -> List[str]:
    """Generate content improvement suggestions"""
    suggestions = []
    content_lower = content.lower()
    
    if len(content) < 200:
        suggestions.append("Consider expanding the content for better engagement")
    
    if "call to action" not in content_lower and content_type in ["blog", "landing", "email"]:
        suggestions.append("Add a clear call to action")
    
    if "raptorflow" not in content_lower:
        suggestions.append("Consider mentioning Raptorflow for brand consistency")
    
    if content.count(".") < 3:
        suggestions.append("Break up long paragraphs for better readability")
    
    return suggestions

def generate_chat_suggestions(ai_response: str, user_message: str) -> List[str]:
    """Generate follow-up suggestions based on chat"""
    suggestions = []
    ai_lower = ai_response.lower()
    user_lower = user_message.lower()
    
    if "blog" in user_lower or "content" in user_lower:
        suggestions.append("Generate a blog post outline")
        suggestions.append("Create social media content")
    
    if "strategy" in user_lower or "plan" in user_lower:
        suggestions.append("Develop a marketing campaign")
        suggestions.append("Create an action plan")
    
    if "email" in user_lower:
        suggestions.append("Design an email template")
        suggestions.append("Plan an email sequence")
    
    if "seo" in ai_lower or "optimization" in ai_lower:
        suggestions.append("Analyze website SEO")
        suggestions.append("Create SEO content strategy")
    
    return suggestions[:3]  # Return top 3 suggestions

from services.crm_service import crm_service, CRMProvider

@router.get("/prospects")
async def get_crm_prospects(
    provider: str = "hubspot",
    current_user = Depends(get_current_user)
):
    """Fetch prospects from connected CRM"""
    try:
        crm_provider = CRMProvider(provider.lower())
        prospects = await crm_service.get_prospects(crm_provider)
        return {"success": True, "prospects": prospects}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class SyncProspectRequest(BaseModel):
    prospect_id: str
    asset_id: str
    provider: str = "hubspot"

@router.post("/sync-prospect")
async def sync_asset_to_crm(
    request: SyncProspectRequest,
    current_user = Depends(get_current_user)
):
    """Sync a generated asset to a CRM prospect's timeline"""
    try:
        crm_provider = CRMProvider(request.provider.lower())
        result = await crm_service.sync_content_to_prospect(
            request.prospect_id, 
            request.asset_id, 
            crm_provider
        )
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from services.repurposing_service import repurposing_service, PlatformType

class RepurposeRequest(BaseModel):
    content: str
    target_platform: str
    tone: str = "professional"
    additional_instructions: str = ""

@router.post("/repurpose")
async def repurpose_content(
    request: RepurposeRequest,
    current_user = Depends(get_current_user)
):
    """Repurpose content for a different platform"""
    try:
        platform = PlatformType(request.target_platform.lower())
        result = await repurposing_service.repurpose_content(
            request.content,
            platform,
            request.tone,
            request.additional_instructions
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from services.collaboration_service import collaboration_service, ApprovalStatus

class CommentRequest(BaseModel):
    asset_id: str
    text: str

@router.post("/comment")
async def add_comment(
    request: CommentRequest,
    current_user = Depends(get_current_user)
):
    """Add a comment to an asset"""
    return await collaboration_service.add_comment(
        request.asset_id,
        current_user["id"],
        request.text
    )

@router.get("/comments/{asset_id}")
async def get_comments(
    asset_id: str,
    current_user = Depends(get_current_user)
):
    """Get all comments for an asset"""
    comments = await collaboration_service.get_comments(asset_id)
    return {"success": True, "comments": comments}

class ApprovalRequest(BaseModel):
    asset_id: str
    status: str

@router.post("/approve")
async def update_approval(
    request: ApprovalRequest,
    current_user = Depends(get_current_user)
):
    """Update asset approval status"""
    try:
        status = ApprovalStatus(request.status.lower())
        return await collaboration_service.update_approval_status(
            request.asset_id,
            status,
            current_user["id"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from services.brand_voice_service import brand_voice_service

class VoiceAnalysisRequest(BaseModel):
    samples: List[str]

@router.post("/analyze-voice")
async def analyze_voice(
    request: VoiceAnalysisRequest,
    current_user = Depends(get_current_user)
):
    """Analyze content samples to extract brand voice profile"""
    return await brand_voice_service.analyze_brand_voice(
        request.samples,
        current_user["id"]
    )

@router.get("/brand-voice")
async def get_brand_voice(
    current_user = Depends(get_current_user)
):
    """Get user's brand voice profile"""
    profile = await brand_voice_service.get_profile(current_user["id"])
    if not profile:
        return {"success": False, "error": "No profile found"}
    return {"success": True, "profile": profile}

from services.distribution_service import distribution_service, DistributionPlatform

class DistributionRequest(BaseModel):
    content: str
    platform: str
    scheduled_at: Optional[datetime] = None

@router.post("/distribute")
async def distribute_content(
    request: DistributionRequest,
    current_user = Depends(get_current_user)
):
    """Post or schedule content to a social platform"""
    try:
        platform = DistributionPlatform(request.platform.lower())
        return await distribution_service.post_to_platform(
            request.content,
            platform,
            request.scheduled_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/distribution-plan")
async def get_distribution_plan(
    content: str,
    current_user = Depends(get_current_user)
):
    """Get a multi-platform distribution plan for content"""
    plan = await distribution_service.get_multi_platform_plan(content)
    return {"success": True, "plan": plan}

from services.audit_service import audit_service

class AuditRequest(BaseModel):
    assets: List[Dict[str, Any]]
    gtm_goals: List[str]

@router.post("/audit")
async def audit_content(
    request: AuditRequest,
    current_user = Depends(get_current_user)
):
    """Audit content library for strategic gaps"""
    return await audit_service.audit_content_library(
        request.assets,
        request.gtm_goals
    )

from services.seo_service import seo_service

class SEORequest(BaseModel):
    content: str
    target_keywords: List[str]

@router.post("/seo-optimize")
async def optimize_content_seo(
    request: SEORequest,
    current_user = Depends(get_current_user)
):
    """Audit and optimize content for SEO"""
    return await seo_service.optimize_content(
        request.content,
        request.target_keywords
    )

from services.brief_service import brief_service

class BriefRequest(BaseModel):
    topic: str
    icp_context: Dict[str, Any]
    platform: str = "blog"

from services.advanced_analytics_service import advanced_analytics_service

@router.get("/roi-report")
async def get_roi_report(
    timeframe: int = 30,
    current_user = Depends(get_current_user)
):
    """Get advanced ROI and performance metrics"""
    return await advanced_analytics_service.get_roi_report(timeframe)

from services.automation_service import automation_service

class SequenceRequest(BaseModel):
    goal: str
    steps: int = 5
    tone: str = "professional"

from services.coaching_service import coaching_service

class CoachingRequest(BaseModel):
    content: str
    bcm_context: Dict[str, Any]

from services.marketplace_service import marketplace_service

class ProjectRequest(BaseModel):
    title: str
    description: str
    budget_range: str

@router.post("/marketplace/project")
async def post_project(
    request: ProjectRequest,
    current_user = Depends(get_current_user)
):
    """Post a content project to the marketplace"""
    return await marketplace_service.post_project(
        request.title,
        request.description,
        request.budget_range,
        current_user["id"]
    )

from services.onboarding_service import muse_onboarding_service

@router.get("/onboarding/status")
async def get_onboarding_status(
    current_user = Depends(get_current_user)
):
    """Get Muse-specific onboarding progress"""
    return await muse_onboarding_service.get_onboarding_status(current_user["id"])

@router.post("/onboarding/complete/{step_id}")
async def complete_onboarding_step(
    step_id: str,
    current_user = Depends(get_current_user)
):
    """Mark an onboarding step as completed"""
    return await muse_onboarding_service.complete_step(current_user["id"], step_id)

from services.premium_service import premium_service

@router.get("/premium/analytics")
async def get_enterprise_metrics(
    workspace_id: str,
    current_user = Depends(get_current_user)
):
    """Fetch advanced enterprise-level analytics"""
    is_premium = await premium_service.check_premium_eligibility(current_user["id"])
    if not is_premium:
        raise HTTPException(status_code=403, detail="Premium subscription required")
    return await premium_service.get_enterprise_analytics(workspace_id)

@router.get("/premium/roadmap")
async def get_premium_roadmap():
    """Get the upcoming premium feature roadmap"""
    roadmap = await premium_service.get_premium_roadmap()
    return {"success": True, "roadmap": roadmap}
