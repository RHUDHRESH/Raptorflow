//! Tests for the 21-screen Foundation model
//!
//! Run with: cargo test --package raptorflow-foundation

use crate::models::*;
use serde_json::json;

#[test]
fn test_full_21_screen_payload_serialization() {
    // Create a complete 21-screen payload matching the frontend store
    let foundation = FoundationData {
        // Legacy/deprecated fields
        brand_voice: None,
        brand_voice_sliders: None,
        brand_voice_descriptors: None,
        voice_fingerprint: None,
        writing_samples: None,
        channel_performance: None,
        version: 1,
        
        // Screen 1: URL
        company_url: Some("https://acme.com".to_string()),
        
        // Screen 2: Company Info
        company_info: CompanyInfo {
            name: Some("Acme Corp".to_string()),
            website: Some("https://acme.com".to_string()),
            industry: Some("SaaS".to_string()),
            stage: Some("Growth".to_string()),
            team_size: Some("10-50".to_string()),
            description: Some("Leading B2B SaaS platform".to_string()),
            legal_name: Some("Acme Corporation".to_string()),
            year_founded: Some(2020),
            tagline: Some("Empowering teams to do more".to_string()),
            logo_url: None,
        },
        
        // Screen 3: Stage
        company_stage: Some("growth".to_string()),
        
        // Screen 4: Product Catalog
        product_catalog: ProductCatalog {
            products: vec![
                Product {
                    name: "Pro Plan".to_string(),
                    description: Some("For growing teams".to_string()),
                    price: Some("$99/mo".to_string()),
                    target_segment: Some("SMB".to_string()),
                }
            ],
            primary_product: Some("Pro Plan".to_string()),
            pricing_model: Some("subscription".to_string()),
        },
        
        // Screen 5: Problem Statement
        problem_statement: Some("Teams struggle with coordination".to_string()),
        
        // Screen 6: Primary ICP (using B2B variant)
        target_audience: TargetAudience {
            mode: "b2b".to_string(),
            primary_icp: PrimaryIcp::B2B(B2BIcp {
                name: "SMB Owners".to_string(),
                persona_name: "Tech-savvy SMB Owner".to_string(),
                role_identity: "Operations Manager".to_string(),
                reporting_to: Some("CEO".to_string()),
                key_goals: vec!["Scale business".to_string()],
                pressures: vec!["Time constraints".to_string()],
                decision_process: Some("Owner-driven".to_string()),
                language_samples: vec!["Efficiency".to_string(), "ROI".to_string()],
                pain_points: vec!["Time management".to_string()],
                goals: vec!["Growth".to_string()],
                demographics: json!({"age": "30-50", "team_size": "10-50"}),
            }),
        },
        
        // Screen 7: Secondary ICPs
        secondary_icps: vec![
            SecondaryIcp::B2B(B2BIcp {
                name: "Enterprise".to_string(),
                persona_name: "Enterprise CTO".to_string(),
                role_identity: "CTO".to_string(),
                reporting_to: Some("CEO".to_string()),
                key_goals: vec!["Innovation".to_string()],
                pressures: vec!["Budget constraints".to_string()],
                decision_process: Some("Procurement".to_string()),
                language_samples: vec!["Enterprise-grade".to_string()],
                pain_points: vec!["Legacy systems".to_string()],
                goals: vec!["Digital transformation".to_string()],
                demographics: json!({"size": "500+"}),
            })
        ],
        
        // Screen 8: Competitors
        competitors: Competitors {
            direct: vec![
                Competitor {
                    name: "CompetitorA".to_string(),
                    competitor_url: Some("https://competitor-a.com".to_string()),
                    tracking_enabled: true,
                    strengths: vec!["Brand".to_string()],
                    weaknesses: vec!["Price".to_string()],
                    positioning: None,
                }
            ],
            indirect: vec![],
        },
        
        // Screen 9: Differentiation
        differentiation: vec![
            "Better UX".to_string(),
            "Lower price".to_string(),
        ],
        
        // Screen 10: Positioning
        positioning: Positioning {
            tagline: Some("The modern choice".to_string()),
            mission: Some("Empower businesses".to_string()),
            vision: Some("A connected world".to_string()),
            core_values: vec!["Innovation".to_string(), "Customer first".to_string()],
            unique_value_proposition: Some("Best-in-class UX".to_string()),
            statement: None,
            template_components: None,
            quality_score: None,
            quality_feedback: None,
            is_locked: false,
            locked_at: None,
            ai_draft: None,
        },
        
        // Screen 11: Brand Personality
        brand_personality: BrandPersonality {
            traits: vec!["Innovative".to_string(), "Friendly".to_string()],
            tone: "Professional but approachable".to_string(),
            style: "Modern".to_string(),
            archetype: Some("Hero".to_string()),
        },
        
        // Screen 12: Voice Practice
        voice_practice: VoicePractice {
            sliders: BrandVoiceSliders {
                formal_informal: 6,
                serious_playful: 4,
                technical_simple: 7,
                authoritative_collegial: 5,
                traditional_innovative: 8,
            },
            writing_samples: vec![
                WritingSample {
                    title: "Welcome Email".to_string(),
                    content: "Welcome to Acme! We're excited to have you.".to_string(),
                    category: "email".to_string(),
                    quality_score: Some(4.5),
                }
            ],
            voice_fingerprint: Some("confident-friendly-informative".to_string()),
        },
        
        // Screen 13: Content Territories
        content_territories: vec![
            ContentTerritory {
                name: "Product Updates".to_string(),
                description: "Latest features and releases".to_string(),
                priority: 1,
                topics: vec!["New features".to_string()],
                content_types: vec!["Blog".to_string()],
            }
        ],
        
        // Screen 14: Channels
        channels: Channels {
            primary: vec![
                Channel {
                    name: "LinkedIn".to_string(),
                    platform: "LinkedIn".to_string(),
                    frequency: Some("Weekly".to_string()),
                    audience_size: Some("10k".to_string()),
                    url: Some("https://linkedin.com/company/acme".to_string()),
                    is_active: true,
                }
            ],
            secondary: vec![],
            content_history: ContentHistory {
                current_output: Some("Bi-weekly blogs".to_string()),
                satisfaction: Some("Satisfied".to_string()),
                challenges: vec!["Content calendar".to_string()],
            },
        },
        
        // Screen 15: Goals & KPIs
        goals: Goals {
            primary_goal: Some("Brand awareness".to_string()),
            secondary_goals: vec!["Lead generation".to_string()],
            kpis: vec![
                Kpi {
                    name: "Website traffic".to_string(),
                    target: "50k/mo".to_string(),
                    current: Some("20k/mo".to_string()),
                    metric: "visitors".to_string(),
                }
            ],
            budget: Budget {
                monthly: Some("$5000".to_string()),
                total: Some("$60000".to_string()),
                currency: "USD".to_string(),
            },
            timeline: Some("12 months".to_string()),
        },
        
        // Screen 16: SEO Keywords
        seo_keywords: SeoKeywords {
            primary_keywords: vec!["project management".to_string(), "team collaboration".to_string()],
            secondary_keywords: vec!["productivity tools".to_string()],
            negative_keywords: vec!["free".to_string()],
            search_volume_data: None,
            competitor_keywords: None,
        },
        
        // Screen 17: Asset Inventory
        asset_inventory: AssetInventory {
            logos: vec![
                Asset {
                    name: "Primary Logo".to_string(),
                    url: Some("https://acme.com/logo.png".to_string()),
                    asset_type: "logo".to_string(),
                    description: None,
                }
            ],
            images: vec![],
            templates: vec![],
            documents: vec![],
            existing_brand_guidelines: None,
        },
        
        // Screen 18: Frustrations
        frustrations: Frustrations {
            current_solutions: vec!["Spreadsheets".to_string()],
            pain_points: vec![
                Frustration {
                    description: "Disorganized workflows".to_string(),
                    severity: "high".to_string(),
                    frequency: "daily".to_string(),
                    impact: "productivity".to_string(),
                }
            ],
            analytics_tracking: AnalyticsTracking {
                current_tools: vec!["Google Analytics".to_string()],
                satisfaction: Some("Neutral".to_string()),
                gaps: vec!["Attribution".to_string()],
            },
        },
        
        // Screen 19: Tools
        tools: Tools {
            crm: vec![
                Tool {
                    name: "HubSpot".to_string(),
                    category: "CRM".to_string(),
                    usage: "Customer management".to_string(),
                    integration_status: Some("Connected".to_string()),
                }
            ],
            marketing: vec![],
            analytics: vec![],
            design: vec![],
            other: vec![],
        },
        
        // Screen 20: Reference Brands
        reference_brands: vec![
            ReferenceBrand {
                name: "Stripe".to_string(),
                website: Some("https://stripe.com".to_string()),
                what_to_imitate: "Developer experience".to_string(),
                aspects: vec!["Documentation".to_string(), "API design".to_string()],
            }
        ],
        
        // Screen 21: Strategist
        strategist: Strategist {
            name: "Alex".to_string(),
            personality: StrategistPersonality {
                communication_style: "Direct and practical".to_string(),
                expertise_areas: vec!["B2B SaaS".to_string(), "Growth".to_string()],
                tone_preferences: json!({"formality": 6, "playfulness": 4}),
                industry_focus: vec!["SaaS".to_string()],
                avatar_style: Some("Professional".to_string()),
            },
            calibration_notes: Some("Prefers data-driven insights".to_string()),
            avatar_seed: None,
        },
        
        extra: json!({}),
    };

    // Serialize to JSON
    let json_str = serde_json::to_string_pretty(&foundation).expect("Failed to serialize");
    
    // Verify key fields are present in the JSON
    let json: serde_json::Value = serde_json::from_str(&json_str).expect("Failed to parse JSON");
    
    // Screen 1: URL
    assert_eq!(json["company_url"].as_str().unwrap(), "https://acme.com");
    
    // Screen 2: Company Info
    assert_eq!(json["company_info"]["name"].as_str().unwrap(), "Acme Corp");
    assert_eq!(json["company_info"]["legal_name"].as_str().unwrap(), "Acme Corporation");
    assert_eq!(json["company_info"]["year_founded"].as_i64().unwrap(), 2020);
    
    // Screen 3: Stage
    assert_eq!(json["company_stage"].as_str().unwrap(), "growth");
    
    // Screen 4: Products
    assert_eq!(json["product_catalog"]["pricing_model"].as_str().unwrap(), "subscription");
    
    // Screen 5: Problem Statement
    assert_eq!(json["problem_statement"].as_str().unwrap(), "Teams struggle with coordination");
    
    // Screen 6: Primary ICP
    assert!(json["target_audience"]["mode"].is_string());
    assert_eq!(json["target_audience"]["mode"].as_str().unwrap(), "b2b");
    
    // Screen 7: Secondary ICPs
    assert!(json["secondary_icps"].is_array());
    
    // Screen 8: Competitors
    assert_eq!(json["competitors"]["direct"][0]["name"].as_str().unwrap(), "CompetitorA");
    
    // Screen 9: Differentiation
    assert_eq!(json["differentiation"][0].as_str().unwrap(), "Better UX");
    
    // Screen 10: Positioning
    assert_eq!(json["positioning"]["tagline"].as_str().unwrap(), "The modern choice");
    
    // Screen 11: Brand Personality
    assert_eq!(json["brand_personality"]["archetype"].as_str().unwrap(), "Hero");
    
    // Screen 12: Voice Practice
    assert_eq!(json["voice_practice"]["sliders"]["formal_informal"].as_u64().unwrap(), 6);
    
    // Screen 13: Content Territories
    assert_eq!(json["content_territories"][0]["name"].as_str().unwrap(), "Product Updates");
    
    // Screen 14: Channels
    assert_eq!(json["channels"]["primary"][0]["platform"].as_str().unwrap(), "LinkedIn");
    
    // Screen 15: Goals & KPIs
    assert_eq!(json["goals"]["primary_goal"].as_str().unwrap(), "Brand awareness");
    
    // Screen 16: SEO Keywords
    assert_eq!(json["seo_keywords"]["primary_keywords"][0].as_str().unwrap(), "project management");
    
    // Screen 17: Asset Inventory
    assert_eq!(json["asset_inventory"]["logos"][0]["name"].as_str().unwrap(), "Primary Logo");
    
    // Screen 18: Frustrations
    assert_eq!(json["frustrations"]["pain_points"][0]["severity"].as_str().unwrap(), "high");
    
    // Screen 19: Tools
    assert_eq!(json["tools"]["crm"][0]["name"].as_str().unwrap(), "HubSpot");
    
    // Screen 20: Reference Brands
    assert_eq!(json["reference_brands"][0]["name"].as_str().unwrap(), "Stripe");
    
    // Screen 21: Strategist
    assert_eq!(json["strategist"]["name"].as_str().unwrap(), "Alex");
    assert_eq!(json["strategist"]["personality"]["communication_style"].as_str().unwrap(), "Direct and practical");
    
    // Version field
    assert_eq!(json["version"].as_i64().unwrap(), 1);
    
    println!("✅ All 21 screen fields serialize correctly!");
    println!("\nSerialized payload:\n{}", json_str);
}

