"""
Unit tests for BCMReducer foundation extraction.
Tests cover all 23 onboarding steps and validation logic.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import logging

from backend.integration.bcm_reducer import BCMReducer
from backend.schemas.bcm_schema import IndustryType, CompanyStage


class TestBCMReducerFoundation:
    """Test suite for BCMReducer foundation extraction."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reducer = BCMReducer()
        self.sample_data = self._create_sample_onboarding_data()

    def _create_sample_onboarding_data(self) -> dict:
        """Create comprehensive sample onboarding data for all 23 steps."""
        return {
            "metadata": {
                "workspace_id": "test-workspace-123",
                "user_id": "test-user-456",
            },
            "step_1": {
                "data": {
                    "company_name": "TestCorp Inc.",
                    "website": "https://testcorp.com",
                    "industry": "technology",
                    "stage": "seed",
                    "description": "AI-powered business intelligence platform",
                    "founded_year": 2023,
                    "employee_count": "11-50",
                    "revenue_range": "$1M-$5M",
                    "headquarters": "San Francisco, CA",
                }
            },
            "step_2": {
                "data": {
                    "value_proposition": "Transform data into actionable insights with AI"
                }
            },
            "step_3": {
                "data": {
                    "contradictions": [
                        {
                            "type": "market_positioning",
                            "description": "Premium product with mass-market pricing",
                            "severity": "high",
                        }
                    ]
                }
            },
            "step_4": {"data": {"target_audience": "Mid-market B2B companies"}},
            "step_5": {
                "data": {
                    "problem_statement": "Companies struggle with data analysis complexity"
                }
            },
            "step_6": {"data": {"solution": "Simplified AI-driven analytics platform"}},
            "step_7": {
                "data": {
                    "competitors": [
                        {"name": "CompetitorA", "type": "direct"},
                        {"name": "CompetitorB", "type": "indirect"},
                    ]
                }
            },
            "step_8": {
                "data": {
                    "positioning": {
                        "unique_value": "Easiest to use AI analytics",
                        "market_segment": "SMB B2B",
                    }
                }
            },
            "step_9": {"data": {"revenue_model": "SaaS subscription"}},
            "step_10": {"data": {"pricing_strategy": "Tiered pricing based on usage"}},
            "step_11": {"data": {"go_to_market": "Direct sales + channel partners"}},
            "step_12": {
                "data": {
                    "values": [
                        {"value": "innovation", "description": "Push boundaries"},
                        {"value": "simplicity", "description": "Make complex simple"},
                    ]
                }
            },
            "step_13": {
                "data": {
                    "personality": {
                        "traits": ["innovative", "reliable", "approachable"]
                    }
                }
            },
            "step_14": {
                "data": {
                    "icps": [
                        {
                            "name": "Tech Startups",
                            "description": "Early-stage technology companies",
                            "company_size": "11-50",
                            "vertical": "technology",
                            "confidence_score": 0.9,
                        },
                        {
                            "name": "Digital Agencies",
                            "description": "Marketing agencies needing data insights",
                            "company_size": "51-200",
                            "vertical": "marketing",
                            "confidence_score": 0.8,
                        },
                    ]
                }
            },
            "step_15": {
                "data": {
                    "pain_points": [
                        {
                            "category": "technical",
                            "description": "Complex data integration",
                            "severity": 8,
                        }
                    ]
                }
            },
            "step_16": {
                "data": {
                    "goals": [
                        {
                            "category": "business",
                            "description": "Improve decision making",
                            "priority": "high",
                        }
                    ]
                }
            },
            "step_17": {
                "data": {
                    "messaging": {
                        "primary_message": "Data insights made simple",
                        "tone": "professional yet approachable",
                    }
                }
            },
            "step_18": {
                "data": {"content_strategy": "Educational blog + case studies"}
            },
            "step_19": {"data": {"sales_strategy": "Consultative selling approach"}},
            "step_20": {
                "data": {
                    "channels": [
                        {"type": "website", "effectiveness": "high"},
                        {"type": "linkedin", "effectiveness": "medium"},
                    ]
                }
            },
            "step_21": {
                "data": {"market_sizing": {"tam": "$10B", "sam": "$2B", "som": "$100M"}}
            },
            "step_22": {
                "data": {
                    "goals": [
                        {"title": "Reach 1000 customers", "priority": "high"},
                        {"title": "Expand to Europe", "priority": "medium"},
                    ],
                    "kpis": [
                        {"name": "MRR", "target": "$100K"},
                        {"name": "CAC", "target": "$500"},
                    ],
                }
            },
            "step_23": {
                "data": {
                    "team": {"founders": 2, "engineers": 5, "sales": 3},
                    "resources": {
                        "funding": "$2M seed round",
                        "burn_rate": "$50K/month",
                    },
                }
            },
        }

    def test_extract_foundation_complete_data(self):
        """Test foundation extraction with complete onboarding data."""
        foundation = self.reducer._extract_foundation(self.sample_data)

        # Verify structure
        assert "company_profile" in foundation
        assert "intelligence" in foundation
        assert "validation" in foundation

        # Verify company profile
        company_profile = foundation["company_profile"]
        assert company_profile["name"] == "TestCorp Inc."
        assert company_profile["website"] == "https://testcorp.com"
        assert company_profile["industry"] == "technology"
        assert company_profile["stage"] == "seed"

        # Verify intelligence
        intelligence = foundation["intelligence"]
        assert intelligence["evidence_count"] > 0
        assert len(intelligence["facts"]) > 0
        assert len(intelligence["icps"]) == 2
        assert "positioning" in intelligence
        assert "messaging" in intelligence

        # Verify validation
        validation = foundation["validation"]
        assert validation["completeness_score"] == 100.0
        assert len(validation["missing_fields"]) == 0
        assert len(validation["warnings"]) == 0

    def test_extract_foundation_missing_critical_fields(self):
        """Test foundation extraction with missing critical fields."""
        incomplete_data = {
            "step_1": {"data": {}},  # Missing company_name
            "step_14": {"data": {}},  # Missing ICPs
        }

        foundation = self.reducer._extract_foundation(incomplete_data)

        validation = foundation["validation"]
        assert validation["completeness_score"] < 100.0
        assert "step_1.company_name" in validation["missing_fields"]
        assert "step_14.icps" in validation["missing_fields"]
        assert len(validation["warnings"]) > 0

    def test_extract_foundation_partial_data(self):
        """Test foundation extraction with partial step data."""
        partial_data = {
            "step_1": {
                "data": {
                    "company_name": "Partial Corp",
                    # Missing other fields
                }
            },
            "step_2": {"data": {"value_proposition": "Some value prop"}},
            # Missing many other steps
        }

        foundation = self.reducer._extract_foundation(partial_data)

        # Should still extract what's available
        assert foundation["company_profile"]["name"] == "Partial Corp"
        assert foundation["company_profile"]["value_proposition"] == "Some value prop"

        # Should track missing fields
        validation = foundation["validation"]
        assert validation["completeness_score"] < 100.0
        assert len(validation["missing_fields"]) > 0

    def test_extract_foundation_no_data(self):
        """Test foundation extraction with no onboarding data."""
        foundation = self.reducer._extract_foundation({})

        # Should return empty structure with validation warnings
        assert foundation["company_profile"] == {}
        assert foundation["intelligence"]["evidence_count"] == 0
        assert len(foundation["intelligence"]["facts"]) == 0

        validation = foundation["validation"]
        assert validation["completeness_score"] == 0.0
        assert len(validation["warnings"]) > 0

    def test_extract_foundation_evidence_counting(self):
        """Test evidence counting logic."""
        foundation = self.reducer._extract_foundation(self.sample_data)

        intelligence = foundation["intelligence"]
        assert intelligence["evidence_count"] > 0

        # ICPs should be weighted heavily (3 points each)
        assert intelligence["evidence_count"] >= 6  # 2 ICPs * 3 points

        # Facts should be tracked
        assert len(intelligence["facts"]) > 0
        assert any(
            "Company name: TestCorp Inc." in fact for fact in intelligence["facts"]
        )

    def test_extract_foundation_logging(self):
        """Test logging of validation results."""
        with patch.object(
            logging.getLogger("backend.integration.bcm_reducer"), "warning"
        ) as mock_warning, patch.object(
            logging.getLogger("backend.integration.bcm_reducer"), "info"
        ) as mock_info:

            # Test with missing data
            incomplete_data = {"step_1": {"data": {}}}
            self.reducer._extract_foundation(incomplete_data)

            # Should log warnings
            mock_warning.assert_called()

            # Test with complete data
            self.reducer._extract_foundation(self.sample_data)

            # Should log info
            mock_info.assert_called()

    def test_extract_foundation_step_data_extraction(self):
        """Test step data extraction edge cases."""
        # Test with step data without 'data' wrapper
        data_without_wrapper = {
            "step_1": {"company_name": "Direct Corp", "industry": "healthcare"}
        }

        foundation = self.reducer._extract_foundation(data_without_wrapper)

        # Should still extract data
        assert foundation["company_profile"]["name"] == "Direct Corp"
        assert foundation["company_profile"]["industry"] == "healthcare"

    def test_extract_foundation_industry_stage_mapping(self):
        """Test that industry and stage mapping works in foundation context."""
        foundation = self.reducer._extract_foundation(self.sample_data)

        # The foundation extraction preserves the raw string values
        # The enum mapping happens in _extract_company_info
        assert foundation["company_profile"]["industry"] == "technology"
        assert foundation["company_profile"]["stage"] == "seed"

    def test_extract_foundation_completeness_calculation(self):
        """Test completeness score calculation."""
        # Test with exactly half the steps
        half_data = {}
        for i in range(1, 13):  # Steps 1-12
            half_data[f"step_{i}"] = {"data": {"field": f"value_{i}"}}

        foundation = self.reducer._extract_foundation(half_data)
        validation = foundation["validation"]

        # Should be approximately 50% complete
        assert 45.0 <= validation["completeness_score"] <= 55.0

    def test_extract_foundation_icp_weighting(self):
        """Test that ICPs are weighted heavily in evidence counting."""
        data_with_icps = {
            "step_14": {
                "data": {"icps": [{"name": "ICP1"}, {"name": "ICP2"}, {"name": "ICP3"}]}
            }
        }

        foundation = self.reducer._extract_foundation(data_with_icps)
        intelligence = foundation["intelligence"]

        # 3 ICPs * 3 points each = 9 evidence points minimum
        assert intelligence["evidence_count"] >= 9
        assert len(intelligence["icps"]) == 3

    @pytest.mark.parametrize(
        "step_number,expected_field",
        [
            (1, "company_name"),
            (2, "value_proposition"),
            (3, "contradictions"),
            (4, "target_audience"),
            (5, "problem_statement"),
            (6, "solution"),
            (7, "competitors"),
            (8, "positioning"),
            (9, "revenue_model"),
            (10, "pricing_strategy"),
            (11, "go_to_market"),
            (12, "values"),
            (13, "personality"),
            (14, "icps"),
            (15, "pain_points"),
            (16, "goals"),
            (17, "messaging"),
            (18, "content_strategy"),
            (19, "sales_strategy"),
            (20, "channels"),
            (21, "market_sizing"),
            (22, "goals"),
            (23, "team"),
        ],
    )
    def test_extract_foundation_individual_steps(self, step_number, expected_field):
        """Test extraction of individual step data."""
        step_data = {
            f"step_{step_number}": {
                "data": {expected_field: f"test_value_{step_number}"}
            }
        }

        foundation = self.reducer._extract_foundation(step_data)

        # Should extract the expected field
        if step_number == 1:  # Company name goes to company_profile
            assert (
                foundation["company_profile"].get(expected_field)
                == f"test_value_{step_number}"
            )
        elif step_number == 14:  # ICPs go to intelligence
            assert expected_field in foundation["intelligence"]
        elif step_number in [7, 8]:  # Competitive and positioning go to intelligence
            assert expected_field in foundation["intelligence"]
        else:
            # Most fields go to company_profile
            assert (
                foundation["company_profile"].get(expected_field)
                == f"test_value_{step_number}"
            )


if __name__ == "__main__":
    pytest.main([__file__])
