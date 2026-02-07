"""
Radar Service - Competitive intelligence and signal discovery
"""

import logging
from typing import Any, Dict, List, Optional

from core.vault import Vault
from services.radar_repository import RadarRepository
from services.signal_extraction_service import SignalExtractionService
from services.signal_processing_service import SignalProcessingService

logger = logging.getLogger("raptorflow.radar_service")


class RadarService:
    """
    Service for managing competitive intelligence radar.
    Orchestrates signal discovery, extraction, processing, and dossier generation.
    """

    def __init__(self, vault: Optional[Vault] = None):
        self.vault = vault or Vault()
        self.repository = RadarRepository()
        self.extraction_service = SignalExtractionService()
        self.processing_service = SignalProcessingService()

    async def scan_recon(
        self, tenant_id: str, icp_id: str, source_urls: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs a reconnaissance scan for competitive signals.
        If source_urls not provided, uses URLs from the tenant's ICP/competitor list.
        """
        logger.info(f"Starting recon scan for tenant {tenant_id}, ICP {icp_id}")

        if not source_urls:
            # In real implementation, fetch from vault/repository
            source_urls = []

        all_signals = []
        for url in source_urls:
            try:
                # 1. Get previous content for change detection
                previous_content = None  # Fetch from cache/repository

                # 2. Extract signals
                signals = await self.extraction_service.extract_signals_from_source(
                    url, previous_content, tenant_id
                )
                all_signals.extend(signals)
            except Exception as e:
                logger.error(f"Failed to scan {url}: {str(e)}")

        # 3. Process and cluster signals
        if all_signals:
            processed_signals, clusters = await self.processing_service.process_signals(
                all_signals, tenant_id
            )
            await self.repository.save_clusters(clusters)
            await self.repository.save_signals(processed_signals)
            return [s.model_dump() for s in processed_signals]

        return []

    async def generate_dossier(
        self, tenant_id: str, campaign_id: str, signal_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generates a deep competitor dossier for a specific campaign.
        Uses signals to build hypotheses and recommended tactical moves.
        """
        logger.info(
            f"Generating dossier for tenant {tenant_id}, campaign {campaign_id}"
        )

        # 1. Fetch relevant signals
        if not signal_ids:
            signals = await self.repository.fetch_signals(tenant_id, window_days=90)
        else:
            signals = await self.repository.fetch_signals(
                tenant_id, signal_ids=signal_ids
            )

        # 2. Synthesize intelligence
        dossier = await self.processing_service.synthesize_dossier(
            signals, tenant_id, campaign_id
        )

        # 3. Save dossier
        await self.repository.save_dossier(dossier)

        return dossier.model_dump()

    async def get_signal_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """Returns signal volume and quality metrics for the dashboard."""
        signals = await self.repository.fetch_signals(tenant_id, window_days=30)
        return self.processing_service.calculate_signal_metrics(signals)
