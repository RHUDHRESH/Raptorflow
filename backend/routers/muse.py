"""
Muse Guild Router

API endpoints for creative content generation and marketing copy optimization.
Provides access to A/B testing variant generation and marketing creativity tools.

Endpoints:
- POST /muse/generate_variants - Generate A/B testing variants
- POST /muse/generate_variants_batch - Batch variant generation
"""

import structlog
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from backend.utils.auth import get_current_user_and_workspace
from backend.agents.muse.ab_test_agent import ab_test_agent
from backend.models.muse import (
    VariantRequest,
    VariantReport,
    CreativeBatchRequest,
    CreativeBatchResponse,
    ContentOptimizationContext,
    OptimizedVariantRequest,
    HookRequest,
    HookReport,
    MemeRequest,
    MemeReport,
    WhitepaperRequest,
    Whitepaper
)
from backend.agents.muse.ab_test_agent import ab_test_agent
from backend.agents.muse.whitepaper_agent import whitepaper_agent
from backend.agents.muse.hook_generator import hook_generator_agent
from backend.agents.muse.meme_agent import meme_agent

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/muse/generate_variants", response_model=VariantReport, summary="Generate A/B Testing Variants", tags=["Muse Guild - Creative"])
async def generate_ab_test_variants(
    request: VariantRequest,
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Generate creative variations of marketing copy for A/B testing.

    This endpoint takes a piece of marketing copy and generates multiple
    creative variations focused on a specific psychological trigger like
    urgency, tone, or simplicity. Ideal for optimizing email subject lines,
    button text, headlines, and call-to-action phrases.

    **Authentication Required:** User must be authenticated and have a workspace.

    **Input:**
    - Original marketing text
    - Variation focus (URGENCY, TONE, SIMPLICITY, etc.)
    - Number of variants to generate (1-10)

    **Available Focuses:**
    - **URGENCY**: Create scarcity and immediacy
    - **TONE**: Professional, playful, empathetic variations
    - **SIMPLICITY**: Clear, simple language for broader appeal
    - **BENEFIT_ORIENTED**: Focus on customer benefits and outcomes
    - **EMOTIONAL**: Connect emotionally with storytelling
    - **QUESTIONS**: Curiosity-driven engagement hooks
    - **SOCIAL_PROOF**: Include trust indicators and testimonials
    - **RISK_REVERSAL**: Address concerns and provide guarantees
    - **EXCLUSIVITY**: Emphasize premium positioning
    - **PROBLEM_SOLUTION**: Classic problem-agitate-solution format

    **Returns:**
    - Original text, focus used, and list of creative variants
    - Each variant designed to perform differently in testing

    **Use Cases:**
    - Email subject line optimization
    - Landing page headline testing
    - Call-to-action button text variation
    - Social media post A/B testing
    """
    logger.info(
        "Generating A/B test variants",
        user_id=auth["user_id"],
        workspace_id=str(auth["workspace_id"]),
        text_length=len(request.original_text),
        focus=request.variation_focus,
        variant_count=request.number_of_variants
    )

    # Validate variant count limits
    if request.number_of_variants < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 1 variant must be requested"
        )

    if request.number_of_variants > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 variants can be generated per request"
        )

    # Validate text length
    if len(request.original_text.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original text cannot be empty"
        )

    if len(request.original_text) > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original text cannot exceed 5000 characters"
        )

    try:
        # Generate variants using the agent
        report = await ab_test_agent.generate_variants(request)

        logger.info(
            "A/B test variants generated successfully",
            user_id=auth["user_id"],
            variants_created=len(report.variants),
            focus=request.variation_focus
        )

        return report

    except Exception as e:
        logger.error(
            "A/B test variant generation failed",
            user_id=auth["user_id"],
            workspace_id=str(auth["workspace_id"]),
            focus=request.variation_focus,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"A/B test variant generation failed: {str(e)}"
        )


@router.post("/muse/generate_variants_batch", response_model=CreativeBatchResponse, summary="Batch Generate A/B Testing Variants", tags=["Muse Guild - Creative"])
async def generate_ab_test_variants_batch(
    batch_request: CreativeBatchRequest,
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Generate A/B testing variants for multiple pieces of marketing copy.

    This endpoint processes multiple variant requests efficiently, allowing
    you to optimize entire campaigns or test multiple marketing elements
    simultaneously. Useful for comprehensive campaign optimization workflows.

    **Authentication Required:** User must be authenticated and have a workspace.

    **Input:**
    - Array of variant requests (1-20 requests per batch)
    - Each request includes original text, focus, and variant count

    **Returns:**
    - Array of variant reports corresponding to input requests
    - Total request count processed
    - Each report contains original text, focus, and generated variants

    **Processing Notes:**
    - Requests are processed sequentially
    - Individual request failures don't stop batch processing
    - Results maintain the same order as input requests
    - Performance optimized for multiple concurrent variant generation

    **Use Cases:**
    - Full campaign optimization (headlines, CTAs, email subjects)
    - Multi-channel marketing testing
    - Seasonal campaign variant preparation
    """
    request_count = len(batch_request.variants)

    logger.info(
        "Processing batch A/B test variant generation",
        user_id=auth["user_id"],
        workspace_id=str(auth["workspace_id"]),
        request_count=request_count
    )

    # Validate batch limits
    if request_count < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one variant request must be provided"
        )

    if request_count > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 20 variant requests allowed per batch"
        )

    # Pre-validate all requests in the batch
    for i, variant_request in enumerate(batch_request.variants):
        if variant_request.number_of_variants < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Request {i+1}: At least 1 variant must be requested"
            )

        if variant_request.number_of_variants > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Request {i+1}: Maximum 10 variants allowed per request"
            )

        if len(variant_request.original_text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Request {i+1}: Original text cannot be empty"
            )

        if len(variant_request.original_text) > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Request {i+1}: Original text cannot exceed 5000 characters"
            )

    try:
        # Process batch using agent
        response = await ab_test_agent.generate_batch_variants(batch_request)

        logger.info(
            "Batch A/B test variant generation completed",
            user_id=auth["user_id"],
            total_requests=len(batch_request.variants),
            total_variants_generated=sum(len(report.variants) for report in response.reports)
        )

        return response

    except Exception as e:
        logger.error(
            "Batch A/B test variant generation failed",
            user_id=auth["user_id"],
            workspace_id=str(auth["workspace_id"]),
            request_count=request_count,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch variant generation failed: {str(e)}"
        )


