"""
BCM Reducer Test Suite

Comprehensive tests for Business Context Manifest (BCM) reducer functionality
including extraction, compression, token management, and integration tests.
"""

import pytest
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List

# Import BCM reducer and dependencies
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.integration.bcm_reducer import BCMReducer
from backend.services.token_compressor import TokenCompressor, compress_bcm_to_budget
from backend.utils.token_helpers import count_tokens_safe, validate_token_budget

# Sample test data
SAMPLE_ONBOARDING_DATA = {
    "version": "2.0",
    "generated_at": datetime.utcnow().isoformat(),
    "session_id": "test_session_123",
    "metadata": {
        "workspace_id": "test_workspace",
        "user_id": "test_user_123"
    },
    "progress": {
        "completed_steps": 23,
        "total_steps": 23,
        "completion_percentage": 100.0
    },
    "steps": {
        "step_1": {
            "company_name": "TestCorp Inc.",
            "website": "https://testcorp.com",
            "industry": "technology",
            "stage": "seed",
            "description": "A innovative technology company building solutions for businesses",
            "founded_year": 2023,
            "employee_count": 5,
            "revenue_range": "0-100k",
            "headquarters": "San Francisco, CA"
        },
        "step_2": {
            "value_proposition": "We help businesses streamline their operations through AI-powered automation"
        },
        "step_7": {
            "competitors": [
                {
                    "name": "CompetitorA",
                    "description": "Large enterprise solution provider",
                    "strengths": ["Market presence", "Resources"],
                    "weaknesses": ["Slow innovation", "High pricing"]
                },
                {
                    "name": "CompetitorB",
                    "description": "Startup in same space",
                    "strengths": ["Agile", "Innovative"],
                    "weaknesses": ["Limited resources", "Unproven"]
                }
            ]
        },
        "step_8": {
            "positioning": "Premium AI automation for mid-market businesses"
        },
        "step_12": {
            "values": ["Innovation", "Customer Success", "Integrity", "Excellence"],
            "personality": "Innovative, reliable, customer-focused"
        },
        "step_14": {
            "icps": [
                {
                    "name": "Mid-Market Manufacturing",
                    "description": "Manufacturing companies with 100-500 employees looking to modernize operations",
                    "company_size": "100-500",
                    "vertical": "manufacturing",
                    "geography": ["North America", "Europe"],
                    "pains": [
                        {
                            "category": "inefficiency",
                            "description": "Outdated manual processes causing delays",
                            "severity": 8,
                            "frequency": "daily"
                        },
                        {
                            "category": "cost",
                            "description": "High operational costs eating into margins",
                            "severity": 7,
                            "frequency": "monthly"
                        }
                    ],
                    "goals": [
                        {
                            "category": "efficiency",
                            "description": "Reduce operational costs by 30%",
                            "priority": "high",
                            "timeline": "12 months"
                        }
                    ],
                    "objections": [
                        {
                            "type": "price",
                            "description": "Too expensive for our budget",
                            "response": "ROI achieved within 6 months"
                        }
                    ],
                    "triggers": [
                        {
                            "event": "Budget planning cycle",
                            "timing": "Q4",
                            "impact": "High"
                        }
                    ]
                },
                {
                    "name": "Healthcare Providers",
                    "description": "Small to medium healthcare practices seeking efficiency improvements",
                    "company_size": "50-200",
                    "vertical": "healthcare",
                    "geography": ["North America"],
                    "pains": [
                        {
                            "category": "compliance",
                            "description": "Regulatory compliance complexity",
                            "severity": 9,
                            "frequency": "ongoing"
                        }
                    ],
                    "goals": [
                        {
                            "category": "compliance",
                            "description": "Improve compliance reporting accuracy",
                            "priority": "critical",
                            "timeline": "6 months"
                        }
                    ]
                }
            ]
        },
        "step_17": {
            "messaging": {
                "primary": "AI-powered automation for modern businesses",
                "secondary": "Transform your operations with intelligent automation",
                "tone": "Professional, innovative, trustworthy"
            }
        },
        "step_20": {
            "channels": [
                {
                    "name": "Direct Sales",
                    "type": "direct",
                    "priority": "high",
                    "description": "Direct outreach to target companies"
                },
                {
                    "name": "Content Marketing",
                    "type": "content",
                    "priority": "medium",
                    "description": "Educational content about automation benefits"
                }
            ],
            "strategy_summary": "Focus on direct sales to high-value prospects supported by thought leadership content"
        },
        "step_21": {
            "market_sizing": {
                "tam": 50000000000,  # $50B
                "sam": 5000000000,   # $5B
                "som": 500000000     # $500M
            },
            "verticals": ["manufacturing", "healthcare", "retail", "financial_services"],
            "geography": ["North America", "Europe", "Asia Pacific"]
        },
        "step_22": {
            "goals": [
                {
                    "title": "Acquire 100 customers",
                    "timeline": "12 months",
                    "category": "growth"
                },
                {
                    "title": "Reach $1M ARR",
                    "timeline": "18 months",
                    "category": "revenue"
                }
            ],
            "kpis": [
                {
                    "name": "Monthly Recurring Revenue",
                    "target": "$100K",
                    "frequency": "monthly"
                },
                {
                    "name": "Customer Acquisition Cost",
                    "target": "$5K",
                    "frequency": "quarterly"
                }
            ]
        }
    }
}

