"""
RaptorFlow External Data Sources Service
Phase 4.2.1: External Data Sources

Integrates with external APIs for market research, financial data,
industry benchmarks, and real-time data enrichment.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import aiohttp
import pandas as pd

from .config import get_settings
from .core.logging import get_logger
from .services.llm_service import ExtractionContext, LLMService

logger = get_logger(__name__)
settings = get_settings()


class DataSource(str, Enum):
    """External data source types."""

    MARKET_RESEARCH = "market_research"
    FINANCIAL_DATA = "financial_data"
    INDUSTRY_BENCHMARKS = "industry_benchmarks"
    ECONOMIC_INDICATORS = "economic_indicators"
    SOCIAL_MEDIA = "social_media"
    NEWS_API = "news_api"
    COMPANY_DATABASE = "company_database"
    SURVEY_DATA = "survey_data"


class DataFrequency(str, Enum):
    """Data update frequency."""

    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


@dataclass
class DataSourceConfig:
    """Configuration for external data source."""

    name: str
    type: DataSource
    url: str
    api_key_env: str
    rate_limit: int
    data_format: str
    update_frequency: DataFrequency
    reliability_score: float
    cost_per_request: float


@dataclass
class DataPoint:
    """Individual data point from external source."""

    source: str
    data_type: str
    value: Any
    timestamp: datetime
    confidence: float
    metadata: Dict


@dataclass
class EnrichmentResult:
    """Data enrichment result."""

    business_id: str
    original_data: Dict
    enriched_data: Dict
    added_fields: List[str]
    confidence_score: float
    sources_used: List[str]
    enrichment_timestamp: datetime


class MarketResearchAPI:
    """Market research data integration."""

    def __init__(self):
        self.session = None
        self.api_key = settings.MARKET_RESEARCH_API_KEY
        self.base_url = "https://api.marketresearch.com/v1"

    async def _get_session(self):
        """Get HTTP session."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=aiohttp.ClientTimeout(total=30),
            )
        return self.session

    async def get_market_size(self, industry: str, geography: str = "global") -> Dict:
        """Get market size data."""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/market-size"
            params = {
                "industry": industry,
                "geography": geography,
                "year": datetime.now().year,
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "tam": data.get("tam", 0),
                        "sam": data.get("sam", 0),
                        "som": data.get("som", 0),
                        "growth_rate": data.get("growth_rate", 0),
                        "currency": data.get("currency", "USD"),
                        "source": "market_research_api",
                    }
                else:
                    logger.error(f"Market research API error: {response.status}")
                    return {}

        except Exception as e:
            logger.error(f"Market size fetch failed: {e}")
            return {}

    async def get_competitor_data(self, industry: str, limit: int = 10) -> List[Dict]:
        """Get competitor data."""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/competitors"
            params = {"industry": industry, "limit": limit, "include_financials": True}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("competitors", [])
                else:
                    logger.error(f"Competitor data API error: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Competitor data fetch failed: {e}")
            return []

    async def get_industry_trends(
        self, industry: str, timeframe: str = "1year"
    ) -> List[Dict]:
        """Get industry trends."""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/trends"
            params = {
                "industry": industry,
                "timeframe": timeframe,
                "trend_types": ["technology", "consumer_behavior", "market_shifts"],
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("trends", [])
                else:
                    logger.error(f"Industry trends API error: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Industry trends fetch failed: {e}")
            return []


class FinancialDataAPI:
    """Financial data integration."""

    def __init__(self):
        self.session = None
        self.api_key = settings.FINANCIAL_DATA_API_KEY
        self.base_url = "https://api.financialdata.com/v1"

    async def _get_session(self):
        """Get HTTP session."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=aiohttp.ClientTimeout(total=30),
            )
        return self.session

    async def get_company_financials(self, company_identifier: str) -> Dict:
        """Get company financial data."""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/company/{company_identifier}/financials"

            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "revenue": data.get("revenue", {}),
                        "profit": data.get("profit", {}),
                        "growth_rate": data.get("growth_rate", 0),
                        "debt_ratio": data.get("debt_ratio", 0),
                        "market_cap": data.get("market_cap", 0),
                        "currency": data.get("currency", "USD"),
                        "last_updated": data.get("last_updated", ""),
                        "source": "financial_data_api",
                    }
                else:
                    logger.error(f"Financial data API error: {response.status}")
                    return {}

        except Exception as e:
            logger.error(f"Company financials fetch failed: {e}")
            return {}

    async def get_industry_benchmarks(self, industry: str, metrics: List[str]) -> Dict:
        """Get industry benchmarks."""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/benchmarks"
            params = {"industry": industry, "metrics": metrics, "period": "3years"}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "benchmarks": data.get("benchmarks", {}),
                        "percentiles": data.get("percentiles", {}),
                        "industry_average": data.get("industry_average", {}),
                        "source": "financial_data_api",
                    }
                else:
                    logger.error(f"Benchmarks API error: {response.status}")
                    return {}

        except Exception as e:
            logger.error(f"Industry benchmarks fetch failed: {e}")
            return {}


class EconomicIndicatorsAPI:
    """Economic indicators integration."""

    def __init__(self):
        self.session = None
        self.api_key = settings.ECONOMIC_INDICATORS_API_KEY
        self.base_url = "https://api.economicdata.com/v1"

    async def _get_session(self):
        """Get HTTP session."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=aiohttp.ClientTimeout(total=30),
            )
        return self.session

    async def get_gdp_data(self, country: str, period: str = "5years") -> Dict:
        """Get GDP data."""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/gdp"
            params = {"country": country, "period": period, "frequency": "annual"}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "gdp_values": data.get("values", []),
                        "growth_rates": data.get("growth_rates", []),
                        "currency": data.get("currency", "USD"),
                        "source": "economic_indicators_api",
                    }
                else:
                    logger.error(f"GDP data API error: {response.status}")
                    return {}

        except Exception as e:
            logger.error(f"GDP data fetch failed: {e}")
            return {}

    async def get_inflation_data(self, country: str, period: str = "5years") -> Dict:
        """Get inflation data."""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/inflation"
            params = {"country": country, "period": period, "frequency": "monthly"}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "inflation_rates": data.get("rates", []),
                        "cpi_values": data.get("cpi", []),
                        "source": "economic_indicators_api",
                    }
                else:
                    logger.error(f"Inflation data API error: {response.status}")
                    return {}

        except Exception as e:
            logger.error(f"Inflation data fetch failed: {e}")
            return {}


