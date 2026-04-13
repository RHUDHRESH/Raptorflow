//! DragonflyDB (Redis-compatible) cache service for RaptorFlow.
//!
//! Provides a typed, namespaced cache backed by DragonflyDB. All values are
//! JSON-serialized. Keys are prefixed with `raptorflow:{namespace}:{key}`.
//!
//! ## Cache layers
//!
//! - [`CacheService`] — base cache with get/set/delete + TTL support
//! - [`FoundationCache`] — foundation content + version caching (30-min TTL)
//! - [`SessionCache`] — session state caching (24-hour TTL)
//! - [`StreamCache`] — stream/office event cursor tracking (7-day TTL)
//!
//! ## Error handling
//!
//! [`CacheError`] is a typed enum covering connection, serialization, and Redis command errors.
//! It implements `std::error::Error` and is convertible to an Axum response via `IntoResponse`.

use redis::aio::ConnectionManager;
use redis::{AsyncCommands, Client};
use serde::{de::DeserializeOwned, Serialize};
use std::sync::Arc;

const DEFAULT_TTL: u64 = 3600;
const NAMESPACE_PREFIX: &str = "raptorflow";

#[derive(Clone)]
pub struct CacheService {
    conn: Arc<ConnectionManager>,
    namespace: String,
}

impl CacheService {
    pub async fn new(dragonfly_url: &str) -> Result<Self, CacheError> {
        let client = Client::open(dragonfly_url)
            .map_err(|e| CacheError::Connection(e.to_string()))?;
        
        let conn = ConnectionManager::new(client)
            .await
            .map_err(|e| CacheError::Connection(e.to_string()))?;

        Ok(Self {
            conn: Arc::new(conn),
            namespace: NAMESPACE_PREFIX.to_string(),
        })
    }

    pub async fn with_namespace(dragonfly_url: &str, namespace: &str) -> Result<Self, CacheError> {
        let client = Client::open(dragonfly_url)
            .map_err(|e| CacheError::Connection(e.to_string()))?;
        
        let conn = ConnectionManager::new(client)
            .await
            .map_err(|e| CacheError::Connection(e.to_string()))?;

        Ok(Self {
            conn: Arc::new(conn),
            namespace: format!("{}:{}", NAMESPACE_PREFIX, namespace),
        })
    }

    pub async fn from_settings(settings: &raptorflow_config::Settings) -> Result<Self, CacheError> {
        Self::new(&settings.dragonfly_url).await
    }

    fn make_key(&self, key: &str) -> String {
        format!("{}:{}", self.namespace, key)
    }

    pub async fn get<T: DeserializeOwned>(&self, key: &str) -> Result<Option<T>, CacheError> {
        let mut conn = (*self.conn).clone();
        let full_key = self.make_key(key);
        
        let result: Option<String> = conn.get(&full_key).await
            .map_err(|e| CacheError::Get(e.to_string()))?;
        
        match result {
            Some(json) => {
                let value: T = serde_json::from_str(&json)
                    .map_err(|e| CacheError::Deserialize(e.to_string()))?;
                Ok(Some(value))
            }
            None => Ok(None)
        }
    }

    pub async fn set<T: Serialize + ?Sized>(&self, key: &str, value: &T) -> Result<(), CacheError> {
        self.set_with_ttl(key, value, DEFAULT_TTL).await
    }

    pub async fn set_with_ttl<T: Serialize + ?Sized>(
        &self, 
        key: &str, 
        value: &T, 
        ttl_seconds: u64
    ) -> Result<(), CacheError> {
        let mut conn = (*self.conn).clone();
        let full_key = self.make_key(key);
        
        let json = serde_json::to_string(value)
            .map_err(|e| CacheError::Serialize(e.to_string()))?;
        
        let _: () = redis::cmd("SETEX")
            .arg(&full_key)
            .arg(ttl_seconds)
            .arg(&json)
            .query_async(&mut conn)
            .await
            .map_err(|e| CacheError::Set(e.to_string()))?;
        
        Ok(())
    }

