import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from core.cache import get_cache_client
from core.config import get_settings
from core.vault import get_vault


DEFAULT_MAX_AGE_SECONDS = 900
DEFAULT_ENTRY_TTL_SECONDS = 86400


@dataclass(frozen=True)
class CacheLookup:
    entry: Optional[Dict[str, Any]]
    is_fresh: bool


def _now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = (parsed.scheme or "http").lower()
    hostname = (parsed.hostname or parsed.netloc or "").lower()
    port = parsed.port
    if port and not (
        (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    ):
        hostname = f"{hostname}:{port}"
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)))
    return urlunparse((scheme, hostname, path, "", query, ""))


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _entry_key(normalized_url: str, hash_value: str) -> str:
    return f"crawl:entry:{normalized_url}:{hash_value}"


def _index_key(normalized_url: str) -> str:
    return f"crawl:index:{normalized_url}"


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _is_fresh(entry: Dict[str, Any], max_age_seconds: int) -> bool:
    last_fetched = _parse_timestamp(entry.get("last_fetched"))
    if not last_fetched:
        return False
    return _now() - last_fetched <= timedelta(seconds=max_age_seconds)


class CrawlCache:
    def __init__(self):
        self._redis = get_cache_client()
        self._supabase = None
        settings = get_settings()
        if (
            not self._redis
            and settings.SUPABASE_URL
            and "placeholder" not in settings.SUPABASE_URL
        ):
            self._supabase = get_vault().get_session()

    def get(
        self, url: str, max_age_seconds: int = DEFAULT_MAX_AGE_SECONDS
    ) -> CacheLookup:
        normalized_url = normalize_url(url)
        entry = None

        if self._redis:
            hash_value = self._redis.get(_index_key(normalized_url))
            if hash_value:
                raw = self._redis.get(_entry_key(normalized_url, hash_value))
                if raw:
                    entry = json.loads(raw)
        elif self._supabase:
            result = (
                self._supabase.table("crawl_cache")
                .select("payload")
                .eq("normalized_url", normalized_url)
                .order("last_fetched", desc=True)
                .limit(1)
                .execute()
            )
            if result.data:
                entry = result.data[0].get("payload")

        return CacheLookup(entry=entry, is_fresh=_is_fresh(entry, max_age_seconds) if entry else False)

    def set(
        self,
        url: str,
        content: str,
        etag: Optional[str] = None,
        last_modified: Optional[str] = None,
        expiry_seconds: int = DEFAULT_ENTRY_TTL_SECONDS,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized_url = normalize_url(url)
        hash_value = content_hash(content)
        entry = {
            "url": url,
            "normalized_url": normalized_url,
            "content": content,
            "content_hash": hash_value,
            "last_fetched": _now().isoformat(),
            "etag": etag,
            "last_modified": last_modified,
        }
        if metadata:
            entry.update(metadata)
        self._store_entry(entry, expiry_seconds)
        if self._redis:
            self._redis.set(_index_key(normalized_url), hash_value, ex=expiry_seconds)
        elif self._supabase:
            self._supabase.table("crawl_cache").upsert(
                {
                    "normalized_url": normalized_url,
                    "content_hash": hash_value,
                    "last_fetched": entry["last_fetched"],
                    "payload": entry,
                },
                on_conflict="normalized_url,content_hash",
            ).execute()
        return entry

    def touch(
        self,
        entry: Dict[str, Any],
        expiry_seconds: int = DEFAULT_ENTRY_TTL_SECONDS,
    ) -> Dict[str, Any]:
        updated = dict(entry)
        updated["last_fetched"] = _now().isoformat()
        self._store_entry(updated, expiry_seconds)
        if self._supabase:
            self._supabase.table("crawl_cache").update(
                {"last_fetched": updated["last_fetched"], "payload": updated}
            ).eq("normalized_url", updated["normalized_url"]).eq(
                "content_hash", updated["content_hash"]
            ).execute()
        return updated

    def _store_entry(self, entry: Dict[str, Any], expiry_seconds: int) -> None:
        if not self._redis:
            return
        payload = json.dumps(entry)
        self._redis.set(
            _entry_key(entry["normalized_url"], entry["content_hash"]),
            payload,
            ex=expiry_seconds,
        )

    @staticmethod
    def build_revalidation_headers(entry: Dict[str, Any]) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if entry.get("etag"):
            headers["If-None-Match"] = entry["etag"]
        if entry.get("last_modified"):
            headers["If-Modified-Since"] = entry["last_modified"]
        return headers
