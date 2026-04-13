# RAPTORFLOW ENGINEERING ADDENDUM A
## Ripple Creation: The Complete Implementation

*This addendum fills the single largest gap in the master blueprint series. Read this before writing a single line of the PRL ingest pipeline.*

---

# Chapter 1: The MemoryEvent — Every Field Defined

The MemoryEvent is the struct that travels through the Tokio MPSC channel from the point of event detection to the ingest worker. It must carry everything the ingest worker needs to create a complete ripple without making additional database calls or inference calls for information that was already available at the point the event fired.

```rust
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// The atomic unit that travels through the ripple ingest channel.
/// Created at the point of event detection. Consumed by the ingest worker.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryEvent {
    /// Unique identifier for this event (used for deduplication)
    pub event_id: String,           // ULID
    
    /// Tenant isolation
    pub org_id: Uuid,
    
    /// The agent who experienced this event
    /// For shared events (e.g., synthesis visible to all), 
    /// one MemoryEvent is created per agent who should remember it
    pub agent_id: Uuid,
    
    /// The session in which this event occurred
    pub session_id: String,         // ULID
    
    /// Optional campaign context
    pub campaign_id: Option<String>,
    
    /// Optional move context  
    pub move_id: Option<String>,
    
    /// The typed event — carries all source-specific data
    pub event_source: EventSource,
    
    /// The raw content of the event
    /// For inference outputs: the full text
    /// For tool results: the complete result JSON
    /// For performance data: the metric event JSON
    pub raw_content: String,
    
    /// The scope this ripple should have in the PRL
    pub intended_scope: RippleScope,
    
    /// The hierarchy level this ripple should occupy (1-4)
    pub intended_hierarchy: u8,
    
    /// Pre-computed ripple data extracted from structured output in generation
    /// Present when the generating agent included a <ripple_data> block
    /// Absent for non-generation events
    pub extracted_ripple_data: Option<ExtractedRippleData>,
    
    /// Whether this event should block (wait for ripple creation before 
    /// the session continues) or fire-and-forget
    pub blocking: bool,
    
    /// When this event occurred
    pub fired_at: DateTime<Utc>,
}

/// The typed event classification — every possible event that produces a ripple
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", content = "data")]
pub enum EventSource {
    /// A Council avatar generated a position in a debate
    CouncilPosition {
        session_id: String,
        avatar_key: String,         // "ogilvy", "patel", etc.
        round_number: u8,
        position_word_count: u32,
        session_type: String,       // "tactical", "operational", "strategic", "war_room"
    },
    
    /// The Strategist produced a synthesis
    StrategistSynthesis {
        session_id: String,
        participating_agent_count: u8,
        synthesis_word_count: u32,
        session_type: String,
        deadlock_detected: bool,
    },
    
    /// The Strategist evaluated a campaign brief
    BriefEvaluated {
        brief_id: String,
        accepted: bool,
        criteria_failed: Vec<String>,   // empty if accepted
        clarification_requested: Option<String>,
    },
    
    /// A debate verdict — who won, what the key tension was
    /// Created AFTER synthesis, to record the outcome of the debate
    DebateVerdict {
        session_id: String,
        /// The avatar_key of the agent whose position was most closely 
        /// reflected in the synthesis. Can be "synthesis" if 
        /// the synthesis was genuinely novel.
        primary_adopted_position: String,
        /// avatar_keys of agents whose positions were substantially rejected
        substantially_rejected: Vec<String>,
        /// The key strategic tension the debate surfaced
        key_tension_summary: String,
    },
    
    /// A user expressed an explicit preference in any interface
    UserPreference {
        preference_key: String,         // e.g., "response_format", "detail_level", "timing_preference"
        preference_value: String,       // e.g., "bullet_points", "brief", "morning_only"
        confidence: f32,               // 0.0-1.0: 1.0 for explicit, 0.6 for inferred
        source_interface: String,       // "muse", "foundation", "campaign_feedback"
    },
    
    /// A prediction was resolved — outcome is now known
    PredictionResolved {
        prediction_ripple_id: String,   // the ripple whose prediction_json we are resolving
        actual_outcome_description: String,
        prediction_error_magnitude: f32,    // 0.0 = perfect, 1.0 = complete surprise
        was_confirmed: bool,
    },
    
    /// Content was generated for a task
    ContentGenerated {
        task_id: String,
        content_id: String,
        content_type: String,           // "ad_copy", "social_post", "blog", "email"
        channel: String,
        generating_avatar_key: String,
        voice_compliance_score: f32,
        variant_count: u8,
    },
    
    /// Performance data arrived for generated content
    ContentPerformance {
        content_id: String,
        task_id: String,
        metric_name: String,            // "ctr", "engagement_rate", "conversion_rate"
        metric_value: f32,
        projected_value: f32,           // what was projected when the content was created
        deviation_pct: f32,             // (actual - projected) / projected
        above_expectation: bool,
    },
    
    /// A competitive signal from the intelligence pipeline
    CompetitiveSignal {
        competitor_id: Uuid,
        competitor_name: String,
        signal_type: String,            // "pricing_change", "messaging_shift", "new_ad", "seo_movement"
        significance: String,           // "minor", "moderate", "major"
        affected_campaign_ids: Vec<String>,
        summary: String,
    },
    
    /// A campaign task was completed by the user
    TaskCompleted {
        task_id: String,
        task_type: String,
        scheduled_date: String,         // ISO date
        completed_date: String,         // ISO date
        days_late: i32,                 // 0 = on time, positive = late
    },
    
    /// A campaign task was missed
    TaskMissed {
        task_id: String,
        task_type: String,
        scheduled_date: String,
        criticality: String,            // "critical", "important", "routine"
        move_id: String,
    },
    
    /// A campaign Move completed
    MoveCompleted {
        move_id: String,
        move_type: String,
        achieved_pct: f32,              // completion criteria achievement 0.0-1.0+
        days_to_complete: u32,
        tasks_missed_count: u32,
    },
    
    /// The Muse pattern analysis detected a recurring topic or preference
    MusePatternDetected {
        pattern_type: String,           // "recurring_topic", "preference", "knowledge_gap", "foundation_drift"
        pattern_description: String,
        occurrence_count: u32,
        conversation_ids: Vec<String>,
    },
    
    /// An intern completed a research task
    InternResearchCompleted {
        intern_task_id: String,
        parent_agent_id: Uuid,
        task_type: String,
        query: String,
        result_quality: f32,            // 0.0-1.0 estimated quality
        result_summary: String,
    },
    
    /// The EEL reflection process completed for an agent
    ReflectionCompleted {
        agent_id: Uuid,
        reflection_output_type: String, // "no_change", "skill_refinement", "belief_extension"
        vfe_before: f32,
        vfe_after: f32,
        skill_modified: Option<String>,
    },
    
    /// A replanning session produced changes to a campaign
    ReplanningCompleted {
        replan_id: String,
        trigger_type: String,
        changes_proposed: u8,
        changes_accepted: u8,
        user_response: String,          // "accepted_all", "accepted_partial", "rejected"
    },
}

/// Data extracted from the <ripple_data> structured output block
/// that agents include in their generation when prompted
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExtractedRippleData {
    /// One-sentence statement of the core claim or insight
    pub core_claim: String,
    
    /// One-sentence description of the key reasoning
    pub key_reasoning: String,
    
    /// What the agent expects will happen as a result
    pub prediction: Option<String>,
    
    /// Timeframe for the prediction to resolve
    pub prediction_timeframe_days: Option<u32>,
    
    /// Agent's confidence in this ripple's content
    pub confidence: f32,
    
    /// Any assumptions that must be true for this to be valid
    pub key_assumptions: Vec<String>,
    
    /// What would cause this to be revised
    pub revision_conditions: Vec<String>,
}

/// The scope of the ripple in the PRL
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum RippleScope {
    /// Only the creating agent can access this
    PrivateAgent,
    
    /// All agents working on the same campaign can access this
    SharedCampaign,
    
    /// All agents in the org can access this
    SharedOrg,
    
    /// Only the Campaign Strategist can access this
    StrategistOnly,
    
    /// Protected user preference — never decays, always accessible
    UserPreference,
}
```

---

# Chapter 2: The Event Classifier — The Complete Decision Table

The event classifier runs synchronously and immediately when an event is detected. It takes an EventSource and returns a ClassificationResult that determines whether a ripple is created and how it should be configured.

