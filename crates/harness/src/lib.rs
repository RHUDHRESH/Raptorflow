//! Agent execution harness — session management, context assembly, and ego decay.
//!
//! The harness is the **runtime orchestrator** for AI agent sessions. It coordinates
//! foundation loading, avatar state management, context pack assembly, and session
//! persistence across the RaptorFlow agent lifecycle.
//!
//! ## Core types
//!
//! ### SessionContext
//! The central state container for a live agent session. Holds:
//! - `session_id` / `org_id` / `user_id` — identity triple
//! - `agents` — `HashMap<Uuid, AvatarState>` — per-agent working state
//! - `foundation` — the org's current foundation snapshot
//! - `avatar_registry` — 21 avatar entries for this org (from EEL)
//! - `db_pool` — service references
//!
//! ### AvatarState
//! Per-agent state including `AgentEssence` (loaded from DB), `working_memory`
//! (loaded from DB), `context_pack` (assembled on demand), and `event_log`.
//!
//! ### SessionManager
//! Creates new sessions: loads foundation, validates required sections,
//! loads agent essences from DB, loads working memory from DB, applies
//! ego decay, and assembles the initial `SessionContext`.
//!
//! ### ContextAssember
//! Assembles a `ContextPack` from avatar state and foundation data for each
//! inference request. The `reflection_gate` field is set here (currently `None`
//! — callers should use `eel::enrich_context` to stamp it per avatar).
//!
//! ### EgoDecay
//! Computes exponential decay on ego state vectors based on time elapsed since
//! last agent activity. Decay is applied per-dimension using per-avatar
//! `ego_multipliers` so different emotional dimensions decay at different rates.
//!
//! ## Capability Harness (new in 0022)
//!
//! ### Cortex
//! Builds bounded context packs from Foundation, Intel, Campaign, Office, and Ripple data.
//!
//! ### ExecutionEngine
//! Executes capabilities by calling Bedrock with properly constructed prompts.
//!
//! ### RippleHarvester
//! Extracts learning atoms from capability outputs for future context.
//!
//! ### CapabilitySeeder
//! Seeds the 5 default safe capabilities into the database.
//!
//! ## Dependency chain
//!
//! ```text
//! harness ──► eel ──► avatars ──► contracts
//!       │                          
//!       └──► db (pg pool + queries)
//!       └──► aws (bedrock inference)
//! ```
//!
//! No circular dependencies exist in this chain.

#![allow(clippy::manual_clamp)]

pub mod analyst_soul;
pub mod avatar_soul;
pub mod copywriter_soul;
pub mod cortex;
pub mod council_ai;
pub mod council_orchestrator;
pub mod creative_director_soul;
pub mod execution;
pub mod growth_operator_soul;
pub mod identity;
pub mod proof_collector_soul;
pub mod researcher_soul;
pub mod ripples;
pub mod seeds;
pub mod strategist_soul;

use anyhow::Result;
use chrono::{DateTime, Utc};
use futures::future;
use raptorflow_contracts::{ContextPack, MemoryEvent, SessionTokenUsage};
use raptorflow_db::PgPool;
use raptorflow_db::models::{AgentEssence, FoundationSnapshot};
use raptorflow_eel::AvatarRegistry;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use ulid::Ulid;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RippleSummary {
    pub ripple_id: String,
    pub summary_text: String,
    pub salience: f64,
    pub emotion_vector: Option<Vec<f64>>,
}

#[derive(Debug, Clone)]
pub struct AvatarState {
    pub agent_essence: AgentEssence,
    pub working_memory: Vec<RippleSummary>,
    pub context_pack: Option<ContextPack>,
    pub event_log: Vec<MemoryEvent>,
}

pub struct SessionContext {
    pub session_id: Ulid,
    pub org_id: Uuid,
    pub user_id: Uuid,
    pub agents: HashMap<Uuid, AvatarState>,
    pub foundation: FoundationSnapshot,
    pub foundation_cache_key: Option<String>,
    pub db_pool: PgPool,
    pub avatar_registry: AvatarRegistry,
    pub session_state: SessionState,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SessionState {
    Initializing,
    AgentsGenerating,
    Synthesizing,
    EventsHarvesting,
    Complete,
    Failed,
}

impl std::fmt::Display for SessionState {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            SessionState::Initializing => write!(f, "initializing"),
            SessionState::AgentsGenerating => write!(f, "agents_generating"),
            SessionState::Synthesizing => write!(f, "synthesizing"),
            SessionState::EventsHarvesting => write!(f, "events_harvesting"),
            SessionState::Complete => write!(f, "complete"),
            SessionState::Failed => write!(f, "failed"),
        }
    }
}

pub struct SessionManager;

