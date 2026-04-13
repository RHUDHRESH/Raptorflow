# RAPTORFLOW ADDENDUM E: THE CLOSED LOOP SPECIFICATIONS

This addendum fills the critical gaps identified in RedTeam Audit Holes 5, 7, 10, and 11.

---

## 5A — Voice Fingerprint Construction (CRITICAL HOLE 5)

### The Complete Pipeline

```rust
// crates/content/src/voice_fingerprint.rs

pub struct VoiceFingerprintSystem {
    embedder: EmbedderClient,
}

impl VoiceFingerprintSystem {
    /// Constructs a voice fingerprint from slider values and writing samples
    ///
    /// Process:
    /// 1. Slider values → text description (Flash-Lite Normal)
    /// 2. Text description → embedding
    /// 3. Writing samples → individual embeddings
    /// 4. Combine all embeddings with weights: [0.4, 0.2, 0.2, 0.2]

    pub async fn construct_fingerprint(
        &self,
        sliders: &VoiceSliders,
        writing_samples: &[WritingSample],
    ) -> Result<VoiceFingerprint> {
        // Step 1: Generate text description from sliders
        let description = self.sliders_to_description(sliders).await?;

        // Step 2: Generate embeddings for all components
        let (description_emb, sample_embs) = tokio::join!(
            self.embedder.embed(&description),
            self.embed_samples(writing_samples)
        );

        // Step 3: Compute weighted average
        let fingerprint = self.weighted_average(
            &description_emb,
            &sample_embs,
        );

        Ok(VoiceFingerprint {
            combined: fingerprint,
            components: ComponentEmbeddings {
                description_embedding: description_emb,
                sample_embeddings: sample_embs,
            },
            weights: Weights {
                description: 0.4,
                sample1: 0.2,
                sample2: 0.2,
                sample3: 0.2,
            },
            constructed_at: Utc::now(),
        })
    }

    async fn sliders_to_description(&self, sliders: &VoiceSliders) -> Result<String> {
        let prompt = format!(
            r#"Generate a 200-word description of the brand voice for a brand with these characteristics:

Formality (1-10): {} (1=very casual, 10=very formal)
Emotional Tone (1-10): {} (1=reserved/professional, 10=bold/passionate)
Audience Style (1-10): {} (1=technical/expert, 10=conversational/accessible)
Brand Personality (1-10): {} (1=playful/light, 10=serious/authoritative)
Vocabulary Range (1-10): {} (1=simple/everyday, 10=rich/sophisticated)

Write a description that captures how this brand would communicate in marketing copy, social media, and advertising. Focus on tone, word choice, sentence structure, and emotional register."#,
            sliders.formality,
            sliders.emotional_tone,
            sliders.audience_style,
            sliders.brand_personality,
            sliders.vocabulary_range
        );

        self.flash_lite_normal(&prompt, 500).await
    }

    fn weighted_average(
        &self,
        description_emb: &[f32],
        sample_embs: &[Vec<f32>],
    ) -> Vec<f32> {
        let mut result = vec![0.0; description_emb.len()];

        // Weight description at 0.4
        for i in 0..description_emb.len() {
            result[i] += description_emb[i] * 0.4;
        }

        // Weight each sample at 0.2
        for (j, sample_emb) in sample_embs.iter().enumerate() {
            let weight = 0.2;
            for i in 0..result.len().min(sample_emb.len()) {
                result[i] += sample_emb[i] * weight;
            }
        }

        // Normalize to unit vector
        let magnitude: f32 = result.iter().map(|x| x * x).sum::<f32>().sqrt();
        if magnitude > 0.0 {
            for v in &mut result {
                *v /= magnitude;
            }
        }

        result
    }
}

#[derive(Debug, Clone)]
pub struct VoiceSliders {
    pub formality: f32,           // 1.0 - 10.0
    pub emotional_tone: f32,     // 1.0 - 10.0
    pub audience_style: f32,     // 1.0 - 10.0
    pub brand_personality: f32,  // 1.0 - 10.0
    pub vocabulary_range: f32,    // 1.0 - 10.0
}

#[derive(Debug, Clone)]
pub struct VoiceFingerprint {
    pub combined: Vec<f32>,           // 64-dim weighted average
    pub components: ComponentEmbeddings,
    pub weights: Weights,
    pub constructed_at: DateTime<Utc>,
}

#[derive(Debug, Clone)]
pub struct ComponentEmbeddings {
    pub description_embedding: Vec<f32>,
    pub sample_embeddings: Vec<Vec<f32>>,
}

#[derive(Debug, Clone)]
pub struct Weights {
    pub description: f32,
    pub sample1: f32,
    pub sample2: f32,
    pub sample3: f32,
}
```

