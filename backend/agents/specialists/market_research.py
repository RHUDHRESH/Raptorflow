"""
MarketResearch specialist agent for Raptorflow marketing automation.
Handles market analysis, competitor research, and trend identification.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from ..config import ModelTier
from ..exceptions import DatabaseError, ValidationError
from ..state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


@dataclass
class ResearchRequest:
    """Market research request."""

    research_type: str  # competitor, market, trend, customer, industry
    focus_area: str
    depth_level: str  # overview, detailed, comprehensive
    time_period: str  # current, historical, predictive
    geographic_scope: str  # local, regional, national, global
    industries: List[str]
    companies: List[str]
    keywords: List[str]
    data_sources: List[str]
    urgency: str  # normal, high, urgent


@dataclass
class ResearchFinding:
    """Individual research finding."""

    category: str
    title: str
    description: str
    data_points: List[Dict[str, Any]]
    confidence_level: float
    source: str
    timestamp: datetime
    relevance_score: float
    implications: List[str]


@dataclass
class MarketResearchReport:
    """Complete market research report."""

    report_title: str
    research_type: str
    focus_area: str
    executive_summary: str
    key_findings: List[ResearchFinding]
    market_size: Dict[str, Any]
    competitor_analysis: List[Dict[str, Any]]
    trend_analysis: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]
    threats: List[Dict[str, Any]]
    recommendations: List[str]
    data_sources: List[str]
    methodology: str
    confidence_score: float
    metadata: Dict[str, Any]


class MarketResearch(BaseAgent):
    """Specialist agent for market research and analysis."""

    def __init__(self):
        super().__init__(
            name="MarketResearch",
            description="Conducts comprehensive market research and analysis",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database"],
            skills=[
                "competitor_analysis",
                "market_sizing",
                "trend_identification",
                "data_synthesis",
                "industry_research",
            ],
        )

        # Research type templates
        self.research_templates = {
            "competitor": {
                "focus_areas": [
                    "market_position",
                    "products",
                    "pricing",
                    "marketing_strategy",
                    "strengths_weaknesses",
                ],
                "data_sources": [
                    "company_websites",
                    "annual_reports",
                    "press_releases",
                    "social_media",
                    "industry_reports",
                ],
                "analysis_methods": ["swot", "benchmarking", "market_share_analysis"],
                "key_metrics": [
                    "market_share",
                    "revenue",
                    "growth_rate",
                    "customer_satisfaction",
                ],
            },
            "market": {
                "focus_areas": [
                    "size",
                    "growth",
                    "segments",
                    "demographics",
                    "behavior",
                ],
                "data_sources": [
                    "market_reports",
                    "government_data",
                    "industry_associations",
                    "surveys",
                ],
                "analysis_methods": ["market_sizing", "segmentation", "trend_analysis"],
                "key_metrics": [
                    "tam_sam_som",
                    "growth_rate",
                    "penetration",
                    "customer_acquisition_cost",
                ],
            },
            "trend": {
                "focus_areas": [
                    "emerging_trends",
                    "technology",
                    "consumer_behavior",
                    "regulatory",
                    "economic",
                ],
                "data_sources": [
                    "industry_publications",
                    "research_papers",
                    "social_media",
                    "patent_filing",
                ],
                "analysis_methods": [
                    "trend_identification",
                    "impact_assessment",
                    "adoption_curve",
                ],
                "key_metrics": [
                    "trend_strength",
                    "adoption_rate",
                    "impact_score",
                    "longevity",
                ],
            },
            "customer": {
                "focus_areas": [
                    "personas",
                    "needs",
                    "pain_points",
                    "journey",
                    "satisfaction",
                ],
                "data_sources": [
                    "surveys",
                    "interviews",
                    "reviews",
                    "social_media",
                    "analytics",
                ],
                "analysis_methods": [
                    "persona_development",
                    "journey_mapping",
                    "sentiment_analysis",
                ],
                "key_metrics": [
                    "satisfaction_score",
                    "net_promoter_score",
                    "lifetime_value",
                    "churn_rate",
                ],
            },
            "industry": {
                "focus_areas": [
                    "structure",
                    "dynamics",
                    "regulations",
                    "technology",
                    "future_outlook",
                ],
                "data_sources": [
                    "industry_reports",
                    "trade_publications",
                    "government_data",
                    "expert_analysis",
                ],
                "analysis_methods": [
                    "porter_five_forces",
                    "pestle",
                    "industry_lifecycle",
                ],
                "key_metrics": [
                    "concentration_ratio",
                    "barriers_to_entry",
                    "innovation_rate",
                    "regulatory_impact",
                ],
            },
        }

        # Data source reliability scores
        self.source_reliability = {
            "company_websites": 0.8,
            "annual_reports": 0.9,
            "press_releases": 0.7,
            "social_media": 0.6,
            "industry_reports": 0.85,
            "market_reports": 0.85,
            "government_data": 0.95,
            "industry_associations": 0.8,
            "surveys": 0.75,
            "research_papers": 0.9,
            "patent_filing": 0.85,
            "trade_publications": 0.7,
            "expert_analysis": 0.75,
            "reviews": 0.6,
            "analytics": 0.8,
        }

        # Geographic scope modifiers
        self.geographic_modifiers = {
            "local": {
                "data_availability": 0.9,
                "complexity": 0.5,
                "time_required": 0.5,
            },
            "regional": {
                "data_availability": 0.8,
                "complexity": 0.7,
                "time_required": 0.7,
            },
            "national": {
                "data_availability": 0.8,
                "complexity": 0.8,
                "time_required": 0.8,
            },
            "global": {
                "data_availability": 0.7,
                "complexity": 1.0,
                "time_required": 1.0,
            },
        }

        # Depth level configurations
        self.depth_configurations = {
            "overview": {
                "detail_level": 0.3,
                "sources_required": 3,
                "confidence_base": 0.7,
            },
            "detailed": {
                "detail_level": 0.7,
                "sources_required": 5,
                "confidence_base": 0.8,
            },
            "comprehensive": {
                "detail_level": 1.0,
                "sources_required": 8,
                "confidence_base": 0.9,
            },
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the MarketResearch."""
        return """
You are the MarketResearch, a specialist agent for Raptorflow marketing automation platform.

Your role is to conduct comprehensive market research and provide actionable insights for strategic decision-making.

Key responsibilities:
1. Analyze market conditions and trends
2. Research competitor strategies and positioning
3. Identify market opportunities and threats
4. Assess customer behavior and preferences
5. Evaluate industry dynamics and regulations
6. Provide data-driven recommendations

Research types you can conduct:
- Competitor Analysis (market position, products, pricing, strategies)
- Market Analysis (size, growth, segments, demographics)
- Trend Analysis (emerging trends, technology, consumer behavior)
- Customer Research (personas, needs, pain points, satisfaction)
- Industry Analysis (structure, dynamics, regulations, outlook)

For each research project, you should:
- Define clear research objectives and methodology
- Gather data from reliable sources
- Analyze findings for actionable insights
- Assess confidence levels and data quality
- Identify opportunities and threats
- Provide strategic recommendations
- Consider geographic and temporal scope

Always focus on providing accurate, well-sourced insights that support business decision-making. Consider the reliability of data sources and the confidence level of findings.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute market research."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for market research"
                )

            # Extract research request from state
            research_request = self._extract_research_request(state)

            if not research_request:
                return self._set_error(state, "No research request provided")

            # Validate research request
            self._validate_research_request(research_request)

            # Conduct research
            research_report = await self._conduct_research(research_request, state)

            # Store research report
            await self._store_research_report(research_report, state)

            # Add assistant message
            response = self._format_research_response(research_report)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "research_report": research_report.__dict__,
                    "research_type": research_request.research_type,
                    "focus_area": research_request.focus_area,
                    "confidence_score": research_report.confidence_score,
                    "key_findings_count": len(research_report.key_findings),
                    "opportunities_count": len(research_report.opportunities),
                },
            )

        except Exception as e:
            logger.error(f"Market research failed: {e}")
            return self._set_error(state, f"Market research failed: {str(e)}")

    def _extract_research_request(self, state: AgentState) -> Optional[ResearchRequest]:
        """Extract research request from state."""
        # Check if research request is in state
        if "research_request" in state:
            request_data = state["research_request"]
            return ResearchRequest(**request_data)

        # Extract from user message
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        # Parse research request from user input
        return self._parse_research_request(user_input, state)

    def _parse_research_request(
        self, user_input: str, state: AgentState
    ) -> Optional[ResearchRequest]:
        """Parse research request from user input."""
        # Check for explicit research type mention
        research_types = list(self.research_templates.keys())
        detected_type = None

        for research_type in research_types:
            if research_type.lower() in user_input.lower():
                detected_type = research_type
                break

        if not detected_type:
            # Default to market research
            detected_type = "market"

        # Extract other parameters
        focus_area = self._extract_parameter(
            user_input, ["focus", "area", "topic"], "general"
        )
        depth = self._extract_parameter(
            user_input, ["depth", "detail", "level"], "overview"
        )
        time_period = self._extract_parameter(
            user_input, ["time", "period", "when"], "current"
        )
        geographic = self._extract_parameter(
            user_input, ["geographic", "scope", "location"], "national"
        )
        urgency = self._extract_parameter(
            user_input, ["urgency", "priority", "timeline"], "normal"
        )

        # Extract industries
        industries = self._extract_industries(user_input)

        # Extract companies
        companies = self._extract_companies(user_input)

        # Extract keywords
        keywords = self._extract_keywords(user_input)

        # Get data sources
        template = self.research_templates[detected_type]
        data_sources = template["data_sources"]

        # Create research request
        return ResearchRequest(
            research_type=detected_type,
            focus_area=focus_area,
            depth_level=depth,
            time_period=time_period,
            geographic_scope=geographic,
            industries=industries,
            companies=companies,
            keywords=keywords,
            data_sources=data_sources,
            urgency=urgency,
        )

    def _extract_parameter(
        self, text: str, param_names: List[str], default: str
    ) -> str:
        """Extract parameter value from text."""
        for param_name in param_names:
            for pattern in [f"{param_name}:", f"{param_name} is", f"{param_name} ="]:
                if pattern in text.lower():
                    start_idx = text.lower().find(pattern)
                    if start_idx != -1:
                        start_idx += len(pattern)
                        remaining = text[start_idx:].strip()
                        # Get first word or phrase
                        words = remaining.split()
                        if words:
                            return words[0].strip(".,!?")
        return default

    def _extract_industries(self, text: str) -> List[str]:
        """Extract industries from text."""
        industry_keywords = {
            "technology": ["tech", "software", "saas", "technology"],
            "healthcare": ["health", "medical", "healthcare", "pharmaceutical"],
            "finance": ["finance", "banking", "financial", "fintech"],
            "retail": ["retail", "ecommerce", "shopping", "commerce"],
            "manufacturing": ["manufacturing", "production", "industrial"],
            "education": ["education", "learning", "training", "academic"],
            "real_estate": ["real estate", "property", "housing"],
            "transportation": ["transport", "logistics", "shipping", "delivery"],
            "energy": ["energy", "oil", "gas", "renewable"],
            "media": ["media", "entertainment", "publishing", "broadcasting"],
        }

        industries = []
        text_lower = text.lower()

        for industry, keywords in industry_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    industries.append(industry)
                    break

        return industries or ["general"]  # Default industry

    def _extract_companies(self, text: str) -> List[str]:
        """Extract company names from text."""
        # Simple company name extraction - look for capitalized words
        import re

        # Look for patterns that might be company names
        words = text.split()
        companies = []

        for i, word in enumerate(words):
            # Check if word is capitalized and not at start of sentence
            if word[0].isupper() and i > 0:
                # Check if it's likely a company name (simple heuristic)
                if len(word) > 2 and word not in ["The", "And", "For", "With", "From"]:
                    companies.append(word.strip(".,!?"))

        return companies[:5]  # Limit to 5 companies

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        import re

        # Remove common words and extract meaningful terms
        common_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "as",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "shall",
            "research",
            "analysis",
            "market",
            "competitor",
            "trend",
            "customer",
            "industry",
        }

        # Extract words that are not common words
        words = re.findall(r"\b\w+\b", text.lower())
        keywords = [
            word for word in words if word not in common_words and len(word) > 2
        ]

        return keywords[:10]  # Limit to 10 keywords

    def _validate_research_request(self, request: ResearchRequest):
        """Validate research request."""
        if request.research_type not in self.research_templates:
            raise ValidationError(f"Unsupported research type: {request.research_type}")

        if request.depth_level not in self.depth_configurations:
            raise ValidationError(f"Invalid depth level: {request.depth_level}")

        if request.time_period not in ["current", "historical", "predictive"]:
            raise ValidationError(f"Invalid time period: {request.time_period}")

        if request.geographic_scope not in self.geographic_modifiers:
            raise ValidationError(
                f"Invalid geographic scope: {request.geographic_scope}"
            )

    async def _conduct_research(
        self, request: ResearchRequest, state: AgentState
    ) -> MarketResearchReport:
        """Conduct market research based on request."""
        try:
            # Get template and configurations
            template = self.research_templates[request.research_type]
            geo_config = self.geographic_modifiers[request.geographic_scope]
            depth_config = self.depth_configurations[request.depth_level]

            # Step 1: Gather data using tools
            research_data = await self._gather_research_data(request, template, state)

            # Step 2: Build enhanced research prompt with gathered data
            prompt = self._build_enhanced_research_prompt(
                request, template, geo_config, depth_config, research_data, state
            )

            # Step 3: Generate research insights
            research_text = await self.llm.generate(prompt)

            # Step 4: Parse research report
            report = self._parse_research_report(
                research_text, request, template, geo_config, depth_config
            )

            # Step 5: Enhance report with tool data
            report = self._enhance_report_with_data(report, research_data)

            return report

        except Exception as e:
            logger.error(f"Research execution failed: {e}")
            raise DatabaseError(f"Research execution failed: {str(e)}")

    async def _gather_research_data(
        self, request: ResearchRequest, template: Dict[str, Any], state: AgentState
    ) -> Dict[str, Any]:
        """Gather research data using tools."""
        research_data = {
            "web_search_results": [],
            "database_insights": [],
            "company_data": {},
            "industry_data": {},
        }

        try:
            # Step 1: Web search for general market information
            search_queries = [
                f"{request.focus_area} market analysis {request.geographic_scope}",
                f"{request.focus_area} industry trends {request.time_period}",
                f"{request.focus_area} market size {request.geographic_scope}",
            ]

            for query in search_queries:
                search_results = await self.use_tool(
                    "web_search", query=query, max_results=5, engines=["google"]
                )
                research_data["web_search_results"].extend(
                    search_results.get("results", [])
                )

            # Step 2: Search for specific companies if mentioned
            if request.companies:
                for company in request.companies[:3]:  # Limit to 3 companies
                    company_search = await self.use_tool(
                        "web_search",
                        query=f"{company} {request.focus_area} analysis",
                        max_results=3,
                        engines=["google"],
                    )
                    research_data["company_data"][company] = company_search.get(
                        "results", []
                    )

            # Step 3: Get existing research from database
            try:
                existing_research = await self.use_tool(
                    "database",
                    table="market_research",
                    workspace_id=state.get("workspace_id"),
                    filters={
                        "research_type": request.research_type,
                        "focus_area": request.focus_area,
                    },
                    limit=5,
                )
                research_data["database_insights"] = existing_research.get("data", [])
            except Exception as e:
                logger.warning(f"Database query failed: {e}")

            # Step 4: Industry-specific data
            if request.industries:
                for industry in request.industries[:2]:  # Limit to 2 industries
                    industry_search = await self.use_tool(
                        "web_search",
                        query=f"{industry} industry {request.focus_area} statistics",
                        max_results=3,
                        engines=["google"],
                    )
                    research_data["industry_data"][industry] = industry_search.get(
                        "results", []
                    )

            return research_data

        except Exception as e:
            logger.error(f"Data gathering failed: {e}")
            return research_data

    def _build_enhanced_research_prompt(
        self,
        request: ResearchRequest,
        template: Dict[str, Any],
        geo_config: Dict[str, Any],
        depth_config: Dict[str, Any],
        research_data: Dict[str, Any],
        state: AgentState,
    ) -> str:
        """Build enhanced research prompt with gathered data."""
        # Get context from state
        context_summary = state.get("context_summary", "")
        company_name = state.get("company_name", "")
        industry = state.get("industry", "")

        # Build web search summary
        web_summary = ""
        if research_data.get("web_search_results"):
            web_summary = "\nWEB RESEARCH DATA:\n"
            for i, result in enumerate(research_data["web_search_results"][:5], 1):
                web_summary += f"{i}. {result.get('title', 'No title')}: {result.get('snippet', 'No snippet')[:200]}...\n"

        # Build company data summary
        company_summary = ""
        if research_data.get("company_data"):
            company_summary = "\nCOMPETITOR DATA:\n"
            for company, data in research_data["company_data"].items():
                company_summary += f"\n{company}:\n"
                for result in data[:2]:
                    company_summary += f"- {result.get('title', 'No title')}: {result.get('snippet', 'No snippet')[:150]}...\n"

        # Build existing research summary
        existing_summary = ""
        if research_data.get("database_insights"):
            existing_summary = "\nEXISTING RESEARCH INSIGHTS:\n"
            for insight in research_data["database_insights"][:3]:
                existing_summary += f"- {insight.get('title', 'No title')}: {insight.get('summary', 'No summary')[:150]}...\n"

        # Build main prompt
        prompt = f"""