class TestBCMReducer:
    """Test suite for BCM Reducer functionality."""

    @pytest.fixture
    def bcm_reducer(self):
        """Create BCM reducer instance for testing."""
        return BCMReducer()

    @pytest.fixture
    def sample_onboarding_data(self):
        """Sample onboarding data for testing."""
        return SAMPLE_ONBOARDING_DATA.copy()

    @pytest.fixture
    def minimal_onboarding_data(self):
        """Minimal onboarding data for edge case testing."""
        return {
            "version": "2.0",
            "generated_at": datetime.utcnow().isoformat(),
            "session_id": "minimal_session",
            "metadata": {
                "workspace_id": "test_workspace",
                "user_id": "test_user"
            },
            "progress": {
                "completed_steps": 3,
                "total_steps": 23,
                "completion_percentage": 13.0
            },
            "steps": {
                "step_1": {
                    "company_name": "Minimal Corp",
                    "industry": "technology"
                },
                "step_14": {
                    "icps": [
                        {
                            "name": "Basic ICP",
                            "description": "Simple customer profile"
                        }
                    ]
                ]
            }
        }

    @pytest.mark.asyncio
    async def test_bcm_reducer_initialization(self, bcm_reducer):
        """Test BCM reducer initialization."""
        assert bcm_reducer.max_token_budget == 1200
        assert bcm_reducer.encoding_name == "cl100k_base"

        # Test tokenizer availability
        if bcm_reducer.tokenizer:
            assert bcm_reducer.tokenizer.name == "cl100k_base"

    @pytest.mark.asyncio
    async def test_complete_bcm_generation(self, bcm_reducer, sample_onboarding_data):
        """Test complete BCM generation from sample data."""
        manifest = await bcm_reducer.reduce(sample_onboarding_data)

        # Verify manifest structure
        assert manifest is not None
        assert manifest.version == "2.0"
        assert manifest.workspace_id == "test_workspace"
        assert manifest.user_id == "test_user_123"

        # Verify company info
        assert manifest.company.name == "TestCorp Inc."
        assert manifest.company.industry.value == "technology"
        assert manifest.company.stage.value == "seed"

        # Verify ICPs
        assert len(manifest.icps) > 0
        assert any(icp.name == "Mid-Market Manufacturing" for icp in manifest.icps)

        # Verify competitors
        assert len(manifest.competitors) > 0

        # Verify completion percentage
        assert manifest.completion_percentage == 100.0

    @pytest.mark.asyncio
    async def test_company_info_extraction(self, bcm_reducer, sample_onboarding_data):
        """Test company information extraction."""
        company_info = bcm_reducer._extract_company_info(sample_onboarding_data)

        assert company_info.name == "TestCorp Inc."
        assert company_info.website == "https://testcorp.com"
        assert company_info.industry.value == "technology"
        assert company_info.stage.value == "seed"
        assert company_info.employee_count == 5
        assert company_info.founded_year == 2023

    @pytest.mark.asyncio
    async def test_icp_extraction(self, bcm_reducer, sample_onboarding_data):
        """Test ICP extraction and validation."""
        icps = bcm_reducer._extract_icps(sample_onboarding_data)

        assert len(icps) >= 1
        assert len(icps) <= 3  # Should be limited to 3 ICPs max

        # Check first ICP
        first_icp = icps[0]
        assert first_icp.name == "Mid-Market Manufacturing"
        assert first_icp.company_size == "100-500"
        assert first_icp.vertical == "manufacturing"

        # Check pains
        assert len(first_icp.pains) >= 1
        pain = first_icp.pains[0]
        assert pain.category == "inefficiency"
        assert pain.severity == 8

        # Check goals
        assert len(first_icp.goals) >= 1
        goal = first_icp.goals[0]
        assert goal.category == "efficiency"
        assert goal.priority == "high"

        # Check confidence score
        assert 0.0 <= first_icp.confidence_score <= 1.0

    @pytest.mark.asyncio
    async def test_competitive_data_extraction(self, bcm_reducer, sample_onboarding_data):
        """Test competitive data extraction."""
        competitive_data = bcm_reducer._extract_competitive_data(sample_onboarding_data)

        assert "competitors" in competitive_data
        assert "direct_competitors" in competitive_data
        assert "validation" in competitive_data

        # Check validation
        validation = competitive_data["validation"]
        assert "completeness_score" in validation
        assert "warnings" in validation
        assert "missing_fields" in validation

    @pytest.mark.asyncio
    async def test_messaging_data_extraction(self, bcm_reducer, sample_onboarding_data):
        """Test messaging data extraction."""
        messaging_data = bcm_reducer._extract_messaging_data(sample_onboarding_data)

        assert "messaging" in messaging_data
        assert "value_prop" in messaging_data
        assert "taglines" in messaging_data
        assert "key_messages" in messaging_data
        assert "soundbites" in messaging_data

        # Check messaging content
        messaging = messaging_data["messaging"]
        assert "primary" in messaging
        assert messaging["primary"] == "AI-powered automation for modern businesses"

    @pytest.mark.asyncio
    async def test_token_counting(self, bcm_reducer, sample_onboarding_data):
        """Test token counting functionality."""
        manifest = await bcm_reducer.reduce(sample_onboarding_data)

        if bcm_reducer.tokenizer:
            token_count = bcm_reducer._count_tokens(manifest.dict())
            assert token_count > 0
            assert isinstance(token_count, int)

            # Test with different data types
            text_tokens = bcm_reducer._count_tokens("Sample text for testing")
            assert text_tokens > 0

            dict_tokens = bcm_reducer._count_tokens({"key": "value", "number": 123})
            assert dict_tokens > 0

    @pytest.mark.asyncio
    async def test_compression_to_budget(self, bcm_reducer, sample_onboarding_data):
        """Test compression to token budget."""
        manifest = await bcm_reducer.reduce(sample_onboarding_data)

        if bcm_reducer.tokenizer:
            original_tokens = bcm_reducer._count_tokens(manifest.dict())

            # Create a larger manifest to test compression
            large_data = sample_onboarding_data.copy()

            # Add verbose descriptions to increase token count
            for step_key, step_data in large_data["steps"].items():
                if isinstance(step_data, dict):
                    step_data["verbose_description"] = "This is a very long and verbose description " * 50

            large_manifest = await bcm_reducer.reduce(large_data)
            large_tokens = bcm_reducer._count_tokens(large_manifest.dict())

            if large_tokens > bcm_reducer.max_token_budget:
                # Test compression
                compressed = bcm_reducer._compress_to_budget(large_manifest)
                compressed_tokens = bcm_reducer._count_tokens(compressed.dict())

                assert compressed_tokens <= bcm_reducer.max_token_budget
                assert compressed_tokens < large_tokens

    @pytest.mark.asyncio
    async def test_checksum_computation(self, bcm_reducer, sample_onboarding_data):
        """Test checksum computation and verification."""
        manifest = await bcm_reducer.reduce(sample_onboarding_data)
        manifest_dict = manifest.dict()

        # Compute checksum
        checksum = bcm_reducer._compute_checksum(manifest_dict)

        assert checksum is not None
        assert len(checksum) == 64  # SHA256 produces 64 character hex string
        assert all(c in '0123456789abcdef' for c in checksum.lower())

        # Verify checksum
        is_valid = bcm_reducer._verify_checksum(manifest_dict, checksum)
        assert is_valid is True

        # Test with modified data
        modified_dict = manifest_dict.copy()
        modified_dict["company"]["name"] = "Modified Name"

        is_invalid = bcm_reducer._verify_checksum(modified_dict, checksum)
        assert is_invalid is False

    @pytest.mark.asyncio
    async def test_minimal_data_handling(self, bcm_reducer, minimal_onboarding_data):
        """Test handling of minimal/incomplete data."""
        manifest = await bcm_reducer.reduce(minimal_onboarding_data)

        # Should still generate a valid manifest
        assert manifest is not None
        assert manifest.workspace_id == "test_workspace"
        assert manifest.completion_percentage == 13.0

        # Should handle missing data gracefully
        assert manifest.company.name == "Minimal Corp"
        # Other fields should have default values or be empty

    @pytest.mark.asyncio
    async def test_error_handling(self, bcm_reducer):
        """Test error handling with invalid data."""
        # Test with empty data
        empty_data = {}

        try:
            manifest = await bcm_reducer.reduce(empty_data)
            # Should handle gracefully with default values
            assert manifest is not None
        except Exception as e:
            # If it raises, should be a meaningful error
            assert "error" in str(e).lower() or "invalid" in str(e).lower()

        # Test with malformed data
        malformed_data = {
            "steps": {
                "step_1": "not a dictionary"
            }
        }

        try:
            manifest = await bcm_reducer.reduce(malformed_data)
            # Should handle gracefully
            assert manifest is not None
        except Exception as e:
            # Should not crash completely
            assert not isinstance(e, KeyboardInterrupt)

    def test_icp_prioritization(self, bcm_reducer):
        """Test ICP prioritization logic."""
        # Create mock ICPs with different confidence scores
        from backend.schemas.bcm_schema import ICPProfile

        icps = [
            ICPProfile(
                name="High Confidence ICP",
                description="Well-defined profile",
                confidence_score=0.9
            ),
            ICPProfile(
                name="Medium Confidence ICP",
                description="Partially defined",
                confidence_score=0.6
            ),
            ICPProfile(
                name="Low Confidence ICP",
                description="Poorly defined",
                confidence_score=0.2
            ),
            ICPProfile(
                name="Another High Confidence",
                description="Another well-defined",
                confidence_score=0.85
            )
        ]

        prioritized = bcm_reducer._prioritize_icps(icps)

        # Should be sorted by confidence (descending)
        assert prioritized[0].confidence_score >= prioritized[1].confidence_score
        assert len(prioritized) <= 3  # Should limit to 3 ICPs

        # Should filter out low confidence ICPs
        assert all(icp.confidence_score >= 0.3 for icp in prioritized)