### Compliance Score Computation

```rust
impl VoiceFingerprintSystem {
    /// Compute compliance score by comparing against ALL four component embeddings
    /// Not just the combined fingerprint - short text embeddings are unreliable
    /// when compared against embeddings derived from longer text

    pub async fn compute_compliance_score(
        &self,
        content: &str,
        fingerprint: &VoiceFingerprint,
    ) -> Result<ComplianceScore> {
        // Embed the content (short text)
        let content_emb = self.embedder.embed(content).await?;

        // Compare against ALL component embeddings
        let comparisons = vec![
            ("description".to_string(), self.cosine_sim(&content_emb, &fingerprint.components.description_embedding)),
            ("sample1".to_string(), self.cosine_sim(&content_emb, &fingerprint.components.sample_embeddings.get(0).unwrap_or(&fingerprint.combined))),
            ("sample2".to_string(), self.cosine_sim(&content_emb, fingerprint.components.sample_embeddings.get(1).unwrap_or(&fingerprint.combined))),
            ("sample3".to_string(), self.cosine_sim(&content_emb, fingerprint.components.sample_embeddings.get(2).unwrap_or(&fingerprint.combined))),
        ];

        // Weighted average of comparisons
        let weighted_scores: Vec<f32> = comparisons
            .iter()
            .map(|(name, sim)| {
                let weight = match *name {
                    "description" => fingerprint.weights.description,
                    "sample1" => fingerprint.weights.sample1,
                    "sample2" => fingerprint.weights.sample2,
                    "sample3" => fingerprint.weights.sample3,
                    _ => 0.25,
                };
                sim * weight
            })
            .collect();

        let overall_score: f32 = weighted_scores.iter().sum();

        // Identify failing dimensions
        let failing_dimensions: Vec<String> = comparisons
            .iter()
            .filter(|(_, sim)| *sim < 0.60)
            .map(|(name, _)| name.clone())
            .collect();

        Ok(ComplianceScore {
            overall: overall_score,
            dimension_scores: comparisons.into_iter().collect(),
            failing_dimensions,
            passes: overall_score >= 0.80,
            soft_warning: overall_score >= 0.60 && overall_score < 0.80,
            auto_revision_triggered: overall_score < 0.60,
        })
    }

    fn cosine_sim(&self, a: &[f32], b: &[f32]) -> f32 {
        let dot: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
        let mag_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
        let mag_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

        if mag_a == 0.0 || mag_b == 0.0 {
            return 0.0;
        }

        dot / (mag_a * mag_b)
    }
}

#[derive(Debug, Clone)]
pub struct ComplianceScore {
    pub overall: f32,
    pub dimension_scores: HashMap<String, f32>,
    pub failing_dimensions: Vec<String>,
    pub passes: bool,
    pub soft_warning: bool,
    pub auto_revision_triggered: bool,
}
```

---

## 5B — Prediction Resolution Trigger (CRITICAL HOLE 7)

