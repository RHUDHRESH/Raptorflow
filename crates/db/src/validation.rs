use serde_json::Value;
use std::sync::LazyLock;

macro_rules! load_schema {
    ($path:expr) => {{
        const SCHEMA_STR: &str = include_str!(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/../../schemas/content/",
            $path
        ));
        let schema: Value =
            serde_json::from_str(SCHEMA_STR).expect(concat!("Invalid JSON schema: ", $path));
        jsonschema::Validator::new(&schema).expect(concat!("Failed to compile schema: ", $path))
    }};
}

static COUNCIL_SYNTHESIS: LazyLock<jsonschema::Validator> =
    LazyLock::new(|| load_schema!("council-synthesis.json"));

pub fn validate_council_synthesis(body: &Value) -> Result<(), Vec<String>> {
    match COUNCIL_SYNTHESIS.validate(body) {
        Ok(()) => Ok(()),
        Err(errors) => Err(vec![errors.to_string()]),
    }
}
