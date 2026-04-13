//! Foundation data management for RaptorFlow.
//!
//! The "Foundation" is a versioned snapshot of a client's core marketing data:
//! company info, target audience, value proposition, and competitive positioning.
//! When a client completes the onboarding wizard, [`FoundationService::create_initial`]
//! writes the snapshot and seeds all 21 avatar templates via [`raptorflow_avatars::seed_org_avatars`].
//!
//! ## Key services
//!
//! - [`FoundationService`] — create/update foundation snapshots
//! - [`VersioningService`] — snapshot versioning logic
//! - [`ScanService`] — foundation scanning stub (see `scan.rs`)
//!
//! ## Dependency chain
//!
//! ```text
//! foundation → db, avatars, config
//! ```

pub mod models;
pub mod scan;
pub mod service;
pub mod versioning;

pub use models::*;
pub use service::FoundationService;
pub use versioning::VersioningService;
pub use scan::ScanService;
