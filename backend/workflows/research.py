"""
ResearchWorkflow - End-to-end research orchestration.
Handles research execution, findings storage, and result presentation.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from memory.controller import MemoryController

from cognitive import CognitiveEngine
from supabase import Client

from .agents.dispatcher import AgentDispatcher
from .agents.state import AgentState

logger = logging.getLogger(__name__)


class ResearchWorkflow:
    """
    End-to-end research workflow orchestrator.

    Handles the complete research process from query initiation
    through data collection, analysis, findings storage, and presentation.
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

    async def conduct_research(
        self, workspace_id: str, query: str, research_type: str = "market"
    ) -> Dict[str, Any]:
        """
        Conduct research with full orchestration.

        Args:
            workspace_id: Workspace ID
            query: Research query
            research_type: Type of research (market, competitor, industry, trend)

        Returns:
            Research execution result
        """
        try:
            logger.info(f"Conducting research: {query} for workspace {workspace_id}")

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Plan research approach
            planning_result = await self._plan_research_approach(
                workspace_id, query, research_type, context
            )

            if not planning_result["success"]:
                return planning_result

            # Step 2: Create research record
            research_record = {
                "workspace_id": workspace_id,
                "query": query,
                "research_type": research_type,
                "status": "initiated",
                "approach": planning_result["approach"],
                "estimated_duration": planning_result["estimated_duration"],
                "initiated_at": time.time(),
            }

            result = (
                self.db_client.table("research_sessions")
                .insert(research_record)
                .execute()
            )

            if not result.data:
                return {"success": False, "error": "Failed to create research record"}

            research_id = result.data[0]["id"]

            # Step 3: Execute research phases
            execution_results = await self._execute_research_phases(
                research_id, planning_result["approach"], context
            )

            # Step 4: Analyze findings
            analysis_result = await self._analyze_research_findings(
                research_id, execution_results, context
            )

            # Step 5: Generate insights
            insights_result = await self._generate_research_insights(
                research_id, analysis_result, context
            )

            # Step 6: Store findings
            storage_result = await self._store_research_findings(
                research_id, analysis_result, insights_result
            )

            # Step 7: Update research status
            self.db_client.table("research_sessions").update(
                {
                    "status": "completed",
                    "completed_at": time.time(),
                    "findings_count": len(analysis_result.get("findings", [])),
                    "insights_count": len(insights_result.get("insights", [])),
                }
            ).eq("id", research_id).execute()

            return {
                "success": True,
                "research_id": research_id,
                "query": query,
                "research_type": research_type,
                "approach": planning_result["approach"],
                "execution_results": execution_results,
                "analysis": analysis_result,
                "insights": insights_result,
                "findings_count": len(analysis_result.get("findings", [])),
                "completed_at": time.time(),
            }

        except Exception as e:
            logger.error(f"Error conducting research: {e}")
            return {"success": False, "error": str(e)}

    async def store_findings(
        self, workspace_id: str, findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store research findings in database and memory.

        Args:
            workspace_id: Workspace ID
            findings: Research findings to store

        Returns:
            Storage result
        """
        try:
            logger.info(f"Storing research findings for workspace {workspace_id}")

            # Step 1: Store in database
            findings_record = {
                "workspace_id": workspace_id,
                "findings_data": findings,
                "stored_at": time.time(),
            }

            result = (
                self.db_client.table("research_findings")
                .insert(findings_record)
                .execute()
            )

            if not result.data:
                return {
                    "success": False,
                    "error": "Failed to store findings in database",
                }

            findings_id = result.data[0]["id"]

            # Step 2: Store in memory
            await self._store_findings_in_memory(workspace_id, findings_id, findings)

            # Step 3: Update graph memory with entities
            await self._update_graph_memory_with_findings(workspace_id, findings)

            return {
                "success": True,
                "findings_id": findings_id,
                "stored_at": time.time(),
            }

        except Exception as e:
            logger.error(f"Error storing findings: {e}")
            return {"success": False, "error": str(e)}

    async def present_results(self, research_id: str) -> Dict[str, Any]:
        """
        Present research results in formatted way.

        Args:
            research_id: Research ID to present

        Returns:
            Presentation result
        """
        try:
            logger.info(f"Presenting research results for {research_id}")

            # Get research session
            research_result = (
                self.db_client.table("research_sessions")
                .select("*")
                .eq("id", research_id)
                .execute()
            )

            if not research_result.data:
                return {"success": False, "error": "Research session not found"}

            research = research_result.data[0]
            workspace_id = research["workspace_id"]

            # Get findings
            findings_result = (
                self.db_client.table("research_findings")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Generate presentation
            presentation_result = await self._generate_research_presentation(
                research, findings_result.data, context
            )

            # Step 2: Create presentation record
            presentation_record = {
                "research_id": research_id,
                "workspace_id": workspace_id,
                "presentation_data": presentation_result,
                "created_at": time.time(),
            }

            result = (
                self.db_client.table("research_presentations")
                .insert(presentation_record)
                .execute()
            )

            if result.data:
                presentation_id = result.data[0]["id"]

                return {
                    "success": True,
                    "presentation_id": presentation_id,
                    "presentation": presentation_result,
                    "research_summary": research,
                    "findings_count": len(findings_result.data),
                }
            else:
                return {"success": False, "error": "Failed to create presentation"}

        except Exception as e:
            logger.error(f"Error presenting results: {e}")
            return {"success": False, "error": str(e)}

    async def _plan_research_approach(
        self, workspace_id: str, query: str, research_type: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Plan research approach using market research agent."""
        try:
            agent = self.agent_dispatcher.get_agent("market_research")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "query": query,
                    "research_type": research_type,
                    "task": "plan_research_approach",
                }
            )

            result = await agent.execute(state)

            approach = result.get("research_approach", {})

            if not approach:
                return {
                    "success": False,
                    "error": "Failed to generate research approach",
                }

            return {"success": True, "approach": approach}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_research_phases(
        self, research_id: str, approach: Dict[str, Any], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute research phases based on approach."""
        try:
            phases = approach.get("phases", [])
            execution_results = []

            for phase in phases:
                phase_result = await self._execute_research_phase(
                    research_id, phase, context
                )
                execution_results.append(phase_result)

                # Update research progress
                await self._update_research_progress(research_id, phase, phase_result)

            return execution_results

        except Exception as e:
            logger.error(f"Error executing research phases: {e}")
            return []

    async def _execute_research_phase(
        self, research_id: str, phase: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single research phase."""
        try:
            phase_name = phase.get("name")
            phase_type = phase.get("type")

            logger.info(f"Executing research phase: {phase_name}")

            # Get appropriate agent for phase type
            agent_name = self._get_agent_for_phase_type(phase_type)
            agent = self.agent_dispatcher.get_agent(agent_name)

            if not agent:
                return {"success": False, "error": f"Agent {agent_name} not available"}

            # Prepare agent state
            state = AgentState()
            state.update(
                {
                    "workspace_id": context["workspace_id"],
                    "user_id": context["user_id"],
                    "research_id": research_id,
                    "phase": phase,
                    "task": f"execute_research_phase_{phase_type}",
                }
            )

            # Execute phase
            start_time = time.time()
            result = await agent.execute(state)
            execution_time = time.time() - start_time

            # Process phase results
            phase_data = result.get("phase_data", {})

            return {
                "success": True,
                "phase_name": phase_name,
                "phase_type": phase_type,
                "execution_time": execution_time,
                "data": phase_data,
                "agent_used": agent_name,
            }

        except Exception as e:
            logger.error(f"Error executing research phase: {e}")
            return {"success": False, "error": str(e)}

    def _get_agent_for_phase_type(self, phase_type: str) -> str:
        """Get appropriate agent for research phase type."""
        agent_map = {
            "market_research": "market_research",
            "competitor_analysis": "competitor_intel",
            "industry_analysis": "market_research",
            "trend_analysis": "trend_analyzer",
            "data_collection": "fact_extractor",
            "survey_analysis": "analytics_agent",
            "web_scraping": "fact_extractor",
        }

        return agent_map.get(phase_type, "market_research")

    async def _update_research_progress(
        self, research_id: str, phase: Dict[str, Any], phase_result: Dict[str, Any]
    ):
        """Update research progress."""
        try:
            progress_record = {
                "research_id": research_id,
                "phase_name": phase.get("name"),
                "status": "completed" if phase_result["success"] else "failed",
                "completed_at": time.time(),
                "execution_time": phase_result.get("execution_time", 0),
                "data": phase_result.get("data", {}),
            }

            self.db_client.table("research_progress").insert(progress_record).execute()

        except Exception as e:
            logger.error(f"Error updating research progress: {e}")

    async def _analyze_research_findings(
        self,
        research_id: str,
        execution_results: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze research findings from execution results."""
        try:
            # Collect all data from phases
            all_data = {}
            for result in execution_results:
                if result["success"]:
                    phase_name = result["phase_name"]
                    all_data[phase_name] = result.get("data", {})

            # Use analytics agent for analysis
            agent = self.agent_dispatcher.get_agent("analytics_agent")

            state = AgentState()
            state.update(
                {
                    "workspace_id": context["workspace_id"],
                    "user_id": context["user_id"],
                    "research_id": research_id,
                    "phase_data": all_data,
                    "task": "analyze_research_findings",
                }
            )

            result = await agent.execute(state)

            findings = result.get("findings", [])

            return {
                "findings": findings,
                "total_phases": len(execution_results),
                "successful_phases": len(
                    [r for r in execution_results if r["success"]]
                ),
            }

        except Exception as e:
            return {"findings": [], "error": str(e)}

    async def _generate_research_insights(
        self, research_id: str, analysis_result: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights from research analysis."""
        try:
            # Use market research agent for insights
            agent = self.agent_dispatcher.get_agent("market_research")

            state = AgentState()
            state.update(
                {
                    "workspace_id": context["workspace_id"],
                    "user_id": context["user_id"],
                    "research_id": research_id,
                    "findings": analysis_result.get("findings", []),
                    "task": "generate_research_insights",
                }
            )

            result = await agent.execute(state)

            insights = result.get("insights", [])

            return {"insights": insights, "insights_count": len(insights)}

        except Exception as e:
            return {"insights": [], "error": str(e)}

    async def _store_research_findings(
        self,
        research_id: str,
        analysis_result: Dict[str, Any],
        insights_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Store research findings in database."""
        try:
            findings_record = {
                "research_id": research_id,
                "findings": analysis_result.get("findings", []),
                "insights": insights_result.get("insights", []),
                "analysis_summary": {
                    "total_findings": len(analysis_result.get("findings", [])),
                    "total_insights": len(insights_result.get("insights", [])),
                    "analysis_timestamp": time.time(),
                },
                "stored_at": time.time(),
            }

            result = (
                self.db_client.table("research_findings")
                .insert(findings_record)
                .execute()
            )

            if result.data:
                return {"success": True, "findings_id": result.data[0]["id"]}
            else:
                return {"success": False, "error": "Failed to store findings"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _store_findings_in_memory(
        self, workspace_id: str, findings_id: str, findings: Dict[str, Any]
    ):
        """Store findings in memory system."""
        try:
            content = f"""
            Research Findings:
            Findings Count: {len(findings.get("findings", []))}
            Insights Count: {len(findings.get("insights", []))}

            Key Findings:
            {str(findings.get("findings", [])[:3])}

            Key Insights:
            {str(findings.get("insights", [])[:3])}
            """

            await self.memory_controller.store(
                workspace_id=workspace_id,
                memory_type="research",
                content=content,
                metadata={
                    "findings_id": findings_id,
                    "type": "research_findings",
                    "findings_count": len(findings.get("findings", [])),
                    "insights_count": len(findings.get("insights", [])),
                },
            )

        except Exception as e:
            logger.error(f"Error storing findings in memory: {e}")

    async def _update_graph_memory_with_findings(
        self, workspace_id: str, findings: Dict[str, Any]
    ):
        """Update graph memory with research entities."""
        try:
            # Extract entities from findings and insights
            entities = []

            for finding in findings.get("findings", []):
                if isinstance(finding, dict):
                    # Extract entities from finding
                    entity_data = {
                        "type": "research_finding",
                        "name": finding.get("title", "Unnamed Finding"),
                        "properties": {
                            "category": finding.get("category"),
                            "impact": finding.get("impact"),
                            "confidence": finding.get("confidence"),
                        },
                    }
                    entities.append(entity_data)

            for insight in findings.get("insights", []):
                if isinstance(insight, dict):
                    # Extract entities from insights
                    entity_data = {
                        "type": "research_insight",
                        "name": insight.get("title", "Unnamed Insight"),
                        "properties": {
                            "category": insight.get("category"),
                            "actionability": insight.get("actionability"),
                            "priority": insight.get("priority"),
                        },
                    }
                    entities.append(entity_data)

            # Add entities to graph memory
            for entity in entities:
                await self.memory_controller.graph_memory.add_entity(
                    workspace_id=workspace_id,
                    entity_type=entity["type"],
                    name=entity["name"],
                    properties=entity["properties"],
                )

        except Exception as e:
            logger.error(f"Error updating graph memory: {e}")

    async def _generate_research_presentation(
        self,
        research: Dict[str, Any],
        findings: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate formatted research presentation."""
        try:
            # Use content creator agent for presentation
            agent = self.agent_dispatcher.get_agent("content_creator")

            state = AgentState()
            state.update(
                {
                    "workspace_id": context["workspace_id"],
                    "user_id": context["user_id"],
                    "task": "generate_research_presentation",
                    "research": research,
                    "findings": findings,
                    "presentation_format": "executive_summary",
                }
            )

            result = await agent.execute(state)

            presentation = result.get("presentation", {})

            return {
                "title": presentation.get(
                    "title", f"Research Report: {research['query']}"
                ),
                "summary": presentation.get("summary"),
                "key_findings": presentation.get("key_findings", []),
                "recommendations": presentation.get("recommendations", []),
                "appendix": presentation.get("appendix", {}),
                "generated_at": time.time(),
            }

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
