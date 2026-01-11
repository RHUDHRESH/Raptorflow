"""
Human-in-the-Loop Module - Cognitive Approval Layer

Handles approval gates, feedback collection, preference learning,
and human oversight for high-risk or sensitive operations.
"""

import json
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackType(str, Enum):
    CONTENT = "content"
    STYLE = "style"
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    TONE = "tone"
    LENGTH = "length"
    STRATEGY = "strategy"
    OTHER = "other"


class ApprovalGate(BaseModel):
    """Human approval checkpoint."""

    # Identification
    gate_id: str
    workspace_id: str
    session_id: str

    # Content
    gate_type: str = Field(description="Type of approval gate")
    description: str = Field(description="Human-readable description")
    pending_output: Dict[str, Any] = Field(description="Output awaiting approval")

    # Risk assessment
    risk_level: ApprovalLevel = Field(description="Risk level of this approval")
    risk_reasons: List[str] = Field(
        default=[], description="Reasons for risk assessment"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field(description="When this gate expires")

    # Decision tracking
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    decided_by: Optional[str] = Field(
        default=None, description="User who made decision"
    )
    decided_at: Optional[datetime] = Field(
        default=None, description="When decision was made"
    )
    decision_reason: Optional[str] = Field(
        default=None, description="Reason for decision"
    )

    # Feedback
    feedback_text: Optional[str] = Field(default=None, description="User feedback")
    feedback_type: Optional[FeedbackType] = Field(
        default=None, description="Type of feedback"
    )
    feedback_rating: Optional[int] = Field(
        default=None, description="User rating (1-5)"
    )

    # Modifications
    modified_output: Optional[Dict[str, Any]] = Field(
        default=None, description="Modified output after feedback"
    )
    modification_summary: Optional[str] = Field(
        default=None, description="Summary of changes made"
    )

    # Context
    context: Dict[str, Any] = Field(default={}, description="Additional context")


class UserFeedback(BaseModel):
    """Structured user feedback."""

    # Identification
    feedback_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspace_id: str
    session_id: str

    # Content
    output_id: Optional[str] = Field(
        default=None, description="ID of output being feedback on"
    )
    gate_id: Optional[str] = Field(
        default=None, description="ID of approval gate if applicable"
    )

    # Feedback details
    feedback_type: FeedbackType = Field(description="Type of feedback")
    rating: int = Field(description="User rating (1-5)")
    feedback_text: str = Field(description="User feedback text")

    # Preferences
    tone_preference: Optional[str] = Field(
        default=None, description="Preferred tone (formal, casual, etc.)"
    )
    length_preference: Optional[str] = Field(
        default=None, description="Preferred length (shorter, just_right, longer)"
    )
    detail_preference: Optional[str] = Field(
        default=None,
        description="Preferred detail level (less_detail, just_right, more_detail)",
    )

    # Content preferences
    content_preferences: List[str] = Field(
        default=[], description="Specific content preferences"
    )
    style_preferences: List[str] = Field(
        default=[], description="Style and formatting preferences"
    )

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    user_agent: Optional[str] = Field(default=None, description="User agent string")
    ip_address: Optional[str] = Field(default=None, description="User IP address")


class PreferenceProfile(BaseModel):
    """Learned user preferences."""

    # Identification
    workspace_id: str
    profile_version: str = Field(default="1.0")
    last_updated: datetime = Field(default_factory=datetime.now)

    # Communication preferences
    preferred_tone: str = Field(default="professional")
    preferred_formality: str = Field(default="balanced")
    preferred_length: str = Field(default="medium")

    # Content preferences
    content_style: List[str] = Field(default=[], description="Preferred content styles")
    topics_of_interest: List[str] = Field(
        default=[], description="Topics user engages with"
    )
    avoided_topics: List[str] = Field(default=[], description="Topics to avoid")

    # Quality preferences
    minimum_quality_score: int = Field(
        default=70, description="Minimum acceptable quality score"
    )
    detail_tolerance: int = Field(
        default=3, description="Tolerance for detail level (1-5)"
    )

    # Interaction preferences
    approval_threshold: ApprovalLevel = Field(default=ApprovalLevel.MEDIUM)
    auto_approve_safe: bool = Field(
        default=False, description="Auto-approve low-risk content"
    )

    # Learning data
    total_feedback_count: int = Field(default=0)
    average_rating: float = Field(default=3.0)
    feedback_history: List[Dict[str, Any]] = Field(
        default=[], description="Recent feedback history"
    )


# Approval rules for different content types
APPROVAL_RULES = {
    # Marketing content
    "marketing_campaign": {
        "condition": lambda c: c.get("budget_limit", 0) > 1000,
        "level": ApprovalLevel.MEDIUM,
        "reasons": ["Marketing spend involved", "Public visibility"],
    },
    "email_campaign": {
        "condition": lambda c: c.get("is_cold_outreach", False),
        "level": ApprovalLevel.MEDIUM,
        "reasons": ["Cold outreach can affect brand reputation"],
    },
    "ad_copy": {
        "condition": lambda c: True,  # Always approve ads
        "level": ApprovalLevel.HIGH,
        "reasons": ["Ad spend involved", "Public visibility"],
    },
    # Strategic content
    "strategy_document": {
        "condition": lambda c: c.get("risk_level", 0) >= 7,
        "level": ApprovalLevel.HIGH,
        "reasons": ["High-risk strategy", "Significant business impact"],
    },
    "business_plan": {
        "condition": lambda c: c.get("financial_implications", False),
        "level": ApprovalLevel.MEDIUM,
        "reasons": ["Business planning", "Strategic decisions"],
    },
    # Technical content
    "code_deployment": {
        "condition": lambda c: c.get("is_production", False),
        "level": ApprovalLevel.HIGH,
        "reasons": ["Production deployment", "System changes"],
    },
    "api_integration": {
        "condition": lambda c: c.get("is_write_operation", False),
        "level": ApprovalLevel.MEDIUM,
        "reasons": ["External system modification"],
    },
    # Legal/Compliance
    "legal_document": {
        "condition": lambda c: True,
        "level": ApprovalLevel.CRITICAL,
        "reasons": ["Legal implications", "Compliance requirements"],
    },
    "financial_report": {
        "condition": lambda c: True,
        "level": ApprovalLevel.HIGH,
        "reasons": ["Financial data", "Regulatory compliance"],
    },
    # Data operations
    "data_deletion": {
        "condition": lambda c: True,
        "level": ApprovalLevel.HIGH,
        "reasons": ["Irreversible action"],
    },
    "data_export": {
        "condition": lambda c: c.get("contains_pii", False),
        "level": ApprovalLevel.MEDIUM,
        "reasons": ["Data privacy", "PII concerns"],
    },
}


class HumanLoopModule:
    """
    Advanced human-in-the-loop module for approval and feedback.

    Manages approval gates, collects user feedback, learns preferences,
    and provides human oversight for sensitive operations.
    """

    def __init__(self, storage_backend=None, cache_backend=None):
        """
        Initialize the human-in-the-loop module.

        Args:
            storage_backend: Storage backend for persistence (database, file system, etc.)
            cache_backend: Cache backend for fast access (Redis, memory, etc.)
        """
        self.storage = storage_backend
        self.cache = cache_backend

        # Configuration
        self.default_expiry_hours = 24
        self.max_feedback_history = 100
        self.preference_learning_enabled = True

        # Approval rules
        self.approval_rules = APPROVAL_RULES

        # Initialize cache for active gates
        self._active_gates = {}

    async def create_approval_gate(
        self,
        workspace_id: str,
        session_id: str,
        gate_type: str,
        pending_output: Dict[str, Any],
        risk_signals: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ApprovalGate:
        """
        Create an approval gate for human review.

        Args:
            workspace_id: Workspace identifier
            session_id: Session identifier
            gate_type: Type of content requiring approval
            pending_output: Output awaiting approval
            risk_signals: Risk assessment signals
            context: Additional context for approval decision

        Returns:
            ApprovalGate with approval details
        """
        # Determine if approval is needed
        needs_approval, risk_level, reasons = self._should_require_approval(
            gate_type, risk_signals, context or {}
        )

        if not needs_approval:
            # Return a pre-approved gate
            return ApprovalGate(
                gate_id=str(uuid.uuid4()),
                workspace_id=workspace_id,
                session_id=session_id,
                gate_type=gate_type,
                description=f"Auto-approved {gate_type}",
                pending_output=pending_output,
                risk_level=risk_level,
                risk_reasons=reasons,
                expires_at=datetime.now() + timedelta(hours=1),
                status=ApprovalStatus.APPROVED,
                decided_by="system",
                decided_at=datetime.now(),
                decision_reason="Auto-approved - low risk",
            )

        # Create pending approval gate
        gate = ApprovalGate(
            gate_id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            session_id=session_id,
            gate_type=gate_type,
            description=f"Human approval required for {gate_type}",
            pending_output=pending_output,
            risk_level=risk_level,
            risk_reasons=reasons,
            expires_at=datetime.now() + timedelta(hours=self.default_expiry_hours),
            context=context or {},
        )

        # Store in cache for fast access
        cache_key = f"approval_gate:{gate.gate_id}"
        if self.cache:
            self.cache.setex(
                cache_key,
                self.default_expiry_hours * 3600,  # Convert to seconds
                json.dumps(gate.model_dump(mode="json")),
            )

        # Store in persistent storage
        if self.storage:
            await self._store_approval_gate(gate)

        # Track active gate
        self._active_gates[gate.gate_id] = gate

        return gate

    async def process_approval_decision(
        self,
        gate_id: str,
        decision: ApprovalStatus,
        decided_by: str,
        decision_reason: str,
        feedback_text: Optional[str] = None,
        feedback_type: Optional[FeedbackType] = None,
        feedback_rating: Optional[int] = None,
        modified_output: Optional[Dict[str, Any]] = None,
    ) -> ApprovalGate:
        """
        Process human approval decision.

        Args:
            gate_id: Approval gate identifier
            decision: Approval decision
            decided_by: User making decision
            decision_reason: Reason for decision
            feedback_text: User feedback text
            feedback_type: Type of feedback
            feedback_rating: User rating (1-5)
            modified_output: Modified output if changes were made

        Returns:
            Updated ApprovalGate
        """
        # Get the gate
        gate = await self._get_approval_gate(gate_id)
        if not gate:
            raise ValueError(f"Approval gate {gate_id} not found")

        # Update gate with decision
        gate.status = decision
        gate.decided_by = decided_by
        gate.decided_at = datetime.now()
        gate.decision_reason = decision_reason
        gate.feedback_text = feedback_text
        gate.feedback_type = feedback_type
        gate.feedback_rating = feedback_rating
        gate.modified_output = modified_output

        # Generate modification summary if output was modified
        if modified_output:
            gate.modification_summary = self._generate_modification_summary(
                gate.pending_output, modified_output
            )

        # Update storage
        if self.storage:
            await self._update_approval_gate(gate)

        # Update cache
        cache_key = f"approval_gate:{gate_id}"
        if self.cache:
            self.cache.setex(
                cache_key,
                self.default_expiry_hours * 3600,
                json.dumps(gate.model_dump(mode="json")),
            )

        # Remove from active gates if approved/rejected
        if decision in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]:
            self._active_gates.pop(gate_id, None)

        # Process feedback if provided
        if feedback_text and feedback_type and feedback_rating:
            await self._process_feedback(
                workspace_id=gate.workspace_id,
                session_id=gate.session_id,
                output_id=gate.gate_id,
                feedback_type=feedback_type,
                rating=feedback_rating,
                feedback_text=feedback_text,
                user_context=gate.context,
            )

        return gate

    async def collect_feedback(
        self,
        workspace_id: str,
        session_id: str,
        output_id: Optional[str],
        feedback_type: FeedbackType,
        rating: int,
        feedback_text: str,
        user_preferences: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> UserFeedback:
        """
        Collect user feedback on output.

        Args:
            workspace_id: Workspace identifier
            session_id: Session identifier
            output_id: Output identifier
            feedback_type: Type of feedback
            rating: User rating (1-5)
            feedback_text: Feedback text
            user_preferences: User preference settings
            user_context: Additional context

        Returns:
            UserFeedback with feedback details
        """
        feedback = UserFeedback(
            workspace_id=workspace_id,
            session_id=session_id,
            output_id=output_id,
            feedback_type=feedback_type,
            rating=rating,
            feedback_text=feedback_text,
            tone_preference=(
                user_preferences.get("tone_preference") if user_preferences else None
            ),
            length_preference=(
                user_preferences.get("length_preference") if user_preferences else None
            ),
            detail_preference=(
                user_preferences.get("detail_preference") if user_preferences else None
            ),
            content_preferences=(
                user_preferences.get("content_preferences", [])
                if user_preferences
                else []
            ),
            style_preferences=(
                user_preferences.get("style_preferences", [])
                if user_preferences
                else []
            ),
            context=user_context or {},
        )

        # Store feedback
        if self.storage:
            await self._store_feedback(feedback)

        # Update preference learning
        if self.preference_learning_enabled:
            await self._update_preferences(feedback)

        return feedback

    async def get_preference_profile(self, workspace_id: str) -> PreferenceProfile:
        """
        Get learned preference profile for workspace.

        Args:
            workspace_id: Workspace identifier

        Returns:
            PreferenceProfile with learned preferences
        """
        # Try to get from cache first
        cache_key = f"preference_profile:{workspace_id}"
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                try:
                    profile_data = json.loads(cached)
                    return PreferenceProfile(**profile_data)
                except (json.JSONDecodeError, TypeError):
                    pass

        # Get from storage
        if self.storage:
            profile = await self._get_preference_profile(workspace_id)
            if profile:
                # Update cache
                if self.cache:
                    self.cache.setex(
                        cache_key,
                        3600,  # 1 hour cache
                        json.dumps(profile.model_dump(mode="json")),
                    )
                return profile

        # Return default profile
        return PreferenceProfile(
            workspace_id=workspace_id,
            preferred_tone="professional",
            preferred_formality="balanced",
            preferred_length="medium",
            minimum_quality_score=70,
            approval_threshold=ApprovalLevel.MEDIUM,
            auto_approve_safe=False,
        )

    async def update_preference_profile(
        self, workspace_id: str, updates: Dict[str, Any]
    ) -> PreferenceProfile:
        """
        Update preference profile with new data.

        Args:
            workspace_id: Workspace identifier
            updates: Preference updates

        Returns:
            Updated PreferenceProfile
        """
        profile = await self.get_preference_profile(workspace_id)

        # Apply updates
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        profile.last_updated = datetime.now()

        # Update storage
        if self.storage:
            await self._update_preference_profile(profile)

        # Update cache
        cache_key = f"preference_profile:{workspace_id}"
        if self.cache:
            self.cache.setex(
                cache_key, 3600, json.dumps(profile.model_dump(mode="json"))
            )

        return profile

    async def get_active_gates(
        self, workspace_id: Optional[str] = None, session_id: Optional[str] = None
    ) -> List[ApprovalGate]:
        """
        Get list of active approval gates.

        Args:
            workspace_id: Filter by workspace (optional)
            session_id: Filter by session (optional)

        Returns:
            List of active ApprovalGate objects
        """
        gates = list(self._active_gates.values())

        # Apply filters
        if workspace_id:
            gates = [g for g in gates if g.workspace_id == workspace_id]

        if session_id:
            gates = [g for g in gates if g.session_id == session_id]

        return gates

    async def expire_gate(self, gate_id: str) -> bool:
        """
        Expire an approval gate.

        Args:
            gate_id: Gate identifier to expire

        Returns:
            True if gate was expired, False if not found or already expired
        """
        gate = await self._get_approval_gate(gate_id)
        if not gate:
            return False

        if gate.status != ApprovalStatus.PENDING:
            return False

        # Update status to expired
        gate.status = ApprovalStatus.EXPIRED
        gate.decided_at = datetime.now()
        gate.decision_reason = "Approval gate expired"

        # Update storage
        if self.storage:
            await self._update_approval_gate(gate)

        # Update cache
        cache_key = f"approval_gate:{gate_id}"
        if self.cache:
            self.cache.setex(
                cache_key,
                self.default_expiry_hours * 3600,
                json.dumps(gate.model_dump(mode="json")),
            )

        # Remove from active gates
        self._active_gates.pop(gate_id, None)

        return True

    async def get_gate_history(
        self, workspace_id: str, limit: int = 50
    ) -> List[ApprovalGate]:
        """
        Get approval gate history for workspace.

        Args:
            workspace_id: Workspace identifier
            limit: Maximum number of gates to return

        Returns:
            List of ApprovalGate objects
        """
        if not self.storage:
            return []

        # Query storage for gate history
        # This would be implemented based on the storage backend
        # For now, return empty list
        return []

    def _should_require_approval(
        self, gate_type: str, risk_signals: Dict[str, Any], context: Dict[str, Any]
    ) -> Tuple[bool, ApprovalLevel, List[str]]:
        """
        Determine if approval is required based on rules.

        Args:
            gate_type: Type of content
            risk_signals: Risk assessment signals
            context: Additional context

        Returns:
            Tuple of (needs_approval, risk_level, reasons)
        """
        rule = self.approval_rules.get(gate_type)

        if not rule:
            return False, ApprovalLevel.LOW, []

        # Evaluate condition
        try:
            needs_approval = rule["condition"](risk_signals)
        except (KeyError, TypeError):
            needs_approval = False

        return (needs_approval, rule["level"], rule["reasons"])

    def _generate_modification_summary(
        self, original: Dict[str, Any], modified: Dict[str, Any]
    ) -> str:
        """Generate summary of modifications made."""
        changes = []

        # Simple comparison for demonstration
        if isinstance(original, dict) and isinstance(modified, dict):
            for key in modified:
                if key not in original:
                    changes.append(f"Added {key}")
                elif original[key] != modified[key]:
                    changes.append(f"Modified {key}")

        for key in original:
            if key not in modified:
                changes.append(f"Removed {key}")

        if changes:
            return "Changes made: " + ", ".join(changes)

        return "No changes detected"

    async def _process_feedback(
        self,
        workspace_id: str,
        session_id: str,
        output_id: Optional[str],
        feedback_type: FeedbackType,
        rating: int,
        feedback_text: str,
        user_context: Dict[str, Any],
    ) -> None:
        """Process feedback for learning."""
        # This would implement feedback processing logic
        # For now, just log the feedback
        print(f"Feedback processed: {feedback_type.value} - {rating}/5")

    async def _update_preferences(self, feedback: UserFeedback) -> None:
        """Update preference learning from feedback."""
        # Get current profile
        profile = await self.get_preference_profile(feedback.workspace_id)

        # Update based on feedback
        if feedback.tone_preference:
            profile.preferred_tone = feedback.tone_preference

        if feedback.length_preference:
            profile.preferred_length = feedback.length_preference

        if feedback.detail_preference:
            profile.detail_tolerance = self._map_detail_preference(
                feedback.detail_preference
            )

        # Update rating statistics
        profile.total_feedback_count += 1
        profile.average_rating = (
            profile.average_rating * (profile.total_feedback_count - 1)
            + feedback.rating
        ) / profile.total_feedback_count

        # Add to feedback history
        feedback_entry = {
            "timestamp": feedback.timestamp.isoformat(),
            "type": feedback.feedback_type.value,
            "rating": feedback.rating,
            "text": feedback.feedback_text[:200],  # Truncated for storage
        }

        profile.feedback_history.append(feedback_entry)

        # Keep only recent history
        if len(profile.feedback_history) > self.max_feedback_history:
            profile.feedback_history = profile.feedback_history[
                -self.max_feedback_history :
            ]

        # Update storage
        if self.storage:
            await self._update_preference_profile(profile)

        # Update cache
        cache_key = f"preference_profile:{feedback.workspace_id}"
        if self.cache:
            self.cache.setex(
                cache_key, 3600, json.dumps(profile.model_dump(mode="json"))
            )

    def _map_detail_preference(self, preference: str) -> int:
        """Map detail preference to tolerance level."""
        mapping = {"less_detail": 1, "just_right": 3, "more_detail": 5}
        return mapping.get(preference, 3)

    async def _store_approval_gate(self, gate: ApprovalGate) -> None:
        """Store approval gate in persistent storage."""
        # This would be implemented based on the storage backend
        # For now, just log the gate creation
        print(f"Approval gate stored: {gate.gate_id} - {gate.status}")

    async def _update_approval_gate(self, gate: ApprovalGate) -> None:
        """Update approval gate in persistent storage."""
        # This would be implemented based on the storage backend
        # For now, just log the update
        print(f"Approval gate updated: {gate.gate_id} - {gate.status}")

    async def _get_approval_gate(self, gate_id: str) -> Optional[ApprovalGate]:
        """Get approval gate by ID."""
        # Try cache first
        cache_key = f"approval_gate:{gate_id}"
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                try:
                    gate_data = json.loads(cached)
                    return ApprovalGate(**gate_data)
                except (json.JSONDecodeError, TypeError):
                    pass

        # Try active gates
        if gate_id in self._active_gates:
            return self._active_gates[gate_id]

        # Try storage
        if self.storage:
            # This would be implemented based on the storage backend
            # For now, return None
            pass

        return None

    async def _store_feedback(self, feedback: UserFeedback) -> None:
        """Store feedback in persistent storage."""
        # This would be implemented based on the storage backend
        # For now, just log the feedback
        print(f"Feedback stored: {feedback.feedback_id}")

    async def _get_preference_profile(
        self, workspace_id: str
    ) -> Optional[PreferenceProfile]:
        """Get preference profile from storage."""
        # This would be implemented based on the storage backend
        # For now, return None
        return None

    async def _update_preference_profile(self, profile: PreferenceProfile) -> None:
        """Update preference profile in storage."""
        # This would be implemented based on the storage backend
        # For now, just log the update
        print(f"Preference profile updated: {profile.workspace_id}")


# Export main classes
__all__ = [
    "ApprovalGate",
    "UserFeedback",
    "PreferenceProfile",
    "HumanLoopModule",
    "ApprovalStatus",
    "ApprovalLevel",
    "FeedbackType",
]