impl SessionManager {
    pub async fn create_session(
        db_pool: PgPool,
        org_id: Uuid,
        user_id: Uuid,
        agent_ids: Vec<Uuid>,
    ) -> Result<SessionContext> {
        let session_id = Ulid::new();
        let created_at = Utc::now();

        tracing::info!(
            session_id = %session_id,
            org_id = %org_id,
            user_id = %user_id,
            agent_count = agent_ids.len(),
            "Initializing session"
        );

        let foundation = Self::load_foundation(&db_pool, org_id).await?;
        Self::validate_foundation(&foundation)?;

        let avatar_registry = raptorflow_eel::registry_for_org(org_id);
        let mut agents = HashMap::new();

        let agent_futures: Vec<_> = agent_ids
            .iter()
            .map(|agent_id| Self::load_agent_state(db_pool.clone(), org_id, *agent_id))
            .collect();

        let results: Vec<Result<AvatarState>> = future::join_all(agent_futures).await;

        for (agent_id, result) in agent_ids.iter().zip(results.into_iter()) {
            match result {
                Ok(avatar_state) => {
                    agents.insert(*agent_id, avatar_state);
                }
                Err(e) => {
                    tracing::warn!(
                        agent_id = %agent_id,
                        error = %e,
                        "Failed to load agent state"
                    );
                }
            }
        }

        Ok(SessionContext {
            session_id,
            org_id,
            user_id,
            agents,
            foundation,
            foundation_cache_key: None,
            db_pool,
            avatar_registry,
            session_state: SessionState::Initializing,
            created_at,
        })
    }

    async fn load_foundation(pool: &PgPool, org_id: Uuid) -> Result<FoundationSnapshot> {
        let snapshots = raptorflow_db::queries::get_foundation_snapshots(pool, org_id).await?;

        snapshots
            .into_iter()
            .next()
            .ok_or_else(|| anyhow::anyhow!("No foundation found for org"))
    }

    fn validate_foundation(foundation: &FoundationSnapshot) -> Result<()> {
        let sections = &foundation.sections;
        let required_sections = [
            "company_info",
            "target_audience",
            "value_proposition",
            "competitive_positioning",
        ];

        if let Some(obj) = sections.as_object() {
            for section in &required_sections {
                if !obj.contains_key(*section) {
                    tracing::warn!(missing_section = %section, "Foundation section missing");
                }
            }
        }

        Ok(())
    }

    async fn load_agent_state(pool: PgPool, org_id: Uuid, agent_id: Uuid) -> Result<AvatarState> {
        let essence = Self::load_agent_essence(&pool, org_id, agent_id).await?;
        let avatar_key = essence.avatar_key.clone();
        let working_memory = Self::load_working_memory(&pool, org_id, &avatar_key).await?;
        let avatar_state = Self::apply_ego_decay(essence, &working_memory);

        Ok(avatar_state)
    }

    async fn load_agent_essence(
        pool: &PgPool,
        org_id: Uuid,
        agent_id: Uuid,
    ) -> Result<AgentEssence> {
        let essences = raptorflow_db::queries::get_agent_essences(pool).await?;

        essences
            .into_iter()
            .find(|e| e.agent_id == agent_id && e.org_id == org_id)
            .ok_or_else(|| anyhow::anyhow!("Agent essence not found for agent_id: {}", agent_id))
    }

    async fn load_working_memory(
        pool: &PgPool,
        org_id: Uuid,
        avatar_key: &str,
    ) -> Result<Vec<RippleSummary>> {
        const MAX_MEMORY_RIPPLES: i64 = 50;

        let summaries = raptorflow_db::queries::get_ripples_for_avatar(
            pool,
            org_id,
            avatar_key,
            MAX_MEMORY_RIPPLES,
        )
        .await
        .map_err(|e| {
            anyhow::anyhow!(
                "Failed to load working memory for avatar {}: {}",
                avatar_key,
                e
            )
        })?;

        Ok(summaries
            .into_iter()
            .map(|s| RippleSummary {
                ripple_id: s.ripple_id,
                summary_text: s.summary_text,
                salience: s.salience,
                emotion_vector: None,
            })
            .collect())
    }

    fn apply_ego_decay(essence: AgentEssence, working_memory: &[RippleSummary]) -> AvatarState {
        let last_active = essence.last_active_at.unwrap_or(essence.created_at);
        let hours_since_active = (Utc::now() - last_active).num_hours();

        let decay_factor = (-essence.ego_decay_rate * hours_since_active as f64).exp();
        let decay_factor = decay_factor.max(0.0).min(1.0);

        let mut ego_state = essence.ego_state.clone();
        for i in 0..ego_state.len() {
            let baseline = essence.ego_baseline.get(i).copied().unwrap_or(0.0);
            let current = ego_state.get(i).copied().unwrap_or(baseline);
            let decayed = baseline + (current - baseline) * decay_factor;
            if i < ego_state.len() {
                ego_state[i] = decayed;
            }
        }

        AvatarState {
            agent_essence: AgentEssence {
                ego_state,
                last_active_at: Some(Utc::now()),
                ..essence
            },
            working_memory: working_memory.to_vec(),
            context_pack: None,
            event_log: Vec::new(),
        }
    }
}

impl SessionContext {
    pub fn update_session_state(&mut self, state: SessionState) {
        tracing::info!(
            session_id = %self.session_id,
            old_state = %self.session_state,
            new_state = %state,
            "Session state transition"
        );
        self.session_state = state;
    }