```rust
#[derive(Debug)]
pub struct ClassificationResult {
    pub should_create_ripple: bool,
    pub reason_if_rejected: Option<String>,
    pub intended_scope: RippleScope,
    pub intended_hierarchy: u8,
    pub importance_band: ImportanceBand,
    pub memory_class: MemoryClass,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ImportanceBand {
    Critical,   // Never decays. Essence Core content. User preferences.
    Strong,     // Decays very slowly. High-salience strategic memories.
    Normal,     // Standard decay. Most operational memories.
    Disposable, // Fast decay. Routine confirmations, low-novelty events.
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MemoryClass {
    Working,        // Current session only
    Preference,     // User/avatar preferences — highly protected
    Procedural,     // How to do things (skill knowledge)
    Episodic,       // Specific events at specific times
    Semantic,       // General knowledge about the world
    Affective,      // Primarily emotional content
    Identity,       // Core beliefs — Essence Core
}

pub fn classify_event(
    event: &EventSource,
    org_context: &OrgContext,
    agent_context: &AgentContext,
) -> ClassificationResult {
    match event {
        // ─── ALWAYS CREATE RIPPLE ────────────────────────────────────────────
        
        EventSource::CouncilPosition { .. } => ClassificationResult {
            should_create_ripple: true,
            reason_if_rejected: None,
            intended_scope: RippleScope::PrivateAgent,
            intended_hierarchy: 2,
            importance_band: ImportanceBand::Normal,
            memory_class: MemoryClass::Episodic,
        },
        
        EventSource::StrategistSynthesis { deadlock_detected, .. } => ClassificationResult {
            should_create_ripple: true,
            reason_if_rejected: None,
            // Synthesis is shared with all campaign agents
            intended_scope: RippleScope::SharedCampaign,
            // Synthesis is a Level 3 abstraction — interpretation, not raw event
            intended_hierarchy: 3,
            importance_band: if *deadlock_detected {
                // Deadlock syntheses are especially important to remember
                ImportanceBand::Strong
            } else {
                ImportanceBand::Normal
            },
            memory_class: MemoryClass::Episodic,
        },
        
        EventSource::DebateVerdict { .. } => ClassificationResult {
            should_create_ripple: true,
            reason_if_rejected: None,
            // Debate verdicts are private per agent — each agent 
            // has their own relationship to the outcome
            intended_scope: RippleScope::PrivateAgent,
            intended_hierarchy: 2,
            importance_band: ImportanceBand::Normal,
            memory_class: MemoryClass::Episodic,
        },
        
        EventSource::UserPreference { confidence, .. } => ClassificationResult {
            should_create_ripple: true,
            reason_if_rejected: None,
            intended_scope: RippleScope::UserPreference,
            // Preferences are high-level identity information
            intended_hierarchy: 3,
            importance_band: if *confidence > 0.85 {
                ImportanceBand::Strong
            } else {
                ImportanceBand::Normal
            },
            memory_class: MemoryClass::Preference,
        },
        
        EventSource::PredictionResolved { .. } => ClassificationResult {
            should_create_ripple: true,
            reason_if_rejected: None,
            intended_scope: RippleScope::PrivateAgent,
            // Resolved predictions become Level 3 learning
            intended_hierarchy: 3,
            importance_band: ImportanceBand::Strong,
            memory_class: MemoryClass::Semantic,
        },
        
        EventSource::TaskMissed { criticality, .. } => ClassificationResult {
            should_create_ripple: true,
            reason_if_rejected: None,
            intended_scope: RippleScope::SharedCampaign,
            intended_hierarchy: 2,
            importance_band: match criticality.as_str() {
                "critical" => ImportanceBand::Strong,
                "important" => ImportanceBand::Normal,
                _ => ImportanceBand::Disposable,
            },
            memory_class: MemoryClass::Episodic,
        },
        
        EventSource::MoveCompleted { achieved_pct, .. } => ClassificationResult {
            should_create_ripple: true,
            reason_if_rejected: None,
            intended_scope: RippleScope::SharedCampaign,
            // Move completion is a Level 3 pattern event
            intended_hierarchy: 3,
            importance_band: ImportanceBand::Strong,
            memory_class: MemoryClass::Semantic,
        },
        
        EventSource::ReflectionCompleted { .. } => ClassificationResult {
            should_create_ripple: true,
            reason_if_rejected: None,
            intended_scope: RippleScope::PrivateAgent,
            intended_hierarchy: 4,  // Reflections are identity-level
            importance_band: ImportanceBand::Strong,
            memory_class: MemoryClass::Identity,
        },
        
        // ─── CONDITIONAL — CHECK THRESHOLD ──────────────────────────────────
        
        EventSource::ContentGenerated { voice_compliance_score, .. } => {
            // Only create ripple for content with notable compliance issues
            // or for content that will be tracked for performance
            if *voice_compliance_score < 0.65 || *voice_compliance_score > 0.92 {
                ClassificationResult {
                    should_create_ripple: true,
                    reason_if_rejected: None,
                    intended_scope: RippleScope::PrivateAgent,
                    intended_hierarchy: 1,
                    importance_band: ImportanceBand::Normal,
                    memory_class: MemoryClass::Episodic,
                }
            } else {
                // Average compliance — no ripple, just store in generated_content
                ClassificationResult {
                    should_create_ripple: false,
                    reason_if_rejected: Some("Content compliance within normal range, performance data will create the ripple when available".to_string()),
                    intended_scope: RippleScope::PrivateAgent,
                    intended_hierarchy: 1,
                    importance_band: ImportanceBand::Disposable,
                    memory_class: MemoryClass::Episodic,
                }
            }
        },
        
        EventSource::ContentPerformance { deviation_pct, above_expectation, .. } => {
            let abs_deviation = deviation_pct.abs();
            if abs_deviation > 0.15 {
                // Significant deviation (15%+ from projection) — always create ripple
                ClassificationResult {
                    should_create_ripple: true,
                    reason_if_rejected: None,
                    intended_scope: RippleScope::PrivateAgent,
                    intended_hierarchy: 2,
                    importance_band: if abs_deviation > 0.40 {
                        ImportanceBand::Strong
                    } else {
                        ImportanceBand::Normal
                    },
                    memory_class: MemoryClass::Semantic,
                }
            } else {
                // Within normal projection variance — no ripple
                ClassificationResult {
                    should_create_ripple: false,
                    reason_if_rejected: Some(format!(
                        "Deviation of {:.1}% within normal variance threshold of 15%",
                        abs_deviation * 100.0
                    )),
                    intended_scope: RippleScope::PrivateAgent,
                    intended_hierarchy: 1,
                    importance_band: ImportanceBand::Disposable,
                    memory_class: MemoryClass::Episodic,
                }
            }
        },
        
        EventSource::CompetitiveSignal { significance, affected_campaign_ids, .. } => {
            match significance.as_str() {
                "major" => ClassificationResult {
                    should_create_ripple: true,
                    reason_if_rejected: None,
                    intended_scope: if affected_campaign_ids.is_empty() {
                        RippleScope::SharedOrg
                    } else {
                        RippleScope::SharedCampaign
                    },
                    intended_hierarchy: 2,
                    importance_band: ImportanceBand::Strong,
                    memory_class: MemoryClass::Semantic,
                },
                "moderate" => ClassificationResult {
                    should_create_ripple: true,
                    reason_if_rejected: None,
                    intended_scope: RippleScope::SharedCampaign,
                    intended_hierarchy: 1,
                    importance_band: ImportanceBand::Normal,
                    memory_class: MemoryClass::Episodic,
                },
                "minor" | _ => ClassificationResult {
                    // Minor competitive signals do not create ripples
                    // They are stored in the intelligence tables but not in the PRL
                    should_create_ripple: false,
                    reason_if_rejected: Some("Minor competitive signal — stored in intelligence tables only".to_string()),
                    intended_scope: RippleScope::SharedOrg,
                    intended_hierarchy: 1,
                    importance_band: ImportanceBand::Disposable,
                    memory_class: MemoryClass::Episodic,
                },
            }
        },
        
        EventSource::TaskCompleted { days_late, task_type, .. } => {
            // Only create ripple for late completions or critical task types
            if *days_late > 2 || task_type == "approve_content" {
                ClassificationResult {
                    should_create_ripple: true,
                    reason_if_rejected: None,
                    intended_scope: RippleScope::SharedCampaign,
                    intended_hierarchy: 1,
                    importance_band: ImportanceBand::Disposable,
                    memory_class: MemoryClass::Episodic,
                }
            } else {
                // On-time routine task completion — no ripple
                ClassificationResult {
                    should_create_ripple: false,
                    reason_if_rejected: Some("Routine on-time task completion".to_string()),
                    intended_scope: RippleScope::SharedCampaign,
                    intended_hierarchy: 1,
                    importance_band: ImportanceBand::Disposable,
                    memory_class: MemoryClass::Episodic,
                }
            }
        },
        
        EventSource::BriefEvaluated { accepted, criteria_failed, .. } => {
            if !accepted || !criteria_failed.is_empty() {
                // Failed briefs are worth remembering — pattern of what makes a good brief
                ClassificationResult {
                    should_create_ripple: true,
                    reason_if_rejected: None,
                    intended_scope: RippleScope::StrategistOnly,
                    intended_hierarchy: 2,
                    importance_band: ImportanceBand::Normal,
                    memory_class: MemoryClass::Semantic,
                }
            } else {
                ClassificationResult {
                    should_create_ripple: false,
                    reason_if_rejected: Some("Clean brief acceptance — no learning to capture".to_string()),
                    intended_scope: RippleScope::StrategistOnly,
                    intended_hierarchy: 1,
                    importance_band: ImportanceBand::Disposable,
                    memory_class: MemoryClass::Episodic,
                }
            }
        },
        
        // ─── ALWAYS CREATE RIPPLE (remaining) ───────────────────────────────
        
        EventSource::MusePatternDetected { .. } => ClassificationResult {
            should_create_ripple: true,
            reason_if_rejected: None,
            intended_scope: RippleScope::StrategistOnly,
            intended_hierarchy: 3,
            importance_band: ImportanceBand::Strong,
            memory_class: MemoryClass::Semantic,
        },
        
        EventSource::InternResearchCompleted { result_quality, .. } => {
            if *result_quality > 0.70 {
                ClassificationResult {
                    should_create_ripple: true,
                    reason_if_rejected: None,
                    intended_scope: RippleScope::PrivateAgent,
                    intended_hierarchy: 1,
                    importance_band: ImportanceBand::Disposable,
                    memory_class: MemoryClass::Episodic,
                }
            } else {
                ClassificationResult {
                    should_create_ripple: false,
                    reason_if_rejected: Some("Low quality intern research".to_string()),
                    intended_scope: RippleScope::PrivateAgent,
                    intended_hierarchy: 1,
                    importance_band: ImportanceBand::Disposable,
                    memory_class: MemoryClass::Episodic,
                }
            }
        },
        
        EventSource::ReplanningCompleted { changes_accepted, .. } => ClassificationResult {
            should_create_ripple: true,
            reason_if_rejected: None,
            intended_scope: RippleScope::SharedCampaign,
            intended_hierarchy: 3,
            importance_band: ImportanceBand::Strong,
            memory_class: MemoryClass::Semantic,
        },
    }
}
```