class TestTokenCompressor:
    """Test suite for Token Compressor functionality."""

    @pytest.fixture
    def compressor(self):
        """Create token compressor for testing."""
        return TokenCompressor(max_tokens=100)

    def test_token_counting(self, compressor):
        """Test token counting."""
        text = "This is a sample text for token counting."
        tokens = compressor.count_tokens(text)

        assert tokens > 0
        assert isinstance(tokens, int)

        # Test with dictionary
        data = {"key": "value", "number": 123}
        dict_tokens = compressor.count_tokens(data)
        assert dict_tokens > 0

    def test_text_compression(self, compressor):
        """Test text compression."""
        long_text = "This is a very long text that should be compressed. " * 20
        target_tokens = 10

        compressed = compressor.compress_text(long_text, target_tokens)

        assert len(compressed) <= len(long_text)
        assert compressor.count_tokens(compressed) <= target_tokens * 1.2  # Allow some tolerance

    def test_dict_compression(self, compressor):
        """Test dictionary compression."""
        data = {
            "name": "Test Item",
            "description": "This is a very long description that should be compressed when the token budget is exceeded. " * 10,
            "details": "Additional details that are less important" * 5,
            "critical_info": "This must be preserved"
        }

        target_tokens = 50
        compressed = compressor.compress_dict(data, target_tokens)

        assert compressor.count_tokens(compressed) <= target_tokens * 1.2
        assert "critical_info" in str(compressed)  # Important info should be preserved

    def test_bcm_manifest_compression(self, compressor):
        """Test BCM manifest compression."""
        manifest = {
            "company": {"name": "Test Corp", "description": "A" * 1000},
            "icps": [{"name": "ICP 1", "description": "B" * 1000}],
            "competitors": [{"name": "Comp 1", "details": "C" * 1000}],
            "messaging": {"primary": "D" * 1000},
            "less_important": {"data": "E" * 1000}
        }

        target_tokens = 100
        compressed = compressor.compress_bcm_manifest(manifest, target_tokens)

        assert compressor.count_tokens(compressed) <= target_tokens * 1.2
        assert "company" in compressed  # Critical sections should be preserved

