//! Ripple harvester — extracts learning atoms from capability outputs.
//!
//! The ripple harvester analyzes AI outputs to identify compact learning
//! atoms that can be stored and later used for context.

#![allow(clippy::manual_clamp, clippy::collapsible_if)]

use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RippleCandidate {
    pub summary: String,
    pub ripple_type: String,
    pub salience: f64,
    pub tags: Vec<String>,
}

pub struct RippleHarvester;

impl RippleHarvester {
    pub fn extract_candidates(
        capability_key: &str,
        artifact: &Value,
        max_ripples: usize,
    ) -> Vec<RippleCandidate> {
        let mut candidates = Vec::new();

        if let Some(obj) = artifact.as_object() {
            if let Some(learnings) = obj.get("learnings").and_then(|v| v.as_array()) {
                for learning in learnings.iter().take(max_ripples) {
                    if let Some(text) = learning.as_str() {
                        if text.len() >= 20 {
                            candidates.push(RippleCandidate {
                                summary: text.to_string(),
                                ripple_type: Self::infer_ripple_type(capability_key, text),
                                salience: 0.7,
                                tags: Self::extract_tags(text),
                            });
                        }
                    } else if let Some(obj) = learning.as_object() {
                        if let Some(text) = obj
                            .get("text")
                            .or(obj.get("learning"))
                            .and_then(|v| v.as_str())
                        {
                            if text.len() >= 20 {
                                candidates.push(RippleCandidate {
                                    summary: text.to_string(),
                                    ripple_type: obj
                                        .get("type")
                                        .and_then(|v| v.as_str())
                                        .unwrap_or("general_learning")
                                        .to_string(),
                                    salience: obj
                                        .get("salience")
                                        .and_then(|v| v.as_f64())
                                        .unwrap_or(0.7),
                                    tags: obj
                                        .get("tags")
                                        .and_then(|v| v.as_array())
                                        .map(|arr| {
                                            arr.iter()
                                                .filter_map(|t| t.as_str().map(String::from))
                                                .collect::<Vec<_>>()
                                        })
                                        .unwrap_or_default(),
                                });
                            }
                        }
                    }
                }
            }

            if let Some(ripple_candidates) = obj.get("ripple_candidates").and_then(|v| v.as_array())
            {
                for candidate in ripple_candidates.iter().take(max_ripples) {
                    if let Some(text) = candidate.as_str() {
                        if text.len() >= 20 {
                            candidates.push(RippleCandidate {
                                summary: text.to_string(),
                                ripple_type: Self::infer_ripple_type(capability_key, text),
                                salience: 0.6,
                                tags: Self::extract_tags(text),
                            });
                        }
                    } else if let Some(obj) = candidate.as_object() {
                        if let Some(text) = obj
                            .get("summary")
                            .or(obj.get("text"))
                            .and_then(|v| v.as_str())
                        {
                            if text.len() >= 20 {
                                candidates.push(RippleCandidate {
                                    summary: text.to_string(),
                                    ripple_type: obj
                                        .get("type")
                                        .and_then(|v| v.as_str())
                                        .unwrap_or("general_learning")
                                        .to_string(),
                                    salience: obj
                                        .get("salience")
                                        .and_then(|v| v.as_f64())
                                        .unwrap_or(0.6),
                                    tags: vec![],
                                });
                            }
                        }
                    }
                }
            }

            if let Some(assumptions) = obj.get("assumptions").and_then(|v| v.as_array()) {
                for assumption in assumptions.iter().take(max_ripples / 2) {
                    if let Some(text) = assumption.as_str() {
                        if text.len() >= 20 {
                            candidates.push(RippleCandidate {
                                summary: format!("Assumption: {}", text),
                                ripple_type: "assumption".to_string(),
                                salience: 0.5,
                                tags: vec!["assumption".to_string()],
                            });
                        }
                    }
                }
            }

            if let Some(winning_angles) = obj.get("winning_angles").and_then(|v| v.as_array()) {
                for angle in winning_angles.iter().take(max_ripples / 2) {
                    if let Some(text) = angle.as_str() {
                        if text.len() >= 15 {
                            candidates.push(RippleCandidate {
                                summary: format!("Winning angle: {}", text),
                                ripple_type: "copy_learning".to_string(),
                                salience: 0.65,
                                tags: vec!["winning_angle".to_string()],
                            });
                        }
                    }
                }
            }

            if let Some(hooks) = obj.get("hooks").and_then(|v| v.as_array()) {
                for hook in hooks.iter().take(max_ripples / 2) {
                    if let Some(text) = hook.as_str() {
                        if text.len() >= 15 {
                            candidates.push(RippleCandidate {
                                summary: format!("Hook: {}", text),
                                ripple_type: "hook_learning".to_string(),
                                salience: 0.55,
                                tags: vec!["hook".to_string()],
                            });
                        }
                    } else if let Some(obj) = hook.as_object() {
                        if let Some(text) =
                            obj.get("text").or(obj.get("hook")).and_then(|v| v.as_str())
                        {
                            if text.len() >= 15 {
                                candidates.push(RippleCandidate {
                                    summary: format!("Hook: {}", text),
                                    ripple_type: "hook_learning".to_string(),
                                    salience: obj
                                        .get("salience")
                                        .and_then(|v| v.as_f64())
                                        .unwrap_or(0.55),
                                    tags: vec!["hook".to_string()],
                                });
                            }
                        }
                    }
                }
            }
        }

        candidates.truncate(max_ripples);
        candidates
    }

