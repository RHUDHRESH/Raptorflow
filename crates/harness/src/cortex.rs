//! Cortex — context pack builder for capability execution.
//!
//! The cortex is the **context assembler** that builds bounded prompt/context packs
//! from Foundation, Intel, Campaign, Office, and Ripple data.

#![allow(clippy::manual_clamp, clippy::collapsible_if, clippy::map_clone)]

use raptorflow_db::PgPool;
use raptorflow_db::models::HarnessContextPack;
use raptorflow_db::queries as db;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone)]
pub struct CortexContextRequest {
    pub org_id: Uuid,
    pub avatar_id: Option<String>,
    pub capability_id: Option<String>,
    pub capability_key: Option<String>,
    pub campaign_id: Option<String>,
    pub run_id: Option<String>,
    pub token_budget: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CortexContextPack {
    pub foundation_context: serde_json::Value,
    pub intel_context: serde_json::Value,
    pub campaign_context: serde_json::Value,
    pub office_context: serde_json::Value,
    pub ripple_context: Vec<serde_json::Value>,
    pub search_context: Option<serde_json::Value>,
    pub compressed_context: String,
}

pub struct Cortex;

impl Cortex {
    pub async fn build_context_pack(
        pool: &PgPool,
        req: CortexContextRequest,
    ) -> Result<CortexContextPack, CortexError> {
        let token_budget = req.token_budget.max(1000).min(32000) as i32;

        let foundation_context = Self::load_foundation_context(pool, req.org_id).await?;
        let intel_context = Self::load_intel_context(pool, req.org_id).await?;
        let campaign_context =
            Self::load_campaign_context(pool, req.org_id, &req.campaign_id).await?;
        let office_context = Self::load_office_context(pool, req.org_id).await?;
        let ripple_context = Self::load_ripple_context(pool, req.org_id, token_budget).await?;

        let compressed_context = Self::compress_context(
            &foundation_context,
            &intel_context,
            &campaign_context,
            &office_context,
            &ripple_context,
            token_budget as usize,
        );

        Ok(CortexContextPack {
            foundation_context,
            intel_context,
            campaign_context,
            office_context,
            ripple_context,
            search_context: None,
            compressed_context,
        })
    }

    pub async fn build_and_store_context_pack(
        pool: &PgPool,
        req: CortexContextRequest,
    ) -> Result<(HarnessContextPack, CortexContextPack), CortexError> {
        let token_budget = req.token_budget.max(1000).min(32000) as i32;

        let cortex_pack = Self::build_context_pack(pool, req.clone()).await?;

        let context_pack_id = uuid::Uuid::new_v4().to_string();

        db::create_context_pack(
            pool,
            &context_pack_id,
            req.org_id,
            req.run_id.as_deref(),
            req.capability_id.as_deref(),
            req.avatar_id.as_deref(),
            "capability",
            token_budget,
            &cortex_pack.foundation_context,
            &cortex_pack.intel_context,
            &cortex_pack.campaign_context,
            &cortex_pack.office_context,
            &serde_json::json!(cortex_pack.ripple_context),
            &cortex_pack.compressed_context,
        )
        .await
        .map_err(|e| CortexError::Database(e.to_string()))?;

        let stored = db::get_context_pack(pool, req.org_id, &context_pack_id)
            .await
            .map_err(|e| CortexError::Database(e.to_string()))?
            .ok_or_else(|| CortexError::Storage("Failed to retrieve stored context pack".into()))?;

        Ok((stored, cortex_pack))
    }

    async fn load_foundation_context(
        pool: &PgPool,
        org_id: Uuid,
    ) -> Result<serde_json::Value, CortexError> {
        let snapshots = db::get_foundation_snapshots(pool, org_id)
            .await
            .map_err(|e| CortexError::Database(e.to_string()))?;

        if let Some(snapshot) = snapshots.into_iter().next() {
            Ok(snapshot.sections)
        } else {
            Ok(serde_json::json!({
                "warning": "No foundation snapshot found for org"
            }))
        }
    }

    async fn load_intel_context(
        pool: &PgPool,
        org_id: Uuid,
    ) -> Result<serde_json::Value, CortexError> {
        let competitor = db::get_latest_competitor_snapshot(pool, org_id)
            .await
            .map_err(|e| CortexError::Database(e.to_string()))?;

        Ok(serde_json::json!({
            "competitor_snapshot": competitor.map(|c| serde_json::json!({
                "snapshot_id": c.snapshot_id,
                "competitor_url": c.competitor_url,
                "status": c.status,
                "created_at": c.created_at
            })),
            "note": "Intel signals loaded via research substrate - see /api/v1/intel for details"
        }))
    }

    async fn load_campaign_context(
        pool: &PgPool,
        org_id: Uuid,
        campaign_id: &Option<String>,
    ) -> Result<serde_json::Value, CortexError> {
        match campaign_id {
            Some(cid) => {
                let campaign = db::get_campaign(pool, cid, org_id)
                    .await
                    .map_err(|e| CortexError::Database(e.to_string()))?;

                match campaign {
                    Some(c) => {
                        let moves = db::list_campaign_moves(pool, cid, org_id)
                            .await
                            .map_err(|e| CortexError::Database(e.to_string()))?;
                        Ok(serde_json::json!({
                            "campaign_id": c.campaign_id,
                            "name": c.name,
                            "goal": c.goal,
                            "status": c.status,
                            "moves": moves,
                            "active_move_id": c.active_move_id
                        }))
                    }
                    None => Ok(serde_json::json!({
                        "warning": "Campaign not found",
                        "campaign_id": cid
                    })),
                }
            }
            None => Ok(serde_json::json!({
                "warning": "No campaign_id provided"
            })),
        }
    }

