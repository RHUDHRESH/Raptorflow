//! HTTP routing layer for the RaptorFlow API.
//!
//! Composes all route modules into a single [`axum::Router`] via [`create_router()`].
//! The router is built in [`crate::router::create_router`] which is called by `raptorflow_api::main`.
//!
//! ## Route structure
//!
//! | Namespace | Module | Auth |
//! |---|---|---|
//! | `/health` | health | Public |
//! | `/api/v1/billing` | billing | Required |
//! | `/api/v1/uploads` | uploads | Required |
//! | `/api/v1/foundation` | foundation | Required |
//! | `/api/v1/intel` | intel | Required |
//! | `/api/v1/prl/*` | prl | Required |
//! | `/api/v1/prl/decay` | prl | Required |
//! | `/api/v1/jobs/*` | jobs | Required |
//! | `/api/v1/webhooks/clerk` | auth | Public |
//! | `/api/v1/webhooks/razorpay` | billing | Public |
//!
//! ## Middleware
//!
//! - [`tower_http::cors::CorsLayer`] — permissive dev CORS (restrictive in prod)
//! - [`AuthMiddleware`] — JWT validation via Clerk JWKS on all `/api/v1/*` routes
//! - [`TraceLayer`] — request tracing via `tracing`

pub mod middleware;
pub mod router;
pub mod routes;

pub use router::create_router;
