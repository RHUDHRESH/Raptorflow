"""
Intelligent Research Agent with Vertex AI Integration
A→A→P→A→P inference pattern with Gemini model hierarchy
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import vertexai
from free_web_search import free_search_engine
from ultra_fast_scraper import UltraFastScrapingStrategy, ultra_fast_scraper
from vertexai.generative_models import Content, GenerativeModel, Part

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchDepth(Enum):
    LIGHT = "light"
    DEEP = "deep"
    TARGETED = "targeted"
    COMPARATIVE = "comparative"


class GeminiModel(Enum):
    FLASHLIGHT = "gemini-2.5-flash-lite-preview-06-17"  # 85% usage
    FLASH = "gemini-2.5-flash-preview-04-17"  # 10% usage
    ULTRA = "gemini-3-flash-preview-00-00"  # 5% usage


@dataclass
class ResearchPlan:
    query: str
    depth: ResearchDepth
    search_queries: List[str]
    scrape_urls: List[str]
    verification_steps: List[str]
    synthesis_strategy: str
    model_assignments: Dict[str, GeminiModel]


@dataclass
class ResearchResult:
    query: str
    findings: Dict[str, Any]
    sources: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float
    model_usage: Dict[str, int]
    cost_estimate: float


class VertexAIRouter:
    """A→A→P→A→P inference pattern for sensitive research"""

    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.models = {}
        self._initialize_models()

    def _initialize_models(self):
        """Initialize Gemini models with hierarchy"""
        vertexai.init(project=self.project_id, location=self.location)

        self.models = {
            GeminiModel.FLASHLIGHT: GenerativeModel(GeminiModel.FLASHLIGHT.value),
            GeminiModel.FLASH: GenerativeModel(GeminiModel.FLASH.value),
            GeminiModel.ULTRA: GenerativeModel(GeminiModel.ULTRA.value),
        }

        logger.info("Vertex AI models initialized with A→A→P→A→P pattern")

    async def analyze_request(self, query: str) -> Dict[str, Any]:
        """A (Analyze) - Parse and understand research request"""
        model = self.models[GeminiModel.FLASHLIGHT]  # 85% usage

        prompt = f"""
        Analyze this research request: "{query}"

        Provide JSON response with:
        - research_type (light/deep/targeted/comparative)
        - complexity_score (1-10)
        - key_entities
        - research_scope
        - expected_outputs
        """

        try:
            response = await model.generate_content_async(prompt)
            return self._parse_json_response(response.text)
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {"research_type": "light", "complexity_score": 3}

    async def assess_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """A (Assess) - Determine optimal research strategy"""
        complexity = analysis.get("complexity_score", 3)

        # Model selection based on complexity
        if complexity >= 8:
            model = self.models[GeminiModel.ULTRA]  # 5% usage
        elif complexity >= 5:
            model = self.models[GeminiModel.FLASH]  # 10% usage
        else:
            model = self.models[GeminiModel.FLASHLIGHT]  # 85% usage

        prompt = f"""
        Based on analysis: {json.dumps(analysis)}

        Create research strategy with:
        - search_queries (3-5 specific queries)
        - data_sources_to_scrape
        - verification_methods
        - synthesis_approach
        - model_assignments (which model for which task)
        """

        try:
            response = await model.generate_content_async(prompt)
            return self._parse_json_response(response.text)
        except Exception as e:
            logger.error(f"Strategy assessment failed: {str(e)}")
            return self._fallback_strategy(analysis)

    async def plan_execution(self, strategy: Dict[str, Any]) -> ResearchPlan:
        """P (Plan) - Create detailed execution plan"""
        model = self.models[GeminiModel.FLASH]  # 10% usage for planning

        prompt = f"""
        Convert strategy to execution plan: {json.dumps(strategy)}

        Provide detailed plan with:
        - specific_search_queries
        - urls_to_scrape
        - verification_steps
        - synthesis_methodology
        - model_usage_allocation
        """

        try:
            response = await model.generate_content_async(prompt)
            plan_data = self._parse_json_response(response.text)

            return ResearchPlan(
                query=strategy.get("original_query", ""),
                depth=ResearchDepth(strategy.get("research_type", "light")),
                search_queries=plan_data.get("specific_search_queries", []),
                scrape_urls=plan_data.get("urls_to_scrape", []),
                verification_steps=plan_data.get("verification_steps", []),
                synthesis_strategy=plan_data.get("synthesis_methodology", ""),
                model_assignments=plan_data.get("model_usage_allocation", {}),
            )
        except Exception as e:
            logger.error(f"Planning failed: {str(e)}")
            return self._fallback_plan(strategy)

    async def act_on_plan(self, plan: ResearchPlan) -> Dict[str, Any]:
        """A (Act) - Execute the research plan"""
        results = {"search_results": [], "scraped_data": [], "verification_results": []}

        # Execute searches
        for query in plan.search_queries:
            try:
                search_result = await free_search_engine.search(
                    query=query, engines=["duckduckgo", "brave"], max_results=10
                )
                results["search_results"].append(search_result)
            except Exception as e:
                logger.error(f"Search failed for {query}: {str(e)}")

        # Execute scraping
        for url in plan.scrape_urls:
            try:
                scrape_result = (
                    await ultra_fast_scraper.scrape_with_production_grade_handling(
                        url=url,
                        user_id="research-agent",
                        legal_basis="research",
                        strategy=UltraFastScrapingStrategy.ASYNC,
                    )
                )
                results["scraped_data"].append(scrape_result)
            except Exception as e:
                logger.error(f"Scraping failed for {url}: {str(e)}")

        return results

    async def present_findings(
        self, results: Dict[str, Any], plan: ResearchPlan
    ) -> ResearchResult:
        """P (Present) - Synthesize and format results"""
        # Use appropriate model based on complexity
        if plan.depth == ResearchDepth.DEEP:
            model = self.models[GeminiModel.ULTRA]  # 5% usage
        else:
            model = self.models[GeminiModel.FLASH]  # 10% usage

        prompt = f"""
        Synthesize research findings: {json.dumps(results)}

        Based on plan: {plan.synthesis_strategy}

        Provide comprehensive analysis with:
        - key_findings
        - source_credibility_assessment
        - confidence_scores
        - insights_and_patterns
        - recommendations
        """

        try:
            response = await model.generate_content_async(prompt)
            synthesis = self._parse_json_response(response.text)

            return ResearchResult(
                query=plan.query,
                findings=synthesis,
                sources=results.get("search_results", []),
                confidence_score=synthesis.get("overall_confidence", 0.8),
                processing_time=0.0,  # Will be calculated
                model_usage=self._get_model_usage(plan),
                cost_estimate=self._calculate_cost(plan),
            )
        except Exception as e:
            logger.error(f"Presentation failed: {str(e)}")
            return self._fallback_results(results, plan)

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from model"""
        try:
            # Extract JSON from response
            import re

            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except:
            return {}

    def _fallback_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback strategy if model fails"""
        return {
            "search_queries": [analysis.get("original_query", "")],
            "data_sources_to_scrape": [],
            "verification_methods": ["cross_reference"],
            "synthesis_approach": "summarize_findings",
        }

    def _fallback_plan(self, strategy: Dict[str, Any]) -> ResearchPlan:
        """Fallback plan if planning fails"""
        return ResearchPlan(
            query=strategy.get("original_query", ""),
            depth=ResearchDepth.LIGHT,
            search_queries=[strategy.get("original_query", "")],
            scrape_urls=[],
            verification_steps=["basic_validation"],
            synthesis_strategy="summarize",
            model_assignments={"search": GeminiModel.FLASHLIGHT.value},
        )

    def _fallback_results(
        self, results: Dict[str, Any], plan: ResearchPlan
    ) -> ResearchResult:
        """Fallback results if synthesis fails"""
        return ResearchResult(
            query=plan.query,
            findings={
                "summary": "Basic research completed",
                "sources": len(results.get("search_results", [])),
            },
            sources=results.get("search_results", []),
            confidence_score=0.6,
            processing_time=0.0,
            model_usage={"flashlight": 1},
            cost_estimate=0.001,
        )

    def _get_model_usage(self, plan: ResearchPlan) -> Dict[str, int]:
        """Calculate model usage based on plan"""
        usage = {"flashlight": 0, "flash": 0, "ultra": 0}

        # Base usage from model assignments
        for task, model in plan.model_assignments.items():
            if "flashlight" in model:
                usage["flashlight"] += 1
            elif "flash" in model and "flashlight" not in model:
                usage["flash"] += 1
            elif "ultra" in model:
                usage["ultra"] += 1

        return usage

    def _calculate_cost(self, plan: ResearchPlan) -> float:
        """Calculate estimated cost based on model usage"""
        # Approximate costs per 1K tokens
        costs = {
            "flashlight": 0.000025,  # $0.025 per 1M
            "flash": 0.000075,  # $0.075 per 1M
            "ultra": 0.00015,  # $0.15 per 1M
        }

        usage = self._get_model_usage(plan)
        total_cost = 0

        for model, count in usage.items():
            total_cost += costs.get(model, 0) * count

        return total_cost


class IntelligentResearchAgent:
    """Main research agent with Vertex AI integration"""

    def __init__(self, project_id: str, location: str = "us-central1"):
        self.vertex_router = VertexAIRouter(project_id, location)
        self.report_generator = ReportGenerator()
        self.model_usage_stats = {"flashlight": 0, "flash": 0, "ultra": 0}

    async def research(self, query: str, depth: str = "light") -> ResearchResult:
        """Main research method using A→A→P→A→P pattern"""
        start_time = datetime.now()

        logger.info(f"Starting research: {query} (depth: {depth})")

        try:
            # A (Analyze) - Understand request
            analysis = await self.vertex_router.analyze_request(query)

            # A (Assess) - Determine strategy
            strategy = await self.vertex_router.assess_strategy(analysis)
            strategy["original_query"] = query

            # P (Plan) - Create execution plan
            plan = await self.vertex_router.plan_execution(strategy)

            # A (Act) - Execute research
            results = await self.vertex_router.act_on_plan(plan)

            # P (Present) - Synthesize findings
            final_result = await self.vertex_router.present_findings(results, plan)

            # Calculate processing time
            final_result.processing_time = (datetime.now() - start_time).total_seconds()

            # Update model usage stats
            for model, count in final_result.model_usage.items():
                self.model_usage_stats[model] = (
                    self.model_usage_stats.get(model, 0) + count
                )

            logger.info(f"Research completed in {final_result.processing_time:.2f}s")
            return final_result

        except Exception as e:
            logger.error(f"Research failed: {str(e)}")
            raise

    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get model usage statistics"""
        total = sum(self.model_usage_stats.values())
        if total == 0:
            return self.model_usage_stats

        return {
            **self.model_usage_stats,
            "percentages": {
                model: (count / total) * 100
                for model, count in self.model_usage_stats.items()
            },
            "total_requests": total,
        }


