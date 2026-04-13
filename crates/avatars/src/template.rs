use raptorflow_contracts::{AvatarRole, SkillAtom};
use serde_json::Value;

pub struct AvatarTemplate {
    pub avatar_key: &'static str,
    pub display_name: &'static str,
    pub role: AvatarRole,
    pub pod: Option<&'static str>,
    pub support_domain: Option<&'static str>,
    pub office_zone_id: &'static str,
    pub reflection_profile: &'static str,

    pub essence_core: fn() -> Value,

    pub essence_ripples: fn() -> Vec<EssenceRippleSeed>,

    pub ego_baseline: [f64; 8],
    pub ego_multipliers: [f64; 8],
    pub ego_decay_rate: f64,

    pub initial_skill_atoms: fn() -> Vec<SkillAtom>,
}

pub struct EssenceRippleSeed {
    pub summary_text: &'static str,
    pub raw_text: &'static str,
    pub trigger_text: &'static str,
    pub emotion_vector: [f64; 8],
}