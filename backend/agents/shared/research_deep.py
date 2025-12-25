import json
from typing import List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from backend.core.config import get_settings
from backend.core.research_engine import ResearchEngine
from backend.core.search_provider import SearchProviderRegistry
from backend.inference import InferenceProvider


class ResearchPlan(BaseModel):
    queries: List[str] = Field(description="3-5 surgical search queries")
    focus_areas: List[str] = Field(description="Specific data points to extract")


class Evidence(BaseModel):
    claim: str
    source_url: str
    confidence: float


class DeepInsight(BaseModel):
    summary: str = Field(description="Executive summary of findings")
    evidence_bundle: List[Evidence]
    red_flags: List[str] = Field(description="Contradictions or missing info")


class ResearchDeepAgent:
    """
    A11: Research Deep.
    Structured crawl + compare sources + extract claims + citations.
    """

    def __init__(self):
        self.planner = InferenceProvider.get_model(
            model_tier="reasoning"
        ).with_structured_output(ResearchPlan)
        self.synthesizer = InferenceProvider.get_model(
            model_tier="ultra"
        ).with_structured_output(DeepInsight)
        self.engine = ResearchEngine()
        settings = get_settings()
        self.search_api = SearchProviderRegistry(settings=settings)

    async def execute(self, task: str, context: Optional[dict] = None) -> DeepInsight:
        context = context or {}
        # Step 1: Query Planning
        plan = await self.planner.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You are the RaptorFlow Lead Researcher. Create a surgical "
                        "plan to gather evidence for the user's task."
                    )
                ),
                HumanMessage(content=f"TASK: {task}\nCONTEXT: {json.dumps(context)}"),
            ]
        )

        # Step 2: Search & Scrape (Async)
        all_urls = []
        for query in plan.queries:
            links = await self.search_api.search(query)
            all_urls.extend(links)

        unique_urls = list(set(all_urls))[:10]  # Limit to top 10 for economy
        scraped_data = await self.engine.batch_fetch(unique_urls)

        # Step 3: Synthesis with RAG-style context
        system_msg = SystemMessage(
            content="""
            Synthesize the following web data into a surgical evidence bundle.
            Verify claims across multiple sources.
            If a source is low quality, ignore it.
            Always include citations.
        """
        )

        data_packet = "\n\n".join(
            [
                f"SOURCE: {d['url']}\nCONTENT: {d['content'][:3000]}"
                for d in scraped_data
            ]
        )

        return await self.synthesizer.ainvoke(
            [
                system_msg,
                HumanMessage(content=f"TASK: {task}\n\nWEB DATA:{data_packet}"),
            ]
        )