    fn infer_ripple_type(capability_key: &str, text: &str) -> String {
        let lower = text.to_lowercase();

        if capability_key.contains("copy") || capability_key.contains("hooks") {
            if capability_key.contains("hooks") || lower.contains("hook") {
                return "hook_learning".to_string();
            }
            if lower.contains("proof")
                || lower.contains("testimonial")
                || lower.contains("case study")
            {
                return "proof_learning".to_string();
            }
            return "copy_learning".to_string();
        }

        if capability_key.contains("foundation") || capability_key.contains("icp") {
            if lower.contains("audience") || lower.contains("customer") {
                return "audience_learning".to_string();
            }
            return "foundation_learning".to_string();
        }

        if capability_key.contains("positioning") || capability_key.contains("offer") {
            return "positioning_learning".to_string();
        }

        if capability_key.contains("content") || capability_key.contains("calendar") {
            return "content_learning".to_string();
        }

        "general_learning".to_string()
    }

    fn extract_tags(text: &str) -> Vec<String> {
        let lower = text.to_lowercase();
        let mut tags = Vec::new();

        let tag_keywords = [
            ("founder", "founder_brand"),
            ("proof", "proof"),
            ("testimonial", "proof"),
            ("case study", "proof"),
            ("audience", "audience"),
            ("customer", "audience"),
            ("hook", "hook"),
            ("angle", "angle"),
            ("positioning", "positioning"),
            ("differentiation", "positioning"),
            ("value", "value"),
            ("benefit", "benefit"),
            ("pain", "pain_point"),
            ("challenge", "pain_point"),
        ];

        for (keyword, tag) in tag_keywords.iter() {
            if lower.contains(keyword) && !tags.contains(&tag.to_string()) {
                tags.push(tag.to_string());
            }
        }

        if tags.len() > 3 {
            tags.truncate(3);
        }

        tags
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extract_candidates_from_learnings() {
        let artifact = serde_json::json!({
            "learnings": [
                "This ICP responds well to founder-led proof stories.",
                "LinkedIn posts with numbers perform better for this audience."
            ]
        });

        let candidates = RippleHarvester::extract_candidates("copy.hooks.generate", &artifact, 5);

        assert_eq!(candidates.len(), 2);
        assert!(candidates[0].summary.contains("founder-led proof"));
        assert_eq!(candidates[0].ripple_type, "hook_learning");
    }

    #[test]
    fn test_extract_candidates_from_hooks() {
        let artifact = serde_json::json!({
            "hooks": [
                { "text": "The shortcut most founders take that kills credibility", "salience": 0.8 },
                { "hook": "Why your ICP is your most underrated asset", "salience": 0.75 }
            ]
        });

        let candidates = RippleHarvester::extract_candidates("copy.hooks.generate", &artifact, 5);

        assert_eq!(candidates.len(), 2);
        assert_eq!(candidates[0].ripple_type, "hook_learning");
    }

    #[test]
    fn test_ignore_short_text() {
        let artifact = serde_json::json!({
            "learnings": [
                "Good.",
                "This is a longer learning that should be captured because it is over 20 characters."
            ]
        });

        let candidates = RippleHarvester::extract_candidates("copy.hooks.generate", &artifact, 5);

        assert_eq!(candidates.len(), 1);
    }

    #[test]
    fn test_max_ripples() {
        let learnings: Vec<String> = (0..10)
            .map(|i| {
                format!(
                    "Learning {} - this is a longer text to pass the 20 char test",
                    i
                )
            })
            .collect();

        let artifact = serde_json::json!({
            "learnings": learnings
        });

        let candidates = RippleHarvester::extract_candidates("copy.hooks.generate", &artifact, 3);

        assert_eq!(candidates.len(), 3);
    }
}
