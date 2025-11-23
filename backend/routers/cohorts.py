"""
Cohorts Router - API endpoints for ICP/cohort creation and management.
"""

import structlog
from typing import Annotated, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.main import get_current_user_and_workspace
from backend.services.vertex_ai_client import vertex_ai_client
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import generate_correlation_id
from backend.graphs.customer_intelligence_graph import customer_intelligence_graph

router = APIRouter()
logger = structlog.get_logger(__name__)


# --- Request/Response Models ---
class ICPRequest(BaseModel):
    """Request to create an ICP/cohort."""
    nickname: str
    role: Optional[str] = None
    pain_point: Optional[str] = None
    known_attributes: Dict[str, Any] = {}
    depth: str = "quick"  # "quick" or "deep"


class CohortGenerateRequest(BaseModel):
    """Request to generate a cohort from business inputs."""
    businessDescription: str
    productDescription: Optional[str] = ""
    targetMarket: Optional[str] = ""
    valueProposition: Optional[str] = ""
    topCustomers: Optional[str] = ""
    location: Optional[str] = ""
    currentMarketing: Optional[str] = ""
    timeAvailable: Optional[str] = ""
    goals: Optional[str] = ""


class CohortData(BaseModel):
    """Cohort data structure."""
    name: Optional[str] = ""
    executiveSummary: str
    demographics: dict
    buyerRole: str
    psychographics: dict
    painPoints: list[str]
    goals: list[str]
    behavioralTriggers: list[str]
    communication: dict
    budget: str
    timeline: str
    decisionStructure: Optional[str] = ""


class CohortResponse(BaseModel):
    """Cohort response."""
    id: UUID
    workspace_id: UUID
    name: str
    data: dict
    created_at: str
    updated_at: str


class PsychographicsRequest(BaseModel):
    """Request to compute psychographics for a cohort."""
    cohort: dict


