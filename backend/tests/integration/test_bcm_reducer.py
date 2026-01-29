"""
Tests for BCM Reducer Integration

Integration tests for the Business Context Manifest reducer
with Redis session manager and onboarding data.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from integration.bcm_reducer import BCMReducer
from schemas.bcm_schema import (
    BusinessContextManifest,
    CompanyInfo,
    IndustryType,
    CompanyStage,
)


class TestBCMReducer:
    """Test BCM Reducer functionality."""

    @pytest.fixture
    def reducer(self):
        """Create BCM reducer instance."""
        return BCMReducer()

    @pytest.fixture
    def sample_onboarding_data(self):
        """Sample onboarding step data."""
        return {
            "metadata": {"workspace_id": "workspace123", "user_id": "user456"},
            "step_1": {
                "data": {
                    "company_name": "TechCorp Solutions",
                    "industry": "technology",
                    "description": "AI-powered business analytics platform",
                    "stage": "series_a",
                    "website": "https://techcorp.com",
                    "founded_year": 2020,
                    "employee_count": 75,
                    "revenue_range": "$5M-$10M",
                }
            },
            "step_14": {
                "data": {
                    "icps": [
                        {
                            "name": "Enterprise SaaS Companies",
                            "description": "Large B2B SaaS companies with 500+ employees",
                            "company_size": "500+",
                            "vertical": "software",
                            "geography": ["US", "Canada", "UK"],
                            "pains": [
                                {
                                    "category": "operational",
                                    "description": "Manual data analysis processes",
                                    "severity": 7,
                                    "frequency": "weekly",
                                }
                            ],
                            "goals": [
                                {
                                    "category": "efficiency",
                                    "description": "Automate data analysis workflows",
                                    "priority": "high",
                                    "timeline": "6 months",
                                }
                            ],
                            "confidence_score": 0.9,
                        }
                    ]
                }
            },
            "step_7": {
                "data": {
                    "direct_competitors": [
                        {
                            "name": "DataAnalytics Inc",
                            "type": "direct",
                            "strengths": ["Market leader", "Comprehensive features"],
                            "weaknesses": ["Expensive", "Complex interface"],
                            "market_share": "35%",
                            "pricing_model": "Enterprise subscription",
                        }
                    ],
                    "indirect_competitors": [],
                    "positioning_delta": [
                        {
                            "axis": "price_vs_quality",
                            "our_position": "premium_quality",
                            "competitor_position": "premium_price",
                            "differentiation": "Better value at lower cost",
                        }
                    ],
                }
            },
            "step_21": {
                "data": {
                    "tam": {"value": 50000000000, "currency": "USD"},
                    "sam": {"value": 5000000000, "currency": "USD"},
                    "som": {"value": 500000000, "currency": "USD"},
                    "currency": "USD",
                    "year": 2026,
                    "verticals": ["software", "analytics"],
                    "geography": ["US", "Canada", "Europe"],
                }
            },
            "step_17": {
                "data": {
                    "value_prop": {
                        "primary": "Transform your enterprise data into actionable insights with AI",
                        "secondary": "Reduce analysis time by 80% while improving accuracy",
                        "supporting_points": [
                            "AI-powered automation",
                            "Real-time insights",
                        ],
                    },
                    "taglines": [
                        {
                            "text": "Data Intelligence, Delivered.",
                            "context": "brand",
                            "variants": [
                                "Intelligence Delivered.",
                                "Data Intelligence.",
                            ],
                        }
                    ],
                    "key_messages": [
                        {
                            "title": "AI-Powered Analytics",
                            "content": "Leverage artificial intelligence to automate data analysis",
                            "audience": "CTOs",
                            "priority": "high",
                        }
                    ],
                    "soundbites": [
                        {
                            "text": "From data to decisions in seconds",
                            "context": "sales",
                            "length": "short",
                        }
                    ],
                }
            },
            "step_20": {
                "data": {
                    "primary_channels": [
                        {
                            "type": "direct_sales",
                            "name": "Enterprise Sales Team",
                            "description": "Direct sales to enterprise accounts",
                            "effectiveness": "high",
                            "cost_efficiency": "medium",
                            "target_audience": "Enterprise decision makers",
                        }
                    ],
                    "secondary_channels": [
                        {
                            "type": "content_marketing",
                            "name": "Technical Blog",
                            "description": "Educational content for technical buyers",
                            "effectiveness": "medium",
                            "cost_efficiency": "high",
                            "target_audience": "Engineers and architects",
                        }
                    ],
                    "strategy_summary": "Focus on direct sales for enterprise accounts supported by technical content marketing",
                }
            },
            "step_22": {
                "data": {
                    "short_term_goals": [
                        {
                            "title": "Achieve Product-Market Fit",
                            "description": "Validate product-market fit with 10 enterprise customers",
                            "timeframe": "12 months",
                            "metrics": ["Customer satisfaction", "Retention rate"],
                            "priority": "high",
                        }
                    ],
                    "long_term_goals": [
                        {
                            "title": "Market Leadership",
                            "description": "Become #1 in enterprise AI analytics",
                            "timeframe": "5 years",
                            "metrics": ["Market share", "Revenue growth"],
                            "priority": "high",
                        }
                    ],
                    "kpis": [
                        {
                            "name": "Monthly Recurring Revenue",
                            "description": "MRR from subscription customers",
                            "target": 1000000,
                            "current": 250000,
                            "unit": "USD",
                            "frequency": "monthly",
                        }
                    ],
                }
            },
            "step_3": {
                "data": {
                    "contradictions": [
                        {
                            "type": "market_positioning",
                            "description": "Claiming both premium and low-cost positioning",
                            "severity": "high",
                            "resolution": "Focus on premium positioning with clear value justification",
                        }
                    ]
                }
            },
        }

    @pytest.mark.asyncio
    async def test_reduce_complete_manifest(self, reducer, sample_onboarding_data):
        """Test reducing complete onboarding data to BCM."""
        manifest = await reducer.reduce(sample_onboarding_data)

        # Verify manifest structure
        assert isinstance(manifest, BusinessContextManifest)
        assert manifest.version == "2.0"
        assert manifest.workspace_id == "workspace123"
        assert manifest.user_id == "user456"
        assert manifest.completion_percentage == 30.43  # 7 steps / 23 * 100

        # Verify company info
        assert manifest.company.name == "TechCorp Solutions"
        assert manifest.company.industry == IndustryType.TECHNOLOGY
        assert manifest.company.stage == CompanyStage.SERIES_A
        assert manifest.company.website == "https://techcorp.com"
        assert manifest.company.employee_count == 75

        # Verify ICPs
        assert len(manifest.icps) == 1
        icp = manifest.icps[0]
        assert icp.name == "Enterprise SaaS Companies"
        assert icp.company_size == "500+"
        assert len(icp.pains) == 1
        assert len(icp.goals) == 1
        assert icp.confidence_score == 0.9

        # Verify competitors
        assert len(manifest.direct_competitors) == 1
        competitor = manifest.direct_competitors[0]
        assert competitor.name == "DataAnalytics Inc"
        assert competitor.type == "direct"
        assert len(competitor.strengths) == 2
        assert len(competitor.weaknesses) == 2

        # Verify positioning deltas
        assert len(manifest.positioning_delta) == 1
        delta = manifest.positioning_delta[0]
        assert delta.axis == "price_vs_quality"
        assert delta.our_position == "premium_quality"

        # Verify market sizing
        assert manifest.market.tam["value"] == 50000000000
        assert manifest.market.sam["value"] == 5000000000
        assert manifest.market.som["value"] == 500000000
        assert manifest.market.currency == "USD"
        assert manifest.market.year == 2026

        # Verify messaging
        assert (
            manifest.value_prop.primary
            == "Transform your enterprise data into actionable insights with AI"
        )
        assert len(manifest.taglines) == 1
        assert len(manifest.key_messages) == 1
        assert len(manifest.soundbites) == 1

        # Verify channels
        assert len(manifest.primary_channels) == 1
        assert len(manifest.secondary_channels) == 1
        assert manifest.strategy_summary is not None

        # Verify goals and KPIs
        assert len(manifest.short_term_goals) == 1
        assert len(manifest.long_term_goals) == 1
        assert len(manifest.kpis) == 1

        # Verify contradictions
        assert len(manifest.contradictions) == 1
        contradiction = manifest.contradictions[0]
        assert contradiction.type == "market_positioning"
        assert contradiction.severity == "high"

        # Verify metadata
        assert len(manifest.raw_step_ids) == 7
        assert "step_1" in manifest.raw_step_ids
        assert manifest.checksum is not None

    @pytest.mark.asyncio
    async def test_reduce_minimal_data(self, reducer):
        """Test reducing minimal onboarding data."""
        minimal_data = {
            "metadata": {"workspace_id": "workspace123"},
            "step_1": {
                "data": {
                    "company_name": "Test Corp",
                    "industry": "technology",
                    "description": "Test company",
                    "stage": "seed",
                }
            },
        }

        manifest = await reducer.reduce(minimal_data)

        assert isinstance(manifest, BusinessContextManifest)
        assert manifest.company.name == "Test Corp"
        assert manifest.company.industry == IndustryType.TECHNOLOGY
        assert manifest.completion_percentage == 4.35  # 1 step / 23 * 100

        # Should have empty collections for missing data
        assert len(manifest.icps) == 0
        assert len(manifest.direct_competitors) == 0
        assert len(manifest.indirect_competitors) == 0
        assert len(manifest.taglines) == 0
        assert len(manifest.kpis) == 0

    @pytest.mark.asyncio
    async def test_extract_company_info(self, reducer):
        """Test company info extraction."""
        data = {
            "step_1": {
                "data": {
                    "company_name": "TechCorp",
                    "industry": "healthcare",
                    "description": "Health tech company",
                    "stage": "series_b",
                    "website": "https://techcorp.health",
                }
            }
        }

        company = reducer._extract_company_info(data)

        assert company.name == "TechCorp"
        assert company.industry == IndustryType.HEALTHCARE
        assert company.stage == CompanyStage.SERIES_B
        assert company.website == "https://techcorp.health"

    @pytest.mark.asyncio
    async def test_extract_company_info_fallback(self, reducer):
        """Test company info extraction with fallback to foundation."""
        data = {
            "foundation": {
                "data": {
                    "company_name": "Fallback Corp",
                    "industry": "finance",
                    "description": "Finance company",
                    "stage": "growth",
                }
            }
        }

        company = reducer._extract_company_info(data)

        assert company.name == "Fallback Corp"
        assert company.industry == IndustryType.FINANCE
        assert company.stage == CompanyStage.GROWTH

    @pytest.mark.asyncio
    async def test_extract_icps_multiple(self, reducer):
        """Test extracting multiple ICPs."""
        data = {
            "step_14": {
                "data": {
                    "icps": [
                        {
                            "name": "ICP 1",
                            "description": "First ICP",
                            "pains": [
                                {
                                    "category": "cost",
                                    "description": "High costs",
                                    "severity": 8,
                                }
                            ],
                            "goals": [
                                {
                                    "category": "growth",
                                    "description": "Grow revenue",
                                    "priority": "high",
                                }
                            ],
                        },
                        {
                            "name": "ICP 2",
                            "description": "Second ICP",
                            "pains": [
                                {
                                    "category": "time",
                                    "description": "Slow processes",
                                    "severity": 6,
                                }
                            ],
                            "goals": [
                                {
                                    "category": "efficiency",
                                    "description": "Improve speed",
                                    "priority": "medium",
                                }
                            ],
                        },
                    ]
                }
            }
        }

        icps = reducer._extract_icps(data)

        assert len(icps) == 2
        assert icps[0].name == "ICP 1"
        assert icps[1].name == "ICP 2"
        assert len(icps[0].pains) == 1
        assert len(icps[1].pains) == 1

    @pytest.mark.asyncio
    async def test_extract_competitive_data(self, reducer):
        """Test competitive data extraction."""
        data = {
            "step_7": {
                "data": {
                    "direct_competitors": [
                        {
                            "name": "Competitor 1",
                            "strengths": ["Brand", "Features"],
                            "weaknesses": ["Price", "Support"],
                        }
                    ],
                    "indirect_competitors": [
                        {
                            "name": "Alternative 1",
                            "strengths": ["Simplicity"],
                            "weaknesses": ["Limited features"],
                        }
                    ],
                    "positioning_delta": [
                        {
                            "axis": "quality",
                            "our_position": "premium",
                            "competitor_position": "standard",
                        }
                    ],
                }
            }
        }

        competitive_data = reducer._extract_competitive_data(data)

        assert len(competitive_data["direct_competitors"]) == 1
        assert len(competitive_data["indirect_competitors"]) == 1
        assert len(competitive_data["positioning_delta"]) == 1

        direct_comp = competitive_data["direct_competitors"][0]
        assert direct_comp.name == "Competitor 1"
        assert direct_comp.type == "direct"
        assert len(direct_comp.strengths) == 2

    @pytest.mark.asyncio
    async def test_get_step_data_by_number(self, reducer):
        """Test getting step data by step number."""
        data = {"step_5": {"data": {"test": "value"}}}

        step_data = reducer._get_step_data(data, 5)
        assert step_data == {"test": "value"}

    @pytest.mark.asyncio
    async def test_get_step_data_by_identifier(self, reducer):
        """Test getting step data by identifier."""
        data = {"foundation": {"data": {"test": "foundation_value"}}}

        step_data = reducer._get_step_data(data, "foundation")
        assert step_data == {"test": "foundation_value"}

    @pytest.mark.asyncio
    async def test_get_step_data_nested(self, reducer):
        """Test getting step data when data is nested."""
        data = {"step_10": {"nested": {"actual_data": {"test": "nested_value"}}}}

        step_data = reducer._get_step_data(data, 10)
        assert step_data == {"nested": {"actual_data": {"test": "nested_value"}}}

    @pytest.mark.asyncio
    async def test_get_step_data_not_found(self, reducer):
        """Test getting step data when step doesn't exist."""
        data = {"step_1": {"data": {"test": "value"}}}

        step_data = reducer._get_step_data(data, 99)
        assert step_data is None

    @pytest.mark.asyncio
    async def test_extract_issues_data(self, reducer):
        """Test extracting issues data (contradictions, wins, risks)."""
        data = {
            "step_3": {
                "data": {
                    "contradictions": [
                        {
                            "type": "positioning",
                            "description": "Conflicting positioning statements",
                            "severity": "medium",
                            "resolution": "Clarify positioning",
                        }
                    ]
                }
            },
            "step_5": {
                "data": {
                    "recent_wins": [
                        {
                            "title": "First Enterprise Customer",
                            "description": "Signed first enterprise customer",
                            "impact": "high",
                            "customer": "Enterprise Corp",
                        }
                    ]
                }
            },
            "step_8": {
                "data": {
                    "risks": [
                        {
                            "title": "Market Competition",
                            "description": "Intense competition from established players",
                            "probability": "high",
                            "impact": "medium",
                            "mitigation": "Focus on differentiation",
                        }
                    ]
                }
            },
        }

        issues = reducer._extract_issues_data(data)

        assert len(issues["contradictions"]) == 1
        assert len(issues["recent_wins"]) == 1
        assert len(issues["risks"]) == 1

        contradiction = issues["contradictions"][0]
        assert contradiction.type == "positioning"
        assert contradiction.severity == "medium"

        win = issues["recent_wins"][0]
        assert win.title == "First Enterprise Customer"
        assert win.customer == "Enterprise Corp"

        risk = issues["risks"][0]
        assert risk.title == "Market Competition"
        assert risk.probability == "high"

    @pytest.mark.asyncio
    async def test_completion_percentage_calculation(self, reducer):
        """Test completion percentage calculation."""
        # Test with various numbers of completed steps
        test_cases = [
            ({"step_1": {"data": {}}}, 4.35),  # 1/23 * 100
            ({"step_1": {}, "step_2": {}, "step_3": {}}, 13.04),  # 3/23 * 100
            ({}, 0.0),  # No steps
        ]

        for data, expected_percentage in test_cases:
            data["metadata"] = {"workspace_id": "test"}
            manifest = await reducer.reduce(data)
            assert abs(manifest.completion_percentage - expected_percentage) < 0.01

    @pytest.mark.asyncio
    async def test_enum_mapping_fallbacks(self, reducer):
        """Test enum mapping with invalid values."""
        data = {
            "step_1": {
                "data": {
                    "company_name": "Test Corp",
                    "industry": "invalid_industry",  # Should fallback to OTHER
                    "stage": "invalid_stage",  # Should fallback to SEED
                    "description": "Test company",
                }
            }
        }

        company = reducer._extract_company_info(data)

        assert company.industry == IndustryType.OTHER
        assert company.stage == CompanyStage.SEED

    @pytest.mark.asyncio
    async def test_channel_type_mapping(self, reducer):
        """Test channel type mapping with fallbacks."""
        data = {
            "step_20": {
                "data": {
                    "primary_channels": [
                        {
                            "type": "invalid_channel",  # Should fallback to WEBSITE
                            "name": "Test Channel",
                        }
                    ]
                }
            }
        }

        channels_data = reducer._extract_channels_data(data)
        primary_channels = channels_data["primary_channels"]

        assert len(primary_channels) == 1
        assert primary_channels[0].type.value == "website"

    @pytest.mark.asyncio
    async def test_manifest_checksum_consistency(self, reducer, sample_onboarding_data):
        """Test that same data produces same checksum."""
        manifest1 = await reducer.reduce(sample_onboarding_data)
        manifest2 = await reducer.reduce(sample_onboarding_data)

        assert manifest1.checksum == manifest2.checksum

        # Different data should produce different checksum
        modified_data = sample_onboarding_data.copy()
        modified_data["step_1"]["data"]["company_name"] = "Different Corp"

        manifest3 = await reducer.reduce(modified_data)
        assert manifest1.checksum != manifest3.checksum

    @pytest.mark.asyncio
    async def test_token_budget_validation(self, reducer, sample_onboarding_data):
        """Test that manifest stays within token budget."""
        manifest = await reducer.reduce(sample_onboarding_data)

        # Estimate token count
        manifest_json = manifest.json()
        token_count = len(manifest_json) // 4  # Rough estimation

        # Should be within reasonable bounds (much less than 1200 tokens)
        assert token_count < 1200
        assert token_count > 0


if __name__ == "__main__":
    pytest.main([__file__])
