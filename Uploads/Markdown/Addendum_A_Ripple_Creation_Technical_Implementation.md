# RAPTORFLOW ADDENDUM A: RIPPLE CREATION — THE COMPLETE TECHNICAL IMPLEMENTATION

This addendum fills the critical gaps identified in RedTeam Audit Hole 1.

---

## 1A — The MemoryEvent Struct (Complete Definition)

```rust
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryEvent {
    pub org_id: Uuid,
    pub agent_id: Uuid,
    pub session_id: String,
    pub campaign_id: Option<String>,
    pub event_source: EventSource,
    pub raw_content: String,
    pub context: EventContext,
    pub timestamp: DateTime<Utc>,
    pub fired_by: FiredBy,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum EventSource {
    CouncilPosition {
        round: u8,
        agent_key: String,
    },
    StrategistSynthesis {
        session_type: String,
    },
    MuseConversation {
        message_id: String,
    },
    ContentGenerated {
        content_type: String,
        content_id: String,
    },
    ContentPerformance {
        content_id: String,
        metric: String,
        value: f64,
    },
    CompetitiveSignal {
        competitor_id: Uuid,
        signal_type: String,
        significance: String,
    },
    UserPreference {
        preference_key: String,
        preference_value: String,
    },
    PredictionResolved {
        prediction_id: String,
        outcome: String,
    },
    TaskCompleted {
        task_id: String,
        task_type: String,
    },
    TaskMissed {
        task_id: String,
        miss_reason: String,
    },
    BriefEvaluated {
        brief_id: String,
        accepted: bool,
    },
    DebateVerdict {
        won_by: String,
        losing_position: String,
    },
    CampaignCreated {
        campaign_id: String,
    },
    MoveCompleted {
        move_id: String,
        outcome: String,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EventContext {
    pub brief_text: Option<String>,
    pub move_id: Option<String>,
    pub task_id: Option<String>,
    pub org_id: Uuid,
    pub user_id: Option<Uuid>,
    pub additional_data: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum FiredBy {
    Agent { agent_id: Uuid, agent_key: String },
    System,
    User { user_id: Uuid },
    ScheduledJob { job_name: String },
}
```

---

## 1B — The Event Classifier Decision Table

The Event Classifier determines which events produce PRL ripples.

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RippleTrigger {
    Always,
    Conditional { threshold: f64 },
    Never,
}

pub struct EventClassifier;

impl EventClassifier {
    pub fn classify(event: &EventSource) -> RippleTrigger {
        match event {
            // ALWAYS → ripple
            EventSource::CouncilPosition { .. } => RippleTrigger::Always,
            EventSource::StrategistSynthesis { .. } => RippleTrigger::Always,
            EventSource::UserPreference { .. } => RippleTrigger::Always,
            EventSource::PredictionResolved { .. } => RippleTrigger::Always,
            EventSource::DebateVerdict { .. } => RippleTrigger::Always,
            EventSource::BriefEvaluated { .. } => RippleTrigger::Always,
            EventSource::MoveCompleted { .. } => RippleTrigger::Always,

            // CONDITIONAL → ripple (only if threshold met)
            EventSource::ContentPerformance { value, .. } => {
                RippleTrigger::Conditional { threshold: 0.15 }
            }
            EventSource::CompetitiveSignal { significance, .. } => {
                match significance.as_str() {
                    "moderate" | "major" => RippleTrigger::Always,
                    _ => RippleTrigger::Never,
                }
            }
            EventSource::TaskCompleted { task_type, .. } => {
                match task_type.as_str() {
                    "critical" => RippleTrigger::Always,
                    _ => RippleTrigger::Conditional { threshold: 0.0 },
                }
            }
            EventSource::TaskMissed { .. } => RippleTrigger::Always,
            EventSource::ContentGenerated { .. } => RippleTrigger::Never,
            EventSource::CampaignCreated { .. } => RippleTrigger::Never,
            EventSource::MuseConversation { .. } => RippleTrigger::Never,
        }
    }

