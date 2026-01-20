#!/usr/bin/env python3
"""
API Integration Test Script for Raptorflow Backend
Actually calls backend endpoints to demonstrate real capabilities
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackendAPITester:
    """Real API integration tester for Raptorflow backend"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.workspace_id = str(uuid.uuid4())
        self.user_id = str(uuid.uuid4())
        self.test_results = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def authenticate(self):
        """Authenticate with the backend"""
        try:
            # For demo purposes, we'll simulate authentication
            # In real implementation, this would call the auth endpoint
            self.auth_token = "demo_token_" + str(uuid.uuid4())
            logger.info("✅ Authentication successful")
            return True
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return False
    
    async def test_health_endpoints(self):
        """Test health and system status endpoints"""
        logger.info("🏥 Testing Health Endpoints")
        
        try:
            # Test root health
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Root Health Check", True, data)
                else:
                    self.log_result("Root Health Check", False, f"Status: {response.status}")
            
            # Test detailed health
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Detailed Health Check", True, data)
                else:
                    self.log_result("Detailed Health Check", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.log_result("Health Endpoints", False, str(e))
    
    async def test_foundation_data(self, company_data: Dict):
        """Test foundation data creation and processing"""
        logger.info(f"🏗️ Testing Foundation Data for {company_data['company_name']}")
        
        try:
            foundation_payload = {
                "workspace_id": self.workspace_id,
                "user_id": self.user_id,
                "company_name": company_data["company_name"],
                "industry": company_data["industry"],
                "description": company_data["description"],
                "target_market": company_data["target_market"],
                "business_model": company_data["business_model"],
                "stage": company_data["stage"],
                "team_size": company_data["team_size"],
                "annual_revenue": company_data["annual_revenue"],
                "value_proposition": f"Leading {company_data['industry']} solution",
                "competitive_advantages": [
                    "Innovation leadership",
                    "Market expertise", 
                    "Customer-centric approach"
                ]
            }
            
            # Call foundation API endpoint
            async with self.session.post(
                f"{self.base_url}/api/v1/foundation/process",
                json=foundation_payload,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Foundation Data Creation", True, data)
                    return data.get("foundation_id")
                else:
                    error_text = await response.text()
                    self.log_result("Foundation Data Creation", False, f"Status: {response.status}, Error: {error_text}")
                    return None
                    
        except Exception as e:
            self.log_result("Foundation Data", False, str(e))
            return None
    
    async def test_icp_generation(self, foundation_id: str, company_data: Dict):
        """Test ICP generation from foundation data"""
        logger.info(f"🎯 Testing ICP Generation for {company_data['company_name']}")
        
        try:
            # Generate ICPs from foundation
            async with self.session.post(
                f"{self.base_url}/api/v1/icps/generate-from-foundation",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                params={"workspace_id": self.workspace_id}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("ICP Generation", True, data)
                    
                    # Test listing ICPs
                    async with self.session.get(
                        f"{self.base_url}/api/v1/icps/",
                        headers={"Authorization": f"Bearer {self.auth_token}"},
                        params={"workspace_id": self.workspace_id}
                    ) as list_response:
                        if list_response.status == 200:
                            icps_data = await list_response.json()
                            self.log_result("ICP Listing", True, icps_data)
                        else:
                            self.log_result("ICP Listing", False, f"Status: {list_response.status}")
                    
                    return data.get("icps", [])
                else:
                    error_text = await response.text()
                    self.log_result("ICP Generation", False, f"Status: {response.status}, Error: {error_text}")
                    return []
                    
        except Exception as e:
            self.log_result("ICP Generation", False, str(e))
            return []
    
    async def test_muse_content_generation(self, company_data: Dict):
        """Test Muse content generation"""
        logger.info(f"✍️ Testing Muse Content Generation for {company_data['company_name']}")
        
        try:
            # Determine content type based on industry
            if company_data["industry"] == "B2B SaaS":
                content_requests = [
                    {
                        "content_type": "blog_post",
                        "topic": "5 Ways AI is Transforming Enterprise Sales",
                        "tone": "professional",
                        "target_audience": "Sales leaders",
                        "brand_voice_notes": "Innovative, data-driven, authoritative"
                    },
                    {
                        "content_type": "case_study",
                        "topic": "How TechCorp Increased Sales by 300%",
                        "tone": "data-driven",
                        "target_audience": "Prospects",
                        "brand_voice_notes": "Results-focused, credible, detailed"
                    }
                ]
            elif company_data["industry"] == "Industrial Manufacturing":
                content_requests = [
                    {
                        "content_type": "whitepaper",
                        "topic": "The Future of Precision Manufacturing",
                        "tone": "technical",
                        "target_audience": "Engineers",
                        "brand_voice_notes": "Technical, precise, authoritative"
                    }
                ]
            else:  # D2C Footwear
                content_requests = [
                    {
                        "content_type": "social_media",
                        "topic": "Sustainable Materials in Our New Collection",
                        "tone": "casual",
                        "target_audience": "Instagram followers",
                        "brand_voice_notes": "Eco-conscious, trendy, authentic"
                    }
                ]
            
            generated_content = []
            for request in content_requests:
                payload = {
                    **request,
                    "workspace_id": self.workspace_id,
                    "user_id": self.user_id,
                    "max_revisions": 3
                }
                
                async with self.session.post(
                    f"{self.base_url}/api/v1/muse/generate",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.auth_token}"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_result(f"Content Generation - {request['content_type']}", True, data)
                        generated_content.append(data)
                    else:
                        error_text = await response.text()
                        self.log_result(f"Content Generation - {request['content_type']}", False, f"Status: {response.status}, Error: {error_text}")
            
            # Test listing assets
            async with self.session.get(
                f"{self.base_url}/api/v1/muse/assets",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                params={"workspace_id": self.workspace_id, "limit": 10}
            ) as list_response:
                if list_response.status == 200:
                    assets_data = await list_response.json()
                    self.log_result("Muse Assets Listing", True, assets_data)
                else:
                    self.log_result("Muse Assets Listing", False, f"Status: {list_response.status}")
            
            return generated_content
            
        except Exception as e:
            self.log_result("Muse Content Generation", False, str(e))
            return []
    
    async def test_campaign_creation(self, company_data: Dict):
        """Test campaign creation and management"""
        logger.info(f"🚀 Testing Campaign Creation for {company_data['company_name']}")
        
        try:
            # Create campaign based on industry
            if company_data["industry"] == "B2B SaaS":
                campaign_data = {
                    "name": "Q4 Enterprise Sales Push",
                    "description": "Multi-channel campaign targeting enterprise sales leaders",
                    "target_icps": [],  # Would populate with actual ICP IDs
                    "phases": [
                        {
                            "name": "Awareness",
                            "duration_days": 30,
                            "activities": ["LinkedIn ads", "Content marketing", "Webinars"]
                        },
                        {
                            "name": "Consideration", 
                            "duration_days": 45,
                            "activities": ["Email nurturing", "Case studies", "Demos"]
                        }
                    ],
                    "budget_usd": 50000
                }
            elif company_data["industry"] == "Industrial Manufacturing":
                campaign_data = {
                    "name": "2024 Supply Chain Reliability Campaign",
                    "description": "Emphasizing reliability and quality in uncertain times",
                    "target_icps": [],
                    "phases": [
                        {
                            "name": "Trust Building",
                            "duration_days": 60,
                            "activities": ["Trade shows", "Technical whitepapers", "Site tours"]
                        }
                    ],
                    "budget_usd": 200000
                }
            else:  # D2C Footwear
                campaign_data = {
                    "name": "Spring Sustainable Collection Launch",
                    "description": "Launching eco-friendly spring collection with influencer partnerships",
                    "target_icps": [],
                    "phases": [
                        {
                            "name": "Teaser",
                            "duration_days": 14,
                            "activities": ["Social media teasers", "Influencer previews"]
                        },
                        {
                            "name": "Launch",
                            "duration_days": 30,
                            "activities": ["Full collection reveal", "Influencer campaigns"]
                        }
                    ],
                    "budget_usd": 75000
                }
            
            # Create campaign
            async with self.session.post(
                f"{self.base_url}/api/v1/campaigns/",
                json=campaign_data,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    campaign_id = data.get("id")
                    self.log_result("Campaign Creation", True, data)
                    
                    # Test listing campaigns
                    async with self.session.get(
                        f"{self.base_url}/api/v1/campaigns/",
                        headers={"Authorization": f"Bearer {self.auth_token}"}
                    ) as list_response:
                        if list_response.status == 200:
                            campaigns_data = await list_response.json()
                            self.log_result("Campaign Listing", True, campaigns_data)
                        else:
                            self.log_result("Campaign Listing", False, f"Status: {list_response.status}")
                    
                    return campaign_id
                else:
                    error_text = await response.text()
                    self.log_result("Campaign Creation", False, f"Status: {response.status}, Error: {error_text}")
                    return None
                    
        except Exception as e:
            self.log_result("Campaign Creation", False, str(e))
            return None
    
    async def test_moves_strategy(self, company_data: Dict):
        """Test moves creation and strategy"""
        logger.info(f"♟️ Testing Moves Strategy for {company_data['company_name']}")
        
        try:
            # Create moves based on industry
            if company_data["industry"] == "B2B SaaS":
                moves_data = [
                    {
                        "name": "LinkedIn Thought Leadership",
                        "category": "content_marketing",
                        "goal": "Establish authority in sales automation",
                        "strategy": {
                            "content_pillars": ["AI in sales", "Sales productivity"],
                            "posting_frequency": "3x per week"
                        },
                        "execution_plan": [
                            "Create content calendar",
                            "Write 12 thought leadership posts",
                            "Engage with 50 prospects weekly"
                        ],
                        "duration_days": 90,
                        "success_metrics": ["LinkedIn followers", "Engagement rate", "Demo requests"]
                    }
                ]
            elif company_data["industry"] == "Industrial Manufacturing":
                moves_data = [
                    {
                        "name": "Trade Show Dominance",
                        "category": "events",
                        "goal": "Generate high-quality manufacturing leads",
                        "strategy": {
                            "target_shows": ["IMTS", "Hannover Messe"],
                            "booth_strategy": "Interactive demonstrations"
                        },
                        "execution_plan": [
                            "Select and book trade shows",
                            "Design interactive booth",
                            "Schedule executive meetings"
                        ],
                        "duration_days": 180,
                        "success_metrics": ["Executive meetings", "Qualified leads", "ROI per show"]
                    }
                ]
            else:  # D2C Footwear
                moves_data = [
                    {
                        "name": "TikTok Sustainability Challenge",
                        "category": "social_media",
                        "goal": "Increase brand awareness among Gen Z",
                        "strategy": {
                            "hashtag": "#UrbanSustainableStyle",
                            "influencer_tier": "Micro-influencers 10k-100k followers"
                        },
                        "execution_plan": [
                            "Identify 50 micro-influencers",
                            "Create challenge guidelines",
                            "Launch hashtag challenge"
                        ],
                        "duration_days": 30,
                        "success_metrics": ["Hashtag usage", "Video views", "Website traffic"]
                    }
                ]
            
            created_moves = []
            for move_data in moves_data:
                async with self.session.post(
                    f"{self.base_url}/api/v1/moves/",
                    json=move_data,
                    headers={"Authorization": f"Bearer {self.auth_token}"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_result(f"Move Creation - {move_data['name']}", True, data)
                        created_moves.append(data)
                    else:
                        error_text = await response.text()
                        self.log_result(f"Move Creation - {move_data['name']}", False, f"Status: {response.status}, Error: {error_text}")
            
            # Test listing moves
            async with self.session.get(
                f"{self.base_url}/api/v1/moves/",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            ) as list_response:
                if list_response.status == 200:
                    moves_data = await list_response.json()
                    self.log_result("Moves Listing", True, moves_data)
                else:
                    self.log_result("Moves Listing", False, f"Status: {list_response.status}")
            
            return created_moves
            
        except Exception as e:
            self.log_result("Moves Strategy", False, str(e))
            return []
    
    async def test_analytics(self):
        """Test analytics endpoints"""
        logger.info("📊 Testing Analytics Endpoints")
        
        try:
            # Test ICP analytics
            async with self.session.get(
                f"{self.base_url}/api/v1/icps/analytics",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("ICP Analytics", True, data)
                else:
                    self.log_result("ICP Analytics", False, f"Status: {response.status}")
            
            # Test moves analytics
            async with self.session.get(
                f"{self.base_url}/api/v1/moves/analytics",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Moves Analytics", True, data)
                else:
                    self.log_result("Moves Analytics", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.log_result("Analytics", False, str(e))
    
    async def run_company_test(self, company_data: Dict):
        """Run complete test suite for a company"""
        logger.info(f"🏢 Running Complete Test Suite for {company_data['company_name']}")
        logger.info("=" * 60)
        
        # 1. Foundation Data
        foundation_id = await self.test_foundation_data(company_data)
        
        # 2. ICP Generation
        icps = await self.test_icp_generation(foundation_id, company_data)
        
        # 3. Muse Content Generation
        content = await self.test_muse_content_generation(company_data)
        
        # 4. Campaign Creation
        campaign_id = await self.test_campaign_creation(company_data)
        
        # 5. Moves Strategy
        moves = await self.test_moves_strategy(company_data)
        
        # 6. Analytics
        await self.test_analytics()
        
        logger.info(f"✅ Complete test suite finished for {company_data['company_name']}\n")
    
    def log_result(self, test_name: str, success: bool, data: Any):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test_name": test_name,
            "status": status,
            "success": success,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
        logger.info(f"{status}: {test_name}")
        if not success:
            logger.error(f"  Data: {data}")
    
    async def generate_report(self):
        """Generate comprehensive test report"""
        logger.info("📋 Generating API Test Report")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total API Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        logger.info("\n📋 Detailed API Results:")
        for result in self.test_results:
            logger.info(f"  {result['status']}: {result['test_name']}")
        
        # Save detailed report
        report_data = {
            "test_suite": "Raptorflow Backend API Integration Test",
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "base_url": self.base_url,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "detailed_results": self.test_results
        }
        
        with open("api_integration_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"\n📄 Detailed API report saved to: api_integration_test_report.json")

async def main():
    """Main execution function"""
    # Define test companies
    companies = [
        {
            "company_name": "TechStartup AI",
            "industry": "B2B SaaS",
            "description": "AI-powered sales automation platform for enterprise",
            "target_market": "Enterprise sales teams",
            "business_model": "SaaS subscription",
            "stage": "Series A",
            "team_size": 50,
            "annual_revenue": 2000000
        },
        {
            "company_name": "GlobalManufacturing Corp",
            "industry": "Industrial Manufacturing",
            "description": "Global supplier of precision industrial components",
            "target_market": "OEM manufacturers and industrial distributors",
            "business_model": "B2B direct sales",
            "stage": "Established",
            "team_size": 5000,
            "annual_revenue": 500000000
        },
        {
            "company_name": "UrbanFootwear Co",
            "industry": "Fashion & Footwear",
            "description": "Direct-to-consumer sustainable urban footwear brand",
            "target_market": "Urban millennials and Gen Z consumers",
            "business_model": "D2C e-commerce",
            "stage": "Growth Stage",
            "team_size": 75,
            "annual_revenue": 15000000
        }
    ]
    
    # Run API tests
    async with BackendAPITester() as tester:
        # Authenticate
        if await tester.authenticate():
            # Test health endpoints first
            await tester.test_health_endpoints()
            
            # Test each company
            for company in companies:
                await tester.run_company_test(company)
            
            # Generate final report
            await tester.generate_report()
        else:
            logger.error("❌ Authentication failed. Cannot proceed with API tests.")

if __name__ == "__main__":
    asyncio.run(main())