class TestTokenHelpers:
    """Test suite for Token Helper utilities."""

    def test_token_counting_safe(self):
        """Test safe token counting."""
        text = "Sample text for testing"
        tokens = count_tokens_safe(text)
        assert tokens > 0

        # Test with dictionary
        data = {"key": "value"}
        dict_tokens = count_tokens_safe(data)
        assert dict_tokens > 0

    def test_token_budget_validation(self):
        """Test token budget validation."""
        manifest = {
            "section1": "Short text",
            "section2": {"data": "Slightly longer text " * 10},
            "section3": ["item1", "item2", "item3"]
        }

        is_valid, total_tokens, section_tokens = validate_token_budget(manifest, 100)

        assert isinstance(is_valid, bool)
        assert total_tokens > 0
        assert isinstance(section_tokens, dict)
        assert len(section_tokens) == 3

    def test_token_usage_summary(self):
        """Test token usage summary generation."""
        from backend.utils.token_helpers import get_token_usage_summary

        manifest = {
            "company": {"name": "Test", "description": "A company" * 10},
            "icps": [{"name": "ICP", "description": "Customer profile" * 5}]
        }

        summary = get_token_usage_summary(manifest)

        assert "total_tokens" in summary
        assert "max_tokens" in summary
        assert "is_within_budget" in summary
        assert "utilization_percentage" in summary
        assert "section_breakdown" in summary

