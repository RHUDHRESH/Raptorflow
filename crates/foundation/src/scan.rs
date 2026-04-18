use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ScanMode {
    Quick,
    Deep,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScanJob {
    pub job_id: String,
    pub org_id: Uuid,
    pub mode: ScanMode,
    pub status: ScanStatus,
    pub progress: f32,
    pub results: Option<serde_json::Value>,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ScanStatus {
    Pending,
    Running,
    Completed,
    Failed,
}

pub struct ScanService;

impl ScanService {
    pub async fn trigger_scan(
        _pool: &raptorflow_db::PgPool,
        org_id: Uuid,
        mode: ScanMode,
    ) -> Result<ScanJob, sqlx::Error> {
        Ok(ScanJob {
            job_id: format!("scan-{}-{}", org_id, uuid::Uuid::new_v4()),
            org_id,
            mode,
            status: ScanStatus::Pending,
            progress: 0.0,
            results: None,
            created_at: chrono::Utc::now(),
        })
    }

    pub async fn get_scan_status(
        _pool: &raptorflow_db::PgPool,
        _job_id: &str,
    ) -> Result<Option<ScanJob>, sqlx::Error> {
        Ok(None)
    }

    pub async fn process_quick_scan(
        _org_id: Uuid,
        _website: &str,
    ) -> Result<serde_json::Value, String> {
        Ok(serde_json::json!({
            "title": serde_json::Value::Null,
            "description": serde_json::Value::Null,
            "industry": serde_json::Value::Null,
            "note": "Quick scan stub - implement with actual scraping logic"
        }))
    }
}