@router.post("/generate", response_model=CohortData, summary="Generate Cohort from Inputs", tags=["Cohorts"])
async def generate_cohort(
    request: CohortGenerateRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Generates an ICP/cohort using AI based on business inputs.
    This endpoint replaces direct frontend calls to Vertex AI for security.
    """
    correlation_id = generate_correlation_id()
    logger.info("Generating cohort from inputs", correlation_id=correlation_id)
    
    try:
        # Build context for AI
        context = f"""
Analyze the following business data and generate a detailed Ideal Customer Profile (ICP)/cohort.

Business Description: {request.businessDescription}
Product Description: {request.productDescription}
Target Market: {request.targetMarket}
Value Proposition: {request.valueProposition}
Top Customers: {request.topCustomers}
Location: {request.location}
Current Marketing: {request.currentMarketing}
Time Available: {request.timeAvailable}
Goals: {request.goals}

Generate a comprehensive cohort profile including:
- Executive summary (2-3 sentences)
- Demographics (company size, industry, revenue, location)
- Buyer role
- Psychographics (values, decision style, priorities)
- Pain points (3-5 specific challenges)
- Goals (3-5 specific objectives)
- Behavioral triggers (2-4 buying signals)
- Communication preferences (channels, tone, format)
- Budget range
- Purchase timeline
- Decision-making structure

Return as valid JSON matching this exact structure:
{{
  "name": "Suggested Cohort Name",
  "executiveSummary": "Brief summary",
  "demographics": {{
    "companySize": "50-200",
    "industry": "SaaS",
    "revenue": "$5M-$25M",
    "location": "North America"
  }},
  "buyerRole": "CTO",
  "psychographics": {{
    "values": ["Efficiency", "Innovation"],
    "decisionStyle": "Analytical and data-driven",
    "priorities": ["Cost savings", "Scalability"]
  }},
  "painPoints": ["Challenge 1", "Challenge 2"],
  "goals": ["Goal 1", "Goal 2"],
  "behavioralTriggers": ["Trigger 1", "Trigger 2"],
  "communication": {{
    "channels": ["LinkedIn", "Email"],
    "tone": "Professional and data-focused",
    "format": "Case studies and whitepapers"
  }},
  "budget": "$50k-$200k annually",
  "timeline": "3-6 months",
  "decisionStructure": "Committee-based with exec approval"
}}
"""
        
        # Call Vertex AI using creative reasoning model
        messages = [
            {"role": "user", "content": context}
        ]
        
        response_text = await vertex_ai_client.chat_completion(
            messages=messages,
            model_type="creative_reasoning",  # Claude Sonnet for creative reasoning
            temperature=0.8,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        import json
        cohort_data = json.loads(response_text)
        
        # Ensure all required fields exist with defaults
        cohort_data = {
            "name": cohort_data.get("name", ""),
            "executiveSummary": cohort_data.get("executiveSummary", ""),
            "demographics": cohort_data.get("demographics", {
                "companySize": "Unknown",
                "industry": "Unknown",
                "revenue": "Unknown",
                "location": "Unknown"
            }),
            "buyerRole": cohort_data.get("buyerRole", ""),
            "psychographics": cohort_data.get("psychographics", {
                "values": [],
                "decisionStyle": "",
                "priorities": []
            }),
            "painPoints": cohort_data.get("painPoints", []),
            "goals": cohort_data.get("goals", []),
            "behavioralTriggers": cohort_data.get("behavioralTriggers", []),
            "communication": cohort_data.get("communication", {
                "channels": [],
                "tone": "",
                "format": ""
            }),
            "budget": cohort_data.get("budget", ""),
            "timeline": cohort_data.get("timeline", ""),
            "decisionStructure": cohort_data.get("decisionStructure", "")
        }
        
        logger.info("Cohort generated successfully", correlation_id=correlation_id)
        return CohortData(**cohort_data)
        
    except Exception as e:
        logger.error(f"Failed to generate cohort: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate cohort: {str(e)}"
        )


@router.post("/psychographics", response_model=dict, summary="Compute Psychographics", tags=["Cohorts"])
async def compute_psychographics(
    request: PsychographicsRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Computes deep psychographic insights for a cohort using AI.
    """
    correlation_id = generate_correlation_id()
    logger.info("Computing psychographics", correlation_id=correlation_id)
    
    try:
        context = f"""
Analyze this customer cohort and generate deep psychographic insights.

Cohort Data: {request.cohort}

Generate detailed psychographic analysis including:
- Core values and motivations
- Decision-making style and patterns
- Personality traits
- Professional interests
- Pain psychology (fears, motivations, emotional drivers)
- Content and communication preferences

Return as valid JSON:
{{
  "values": ["Value1", "Value2"],
  "decisionStyle": "Style description",
  "personalityTraits": ["Trait1", "Trait2"],
  "interests": ["Interest1", "Interest2"],
  "painPsychology": {{
    "primaryFear": "Main fear/concern",
    "motivation": "Core motivation",
    "emotionalDriver": "Emotional driver"
  }},
  "contentPreferences": {{
    "format": "Preferred content format",
    "tone": "Preferred communication tone",
    "channels": ["Channel1", "Channel2"]
  }}
}}
"""
        
        messages = [
            {"role": "user", "content": context}
        ]
        
        response_text = await vertex_ai_client.chat_completion(
            messages=messages,
            model_type="creative_reasoning",
            temperature=0.7,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        import json
        psychographics = json.loads(response_text)
        
        # Ensure structure
        psychographics = {
            "values": psychographics.get("values", []),
            "decisionStyle": psychographics.get("decisionStyle", ""),
            "personalityTraits": psychographics.get("personalityTraits", []),
            "interests": psychographics.get("interests", []),
            "painPsychology": psychographics.get("painPsychology", {
                "primaryFear": "",
                "motivation": "",
                "emotionalDriver": ""
            }),
            "contentPreferences": psychographics.get("contentPreferences", {
                "format": "",
                "tone": "",
                "channels": []
            })
        }
        
        logger.info("Psychographics computed successfully", correlation_id=correlation_id)
        return psychographics
        
    except Exception as e:
        logger.error(f"Failed to compute psychographics: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute psychographics: {str(e)}"
        )


@router.post("/create", response_model=dict, summary="Create ICP/Cohort", tags=["Cohorts"])
async def create_icp(
    request: ICPRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Creates a complete ICP/cohort using the Customer Intelligence Graph.
    Calls the research supervisor to build ICP with tags, narrative, pain points, and psychographics.
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Creating ICP via customer intelligence graph",
                nickname=request.nickname,
                correlation_id=correlation_id)

    try:
        # Build persona input from request
        persona_input = {
            "nickname": request.nickname,
            "role": request.role,
            "pain_point": request.pain_point,
            **request.known_attributes
        }

        # Call customer intelligence graph
        result = await customer_intelligence_graph.create_icp(
            workspace_id=workspace_id,
            persona_input=persona_input,
            depth=request.depth
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to create ICP")
            )

        logger.info("ICP created successfully",
                   icp_id=result["icp"].get("id"),
                   correlation_id=correlation_id)

        return {
            "status": "success",
            "icp": result["icp"],
            "narrative": result["narrative"],
            "pain_points": result["pain_points"],
            "triggers": result["triggers"],
            "correlation_id": correlation_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create ICP: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", response_model=CohortResponse, summary="Save Cohort", tags=["Cohorts"])
async def create_cohort(
    cohort_data: CohortData,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Saves a cohort to the database."""
    workspace_id = auth["workspace_id"]
    user_id = auth["user_id"]

    try:
        cohort_record = {
            "workspace_id": str(workspace_id),
            "user_id": str(user_id),
            "name": cohort_data.name,
            "data": cohort_data.dict(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        saved = await supabase_client.insert("cohorts", cohort_record)

        return CohortResponse(**saved)

    except Exception as e:
        logger.error(f"Failed to save cohort: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/list", response_model=list[CohortResponse], summary="List Cohorts", tags=["Cohorts"])
async def list_cohorts(auth: Annotated[dict, Depends(get_current_user_and_workspace)]):
    """Fetches all cohort entries from Supabase for the workspace."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Fetching cohorts list", workspace_id=workspace_id, correlation_id=correlation_id)

    try:
        cohorts = await supabase_client.fetch_all(
            "cohorts",
            {"workspace_id": str(workspace_id)}
        )

        logger.info(f"Retrieved {len(cohorts)} cohorts", correlation_id=correlation_id)
        return [CohortResponse(**c) for c in cohorts]

    except Exception as e:
        logger.error(f"Failed to fetch cohorts: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{cohort_id}", response_model=CohortResponse, summary="Get Cohort", tags=["Cohorts"])
async def get_cohort(
    cohort_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Retrieves a specific cohort."""
    workspace_id = auth["workspace_id"]

    cohort = await supabase_client.fetch_one(
        "cohorts",
        {"id": str(cohort_id), "workspace_id": str(workspace_id)}
    )

    if not cohort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cohort not found"
        )

    return CohortResponse(**cohort)


@router.post("/{cohort_id}/enrich", response_model=dict, summary="Enrich Cohort with Psychographic Tags", tags=["Cohorts"])
async def enrich_cohort(
    cohort_id: UUID,
    depth: str = "deep",
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Calls the Tag Assignment Agent to add additional psychographic tags to an existing cohort.
    Enriches with deeper pain points, behavioral triggers, and psychographic insights.
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Enriching cohort",
                cohort_id=cohort_id,
                depth=depth,
                correlation_id=correlation_id)

    try:
        # Verify cohort exists and belongs to workspace
        cohort = await supabase_client.fetch_one(
            "cohorts",
            {"id": str(cohort_id), "workspace_id": str(workspace_id)}
        )

        if not cohort:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cohort not found"
            )

        # Call customer intelligence graph to enrich existing ICP
        result = await customer_intelligence_graph.enrich_existing_icp(
            icp_id=cohort_id,
            depth=depth
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to enrich cohort")
            )

        logger.info("Cohort enriched successfully",
                   cohort_id=cohort_id,
                   correlation_id=correlation_id)

        return {
            "status": "success",
            "cohort_id": str(cohort_id),
            "enriched_icp": result["icp"],
            "correlation_id": correlation_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enrich cohort: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{cohort_id}", summary="Delete Cohort", tags=["Cohorts"])
async def delete_cohort(
    cohort_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Deletes a cohort."""
    workspace_id = auth["workspace_id"]
    
    try:
        await supabase_client.delete(
            "cohorts",
            {"id": str(cohort_id), "workspace_id": str(workspace_id)}
        )
        
        return {"status": "success", "message": "Cohort deleted"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

