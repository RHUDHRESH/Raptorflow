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

#[cfg(test)]
mod tests {
    use std::collections::BTreeSet;
    use std::fs;
    use std::path::PathBuf;

    fn migrations_dir() -> PathBuf {
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../database/migrations")
    }

    fn normalize_table_name(raw: &str) -> String {
        raw.trim()
            .trim_end_matches('(')
            .trim_matches('"')
            .trim_end_matches(';')
            .to_ascii_lowercase()
    }

    fn table_name_from_create(line: &str) -> Option<String> {
        let tokens: Vec<&str> = line.split_whitespace().collect();
        let table_idx = tokens
            .iter()
            .position(|token| token.eq_ignore_ascii_case("TABLE"))?;
        let mut name_idx = table_idx + 1;
        if tokens
            .get(name_idx)
            .is_some_and(|token| token.eq_ignore_ascii_case("IF"))
        {
            name_idx += 3;
        }
        tokens.get(name_idx).map(|name| normalize_table_name(name))
    }

    fn table_name_from_alter(line: &str) -> Option<String> {
        let tokens: Vec<&str> = line.split_whitespace().collect();
        let table_idx = tokens
            .iter()
            .position(|token| token.eq_ignore_ascii_case("TABLE"))?;
        tokens
            .get(table_idx + 1)
            .map(|name| normalize_table_name(name))
    }

    #[test]
    fn org_scoped_tables_enable_rls_in_migrations() {
        let mut org_tables = BTreeSet::new();
        let mut rls_tables = BTreeSet::new();

        for entry in fs::read_dir(migrations_dir()).expect("read database/migrations") {
            let path = entry.expect("migration entry").path();
            if path.extension().and_then(|ext| ext.to_str()) != Some("sql") {
                continue;
            }

            let sql = fs::read_to_string(&path).expect("read migration");
            let mut current_table: Option<String> = None;
            let mut current_block = String::new();

            for line in sql.lines() {
                if line.to_ascii_uppercase().contains("CREATE TABLE") {
                    if let Some(table) = current_table.take() {
                        if current_block.to_ascii_lowercase().contains("org_id") {
                            org_tables.insert(table);
                        }
                    }
                    current_table = table_name_from_create(line);
                    current_block.clear();
                }

                if let Some(table) = &current_table {
                    current_block.push_str(line);
                    current_block.push('\n');

                    if line.trim_end().ends_with(");") {
                        if current_block.to_ascii_lowercase().contains("org_id") {
                            org_tables.insert(table.clone());
                        }
                        current_table = None;
                        current_block.clear();
                    }
                }

                if line
                    .to_ascii_uppercase()
                    .contains("ENABLE ROW LEVEL SECURITY")
                {
                    if let Some(table) = table_name_from_alter(line) {
                        rls_tables.insert(table);
                    }
                }
            }

            if let Some(table) = current_table {
                if current_block.to_ascii_lowercase().contains("org_id") {
                    org_tables.insert(table);
                }
            }
        }

        let missing: Vec<_> = org_tables.difference(&rls_tables).cloned().collect();
        assert!(
            missing.is_empty(),
            "org-scoped tables missing ENABLE ROW LEVEL SECURITY: {missing:?}"
        );
    }
}