    pub fn should_fire(event: &EventSource, context: &EventContext) -> bool {
        match Self::classify(event) {
            RippleTrigger::Always => true,
            RippleTrigger::Conditional { threshold } => {
                if let EventSource::ContentPerformance { value, .. } = event {
                    let deviation = (value - 1.0).abs();
                    deviation > threshold
                } else {
                    true
                }
            }
            RippleTrigger::Never => false,
        }
    }
}
```

**Decision Table Summary:**

| EventSource         | Trigger     | Condition                       |
| ------------------- | ----------- | ------------------------------- |
| CouncilPosition     | Always      | —                               |
| StrategistSynthesis | Always      | —                               |
| UserPreference      | Always      | —                               |
| PredictionResolved  | Always      | —                               |
| DebateVerdict       | Always      | —                               |
| BriefEvaluated      | Always      | —                               |
| MoveCompleted       | Always      | —                               |
| TaskMissed          | Always      | —                               |
| CompetitiveSignal   | Always      | significance = moderate/major   |
| TaskCompleted       | Always      | task_type = critical            |
| ContentPerformance  | Conditional | deviation > 15% from projection |
| ContentGenerated    | Never       | —                               |
| MuseConversation    | Never       | —                               |
| CampaignCreated     | Never       | —                               |

---

## 1C — The Two Ripple Creation Points

There are TWO distinct ripple creation points that were conflated in Vol 5:

### Point 1 — Real-time (During Session)

Fire immediately via `tokio::spawn` into the MPSC channel:

```rust
// Events that fire in real-time during active sessions
// These use tokio::spawn for fire-and-forget behavior

async fn fire_realtime_ripple(event: MemoryEvent, ingest_tx: mpsc::Sender<MemoryEvent>) {
    let _ = ingest_tx.send(event).await;
}
```

**Real-time events:**

- User preference statements (detected mid-session)
- Mid-session tool results that change direction
- Detected prediction violations during streaming
- Task completion during active campaign execution

### Point 2 — Post-Session (Event Harvester)

Fire during the Event Harvester's processing pass AFTER all streams complete:

```rust
pub struct EventHarvester;

impl EventHarvester {
    pub async fn harvest_session(
        &self,
        session_id: &str,
        db: &DbPool,
    ) -> Result<Vec<MemoryEvent>> {
        let mut events = Vec::new();

        // Agent positions from council_agent_positions table
        let positions = self.fetch_agent_positions(session_id, db).await?;
        for pos in positions {
            events.push(self.position_to_event(pos));
        }

        // Synthesis from council_sessions table
        if let Some(synthesis) = self.fetch_synthesis(session_id, db).await? {
            events.push(self.synthesis_to_event(synthesis));
        }

        // Performance data from campaign_performance_log
        let perf_data = self.fetch_performance_data(session_id, db).await?;
        for perf in perf_data {
            if self.should_ripple_performance(&perf) {
                events.push(self.performance_to_event(perf));
            }
        }

        // Debate verdicts from council_agent_positions round comparisons
        let verdicts = self.compute_debate_verdicts(session_id, db).await?;
        events.extend(verdicts);

        Ok(events)
    }
}
```

**Post-session events:**

- Agent positions (Round 1, Round 2)
- Strategist synthesis
- Performance data comparisons
- Debate verdicts (who won/lost)
- Private reflections

---

## 1D — Structured Output Format for Ripple Data Extraction

Every Council position prompt MUST include this JSON block directive:

```rust
pub const RIPPLE_DATA_INSTRUCTION: &str = r#"End your response with a JSON block:
<ripple_data>
{
  "core_claim": "one sentence stating your primary recommendation",
  "key_reasoning": "one sentence explaining your main justification",
  "prediction": "what specific outcome you expect if your recommendation is followed",
  "confidence": 0.0-1.0,
  "assumption": "the key assumption your recommendation rests on",
  "would_change_if": "the specific evidence or condition that would change your position"
}
</ripple_data>"#;

pub struct RippleDataExtractor;

#[derive(Debug, Deserialize)]
pub struct RippleData {
    pub core_claim: String,
    pub key_reasoning: String,
    pub prediction: String,
    pub confidence: f64,
    pub assumption: String,
    pub would_change_if: String,
}

