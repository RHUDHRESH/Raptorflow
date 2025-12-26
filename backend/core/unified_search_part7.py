"""
Part 7: AI Agent-Friendly Search Interface
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module provides a clean, intuitive interface for AI agents to interact with
the unified search system, with simplified APIs and intelligent defaults.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from core.unified_search_part1 import (
    ContentType,
    SearchMode,
    SearchQuery,
    SearchResult,
    SearchSession,
)
from core.unified_search_part2 import SearchProvider, create_search_provider
from core.unified_search_part4 import ResultConsolidator
from core.unified_search_part5 import FaultTolerantExecutor
from core.unified_search_part6 import (
    DeepResearchAgent,
    ResearchDepth,
    ResearchPlan,
)

logger = logging.getLogger("raptorflow.unified_search.interface")


@dataclass
class SimpleSearchRequest:
    """Simplified search request for AI agents."""

    query: str
    mode: str = "standard"  # lightning, standard, deep, exhaustive
    max_results: int = 10
    content_types: List[str] = field(default_factory=lambda: ["web"])
    language: str = "en"
    region: str = "us"
    time_range: Optional[str] = None  # 1d, 1w, 1m, 1y
    include_images: bool = False
    include_videos: bool = False
    safe_search: bool = True

    def to_search_query(self) -> SearchQuery:
        """Convert to internal SearchQuery."""
        # Convert mode
        mode_map = {
            "lightning": SearchMode.LIGHTNING,
            "standard": SearchMode.STANDARD,
            "deep": SearchMode.DEEP,
            "exhaustive": SearchMode.EXHAUSTIVE,
        }
        search_mode = mode_map.get(self.mode.lower(), SearchMode.STANDARD)

        # Convert content types
        content_type_map = {
            "web": ContentType.WEB,
            "academic": ContentType.ACADEMIC,
            "news": ContentType.NEWS,
            "social": ContentType.SOCIAL,
            "forum": ContentType.FORUM,
            "documentation": ContentType.DOCUMENTATION,
            "ecommerce": ContentType.ECOMMERCE,
            "video": ContentType.VIDEO,
        }

        search_content_types = []
        for ct in self.content_types:
            if ct.lower() in content_type_map:
                search_content_types.append(content_type_map[ct.lower()])

        return SearchQuery(
            text=self.query,
            mode=search_mode,
            content_types=search_content_types,
            max_results=self.max_results,
            language=self.language,
            region=self.region,
            time_range=self.time_range,
            include_images=self.include_images,
            include_videos=self.include_videos,
            safe_search=self.safe_search,
        )


@dataclass
class SimpleSearchResult:
    """Simplified search result for AI agents."""

    url: str
    title: str
    content: str
    snippet: str
    relevance_score: float
    domain: str
    is_https: bool
    publish_date: Optional[str] = None
    content_type: str = "web"
    word_count: int = 0
    reading_time: int = 0
    provider: str = "unified"

    @classmethod
    def from_search_result(cls, result: SearchResult) -> "SimpleSearchResult":
        """Create from internal SearchResult."""
        return cls(
            url=result.url,
            title=result.title,
            content=result.content,
            snippet=result.snippet,
            relevance_score=result.relevance_score,
            domain=result.domain,
            is_https=result.is_https,
            publish_date=(
                result.publish_date.isoformat() if result.publish_date else None
            ),
            content_type=result.content_type.value,
            word_count=result.word_count,
            reading_time=result.reading_time_minutes,
            provider=result.provider.value,
        )


@dataclass
class SimpleResearchRequest:
    """Simplified research request for AI agents."""

    topic: str
    research_question: str
    depth: str = "moderate"  # surface, moderate, deep, exhaustive
    max_sources: int = 20
    time_limit_minutes: int = 30
    content_types: List[str] = field(default_factory=lambda: ["web"])
    verification_required: bool = True
    synthesis_format: str = "comprehensive"  # summary, detailed, comprehensive

    def to_research_plan(self) -> ResearchPlan:
        """Convert to internal ResearchPlan."""
        # Convert depth
        depth_map = {
            "surface": ResearchDepth.SURFACE,
            "moderate": ResearchDepth.MODERATE,
            "deep": ResearchDepth.DEEP,
            "exhaustive": ResearchDepth.EXHAUSTIVE,
        }
        research_depth = depth_map.get(self.depth.lower(), ResearchDepth.MODERATE)

        # Convert content types
        content_type_map = {
            "web": ContentType.WEB,
            "academic": ContentType.ACADEMIC,
            "news": ContentType.NEWS,
            "social": ContentType.SOCIAL,
            "forum": ContentType.FORUM,
            "documentation": ContentType.DOCUMENTATION,
            "ecommerce": ContentType.ECOMMERCE,
            "video": ContentType.VIDEO,
        }

        research_content_types = []
        for ct in self.content_types:
            if ct.lower() in content_type_map:
                research_content_types.append(content_type_map[ct.lower()])

        return ResearchPlan(
            topic=self.topic,
            research_question=self.research_question,
            depth=research_depth,
            phases=["planning", "discovery", "extraction", "verification", "synthesis"],
            max_sources=self.max_sources,
            time_limit_minutes=self.time_limit_minutes,
            content_types=research_content_types,
            quality_threshold=0.6,
            verification_required=self.verification_required,
            synthesis_format=self.synthesis_format,
        )


@dataclass
class SimpleResearchReport:
    """Simplified research report for AI agents."""

    topic: str
    research_question: str
    executive_summary: str
    key_findings: List[Dict[str, Any]]
    detailed_analysis: str
    sources: List[SimpleSearchResult]
    confidence_score: float
    completeness_score: float
    research_duration_minutes: int
    recommendations: List[str]
    limitations: List[str]

    @classmethod
    def from_research_report(cls, report) -> "SimpleResearchReport":
        """Create from internal ResearchReport."""
        simple_sources = [
            SimpleSearchResult.from_search_result(s) for s in report.sources
        ]

        simple_findings = []
        for finding in report.key_findings:
            simple_findings.append(
                {
                    "content": finding.content,
                    "source_url": finding.source_url,
                    "source_title": finding.source_title,
                    "confidence": finding.confidence,
                    "relevance": finding.relevance,
                    "factuality": finding.factuality,
                    "verification_status": finding.verification_status,
                }
            )

        return cls(
            topic=report.topic,
            research_question=report.research_question,
            executive_summary=report.executive_summary,
            key_findings=simple_findings,
            detailed_analysis=report.detailed_analysis,
            sources=simple_sources,
            confidence_score=report.confidence_score,
            completeness_score=report.completeness_score,
            research_duration_minutes=report.research_duration_minutes,
            recommendations=report.recommendations,
            limitations=report.limitations,
        )


class UnifiedSearchInterface:
    """Main interface for AI agents to interact with the unified search system."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.consolidator = ResultConsolidator()
        self.fault_executor = FaultTolerantExecutor()
        self.deep_research_agent = DeepResearchAgent()

        # Initialize providers
        self.providers = {}
        self._initialize_providers()

        # Search statistics
        self.search_stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "total_research_requests": 0,
            "successful_research": 0,
            "failed_research": 0,
        }

    def _initialize_providers(self):
        """Initialize search providers based on configuration."""
        provider_configs = {
            SearchProvider.NATIVE: {
                "brave_api_key": self.config.get("brave_api_key"),
                "serper_api_key": self.config.get("serper_api_key"),
            },
            SearchProvider.SERPER: {
                "serper_api_key": self.config.get("serper_api_key")
            },
        }

        for provider_type, config in provider_configs.items():
            try:
                provider = create_search_provider(provider_type, config)
                self.providers[provider_type] = provider
                logger.info(f"Initialized {provider_type.value} provider")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize {provider_type.value} provider: {e}"
                )

    async def search(self, request: SimpleSearchRequest) -> List[SimpleSearchResult]:
        """Perform search using simplified interface."""
        self.search_stats["total_searches"] += 1

        try:
            # Convert to internal query
            query = request.to_search_query()

            # Execute search across providers
            provider_results = {}

            for provider_type, provider in self.providers.items():
                try:
                    results = await self.fault_executor.execute_with_fault_tolerance(
                        provider_type, provider.search, query
                    )
                    provider_results[provider_type] = results
                except Exception as e:
                    logger.warning(f"Provider {provider_type.value} failed: {e}")
                    continue

            # Consolidate results
            if provider_results:
                consolidated_results = self.consolidator.consolidate_results(
                    provider_results, query
                )
            else:
                consolidated_results = []

            # Convert to simple results
            simple_results = [
                SimpleSearchResult.from_search_result(r) for r in consolidated_results
            ]

            self.search_stats["successful_searches"] += 1
            logger.info(f"Search completed: {len(simple_results)} results")

            return simple_results

        except Exception as e:
            self.search_stats["failed_searches"] += 1
            logger.error(f"Search failed: {e}")
            raise

    async def research(self, request: SimpleResearchRequest) -> SimpleResearchReport:
        """Perform deep research using simplified interface."""
        self.search_stats["total_research_requests"] += 1

        try:
            # Convert to internal plan
            plan = request.to_research_plan()

            # Conduct research
            report = await self.deep_research_agent.conduct_research(plan)

            # Convert to simple report
            simple_report = SimpleResearchReport.from_research_report(report)

            self.search_stats["successful_research"] += 1
            logger.info(
                f"Research completed: {len(simple_report.key_findings)} findings"
            )

            return simple_report

        except Exception as e:
            self.search_stats["failed_research"] += 1
            logger.error(f"Research failed: {e}")
            raise

    async def quick_search(
        self, query: str, max_results: int = 5
    ) -> List[SimpleSearchResult]:
        """Quick search with minimal parameters."""
        request = SimpleSearchRequest(
            query=query, mode="lightning", max_results=max_results
        )
        return await self.search(request)

    async def comprehensive_search(
        self, query: str, max_results: int = 20
    ) -> List[SimpleSearchResult]:
        """Comprehensive search with high quality results."""
        request = SimpleSearchRequest(
            query=query,
            mode="deep",
            max_results=max_results,
            content_types=["web", "academic", "news"],
        )
        return await self.search(request)

    async def news_search(
        self, query: str, max_results: int = 10, time_range: str = "1w"
    ) -> List[SimpleSearchResult]:
        """Search for news content."""
        request = SimpleSearchRequest(
            query=query,
            mode="standard",
            max_results=max_results,
            content_types=["news"],
            time_range=time_range,
        )
        return await self.search(request)

    async def academic_search(
        self, query: str, max_results: int = 15
    ) -> List[SimpleSearchResult]:
        """Search for academic content."""
        request = SimpleSearchRequest(
            query=query,
            mode="deep",
            max_results=max_results,
            content_types=["academic", "web"],
        )
        return await self.search(request)

    async def quick_research(self, topic: str, question: str) -> SimpleResearchReport:
        """Quick research with moderate depth."""
        request = SimpleResearchRequest(
            topic=topic,
            research_question=question,
            depth="moderate",
            max_sources=10,
            time_limit_minutes=15,
        )
        return await self.research(request)

    async def deep_research(self, topic: str, question: str) -> SimpleResearchReport:
        """Deep research with comprehensive analysis."""
        request = SimpleResearchRequest(
            topic=topic,
            research_question=question,
            depth="deep",
            max_sources=30,
            time_limit_minutes=60,
            verification_required=True,
            content_types=["web", "academic", "news"],
        )
        return await self.research(request)

    async def exhaustive_research(
        self, topic: str, question: str
    ) -> SimpleResearchReport:
        """Exhaustive research with maximum depth."""
        request = SimpleResearchRequest(
            topic=topic,
            research_question=question,
            depth="exhaustive",
            max_sources=50,
            time_limit_minutes=120,
            verification_required=True,
            content_types=["web", "academic", "news", "forum", "documentation"],
        )
        return await self.research(request)

    def get_search_stats(self) -> Dict[str, Any]:
        """Get search statistics."""
        return self.search_stats.copy()

    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers."""
        status = {}

        for provider_type, provider in self.providers.items():
            status[provider_type.value] = {
                "available": provider.is_available,
                "success_rate": provider.get_success_rate(),
                "total_requests": provider.total_requests,
                "consecutive_failures": provider.consecutive_failures,
            }

        return status

    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check."""
        health = {
            "status": "healthy",
            "providers": self.get_provider_status(),
            "search_stats": self.get_search_stats(),
            "timestamp": datetime.now().isoformat(),
        }

        # Check if any providers are unhealthy
        unhealthy_providers = [
            name
            for name, info in health["providers"].items()
            if not info["available"] or info["consecutive_failures"] >= 3
        ]

        if unhealthy_providers:
            health["status"] = "degraded"
            health["unhealthy_providers"] = unhealthy_providers

        # Check success rates
        total_searches = self.search_stats["total_searches"]
        if total_searches > 0:
            success_rate = self.search_stats["successful_searches"] / total_searches
            if success_rate < 0.8:
                health["status"] = "unhealthy"
                health["search_success_rate"] = success_rate

        return health


