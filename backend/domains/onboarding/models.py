"""
Onboarding Domain - Models
Foundation, ICP, and onboarding state models
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class OnboardingState(BaseModel):
    """Onboarding progress state"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    workspace_id: str
    current_step: str = "foundation"  # foundation, icp, complete
    completed_steps: List[str] = Field(default_factory=list)
    data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FoundationData(BaseModel):
    """Business foundation data"""
    workspace_id: str
    company_name: str
    industry: str
    company_size: str
    website: Optional[str] = None
    description: str
    target_audience: str
    value_proposition: str
    goals: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ICPProfile(BaseModel):
    """Ideal Customer Profile"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    workspace_id: str
    name: str
    description: str
    firmographics: Dict[str, Any] = Field(default_factory=dict)
    psychographics: Dict[str, Any] = Field(default_factory=dict)
    pain_points: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Cohort(BaseModel):
    """Customer cohort/segment"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    workspace_id: str
    icp_id: str
    name: str
    description: str
    criteria: Dict[str, Any] = Field(default_factory=dict)
    size_estimate: Optional[int] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
