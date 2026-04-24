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

//! ## Foundation scan routes
//!
//! The following scan routes are available:
//! - `/scan/quick` — lightweight website scan
//! - `/scan/deep` — comprehensive website analysis
//! - `/scan/:scan_id` — get scan by ID
//! - `/versions` — list foundation versions
//! - `/versions/:version_id` — get specific version
//! - `/versions/:version_id/sections/:section` — get specific section from version
//!
//! ## Data contracts
//!
//! - [`FoundationScanMode`] — scan mode enum (Quick, Deep)
//! - [`FoundationScanRequest`] — scan request payload
//! - [`FoundationScanStatusRecord`] — scan status record
//! - [`FoundationVersion`] — foundation version record

pub mod models;
pub mod scan;
pub mod service;
pub mod versioning;

pub use models::*;
pub use scan::*;
pub use service::FoundationService;
#[cfg(test)]
mod test_21_screens;

pub use versioning::VersioningService;
