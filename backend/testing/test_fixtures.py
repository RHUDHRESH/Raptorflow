"""
Test Fixtures
Pre-defined test data and fixtures for the testing framework
"""

import logging
from typing import Any, Dict, List
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class OnboardingFixtures:
    """Fixtures for onboarding tests"""
    
    def get_all_fixtures(self) -> Dict[str, Any]:
        """Get all onboarding fixtures"""
        return {
            "sample_company": self.get_sample_company(),
            "sample_evidence": self.get_sample_evidence(),
            "sample_workflow": self.get_sample_workflow(),
            "sample_session": self.get_sample_session(),
            "step_definitions": self.get_step_definitions()
        }
    
    def get_sample_company(self) -> Dict[str, Any]:
        """Get sample company data"""
        return {
            "name": "TechCorp Solutions",
            "size": "startup",
            "industry": "marketing technology",
            "founded_year": 2020,
            "employee_count": 25,
            "revenue": 1500000,
            "headquarters": "San Francisco, CA",
            "target_market": "B2B SaaS",
            "product_category": "Marketing Automation",
            "growth_stage": "early",
            "financial_resources": "moderate",
            "innovation_capability": "developing",
            "risk_tolerance": "medium",
            "website": "https://techcorp.com",
            "description": "AI-powered marketing automation platform for small businesses"
        }
    
    def get_sample_evidence(self) -> List[Dict[str, Any]]:
        """Get sample evidence documents"""
        return [
            {
                "id": "evi_001",
                "name": "Q3 2023 Financial Report",
                "type": "financial",
                "content": """
                Q3 2023 Financial Report
                
                Revenue: $1,500,000
                Growth Rate: 25% YoY
                Profit Margin: 15%
                Customer Acquisition Cost: $500
                Lifetime Value: $5,000
                
                Key Metrics:
                - Monthly Active Users: 10,000
                - Conversion Rate: 3.5%
                - Churn Rate: 2.1%
                """,
                "source": "upload",
                "confidence": 0.95,
                "created_at": "2023-10-15T10:00:00Z"
            },
            {
                "id": "evi_002",
                "name": "Product Roadmap 2024",
                "type": "strategic",
                "content": """
                Product Roadmap 2024
                
                Q1 2024:
                - AI-powered campaign optimization
                - Advanced analytics dashboard
                - Mobile app launch
                
                Q2 2024:
                - Enterprise features
                - API integrations
                - Multi-language support
                
                Q3 2024:
                - Machine learning models
                - Predictive analytics
                - Custom workflows
                
                Q4 2024:
                - Voice commands
                - Augmented reality features
                - Blockchain integration
                """,
                "source": "upload",
                "confidence": 0.90,
                "created_at": "2023-11-01T14:30:00Z"
            },
            {
                "id": "evi_003",
                "name": "Competitive Analysis",
                "type": "competitive",
                "content": """
                Competitive Analysis
                
                Key Competitors:
                1. HubSpot - Market leader, $1.5B revenue
                2. ActiveCampaign - Strong automation, $200M revenue
                3. Mailchimp - Email focus, $800M revenue
                
                Market Position:
                - Price: 20% lower than HubSpot
                - Features: More AI capabilities
                - Target: Small to mid-market businesses
                
                Competitive Advantages:
                - Superior AI algorithms
                - Better user experience
                - Lower total cost of ownership
                """,
                "source": "upload",
                "confidence": 0.85,
                "created_at": "2023-10-20T09:15:00Z"
            }
        ]
    
    def get_sample_workflow(self) -> Dict[str, Any]:
        """Get sample workflow data"""
        return {
            "id": "workflow_001",
            "name": "Standard Onboarding Workflow",
            "steps": [
                {
                    "step_number": 1,
                    "name": "evidence_vault",
                    "title": "Evidence Vault",
                    "description": "Upload and organize business evidence",
                    "estimated_duration": 30,
                    "dependencies": [],
                    "status": "completed"
                },
                {
                    "step_number": 2,
                    "name": "brand_voice",
                    "title": "Brand Voice",
                    "description": "Define brand personality and communication style",
                    "estimated_duration": 45,
                    "dependencies": ["evidence_vault"],
                    "status": "completed"
                },
                {
                    "step_number": 3,
                    "name": "auto_extraction",
                    "title": "Auto Extraction",
                    "description": "AI-powered fact extraction from evidence",
                    "estimated_duration": 20,
                    "dependencies": ["evidence_vault"],
                    "status": "in_progress"
                }
            ],
            "created_at": "2023-12-01T10:00:00Z",
            "updated_at": "2023-12-01T15:30:00Z"
        }
    
    def get_sample_session(self) -> Dict[str, Any]:
        """Get sample onboarding session"""
        return {
            "id": "session_001",
            "workspace_id": "workspace_001",
            "user_id": "user_001",
            "status": "active",
            "current_step": 3,
            "completed_steps": 2,
            "progress_percentage": 8.7,
            "created_at": "2023-12-01T10:00:00Z",
            "updated_at": "2023-12-01T15:30:00Z",
            "step_data": {
                "evidence_vault": {
                    "status": "completed",
                    "data": {"evidence_count": 3},
                    "completed_at": "2023-12-01T11:00:00Z"
                },
                "brand_voice": {
                    "status": "completed",
                    "data": {"personality": "innovative", "tone": "professional"},
                    "completed_at": "2023-12-01T12:00:00Z"
                },
                "auto_extraction": {
                    "status": "in_progress",
                    "data": {"facts_extracted": 15},
                    "started_at": "2023-12-01T15:30:00Z"
                }
            }
        }
    
    def get_step_definitions(self) -> Dict[str, Any]:
        """Get step definitions for all 23 steps"""
        return {
            "evidence_vault": {
                "name": "Evidence Vault",
                "description": "Upload and organize business evidence",
                "estimated_duration": 30,
                "type": "data_collection"
            },
            "brand_voice": {
                "name": "Brand Voice",
                "description": "Define brand personality and communication style",
                "estimated_duration": 45,
                "type": "branding"
            },
            "auto_extraction": {
                "name": "Auto Extraction",
                "description": "AI-powered fact extraction from evidence",
                "estimated_duration": 20,
                "type": "analysis"
            },
            "contradiction_check": {
                "name": "Contradiction Check",
                "description": "Identify and resolve data inconsistencies",
                "estimated_duration": 15,
                "type": "validation"
            },
            "reddit_research": {
                "name": "Reddit Research",
                "description": "Market intelligence from Reddit discussions",
                "estimated_duration": 25,
                "type": "research"
            },
            "category_paths": {
                "name": "Category Paths",
                "description": "Safe/Clever/Bold strategic positioning",
                "estimated_duration": 30,
                "type": "strategy"
            },
            "capability_rating": {
                "name": "Capability Rating",
                "description": "Assess organizational capabilities",
                "estimated_duration": 20,
                "type": "assessment"
            },
            "perceptual_map": {
                "name": "Perceptual Map",
                "description": "AI-powered competitive positioning map",
                "estimated_duration": 25,
                "type": "visualization"
            },
            "neuroscience_copy": {
                "name": "Neuroscience Copy",
                "description": "Neuroscience-based copywriting",
                "estimated_duration": 35,
                "type": "content"
            },
            "focus_sacrifice": {
                "name": "Focus/Sacrifice",
                "description": "Strategic focus and sacrifice decisions",
                "estimated_duration": 20,
                "type": "strategy"
            },
            "icp_generation": {
                "name": "ICP Generation",
                "description": "Deep Ideal Customer Profile creation",
                "estimated_duration": 30,
                "type": "profiling"
            },
            "messaging_rules": {
                "name": "Messaging Rules",
                "description": "Strategic messaging framework",
                "estimated_duration": 25,
                "type": "content"
            },
            "channel_strategy": {
                "name": "Channel Strategy",
                "description": "Go-to-market channel recommendations",
                "estimated_duration": 30,
                "type": "strategy"
            },
            "tam_sam_som": {
                "name": "TAM/SAM/SOM",
                "description": "Market sizing and opportunity analysis",
                "estimated_duration": 20,
                "type": "analysis"
            },
            "validation_tasks": {
                "name": "Validation Tasks",
                "description": "Final validation and completion",
                "estimated_duration": 15,
                "type": "validation"
            }
        }


