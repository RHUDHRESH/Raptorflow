"""
RaptorFlow Market Sizing Service
Phase 3.2.1: TAM/SAM/SOM Calculator

Calculates Total Addressable Market, Serviceable Available Market,
Serviceable Obtainable Market with growth projections and market penetration analysis.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from .config import get_settings
from .core.logging import get_logger
from .services.llm_service import ExtractionContext, LLMService

logger = get_logger(__name__)
settings = get_settings()


class MarketSizeUnit(str, Enum):
    """Units for market size calculation."""

    REVENUE = "revenue"
    CUSTOMERS = "customers"
    USERS = "users"
    UNITS = "units"


class GrowthRate(str, Enum):
    """Growth rate types."""

    CAGR = "cagr"  # Compound Annual Growth Rate
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"


@dataclass
class MarketSegment:
    """Individual market segment."""

    id: str
    name: str
    description: str
    characteristics: Dict
    size: float
    growth_rate: float
    growth_type: GrowthRate
    penetration_rate: float
    confidence_score: float


@dataclass
class MarketSizing:
    """Market sizing calculation result."""

    tam: float  # Total Addressable Market
    sam: float  # Serviceable Available Market
    som: float  # Serviceable Obtainable Market
    tam_unit: MarketSizeUnit
    sam_unit: MarketSizeUnit
    som_unit: MarketSizeUnit
    market_segments: List[MarketSegment]
    growth_projections: Dict[str, float]
    penetration_analysis: Dict
    calculation_method: str
    confidence_score: float
    calculated_at: datetime
    assumptions: List[str]


class TAMCalculator:
    """Total Addressable Market calculator."""

    def __init__(self):
        self.llm_service = LLMService()

    async def calculate_tam(self, business_data: Dict, industry: str) -> Dict:
        """
        Calculate Total Addressable Market.

        Args:
            business_data: Business information
            industry: Industry type

        Returns:
            TAM calculation with methodology
        """
        try:
            # Industry-specific TAM calculation methods
            industry_methods = {
                "technology": self._calculate_tam_tech,
                "healthcare": self._calculate_tam_healthcare,
                "finance": self._calculate_tam_finance,
                "retail": self._calculate_tam_retail,
                "manufacturing": self._calculate_tam_manufacturing,
            }

            calculator = industry_methods.get(industry, self._calculate_tam_general)

            # Calculate TAM using industry-specific method
            tam_result = await calculator(business_data)

            # Validate and enhance with LLM
            enhanced_tam = await self._enhance_tam_with_llm(
                tam_result, business_data, industry
            )

            return enhanced_tam

        except Exception as e:
            logger.error(f"TAM calculation failed: {e}")
            return {"tam": 0, "method": "error", "confidence": 0.0}

    async def _calculate_tam_tech(self, business_data: Dict) -> Dict:
        """Calculate TAM for technology industry."""
        # Method 1: Bottom-up TAM calculation
        target_customers = business_data.get("target_customers", {})

        # Calculate potential customers
        total_potential = 0

        if "companies" in target_customers:
            company_sizes = target_customers["companies"]
            for size, count in company_sizes.items():
                total_potential += count

        # Calculate average revenue per customer
        avg_revenue_per_customer = business_data.get("avg_revenue_per_customer", 10000)

        # Calculate TAM
        tam = total_potential * avg_revenue_per_customer

        # Alternative calculation using market research
        market_research_tam = await self._get_market_research_tam(
            "technology", business_data
        )

        return {
            "tam": max(tam, market_research_tam),
            "method": "bottom_up",
            "total_potential_customers": total_potential,
            "avg_revenue_per_customer": avg_revenue_per_customer,
            "market_research_tam": market_research_tam,
            "assumptions": [
                f"Total potential customers: {total_potential:,}",
                f"Average revenue per customer: ${avg_revenue_per_customer:,}",
                "All potential customers can be served",
            ],
        }

    async def _calculate_tam_healthcare(self, business_data: Dict) -> Dict:
        """Calculate TAM for healthcare industry."""
        # Population-based TAM calculation
        target_population = business_data.get("target_population", {})

        # Calculate addressable population
        total_population = 0

        for demographic, data in target_population.items():
            if isinstance(data, dict):
                total_population += data.get("count", 0)
            else:
                total_population += data

        # Calculate penetration rate
        penetration_rate = business_data.get("penetration_rate", 0.1)  # 10% default

        # Calculate average revenue per patient/customer
        avg_revenue_per_patient = business_data.get("avg_revenue_per_patient", 1000)

        # Calculate TAM
        addressable_population = total_population * penetration_rate
        tam = addressable_population * avg_revenue_per_patient

        return {
            "tam": tam,
            "method": "population_based",
            "total_population": total_population,
            "addressable_population": addressable_population,
            "penetration_rate": penetration_rate,
            "avg_revenue_per_patient": avg_revenue_per_patient,
            "assumptions": [
                f"Total population: {total_population:,}",
                f"Penetration rate: {penetration_rate*100:.1f}%",
                f"Average revenue per patient: ${avg_revenue_per_patient:,}",
            ],
        }

    async def _calculate_tam_finance(self, business_data: Dict) -> Dict:
        """Calculate TAM for finance industry."""
        # Asset-based TAM calculation
        target_assets = business_data.get("target_assets", {})

        # Calculate total addressable assets
        total_assets = 0

        for asset_type, data in target_assets.items():
            if isinstance(data, dict):
                total_assets += data.get("value", 0)
            else:
                total_assets += data

        # Calculate assets under management percentage
        aum_percentage = business_data.get("aum_percentage", 0.05)  # 5% default

        # Calculate TAM
        tam = total_assets * aum_percentage

        return {
            "tam": tam,
            "method": "asset_based",
            "total_assets": total_assets,
            "aum_percentage": aum_percentage,
            "assumptions": [
                f"Total addressable assets: ${total_assets:,.0f}",
                f"Assets under management percentage: {aum_percentage*100:.1f}%",
                "Conservative AUM capture rate",
            ],
        }

    async def _calculate_tam_retail(self, business_data: Dict) -> Dict:
        """Calculate TAM for retail industry."""
        # Geographic-based TAM calculation
        geographic_markets = business_data.get("geographic_markets", {})

        # Calculate total addressable market
        total_market_size = 0

        for market, data in geographic_markets.items():
            if isinstance(data, dict):
                total_market_size += data.get("market_size", 0)
            else:
                total_market_size += data

        # Calculate average spend per customer
        avg_spend_per_customer = business_data.get("avg_spend_per_customer", 500)

        # Calculate TAM
        tam = total_market_size * avg_spend_per_customer

        return {
            "tam": tam,
            "method": "geographic",
            "total_market_size": total_market_size,
            "avg_spend_per_customer": avg_spend_per_customer,
            "geographic_breakdown": geographic_markets,
            "assumptions": [
                f"Total addressable market: {total_market_size:,}",
                f"Average spend per customer: ${avg_spend_per_customer:,}",
                "Full market penetration possible",
            ],
        }

    async def _calculate_tam_manufacturing(self, business_data: Dict) -> Dict:
        """Calculate TAM for manufacturing industry."""
        # Production capacity-based TAM
        target_products = business_data.get("target_products", {})

        # Calculate total production capacity
        total_capacity = 0

        for product, data in target_products.items():
            if isinstance(data, dict):
                total_capacity += data.get("annual_capacity", 0)
            else:
                total_capacity += data

        # Calculate average price per unit
        avg_price_per_unit = business_data.get("avg_price_per_unit", 100)

        # Calculate TAM
        tam = total_capacity * avg_price_per_unit

        return {
            "tam": tam,
            "method": "capacity_based",
            "total_capacity": total_capacity,
            "avg_price_per_unit": avg_price_per_unit,
            "product_breakdown": target_products,
            "assumptions": [
                f"Total production capacity: {total_capacity:,}",
                f"Average price per unit: ${avg_price_per_unit:,}",
                "Full capacity utilization",
            ],
        }

    async def _calculate_tam_general(self, business_data: Dict) -> Dict:
        """General TAM calculation for unspecified industries."""
        # Use LLM for general TAM calculation
        try:
            context = ExtractionContext(
                industry=business_data.get("industry", ""),
                business_context=business_data,
            )

            prompt = f"""
            Calculate the Total Addressable Market (TAM) for this business:

            Business Information:
            - Industry: {business_data.get('industry', '')}
            - Target Market: {business_data.get('target_market', '')}
            - Business Model: {business_data.get('business_model', '')}
            - Current Revenue: {business_data.get('current_revenue', '')}
            - Target Customers: {business_data.get('target_customers', '')}

            Provide:
            1. TAM calculation methodology
            2. Total market size in USD
            3. Key assumptions
            4. Confidence level (0-1)
            5. Alternative calculation methods

            Format as JSON with keys: tam, method, assumptions, confidence, alternatives
            """

            llm_result = await self.llm_service.generate_response(
                LLMRequest(
                    prompt=prompt,
                    model=ModelType.GPT4_TURBO,
                    temperature=0.1,
                    max_tokens=1000,
                )
            )

            # Parse LLM response
            import json

            result = json.loads(llm_result.content)

            return result

        except Exception as e:
            logger.error(f"General TAM calculation failed: {e}")
            return {"tam": 0, "method": "error", "confidence": 0.0}

    async def _get_market_research_tam(
        self, industry: str, business_data: Dict
    ) -> float:
        """Get TAM from market research data."""
        # This would integrate with market research APIs
        # For now, return estimated values
        industry_estimates = {
            "technology": 1000000000,  # $1B
            "healthcare": 500000000,  # $500M
            "finance": 2000000000,  # $2B
            "retail": 1500000000,  # $1.5B
            "manufacturing": 800000000,  # $800M
        }

        return industry_estimates.get(industry, 500000000)

    async def _enhance_tam_with_llm(
        self, tam_result: Dict, business_data: Dict, industry: str
    ) -> Dict:
        """Enhance TAM calculation with LLM validation."""
        try:
            context = ExtractionContext(
                industry=industry, business_context=business_data
            )

            prompt = f"""
            Review and enhance this TAM calculation:

            Original TAM Calculation:
            - TAM: ${tam_result.get('tam', 0):,.0f}
            - Method: {tam_result.get('method', '')}
            - Assumptions: {tam_result.get('assumptions', [])}

            Business Context:
            - Industry: {industry}
            - Target Market: {business_data.get('target_market', '')}
            - Business Model: {business_data.get('business_model', '')}

            Provide:
            1. Validation of calculation method
            2. Alternative TAM calculations
            3. Missing market segments
            4. Adjusted TAM with confidence level
            5. Additional assumptions needed

            Format as JSON with keys: validated_tam, alternatives, missing_segments, confidence, additional_assumptions
            """

            llm_result = await self.llm_service.generate_response(
                LLMRequest(
                    prompt=prompt,
                    model=ModelType.GPT4_TURBO,
                    temperature=0.1,
                    max_tokens=800,
                )
            )

            # Parse and merge results
            import json

            enhancement = json.loads(llm_result.content)

            return {
                "tam": enhancement.get("validated_tam", tam_result.get("tam", 0)),
                "method": tam_result.get("method", ""),
                "alternatives": enhancement.get("alternatives", []),
                "missing_segments": enhancement.get("missing_segments", []),
                "confidence": enhancement.get("confidence", 0.5),
                "assumptions": tam_result.get("assumptions", [])
                + enhancement.get("additional_assumptions", []),
            }

        except Exception as e:
            logger.error(f"TAM enhancement failed: {e}")
            return tam_result


class SAMCalculator:
    """Serviceable Available Market calculator."""

    def __init__(self):
        self.llm_service = LLMService()

    async def calculate_sam(
        self, tam: float, business_data: Dict, constraints: List[str]
    ) -> Dict:
        """
        Calculate Serviceable Available Market.

        Args:
            tam: Total Addressable Market
            business_data: Business information
            constraints: Service constraints

        Returns:
            SAM calculation with methodology
        """
        try:
            # Calculate serviceability factors
            serviceability_factors = await self._calculate_serviceability_factors(
                business_data, constraints
            )

            # Calculate SAM as percentage of TAM
            sam_percentage = 1.0

            for factor, value in serviceability_factors.items():
                sam_percentage *= value

            sam = tam * sam_percentage

            # Validate with LLM
            enhanced_sam = await self._enhance_sam_with_llm(
                sam, sam_percentage, serviceability_factors, business_data
            )

            return enhanced_sam

        except Exception as e:
            logger.error(f"SAM calculation failed: {e}")
            return {"sam": tam * 0.5, "method": "error", "confidence": 0.0}

    async def _calculate_serviceability_factors(
        self, business_data: Dict, constraints: List[str]
    ) -> Dict:
        """Calculate factors that affect serviceability."""
        factors = {}

        # Geographic constraints
        if "geographic" in constraints:
            geographic_reach = business_data.get("geographic_reach", 0.5)  # 50% default
            factors["geographic"] = geographic_reach

        # Resource constraints
        if "resources" in constraints:
            resource_availability = business_data.get(
                "resource_availability", 0.7
            )  # 70% default
            factors["resources"] = resource_availability

        # Regulatory constraints
        if "regulatory" in constraints:
            regulatory_compliance = business_data.get(
                "regulatory_compliance", 0.8
            )  # 80% default
            factors["regulatory"] = regulatory_compliance

        # Technical constraints
        if "technical" in constraints:
            technical_feasibility = business_data.get(
                "technical_feasibility", 0.9
            )  # 90% default
            factors["technical"] = technical_feasibility

        # Channel constraints
        if "channels" in constraints:
            channel_access = business_data.get("channel_access", 0.6)  # 60% default
            factors["channels"] = channel_access

        # Default factors if no constraints specified
        if not factors:
            factors = {
                "geographic": 0.7,
                "resources": 0.8,
                "regulatory": 0.9,
                "technical": 0.95,
                "channels": 0.75,
            }

        return factors

    async def _enhance_sam_with_llm(
        self, sam: float, sam_percentage: float, factors: Dict, business_data: Dict
    ) -> Dict:
        """Enhance SAM calculation with LLM validation."""
        try:
            context = ExtractionContext(business_context=business_data)

            prompt = f"""
            Review and enhance this SAM calculation:

            Original SAM Calculation:
            - SAM: ${sam:,.0f}
            - SAM Percentage: {sam_percentage*100:.1f}%
            - Serviceability Factors: {factors}

            Business Context:
            - Industry: {business_data.get('industry', '')}
            - Business Model: {business_data.get('business_model', '')}
            - Current Capabilities: {business_data.get('capabilities', '')}

            Provide:
            1. Validation of serviceability factors
            2. Additional constraints to consider
            3. Adjusted SAM with confidence level
            4. Time to achieve full SAM
            5. Strategic recommendations

            Format as JSON with keys: validated_sam, additional_constraints, confidence, time_to_full_sam, recommendations
            """

            llm_result = await self.llm_service.generate_response(
                LLMRequest(
                    prompt=prompt,
                    model=ModelType.GPT4_TURBO,
                    temperature=0.1,
                    max_tokens=800,
                )
            )

            # Parse and merge results
            import json

            enhancement = json.loads(llm_result.content)

            return {
                "sam": enhancement.get("validated_sam", sam),
                "sam_percentage": sam_percentage,
                "serviceability_factors": factors,
                "additional_constraints": enhancement.get("additional_constraints", []),
                "confidence": enhancement.get("confidence", 0.5),
                "time_to_full_sam": enhancement.get("time_to_full_sam", "3-5 years"),
                "recommendations": enhancement.get("recommendations", []),
            }

        except Exception as e:
            logger.error(f"SAM enhancement failed: {e}")
            return {
                "sam": sam,
                "sam_percentage": sam_percentage,
                "serviceability_factors": factors,
            }


class SOMCalculator:
    """Serviceable Obtainable Market calculator."""

    def __init__(self):
        self.llm_service = LLMService()

    async def calculate_som(
        self, sam: float, business_data: Dict, competitive_factors: Dict
    ) -> Dict:
        """
        Calculate Serviceable Obtainable Market.

        Args:
            sam: Serviceable Available Market
            business_data: Business information
            competitive_factors: Competitive landscape factors

        Returns:
            SOM calculation with methodology
        """
        try:
            # Calculate competitive factors
            competition_factors = await self._calculate_competition_factors(
                competitive_factors
            )

            # Calculate SOM as percentage of SAM
            som_percentage = 1.0

            for factor, value in competition_factors.items():
                som_percentage *= value

            som = sam * som_percentage

            # Validate with LLM
            enhanced_som = await self._enhance_som_with_llm(
                som, som_percentage, competition_factors, business_data
            )

            return enhanced_som

        except Exception as e:
            logger.error(f"SOM calculation failed: {e}")
            return {"som": sam * 0.3, "method": "error", "confidence": 0.0}

    async def _calculate_competition_factors(self, competitive_factors: Dict) -> Dict:
        """Calculate factors that affect obtainability."""
        factors = {}

        # Market share factors
        if "market_share" in competitive_factors:
            market_share = competitive_factors["market_share"]
            factors["market_share"] = 1.0 - market_share  # Remaining market share

        # Brand strength factors
        if "brand_strength" in competitive_factors:
            brand_strength = competitive_factors["brand_strength"]
            factors["brand_strength"] = brand_strength

        # Distribution factors
        if "distribution" in competitive_factors:
            distribution = competitive_factors["distribution"]
            factors["distribution"] = distribution

        # Pricing factors
        if "pricing" in competitive_factors:
            pricing = competitive_factors["pricing"]
            factors["pricing"] = pricing

        # Product differentiation factors
        if "product_differentiation" in competitive_factors:
            differentiation = competitive_factors["product_differentiation"]
            factors["product_differentiation"] = differentiation

        # Default factors if none specified
        if not factors:
            factors = {
                "market_share": 0.3,  # 30% market share available
                "brand_strength": 0.7,  # 70% brand strength
                "distribution": 0.8,  # 80% distribution capability
                "pricing": 0.6,  # 60% pricing competitiveness
                "product_differentiation": 0.75,  # 75% product differentiation
            }

        return factors

    async def _enhance_som_with_llm(
        self, som: float, som_percentage: float, factors: Dict, business_data: Dict
    ) -> Dict:
        """Enhance SOM calculation with LLM validation."""
        try:
            context = ExtractionContext(business_context=business_data)

            prompt = f"""
            Review and enhance this SOM calculation:

            Original SOM Calculation:
            - SOM: ${som:,.0f}
            - SOM Percentage: {som_percentage*100:.1f}%
            - Competitive Factors: {factors}

            Business Context:
            - Industry: {business_data.get('industry', '')}
            - Competitive Position: {business_data.get('competitive_position', '')}
            - Market Share: {business_data.get('market_share', '')}
            - Brand Strength: {business_data.get('brand_strength', '')}

            Provide:
            1. Validation of competitive factors
            2. Market share growth potential
            3. Adjusted SOM with confidence level
            4. Time to achieve target SOM
            5. Strategic recommendations for market capture

            Format as JSON with keys: validated_som, growth_potential, confidence, time_to_target_som, recommendations
            """

            llm_result = await self.llm_service.generate_response(
                LLMRequest(
                    prompt=prompt,
                    model=ModelType.GPT4_TURBO,
                    temperature=0.1,
                    max_tokens=800,
                )
            )

            # Parse and merge results
            import json

            enhancement = json.loads(llm_result.content)

            return {
                "som": enhancement.get("validated_som", som),
                "som_percentage": som_percentage,
                "competitive_factors": factors,
                "growth_potential": enhancement.get("growth_potential", "medium"),
                "confidence": enhancement.get("confidence", 0.5),
                "time_to_target_som": enhancement.get(
                    "time_to_target_som", "2-3 years"
                ),
                "recommendations": enhancement.get("recommendations", []),
            }

        except Exception as e:
            logger.error(f"SOM enhancement failed: {e}")
            return {
                "som": som,
                "som_percentage": som_percentage,
                "competitive_factors": factors,
            }


class MarketSizingService:
    """Main market sizing service."""

    def __init__(self):
        self.tam_calculator = TAMCalculator()
        self.sam_calculator = SAMCalculator()
        self.som_calculator = SOMCalculator()
        self.llm_service = LLMService()

    async def calculate_market_sizing(self, business_data: Dict) -> MarketSizing:
        """
        Calculate comprehensive market sizing (TAM/SAM/SOM).

        Args:
            business_data: Business information

        Returns:
            Complete market sizing analysis
        """
        try:
            industry = business_data.get("industry", "")

            # Calculate TAM
            tam_result = await self.tam_calculator.calculate_tam(
                business_data, industry
            )
            tam = tam_result.get("tam", 0)

            # Calculate SAM
            constraints = business_data.get(
                "service_constraints", ["geographic", "resources", "regulatory"]
            )
            sam_result = await self.sam_calculator.calculate_sam(
                tam, business_data, constraints
            )
            sam = sam_result.get("sam", tam * 0.6)

            # Calculate SOM
            competitive_factors = business_data.get("competitive_factors", {})
            som_result = await self.som_calculator.calculate_som(
                sam, business_data, competitive_factors
            )
            som = som_result.get("som", sam * 0.5)

            # Generate market segments
            market_segments = await self._generate_market_segments(
                business_data, tam, sam, som
            )

            # Calculate growth projections
            growth_projections = await self._calculate_growth_projections(
                business_data, tam, sam, som
            )

            # Calculate penetration analysis
            penetration_analysis = await self._calculate_penetration_analysis(
                tam, sam, som
            )

            # Calculate overall confidence
            confidence_score = self._calculate_overall_confidence(
                tam_result, sam_result, som_result
            )

            return MarketSizing(
                tam=tam,
                sam=sam,
                som=som,
                tam_unit=MarketSizeUnit.REVENUE,
                sam_unit=MarketSizeUnit.REVENUE,
                som_unit=MarketSizeUnit.REVENUE,
                market_segments=market_segments,
                growth_projections=growth_projections,
                penetration_analysis=penetration_analysis,
                calculation_method="comprehensive_llm_enhanced",
                confidence_score=confidence_score,
                calculated_at=datetime.utcnow(),
                assumptions=tam_result.get("assumptions", [])
                + sam_result.get("additional_constraints", [])
                + som_result.get("recommendations", []),
            )

        except Exception as e:
            logger.error(f"Market sizing calculation failed: {e}")
            raise

    async def _generate_market_segments(
        self, business_data: Dict, tam: float, sam: float, som: float
    ) -> List[MarketSegment]:
        """Generate market segments for analysis."""
        segments = []

        # Use LLM to generate segments
        try:
            context = ExtractionContext(
                industry=business_data.get("industry", ""),
                business_context=business_data,
            )

            prompt = f"""
            Generate market segments for this business:

            Business Information:
            - Industry: {business_data.get('industry', '')}
            - Target Market: {business_data.get('target_market', '')}
            - Business Model: {business_data.get('business_model', '')}

            Market Sizing:
            - TAM: ${tam:,.0f}
            - SAM: ${sam:,.0f}
            - SOM: ${som:,.0f}

            Generate 5-8 market segments with:
            1. Segment name
            2. Description
            3. Key characteristics
            4. Size (as % of TAM)
            5. Growth rate (%)
            6. Penetration rate (%)
            7. Confidence score (0-1)

            Format as JSON with array of segments
            """

            llm_result = await self.llm_service.generate_response(
                LLMRequest(
                    prompt=prompt,
                    model=ModelType.GPT4_TURBO,
                    temperature=0.2,
                    max_tokens=1000,
                )
            )

            # Parse segments
            import json

            segments_data = json.loads(llm_result.content)

            for i, segment_data in enumerate(segments_data.get("segments", [])):
                segment = MarketSegment(
                    id=f"segment_{i}",
                    name=segment_data.get("name", ""),
                    description=segment_data.get("description", ""),
                    characteristics=segment_data.get("characteristics", {}),
                    size=tam * segment_data.get("size_percentage", 0.1),
                    growth_rate=segment_data.get("growth_rate", 0.1),
                    growth_type=GrowthRate.CAGR,
                    penetration_rate=segment_data.get("penetration_rate", 0.1),
                    confidence_score=segment_data.get("confidence_score", 0.5),
                )
                segments.append(segment)

            return segments

        except Exception as e:
            logger.error(f"Market segment generation failed: {e}")
            return []

    async def _calculate_growth_projections(
        self, business_data: Dict, tam: float, sam: float, som: float
    ) -> Dict:
        """Calculate growth projections."""
        projections = {}

        # Industry growth rates
        industry_growth_rates = {
            "technology": 0.15,  # 15% CAGR
            "healthcare": 0.08,  # 8% CAGR
            "finance": 0.10,  # 10% CAGR
            "retail": 0.05,  # 5% CAGR
            "manufacturing": 0.04,  # 4% CAGR
        }

        industry = business_data.get("industry", "")
        base_growth_rate = industry_growth_rates.get(industry, 0.08)

        # Calculate projections for 5 years
        for year in range(1, 6):
            projections[f"year_{year}"] = {
                "tam": tam * ((1 + base_growth_rate) ** year),
                "sam": sam * ((1 + base_growth_rate * 0.8) ** year),  # SAM grows slower
                "som": som
                * ((1 + base_growth_rate * 0.6) ** year),  # SOM grows slowest
            }

        return projections

    async def _calculate_penetration_analysis(
        self, tam: float, sam: float, som: float
    ) -> Dict:
        """Calculate market penetration analysis."""
        return {
            "tam_to_sam_ratio": sam / tam if tam > 0 else 0,
            "sam_to_som_ratio": som / sam if sam > 0 else 0,
            "tam_to_som_ratio": som / tam if tam > 0 else 0,
            "serviceability_gap": tam - sam,
            "obtainability_gap": sam - som,
            "total_penetration_rate": som / tam if tam > 0 else 0,
            "market_capture_opportunity": tam - som,
        }

    def _calculate_overall_confidence(
        self, tam_result: Dict, sam_result: Dict, som_result: Dict
    ) -> float:
        """Calculate overall confidence score."""
        tam_confidence = tam_result.get("confidence", 0.5)
        sam_confidence = sam_result.get("confidence", 0.5)
        som_confidence = som_result.get("confidence", 0.5)

        # Weight TAM higher as it's the foundation
        return tam_confidence * 0.5 + sam_confidence * 0.3 + som_confidence * 0.2


# Pydantic models for API responses
class MarketSegmentResponse(BaseModel):
    """Response model for market segment."""

    id: str
    name: str
    description: str
    characteristics: Dict
    size: float
    growth_rate: float
    growth_type: str
    penetration_rate: float
    confidence_score: float


class MarketSizingResponse(BaseModel):
    """Response model for market sizing."""

    tam: float
    sam: float
    som: float
    tam_unit: str
    sam_unit: str
    som_unit: str
    market_segments: List[MarketSegmentResponse]
    growth_projections: Dict[str, Dict]
    penetration_analysis: Dict
    calculation_method: str
    confidence_score: float
    calculated_at: datetime
    assumptions: List[str]


# Error classes
class MarketSizingError(Exception):
    """Base market sizing error."""

    pass


class TAMCalculationError(MarketSizingError):
    """TAM calculation error."""

    pass


class SAMCalculationError(MarketSizingError):
    """SAM calculation error."""

    pass


class SOMCalculationError(MarketSizingError):
    """SOM calculation error."""

    pass
