"""
OnboardingWorkflow - End-to-end onboarding orchestration.
Handles all 13 steps of the onboarding process with agent coordination.
Enhanced with state management, validation, and error recovery.
"""

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from backend.agents.dispatcher import AgentDispatcher
from backend.agents.state import AgentState
from backend.cognitive import CognitiveEngine
from backend.memory.controller import MemoryController

from supabase import Client
from backend.services.onboarding_state_service import OnboardingStateService, StepStatus
from backend.services.onboarding_validator import OnboardingValidator
from backend.services.upstash_client import UpstashClient

logger = logging.getLogger(__name__)


class OnboardingWorkflow:
    """
    End-to-end onboarding workflow orchestrator.

    Handles the complete onboarding process from evidence collection
    through foundation creation to ICP generation.
    """

    def __init__(
        self,
        db_client: Client,
        memory_controller: MemoryController,
        cognitive_engine: CognitiveEngine,
        agent_dispatcher: AgentDispatcher,
        redis_client: UpstashClient,
    ):
        self.db_client = db_client
        self.memory_controller = memory_controller
        self.cognitive_engine = cognitive_engine
        self.agent_dispatcher = agent_dispatcher
        self.redis_client = redis_client
        
        # Initialize state management and validation
        self.state_service = OnboardingStateService(db_client, redis_client)
        self.validator = OnboardingValidator()
        self.workflow_id = str(uuid.uuid4())  # Unique workflow instance identifier

        # Define onboarding steps
        self.steps = [
            "evidence_upload",
            "evidence_extraction",
            "business_classification",
            "industry_analysis",
            "competitor_analysis",
            "value_proposition",
            "target_audience",
            "messaging_framework",
            "foundation_creation",
            "icp_generation",
            "move_planning",
            "campaign_setup",
            "onboarding_complete",
        ]

    async def execute_step(
        self, workspace_id: str, step: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a specific onboarding step with state management and validation.

        Args:
            workspace_id: Workspace ID
            step: Step to execute
            data: Step data

        Returns:
            Step execution result with state information
        """
        lock_owner = f"workflow_{self.workflow_id}"
        
        try:
            logger.info(
                f"Executing onboarding step: {step} for workspace {workspace_id}"
            )

            # Validate step input
            is_valid, validation_errors = self.validator.validate_step_input(step, data)
            if not is_valid:
                return {
                    "success": False,
                    "step": step,
                    "error": "Validation failed",
                    "validation_errors": validation_errors
                }

            # Check if step can be executed
            can_execute, reason = await self.state_service.can_execute_step(workspace_id, step)
            if not can_execute:
                return {
                    "success": False,
                    "step": step,
                    "error": "Step cannot be executed",
                    "reason": reason
                }

            # Acquire workspace lock
            lock_acquired = await self.state_service.acquire_lock(workspace_id, lock_owner)
            if not lock_acquired:
                return {
                    "success": False,
                    "step": step,
                    "error": "Workspace is locked by another operation"
                }

            # Update step status to IN_PROGRESS
            await self.state_service.update_step_state(
                workspace_id, step, StepStatus.IN_PROGRESS
            )

            # Get workspace context with accumulated data
            context = await self._get_workspace_context_with_data(workspace_id)

            # Execute step with error handling and retry
            result = await self._execute_step_with_retry(
                workspace_id, step, data, context
            )

            # Update step status based on result
            if result.get("success", False):
                await self.state_service.update_step_state(
                    workspace_id, step, StepStatus.COMPLETED, result_data=result
                )
            else:
                await self.state_service.update_step_state(
                    workspace_id, step, StepStatus.FAILED, error_message=result.get("error")
                )

            # Release lock
            await self.state_service.release_lock(workspace_id, lock_owner)

            # Get progress and next step
            progress = await self.state_service.get_progress_summary(workspace_id)
            next_step = await self._determine_next_step(workspace_id, step)

            return {
                "success": result.get("success", True),
                "step": step,
                "result": result,
                "next_step": next_step,
                "progress": progress,
                "workspace_id": workspace_id
            }

        except Exception as e:
            logger.error(f"Error executing onboarding step {step}: {e}")
            
            # Ensure lock is released on error
            try:
                await self.state_service.release_lock(workspace_id, lock_owner)
            except:
                pass
            
            return {
                "success": False,
                "step": step,
                "error": str(e),
                "workspace_id": workspace_id
            }

    async def _execute_step_with_retry(
        self, workspace_id: str, step: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute step with retry mechanism and error handling.
        """
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                # Execute step based on type
                if step == "evidence_upload":
                    result = await self._handle_evidence_upload(workspace_id, data, context)
                elif step == "evidence_extraction":
                    result = await self._handle_evidence_extraction(workspace_id, data, context)
                elif step == "business_classification":
                    result = await self._handle_business_classification(workspace_id, data, context)
                elif step == "industry_analysis":
                    result = await self._handle_industry_analysis(workspace_id, data, context)
                elif step == "competitor_analysis":
                    result = await self._handle_competitor_analysis(workspace_id, data, context)
                elif step == "value_proposition":
                    result = await self._handle_value_proposition(workspace_id, data, context)
                elif step == "target_audience":
                    result = await self._handle_target_audience(workspace_id, data, context)
                elif step == "messaging_framework":
                    result = await self._handle_messaging_framework(workspace_id, data, context)
                elif step == "foundation_creation":
                    result = await self._handle_foundation_creation(workspace_id, data, context)
                elif step == "icp_generation":
                    result = await self._handle_icp_generation(workspace_id, data, context)
                elif step == "move_planning":
                    result = await self._handle_move_planning(workspace_id, data, context)
                elif step == "campaign_setup":
                    result = await self._handle_campaign_setup(workspace_id, data, context)
                elif step == "onboarding_complete":
                    result = await self._handle_onboarding_complete(workspace_id, data, context)
                else:
                    result = {"success": False, "error": f"Unknown step: {step}"}
                
                # If successful, return result
                if result.get("success", False):
                    return result
                
                # If this is the last attempt, return the error
                if attempt == max_retries - 1:
                    return result
                
                # Wait before retry
                await asyncio.sleep(retry_delay * (attempt + 1))
                
            except Exception as e:
                logger.error(f"Step {step} attempt {attempt + 1} failed: {e}")
                
                # If this is the last attempt, return the error
                if attempt == max_retries - 1:
                    return {"success": False, "error": str(e)}
                
                # Wait before retry
                await asyncio.sleep(retry_delay * (attempt + 1))
        
        return {"success": False, "error": "Max retries exceeded"}
    
    async def _get_workspace_context_with_data(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get workspace context with accumulated data from completed steps.
        """
        try:
            # Get base context
            base_context = await self._get_workspace_context(workspace_id)
            
            # Get completed step data
            state = await self.state_service.get_state(workspace_id)
            if not state:
                return base_context
            
            # Accumulate data from completed steps
            accumulated_data = {}
            for step_id, step_state in state.steps.items():
                if step_state.status == StepStatus.COMPLETED and step_state.result_data:
                    accumulated_data[step_id] = step_state.result_data
            
            # Merge with base context
            base_context["accumulated_data"] = accumulated_data
            return base_context
            
        except Exception as e:
            logger.error(f"Error getting workspace context with data: {e}")
            return await self._get_workspace_context(workspace_id)
    
    async def _determine_next_step(self, workspace_id: str, current_step: str) -> Optional[str]:
        """
        Determine the next available step based on dependencies and completion status.
        """
        try:
            state = await self.state_service.get_state(workspace_id)
            if not state:
                return None
            
            # Find next step that can be executed
            for step_id in self.steps:
                if step_id == current_step:
                    continue
                
                # Skip if already completed
                step_state = state.steps.get(step_id)
                if step_state and step_state.status == StepStatus.COMPLETED:
                    continue
                
                # Check if can execute
                can_execute, _ = await self.state_service.can_execute_step(workspace_id, step_id)
                if can_execute:
                    return step_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error determining next step: {e}")
            return None
    
    async def resume_onboarding(self, workspace_id: str) -> Dict[str, Any]:
        """
        Resume onboarding from current state.
        """
        try:
            return await self.state_service.resume_onboarding(workspace_id)
        except Exception as e:
            logger.error(f"Error resuming onboarding: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_onboarding_status(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get comprehensive onboarding status.
        """
        try:
            return await self.state_service.get_progress_summary(workspace_id)
        except Exception as e:
            logger.error(f"Error getting onboarding status: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_evidence_upload(
        self, workspace_id: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle evidence upload step."""
        try:
            # Store uploaded files
            files = data.get("files", [])
            stored_files = []

            for file_data in files:
                # Store file in database
                file_record = {
                    "workspace_id": workspace_id,
                    "filename": file_data.get("filename"),
                    "file_type": file_data.get("file_type"),
                    "file_size": file_data.get("file_size"),
                    "file_path": file_data.get("file_path"),
                    "uploaded_at": time.time(),
                }

                result = (
                    self.db_client.table("evidence_files").insert(file_record).execute()
                )
                if result.data:
                    stored_files.append(result.data[0])

            return {
                "success": True,
                "files_stored": len(stored_files),
                "file_ids": [f["id"] for f in stored_files],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_evidence_extraction(
        self, workspace_id: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle evidence extraction step."""
        try:
            # Get evidence files
            files_result = (
                self.db_client.table("evidence_files")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )

            if not files_result.data:
                return {"success": False, "error": "No evidence files found"}

            # Use evidence processor agent
            agent = self.agent_dispatcher.get_agent("evidence_processor")
            if not agent:
                return {
                    "success": False,
                    "error": "Evidence processor agent not available",
                }

            # Prepare agent state
            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "files": files_result.data,
                    "task": "extract_business_evidence",
                }
            )

            # Execute agent
            result = await agent.execute(state)

            # Store extracted evidence
            extracted_data = result.get("extracted_evidence", {})

            evidence_record = {
                "workspace_id": workspace_id,
                "extracted_data": extracted_data,
                "extraction_timestamp": time.time(),
                "files_processed": len(files_result.data),
            }

            self.db_client.table("evidence_extractions").insert(
                evidence_record
            ).execute()

            return {
                "success": True,
                "extracted_evidence": extracted_data,
                "files_processed": len(files_result.data),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_business_classification(
        self, workspace_id: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle business classification step."""
        try:
            # Get extracted evidence
            evidence_result = (
                self.db_client.table("evidence_extractions")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )

            if not evidence_result.data:
                return {"success": False, "error": "No extracted evidence found"}

            # Use market research agent for classification
            agent = self.agent_dispatcher.get_agent("market_research")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "evidence_data": evidence_result.data[0]["extracted_data"],
                    "task": "classify_business",
                }
            )

            result = await agent.execute(state)

            classification = result.get("business_classification", {})

            return {"success": True, "classification": classification}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_industry_analysis(
        self, workspace_id: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle industry analysis step."""
        try:
            # Use market research agent
            agent = self.agent_dispatcher.get_agent("market_research")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "task": "analyze_industry",
                    "business_info": data.get("business_info", {}),
                }
            )

            result = await agent.execute(state)

            industry_analysis = result.get("industry_analysis", {})

            return {"success": True, "industry_analysis": industry_analysis}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_competitor_analysis(
        self, workspace_id: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle competitor analysis step."""
        try:
            # Use competitor intel agent
            agent = self.agent_dispatcher.get_agent("competitor_intel")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "task": "analyze_competitors",
                    "industry_info": data.get("industry_info", {}),
                }
            )

            result = await agent.execute(state)

            competitor_analysis = result.get("competitor_analysis", {})

            return {"success": True, "competitor_analysis": competitor_analysis}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_value_proposition(
        self, workspace_id: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle value proposition step."""
        try:
            # Use content creator agent
            agent = self.agent_dispatcher.get_agent("content_creator")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "task": "create_value_proposition",
                    "business_info": data.get("business_info", {}),
                    "competitor_info": data.get("competitor_info", {}),
                }
            )

            result = await agent.execute(state)

            value_proposition = result.get("value_proposition", {})

            return {"success": True, "value_proposition": value_proposition}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_target_audience(
        self, workspace_id: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle target audience step."""
        try:
            # Use ICP architect agent
            agent = self.agent_dispatcher.get_agent("icp_architect")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "task": "define_target_audience",
                    "value_proposition": data.get("value_proposition", {}),
                }
            )

            result = await agent.execute(state)

            target_audience = result.get("target_audience", {})

            return {"success": True, "target_audience": target_audience}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_messaging_framework(
        self, workspace_id: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle messaging framework step."""
        try:
            # Use content creator agent
            agent = self.agent_dispatcher.get_agent("content_creator")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "task": "create_messaging_framework",
                    "target_audience": data.get("target_audience", {}),
                    "value_proposition": data.get("value_proposition", {}),
                }
            )

            result = await agent.execute(state)

            messaging_framework = result.get("messaging_framework", {})

            return {"success": True, "messaging_framework": messaging_framework}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_foundation_creation(
        self, workspace_id: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle foundation creation step."""
        try:
            # Compile all onboarding data
            foundation_data = {
                "workspace_id": workspace_id,
                "business_name": data.get("business_name"),
                "business_description": data.get("business_description"),
                "industry": data.get("industry"),
                "classification": data.get("classification"),
                "industry_analysis": data.get("industry_analysis"),
                "competitor_analysis": data.get("competitor_analysis"),
                "value_proposition": data.get("value_proposition"),
                "target_audience": data.get("target_audience"),
                "messaging_framework": data.get("messaging_framework"),
                "created_at": time.time(),
            }

            # Create foundation record
            result = (
                self.db_client.table("foundations").insert(foundation_data).execute()
            )

            if result.data:
                foundation_id = result.data[0]["id"]

                # Store in memory
                await self.memory_controller.store(
                    workspace_id=workspace_id,
                    memory_type="foundation",
                    content=str(foundation_data),
                    metadata={"foundation_id": foundation_id},
                )

                return {
                    "success": True,
                    "foundation_id": foundation_id,
                    "foundation_data": foundation_data,
                }
            else:
                return {"success": False, "error": "Failed to create foundation"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_icp_generation(
        self, workspace_id: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle ICP generation step."""
        try:
            # Use ICP architect agent to generate ICPs
            agent = self.agent_dispatcher.get_agent("icp_architect")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "task": "generate_icps",
                    "foundation_data": data.get("foundation_data", {}),
                    "target_count": 3,  # Generate 3 ICPs
                }
            )

            result = await agent.execute(state)

            icps = result.get("generated_icps", [])

            # Store ICPs in database
            stored_icps = []
            for icp_data in icps:
                icp_record = {
                    "workspace_id": workspace_id,
                    "name": icp_data.get("name"),
                    "description": icp_data.get("description"),
                    "demographics": icp_data.get("demographics", {}),
                    "psychographics": icp_data.get("psychographics", {}),
                    "pain_points": icp_data.get("pain_points", []),
                    "created_at": time.time(),
                }

                db_result = (
                    self.db_client.table("icp_profiles").insert(icp_record).execute()
                )
                if db_result.data:
                    stored_icps.append(db_result.data[0])

            return {
                "success": True,
                "icps_generated": len(stored_icps),
                "icp_ids": [icp["id"] for icp in stored_icps],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_move_planning(
        self, workspace_id: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle move planning step."""
        try:
            # Use move strategist agent
            agent = self.agent_dispatcher.get_agent("move_strategist")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "task": "plan_initial_moves",
                    "foundation_data": data.get("foundation_data", {}),
                    "icps": data.get("icps", []),
                }
            )

            result = await agent.execute(state)

            moves = result.get("planned_moves", [])

            # Store moves in database
            stored_moves = []
            for move_data in moves:
                move_record = {
                    "workspace_id": workspace_id,
                    "title": move_data.get("title"),
                    "description": move_data.get("description"),
                    "type": move_data.get("type"),
                    "priority": move_data.get("priority"),
                    "status": "planned",
                    "created_at": time.time(),
                }

                db_result = self.db_client.table("moves").insert(move_record).execute()
                if db_result.data:
                    stored_moves.append(db_result.data[0])

            return {
                "success": True,
                "moves_planned": len(stored_moves),
                "move_ids": [move["id"] for move in stored_moves],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_campaign_setup(
        self, workspace_id: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle campaign setup step."""
        try:
            # Use campaign planner agent
            agent = self.agent_dispatcher.get_agent("campaign_planner")

            state = AgentState()
            state.update(
                {
                    "workspace_id": workspace_id,
                    "user_id": context["user_id"],
                    "task": "setup_initial_campaign",
                    "moves": data.get("moves", []),
                    "icps": data.get("icps", []),
                }
            )

            result = await agent.execute(state)

            campaign = result.get("campaign_setup", {})

            # Store campaign in database
            campaign_record = {
                "workspace_id": workspace_id,
                "name": campaign.get("name", "Initial Campaign"),
                "description": campaign.get("description"),
                "target_icps": campaign.get("target_icps", []),
                "status": "draft",
                "created_at": time.time(),
            }

            db_result = (
                self.db_client.table("campaigns").insert(campaign_record).execute()
            )

            if db_result.data:
                campaign_id = db_result.data[0]["id"]

                return {
                    "success": True,
                    "campaign_id": campaign_id,
                    "campaign_data": campaign,
                }
            else:
                return {"success": False, "error": "Failed to create campaign"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_onboarding_complete(
        self, workspace_id: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle onboarding completion step."""
        try:
            # Update workspace status
            self.db_client.table("workspaces").update(
                {
                    "onboarding_status": "completed",
                    "onboarding_completed_at": time.time(),
                }
            ).eq("id", workspace_id).execute()

            # Get evidence files
            files_result = (
                self.db_client.table("evidence_files")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )

            # Delete original OCR-processed files
            for file in files_result.data:
                if file.get('extracted_data') and file.get('status') == 'processed':
                    await self.db_client.storage.remove(file['original_path'])

            # Generate onboarding summary
            summary = await self._generate_onboarding_summary(workspace_id)
            
            # Generate and write businesscontext.json
            from backend.integration.context_builder import build_business_context_manifest
            bcm = await build_business_context_manifest(
                workspace_id=workspace_id,
                db_client=self.db_client,
                memory_controller=self.memory_controller,
                version_major=1,
                version_minor=0,
                version_patch=0
            )
            
            import json
            file_path = "businesscontext.json"
            with open(file_path, 'w') as f:
                json.dump(bcm['content'], f, indent=2)

            return {
                "success": True,
                "onboarding_complete": True,
                "summary": summary,
                "businesscontext_file": file_path
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _get_workspace_context(self, workspace_id: str) -> Dict[str, Any]:
        """Get workspace context for workflow execution."""
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

    async def _update_progress(
        self, workspace_id: str, step: str, result: Dict[str, Any]
    ):
        """Update onboarding progress."""
        try:
            progress_record = {
                "workspace_id": workspace_id,
                "step": step,
                "status": "completed" if result.get("success") else "failed",
                "completed_at": time.time(),
                "result_data": result,
            }

            self.db_client.table("onboarding_progress").upsert(
                progress_record
            ).execute()

        except Exception as e:
            logger.error(f"Error updating progress: {e}")

    def _get_next_step(self, current_step: str) -> Optional[str]:
        """Get the next step in the onboarding process."""
        try:
            current_index = self.steps.index(current_step)
            if current_index < len(self.steps) - 1:
                return self.steps[current_index + 1]
            return None
        except ValueError:
            return None

    async def _get_progress(self, workspace_id: str) -> Dict[str, Any]:
        """Get current onboarding progress."""
        try:
            progress_result = (
                self.db_client.table("onboarding_progress")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )

            completed_steps = [
                p["step"] for p in progress_result.data if p["status"] == "completed"
            ]

            return {
                "total_steps": len(self.steps),
                "completed_steps": len(completed_steps),
                "progress_percentage": (len(completed_steps) / len(self.steps)) * 100,
                "completed_step_names": completed_steps,
            }

        except Exception as e:
            logger.error(f"Error getting progress: {e}")
            return {
                "total_steps": len(self.steps),
                "completed_steps": 0,
                "progress_percentage": 0,
            }

    async def _generate_onboarding_summary(self, workspace_id: str) -> Dict[str, Any]:
        """Generate onboarding completion summary."""
        try:
            # Get foundation
            foundation_result = (
                self.db_client.table("foundations")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )

            # Get ICPs
            icp_result = (
                self.db_client.table("icp_profiles")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )

            # Get moves
            moves_result = (
                self.db_client.table("moves")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )

            # Get campaigns
            campaign_result = (
                self.db_client.table("campaigns")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )

            return {
                "foundation_created": bool(foundation_result.data),
                "icps_generated": len(icp_result.data) if icp_result.data else 0,
                "moves_planned": len(moves_result.data) if moves_result.data else 0,
                "campaigns_created": (
                    len(campaign_result.data) if campaign_result.data else 0
                ),
                "workspace_ready": all(
                    [
                        bool(foundation_result.data),
                        len(icp_result.data) > 0,
                        len(moves_result.data) > 0,
                    ]
                ),
            }

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {"error": str(e)}
