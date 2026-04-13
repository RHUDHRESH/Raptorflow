use axum::{
    body::Body,
    http::{Request, StatusCode},
    response::Response,
};
use std::{
    collections::HashMap,
    sync::Arc,
    time::Instant,
};
use tokio::sync::RwLock;
use tower::{Layer, Service};
use std::future::Future;
use std::pin::Pin;

#[derive(Clone)]
pub struct RateLimitConfig {
    pub requests_per_minute: u32,
    pub burst_size: u32,
}

impl Default for RateLimitConfig {
    fn default() -> Self {
        Self {
            requests_per_minute: 60,
            burst_size: 10,
        }
    }
}

impl RateLimitConfig {
    pub fn new(requests_per_minute: u32) -> Self {
        Self {
            requests_per_minute,
            burst_size: requests_per_minute / 6,
        }
    }

    pub fn per_minute(requests: u32) -> Self {
        Self::new(requests)
    }

    pub fn strict() -> Self {
        Self {
            requests_per_minute: 30,
            burst_size: 5,
        }
    }

    pub fn relaxed() -> Self {
        Self {
            requests_per_minute: 300,
            burst_size: 50,
        }
    }
}

#[derive(Clone)]
pub struct RateLimitState {
    config: RateLimitConfig,
    tokens: Arc<RwLock<HashMap<String, TokenBucket>>>,
}

#[derive(Clone)]
struct TokenBucket {
    tokens: f32,
    last_update: Instant,
}

impl TokenBucket {
    fn new(capacity: f32) -> Self {
        Self {
            tokens: capacity,
            last_update: Instant::now(),
        }
    }

    fn try_consume(&mut self, cost: f32, config: &RateLimitConfig) -> bool {
        let now = Instant::now();
        let elapsed = now.duration_since(self.last_update).as_secs_f32();
        self.last_update = now;

        let refill_rate = config.requests_per_minute as f32 / 60.0;
        self.tokens = (self.tokens + elapsed * refill_rate).min(config.burst_size as f32);

        if self.tokens >= cost {
            self.tokens -= cost;
            true
        } else {
            false
        }
    }
}

impl RateLimitState {
    pub fn new(config: RateLimitConfig) -> Self {
        Self {
            config,
            tokens: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub async fn check_rate_limit(&self, key: &str) -> Result<(), RateLimitError> {
        let mut buckets = self.tokens.write().await;
        
        let bucket = buckets
            .entry(key.to_string())
            .or_insert_with(|| TokenBucket::new(self.config.burst_size as f32));

        if bucket.try_consume(1.0, &self.config) {
            Ok(())
        } else {
            Err(RateLimitError::TooManyRequests)
        }
    }
}

#[derive(Clone)]
pub struct RateLimitLayer {
    state: RateLimitState,
    key_fn: Arc<dyn Fn(&Request<Body>) -> String + Send + Sync>,
}

impl RateLimitLayer {
    pub fn new(state: RateLimitState) -> Self {
        Self {
            state,
            key_fn: Arc::new(default_key_fn),
        }
    }

    pub fn with_key_fn<F>(state: RateLimitState, key_fn: F) -> Self
    where
        F: Fn(&Request<Body>) -> String + Clone + Send + Sync + 'static,
    {
        Self {
            state,
            key_fn: Arc::new(key_fn),
        }
    }

    pub fn per_ip(state: RateLimitState) -> Self {
        Self {
            state,
            key_fn: Arc::new(ip_key_fn),
        }
    }

    pub fn per_org(state: RateLimitState) -> Self {
        Self {
            state,
            key_fn: Arc::new(org_key_fn),
        }
    }
}

fn default_key_fn(_: &Request<Body>) -> String {
    "default".to_string()
}

fn ip_key_fn(request: &Request<Body>) -> String {
    request
        .headers()
        .get("x-forwarded-for")
        .and_then(|v| v.to_str().ok())
        .or_else(|| request.headers().get("x-real-ip").and_then(|v| v.to_str().ok()))
        .map(|s| s.split(',').next().unwrap_or(s).trim().to_string())
        .unwrap_or_else(|| "unknown".to_string())
}

fn org_key_fn(request: &Request<Body>) -> String {
    request
        .headers()
        .get("x-org-id")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("anonymous")
        .to_string()
}

impl<S> Layer<S> for RateLimitLayer {
    type Service = RateLimitService<S>;

    fn layer(&self, inner: S) -> Self::Service {
        RateLimitService {
            inner,
            state: self.state.clone(),
            key_fn: self.key_fn.clone(),
        }
    }
}

#[derive(Clone)]
pub struct RateLimitService<S> {
    inner: S,
    state: RateLimitState,
    key_fn: Arc<dyn Fn(&Request<Body>) -> String + Send + Sync>,
}

impl<S> Service<Request<Body>> for RateLimitService<S>
where
    S: Service<Request<Body>, Response = Response<Body>> + Clone + Send + 'static,
    S::Future: Send + 'static,
{
    type Response = Response<Body>;
    type Future = Pin<Box<dyn Send + Future<Output = Result<Self::Response, std::convert::Infallible>>>>;
    type Error = std::convert::Infallible;

    fn poll_ready(
        &mut self,
        cx: &mut std::task::Context<'_>,
    ) -> std::task::Poll<Result<(), Self::Error>> {
        self.inner.poll_ready(cx).map_ok(|_| ()).map_err(|_| unreachable!())
    }

    fn call(&mut self, request: Request<Body>) -> Self::Future {
        let key = (self.key_fn)(&request);
        let mut inner = self.inner.clone();
        let state = self.state.clone();

        Box::pin(async move {
            if let Err(RateLimitError::TooManyRequests) = state.check_rate_limit(&key).await {
                let response = Response::builder()
                    .status(StatusCode::TOO_MANY_REQUESTS)
                    .header("X-RateLimit-Limit", state.config.requests_per_minute.to_string())
                    .header("Retry-After", "60")
                    .body(Body::from("Rate limit exceeded"));
                return Ok(response.unwrap_or_else(|_| {
                    Response::builder()
                        .status(StatusCode::INTERNAL_SERVER_ERROR)
                        .body(Body::empty())
                        .expect("Failed to build error response")
                }));
            }

            Ok(inner.call(request).await.unwrap_or_else(|_| {
                Response::builder()
                    .status(StatusCode::INTERNAL_SERVER_ERROR)
                    .body(Body::empty())
                    .expect("Failed to build error response")
            }))
        })
    }
}

#[derive(Debug)]
pub enum RateLimitError {
    TooManyRequests,
}

impl std::fmt::Display for RateLimitError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            RateLimitError::TooManyRequests => write!(f, "Rate limit exceeded"),
        }
    }
}

impl std::error::Error for RateLimitError {}