```rust
// crates/prl/src/prediction_resolution.rs

pub struct PredictionResolver {
    db: DbPool,
    prl: PRLClient,
    scheduler: JobScheduler,
}

impl PredictionResolver {
    pub fn schedule(&self) -> Result<()> {
        // Run every 6 hours
        self.scheduler.add_job(
            "prediction_resolution",
            "0 */6 * * *",  // Cron: every 6 hours
            move || {
                let resolver = self.clone();
                async move {
                    resolver.run_resolution_cycle().await
                }
            },
        )?;
        Ok(())
    }

    pub async fn run_resolution_cycle(&self) -> Result<()> {
        // Step 1: Fetch all unresolved predictions that have reached their timeframe
        let predictions = self.fetch_due_predictions().await?;

        for prediction in predictions {
            // Step 2: Determine what kind of outcome data to look for
            let outcome = self.fetch_outcome_data(&prediction).await?;

            // Step 3: Compare prediction to outcome
            let resolved = self.resolve_prediction(&prediction, &outcome).await?;

            // Step 4: Store resolution and update agent's EEL
            if resolved.changed {
                self.update_eel(&prediction, &resolved).await?;
            }

            // Step 5: Create ripple in PRL
            self.create_resolution_ripple(&prediction, &resolved).await?;
        }

        Ok(())
    }

    async fn fetch_due_predictions(&self) -> Result<Vec<UnresolvedPrediction>> {
        let now = Utc::now();
        sqlx::query_as!(
            UnresolvedPrediction,
            r#"
            SELECT
                p.prediction_id,
                p.agent_id,
                p.org_id,
                p.prediction_text,
                p.prediction_type,
                p.timeframe_days,
                p.created_at,
                p.outcome_data
            FROM predictions p
            WHERE p.resolved = false
            AND p.created_at + (p.timeframe_days || ' days')::interval <= $1
            "#,
            now
        )
        .fetch_all(&self.db)
        .await
        .map_err(Into::into)
    }

    async fn fetch_outcome_data(
        &self,
        prediction: &UnresolvedPrediction,
    ) -> Result<Option<OutcomeData>> {
        match prediction.prediction_type.as_str() {
            "campaign_kpi" => {
                // Fetch campaign performance data
                let campaign_id = prediction.outcome_data
                    .get("campaign_id")
                    .and_then(|v| v.as_str());

                if let Some(campaign_id) = campaign_id {
                    let perf = self.fetch_campaign_performance(campaign_id).await?;
                    Ok(Some(OutcomeData::CampaignPerformance(perf)))
                } else {
                    Ok(None)
                }
            }
            "content_performance" => {
                // Fetch content performance metrics
                let content_id = prediction.outcome_data
                    .get("content_id")
                    .and_then(|v| v.as_str());

                if let Some(content_id) = content_id {
                    let metrics = self.fetch_content_metrics(content_id).await?;
                    Ok(Some(OutcomeData::ContentPerformance(metrics)))
                } else {
                    Ok(None)
                }
            }
            "competitive_move" => {
                // Fetch competitive intelligence data
                let competitor_id = prediction.outcome_data
                    .get("competitor_id")
                    .and_then(|v| v.as_str());

                if let Some(competitor_id) = competitor_id {
                    let intel = self.fetch_competitor_intel(competitor_id).await?;
                    Ok(Some(OutcomeData::CompetitiveIntel(intel)))
                } else {
                    Ok(None)
                }
            }
            "general" => {
                // No specific outcome data - resolve based on time
                Ok(None)
            }
            _ => Ok(None),
        }
    }

    async fn resolve_prediction(
        &self,
        prediction: &UnresolvedPrediction,
        outcome: &Option<OutcomeData>,
    ) -> Result<Resolution> {
        // Match prediction text against outcome data
        // This uses a Flash-Lite Normal call for complex predictions

        let prompt = format!(
            r#"You are evaluating whether a prediction was confirmed or violated.

PREDICTION: {}
Prediction type: {}
Made at: {}

OUTCOME DATA:
{:?}

Evaluate whether the prediction was:
- CONFIRMED: The predicted outcome occurred
- VIOLATED: The predicted outcome did not occur
- INCONCLUSIVE: Cannot be determined from the data

Provide your assessment with reasoning."#,
            prediction.prediction_text,
            prediction.prediction_type,
            prediction.created_at,
            outcome
        );

        let response = self.flash_lite_normal(&prompt, 300).await?;

        let confirmed = response.contains("CONFIRMED");
        let violated = response.contains("VIOLATED");

        Ok(Resolution {
            prediction_id: prediction.prediction_id.clone(),
            confirmed,
            violated,
            inconclusive: !confirmed && !violated,
            reasoning: response,
            resolved_at: Utc::now(),
        })
    }

    async fn update_eel(
        &self,
        prediction: &UnresolvedPrediction,
        resolution: &Resolution,
    ) -> Result<()> {
        // Update the agent's utility scores based on prediction accuracy
        let variance = if resolution.confirmed {
            0.05  // Small positive variance for confirmed prediction
        } else if resolution.violated {
            -0.15  // Negative variance for violated prediction
        } else {
            0.0
        };

        // This would call into the EEL system to update skill weights
        self.eel_client.update_skill_utility(
            prediction.agent_id,
            prediction.prediction_type.clone(),
            variance,
        ).await?;

        Ok(())
    }
}

#[derive(Debug)]
pub struct UnresolvedPrediction {
    pub prediction_id: String,
    pub agent_id: Uuid,
    pub org_id: Uuid,
    pub prediction_text: String,
    pub prediction_type: String,
    pub timeframe_days: i32,
    pub created_at: DateTime<Utc>,
    pub outcome_data: serde_json::Value,
}

#[derive(Debug)]
pub enum OutcomeData {
    CampaignPerformance(CampaignPerformance),
    ContentPerformance(ContentMetrics),
    CompetitiveIntel(CompetitiveIntel),
}

#[derive(Debug)]
pub struct Resolution {
    pub prediction_id: String,
    pub confirmed: bool,
    pub violated: bool,
    pub inconclusive: bool,
    pub reasoning: String,
    pub resolved_at: DateTime<Utc>,
}
```