@dataclass
class AgentFixtures:
    """Fixtures for agent tests"""
    
    def get_all_fixtures(self) -> Dict[str, Any]:
        """Get all agent fixtures"""
        return {
            "sample_documents": self.get_sample_documents(),
            "sample_facts": self.get_sample_facts(),
            "sample_competitors": self.get_sample_competitors(),
            "sample_posts": self.get_sample_posts(),
            "sample_channels": self.get_sample_channels(),
            "sample_principles": self.get_sample_principles()
        }
    
    def get_sample_documents(self) -> List[Dict[str, Any]]:
        """Get sample documents for classification"""
        return [
            {
                "id": "doc_001",
                "name": "Annual Report 2023",
                "content": "Revenue increased by 25% to $10M. Profit margin improved to 15%.",
                "type": "financial",
                "metadata": {"pages": 50, "format": "pdf"}
            },
            {
                "id": "doc_002",
                "name": "Terms of Service",
                "content": "This agreement governs the use of our software platform...",
                "type": "legal",
                "metadata": {"pages": 15, "format": "docx"}
            },
            {
                "id": "doc_003",
                "name": "Marketing Campaign Brief",
                "content": "Q4 campaign targeting small businesses with AI solutions...",
                "type": "marketing",
                "metadata": {"pages": 8, "format": "pdf"}
            }
        ]
    
    def get_sample_facts(self) -> List[Dict[str, Any]]:
        """Get sample facts for extraction"""
        return [
            {
                "id": "fact_001",
                "label": "Revenue",
                "value": "$10,000,000",
                "category": "financial",
                "confidence": 0.95,
                "source": "Annual Report 2023"
            },
            {
                "id": "fact_002",
                "label": "Growth Rate",
                "value": "25%",
                "category": "financial",
                "confidence": 0.90,
                "source": "Annual Report 2023"
            },
            {
                "id": "fact_003",
                "label": "Employee Count",
                "value": "150",
                "category": "company",
                "confidence": 0.85,
                "source": "Company Overview"
            },
            {
                "id": "fact_004",
                "label": "Target Market",
                "value": "Small Businesses",
                "category": "market",
                "confidence": 0.80,
                "source": "Marketing Strategy"
            }
        ]
    
    def get_sample_competitors(self) -> List[Dict[str, Any]]:
        """Get sample competitors for analysis"""
        return [
            {
                "id": "comp_001",
                "name": "HubSpot",
                "revenue": 1500000000,
                "market_share": 0.35,
                "employees": 7000,
                "founded": 2006,
                "strengths": ["Brand recognition", "Comprehensive platform", "Large customer base"],
                "weaknesses": ["High prices", "Complex interface", "Slow innovation"]
            },
            {
                "id": "comp_002",
                "name": "ActiveCampaign",
                "revenue": 200000000,
                "market_share": 0.04,
                "employees": 800,
                "founded": 2003,
                "strengths": ["Automation features", "Good pricing", "User-friendly"],
                "weaknesses": ["Limited enterprise features", "Smaller market share"]
            },
            {
                "id": "comp_003",
                "name": "Mailchimp",
                "revenue": 800000000,
                "market_share": 0.12,
                "employees": 1200,
                "founded": 2001,
                "strengths": ["Email expertise", "Brand recognition", "Easy to use"],
                "weaknesses": ["Limited automation", "Focus on email only"]
            }
        ]
    
    def get_sample_posts(self) -> List[Dict[str, Any]]:
        """Get sample Reddit posts for research"""
        return [
            {
                "id": "post_001",
                "title": "Best marketing automation tools for small business?",
                "content": "Looking for recommendations for marketing automation tools that work well for small businesses with limited budgets.",
                "subreddit": "marketing",
                "score": 150,
                "comments": 45,
                "sentiment": "neutral",
                "post_type": "question"
            },
            {
                "id": "post_002",
                "title": "HubSpot is way too expensive for what it offers",
                "content": "I've been using HubSpot for 6 months and the pricing is just ridiculous for the features you get.",
                "subreddit": "marketing",
                "score": 200,
                "comments": 78,
                "sentiment": "negative",
                "post_type": "complaint"
            },
            {
                "id": "post_003",
                "title": "ActiveCampaign has been a game changer for us",
                "content": "We switched to ActiveCampaign 3 months ago and the automation features are incredible. Highly recommend!",
                "subreddit": "marketing",
                "score": 120,
                "comments": 32,
                "sentiment": "positive",
                "post_type": "praise"
            }
        ]
    
    def get_sample_channels(self) -> List[Dict[str, Any]]:
        """Get sample channels for recommendation"""
        return [
            {
                "id": "channel_001",
                "name": "LinkedIn Ads",
                "type": "social",
                "cost_per_lead": 50,
                "conversion_rate": 0.025,
                "reach": 1000000,
                "target_audience": "B2B professionals"
            },
            {
                "id": "channel_002",
                "name": "Google Ads",
                "type": "search",
                "cost_per_lead": 80,
                "conversion_rate": 0.03,
                "reach": 500000,
                "target_audience": "Active searchers"
            },
            {
                "id": "channel_003",
                "name": "Email Marketing",
                "type": "direct",
                "cost_per_lead": 20,
                "conversion_rate": 0.04,
                "reach": 50000,
                "target_audience": "Existing contacts"
            },
            {
                "id": "channel_004",
                "name": "Content Marketing",
                "type": "organic",
                "cost_per_lead": 30,
                "conversion_rate": 0.02,
                "reach": 200000,
                "target_audience": "Information seekers"
            }
        ]
    
    def get_sample_principles(self) -> List[Dict[str, Any]]:
        """Get sample neuroscience principles"""
        return [
            {
                "id": "principle_001",
                "name": "Cognitive Ease",
                "description": "People prefer things that are easy to think about",
                "application": "Use simple language and clear structure"
            },
            {
                "id": "principle_002",
                "name": "Social Proof",
                "description": "People follow the actions of others",
                "application": "Show testimonials and case studies"
            },
            {
                "id": "principle_003",
                "name": "Scarcity",
                "description": "People value things more when they're limited",
                "application": "Create urgency with limited offers"
            },
            {
                "id": "principle_004",
                "name": "Authority",
                "description": "People follow authority figures",
                "application": "Highlight expertise and credentials"
            },
            {
                "id": "principle_005",
                "name": "Reciprocity",
                "description": "People feel obligated to return favors",
                "application": "Provide value before asking for anything"
            }
        ]