#[test]
fn test_brand_voice_sliders_defaults() {
    let sliders = BrandVoiceSliders::defaults();
    
    assert_eq!(sliders.formal_informal, 5);
    assert_eq!(sliders.serious_playful, 5);
    assert_eq!(sliders.technical_simple, 5);
    assert_eq!(sliders.authoritative_collegial, 5);
    assert_eq!(sliders.traditional_innovative, 5);
}

#[test]
fn test_foundation_data_roundtrip() {
    // Test that we can deserialize from JSON and serialize back
    let json_payload = json!({
        "version": 1,
        "company_url": "https://test.com",
        "company_info": {
            "name": "Test Co",
            "legal_name": "Test Company LLC",
            "year_founded": 2021
        },
        "company_stage": "startup",
        "product_catalog": {
            "products": [],
            "pricing_model": "tiered"
        },
        "problem_statement": "Customer pain point",
        "target_audience": {
            "mode": "b2b",
            "primary_icp": {
                "B2B": {
                    "name": "Primary ICP",
                    "persona_name": "Persona",
                    "role_identity": "Manager",
                    "key_goals": [],
                    "pressures": [],
                    "language_samples": [],
                    "pain_points": [],
                    "goals": [],
                    "demographics": {}
                }
            }
        },
        "secondary_icps": [],
        "competitors": {
            "direct": [],
            "indirect": []
        },
        "differentiation": ["Feature A", "Feature B"],
        "positioning": {
            "tagline": "The better choice",
            "mission": "Our mission",
            "vision": "Our vision",
            "core_values": ["Value 1"],
            "unique_value_proposition": "UVP here",
            "statement": null,
            "template_components": null,
            "quality_score": null,
            "quality_feedback": null,
            "is_locked": false,
            "locked_at": null,
            "ai_draft": null
        },
        "brand_personality": {
            "traits": ["Trait 1"],
            "tone": "Professional",
            "style": "Modern",
            "archetype": "Innocent"
        },
        "voice_practice": {
            "sliders": {
                "formal_informal": 7,
                "serious_playful": 3,
                "technical_simple": 8,
                "authoritative_collegial": 5,
                "traditional_innovative": 6
            },
            "writing_samples": [],
            "voice_fingerprint": null
        },
        "content_territories": [],
        "channels": {
            "primary": [],
            "secondary": [],
            "content_history": {
                "current_output": null,
                "satisfaction": null,
                "challenges": []
            }
        },
        "goals": {
            "primary_goal": "Revenue growth",
            "secondary_goals": [],
            "kpis": [],
            "budget": {
                "monthly": "$10000",
                "total": "$120000",
                "currency": "USD"
            },
            "timeline": null
        },
        "seo_keywords": {
            "primary_keywords": ["keyword 1"],
            "secondary_keywords": [],
            "negative_keywords": []
        },
        "asset_inventory": {
            "logos": [],
            "images": [],
            "templates": [],
            "documents": []
        },
        "frustrations": {
            "current_solutions": [],
            "pain_points": [],
            "analytics_tracking": {
                "current_tools": [],
                "satisfaction": null,
                "gaps": []
            }
        },
        "tools": {
            "crm": [],
            "marketing": [],
            "analytics": [],
            "design": [],
            "other": []
        },
        "reference_brands": [],
        "strategist": {
            "name": "Sarah",
            "personality": {
                "communication_style": "Collaborative",
                "expertise_areas": ["B2B"],
                "tone_preferences": {},
                "industry_focus": []
            },
            "calibration_notes": null,
            "avatar_seed": null
        }
    });
    
    // Deserialize
    let foundation: FoundationData = serde_json::from_value(json_payload.clone())
        .expect("Failed to deserialize");
    
    assert_eq!(foundation.company_url.as_deref(), Some("https://test.com"));
    assert_eq!(foundation.company_info.name.as_deref(), Some("Test Co"));
    assert_eq!(foundation.company_info.legal_name.as_deref(), Some("Test Company LLC"));
    assert_eq!(foundation.company_info.year_founded, Some(2021));
    assert_eq!(foundation.company_stage.as_deref(), Some("startup"));
    assert_eq!(foundation.product_catalog.pricing_model.as_deref(), Some("tiered"));
    assert_eq!(foundation.strategist.name, "Sarah");
    
    // Serialize back
    let serialized = serde_json::to_value(&foundation).expect("Failed to serialize back");
    
    // Verify the roundtrip preserved all fields
    assert_eq!(serialized["company_url"], json_payload["company_url"]);
    assert_eq!(serialized["company_info"]["name"], json_payload["company_info"]["name"]);
    assert_eq!(serialized["company_stage"], json_payload["company_stage"]);
    
    println!("✅ Foundation data roundtrip test passed!");
}