# Integration Tests
class TestBCMIntegration:
    """Integration tests for BCM system."""

    @pytest.mark.asyncio
    async def test_end_to_end_bcm_generation(self):
        """Test end-to-end BCM generation pipeline."""
        # Create BCM reducer
        reducer = BCMReducer()

        # Generate BCM from sample data
        manifest = await reducer.reduce(SAMPLE_ONBOARDING_DATA)

        # Verify manifest structure
        assert manifest is not None
        assert manifest.version == "2.0"

        # Test token compression
        compressed_manifest = compress_bcm_to_budget(manifest.dict(), 1200)

        # Verify compression worked
        original_tokens = count_tokens_safe(manifest.dict())
        compressed_tokens = count_tokens_safe(compressed_manifest)

        if original_tokens > 1200:
            assert compressed_tokens <= 1200
            assert compressed_tokens < original_tokens

        # Test checksum
        checksum = reducer._compute_checksum(compressed_manifest)
        assert len(checksum) == 64

        # Verify checksum
        is_valid = reducer._verify_checksum(compressed_manifest, checksum)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_bcm_with_realistic_data(self):
        """Test BCM generation with realistic onboarding data."""
        # Create realistic onboarding data
        realistic_data = {
            "version": "2.0",
            "generated_at": datetime.utcnow().isoformat(),
            "session_id": "realistic_session",
            "metadata": {
                "workspace_id": "company_workspace",
                "user_id": "business_user"
            },
            "progress": {
                "completed_steps": 23,
                "total_steps": 23,
                "completion_percentage": 100.0
            },
            "steps": {}
        }

        # Add realistic step data
        for i in range(1, 24):
            step_key = f"step_{i}"
            realistic_data["steps"][step_key] = {
                "field1": f"Value for step {i}",
                "field2": f"Description for step {i} " * 5,
                "field3": ["item1", "item2", "item3"],
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            }

        # Generate BCM
        reducer = BCMReducer()
        manifest = await reducer.reduce(realistic_data)

        # Verify it handles realistic data
        assert manifest is not None
        assert manifest.completion_percentage == 100.0
        assert len(manifest.raw_step_ids) == 23

