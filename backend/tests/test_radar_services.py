"""
Tests for Radar Services
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.radar_models import (
    Evidence,
    EvidenceType,
    Signal,
    SignalCategory,
    SignalFreshness,
    SignalStrength,
)
from services.radar_analytics_service import RadarAnalyticsService
from services.radar_integration_service import RadarIntegrationService
from services.radar_notification_service import RadarNotificationService
from services.signal_extraction_service import SignalExtractionService
from services.signal_processing_service import SignalProcessingService


class TestSignalExtractionService:
    """Test signal extraction service."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        service = SignalExtractionService()
        service.crawler = AsyncMock()
        service.llm = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_extract_signals_from_source(self, service):
        """Test signal extraction from source."""
        # Mock crawler response
        service.crawler.scrape_semantic.return_value = {
            "content": "New pricing: $299/month with free trial",
            "title": "Pricing Page",
            "source": "firecrawl",
        }

        signals = await service.extract_signals_from_source(
            "https://example.com/pricing", tenant_id="test-tenant"
        )

        assert len(signals) > 0
        assert signals[0].tenant_id == "test-tenant"
        assert signals[0].source_url == "https://example.com/pricing"

    def test_categorize_content(self, service):
        """Test content categorization."""
        # Test pricing content
        category = service._categorize_content("New pricing: $299/month")
        assert category == SignalCategory.OFFER

        # Test hook content
        category = service._categorize_content("The only AI that works")
        assert category == SignalCategory.HOOK

        # Test proof content
        category = service._categorize_content(
            "Customer testimonials show 95% satisfaction"
        )
        assert category == SignalCategory.PROOF

    def test_calculate_strength(self, service):
        """Test signal strength calculation."""
        strength = service._calculate_strength("Important signal", 3, 0.9)
        assert strength == SignalStrength.HIGH

        strength = service._calculate_strength("Weak signal", 1, 0.3)
        assert strength == SignalStrength.LOW


class TestSignalProcessingService:
    """Test signal processing service."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        service = SignalProcessingService()
        service.llm = AsyncMock()
        return service

    @pytest.fixture
    def sample_signals(self):
        """Create sample signals for testing."""
        return [
            Signal(
                tenant_id="test",
                category=SignalCategory.OFFER,
                title="Pricing Change",
                content="New pricing: $299/month",
                strength=SignalStrength.HIGH,
                freshness=SignalFreshness.FRESH,
                source_competitor="Competitor A",
            ),
            Signal(
                tenant_id="test",
                category=SignalCategory.OFFER,
                title="Similar Pricing",
                content="Similar pricing: $299/month",
                strength=SignalStrength.HIGH,
                freshness=SignalFreshness.FRESH,
                source_competitor="Competitor A",
            ),
        ]

    @pytest.mark.asyncio
    async def test_process_signals(self, service, sample_signals):
        """Test signal processing."""
        processed_signals, clusters = await service.process_signals(
            sample_signals, "test-tenant"
        )

        assert len(processed_signals) <= len(sample_signals)  # Deduplication
        assert len(clusters) >= 0

    def test_are_signals_similar(self, service, sample_signals):
        """Test signal similarity detection."""
        signal1, signal2 = sample_signals

        # Similar signals should be detected
        assert service._are_signals_similar(signal1, signal2) == True

        # Different categories should not be similar
        signal2.category = SignalCategory.HOOK
        assert service._are_signals_similar(signal1, signal2) == False

    def test_update_signal_freshness(self, service, sample_signals):
        """Test freshness updates."""
        # Create old signal
        old_signal = Signal(
            tenant_id="test",
            category=SignalCategory.OFFER,
            title="Old Signal",
            content="Old content",
            strength=SignalStrength.HIGH,
            freshness=SignalFreshness.FRESH,
            created_at=datetime.utcnow() - timedelta(days=15),
        )

        updated = service._update_signal_freshness([old_signal])
        assert updated[0].freshness == SignalFreshness.WARM


class TestRadarIntegrationService:
    """Test radar integration service."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        service = RadarIntegrationService()
        service.llm = AsyncMock()
        return service

    @pytest.fixture
    def sample_signals(self):
        """Create sample signals."""
        return [
            Signal(
                tenant_id="test",
                category=SignalCategory.OFFER,
                title="Pricing Change",
                content="New pricing: $299/month",
                strength=SignalStrength.HIGH,
                freshness=SignalFreshness.FRESH,
            )
        ]

    @pytest.mark.asyncio
    async def test_map_signals_to_moves(self, service, sample_signals):
        """Test signal to move mapping."""
        from models.radar_models import MoveObjective

        mappings = await service.map_signals_to_moves(
            sample_signals, [MoveObjective.ACQUIRE], "test-tenant"
        )

        assert len(mappings) > 0
        assert mappings[0].objective == MoveObjective.ACQUIRE

    @pytest.mark.asyncio
    async def test_generate_experiment_ideas(self, service, sample_signals):
        """Test experiment idea generation."""
        from models.radar_models import MoveObjective, MoveStage

        service.llm.ainvoke.return_value = MagicMock(
            content='["Test pricing at $249/month", "Add annual discount", "Free trial extension"]'
        )

        ideas = await service.generate_experiment_ideas(
            sample_signals[0],
            MoveObjective.ACQUIRE,
            MoveStage.CONVERSION,
            "landing_page",
        )

        assert len(ideas) <= 3
        assert all(isinstance(idea, str) for idea in ideas)

    @pytest.mark.asyncio
    async def test_create_dossier(self, service, sample_signals):
        """Test dossier creation."""
        dossier = await service.create_dossier(
            campaign_id="campaign-123", signals=sample_signals, tenant_id="test-tenant"
        )

        assert dossier.campaign_id == "campaign-123"
        assert len(dossier.pinned_signals) == len(sample_signals)
        assert dossier.tenant_id == "test-tenant"


