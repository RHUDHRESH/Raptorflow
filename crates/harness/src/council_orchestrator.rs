use raptorflow_aws::bedrock::BedrockInferenceClient;
use raptorflow_db::PgPool;
use raptorflow_db::models::AvatarDebateEvent;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use uuid::Uuid;

use super::avatar_soul::{
    AvatarEmbodimentPack, ChallengeDecision, DerivedInstinctFrame, analyst_challenge_decision,
    build_avatar_embodiment_pack, copywriter_challenge_decision,
    creative_director_challenge_decision, derive_analyst_instinct_frame,
    derive_copywriter_instinct_frame, derive_creative_director_instinct_frame,
    derive_growth_operator_instinct_frame, derive_proof_collector_instinct_frame,
    derive_researcher_instinct_frame, derive_strategist_instinct_frame,
    growth_operator_challenge_decision, proof_collector_challenge_decision,
    researcher_challenge_decision, strategist_challenge_decision,
};
use super::council_ai;

const DEFAULT_AVATAR_KEYS: &[&str] = &[
    "strategist",
    "researcher",
    "copywriter",
    "growth_operator",
    "analyst",
    "creative_director",
    "proof_collector",
];

const ALLOWED_AVATAR_KEYS: &[&str] = DEFAULT_AVATAR_KEYS;

const ALLOWED_MODES: &[&str] = &["dry_run", "draft"];

const MAX_CHALLENGE_ROUNDS: usize = 2;
const MAX_CHALLENGES_PER_AVATAR: usize = 3;
const MAX_TOTAL_CHALLENGES: usize = 21;

mod execution;
mod routing;
mod synthesis;
mod types;

pub use execution::{run_council_dry_run, run_council_run};
pub(crate) use routing::{
    compute_challenge_routing, create_position_content, derive_instinct_for_avatar,
    get_challenge_function,
};
pub use synthesis::synthesize_council_result;
pub(crate) use synthesis::{persist_council_synthesis_artifact, truncate_c};
pub use types::{
    AvatarPresenceStateOutput, CouncilOrchestratorError, CouncilRunRequest, CouncilRunResult,
    CouncilTurnOutput, validate_request,
};
pub(crate) use types::{generate_id, resolve_avatar_roster};

#[cfg(test)]
mod tests {
    use super::*;

    const ALL_7_KEYS: [&str; 7] = [
        "strategist",
        "researcher",
        "copywriter",
        "growth_operator",
        "analyst",
        "creative_director",
        "proof_collector",
    ];

    #[test]
    fn test_default_roster_contains_all_7_avatars() {
        let roster = resolve_avatar_roster(&[]);
        assert_eq!(roster.len(), 7);
        for key in &ALL_7_KEYS {
            assert!(roster.contains(&key.to_string()), "Missing avatar: {}", key);
        }
    }

    #[test]
    fn test_requested_roster_rejects_unknown_key() {
        let req = CouncilRunRequest {
            org_id: Uuid::new_v4(),
            request_summary: "Test request summary for council".to_string(),
            context_summary: "Test context".to_string(),
            mode: "dry_run".to_string(),
            requested_avatar_keys: vec!["unknown_avatar".to_string()],
            max_challenge_rounds: 1,
        };
        let result = validate_request(&req);
        assert!(result.is_err());
        let err = result.unwrap_err();
        match err {
            CouncilOrchestratorError::InvalidRequest(msg) => {
                assert!(msg.contains("unknown_avatar"));
            }
            _ => panic!("Expected InvalidRequest error"),
        }
    }

    #[test]
    fn test_validate_request_accepts_valid() {
        let req = CouncilRunRequest {
            org_id: Uuid::new_v4(),
            request_summary: "Valid test request summary for council".to_string(),
            context_summary: "Test context".to_string(),
            mode: "dry_run".to_string(),
            requested_avatar_keys: vec!["strategist".to_string(), "analyst".to_string()],
            max_challenge_rounds: 1,
        };
        assert!(validate_request(&req).is_ok());
    }

    #[test]
    fn test_max_challenge_rounds_rejects_gt_2() {
        let req = CouncilRunRequest {
            org_id: Uuid::new_v4(),
            request_summary: "Test request summary for council validation".to_string(),
            context_summary: "Test".to_string(),
            mode: "dry_run".to_string(),
            requested_avatar_keys: vec![],
            max_challenge_rounds: 5,
        };
        let result = validate_request(&req);
        assert!(result.is_err());
    }

    #[test]
    fn test_synthesis_contains_all_required_sections() {
        let debate_events = vec![];
        let avatar_roster = vec!["strategist".to_string(), "researcher".to_string()];
        let synthesis =
            synthesize_council_result("Test task", "Test context", &debate_events, &avatar_roster);
        assert!(synthesis.get("known_facts").is_some());
        assert!(synthesis.get("assumptions").is_some());
        assert!(synthesis.get("council_recommendation").is_some());
        assert!(synthesis.get("avatar_positions").is_some());
        assert!(synthesis.get("challenges").is_some());
        assert!(synthesis.get("risks").is_some());
        assert!(synthesis.get("open_questions").is_some());
        assert!(synthesis.get("next_actions").is_some());
    }

