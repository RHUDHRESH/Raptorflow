import logging
from typing import Dict, List, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

logger = logging.getLogger("raptorflow.creatives.linkedin")


class LinkedInPost(BaseModel):
    """SOTA structured social post representation."""

    hook: str = Field(description="The first line that stops the scroll.")
    body: str = Field(description="The main tactical or philosophical insight.")
    cta: str = Field(description="The one clear action or question.")
    post_vibe: str = Field(description="The tone signal (e.g., surgical, calm).")


class LinkedInArchitect:
    """
    SOTA Social Production Node.
    Generates surgical 'Thought Leader' style LinkedIn posts using Gemini.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master ghostwriter for high-stakes founders. "
                    "Generate a surgical 'Thought Leader' style LinkedIn post. "
                    "NO emojis. NO hype. NO corporate-speak. "
                    "Vibe: Calm, Expensive, Decisive.",
                ),
                ("user", "Brief: {brief}\nContext: {context}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(LinkedInPost)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        brief = state.get("context_brief", {}).get("uvps", "No specific UVPs")
        context = state.get("research_bundle", {}).get(
            "executive_brief", "General marketing"
        )
        logger.info("Architecting LinkedIn thought leader post...")

        post = await self.chain.ainvoke({"brief": str(brief), "context": str(context)})
        logger.info("LinkedIn post generation complete.")

        # We append to variants in the global state
        return {"variants": [post.model_dump()], "current_draft": post.body}


class TwitterThread(BaseModel):
    """SOTA structured Twitter thread representation."""

    hook_tweet: str = Field(description="The viral opener.")
    body_tweets: List[str] = Field(description="The mid-thread insights (2-5 tweets).")
    closing_tweet: str = Field(description="The CTA and link.")


class TwitterArchitect:
    """
    SOTA Social Production Node.
    Generates high-leverage Twitter threads using Gemini.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master of high-velocity social signals. "
                    "Generate a surgical Twitter thread. "
                    "NO hype. NO emoji spam. "
                    "Vibe: Calm, Expensive, Decisive.",
                ),
                ("user", "Brief: {brief}\nContext: {context}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(TwitterThread)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        brief = state.get("context_brief", {}).get("uvps", "No specific UVPs")
        context = state.get("research_bundle", {}).get(
            "executive_brief", "General marketing"
        )
        logger.info("Architecting Twitter viral thread...")

        thread = await self.chain.ainvoke(
            {"brief": str(brief), "context": str(context)}
        )
        logger.info("Twitter thread generation complete.")

        return {"variants": [thread.model_dump()], "current_draft": thread.hook_tweet}


class AdCopy(BaseModel):
    """SOTA structured Ad representation."""

    platform: str  # FB, Google, LinkedIn
    headline: str
    body_text: str
    call_to_action: str


class AdAnalysis(BaseModel):
    ads: List[AdCopy]


class AdArchitect:
    """
    SOTA Paid Media Production Node.
    Generates high-conversion ad copy using Gemini.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master performance marketer. "
                    "Generate exactly 3 surgical ad variations for the specified platform. "
                    "NO hype words. NO fake scarcity. "
                    "Focus on solving the ICP's burning pain points.",
                ),
                ("user", "Brief: {brief}\nICP: {icp}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(AdAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        brief = state.get("context_brief", {}).get("uvps", {})
        icp = state.get("context_brief", {}).get("icp_demographics", {})
        logger.info("Architecting high-conversion ad copy...")

        analysis = await self.chain.ainvoke({"brief": str(brief), "icp": str(icp)})
        logger.info("Ad copy generation complete.")

        return {"variants": analysis.model_dump()["ads"]}


class BlogPost(BaseModel):
    """SOTA structured Blog representation."""

    title: str
    introduction: str
    key_sections: List[Dict[str, str]]  # Section title and body
    conclusion: str


class ContentTransformer:
    """
    SOTA Editorial Production Node.
    Transforms deep research bundles into long-form, authoritative blog posts using Gemini.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master editorial lead. "
                    "Transform the research brief into a surgical, 800-word blog post. "
                    "Avoid corporate fluff. Focus on unique tactical insights.",
                ),
                ("user", "Research Brief: {brief}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(BlogPost)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        brief = state.get("research_bundle", {}).get(
            "executive_brief", "General marketing research"
        )
        logger.info("Transforming research into long-form blog post...")

        post = await self.chain.ainvoke({"brief": str(brief)})
        logger.info("Blog post generation complete.")

        return {
            "variants": [post.model_dump()],
            "current_draft": post.introduction + "\n" + post.conclusion,
        }


