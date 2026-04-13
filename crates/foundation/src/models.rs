use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct FoundationData {
    pub company_info: CompanyInfo,
    pub target_audience: TargetAudience,
    pub value_proposition: ValueProposition,
    pub competitive_positioning: CompetitivePositioning,
    #[serde(flatten)]
    pub extra: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct CompanyInfo {
    pub name: Option<String>,
    pub website: Option<String>,
    pub industry: Option<String>,
    pub stage: Option<String>,
    pub team_size: Option<String>,
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct TargetAudience {
    pub segments: Vec<TargetSegment>,
    pub problems: Vec<String>,
    pub tried_before: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TargetSegment {
    pub name: String,
    pub description: String,
    pub demographics: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ValueProposition {
    pub core_message: Option<String>,
    pub key_benefits: Vec<String>,
    pub proof_points: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct CompetitivePositioning {
    pub direct_competitors: Vec<Competitor>,
    pub differentiation: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Competitor {
    pub name: String,
    pub website: Option<String>,
    pub strengths: Vec<String>,
    pub weaknesses: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateFoundationRequest {
    pub website: Option<String>,
    pub company_name: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateSectionRequest {
    pub section: String,
    pub data: serde_json::Value,
}
