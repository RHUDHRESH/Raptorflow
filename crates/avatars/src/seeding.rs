use anyhow::Result;
use raptorflow_db::PgPool;
use raptorflow_db::models::FoundationSnapshot;
use tracing::info;
use ulid::Ulid;
use uuid::Uuid;

use crate::templates;

#[derive(Debug, Default)]
pub struct SeedReport {
    pub seeded: Vec<(&'static str, Uuid)>,
}

pub async fn seed_org_avatars(
    pool: &PgPool,
    org_id: Uuid,
    foundation: Option<&FoundationSnapshot>,
) -> Result<SeedReport> {
    let mut tx = pool.begin().await?;
    let mut report = SeedReport::default();

    for tmpl in templates::all() {
        let agent_id = Uuid::new_v4();

        let ego_baseline = tmpl.ego_baseline.to_vec();
        let ego_multipliers = tmpl.ego_multipliers.to_vec();
        let ego_state = ego_baseline.clone();
        let mut essence_core = (tmpl.essence_core)();

        if tmpl.avatar_key == "strategist" {
            if let Some(fs) = foundation {
                essence_core = overlay_strategist_essence(essence_core, fs);
            }
        }

        let skill_atoms = serde_json::to_value((tmpl.initial_skill_atoms)())?;

        sqlx::query(
            r#"
            INSERT INTO agent_essences (
                agent_id, org_id, avatar_key, display_name,
                essence_core, ego_baseline, ego_state, ego_multipliers,
                ego_decay_rate, skill_atoms
            ) VALUES (
                $1, $2, $3, $4,
                $5, $6, $7, $8,
                $9, $10
            )
            ON CONFLICT (org_id, avatar_key) DO NOTHING
            "#,
        )
        .bind(agent_id)
        .bind(org_id)
        .bind(tmpl.avatar_key)
        .bind(tmpl.display_name)
        .bind(&essence_core)
        .bind(&ego_baseline)
        .bind(&ego_state)
        .bind(&ego_multipliers)
        .bind(tmpl.ego_decay_rate)
        .bind(&skill_atoms)
        .execute(&mut *tx)
        .await?;

        for seed in (tmpl.essence_ripples)() {
            let ripple_id = Ulid::new().to_string();
            let emotion_vector = seed.emotion_vector.to_vec();

            sqlx::query(
                r#"
                INSERT INTO ripples (
                    ripple_id, org_id, agent_id,
                    scope, hierarchy_level, memory_class, source,
                    trigger_text, raw_text, summary_text,
                    emotion_vector, salience, confidence, importance_band
                ) VALUES (
                    $1, $2, $3,
                    'private_agent', 4, 'strategic', 'essence_seed',
                    $4, $5, $6,
                    $7, 1.0, 1.0, 'protected'
                )
                ON CONFLICT (ripple_id) DO NOTHING
                "#,
            )
            .bind(&ripple_id)
            .bind(org_id)
            .bind(agent_id)
            .bind(seed.trigger_text)
            .bind(seed.raw_text)
            .bind(seed.summary_text)
            .bind(&emotion_vector)
            .execute(&mut *tx)
            .await?;
        }

        info!(avatar_key = tmpl.avatar_key, %agent_id, "seeded avatar");
        report.seeded.push((tmpl.avatar_key, agent_id));
    }

    tx.commit().await?;
    Ok(report)
}

fn overlay_strategist_essence(
    base_essence: serde_json::Value,
    foundation: &FoundationSnapshot,
) -> serde_json::Value {
    let mut essence = base_essence;

    let company_name = foundation
        .sections
        .get("company_info")
        .and_then(|ci| ci.get("name"))
        .and_then(|v| v.as_str())
        .unwrap_or("the client");

    let industry = foundation
        .sections
        .get("company_info")
        .and_then(|ci| ci.get("industry"))
        .and_then(|v| v.as_str())
        .unwrap_or("their");

    let core_message = foundation
        .sections
        .get("value_proposition")
        .and_then(|vp| vp.get("core_message"))
        .and_then(|v| v.as_str());

    let target_audience = foundation
        .sections
        .get("target_audience")
        .and_then(|ta| ta.get("segments"))
        .and_then(|v| v.as_array())
        .and_then(|arr| arr.first())
        .and_then(|s| s.get("name"))
        .and_then(|v| v.as_str());

    if let Some(arr) = essence
        .get_mut("constitutional_principles")
        .and_then(|v| v.as_array_mut())
    {
        arr.push(serde_json::json!(
            format!(
                "This Strategist serves {} in the {} industry, crafting campaigns that resonate with their specific market context.",
                company_name, industry
            )
        ));
        if let Some(msg) = core_message {
            arr.push(serde_json::json!(format!(
                "The brand's core message is: {}",
                msg
            )));
        }
        if let Some(audience) = target_audience {
            arr.push(serde_json::json!(format!(
                "The primary target audience is: {}",
                audience
            )));
        }
    }

    if let Some(arr) = essence
        .get_mut("core_beliefs")
        .and_then(|v| v.as_array_mut())
    {
        if let Some(audience) = target_audience {
            arr.push(serde_json::json!(format!(
                "Every campaign must speak directly to {} with precision and authenticity.",
                audience
            )));
        }
    }

    essence
}
