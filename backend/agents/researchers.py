import logging
from typing import Dict, List, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from db import get_memory, save_entity, summarize_recursively
from models.cognitive import hydrate_shared_learnings

logger = logging.getLogger("raptorflow.researchers.reddit")


class RedditInsight(BaseModel):
    """SOTA structured pain-point representation."""

    pain_point: str = Field(
        description="The specific user problem or frustration found."
    )
    sentiment: str = Field(
        description="The emotional tone (e.g., angry, confused, hopeful)."
    )
    evidence_quote: str = Field(
        description="A direct quote or paraphrase from the data."
    )


class RedditAnalysis(BaseModel):
    """Aggregate insights from social research."""

    insights: List[RedditInsight] = Field(
        description="List of extracted customer insights."
    )


class RedditSentimentAnalyst:
    """
    SOTA Reddit Analysis Node.
    Extracts 'unfiltered' customer pain points from raw social data.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master social listening specialist. "
                    "Analyze the following raw social data and extract specific, "
                    "unfiltered customer pain points and their sentiments.",
                ),
                ("user", "Data: {data}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(RedditAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        # In a real SOTA graph, 'raw_research_data' would be populated by a search tool
        raw_data = state.get("research_bundle", {}).get(
            "raw_social_data", "No data available"
        )
        logger.info("Analyzing Reddit sentiment...")

        analysis = await self.chain.ainvoke({"data": raw_data})
        logger.info(
            f"Reddit analysis complete. Found {len(analysis.insights)} insights."
        )

        return {"research_bundle": {"social_insights": analysis.model_dump()}}


class LinkedInProfile(BaseModel):
    """SOTA structured representation of a thought leader."""

    name: str = Field(description="Name of the thought leader.")
    key_themes: List[str] = Field(description="Top 3-5 recurring topics they discuss.")
    authority_score: float = Field(description="Score between 0 and 1.")


class LinkedInAnalysis(BaseModel):
    """Aggregate insights from LinkedIn research."""

    profiles: List[LinkedInProfile] = Field(
        description="List of analyzed thought leaders."
    )


class LinkedInProfiler:
    """
    SOTA LinkedIn Analysis Node.
    Maps out thought leadership and recurring themes in a specific niche.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert executive headhunter and trend analyst. "
                    "Analyze the following data and profile the top thought leaders "
                    "and their key strategic themes.",
                ),
                ("user", "Data: {data}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(LinkedInAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        raw_data = state.get("research_bundle", {}).get(
            "raw_linkedin_data", "No data available"
        )
        logger.info("Profiling LinkedIn thought leaders...")

        analysis = await self.chain.ainvoke({"data": raw_data})
        logger.info(
            f"LinkedIn profiling complete. Profiled {len(analysis.profiles)} leaders."
        )

        return {"research_bundle": {"linkedin_insights": analysis.model_dump()}}


class CompetitorPlan(BaseModel):
    """SOTA structured representation of a competitor plan."""

    name: str
    price: str
    features: List[str]


class CompetitorAnalysis(BaseModel):
    """Aggregate insights from competitor research."""

    brand_name: str
    plans: List[CompetitorPlan]
    unique_selling_points: List[str]


