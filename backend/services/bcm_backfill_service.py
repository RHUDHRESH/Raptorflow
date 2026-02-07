"""
BCM Vector Backfill Service

Backfills vector memory from existing BCM records in Supabase.
Supports dry-run mode for counting records without writes.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from core.supabase_mgr import get_supabase_admin
from services.bcm_vectorize_service import BCMVectorizeService

from backend.redis.client import get_redis

logger = logging.getLogger(__name__)


class BCMVectorBackfillService:
    def __init__(self):
        self.supabase = get_supabase_admin()
        self.vectorizer = BCMVectorizeService()
        self.redis = None

        try:
            self.redis = get_redis()
        except Exception as e:
            logger.warning("Redis unavailable for BCM backfill lock/status: %s", e)

        self.lock_key = "bcm:vector_backfill:lock"
        self.status_key = "bcm:vector_backfill:status"

    async def backfill(
        self,
        table: str = "both",
        batch_size: int = 50,
        max_records: int = 0,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        total = 0

        if table in ("bcm_manifests", "both"):
            total += await self._backfill_table(
                "bcm_manifests", batch_size, max_records, dry_run
            )

        if table in ("business_context_manifests", "both"):
            total += await self._backfill_table(
                "business_context_manifests", batch_size, max_records, dry_run
            )

        return {
            "success": True,
            "table": table,
            "dry_run": dry_run,
            "vectorized_records": total,
        }

    async def backfill_with_lock(
        self,
        run_id: str,
        table: str = "both",
        batch_size: int = 50,
        max_records: int = 0,
        dry_run: bool = False,
        lock_ttl_seconds: int = 3600,
    ) -> Dict[str, Any]:
        if not self.redis:
            return {
                "success": False,
                "error": "Redis not available for lock/status",
            }

        acquired = await self._acquire_lock(run_id, lock_ttl_seconds)
        if not acquired:
            return {
                "success": False,
                "error": "Backfill already in progress",
            }

        await self._set_status(
            {
                "run_id": run_id,
                "status": "running",
                "table": table,
                "dry_run": dry_run,
                "started_at": self._now_iso(),
            }
        )

        try:
            started_at = await self._get_started_at()
            result = await self.backfill(
                table=table,
                batch_size=batch_size,
                max_records=max_records,
                dry_run=dry_run,
            )
            await self._set_status(
                {
                    "run_id": run_id,
                    "status": "completed",
                    "table": table,
                    "dry_run": dry_run,
                    "started_at": started_at,
                    "completed_at": self._now_iso(),
                    "vectorized_records": result.get("vectorized_records", 0),
                }
            )
            return result
        except Exception as e:
            started_at = await self._get_started_at()
            await self._set_status(
                {
                    "run_id": run_id,
                    "status": "failed",
                    "table": table,
                    "dry_run": dry_run,
                    "started_at": started_at,
                    "completed_at": self._now_iso(),
                    "error": str(e),
                }
            )
            raise
        finally:
            await self._release_lock(run_id)

    async def get_status(self) -> Dict[str, Any]:
        if not self.redis:
            return {"status": "unknown", "error": "Redis not available"}
        status = await self.redis.get_json(self.status_key)
        return status or {"status": "unknown"}

    async def is_locked(self) -> bool:
        if not self.redis:
            return False
        try:
            return (await self.redis.exists(self.lock_key)) == 1
        except Exception:
            return False

    async def set_status(self, status: Dict[str, Any]) -> None:
        await self._set_status(status)

    async def _backfill_table(
        self,
        table_name: str,
        batch_size: int,
        max_records: int,
        dry_run: bool,
    ) -> int:
        offset = 0
        processed = 0

        while True:
            result = (
                self.supabase.table(table_name)
                .select("*")
                .order("created_at", desc=True)
                .range(offset, offset + batch_size - 1)
                .execute()
            )

            records = result.data or []
            if not records:
                break

            for record in records:
                workspace_id = record.get("workspace_id")
                if not workspace_id:
                    continue

                if table_name == "bcm_manifests":
                    manifest = self._manifest_from_bcm_manifests(record)
                else:
                    manifest = self._manifest_from_business_context_manifests(record)

                if not manifest:
                    continue

                processed += 1
                if dry_run:
                    if max_records and processed >= max_records:
                        return processed
                    continue

                version = self._get_version(record)

                await self.vectorizer.vectorize_manifest(
                    workspace_id=workspace_id,
                    manifest=manifest,
                    version=version,
                    source=f"backfill:{table_name}",
                )

                if max_records and processed >= max_records:
                    return processed

            offset += batch_size

        return processed

    def _manifest_from_bcm_manifests(
        self, record: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        manifest = record.get("manifest_json")
        if isinstance(manifest, dict):
            return manifest
        return None

    def _manifest_from_business_context_manifests(
        self, record: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        if isinstance(record.get("content"), dict):
            return record["content"]
        if isinstance(record.get("manifest_json"), dict):
            return record["manifest_json"]

        if any(
            k in record
            for k in (
                "company_info",
                "icps",
                "competitors",
                "brand_data",
                "market_data",
                "messaging_data",
                "channels_data",
                "goals_data",
            )
        ):
            return {
                "version": record.get("version_string"),
                "generated_at": record.get("generated_at"),
                "workspace_id": record.get("workspace_id"),
                "user_id": record.get("user_id"),
                "company": record.get("company_info"),
                "icps": record.get("icps"),
                "competitors": record.get("competitors"),
                "brand": (record.get("brand_data") or {}).get("brand"),
                "values": (record.get("brand_data") or {}).get("values"),
                "personality": (record.get("brand_data") or {}).get("personality"),
                "tone": (record.get("brand_data") or {}).get("tone"),
                "positioning": (record.get("brand_data") or {}).get("positioning"),
                "market": (record.get("market_data") or {}).get("market"),
                "verticals": (record.get("market_data") or {}).get("verticals"),
                "geography": (record.get("market_data") or {}).get("geography"),
                "messaging": (record.get("messaging_data") or {}).get("messaging"),
                "value_prop": (record.get("messaging_data") or {}).get("value_prop"),
                "taglines": (record.get("messaging_data") or {}).get("taglines"),
                "key_messages": (record.get("messaging_data") or {}).get(
                    "key_messages"
                ),
                "soundbites": (record.get("messaging_data") or {}).get("soundbites"),
                "channels": (record.get("channels_data") or {}).get("channels"),
                "primary_channels": (record.get("channels_data") or {}).get(
                    "primary_channels"
                ),
                "secondary_channels": (record.get("channels_data") or {}).get(
                    "secondary_channels"
                ),
                "strategy_summary": (record.get("channels_data") or {}).get(
                    "strategy_summary"
                ),
                "goals": (record.get("goals_data") or {}).get("goals"),
                "short_term_goals": (record.get("goals_data") or {}).get(
                    "short_term_goals"
                ),
                "long_term_goals": (record.get("goals_data") or {}).get(
                    "long_term_goals"
                ),
                "kpis": (record.get("goals_data") or {}).get("kpis"),
                "completion_percentage": record.get("completion_percentage"),
                "checksum": record.get("checksum"),
                "raw_step_ids": record.get("raw_step_ids"),
            }

        return None

    def _get_version(self, record: Dict[str, Any]) -> Optional[str]:
        for key in ("version_string", "version", "version_major"):
            value = record.get(key)
            if value:
                return str(value)
        # Fallback: stable hash-based version marker
        return hashlib.md5(
            json.dumps(record, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()[:8]

    async def _acquire_lock(self, run_id: str, ttl: int) -> bool:
        try:
            return (
                await self.redis.async_client.set(
                    self.lock_key, run_id, nx=True, ex=ttl
                )
                is True
            )
        except Exception:
            return False

    async def _release_lock(self, run_id: str) -> None:
        try:
            current = await self.redis.async_client.get(self.lock_key)
            if current and current == run_id:
                await self.redis.delete(self.lock_key)
        except Exception:
            pass

    async def _set_status(self, status: Dict[str, Any]) -> None:
        try:
            await self.redis.set_json(self.status_key, status, ex=86400)
        except Exception:
            pass

    async def _get_started_at(self) -> str:
        status = await self.redis.get_json(self.status_key)
        if status and status.get("started_at"):
            return status["started_at"]
        return self._now_iso()

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()
