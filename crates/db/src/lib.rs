//! Database layer for RaptorFlow.
//!
//! Exposes a [`PgPool`] (sqlx PostgreSQL connection pool) and typed query
//! functions. Models are re-exported so callers only need one import.
//!
//! ## Migration location
//!
//! **Authoritative migrations live in `database/migrations/`** (not here).
//! These are applied manually in production. The `crates/db/migrations/` directory
//! (sqlx migrate format) is not wired in — do not use it.
//!
//! ## Key modules
//!
//! - [`models`] — SQLx row types (`FoundationSnapshot`, `AgentEssence`, etc.)
//! - [`pool`] — `PgPool` constructor from a URL
//! - [`queries`] — all typed query functions (get_foundation_snapshots, etc.)
//!
//! ## RLS
//!
//! All tenant-scoped tables use Row Level Security via `app.current_org_id()`.
//! The application must `SET LOCAL app.current_org_id = '{org_id}'` before
//! executing queries on behalf of a tenant.

pub mod models;
pub mod pool;
pub mod queries;

pub use models::*;
pub use pool::{PgPool, TenantDbPool};
