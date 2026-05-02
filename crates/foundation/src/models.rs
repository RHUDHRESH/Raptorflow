use serde::{Deserialize, Serialize};

// =============================================================================
// Foundation Data — 21-Screen Onboarding Model
// =============================================================================
// The Foundation captures the complete brand setup across all 21 screens:
//  1. URL              8.  Competitors        15. Goals/KPIs
//  2. Identity         9.  Differentiation    16. Keywords/SEO
//  3. Stage           10.  Positioning        17. Assets
//  4. Products        11.  Brand Personality  18. Frustrations
//  5. Problem         12.  Voice Practice     19. Tools
//  6. ICP             13.  Content Territories 20. Reference Brands
//  7. Secondary ICP   14.  Channels          21. Strategist + Calibration
// =============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct FoundationData {
    // ─────────────────────────────────────────────────────────────────────────
    // Legacy fields (for backward compatibility)
    // ─────────────────────────────────────────────────────────────────────────
    pub brand_voice: Option<String>, // Deprecated, use voice_practice instead

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 1: URL
    // ─────────────────────────────────────────────────────────────────────────
    pub company_url: Option<String>,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 2: Identity (company info)
    // ─────────────────────────────────────────────────────────────────────────
    pub company_info: CompanyInfo,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 3: Stage
    // ─────────────────────────────────────────────────────────────────────────
    pub company_stage: Option<String>,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 4: Products
    // ─────────────────────────────────────────────────────────────────────────
    pub product_catalog: ProductCatalog,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 5: Problem
    // ─────────────────────────────────────────────────────────────────────────
    pub problem_statement: Option<String>,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 6: ICP (Primary Ideal Customer Profile)
    // ─────────────────────────────────────────────────────────────────────────
    pub target_audience: TargetAudience,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 7: Secondary ICP
    // ─────────────────────────────────────────────────────────────────────────
    pub secondary_icps: Vec<SecondaryIcp>,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 8: Competitors
    // ─────────────────────────────────────────────────────────────────────────
    pub competitors: Competitors,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 9: Differentiation
    // ─────────────────────────────────────────────────────────────────────────
    pub differentiation: Vec<String>,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 10: Positioning
    // ─────────────────────────────────────────────────────────────────────────
    pub positioning: Positioning,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 11: Brand Personality
    // ─────────────────────────────────────────────────────────────────────────
    pub brand_personality: BrandPersonality,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 12: Voice Practice (5 sliders with live AI examples)
    // ─────────────────────────────────────────────────────────────────────────
    pub voice_practice: VoicePractice,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 13: Content Territories
    // ─────────────────────────────────────────────────────────────────────────
    pub content_territories: Vec<ContentTerritory>,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 14: Channels
    // ─────────────────────────────────────────────────────────────────────────
    pub channels: Channels,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 15: Goals/KPIs
    // ─────────────────────────────────────────────────────────────────────────
    pub goals: Goals,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 16: Keywords/SEO
    // ─────────────────────────────────────────────────────────────────────────
    pub seo_keywords: SeoKeywords,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 17: Assets
    // ─────────────────────────────────────────────────────────────────────────
    pub asset_inventory: AssetInventory,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 18: Frustrations
    // ─────────────────────────────────────────────────────────────────────────
    pub frustrations: Frustrations,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 19: Tools
    // ─────────────────────────────────────────────────────────────────────────
    pub tools: Tools,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 20: Reference Brands
    // ─────────────────────────────────────────────────────────────────────────
    pub reference_brands: Vec<ReferenceBrand>,

    // ─────────────────────────────────────────────────────────────────────────
    // Screen 21: Strategist (Naming + Personality Calibration)
    // ─────────────────────────────────────────────────────────────────────────
    pub strategist: Strategist,

    // ─────────────────────────────────────────────────────────────────────────
    // Additional fields for richer foundation structure
    // ─────────────────────────────────────────────────────────────────────────
    pub brand_voice_sliders: Option<serde_json::Value>,
    pub brand_voice_descriptors: Option<serde_json::Value>,
    pub voice_fingerprint: Option<serde_json::Value>,
    pub writing_samples: Option<serde_json::Value>,
    pub channel_performance: Option<serde_json::Value>,
    pub version: i32,

    // ─────────────────────────────────────────────────────────────────────────
    // Legacy fields (kept for backwards compat)
    // ─────────────────────────────────────────────────────────────────────────
    #[serde(flatten)]
    pub extra: serde_json::Value,
}