#[test]
fn test_partial_payload_deserialization() {
    // Test that we can deserialize partial payloads (for individual section updates)
    // Note: Required fields must be present, but their inner values can be null/empty
    let partial_json = json!({
        "version": 1,
        "company_url": "https://partial.com",
        "company_info": {},
        "target_audience": {
            "mode": "b2b",
            "primary_icp": {
                "B2B": {
                    "name": "Default",
                    "persona_name": "Default",
                    "role_identity": "",
                    "key_goals": [],
                    "pressures": [],
                    "language_samples": [],
                    "pain_points": [],
                    "goals": [],
                    "demographics": {}
                }
            }
        },
        "competitors": { "direct": [], "indirect": [] },
        "positioning": {
            "is_locked": false
        },
        "brand_personality": { "traits": [], "tone": "", "style": "" },
        "voice_practice": {
            "sliders": {
                "formal_informal": 5,
                "serious_playful": 5,
                "technical_simple": 5,
                "authoritative_collegial": 5,
                "traditional_innovative": 5
            },
            "writing_samples": []
        },
        "channels": { "primary": [], "secondary": [], "content_history": { "challenges": [] } },
        "goals": { "secondary_goals": [], "kpis": [], "budget": { "currency": "USD" } },
        "asset_inventory": { "logos": [], "images": [], "templates": [], "documents": [] },
        "frustrations": { "current_solutions": [], "pain_points": [], "analytics_tracking": { "current_tools": [], "gaps": [] } },
        "tools": { "crm": [], "marketing": [], "analytics": [], "design": [], "other": [] },
        "strategist": {
            "name": "",
            "personality": {
                "communication_style": "",
                "expertise_areas": [],
                "tone_preferences": {},
                "industry_focus": []
            }
        },
        "differentiation": ["Diff 1", "Diff 2"]
    });
    
    let foundation: FoundationData = serde_json::from_value(partial_json)
        .expect("Failed to deserialize partial payload");
    
    assert_eq!(foundation.company_url.as_deref(), Some("https://partial.com"));
    assert_eq!(foundation.differentiation.len(), 2);
    
    // Other fields should be default
    assert!(foundation.company_info.name.is_none());
    assert!(foundation.strategist.name.is_empty());
    
    println!("✅ Partial payload deserialization works!");
}