impl RippleDataExtractor {
    pub fn extract(text: &str) -> Option<RippleData> {
        let start = text.find("<ripple_data>")?;
        let end = text.find("</ripple_data>")?;
        let json_str = &text[start + 14..end];

        serde_json::from_str(json_str).ok()
    }
}
```

**Example Council Position with Ripple Data:**

```
[Full position text discussing campaign strategy...]

<ripple_data>
{
  "core_claim": "Extend Move 2 (Consideration) by 7 days before transitioning to Move 3 (Conversion) to allow sufficient nurture time for leads generated in Move 1.",
  "key_reasoning": "Historical data from similar D2C campaigns shows that leads require 14-21 days of consideration before conversion, and our current Move 2 timeline only provides 10 days.",
  "prediction": "If we proceed on schedule, we expect conversion rates to fall 20-30% below target. With the 7-day extension, we project achieving 95% of conversion target.",
  "confidence": 0.82,
  "assumption": "The manufacturing sector ICP has a 14-21 day consideration cycle as observed in Q4 data.",
  "would_change_if": "Patel's platform data shows that this ICP converts at above-average rates (above 5% within 7 days), which would contradict the consideration timeline assumption."
}
</ripple_data>
```

---

## 1E — The Emotion Vector Computation

```rust
#[derive(Debug, Clone, Copy)]
pub struct EmotionVector([f32; 8]);

impl EmotionVector {
    pub const JOY: usize = 0;
    pub const TRUST: usize = 1;
    pub const FEAR: usize = 2;
    pub const SURPRISE: usize = 3;
    pub const SADNESS: usize = 4;
    pub const DISGUST: usize = 5;
    pub const ANGER: usize = 6;
    pub const ANTICIPATION: usize = 7;

    pub fn zero() -> Self {
        Self([0.0; 8])
    }

    pub fn event_emotion_delta(
        event: &EventSource,
        agent_key: &str,
        prediction_confirmed: bool,
    ) -> Self {
        match event {
            EventSource::DebateVerdict { won_by, .. } => {
                if won_by == agent_key {
                    // Won
                    Self([
                        0.25,  // joy
                        0.10,  // trust
                        -0.05, // fear
                        0.05,  // surprise
                        -0.10, // sadness
                        -0.05, // disgust
                        -0.10, // anger
                        0.20,  // anticipation
                    ])
                } else {
                    // Lost
                    Self([
                        -0.15, // joy
                        -0.10, // trust
                        0.05,  // fear
                        0.15,  // surprise
                        0.20,  // sadness
                        0.25,  // disgust
                        0.10,  // anger
                        -0.10, // anticipation
                    ])
                }
            }
            EventSource::PredictionResolved { .. } => {
                if prediction_confirmed {
                    Self([
                        0.15,  // joy
                        0.20,  // trust
                        -0.05, // fear
                        0.05,  // surprise
                        -0.05, // sadness
                        -0.05, // disgust
                        -0.05, // anger
                        0.15,  // anticipation
                    ])
                } else {
                    Self([
                        0.00,  // joy
                        -0.15, // trust
                        0.10,  // fear
                        0.35,  // surprise
                        0.10,  // sadness
                        0.20,  // disgust
                        0.05,  // anger
                        -0.10, // anticipation
                    ])
                }
            }
            EventSource::UserPreference { .. } => Self([
                0.10,  // joy
                0.20,  // trust
                -0.05, // fear
                0.00,  // surprise
                0.00,  // sadness
                0.00,  // disgust
                0.00,  // anger
                0.05,  // anticipation
            ]),
            EventSource::ContentPerformance { value, .. } => {
                let above = *value > 1.0;
                if above {
                    Self([
                        0.20,  // joy
                        0.15,  // trust
                        -0.05, // fear
                        0.10,  // surprise
                        -0.05, // sadness
                        -0.10, // disgust
                        -0.05, // anger
                        0.15,  // anticipation
                    ])
                } else {
                    Self([
                        -0.15, // joy
                        -0.10, // trust
                        0.05,  // fear
                        0.10,  // surprise
                        0.20,  // sadness
                        0.10,  // disgust
                        0.10,  // anger
                        0.20,  // anticipation
                    ])
                }
            }
            EventSource::CompetitiveSignal { .. } => Self([
                -0.05, // joy
                -0.10, // trust
                0.15,  // fear
                0.20,  // surprise
                0.05,  // sadness
                0.05,  // disgust
                0.10,  // anger
                0.25,  // anticipation
            ]),
            EventSource::BriefEvaluated { accepted, .. } => {
                if *accepted {
                    Self([
                        0.15,  // joy
                        0.10,  // trust
                        -0.05, // fear
                        0.05,  // surprise
                        -0.05, // sadness
                        -0.05, // disgust
                        -0.05, // anger
                        0.10,  // anticipation
                    ])
                } else {
                    Self([
                        -0.05, // joy
                        -0.05, // trust
                        0.05,  // fear
                        0.10,  // surprise
                        0.10,  // sadness
                        0.05,  // disgust
                        0.05,  // anger
                        0.00,  // anticipation
                    ])
                }
            }
            EventSource::MoveCompleted { outcome, .. } => {
                match outcome {
                    "exceeded" => Self([
                        0.30,  // joy
                        0.20,  // trust
                        -0.05, // fear
                        0.10,  // surprise
                        -0.10, // sadness
                        -0.10, // disgust
                        -0.05, // anger
                        0.25,  // anticipation
                    ]),
                    "met" => Self([
                        0.15,  // joy
                        0.15,  // trust
                        0.00,  // fear
                        0.00,  // surprise
                        0.00,  // sadness
                        0.00,  // disgust
                        0.00,  // anger
                        0.10,  // anticipation
                    ]),
                    _ => Self([
                        -0.10, // joy
                        -0.05, // trust
                        0.10,  // fear
                        0.05,  // surprise
                        0.15,  // sadness
                        0.10,  // disgust
                        0.05,  // anger
                        0.05,  // anticipation
                    ]),
                }
            }
            _ => Self::zero(),
        }
    }

