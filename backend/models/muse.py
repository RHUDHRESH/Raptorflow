"""
Muse Guild Models

Data models for creative content generation, copy variations,
and marketing optimization within the Muse Guild.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class VariantRequest(BaseModel):
    """
    Request model for generating creative variations of marketing copy.

    This model defines the input parameters for A/B testing variant generation,
    allowing users to specify the original text and the specific focus for
    generating creative alternatives.
    """

    original_text: str = Field(
        ...,
        description="The original marketing copy to generate variations for",
        min_length=1,
        max_length=5000,  # Reasonable limit for marketing copy
        examples=["Buy Now! Limited Time Offer", "Improve Your Skills with Our Training Program"]
    )
    variation_focus: str = Field(
        ...,
        description="Specific focus for generating variations (controls the creative direction)",
        examples=["URGENCY", "TONE", "SIMPLICITY", "BENEFIT_ORIENTED", "EMOTIONAL", "QUESTIONS"]
    )
    number_of_variants: int = Field(
        3,
        description="Number of creative variants to generate",
        ge=1,
        le=10,  # Reasonable limit to prevent excessive generation
        examples=[3, 5, 7]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v,
            int: lambda v: v
        }


class VariantReport(BaseModel):
    """
    Comprehensive report containing creative marketing copy variations.

    This model contains the original text, the focus used for generation,
    and all the creative variants produced by the A/B testing agent.
    """

    original_text: str = Field(
        ...,
        description="The original marketing copy that was used as input",
        examples=["Buy Now! Limited Time Offer"]
    )
    focus: str = Field(
        ...,
        description="The variation focus that guided the creative generation",
        examples=["URGENCY", "TONE", "SIMPLICITY"]
    )
    variants: List[str] = Field(
        ...,
        description="List of creative variations generated based on the focus",
        min_items=1,
        max_items=10,
        examples=[
            [
                "Buy Now! Limited Time Offer - Don't Wait!",
                "Act Fast! Limited Time Only!",
                "Don't Miss Out - Limited Time Offer!"
            ]
        ]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v,
            list: lambda v: v
        }


class CreativeBatchRequest(BaseModel):
    """
    Request model for batch variant generation across multiple pieces of copy.

    Allows processing multiple marketing elements simultaneously for
    comprehensive campaign optimization.
    """

    variants: List[VariantRequest] = Field(
        ...,
        description="List of variant requests to process in batch",
        min_items=1,
        max_items=20  # Limit batch size for performance
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            list: lambda v: v
        }


class CreativeBatchResponse(BaseModel):
    """
    Response model for batch variant generation.

    Contains variant reports for multiple original texts in the same order
    as the input requests.
    """

    reports: List[VariantReport] = Field(
        ...,
        description="List of variant reports corresponding to input requests",
        min_items=1
    )
    total_requests: int = Field(
        ...,
        description="Total number of variant requests processed",
        ge=1
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            list: lambda v: v,
            int: lambda v: v
        }


class ContentOptimizationContext(BaseModel):
    """
    Context information for content optimization scenarios.

    Provides additional context about the content being optimized,
    which can help guide more relevant variant generation.
    """

    content_type: str = Field(
        ...,
        description="Type of content being optimized",
        examples=["headline", "button_text", "email_subject", "ad_copy", "call_to_action"]
    )
    target_audience: str = Field(
        ...,
        description="Target audience for the content",
        examples=["young_professionals", "small_business_owners", "students", "senior_citizens"]
    )
    brand_personality: str = Field(
        ...,
        description="Brand personality traits to maintain in variations",
        examples=["professional", "fun_and_playful", "trustworthy", "innovative"]
    )
    industry: str = Field(
        ...,
        description="Industry or domain context",
        examples=["technology", "healthcare", "finance", "education", "ecommerce"]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v
        }


class OptimizedVariantRequest(BaseModel):
    """
    Enhanced variant request with optimization context.

    Combines basic variant generation with contextual information
    for more sophisticated and relevant creative suggestions.
    """

    request: VariantRequest = Field(
        ...,
        description="Base variant request parameters"
    )
    context: ContentOptimizationContext = Field(
        ...,
        description="Additional context for optimization"
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            dict: lambda v: v
        }


class HookRequest(BaseModel):
    """
    Request model for generating viral content hooks.

    Defines the parameters for creating compelling, scroll-stopping
    opening lines designed to hook viewer's attention immediately.
    """

    topic: str = Field(
        ...,
        description="The main topic or theme for which to generate hooks",
        min_length=3,
        max_length=200,
        examples=["AI automation in business", "Sustainable living tips", "Crypto investment strategies"]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v
        }


class HookReport(BaseModel):
    """
    Comprehensive hook generation report.

    Contains a set of viral, attention-grabbing hooks optimized
    for social media content and short-form video platforms.
    """

    hooks: List[str] = Field(
        ...,
        description="List of viral content hooks tailored for the topic",
        min_items=3,
        max_items=10,  # Always generates 5 hooks but allows flexibility
        examples=[
            [
                "What if I told you AI could 10x your business overnight?",
                "Stop wasting money - Here's what billionaires do instead...",
                "The #1 mistake killing your productivity (and how to fix it)"
            ]
        ]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            list: lambda v: v
        }


class MemeRequest(BaseModel):
    """
    Request model for generating creative meme ideas.

    Defines the parameters for creating viral meme concepts
    with specific format specifications and written content.
    """

    topic: str = Field(
        ...,
        description="The topic or theme around which to create memes",
        min_length=3,
        max_length=200,
        examples=["Working from home", "Coffee addiction", "Startup life", "Social media marketing"]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v
        }


class MemeIdea(BaseModel):
    """
    Individual meme concept with format and text specification.

    Contains both the meme format/style and the specific text
    that should be used in the meme for viral effectiveness.
    """

    format: str = Field(
        ...,
        description="Meme format or template style to use",
        examples=["Drake Hotline Bling", "Distracted Boyfriend", "Woman Yelling at Cat", "This is Fine"]
    )
    text: str = Field(
        ...,
        description="The actual text content for the meme",
        min_length=10,
        examples=["Top panel: 'My code after 3 AM' Bottom panel: 'perfection!'", "Me trying to adult: *buys planner* Also me: *uses stickies*"]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v
        }


class MemeReport(BaseModel):
    """
    Comprehensive meme idea generation report.

    Contains multiple meme concepts with format specifications
    and text content optimized for viral social media engagement.
    """

    meme_ideas: List[MemeIdea] = Field(
        ...,
        description="List of creative meme concepts with formats and text",
        min_items=1,
        max_items=10,  # Typically generates 3 but allows flexibility
        examples=[
            [
                {
                    "format": "Drake Hotline Bling",
                    "text": "Top panel: 'Being a developer'\nBottom panel: 'Getting stuck on a CSS layout for 3 hours'"
                },
                {
                    "format": "Distracted Boyfriend",
                    "text": "Boyfriend: 'My attention'\nGirlfriend: 'Working on side project'\nOther woman: 'Netflix and chill'"
                }
            ]
        ]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            list: lambda v: v
        }


class WhitepaperRequest(BaseModel):
    """
    Request model for generating structured long-form content.

    Defines the parameters for creating comprehensive whitepapers,
    articles, or technical documents with specified structure and audience.
    """

    topic: str = Field(
        ...,
        description="The main topic or subject of the whitepaper",
        min_length=5,
        max_length=200,
        examples=["The Future of AI in Digital Marketing", "Cloud Security Best Practices"]
    )
    outline: List[str] = Field(
        ...,
        description="List of section titles that form the document structure",
        min_items=1,
        max_items=20,  # Reasonable limit for document sections
        examples=[
            [
                "Introduction to AI Marketing",
                "AI-Powered Personalization",
                "Predictive Analytics for Campaigns",
                "Ethical Considerations"
            ]
        ]
    )
    target_audience: str = Field(
        ...,
        description="Description of the intended audience for tone and content adjustment",
        min_length=5,
        max_length=200,
        examples=["CMOs at B2B SaaS companies", "IT decision makers in Fortune 500 enterprises"]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v,
            list: lambda v: v
        }


class Whitepaper(BaseModel):
    """
    Complete generated whitepaper or long-form document.

    Contains the final title and fully assembled document content
    in structured Markdown format with all sections integrated.
    """

    title: str = Field(
        ...,
        description="The generated title for the whitepaper",
        min_length=5,
        max_length=300,
        examples=["The Future of AI in Digital Marketing: A Comprehensive Guide"]
    )
    full_text_markdown: str = Field(
        ...,
        description="Complete document content in Markdown format with sections and formatting",
        min_length=100,  # Minimum meaningful content
        examples=[
            """# The Future of AI in Digital Marketing

## Introduction to AI Marketing

Artificial intelligence is revolutionizing the way organizations approach digital marketing...

*(continued with full document)*
"""
        ]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v
        }


class WhitepaperGenerationStatus(BaseModel):
    """
    Status tracking for whitepaper generation progress.

    Provides visibility into the multi-step generation process
    for longer-running document creation tasks.
    """

    total_steps: int = Field(
        ...,
        description="Total number of generation steps required",
        ge=3  # Minimum: title, intro, conclusion
    )
    completed_steps: int = Field(
        0,
        description="Number of steps completed so far",
        ge=0
    )
    current_step: str = Field(
        ...,
        description="Description of the currently executing step",
        examples=["Generating title", "Writing introduction", "Creating section: AI-Powered Personalization"]
    )
    estimated_time_remaining: Optional[str] = Field(
        None,
        description="Estimated time remaining for completion",
        examples=["30 seconds", "2 minutes"]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            int: lambda v: v,
            str: lambda v: v
        }
