use serde_json::Value;
use std::sync::LazyLock;

macro_rules! load_schema {
    ($path:expr) => {{
        const SCHEMA_STR: &str = include_str!(concat!(
            env!("CARGO_MANIFEST_DIR"), "/../../", $path
        ));
        let schema: Value = serde_json::from_str(SCHEMA_STR)
            .expect(concat!("Invalid JSON schema: ", $path));
        jsonschema::Validator::new(&schema)
            .expect(concat!("Failed to compile schema: ", $path))
    }};
}

static HOOK_SET: LazyLock<jsonschema::Validator> =
    LazyLock::new(|| load_schema!("schemas/content/hook-set.json"));

static ICP_REFINED: LazyLock<jsonschema::Validator> =
    LazyLock::new(|| load_schema!("schemas/content/icp-refined.json"));

static POSITIONING: LazyLock<jsonschema::Validator> =
    LazyLock::new(|| load_schema!("schemas/content/positioning.json"));

static OFFER_DESIGN: LazyLock<jsonschema::Validator> =
    LazyLock::new(|| load_schema!("schemas/content/offer-design.json"));

static CALENDAR_PLAN: LazyLock<jsonschema::Validator> =
    LazyLock::new(|| load_schema!("schemas/content/calendar-plan.json"));

static COUNCIL_SYNTHESIS: LazyLock<jsonschema::Validator> =
    LazyLock::new(|| load_schema!("schemas/content/council-synthesis.json"));

pub fn validate_content(content_type: &str, body: &Value) -> Result<(), Vec<String>> {
    let validator = match content_type {
        "hook_set" => &*HOOK_SET,
        "icp_refined" => &*ICP_REFINED,
        "positioning" => &*POSITIONING,
        "offer_design" => &*OFFER_DESIGN,
        "calendar_plan" => &*CALENDAR_PLAN,
        "council_synthesis" => &*COUNCIL_SYNTHESIS,
        _ => return Ok(()),
    };

    match validator.validate(body) {
        Ok(()) => Ok(()),
        Err(errors) => {
            Err(vec![errors.to_string()])
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_valid_hook_set() {
        let body = json!({
            "hooks": [{"text": "The shortcut most founders take", "type": "hook", "salience": 0.8}],
            "winning_angles": ["founder-led proof"]
        });
        assert!(validate_content("hook_set", &body).is_ok());
    }

    #[test]
    fn test_invalid_hook_set_missing_hooks() {
        let body = json!({});
        assert!(validate_content("hook_set", &body).is_err());
    }

    #[test]
    fn test_invalid_hook_set_empty_hooks() {
        let body = json!({"hooks": [], "winning_angles": []});
        assert!(validate_content("hook_set", &body).is_err());
    }

    #[test]
    fn test_valid_icp() {
        let body = json!({
            "refined_icp": {
                "demographics": {"role": "CTO"},
                "psychographics": {"values": ["efficiency"], "fears": ["lagging"], "aspirations": ["lead"]},
                "pain_points": ["slow onboarding"]
            },
            "confidence": 0.85
        });
        assert!(validate_content("icp_refined", &body).is_ok());
    }

    #[test]
    fn test_valid_positioning() {
        let body = json!({
            "positioning_statements": [
                {"statement": "RaptorFlow helps marketing teams accelerate growth", "variant": "primary"}
            ]
        });
        assert!(validate_content("positioning", &body).is_ok());
    }

    #[test]
    fn test_valid_offer() {
        let body = json!({
            "offer_components": [{"name": "Starter", "description": "Basic marketing platform for small teams"}],
            "value_metrics": ["leads per month"]
        });
        assert!(validate_content("offer_design", &body).is_ok());
    }

    #[test]
    fn test_valid_calendar() {
        let body = json!({
            "calendar": [{"week": 1, "content_type": "blog", "platform": "linkedin", "topic": "AI marketing trends"}],
            "themes": ["AI-first growth"]
        });
        assert!(validate_content("calendar_plan", &body).is_ok());
    }

    #[test]
    fn test_valid_synthesis() {
        let body = json!({
            "decision": "Focus on AI marketing",
            "rationale": "Council determined AI is the highest-leverage opportunity based on competitive analysis.",
            "risks": ["Validation needed"],
            "next_actions": ["Build prototype"]
        });
        assert!(validate_content("council_synthesis", &body).is_ok());
    }

    #[test]
    fn test_unknown_type_passes() {
        assert!(validate_content("unknown", &json!({"any": "thing"})).is_ok());
    }
}