    pub fn apply(&mut self, delta: Self) {
        for i in 0..8 {
            self.0[i] = (self.0[i] + delta.0[i]).clamp(-1.0, 1.0);
        }
    }
}
```

---

## 1F — The Complete Ingest Worker Code Flow

```rust
pub struct IngestWorker {
    rx: mpsc::Receiver<MemoryEvent>,
    db: DbPool,
    qdrant: QdrantClient,
    redis: RedisPool,
}

impl IngestWorker {
    pub async fn run(&mut self) -> Result<()> {
        while let Some(event) = self.rx.recv().await {
            if EventClassifier::should_fire(&event.event_source, &event.context) {
                self.process_event(event).await?;
            }
        }
        Ok(())
    }

    async fn process_event(&self, event: MemoryEvent) -> Result<()> {
        let ripple_id = Uuid::new_v4();

        // Step 1: Compute summary text using Tier 1 template
        let summary = self.compute_summary(&event);

        // Step 2: Compute emotion vector delta
        let emotion_delta = EmotionVector::event_emotion_delta(
            &event.event_source,
            &event.fired_by.to_agent_key(),
            event.context.additional_data.get("prediction_confirmed")
                .and_then(|v| v.as_bool())
                .unwrap_or(true),
        );

        // Step 3: Compute embedding via GCP
        let embedding = self.compute_embedding(&summary).await?;

        // Step 4: Store in PostgreSQL
        self.store_ripple_db(&event, &summary, &emotion_delta, ripple_id).await?;

        // Step 5: Store in Qdrant
        self.store_ripple_qdrant(&event, &embedding, ripple_id).await?;

        // Step 6: Update working memory cache in DragonflyDB
        self.update_working_memory(&event, ripple_id).await?;

        // Step 7: Compute SimHash and store for deduplication
        let simhash = self.compute_simhash(&event.raw_content);
        self.check_and_store_simhash(simhash, ripple_id).await?;

        Ok(())
    }

