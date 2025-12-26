import logging
from typing import Any, Dict, List, Optional

from core.config import get_settings
from core.vault import Vault
from services.radar_cache import RadarCache
from services.radar_integration_service import RadarIntegrationService
from services.radar_repository import RadarRepository
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
        settings = get_settings()
        self.repository = RadarRepository(storage_bucket=settings.GCS_INGEST_BUCKET)
        self.cache = RadarCache()

    async def scan_recon(
        self,
        tenant_id: str,
        icp_id: str,
        source_urls: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Performs real competitive signal extraction from sources.
        """
        try:
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
                previous_content = await self.cache.get_source_content(tenant_id, url)
                signals = await self.extraction_service.extract_signals_from_source(
                    url, previous_content=previous_content, tenant_id=tenant_id
                )
                current_content = self.extraction_service.get_last_content(url)
                if current_content:
                    await self.cache.set_source_content(tenant_id, url, current_content)

                for signal in signals:
                    if not signal.source_url:
                        signal.source_url = url
                    if not signal.source_competitor:
                        signal.source_competitor = url.split("//")[-1].split("/")[0]
                    signal.metadata["icp_id"] = icp_id
                all_signals.extend(signals)

            # Process signals (cluster, deduplicate, update freshness)
            processed_signals, clusters = await self.processing_service.process_signals(
                all_signals, tenant_id
            )
            await self.repository.save_clusters(clusters)
            await self.repository.save_signals(processed_signals)

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
        self,
        tenant_id: str,
        campaign_id: str,
        signal_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generates real intelligence dossiers from signals.
        """
        try:
            if not signal_ids:
                signals = await self.repository.fetch_signals(
                    tenant_id, window_days=30, limit=50
                )
            else:
                signals = await self.repository.fetch_signals(
                    tenant_id, signal_ids=signal_ids
                )

            # Create dossierandi intelligence dossier
            dossier = await self.integration_service.create_dossier(
                campaign_id=campaign_id, signals=signals, tenant_id=tenant_id
            )
            await self.repository.save_dossier(dossier)

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

    def _strength_to_numeric(self, strength: str) -> float:
        """Convert strength string to numeric."""
        mapping = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.9,
        }
        key = strength.value if hasattr(strength, "value") else strength
        return mapping.get(key, 0.5)
