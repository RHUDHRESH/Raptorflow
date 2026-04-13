#[cfg(test)]
mod tests {
    use raptorflow_avatars::templates;
    use raptorflow_avatars::registry::build_avatar_registry;
    use raptorflow_contracts::{AvatarRegistryEntry, AvatarRole, ContextPack};
    use raptorflow_avatars::SeedReport;
    use raptorflow_eel::{enrich_context, lattice_for_avatar};
    use uuid::Uuid;

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
            "ogilvy" | "bernbach" | "hopkins" | "draper" |
            "patel" | "vaynerchuk" | "sharp" | "godin" |
            "kotler" | "ries" | "cialdini" | "sutherland" => AvatarRole::Council,
            _ => AvatarRole::SupportSpecialist,
        }
    }

    fn expected_reflection_gate_for_role(role: &AvatarRole) -> &'static str {
        match role {
            AvatarRole::Strategist => "post-synthesis-only",
            AvatarRole::Council => "session-close",
            AvatarRole::SupportSpecialist => "artifact-feedback",
            AvatarRole::Intern => "supervisor-reviewed",
        }
    }

    #[test]
    fn test_all_21_templates_return_valid_avatar_template() {
        let all_templates = templates::all();
        assert_eq!(all_templates.len(), EXPECTED_AVATAR_COUNT);

        let expected_keys = all_avatar_keys();
        for key in expected_keys {
            let tmpl = all_templates.iter().find(|t| t.avatar_key == key);
            assert!(
                tmpl.is_some(),
                "template '{}' should be present",
                key
            );
            let tmpl = tmpl.unwrap();
            assert!(!tmpl.display_name.is_empty(), "template '{}' must have a display_name", key);
            assert!(
                tmpl.ego_baseline.iter().all(|&v| (0.0..=1.0).contains(&v)),
                "template '{}' ego_baseline values must be in [0,1]",
                key
            );
            assert!(
                tmpl.ego_multipliers.iter().all(|&v| (0.0..=1.0).contains(&v)),
                "template '{}' ego_multipliers values must be in [0,1]",
                key
            );
            assert!(
                tmpl.ego_decay_rate >= 0.0 && tmpl.ego_decay_rate <= 1.0,
                "template '{}' ego_decay_rate must be in [0,1], got {}",
                key,
                tmpl.ego_decay_rate
            );
            let essence = (tmpl.essence_core)();
            assert!(essence.is_object(), "template '{}' essence_core must be a JSON object", key);
            let ripples = (tmpl.essence_ripples)();
            assert!(
                !ripples.is_empty(),
                "template '{}' must have at least one essence ripple",
                key
            );
            for ripple in ripples {
                assert!(
                    ripple.emotion_vector.iter().all(|&v| (0.0..=1.0).contains(&v)),
                    "template '{}' ripple '{}' emotion_vector values must be in [0,1]",
                    key,
                    ripple.summary_text.chars().take(20).collect::<String>()
                );
            }
            let skill_atoms = (tmpl.initial_skill_atoms)();
            assert!(
                !skill_atoms.is_empty(),
                "template '{}' must have at least one skill atom",
                key
            );
        }
    }

    #[test]
    fn test_avatar_count_by_role() {
        let all_templates = templates::all();
        let strategist_count = all_templates.iter().filter(|t| t.role == AvatarRole::Strategist).count();
        let council_count = all_templates.iter().filter(|t| t.role == AvatarRole::Council).count();
        let support_count = all_templates.iter().filter(|t| t.role == AvatarRole::SupportSpecialist).count();

        assert_eq!(strategist_count, 1, "expected 1 strategist");
        assert_eq!(council_count, 12, "expected 12 council members");
        assert_eq!(support_count, 8, "expected 8 support specialists");
        assert_eq!(strategist_count + council_count + support_count, EXPECTED_AVATAR_COUNT);
    }

    #[test]
    fn test_build_avatar_registry_returns_correct_count_and_org_id() {
        let org_id = Uuid::new_v4();
        let registry = build_avatar_registry(org_id);

        assert_eq!(registry.entries.len(), EXPECTED_AVATAR_COUNT);

        for entry in &registry.entries {
            assert_eq!(
                entry.org_id, org_id,
                "registry entry '{}' should have the correct org_id",
                entry.avatar_key
            );
            assert!(!entry.avatar_key.is_empty());
            assert!(!entry.display_name.is_empty());
            assert!(!entry.office_zone_id.is_empty());
            assert!(!entry.reflection_profile.is_empty());
        }
    }

    #[test]
    fn test_registry_contains_all_expected_avatar_keys() {
        let org_id = Uuid::new_v4();
        let registry = build_avatar_registry(org_id);
        let keys: Vec<_> = registry.entries.iter().map(|e| e.avatar_key.as_str()).collect();

        for expected_key in all_avatar_keys() {
            assert!(
                keys.contains(&expected_key),
                "registry should contain avatar key '{}'",
                expected_key
            );
        }
    }

    #[test]
    fn test_registry_entry_role_matches_template_role() {
        let org_id = Uuid::new_v4();
        let registry = build_avatar_registry(org_id);

        for entry in &registry.entries {
            let expected_role = expected_role_for_key(&entry.avatar_key);
            assert_eq!(
                &entry.role, &expected_role,
                "avatar '{}' should have role {:?}, got {:?}",
                entry.avatar_key, expected_role, entry.role
            );
        }
    }

    #[test]
    fn test_lattice_for_avatar_returns_correct_reflection_gate() {
        let org_id = Uuid::new_v4();

        for avatar_key in all_avatar_keys() {
            let role = expected_role_for_key(avatar_key);
            let entry = AvatarRegistryEntry {
                org_id,
                avatar_key: avatar_key.to_string(),
                display_name: avatar_key.to_string(),
                role: role.clone(),
                support_domain: None,
                office_zone_id: "test-zone".to_string(),
                reflection_profile: "test".to_string(),
            };

            let lattice = lattice_for_avatar(&entry);
            let expected_gate = expected_reflection_gate_for_role(&role);

            assert_eq!(
                lattice.reflection_gate, expected_gate,
                "avatar '{}' with role {:?} should have reflection_gate '{}', got '{}'",
                avatar_key, role, expected_gate, lattice.reflection_gate
            );
        }
    }

    #[test]
    fn test_enrich_context_stamps_reflection_gate() {
        let org_id = Uuid::new_v4();
        let registry = build_avatar_registry(org_id);

        for avatar_key in all_avatar_keys() {
            let role = expected_role_for_key(avatar_key);
            let expected_gate = expected_reflection_gate_for_role(&role);

            let context_pack = ContextPack {
                org_id,
                foundation_sections: vec!["company_info".to_string()],
                retrieved_ripple_ids: vec![],
                skill_atom_ids: vec![],
                reflection_gate: None,
            };

            let enriched = enrich_context(context_pack, avatar_key, &registry);

            assert_eq!(
                enriched.reflection_gate,
                Some(expected_gate.to_string()),
                "enrich_context('{}') should stamp reflection_gate '{}', got {:?}",
                avatar_key,
                expected_gate,
                enriched.reflection_gate
            );
        }
    }

    #[test]
    fn test_enrich_context_returns_unmodified_pack_for_unknown_avatar() {
        let org_id = Uuid::new_v4();
        let registry = build_avatar_registry(org_id);

        let context_pack = ContextPack {
            org_id,
            foundation_sections: vec!["company_info".to_string()],
            retrieved_ripple_ids: vec![],
            skill_atom_ids: vec![],
            reflection_gate: None,
        };

        let enriched = enrich_context(context_pack, "nonexistent-avatar", &registry);

        assert_eq!(enriched.reflection_gate, None);
        assert_eq!(enriched.foundation_sections, vec!["company_info".to_string()]);
    }

    #[test]
    fn test_enrich_context_preserves_other_context_pack_fields() {
        let org_id = Uuid::new_v4();
        let registry = build_avatar_registry(org_id);

        let context_pack = ContextPack {
            org_id,
            foundation_sections: vec!["a".to_string(), "b".to_string()],
            retrieved_ripple_ids: vec![],
            skill_atom_ids: vec![],
            reflection_gate: None,
        };

        let enriched = enrich_context(context_pack, "strategist", &registry);

        assert_eq!(enriched.foundation_sections.len(), 2);
        assert_eq!(enriched.foundation_sections[0], "a");
        assert_eq!(enriched.foundation_sections[1], "b");
        assert!(enriched.reflection_gate.is_some());
    }

    #[test]
    fn test_seed_report_struct_is_default_constructible() {
        let report = SeedReport::default();
        assert!(report.seeded.is_empty());
    }

    #[test]
    fn test_essence_ripple_seed_fields_are_populated() {
        let all_templates = templates::all();

        for tmpl in all_templates {
            let ripples = (tmpl.essence_ripples)();
            assert!(
                !ripples.is_empty(),
                "template '{}' should have essence ripples",
                tmpl.avatar_key
            );

            for ripple in ripples {
                assert!(
                    !ripple.summary_text.is_empty(),
                    "ripple in '{}' should have non-empty summary_text",
                    tmpl.avatar_key
                );
                assert!(
                    !ripple.raw_text.is_empty(),
                    "ripple in '{}' should have non-empty raw_text",
                    tmpl.avatar_key
                );
                assert!(
                    ripple.emotion_vector.len() == 8,
                    "ripple in '{}' should have 8 emotion values (Plutchik), got {}",
                    tmpl.avatar_key,
                    ripple.emotion_vector.len()
                );
            }
        }
    }

    #[test]
    fn test_skill_atoms_have_valid_structure() {
        let all_templates = templates::all();

        for tmpl in all_templates {
            let skill_atoms = (tmpl.initial_skill_atoms)();
            assert!(
                !skill_atoms.is_empty(),
                "template '{}' should have skill atoms",
                tmpl.avatar_key
            );

            for atom in skill_atoms {
                assert!(
                    !atom.skill_id.is_empty(),
                    "skill atom in '{}' should have non-empty skill_id",
                    tmpl.avatar_key
                );
                assert!(
                    !atom.name.is_empty(),
                    "skill atom in '{}' should have non-empty name",
                    tmpl.avatar_key
                );
                assert!(
                    !atom.description.is_empty(),
                    "skill atom in '{}' should have non-empty description",
                    tmpl.avatar_key
                );
                assert!(
                    !atom.domain_tags.is_empty(),
                    "skill atom '{}' in '{}' should have domain_tags",
                    atom.name, tmpl.avatar_key
                );
            }
        }
    }

    #[test]
    fn test_avatar_templates_have_unique_keys() {
        let all_templates = templates::all();
        let mut keys: Vec<_> = all_templates.iter().map(|t| t.avatar_key).collect();
        keys.sort();
        keys.dedup();
        assert_eq!(
            keys.len(),
            EXPECTED_AVATAR_COUNT,
            "all avatar keys must be unique"
        );
    }

    #[test]
    fn test_reflection_profile_is_set_for_all_avatars() {
        let all_templates = templates::all();
        for tmpl in all_templates {
            assert!(
                !tmpl.reflection_profile.is_empty(),
                "template '{}' must have a reflection_profile",
                tmpl.avatar_key
            );
            let profile: &str = &tmpl.reflection_profile[..];
            assert!(
                profile == "post-synthesis-only"
                    || profile == "session-close"
                    || profile == "artifact-feedback"
                    || profile == "supervisor-reviewed",
                "template '{}' has unexpected reflection_profile '{}'",
                tmpl.avatar_key,
                tmpl.reflection_profile
            );
        }
    }

    #[test]
    fn test_ego_baseline_length_is_8_for_all_avatars() {
        let all_templates = templates::all();
        for tmpl in all_templates {
            assert_eq!(
                tmpl.ego_baseline.len(),
                8,
                "template '{}' ego_baseline must have 8 values (Plutchik emotions), got {}",
                tmpl.avatar_key,
                tmpl.ego_baseline.len()
            );
            assert_eq!(
                tmpl.ego_multipliers.len(),
                8,
                "template '{}' ego_multipliers must have 8 values, got {}",
                tmpl.avatar_key,
                tmpl.ego_multipliers.len()
            );
        }
    }
}
