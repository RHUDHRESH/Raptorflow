"""
Research workflow graph for market research and data gathering.
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from ..specialists.market_research import MarketResearchAgent
from ..state import AgentState
from ..tools.web_scraper import WebScraperTool
from ..tools.web_search import WebSearchTool


class ResearchState(AgentState):
    """Extended state for research workflow."""

    research_query: str
    research_depth: Literal["basic", "comprehensive", "deep"]
    research_categories: List[Literal["customers", "competitors", "trends", "market"]]
    sources_found: List[Dict[str, Any]]
    sources_analyzed: List[Dict[str, Any]]
    research_findings: Dict[str, Any]
    confidence_scores: Dict[str, float]
    research_status: Literal[
        "planning",
        "searching",
        "scraping",
        "analyzing",
        "synthesizing",
        "completed",
        "failed",
    ]
    search_queries: List[str]
    scraped_urls: List[str]
    synthesis_summary: str
    recommendations: List[str]


async def plan_research(state: ResearchState) -> ResearchState:
    """Plan the research approach based on query and depth."""
    try:
        query = state["research_query"]
        depth = state.get("research_depth", "comprehensive")
        categories = state.get(
            "research_categories", ["customers", "competitors", "trends", "market"]
        )

        # Generate search queries based on categories
        search_queries = []

        if "customers" in categories:
            search_queries.extend(
                [
                    f"{query} customer insights",
                    f"{query} target audience demographics",
                    f"{query} customer pain points",
                    f"{query} user behavior patterns",
                ]
            )

        if "competitors" in categories:
            search_queries.extend(
                [
                    f"{query} competitor analysis",
                    f"{query} market leaders",
                    f"{query} competitive landscape",
                    f"{query} competitor strategies",
                ]
            )

        if "trends" in categories:
            search_queries.extend(
                [
                    f"{query} market trends 2024",
                    f"{query} industry developments",
                    f"{query} emerging technologies",
                    f"{query} future predictions",
                ]
            )

        if "market" in categories:
            search_queries.extend(
                [
                    f"{query} market size",
                    f"{query} market growth",
                    f"{query} industry analysis",
                    f"{query} market opportunities",
                ]
            )

        # Adjust number of queries based on depth
        if depth == "basic":
            search_queries = search_queries[:2]
        elif depth == "comprehensive":
            search_queries = search_queries[:4]
        elif depth == "deep":
            search_queries = search_queries[:8]

        state["search_queries"] = search_queries
        state["research_status"] = "searching"

        return state
    except Exception as e:
        state["error"] = f"Research planning failed: {str(e)}"
        state["research_status"] = "failed"
        return state


async def search_sources(state: ResearchState) -> ResearchState:
    """Search for relevant sources using web search."""
    try:
        web_search_tool = WebSearchTool()
        search_queries = state.get("search_queries", [])
        all_sources = []

        for query in search_queries:
            # Perform web search
            search_result = await web_search_tool._arun(
                query=query,
                max_results=5 if state.get("research_depth") == "basic" else 10,
            )

            if search_result.get("success"):
                sources = search_result.get("data", [])
                all_sources.extend(sources)

        # Remove duplicates and limit results
        unique_sources = []
        seen_urls = set()

        for source in all_sources:
            url = source.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(source)

        # Limit based on depth
        depth = state.get("research_depth", "comprehensive")
        if depth == "basic":
            unique_sources = unique_sources[:5]
        elif depth == "comprehensive":
            unique_sources = unique_sources[:15]
        elif depth == "deep":
            unique_sources = unique_sources[:30]

        state["sources_found"] = unique_sources
        state["research_status"] = "scraping"

        return state
    except Exception as e:
        state["error"] = f"Source search failed: {str(e)}"
        state["research_status"] = "failed"
        return state


async def scrape_sources(state: ResearchState) -> ResearchState:
    """Scrape content from relevant sources."""
    try:
        web_scraper = WebScraperTool()
        sources = state.get("sources_found", [])
        scraped_content = []
        scraped_urls = []

        # Select top sources for scraping based on relevance and credibility
        top_sources = (
            sources[:10] if state.get("research_depth") == "deep" else sources[:5]
        )

        for source in top_sources:
            url = source.get("url", "")
            if not url:
                continue

            try:
                # Scrape content
                scrape_result = await web_scraper._arun(url=url, extract_text=True)

                if scrape_result.get("success"):
                    content = scrape_result.get("data", {}).get("content", "")
                    if content and len(content) > 100:  # Only keep substantial content
                        scraped_content.append(
                            {
                                "url": url,
                                "title": source.get("title", ""),
                                "content": content[:5000],  # Limit content length
                                "source_type": "web_scrape",
                                "relevance_score": source.get("relevance_score", 0.5),
                            }
                        )
                        scraped_urls.append(url)
            except Exception as e:
                # Continue with other sources if one fails
                continue

        state["sources_analyzed"] = scraped_content
        state["scraped_urls"] = scraped_urls
        state["research_status"] = "analyzing"

        return state
    except Exception as e:
        state["error"] = f"Source scraping failed: {str(e)}"
        state["research_status"] = "failed"
        return state


async def analyze_sources(state: ResearchState) -> ResearchState:
    """Analyze scraped sources and extract insights."""
    try:
        market_research_agent = MarketResearchAgent()
        sources = state.get("sources_analyzed", [])

        if not sources:
            state["error"] = "No sources to analyze"
            state["research_status"] = "failed"
            return state

        # Prepare analysis request
        analysis_request = {
            "query": state["research_query"],
            "sources": sources,
            "categories": state.get(
                "research_categories", ["customers", "competitors", "trends", "market"]
            ),
            "depth": state.get("research_depth", "comprehensive"),
        }

        # Perform analysis
        result = await market_research_agent.execute(state)

        analysis_output = result.get("output", {})
        state["research_findings"] = analysis_output.get("findings", {})
        state["confidence_scores"] = analysis_output.get("confidence_scores", {})
        state["research_status"] = "synthesizing"

        return state
    except Exception as e:
        state["error"] = f"Source analysis failed: {str(e)}"
        state["research_status"] = "failed"
        return state


async def synthesize_findings(state: ResearchState) -> ResearchState:
    """Synthesize research findings into coherent summary."""
    try:
        findings = state.get("research_findings", {})
        confidence_scores = state.get("confidence_scores", {})
        categories = state.get("research_categories", [])

        # Create synthesis summary
        summary_parts = []

        for category in categories:
            category_findings = findings.get(category, {})
            confidence = confidence_scores.get(category, 0.5)

            if category_findings:
                category_summary = (
                    f"## {category.title()} Analysis (Confidence: {confidence:.1%})\n"
                )

                if isinstance(category_findings, dict):
                    for key, value in category_findings.items():
                        if isinstance(value, list):
                            category_summary += (
                                f"- {key}: {', '.join(str(v) for v in value[:3])}\n"
                            )
                        else:
                            category_summary += f"- {key}: {value}\n"
                elif isinstance(category_findings, list):
                    category_summary += "- Key findings:\n"
                    for item in category_findings[:5]:
                        category_summary += f"  • {item}\n"
                else:
                    category_summary += f"- {category_findings}\n"

                summary_parts.append(category_summary)

        # Add overall insights
        summary_parts.append("## Key Insights\n")

        # Extract high-confidence insights
        high_confidence_insights = []
        for category, confidence in confidence_scores.items():
            if confidence > 0.7:
                category_findings = findings.get(category, {})
                if category_findings:
                    high_confidence_insights.append(
                        f"• {category.title()}: {str(category_findings)[:100]}..."
                    )

        if high_confidence_insights:
            summary_parts.extend(high_confidence_insights)

        # Generate recommendations
        recommendations = []

        # Customer-focused recommendations
        if "customers" in categories and findings.get("customers"):
            recommendations.append(
                "Focus on customer pain points identified in research"
            )

        # Competitor-focused recommendations
        if "competitors" in categories and findings.get("competitors"):
            recommendations.append("Differentiate from competitors based on analysis")

        # Trend-focused recommendations
        if "trends" in categories and findings.get("trends"):
            recommendations.append(
                "Leverage identified market trends for strategic advantage"
            )

        # Market-focused recommendations
        if "market" in categories and findings.get("market"):
            recommendations.append("Position based on market opportunities identified")

        synthesis_summary = "\n\n".join(summary_parts)

        state["synthesis_summary"] = synthesis_summary
        state["recommendations"] = recommendations
        state["research_status"] = "completed"

        return state
    except Exception as e:
        state["error"] = f"Findings synthesis failed: {str(e)}"
        state["research_status"] = "failed"
        return state


async def validate_sources(state: ResearchState) -> ResearchState:
    """Validate source credibility and relevance."""
    try:
        sources = state.get("sources_found", [])
        validated_sources = []

        for source in sources:
            # Simple validation criteria
            url = source.get("url", "")
            title = source.get("title", "")

            # Check for credible domains
            credible_domains = [
                "harvard.edu",
                "stanford.edu",
                "mit.edu",
                "gov",
                "org",
                "forbes.com",
                "wsj.com",
                "reuters.com",
                "bloomberg.com",
            ]

            credibility_score = 0.5  # Base score

            # Boost for credible domains
            for domain in credible_domains:
                if domain in url:
                    credibility_score += 0.3
                    break

            # Boost for substantial titles
            if len(title) > 10:
                credibility_score += 0.1

            # Boost for relevance score
            relevance = source.get("relevance_score", 0.5)
            credibility_score += relevance * 0.2

            # Cap at 1.0
            credibility_score = min(credibility_score, 1.0)

            source["credibility_score"] = credibility_score

            if credibility_score >= 0.3:  # Minimum threshold
                validated_sources.append(source)

        # Sort by credibility and relevance
        validated_sources.sort(
            key=lambda x: (x.get("credibility_score", 0) + x.get("relevance_score", 0))
            / 2,
            reverse=True,
        )

        state["sources_found"] = validated_sources

        return state
    except Exception as e:
        state["error"] = f"Source validation failed: {str(e)}"
        return state


def should_continue_research(state: ResearchState) -> str:
    """Determine next step in research workflow."""
    if state.get("error"):
        return END

    research_status = state.get("research_status", "planning")

    if research_status == "planning":
        return "plan"
    elif research_status == "searching":
        return "search"
    elif research_status == "scraping":
        return "scrape"
    elif research_status == "analyzing":
        return "analyze"
    elif research_status == "synthesizing":
        return "synthesize"
    elif research_status == "completed":
        return END
    elif research_status == "failed":
        return END
    else:
        return END


class ResearchGraph:
    """Research workflow graph."""

    def __init__(self):
        self.graph = None

    def create_graph(self) -> StateGraph:
        """Create the research workflow graph."""
        workflow = StateGraph(ResearchState)

        # Add nodes
        workflow.add_node("plan", plan_research)
        workflow.add_node("search", search_sources)
        workflow.add_node("scrape", scrape_sources)
        workflow.add_node("validate", validate_sources)
        workflow.add_node("analyze", analyze_sources)
        workflow.add_node("synthesize", synthesize_findings)

        # Set entry point
        workflow.set_entry_point("plan")

        # Add conditional edges
        workflow.add_conditional_edges(
            "plan", should_continue_research, {"search": "search", END: END}
        )
        workflow.add_conditional_edges(
            "search", should_continue_research, {"scrape": "scrape", END: END}
        )
        workflow.add_conditional_edges(
            "scrape", should_continue_research, {"validate": "validate", END: END}
        )
        workflow.add_conditional_edges(
            "validate", should_continue_research, {"analyze": "analyze", END: END}
        )
        workflow.add_conditional_edges(
            "analyze", should_continue_research, {"synthesize": "synthesize", END: END}
        )
        workflow.add_edge("synthesize", END)

        # Add memory checkpointing
        memory = MemorySaver()

        # Compile the graph
        self.graph = workflow.compile(checkpointer=memory)
        return self.graph

    async def conduct_research(
        self,
        query: str,
        depth: str = "comprehensive",
        categories: List[str] = None,
        workspace_id: str = "",
        user_id: str = "",
        session_id: str = "",
    ) -> Dict[str, Any]:
        """Conduct research using the workflow."""
        if not self.graph:
            self.create_graph()

        if categories is None:
            categories = ["customers", "competitors", "trends", "market"]

        # Create initial state
        initial_state = ResearchState(
            research_query=query,
            research_depth=depth,
            research_categories=categories,
            sources_found=[],
            sources_analyzed=[],
            research_findings={},
            confidence_scores={},
            research_status="planning",
            search_queries=[],
            scraped_urls=[],
            synthesis_summary="",
            recommendations=[],
            workspace_id=workspace_id,
            user_id=user_id,
            session_id=session_id,
            messages=[],
            routing_path=[],
            memory_context={},
            foundation_summary={},
            active_icps=[],
            pending_approval=False,
            error=None,
            output=None,
            tokens_used=0,
            cost_usd=0.0,
        )

        # Configure execution
        thread_config = {
            "configurable": {
                "thread_id": f"research_{session_id}",
                "checkpoint_ns": f"research_{workspace_id}",
            }
        }

        try:
            result = await self.graph.ainvoke(initial_state, config=thread_config)

            return {
                "success": True,
                "query": query,
                "research_status": result.get("research_status"),
                "sources_found": result.get("sources_found", []),
                "sources_analyzed": result.get("sources_analyzed", []),
                "research_findings": result.get("research_findings", {}),
                "confidence_scores": result.get("confidence_scores", {}),
                "synthesis_summary": result.get("synthesis_summary"),
                "recommendations": result.get("recommendations", []),
                "search_queries": result.get("search_queries", []),
                "scraped_urls": result.get("scraped_urls", []),
                "error": result.get("error"),
            }

        except Exception as e:
            return {"success": False, "error": f"Research failed: {str(e)}"}
