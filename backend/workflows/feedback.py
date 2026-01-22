"""
FeedbackWorkflow - End-to-end feedback orchestration.
Handles feedback collection, analysis, and integration into system improvements.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from backend.agents.dispatcher import AgentDispatcher
from backend.agents.state import AgentState
from backend.cognitive import CognitiveEngine
from backend.memory.controller import MemoryController

from supabase import Client

logger = logging.getLogger(__name__)


class FeedbackWorkflow:
    """
    End-to-end feedback workflow orchestrator.

    Handles the complete feedback process from collection
    through analysis, categorization, and system integration.
    """

    def __init__(
        self,
        db_client: Client,
        memory_controller: MemoryController,
        cognitive_engine: CognitiveEngine,
        agent_dispatcher: AgentDispatcher,
    ):
        self.db_client = db_client
        self.memory_controller = memory_controller
        self.cognitive_engine = cognitive_engine
        self.agent_dispatcher = agent_dispatcher

    async def collect_feedback(
        self, workspace_id: str, feedback_data: Dict[str, Any], source: str = "user"
    ) -> Dict[str, Any]:
        """
        Collect feedback from various sources.

        Args:
            workspace_id: Workspace ID
            feedback_data: Feedback content and metadata
            source: Feedback source (user, system, agent, external)

        Returns:
            Feedback collection result
        """
        try:
            logger.info(
                f"Collecting feedback from {source} for workspace {workspace_id}"
            )

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Validate feedback data
            validation_result = await self._validate_feedback_data(
                feedback_data, source, context
            )

            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Feedback validation failed",
                    "validation_issues": validation_result["issues"],
                }

            # Step 2: Store feedback
            feedback_record = {
                "workspace_id": workspace_id,
                "source": source,
                "content": feedback_data.get("content"),
                "type": feedback_data.get("type", "general"),
                "category": feedback_data.get("category"),
                "rating": feedback_data.get("rating"),
                "metadata": feedback_data.get("metadata", {}),
                "status": "collected",
                "collected_at": time.time(),
            }

            result = self.db_client.table("feedback").insert(feedback_record).execute()

            if not result.data:
                return {"success": False, "error": "Failed to store feedback"}

            feedback_id = result.data[0]["id"]

            # Step 3: Store in memory
            await self._store_feedback_in_memory(
                workspace_id, feedback_id, feedback_data
            )

            return {
                "success": True,
                "feedback_id": feedback_id,
                "source": source,
                "collected_at": time.time(),
            }

        except Exception as e:
            logger.error(f"Error collecting feedback: {e}")
            return {"success": False, "error": str(e)}

    async def analyze_feedback(self, feedback_id: str) -> Dict[str, Any]:
        """
        Analyze collected feedback for insights and patterns.

        Args:
            feedback_id: Feedback ID to analyze

        Returns:
            Feedback analysis result
        """
        try:
            logger.info(f"Analyzing feedback: {feedback_id}")

            # Get feedback details
            feedback_result = (
                self.db_client.table("feedback")
                .select("*")
                .eq("id", feedback_id)
                .execute()
            )

            if not feedback_result.data:
                return {"success": False, "error": "Feedback not found"}

            feedback = feedback_result.data[0]
            workspace_id = feedback["workspace_id"]

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Extract insights
            insights_result = await self._extract_feedback_insights(feedback, context)

            # Step 2: Categorize feedback
            categorization_result = await self._categorize_feedback(
                feedback, insights_result, context
            )

            # Step 3: Analyze sentiment
            sentiment_result = await self._analyze_feedback_sentiment(feedback, context)

            # Step 4: Identify patterns
            patterns_result = await self._identify_feedback_patterns(
                feedback, workspace_id, context
            )

            # Step 5: Store analysis results
            analysis_record = {
                "feedback_id": feedback_id,
                "insights": insights_result,
                "categorization": categorization_result,
                "sentiment": sentiment_result,
                "patterns": patterns_result,
                "analyzed_at": time.time(),
            }

            self.db_client.table("feedback_analysis").insert(analysis_record).execute()

            # Step 6: Update feedback status
            self.db_client.table("feedback").update(
                {"status": "analyzed", "analyzed_at": time.time()}
            ).eq("id", feedback_id).execute()

            return {
                "success": True,
                "feedback_id": feedback_id,
                "insights": insights_result,
                "categorization": categorization_result,
                "sentiment": sentiment_result,
                "patterns": patterns_result,
                "analyzed_at": time.time(),
            }

        except Exception as e:
            logger.error(f"Error analyzing feedback {feedback_id}: {e}")
            return {"success": False, "error": str(e)}

    async def integrate_feedback(self, feedback_id: str) -> Dict[str, Any]:
        """
        Integrate feedback insights into system improvements.

        Args:
            feedback_id: Feedback ID to integrate

        Returns:
            Feedback integration result
        """
        try:
            logger.info(f"Integrating feedback: {feedback_id}")

            # Get feedback and analysis
            feedback_result = (
                self.db_client.table("feedback")
                .select("*")
                .eq("id", feedback_id)
                .execute()
            )
            analysis_result = (
                self.db_client.table("feedback_analysis")
                .select("*")
                .eq("feedback_id", feedback_id)
                .execute()
            )

            if not feedback_result.data:
                return {"success": False, "error": "Feedback not found"}

            feedback = feedback_result.data[0]
            analysis = analysis_result.data[0] if analysis_result.data else {}
            workspace_id = feedback["workspace_id"]

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Generate improvement suggestions
            improvements_result = await self._generate_improvement_suggestions(
                feedback, analysis, context
            )

            # Step 2: Create action items
            action_items_result = await self._create_feedback_action_items(
                feedback_id, improvements_result, context
            )

            # Step 3: Update knowledge base
            await self._update_knowledge_base_with_feedback(
                feedback, analysis, improvements_result
            )

            # Step 4: Trigger system adaptations
            adaptations_result = await self._trigger_system_adaptations(
                feedback, improvements_result, context
            )

            # Step 5: Update feedback status
            self.db_client.table("feedback").update(
                {
                    "status": "integrated",
                    "integrated_at": time.time(),
                    "action_items_created": len(
                        action_items_result.get("action_items", [])
                    ),
                }
            ).eq("id", feedback_id).execute()

            return {
                "success": True,
                "feedback_id": feedback_id,
                "improvements": improvements_result,
                "action_items": action_items_result,
                "adaptations": adaptations_result,
                "integrated_at": time.time(),
            }

        except Exception as e:
            logger.error(f"Error integrating feedback {feedback_id}: {e}")
            return {"success": False, "error": str(e)}

    async def _validate_feedback_data(
        self, feedback_data: Dict[str, Any], source: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate feedback data."""
        try:
            issues = []

            # Check required fields
            if not feedback_data.get("content"):
                issues.append("Feedback content is required")

            if not feedback_data.get("type"):
                issues.append("Feedback type is required")

            # Validate content length
            content = feedback_data.get("content", "")
            if len(content) < 10:
                issues.append("Feedback content too short")
            elif len(content) > 10000:
                issues.append("Feedback content too long")

            # Validate rating if provided
            rating = feedback_data.get("rating")
            if rating is not None:
                if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                    issues.append("Rating must be a number between 1 and 5")

            # Validate source
            valid_sources = ["user", "system", "agent", "external"]
            if source not in valid_sources:
                issues.append(f"Invalid source: {source}")

            return {"valid": len(issues) == 0, "issues": issues}

        except Exception as e:
            return {"valid": False, "issues": [str(e)]}

    async def _store_feedback_in_memory(
        self, workspace_id: str, feedback_id: str, feedback_data: Dict[str, Any]
    ):
        """Store feedback in memory system."""
        try:
            content = f"""
            Feedback: {feedback_data.get('content')}
            Type: {feedback_data.get('type')}
            Rating: {feedback_data.get('rating')}
            Source: {feedback_data.get('source')}
            """

            await self.memory_controller.store(
                workspace_id=workspace_id,
                memory_type="feedback",
                content=content,
                metadata={
                    "feedback_id": feedback_id,
                    "type": feedback_data.get("type"),
                    "rating": feedback_data.get("rating"),
                    "source": feedback_data.get("source"),
                    "timestamp": time.time(),
                },
            )

        except Exception as e:
            logger.error(f"Error storing feedback in memory: {e}")

    async def _extract_feedback_insights(
        self, feedback: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract insights from feedback using cognitive engine."""
        try:
            # Use cognitive reflection for insight extraction
            reflection_result = await self.cognitive_engine.reflection.reflect(
                output=feedback["content"],
                goal="Extract feedback insights",
                context=context,
                max_iterations=2,
            )

            return {
                "key_points": reflection_result.get("key_points", []),
                "themes": reflection_result.get("themes", []),
                "suggestions": reflection_result.get("suggestions", []),
                "quality_score": reflection_result.quality_score,
            }

        except Exception as e:
            return {"error": str(e)}

    async def _categorize_feedback(
        self,
        feedback: Dict[str, Any],
        insights: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Categorize feedback using analytics agent."""
        try:
            agent = self.agent_dispatcher.get_agent("analytics_agent")

            state = AgentState()
            state.update(
                {
                    "workspace_id": context["workspace_id"],
                    "user_id": context["user_id"],
                    "task": "categorize_feedback",
                    "feedback": feedback,
                    "insights": insights,
                }
            )

            result = await agent.execute(state)

            return result.get("categorization", {})

        except Exception as e:
            return {"error": str(e)}

    async def _analyze_feedback_sentiment(
        self, feedback: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze feedback sentiment."""
        try:
            # Use cognitive engine for sentiment analysis
            sentiment_result = await self.cognitive_engine.perception.perceive(
                text=feedback["content"], history=[]
            )

            return {
                "sentiment": sentiment_result.get("sentiment", "neutral"),
                "confidence": sentiment_result.get("confidence", 0.5),
                "emotions": sentiment_result.get("emotions", []),
                "tone": sentiment_result.get("tone", "neutral"),
            }

        except Exception as e:
            return {"error": str(e)}

    async def _identify_feedback_patterns(
        self, feedback: Dict[str, Any], workspace_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Identify patterns in feedback across workspace."""
        try:
            # Get similar feedback from memory
            similar_feedback = await self.memory_controller.search(
                workspace_id=workspace_id,
                query=feedback["content"][:100],  # Use first 100 chars for similarity
                memory_types=["feedback"],
                limit=10,
            )

            # Analyze patterns
            patterns = {
                "similar_feedback_count": len(similar_feedback),
                "common_themes": [],
                "recurring_issues": [],
                "trend_analysis": {},
            }

            # Extract common themes from similar feedback
            themes = {}
            for item in similar_feedback:
                content = item.content.lower()
                if "bug" in content:
                    themes["bug_reports"] = themes.get("bug_reports", 0) + 1
                if "feature" in content:
                    themes["feature_requests"] = themes.get("feature_requests", 0) + 1
                if "ui" in content or "interface" in content:
                    themes["ui_issues"] = themes.get("ui_issues", 0) + 1
                if "performance" in content:
                    themes["performance_issues"] = (
                        themes.get("performance_issues", 0) + 1
                    )

            patterns["common_themes"] = sorted(
                themes.items(), key=lambda x: x[1], reverse=True
            )

            return patterns

        except Exception as e:
            return {"error": str(e)}

    async def _generate_improvement_suggestions(
        self,
        feedback: Dict[str, Any],
        analysis: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate improvement suggestions from feedback."""
        try:
            # Use content creator agent for suggestions
            agent = self.agent_dispatcher.get_agent("content_creator")

            state = AgentState()
            state.update(
                {
                    "workspace_id": context["workspace_id"],
                    "user_id": context["user_id"],
                    "task": "generate_improvement_suggestions",
                    "feedback": feedback,
                    "analysis": analysis,
                }
            )

            result = await agent.execute(state)

            return result.get("suggestions", {})

        except Exception as e:
            return {"error": str(e)}

    async def _create_feedback_action_items(
        self, feedback_id: str, suggestions: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create action items from feedback suggestions."""
        try:
            action_items = []

            # Extract action items from suggestions
            suggestions_list = suggestions.get("action_items", [])

            for i, suggestion in enumerate(suggestions_list):
                action_item = {
                    "feedback_id": feedback_id,
                    "title": suggestion.get("title", f"Action Item {i+1}"),
                    "description": suggestion.get("description"),
                    "priority": suggestion.get("priority", "medium"),
                    "category": suggestion.get("category", "general"),
                    "status": "pending",
                    "created_at": time.time(),
                }

                # Store action item
                result = (
                    self.db_client.table("feedback_action_items")
                    .insert(action_item)
                    .execute()
                )
                if result.data:
                    action_items.append(result.data[0])

            return {"action_items": action_items, "total_items": len(action_items)}

        except Exception as e:
            return {"error": str(e)}

    async def _update_knowledge_base_with_feedback(
        self,
        feedback: Dict[str, Any],
        analysis: Dict[str, Any],
        suggestions: Dict[str, Any],
    ):
        """Update knowledge base with feedback insights."""
        try:
            workspace_id = feedback["workspace_id"]

            # Create knowledge entry
            knowledge_content = f"""
            Feedback Insights:
            Content: {feedback['content']}
            Type: {feedback['type']}
            Rating: {feedback['rating']}

            Key Insights:
            {str(analysis.get('insights', {}))}

            Suggestions:
            {str(suggestions)}
            """

            await self.memory_controller.store(
                workspace_id=workspace_id,
                memory_type="knowledge",
                content=knowledge_content,
                metadata={
                    "type": "feedback_insights",
                    "feedback_id": feedback["id"],
                    "feedback_type": feedback["type"],
                    "rating": feedback["rating"],
                    "timestamp": time.time(),
                },
            )

        except Exception as e:
            logger.error(f"Error updating knowledge base: {e}")

    async def _trigger_system_adaptations(
        self,
        feedback: Dict[str, Any],
        suggestions: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Trigger system adaptations based on feedback."""
        try:
            adaptations = []

            # Analyze feedback for system adaptations
            feedback_type = feedback["type"]
            rating = feedback.get("rating", 3)

            # Low rating feedback triggers adaptations
            if rating <= 2:
                if feedback_type == "ui":
                    adaptations.append(
                        {
                            "type": "ui_improvement",
                            "priority": "high",
                            "description": "UI improvement needed based on negative feedback",
                        }
                    )
                elif feedback_type == "performance":
                    adaptations.append(
                        {
                            "type": "performance_optimization",
                            "priority": "high",
                            "description": "Performance optimization needed",
                        }
                    )
                elif feedback_type == "feature":
                    adaptations.append(
                        {
                            "type": "feature_enhancement",
                            "priority": "medium",
                            "description": "Feature enhancement requested",
                        }
                    )

            # Store adaptations
            for adaptation in adaptations:
                adaptation_record = {
                    "feedback_id": feedback["id"],
                    "workspace_id": feedback["workspace_id"],
                    "type": adaptation["type"],
                    "priority": adaptation["priority"],
                    "description": adaptation["description"],
                    "status": "pending",
                    "created_at": time.time(),
                }

                self.db_client.table("system_adaptations").insert(
                    adaptation_record
                ).execute()

            return {"adaptations": adaptations, "total_adaptations": len(adaptations)}

        except Exception as e:
            return {"error": str(e)}

    async def _get_workspace_context(self, workspace_id: str) -> Dict[str, Any]:
        """Get workspace context."""
        try:
            workspace_result = (
                self.db_client.table("workspaces")
                .select("*")
                .eq("id", workspace_id)
                .execute()
            )

            if workspace_result.data:
                workspace = workspace_result.data[0]
                return {
                    "workspace_id": workspace_id,
                    "user_id": workspace["user_id"],
                    "workspace": workspace,
                }
            else:
                return {"workspace_id": workspace_id, "user_id": None}

        except Exception as e:
            logger.error(f"Error getting workspace context: {e}")
            return {"workspace_id": workspace_id, "user_id": None}