# Performance Tests
class TestBCMPerformance:
    """Performance tests for BCM system."""

    @pytest.mark.asyncio
    async def test_large_dataset_performance(self):
        """Test performance with large datasets."""
        import time

        # Create large dataset
        large_data = SAMPLE_ONBOARDING_DATA.copy()

        # Add verbose content to increase size
        for step_key in large_data["steps"]:
            step = large_data["steps"][step_key]
            if isinstance(step, dict):
                step["large_field"] = "Large content " * 1000
                step["detailed_description"] = "Detailed description " * 500

        # Measure performance
        start_time = time.time()
        reducer = BCMReducer()
        manifest = await reducer.reduce(large_data)
        end_time = time.time()

        processing_time = end_time - start_time

        # Should complete within reasonable time (adjust threshold as needed)
        assert processing_time < 10.0  # 10 seconds max
        assert manifest is not None

        # Test compression performance
        compression_start = time.time()
        compressed = reducer._compress_to_budget(manifest)
        compression_end = time.time()

        compression_time = compression_end - compression_start
        assert compression_time < 5.0  # 5 seconds max for compression

# Error Handling Tests
class TestBCMErrorHandling:
    """Error handling tests for BCM system."""

    @pytest.mark.asyncio
    async def test_malformed_data_handling(self):
        """Test handling of malformed data."""
        reducer = BCMReducer()

        # Test with None values
        malformed_data = {
            "steps": {
                "step_1": None,
                "step_2": {"field": None}
            }
        }

        try:
            manifest = await reducer.reduce(malformed_data)
            # Should handle gracefully
            assert manifest is not None
        except Exception as e:
            # Should provide meaningful error
            assert isinstance(e, (ValueError, KeyError, TypeError))

    @pytest.mark.asyncio
    async def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        reducer = BCMReducer()

        # Data missing critical fields
        incomplete_data = {
            "steps": {
                "step_1": {"some_field": "value"}  # Missing company_name
            }
        }

        manifest = await reducer.reduce(incomplete_data)

        # Should still produce a manifest with defaults
        assert manifest is not None
        assert manifest.company.name == ""  # Default empty value

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