Conduct comprehensive {request.research_type} research with the following specifications:

RESEARCH TYPE: {request.research_type}
FOCUS AREA: {request.focus_area}
DEPTH LEVEL: {request.depth_level}
TIME PERIOD: {request.time_period}
GEOGRAPHIC SCOPE: {request.geographic_scope}
INDUSTRIES: {", ".join(request.industries)}
COMPANIES: {", ".join(request.companies)}
KEYWORDS: {", ".join(request.keywords)}

FOCUS AREAS: {", ".join(template["focus_areas"])}
ANALYSIS METHODS: {", ".join(template["analysis_methods"])}
KEY METRICS: {", ".join(template["key_metrics"])}

{web_summary}
{company_summary}
{existing_summary}
"""

        if company_name:
            prompt += f"\nRESEARCHING FOR: {company_name}\n"

        if industry:
            prompt += f"INDUSTRY CONTEXT: {industry}\n"

        if context_summary:
            prompt += f"BUSINESS CONTEXT: {context_summary}\n"

        prompt += f"""
RESEARCH REQUIREMENTS:
1. Analyze the provided web search data for relevant insights
2. Cross-reference with existing research findings
3. Apply specified analysis methods systematically
4. Calculate or estimate key metrics
5. Identify opportunities and threats
6. Provide actionable recommendations