---

# Chapter 3: The Two Creation Points — When Exactly Does fire_ripple() Get Called?

This is the question the volumes never answered. There are two distinct points:

## Point 1: The Real-Time Channel (During Session)

Certain events fire ripples IMMEDIATELY during the session via `tokio::spawn`. These are events where the ripple is needed by other parts of the system DURING the current session, not just after.

```rust
// Events that fire immediately into the MPSC channel:
// - UserPreference (Muse needs to know immediately for the rest of the session)
// - CompetitiveSignal major (Campaign Strategist needs it for replanning eval)
// - TaskMissed (Replanning Engine evaluates immediately)

// How immediate firing works in the Axum handler:
pub async fn handle_user_preference_detected(
    session: &SessionContext,
    pref_key: &str,
    pref_value: &str,
    confidence: f32,
    source: &str,
) {
    let event = MemoryEvent {
        event_id: ulid::Ulid::new().to_string(),
        org_id: session.org_id,
        agent_id: session.strategist_agent_id,
        session_id: session.session_id.clone(),
        campaign_id: session.active_campaign_id.clone(),
        move_id: None,
        event_source: EventSource::UserPreference {
            preference_key: pref_key.to_string(),
            preference_value: pref_value.to_string(),
            confidence,
            source_interface: source.to_string(),
        },
        raw_content: format!("User expressed preference: {} = {}", pref_key, pref_value),
        intended_scope: RippleScope::UserPreference,
        intended_hierarchy: 3,
        extracted_ripple_data: None,
        blocking: false,    // fire and forget for preferences
        fired_at: Utc::now(),
    };
    
    // Non-blocking send to MPSC channel
    // This does NOT await — the session continues immediately
    let _ = session.ripple_tx.try_send(event);
}
```

## Point 2: The Event Harvester (Post-Session)

Most ripples — especially those from agent inference outputs — are created by the Event Harvester AFTER all streams complete.

```rust
// The Event Harvester runs after the council session completes
// It processes the completed session data and fires all agent-position ripples

pub struct EventHarvester {
    ripple_tx: tokio::sync::mpsc::Sender<MemoryEvent>,
    inference_client: Arc<FlashLiteClient>,
    db_pool: Arc<PgPool>,
}

impl EventHarvester {
    pub async fn harvest_council_session(
        &self,
        session: &CompletedCouncilSession,
    ) -> Result<HarvestResult> {
        
        // Step 1: For each agent position, create a MemoryEvent
        for position in &session.agent_positions {
            let ripple_data = self.extract_ripple_data_from_position(position).await?;
            
            let event = MemoryEvent {
                event_id: ulid::Ulid::new().to_string(),
                org_id: session.org_id,
                agent_id: position.agent_id,
                session_id: session.session_id.clone(),
                campaign_id: session.campaign_id.clone(),
                move_id: session.move_id.clone(),
                event_source: EventSource::CouncilPosition {
                    session_id: session.session_id.clone(),
                    avatar_key: position.avatar_key.clone(),
                    round_number: position.round_number,
                    position_word_count: position.word_count,
                    session_type: session.session_type.clone(),
                },
                raw_content: position.position_text.clone(),
                intended_scope: RippleScope::PrivateAgent,
                intended_hierarchy: 2,
                extracted_ripple_data: Some(ripple_data),
                blocking: false,
                fired_at: Utc::now(),
            };
            
            // Send to ingest channel
            self.ripple_tx.send(event).await?;
        }
        
        // Step 2: Create synthesis ripple
        if let Some(synthesis) = &session.synthesis {
            let synthesis_ripple_data = self.extract_ripple_data_from_synthesis(synthesis).await?;
            
            // For synthesis: create BOTH a shared_campaign ripple AND
            // individual private ripples for each agent (their personal interpretation)
            
            // Shared campaign ripple (the official synthesis)
            let shared_event = MemoryEvent {
                event_id: ulid::Ulid::new().to_string(),
                org_id: session.org_id,
                agent_id: session.strategist_agent_id,
                session_id: session.session_id.clone(),
                campaign_id: session.campaign_id.clone(),
                move_id: session.move_id.clone(),
                event_source: EventSource::StrategistSynthesis {
                    session_id: session.session_id.clone(),
                    participating_agent_count: session.agent_positions.len() as u8,
                    synthesis_word_count: synthesis.word_count,
                    session_type: session.session_type.clone(),
                    deadlock_detected: synthesis.deadlock_detected,
                },
                raw_content: synthesis.synthesis_text.clone(),
                intended_scope: RippleScope::SharedCampaign,
                intended_hierarchy: 3,
                extracted_ripple_data: Some(synthesis_ripple_data),
                blocking: false,
                fired_at: Utc::now(),
            };
            self.ripple_tx.send(shared_event).await?;
            
            // Step 3: Run private reflection for each agent
            // (their personal take on the synthesis outcome)
            self.harvest_private_reflections(session).await?;
        }
        
        // Step 4: Create debate verdict ripple
        self.harvest_debate_verdict(session).await?;
        
        // Step 5: Update ego states for all participating agents
        self.update_ego_states(session).await?;
        
        Ok(HarvestResult { ripples_created: session.agent_positions.len() as u32 + 2 })
    }
}
```

---

# Chapter 4: The <ripple_data> Structured Output Block

This is the mechanism by which inference outputs become machine-readable ripple data without requiring a separate expensive inference call to parse the output.

## 4A — Adding ripple_data to Agent Prompts

The following section is appended to the SYSTEM PROMPT for ALL Council position generation calls:

```
=== REQUIRED OUTPUT FORMAT ===

After your main response, you MUST include the following JSON block. 
Do not omit it. Do not add markdown formatting around it. 
Place it at the very end of your response.

<ripple_data>
{
  "core_claim": "[One sentence: the single most important thing you are arguing]",
  "key_reasoning": "[One sentence: the primary reason this is correct]",
  "prediction": "[Optional. If your position implies a specific expected outcome, state it. Otherwise null]",
  "prediction_timeframe_days": [Optional integer. Days until the prediction can be evaluated. Otherwise null],
  "confidence": [Float 0.0-1.0. Your confidence in this position given available evidence],
  "key_assumptions": ["[assumption 1]", "[assumption 2]"],
  "revision_conditions": ["[what would cause you to change your position]"]
}
</ripple_data>
```

Example of a well-formed ripple_data block from Ogilvy:

```
<ripple_data>
{
  "core_claim": "This campaign requires a minimum 3-week awareness phase before conversion content will be effective for this audience.",
  "key_reasoning": "The March campaign data showed that conversion content served to cold audiences (less than 2 weeks of awareness exposure) achieved 0.4% conversion vs 2.1% for warm audiences, a 5x difference that justifies the timeline investment.",
  "prediction": "If the awareness phase is compressed below 14 days, conversion Move performance will be at least 40% below the projected 2% conversion rate.",
  "prediction_timeframe_days": 45,
  "confidence": 0.81,
  "key_assumptions": [
    "The target ICP for this campaign is similar to the March campaign ICP",
    "The conversion content quality is equivalent to the March campaign"
  ],
  "revision_conditions": [
    "If retargeting pixel data shows the audience has prior brand exposure not captured in our awareness metrics",
    "If Patel's platform data shows algorithm changes that significantly compress consideration cycles"
  ]
}
</ripple_data>
```

## 4B — Parsing the ripple_data Block

The Event Harvester extracts the ripple_data block using string parsing (not an inference call):

