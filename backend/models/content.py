"""
Pydantic models for Content Generation.
These models define the structure for content requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Any
from uuid import UUID, uuid4
from datetime import datetime


class ContentMetadata(BaseModel):
    """Metadata shared across generated content assets."""

    status: Literal["draft", "review", "approved", "rejected", "published"] = "draft"
    reviewer: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    correlation_id: Optional[str] = None


class BlogRequest(BaseModel):
    """Request schema for blog generation."""

    workspace_id: UUID
    persona_id: Optional[UUID] = None
    topic: str
    outline: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    tone: Optional[str] = None
    target_length: Optional[int] = Field(None, description="Desired word count")
    brand_voice: Optional[str] = None
    include_cta: bool = True
    correlation_id: Optional[str] = None


class BlogResponse(BaseModel):
    """Response for blog generation requests."""

    blog_id: UUID
    title: str
    meta_description: Optional[str] = None
    body: str
    outline: List[str] = Field(default_factory=list)
    seo_keywords: List[str] = Field(default_factory=list)
    hooks: List[str] = Field(default_factory=list)
    metadata: ContentMetadata = Field(default_factory=ContentMetadata)


class EmailRequest(BaseModel):
    """Request schema for email/sequence generation."""

    workspace_id: UUID
    persona_id: Optional[UUID] = None
    sequence_name: Optional[str] = None
    product_offer: Optional[str] = None
    goal: Optional[str] = Field(None, description="Objective for the sequence (demo, signup, upsell)")
    tone: Optional[str] = None
    number_of_emails: int = Field(default=3, ge=1, le=7)
    personalization_hints: List[str] = Field(default_factory=list)
    brand_voice: Optional[str] = None
    correlation_id: Optional[str] = None


class EmailMessage(BaseModel):
    """Single email message with subject/body."""

    subject: str
    preheader: Optional[str] = None
    body: str
    cta: Optional[str] = None
    personalization_tokens: Dict[str, str] = Field(default_factory=dict)


class SocialPostRequest(BaseModel):
    """Request schema for social post generation."""

    workspace_id: UUID
    persona_id: Optional[UUID] = None
    platform: Literal["linkedin", "twitter", "instagram", "facebook", "tiktok", "youtube", "threads"]
    topic: str
    angle: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)
    character_limit: Optional[int] = None
    include_visual_directions: bool = True
    brand_voice: Optional[str] = None
    correlation_id: Optional[str] = None


class ContentRequest(BaseModel):
    """Request to generate content."""
    workspace_id: UUID
    move_id: Optional[UUID] = Field(None, description="Associated campaign")
    content_type: Literal[
        "blog_post",
        "email",
        "social_post",
        "hook",
        "video_script",
        "carousel",
        "meme",
        "landing_page",
        "case_study",
        "ebook",
        "newsletter",
        "press_release",
        "ad_copy",
        "other"
    ]
    
    # Targeting
    persona_id: Optional[UUID] = Field(None, description="Target ICP cohort")
    
    # Content specifications
    topic: str = Field(..., description="Main subject or theme")
    angle: Optional[str] = Field(None, description="Unique perspective or approach")
    keywords: List[str] = Field(default_factory=list, description="SEO keywords to include")
    tone: Optional[Literal["professional", "casual", "inspirational", "educational", "witty", "authoritative"]] = None
    length: Optional[Literal["short", "medium", "long"]] = Field(None, description="Desired content length")
    
    # Platform-specific
    platform: Optional[Literal["linkedin", "twitter", "instagram", "facebook", "youtube", "email", "blog"]] = None
    format_requirements: Dict[str, Any] = Field(default_factory=dict, description="Platform-specific formatting")
    
    # References
    include_cta: bool = Field(default=True, description="Include call-to-action")
    cta_text: Optional[str] = None
    reference_urls: List[str] = Field(default_factory=list, description="Links to include or reference")
    brand_voice_sample: Optional[str] = Field(None, description="Example of desired writing style")
    
    # Constraints
    avoid_topics: List[str] = Field(default_factory=list)
    must_include_phrases: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
                "move_id": "750e8400-e29b-41d4-a716-446655440000",
                "content_type": "blog_post",
                "persona_id": "650e8400-e29b-41d4-a716-446655440000",
                "topic": "How AI is transforming sales forecasting",
                "tone": "professional",
                "length": "long",
                "keywords": ["AI sales", "forecasting", "revenue prediction"],
                "platform": "blog"
            }
        }


class ContentVariant(BaseModel):
    """A single variant of generated content."""

    variant_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for this variant")
    format: Optional[str] = Field(default=None, description="Content format (blog, email_body, social_post, etc.)")
    content: str = Field(..., alias="text", description="The generated content body")
    headline: Optional[str] = Field(None, description="Title or subject line")
    summary: Optional[str] = None
    word_count: Optional[int] = None
    readability_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    quality_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="AI-assessed quality score")
    reasoning: Optional[str] = Field(None, description="Why this approach was chosen")
    seo_keywords: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    platform_specific_attributes: Dict[str, Any] = Field(default_factory=dict)
    estimated_performance: Optional[Dict[str, Any]] = Field(
        None,
        description="Predicted metrics (engagement, clicks, etc.)",
    )

    class Config:
        populate_by_name = True

    @property
    def text(self) -> str:
        """Alias for backward compatibility with earlier models."""
        return self.content


class Hook(BaseModel):
    """A hook/tagline/subject line."""
    text: str
    hook_type: Literal["curiosity", "urgency", "social_proof", "benefit", "question", "stat", "other"]
    score: float = Field(ge=0.0, le=1.0, description="Resonance score")
    rationale: Optional[str] = None


class ContentResponse(BaseModel):
    """Response containing generated content."""
    content_id: UUID
    request: ContentRequest
    
    # Generated content
    variants: List[ContentVariant] = Field(..., min_items=1, description="Generated content variants")
    recommended_variant_id: str = Field(..., description="ID of the best variant")
    hooks: List[Hook] = Field(default_factory=list, description="Alternative hooks if applicable")
    
    # Metadata
    seo_metadata: Optional[Dict[str, Any]] = Field(None, description="Meta title, description, tags")
    hashtags: List[str] = Field(default_factory=list)
    suggested_visuals: List[str] = Field(default_factory=list, description="Image prompts or URLs")
    
    # Quality assessment
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    critique: Optional[str] = Field(None, description="Critic agent feedback")
    suggestions_for_improvement: List[str] = Field(default_factory=list)
    
    # Status
    status: Literal["draft", "review", "approved", "rejected", "published"] = Field(default="draft")
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    
    # Timestamps
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_id": "850e8400-e29b-41d4-a716-446655440000",
                "variants": [
                    {
                        "variant_id": "v1",
                        "text": "AI is revolutionizing sales forecasting...",
                        "headline": "The Future of Sales Forecasting is Here",
                        "quality_score": 0.87
                    }
                ],
                "recommended_variant_id": "v1",
                "hooks": [
                    {
                        "text": "Stop guessing your quarterly revenue",
                        "hook_type": "urgency",
                        "score": 0.91
                    }
                ],
                "overall_quality_score": 0.87,
                "status": "draft",
                "generated_at": "2024-04-15T10:30:00Z"
            }
        }


class ContentApprovalRequest(BaseModel):
    """Request to approve or reject content."""
    content_id: UUID
    variant_id: str
    action: Literal["approve", "reject", "request_revision"]
    feedback: Optional[str] = Field(None, description="User feedback for revisions")
    schedule_publish: bool = Field(default=False)
    publish_at: Optional[datetime] = Field(None, description="Scheduled publish time")


class BulkContentRequest(BaseModel):
    """Request to generate multiple pieces of content at once."""
    workspace_id: UUID
    move_id: Optional[UUID] = None
    content_plan: List[ContentRequest] = Field(..., min_items=1, description="List of content items to generate")
    generate_sequentially: bool = Field(
        default=False, 
        description="Generate one at a time (slower but considers context)"
    )
    maintain_consistency: bool = Field(
        default=True, 
        description="Ensure consistent tone and messaging across all pieces"
    )


class ContentCalendar(BaseModel):
    """A content calendar for a campaign."""
    move_id: UUID
    entries: List["ContentCalendarEntry"] = Field(default_factory=list)
    start_date: datetime
    end_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ContentCalendarEntry(BaseModel):
    """A single entry in the content calendar."""
    id: Optional[UUID] = None
    content_id: Optional[UUID] = Field(None, description="Links to generated content if created")
    publish_date: datetime
    content_type: str
    platform: str
    topic: str
    persona_id: Optional[UUID] = None
    status: Literal["planned", "in_progress", "ready", "published", "cancelled"] = Field(default="planned")
    notes: Optional[str] = None


class AssetMetadata(BaseModel):
    """Metadata for generated assets (images, videos, etc.)."""
    asset_id: UUID
    content_id: Optional[UUID] = Field(None, description="Associated content")
    asset_type: Literal["image", "video", "audio", "document", "other"]
    file_url: str
    file_size_bytes: Optional[int] = None
    dimensions: Optional[Dict[str, int]] = Field(None, description="Width, height for images/videos")
    duration_seconds: Optional[float] = Field(None, description="For video/audio")
    format: Optional[str] = Field(None, description="File format (jpg, mp4, etc.)")
    source: Literal["canva", "dall-e", "stable_diffusion", "manual_upload", "other"]
    quality_check_passed: bool = Field(default=False)
    quality_issues: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BrandVoiceProfile(BaseModel):
    """Learned brand voice characteristics."""
    workspace_id: UUID
    voice_characteristics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Learned writing patterns, vocabulary, sentence structure"
    )
    sample_texts: List[str] = Field(default_factory=list, description="Example content used for learning")
    tone_distribution: Dict[str, float] = Field(
        default_factory=dict,
        description="Distribution of tones (professional: 0.7, witty: 0.3)"
    )
    vocabulary_preferences: Dict[str, float] = Field(
        default_factory=dict,
        description="Common words/phrases and their frequencies"
    )
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Update forward reference for ContentCalendar
ContentCalendar.model_rebuild()

