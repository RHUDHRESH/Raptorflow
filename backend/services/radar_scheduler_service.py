"""
Radar Scheduler Service - Automated scanning and monitoring
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from core.crawl_cache import content_hash
from models.radar_models import RadarSource, ScanFrequency, ScanJob
from services.radar_cache import RadarCache
from services.radar_repository import RadarRepository
from services.signal_extraction_service import SignalExtractionService
from services.signal_processing_service import SignalProcessingService

logger = logging.getLogger("raptorflow.radar_scheduler")


class RadarSchedulerService:
    """
    Service for scheduling and managing automated Radar scans.
    Handles recurring scans, source health monitoring, and job management.
    """

    def __init__(self):
        self.extraction_service = SignalExtractionService()
        self.processing_service = SignalProcessingService()
        self.repository = RadarRepository()
        self.cache = RadarCache()
        self.active_schedulers: Dict[str, asyncio.Task] = {}
        self.content_cache: Dict[str, str] = {}  # Fallback in-memory cache

        # Frequency intervals in seconds
        self.frequency_intervals = {
            ScanFrequency.HOURLY: 3600,
            ScanFrequency.DAILY: 86400,
            ScanFrequency.WEEKLY: 604800,
        }

    async def start_scheduler(
        self, tenant_id: str, sources: Optional[List[RadarSource]] = None
    ):
        """Start scheduler for a tenant with their sources."""
        if tenant_id in self.active_schedulers:
            await self.stop_scheduler(tenant_id)

        if sources is None:
            sources = await self.repository.fetch_sources(tenant_id)

        # Group sources by frequency
        by_frequency = {}
        for source in sources:
            if source.scan_frequency not in by_frequency:
                by_frequency[source.scan_frequency] = []
            by_frequency[source.scan_frequency].append(source)

        # Create scheduler task
        task = asyncio.create_task(self._scheduler_loop(tenant_id, by_frequency))
        self.active_schedulers[tenant_id] = task

        logger.info(
            f"Started Radar scheduler for tenant {tenant_id} with {len(sources)} sources"
        )
        await self.cache.set_scheduler_status(
            tenant_id,
            {
                "tenant_id": tenant_id,
                "is_active": True,
                "source_count": len(sources),
                "started_at": datetime.utcnow().isoformat(),
            },
        )

    async def stop_scheduler(self, tenant_id: str):
        """Stop scheduler for a tenant."""
        if tenant_id in self.active_schedulers:
            task = self.active_schedulers[tenant_id]
            task.cancel()
            del self.active_schedulers[tenant_id]
            logger.info(f"Stopped Radar scheduler for tenant {tenant_id}")
        await self.cache.set_scheduler_status(
            tenant_id,
            {
                "tenant_id": tenant_id,
                "is_active": False,
                "stopped_at": datetime.utcnow().isoformat(),
            },
        )

    async def schedule_manual_scan(
        self, tenant_id: str, source_ids: List[str], scan_type: str = "recon"
    ) -> ScanJob:
        """Schedule a manual scan job."""
        job = ScanJob(
            tenant_id=tenant_id,
            source_ids=source_ids,
            scan_type=scan_type,
            status="pending",
        )
        await self.repository.create_scan_job(job)

        # Execute scan asynchronously
        asyncio.create_task(self._execute_scan_job(job))

        return job

    async def _scheduler_loop(
        self, tenant_id: str, by_frequency: Dict[str, List[RadarSource]]
    ):
        """Main scheduler loop for automated scanning."""
        next_scans = {}

        while True:
            try:
                current_time = datetime.utcnow()

                for frequency, sources in by_frequency.items():
                    # Check if it's time to scan this frequency
                    if frequency not in next_scans:
                        next_scans[frequency] = current_time

                    if current_time >= next_scans[frequency]:
                        # Schedule scan for this frequency
                        source_ids = [
                            source.id for source in sources if source.is_active
                        ]
                        if source_ids:
                            await self.schedule_manual_scan(
                                tenant_id, source_ids, f"scheduled_{frequency}"
                            )

                        # Set next scan time
                        interval = self.frequency_intervals.get(frequency, 86400)
                        next_scans[frequency] = current_time + timedelta(
                            seconds=interval
                        )

                # Sleep for 1 minute before next check
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                logger.info(f"Scheduler loop cancelled for tenant {tenant_id}")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop for tenant {tenant_id}: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _execute_scan_job(self, job: ScanJob):
        """Execute a scan job."""
        try:
            job.status = "running"
            job.started_at = datetime.utcnow()
            await self.repository.update_scan_job(job)

            # In real implementation, fetch sources from database
            sources = await self.repository.fetch_sources(job.tenant_id, job.source_ids)

            all_signals = []
            errors = []

            for source in sources:
                try:
                    # Get previous content for change detection
                    previous_content = await self.cache.get_source_content(
                        job.tenant_id, source.id
                    )

                    # Extract signals
                    signals = await self.extraction_service.extract_signals_from_source(
                        source.url, previous_content, job.tenant_id
                    )

                    # Cache content for next scan
                    current_content = self.extraction_service.get_last_content(
                        source.url
                    )
                    if current_content:
                        await self.cache.set_source_content(
                            job.tenant_id, source.id, current_content
                        )
                        self.content_cache[source.url] = content_hash(current_content)

                    for signal in signals:
                        if not signal.source_competitor:
                            signal.source_competitor = source.name
                        if not signal.source_url:
                            signal.source_url = source.url
                        signal.metadata["source_id"] = source.id
                        signal.metadata["scan_job_id"] = job.id

                    all_signals.extend(signals)

                    # Update source health
                    source.health_score = min(100, source.health_score + 5)
                    source.last_checked = datetime.utcnow()
                    source.last_success = datetime.utcnow()
                    await self.repository.update_source_health(source)

                except Exception as e:
                    error_msg = f"Failed to scan {source.url}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

                    # Decrease source health
                    source.health_score = max(0, source.health_score - 10)
                    source.last_checked = datetime.utcnow()
                    await self.repository.update_source_health(source)

            # Process signals
            if all_signals:
                processed_signals, clusters = (
                    await self.processing_service.process_signals(
                        all_signals, job.tenant_id
                    )
                )
                job.signals_found = len(processed_signals)
                await self.repository.save_clusters(clusters)
                await self.repository.save_signals(processed_signals)
                logger.info(
                    f"Processed {len(processed_signals)} signals into {len(clusters)} clusters"
                )

            # Update job status
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.errors = errors
            await self.repository.update_scan_job(job)

            logger.info(
                f"Scan job {job.id} completed: {job.signals_found} signals found"
            )

        except Exception as e:
            job.status = "failed"
            job.completed_at = datetime.utcnow()
            job.errors = [str(e)]
            await self.repository.update_scan_job(job)
            logger.error(f"Scan job {job.id} failed: {e}")

    async def get_source_health(
        self,
        sources: Optional[List[RadarSource]] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get health summary for all sources."""
        if sources is None and tenant_id:
            sources = await self.repository.fetch_sources(tenant_id)
        if not sources:
            return {"total_sources": 0, "healthy_sources": 0, "avg_health": 0}

        healthy_sources = len([s for s in sources if s.health_score >= 80])
        avg_health = sum(s.health_score for s in sources) / len(sources)

        health_distribution = {
            "excellent": len([s for s in sources if s.health_score >= 90]),
            "good": len([s for s in sources if 80 <= s.health_score < 90]),
            "fair": len([s for s in sources if 60 <= s.health_score < 80]),
            "poor": len([s for s in sources if s.health_score < 60]),
        }

        return {
            "total_sources": len(sources),
            "healthy_sources": healthy_sources,
            "avg_health": round(avg_health, 1),
            "health_distribution": health_distribution,
            "last_scan": max(
                (s.last_checked for s in sources if s.last_checked), default=None
            ),
        }

    async def cleanup_old_cache(self, days_old: int = 30):
        """Clean up old content cache entries."""
        # In real implementation, would use timestamps
        # For now, just clear cache if it's getting large
        if len(self.content_cache) > 10000:
            self.content_cache.clear()
            logger.info("Cleared Radar content cache due to size limit")

    async def get_scheduler_status(self, tenant_id: str) -> Dict[str, Any]:
        """Get scheduler status for a tenant."""
        is_active = tenant_id in self.active_schedulers
        status = {
            "tenant_id": tenant_id,
            "is_active": is_active,
            "cache_size": len(self.content_cache),
            "active_tasks": len(self.active_schedulers),
        }
        cached_status = await self.cache.get_scheduler_status(tenant_id)
        if cached_status:
            status["last_reported"] = cached_status
        return status
