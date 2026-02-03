"""
Onboarding Domain - Service
Foundation and ICP generation logic
"""

import logging
from typing import Any, Dict, List, Optional

from infrastructure.database import get_supabase
from infrastructure.llm import get_llm

from .models import FoundationData, ICPProfile, OnboardingState

logger = logging.getLogger(__name__)


class OnboardingService:
    """Onboarding business logic"""

    def __init__(self):
        self.db = get_supabase()
        self.llm = get_llm()

    async def get_state(self, workspace_id: str) -> Optional[OnboardingState]:
        """Get onboarding state for workspace"""
        try:
            result = await self.db.select(
                "onboarding_states", {"workspace_id": workspace_id}
            )
            if result.data:
                return OnboardingState(**result.data[0])

            # Create initial state
            state_data = {
                "workspace_id": workspace_id,
                "current_step": "foundation",
                "completed_steps": [],
                "data": {},
            }
            result = await self.db.insert("onboarding_states", state_data)
            if result.data:
                return OnboardingState(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get onboarding state: {e}")
            return None

    async def save_foundation(
        self, workspace_id: str, data: Dict[str, Any]
    ) -> Optional[FoundationData]:
        """Save foundation data"""
        try:
            foundation_data = {
                "workspace_id": workspace_id,
                **data,
            }

            # Upsert foundation data
            result = await self.db.insert("foundation_data", foundation_data)
            if not result.data:
                return None

            # Update onboarding state
            await self.db.update(
                "onboarding_states",
                {
                    "current_step": "icp",
                    "completed_steps": ["foundation"],
                },
                {"workspace_id": workspace_id},
            )

            return FoundationData(**result.data[0])
        except Exception as e:
            logger.error(f"Failed to save foundation: {e}")
            return None

    async def get_foundation(self, workspace_id: str) -> Optional[FoundationData]:
        """Get foundation data"""
        try:
            result = await self.db.select(
                "foundation_data", {"workspace_id": workspace_id}
            )
            if result.data:
                return FoundationData(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get foundation: {e}")
            return None

    async def generate_icps(self, workspace_id: str) -> List[ICPProfile]:
        """Generate ICPs from foundation data"""
        try:
            # Get foundation data
            foundation = await self.get_foundation(workspace_id)
            if not foundation:
                return []

            # Generate ICPs using LLM
            prompt = f"""
            Based on this business information, create 3 Ideal Customer Profiles (ICPs):

            Company: {foundation.company_name}
            Industry: {foundation.industry}
            Description: {foundation.description}
            Target Audience: {foundation.target_audience}
            Value Proposition: {foundation.value_proposition}

            For each ICP, provide:
            1. Name (descriptive title)
            2. Description
            3. Firmographics (company size, industry, revenue)
            4. Pain points (3-5 items)
            5. Buying triggers (3-5 items)

            Return as JSON array with fields: name, description, firmographics (object), pain_points (array), triggers (array)
            """

            response = await self.llm.generate(prompt)
            if not response:
                return []

            # Parse response
            import json

            try:
                icps_data = json.loads(response)
            except json.JSONDecodeError:
                return []

            # Save ICPs
            created_icps = []
            for icp_data in icps_data[:3]:  # Max 3 ICPs
                icp_record = {
                    "workspace_id": workspace_id,
                    "name": icp_data["name"],
                    "description": icp_data["description"],
                    "firmographics": icp_data.get("firmographics", {}),
                    "pain_points": icp_data.get("pain_points", []),
                    "triggers": icp_data.get("triggers", []),
                }

                result = await self.db.insert("icp_profiles", icp_record)
                if result.data:
                    created_icps.append(ICPProfile(**result.data[0]))

            # Update onboarding state
            await self.db.update(
                "onboarding_states",
                {
                    "current_step": "complete",
                    "completed_steps": ["foundation", "icp"],
                },
                {"workspace_id": workspace_id},
            )

            return created_icps
        except Exception as e:
            logger.error(f"Failed to generate ICPs: {e}")
            return []

    async def get_icps(self, workspace_id: str) -> List[ICPProfile]:
        """Get ICPs for workspace"""
        try:
            result = await self.db.select(
                "icp_profiles", {"workspace_id": workspace_id}
            )
            return [ICPProfile(**item) for item in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Failed to get ICPs: {e}")
            return []


# Global instance
onboarding_service = OnboardingService()


def get_onboarding_service() -> OnboardingService:
    """Get onboarding service instance"""
    return onboarding_service
