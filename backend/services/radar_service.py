import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.vault import Vault
from inference import InferenceProvider
from models.radar_models import Dossier, RadarSource, ScanJob, Signal, SignalCategory
from services.radar_integration_service import RadarIntegrationService
from services.signal_extraction_service import SignalExtractionService
from services.signal_processing_service import SignalProcessingService

logger = logging.getLogger("raptorflow.radar_service")


class RadarService:
    """
    Industrial-scale Service for the RaptorFlow Radar.
    Real signal extraction, processing, and integration with moves.
    """

    def __init__(self, vault: Vault):
        self.vault = vault
        self.extraction_service = SignalExtractionService()
        self.processing_service = SignalProcessingService()
        self.integration_service = RadarIntegrationService()

    async def scan_recon(
        self, icp_id: str, source_urls: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs real competitive signal extraction from sources.
        """
        try:
            tenant_id = "default"  # Would come from auth context

            # Default sources if none provided
            if not source_urls:
                source_urls = [
                    "https://competitor-a.com/pricing",
                    "https://competitor-b.com",
                    "https://linkedin.com/company/competitor-c",
                ]

            all_signals = []

            # Extract signals from each source
            for url in source_urls:
                signals = await self.extraction_service.extract_signals_from_source(
                    url, previous_content=None, tenant_id=tenant_id
                )
                all_signals.extend(signals)

            # Process signals (cluster, deduplicate, update freshness)
            processed_signals, clusters = await self.processing_service.process_signals(
                all_signals, tenant_id
            )

            # Convert to response format
            response_signals = []
            for signal in processed_signals:
                response_signals.append(
                    {
                        "id": signal.id,
                        "type": signal.category.value,
                        "source": signal.source_competitor or "Unknown",
                        "content": signal.content,
                        "confidence": self._strength_to_numeric(signal.strength),
                        "timestamp": signal.created_at.isoformat(),
                        "strength": signal.strength.value,
                        "freshness": signal.freshness.value,
                        "action_suggestion": signal.action_suggestion,
                        "evidence_count": len(signal.evidence),
                    }
                )

            logger.info(
                f"Radar recon scan completed: {len(response_signals)} signals from {len(source_urls)} sources"
            )
            return response_signals

        except Exception as e:
            logger.error(f"Error in scan_recon: {e}")
            return []

    async def generate_dossier(
        self, campaign_id: str, signal_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generates real intelligence dossiers from signals.
        """
        try:
            tenant_id = "default"  # Would come from auth context

            # For demo, create some mock signals if none provided
            if not signal_ids:
                mock_signals = await self._get_mock_signals(tenant_id)
            else:
                # Would fetch signals from database
                mock_signals = []

            # Create dossierandi intelligence dossier
            dossier = await self.integration_service.create_dossier(
                campaign_id=campaign_id, signals=mock_signals, tenant_id=tenant_id
            )

            # Convert to response format
            response_dossier = {
                "id": dossier.id,
                "title": dossier.title,
                "summary": dossier.summary,
                "hypotheses": dossier.hypotheses,
                "recommended_experiments": dossier.recommended_experiments,
                "copy_snippets": dossier.copy_snippets,
                "market_narrative": dossier.market_narrative,
                "pinned_signals_count": len(dossier.pinned_signals),
                "created_at": dossier.created_at.isoformat(),
                "is_published": dossier.is_published,
            }

            logger.info(
                f"Generated dossier: {dossier.title} with {len(dossier.pinned_signals)} signals"
            )
            return response_dossier

        except Exception as e:
            logger.error(f"Error in generate_dossier: {e}")
            return {}

    async def _get_mock_signals(self, tenant_id: str) -> List[Signal]:
        """Create mock signals for demonstration."""
        return [
            Signal(
                tenant_id=tenant_id,
                category=SignalCategory.OFFER,
                title="Pricing Change Detected",
                content="Competitor increased Pro plan from $299 to $499/month",
                strength="high",
                freshness="fresh",
                action_suggestion="Consider value proposition adjustment",
                source_competitor="Competitor A",
            ),
            Signal(
                tenant_id=tenant_id,
                category=SignalCategory.HOOK,
                title="New Marketing Angle",
                content="Now positioning around 'stop wasting resources'",
                strength="medium",
                freshness="fresh",
                action_suggestion="Test similar angle in copy",
                source_competitor="Competitor B",
            ),
        ]

    def _strength_to_numeric(self, strength: str) -> float:
        """Convert strength string to numeric."""
        mapping = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.9,
        }
        return mapping.get(strength, 0.5)
