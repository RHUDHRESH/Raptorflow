use raptorflow_db::PgPool;
use raptorflow_db::models::{AvatarDebateEvent, AvatarMemoryEdge};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

mod analyst;
mod copywriter;
mod core;
mod creative_director;
mod growth_operator;
mod proof_collector;
mod researcher;
mod strategist;

pub use analyst::*;
pub use copywriter::*;
pub use core::*;
pub use creative_director::*;
pub use growth_operator::*;
pub use proof_collector::*;
pub use researcher::*;
pub use strategist::*;

#[cfg(test)]
mod tests {
    use super::*;
    use raptorflow_db::models::AvatarDebateEvent;

    #[test]
    fn test_validate_salience_bounds() {
        assert!(validate_salience(0.0));
        assert!(validate_salience(0.5));
        assert!(validate_salience(1.0));
        assert!(!validate_salience(-0.1));
        assert!(!validate_salience(1.1));
    }

    #[test]
    fn test_validate_confidence_bounds() {
        assert!(validate_confidence(0.0));
        assert!(validate_confidence(1.0));
        assert!(!validate_confidence(-0.01));
        assert!(!validate_confidence(2.0));
    }

    #[test]
    fn test_derive_instinct_frame_proof_required() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec!["proof".to_string()],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_instinct_frame(
            &pack,
            "campaign_request",
            "Create content about why our product is the best",
            "Some context without sources",
        );

