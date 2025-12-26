import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from core.database_pool import get_db_session
from models.radar_models import Dossier, Evidence, RadarSource, ScanJob, Signal, SignalCluster
from utils.storage import upload_text_to_gcs

logger = logging.getLogger("raptorflow.radar_repository")


class RadarRepository:
    """Database access layer for Radar data."""

    def __init__(
        self,
        storage_bucket: Optional[str] = None,
        evidence_content_limit: int = 2000,
    ):
        self.storage_bucket = storage_bucket
        self.evidence_content_limit = evidence_content_limit

    async def fetch_sources(
        self, tenant_id: str, source_ids: Optional[List[str]] = None
    ) -> List[RadarSource]:
        query = """
            SELECT id, tenant_id, name, type, url, scan_frequency, health_score,
                   last_checked, last_success, is_active, config, created_at, updated_at
            FROM radar_sources
            WHERE tenant_id = :tenant_id
        """
        params: Dict[str, Any] = {"tenant_id": tenant_id}
        if source_ids:
            query += " AND id = ANY(:source_ids)"
            params["source_ids"] = source_ids

        async with await get_db_session() as session:
            result = await session.execute(text(query), params)
            rows = result.mappings().all()

        sources = []
        for row in rows:
            sources.append(
                RadarSource(
                    id=str(row["id"]),
                    tenant_id=str(row["tenant_id"]),
                    name=row["name"],
                    type=row["type"],
                    url=row["url"],
                    scan_frequency=row["scan_frequency"],
                    health_score=row["health_score"],
                    last_checked=row["last_checked"],
                    last_success=row["last_success"],
                    is_active=row["is_active"],
                    config=row["config"] or {},
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            )
        return sources

    async def create_source(self, source: RadarSource) -> RadarSource:
        query = """
            INSERT INTO radar_sources (
                id, tenant_id, name, type, url, scan_frequency, health_score,
                last_checked, last_success, is_active, config, created_at, updated_at
            )
            VALUES (
                :id, :tenant_id, :name, :type, :url, :scan_frequency, :health_score,
                :last_checked, :last_success, :is_active, CAST(:config AS JSONB),
                :created_at, :updated_at
            )
        """
        params = {
            "id": source.id,
            "tenant_id": source.tenant_id,
            "name": source.name,
            "type": source.type,
            "url": source.url,
            "scan_frequency": source.scan_frequency,
            "health_score": source.health_score,
            "last_checked": source.last_checked,
            "last_success": source.last_success,
            "is_active": source.is_active,
            "config": json.dumps(source.config or {}),
            "created_at": source.created_at,
            "updated_at": source.updated_at,
        }
        async with await get_db_session() as session:
            async with session.begin():
                await session.execute(text(query), params)
        return source

    async def delete_source(self, tenant_id: str, source_id: str) -> None:
        query = """
            DELETE FROM radar_sources
            WHERE tenant_id = :tenant_id AND id = :source_id
        """
        async with await get_db_session() as session:
            async with session.begin():
                await session.execute(
                    text(query), {"tenant_id": tenant_id, "source_id": source_id}
                )

    async def fetch_dossiers(
        self, tenant_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT id, tenant_id, campaign_id, title, summary, pinned_signals, hypotheses,
                   recommended_experiments, copy_snippets, market_narrative,
                   created_at, updated_at, is_published
            FROM radar_dossiers
            WHERE tenant_id = :tenant_id
            ORDER BY created_at DESC
            LIMIT :limit
        """
        async with await get_db_session() as session:
            result = await session.execute(
                text(query), {"tenant_id": tenant_id, "limit": limit}
            )
            rows = result.mappings().all()
        return [dict(row) for row in rows]

    async def fetch_dossier(self, tenant_id: str, dossier_id: str) -> Optional[dict]:
        query = """
            SELECT id, tenant_id, campaign_id, title, summary, pinned_signals, hypotheses,
                   recommended_experiments, copy_snippets, market_narrative,
                   created_at, updated_at, is_published
            FROM radar_dossiers
            WHERE tenant_id = :tenant_id AND id = :dossier_id
        """
        async with await get_db_session() as session:
            result = await session.execute(
                text(query), {"tenant_id": tenant_id, "dossier_id": dossier_id}
            )
            row = result.mappings().first()
        return dict(row) if row else None

    async def update_source_health(self, source: RadarSource) -> None:
        query = """
            UPDATE radar_sources
            SET health_score = :health_score,
                last_checked = :last_checked,
                last_success = :last_success,
                is_active = :is_active,
                config = CAST(:config AS JSONB)
            WHERE id = :id
        """
        params = {
            "id": source.id,
            "health_score": source.health_score,
            "last_checked": source.last_checked,
            "last_success": source.last_success,
            "is_active": source.is_active,
            "config": json.dumps(source.config or {}),
        }
        async with await get_db_session() as session:
            async with session.begin():
                await session.execute(text(query), params)

    async def create_scan_job(self, job: ScanJob) -> None:
        query = """
            INSERT INTO radar_scan_jobs (
                id, tenant_id, source_ids, scan_type, status, started_at,
                completed_at, signals_found, errors, config, created_at
            )
            VALUES (
                :id, :tenant_id, CAST(:source_ids AS JSONB), :scan_type, :status,
                :started_at, :completed_at, :signals_found, CAST(:errors AS JSONB),
                CAST(:config AS JSONB), :created_at
            )
        """
        params = self._scan_job_params(job)
        async with await get_db_session() as session:
            async with session.begin():
                await session.execute(text(query), params)

    async def update_scan_job(self, job: ScanJob) -> None:
        query = """
            UPDATE radar_scan_jobs
            SET status = :status,
                started_at = :started_at,
                completed_at = :completed_at,
                signals_found = :signals_found,
                errors = CAST(:errors AS JSONB),
                config = CAST(:config AS JSONB)
            WHERE id = :id
        """
        params = self._scan_job_params(job)
        async with await get_db_session() as session:
            async with session.begin():
                await session.execute(text(query), params)

    async def save_signals(self, signals: List[Signal]) -> None:
        if not signals:
            return
        signal_rows = []
        evidence_rows: List[Dict[str, Any]] = []

        for signal in signals:
            signal_rows.append(
                {
                    "id": signal.id,
                    "tenant_id": signal.tenant_id,
                    "category": signal.category.value
                    if hasattr(signal.category, "value")
                    else signal.category,
                    "title": signal.title,
                    "content": signal.content,
                    "strength": signal.strength.value
                    if hasattr(signal.strength, "value")
                    else signal.strength,
                    "freshness": signal.freshness.value
                    if hasattr(signal.freshness, "value")
                    else signal.freshness,
                    "action_suggestion": signal.action_suggestion,
                    "source_competitor": signal.source_competitor,
                    "source_url": signal.source_url,
                    "cluster_id": signal.cluster_id,
                    "created_at": signal.created_at,
                    "updated_at": signal.updated_at,
                    "metadata": json.dumps(signal.metadata or {}),
                }
            )

            for evidence in signal.evidence:
                content, metadata = await self._prepare_evidence_content(evidence)
                evidence_rows.append(
                    {
                        "id": evidence.id,
                        "signal_id": signal.id,
                        "type": evidence.type.value
                        if hasattr(evidence.type, "value")
                        else evidence.type,
                        "source": evidence.source,
                        "url": evidence.url,
                        "content": content,
                        "confidence": evidence.confidence,
                        "timestamp": evidence.timestamp,
                        "metadata": json.dumps(metadata),
                    }
                )

        insert_signals = """
            INSERT INTO radar_signals (
                id, tenant_id, category, title, content, strength, freshness,
                action_suggestion, source_competitor, source_url, cluster_id,
                created_at, updated_at, metadata
            )
            VALUES (
                :id, :tenant_id, :category, :title, :content, :strength, :freshness,
                :action_suggestion, :source_competitor, :source_url, :cluster_id,
                :created_at, :updated_at, CAST(:metadata AS JSONB)
            )
        """

        insert_evidence = """
            INSERT INTO radar_signal_evidence (
                id, signal_id, type, source, url, content, confidence, timestamp, metadata
            )
            VALUES (
                :id, :signal_id, :type, :source, :url, :content, :confidence, :timestamp,
                CAST(:metadata AS JSONB)
            )
        """

        async with await get_db_session() as session:
            async with session.begin():
                await session.execute(text(insert_signals), signal_rows)
                if evidence_rows:
                    await session.execute(text(insert_evidence), evidence_rows)

    async def save_clusters(self, clusters: List[SignalCluster]) -> None:
        if not clusters:
            return
        rows = []
        for cluster in clusters:
            rows.append(
                {
                    "id": cluster.id,
                    "tenant_id": cluster.tenant_id,
                    "category": cluster.category.value
                    if hasattr(cluster.category, "value")
                    else cluster.category,
                    "theme": cluster.theme,
                    "signal_count": cluster.signal_count,
                    "strength": cluster.strength.value
                    if hasattr(cluster.strength, "value")
                    else cluster.strength,
                    "created_at": cluster.created_at,
                    "updated_at": cluster.updated_at,
                }
            )

        query = """
            INSERT INTO radar_signal_clusters (
                id, tenant_id, category, theme, signal_count, strength, created_at, updated_at
            )
            VALUES (
                :id, :tenant_id, :category, :theme, :signal_count, :strength, :created_at, :updated_at
            )
        """
        async with await get_db_session() as session:
            async with session.begin():
                await session.execute(text(query), rows)

    async def save_dossier(self, dossier: Dossier) -> None:
        query = """
            INSERT INTO radar_dossiers (
                id, tenant_id, campaign_id, title, summary, pinned_signals, hypotheses,
                recommended_experiments, copy_snippets, market_narrative,
                created_at, updated_at, is_published
            )
            VALUES (
                :id, :tenant_id, :campaign_id, :title, CAST(:summary AS JSONB),
                CAST(:pinned_signals AS JSONB), CAST(:hypotheses AS JSONB),
                CAST(:recommended_experiments AS JSONB), CAST(:copy_snippets AS JSONB),
                CAST(:market_narrative AS JSONB), :created_at, :updated_at, :is_published
            )
        """
        params = {
            "id": dossier.id,
            "tenant_id": dossier.tenant_id,
            "campaign_id": dossier.campaign_id,
            "title": dossier.title,
            "summary": json.dumps(dossier.summary or []),
            "pinned_signals": json.dumps(dossier.pinned_signals or []),
            "hypotheses": json.dumps(dossier.hypotheses or []),
            "recommended_experiments": json.dumps(
                dossier.recommended_experiments or []
            ),
            "copy_snippets": json.dumps(dossier.copy_snippets or []),
            "market_narrative": json.dumps(dossier.market_narrative or {}),
            "created_at": dossier.created_at,
            "updated_at": dossier.updated_at,
            "is_published": dossier.is_published,
        }
        async with await get_db_session() as session:
            async with session.begin():
                await session.execute(text(query), params)

    async def fetch_signals(
        self,
        tenant_id: str,
        signal_ids: Optional[List[str]] = None,
        window_days: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Signal]:
        query = """
            SELECT id, tenant_id, category, title, content, strength, freshness,
                   action_suggestion, source_competitor, source_url, cluster_id,
                   created_at, updated_at, metadata
            FROM radar_signals
            WHERE tenant_id = :tenant_id
        """
        params: Dict[str, Any] = {"tenant_id": tenant_id}

        if signal_ids:
            query += " AND id = ANY(:signal_ids)"
            params["signal_ids"] = signal_ids

        if window_days:
            query += " AND created_at >= :cutoff"
            params["cutoff"] = datetime.utcnow() - timedelta(days=window_days)

        query += " ORDER BY created_at DESC"
        if limit:
            query += " LIMIT :limit"
            params["limit"] = limit

        async with await get_db_session() as session:
            result = await session.execute(text(query), params)
            rows = result.mappings().all()

        signals = []
        for row in rows:
            signals.append(
                Signal(
                    id=str(row["id"]),
                    tenant_id=str(row["tenant_id"]),
                    category=row["category"],
                    title=row["title"],
                    content=row["content"],
                    strength=row["strength"],
                    freshness=row["freshness"],
                    action_suggestion=row["action_suggestion"],
                    source_competitor=row["source_competitor"],
                    source_url=row["source_url"],
                    cluster_id=row["cluster_id"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    metadata=row["metadata"] or {},
                    evidence=[],
                )
            )
        return signals

    async def fetch_clusters(self, tenant_id: str) -> List[SignalCluster]:
        query = """
            SELECT id, tenant_id, category, theme, signal_count, strength,
                   created_at, updated_at
            FROM radar_signal_clusters
            WHERE tenant_id = :tenant_id
        """
        async with await get_db_session() as session:
            result = await session.execute(text(query), {"tenant_id": tenant_id})
            rows = result.mappings().all()

        clusters = []
        for row in rows:
            clusters.append(
                SignalCluster(
                    id=str(row["id"]),
                    tenant_id=str(row["tenant_id"]),
                    category=row["category"],
                    theme=row["theme"],
                    signal_count=row["signal_count"],
                    strength=row["strength"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            )
        return clusters

    def _scan_job_params(self, job: ScanJob) -> Dict[str, Any]:
        return {
            "id": job.id,
            "tenant_id": job.tenant_id,
            "source_ids": json.dumps(job.source_ids or []),
            "scan_type": job.scan_type,
            "status": job.status,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "signals_found": job.signals_found,
            "errors": json.dumps(job.errors or []),
            "config": json.dumps(job.config or {}),
            "created_at": job.created_at,
        }

    async def _prepare_evidence_content(self, evidence: Evidence) -> tuple[str, dict]:
        content = evidence.content or ""
        metadata = dict(evidence.metadata or {})
        if content and len(content) > self.evidence_content_limit:
            try:
                uri = await upload_text_to_gcs(
                    content, bucket_name=self.storage_bucket
                )
                metadata["content_uri"] = uri
                metadata["content_length"] = len(content)
                content = content[: self.evidence_content_limit]
            except Exception as exc:
                logger.warning("Evidence archival failed: %s", exc)
        return content, metadata