    pub async fn delete(&self, key: &str) -> Result<bool, CacheError> {
        let mut conn = (*self.conn).clone();
        let full_key = self.make_key(key);
        
        let deleted: i32 = conn.del(&full_key).await
            .map_err(|e| CacheError::Delete(e.to_string()))?;
        
        Ok(deleted > 0)
    }

    pub async fn exists(&self, key: &str) -> Result<bool, CacheError> {
        let mut conn = (*self.conn).clone();
        let full_key = self.make_key(key);
        
        let exists: bool = conn.exists(&full_key).await
            .map_err(|e| CacheError::Exists(e.to_string()))?;
        
        Ok(exists)
    }

    pub async fn expire(&self, key: &str, ttl_seconds: u64) -> Result<bool, CacheError> {
        let mut conn = (*self.conn).clone();
        let full_key = self.make_key(key);
        
        let result: bool = conn.expire(&full_key, ttl_seconds as i64).await
            .map_err(|e| CacheError::Expire(e.to_string()))?;
        
        Ok(result)
    }

    pub async fn increment(&self, key: &str) -> Result<i64, CacheError> {
        let mut conn = (*self.conn).clone();
        let full_key = self.make_key(key);
        
        let value: i64 = conn.incr(&full_key, 1i64).await
            .map_err(|e| CacheError::Increment(e.to_string()))?;
        
        Ok(value)
    }

    pub async fn decrement(&self, key: &str) -> Result<i64, CacheError> {
        let mut conn = (*self.conn).clone();
        let full_key = self.make_key(key);
        
        let value: i64 = conn.decr(&full_key, 1i64).await
            .map_err(|e| CacheError::Decrement(e.to_string()))?;
        
        Ok(value)
    }

    pub async fn get_or_set<T: Serialize + DeserializeOwned + ?Sized>(
        &self,
        key: &str,
        factory: impl FnOnce() -> Result<T, CacheError>,
    ) -> Result<T, CacheError> {
        if let Some(cached) = self.get::<T>(key).await? {
            return Ok(cached);
        }
        
        let value = factory()?;
        self.set(key, &value).await?;
        Ok(value)
    }

    async fn scan_keys(&self, pattern: &str) -> Result<Vec<String>, CacheError> {
        let mut conn = (*self.conn).clone();
        let mut keys = Vec::new();
        let mut cursor: u64 = 0;

        loop {
            let result: (u64, Vec<String>) = redis::cmd("SCAN")
                .arg(cursor)
                .arg("MATCH")
                .arg(pattern)
                .arg("COUNT")
                .arg(100)
                .query_async(&mut conn)
                .await
                .map_err(|e| CacheError::Keys(e.to_string()))?;

            cursor = result.0;
            keys.extend(result.1);

            if cursor == 0 {
                break;
            }
        }

        Ok(keys)
    }

    pub async fn invalidate_prefix(&self, prefix: &str) -> Result<i32, CacheError> {
        let pattern = format!("{}:{}*", self.namespace, prefix);
        
        let keys = self.scan_keys(&pattern).await?;
        
        if keys.is_empty() {
            return Ok(0);
        }
        
        let mut conn = (*self.conn).clone();
        let deleted: i32 = conn.del(&keys).await
            .map_err(|e| CacheError::Delete(e.to_string()))?;
        
        Ok(deleted)
    }

    pub async fn flush_namespace(&self) -> Result<i32, CacheError> {
        let pattern = format!("{}:*", self.namespace);
        
        let keys = self.scan_keys(&pattern).await?;
        
        if keys.is_empty() {
            return Ok(0);
        }
        
        let mut conn = (*self.conn).clone();
        let deleted: i32 = conn.del(&keys).await
            .map_err(|e| CacheError::Delete(e.to_string()))?;
        
        Ok(deleted)
    }
}

#[derive(Debug, thiserror::Error)]
pub enum CacheError {
    #[error("Connection error: {0}")]
    Connection(String),

    #[error("Get error: {0}")]
    Get(String),

