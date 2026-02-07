import json
import logging
from typing import Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from core.config import get_settings
from core.gap_planner import build_gap_queries, evaluate_dossier_gaps
from core.research_engine import ResearchEngine, SearchProvider
from inference import InferenceProvider
from models.dossier_schema import DEFAULT_DOSSIER_SCHEMA, build_dossier_model

logger = logging.getLogger("raptorflow.research_deep")


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
        self.dossier_extractor = InferenceProvider.get_model(
            model_tier="reasoning"
        ).with_structured_output(build_dossier_model(DEFAULT_DOSSIER_SCHEMA))
        self.engine = ResearchEngine()
        settings = get_settings()
        self.search_api = SearchProvider(api_key=settings.SERPER_API_KEY or "")

    @staticmethod
    def _is_missing_value(value: object) -> bool:
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip()
        if isinstance(value, (list, tuple, set, dict)):
            return len(value) == 0
        return False

    def _merge_dossier_data(
        self, existing: Dict[str, object], updates: Dict[str, object]
    ) -> Dict[str, object]:
        merged = dict(existing)
        for key, value in updates.items():
            if self._is_missing_value(value):
                continue
            current = merged.get(key)
            if self._is_missing_value(current):
                merged[key] = value
                continue
            if isinstance(current, list) and isinstance(value, list):
                merged[key] = sorted(set(current + value))
        return merged

    async def execute(self, task: str, context: Optional[dict] = None) -> DeepInsight:
        context = context or {}
        dossier_data: Dict[str, object] = dict(context.get("dossier_data", {}))
        company_name = context.get("company_name") or task
        max_depth = context.get("max_depth", 3)
        research_logs: List[str] = []

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

        missing_fields, _, gap_notes = evaluate_dossier_gaps(dossier_data)
        depth = 0
        scraped_data: List[Dict[str, str]] = []

        while depth < max_depth:
            if missing_fields:
                gap_queries = build_gap_queries(company_name, missing_fields, gap_notes)
                combined_queries = list(dict.fromkeys(plan.queries + gap_queries))
                research_logs.append(
                    f"Depth {depth}: {len(missing_fields)} gaps detected "
                    f"({', '.join(missing_fields)})."
                )
                logger.info(research_logs[-1])
            else:
                research_logs.append(
                    f"Depth {depth}: No dossier gaps detected. Halting research loop."
                )
                logger.info(research_logs[-1])
                break

            # Step 2: Search & Scrape (Async)
            all_urls = []
            for query in combined_queries:
                links = await self.search_api.search(query)
                all_urls.extend(links)

            unique_urls = list(dict.fromkeys(all_urls))[:10]  # Limit to top 10
            scraped_data = await self.engine.batch_fetch(unique_urls)

            # Step 3: Extract dossier fields from web data
            data_packet = "\n\n".join(
                [
                    f"SOURCE: {d['url']}\nCONTENT: {d['content'][:3000]}"
                    for d in scraped_data
                ]
            )

            extraction = await self.dossier_extractor.ainvoke(
                [
                    SystemMessage(
                        content=(
                            "Extract dossier fields from the web data. "
                            "Return only fields with high confidence."
                        )
                    ),
                    HumanMessage(
                        content=(
                            f"TASK: {task}\nCOMPANY: {company_name}\n\nWEB DATA:{data_packet}"
                        )
                    ),
                ]
            )

            dossier_data = self._merge_dossier_data(
                dossier_data, extraction.model_dump()
            )
            missing_fields, _, gap_notes = evaluate_dossier_gaps(dossier_data)
            research_logs.append(
                f"Depth {depth}: Remaining gaps "
                f"({len(missing_fields)}): {', '.join(missing_fields) or 'none'}."
            )
            logger.info(research_logs[-1])

            if not missing_fields:
                research_logs.append(f"Depth {depth}: All dossier gaps resolved.")
                logger.info(research_logs[-1])
                break

            depth += 1

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