    fn compute_summary(&self, event: &MemoryEvent) -> String {
        match &event.event_source {
            EventSource::CouncilPosition { agent_key, round } => {
                let ripple_data = RippleDataExtractor::extract(&event.raw_content)
                    .unwrap_or(RippleData {
                        core_claim: "Position generated".to_string(),
                        key_reasoning: "No structured data".to_string(),
                        prediction: "Unknown".to_string(),
                        confidence: 0.5,
                        assumption: "None specified".to_string(),
                        would_change_if: "None specified".to_string(),
                    });

                format!(
                    "[{}] argued that {} because {}, predicting that {}.",
                    agent_key,
                    ripple_data.core_claim,
                    ripple_data.key_reasoning,
                    ripple_data.prediction
                )
            }
            EventSource::StrategistSynthesis { .. } => {
                format!(
                    "Strategist synthesis: {}",
                    truncate(&event.raw_content, 200)
                )
            }
            EventSource::TaskMissed { task_id, .. } => {
                format!("Task {} was missed.", task_id)
            }
            EventSource::UserPreference { preference_key, preference_value } => {
                format!(
                    "User preference recorded: {} = {}",
                    preference_key, preference_value
                )
            }
            _ => truncate(&event.raw_content, 200),
        }
    }

    async fn compute_embedding(&self, text: &str) -> Result<Vec<f32>> {
        // GCP Vertex AI embedding API call
        let client = GCPClient::new();
        client.embed(text).await
    }

    fn compute_simhash(&self, text: &str) -> u64 {
        // Simplified SimHash implementation
        // In production, use a proper SimHash crate
        let tokens: Vec<&str> = text.split_whitespace().collect();
        let mut hash = [0u64; 8];

        for (i, token) in tokens.iter().take(64).enumerate() {
            let token_hash = simple_hash(token);
            for j in 0..8 {
                hash[j] ^= if (token_hash >> j) & 1 == 1 { u64::MAX } else { 0 };
            }
        }

        hash.into_iter().fold(0u64, |acc, h| acc.wrapping_add(h))
    }
}

fn simple_hash(text: &str) -> u64 {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    let mut hasher = DefaultHasher::new();
    text.hash(&mut hasher);
    hasher.finish()
}

fn truncate(s: &str, max_len: usize) -> String {
    if s.len() <= max_len {
        s.to_string()
    } else {
        format!("{}...", &s[..max_len.saturating_sub(3)])
    }
}
```

---

## 1G — SimHash Algorithm for Ripple Deduplication

```rust
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

pub struct SimHash {
    dimensions: usize,
}

impl SimHash {
    pub fn new(dimensions: usize) -> Self {
        Self { dimensions })
    }

    pub fn compute(&self, text: &str) -> u64 {
        let tokens = self.tokenize(text);
        let mut v = vec![0i32; 64];

        for token in tokens {
            let hash = self.hash_token(token);
            for i in 0..64 {
                v[i] += if (hash >> i) & 1 == 1 { 1 } else { -1 };
            }
        }

        let mut result = 0u64;
        for (i, val) in v.iter().enumerate() {
            if *val > 0 {
                result |= 1u64 << i;
            }
        }

        result
    }

    fn tokenize(&self, text: &str) -> Vec<String> {
        text.to_lowercase()
            .split(|c: char| !c.is_alphanumeric())
            .filter(|s| s.len() > 2)
            .map(|s| s.to_string())
            .collect()
    }

    fn hash_token(&self, token: &str) -> u64 {
        let mut hasher = DefaultHasher::new();
        token.hash(&mut hasher);
        hasher.finish()
    }

    pub fn hamming_distance(&self, a: u64, b: u64) -> u32 {
        (a ^ b).count_ones()
    }

    pub fn is_similar(&self, a: u64, b: u64, threshold: u32) -> bool {
        self.hamming_distance(a, b) <= threshold
    }
}

#[cfg(test)]
mod tests {
    use super::SimHash;

    #[test]
    fn test_similar_texts() {
        let simhash = SimHash::new(64);
        let h1 = simhash.compute("The quick brown fox jumps");
        let h2 = simhash.compute("The quick brown fox jumped");
        assert!(simhash.hamming_distance(h1, h2) < 5);
    }
}
```

---

## Summary

This addendum provides:

1. **Complete MemoryEvent struct** with all EventSource variants
2. **EventClassifier decision table** with always/conditional/never logic
3. **Two ripple creation points** clearly distinguished (real-time vs post-session)
4. **Structured output format** with RippleData JSON block specification
5. **Emotion vector computation** with complete lookup table for all event types
6. **Ingest worker code flow** in pseudocode/Rust
7. **SimHash algorithm** implementation for deduplication

These specifications complete the implementation gap identified in RedTeam Audit Hole 1.