    #[test]
    fn test_thin_context_produces_open_questions() {
        let debate_events = vec![];
        let avatar_roster = vec!["strategist".to_string()];
        let synthesis = synthesize_council_result("Brief task", "", &debate_events, &avatar_roster);
        let open_questions = synthesis["open_questions"].as_array().unwrap();
        assert!(!open_questions.is_empty());
    }

    #[test]
    fn test_challenge_routing_prevents_self_challenge() {
        for key in &ALL_7_KEYS {
            let targets = compute_challenge_routing(key);
            assert!(
                !targets.contains(key),
                "Avatar {} can challenge itself",
                key
            );
        }
    }

    #[test]
    fn test_challenge_cap_enforced() {
        let challengers = [
            (
                "researcher",
                [
                    "strategist",
                    "copywriter",
                    "creative_director",
                    "growth_operator",
                ]
                .as_slice(),
            ),
            (
                "proof_collector",
                [
                    "strategist",
                    "copywriter",
                    "creative_director",
                    "growth_operator",
                    "researcher",
                ]
                .as_slice(),
            ),
            (
                "analyst",
                ["strategist", "growth_operator", "copywriter"].as_slice(),
            ),
            ("strategist", ["researcher", "copywriter"].as_slice()),
            ("copywriter", ["strategist", "creative_director"].as_slice()),
            ("growth_operator", ["strategist", "copywriter"].as_slice()),
            ("creative_director", ["strategist", "copywriter"].as_slice()),
        ];
        for (key, expected_targets) in &challengers {
            let targets = compute_challenge_routing(key);
            assert!(!targets.contains(key));
            assert_eq!(targets.len(), expected_targets.len());
        }
    }

    #[test]
    fn test_researcher_challenges_unsupported_claim() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };
        let event = AvatarDebateEvent {
            debate_event_id: "test".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: String::new(),
            speaker_avatar_id: Some("strategist".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("test".to_string()),
            content: serde_json::json!({"text": "We are the best solution and always deliver massive results without any proven evidence"}),
            confidence: 0.8,
            created_at: chrono::Utc::now(),
        };
        let decision = researcher_challenge_decision(&pack, &event);
        assert!(decision.should_challenge);
    }

    #[test]
    fn test_analyst_challenges_scaling_from_weak_signal() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "analyst".to_string(),
            display_name: "Analyst".to_string(),
            role: "analyst".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };
        let event = AvatarDebateEvent {
            debate_event_id: "test".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: String::new(),
            speaker_avatar_id: Some("strategist".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("test".to_string()),
            content: serde_json::json!({"text": "We should double down on this channel based on the impressions we saw"}),
            confidence: 0.8,
            created_at: chrono::Utc::now(),
        };
        let decision = analyst_challenge_decision(&pack, &event);
        assert!(decision.should_challenge);
    }

    #[test]
    fn test_proof_collector_challenges_unsupported_proof() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "proof_collector".to_string(),
            display_name: "Proof Collector".to_string(),
            role: "proof".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };
        let event = AvatarDebateEvent {
            debate_event_id: "test".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: String::new(),
            speaker_avatar_id: Some("copywriter".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("test".to_string()),
            content: serde_json::json!({"text": "Our solution is guaranteed to deliver 10x ROI"}),
            confidence: 0.8,
            created_at: chrono::Utc::now(),
        };
        let decision = proof_collector_challenge_decision(&pack, &event);
        assert!(decision.should_challenge);
    }

    #[test]
    fn test_creative_director_challenges_generic_concept() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "creative_director".to_string(),
            display_name: "Creative Director".to_string(),
            role: "creative".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };
        let event = AvatarDebateEvent {
            debate_event_id: "test".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: String::new(),
            speaker_avatar_id: Some("strategist".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("test".to_string()),
            content: serde_json::json!({"text": "Use a generic stock photo template with our logo"}),
            confidence: 0.8,
            created_at: chrono::Utc::now(),
        };
        let decision = creative_director_challenge_decision(&pack, &event);
        assert!(decision.should_challenge);
    }

    #[test]
    fn test_dry_run_does_not_call_bedrock() {
        let req = CouncilRunRequest {
            org_id: Uuid::new_v4(),
            request_summary: "Test council dry run with minimal context".to_string(),
            context_summary: "Simple test".to_string(),
            mode: "dry_run".to_string(),
            requested_avatar_keys: vec![],
            max_challenge_rounds: 0,
        };
        assert!(validate_request(&req).is_ok());
    }

    #[test]
    fn test_validate_request_short_summary_rejected() {
        let req = CouncilRunRequest {
            org_id: Uuid::new_v4(),
            request_summary: "Short".to_string(),
            context_summary: "Test context".to_string(),
            mode: "dry_run".to_string(),
            requested_avatar_keys: vec![],
            max_challenge_rounds: 1,
        };
        assert!(validate_request(&req).is_err());
    }

    #[test]
    fn test_create_position_content_all_avatars() {
        let instinct = DerivedInstinctFrame {
            instinct_frame_id: "test".to_string(),
            dominant_concern: "Test concern".to_string(),
            risk_flags: vec!["missing_proof".to_string(), "weak_signal".to_string()],
            recommended_posture: "Test posture".to_string(),
            visible_summary: "Test summary".to_string(),
        };
        for key in &ALL_7_KEYS {
            let content = create_position_content(key, &instinct);
            assert!(
                content.is_object(),
                "Position content for {} is not an object",
                key
            );
        }
    }
}