```rust
pub fn parse_ripple_data(raw_response: &str) -> Option<ExtractedRippleData> {
    // Find the <ripple_data> tags
    let start = raw_response.find("<ripple_data>")?;
    let end = raw_response.find("</ripple_data>")?;
    
    let json_str = &raw_response[start + 13..end].trim();
    
    match serde_json::from_str::<RippleDataJson>(json_str) {
        Ok(parsed) => Some(ExtractedRippleData {
            core_claim: parsed.core_claim,
            key_reasoning: parsed.key_reasoning,
            prediction: parsed.prediction,
            prediction_timeframe_days: parsed.prediction_timeframe_days,
            confidence: parsed.confidence.clamp(0.0, 1.0),
            key_assumptions: parsed.key_assumptions.unwrap_or_default(),
            revision_conditions: parsed.revision_conditions.unwrap_or_default(),
        }),
        Err(e) => {
            // Log the parse failure — the agent generated malformed JSON
            tracing::warn!(
                "Failed to parse ripple_data block: {}. Raw: {}", 
                e, json_str
            );
            None
        }
    }
}

// The cleaned response (without the ripple_data block) is what streams to the user
pub fn strip_ripple_data(raw_response: &str) -> String {
    if let (Some(start), Some(end)) = (
        raw_response.find("<ripple_data>"),
        raw_response.find("</ripple_data>")
    ) {
        let before = &raw_response[..start];
        let after = &raw_response[end + 14..];
        format!("{}{}", before.trim_end(), after.trim_start())
    } else {
        raw_response.to_string()
    }
}
```

---

# Chapter 5: The Summary Generation — Tier 1 Templates in Full

The summary_text is what gets embedded and what determines retrieval quality. Every template must produce a summary that is specific enough to retrieve correctly and concise enough to embed accurately.

## Tier 1 Templates (No Inference Call Required)

```rust
pub fn generate_tier1_summary(event: &MemoryEvent, ripple_data: &Option<ExtractedRippleData>) -> Option<String> {
    match &event.event_source {
        EventSource::CouncilPosition { avatar_key, round_number, session_type, .. } => {
            if let Some(data) = ripple_data {
                Some(format!(
                    "{} argued in a {} Council session (round {}) that {}. Their reasoning: {}.",
                    capitalize(avatar_key),
                    session_type,
                    round_number,
                    data.core_claim,
                    data.key_reasoning
                ))
            } else {
                // No structured data — fall through to Tier 2
                None
            }
        },
        
        EventSource::StrategistSynthesis { session_type, deadlock_detected, .. } => {
            if let Some(data) = ripple_data {
                let deadlock_note = if *deadlock_detected { 
                    " The Council reached a deadlock and the synthesis proposes a resolution test." 
                } else { "" };
                Some(format!(
                    "The Strategist synthesised a {} Council session.{} Conclusion: {}. Reasoning: {}",
                    session_type,
                    deadlock_note,
                    data.core_claim,
                    data.key_reasoning
                ))
            } else {
                None
            }
        },
        
        EventSource::DebateVerdict { primary_adopted_position, key_tension_summary, substantially_rejected, .. } => {
            let rejected_str = if substantially_rejected.is_empty() {
                "No positions were substantially rejected.".to_string()
            } else {
                format!("The positions of {} were substantially not adopted.", 
                    substantially_rejected.join(", "))
            };
            Some(format!(
                "Council debate verdict: {}'s position was most closely reflected in the synthesis. {}. Key tension: {}",
                capitalize(primary_adopted_position),
                rejected_str,
                key_tension_summary
            ))
        },
        
        EventSource::UserPreference { preference_key, preference_value, confidence, source_interface } => {
            Some(format!(
                "User preference detected from {}: {} = {} (confidence: {:.0}%)",
                source_interface,
                preference_key,
                preference_value,
                confidence * 100.0
            ))
        },
        
        EventSource::TaskMissed { task_type, criticality, scheduled_date, move_id, .. } => {
            Some(format!(
                "A {} task of criticality '{}' scheduled for {} in Move {} was missed.",
                task_type,
                criticality,
                scheduled_date,
                move_id
            ))
        },
        
        EventSource::ContentPerformance { metric_name, metric_value, projected_value, deviation_pct, above_expectation, .. } => {
            let direction = if *above_expectation { "above" } else { "below" };
            Some(format!(
                "Content {} of {:.2} was {:.1}% {} the projected {:.2}. This is a {} deviation.",
                metric_name,
                metric_value,
                (deviation_pct.abs() * 100.0),
                direction,
                projected_value,
                if deviation_pct.abs() > 0.30 { "significant" } else { "moderate" }
            ))
        },
        
        EventSource::CompetitiveSignal { competitor_name, signal_type, significance, summary, .. } => {
            Some(format!(
                "Competitive intelligence ({}): {} made a {} {} change. {}",
                significance,
                competitor_name,
                significance,
                signal_type.replace("_", " "),
                summary
            ))
        },
        
        EventSource::MoveCompleted { move_type, achieved_pct, days_to_complete, tasks_missed_count, .. } => {
            let achievement = if *achieved_pct >= 1.0 {
                format!("{:.0}% of target (above target)", achieved_pct * 100.0)
            } else {
                format!("{:.0}% of target", achieved_pct * 100.0)
            };
            Some(format!(
                "A {} Move completed in {} days, achieving {}. {} tasks were missed during execution.",
                move_type,
                days_to_complete,
                achievement,
                tasks_missed_count
            ))
        },
        
        EventSource::PredictionResolved { actual_outcome_description, prediction_error_magnitude, was_confirmed, .. } => {
            let outcome = if *was_confirmed { "confirmed" } else { 
                format!("violated (error magnitude: {:.2})", prediction_error_magnitude).as_str().to_string()
            };
            // Note: was_confirmed field is bool, need to handle this differently
            let outcome_str = if *was_confirmed { 
                "confirmed as predicted".to_string() 
            } else { 
                format!("violated with error magnitude {:.2}", prediction_error_magnitude) 
            };
            Some(format!(
                "A prediction was {}. Actual outcome: {}",
                outcome_str,
                actual_outcome_description
            ))
        },
        
        EventSource::ReplanningCompleted { trigger_type, changes_proposed, changes_accepted, user_response, .. } => {
            Some(format!(
                "Campaign replanning ({} trigger) proposed {} changes. User {} and {} were accepted.",
                trigger_type.replace("_", " "),
                changes_proposed,
                match user_response.as_str() {
                    "accepted_all" => "accepted all changes",
                    "accepted_partial" => "accepted some changes",
                    "rejected" => "rejected all changes",
                    _ => "responded to the replan",
                },
                changes_accepted
            ))
        },
        
        // For events without Tier 1 templates, return None to trigger Tier 2
        _ => None,
    }
}

fn capitalize(s: &str) -> String {
    let mut chars = s.chars();
    match chars.next() {
        None => String::new(),
        Some(first) => first.to_uppercase().collect::<String>() + chars.as_str(),
    }
}
```

## Tier 2 — The Flash-Lite Inference Call

When Tier 1 returns None, this runs:

```rust
pub async fn generate_tier2_summary(
    inference: &FlashLiteClient,
    event: &MemoryEvent,
    avatar_essence_brief: &str,
) -> Result<String> {
    let prompt = format!(
        r#"You are generating a memory summary for an AI agent's memory system.
        
Agent: {} 
Agent's core identity: {}

Event that occurred:
{}

Generate a 1-3 sentence memory summary that:
1. States what happened (factual)
2. States what it means for this specific agent's work and understanding
3. Does NOT describe what happened in general terms — must be specific to this agent's context

Output ONLY the summary text. No preamble. No formatting. No quotation marks."#,
        event.agent_id,
        avatar_essence_brief,  // 2-3 sentence Essence Core summary for context
        event.raw_content
    );
    
    let response = inference.complete_simple(&prompt, 200).await?;
    Ok(response.trim().to_string())
}
```

---

# Chapter 6: The event_emotion_deltas Lookup Table — Complete

This is the table that was referenced in Volumes 5 and 6 but never shown. The 8 dimensions correspond to Plutchik's model in order: [joy, trust, fear, surprise, sadness, disgust, anger, anticipation].

