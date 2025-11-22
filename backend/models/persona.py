"""
Pydantic models for ICP/Persona data
"""

from typing import List, Dict, Optional, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ICPBase(BaseModel):
    """Base ICP/Cohort model"""
    name: str = Field(..., description="ICP name (e.g., 'Tech Startup Founder')")
    executive_summary: Optional[str] = Field(None, description="Brief overview of this ICP")
    
    # Demographics
    demographics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Demographics like company_size, industry, revenue, location"
    )
    buyer_role: Optional[str] = Field(None, description="Decision-maker role")
    
    # Psychographics (B=MAP framework)
    psychographics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Motivation, ability, prompt_receptiveness, risk_tolerance, etc."
    )
    
    # Core fields
    pain_points: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    behavioral_triggers: List[str] = Field(default_factory=list)
    
    # Communication preferences
    communication: Dict[str, Any] = Field(
        default_factory=dict,
        description="Channels, tone, format preferences"
    )
    budget: Optional[str] = None
    timeline: Optional[str] = None
    decision_structure: Optional[str] = None
    
    # Tag fabric (50+ psychographic tags)
    tags: List[str] = Field(default_factory=list, description="Psychographic/demographic tags")


class ICPCreate(ICPBase):
    """ICP creation payload"""
    workspace_id: UUID


class ICPUpdate(BaseModel):
    """ICP update payload (all fields optional)"""
    name: Optional[str] = None
    executive_summary: Optional[str] = None
    demographics: Optional[Dict[str, Any]] = None
    buyer_role: Optional[str] = None
    psychographics: Optional[Dict[str, Any]] = None
    pain_points: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    behavioral_triggers: Optional[List[str]] = None
    communication: Optional[Dict[str, Any]] = None
    budget: Optional[str] = None
    timeline: Optional[str] = None
    decision_structure: Optional[str] = None
    tags: Optional[List[str]] = None


class ICPResponse(ICPBase):
    """ICP response with metadata"""
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PersonaNarrativeRequest(BaseModel):
    """Request to generate persona narrative"""
    icp_id: UUID
    tone: Optional[str] = Field("professional", description="Narrative tone")


class PersonaNarrativeResponse(BaseModel):
    """Generated persona narrative"""
    icp_id: UUID
    narrative: str = Field(..., description="2-3 paragraph persona story")
    name_suggestion: Optional[str] = Field(None, description="Suggested persona name")


class TagEnrichmentRequest(BaseModel):
    """Request to enrich ICP with tags"""
    icp_id: UUID
    description: str = Field(..., description="Raw ICP description")


class TagEnrichmentResponse(BaseModel):
    """Enriched tags"""
    icp_id: UUID
    tags: List[str] = Field(..., description="50+ assigned tags")
    categories: Dict[str, List[str]] = Field(
        ...,
        description="Tags grouped by category (demographic, psychographic, behavioral)"
    )


class PainPointMiningRequest(BaseModel):
    """Request to mine pain points"""
    icp_id: UUID
    sources: List[str] = Field(
        default=["reddit", "quora", "g2", "trustpilot"],
        description="Sources to scrape"
    )


class PainPointMiningResponse(BaseModel):
    """Mined pain points with evidence"""
    icp_id: UUID
    pain_points: List[Dict[str, Any]] = Field(
        ...,
        description="Each pain point with description, frequency, evidence quotes"
    )
    triggers: List[str] = Field(..., description="Buying triggers identified")
    objections: List[str] = Field(..., description="Common objections")

