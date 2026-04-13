//! Entity Essence Language — avatar registry, context enrichment, and lattice state.
//!
//! EEL provides the **avatar-aware context assembly** layer that sits between the
//! foundation data layer and the AI inference layer. It is the core bridge that
//! stamps every AI request with the correct avatar identity, reflection gate, and
//! skill context.
//!
//! ## Core concepts
//!
//! ### Avatar registry
//! `registry_for_org(org_id)` builds a complete `AvatarRegistry` — 21 avatar entries
//! per organization covering strategist, council, and support specialist roles.
//! The registry is constructed from avatar templates defined in `raptorflow_avatars`
//! and is deterministic for a given `org_id`.
//!
//! ### Context enrichment
//! `enrich_context(context_pack, avatar_key, registry)` takes a raw context pack
//! and stamps it with the avatar's `reflection_gate` by looking up the avatar's
//! role in the registry. Unknown avatar keys pass through unchanged with
//! `reflection_gate: None`.
//!
//! ### Lattice state
//! `lattice_for_avatar(entry)` constructs a full `EelLatticeState` — the complete
//! essence, ego, skill-weave, and reflection gate for an avatar. Used by the
//! inference harness to construct prompts.
//!
//! ## Reflection gates by role
//!
//! | Role | Gate | Meaning |
//! |---|---|---|
//! | Strategist | `post-synthesis-only` | Ego only activated after synthesis phase |
//! | Council | `session-close` | Ego review at end of council session |
//! | SupportSpecialist | `artifact-feedback` | Ego activated on artifact receipt |
//! | Intern | `supervisor-reviewed` | Requires supervisor approval before ego activation |
//!
//! ## Dependency chain
//!
//! ```text
//! eel ──► avatars ──► contracts
//!   │                  
//!   └───────────────────► db
//! ```
//!
//! No circular dependencies exist in this chain.

use raptorflow_contracts::{AvatarRegistryEntry, AvatarRole, ContextPack, EelLatticeState};
pub use raptorflow_contracts::AvatarRegistry;
use raptorflow_avatars::build_avatar_registry;
use serde::{Deserialize, Serialize};
use serde_json::json;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EelTopology {
    pub essence_force_include: bool,
    pub reflection_enabled: bool,
    pub skill_alignment_gate: bool,
    pub strategist_reflection_gate: &'static str,
    pub council_reflection_gate: &'static str,
    pub support_specialist_reflection_gate: &'static str,
}

impl Default for EelTopology {
    fn default() -> Self {
        Self {
            essence_force_include: true,
            reflection_enabled: true,
            skill_alignment_gate: true,
            strategist_reflection_gate: "post-synthesis-only",
            council_reflection_gate: "session-close",
            support_specialist_reflection_gate: "artifact-feedback",
        }
    }
}

pub fn registry_for_org(org_id: uuid::Uuid) -> AvatarRegistry {
    build_avatar_registry(org_id)
}

pub fn enrich_context(
    context_pack: ContextPack,
    avatar_key: &str,
    registry: &AvatarRegistry,
) -> ContextPack {
    let entry = registry.entries.iter().find(|e| e.avatar_key == avatar_key);

    match entry {
        None => {
            tracing::warn!(avatar_key, "enrich_context: avatar not found in registry");
            context_pack
        }
        Some(e) => {
            let lattice = lattice_for_avatar(e);
            ContextPack {
                reflection_gate: Some(lattice.reflection_gate),
                ..context_pack
            }
        }
    }
}

pub fn lattice_for_avatar(entry: &AvatarRegistryEntry) -> EelLatticeState {
    let reflection_gate = match &entry.role {
        AvatarRole::Strategist => "post-synthesis-only",
        AvatarRole::Council => "session-close",
        AvatarRole::SupportSpecialist => "artifact-feedback",
        AvatarRole::Intern => "supervisor-reviewed",
    };

    EelLatticeState {
        org_id: entry.org_id,
        avatar_key: entry.avatar_key.clone(),
        role: entry.role.clone(),
        essence_core: json!({
            "display_name": entry.display_name.clone(),
            "office_zone_id": entry.office_zone_id.clone(),
        }),
        ego_signature: json!({
            "reflection_profile": entry.reflection_profile.clone(),
            "support_domain": entry.support_domain.clone(),
        }),
        skill_weave: json!({
            "role": entry.role.clone(),
            "gate": reflection_gate,
        }),
        reflection_gate: reflection_gate.to_string(),
    }
}