    async fn load_office_context(
        pool: &PgPool,
        org_id: Uuid,
    ) -> Result<serde_json::Value, CortexError> {
        let active_campaigns: (i64,) = sqlx::query_as(
            "SELECT COUNT(*)::bigint FROM campaigns WHERE org_id = $1 AND status IN ('active', 'draft')",
        )
        .bind(org_id)
        .fetch_one(pool)
        .await
        .map_err(|e| CortexError::Database(e.to_string()))?;

        let open_nudges: (i64,) = sqlx::query_as(
            "SELECT COUNT(*)::bigint FROM nudges WHERE org_id = $1 AND suppressed = false AND dismissed_at IS NULL",
        )
        .bind(org_id)
        .fetch_one(pool)
        .await
        .map_err(|e| CortexError::Database(e.to_string()))?;

        Ok(serde_json::json!({
            "active_campaigns": active_campaigns.0,
            "open_nudges": open_nudges.0
        }))
    }

    async fn load_ripple_context(
        pool: &PgPool,
        _org_id: Uuid,
        token_budget: i32,
    ) -> Result<Vec<serde_json::Value>, CortexError> {
        let ripples = db::get_ripples(pool)
            .await
            .map_err(|e| CortexError::Database(e.to_string()))?;

        let mut total_chars = 0i32;
        let max_chars = token_budget / 4;

        let selected: Vec<serde_json::Value> = ripples
            .into_iter()
            .take(20)
            .take_while(|r| {
                let len = r.summary_text.len() as i32;
                if total_chars + len <= max_chars {
                    total_chars += len;
                    true
                } else {
                    false
                }
            })
            .map(|r| {
                serde_json::json!({
                    "ripple_id": r.ripple_id,
                    "summary_text": r.summary_text,
                    "salience": r.salience,
                    "source": r.source,
                    "created_at": r.created_at
                })
            })
            .collect();

        Ok(selected)
    }

    fn compress_context(
        foundation: &serde_json::Value,
        intel: &serde_json::Value,
        campaign: &serde_json::Value,
        office: &serde_json::Value,
        ripples: &[serde_json::Value],
        token_budget: usize,
    ) -> String {
        let mut parts = Vec::new();

        parts.push("## Foundation".to_string());
        if let Some(obj) = foundation.as_object() {
            for (key, val) in obj.iter().take(6) {
                let summary = Self::summarize_value(val);
                parts.push(format!("- {}: {}", key, summary));
            }
        }

        parts.push("\n## Intel".to_string());
        if let Some(obj) = intel.as_object() {
            if let Some(comp) = obj.get("competitor_snapshot") {
                if !comp.is_null() {
                    parts.push("- Competitor snapshot available".to_string());
                }
            }
        }

        parts.push("\n## Campaign".to_string());
        if let Some(obj) = campaign.as_object() {
            if let Some(name) = obj.get("name").and_then(|v| v.as_str()) {
                parts.push(format!("- Name: {}", name));
            }
            if let Some(goal) = obj.get("goal").and_then(|v| v.as_str()) {
                let truncated = if goal.len() > 100 { &goal[..100] } else { goal };
                parts.push(format!("- Goal: {}", truncated));
            }
            if let Some(moves) = obj.get("moves").and_then(|v| v.as_array()) {
                parts.push(format!("- {} moves", moves.len()));
            }
        }

        parts.push("\n## Office".to_string());
        if let Some(obj) = office.as_object() {
            if let Some(campaigns) = obj.get("active_campaigns") {
                parts.push(format!("- Active campaigns: {}", campaigns));
            }
            if let Some(nudges) = obj.get("open_nudges") {
                parts.push(format!("- Open nudges: {}", nudges));
            }
        }

        if !ripples.is_empty() {
            parts.push("\n## Relevant Ripples".to_string());
            for ripple in ripples.iter().take(5) {
                if let Some(summary) = ripple.get("summary_text").and_then(|v| v.as_str()) {
                    let truncated = if summary.len() > 80 {
                        &summary[..80]
                    } else {
                        summary
                    };
                    parts.push(format!("- {}", truncated));
                }
            }
        }

        let result = parts.join("\n");
        let chars_available = token_budget * 4;

        if result.len() > chars_available {
            result[..chars_available].to_string()
        } else {
            result
        }
    }

    fn summarize_value(val: &serde_json::Value) -> String {
        match val {
            serde_json::Value::String(s) => {
                let truncated = if s.len() > 60 { &s[..60] } else { s };
                format!("\"{}\"", truncated)
            }
            serde_json::Value::Array(arr) => format!("[{} items]", arr.len()),
            serde_json::Value::Object(obj) => {
                let keys: Vec<String> = obj.keys().map(|k| k.clone()).take(4).collect();
                format!("{{{}}}", keys.join(", "))
            }
            _ => val.to_string(),
        }
    }
}

#[derive(Debug, thiserror::Error)]
pub enum CortexError {
    #[error("Database error: {0}")]
    Database(String),

    #[error("Capability error: {0}")]
    Capability(String),

    #[error("Storage error: {0}")]
    Storage(String),
}