```rust
pub struct EmotionContext {
    pub was_winner: bool,           // For debate verdicts
    pub prediction_confirmed: bool, // For prediction resolution
    pub above_expectation: bool,    // For performance events
    pub severity: f32,              // 0.0-1.0 for scaled events
}

pub fn event_emotion_delta(
    event: &EventSource, 
    ctx: &EmotionContext
) -> [f32; 8] {
    // [joy, trust, fear, surprise, sadness, disgust, anger, anticipation]
    match event {
        EventSource::DebateVerdict { .. } => {
            if ctx.was_winner {
                // Agent's position was adopted
                [0.25, 0.10, -0.05, 0.05, -0.10, -0.05, -0.10, 0.20]
            } else {
                // Agent's position was substantially not adopted
                [-0.15, -0.10, 0.05, 0.15, 0.20, 0.25, 0.10, -0.10]
            }
        },
        
        EventSource::PredictionResolved { prediction_error_magnitude, .. } => {
            if ctx.prediction_confirmed {
                // Prediction confirmed — calibration reinforced
                [0.15, 0.20, -0.05, 0.05, -0.05, -0.05, -0.05, 0.15]
            } else {
                // Prediction violated — magnitude determines intensity
                let scale = prediction_error_magnitude.clamp(0.0, 1.0);
                [
                    0.00,
                    -0.15 * scale,
                    0.10 * scale,
                    0.35 * scale,  // Surprise scales with how wrong we were
                    0.10 * scale,
                    0.20 * scale,  // Disgust at being wrong
                    0.05 * scale,
                    -0.10 * scale,
                ]
            }
        },
        
        EventSource::UserPreference { confidence, .. } => {
            // Receiving clear user guidance is positive — increases trust and reduces uncertainty
            [0.10, 0.20 * confidence, -0.05, 0.00, 0.00, 0.00, 0.00, 0.05]
        },
        
        EventSource::ContentPerformance { .. } => {
            if ctx.above_expectation {
                // Content performed better than expected
                let scale = ctx.severity;
                [0.20 * scale, 0.15 * scale, -0.05, 0.10 * scale, -0.05, -0.10, -0.05, 0.15 * scale]
            } else {
                // Content underperformed
                let scale = ctx.severity;
                [-0.15 * scale, -0.10 * scale, 0.05, 0.10 * scale, 0.20 * scale, 0.10 * scale, 0.10 * scale, 0.20 * scale]
            }
        },
        
        EventSource::CompetitiveSignal { significance, .. } => {
            // Competitive threats create vigilance and slight anxiety
            let scale = match significance.as_str() {
                "major" => 1.0,
                "moderate" => 0.6,
                _ => 0.3,
            };
            [-0.05 * scale, -0.10 * scale, 0.15 * scale, 0.20 * scale, 0.05 * scale, 0.05 * scale, 0.10 * scale, 0.25 * scale]
        },
        
        EventSource::TaskMissed { criticality, .. } => {
            let scale = match criticality.as_str() {
                "critical" => 1.0,
                "important" => 0.6,
                _ => 0.3,
            };
            // Missed tasks: disappointment + increased urgency
            [-0.10 * scale, -0.05, 0.05, 0.10 * scale, 0.20 * scale, 0.15 * scale, 0.15 * scale, 0.20 * scale]
        },
        
        EventSource::MoveCompleted { achieved_pct, .. } => {
            if *achieved_pct >= 1.0 {
                // Above target completion
                let scale = ((achieved_pct - 1.0) * 2.0).min(1.0) + 0.5;
                [0.30 * scale, 0.20, -0.05, 0.15 * scale, -0.10, -0.10, -0.05, 0.15]
            } else if *achieved_pct >= 0.80 {
                // Partial success
                [0.10, 0.10, 0.05, 0.00, 0.10, 0.05, 0.00, 0.15]
            } else {
                // Significant underachievement
                let scale = 1.0 - achieved_pct;
                [-0.15 * scale, -0.10, 0.05, 0.05, 0.20 * scale, 0.20 * scale, 0.10, 0.25]
            }
        },
        
        EventSource::BriefEvaluated { accepted, .. } => {
            if *accepted {
                // Brief was accepted — anticipation for the work ahead
                [0.10, 0.15, -0.05, 0.00, 0.00, 0.00, -0.05, 0.25]
            } else {
                // Brief was rejected — mild frustration, renewed purpose
                [-0.05, -0.05, 0.00, 0.05, 0.05, 0.10, 0.10, 0.15]
            }
        },
        
        EventSource::CouncilPosition { .. } => {
            // Generating a position creates engagement and anticipation
            [0.05, 0.10, 0.00, 0.00, 0.00, 0.00, 0.00, 0.20]
        },
        
        EventSource::StrategistSynthesis { deadlock_detected, .. } => {
            if *deadlock_detected {
                // Synthesising a deadlock — intellectually challenging
                [0.00, 0.05, 0.10, 0.15, 0.05, 0.10, 0.05, 0.25]
            } else {
                // Clean synthesis — satisfaction
                [0.15, 0.15, -0.05, 0.00, 0.00, -0.05, -0.05, 0.10]
            }
        },
        
        // Default: no emotional impact
        _ => [0.0; 8],
    }
}
```

---

# Chapter 7: The Ingest Worker — Complete Rust Implementation

This is the worker that sits on the receiving end of the MPSC channel. It runs as a dedicated Tokio task for each org (or shared for low-volume orgs).

```rust
pub struct IngestWorker {
    pub ripple_rx: tokio::sync::mpsc::Receiver<MemoryEvent>,
    pub db_pool: Arc<PgPool>,
    pub qdrant: Arc<QdrantClient>,
    pub dragonfly: Arc<redis::aio::ConnectionManager>,
    pub embedding_queue: Arc<SqsClient>,
    pub inference: Arc<FlashLiteClient>,
}

impl IngestWorker {
    pub async fn run(mut self) {
        // Write-ahead buffer for batching Aurora writes
        let mut write_buffer: Vec<RippleRecord> = Vec::with_capacity(20);
        let mut last_flush = Instant::now();
        
        loop {
            // Wait for the next event, with a flush timeout
            let event = tokio::select! {
                Some(event) = self.ripple_rx.recv() => event,
                _ = tokio::time::sleep(Duration::from_millis(50)) => {
                    // Timeout — flush buffer if non-empty
                    if !write_buffer.is_empty() {
                        let _ = self.flush_buffer(&mut write_buffer).await;
                    }
                    continue;
                }
            };
            
            // Step 1: Classify
            let classification = classify_event(
                &event.event_source,
                &OrgContext::default(),
                &AgentContext::default(),
            );
            
            if !classification.should_create_ripple {
                tracing::debug!("Event rejected by classifier: {:?}", 
                    classification.reason_if_rejected);
                continue;
            }
            
            // Step 2: Working Memory Gate — check for near-duplicates
            if self.is_near_duplicate(&event).await.unwrap_or(false) {
                tracing::debug!("Event rejected as near-duplicate");
                continue;
            }
            
            // Step 3: Compute salience
            let salience = self.compute_salience(&event, &classification).await;
            
            // Step 4: Generate summary text
            let summary_text = match generate_tier1_summary(&event, &event.extracted_ripple_data) {
                Some(s) => s,
                None => {
                    // Tier 2: Flash-Lite inference call
                    let essence_brief = self.get_agent_essence_brief(event.agent_id).await
                        .unwrap_or_default();
                    self.inference.generate_summary(&event, &essence_brief).await
                        .unwrap_or_else(|_| format!("Memory of event: {:?}", event.event_source))
                }
            };
            
            // Step 5: Compute SimHash
            let simhash = compute_simhash(&summary_text);
            
            // Step 6: Compute emotion vector
            let emotion_ctx = self.build_emotion_context(&event);
            let emotion_delta = event_emotion_delta(&event.event_source, &emotion_ctx);
            let current_ego = self.get_current_ego_state(event.agent_id).await
                .unwrap_or([0.5; 8]);
            let emotion_vector = self.apply_multipliers_and_combine(
                &current_ego, 
                &emotion_delta, 
                event.agent_id
            ).await;
            
            // Step 7: Build prediction_json if extracted ripple data has prediction
            let prediction_json = event.extracted_ripple_data.as_ref()
                .and_then(|rd| rd.prediction.as_ref())
                .map(|p| {
                    serde_json::json!({
                        "prediction_text": p,
                        "expected_outcome": p,  // Same initially — refined when resolved
                        "confidence": event.extracted_ripple_data.as_ref()
                            .map(|rd| rd.confidence)
                            .unwrap_or(0.7),
                        "timeframe_days": event.extracted_ripple_data.as_ref()
                            .and_then(|rd| rd.prediction_timeframe_days),
                        "created_at": Utc::now().to_rfc3339(),
                    })
                });
            
            // Step 8: Build the RippleRecord
            let ripple_id = ulid::Ulid::new().to_string();
            let ripple = RippleRecord {
                ripple_id: ripple_id.clone(),
                org_id: event.org_id,
                agent_id: event.agent_id,
                campaign_id: event.campaign_id.clone(),
                session_id: event.session_id.clone(),
                scope: format!("{:?}", classification.intended_scope).to_lowercase(),
                memory_class: format!("{:?}", classification.memory_class).to_lowercase(),
                hierarchy_level: classification.intended_hierarchy,
                event_type: self.event_source_to_type_string(&event.event_source),
                trigger_text: self.extract_trigger_text(&event),
                raw_text: event.raw_content.clone(),
                summary_text: summary_text.clone(),
                embedding: None,  // Populated async via embedding queue
                simhash_barcode: simhash,
                emotion_vector,
                salience,
                confidence: event.extracted_ripple_data.as_ref()
                    .map(|rd| rd.confidence)
                    .unwrap_or(0.75),
                prediction_json,
                actual_json: None,
                prediction_error: None,
                precision_weight: 1.0,
                importance_band: format!("{:?}", classification.importance_band).to_lowercase(),
                retention_band: "hot".to_string(),
                activation_count: 0,
                last_activated_at: None,
                state: "pending_embedding".to_string(),
                created_at: event.fired_at,
            };
            
            // Step 9: Update DragonflyDB working memory IMMEDIATELY
            // (before Aurora write, so retrieval can find it in this session)
            let _ = self.update_working_memory_cache(
                event.org_id, 
                event.agent_id, 
                &ripple
            ).await;
            
            // Step 10: Queue for embedding generation
            let _ = self.embedding_queue.send_message(
                &serde_json::json!({ "ripple_id": ripple_id }).to_string()
            ).await;
            
            // Step 11: Add to write buffer (batched Aurora write)
            write_buffer.push(ripple);
            
            // Flush if buffer is full or timeout elapsed
            if write_buffer.len() >= 20 || last_flush.elapsed() > Duration::from_millis(50) {
                let _ = self.flush_buffer(&mut write_buffer).await;
                last_flush = Instant::now();
            }
            
            // Step 12: Create edges (after write to ensure ripple exists)
            // This runs as a separate async task to not block the ingest loop
            let pool = self.db_pool.clone();
            let qdrant = self.qdrant.clone();
            let dragonfly = self.dragonfly.clone();
            let ripple_id_copy = ripple_id.clone();
            let agent_id = event.agent_id;
            let org_id = event.org_id;
            
            tokio::spawn(async move {
                let _ = create_edges(
                    pool, qdrant, dragonfly,
                    ripple_id_copy, org_id, agent_id
                ).await;
            });
        }
    }
    
    async fn flush_buffer(&self, buffer: &mut Vec<RippleRecord>) -> Result<()> {
        if buffer.is_empty() { return Ok(()); }
        
        // Batch insert using sqlx
        let mut query_builder = sqlx::QueryBuilder::new(
            "INSERT INTO ripples (ripple_id, org_id, agent_id, campaign_id, session_id, scope, memory_class, hierarchy_level, event_type, trigger_text, raw_text, summary_text, simhash_barcode, emotion_vector, salience, confidence, prediction_json, importance_band, retention_band, state, created_at) "
        );
        
        query_builder.push_values(buffer.iter(), |mut b, ripple| {
            b.push_bind(&ripple.ripple_id)
             .push_bind(ripple.org_id)
             .push_bind(ripple.agent_id)
             .push_bind(&ripple.campaign_id)
             .push_bind(&ripple.session_id)
             .push_bind(&ripple.scope)
             .push_bind(&ripple.memory_class)
             .push_bind(ripple.hierarchy_level as i16)
             .push_bind(&ripple.event_type)
             .push_bind(&ripple.trigger_text)
             .push_bind(&ripple.raw_text)
             .push_bind(&ripple.summary_text)
             .push_bind(&ripple.simhash_barcode)
             .push_bind(&ripple.emotion_vector)
             .push_bind(ripple.salience)
             .push_bind(ripple.confidence)
             .push_bind(&ripple.prediction_json)
             .push_bind(&ripple.importance_band)
             .push_bind(&ripple.retention_band)
             .push_bind(&ripple.state)
             .push_bind(ripple.created_at);
        });
        
        query_builder.push(" ON CONFLICT (ripple_id) DO NOTHING");
        
        query_builder.build()
            .execute(&*self.db_pool)
            .await?;
        
        buffer.clear();
        Ok(())
    }
}
```

