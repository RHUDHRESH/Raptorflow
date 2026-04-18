#[cfg(test)]
mod tests {
    use raptorflow_cache::CacheError;

    const TEST_NAMESPACE: &str = "test";
    const TEST_KEY: &str = "test_key";

    fn make_key(key: &str) -> String {
        format!("raptorflow:{}:{}", TEST_NAMESPACE, key)
    }

    #[test]
    fn test_key_formation() {
        let key = make_key("foo");
        assert_eq!(key, "raptorflow:test:foo");
    }

    #[test]
    fn test_cache_error_display() {
        let err = CacheError::Connection("connection failed".to_string());
        assert_eq!(err.to_string(), "Connection error: connection failed");

        let err = CacheError::Get("key not found".to_string());
        assert_eq!(err.to_string(), "Get error: key not found");

        let err = CacheError::Connection("webhook signature mismatch".to_string());
        assert_eq!(
            err.to_string(),
            "Connection error: webhook signature mismatch"
        );
    }

    #[test]
    fn test_namespace_prefix() {
        let key = format!("raptorflow:{}:content", TEST_NAMESPACE);
        assert!(key.starts_with("raptorflow:test:"));
    }

    #[test]
    fn test_invalidate_prefix_pattern() {
        let prefix = "foundation";
        let pattern = format!("raptorflow:{}:{}*", TEST_NAMESPACE, prefix);
        assert_eq!(pattern, "raptorflow:test:foundation*");
    }
}
