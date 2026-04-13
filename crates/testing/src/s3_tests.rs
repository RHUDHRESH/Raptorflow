#[cfg(test)]
mod tests {
    use raptorflow_aws::{S3Service, S3Error};
    
    #[test]
    fn test_object_key_formation() {
        let key = S3Service::object_key("uploads", "org-123", "file.pdf");
        assert_eq!(key, "uploads/org-123/file.pdf");
    }
    
    #[test]
    fn test_object_key_with_prefix() {
        let key = S3Service::object_key("screenshots", "org-456", "campaign-789.png");
        assert_eq!(key, "screenshots/org-456/campaign-789.png");
    }
    
    #[test]
    fn test_object_key_exports() {
        let key = S3Service::object_key("exports", "org-abc", "report.json");
        assert_eq!(key, "exports/org-abc/report.json");
    }
    
    #[test]
    fn test_s3_error_display() {
        let err = S3Error::Config("missing region".to_string());
        assert_eq!(err.to_string(), "Config error: missing region");
        
        let err = S3Error::Presigning("timeout".to_string());
        assert_eq!(err.to_string(), "Presigning error: timeout");
        
        let err = S3Error::Api("access denied".to_string());
        assert_eq!(err.to_string(), "API error: access denied");
        
        let err = S3Error::NotFound;
        assert_eq!(err.to_string(), "Not found");
    }
}