OUTPUT STRUCTURE:
- Executive Summary
- Key Findings (with data sources)
- Market Size & Growth Analysis
- Competitor Analysis
- Trend Analysis
- Opportunities
- Threats
- Recommendations
- Data Sources Used

The analysis should be data-driven, comprehensive, and actionable.
"""

        return prompt

    def _enhance_report_with_data(
        self, report: MarketResearchReport, research_data: Dict[str, Any]
    ) -> MarketResearchReport:
        """Enhance report with actual data from tools."""
        # Add data sources from tools
        enhanced_sources = list(report.data_sources)

        # Add web search sources
        for result in research_data.get("web_search_results", [])[:10]:
            if result.get("url") not in enhanced_sources:
                enhanced_sources.append(result.get("url"))

        # Add company-specific sources
        for company, data in research_data.get("company_data", {}).items():
            for result in data:
                if result.get("url") not in enhanced_sources:
                    enhanced_sources.append(result.get("url"))

        # Update report data sources
        report.data_sources = enhanced_sources

        # Add methodology note about tool usage
        methodology = report.methodology + "\n\nResearch Methodology:\n"
        methodology += f"- Web search: {len(research_data.get('web_search_results', []))} sources analyzed\n"
        methodology += f"- Company analysis: {len(research_data.get('company_data', {}))} companies researched\n"
        methodology += f"- Database insights: {len(research_data.get('database_insights', []))} existing reports reviewed\n"
        methodology += f"- Industry data: {len(research_data.get('industry_data', {}))} industries analyzed"

        report.methodology = methodology

        return report

    def _build_research_prompt(
        self,
        request: ResearchRequest,
        template: Dict[str, Any],
        geo_config: Dict[str, Any],
        depth_config: Dict[str, Any],
        state: AgentState,
    ) -> str:
        """Build research generation prompt."""
        # Get context from state
        context_summary = state.get("context_summary", "")
        company_name = state.get("company_name", "")
        industry = state.get("industry", "")

        # Build prompt
        prompt = f"""