impl Default for FoundationData {
    fn default() -> Self {
        Self {
            brand_voice: None,
            company_url: None,
            company_info: CompanyInfo::default(),
            company_stage: None,
            product_catalog: ProductCatalog::default(),
            problem_statement: None,
            target_audience: TargetAudience::default(),
            secondary_icps: Vec::new(),
            competitors: Competitors::default(),
            differentiation: Vec::new(),
            positioning: Positioning::default(),
            brand_personality: BrandPersonality::default(),
            voice_practice: VoicePractice::default(),
            content_territories: Vec::new(),
            channels: Channels::default(),
            goals: Goals::default(),
            seo_keywords: SeoKeywords::default(),
            asset_inventory: AssetInventory::default(),
            frustrations: Frustrations::default(),
            tools: Tools::default(),
            reference_brands: Vec::new(),
            strategist: Strategist::default(),
            brand_voice_sliders: None,
            brand_voice_descriptors: None,
            voice_fingerprint: None,
            writing_samples: None,
            channel_performance: None,
            version: 1,
            extra: serde_json::Value::Object(serde_json::Map::new()),
        }
    }
}

// =============================================================================
// Screen 2: Company Info
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct CompanyInfo {
    pub name: Option<String>,
    pub website: Option<String>,
    pub industry: Option<String>,
    pub stage: Option<String>,
    pub team_size: Option<String>,
    pub description: Option<String>,
    pub legal_name: Option<String>,
    pub year_founded: Option<i32>,
    pub logo_url: Option<String>,
    pub tagline: Option<String>,
}

