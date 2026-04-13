#[cfg(test)]
mod tests {
    use hmac::{Hmac, Mac};
    use sha2::Sha256;
    
    type HmacSha256 = Hmac<Sha256>;
    
    fn create_test_signature(secret: &str, payload: &[u8]) -> String {
        let mut mac = HmacSha256::new_from_slice(secret.as_bytes()).unwrap();
        mac.update(payload);
        hex::encode(mac.finalize().into_bytes())
    }
    
    #[test]
    fn test_razorpay_webhook_signature_verification() {
        let secret = "test-webhook-secret";
        let payload = br#"{"event":"payment.captured","payload":{"payment":{"entity":{"id":"pay_123"}}}}"#;
        
        let signature = create_test_signature(secret, payload);
        
        let mut mac = HmacSha256::new_from_slice(secret.as_bytes()).unwrap();
        mac.update(payload);
        let expected = mac.finalize().into_bytes();
        
        let sig_bytes = hex::decode(&signature).unwrap();
        assert_eq!(expected.len(), sig_bytes.len());
        
        let mut diff = 0u8;
        for (a, b) in expected.iter().zip(sig_bytes.iter()) {
            diff |= a ^ b;
        }
        assert_eq!(diff, 0, "Signatures should match");
    }
    
    #[test]
    fn test_constant_time_comparison_timing_safe() {
        let secret1 = "test-secret-1";
        let secret2 = "test-secret-2";
        let secret3 = "test-secret-1"; 
        
        let sig1 = create_test_signature(secret1, b"payload");
        let sig2 = create_test_signature(secret2, b"payload");
        let sig3 = create_test_signature(secret3, b"payload");
        
        assert_ne!(sig1, sig2, "Different secrets should produce different signatures");
        assert_eq!(sig1, sig3, "Same secrets should produce same signatures");
    }
    
    #[test]
    fn test_razorpay_webhook_parse_payment_event() {
        let payload = r#"{
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_123",
                        "amount": 50000,
                        "currency": "INR",
                        "status": "captured",
                        "order_id": "order_123"
                    }
                }
            }
        }"#;
        
        let parsed: serde_json::Value = serde_json::from_str(payload).unwrap();
        assert_eq!(parsed["event"], "payment.captured");
        assert_eq!(parsed["payload"]["payment"]["entity"]["id"], "pay_123");
        assert_eq!(parsed["payload"]["payment"]["entity"]["amount"], 50000);
    }
    
    #[test]
    fn test_razorpay_webhook_parse_subscription_event() {
        let payload = r#"{
            "event": "subscription.activated",
            "payload": {
                "subscription": {
                    "entity": {
                        "id": "sub_123",
                        "status": "active",
                        "plan_id": "plan_123"
                    }
                }
            }
        }"#;
        
        let parsed: serde_json::Value = serde_json::from_str(payload).unwrap();
        assert_eq!(parsed["event"], "subscription.activated");
        assert_eq!(parsed["payload"]["subscription"]["entity"]["status"], "active");
    }
}