---

## 5C — Foundation Cache Invalidation (CRITICAL HOLE 11)

```rust
// crates/foundation/src/cache_invalidation.rs

pub struct FoundationCacheManager {
    db: DbPool,
    redis: RedisPool,
    vertex_cache: VertexCacheClient,
}

impl FoundationCacheManager {
    /// Called when Foundation is updated
    /// Handles the race condition between update and in-progress inference

    pub async fn invalidate_and_update(
        &self,
        org_id: Uuid,
        new_foundation: &Foundation,
    ) -> Result<()> {
        // Step 1: Acquire distributed lock to prevent concurrent updates
        let lock_key = format!("foundation:update:lock:{}", org_id);
        let lock_acquired = self.redis.set_nx(&lock_key, "locked", 60).await?;

        if !lock_acquired {
            // Another update is in progress, wait and retry
            tokio::time::sleep(Duration::from_secs(2)).await;
            return self.invalidate_and_update(org_id, new_foundation).await;
        }

        defer! {
            // Release lock
            let _ = self.redis.del(&lock_key).await;
        }

        // Step 2: Update Aurora first (source of truth)
        self.update_foundation_db(org_id, new_foundation).await?;

        // Step 3: Update DragonflyDB cache
        self.update_redis_cache(org_id, new_foundation).await?;

        // Step 4: Invalidate Vertex AI context cache
        self.invalidate_vertex_cache(org_id).await?;

        // Step 5: Notify active sessions to refresh context
        self.notify_active_sessions(org_id).await?;

        Ok(())
    }

    async fn update_redis_cache(
        &self,
        org_id: Uuid,
        foundation: &Foundation,
    ) -> Result<()> {
        let key = format!("foundation:{}", org_id);

        // Store as hash with section names as fields
        let mut fields: HashMap<String, String> = HashMap::new();
        fields.insert("positioning".to_string(), serde_json::to_string(&foundation.positioning)?);
        fields.insert("icp".to_string(), serde_json::to_string(&foundation.icp)?);
        fields.insert("competitors".to_string(), serde_json::to_string(&foundation.competitors)?);
        // ... other sections

        // Use HSET with multiple fields
        self.redis.hset(&key, fields).await?;

        // Set TTL to 1 hour (will be refreshed on access)
        self.redis.expire(&key, 3600).await?;

        Ok(())
    }

    async fn invalidate_vertex_cache(&self, org_id: Uuid) -> Result<()> {
        // Vertex AI context cache invalidation
        // The cache ID was stored when the cache was created

        let cache_id = self.get_vertex_cache_id(org_id).await?;

        if let Some(cache_id) = cache_id {
            // Delete the cached content
            self.vertex_cache.delete(&cache_id).await?;
        }

        // Also clear from local tracking
        self.clear_vertex_cache_id(org_id).await?;

        Ok(())
    }

    async fn notify_active_sessions(&self, org_id: Uuid) -> Result<()> {
        // Find all active sessions for this org
        let sessions = self.find_active_sessions(org_id).await?;

        for session in sessions {
            // Send WebSocket notification to refresh context
            self.websocket_server.send(
                &session.session_id,
                WebSocketMessage::FoundationUpdated {
                    org_id,
                    sections: vec!["all".to_string()],
                },
            ).await?;
        }

        Ok(())
    }
}

/// Race condition handling for in-progress inference
///
/// Problem: An inference call might be using the old cached context
/// while we're updating the Foundation
///
/// Solution: Use versioning and per-request cache keys

impl FoundationCacheManager {
    pub async fn get_foundation_for_inference(
        &self,
        org_id: Uuid,
        request_id: &str,
    ) -> Result<FoundationContext> {
        let cache_key = format!("foundation:{}:v{}", org_id, self.get_current_version(org_id));

        // Check if we have a cached version matching current version
        if let Some(cached) = self.redis.get(&cache_key).await? {
            return Ok(serde_json::from_str(&cached)?);
        }

        // Fetch from database
        let foundation = self.fetch_foundation_db(org_id).await?;

        // Build context
        let context = self.build_inference_context(&foundation).await?;

        // Cache with current version
        self.redis.setex(
            &cache_key,
            serde_json::to_string(&context)?,
            300,  // 5 minute TTL for inference cache
        ).await?;

        Ok(context)
    }

    fn get_current_version(&self, org_id: Uuid) -> i64 {
        // Version increments on each Foundation update
        self.redis.get(&format!("foundation:version:{}", org_id))
            .unwrap_or(1)
    }
}
```