class NewsAPIService:
    """News and media monitoring."""

    def __init__(self):
        self.session = None
        self.api_key = settings.NEWS_API_KEY
        self.base_url = "https://api.news.com/v1"

    async def _get_session(self):
        """Get HTTP session."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=aiohttp.ClientTimeout(total=30),
            )
        return self.session

    async def search_news(
        self, query: str, limit: int = 10, timeframe: str = "7days"
    ) -> List[Dict]:
        """Search news articles."""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/search"
            params = {
                "q": query,
                "limit": limit,
                "timeframe": timeframe,
                "sort": "relevance",
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("articles", [])
                else:
                    logger.error(f"News search API error: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"News search failed: {e}")
            return []

    async def get_company_news(self, company_name: str, limit: int = 10) -> List[Dict]:
        """Get news about specific company."""
        try:
            session = await self._get_session()

            url = f"{self.base_url}/company/{company_name}"
            params = {"limit": limit, "timeframe": "30days", "sentiment": True}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("articles", [])
                else:
                    logger.error(f"Company news API error: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Company news fetch failed: {e}")
            return []


class DataEnrichment:
    """Data enrichment and validation."""

    def __init__(self):
        self.llm_service = LLMService()
        self.market_research = MarketResearchAPI()
        self.financial_data = FinancialDataAPI()
        self.economic_indicators = EconomicIndicatorsAPI()
        self.news_api = NewsAPIService()

    async def enrich_business_data(self, business_data: Dict) -> EnrichmentResult:
        """
        Enrich business data with external sources.

        Args:
            business_data: Original business data

        Returns:
            Enrichment result with added data
        """
        try:
            enriched_data = business_data.copy()
            added_fields = []
            sources_used = []
            confidence_scores = []

            # Enrich with market research data
            if business_data.get("industry"):
                market_data = await self.market_research.get_market_size(
                    business_data["industry"], business_data.get("geography", "global")
                )

                if market_data:
                    enriched_data.update(
                        {
                            "market_tam": market_data.get("tam", 0),
                            "market_sam": market_data.get("sam", 0),
                            "market_som": market_data.get("som", 0),
                            "market_growth_rate": market_data.get("growth_rate", 0),
                        }
                    )
                    added_fields.extend(
                        ["market_tam", "market_sam", "market_som", "market_growth_rate"]
                    )
                    sources_used.append("market_research_api")
                    confidence_scores.append(0.8)  # High confidence for market research

            # Enrich with competitor data
            if business_data.get("industry"):
                competitors = await self.market_research.get_competitor_data(
                    business_data["industry"], limit=5
                )

                if competitors:
                    enriched_data["competitors"] = competitors
                    added_fields.append("competitors")
                    sources_used.append("market_research_api")
                    confidence_scores.append(
                        0.7
                    )  # Medium confidence for competitor data

            # Enrich with financial benchmarks
            if business_data.get("industry"):
                benchmarks = await self.financial_data.get_industry_benchmarks(
                    business_data["industry"],
                    ["profit_margin", "revenue_growth", "debt_ratio"],
                )

                if benchmarks:
                    enriched_data["industry_benchmarks"] = benchmarks
                    added_fields.extend(
                        [
                            "industry_profit_margin",
                            "industry_revenue_growth",
                            "industry_debt_ratio",
                        ]
                    )
                    sources_used.append("financial_data_api")
                    confidence_scores.append(
                        0.75
                    )  # Medium-high confidence for benchmarks

            # Enrich with economic indicators
            if business_data.get("country"):
                gdp_data = await self.economic_indicators.get_gdp_data(
                    business_data["country"]
                )

                if gdp_data:
                    enriched_data["country_gdp"] = gdp_data.get("gdp_values", [])
                    enriched_data["country_gdp_growth"] = gdp_data.get(
                        "growth_rates", []
                    )
                    added_fields.extend(["country_gdp", "country_gdp_growth"])
                    sources_used.append("economic_indicators_api")
                    confidence_scores.append(0.9)  # High confidence for economic data

            # Enrich with news data
            if business_data.get("name"):
                news_articles = await self.news_api.get_company_news(
                    business_data["name"], limit=5
                )

                if news_articles:
                    enriched_data["recent_news"] = news_articles
                    added_fields.append("recent_news")
                    sources_used.append("news_api")
                    confidence_scores.append(0.6)  # Medium confidence for news

            # Calculate overall confidence
            overall_confidence = (
                np.mean(confidence_scores) if confidence_scores else 0.5
            )

            # Validate and clean enriched data
            validated_data = await self._validate_enriched_data(enriched_data)

            return EnrichmentResult(
                business_id=business_data.get("id", ""),
                original_data=business_data,
                enriched_data=validated_data,
                added_fields=list(set(added_fields)),
                confidence_score=overall_confidence,
                sources_used=list(set(sources_used)),
                enrichment_timestamp=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Data enrichment failed: {e}")
            return EnrichmentResult(
                business_id=business_data.get("id", ""),
                original_data=business_data,
                enriched_data=business_data,
                added_fields=[],
                confidence_score=0.0,
                sources_used=[],
                enrichment_timestamp=datetime.utcnow(),
            )

    async def _validate_enriched_data(self, data: Dict) -> Dict:
        """Validate and clean enriched data."""
        validated_data = {}

        for key, value in data.items():
            if value is not None:
                # Remove outliers and invalid data
                if isinstance(value, (int, float)):
                    if key.endswith("_rate") and (value < -1 or value > 1):
                        continue  # Skip invalid rates
                    if key.endswith("_ratio") and (value < 0 or value > 10):
                        continue  # Skip invalid ratios
                elif isinstance(value, str) and len(value.strip()) == 0:
                    continue  # Skip empty strings

                validated_data[key] = value

        return validated_data


class ExternalDataService:
    """Main external data service."""

    def __init__(self):
        self.data_enrichment = DataEnrichment()
        self.llm_service = LLMService()

        # Configure data sources
        self.data_sources = [
            DataSourceConfig(
                name="Market Research API",
                type=DataSource.MARKET_RESEARCH,
                url="https://api.marketresearch.com/v1",
                api_key_env="MARKET_RESEARCH_API_KEY",
                rate_limit=1000,
                data_format="json",
                update_frequency=DataFrequency.QUARTERLY,
                reliability_score=0.8,
                cost_per_request=0.01,
            ),
            DataSourceConfig(
                name="Financial Data API",
                type=DataSource.FINANCIAL_DATA,
                url="https://api.financialdata.com/v1",
                api_key_env="FINANCIAL_DATA_API_KEY",
                rate_limit=500,
                data_format="json",
                update_frequency=DataFrequency.ANNUAL,
                reliability_score=0.9,
                cost_per_request=0.02,
            ),
            DataSourceConfig(
                name="Economic Indicators API",
                type=DataSource.ECONOMIC_INDICATORS,
                url="https://api.economicdata.com/v1",
                api_key_env="ECONOMIC_INDICATORS_API_KEY",
                rate_limit=2000,
                data_format="json",
                update_frequency=DataFrequency.MONTHLY,
                reliability_score=0.95,
                cost_per_request=0.005,
            ),
            DataSourceConfig(
                name="News API",
                type=DataSource.NEWS_API,
                url="https://api.news.com/v1",
                api_key_env="NEWS_API_KEY",
                rate_limit=5000,
                data_format="json",
                update_frequency=DataFrequency.REAL_TIME,
                reliability_score=0.7,
                cost_per_request=0.001,
            ),
        ]

    async def get_market_intelligence(self, business_data: Dict) -> Dict:
        """
        Get comprehensive market intelligence.

        Args:
            business_data: Business information

        Returns:
            Market intelligence data
        """
        try:
            # Enrich business data
            enrichment_result = await self.data_enrichment.enrich_business_data(
                business_data
            )

            # Generate market insights using LLM
            insights = await self._generate_market_insights(
                enrichment_result.enriched_data, enrichment_result.sources_used
            )

            return {
                "business_id": business_data.get("id", ""),
                "original_data": business_data,
                "enriched_data": enrichment_result.enriched_data,
                "added_fields": enrichment_result.added_fields,
                "confidence_score": enrichment_result.confidence_score,
                "sources_used": enrichment_result.sources_used,
                "market_insights": insights,
                "data_quality_score": await self._assess_data_quality(
                    enrichment_result.enriched_data
                ),
                "enrichment_timestamp": enrichment_result.enrichment_timestamp,
            }

        except Exception as e:
            logger.error(f"Market intelligence failed: {e}")
            return {"error": str(e)}

    async def _generate_market_insights(
        self, enriched_data: Dict, sources_used: List[str]
    ) -> Dict:
        """Generate market insights using LLM."""
        try:
            context = ExtractionContext(business_context=enriched_data)

            prompt = f"""
            Analyze this enriched business data and generate market insights:

            Business Data:
            {json.dumps(enriched_data, indent=2)}

            Data Sources Used:
            {', '.join(sources_used)}

            Provide:
            1. Market opportunity analysis
            2. Competitive positioning insights
            3. Growth potential assessment
            4. Risk factors identification
            5. Strategic recommendations
            6. Data quality assessment

            Format as JSON with keys: opportunities, positioning, growth_potential, risks, recommendations, data_quality
            """

            llm_result = await self.llm_service.generate_response(
                LLMRequest(
                    prompt=prompt,
                    model=ModelType.GPT4_TURBO,
                    temperature=0.2,
                    max_tokens=1500,
                )
            )

            import json

            return json.loads(llm_result.content)

        except Exception as e:
            logger.error(f"Market insights generation failed: {e}")
            return {}

    async def _assess_data_quality(self, data: Dict) -> float:
        """Assess quality of enriched data."""
        quality_score = 0.5  # Base score

        # Check for completeness
        required_fields = ["market_tam", "competitors", "industry_benchmarks"]
        completeness = sum(
            1 for field in required_fields if field in data and data[field]
        )
        quality_score += (completeness / len(required_fields)) * 0.3

        # Check for recency
        if "enrichment_timestamp" in data:
            days_old = (datetime.utcnow() - data["enrichment_timestamp"]).days
            recency_score = max(0, 1 - (days_old / 365))  # Decay over time
            quality_score += recency_score * 0.2

        return min(1.0, quality_score)

    async def get_data_source_status(self) -> Dict:
        """Get status of all data sources."""
        status = {}

        for source in self.data_sources:
            try:
                # Test connectivity
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{source.url}/health", timeout=5
                    ) as response:
                        status[source.name] = {
                            "available": response.status == 200,
                            "last_check": datetime.utcnow().isoformat(),
                            "response_time": 0,  # Would measure actual response time
                            "rate_limit_remaining": source.rate_limit,
                            "cost_per_request": source.cost_per_request,
                        }
            except Exception as e:
                status[source.name] = {
                    "available": False,
                    "last_check": datetime.utcnow().isoformat(),
                    "error": str(e),
                }

        return status


# Pydantic models for API responses
class DataEnrichmentResponse(BaseModel):
    """Response model for data enrichment."""

    business_id: str
    enriched_data: Dict
    added_fields: List[str]
    confidence_score: float
    sources_used: List[str]
    enrichment_timestamp: datetime


class MarketIntelligenceResponse(BaseModel):
    """Response model for market intelligence."""

    business_id: str
    original_data: Dict
    enriched_data: Dict
    added_fields: List[str]
    confidence_score: float
    sources_used: List[str]
    market_insights: Dict
    data_quality_score: float
    enrichment_timestamp: datetime


class DataSourceStatusResponse(BaseModel):
    """Response model for data source status."""

    sources: Dict[str, Dict]
    checked_at: datetime


# Error classes
class ExternalDataError(Exception):
    """Base external data error."""

    pass


class APIError(ExternalDataError):
    """API-related error."""

    pass


class DataValidationError(ExternalDataError):
    """Data validation error."""

    pass
