//! Integration test fixtures and helpers for RaptorFlow crates.
//!
//! This crate provides reusable test fixtures across the RaptorFlow workspace.
//! It is a **dev-dependency** only — never included in production builds.
//!
//! ## Test modules
//!
//! | Module | Purpose |
//! |---|---|
//! | `s3_tests` | S3 upload/download test helpers |
//!
//! ## Usage
//!
//! ```rust,ignore
//! use raptorflow_testing::{sample_campaign, sample_json_fixture};
//! ```
//!
//! ## Note on AWS SDK
//!
//! `raptorflow_aws` is a dependency of this crate. On Windows, the AWS SDK
//! requires linking against `pthread`, `vsnprintf`, and `RtlSecureZeroMemory`
//! which may not be available. If `cargo test --workspace` fails to link on
//! Windows, exclude this crate from the test run: `cargo test --workspace
//! --exclude raptorflow-testing`.

use raptorflow_contracts::Campaign;
use serde_json::json;
use uuid::Uuid;

pub mod s3_tests;

pub fn sample_campaign() -> Campaign {
    Campaign {
        org_id: Uuid::nil(),
        campaign_id: "campaign_01".to_string(),
        status: "draft".to_string(),
        name: "Sample Campaign".to_string(),
    }
}

pub fn sample_json_fixture() -> serde_json::Value {
    json!({
        "org_id": Uuid::nil(),
        "campaign": sample_campaign(),
    })
}