@dataclass
class ServiceFixtures:
    """Fixtures for service tests"""
    
    def get_all_fixtures(self) -> Dict[str, Any]:
        """Get all service fixtures"""
        return {
            "mock_database": self.get_mock_database(),
            "mock_storage": self.get_mock_storage(),
            "mock_ai": self.get_mock_ai(),
            "sample_strategies": self.get_sample_strategies(),
            "sample_capabilities": self.get_sample_capabilities(),
            "load_test_fixtures": self.get_load_test_fixtures()
        }
    
    def get_mock_database(self) -> Dict[str, Any]:
        """Get mock database responses"""
        return {
            "onboarding_sessions": [
                {
                    "id": "session_001",
                    "workspace_id": "workspace_001",
                    "status": "active",
                    "current_step": 5
                },
                {
                    "id": "session_002",
                    "workspace_id": "workspace_002",
                    "status": "completed",
                    "current_step": 23
                }
            ],
            "evidence_items": [
                {
                    "id": "evi_001",
                    "session_id": "session_001",
                    "type": "financial",
                    "processed": True
                },
                {
                    "id": "evi_002",
                    "session_id": "session_001",
                    "type": "strategic",
                    "processed": False
                }
            ],
            "user_profiles": [
                {
                    "id": "user_001",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "CEO"
                }
            ]
        }
    
    def get_mock_storage(self) -> Dict[str, Any]:
        """Get mock storage responses"""
        return {
            "upload_response": {
                "status": "success",
                "file_id": "file_001",
                "url": "https://storage.example.com/file_001",
                "size": 1024000
            },
            "download_response": {
                "status": "success",
                "content": "Mock file content",
                "metadata": {
                    "type": "pdf",
                    "size": 1024000,
                    "created_at": "2023-12-01T10:00:00Z"
                }
            }
        }
    
    def get_mock_ai(self) -> Dict[str, Any]:
        """Get mock AI responses"""
        return {
            "classification_response": {
                "status": "success",
                "document_type": "financial",
                "confidence": 0.95,
                "categories": ["finance", "reporting", "quarterly"]
            },
            "extraction_response": {
                "status": "success",
                "facts": [
                    {"label": "Revenue", "value": "$10M", "confidence": 0.9},
                    {"label": "Growth", "value": "25%", "confidence": 0.85}
                ],
                "total_facts": 2
            },
            "contradiction_response": {
                "status": "success",
                "contradictions": [],
                "consistency_score": 0.95
            },
            "generation_response": {
                "status": "success",
                "content": "AI-generated content for testing",
                "confidence": 0.8,
                "tokens_used": 150
            }
        }
    
    def get_sample_strategies(self) -> List[Dict[str, Any]]:
        """Get sample strategic options"""
        return [
            {
                "id": "strategy_001",
                "name": "Market Follower",
                "type": "safe",
                "risk_level": "low",
                "investment": 0.2,
                "expected_roi": 0.3,
                "description": "Conservative approach with proven methods"
            },
            {
                "id": "strategy_002",
                "name": "Smart Challenger",
                "type": "clever",
                "risk_level": "medium",
                "investment": 0.5,
                "expected_roi": 0.6,
                "description": "Innovative approach within acceptable risk"
            },
            {
                "id": "strategy_003",
                "name": "Market Disruptor",
                "type": "bold",
                "risk_level": "high",
                "investment": 0.8,
                "expected_roi": 0.9,
                "description": "Aggressive approach with high reward potential"
            }
        ]
    
    def get_sample_capabilities(self) -> List[Dict[str, Any]]:
        """Get sample capability assessments"""
        return [
            {
                "id": "cap_001",
                "name": "Product Development",
                "category": "technical",
                "proficiency": 0.8,
                "importance": 0.9,
                "level": "competitive",
                "maturity": "maturing"
            },
            {
                "id": "cap_002",
                "name": "Brand Building",
                "category": "marketing",
                "proficiency": 0.6,
                "importance": 0.7,
                "level": "competitive",
                "maturity": "developing"
            },
            {
                "id": "cap_003",
                "name": "Data Analytics",
                "category": "technical",
                "proficiency": 0.4,
                "importance": 0.8,
                "level": "table_stakes",
                "maturity": "developing"
            }
        ]
    
    def get_load_test_fixtures(self) -> Dict[str, Any]:
        """Get load testing fixtures"""
        return {
            "concurrent_requests": 10,
            "duration": 60,
            "ramp_up": 10,
            "test_scenarios": [
                {
                    "name": "Evidence Upload",
                    "endpoint": "/api/v1/onboarding/evidence",
                    "method": "POST",
                    "payload": {"file": "test.pdf"},
                    "expected_response_time": 2.0
                },
                {
                    "name": "Step Progress",
                    "endpoint": "/api/v1/onboarding/advance-step",
                    "method": "POST",
                    "payload": {"session_id": "test_session"},
                    "expected_response_time": 1.0
                },
                {
                    "name": "Agent Processing",
                    "endpoint": "/api/v1/onboarding/process-step",
                    "method": "POST",
                    "payload": {"agent": "evidence_classifier"},
                    "expected_response_time": 5.0
                }
            ]
        }


# Export fixtures
__all__ = ["OnboardingFixtures", "AgentFixtures", "ServiceFixtures"]