class TestRadarAnalyticsService:
    """Test radar analytics service."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return RadarAnalyticsService()

    @pytest.fixture
    def sample_signals(self):
        """Create sample signals with different dates."""
        base_time = datetime.utcnow()
        return [
            Signal(
                tenant_id="test",
                category=SignalCategory.OFFER,
                title="Signal 1",
                content="Content 1",
                strength=SignalStrength.HIGH,
                freshness=SignalFreshness.FRESH,
                created_at=base_time - timedelta(days=1),
            ),
            Signal(
                tenant_id="test",
                category=SignalCategory.HOOK,
                title="Signal 2",
                content="Content 2",
                strength=SignalStrength.MEDIUM,
                freshness=SignalFreshness.FRESH,
                created_at=base_time - timedelta(days=5),
            ),
        ]

    @pytest.mark.asyncio
    async def test_analyze_signal_trends(self, service, sample_signals):
        """Test signal trend analysis."""
        trends = await service.analyze_signal_trends(sample_signals, 30)

        assert "period_days" in trends
        assert "total_signals" in trends
        assert "category_trends" in trends
        assert trends["total_signals"] == len(sample_signals)

    @pytest.mark.asyncio
    async def test_analyze_competitor_patterns(self, service, sample_signals):
        """Test competitor pattern analysis."""
        analysis = await service.analyze_competitor_patterns(sample_signals)

        assert "competitors" in analysis
        assert "market_leaders" in analysis
        assert "emerging_threats" in analysis

    @pytest.mark.asyncio
    async def test_generate_market_intelligence(self, service, sample_signals):
        """Test market intelligence generation."""
        intelligence = await service.generate_market_intelligence(sample_signals, [])

        assert "signal_trends" in intelligence
        assert "competitor_analysis" in intelligence
        assert "market_dynamics" in intelligence
        assert "predictive_insights" in intelligence


class TestRadarNotificationService:
    """Test radar notification service."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return RadarNotificationService()

    @pytest.fixture
    def sample_signals(self):
        """Create sample signals."""
        return [
            Signal(
                tenant_id="test",
                category=SignalCategory.OFFER,
                title="High Strength Signal",
                content="Important pricing change",
                strength=SignalStrength.HIGH,
                freshness=SignalFreshness.FRESH,
                source_competitor="Competitor A",
            )
        ]

    @pytest.mark.asyncio
    async def test_process_signal_notifications(self, service, sample_signals):
        """Test notification processing."""
        notifications = await service.process_signal_notifications(sample_signals)

        assert isinstance(notifications, list)
        # Should have high strength signal notification
        high_strength_notifications = [
            n for n in notifications if n["type"] == "high_strength_signal"
        ]
        assert len(high_strength_notifications) > 0

    @pytest.mark.asyncio
    async def test_create_daily_digest(self, service, sample_signals):
        """Test daily digest creation."""
        digest = await service.create_daily_digest(sample_signals, "test-tenant")

        assert digest["type"] == "daily_digest"
        assert "signal_count" in digest
        assert "by_category" in digest
        assert digest["signal_count"] == len(sample_signals)

    def test_apply_tenant_preferences(self, service):
        """Test tenant preference application."""
        preferences = {"high_strength_signals": {"enabled": False, "threshold": 2}}

        customized_rules = service._apply_tenant_preferences(preferences)

        assert customized_rules["high_strength_signals"]["enabled"] == False
        assert customized_rules["high_strength_signals"]["threshold"] == 2


if __name__ == "__main__":
    pytest.main([__file__])