class ToneAdjuster:
    """
    SOTA Brand Alignment Node.
    Recursively fine-tunes copy to match the 'Calm, Expensive, Decisive' vibe.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master brand editor. Fine-tune the following copy. "
                    "Make it exactly 'Calm, Expensive, and Decisive'. "
                    "Remove all exclamation marks. Remove all hype words. "
                    "Increase lexical density. Use short, surgical sentences.",
                ),
                ("user", "Copy: {copy}"),
            ]
        )
        self.llm = llm

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        draft = state.get("current_draft", "No draft available")
        logger.info("Refining brand tone...")

        res = await self.llm.ainvoke(self.prompt.format(copy=draft))
        logger.info("Tone adjustment complete.")

        return {"current_draft": res.content}


class ImagePrompt(BaseModel):
    """SOTA structured representation of a visual prompt."""

    prompt_text: str
    negative_prompt: str
    aspect_ratio: str = "16:9"


class VisualPrompter:
    """
    SOTA Multimodal Creative Node.
    Generates surgical image prompts for DALL-E/Midjourney/Imagen based on brand vibes.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master visual director. Generate a surgical image prompt "
                    "that reflects the brand vibe: 'Calm, Expensive, Decisive'. "
                    "Style: Studio photography, high-end editorial, neutral tones.",
                ),
                ("user", "Context: {context}\nVisual Trends: {trends}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(ImagePrompt)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        context = state.get("current_draft", "Minimalist office")
        trends = state.get("research_bundle", {}).get("visual_trends", {})
        logger.info("Generating visual prompts...")

        prompt = await self.chain.ainvoke({"context": context, "trends": str(trends)})
        logger.info("Visual prompt generation complete.")

        return {"current_brief": {"image_prompt": prompt.model_dump()}}


class SVGDiagram(BaseModel):
    """SOTA structured SVG representation."""

    svg_code: str
    explanation: str
    accessibility_alt: str


class DiagramArchitect:
    """
    SOTA Visualization Node.
    Generates surgical technical diagrams (SVG) to illustrate complex marketing concepts.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master technical illustrator. Generate a surgical SVG diagram "
                    "that explains the provided concept. NO colors other than Slate and Ivory. "
                    "Use clean lines and minimalist geometric shapes.",
                ),
                ("user", "Concept: {concept}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(SVGDiagram)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        concept = state.get("current_draft", "SOTA Growth Loop")
        logger.info(f"Architecting SVG diagram for: {concept[:50]}...")

        diagram = await self.chain.ainvoke({"concept": concept})
        logger.info("SVG diagram generation complete.")

        return {"variants": [diagram.model_dump()], "final_output": diagram.svg_code}


class MultiVariantGenerator:
    """
    SOTA Parallel Production Node.
    Executes exactly 5 variants of a creative asset in parallel using Gemini.
    """

    def __init__(self, llm: any):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a surgical creative director. Generate a unique variant "
                    "of the provided post that emphasizes a different strategic angle "
                    "(e.g., speed, status, or security).",
                ),
                ("user", "Draft: {draft}"),
            ]
        )

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        import asyncio

        draft = state.get("current_draft", "Default post")
        logger.info("Generating 5 surgical creative variants in parallel...")

        # Parallel execution (SOTA)
        tasks = [self.llm.ainvoke(self.prompt.format(draft=draft)) for _ in range(5)]
        responses = await asyncio.gather(*tasks)

        variants = [
            {"variant_index": i, "content": res.content}
            for i, res in enumerate(responses)
        ]
        logger.info("Parallel variant production complete.")

        return {"variants": variants}


class CreativeLintResult(BaseModel):
    """SOTA structured linting result."""

    clean_content: str
    changes_made: List[str]
    has_prohibited_emojis: bool


class FormattingFilter:
    """
    SOTA visual integrity Node.
    Surgically removes emojis, excessive punctuation, and enforces brand formatting.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a ruthless visual editor. Clean the provided content. "
                    "ENFORCE: Zero emojis. Exactly one space after periods. "
                    "Remove all marketing 'fluff' exclamation marks.",
                ),
                ("user", "Content: {content}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(CreativeLintResult)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        content = state.get("current_draft", "No content")
        logger.info("Enforcing brand formatting and 'No Emoji' policy...")

        lint = await self.chain.ainvoke({"content": content})
        logger.info(
            f"Formatting complete. Emojis detected: {lint.has_prohibited_emojis}"
        )

        return {"current_draft": lint.clean_content}


class ImageArchitect:
    """
    SOTA Image Production Node.
    Generates high-fidelity visual assets using Gemini Nano Banana.
    """

    def __init__(self, model_tier: str = "nano"):
        from core.usage_tracker import usage_tracker
        from inference import InferenceProvider

        self.model = InferenceProvider.get_image_model(model_tier=model_tier)
        self.usage_tracker = usage_tracker

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        from utils.storage import pil_to_bytes, upload_image_to_gcs

        tenant_id = state.get("tenant_id", "default")

        # Check quota
        if not await self.usage_tracker.check_quota(tenant_id, "image"):
            logger.warning(f"Quota exceeded for tenant {tenant_id}")
            return {"error": "Image generation quota exceeded"}

        # Extract prompt from state (VisualPrompter should have run before this)
        brief = state.get("brief", {})
        image_meta = brief.get("image_prompt", {})
        image_prompt = image_meta.get("prompt_text")
        aspect_ratio = image_meta.get("aspect_ratio", "16:9")

        if not image_prompt:
            # Fallback to current_draft if no explicit image prompt
            image_prompt = state.get("current_draft", "A professional marketing asset")

        logger.info(
            f"Generating image with Nano Banana: {image_prompt[:50]} (Ratio: {aspect_ratio})..."
        )

        # Update model config with aspect ratio if supported
        from google.genai import types

        model_config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
        )

        # Generate image using direct call with custom config
        response = await self.model.ainvoke(image_prompt, config=model_config)

        if not response.images:
            logger.error("No images generated by Nano Banana")
            return {"error": "Image generation failed"}

        # Process and upload images
        image_urls = []
        for img in response.images:
            img_bytes = pil_to_bytes(img)
            url = await upload_image_to_gcs(img_bytes, tenant_id=tenant_id)
            image_urls.append(url)

        # Track usage
        await self.usage_tracker.track_usage(
            tenant_id, amount=len(image_urls), service_type="image"
        )

        logger.info(f"Generated {len(image_urls)} images.")

        return {
            "generated_assets": [
                {"family": "image", "content": url, "version": "draft"}
                for url in image_urls
            ],
            "current_draft": image_urls[0] if image_urls else None,
        }


def create_linkedin_architect(llm: any):
    return LinkedInArchitect(llm)


def create_twitter_architect(llm: any):
    return TwitterArchitect(llm)


def create_ad_architect(llm: any):
    return AdArchitect(llm)


def create_content_transformer(llm: any):
    return ContentTransformer(llm)


def create_tone_adjuster(llm: any):
    return ToneAdjuster(llm)


def create_visual_prompter(llm: any):
    return VisualPrompter(llm)


def create_image_architect(model_tier: str = "nano"):
    return ImageArchitect(model_tier=model_tier)


def create_diagram_architect(llm: any):
    return DiagramArchitect(llm)


def create_multi_variant_generator(llm: any):
    return MultiVariantGenerator(llm)


def create_formatting_filter(llm: any):
    return FormattingFilter(llm)
