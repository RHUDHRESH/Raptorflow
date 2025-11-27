# backend/agents/council_of_lords/cognition.py
# RaptorFlow Codex - Cognition Lord Agent
# Phase 2A Week 4 - Learning, Synthesis, and Decision Support

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import json
import logging
from abc import ABC

from agents.base_agent import BaseAgent, AgentType, AgentStatus, Capability, AgentRole

logger = logging.getLogger(__name__)

# ==============================================================================
# ENUMS
# ==============================================================================

class LearningType(str, Enum):
    """Types of learning experiences"""
    SUCCESS = "success"  # Successful initiative/campaign
    FAILURE = "failure"  # Failed initiative
    PARTIAL = "partial"  # Partial success
    OPTIMIZATION = "optimization"  # Optimization insight
    PATTERN = "pattern"  # Identified pattern
    RISK = "risk"  # Risk identified
    OPPORTUNITY = "opportunity"  # Market opportunity


class SynthesisType(str, Enum):
    """Types of knowledge synthesis"""
    TREND = "trend"  # Market/performance trend
    PATTERN = "pattern"  # Behavioral pattern
    PREDICTION = "prediction"  # Future prediction
    RECOMMENDATION = "recommendation"  # Best practice
    WARNING = "warning"  # Risk warning
    OPPORTUNITY = "opportunity"  # Strategic opportunity


class DecisionStatus(str, Enum):
    """Status of decisions"""
    PROPOSED = "proposed"
    ANALYZED = "analyzed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    EVALUATED = "evaluated"


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

class LearningEntry:
    """Represents a single learning instance"""

    def __init__(
        self,
        learning_id: str,
        learning_type: LearningType,
        source: str,
        description: str,
        key_insight: str,
        context: Dict[str, Any],
        confidence: float = 0.8
    ):
        self.id = learning_id
        self.type = learning_type
        self.source = source  # e.g., "initiative_123", "agent_456"
        self.description = description
        self.key_insight = key_insight
        self.context = context  # Full context of the learning
        self.confidence = confidence  # 0.0-1.0
        self.created_at = datetime.utcnow().isoformat()
        self.applied_count = 0
        self.effectiveness_score = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "description": self.description,
            "key_insight": self.key_insight,
            "context": self.context,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "applied_count": self.applied_count,
            "effectiveness_score": self.effectiveness_score
        }


class SynthesisResult:
    """Represents synthesized knowledge"""

    def __init__(
        self,
        synthesis_id: str,
        synthesis_type: SynthesisType,
        title: str,
        description: str,
        supporting_learnings: List[str],  # List of learning IDs
        recommendations: List[str],
        confidence: float = 0.85
    ):
        self.id = synthesis_id
        self.type = synthesis_type
        self.title = title
        self.description = description
        self.supporting_learnings = supporting_learnings
        self.recommendations = recommendations
        self.confidence = confidence
        self.created_at = datetime.utcnow().isoformat()
        self.applied_count = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "description": self.description,
            "supporting_learnings": self.supporting_learnings,
            "recommendations": self.recommendations,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "applied_count": self.applied_count
        }


class Decision:
    """Represents a strategic decision"""

    def __init__(
        self,
        decision_id: str,
        title: str,
        description: str,
        decision_type: str,  # e.g., "resource_allocation", "process_change"
        options: Dict[str, Any],
        recommendation: str,
        supporting_synthesis: List[str],  # List of synthesis IDs
        impact_forecast: Dict[str, float]  # e.g., {"productivity": 0.25, "cost": -0.10}
    ):
        self.id = decision_id
        self.title = title
        self.description = description
        self.decision_type = decision_type
        self.options = options
        self.recommendation = recommendation
        self.supporting_synthesis = supporting_synthesis
        self.impact_forecast = impact_forecast
        self.status = DecisionStatus.PROPOSED
        self.created_at = datetime.utcnow().isoformat()
        self.confidence = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "decision_type": self.decision_type,
            "options": self.options,
            "recommendation": self.recommendation,
            "supporting_synthesis": self.supporting_synthesis,
            "impact_forecast": self.impact_forecast,
            "status": self.status.value,
            "created_at": self.created_at,
            "confidence": self.confidence
        }


# ==============================================================================
# COGNITION LORD AGENT
# ==============================================================================