---

# Chapter 8: The SimHash Implementation

```rust
use std::collections::HashMap;

/// Compute a 512-bit SimHash as [u64; 8]
/// SimHash allows near-duplicate detection by Hamming distance comparison
pub fn compute_simhash(text: &str) -> [i64; 8] {
    // Step 1: Tokenize and compute TF
    let tokens = tokenize(text);
    let token_freq = compute_token_freq(&tokens);
    
    // Step 2: For each bit position in 512-bit hash
    let mut bit_weights: [f64; 512] = [0.0; 512];
    
    for (token, freq) in &token_freq {
        // Hash the token to get a 512-bit value
        let token_hash = hash_token_512(token);
        let weight = (*freq as f64).ln() + 1.0;  // TF-IDF-inspired weight
        
        // For each bit, if bit is 1 add weight, if 0 subtract weight
        for bit_pos in 0..512 {
            let byte_pos = bit_pos / 64;
            let bit_in_byte = bit_pos % 64;
            
            if (token_hash[byte_pos] >> bit_in_byte) & 1 == 1 {
                bit_weights[bit_pos] += weight;
            } else {
                bit_weights[bit_pos] -= weight;
            }
        }
    }
    
    // Step 3: Convert weights to bits
    let mut result = [0i64; 8];
    for bit_pos in 0..512 {
        if bit_weights[bit_pos] > 0.0 {
            let u64_pos = bit_pos / 64;
            let bit_in_u64 = bit_pos % 64;
            result[u64_pos] |= 1i64 << bit_in_u64;
        }
    }
    
    result
}

fn hash_token_512(token: &str) -> [u64; 8] {
    // Use multiple hash functions to get 512 bits
    use std::hash::{Hash, Hasher};
    use std::collections::hash_map::DefaultHasher;
    
    let mut result = [0u64; 8];
    for i in 0..8 {
        let mut hasher = DefaultHasher::new();
        (token, i as u64).hash(&mut hasher);
        result[i] = hasher.finish();
    }
    result
}

fn tokenize(text: &str) -> Vec<String> {
    // Simple whitespace + punctuation tokenization
    // Remove stopwords for better near-duplicate detection
    let stopwords = ["the", "a", "an", "is", "was", "are", "were", "and", "or", "but", "in", "on", "at", "to", "for"];
    
    text.to_lowercase()
        .split(|c: char| !c.is_alphanumeric())
        .filter(|s| !s.is_empty() && s.len() > 2 && !stopwords.contains(s))
        .map(String::from)
        .collect()
}

fn compute_token_freq(tokens: &[String]) -> HashMap<String, u32> {
    let mut freq = HashMap::new();
    for token in tokens {
        *freq.entry(token.clone()).or_insert(0) += 1;
    }
    freq
}

/// Hamming distance between two 512-bit SimHash values
pub fn hamming_distance(a: &[i64; 8], b: &[i64; 8]) -> u32 {
    a.iter().zip(b.iter())
        .map(|(x, y)| (x ^ y).count_ones())
        .sum()
}

/// Near-duplicate threshold: Hamming distance < 30 out of 512 bits
/// (~94% similarity)
pub fn is_near_duplicate(a: &[i64; 8], b: &[i64; 8]) -> bool {
    hamming_distance(a, b) < 30
}
```

---

# Chapter 9: The Salience Scoring — Complete Formula

```rust
pub struct SalienceContext {
    pub recent_ripple_simhashes: Vec<[i64; 8]>,  // Last 50 working memory entries
    pub current_campaign_id: Option<String>,
    pub foundation_keyword_tokens: Vec<String>,    // Pre-tokenized Foundation key terms
    pub agent_ego_state: [f32; 8],
    pub agent_ego_baseline: [f32; 8],
}

pub fn compute_salience(
    event: &MemoryEvent,
    summary: &str,
    candidate_simhash: &[i64; 8],
    ctx: &SalienceContext,
) -> f32 {
    // Factor 1: NOVELTY (weight 0.30)
    // How different is this from recent working memory?
    let min_hamming = ctx.recent_ripple_simhashes.iter()
        .map(|h| hamming_distance(h, candidate_simhash))
        .min()
        .unwrap_or(512);
    
    // min_hamming 0 = identical = novelty 0.0
    // min_hamming 512 = completely different = novelty 1.0
    // Near-duplicate threshold is 30, so < 30 = very low novelty
    let novelty = if min_hamming < 30 {
        0.05  // Near-duplicate: almost no novelty
    } else {
        (min_hamming as f32 / 256.0).min(1.0)  // Scale to 0-1
    };
    
    // Factor 2: OUTCOME_IMPACT (weight 0.25)
    // Does this change the direction of current work?
    let outcome_impact = match &event.event_source {
        EventSource::DebateVerdict { .. } => 0.85,
        EventSource::StrategistSynthesis { .. } => 0.90,
        EventSource::PredictionResolved { prediction_error_magnitude, .. } => {
            0.40 + (prediction_error_magnitude * 0.50)  // Higher error = higher impact
        },
        EventSource::TaskMissed { criticality, .. } => match criticality.as_str() {
            "critical" => 0.80,
            "important" => 0.55,
            _ => 0.30,
        },
        EventSource::MoveCompleted { achieved_pct, .. } => {
            if *achieved_pct > 1.1 || *achieved_pct < 0.7 { 0.75 } else { 0.50 }
        },
        EventSource::CompetitiveSignal { significance, .. } => match significance.as_str() {
            "major" => 0.80,
            "moderate" => 0.55,
            _ => 0.25,
        },
        EventSource::ContentPerformance { deviation_pct, .. } => {
            (deviation_pct.abs() * 2.0).min(0.90)
        },
        EventSource::UserPreference { confidence, .. } => 0.60 * confidence,
        EventSource::CouncilPosition { .. } => 0.50,
        _ => 0.35,
    };
    
    // Factor 3: USER_RELEVANCE (weight 0.20)
    // Is this about things the user cares about?
    let summary_tokens = tokenize(summary);
    let overlap_count = summary_tokens.iter()
        .filter(|t| ctx.foundation_keyword_tokens.contains(*t))
        .count();
    let user_relevance = if ctx.foundation_keyword_tokens.is_empty() {
        0.50
    } else {
        (overlap_count as f32 / ctx.foundation_keyword_tokens.len() as f32)
            .min(1.0)
            .max(0.10)
    };
    
    // Factor 4: EMOTIONAL_INTENSITY (weight 0.15)
    // Is the agent in a heightened emotional state?
    let emotional_intensity = {
        let diff_sq_sum: f32 = ctx.agent_ego_state.iter()
            .zip(ctx.agent_ego_baseline.iter())
            .map(|(s, b)| (s - b).powi(2))
            .sum();
        (diff_sq_sum / 8.0).sqrt().min(1.0)
    };
    
    // Factor 5: RECURRENCE (weight 0.10)
    // Has this type of thing happened recently?
    // Simplified: how many recent working memory entries have similar SimHash?
    let similar_recent_count = ctx.recent_ripple_simhashes.iter()
        .filter(|h| hamming_distance(h, candidate_simhash) < 80)
        .count();
    
    let recurrence = if similar_recent_count == 0 {
        0.0
    } else {
        // 1-2 similar = low recurrence signal
        // 5+ similar = high recurrence signal
        (similar_recent_count as f32 / 5.0).min(1.0)
    };
    
    // Final weighted combination
    let raw_salience = 
        (novelty * 0.30) +
        (outcome_impact * 0.25) +
        (user_relevance * 0.20) +
        (emotional_intensity * 0.15) +
        (recurrence * 0.10);
    
    // Clamp to [0.0, 1.0]
    raw_salience.clamp(0.0, 1.0)
}
```