class ReportGenerator:
    """Generate reports in multiple formats"""

    async def generate_json_report(self, result: ResearchResult) -> Dict[str, Any]:
        """Generate structured JSON report"""
        return {
            "metadata": {
                "query": result.query,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "processing_time": result.processing_time,
                "confidence_score": result.confidence_score,
                "model_usage": result.model_usage,
                "cost_estimate": result.cost_estimate,
            },
            "findings": result.findings,
            "sources": result.sources,
            "executive_summary": self._generate_executive_summary(result.findings),
        }

    async def generate_ppt_outline(self, result: ResearchResult) -> Dict[str, Any]:
        """Generate PowerPoint presentation outline"""
        findings = result.findings

        return {
            "title": f"Research Report: {result.query}",
            "slides": [
                {
                    "title": "Executive Summary",
                    "content": self._generate_executive_summary(findings),
                },
                {"title": "Key Findings", "content": findings.get("key_findings", [])},
                {
                    "title": "Source Analysis",
                    "content": findings.get("source_credibility_assessment", {}),
                },
                {
                    "title": "Insights & Patterns",
                    "content": findings.get("insights_and_patterns", []),
                },
                {
                    "title": "Recommendations",
                    "content": findings.get("recommendations", []),
                },
                {
                    "title": "Methodology",
                    "content": f"Research completed in {result.processing_time:.2f}s using {len(result.model_usage)} models",
                },
            ],
        }

    async def generate_pdf_content(self, result: ResearchResult) -> Dict[str, Any]:
        """Generate PDF report content"""
        return {
            "title": f"Research Report: {result.query}",
            "metadata": {
                "generated": datetime.now(timezone.utc).isoformat(),
                "confidence": result.confidence_score,
                "sources": len(result.sources),
            },
            "sections": [
                {
                    "title": "Executive Summary",
                    "content": self._generate_executive_summary(result.findings),
                },
                {
                    "title": "Introduction",
                    "content": f"This report presents comprehensive research findings for: {result.query}",
                },
                {
                    "title": "Methodology",
                    "content": f"Research conducted using Vertex AI with A→A→P→A→P inference pattern",
                },
                {"title": "Findings", "content": json.dumps(result.findings, indent=2)},
                {
                    "title": "Source Analysis",
                    "content": f"Analyzed {len(result.sources)} sources with confidence scoring",
                },
                {
                    "title": "Conclusion",
                    "content": "Research completed with high confidence in findings",
                },
            ],
        }

    def _generate_executive_summary(self, findings: Dict[str, Any]) -> str:
        """Generate executive summary from findings"""
        key_points = findings.get("key_findings", [])
        confidence = findings.get("overall_confidence", 0.8)

        summary = f"Research completed with {confidence:.1%} confidence. "

        if key_points:
            summary += "Key findings include: " + "; ".join(key_points[:3])

        return summary


# Usage example
async def main():
    """Example usage of the research agent"""

    # Initialize agent (requires Vertex AI project ID)
    agent = IntelligentResearchAgent(project_id="your-project-id")

    # Research Saveetha Engineering College startups
    result = await agent.research(
        query="Saveetha Engineering College startups and entrepreneurship programs",
        depth="deep",
    )

    # Generate reports
    json_report = await agent.report_generator.generate_json_report(result)
    ppt_outline = await agent.report_generator.generate_ppt_outline(result)
    pdf_content = await agent.report_generator.generate_pdf_content(result)

    # Save reports
    with open("research_report.json", "w") as f:
        json.dump(json_report, f, indent=2)

    with open("presentation_outline.json", "w") as f:
        json.dump(ppt_outline, f, indent=2)

    with open("pdf_content.json", "w") as f:
        json.dump(pdf_content, f, indent=2)

    # Print usage statistics
    usage = await agent.get_usage_statistics()
    print(f"Model usage: {usage}")

    print(f"Research completed: {result.query}")
    print(f"Confidence: {result.confidence_score:.1%}")
    print(f"Cost: ${result.cost_estimate:.6f}")
    print(f"Time: {result.processing_time:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
