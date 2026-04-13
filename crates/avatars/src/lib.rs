//! Avatar template library for RaptorFlow's 21 multi-agent council system.
//!
//! This crate implements the "data-not-code" avatar architecture. Every avatar
//! is a pure data record — no per-avatar behaviour code exists. Avatars are
//! differentiated by their `essence_core` JSONB, `ego_baseline[8]` Plutchik
//! emotion vector, and `skill_atoms` JSONB.
//!
//! ## Avatar roster (21 total)
//!
//! | Role | Count | Examples |
//! |---|---|---|
//! | Strategist | 1 | strategist |
//! | Council Creative | 4 | ogilvy, bernbach, hopkins, draper |
//! | Council Digital | 4 | patel, vaynerchuk, sharp, godin |
//! | Council Strategy | 4 | kotler, ries, cialdini, sutherland |
//! | Support Specialist | 8 | qa_director, legal_advisor, analytics_director, … |
//!
//! ## Key types
//!
//! - [`AvatarTemplate`] — the static template for one avatar
//! - [`EssenceRippleSeed`] — a pre-seeded memory ripple baked into the avatar
//! - [`build_avatar_registry()`][registry::build_avatar_registry] — builds the full 21-entry registry for an org
//! - [`seed_org_avatars()`][seeding::seed_org_avatars] — persists all 21 avatars + ripples into the DB
//!
//! ## Dependency chain
//!
//! ```text
//! foundation → avatars → contracts
//!                  ↘ db
//! harness   → eel   → avatars
//! ```
//!
//! Avatars MUST NOT depend on foundation, harness, or eel (no circular deps).

pub mod template;
pub mod seeding;
pub mod registry;
pub mod templates;

pub use template::{AvatarTemplate, EssenceRippleSeed};
pub use seeding::{seed_org_avatars, SeedReport};
pub use registry::build_avatar_registry;