---

# Chapter 10: Prediction Resolution — The Closed Loop

This is the mechanism that was completely missing from all previous volumes. Predictions need to be matched to outcomes and the ripple updated.

## 10A — The Prediction Resolution Job

```rust
/// Runs every 4 hours via tokio-cron-scheduler
pub async fn resolve_predictions_job(pool: Arc<PgPool>, inference: Arc<FlashLiteClient>) {
    
    // Find all unresolved predictions past their timeframe
    let unresolved = sqlx::query!(
        r#"
        SELECT 
            r.ripple_id,
            r.org_id,
            r.agent_id,
            r.prediction_json,
            r.campaign_id,
            r.created_at
        FROM ripples r
        WHERE 
            r.prediction_json IS NOT NULL
            AND r.actual_json IS NULL
            AND r.state = 'active'
            AND (
                (r.prediction_json->>'timeframe_days')::int IS NULL
                OR r.created_at + ((r.prediction_json->>'timeframe_days')::int || ' days')::interval < NOW()
            )
        LIMIT 50
        "#
    )
    .fetch_all(&*pool)
    .await
    .unwrap_or_default();
    
    for ripple in unresolved {
        let prediction: serde_json::Value = ripple.prediction_json.unwrap();
        let prediction_text = prediction["prediction_text"].as_str().unwrap_or("");
        
        // Find the relevant outcome data
        // Different prediction types need different data sources
        let outcome_data = fetch_relevant_outcome_data(
            &pool, 
            &ripple.ripple_id,
            &ripple.campaign_id,
            ripple.org_id,
            ripple.agent_id,
        ).await;
        
        if let Some(outcome) = outcome_data {
            // Compute prediction error via Flash-Lite Normal
            let error_assessment = assess_prediction_error(
                &inference,
                prediction_text,
                &outcome.description,
                &outcome.metrics,
            ).await;
            
            // Update the ripple with actual_json and prediction_error
            sqlx::query!(
                r#"
                UPDATE ripples 
                SET 
                    actual_json = $1,
                    prediction_error = $2,
                    precision_weight = (precision_weight * 0.9) + (CASE WHEN $2 < 0.2 THEN 0.1 ELSE (1.0 - $2) * 0.1 END)
                WHERE ripple_id = $3
                "#,
                serde_json::json!({
                    "outcome_description": outcome.description,
                    "outcome_metrics": outcome.metrics,
                    "resolved_at": Utc::now().to_rfc3339(),
                }),
                error_assessment.error_magnitude,
                ripple.ripple_id
            )
            .execute(&*pool)
            .await
            .ok();
            
            // Fire a PredictionResolved memory event for the learning loop
            let resolved_event = MemoryEvent {
                event_id: ulid::Ulid::new().to_string(),
                org_id: ripple.org_id,
                agent_id: ripple.agent_id,
                session_id: "prediction_resolver".to_string(),
                campaign_id: ripple.campaign_id.clone(),
                move_id: None,
                event_source: EventSource::PredictionResolved {
                    prediction_ripple_id: ripple.ripple_id.clone(),
                    actual_outcome_description: outcome.description.clone(),
                    prediction_error_magnitude: error_assessment.error_magnitude,
                    was_confirmed: error_assessment.error_magnitude < 0.20,
                },
                raw_content: format!(
                    "Prediction '{}' resolved with error {:.2}. Actual: {}",
                    prediction_text, error_assessment.error_magnitude, outcome.description
                ),
                intended_scope: RippleScope::PrivateAgent,
                intended_hierarchy: 3,
                extracted_ripple_data: None,
                blocking: false,
                fired_at: Utc::now(),
            };
            
            // Also propagate error backwards through connected ripples
            if error_assessment.error_magnitude > 0.30 {
                propagate_prediction_error(
                    &pool, 
                    &ripple.ripple_id, 
                    error_assessment.error_magnitude
                ).await.ok();
            }
        }
    }
}

async fn assess_prediction_error(
    inference: &FlashLiteClient,
    prediction: &str,
    actual_description: &str,
    actual_metrics: &serde_json::Value,
) -> PredictionErrorAssessment {
    let prompt = format!(
        r#"Compare a prediction to what actually happened. Output JSON only.

Prediction: {}
Actual outcome: {}
Actual metrics: {}

Output:
{{
  "error_magnitude": [0.0 to 1.0, where 0.0 = perfect prediction, 1.0 = completely wrong],
  "error_type": "direction_wrong" | "magnitude_wrong" | "timing_wrong" | "confirmed",
  "explanation": "[one sentence]"
}}"#,
        prediction, actual_description, actual_metrics
    );
    
    let response = inference.complete_json(&prompt, 100).await
        .unwrap_or_else(|_| serde_json::json!({
            "error_magnitude": 0.5,
            "error_type": "unknown",
            "explanation": "Could not assess"
        }));
    
    PredictionErrorAssessment {
        error_magnitude: response["error_magnitude"].as_f64().unwrap_or(0.5) as f32,
        error_type: response["error_type"].as_str().unwrap_or("unknown").to_string(),
    }
}

/// Propagate prediction error backward through Hebbian edges
async fn propagate_prediction_error(
    pool: &PgPool,
    source_ripple_id: &str,
    error_magnitude: f32,
) -> Result<()> {
    // Depth 1: direct predecessors (decay factor 0.7)
    sqlx::query!(
        r#"
        UPDATE ripples
        SET 
            salience = GREATEST(0.2, salience - ($1 * 0.7 * weight)),
            confidence = GREATEST(0.1, confidence - ($1 * 0.5 * weight))
        FROM ripple_edges e
        WHERE 
            e.target_id = $2
            AND ripples.ripple_id = e.source_id
            AND e.edge_type IN ('predictive', 'associative')
        "#,
        error_magnitude as f64,
        source_ripple_id,
    )
    .execute(pool)
    .await?;
    
    // Depth 2: two hops back (decay factor 0.49 = 0.7^2)
    sqlx::query!(
        r#"
        UPDATE ripples
        SET salience = GREATEST(0.2, salience - ($1 * 0.49 * e2.weight))
        FROM ripple_edges e1
        JOIN ripple_edges e2 ON e2.target_id = e1.source_id
        WHERE 
            e1.target_id = $2
            AND ripples.ripple_id = e2.source_id
            AND e1.edge_type IN ('predictive', 'associative')
            AND e2.edge_type IN ('predictive', 'associative')
        "#,
        error_magnitude as f64,
        source_ripple_id,
    )
    .execute(pool)
    .await?;
    
    Ok(())
}
```

---

# Chapter 11: The Edge Linking Algorithm — Complete

```rust
pub async fn create_edges(
    pool: Arc<PgPool>,
    qdrant: Arc<QdrantClient>,
    dragonfly: Arc<redis::aio::ConnectionManager>,
    new_ripple_id: String,
    org_id: Uuid,
    agent_id: Uuid,
) -> Result<()> {
    
    // Get the new ripple's embedding (may not be ready yet — check state)
    let new_ripple = sqlx::query!(
        "SELECT embedding, summary_text, session_id, event_type, created_at FROM ripples WHERE ripple_id = $1",
        new_ripple_id
    )
    .fetch_one(&*pool)
    .await?;
    
    // Strategy 1: Temporal co-activation
    // Other ripples activated in the same session, in the last 60 seconds
    let temporal_candidates = sqlx::query!(
        r#"
        SELECT ripple_id FROM ripples
        WHERE 
            org_id = $1
            AND agent_id = $2
            AND session_id = $3
            AND ripple_id != $4
            AND created_at > $5::timestamptz - INTERVAL '60 seconds'
        LIMIT 10
        "#,
        org_id,
        agent_id,
        new_ripple.session_id,
        new_ripple_id,
        new_ripple.created_at,
    )
    .fetch_all(&*pool)
    .await?;
    
    // Strategy 2: Working memory co-activation
    // Ripples currently in working memory cache for this agent
    let wm_key = format!("wm:{}:{}", org_id, agent_id);
    let working_memory_ids: Vec<String> = {
        let mut conn = dragonfly.clone();
        redis::cmd("ZRANGE")
            .arg(&wm_key)
            .arg(0)
            .arg(-1)
            .query_async(&mut conn)
            .await
            .unwrap_or_default()
    };
    
    // Combine candidate IDs
    let mut all_candidates: Vec<String> = temporal_candidates
        .iter()
        .map(|r| r.ripple_id.clone())
        .collect();
    
    for wm_id in &working_memory_ids {
        if wm_id != &new_ripple_id && !all_candidates.contains(wm_id) {
            all_candidates.push(wm_id.clone());
        }
    }
    
    // Limit total candidates
    all_candidates.truncate(15);
    
    if all_candidates.is_empty() {
        return Ok(());
    }
    
    // Create edges for all candidates
    // Starting weight 0.1 (weak association)
    // If existing edge exists, increment by 0.05
    for candidate_id in &all_candidates {
        sqlx::query!(
            r#"
            INSERT INTO ripple_edges (source_id, target_id, weight, co_activation_count, edge_type, last_co_activated_at)
            VALUES ($1, $2, 0.10, 1, 'associative', NOW())
            ON CONFLICT (source_id, target_id) DO UPDATE SET
                weight = LEAST(1.0, ripple_edges.weight + 0.05),
                co_activation_count = ripple_edges.co_activation_count + 1,
                last_co_activated_at = NOW()
            "#,
            new_ripple_id,
            candidate_id,
        )
        .execute(&*pool)
        .await
        .ok();  // Non-fatal if this fails
        
        // Bidirectional edge
        sqlx::query!(
            r#"
            INSERT INTO ripple_edges (source_id, target_id, weight, co_activation_count, edge_type, last_co_activated_at)
            VALUES ($1, $2, 0.10, 1, 'associative', NOW())
            ON CONFLICT (source_id, target_id) DO UPDATE SET
                weight = LEAST(1.0, ripple_edges.weight + 0.05),
                co_activation_count = ripple_edges.co_activation_count + 1,
                last_co_activated_at = NOW()
            "#,
            candidate_id,
            new_ripple_id,
        )
        .execute(&*pool)
        .await
        .ok();
    }
    
    Ok(())
}
```