#[test]
fn test_b2b_b2c_icp_variants() {
    // Test B2B ICP
    let b2b_icp = PrimaryIcp::B2B(B2BIcp {
        name: "B2B Customer".to_string(),
        persona_name: "B2B Persona".to_string(),
        role_identity: "Director".to_string(),
        reporting_to: Some("VP".to_string()),
        key_goals: vec!["Scale".to_string()],
        pressures: vec!["Market pressure".to_string()],
        decision_process: Some("Committee".to_string()),
        language_samples: vec!["ROI".to_string()],
        pain_points: vec!["Efficiency".to_string()],
        goals: vec!["Growth".to_string()],
        demographics: json!({"age": "40-55"}),
    });
    
    // Test B2C ICP
    let b2c_icp = PrimaryIcp::B2C(B2CIcp {
        name: "B2C Customer".to_string(),
        persona_name: "B2C Persona".to_string(),
        life_situation: "Working parent".to_string(),
        aspirations: vec!["Work-life balance".to_string()],
        behaviors: vec!["Online shopping".to_string()],
        language_samples: vec!["Convenient".to_string()],
        pain_points: vec!["Time".to_string()],
        goals: vec!["Save time".to_string()],
        demographics: json!({"age": "30-45"}),
    });
    
    // Serialize both
    let b2b_json = serde_json::to_value(&b2b_icp).unwrap();
    let b2c_json = serde_json::to_value(&b2c_icp).unwrap();
    
    assert!(b2b_json.get("B2B").is_some());
    assert!(b2c_json.get("B2C").is_some());
    
    println!("✅ B2B/B2C ICP variants serialize correctly!");
}