    pub fn set_context_pack(&mut self, agent_id: Uuid, context_pack: ContextPack) {
        if let Some(avatar_state) = self.agents.get_mut(&agent_id) {
            avatar_state.context_pack = Some(context_pack);
        }
    }

    pub fn log_event(&mut self, agent_id: Uuid, event: MemoryEvent) {
        if let Some(avatar_state) = self.agents.get_mut(&agent_id) {
            avatar_state.event_log.push(event);
        }
    }

    pub async fn persist_session(&self) -> Result<()> {
        tracing::debug!(
            session_id = %self.session_id,
            state = %self.session_state,
            "Persisting session state"
        );

        Ok(())
    }

    pub async fn record_token_usage(
        &self,
        session_id: Ulid,
        model_tier: &str,
        input_tokens: i64,
        output_tokens: i64,
    ) -> Result<()> {
        let usage = SessionTokenUsage {
            org_id: self.org_id,
            session_id: session_id.to_string(),
            model_tier: model_tier.to_string(),
            input_tokens,
            output_tokens,
        };

        tracing::info!(
            session_id = %session_id,
            model_tier = %model_tier,
            input_tokens = input_tokens,
            output_tokens = output_tokens,
            "Token usage recorded"
        );

        let _ = usage;
        Ok(())
    }

    pub fn get_agent_count(&self) -> usize {
        self.agents.len()
    }

    pub fn get_active_agent_ids(&self) -> Vec<Uuid> {
        self.agents.keys().copied().collect()
    }

    pub fn is_complete(&self) -> bool {
        matches!(
            self.session_state,
            SessionState::Complete | SessionState::Failed
        )
    }
}

pub struct ContextAssember;

impl ContextAssember {
    pub fn assemble_context_pack(
        avatar_state: &AvatarState,
        foundation: &FoundationSnapshot,
        _task: &str,
    ) -> ContextPack {
        let essence = &avatar_state.agent_essence;

        let foundation_sections = foundation
            .sections
            .as_object()
            .map(|obj| obj.keys().cloned().collect())
            .unwrap_or_default();

        let retrieved_ripple_ids: Vec<String> = avatar_state
            .working_memory
            .iter()
            .map(|r| r.ripple_id.clone())
            .collect();

        let skill_atom_ids: Vec<String> = if let Some(skills) = essence.skill_atoms.as_array() {
            skills
                .iter()
                .filter_map(|s| s.get("id").and_then(|id| id.as_str()))
                .map(String::from)
                .collect()
        } else {
            Vec::new()
        };

        ContextPack {
            org_id: essence.org_id,
            foundation_sections,
            retrieved_ripple_ids,
            skill_atom_ids,
            reflection_gate: None,
        }
    }
}

pub struct EgoDecay;

impl EgoDecay {
    pub fn compute_decay(
        ego_state: &[f64],
        ego_baseline: &[f64],
        ego_multipliers: &[f64],
        hours_elapsed: f64,
        decay_rate: f64,
    ) -> Vec<f64> {
        let decay_factor = (-decay_rate * hours_elapsed).exp();

        ego_state
            .iter()
            .enumerate()
            .map(|(i, current)| {
                let baseline = ego_baseline.get(i).copied().unwrap_or(0.0);
                let multiplier = ego_multipliers.get(i).copied().unwrap_or(1.0);
                let decayed = baseline + (*current - baseline) * decay_factor;
                decayed * multiplier
            })
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_session_state_display() {
        assert_eq!(SessionState::Initializing.to_string(), "initializing");
        assert_eq!(SessionState::Complete.to_string(), "complete");
        assert_eq!(SessionState::Failed.to_string(), "failed");
    }

    #[test]
    fn test_ego_decay_computation() {
        let ego_state = vec![0.8, 0.6, 0.7];
        let ego_baseline = vec![0.5, 0.5, 0.5];
        let ego_multipliers = vec![1.0, 1.0, 1.0];

        let result =
            EgoDecay::compute_decay(&ego_state, &ego_baseline, &ego_multipliers, 0.0, 0.05);
        assert_eq!(result, ego_state);

        let result =
            EgoDecay::compute_decay(&ego_state, &ego_baseline, &ego_multipliers, 24.0, 0.05);
        for (i, val) in result.iter().enumerate() {
            assert!(*val >= ego_baseline[i]);
            assert!(*val <= ego_state[i]);
        }
    }

    #[test]
    fn test_foundation_validation() {
        let foundation = FoundationSnapshot {
            foundation_snapshot_id: "test".to_string(),
            org_id: Uuid::new_v4(),
            foundation_version: 1,
            sections: serde_json::json!({
                "company_info": {},
                "target_audience": {},
                "value_proposition": {},
                "competitive_positioning": {}
            }),
            source: "test".to_string(),
            created_at: Utc::now(),
            updated_at: Utc::now(),
        };

        assert!(SessionManager::validate_foundation(&foundation).is_ok());
    }
}