@router.post("/muse/generate_variants_contextual", response_model=VariantReport, summary="Generate Variants with Context", tags=["Muse Guild - Creative"])
async def generate_ab_test_variants_contextual(
    optimized_request: OptimizedVariantRequest,
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Generate A/B testing variants with enhanced context for sophisticated suggestions.

    This advanced endpoint considers content type, target audience, brand personality,
    and industry context to generate more relevant and effective variations.
    Provides more sophisticated creative suggestions tailored to your specific use case.

    **Authentication Required:** User must be authenticated and have a workspace.

    **Input:**
    - Base variant request (original text, focus, variant count)
    - Contextual information (content type, audience, brand personality, industry)

    **Context Parameters:**
    - **content_type**: headline, button_text, email_subject, ad_copy, call_to_action
    - **target_audience**: young_professionals, small_business_owners, students, etc.
    - **brand_personality**: professional, fun_and_playful, trustworthy, innovative
    - **industry**: technology, healthcare, finance, education, ecommerce

    **Returns:**
    - Original text, focus, and contextually-aware creative variants
    - More targeted and relevant variations based on contextual factors

    **Benefits:**
    - Audience-specific messaging
    - Brand-consistent variations
    - Industry-appropriate language
    - Content-type-optimized suggestions

    **Use Cases:**
    - Brand campaign optimization with personality constraints
    - Industry-specific marketing challenges
    - Audience-segmented creative testing
    """
    logger.info(
        "Generating contextual A/B test variants",
        user_id=auth["user_id"],
        workspace_id=str(auth["workspace_id"]),
        focus=optimized_request.request.variation_focus,
        content_type=optimized_request.context.content_type,
        target_audience=optimized_request.context.target_audience,
        brand_personality=optimized_request.context.brand_personality,
        industry=optimized_request.context.industry
    )

    # Validate request parameters (same as single request validation)
    if optimized_request.request.number_of_variants < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 1 variant must be requested"
        )

    if optimized_request.request.number_of_variants > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 variants can be generated per request"
        )

    if len(optimized_request.request.original_text.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original text cannot be empty"
        )

    if len(optimized_request.request.original_text) > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original text cannot exceed 5000 characters"
        )

    try:
        # Generate context-aware variants
        report = await ab_test_agent.generate_with_context(
            request=optimized_request.request,
            context={
                "content_type": optimized_request.context.content_type,
                "target_audience": optimized_request.context.target_audience,
                "brand_personality": optimized_request.context.brand_personality,
                "industry": optimized_request.context.industry
            }
        )

        logger.info(
            "Contextual A/B test variants generated successfully",
            user_id=auth["user_id"],
            variants_created=len(report.variants),
            context_provided=True
        )

        return report

    except Exception as e:
        logger.error(
            "Contextual A/B test variant generation failed",
            user_id=auth["user_id"],
            workspace_id=str(auth["workspace_id"]),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Contextual variant generation failed: {str(e)}"
        )


@router.get("/muse/variant_focuses", summary="Get Available Variant Focuses", tags=["Muse Guild - Creative"])
async def get_available_variant_focuses(
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Get list of all available variation focuses for A/B testing.

    Provides a catalog of creative strategies that can be used for generating
    marketing copy variations. Each focus targets different psychological
    triggers and marketing principles.

    **Authentication Required:** User must be authenticated.

    **Returns:**
    - Dictionary with focus names as keys
    - Each focus includes a description of its creative strategy

    **Available Focuses:**
    - **URGENCY**: Scarcity, limited time, FOMO elements
    - **TONE**: Professional, playful, empathetic variations
    - **SIMPLICITY**: Clear, accessible language for broader appeal
    - **BENEFIT_ORIENTED**: Customer-centric value propositions
    - **EMOTIONAL**: Storytelling and emotional connections
    - **QUESTIONS**: Curiosity-driven engagement hooks
    - **SOCIAL_PROOF**: Trust indicators and testimonials
    - **RISK_REVERSAL**: Addressing concerns and guarantees
    - **EXCLUSIVITY**: Premium positioning and VIP treatment
    - **PROBLEM_SOLUTION**: Classic problem-agitate-solution format
    """
    logger.info(
        "Retrieving available variant focuses",
        user_id=auth["user_id"]
    )

    try:
        focuses = ab_test_agent.get_available_focuses()
        focus_descriptions = {}

        for focus in focuses:
            description = ab_test_agent.get_focus_description(focus)
            if description:
                focus_descriptions[focus] = description

        return {
            "available_focuses": focus_descriptions,
            "total_focuses": len(focus_descriptions),
            "description": "Creative variation strategies for A/B testing based on psychological triggers and marketing principles"
        }

    except Exception as e:
        logger.error(
            "Failed to retrieve variant focuses",
            user_id=auth["user_id"],
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve variant focuses: {str(e)}"
        )


@router.post("/muse/create_whitepaper", response_model=Whitepaper, summary="Generate Technical Whitepaper", tags=["Muse Guild - Long Form Content"])
async def create_whitepaper(
    request: WhitepaperRequest,
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Generate a complete technical whitepaper from topic and outline.

    This advanced endpoint creates comprehensive, structured long-form content
    by orchestrating multiple LLM calls to build a complete whitepaper section
    by section. Ideal for thought leadership, SEO content, and lead generation assets.

    **Authentication Required:** User must be authenticated and have a workspace.

    **Input:**
    - Topic: Main subject of the whitepaper (5-200 chars)
    - Outline: Structured section titles (1-20 sections)
    - Target Audience: Description for tone adjustment (5-200 chars)

    **Processing Workflow:**
    1. Generate compelling, SEO-friendly title
    2. Write engaging introduction for target audience
    3. Create detailed content for each outline section
    4. Synthesize forward-looking conclusion
    5. Assemble complete document in formatted Markdown

    **Returns:**
    - Complete whitepaper with title and full Markdown content
    - Professional formatting with proper section headers
    - Audience-tailored technical depth and tone

    **Content Characteristics:**
    - **Professional Tone**: Authoritative, credible presentation
    - **Structured Format**: Clear hierarchy with H1/H2 headers
    - **Audience-Aligned**: Language and depth match target readers
    - **Comprehensive Coverage**: Each outline section fully developed
    - **SEO Optimized**: Keyword-rich, searchable titles and content

    **Use Cases:**
    - Thought leadership content creation
    - SEO-optimized blog posts and articles
    - Lead generation gated assets
    - Technical documentation and guides
    - Industry whitepapers and reports
    """
    logger.info(
        "Creating whitepaper",
        user_id=auth["user_id"],
        workspace_id=str(auth["workspace_id"]),
        topic=request.topic,
        section_count=len(request.outline),
        audience=request.target_audience
    )

    # Validate outline requirements
    if len(request.outline) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one outline section must be provided"
        )

    if len(request.outline) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 20 outline sections allowed"
        )

    # Validate topic and audience
    if len(request.topic.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic must be at least 5 characters"
        )

    if len(request.topic.strip()) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic cannot exceed 200 characters"
        )

    if len(request.target_audience.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target audience must be at least 5 characters"
        )

    if len(request.target_audience.strip()) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target audience description cannot exceed 200 characters"
        )

    # Validate outline section names
    for i, section in enumerate(request.outline):
        if not section.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Outline section {i+1} cannot be empty"
            )
        if len(section.strip()) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Outline section {i+1} cannot exceed 100 characters"
            )

    try:
        # Generate whitepaper using the agent
        whitepaper = await whitepaper_agent.create_whitepaper(request)

        logger.info(
            "Whitepaper created successfully",
            user_id=auth["user_id"],
            title_length=len(whitepaper.title),
            content_length=len(whitepaper.full_text_markdown),
            sections_generated=len(request.outline)
        )

        return whitepaper

    except Exception as e:
        logger.error(
            "Whitepaper creation failed",
            user_id=auth["user_id"],
            workspace_id=str(auth["workspace_id"]),
            topic=request.topic,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Whitepaper creation failed: {str(e)}"
        )


@router.post("/muse/generate_hooks", response_model=HookReport, summary="Generate Viral Content Hooks", tags=["Muse Guild - Creative"])
async def generate_hooks(
    request: HookRequest,
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Generate viral content hooks for short-form videos and social media.

    This endpoint creates compelling, scroll-stopping hooks designed to
    capture immediate attention and drive engagement in social media content,
    TikTok videos, Instagram Reels, and other short-form platforms.

    **Authentication Required:** User must be authenticated and have a workspace.

    **Input:**
    - Topic: The main subject for which to generate hooks (3-200 chars)

    **Hook Types Generated:**
    - **Question Hooks**: Provocative questions that spark curiosity
    - **Statement Hooks**: Bold, surprising statements that challenge norms
    - **Numbered Hooks**: Promise of specific valuable insights
    - **Contrarian Hooks**: Challenge common beliefs or popular opinions
    - **Story Hooks**: Hint at relatable stories or transformations

    **Returns:**
    - 5 viral hook variations optimized for social media attention
    - Scroll-stopping copy designed to maximize engagement
    - Platform-agnostic hooks that work across social media

    **Hook Characteristics:**
    - **Short & Punchy**: Under 25 words for immediate impact
    - **Emotionally Charged**: Create curiosity, surprise, or desire
    - **Value-Driven**: Promise insights, secrets, or transformations
    - **Platform Optimized**: Work well as video titles, captions, thumbnails

    **Use Cases:**
    - TikTok video hooks to stop the scroll
    - Instagram Reel openers for engagement
    - YouTube short intros to boost views
    - LinkedIn post openers for professional content
    - Email subject line inspiration
    - Social media caption hooks
    """
    logger.info(
        "Generating viral hooks",
        user_id=auth["user_id"],
        workspace_id=str(auth["workspace_id"]),
        topic=request.topic
    )

    # Validate topic
    if len(request.topic.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic must be at least 3 characters"
        )

    if len(request.topic.strip()) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic cannot exceed 200 characters"
        )

    try:
        # Generate hooks using the agent
        report = await hook_generator_agent.generate_hooks(request)

        logger.info(
            "Viral hooks generated successfully",
            user_id=auth["user_id"],
            hooks_created=len(report.hooks)
        )

        return report

    except Exception as e:
        logger.error(
            "Hook generation failed",
            user_id=auth["user_id"],
            workspace_id=str(auth["workspace_id"]),
            topic=request.topic,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hook generation failed: {str(e)}"
        )


@router.post("/muse/generate_meme_ideas", response_model=MemeReport, summary="Generate Creative Meme Ideas", tags=["Muse Guild - Creative"])
async def generate_meme_ideas(
    request: MemeRequest,
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Generate creative meme ideas with viral potential.

    This endpoint creates viral meme concepts using popular formats like
    Drake Hotline Bling, Distracted Boyfriend, and other recognizable templates
    with engaging, shareable text content for social media engagement.

    **Authentication Required:** User must be authenticated and have a workspace.

    **Input:**
    - Topic: The subject around which to create memes (3-200 chars)

    **Meme Formats Available:**
    - **Drake Hotline Bling**: Top disapproving, bottom approving
    - **Distracted Boyfriend**: Boyfriend, girlfriend, attractive distractor
    - **This is Fine**: Dog in burning room staying calm
    - **Doge**: Shiba Inu with various multi-panel captions
    - **Expanding Brain**: Increasing sophistication panels
    - **Change My Mind**: Challenging opinions at a table
    - And 7+ more popular viral formats

    **Returns:**
    - 3 creative meme ideas with specific formats and text
    - Each meme includes format specification and ready-to-use text
    - Optimized for social sharing and relatability

    **Meme Characteristics:**
    - **Format-Specific**: Uses established, recognizable meme templates
    - **Viral Optimized**: Created for shareability and relatability
    - **Topic Relevant**: Humorous takes on the provided subject
    - **Platform Ready**: Text formatted for immediate use

    **Use Cases:**
    - Social media content creation for organic engagement
    - Brand awareness campaigns with cultural relevance
    - Community building through relatable humor
    - Viral marketing campaigns and trend participation
    - Content team inspiration for creative campaigns
    """
    logger.info(
        "Generating meme ideas",
        user_id=auth["user_id"],
        workspace_id=str(auth["workspace_id"]),
        topic=request.topic
    )

    # Validate topic
    if len(request.topic.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic must be at least 3 characters"
        )

    if len(request.topic.strip()) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic cannot exceed 200 characters"
        )

    try:
        # Generate meme ideas using the agent
        report = await meme_agent.generate_meme_ideas(request)

        logger.info(
            "Meme ideas generated successfully",
            user_id=auth["user_id"],
            memes_created=len(report.meme_ideas),
            formats_used=[meme.format for meme in report.meme_ideas]
        )

        return report

    except Exception as e:
        logger.error(
            "Meme generation failed",
            user_id=auth["user_id"],
            workspace_id=str(auth["workspace_id"]),
            topic=request.topic,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Meme generation failed: {str(e)}"
        )
