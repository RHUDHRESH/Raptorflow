"""
Tests for Business Context Manifest (BCM) Schema

Comprehensive tests for BCM JSON schema validation, serialization,
and business logic.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError
from schemas.bcm_schema import (
    KPI,
    BCMMigration,
    BCMSchemaValidator,
    BCMVersion,
    BusinessContextManifest,
    ChannelInfo,
    ChannelType,
    CompanyInfo,
    CompanyStage,
    CompetitorInfo,
    Contradiction,
    Goal,
    ICPGoal,
    ICPPainPoint,
    ICPProfile,
    IndustryType,
    MarketSizing,
    MessagingValueProp,
    RecentWin,
    Risk,
)


class TestCompanyInfo:
    """Test CompanyInfo schema."""

    def test_valid_company_info(self):
        """Test creating valid CompanyInfo."""
        company = CompanyInfo(
            name="TechCorp Solutions",
            website="https://techcorp.com",
            industry=IndustryType.TECHNOLOGY,
            description="AI-powered business analytics platform",
            stage=CompanyStage.SERIES_A,
            founded_year=2020,
            employee_count=50,
            revenue_range="$1M-$10M",
            headquarters="San Francisco, CA",
        )

        assert company.name == "TechCorp Solutions"
        assert company.industry == IndustryType.TECHNOLOGY
        assert company.stage == CompanyStage.SERIES_A
        assert company.founded_year == 2020

    def test_invalid_website(self):
        """Test invalid website URL."""
        with pytest.raises(ValidationError) as exc_info:
            CompanyInfo(
                name="TechCorp",
                website="invalid-url",
                industry=IndustryType.TECHNOLOGY,
                description="Test company",
                stage=CompanyStage.SEED,
            )
        assert "Website must start with http:// or https://" in str(exc_info.value)

    def test_invalid_founded_year(self):
        """Test invalid founded year."""
        with pytest.raises(ValidationError) as exc_info:
            CompanyInfo(
                name="TechCorp",
                industry=IndustryType.TECHNOLOGY,
                description="Test company",
                stage=CompanyStage.SEED,
                founded_year=2035,  # Future year
            )
        assert "ensure this value is less than or equal to 2030" in str(exc_info.value)


class TestICPProfile:
    """Test ICP Profile schema."""

    def test_valid_icp_profile(self):
        """Test creating valid ICP profile."""
        pains = [
            ICPPainPoint(
                category="operational",
                description="Inefficient data processing",
                severity=8,
                frequency="daily",
            )
        ]

        goals = [
            ICPGoal(
                category="growth",
                description="Increase revenue by 50%",
                priority="high",
                timeline="12 months",
            )
        ]

        icp = ICPProfile(
            name="Mid-market SaaS companies",
            description="B2B SaaS companies with 50-500 employees",
            company_size="50-500",
            vertical="software",
            geography=["US", "Canada"],
            pains=pains,
            goals=goals,
            confidence_score=0.85,
        )

        assert icp.name == "Mid-market SaaS companies"
        assert len(icp.pains) == 1
        assert len(icp.goals) == 1
        assert icp.confidence_score == 0.85

    def test_invalid_confidence_score(self):
        """Test invalid confidence score."""
        with pytest.raises(ValidationError) as exc_info:
            ICPProfile(
                name="Test ICP",
                description="Test description",
                confidence_score=1.5,  # Invalid > 1.0
            )
        assert "ensure this value is less than or equal to 1" in str(exc_info.value)


class TestMarketSizing:
    """Test MarketSizing schema."""

    def test_valid_market_sizing(self):
        """Test creating valid market sizing."""
        market = MarketSizing(
            tam={"value": 1000000000, "currency": "USD"},
            sam={"value": 100000000, "currency": "USD"},
            som={"value": 10000000, "currency": "USD"},
            currency="USD",
            year=2026,
        )

        assert market.tam["value"] == 1000000000
        assert market.currency == "USD"
        assert market.year == 2026


class TestBusinessContextManifest:
    """Test complete BusinessContextManifest."""

    def test_minimal_valid_manifest(self):
        """Test creating minimal valid manifest."""
        company = CompanyInfo(
            name="Test Corp",
            industry=IndustryType.TECHNOLOGY,
            description="Test company",
            stage=CompanyStage.SEED,
        )

        manifest = BusinessContextManifest(
            version=BCMVersion.V2_0,
            generated_at="2026-01-27T06:30:00Z",
            workspace_id="workspace123",
            company=company,
            value_prop=MessagingValueProp(primary="Test value prop"),
            market=MarketSizing(),
            completion_percentage=25.0,
        )

        assert manifest.version == BCMVersion.V2_0
        assert manifest.workspace_id == "workspace123"
        assert manifest.company.name == "Test Corp"
        assert manifest.completion_percentage == 25.0
        assert manifest.checksum is not None  # Should be auto-generated

    def test_complete_manifest(self):
        """Test creating complete manifest with all fields."""
        company = CompanyInfo(
            name="TechCorp Solutions",
            website="https://techcorp.com",
            industry=IndustryType.TECHNOLOGY,
            description="AI-powered business analytics platform",
            stage=CompanyStage.SERIES_A,
        )

        competitor = CompetitorInfo(
            name="Competitor Corp",
            type="direct",
            strengths=["Brand recognition", "Market share"],
            weaknesses=["Outdated technology"],
        )

        channel = ChannelInfo(
            type=ChannelType.WEBSITE,
            name="Company Website",
            effectiveness="high",
            cost_efficiency="medium",
        )

        goal = Goal(
            title="Increase Revenue",
            description="Grow annual revenue by 50%",
            timeframe="12 months",
            metrics=["Revenue", "Customer acquisition"],
            priority="high",
        )

        kpi = KPI(
            name="Monthly Recurring Revenue",
            description="MRR from subscription customers",
            target=1000000,
            current=500000,
            unit="USD",
            frequency="monthly",
        )

        manifest = BusinessContextManifest(
            version=BCMVersion.V2_0,
            generated_at="2026-01-27T06:30:00Z",
            workspace_id="workspace123",
            user_id="user456",
            company=company,
            direct_competitors=[competitor],
            primary_channels=[channel],
            short_term_goals=[goal],
            kpis=[kpi],
            value_prop=MessagingValueProp(
                primary="Transform your data into actionable insights",
                supporting_points=["AI-powered", "Real-time analytics"],
            ),
            market=MarketSizing(
                tam={"value": 1000000000, "currency": "USD"},
                sam={"value": 100000000, "currency": "USD"},
                som={"value": 10000000, "currency": "USD"},
            ),
            completion_percentage=75.0,
        )

        assert len(manifest.direct_competitors) == 1
        assert len(manifest.primary_channels) == 1
        assert len(manifest.short_term_goals) == 1
        assert len(manifest.kpis) == 1
        assert (
            manifest.value_prop.primary
            == "Transform your data into actionable insights"
        )
        assert manifest.checksum is not None

    def test_invalid_timestamp(self):
        """Test invalid timestamp format."""
        company = CompanyInfo(
            name="Test Corp",
            industry=IndustryType.TECHNOLOGY,
            description="Test company",
            stage=CompanyStage.SEED,
        )

        with pytest.raises(ValidationError) as exc_info:
            BusinessContextManifest(
                version=BCMVersion.V2_0,
                generated_at="invalid-timestamp",
                workspace_id="workspace123",
                company=company,
                value_prop=MessagingValueProp(primary="Test"),
                market=MarketSizing(),
                completion_percentage=25.0,
            )
        assert "Invalid timestamp format" in str(exc_info.value)

    def test_invalid_completion_percentage(self):
        """Test invalid completion percentage."""
        company = CompanyInfo(
            name="Test Corp",
            industry=IndustryType.TECHNOLOGY,
            description="Test company",
            stage=CompanyStage.SEED,
        )

        with pytest.raises(ValidationError) as exc_info:
            BusinessContextManifest(
                version=BCMVersion.V2_0,
                generated_at="2026-01-27T06:30:00Z",
                workspace_id="workspace123",
                company=company,
                value_prop=MessagingValueProp(primary="Test"),
                market=MarketSizing(),
                completion_percentage=150.0,  # Invalid > 100
            )
        assert "Completion percentage must be between 0 and 100" in str(exc_info.value)

    def test_checksum_auto_generation(self):
        """Test automatic checksum generation."""
        company = CompanyInfo(
            name="Test Corp",
            industry=IndustryType.TECHNOLOGY,
            description="Test company",
            stage=CompanyStage.SEED,
        )

        manifest1 = BusinessContextManifest(
            version=BCMVersion.V2_0,
            generated_at="2026-01-27T06:30:00Z",
            workspace_id="workspace123",
            company=company,
            value_prop=MessagingValueProp(primary="Test"),
            market=MarketSizing(),
            completion_percentage=25.0,
        )

        manifest2 = BusinessContextManifest(
            version=BCMVersion.V2_0,
            generated_at="2026-01-27T06:30:00Z",
            workspace_id="workspace123",
            company=company,
            value_prop=MessagingValueProp(primary="Test"),
            market=MarketSizing(),
            completion_percentage=25.0,
        )

        # Same data should generate same checksum
        assert manifest1.checksum == manifest2.checksum

        # Different data should generate different checksum
        manifest3 = BusinessContextManifest(
            version=BCMVersion.V2_0,
            generated_at="2026-01-27T06:30:00Z",
            workspace_id="workspace456",  # Different workspace
            company=company,
            value_prop=MessagingValueProp(primary="Test"),
            market=MarketSizing(),
            completion_percentage=25.0,
        )

        assert manifest1.checksum != manifest3.checksum


class TestBCMSchemaValidator:
    """Test BCM schema validation utilities."""

    def test_validate_manifest_success(self):
        """Test successful manifest validation."""
        manifest_data = {
            "version": "2.0",
            "generated_at": "2026-01-27T06:30:00Z",
            "workspace_id": "workspace123",
            "company": {
                "name": "Test Corp",
                "industry": "technology",
                "description": "Test company description",
                "stage": "seed",
            },
            "value_prop": {"primary": "Test value proposition"},
            "market": {},
            "completion_percentage": 50.0,
        }

        manifest = BCMSchemaValidator.validate_manifest(manifest_data)
        assert isinstance(manifest, BusinessContextManifest)
        assert manifest.company.name == "Test Corp"

    def test_validate_manifest_failure(self):
        """Test manifest validation failure."""
        invalid_data = {
            "version": "2.0",
            "generated_at": "2026-01-27T06:30:00Z",
            "workspace_id": "workspace123",
            "company": {
                "name": "",  # Invalid empty name
                "industry": "technology",
                "description": "Test company",
                "stage": "seed",
            },
            "value_prop": {"primary": "Test value proposition"},
            "market": {},
            "completion_percentage": 50.0,
        }

        with pytest.raises(ValueError) as exc_info:
            BCMSchemaValidator.validate_manifest(invalid_data)
        assert "Invalid BCM manifest" in str(exc_info.value)

    def test_validate_compatibility(self):
        """Test version compatibility validation."""
        manifest = BusinessContextManifest(
            version=BCMVersion.V2_0,
            generated_at="2026-01-27T06:30:00Z",
            workspace_id="workspace123",
            company=CompanyInfo(
                name="Test Corp",
                industry=IndustryType.TECHNOLOGY,
                description="Test",
                stage=CompanyStage.SEED,
            ),
            value_prop=MessagingValueProp(primary="Test"),
            market=MarketSizing(),
            completion_percentage=25.0,
        )

        # Same version should be compatible
        assert (
            BCMSchemaValidator.validate_compatibility(manifest, BCMVersion.V2_0) is True
        )

        # Different version should not be compatible
        assert (
            BCMSchemaValidator.validate_compatibility(manifest, BCMVersion.V1_0)
            is False
        )

    def test_estimate_token_count(self):
        """Test token count estimation."""
        manifest = BusinessContextManifest(
            version=BCMVersion.V2_0,
            generated_at="2026-01-27T06:30:00Z",
            workspace_id="workspace123",
            company=CompanyInfo(
                name="Test Corp",
                industry=IndustryType.TECHNOLOGY,
                description="Test company description",
                stage=CompanyStage.SEED,
            ),
            value_prop=MessagingValueProp(primary="Test value proposition"),
            market=MarketSizing(),
            completion_percentage=25.0,
        )

        token_count = BCMSchemaValidator.estimate_token_count(manifest)
        assert token_count > 0
        assert isinstance(token_count, int)

    def test_validate_size_constraints(self):
        """Test size constraint validation."""
        # Small manifest should pass
        small_manifest = BusinessContextManifest(
            version=BCMVersion.V2_0,
            generated_at="2026-01-27T06:30:00Z",
            workspace_id="workspace123",
            company=CompanyInfo(
                name="Test",
                industry=IndustryType.TECHNOLOGY,
                description="Small",
                stage=CompanyStage.SEED,
            ),
            value_prop=MessagingValueProp(primary="Test"),
            market=MarketSizing(),
            completion_percentage=25.0,
        )

        assert BCMSchemaValidator.validate_size_constraints(small_manifest) is True

    def test_get_schema_json(self):
        """Test getting JSON schema."""
        schema = BCMSchemaValidator.get_schema_json()
        assert isinstance(schema, dict)
        assert "title" in schema
        assert "properties" in schema
        assert "BusinessContextManifest" in schema.get("title", "")


class TestBCMMigration:
    """Test BCM schema migration utilities."""

    def test_migrate_v1_to_v2(self):
        """Test v1 to v2 migration."""
        v1_manifest = {
            "version": "1.0",
            "company": {"name": "Test Corp"},
            "foundation": {"mission": "Test mission"},
            "icps": [],
            "competitive": {},
            "messaging": {},
        }

        v2_manifest = BCMMigration.migrate_v1_to_v2(v1_manifest)

        assert v2_manifest["version"] == "2.0"
        assert "completion_percentage" in v2_manifest
        assert "generated_at" in v2_manifest
        assert v2_manifest["completion_percentage"] == 0.0

    def test_can_migrate(self):
        """Test migration compatibility checking."""
        assert BCMMigration.can_migrate("1.0", "2.0") is True
        assert BCMMigration.can_migrate("1.1", "2.0") is True
        assert BCMMigration.can_migrate("2.0", "1.0") is False
        assert BCMMigration.can_migrate("3.0", "2.0") is False


class TestEnums:
    """Test enum definitions."""

    def test_industry_types(self):
        """Test industry type enums."""
        assert IndustryType.TECHNOLOGY == "technology"
        assert IndustryType.HEALTHCARE == "healthcare"
        assert IndustryType.OTHER == "other"

        # Test that all expected values exist
        expected_industries = [
            "technology",
            "healthcare",
            "finance",
            "retail",
            "manufacturing",
            "education",
            "real_estate",
            "entertainment",
            "food_beverage",
            "transportation",
            "energy",
            "consulting",
            "media",
            "agriculture",
            "construction",
            "other",
        ]

        actual_values = [industry.value for industry in IndustryType]
        for expected in expected_industries:
            assert expected in actual_values

    def test_company_stages(self):
        """Test company stage enums."""
        assert CompanyStage.SEED == "seed"
        assert CompanyStage.SERIES_A == "series_a"
        assert CompanyStage.ENTERPRISE == "enterprise"

        expected_stages = [
            "pre_seed",
            "seed",
            "series_a",
            "series_b",
            "series_c",
            "growth",
            "mature",
            "enterprise",
        ]

        actual_values = [stage.value for stage in CompanyStage]
        for expected in expected_stages:
            assert expected in actual_values

    def test_channel_types(self):
        """Test channel type enums."""
        assert ChannelType.WEBSITE == "website"
        assert ChannelType.EMAIL == "email"
        assert ChannelType.SOCIAL_MEDIA == "social_media"

        expected_channels = [
            "website",
            "social_media",
            "email",
            "paid_search",
            "organic_search",
            "content_marketing",
            "direct_sales",
            "partnerships",
            "events",
            "pr_media",
            "referrals",
            "advertising",
        ]

        actual_values = [channel.value for channel in ChannelType]
        for expected in expected_channels:
            assert expected in actual_values


class TestIntegration:
    """Integration tests for complete BCM workflow."""

    def test_complete_bcm_workflow(self):
        """Test complete BCM creation and validation workflow."""
        # Create company info
        company = CompanyInfo(
            name="TechCorp Solutions",
            website="https://techcorp.com",
            industry=IndustryType.TECHNOLOGY,
            description="AI-powered business analytics platform for enterprises",
            stage=CompanyStage.SERIES_A,
            founded_year=2020,
            employee_count=75,
            revenue_range="$5M-$10M",
        )

        # Create ICP profiles
        icps = [
            ICPProfile(
                name="Enterprise SaaS Companies",
                description="Large B2B SaaS companies with 500+ employees",
                company_size="500+",
                vertical="software",
                geography=["US", "Canada", "UK"],
                pains=[
                    ICPPainPoint(
                        category="operational",
                        description="Manual data analysis processes",
                        severity=7,
                        frequency="weekly",
                    )
                ],
                goals=[
                    ICPGoal(
                        category="efficiency",
                        description="Automate data analysis workflows",
                        priority="high",
                        timeline="6 months",
                    )
                ],
                confidence_score=0.9,
            )
        ]

        # Create competitors
        competitors = [
            CompetitorInfo(
                name="DataAnalytics Inc",
                type="direct",
                strengths=["Market leader", "Comprehensive features"],
                weaknesses=["Expensive", "Complex interface"],
                market_share="35%",
                pricing_model="Enterprise subscription",
            )
        ]

        # Create market sizing
        market = MarketSizing(
            tam={"value": 50000000000, "currency": "USD"},
            sam={"value": 5000000000, "currency": "USD"},
            som={"value": 500000000, "currency": "USD"},
            currency="USD",
            year=2026,
        )

        # Create messaging
        value_prop = MessagingValueProp(
            primary="Transform your enterprise data into actionable insights with AI",
            secondary="Reduce analysis time by 80% while improving accuracy",
            supporting_points=[
                "AI-powered automation",
                "Real-time insights",
                "Enterprise security",
            ],
        )

        # Create channels
        channels = [
            ChannelInfo(
                type=ChannelType.DIRECT_SALES,
                name="Enterprise Sales Team",
                description="Direct sales to enterprise accounts",
                effectiveness="high",
                cost_efficiency="medium",
                target_audience="Enterprise decision makers",
            )
        ]

        # Create goals and KPIs
        goals = [
            Goal(
                title="Achieve $50M ARR",
                description="Reach $50 million annual recurring revenue",
                timeframe="3 years",
                metrics=["ARR", "Customer count", "Market share"],
                priority="high",
            )
        ]

        kpis = [
            KPI(
                name="Customer Acquisition Cost",
                description="Cost to acquire new enterprise customer",
                target=25000,
                current=35000,
                unit="USD",
                frequency="quarterly",
            )
        ]

        # Create complete manifest
        manifest = BusinessContextManifest(
            version=BCMVersion.V2_0,
            generated_at="2026-01-27T06:30:00Z",
            workspace_id="workspace123",
            user_id="user456",
            company=company,
            icps=icps,
            direct_competitors=competitors,
            market=market,
            value_prop=value_prop,
            primary_channels=channels,
            short_term_goals=goals,
            kpis=kpis,
            completion_percentage=85.0,
        )

        # Validate the manifest
        assert BCMSchemaValidator.validate_compatibility(manifest, BCMVersion.V2_0)
        assert BCMSchemaValidator.validate_size_constraints(manifest)

        # Test serialization
        manifest_dict = manifest.dict()
        assert isinstance(manifest_dict, dict)
        assert manifest_dict["company"]["name"] == "TechCorp Solutions"
        assert len(manifest_dict["icps"]) == 1
        assert manifest_dict["completion_percentage"] == 85.0

        # Test JSON serialization
        manifest_json = manifest.json()
        assert isinstance(manifest_json, str)

        # Test round-trip validation
        parsed_manifest = BCMSchemaValidator.validate_manifest(manifest_dict)
        assert parsed_manifest.company.name == manifest.company.name
        assert parsed_manifest.checksum == manifest.checksum


if __name__ == "__main__":
    pytest.main([__file__])