    #[error("Set error: {0}")]
    Set(String),

    #[error("Delete error: {0}")]
    Delete(String),

    #[error("Exists error: {0}")]
    Exists(String),

    #[error("Expire error: {0}")]
    Expire(String),

    #[error("Increment error: {0}")]
    Increment(String),

    #[error("Decrement error: {0}")]
    Decrement(String),

    #[error("Serialize error: {0}")]
    Serialize(String),

    #[error("Deserialize error: {0}")]
    Deserialize(String),

    #[error("Keys error: {0}")]
    Keys(String),
}

pub struct FoundationCache {
    cache: CacheService,
}

impl FoundationCache {
    pub fn new(cache: CacheService) -> Self {
        Self { cache }
    }

    pub async fn get_cached_content(&self, org_id: &str) -> Result<Option<String>, CacheError> {
        let key = format!("foundation:{}:content", org_id);
        self.cache.get(&key).await
    }

    pub async fn set_cached_content(&self, org_id: &str, content: &str) -> Result<(), CacheError> {
        let key = format!("foundation:{}:content", org_id);
        self.cache.set_with_ttl(&key, &content, 1800).await
    }

    pub async fn invalidate(&self, org_id: &str) -> Result<bool, CacheError> {
        let key = format!("foundation:{}:content", org_id);
        self.cache.delete(&key).await
    }

    pub async fn get_version(&self, org_id: &str) -> Result<Option<i32>, CacheError> {
        let key = format!("foundation:{}:version", org_id);
        self.cache.get(&key).await
    }

    pub async fn set_version(&self, org_id: &str, version: i32) -> Result<(), CacheError> {
        let key = format!("foundation:{}:version", org_id);
        self.cache.set_with_ttl(&key, &version, 1800).await
    }
}

pub struct SessionCache {
    cache: CacheService,
}

impl SessionCache {
    pub fn new(cache: CacheService) -> Self {
        Self { cache }
    }

    pub async fn get_session<T: DeserializeOwned>(&self, session_id: &str) -> Result<Option<T>, CacheError> {
        let key = format!("session:{}", session_id);
        self.cache.get(&key).await
    }

    pub async fn set_session<T: Serialize + ?Sized>(&self, session_id: &str, session: &T) -> Result<(), CacheError> {
        let key = format!("session:{}", session_id);
        self.cache.set_with_ttl(&key, session, 86400).await
    }

    pub async fn delete_session(&self, session_id: &str) -> Result<bool, CacheError> {
        let key = format!("session:{}", session_id);
        self.cache.delete(&key).await
    }

    pub async fn refresh_session(&self, session_id: &str) -> Result<bool, CacheError> {
        let key = format!("session:{}", session_id);
        self.cache.expire(&key, 86400).await
    }
}

pub struct StreamCache {
    cache: CacheService,
}

impl StreamCache {
    pub fn new(cache: CacheService) -> Self {
        Self { cache }
    }

    pub async fn get_last_message_id(&self, stream_id: &str) -> Result<Option<String>, CacheError> {
        let key = format!("stream:{}:last_id", stream_id);
        self.cache.get(&key).await
    }

    pub async fn set_last_message_id(&self, stream_id: &str, message_id: &str) -> Result<(), CacheError> {
        let key = format!("stream:{}:last_id", stream_id);
        self.cache.set_with_ttl(&key, &message_id, 604800).await
    }

    pub async fn get_pending_messages(&self, stream_id: &str) -> Result<Option<i32>, CacheError> {
        let key = format!("stream:{}:pending", stream_id);
        self.cache.get(&key).await
    }

    pub async fn set_pending_messages(&self, stream_id: &str, count: i32) -> Result<(), CacheError> {
        let key = format!("stream:{}:pending", stream_id);
        self.cache.set_with_ttl(&key, &count, 3600).await
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_key_formation() {
        let service = CacheService::with_namespace("redis://localhost", "test").await.unwrap();
        assert_eq!(service.make_key("foo"), "raptorflow:test:foo");
    }
}