#[cfg(test)]
mod tests {
    use raptorflow_contracts::{AvatarRole, ContextPack};
    use raptorflow_avatars::templates;
    use crate::{enrich_context, lattice_for_avatar, registry_for_org};

    const EXPECTED_AVATAR_COUNT: usize = 21;

    fn all_avatar_keys() -> Vec<&'static str> {
        vec![
            "strategist",
            "ogilvy", "bernbach", "hopkins", "draper",
            "patel", "vaynerchuk", "sharp", "godin",
            "kotler", "ries", "cialdini", "sutherland",
            "qa_director", "legal_advisor", "analytics_director", "brand_manager",
            "market_research_lead", "media_buyer", "pr_director", "growth_hacker",
        ]
    }

    fn expected_role_for_key(key: &str) -> AvatarRole {
        match key {
            "strategist" => AvatarRole::Strategist,
            "ogilvy" | "bernbach" | "hopkins" | "draper"
            | "patel" | "vaynerchuk" | "sharp" | "godin"
            | "kotler" | "ries" | "cialdini" | "sutherland" => AvatarRole::Council,
            _ => AvatarRole::SupportSpecialist,
        }
    }

    fn expected_reflection_gate_for_role(role: AvatarRole) -> &'static str {
        match role {
            AvatarRole::Strategist => "post-synthesis-only",
            AvatarRole::Council => "session-close",
            AvatarRole::SupportSpecialist => "artifact-feedback",
            AvatarRole::Intern => "supervisor-reviewed",
        }
    }

    #[test]
    fn test_registry_for_org_builds_21_entries() {
        let org_id = uuid::Uuid::new_v4();
        let registry = registry_for_org(org_id);
        assert_eq!(registry.entries.len(), EXPECTED_AVATAR_COUNT);
        for entry in &registry.entries {
            assert_eq!(entry.org_id, org_id);
        }
    }

    #[test]
    fn test_registry_contains_all_expected_keys() {
        let registry = registry_for_org(uuid::Uuid::new_v4());
        let keys: Vec<_> = registry.entries.iter().map(|e| e.avatar_key.as_str()).collect();
        for key in all_avatar_keys() {
            assert!(keys.contains(&key), "registry should contain '{}'", key);
        }
    }

    #[test]
    fn test_registry_entry_role_matches_expected() {
        let registry = registry_for_org(uuid::Uuid::new_v4());
        for entry in &registry.entries {
            let expected = expected_role_for_key(&entry.avatar_key);
            assert_eq!(entry.role, expected, "avatar '{}'", entry.avatar_key);
        }
    }

    #[test]
    fn test_enrich_context_stamps_correct_gate_per_avatar() {
        let org_id = uuid::Uuid::new_v4();
        let registry = registry_for_org(org_id);

        for avatar_key in all_avatar_keys() {
            let role = expected_role_for_key(avatar_key);
            let expected_gate = expected_reflection_gate_for_role(role);

            let pack = ContextPack {
                org_id,
                foundation_sections: vec![],
                retrieved_ripple_ids: vec![],
                skill_atom_ids: vec![],
                reflection_gate: None,
            };

            let enriched = enrich_context(pack, avatar_key, &registry);
            assert_eq!(
                enriched.reflection_gate,
                Some(expected_gate.to_string()),
                "enrich_context('{}') expected '{}', got {:?}",
                avatar_key, expected_gate, enriched.reflection_gate
            );
        }
    }

    #[test]
    fn test_enrich_context_passes_through_unknown_avatar() {
        let org_id = uuid::Uuid::new_v4();
        let registry = registry_for_org(org_id);
        let pack = ContextPack {
            org_id,
            foundation_sections: vec!["a".to_string()],
            retrieved_ripple_ids: vec![],
            skill_atom_ids: vec![],
            reflection_gate: None,
        };
        let enriched = enrich_context(pack, "does-not-exist", &registry);
        assert_eq!(enriched.reflection_gate, None);
        assert_eq!(enriched.foundation_sections, vec!["a".to_string()]);
    }

    #[test]
    fn test_lattice_gate_matches_role() {
        let org_id = uuid::Uuid::new_v4();
        for avatar_key in all_avatar_keys() {
            let role = expected_role_for_key(avatar_key);
            let entry = raptorflow_contracts::AvatarRegistryEntry {
                org_id,
                avatar_key: avatar_key.to_string(),
                display_name: avatar_key.to_string(),
                role,
                support_domain: None,
                office_zone_id: "zone".to_string(),
                reflection_profile: "profile".to_string(),
            };
            let lattice = lattice_for_avatar(&entry);
            let expected = expected_reflection_gate_for_role(role);
            assert_eq!(lattice.reflection_gate, expected, "avatar '{}'", avatar_key);
        }
    }

    #[test]
    fn test_all_21_templates_have_valid_structure() {
        let all = templates::all();
        assert_eq!(all.len(), EXPECTED_AVATAR_COUNT);

        for tmpl in &all {
            assert!(!tmpl.display_name.is_empty());
            assert!(tmpl.ego_baseline.iter().all(|&v| (0.0..=1.0).contains(&v)));
            assert!(tmpl.ego_multipliers.iter().all(|&v| (0.0..=1.0).contains(&v)));
            assert!(tmpl.ego_decay_rate >= 0.0 && tmpl.ego_decay_rate <= 1.0);
            let essence = (tmpl.essence_core)();
            assert!(essence.is_object());
            let ripples = (tmpl.essence_ripples)();
            assert!(!ripples.is_empty());
            for r in ripples {
                assert!(r.emotion_vector.len() == 8);
                assert!(r.emotion_vector.iter().all(|&v| (0.0..=1.0).contains(&v)));
            }
            let atoms = (tmpl.initial_skill_atoms)();
            assert!(!atoms.is_empty());
            for a in atoms {
                assert!(!a.skill_id.is_empty());
                assert!(!a.name.is_empty());
            }
        }
    }

    #[test]
    fn test_all_templates_have_unique_keys() {
        let all = templates::all();
        let mut keys: Vec<_> = all.iter().map(|t| t.avatar_key).collect();
        keys.sort();
        keys.dedup();
        assert_eq!(keys.len(), EXPECTED_AVATAR_COUNT);
    }

    #[test]
    fn test_avatar_role_counts() {
        let all = templates::all();
        let strat = all.iter().filter(|t| t.role == AvatarRole::Strategist).count();
        let council = all.iter().filter(|t| t.role == AvatarRole::Council).count();
        let support = all.iter().filter(|t| t.role == AvatarRole::SupportSpecialist).count();
        assert_eq!(strat, 1);
        assert_eq!(council, 12);
        assert_eq!(support, 8);
    }

    #[test]
    fn test_reflection_profiles_are_valid_format() {
        let all = templates::all();
        for tmpl in &all {
            let p = &tmpl.reflection_profile;
            assert!(
                !p.is_empty(),
                "template '{}' must have a non-empty reflection_profile",
                tmpl.avatar_key
            );
            assert!(
                p.chars().all(|c| c.is_lowercase() || c == '-' || c.is_ascii_digit()),
                "template '{}' reflection_profile '{}' must be lowercase-kebab format",
                tmpl.avatar_key, p
            );
        }
    }

    #[test]
    fn test_ego_vectors_are_length_8() {
        let all = templates::all();
        for tmpl in &all {
            assert_eq!(tmpl.ego_baseline.len(), 8, "template '{}'", tmpl.avatar_key);
            assert_eq!(tmpl.ego_multipliers.len(), 8, "template '{}'", tmpl.avatar_key);
        }
    }
}
