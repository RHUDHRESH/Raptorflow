use serde::de::DeserializeOwned;

pub fn strip_json_fence(input: &str) -> &str {
    let trimmed = input.trim();
    if trimmed.starts_with("```json") {
        trimmed
            .strip_prefix("```json")
            .and_then(|s| s.strip_prefix('\n'))
            .unwrap_or(trimmed)
            .strip_suffix("```")
            .unwrap_or(trimmed.trim_end_matches("```").trim_end())
    } else if trimmed.starts_with("```") {
        trimmed
            .strip_prefix("```")
            .and_then(|s| s.strip_prefix('\n'))
            .unwrap_or(trimmed)
            .strip_suffix("```")
            .unwrap_or(trimmed.trim_end_matches("```").trim())
    } else {
        trimmed
    }
}

pub fn extract_json_object(input: &str) -> Result<&str, String> {
    let trimmed = input.trim();
    
    let start = match trimmed.find('{') {
        Some(idx) => idx,
        None => return Err("no_json_object".to_string()),
    };
    
    let mut brace_count = 0;
    for (i, c) in trimmed[start..].chars().enumerate() {
        match c {
            '{' => brace_count += 1,
            '}' => {
                brace_count -= 1;
                if brace_count == 0 {
                    return Ok(&trimmed[start..=start + i]);
                }
            }
            _ => {}
        }
    }
    
    Err("unclosed_json_object".to_string())
}

pub fn parse_ai_json<T: DeserializeOwned>(input: &str) -> Result<T, String> {
    let cleaned = strip_json_fence(input);
    let json_str = extract_json_object(cleaned).map_err(|e| format!("no_valid_json: {e}"))?;
    serde_json::from_str::<T>(json_str).map_err(|e| format!("json_parse_error: {e}"))
}

pub fn truncate_context(text: &str, max_chars: usize) -> String {
    if text.len() <= max_chars {
        text.to_string()
    } else {
        format!("{}...[truncated {} chars]", &text[..max_chars], text.len() - max_chars)
    }
}

pub fn json_error(error: &str) -> serde_json::Value {
    serde_json::json!({ "error": error })
}

#[allow(dead_code)]
pub fn validate_ai_output_not_just_prose(input: &str) -> Result<(), String> {
    let trimmed = input.trim();
    let json_count = trimmed.matches('{').count();
    let comma_count = trimmed.matches(',').count();
    
    if json_count < 2 && comma_count < 2 {
        if trimmed.len() > 50 && !trimmed.starts_with('{') && !trimmed.starts_with('[') {
            return Err("appears_to_be_prose_not_structured_json".to_string());
        }
    }
    
    Ok(())
}