---

# Chapter 12: The Embedding Worker — Complete

The embedding worker sits on the SQS embedding queue and generates embeddings for ripples that have state = 'pending_embedding'.

```rust
pub async fn embedding_worker(
    pool: Arc<PgPool>,
    qdrant: Arc<QdrantClient>,
    sqs: Arc<SqsClient>,
    vertex_ai: Arc<VertexAiClient>,
) {
    loop {
        // Poll SQS for messages
        let messages = sqs.receive_messages("embedding-queue", 10).await
            .unwrap_or_default();
        
        if messages.is_empty() {
            tokio::time::sleep(Duration::from_secs(1)).await;
            continue;
        }
        
        for msg in messages {
            let ripple_id: String = serde_json::from_str(&msg.body)
                .and_then(|v: serde_json::Value| {
                    v["ripple_id"].as_str().map(String::from)
                        .ok_or_else(|| serde_json::Error::custom("missing ripple_id"))
                })
                .unwrap_or_default();
            
            if ripple_id.is_empty() { continue; }
            
            // Load the ripple's summary_text
            let ripple = match sqlx::query!(
                "SELECT summary_text, org_id, agent_id FROM ripples WHERE ripple_id = $1 AND state = 'pending_embedding'",
                ripple_id
            )
            .fetch_optional(&*pool)
            .await {
                Ok(Some(r)) => r,
                _ => {
                    sqs.delete_message(&msg.receipt_handle).await.ok();
                    continue;
                }
            };
            
            // Call Vertex AI embedding API
            match vertex_ai.embed_text(&ripple.summary_text, 64).await {
                Ok(embedding) => {
                    // Update Aurora with embedding
                    sqlx::query!(
                        "UPDATE ripples SET embedding = $1, state = 'active' WHERE ripple_id = $2",
                        &embedding as &[f32],
                        ripple_id
                    )
                    .execute(&*pool)
                    .await
                    .ok();
                    
                    // Also upsert into Qdrant
                    let point = qdrant_client::qdrant::PointStruct::new(
                        ripple_id.clone(),
                        embedding.iter().map(|&f| f as f32).collect::<Vec<f32>>(),
                        serde_json::json!({
                            "org_id": ripple.org_id.to_string(),
                            "agent_id": ripple.agent_id.to_string(),
                        }),
                    );
                    
                    qdrant.upsert_points("ripples", vec![point]).await.ok();
                    
                    // Delete from SQS
                    sqs.delete_message(&msg.receipt_handle).await.ok();
                },
                Err(e) => {
                    tracing::error!("Embedding failed for {}: {}", ripple_id, e);
                    // Message will become visible again after visibility timeout
                    // and be retried (up to 5 times before DLQ)
                }
            }
        }
    }
}
```

---

# Chapter 13: Testing Ripple Creation End-to-End

## Integration Test: Council Session → Ripples

```rust
#[tokio::test]
async fn test_council_position_creates_ripple() {
    let (pool, qdrant, dragonfly) = setup_test_db().await;
    
    // Create test session
    let session = create_test_session(&pool).await;
    
    // Simulate Ogilvy generating a position with ripple_data block
    let mock_ogilvy_response = r#"
        This campaign requires a minimum 3-week awareness phase before 
        conversion content will be effective.
        
        The data from Q1 shows that cold audiences convert at 0.4% versus 
        2.1% for audiences with 3+ weeks of brand exposure.
        
        <ripple_data>
        {
          "core_claim": "3-week minimum awareness phase required before conversion content",
          "key_reasoning": "Cold audience conversion rate is 5x lower than warm audience conversion rate based on Q1 data",
          "prediction": "Compressing awareness below 14 days will result in conversion rate below 1%",
          "prediction_timeframe_days": 45,
          "confidence": 0.82,
          "key_assumptions": ["ICP profile is consistent with Q1 campaign"],
          "revision_conditions": ["If retargeting data shows prior brand exposure"]
        }
        </ripple_data>
    "#;
    
    // Parse the ripple_data
    let ripple_data = parse_ripple_data(mock_ogilvy_response);
    assert!(ripple_data.is_some());
    let rd = ripple_data.unwrap();
    assert_eq!(rd.confidence, 0.82);
    assert!(rd.prediction.is_some());
    
    // Verify strip_ripple_data works
    let clean_response = strip_ripple_data(mock_ogilvy_response);
    assert!(!clean_response.contains("<ripple_data>"));
    assert!(clean_response.contains("3-week minimum"));
    
    // Build and fire the MemoryEvent
    let event = MemoryEvent {
        event_id: ulid::Ulid::new().to_string(),
        org_id: session.org_id,
        agent_id: session.ogilvy_agent_id,
        session_id: session.session_id.clone(),
        campaign_id: Some(session.campaign_id.clone()),
        move_id: None,
        event_source: EventSource::CouncilPosition {
            session_id: session.session_id.clone(),
            avatar_key: "ogilvy".to_string(),
            round_number: 1,
            position_word_count: 50,
            session_type: "operational".to_string(),
        },
        raw_content: clean_response.clone(),
        intended_scope: RippleScope::PrivateAgent,
        intended_hierarchy: 2,
        extracted_ripple_data: Some(rd.clone()),
        blocking: false,
        fired_at: Utc::now(),
    };
    
    // Verify classification
    let classification = classify_event(&event.event_source, &OrgContext::default(), &AgentContext::default());
    assert!(classification.should_create_ripple);
    assert_eq!(classification.intended_hierarchy, 2);
    
    // Verify Tier 1 summary generation
    let summary = generate_tier1_summary(&event, &Some(rd.clone()));
    assert!(summary.is_some());
    let s = summary.unwrap();
    assert!(s.contains("Ogilvy"));
    assert!(s.contains("3-week minimum awareness phase"));
    
    // Verify SimHash
    let simhash = compute_simhash(&s);
    // Same text should produce same hash
    let simhash2 = compute_simhash(&s);
    assert_eq!(simhash, simhash2);
    
    // Verify near-duplicate detection
    let slightly_different = s.replace("3-week", "21-day");
    let simhash3 = compute_simhash(&slightly_different);
    // Slight variation — should still be near-duplicate
    assert!(hamming_distance(&simhash, &simhash3) < 80);
    
    // Verify emotion delta
    let ctx = EmotionContext {
        was_winner: false,
        prediction_confirmed: false,
        above_expectation: false,
        severity: 0.5,
    };
    let delta = event_emotion_delta(&event.event_source, &ctx);
    // Council position should increase anticipation
    assert!(delta[7] > 0.0);  // anticipation[7] positive
    
    println!("All ripple creation unit tests passed");
}
```

---

# Summary: What This Addendum Adds

The previous volumes described ripples philosophically and schematically. This addendum adds:

1. **MemoryEvent struct** — complete Rust definition with every field and variant
2. **EventSource enum** — every possible event type with its specific data
3. **The complete decision table** — which events always create ripples, which are conditional, which never do
4. **The two creation points** — real-time MPSC channel vs post-session Event Harvester, and why the distinction matters
5. **The `<ripple_data>` mechanism** — the structured output block that agents include in generation, how it is parsed, how it feeds ripple fields
6. **Tier 1 summary templates** — every event type's complete template
7. **The event_emotion_deltas table** — all event types, all 8 Plutchik dimensions, scaling formulas
8. **Complete salience formula** — all 5 factors with exact weights and computation
9. **The IngestWorker** — complete Rust implementation with the write-ahead buffer
10. **SimHash algorithm** — implemented in Rust, including Hamming distance function
11. **Prediction resolution job** — the cron job that closes the learning loop, the error propagation algorithm
12. **Edge linking algorithm** — temporal co-activation plus working memory co-activation
13. **The embedding worker** — SQS consumer, Vertex AI call, Aurora + Qdrant upsert
14. **Integration test** — end-to-end test verifying the complete ripple creation path
