use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AvatarMoodState {
    pub confidence: f64,
    pub skepticism: f64,
    pub creativity: f64,
    pub urgency: f64,
}

impl Default for AvatarMoodState {
    fn default() -> Self {
        Self {
            confidence: 0.5,
            skepticism: 0.5,
            creativity: 0.5,
            urgency: 0.3,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ExperienceType {
    ChallengeIssued,
    ChallengeReceived,
    ChallengeWon,
    ChallengeLost,
    PositionAccepted,
    PositionRejected,
    SynthesisInfluenced,
    SynthesisIgnored,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AvatarExperience {
    pub experience_type: ExperienceType,
    pub summary: String,
    pub outcome: String,
    pub salience: f64,
    pub related_avatar_key: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AvatarIdentityState {
    pub avatar_id: String,
    pub avatar_key: String,
    pub mood: AvatarMoodState,
    pub total_debates: u32,
    pub total_challenges_issued: u32,
    pub total_challenges_won: u32,
    pub recent_experiences: Vec<AvatarExperience>,
}

impl AvatarMoodState {
    pub fn apply_experience(&mut self, exp: &AvatarExperience) {
        let delta = match exp.experience_type {
            ExperienceType::ChallengeWon
            | ExperienceType::PositionAccepted
            | ExperienceType::SynthesisInfluenced => 0.08,
            ExperienceType::ChallengeLost
            | ExperienceType::PositionRejected
            | ExperienceType::SynthesisIgnored => -0.06,
            ExperienceType::ChallengeIssued => 0.03,
            ExperienceType::ChallengeReceived => -0.02,
        };

        self.confidence = (self.confidence + delta * 0.3).clamp(0.0, 1.0);

        match exp.experience_type {
            ExperienceType::ChallengeReceived | ExperienceType::ChallengeLost => {
                self.skepticism = (self.skepticism + 0.05).clamp(0.0, 1.0);
            }
            ExperienceType::ChallengeWon | ExperienceType::SynthesisInfluenced => {
                self.skepticism = (self.skepticism - 0.03).clamp(0.0, 1.0);
            }
            _ => {}
        }

        if matches!(exp.experience_type, ExperienceType::ChallengeIssued) {
            self.creativity = (self.creativity + 0.02).clamp(0.0, 1.0);
        }

        if matches!(exp.experience_type, ExperienceType::ChallengeReceived) && exp.salience > 0.7 {
            self.urgency = (self.urgency + 0.05).clamp(0.0, 1.0);
        }
    }

    pub fn decay_to_baseline(&mut self, hours_since_active: f64) {
        let factor = (-0.02 * hours_since_active).exp();
        let baseline = AvatarMoodState::default();
        self.confidence = baseline.confidence + (self.confidence - baseline.confidence) * factor;
        self.skepticism = baseline.skepticism + (self.skepticism - baseline.skepticism) * factor;
        self.creativity = baseline.creativity + (self.creativity - baseline.creativity) * factor;
        self.urgency = baseline.urgency + (self.urgency - baseline.urgency) * factor;
    }
}

pub fn compute_personality_summary(mood: &AvatarMoodState, total_debates: u32, challenges_won: u32) -> String {
    let confidence_desc = if mood.confidence > 0.7 {
        "confident"
    } else if mood.confidence < 0.3 {
        "uncertain"
    } else {
        "measured"
    };

    let skepticism_desc = if mood.skepticism > 0.7 {
        "skeptical"
    } else if mood.skepticism < 0.3 {
        "trusting"
    } else {
        "balanced"
    };

    let creativity_desc = if mood.creativity > 0.7 {
        "visionary"
    } else if mood.creativity < 0.3 {
        "pragmatic"
    } else {
        "structured"
    };

    let experience_desc = if total_debates > 20 {
        "seasoned"
    } else if total_debates > 5 {
        "developing"
    } else {
        "emerging"
    };

    let record_desc = if total_debates > 0 {
        let win_rate = challenges_won as f64 / total_debates.max(1) as f64;
        if win_rate > 0.6 {
            "proven track record"
        } else if win_rate > 0.3 {
            "competitive"
        } else {
            "building experience"
        }
    } else {
        "untested"
    };

    format!("{confidence_desc} {skepticism_desc} {creativity_desc} {experience_desc} operator with {record_desc}")
}

pub fn build_identity_context_block(
    mood: &AvatarMoodState,
    personality_summary: &str,
    experiences: &[AvatarExperience],
) -> serde_json::Value {
    let recent: Vec<serde_json::Value> = experiences.iter().rev().take(5).map(|e| {
        serde_json::json!({
            "type": format!("{:?}", e.experience_type),
            "summary": e.summary,
            "outcome": e.outcome,
            "salience": e.salience,
            "related_avatar": e.related_avatar_key,
        })
    }).collect();

    serde_json::json!({
        "personality_summary": personality_summary,
        "current_disposition": {
            "confidence": mood.confidence,
            "skepticism": mood.skepticism,
            "creativity": mood.creativity,
            "urgency": mood.urgency,
        },
        "recent_experiences": recent,
    })
}

impl AvatarIdentityState {
    pub fn new(avatar_id: String, avatar_key: String) -> Self {
        Self {
            avatar_id,
            avatar_key,
            mood: AvatarMoodState::default(),
            total_debates: 0,
            total_challenges_issued: 0,
            total_challenges_won: 0,
            recent_experiences: Vec::new(),
        }
    }

    pub fn record_experience(&mut self, exp: AvatarExperience) {
        let _salience = exp.salience;
        self.mood.apply_experience(&exp);

        match exp.experience_type {
            ExperienceType::ChallengeIssued => self.total_challenges_issued += 1,
            ExperienceType::ChallengeWon => self.total_challenges_won += 1,
            _ => {}
        }

        if matches!(
            exp.experience_type,
            ExperienceType::PositionAccepted
                | ExperienceType::PositionRejected
                | ExperienceType::ChallengeIssued
                | ExperienceType::ChallengeReceived
        ) {
            self.total_debates += 1;
        }

        self.recent_experiences.push(exp);
        if self.recent_experiences.len() > 20 {
            self.recent_experiences.remove(0);
        }
    }

    pub fn personality_summary(&self) -> String {
        compute_personality_summary(&self.mood, self.total_debates, self.total_challenges_won)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fresh_identity_default_mood() {
        let state = AvatarIdentityState::new("a1".into(), "strategist".into());
        assert_eq!(state.mood.confidence, 0.5);
        assert_eq!(state.total_debates, 0);
    }

    #[test]
    fn test_challenge_won_boosts_confidence() {
        let mut state = AvatarIdentityState::new("a1".into(), "strategist".into());
        state.record_experience(AvatarExperience {
            experience_type: ExperienceType::ChallengeWon,
            summary: "Proved claim was unsupported".into(),
            outcome: "accepted".into(),
            salience: 0.8,
            related_avatar_key: Some("copywriter".into()),
        });
        assert!(state.mood.confidence > 0.5);
        assert_eq!(state.total_challenges_won, 1);
    }

    #[test]
    fn test_challenge_lost_lowers_confidence_raises_skepticism() {
        let mut state = AvatarIdentityState::new("a1".into(), "researcher".into());
        let c_before = state.mood.confidence;
        let s_before = state.mood.skepticism;
        state.record_experience(AvatarExperience {
            experience_type: ExperienceType::ChallengeLost,
            summary: "Challenge was overruled".into(),
            outcome: "overruled".into(),
            salience: 0.9,
            related_avatar_key: Some("strategist".into()),
        });
        assert!(state.mood.confidence < c_before);
        assert!(state.mood.skepticism > s_before);
    }

    #[test]
    fn test_decay_to_baseline() {
        let mut mood = AvatarMoodState {
            confidence: 0.9,
            skepticism: 0.9,
            creativity: 0.9,
            urgency: 0.9,
        };
        mood.decay_to_baseline(48.0);
        assert!(mood.confidence < 0.9);
        assert!(mood.confidence > 0.5);
    }

    #[test]
    fn test_personality_summary_changes_with_experience() {
        let mut state = AvatarIdentityState::new("a1".into(), "analyst".into());
        let initial = state.personality_summary();
        assert!(initial.contains("emerging") || initial.contains("untested"));

        for i in 0..25 {
            state.record_experience(AvatarExperience {
                experience_type: ExperienceType::ChallengeWon,
                summary: format!("Challenge {}", i),
                outcome: "won".into(),
                salience: 0.7,
                related_avatar_key: None,
            });
        }
        let later = state.personality_summary();
        assert!(later.contains("seasoned") || later.contains("proven"));
    }

    #[test]
    fn test_recent_experiences_capped_at_20() {
        let mut state = AvatarIdentityState::new("a1".into(), "strategist".into());
        for i in 0..30 {
            state.record_experience(AvatarExperience {
                experience_type: ExperienceType::SynthesisInfluenced,
                summary: format!("Influence {}", i),
                outcome: "accepted".into(),
                salience: 0.5,
                related_avatar_key: None,
            });
        }
        assert_eq!(state.recent_experiences.len(), 20);
    }

    #[test]
    fn test_identity_context_block_structure() {
        let mut state = AvatarIdentityState::new("a1".into(), "strategist".into());
        state.record_experience(AvatarExperience {
            experience_type: ExperienceType::ChallengeIssued,
            summary: "Challenged vague positioning".into(),
            outcome: "pending".into(),
            salience: 0.6,
            related_avatar_key: Some("copywriter".into()),
        });
        let block = build_identity_context_block(&state.mood, &state.personality_summary(), &state.recent_experiences);
        assert!(block.get("personality_summary").is_some());
        assert!(block.get("current_disposition").is_some());
        assert!(block.get("recent_experiences").is_some());
        let recent = block["recent_experiences"].as_array().unwrap();
        assert_eq!(recent.len(), 1);
    }
}