# Global interface instance
unified_search_interface = UnifiedSearchInterface()


# Convenience functions for direct usage
async def search(
    query: str, mode: str = "standard", max_results: int = 10
) -> List[SimpleSearchResult]:
    """Simple search function."""
    request = SimpleSearchRequest(query=query, mode=mode, max_results=max_results)
    return await unified_search_interface.search(request)


async def quick_search(query: str, max_results: int = 5) -> List[SimpleSearchResult]:
    """Quick search function."""
    return await unified_search_interface.quick_search(query, max_results)


async def research(
    topic: str, question: str, depth: str = "moderate"
) -> SimpleResearchReport:
    """Simple research function."""
    request = SimpleResearchRequest(
        topic=topic, research_question=question, depth=depth
    )
    return await unified_search_interface.research(request)


async def quick_research(topic: str, question: str) -> SimpleResearchReport:
    """Quick research function."""
    return await unified_search_interface.quick_research(topic, question)


# Example usage patterns
"""
# Quick search
results = await quick_search("artificial intelligence trends 2024")

# Comprehensive search
results = await comprehensive_search("machine learning applications", max_results=20)

# News search
news_results = await news_search("climate change", time_range="1w")

# Academic search
academic_results = await academic_search("quantum computing")

# Quick research
report = await quick_research("renewable energy", "What are the latest developments in solar power?")

# Deep research
report = await deep_research("blockchain technology", "How is blockchain being used in supply chain management?")

# Exhaustive research
report = await exhaustive_research("artificial general intelligence", "What are the current challenges and prospects for AGI?")
"""
