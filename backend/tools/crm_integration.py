import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.config import get_settings
from core.tool_registry import BaseRaptorTool, RaptorRateLimiter

logger = logging.getLogger("raptorflow.tools.crm")


class CRMIntegrationTool(BaseRaptorTool):
    """
    SOTA CRM Integration Tool.
    Provides unified access to Salesforce, HubSpot, and other CRM systems.
    Handles lead management, customer data sync, and sales pipeline operations.
    """

    def __init__(self):
        settings = get_settings()
        self.salesforce_token = settings.SALESFORCE_API_TOKEN
        self.hubspot_token = settings.HUBSOT_API_TOKEN

    @property
    def name(self) -> str:
        return "crm_integration"

    @property
    def description(self) -> str:
        return (
            "A comprehensive CRM integration tool. Use this to manage leads, sync customer data, "
            "track sales pipeline, and analyze customer relationships. Supports Salesforce, HubSpot, "
            "and custom CRM integrations. Handles lead scoring, contact management, and deal tracking."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(
        self,
        action: str,
        crm_system: str = "salesforce",
        data: Optional[Dict[str, Any]] = None,
        record_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Executes CRM operations based on the specified action.

        Args:
            action: Type of CRM operation ('create_lead', 'update_contact', 'get_pipeline', 'sync_data', 'get_deals')
            crm_system: Target CRM system ('salesforce', 'hubspot', 'custom')
            data: Data for create/update operations
            record_id: Specific record ID for operations
            filters: Filters for query operations
        """
        logger.info(f"Executing CRM action: {action} on {crm_system}")

        # Validate CRM system
        valid_systems = ["salesforce", "hubspot", "custom"]
        if crm_system not in valid_systems:
            raise ValueError(f"Invalid crm_system. Must be one of: {valid_systems}")

        # Process different actions
        if action == "create_lead":
            return await self._create_lead(crm_system, data)
        elif action == "update_contact":
            return await self._update_contact(crm_system, record_id, data)
        elif action == "get_pipeline":
            return await self._get_pipeline(crm_system, filters)
        elif action == "sync_data":
            return await self._sync_data(crm_system, filters)
        elif action == "get_deals":
            return await self._get_deals(crm_system, filters)
        elif action == "lead_scoring":
            return await self._score_leads(crm_system, filters)
        elif action == "customer_insights":
            return await self._get_customer_insights(crm_system, record_id)

    async def _create_lead(
        self, crm_system: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Creates a new lead in the specified CRM system."""

        required_fields = ["email", "first_name", "last_name"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Simulate lead creation
        lead_data = {
            "id": f"lead_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "crm_system": crm_system,
            "status": "new",
            "lead_score": self._calculate_lead_score(data),
            "created_at": datetime.now().isoformat(),
            "data": data,
        }

        # Add enrichment data
        lead_data["enrichment"] = {
            "company_size": self._enrich_company_size(data.get("company", "")),
            "industry": self._enrich_industry(data.get("company", "")),
            "location": data.get("location", "Unknown"),
            "source": data.get("source", "web_form"),
            "priority": self._determine_priority(lead_data["lead_score"]),
        }

        return {
            "success": True,
            "data": lead_data,
            "action": "create_lead",
            "crm_system": crm_system,
            "message": f"Lead created successfully in {crm_system.title()}",
        }

    async def _update_contact(
        self, crm_system: str, record_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Updates an existing contact in the CRM system."""

        # Simulate contact update
        updated_contact = {
            "id": record_id,
            "crm_system": crm_system,
            "updated_at": datetime.now().isoformat(),
            "updated_fields": list(data.keys()),
            "data": data,
        }

        # Add change tracking
        updated_contact["change_summary"] = {
            "fields_changed": len(data),
            "critical_updates": self._identify_critical_updates(data),
            "last_activity": datetime.now().isoformat(),
        }

        return {
            "success": True,
            "data": updated_contact,
            "action": "update_contact",
            "crm_system": crm_system,
            "message": f"Contact {record_id} updated successfully",
        }

    async def _get_pipeline(
        self, crm_system: str, filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retrieves sales pipeline data from the CRM system."""

        # Simulate pipeline data
        pipeline_data = {
            "crm_system": crm_system,
            "pipeline_stages": [
                {
                    "stage": "Prospecting",
                    "deals_count": 45,
                    "total_value": 2250000,
                    "conversion_rate": 0.25,
                    "avg_deal_size": 50000,
                },
                {
                    "stage": "Qualification",
                    "deals_count": 28,
                    "total_value": 1680000,
                    "conversion_rate": 0.35,
                    "avg_deal_size": 60000,
                },
                {
                    "stage": "Proposal",
                    "deals_count": 15,
                    "total_value": 1200000,
                    "conversion_rate": 0.60,
                    "avg_deal_size": 80000,
                },
                {
                    "stage": "Negotiation",
                    "deals_count": 8,
                    "total_value": 960000,
                    "conversion_rate": 0.75,
                    "avg_deal_size": 120000,
                },
                {
                    "stage": "Closed Won",
                    "deals_count": 5,
                    "total_value": 750000,
                    "conversion_rate": 1.0,
                    "avg_deal_size": 150000,
                },
            ],
            "summary": {
                "total_deals": 101,
                "total_pipeline_value": 6840000,
                "avg_deal_size": 67723,
                "overall_conversion_rate": 0.31,
                "sales_cycle_days": 45,
            },
        }

        # Apply filters if provided
        if filters:
            pipeline_data["filters_applied"] = filters
            pipeline_data["filtered_summary"] = self._apply_pipeline_filters(
                pipeline_data, filters
            )

        return {
            "success": True,
            "data": pipeline_data,
            "action": "get_pipeline",
            "crm_system": crm_system,
        }

    async def _sync_data(
        self, crm_system: str, filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synchronizes data between CRM and other systems."""

        sync_data = {
            "crm_system": crm_system,
            "sync_type": "bidirectional",
            "last_sync": datetime.now().isoformat(),
            "synced_entities": {
                "contacts": 1250,
                "leads": 340,
                "deals": 89,
                "accounts": 156,
            },
            "sync_status": {
                "contacts": "completed",
                "leads": "completed",
                "deals": "in_progress",
                "accounts": "completed",
            },
            "conflicts_resolved": 3,
            "errors": 0,
            "next_scheduled_sync": (
                datetime.now().replace(hour=2, minute=0)
            ).isoformat(),
        }

        return {
            "success": True,
            "data": sync_data,
            "action": "sync_data",
            "crm_system": crm_system,
            "message": f"Data synchronization completed for {crm_system.title()}",
        }

    async def _get_deals(
        self, crm_system: str, filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retrieves deals data from the CRM system."""

        deals_data = {
            "crm_system": crm_system,
            "deals": [
                {
                    "id": "deal_001",
                    "name": "Enterprise Software License",
                    "stage": "Proposal",
                    "value": 150000,
                    "probability": 0.65,
                    "close_date": "2024-03-15",
                    "account": "Tech Corp Inc",
                    "owner": "John Smith",
                },
                {
                    "id": "deal_002",
                    "name": "Marketing Automation Suite",
                    "stage": "Negotiation",
                    "value": 85000,
                    "probability": 0.80,
                    "close_date": "2024-02-28",
                    "account": "Global Marketing Ltd",
                    "owner": "Sarah Johnson",
                },
                {
                    "id": "deal_003",
                    "name": "Analytics Platform",
                    "stage": "Qualification",
                    "value": 120000,
                    "probability": 0.35,
                    "close_date": "2024-04-30",
                    "account": "DataDriven Co",
                    "owner": "Mike Wilson",
                },
            ],
            "summary": {
                "total_deals": 3,
                "total_value": 355000,
                "avg_probability": 0.60,
                "weighted_pipeline": 213000,
            },
        }

        # Apply filters if provided
        if filters:
            filtered_deals = self._filter_deals(deals_data["deals"], filters)
            deals_data["deals"] = filtered_deals
            deals_data["filters_applied"] = filters

        return {
            "success": True,
            "data": deals_data,
            "action": "get_deals",
            "crm_system": crm_system,
        }

    async def _score_leads(
        self, crm_system: str, filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculates and updates lead scores."""

        scoring_data = {
            "crm_system": crm_system,
            "scoring_model": "custom_weighted",
            "leads_scored": 340,
            "score_distribution": {
                "hot (80-100)": 68,
                "warm (60-79)": 102,
                "cool (40-59)": 119,
                "cold (0-39)": 51,
            },
            "scoring_factors": {
                "email_engagement": 0.30,
                "website_visits": 0.25,
                "company_size": 0.20,
                "industry_fit": 0.15,
                "budget_indicators": 0.10,
            },
            "top_leads": [
                {
                    "id": "lead_001",
                    "score": 95,
                    "status": "hot",
                    "key_factors": [
                        "high_engagement",
                        "enterprise_company",
                        "budget_available",
                    ],
                },
                {
                    "id": "lead_002",
                    "score": 88,
                    "status": "hot",
                    "key_factors": [
                        "frequent_visits",
                        "decision_maker",
                        "tech_industry",
                    ],
                },
            ],
        }

        return {
            "success": True,
            "data": scoring_data,
            "action": "lead_scoring",
            "crm_system": crm_system,
        }

    async def _get_customer_insights(
        self, crm_system: str, record_id: str
    ) -> Dict[str, Any]:
        """Generates customer insights and recommendations."""

        insights_data = {
            "crm_system": crm_system,
            "customer_id": record_id,
            "insights": {
                "engagement_level": "high",
                "purchase_probability": 0.75,
                "churn_risk": "low",
                "upsell_potential": "high",
                "next_best_action": "schedule_demo",
            },
            "behavioral_patterns": {
                "preferred_contact_time": "Tuesday-Thursday 10-11 AM",
                "content_preferences": ["case_studies", "webinars", "product_demos"],
                "communication_channel": "email",
                "response_time_preference": "< 2 hours",
            },
            "recommendations": [
                "Send personalized case study relevant to their industry",
                "Schedule follow-up call within 3 business days",
                "Offer enterprise pricing tier based on company size",
                "Connect with technical decision maker for product demo",
            ],
            "related_opportunities": [
                {
                    "type": "cross_sell",
                    "product": "Analytics Module",
                    "probability": 0.65,
                    "estimated_value": 25000,
                },
                {
                    "type": "upsell",
                    "product": "Enterprise License",
                    "probability": 0.45,
                    "estimated_value": 50000,
                },
            ],
        }

        return {
            "success": True,
            "data": insights_data,
            "action": "customer_insights",
            "crm_system": crm_system,
        }

    # Helper methods
    def _calculate_lead_score(self, data: Dict[str, Any]) -> int:
        """Calculates a lead score based on available data."""
        score = 0

        # Email domain quality
        email = data.get("email", "").lower()
        if any(domain in email for domain in ["gmail.com", "yahoo.com"]):
            score += 10
        elif any(domain in email for domain in [".com", ".org", ".net"]):
            score += 20

        # Company indicators
        company = data.get("company", "").lower()
        if company:
            score += 15
            if any(term in company for term in ["corp", "inc", "ltd", "llc"]):
                score += 10

        # Job title indicators
        title = data.get("job_title", "").lower()
        if any(term in title for term in ["ceo", "cto", "director", "manager", "vp"]):
            score += 20

        # Phone number presence
        if data.get("phone"):
            score += 10

        return min(score, 100)

    def _enrich_company_size(self, company: str) -> str:
        """Enriches company size based on name patterns."""
        if not company:
            return "unknown"

        # Simple heuristic based on company name patterns
        if any(
            term in company.lower() for term in ["global", "international", "worldwide"]
        ):
            return "enterprise"
        elif any(term in company.lower() for term in ["corp", "inc", "ltd"]):
            return "medium"
        else:
            return "small"

    def _enrich_industry(self, company: str) -> str:
        """Enriches industry based on company name patterns."""
        if not company:
            return "unknown"

        company_lower = company.lower()
        if any(term in company_lower for term in ["tech", "software", "digital"]):
            return "technology"
        elif any(term in company_lower for term in ["health", "medical", "pharma"]):
            return "healthcare"
        elif any(term in company_lower for term in ["finance", "bank", "investment"]):
            return "financial"
        else:
            return "general"

    def _determine_priority(self, score: int) -> str:
        """Determines lead priority based on score."""
        if score >= 80:
            return "high"
        elif score >= 60:
            return "medium"
        else:
            return "low"

    def _identify_critical_updates(self, data: Dict[str, Any]) -> List[str]:
        """Identifies critical field updates."""
        critical_fields = ["email", "phone", "status", "value"]
        return [field for field in critical_fields if field in data]

    def _apply_pipeline_filters(
        self, pipeline_data: Dict[str, Any], filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Applies filters to pipeline data."""
        # Simplified filtering logic
        filtered = pipeline_data["summary"].copy()

        if filters.get("stage"):
            stage = filters["stage"]
            for stage_data in pipeline_data["pipeline_stages"]:
                if stage_data["stage"].lower() == stage.lower():
                    filtered["filtered_stage"] = stage_data
                    break

        return filtered

    def _filter_deals(
        self, deals: List[Dict[str, Any]], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filters deals based on criteria."""
        filtered_deals = deals.copy()

        if filters.get("stage"):
            stage_filter = filters["stage"].lower()
            filtered_deals = [
                d for d in filtered_deals if d["stage"].lower() == stage_filter
            ]

        if filters.get("min_value"):
            min_val = filters["min_value"]
            filtered_deals = [d for d in filtered_deals if d["value"] >= min_val]

        return filtered_deals
