"""
Onboarding service for business logic operations
Handles onboarding-related business logic and validation
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from backend.core.models import ValidationError
from backend.core.supabase_mgr import get_supabase_client
from backend.db.evidence import EvidenceRepository
from backend.db.foundations import FoundationRepository
from backend.db.repositories.onboarding import OnboardingRepository


class OnboardingService:
    """Service for onboarding business logic"""

    def __init__(self):
        self.repository = OnboardingRepository()
        self.evidence_repository = EvidenceRepository()
        self.foundation_repository = FoundationRepository()
        self.supabase = get_supabase_client()

    async def get_or_create_session(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get existing onboarding session or create new one

        Args:
            workspace_id: Workspace ID

        Returns:
            Onboarding session data
        """
        session = await self.repository.get_by_workspace(workspace_id)

        if not session:
            # Create new session
            session_data = {
                "workspace_id": workspace_id,
                "current_step": 1,
                "completed_steps": [],
                "step_data": {},
                "evidence_items": [],
                "extracted_facts": [],
                "status": "in_progress",
                "started_at": datetime.utcnow().isoformat(),
            }

            session = await self.repository.create(workspace_id, session_data)

        return session

    async def advance_step(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """
        Advance to next onboarding step

        Args:
            workspace_id: Workspace ID

        Returns:
            Updated session data or None if not found
        """
        session = await self.get_or_create_session(workspace_id)

        current_step = session.get("current_step", 1)
        next_step = current_step + 1

        # Check if onboarding is complete
        if next_step > 13:  # Total steps in onboarding
            await self.complete_onboarding(workspace_id)
            return await self.repository.get_by_workspace(workspace_id)

        return await self.repository.update_step(workspace_id, next_step, {})

    async def save_step_data(
        self, workspace_id: str, step: int, step_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Save data for a specific onboarding step

        Args:
            workspace_id: Workspace ID
            step: Step number
            step_data: Step data

        Returns:
            Updated session data or None if not found
        """
        session = await self.get_or_create_session(workspace_id)

        # Validate step
        if step < 1 or step > 13:
            raise ValidationError("Invalid step number")

        # Update step data
        current_step_data = session.get("step_data", {})
        current_step_data[f"step_{step}"] = step_data

        # Add to completed steps if not already there
        completed_steps = session.get("completed_steps", [])
        if step not in completed_steps:
            completed_steps.append(step)

        # Update session
        update_data = {
            "step_data": current_step_data,
            "completed_steps": completed_steps,
            "current_step": max(step, session.get("current_step", 1)),
        }

        return await self.repository.update_step(workspace_id, step, update_data)

    async def complete_step(
        self, workspace_id: str, step: int
    ) -> Optional[Dict[str, Any]]:
        """
        Mark a step as completed

        Args:
            workspace_id: Workspace ID
            step: Step number

        Returns:
            Updated session data or None if not found
        """
        session = await self.get_or_create_session(workspace_id)

        # Add to completed steps if not already there
        completed_steps = session.get("completed_steps", [])
        if step not in completed_steps:
            completed_steps.append(step)

        # Update session
        update_data = {
            "completed_steps": completed_steps,
            "current_step": max(step + 1, session.get("current_step", 1)),
        }

        return await self.repository.update_step(workspace_id, step, update_data)

    async def complete_onboarding(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """
        Complete onboarding for workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Updated session data or None if not found
        """
        session = await self.get_or_create_session(workspace_id)

        # Update session status
        update_data = {
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "current_step": 13,  # Final step
        }

        updated_session = await self.repository.update_step(workspace_id, 13, update_data)

        # Record initial baseline in BCM Ledger
        try:
            from backend.services.bcm_integration import bcm_evolution
            await bcm_evolution.record_strategic_shift(
                workspace_id=workspace_id,
                ucid="RF-BASELINE",
                reason="Initial Onboarding Completion",
                updates=session.get("step_data", {})
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to ledger onboarding completion: {e}")

        return updated_session

    async def reset_step(
        self, workspace_id: str, step: int
    ) -> Optional[Dict[str, Any]]:
        """
        Reset a specific step (remove from completed steps)

        Args:
            workspace_id: Workspace ID
            step: Step number

        Returns:
            Updated session data or None if not found
        """
        session = await self.get_or_create_session(workspace_id)

        # Remove from completed steps
        completed_steps = session.get("completed_steps", [])
        if step in completed_steps:
            completed_steps.remove(step)

        # Remove step data
        step_data = session.get("step_data", {})
        step_data.pop(f"step_{step}", None)

        # Update session
        update_data = {
            "completed_steps": completed_steps,
            "step_data": step_data,
            "current_step": step,
        }

        return await self.repository.update_step(workspace_id, step, update_data)

    async def get_evidence(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        Get all evidence for onboarding session

        Args:
            workspace_id: Workspace ID

        Returns:
            List of evidence data
        """
        session = await self.get_or_create_session(workspace_id)
        session_id = session.get("id")

        if session_id:
            return await self.evidence_repository.list_by_session(
                workspace_id, session_id
            )

        return []

    async def add_evidence(
        self,
        workspace_id: str,
        source_type: str,
        source_name: str,
        content: str,
        file_path: Optional[str] = None,
        url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add evidence to onboarding session

        Args:
            workspace_id: Workspace ID
            source_type: Type of evidence source ('file' or 'url')
            source_name: Name of the source
            content: Content of the evidence
            file_path: Optional file path
            url: Optional URL

        Returns:
            Created evidence data
        """
        session = await self.get_or_create_session(workspace_id)
        session_id = session.get("id")

        # Validate source type
        if source_type not in ["file", "url"]:
            raise ValidationError("Source type must be 'file' or 'url'")

        evidence_data = {
            "workspace_id": workspace_id,
            "session_id": session_id,
            "source_type": source_type,
            "source_name": source_name,
            "content": content,
            "file_path": file_path,
            "url": url,
            "content_type": self._detect_content_type(content),
            "word_count": len(content.split()),
            "processing_status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }

        return await self.evidence_repository.add_evidence(
            workspace_id, session_id, source_type, source_name, content
        )

    async def process_evidence(
        self, workspace_id: str, evidence_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Process evidence (extract topics, etc.)

        Args:
            workspace_id: Workspace ID
            evidence_id: Evidence ID

        Returns:
            Updated evidence data or None if not found
        """
        evidence = await self.evidence_repository.get_by_id(evidence_id, workspace_id)
        if not evidence:
            raise ValidationError("Evidence not found")

        # Extract key topics (simplified)
        content = evidence.get("content", "")
        words = content.lower().split()

        # Simple keyword extraction
        business_keywords = [
            "business",
            "company",
            "revenue",
            "profit",
            "growth",
            "market",
            "customer",
            "product",
            "service",
        ]
        key_topics = [word for word in business_keywords if word in words]

        # Remove duplicates and limit to 10 topics
        key_topics = list(set(key_topics))[:10]

        # Update evidence
        update_data = {
            "key_topics": key_topics,
            "processing_status": "processed",
            "processed_at": datetime.utcnow().isoformat(),
        }

        # Set retention date for OCR-processed files
        if evidence.get("content_type") == "ocr":
            file_record = await self.evidence_repository.get_file_record(evidence_id)
            if file_record:
                file_record['retention_date'] = datetime.utcnow() + timedelta(days=7)
                await self.evidence_repository.update_file_record(file_record)

        return await self.evidence_repository.mark_processed(evidence_id, key_topics)

    async def get_onboarding_progress(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get onboarding progress for workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Progress data
        """
        session = await self.get_or_create_session(workspace_id)

        total_steps = 13
        completed_steps = len(session.get("completed_steps", []))
        current_step = session.get("current_step", 1)

        progress_percentage = (completed_steps / total_steps) * 100

        return {
            "session_id": session.get("id"),
            "current_step": current_step,
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "progress_percentage": round(progress_percentage, 2),
            "status": session.get("status", "in_progress"),
            "started_at": session.get("started_at"),
            "completed_at": session.get("completed_at"),
            "evidence_count": len(session.get("evidence_items", [])),
            "extracted_facts_count": len(session.get("extracted_facts", [])),
        }

    async def generate_foundation_from_onboarding(
        self, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate foundation data from onboarding session

        Args:
            workspace_id: Workspace ID

        Returns:
            Generated foundation data or None if not found
        """
        session = await self.get_or_create_session(workspace_id)
        step_data = session.get("step_data", {})

        # Extract foundation data from onboarding steps
        foundation_data = {
            "company_name": step_data.get("step_1", {}).get("company_name", ""),
            "mission": step_data.get("step_2", {}).get("mission", ""),
            "vision": step_data.get("step_2", {}).get("vision", ""),
            "values": step_data.get("step_3", {}).get("values", []),
            "industry": step_data.get("step_4", {}).get("industry", ""),
            "target_market": step_data.get("step_5", {}).get("target_market", ""),
            "positioning": step_data.get("step_6", {}).get("positioning", ""),
            "brand_voice": step_data.get("step_7", {}).get("brand_voice", ""),
            "messaging_guardrails": step_data.get("step_8", {}).get(
                "messaging_guardrails", []
            ),
        }

        # Create foundation if data is valid
        if foundation_data["company_name"]:
            return await self.foundation_repository.upsert(
                workspace_id, foundation_data
            )

        return None

    def _detect_content_type(self, content: str) -> str:
        """
        Detect content type from content

        Args:
            content: Content to analyze

        Returns:
            Detected content type
        """
        content_lower = content.lower()

        if any(keyword in content_lower for keyword in ["http", "www", ".com", ".org"]):
            return "web_page"
        elif any(keyword in content_lower for keyword in ["<html", "<body", "<div"]):
            return "html"
        elif len(content.split()) < 50:
            return "short_text"
        else:
            return "long_text"

    async def validate_onboarding_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate onboarding data before saving

        Args:
            data: Onboarding data to validate

        Returns:
            True if valid, raises ValidationError if invalid
        """
        # Validate step number
        if "step" in data:
            step = data["step"]
            if not isinstance(step, int) or step < 1 or step > 13:
                raise ValidationError("Step must be an integer between 1 and 13")

        # Validate step data structure
        if "step_data" in data:
            step_data = data["step_data"]
            if not isinstance(step_data, dict):
                raise ValidationError("Step data must be a dictionary")

        # Validate completed steps
        if "completed_steps" in data:
            completed_steps = data["completed_steps"]
            if not isinstance(completed_steps, list):
                raise ValidationError("Completed steps must be a list")

            for step in completed_steps:
                if not isinstance(step, int) or step < 1 or step > 13:
                    raise ValidationError(
                        "Each completed step must be an integer between 1 and 13"
                    )

        # Validate evidence items
        if "evidence_items" in data:
            evidence_items = data["evidence_items"]
            if not isinstance(evidence_items, list):
                raise ValidationError("Evidence items must be a list")

        # Validate extracted facts
        if "extracted_facts" in data:
            extracted_facts = data["extracted_facts"]
            if not isinstance(extracted_facts, list):
                raise ValidationError("Extracted facts must be a list")

        return True
