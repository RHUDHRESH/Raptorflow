"""
Test Utilities
Supporting utilities for the comprehensive testing framework
"""

import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import random
import string
from unittest.mock import Mock, MagicMock
import uuid

logger = logging.getLogger(__name__)


@dataclass
class TestData:
    """Test data container"""
    company_info: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    competitors: List[Dict[str, Any]]
    market_analysis: Dict[str, Any]
    user_profiles: List[Dict[str, Any]]
    onboarding_sessions: List[Dict[str, Any]]


class TestDataGenerator:
    """Generates test data for various scenarios"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_company_info(self, size: str = "startup", industry: str = "technology") -> Dict[str, Any]:
        """Generate company information for testing"""
        sizes = ["startup", "small", "medium", "large", "enterprise"]
        industries = ["technology", "marketing", "finance", "healthcare", "retail"]
        
        company_names = [
            "TechCorp Solutions", "Digital Innovations", "Cloud Systems Inc",
            "DataDriven Analytics", "SmartTech Platforms", "NextGen Software"
        ]
        
        return {
            "name": random.choice(company_names),
            "size": size if size in sizes else random.choice(sizes),
            "industry": industry if industry in industries else random.choice(industries),
            "founded_year": random.randint(2010, 2020),
            "employee_count": random.randint(10, 1000),
            "revenue": random.uniform(100000, 10000000),
            "headquarters": f"{random.choice(['New York', 'San Francisco', 'Austin', 'Boston', 'Seattle'])}, USA",
            "target_market": random.choice(["B2B", "B2C", "B2B2C"]),
            "product_category": random.choice(["SaaS", "Platform", "Service", "Hardware"]),
            "growth_stage": random.choice(["early", "growth", "mature"]),
            "financial_resources": random.choice(["limited", "moderate", "strong"]),
            "innovation_capability": random.choice(["limited", "developing", "mature"]),
            "risk_tolerance": random.choice(["low", "medium", "high"]),
            "website": f"https://www.{uuid.uuid4().hex[:8]}.com",
            "description": f"Leading {random.choice(industries)} company specializing in innovative solutions"
        }
    
    def generate_evidence(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate evidence documents for testing"""
        evidence_types = ["financial", "legal", "marketing", "product", "strategic"]
        
        documents = []
        for i in range(count):
            doc_type = random.choice(evidence_types)
            documents.append({
                "id": f"doc_{i+1:03d}",
                "name": f"{doc_type.title()} Document {i+1}",
                "type": doc_type,
                "content": self._generate_document_content(doc_type),
                "source": random.choice(["upload", "url", "text"]),
                "confidence": random.uniform(0.7, 1.0),
                "created_at": datetime.now().isoformat(),
                "metadata": {
                    "size": random.randint(1000, 10000),
                    "pages": random.randint(1, 20),
                    "format": random.choice(["pdf", "docx", "txt"])
                }
            })
        
        return documents
    
    def _generate_document_content(self, doc_type: str) -> str:
        """Generate realistic document content"""
        content_templates = {
            "financial": f"""
            Financial Report Q{random.randint(1, 4)} {random.randint(2020, 2023)}
            
            Revenue: ${random.randint(1000000, 10000000):,}
            Profit: ${random.randint(100000, 1000000):,}
            Expenses: ${random.randint(500000, 5000000):,}
            
            Key Metrics:
            - Growth Rate: {random.uniform(0.1, 0.3):.1%}
            - Profit Margin: {random.uniform(0.1, 0.25):.1%}
            - ROI: {random.uniform(0.15, 0.35):.1%}
            """,
            "legal": f"""
            Legal Agreement - {random.choice(['Partnership', 'Service', 'Employment'])}
            
            This agreement is made on {datetime.now().strftime('%B %d, %Y')}
            
            Parties:
            - Company A: {random.choice(['TechCorp', 'DataInc', 'CloudSys'])}
            - Company B: {random.choice(['PartnerCo', 'ServicePro', 'SolutionLtd'])}
            
            Terms:
            - Duration: {random.randint(1, 5)} years
            - Value: ${random.randint(10000, 100000):,}
            - Jurisdiction: {random.choice(['Delaware', 'California', 'New York'])}
            """,
            "marketing": f"""
            Marketing Campaign Analysis
            
            Campaign: {random.choice(['Q1 Launch', 'Summer Promotion', 'Holiday Special'])}
            
            Performance Metrics:
            - Impressions: {random.randint(100000, 1000000):,}
            - Clicks: {random.randint(1000, 10000):,}
            - Conversions: {random.randint(100, 1000):,}
            - CPA: ${random.randint(50, 500):,}
            
            Target Audience: {random.choice(['B2B SaaS', 'E-commerce', 'Healthcare'])}
            Channels: {random.choice(['Social Media', 'Email', 'Search', 'Display'])}
            """,
            "product": f"""
            Product Specification Document
            
            Product: {random.choice(['Platform Pro', 'Analytics Suite', 'Cloud Service'])}
            
            Features:
            - {random.choice(['AI-powered', 'Real-time', 'Scalable'])} analytics
            - {random.choice(['Advanced', 'Intelligent', 'Automated'])} reporting
            - {random.choice(['Secure', 'Enterprise-grade', 'Bank-level'])} security
            
            Technical Specs:
            - Response Time: <{random.randint(100, 500)}ms
            - Uptime: {random.uniform(99.5, 99.9):.1f}%
            - Scalability: {random.randint(1000, 100000):,} users
            """,
            "strategic": f"""
            Strategic Plan {random.randint(2023, 2025)}
            
            Mission: To {random.choice(['revolutionize', 'transform', 'innovate'])} the {random.choice(['industry', 'market', 'sector'])}
            
            Strategic Objectives:
            1. {random.choice(['Increase', 'Expand', 'Grow'])} market share by {random.randint(10, 50)}%
            2. {random.choice(['Launch', 'Develop', 'Create'])} {random.randint(1, 5)} new products
            3. {random.choice(['Enter', 'Expand to', 'Penetrate'])} {random.randint(1, 3)} new markets
            
            Key Initiatives:
            - {random.choice(['Digital', 'Technology', 'Product'])} transformation
            - {random.choice(['Market', 'Customer', 'Brand'])} expansion
            - {random.choice(['Operational', 'Process', 'Cost'])} optimization
            """
        }
        
        return content_templates.get(doc_type, "Sample document content for testing purposes.")
    
    def generate_competitors(self, count: int = 3) -> List[Dict[str, Any]]:
        """Generate competitor data for testing"""
        competitor_names = [
            "CompetitorA Corp", "RivalTech Inc", "MarketLeader Ltd",
            "IndustryGiant Co", "StartupDisruptor", "EnterpriseSolution"
        ]
        
        competitors = []
        for i in range(count):
            competitors.append({
                "id": f"competitor_{i+1}",
                "name": random.choice(competitor_names),
                "website": f"https://www.{uuid.uuid4().hex[:8]}.com",
                "description": f"Leading {random.choice(['technology', 'marketing', 'sales'])} company",
                "size": random.choice(["startup", "small", "medium", "large", "enterprise"]),
                "founded_year": random.randint(1995, 2020),
                "employee_count": random.randint(50, 5000),
                "revenue": random.uniform(500000, 50000000),
                "market_share": random.uniform(0.01, 0.3),
                "strengths": random.sample([
                    "Brand recognition", "Technology leadership", "Market presence",
                    "Customer base", "Product quality", "Innovation capability"
                ], k=random.randint(2, 4)),
                "weaknesses": random.sample([
                    "High prices", "Limited features", "Poor support",
                    "Slow innovation", "Complex interface", "Limited scalability"
                ], k=random.randint(1, 3)),
                "key_products": random.sample([
                    "Core Platform", "Analytics Suite", "Mobile App",
                    "API Services", "Enterprise Solution", "Professional Services"
                ], k=random.randint(2, 4))
            })
        
        return competitors
    
    def generate_market_analysis(self) -> Dict[str, Any]:
        """Generate market analysis data"""
        return {
            "market_size": random.uniform(1000000000, 10000000000),
            "growth_rate": random.uniform(0.05, 0.25),
            "competition_level": random.choice(["low", "moderate", "high"]),
            "technological_change": random.choice(["slow", "moderate", "rapid"]),
            "customer_demand": random.choice(["declining", "stable", "growing"]),
            "barriers_to_entry": random.choice(["low", "medium", "high"]),
            "profit_margins": random.choice(["low", "average", "high"]),
            "market_trends": [
                "AI integration",
                "Cloud migration",
                "Data privacy focus",
                "Mobile-first approach",
                "Subscription models"
            ],
            "customer_segments": [
                {
                    "name": "Small Business",
                    "size": random.uniform(100000, 1000000),
                    "growth": random.uniform(0.1, 0.3)
                },
                {
                    "name": "Mid-Market",
                    "size": random.uniform(1000000, 10000000),
                    "growth": random.uniform(0.05, 0.2)
                },
                {
                    "name": "Enterprise",
                    "size": random.uniform(10000000, 100000000),
                    "growth": random.uniform(0.02, 0.15)
                }
            ]
        }
    
    def generate_user_profiles(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate user profile data"""
        first_names = ["John", "Jane", "Mike", "Sarah", "David", "Emily", "Chris", "Lisa"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        
        profiles = []
        for i in range(count):
            profiles.append({
                "id": f"user_{i+1:03d}",
                "name": f"{random.choice(first_names)} {random.choice(last_names)}",
                "email": f"user{i+1}@example.com",
                "role": random.choice(["CEO", "CTO", "CMO", "Founder", "VP Marketing", "Director"]),
                "company": f"Company {i+1}",
                "experience": random.randint(1, 20),
                "preferences": {
                    "communication_style": random.choice(["formal", "casual", "technical"]),
                    "meeting_frequency": random.choice(["weekly", "biweekly", "monthly"]),
                    "decision_making": random.choice(["analytical", "intuitive", "collaborative"])
                },
                "onboarding_progress": {
                    "current_step": random.randint(1, 23),
                    "completed_steps": random.randint(0, 22),
                    "last_active": datetime.now().isoformat()
                }
            })
        
        return profiles
    
    def generate_onboarding_sessions(self, count: int = 3) -> List[Dict[str, Any]]:
        """Generate onboarding session data"""
        sessions = []
        for i in range(count):
            sessions.append({
                "id": f"session_{i+1:03d}",
                "workspace_id": f"workspace_{i+1}",
                "user_id": f"user_{i+1}",
                "status": random.choice(["active", "completed", "paused"]),
                "current_step": random.randint(1, 23),
                "completed_steps": random.randint(0, 22),
                "progress_percentage": random.uniform(0, 100),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "step_data": {
                    f"step_{random.randint(1, 23)}": {
                        "status": "completed",
                        "data": {"sample": "data"},
                        "completed_at": datetime.now().isoformat()
                    }
                }
            })
        
        return sessions
    
    def generate_test_dataset(self) -> TestData:
        """Generate complete test dataset"""
        return TestData(
            company_info=self.generate_company_info(),
            evidence=self.generate_evidence(),
            competitors=self.generate_competitors(),
            market_analysis=self.generate_market_analysis(),
            user_profiles=self.generate_user_profiles(),
            onboarding_sessions=self.generate_onboarding_sessions()
        )


class MockServices:
    """Mock services for testing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_mock_vertex_ai(self):
        """Get mock Vertex AI service"""
        mock_ai = Mock()
        mock_ai.generate_text.return_value = {
            "status": "success",
            "text": "Mock AI response for testing"
        }
        return mock_ai
    
    def get_mock_ocr_service(self):
        """Get mock OCR service"""
        mock_ocr = Mock()
        mock_ocr.extract_text.return_value = Mock(
            extracted_text="Mock OCR text",
            confidence_score=0.9,
            page_count=1
        )
        return mock_ocr
    
    def get_mock_storage_service(self):
        """Get mock storage service"""
        mock_storage = Mock()
        mock_storage.upload_file.return_value = {
            "status": "success",
            "file_id": f"file_{uuid.uuid4().hex[:8]}"
        }
        return mock_storage
    
    def get_mock_database(self):
        """Get mock database service"""
        mock_db = Mock()
        mock_db.query.return_value = [
            {"id": 1, "name": "Test Data 1"},
            {"id": 2, "name": "Test Data 2"}
        ]
        return mock_db
    
    def get_mock_reddit_api(self):
        """Get mock Reddit API"""
        mock_reddit = Mock()
        mock_reddit.get_posts.return_value = [
            {
                "id": "post1",
                "title": "Test Post 1",
                "content": "Test content 1",
                "score": 100,
                "comments": 50
            },
            {
                "id": "post2", 
                "title": "Test Post 2",
                "content": "Test content 2",
                "score": 200,
                "comments": 75
            }
        ]
        return mock_reddit


class TestAssertions:
    """Custom assertion methods for testing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def assert_company_info_valid(self, company_info: Dict[str, Any]):
        """Assert company info is valid"""
        required_fields = ["name", "size", "industry", "founded_year"]
        for field in required_fields:
            assert field in company_info, f"Missing required field: {field}"
            assert company_info[field] is not None, f"Field {field} cannot be None"
    
    def assert_evidence_valid(self, evidence: List[Dict[str, Any]]):
        """Assert evidence list is valid"""
        assert isinstance(evidence, list), "Evidence should be a list"
        for item in evidence:
            assert "id" in item, "Evidence item missing id"
            assert "type" in item, "Evidence item missing type"
            assert "content" in item, "Evidence item missing content"
    
    def assert_competitors_valid(self, competitors: List[Dict[str, Any]]):
        """Assert competitors list is valid"""
        assert isinstance(competitors, list), "Competitors should be a list"
        for competitor in competitors:
            assert "name" in competitor, "Competitor missing name"
            assert "market_share" in competitor, "Competitor missing market_share"
            assert 0 <= competitor["market_share"] <= 1, "Market share should be between 0 and 1"
    
    def assert_onboarding_progress_valid(self, progress: Dict[str, Any]):
        """Assert onboarding progress is valid"""
        assert "current_step" in progress, "Missing current_step"
        assert "completed_steps" in progress, "Missing completed_steps"
        assert 1 <= progress["current_step"] <= 23, "Current step should be between 1 and 23"
        assert 0 <= progress["completed_steps"] <= 22, "Completed steps should be between 0 and 22"
    
    def assert_api_response_valid(self, response: Dict[str, Any]):
        """Assert API response is valid"""
        assert "status" in response, "API response missing status"
        assert "data" in response, "API response missing data"
        assert response["status"] in ["success", "error"], "Invalid status value"
    
    def assert_agent_result_valid(self, result: Any, agent_type: str):
        """Assert agent result is valid"""
        assert result is not None, f"{agent_type} agent returned None result"
        
        if hasattr(result, '__dict__'):
            # Check for common agent result attributes
            result_dict = result.__dict__
            if "confidence" in result_dict:
                assert 0 <= result_dict["confidence"] <= 1, "Confidence should be between 0 and 1"
            if "status" in result_dict:
                assert result_dict["status"] in ["success", "error", "processing"], "Invalid status value"
    
    def assert_performance_within_bounds(self, execution_time: float, max_time: float):
        """Assert performance is within acceptable bounds"""
        assert execution_time <= max_time, f"Execution time {execution_time}s exceeds maximum {max_time}s"
    
    def assert_coverage_threshold_met(self, coverage_percentage: float, threshold: float):
        """Assert code coverage meets threshold"""
        assert coverage_percentage >= threshold, f"Coverage {coverage_percentage}% below threshold {threshold}%"
    
    def assert_data_quality_score(self, score: float, min_score: float):
        """Assert data quality score meets minimum"""
        assert score >= min_score, f"Data quality score {score} below minimum {min_score}"
    
    def assert_workflow_step_valid(self, step_data: Dict[str, Any], step_number: int):
        """Assert workflow step data is valid"""
        assert "step_number" in step_data, "Missing step_number"
        assert "status" in step_data, "Missing status"
        assert step_data["step_number"] == step_number, f"Step number mismatch: expected {step_number}, got {step_data['step_number']}"
        assert step_data["status"] in ["pending", "in_progress", "completed", "failed"], "Invalid step status"


# Export utilities
__all__ = ["TestDataGenerator", "MockServices", "TestAssertions", "TestData"]