        assert!(frame.risk_flags.contains(&"proof_required".to_string()));
    }

    #[test]
    fn test_derive_instinct_frame_positioning_vague() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_instinct_frame(
            &pack,
            "campaign_request",
            "Create vague positioning statement",
            "Some context",
        );

        assert!(frame.risk_flags.contains(&"positioning_vague".to_string()));
    }

    #[test]
    fn test_should_challenge_researcher() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec!["evidence".to_string()],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("speaker".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "This product is the best choice."}),
            confidence: 0.7,
            created_at: chrono::Utc::now(),
        };

        let decision = should_challenge(&pack, &target);

        assert!(decision.should_challenge);
        assert!(decision.reason.contains("lacks supporting evidence"));
    }

    #[test]
    fn test_should_challenge_analyst_unmeasurable() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "analyst".to_string(),
            display_name: "Analyst".to_string(),
            role: "Analyst".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("speaker".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "Our plan is to grow significantly."}),
            confidence: 0.6,
            created_at: chrono::Utc::now(),
        };

        let decision = should_challenge(&pack, &target);

        assert!(decision.should_challenge);
        assert!(
            decision
                .reason
                .contains("lacks measurable success criteria")
        );
    }

    #[test]
    fn test_role_lock_prompt_includes_taboos() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![
                "do not invent proof".to_string(),
                "do not fake metrics".to_string(),
            ],
            operating_principles: vec!["Use context first".to_string()],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let prompt = build_role_lock_prompt(&pack);

        assert!(prompt.contains("do not invent proof"));
        assert!(prompt.contains("do not fake metrics"));
        assert!(prompt.contains("Strategist"));
        assert!(prompt.contains("Use context first"));
        assert!(!prompt.contains("I am human"));
        assert!(!prompt.contains("delusional"));
    }

    #[test]
    fn test_classify_strategist_memory_scar() {
        let summary = "The 'growth hacking' angle failed - low conversion";
        let tags = vec![];
        let result = classify_strategist_memory(summary, &tags);
        assert_eq!(result, StrategistMemoryClassification::Scar);
    }

    #[test]
    fn test_classify_strategist_memory_proof() {
        let summary = "Case study shows 3x ROI with specific messaging";
        let tags = vec![];
        let result = classify_strategist_memory(summary, &tags);
        assert_eq!(result, StrategistMemoryClassification::Proof);
    }

    #[test]
    fn test_classify_strategist_memory_market_learning() {
        let summary = "Competitor positioning as 'enterprise only' opened mid-market gap";
        let tags = vec![];
        let result = classify_strategist_memory(summary, &tags);
        assert_eq!(result, StrategistMemoryClassification::MarketLearning);
    }

    #[test]
    fn test_classify_strategist_memory_customer_learning() {
        let summary = "ICP startups struggle with onboarding complexity";
        let tags = vec![];
        let result = classify_strategist_memory(summary, &tags);
        assert_eq!(result, StrategistMemoryClassification::CustomerLearning);
    }

    #[test]
    fn test_classify_strategist_memory_warning() {
        let summary = "Avoid broad positioning in financial vertical";
        let tags = vec![];
        let result = classify_strategist_memory(summary, &tags);
        assert_eq!(result, StrategistMemoryClassification::Warning);
    }

    #[test]
    fn test_classify_strategist_memory_instinct_fallback() {
        let summary = "Sequencing matters in go-to-market";
        let tags = vec![];
        let result = classify_strategist_memory(summary, &tags);
        assert_eq!(result, StrategistMemoryClassification::Instinct);
    }

    #[test]
    fn test_derive_strategist_instinct_icp_unclear() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_strategist_instinct_frame(
            &pack,
            "Create content about our product",
            "We have a great solution",
        );

        assert!(frame.risk_flags.contains(&"icp_unclear".to_string()));
    }

    #[test]
    fn test_derive_strategist_instinct_enemy_missing() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_strategist_instinct_frame(
            &pack,
            "Build positioning statement",
            "Our product is innovative",
        );

        assert!(frame.risk_flags.contains(&"enemy_missing".to_string()));
    }

    #[test]
    fn test_derive_strategist_instinct_proof_path_missing() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_strategist_instinct_frame(
            &pack,
            "Create revenue growth messaging",
            "Our product helps companies",
        );

        assert!(frame.risk_flags.contains(&"proof_path_missing".to_string()));
    }

    #[test]
    fn test_derive_strategist_instinct_copy_before_strategy() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame =
            derive_strategist_instinct_frame(&pack, "Write ad copy for us", "We sell software");

        assert!(
            frame
                .risk_flags
                .contains(&"copy_before_strategy".to_string())
        );
    }

    #[test]
    fn test_derive_strategist_instinct_positioning_vague() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_strategist_instinct_frame(
            &pack,
            "Position our AI automation platform",
            "We are innovative",
        );

        assert!(frame.risk_flags.contains(&"positioning_vague".to_string()));
    }

    #[test]
    fn test_strategist_challenge_vague_positioning() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("speaker".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "Our AI platform automates everything"}),
            confidence: 0.7,
            created_at: chrono::Utc::now(),
        };

        let decision = strategist_challenge_decision(&pack, &target);

        assert!(decision.should_challenge);
        assert!(decision.reason.contains("generic"));
    }

    #[test]
    fn test_strategist_challenge_proof_claim_without_evidence() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("speaker".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "Studies show our solution increases productivity by 40%"}),
            confidence: 0.8,
            created_at: chrono::Utc::now(),
        };

        let decision = strategist_challenge_decision(&pack, &target);

        assert!(decision.should_challenge);
        assert!(decision.reason.contains("proof"));
    }

    #[test]
    fn test_strategist_challenge_copy_without_icp() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("copywriter".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "How about we say 'Supercharge your workflow'?"}),
            confidence: 0.6,
            created_at: chrono::Utc::now(),
        };

        let decision = strategist_challenge_decision(&pack, &target);

        assert!(decision.should_challenge);
        assert!(decision.reason.contains("ICP"));
    }

    #[test]
    fn test_build_strategist_role_lock_prompt() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec!["ICP clarity".to_string(), "category contrast".to_string()],
            reflexes: vec![],
            taboos: vec![
                "do not invent proof".to_string(),
                "do not write copy before strategy".to_string(),
            ],
            operating_principles: vec![
                "Facts first, then assumptions, then recommendations".to_string(),
            ],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let prompt = build_strategist_role_lock_prompt(&pack);

        assert!(prompt.contains("Strategist"));
        assert!(prompt.contains("Market strategy"));
        assert!(prompt.contains("ICP clarity"));
        assert!(prompt.contains("do not invent proof"));
        assert!(prompt.contains("do not write copy before strategy"));
        assert!(prompt.contains("Facts first"));
        assert!(prompt.contains("Known facts"));
        assert!(prompt.contains("Assumptions"));
        assert!(prompt.contains("Recommendations"));
        assert!(prompt.contains("Open questions"));
        assert!(prompt.contains("highest-leverage strategic move"));
        assert!(prompt.contains("kill vague positioning"));
        assert!(!prompt.contains("I am human"));
        assert!(!prompt.contains("sentient"));
    }

    #[test]
    fn test_classify_researcher_memory_proof() {
        assert_eq!(
            classify_researcher_memory("Verified case study shows results", &[]),
            ResearcherMemoryClassification::Proof
        );
        assert_eq!(
            classify_researcher_memory("Source citation needed", &["evidence".to_string()]),
            ResearcherMemoryClassification::Proof
        );
    }

    #[test]
    fn test_classify_researcher_memory_warning() {
        assert_eq!(
            classify_researcher_memory("Unverified claim found", &[]),
            ResearcherMemoryClassification::Warning
        );
        assert_eq!(
            classify_researcher_memory("This looks hallucinated", &["fake".to_string()]),
            ResearcherMemoryClassification::Warning
        );
    }

    #[test]
    fn test_classify_researcher_memory_scar() {
        assert_eq!(
            classify_researcher_memory("Wrong competitor assumption", &[]),
            ResearcherMemoryClassification::Scar
        );
        assert_eq!(
            classify_researcher_memory("Failed proof claim", &["false assumption".to_string()]),
            ResearcherMemoryClassification::Scar
        );
    }

    #[test]
    fn test_classify_researcher_memory_market_learning() {
        assert_eq!(
            classify_researcher_memory("Competitor pricing analysis", &[]),
            ResearcherMemoryClassification::MarketLearning
        );
        assert_eq!(
            classify_researcher_memory("Category positioning", &["market".to_string()]),
            ResearcherMemoryClassification::MarketLearning
        );
    }

    #[test]
    fn test_classify_researcher_memory_customer_learning() {
        assert_eq!(
            classify_researcher_memory("Customer pain point analysis", &[]),
            ResearcherMemoryClassification::CustomerLearning
        );
        assert_eq!(
            classify_researcher_memory("Buyer objection", &["ICP".to_string()]),
            ResearcherMemoryClassification::CustomerLearning
        );
    }

    #[test]
    fn test_classify_claim_evidence_unsupported() {
        assert_eq!(
            classify_claim_evidence("40% increase in revenue", ""),
            EvidenceLevel::Unsupported
        );
        assert_eq!(
            classify_claim_evidence("10x faster", "Some context"),
            EvidenceLevel::Unsupported
        );
    }

    #[test]
    fn test_classify_claim_evidence_source_backed() {
        assert_eq!(
            classify_claim_evidence("40% increase", "According to verified case study"),
            EvidenceLevel::SourceBacked
        );
        assert_eq!(
            classify_claim_evidence("data shows improvement", "Source: internal data"),
            EvidenceLevel::SourceBacked
        );
    }

    #[test]
    fn test_classify_claim_evidence_contradicted() {
        assert_eq!(
            classify_claim_evidence("40% revenue boost", "This contradicts earlier findings"),
            EvidenceLevel::Contradicted
        );
    }

    #[test]
    fn test_classify_claim_evidence_uncertain() {
        assert_eq!(
            classify_claim_evidence("may increase by 30%", ""),
            EvidenceLevel::PlausibleButUnverified
        );
        assert_eq!(
            classify_claim_evidence("could be faster", ""),
            EvidenceLevel::PlausibleButUnverified
        );
    }

    #[test]
    fn test_claim_safety_action() {
        assert_eq!(
            claim_safety_action(EvidenceLevel::Verified),
            ClaimSafetyAction::Keep
        );
        assert_eq!(
            claim_safety_action(EvidenceLevel::SourceBacked),
            ClaimSafetyAction::Keep
        );
        assert_eq!(
            claim_safety_action(EvidenceLevel::PlausibleButUnverified),
            ClaimSafetyAction::Qualify
        );
        assert_eq!(
            claim_safety_action(EvidenceLevel::Assumption),
            ClaimSafetyAction::DowngradeToAssumption
        );
        assert_eq!(
            claim_safety_action(EvidenceLevel::Unsupported),
            ClaimSafetyAction::NeedsSource
        );
        assert_eq!(
            claim_safety_action(EvidenceLevel::Contradicted),
            ClaimSafetyAction::ContradictionReview
        );
    }

    #[test]
    fn test_derive_researcher_instinct_frame_source_missing() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec!["source quality".to_string()],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_researcher_instinct_frame(
            &pack,
            "studies show this works",
            "Some context without source",
        );

        assert!(frame.risk_flags.contains(&"source_missing".to_string()));
    }

    #[test]
    fn test_derive_researcher_instinct_frame_unsupported_metric() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_researcher_instinct_frame(
            &pack,
            "40% revenue increase claimed",
            "No evidence provided",
        );

        assert!(frame.risk_flags.contains(&"unsupported_metric".to_string()));
    }

    #[test]
    fn test_derive_researcher_instinct_frame_competitor_unverified() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_researcher_instinct_frame(
            &pack,
            "Analyze competitor positioning",
            "Limited context",
        );

        assert!(
            frame
                .risk_flags
                .contains(&"competitor_claim_unverified".to_string())
        );
    }

    #[test]
    fn test_derive_researcher_instinct_frame_overconfident() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_researcher_instinct_frame(
            &pack,
            "Guaranteed to be the #1 solution",
            "Some context",
        );

        assert!(
            frame
                .risk_flags
                .contains(&"overconfident_language".to_string())
        );
    }

    #[test]
    fn test_researcher_challenge_decision_fake_metric() {
        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("strategist".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "40% revenue increase expected"}),
            confidence: 0.6,
            created_at: chrono::Utc::now(),
        };

        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let decision = researcher_challenge_decision(&pack, &target);

        assert!(decision.should_challenge);
        assert!(
            decision
                .reason
                .contains("metric claim without supporting source")
        );
    }

    #[test]
    fn test_researcher_challenge_decision_fake_customer_quote() {
        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("copywriter".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "Customers say this is great"}),
            confidence: 0.6,
            created_at: chrono::Utc::now(),
        };

        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let decision = researcher_challenge_decision(&pack, &target);

        assert!(decision.should_challenge);
        assert!(
            decision
                .reason
                .contains("customer quote without actual attribution")
        );
    }

    #[test]
    fn test_researcher_challenge_decision_unsupported_competitor() {
        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("strategist".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "Competitor does X better"}),
            confidence: 0.6,
            created_at: chrono::Utc::now(),
        };

        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let decision = researcher_challenge_decision(&pack, &target);

        assert!(decision.should_challenge);
        assert!(
            decision
                .reason
                .contains("competitor claim without data or source")
        );
    }

    #[test]
    fn test_build_researcher_role_lock_prompt() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![
                "source quality".to_string(),
                "evidence hierarchy".to_string(),
            ],
            reflexes: vec![],
            taboos: vec![
                "do not invent sources".to_string(),
                "do not invent metrics".to_string(),
            ],
            operating_principles: vec!["Evidence beats confidence.".to_string()],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let prompt = build_researcher_role_lock_prompt(&pack);

        assert!(prompt.contains("Researcher"));
        assert!(prompt.contains("Evidence discipline"));
        assert!(prompt.contains("source quality"));
        assert!(prompt.contains("do not invent sources"));
        assert!(prompt.contains("do not invent metrics"));
        assert!(prompt.contains("Evidence beats confidence"));
        assert!(prompt.contains("Known facts"));
        assert!(prompt.contains("Assumptions"));
        assert!(prompt.contains("Unsupported claims"));
        assert!(prompt.contains("find what is true"));
        assert!(prompt.contains("expose what is unsupported"));
        assert!(!prompt.contains("I am human"));
        assert!(!prompt.contains("sentient"));
    }
}