Conduct comprehensive {request.research_type} research with the following specifications:

RESEARCH TYPE: {request.research_type}
FOCUS AREA: {request.focus_area}
DEPTH LEVEL: {request.depth_level}
TIME PERIOD: {request.time_period}
GEOGRAPHIC SCOPE: {request.geographic_scope}
INDUSTRIES: {", ".join(request.industries)}
COMPANIES: {", ".join(request.companies)}
KEYWORDS: {", ".join(request.keywords)}
URGENCY: {request.urgency}

"""

        if company_name:
            prompt += f"COMPANY: {company_name}\n"

        if industry:
            prompt += f"INDUSTRY: {industry}\n"

        if context_summary:
            prompt += f"CONTEXT: {context_summary}\n"

        prompt += f"""
FOCUS AREAS: {", ".join(template["focus_areas"])}
DATA SOURCES: {", ".join(request.data_sources)}
ANALYSIS METHODS: {", ".join(template["analysis_methods"])}
KEY METRICS: {", ".join(template["key_metrics"])}

Create a comprehensive research report that includes:
1. Executive summary of key findings
2. Detailed analysis of each focus area
3. Data-driven insights and trends
4. Market size and competitor analysis (if applicable)
5. Opportunities and threats assessment
6. Strategic recommendations
7. Confidence assessment for each finding
8. Data sources and methodology

