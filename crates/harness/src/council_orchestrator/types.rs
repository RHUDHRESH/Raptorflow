use super::*;
pub struct CouncilRunRequest {
    pub org_id: Uuid,
    pub request_summary: String,
    pub context_summary: String,
    pub mode: String,
    pub requested_avatar_keys: Vec<String>,
    pub max_challenge_rounds: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CouncilRunResult {
    pub council_run_id: String,
    pub harness_run_id: Option<String>,
    pub status: String,
    pub avatar_roster: Vec<String>,
    pub presence_states: Vec<AvatarPresenceStateOutput>,
    pub debate_events: Vec<AvatarDebateEvent>,
    pub synthesis: serde_json::Value,
    pub turns: Vec<CouncilTurnOutput>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AvatarPresenceStateOutput {
    pub presence_id: String,
    pub avatar_key: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CouncilTurnOutput {
    pub turn_id: String,
    pub avatar_key: String,
    pub turn_type: String,
    pub sequence_number: i32,
    pub status: String,
    pub instinct_frame: Option<DerivedInstinctFrame>,
    pub debate_event: Option<AvatarDebateEvent>,
}

#[derive(Debug)]
pub enum CouncilOrchestratorError {
    InvalidRequest(String),
    AvatarNotFound(String),
    DatabaseError(String),
    InternalError(String),
}

impl std::fmt::Display for CouncilOrchestratorError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            CouncilOrchestratorError::InvalidRequest(msg) => write!(f, "Invalid request: {}", msg),
            CouncilOrchestratorError::AvatarNotFound(key) => write!(f, "Avatar not found: {}", key),
            CouncilOrchestratorError::DatabaseError(msg) => write!(f, "Database error: {}", msg),
            CouncilOrchestratorError::InternalError(msg) => write!(f, "Internal error: {}", msg),
        }
    }
}

impl std::error::Error for CouncilOrchestratorError {}

pub(crate) fn generate_id() -> String {
    Uuid::new_v4().to_string()
}

pub fn validate_request(req: &CouncilRunRequest) -> Result<(), CouncilOrchestratorError> {
    if req.request_summary.len() < 10 || req.request_summary.len() > 2000 {
        return Err(CouncilOrchestratorError::InvalidRequest(
            "request_summary must be between 10 and 2000 characters".to_string(),
        ));
    }
    if req.context_summary.len() > 8000 {
        return Err(CouncilOrchestratorError::InvalidRequest(
            "context_summary must be at most 8000 characters".to_string(),
        ));
    }
    if !ALLOWED_MODES.contains(&req.mode.as_str()) {
        return Err(CouncilOrchestratorError::InvalidRequest(format!(
            "mode must be one of: {:?}",
            ALLOWED_MODES
        )));
    }
    if req.max_challenge_rounds > 2 {
        return Err(CouncilOrchestratorError::InvalidRequest(
            "max_challenge_rounds must be 0, 1, or 2".to_string(),
        ));
    }
    for key in &req.requested_avatar_keys {
        if !ALLOWED_AVATAR_KEYS.contains(&key.as_str()) {
            return Err(CouncilOrchestratorError::InvalidRequest(format!(
                "Unknown avatar key: {}. Allowed: {:?}",
                key, ALLOWED_AVATAR_KEYS
            )));
        }
    }
    Ok(())
}

pub(crate) fn resolve_avatar_roster(requested: &[String]) -> Vec<String> {
    if requested.is_empty() {
        DEFAULT_AVATAR_KEYS.iter().map(|s| s.to_string()).collect()
    } else {
        requested.to_vec()
    }
}
