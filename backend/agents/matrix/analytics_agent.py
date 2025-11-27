"""
Analytics Agent (MAT-004)

Matrix Guild's core analytics engine for campaign performance measurement.
Processes raw campaign data and calculates essential Key Performance Indicators
(KPIs) with mathematical precision and error handling.

Features:
- Pure computational engine (no LLM dependency)
- Synchronous KPI calculations for speed
- Robust division-by-zero protection
- Industry-standard metrics: CTR, CPC, CVR, CPA, ROAS
- Batch processing capabilities
- Precision handling for financial calculations

KPI Calculations:
- CTR (Click-Through Rate): clicks ÷ impressions
- CPC (Cost Per Click): cost ÷ clicks
- CVR (Conversion Rate): conversions ÷ clicks
- CPA (Cost Per Acquisition): cost ÷ conversions
- ROAS (Return on Ad Spend): revenue ÷ cost
"""

from typing import List
import structlog

from backend.models.matrix import (
    CampaignPerformanceData,
    CampaignKPIs,
    KPIBatchRequest,
    KPIBatchResponse
)

logger = structlog.get_logger(__name__)


class AnalyticsAgent:
    """
    MAT-004: Analytics Agent for campaign KPI calculations.

    This agent serves as the Matrix Guild's core analytics engine, providing
    accurate, mathematical calculations of campaign performance metrics. Unlike
    other agents that rely on AI analysis, this is a pure computational engine
    that processes raw performance data into actionable insights.

    Key Capabilities:
    - Synchronous KPI calculations (no I/O wait times)
    - Bulletproof division-by-zero error handling
    - Precision financial calculations with proper rounding
    - Batch processing for multiple campaigns
    - Validation of input data integrity

    Mathematical Precision:
    All calculations follow industry-standard formulas with proper error
    handling. Zero denominators return 0.0 instead of errors, allowing
    incomplete data sets to be processed gracefully.
    """

    def __init__(self):
        """Initialize the Analytics Agent."""
        logger.info("Analytics Agent (MAT-004) initialized")

    def calculate_kpis(self, data: CampaignPerformanceData) -> CampaignKPIs:
        """
        Calculate all KPIs from campaign performance data.

        This is the primary method for individual campaign KPI calculation.
        It takes raw performance metrics and computes all standard KPIs using
        industry-accepted formulas with robust error handling.

        Args:
            data: CampaignPerformanceData containing raw metrics

        Returns:
            CampaignKPIs with all calculated performance indicators

        Example:
            agent = AnalyticsAgent()
            kpis = agent.calculate_kpis(CampaignPerformanceData(
                impressions=10000,
                clicks=500,
                cost_usd=250.50,
                conversions=25,
                revenue_usd=1250.00
            ))
        """
        logger.debug(
            "Calculating KPIs",
            impressions=data.impressions,
            clicks=data.clicks,
            conversions=data.conversions
        )

        # Calculate each KPI with division-by-zero protection
        ctr = self._calculate_ctr(data.clicks, data.impressions)
        cpc = self._calculate_cpc(data.cost_usd, data.clicks)
        cvr = self._calculate_cvr(data.conversions, data.clicks)
        cpa = self._calculate_cpa(data.cost_usd, data.conversions)
        roas = self._calculate_roas(data.revenue_usd, data.cost_usd)

        kpis = CampaignKPIs(
            click_through_rate_ctr=ctr,
            cost_per_click_cpc=cpc,
            conversion_rate_cvr=cvr,
            cost_per_acquisition_cpa=cpa,
            return_on_ad_spend_roas=roas
        )

        logger.debug(
            "KPI calculation completed",
            ctr=ctr,
            cpc=cpc,
            cvr=cvr,
            cpa=cpa,
            roas=roas
        )

        return kpis

    def calculate_kpi_batch(self, request: KPIBatchRequest) -> KPIBatchResponse:
        """
        Calculate KPIs for multiple campaigns in batch.

        Processes multiple campaign datasets efficiently, returning results
        in the same order as provided. Useful for comparing multiple campaigns
        or processing historical data.

        Args:
            request: KPIBatchRequest containing multiple campaign datasets

        Returns:
            KPIBatchResponse with calculated KPIs for all campaigns

        Example:
            batch_request = KPIBatchRequest(campaigns=[data1, data2, data3])
            response = agent.calculate_kpi_batch(batch_request)
            # response.kpis contains results in same order as input
        """
        logger.info(
            "Processing KPI batch calculation",
            campaign_count=len(request.campaigns)
        )

        kpis_list = []
        for i, campaign_data in enumerate(request.campaigns):
            logger.debug(f"Calculating KPIs for campaign {i + 1}")
            campaign_kpis = self.calculate_kpis(campaign_data)
            kpis_list.append(campaign_kpis)

        response = KPIBatchResponse(
            kpis=kpis_list,
            total_campaigns=len(request.campaigns)
        )

        logger.info(
            "Batch KPI calculation completed",
            total_campaigns=response.total_campaigns
        )

        return response

    def _calculate_ctr(self, clicks: int, impressions: int) -> float:
        """
        Calculate Click-Through Rate (CTR).

        Formula: clicks ÷ impressions
        Returns 0.0 if impressions is 0

        Args:
            clicks: Number of clicks
            impressions: Number of impressions

        Returns:
            CTR as decimal (e.g., 0.025 for 2.5%)
        """
        if impressions > 0:
            ctr = clicks / impressions
            return round(ctr, 6)  # Round to 6 decimal places for consistency
        else:
            # Cannot calculate CTR with zero impressions
            return 0.0

    def _calculate_cpc(self, cost_usd: float, clicks: int) -> float:
        """
        Calculate Cost Per Click (CPC).

        Formula: cost_usd ÷ clicks
        Returns 0.0 if clicks is 0

        Args:
            cost_usd: Advertising cost in USD
            clicks: Number of clicks

        Returns:
            CPC in USD per click
        """
        if clicks > 0:
            cpc = cost_usd / clicks
            return round(cpc, 4)  # Round to 4 decimal places ($0.1234 precision)
        else:
            # Cannot calculate CPC with zero clicks
            return 0.0

    def _calculate_cvr(self, conversions: int, clicks: int) -> float:
        """
        Calculate Conversion Rate (CVR).

        Formula: conversions ÷ clicks
        Returns 0.0 if clicks is 0

        Args:
            conversions: Number of conversions
            clicks: Number of clicks

        Returns:
            CVR as decimal (e.g., 0.05 for 5%)
        """
        if clicks > 0:
            cvr = conversions / clicks
            return round(cvr, 6)  # Round to 6 decimal places for consistency
        else:
            # Cannot calculate CVR with zero clicks
            return 0.0

    def _calculate_cpa(self, cost_usd: float, conversions: int) -> float:
        """
        Calculate Cost Per Acquisition (CPA).

        Formula: cost_usd ÷ conversions
        Returns 0.0 if conversions is 0

        Args:
            cost_usd: Advertising cost in USD
            conversions: Number of conversions

        Returns:
            CPA in USD per conversion/acquisition
        """
        if conversions > 0:
            cpa = cost_usd / conversions
            return round(cpa, 4)  # Round to 4 decimal places ($X.XX precision)
        else:
            # Cannot calculate CPA with zero conversions
            return 0.0

    def _calculate_roas(self, revenue_usd: float, cost_usd: float) -> float:
        """
        Calculate Return on Ad Spend (ROAS).

        Formula: revenue_usd ÷ cost_usd
        Returns 0.0 if cost_usd is 0

        Args:
            revenue_usd: Revenue generated in USD
            cost_usd: Advertising cost in USD

        Returns:
            ROAS as multiplier (e.g., 5.0 means $5 revenue per $1 spent)
        """
        if cost_usd > 0:
            roas = revenue_usd / cost_usd
            return round(roas, 2)  # Round to 2 decimal places (common for multipliers)
        else:
            # Cannot calculate ROAS with zero ad spend
            return 0.0

    def validate_performance_data(self, data: CampaignPerformanceData) -> List[str]:
        """
        Validate campaign performance data for potential issues.

        Checks for common data quality issues that might affect KPI calculations
        or indicate problematic data.

        Args:
            data: CampaignPerformanceData to validate

        Returns:
            List of validation warnings/issues found
        """
        warnings = []

        # Check for logical inconsistencies
        if data.clicks > data.impressions:
            warnings.append("Clicks cannot exceed impressions")

        if data.conversions > data.clicks:
            warnings.append("Conversions cannot exceed clicks")

        # Check for suspiciously high/low values
        if data.impressions > 0 and data.clicks / data.impressions > 0.5:
            warnings.append("CTR above 50% may indicate data quality issues")

        if data.cost_usd > 0 and data.revenue_usd / data.cost_usd > 100:
            warnings.append("ROAS above 100x may indicate data quality issues")

        # Check for zero values that prevent calculations
        if data.impressions == 0:
            warnings.append("Zero impressions prevent CTR calculation")

        if data.clicks == 0:
            warnings.append("Zero clicks prevent CPC and CVR calculations")

        if data.conversions == 0:
            warnings.append("Zero conversions prevent CPA calculation")

        if data.cost_usd == 0:
            warnings.append("Zero cost prevents CPC, CPA, and ROAS calculations")

        return warnings

    def calculate_kpi_breakdown(self, data: CampaignPerformanceData) -> dict:
        """
        Calculate KPIs with detailed breakdown and validation.

        Provides not just the final KPIs but also intermediate calculations
        and validation warnings for deeper analysis.

        Args:
            data: CampaignPerformanceData to analyze

        Returns:
            Dictionary with KPIs, validation, and metadata
        """
        kpis = self.calculate_kpis(data)
        warnings = self.validate_performance_data(data)

        return {
            "kpis": kpis,
            "validation_warnings": warnings,
            "input_summary": {
                "impressions": data.impressions,
                "clicks": data.clicks,
                "cost_usd": data.cost_usd,
                "conversions": data.conversions,
                "revenue_usd": data.revenue_usd
            },
            "calculation_date": "2025-01-01T00:00:00Z"  # Would be dynamic in production
        }


# Global singleton instance
analytics_agent = AnalyticsAgent()
