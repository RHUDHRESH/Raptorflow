"""
Research Guild Models

Data models for research, intelligence, and competitive analysis within the
Research Guild. These models define the data contracts for market research,
customer feedback analysis, and competitive intelligence activities.
"""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field


class PainPointRequest(BaseModel):
    """
    Request model for pain point analysis from customer feedback.

    Defines the parameters for extracting specific user pain points
    and categorizing them for product improvement insights.
    """

    customer_feedback: str = Field(
        ...,
        description="Raw customer feedback text to analyze for pain points",
        min_length=10,
        max_length=10000,  # Allow substantial feedback text
        examples=[
            "The app keeps crashing when I try to upload photos. The interface is confusing and I wish there were more customization options for the dashboard."
        ]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v
        }


class PainPoint(BaseModel):
    """
    Individual pain point with categorization.

    Represents a single identified user pain point with its category
    for organized analysis and product improvement prioritization.
    """

    category: str = Field(
        ...,
        description="Classification category for the pain point",
        examples=["Usability", "Pricing", "Missing Feature", "Performance", "Reliability"]
    )
    pain_point: str = Field(
        ...,
        description="Specific description of the user's pain point or problem",
        min_length=5,
        examples=[
            "Application crashes frequently during photo uploads",
            "Dashboard customization options are limited",
            "User interface navigation is confusing"
        ]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v
        }


class PainPointReport(BaseModel):
    """
    Comprehensive pain point analysis report.

    Contains all identified pain points from the customer feedback,
    organized by category for actionable product insights.
    """

    pain_points: List[PainPoint] = Field(
        ...,
        description="List of identified pain points with category classifications",
        min_items=1,
        examples=[
            [
                {"category": "Usability", "pain_point": "Navigation is confusing"},
                {"category": "Performance", "pain_point": "App crashes during uploads"},
                {"category": "Features", "pain_point": "Limited customization options"}
            ]
        ]
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            list: lambda v: v
        }


class WebIntelligenceRequest(BaseModel):
    """
    Request model for web intelligence gathering.

    Defines the parameters for comprehensive competitor and market research
    through web scraping and intelligence analysis.
    """

    target_companies: List[str] = Field(
        ...,
        description="List of companies to analyze",
        min_items=1,
        max_items=10,
        examples=[["competitor1.com", "competitor2.com", "startup.io"]]
    )
    intelligence_focus: str = Field(
        ...,
        description="Specific focus area for intelligence gathering",
        examples=["pricing", "features", "marketing", "social_presence"]
    )
    include_social_media: bool = Field(
        True,
        description="Whether to include social media analysis"
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v,
            list: lambda v: v,
            bool: lambda v: v
        }