// =============================================================================
// Screen 4: Product Catalog
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ProductCatalog {
    pub products: Vec<Product>,
    pub primary_product: Option<String>,
    pub pricing_model: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Product {
    pub name: String,
    pub description: Option<String>,
    pub price: Option<String>,
    pub target_segment: Option<String>,
}

// =============================================================================
// Screen 6: Primary ICP (Ideal Customer Profile)
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TargetAudience {
    pub mode: String, // "b2b" or "b2c"
    pub primary_icp: PrimaryIcp,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PrimaryIcp {
    B2B(B2BIcp),
    B2C(B2CIcp),
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct B2BIcp {
    pub name: String,
    pub persona_name: String,
    pub role_identity: String,
    pub reporting_to: Option<String>,
    pub key_goals: Vec<String>,
    pub pressures: Vec<String>,
    pub decision_process: Option<String>,
    pub language_samples: Vec<String>,
    pub pain_points: Vec<String>,
    pub goals: Vec<String>,
    pub demographics: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct B2CIcp {
    pub name: String,
    pub persona_name: String,
    pub life_situation: String,
    pub aspirations: Vec<String>,
    pub behaviors: Vec<String>,
    pub language_samples: Vec<String>,
    pub pain_points: Vec<String>,
    pub goals: Vec<String>,
    pub demographics: serde_json::Value,
}

impl Default for TargetAudience {
    fn default() -> Self {
        Self {
            mode: "b2b".to_string(),
            primary_icp: PrimaryIcp::B2B(B2BIcp::default()),
        }
    }
}

// =============================================================================
// Screen 7: Secondary ICPs
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SecondaryIcp {
    B2B(B2BIcp),
    B2C(B2CIcp),
}

// =============================================================================
// Screen 8: Competitors
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Competitors {
    pub direct: Vec<Competitor>,
    pub indirect: Vec<Competitor>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Competitor {
    pub name: String,
    pub competitor_url: Option<String>,
    pub tracking_enabled: bool,
    pub strengths: Vec<String>,
    pub weaknesses: Vec<String>,
    pub positioning: Option<String>,
}

// =============================================================================
// Screen 10: Positioning
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(default)]
pub struct Positioning {
    // Legacy fields
    pub tagline: Option<String>,
    pub mission: Option<String>,
    pub vision: Option<String>,
    pub core_values: Vec<String>,
    pub unique_value_proposition: Option<String>,

    // Workshop fields
    pub statement: Option<String>,
    pub template_components: Option<TemplateComponents>,
    pub quality_score: Option<f32>,
    pub quality_feedback: Option<String>,
    pub is_locked: bool,
    pub locked_at: Option<String>,
    pub ai_draft: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct TemplateComponents {
    pub for_who: String,
    pub who_problem: String,
    pub brand: String,
    pub category: String,
    pub differentiation: String,
    pub because: String,
}

// =============================================================================
// Screen 11: Brand Personality
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrandPersonality {
    pub traits: Vec<String>,
    pub tone: String,
    pub style: String,
    pub archetype: Option<String>,
}

// =============================================================================
// Screen 12: Voice Practice (5 sliders with live AI examples)
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct VoicePractice {
    pub sliders: BrandVoiceSliders,
    pub writing_samples: Vec<WritingSample>,
    pub voice_fingerprint: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrandVoiceSliders {
    // 1 = one extreme, 10 = the other extreme
    pub formal_informal: u8,         // "Corporate" ↔ "Casual"
    pub serious_playful: u8,         // "Serious" ↔ "Playful"
    pub technical_simple: u8,        // "Technical" ↔ "Simple"
    pub authoritative_collegial: u8, // "Authoritative" ↔ "Collegial"
    pub traditional_innovative: u8,  // "Traditional" ↔ "Innovative"
}

impl BrandVoiceSliders {
    pub fn defaults() -> Self {
        Self {
            formal_informal: 5,
            serious_playful: 5,
            technical_simple: 5,
            authoritative_collegial: 5,
            traditional_innovative: 5,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct WritingSample {
    pub title: String,
    pub content: String,
    pub category: String,
    pub quality_score: Option<f32>,
}

// =============================================================================
// Screen 13: Content Territories
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ContentTerritory {
    pub name: String,
    pub description: String,
    pub priority: u8,
    pub topics: Vec<String>,
    pub content_types: Vec<String>,
}

// =============================================================================
// Screen 14: Channels
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Channels {
    pub primary: Vec<Channel>,
    pub secondary: Vec<Channel>,
    pub content_history: ContentHistory,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Channel {
    pub name: String,
    pub platform: String,
    pub frequency: Option<String>,
    pub audience_size: Option<String>,
    pub url: Option<String>,
    pub is_active: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ContentHistory {
    pub current_output: Option<String>,
    pub satisfaction: Option<String>,
    pub challenges: Vec<String>,
}

// =============================================================================
// Screen 15: Goals/KPIs
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Goals {
    pub primary_goal: Option<String>,
    pub secondary_goals: Vec<String>,
    pub kpis: Vec<Kpi>,
    pub budget: Budget,
    pub timeline: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Kpi {
    pub name: String,
    pub target: String,
    pub current: Option<String>,
    pub metric: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Budget {
    pub monthly: Option<String>,
    pub total: Option<String>,
    pub currency: String,
}

// =============================================================================
// Screen 16: Keywords/SEO
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct SeoKeywords {
    pub primary_keywords: Vec<String>,
    pub secondary_keywords: Vec<String>,
    pub negative_keywords: Vec<String>,
    pub search_volume_data: Option<serde_json::Value>,
    pub competitor_keywords: Option<serde_json::Value>,
}

// =============================================================================
// Screen 17: Assets
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct AssetInventory {
    pub logos: Vec<Asset>,
    pub images: Vec<Asset>,
    pub templates: Vec<Asset>,
    pub documents: Vec<Asset>,
    pub existing_brand_guidelines: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Asset {
    pub name: String,
    pub url: Option<String>,
    pub asset_type: String,
    pub description: Option<String>,
}

// =============================================================================
// Screen 18: Frustrations
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Frustrations {
    pub current_solutions: Vec<String>,
    pub pain_points: Vec<Frustration>,
    pub analytics_tracking: AnalyticsTracking,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Frustration {
    pub description: String,
    pub severity: String,
    pub frequency: String,
    pub impact: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct AnalyticsTracking {
    pub current_tools: Vec<String>,
    pub satisfaction: Option<String>,
    pub gaps: Vec<String>,
}

// =============================================================================
// Screen 19: Tools
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Tools {
    pub crm: Vec<Tool>,
    pub marketing: Vec<Tool>,
    pub analytics: Vec<Tool>,
    pub design: Vec<Tool>,
    pub other: Vec<Tool>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Tool {
    pub name: String,
    pub category: String,
    pub usage: String,
    pub integration_status: Option<String>,
}

// =============================================================================
// Screen 20: Reference Brands
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ReferenceBrand {
    pub name: String,
    pub website: Option<String>,
    pub what_to_imitate: String,
    pub aspects: Vec<String>,
}

// =============================================================================
// Screen 21: Strategist (Naming + Personality Calibration)
// =============================================================================
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Strategist {
    pub name: String,
    pub personality: StrategistPersonality,
    pub calibration_notes: Option<String>,
    pub avatar_seed: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StrategistPersonality {
    pub communication_style: String,
    pub expertise_areas: Vec<String>,
    pub tone_preferences: serde_json::Value,
    pub industry_focus: Vec<String>,
    pub avatar_style: Option<String>,
}

// =============================================================================
// Legacy / Compatibility Models
// =============================================================================

// Deprecated: use TargetAudience instead
#[deprecated(note = "Use TargetAudience")]
pub type ICP = TargetAudience;

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