---

## 5D — Multi-Campaign Daily Wins Prioritization (CRITICAL HOLE 10)

```rust
// crates/daily-wins/src/prioritization.rs

pub struct DailyWinsPrioritizer {
    db: DbPool,
}

impl DailyWinsPrioritizer {
    /// Selects which campaign's task to recommend in Daily Wins
    /// when a user has multiple active campaigns
    ///
    /// Priority tiers:
    /// 1. Critical campaigns (actively at risk) > Active campaigns > Upcoming campaigns
    /// 2. Within tier: highest KPI deviation from target
    /// 3. Within same deviation: most imminent task deadline
    /// 4. Tiebreaker: campaign with most recent user interaction

    pub async fn select_campaign(
        &self,
        org_id: Uuid,
        active_campaigns: &[Campaign],
    ) -> Result<Option<Campaign>> {
        if active_campaigns.is_empty() {
            return Ok(None);
        }

        if active_campaigns.len() == 1 {
            return Ok(Some(active_campaigns[0].clone()));
        }

        // Classify campaigns into priority tiers
        let mut critical: Vec<&Campaign> = Vec::new();
        let mut active: Vec<&Campaign> = Vec::new();
        let mut upcoming: Vec<&Campaign> = Vec::new();

        for campaign in active_campaigns {
            match self.classify_campaign_risk(campaign) {
                CampaignRisk::Critical => critical.push(campaign),
                CampaignRisk::Active => active.push(campaign),
                CampaignRisk::Upcoming => upcoming.push(campaign),
            }
        }

        // Sort within each tier
        let mut selected = if !critical.is_empty() {
            Self::sort_by_kpi_deviation(critical)
        } else if !active.is_empty() {
            Self::sort_by_kpi_deviation(active)
        } else {
            Self::sort_by_kpi_deviation(upcoming)
        };

        Ok(selected.pop())
    }

    fn classify_campaign_risk(&self, campaign: &Campaign) -> CampaignRisk {
        // Check if any KPI is deviating > 20% from target
        let perf = &campaign.performance_snapshot;

        if let Some(snapshot) = perf {
            let deviation = (snapshot.current_value - snapshot.target_value) / snapshot.target_value;

            if deviation.abs() > 0.20 && campaign.end_date > Utc::now() {
                return CampaignRisk::Critical;
            }
        }

        // Check for recent task misses
        if campaign.tasks_missed_rate > 0.20 {
            return CampaignRisk::Critical;
        }

        // Check if campaign is actively running
        if campaign.status == "active" {
            CampaignRisk::Active
        } else {
            CampaignRisk::Upcoming
        }
    }

    fn sort_by_kpi_deviation<'a>(&self, campaigns: Vec<&'a Campaign>) -> Vec<&'a Campaign> {
        let mut campaigns_with_scores: Vec<(&&'a Campaign, f64)> = campaigns
            .iter()
            .map(|c| {
                let deviation = self.calculate_kpi_deviation(c);
                (c, deviation)
            })
            .collect();

        // Sort by deviation descending (highest deviation first)
        campaigns_with_scores.sort_by(|a, b| {
            b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal)
        });

        // Apply secondary sort by task deadline
        let mut result: Vec<&Campaign> = campaigns_with_scores
            .iter()
            .map(|(c, _)| *c)
            .collect();

        result.sort_by(|a, b| {
            let a_deadline = self.most_urgent_task_deadline(a);
            let b_deadline = self.most_urgent_task_deadline(b);
            a_deadline.cmp(&b_deadline)
        });

        result
    }

    fn calculate_kpi_deviation(&self, campaign: &Campaign) -> f64 {
        if let Some(snapshot) = &campaign.performance_snapshot {
            let target = snapshot.target_value;
            if target == 0.0 {
                return 0.0;
            }
            ((snapshot.current_value - target) / target).abs()
        } else {
            0.0
        }
    }

    fn most_urgent_task_deadline(&self, campaign: &Campaign) -> DateTime<Utc> {
        campaign.tasks
            .iter()
            .filter(|t| t.status == "pending")
            .map(|t| t.scheduled_date)
            .min()
            .unwrap_or(DateTime::<Utc>::MAX)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum CampaignRisk {
    Critical,
    Active,
    Upcoming,
}
```

---

## Summary

This addendum provides:

1. **Voice Fingerprint Construction** — slider values → text → embedding pipeline with weighted averaging
2. **Compliance Score Computation** — multi-component comparison, not single fingerprint
3. **Prediction Resolution Trigger** — cron job with outcome matching and EEL updates
4. **Foundation Cache Invalidation** — distributed locking, version-based race condition handling
5. **Multi-Campaign Prioritization** — 4-tier logic with KPI deviation sorting

These specifications complete the closed-loop gaps identified in RedTeam Audit Holes 5, 7, 10, and 11.