class CognitionLord(BaseAgent):
    """
    The Cognition Lord learns from organizational activities, synthesizes
    knowledge into insights, and provides decision support to other agents.

    Key Responsibilities:
    - Record learning from completed initiatives and actions
    - Synthesize learnings into patterns and predictions
    - Support decision-making with data-driven insights
    - Mentor agents and guilds based on accumulated knowledge
    - Track organizational learning and improvement
    """

    def __init__(self):
        super().__init__(
            name="Cognition",
            agent_type=AgentType.INTELLIGENCE,
            role=AgentRole.COGNITION
        )

        # Learning storage
        self.learnings: Dict[str, LearningEntry] = {}
        self.synthesis_results: Dict[str, SynthesisResult] = {}
        self.decisions: Dict[str, Decision] = {}

        # Metrics
        self.total_learnings_recorded = 0
        self.total_syntheses_created = 0
        self.total_decisions_made = 0
        self.learning_effectiveness_score = 0.0

        # Register capabilities
        self.register_capability(
            Capability(
                name="record_learning",
                description="Record a learning instance from an activity",
                handler=self._record_learning
            )
        )

        self.register_capability(
            Capability(
                name="synthesize_knowledge",
                description="Synthesize multiple learnings into insights",
                handler=self._synthesize_knowledge
            )
        )

        self.register_capability(
            Capability(
                name="make_decision",
                description="Make a strategic decision based on learnings",
                handler=self._make_decision
            )
        )

        self.register_capability(
            Capability(
                name="mentor_agent",
                description="Provide mentoring and guidance to an agent",
                handler=self._mentor_agent
            )
        )

        self.register_capability(
            Capability(
                name="get_learning_summary",
                description="Get summary of learnings and insights",
                handler=self._get_learning_summary
            )
        )

        logger.info(f"✅ Cognition Lord initialized with {len(self.capabilities)} capabilities")

    # ========================================================================
    # CAPABILITY HANDLERS
    # ========================================================================

    async def _record_learning(self, **kwargs) -> Dict[str, Any]:
        """Record a learning experience"""
        try:
            learning_type = LearningType(kwargs.get("learning_type", "success"))
            source = kwargs.get("source", "unknown")
            description = kwargs.get("description", "")
            key_insight = kwargs.get("key_insight", "")
            context = kwargs.get("context", {})
            confidence = kwargs.get("confidence", 0.8)

            # Generate learning ID
            learning_id = f"learning_{self.total_learnings_recorded + 1}_{int(datetime.utcnow().timestamp())}"

            # Create learning entry
            learning = LearningEntry(
                learning_id=learning_id,
                learning_type=learning_type,
                source=source,
                description=description,
                key_insight=key_insight,
                context=context,
                confidence=confidence
            )

            # Store learning
            self.learnings[learning_id] = learning
            self.total_learnings_recorded += 1

            # Try to inject into RAG system
            try:
                if hasattr(self, 'rag_memory'):
                    await self.rag_memory.store(
                        doc_id=learning_id,
                        content=f"Learning: {learning_type.value} from {source}. Insight: {key_insight}. Description: {description}",
                        metadata={"type": "learning", "source": source, "confidence": confidence}
                    )
            except Exception as rag_error:
                logger.debug(f"RAG storage optional: {rag_error}")

            logger.info(f"📚 Learning recorded: {learning_id} ({learning_type.value})")

            return {
                "learning_id": learning_id,
                "type": learning_type.value,
                "source": source,
                "key_insight": key_insight,
                "confidence": confidence,
                "created_at": learning.created_at
            }

        except Exception as e:
            logger.error(f"❌ Error recording learning: {e}")
            return {"error": str(e), "success": False}

    async def _synthesize_knowledge(self, **kwargs) -> Dict[str, Any]:
        """Synthesize learnings into insights"""
        try:
            synthesis_type = SynthesisType(kwargs.get("synthesis_type", "recommendation"))
            title = kwargs.get("title", "Knowledge Synthesis")
            description = kwargs.get("description", "")
            learning_ids = kwargs.get("learning_ids", [])
            recommendations = kwargs.get("recommendations", [])

            # Generate synthesis ID
            synthesis_id = f"synthesis_{self.total_syntheses_created + 1}_{int(datetime.utcnow().timestamp())}"

            # Determine confidence based on supporting learnings
            learning_count = len(learning_ids)
            avg_confidence = 0.0
            if learning_count > 0:
                avg_confidence = sum(
                    self.learnings.get(lid, LearningEntry("", LearningType.SUCCESS, "", "", "", {}, 0.5)).confidence
                    for lid in learning_ids if lid in self.learnings
                ) / max(learning_count, 1)

            synthesis_confidence = min(0.95, 0.7 + (learning_count * 0.05))

            # Create synthesis result
            synthesis = SynthesisResult(
                synthesis_id=synthesis_id,
                synthesis_type=synthesis_type,
                title=title,
                description=description,
                supporting_learnings=learning_ids,
                recommendations=recommendations,
                confidence=synthesis_confidence
            )

            # Store synthesis
            self.synthesis_results[synthesis_id] = synthesis
            self.total_syntheses_created += 1

            # Try to store in RAG
            try:
                if hasattr(self, 'rag_memory'):
                    await self.rag_memory.store(
                        doc_id=synthesis_id,
                        content=f"Synthesis: {title}. Type: {synthesis_type.value}. Recommendations: {', '.join(recommendations)}",
                        metadata={"type": "synthesis", "synthesis_type": synthesis_type.value, "confidence": synthesis_confidence}
                    )
            except Exception as rag_error:
                logger.debug(f"RAG storage optional: {rag_error}")

            logger.info(f"💡 Synthesis created: {synthesis_id} ({synthesis_type.value})")

            return {
                "synthesis_id": synthesis_id,
                "type": synthesis_type.value,
                "title": title,
                "recommendations": recommendations,
                "confidence": synthesis_confidence,
                "supporting_learnings": learning_count,
                "created_at": synthesis.created_at
            }

        except Exception as e:
            logger.error(f"❌ Error synthesizing knowledge: {e}")
            return {"error": str(e), "success": False}

    async def _make_decision(self, **kwargs) -> Dict[str, Any]:
        """Make a strategic decision"""
        try:
            decision_title = kwargs.get("title", "Strategic Decision")
            description = kwargs.get("description", "")
            decision_type = kwargs.get("decision_type", "general")
            options = kwargs.get("options", {})
            synthesis_ids = kwargs.get("synthesis_ids", [])
            impact_forecast = kwargs.get("impact_forecast", {})

            # Generate decision ID
            decision_id = f"decision_{self.total_decisions_made + 1}_{int(datetime.utcnow().timestamp())}"

            # Analyze synthesis to make recommendation
            recommendation = "No clear recommendation"
            decision_confidence = 0.5

            if synthesis_ids and len(synthesis_ids) > 0:
                valid_syntheses = [
                    self.synthesis_results[sid] for sid in synthesis_ids
                    if sid in self.synthesis_results
                ]

                if valid_syntheses:
                    avg_synthesis_confidence = sum(s.confidence for s in valid_syntheses) / len(valid_syntheses)
                    decision_confidence = min(0.95, avg_synthesis_confidence + 0.1)

                    # Generate recommendation from strongest synthesis
                    strongest = max(valid_syntheses, key=lambda x: x.confidence)
                    if strongest.recommendations:
                        recommendation = strongest.recommendations[0]

            # Create decision
            decision = Decision(
                decision_id=decision_id,
                title=decision_title,
                description=description,
                decision_type=decision_type,
                options=options,
                recommendation=recommendation,
                supporting_synthesis=synthesis_ids,
                impact_forecast=impact_forecast
            )
            decision.confidence = decision_confidence

            # Store decision
            self.decisions[decision_id] = decision
            self.total_decisions_made += 1

            logger.info(f"🎯 Decision made: {decision_id} - {decision_title}")

            return {
                "decision_id": decision_id,
                "title": decision_title,
                "recommendation": recommendation,
                "confidence": decision_confidence,
                "impact_forecast": impact_forecast,
                "status": decision.status.value,
                "created_at": decision.created_at
            }

        except Exception as e:
            logger.error(f"❌ Error making decision: {e}")
            return {"error": str(e), "success": False}

    async def _mentor_agent(self, **kwargs) -> Dict[str, Any]:
        """Provide mentoring to an agent"""
        try:
            agent_name = kwargs.get("agent_name", "Unknown Agent")
            current_challenge = kwargs.get("current_challenge", "")
            agent_goal = kwargs.get("agent_goal", "")

            # Find relevant learnings
            relevant_learnings = [
                learning for learning in self.learnings.values()
                if "challenge" in learning.description.lower() or
                   "goal" in learning.description.lower()
            ]

            # Find relevant syntheses
            relevant_syntheses = [
                synthesis for synthesis in self.synthesis_results.values()
                if any(rec.lower() in agent_goal.lower() for rec in synthesis.recommendations)
            ]

            # Build mentoring guidance
            mentoring_points = []

            if relevant_syntheses:
                for synthesis in sorted(relevant_syntheses, key=lambda x: x.confidence, reverse=True)[:3]:
                    mentoring_points.append({
                        "insight": synthesis.title,
                        "recommendations": synthesis.recommendations,
                        "confidence": synthesis.confidence
                    })

            if relevant_learnings:
                for learning in sorted(relevant_learnings, key=lambda x: x.confidence, reverse=True)[:2]:
                    mentoring_points.append({
                        "insight": learning.key_insight,
                        "source": learning.source,
                        "confidence": learning.confidence
                    })

            mentoring_summary = f"Mentoring for {agent_name} on goal: {agent_goal}"
            if mentoring_points:
                mentoring_summary += f"\n\nKey Points:\n"
                for i, point in enumerate(mentoring_points, 1):
                    mentoring_summary += f"{i}. {point.get('insight', 'Unknown')}\n"

            logger.info(f"🎓 Mentoring provided to {agent_name}")

            return {
                "agent": agent_name,
                "mentoring_summary": mentoring_summary,
                "key_points": mentoring_points,
                "relevant_learnings": len(relevant_learnings),
                "relevant_syntheses": len(relevant_syntheses)
            }

        except Exception as e:
            logger.error(f"❌ Error providing mentoring: {e}")
            return {"error": str(e), "success": False}

    async def _get_learning_summary(self, **kwargs) -> Dict[str, Any]:
        """Get summary of learnings and insights"""
        try:
            # Calculate metrics
            total_learning_count = len(self.learnings)
            total_synthesis_count = len(self.synthesis_results)
            total_decisions = len(self.decisions)

            # Learning distribution
            learning_by_type = {}
            for learning in self.learnings.values():
                learning_type = learning.type.value
                learning_by_type[learning_type] = learning_by_type.get(learning_type, 0) + 1

            # Synthesis distribution
            synthesis_by_type = {}
            for synthesis in self.synthesis_results.values():
                synthesis_type = synthesis.type.value
                synthesis_by_type[synthesis_type] = synthesis_by_type.get(synthesis_type, 0) + 1

            # Average confidence scores
            avg_learning_confidence = 0.0
            if self.learnings:
                avg_learning_confidence = sum(l.confidence for l in self.learnings.values()) / len(self.learnings)

            avg_synthesis_confidence = 0.0
            if self.synthesis_results:
                avg_synthesis_confidence = sum(s.confidence for s in self.synthesis_results.values()) / len(self.synthesis_results)

            # Update effectiveness score
            self.learning_effectiveness_score = (avg_learning_confidence + avg_synthesis_confidence) / 2

            logger.info(f"📊 Learning summary: {total_learning_count} learnings, {total_synthesis_count} syntheses, {total_decisions} decisions")

            return {
                "total_learnings": total_learning_count,
                "total_syntheses": total_synthesis_count,
                "total_decisions": total_decisions,
                "learning_distribution": learning_by_type,
                "synthesis_distribution": synthesis_by_type,
                "average_learning_confidence": avg_learning_confidence,
                "average_synthesis_confidence": avg_synthesis_confidence,
                "overall_effectiveness": self.learning_effectiveness_score,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error getting learning summary: {e}")
            return {"error": str(e), "success": False}

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    async def get_recent_learnings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent learnings"""
        sorted_learnings = sorted(
            self.learnings.values(),
            key=lambda x: x.created_at,
            reverse=True
        )
        return [l.to_dict() for l in sorted_learnings[:limit]]

    async def get_recent_syntheses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent syntheses"""
        sorted_syntheses = sorted(
            self.synthesis_results.values(),
            key=lambda x: x.created_at,
            reverse=True
        )
        return [s.to_dict() for s in sorted_syntheses[:limit]]

    async def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent decisions"""
        sorted_decisions = sorted(
            self.decisions.values(),
            key=lambda x: x.created_at,
            reverse=True
        )
        return [d.to_dict() for d in sorted_decisions[:limit]]

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get Cognition performance summary"""
        return {
            "total_learnings_recorded": self.total_learnings_recorded,
            "total_syntheses_created": self.total_syntheses_created,
            "total_decisions_made": self.total_decisions_made,
            "learning_effectiveness_score": self.learning_effectiveness_score,
            "active_learnings": len(self.learnings),
            "active_syntheses": len(self.synthesis_results),
            "active_decisions": len(self.decisions)
        }
