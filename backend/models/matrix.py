"""
Matrix Guild Models

Data models for analytics, KPIs, and performance metrics within the Matrix Guild.
These models define the data contracts for campaign performance analysis and
KPI calculations performed by the Analytics Agent.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CampaignPerformanceData(BaseModel):
    """
    Raw campaign performance data for KPI calculations.

    This model represents the input data structure containing all the
    necessary campaign metrics that will be processed by the Analytics Agent
    to calculate various Key Performance Indicators (KPIs).

    All monetary values are in USD. All count values are integers representing
    actual occurrences or totals.
    """

    impressions: int = Field(
        ...,
        description="Total number of times ads were displayed/shown",
        ge=0,
        examples=[10000, 500000, 2500000]
    )
    clicks: int = Field(
        ...,
        description="Total number of clicks on ads",
        ge=0,
        examples=[500, 25000, 125000]
    )
    cost_usd: float = Field(
        ...,
        description="Total advertising cost in USD",
        ge=0.0,
        examples=[100.50, 2500.75, 12500.00]
    )
    conversions: int = Field(
        ...,
        description="Total number of desired actions (purchases, signups, etc.)",
        ge=0,
        examples=[25, 1250, 6250]
    )
    revenue_usd: float = Field(
        ...,
        description="Total revenue generated from conversions in USD",
        ge=0.0,
        examples=[500.00, 25000.50, 125000.75]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            int: lambda v: v,
            float: lambda v: round(v, 2) if v is not None else 0.0
        }


class CampaignKPIs(BaseModel):
    """
    Calculated Key Performance Indicators for campaign analysis.

    This model contains all the essential calculated KPIs that provide
    insights into campaign performance, efficiency, and effectiveness.
    All metrics are calculated by the Analytics Agent from raw performance data.

    All percentage values are represented as decimals (e.g., 0.025 for 2.5%).
    """

    click_through_rate_ctr: float = Field(
        ...,
        description="Click-Through Rate: clicks ÷ impressions (as decimal)",
        ge=0.0,
        le=1.0,
        examples=[0.025, 0.005, 0.0125]
    )
    cost_per_click_cpc: float = Field(
        ...,
        description="Cost Per Click: cost_usd ÷ clicks (in USD)",
        ge=0.0,
        examples=[0.50, 2.25, 5.00]
    )
    conversion_rate_cvr: float = Field(
        ...,
        description="Conversion Rate: conversions ÷ clicks (as decimal)",
        ge=0.0,
        le=1.0,
        examples=[0.05, 0.02, 0.008]
    )
    cost_per_acquisition_cpa: float = Field(
        ...,
        description="Cost Per Acquisition: cost_usd ÷ conversions (in USD)",
        ge=0.0,
        examples=[20.00, 50.25, 8.50]
    )
    return_on_ad_spend_roas: float = Field(
        ...,
        description="Return on Ad Spend: revenue_usd ÷ cost_usd (multiplier)",
        ge=0.0,
        examples=[2.5, 5.0, 10.25]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            float: lambda v: round(v, 6) if v is not None else 0.0
        }


class KPIBatchRequest(BaseModel):
    """
    Request model for batch KPI calculations.

    Allows processing multiple campaigns or time periods simultaneously.
    """

    campaigns: list[CampaignPerformanceData] = Field(
        ...,
        description="List of campaign performance data to calculate KPIs for",
        min_items=1,
        max_items=100
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            list: lambda v: v
        }


class KPIBatchResponse(BaseModel):
    """
    Response model for batch KPI calculations.

    Contains calculated KPIs for multiple campaigns in the same order as requested.
    """

    kpis: list[CampaignKPIs] = Field(
        ...,
        description="List of calculated KPIs corresponding to input campaigns"
    )
    total_campaigns: int = Field(
        ...,
        description="Total number of campaigns processed",
        ge=1
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            list: lambda v: v,
            int: lambda v: v
        }


class DetectedTrend(BaseModel):
    """
    Represents a single identified market trend.

    Contains the trend name, description, and supporting evidence from
    keyword analysis to provide context and credibility to the trend.
    """

    trend_name: str = Field(
        ...,
        description="Concise, descriptive name of the identified trend",
        examples=["AI in Customer Support", "Sustainable Tech Investing", "Remote Work Evolution"]
    )
    description: str = Field(
        ...,
        description="One-sentence summary explaining the trend's significance and implications",
        examples=[
            "The integration of AI technologies to improve customer support efficiency and personalization",
            "Growing investment in environmentally conscious technology solutions"
        ]
    )
    supporting_keywords: list[str] = Field(
        ...,
        description="List of keywords that support this trend identification",
        min_items=1,
        examples=[["artificial intelligence", "customer support", "automation"],
                 ["sustainable", "green tech", "investment", "renewable"]]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v,
            list: lambda v: v
        }


class TrendReport(BaseModel):
    """
    Comprehensive market trend analysis report.

    Synthesized analysis of multiple documents that identifies emerging
    patterns, themes, and market movements with supporting evidence.
    """

    summary: str = Field(
        ...,
        description="High-level overview of the broader market context and trend landscape",
        examples=[
            "The analyzed content reveals several interconnected trends in technology and business transformation...",
            "Current market signals indicate a convergence of AI innovation, sustainability initiatives, and remote work adaptations..."
        ]
    )
    trends: list[DetectedTrend] = Field(
        ...,
        description="Individual detected trends with detailed analysis",
        min_items=1,
        max_items=10  # Prevent excessive trend generation
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v,
            list: lambda v: v
        }


class TrendDetectionRequest(BaseModel):
    """
    Request model for trend detection analysis.

    Contains the collection of documents to analyze for emerging trends.
    """

    documents: list[str] = Field(
        ...,
        description="List of text documents/articles to analyze for trends",
        min_items=1,
        max_items=50  # Limit to prevent excessive processing
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            list: lambda v: v
        }