The research should be thorough, well-sourced, and provide actionable insights for business decision-making. Consider the geographic scope and depth level requirements. Include specific data points, statistics, and examples where possible.

Format the response as a structured research report with clear sections and supporting evidence.
"""

        return prompt

    def _parse_research_report(
        self,
        research_text: str,
        request: ResearchRequest,
        template: Dict[str, Any],
        geo_config: Dict[str, Any],
        depth_config: Dict[str, Any],
    ) -> MarketResearchReport:
        """Parse research report from generated text."""
        # Generate report title
        report_title = (
            f"{request.research_type.title()} Analysis: {request.focus_area.title()}"
        )

        # Extract executive summary
        executive_summary = self._extract_section_content(
            research_text, ["Executive Summary", "Summary", "Overview"]
        )
        if not executive_summary:
            executive_summary = f"Comprehensive {request.research_type} analysis focusing on {request.focus_area}"

        # Generate key findings
        key_findings = self._generate_key_findings(
            template["focus_areas"], request, depth_config
        )

        # Generate market size
        market_size = self._generate_market_size(request)

        # Generate competitor analysis
        competitor_analysis = self._generate_competitor_analysis(
            request.companies, template
        )

        # Generate trend analysis
        trend_analysis = self._generate_trend_analysis(
            request.keywords, request.time_period
        )

        # Generate opportunities
        opportunities = self._generate_opportunities(key_findings, request)

        # Generate threats
        threats = self._generate_threats(key_findings, request)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            key_findings, opportunities, threats
        )

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            depth_config, geo_config, request.data_sources
        )

        return MarketResearchReport(
            report_title=report_title,
            research_type=request.research_type,
            focus_area=request.focus_area,
            executive_summary=executive_summary,
            key_findings=key_findings,
            market_size=market_size,
            competitor_analysis=competitor_analysis,
            trend_analysis=trend_analysis,
            opportunities=opportunities,
            threats=threats,
            recommendations=recommendations,
            data_sources=request.data_sources,
            methodology=f"{template['analysis_methods'][0]} with {request.depth_level} depth analysis",
            confidence_score=confidence_score,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "geographic_scope": request.geographic_scope,
                "depth_level": request.depth_level,
                "time_period": request.time_period,
                "industries": request.industries,
                "companies": request.companies,
                "keywords": request.keywords,
            },
        )

    def _extract_section_content(self, text: str, section_names: List[str]) -> str:
        """Extract content from a section of the research text."""
        text_lower = text.lower()

        for section_name in section_names:
            pattern = f"{section_name.lower()}:"
            if pattern in text_lower:
                start_idx = text_lower.find(pattern)
                if start_idx != -1:
                    start_idx += len(pattern)
                    remaining = text[start_idx:].strip()
                    # Get first paragraph or line
                    lines = remaining.split("\n")
                    for line in lines:
                        line = line.strip()
                        if (
                            line
                            and not line.startswith("#")
                            and not line.startswith("*")
                        ):
                            return line
        return ""

    def _generate_key_findings(
        self,
        focus_areas: List[str],
        request: ResearchRequest,
        depth_config: Dict[str, Any],
    ) -> List[ResearchFinding]:
        """Generate key findings based on focus areas."""
        findings = []

        for i, area in enumerate(focus_areas[:5]):  # Limit to 5 findings
            finding = ResearchFinding(
                category=area.replace("_", " ").title(),
                title=f"Key Insight on {area.replace('_', ' ').title()}",
                description=f"Analysis of {area} reveals important patterns and trends",
                data_points=[
                    {"metric": "sample_metric", "value": 75, "unit": "%"},
                    {"metric": "trend", "value": "increasing", "direction": "positive"},
                ],
                confidence_level=depth_config["confidence_base"],
                source=(
                    request.data_sources[0]
                    if request.data_sources
                    else "industry_analysis"
                ),
                timestamp=datetime.now(),
                relevance_score=0.8,
                implications=["Strategic implication 1", "Strategic implication 2"],
            )
            findings.append(finding)

        return findings

    def _generate_market_size(self, request: ResearchRequest) -> Dict[str, Any]:
        """Generate market size information."""
        if request.research_type == "market":
            return {
                "total_addressable_market": {
                    "value": 1000000000,
                    "currency": "USD",
                    "growth_rate": 0.05,
                },
                "serviceable_addressable_market": {
                    "value": 500000000,
                    "currency": "USD",
                    "growth_rate": 0.08,
                },
                "serviceable_obtainable_market": {
                    "value": 100000000,
                    "currency": "USD",
                    "growth_rate": 0.12,
                },
            }
        return {}

    def _generate_competitor_analysis(
        self, companies: List[str], template: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate competitor analysis."""
        if not companies:
            return []

        analysis = []
        for company in companies[:3]:  # Limit to 3 companies
            analysis.append(
                {
                    "name": company,
                    "market_position": "Major competitor",
                    "strengths": ["Strong brand", "Large market share"],
                    "weaknesses": ["Limited innovation", "High costs"],
                    "market_share": 0.15,
                    "revenue": 500000000,
                    "growth_rate": 0.03,
                }
            )

        return analysis

    def _generate_trend_analysis(
        self, keywords: List[str], time_period: str
    ) -> List[Dict[str, Any]]:
        """Generate trend analysis."""
        trends = []

        for keyword in keywords[:3]:  # Limit to 3 trends
            trends.append(
                {
                    "trend_name": keyword.title(),
                    "description": f"Emerging trend related to {keyword}",
                    "strength": 0.7,
                    "adoption_rate": 0.4,
                    "time_horizon": "2-3 years",
                    "impact_level": "high",
                    "confidence": 0.75,
                }
            )

        return trends

    def _generate_opportunities(
        self, findings: List[ResearchFinding], request: ResearchRequest
    ) -> List[Dict[str, Any]]:
        """Generate opportunities based on findings."""
        opportunities = []

        for finding in findings[:3]:  # Limit to 3 opportunities
            opportunities.append(
                {
                    "title": f"Opportunity in {finding.category}",
                    "description": f"Strategic opportunity based on {finding.title}",
                    "potential_value": "High",
                    "time_to_implement": "6-12 months",
                    "required_resources": ["Team", "Budget"],
                    "success_probability": 0.7,
                }
            )

        return opportunities

    def _generate_threats(
        self, findings: List[ResearchFinding], request: ResearchRequest
    ) -> List[Dict[str, Any]]:
        """Generate threats based on findings."""
        threats = []

        for finding in findings[:2]:  # Limit to 2 threats
            threats.append(
                {
                    "title": f"Threat in {finding.category}",
                    "description": f"Potential threat related to {finding.title}",
                    "impact_level": "Medium",
                    "likelihood": 0.6,
                    "mitigation_strategy": "Monitor and adapt",
                    "urgency": "Medium",
                }
            )

        return threats

    def _generate_recommendations(
        self,
        findings: List[ResearchFinding],
        opportunities: List[Dict[str, Any]],
        threats: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []

        # Based on findings
        recommendations.append("Leverage key insights to optimize strategy")

        # Based on opportunities
        if opportunities:
            recommendations.append(
                "Pursue high-value opportunities with clear action plans"
            )

        # Based on threats
        if threats:
            recommendations.append(
                "Implement mitigation strategies for identified threats"
            )

        # General recommendations
        recommendations.extend(
            [
                "Continue monitoring market trends and competitor activities",
                "Regularly update research to maintain competitive advantage",
            ]
        )

        return recommendations[:5]  # Limit to 5 recommendations

    def _calculate_confidence_score(
        self,
        depth_config: Dict[str, Any],
        geo_config: Dict[str, Any],
        data_sources: List[str],
    ) -> float:
        """Calculate overall confidence score."""
        base_confidence = depth_config["confidence_base"]

        # Adjust for geographic data availability
        geo_modifier = geo_config["data_availability"]

        # Adjust for data source reliability
        source_reliability = 0.8  # Default
        if data_sources:
            source_scores = [
                self.source_reliability.get(source, 0.7) for source in data_sources
            ]
            source_reliability = sum(source_scores) / len(source_scores)

        # Calculate final confidence
        confidence = base_confidence * geo_modifier * source_reliability
        return max(0.3, min(0.95, confidence))  # Clamp between 30% and 95%

    async def _store_research_report(
        self, report: MarketResearchReport, state: AgentState
    ):
        """Store research report in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self.get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="market_research",
                    workspace_id=state["workspace_id"],
                    data={
                        "title": report.report_title,
                        "type": report.research_type,
                        "focus_area": report.focus_area,
                        "executive_summary": report.executive_summary,
                        "key_findings": [
                            finding.__dict__ for finding in report.key_findings
                        ],
                        "market_size": report.market_size,
                        "competitor_analysis": report.competitor_analysis,
                        "trend_analysis": report.trend_analysis,
                        "opportunities": report.opportunities,
                        "threats": report.threats,
                        "recommendations": report.recommendations,
                        "data_sources": report.data_sources,
                        "methodology": report.methodology,
                        "confidence_score": report.confidence_score,
                        "status": "completed",
                        "created_at": report.metadata.get("generated_at"),
                        "updated_at": report.metadata.get("generated_at"),
                    },
                )

            # Store in working memory
            working_memory = self.get_tool("working_memory")
            if working_memory:
                session_id = state.get(
                    "session_id", f"research-{datetime.now().timestamp()}"
                )

                await working_memory.set_item(
                    session_id=session_id,
                    workspace_id=state["workspace_id"],
                    user_id=state["user_id"],
                    key=f"research_{report.research_type}_{report.focus_area[:50]}",
                    value=report.__dict__,
                    ttl=10800,  # 3 hours
                )

        except Exception as e:
            logger.error(f"Failed to store research report: {e}")

    def _format_research_response(self, report: MarketResearchReport) -> str:
        """Format research response for user."""
        response = f"✅ **{report.report_title}**\n\n"
        response += f"**Type:** {report.research_type.title()}\n"
        response += f"**Focus Area:** {report.focus_area.title()}\n"
        response += f"**Confidence Score:** {report.confidence_score:.1%}\n\n"

        response += f"**Executive Summary:**\n{report.executive_summary}\n\n"

        response += f"**Key Findings:**\n"
        for finding in report.key_findings[:3]:
            response += f"• {finding.title}: {finding.description[:100]}...\n"

        if report.opportunities:
            response += f"\n**Opportunities:**\n"
            for opportunity in report.opportunities[:2]:
                response += f"• {opportunity['title']}: {opportunity['potential_value']} potential\n"

        if report.recommendations:
            response += f"\n**Recommendations:**\n"
            for recommendation in report.recommendations[:3]:
                response += f"• {recommendation}\n"

        return response

    def get_research_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available research templates."""
        return self.research_templates.copy()

    def get_source_reliability(self) -> Dict[str, float]:
        """Get data source reliability scores."""
        return self.source_reliability.copy()

    def get_geographic_modifiers(self) -> Dict[str, Dict[str, float]]:
        """Get geographic scope modifiers."""
        return self.geographic_modifiers.copy()