class CompetitorFeatureMapper:
    """
    SOTA Competitor Mapping Node.
    Extracts structured feature sets and pricing from raw competitor data.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a surgical product marketer. "
                    "Extract the plan names, prices, and features for the following competitor.",
                ),
                ("user", "Data: {data}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(CompetitorAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        raw_data = state.get("research_bundle", {}).get(
            "raw_competitor_data", "No data available"
        )
        logger.info("Mapping competitor features...")

        analysis = await self.chain.ainvoke({"data": raw_data})
        logger.info(f"Mapped features for brand: {analysis.brand_name}")

        return {"research_bundle": {"competitor_map": analysis.model_dump()}}


class EvidenceBundle(BaseModel):
    """SOTA structured representation of a consolidated research packet."""

    topic: str
    key_findings: List[str]
    raw_sources: List[str]
    confidence_score: float


class EvidenceBundler:
    """
    SOTA Research State Management Node.
    Consolidates raw search results into structured, validated JSON packets.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a research analyst. Consolidate the following raw search data "
                    "into a structured 'Evidence Bundle' for the strategy team.",
                ),
                ("user", "Raw Data: {data}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(EvidenceBundle)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        bundle_data = state.get("research_bundle", {})
        logger.info("Bundling research evidence...")

        # In production, we'd consolidate all raw_* fields from the bundle
        consolidated = await self.chain.ainvoke({"data": str(bundle_data)})
        logger.info(f"Evidence bundle created for topic: {consolidated.topic}")

        return {"research_bundle": {"final_evidence": consolidated.model_dump()}}


class SourceValidation(BaseModel):
    """SOTA structured source evaluation."""

    url: str
    credibility_score: float
    reasoning: str
    is_trusted: bool


class ValidatorOutput(BaseModel):
    validations: List[SourceValidation]


class SourceValidator:
    """
    SOTA Credibility Assessment Node.
    Ranks search results by domain authority and factual density.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a factual verification specialist. "
                    "Evaluate the credibility of the following URLs based on "
                    "their domain authority and potential for bias.",
                ),
                ("user", "URLs: {urls}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(ValidatorOutput)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        urls = state.get("research_bundle", {}).get("raw_urls", [])
        logger.info(f"Validating {len(urls)} sources...")

        output = await self.chain.ainvoke({"urls": str(urls)})
        logger.info("Source validation complete.")

        return {"research_bundle": {"validations": output.model_dump()}}


class MarketTrend(BaseModel):
    """SOTA structured market trend representation."""

    name: str
    strength: float  # 0 to 1
    signal: str  # The evidence or 'why' behind the trend


class TrendAnalysis(BaseModel):
    trends: List[MarketTrend]


class TrendExtractor:
    """
    SOTA Trend Synthesis Node.
    Identifies common patterns and emerging signals across research bundles.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master trend forecaster. "
                    "Analyze the following research evidence and extract the "
                    "top 3-5 emerging market trends and their relative strengths.",
                ),
                ("user", "Evidence: {evidence}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(TrendAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        evidence = state.get("research_bundle", {}).get("final_evidence", {})
        logger.info("Extracting market trends...")

        analysis = await self.chain.ainvoke({"evidence": str(evidence)})
        logger.info(
            f"Trend extraction complete. Identified {len(analysis.trends)} trends."
        )

        return {"research_bundle": {"trends": analysis.model_dump()}}


class MarketGap(BaseModel):
    """SOTA structured market gap representation."""

    description: str
    severity: float  # 0 to 1 (importance of the gap)
    opportunity: str  # How our brand can fill it


class GapAnalysis(BaseModel):
    gaps: List[MarketGap]


class GapFinder:
    """
    SOTA White-space Identification Node.
    Identifies what competitors are NOT saying or doing.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master of competitive differentiation. "
                    "Analyze the competitor data and find exactly 3-5 high-leverage "
                    "market gaps where our brand can win.",
                ),
                ("user", "Competitor Data: {data}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(GapAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        comp_data = state.get("research_bundle", {}).get("competitor_map", {})
        logger.info("Finding market gaps...")

        analysis = await self.chain.ainvoke({"data": str(comp_data)})
        logger.info(
            f"Gap identification complete. Found {len(analysis.gaps)} opportunities."
        )

        return {"research_bundle": {"gaps": analysis.model_dump()}}


class CompetitorTracker:
    """
    SOTA Entity Memory Node.
    Syncs identified competitors from research into the permanent entity DB.
    """

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        workspace_id = state.get("workspace_id")
        comp_map = state.get("research_bundle", {}).get("competitor_map", {})

        if not comp_map or "brand_name" not in comp_map:
            logger.warning("No competitor data to track.")
            return {}

        logger.info(
            f"Syncing competitor '{comp_map['brand_name']}' to permanent memory..."
        )

        # In production, we'd generate a real embedding for the description
        dummy_embedding = [0.1] * 768

        await save_entity(
            workspace_id=workspace_id,
            name=comp_map["brand_name"],
            entity_type="competitor",
            description=f"Automated profile for {comp_map['brand_name']}",
            embedding=dummy_embedding,
            metadata=comp_map,
        )

        return {"status": "competitor_sync_complete"}


def create_competitor_tracker():
    return CompetitorTracker()


class BrandHistoryContextualizer:
    """
    SOTA Contextual Memory Node.
    Retrieves historical project data to inform current research and strategy.
    """

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        workspace_id = state.get("workspace_id")
        logger.info(f"Retrieving brand history for workspace: {workspace_id}")

        # In production, we'd generate an embedding for raw_prompt here
        # For the skeleton, we pass a dummy embedding
        dummy_embedding = [0.1] * 768

        # Pull episodic memory (past events/projects)
        history = await get_memory(
            workspace_id=workspace_id,
            query_embedding=dummy_embedding,
            memory_type="episodic",
            limit=3,
        )

        logger.info(f"Retrieved {len(history)} historical context items.")
        return {"research_bundle": {"historical_context": history}}


def create_brand_history_contextualizer():
    return BrandHistoryContextualizer()


class ResearchSummarizer:
    """
    SOTA Research Condensation Node.
    Uses recursive summarization to distill massive research bundles into surgical briefs.
    """

    def __init__(self, llm: any):
        self.llm = llm

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        evidence = state.get("research_bundle", {}).get("final_evidence", {})
        logger.info("Summarizing research bundle...")

        brief = await summarize_recursively(str(evidence), self.llm, max_tokens=1000)
        logger.info("Executive brief generated.")

        return {"research_bundle": {"executive_brief": brief}}


def create_research_summarizer(llm: any):
    return ResearchSummarizer(llm)


class VisualStyle(BaseModel):
    """SOTA structured representation of aesthetic trends."""

    aesthetic: str
    color_palette: List[str]
    signal: str


class VisualAnalysis(BaseModel):
    styles: List[VisualStyle]


class VisualTrendAnalyzer:
    """
    SOTA Multimodal Synthesis Node.
    Analyzes competitor image styles and brand aesthetics via Vision models.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master visual creative director. "
                    "Analyze the following visual data and identify emerging "
                    "aesthetic themes and color signals.",
                ),
                ("user", "Visual Data: {data}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(VisualAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        images = state.get("research_bundle", {}).get("raw_images", [])
        logger.info(f"Analyzing {len(images)} images multimodal style...")

        analysis = await self.chain.ainvoke({"data": str(images)})
        logger.info("Visual trend analysis complete.")

        return {"research_bundle": {"visual_trends": analysis.model_dump()}}


class PositioningMap(BaseModel):
    """SOTA structured representation of competitive positioning."""

    x_axis: str
    y_axis: str
    competitor_coordinates: Dict[
        str, Dict[str, float]
    ]  # e.g., {"CompA": {"x": 0.5, "y": 0.2}}


class PositioningMapper:
    """
    SOTA Competitive Mapping Node.
    Generates a 2D map of competitor positioning based on research.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master of strategic market mapping. "
                    "Analyze the competitor data and define exactly 2 relevant axes "
                    "for differentiation. Then map all competitors onto this 2D space.",
                ),
                ("user", "Competitor Data: {data}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(PositioningMap)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        comp_data = state.get("research_bundle", {}).get("competitor_map", {})
        logger.info("Mapping market positioning...")

        analysis = await self.chain.ainvoke({"data": str(comp_data)})
        logger.info(
            f"Market mapping complete for {len(analysis.competitor_coordinates)} entities."
        )

        return {"research_bundle": {"positioning_map": analysis.model_dump()}}


class SWOTAnalysis(BaseModel):
    """SOTA structured SWOT representation."""

    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]


class SWOTAnalyzer:
    """
    SOTA Strategic Analysis Node.
    Generates a full SWOT analysis for the brand based on research evidence.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master strategic consultant. "
                    "Analyze the following research evidence and generate a surgical "
                    "SWOT analysis (exactly 3-5 points per quadrant).",
                ),
                ("user", "Evidence: {evidence}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(SWOTAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        evidence = state.get("research_bundle", {}).get("final_evidence", {})
        logger.info("Generating SWOT analysis...")

        analysis = await self.chain.ainvoke({"evidence": str(evidence)})
        logger.info("SWOT analysis complete.")

        return {"research_bundle": {"swot": analysis.model_dump()}}


class ResearchQAPass(BaseModel):
    """SOTA structured research evaluation."""

    is_high_quality: bool
    score: float  # 0 to 1
    issues: List[str]
    improvement_suggestions: List[str]


class ResearchQAGuard:
    """
    SOTA Research Verification Node.
    Ensures research data is non-redundant, factually dense, and ready for strategy.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a ruthless editorial research lead. "
                    "Audit the following research brief for quality, "
                    "factual density, and potential hallucinations.",
                ),
                ("user", "Brief: {brief}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(ResearchQAPass)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        state = await hydrate_shared_learnings(state)
        brief = state.get("research_bundle", {}).get("executive_brief", "")
        logger.info("Auditing research quality...")

        output = await self.chain.ainvoke({"brief": brief})
        logger.info(f"Research audit complete. Quality score: {output.score}")

        return {"research_bundle": {"qa_pass": output.model_dump()}}


def create_reddit_analyst(llm: any):
    return RedditSentimentAnalyst(llm)


def create_linkedin_profiler(llm: any):
    return LinkedInProfiler(llm)


def create_competitor_mapper(llm: any):
    return CompetitorFeatureMapper(llm)


def create_evidence_bundler(llm: any):
    return EvidenceBundler(llm)


def create_source_validator(llm: any):
    return SourceValidator(llm)


def create_trend_extractor(llm: any):
    return TrendExtractor(llm)


def create_gap_finder(llm: any):
    return GapFinder(llm)


def create_visual_trend_analyzer(llm: any):
    return VisualTrendAnalyzer(llm)


def create_positioning_mapper(llm: any):
    return PositioningMapper(llm)


def create_swot_analyzer(llm: any):
    return SWOTAnalyzer(llm)


def create_research_qa_guard(llm: any):
    return ResearchQAGuard(llm)
