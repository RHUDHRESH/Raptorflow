"""
Output processing pipeline.
Runs quality checks, stores in database, updates memory, and triggers events.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from backend.cognitive.quality import QualityChecker
from backend.memory.controller import MemoryController

from supabase import Client

logger = logging.getLogger(__name__)


async def process_output(
    output: str,
    workspace_id: str,
    user_id: str,
    agent_name: str,
    output_type: str = "content",
    metadata: Dict[str, Any] = None,
    db_client: Client = None,
    memory_controller: MemoryController = None,
    quality_checker: QualityChecker = None,
) -> Dict[str, Any]:
    """
    Process output through quality check, storage, memory update, and events.

    Args:
        output: Generated output
        workspace_id: Workspace ID
        user_id: User ID
        agent_name: Agent that generated output
        output_type: Type of output (content, analysis, strategy, etc.)
        metadata: Additional metadata
        db_client: Database client
        memory_controller: Memory controller
        quality_checker: Quality checker

    Returns:
        Processing results
    """
    try:
        logger.info(f"Processing {output_type} output from {agent_name}")

        results = {
            "output": output,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "agent_name": agent_name,
            "output_type": output_type,
            "timestamp": time.time(),
        }

        # Step 1: Quality check
        quality_result = await _run_quality_check(output, quality_checker)
        results["quality"] = quality_result

        # Step 2: Store in database
        if db_client:
            storage_result = await _store_in_database(
                output,
                workspace_id,
                user_id,
                agent_name,
                output_type,
                quality_result,
                metadata,
                db_client,
            )
            results["storage"] = storage_result

        # Step 3: Update memory
        if memory_controller:
            memory_result = await _update_memory(
                output,
                workspace_id,
                agent_name,
                output_type,
                quality_result,
                metadata,
                memory_controller,
            )
            results["memory"] = memory_result

        # Step 4: Trigger events
        event_result = await _trigger_events(
            output,
            workspace_id,
            user_id,
            agent_name,
            output_type,
            quality_result,
            metadata,
        )
        results["events"] = event_result

        # Step 5: Generate summary
        results["summary"] = _generate_processing_summary(results)

        logger.info(f"Output processing completed: {results['summary']['status']}")

        return results

    except Exception as e:
        logger.error(f"Error processing output: {e}")
        return {
            "output": output,
            "error": str(e),
            "workspace_id": workspace_id,
            "agent_name": agent_name,
            "timestamp": time.time(),
        }


async def _run_quality_check(
    output: str, quality_checker: QualityChecker
) -> Dict[str, Any]:
    """Run quality check on output."""
    try:
        if not quality_checker:
            return {
                "score": 0.5,
                "approved": True,
                "feedback": "No quality checker available",
                "checks_performed": [],
            }

        # Run quality check
        quality_result = await quality_checker.check_quality(output)

        return {
            "score": quality_result.score,
            "approved": quality_result.approved,
            "feedback": quality_result.feedback,
            "checks_performed": quality_result.checks_performed,
            "improvements": quality_result.improvements,
            "timestamp": time.time(),
        }

    except Exception as e:
        logger.error(f"Error in quality check: {e}")
        return {
            "score": 0.0,
            "approved": False,
            "error": str(e),
            "checks_performed": [],
        }


async def _store_in_database(
    output: str,
    workspace_id: str,
    user_id: str,
    agent_name: str,
    output_type: str,
    quality_result: Dict[str, Any],
    metadata: Dict[str, Any],
    db_client: Client,
) -> Dict[str, Any]:
    """Store output in database."""
    try:
        # Determine table based on output type
        if output_type == "content":
            table = "muse_assets"
            data = {
                "workspace_id": workspace_id,
                "user_id": user_id,
                "title": metadata.get("title", f"Content from {agent_name}"),
                "content": output,
                "content_type": metadata.get("content_type", "text"),
                "agent_generated": True,
                "agent_name": agent_name,
                "quality_score": quality_result.get("score", 0.0),
                "status": (
                    "approved" if quality_result.get("approved", False) else "pending"
                ),
                "created_at": time.time(),
            }
        elif output_type == "move":
            table = "moves"
            data = {
                "workspace_id": workspace_id,
                "user_id": user_id,
                "title": metadata.get("title", f"Move from {agent_name}"),
                "description": output,
                "agent_generated": True,
                "agent_name": agent_name,
                "quality_score": quality_result.get("score", 0.0),
                "status": "planned",
                "created_at": time.time(),
            }
        elif output_type == "campaign":
            table = "campaigns"
            data = {
                "workspace_id": workspace_id,
                "user_id": user_id,
                "name": metadata.get("name", f"Campaign from {agent_name}"),
                "description": output,
                "agent_generated": True,
                "agent_name": agent_name,
                "quality_score": quality_result.get("score", 0.0),
                "status": "draft",
                "created_at": time.time(),
            }
        else:
            # Generic content storage
            table = "generated_content"
            data = {
                "workspace_id": workspace_id,
                "user_id": user_id,
                "content": output,
                "content_type": output_type,
                "agent_name": agent_name,
                "quality_score": quality_result.get("score", 0.0),
                "metadata": metadata,
                "created_at": time.time(),
            }

        # Insert into database
        result = db_client.table(table).insert(data).execute()

        if result.data:
            return {
                "success": True,
                "table": table,
                "record_id": result.data[0]["id"],
                "stored_at": time.time(),
            }
        else:
            return {"success": False, "error": "No data returned from database"}

    except Exception as e:
        logger.error(f"Error storing in database: {e}")
        return {"success": False, "error": str(e)}


async def _update_memory(
    output: str,
    workspace_id: str,
    agent_name: str,
    output_type: str,
    quality_result: Dict[str, Any],
    metadata: Dict[str, Any],
    memory_controller: MemoryController,
) -> Dict[str, Any]:
    """Update memory with output."""
    try:
        # Store as episodic memory
        memory_content = f"""
        Agent: {agent_name}
        Type: {output_type}
        Quality Score: {quality_result.get('score', 0.0)}

        Output:
        {output[:1000]}...
        """

        memory_id = await memory_controller.store(
            workspace_id=workspace_id,
            memory_type="conversation",
            content=memory_content,
            metadata={
                "agent": agent_name,
                "output_type": output_type,
                "quality_score": quality_result.get("score", 0.0),
                "approved": quality_result.get("approved", False),
                "timestamp": time.time(),
            },
        )

        # Update graph memory if applicable
        if output_type in ["icp", "move", "campaign"]:
            await _update_graph_memory(
                workspace_id, output, output_type, metadata, memory_controller
            )

        return {"success": True, "memory_id": memory_id, "stored_at": time.time()}

    except Exception as e:
        logger.error(f"Error updating memory: {e}")
        return {"success": False, "error": str(e)}


async def _update_graph_memory(
    workspace_id: str,
    output: str,
    output_type: str,
    metadata: Dict[str, Any],
    memory_controller: MemoryController,
):
    """Update graph memory with entities."""
    try:
        if output_type == "icp":
            from backend.memory.graph_builders.icp import ICPEntityBuilder

            builder = ICPEntityBuilder()
            await builder.build_icp_entity(workspace_id, metadata)
        elif output_type == "move":
            from backend.memory.graph_builders.move import MoveEntityBuilder

            builder = MoveEntityBuilder()
            await builder.build_move_entity(workspace_id, metadata)
        elif output_type == "campaign":
            from backend.memory.graph_builders.campaign import CampaignEntityBuilder

            builder = CampaignEntityBuilder()
            await builder.build_campaign_entity(workspace_id, metadata)

    except Exception as e:
        logger.warning(f"Error updating graph memory: {e}")


async def _trigger_events(
    output: str,
    workspace_id: str,
    user_id: str,
    agent_name: str,
    output_type: str,
    quality_result: Dict[str, Any],
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """Trigger relevant events."""
    try:
        from .events_all import get_event_bus

        event_bus = get_event_bus()
        if not event_bus:
            return {"success": False, "error": "Event bus not available"}

        events_triggered = []

        # Content generation event
        if output_type in ["content", "analysis", "strategy"]:
            await event_bus.emit(
                "content.generated",
                {
                    "workspace_id": workspace_id,
                    "user_id": user_id,
                    "content": output,
                    "agent": agent_name,
                    "content_type": output_type,
                    "quality_score": quality_result.get("score", 0.0),
                },
            )
            events_triggered.append("content.generated")

        # Quality event
        if quality_result.get("approved", False):
            await event_bus.emit(
                "quality.approved",
                {
                    "workspace_id": workspace_id,
                    "user_id": user_id,
                    "agent": agent_name,
                    "output_type": output_type,
                    "quality_score": quality_result.get("score", 0.0),
                },
            )
            events_triggered.append("quality.approved")
        else:
            await event_bus.emit(
                "quality.rejected",
                {
                    "workspace_id": workspace_id,
                    "user_id": user_id,
                    "agent": agent_name,
                    "output_type": output_type,
                    "quality_score": quality_result.get("score", 0.0),
                    "feedback": quality_result.get("feedback", ""),
                },
            )
            events_triggered.append("quality.rejected")

        return {
            "success": True,
            "events_triggered": events_triggered,
            "triggered_at": time.time(),
        }

    except Exception as e:
        logger.error(f"Error triggering events: {e}")
        return {"success": False, "error": str(e)}


def _generate_processing_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate processing summary."""
    try:
        summary = {
            "status": "completed",
            "success": True,
            "processing_steps": [],
            "quality_score": results.get("quality", {}).get("score", 0.0),
            "approved": results.get("quality", {}).get("approved", False),
            "storage_success": results.get("storage", {}).get("success", False),
            "memory_success": results.get("memory", {}).get("success", False),
            "events_triggered": len(
                results.get("events", {}).get("events_triggered", [])
            ),
        }

        # Add processing steps
        if "quality" in results:
            summary["processing_steps"].append("quality_check")
        if "storage" in results:
            summary["processing_steps"].append("database_storage")
        if "memory" in results:
            summary["processing_steps"].append("memory_update")
        if "events" in results:
            summary["processing_steps"].append("event_triggering")

        # Check for errors
        errors = []
        for step in ["quality", "storage", "memory", "events"]:
            if step in results and not results[step].get("success", True):
                errors.append(f"{step}_failed")

        if errors:
            summary["status"] = "completed_with_errors"
            summary["errors"] = errors

        return summary

    except Exception as e:
        return {"status": "error", "error": str(e)}


class OutputProcessor:
    """
    Advanced output processor with batching and optimization.
    """

    def __init__(
        self,
        db_client: Client,
        memory_controller: MemoryController,
        quality_checker: QualityChecker,
    ):
        self.db_client = db_client
        self.memory_controller = memory_controller
        self.quality_checker = quality_checker
        self.processing_queue = []
        self.batch_size = 10

    async def process_single(
        self,
        output: str,
        workspace_id: str,
        user_id: str,
        agent_name: str,
        output_type: str = "content",
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Process single output."""
        return await process_output(
            output,
            workspace_id,
            user_id,
            agent_name,
            output_type,
            metadata,
            self.db_client,
            self.memory_controller,
            self.quality_checker,
        )

    async def process_batch(
        self, outputs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process multiple outputs in batch."""
        results = []

        for output_data in outputs:
            result = await self.process_single(
                output_data["output"],
                output_data["workspace_id"],
                output_data["user_id"],
                output_data["agent_name"],
                output_data.get("output_type", "content"),
                output_data.get("metadata"),
            )
            results.append(result)

        return results

    async def queue_for_processing(self, output_data: Dict[str, Any]):
        """Queue output for batch processing."""
        self.processing_queue.append(output_data)

        if len(self.processing_queue) >= self.batch_size:
            await self.process_queue()

    async def process_queue(self) -> List[Dict[str, Any]]:
        """Process queued outputs."""
        if not self.processing_queue:
            return []

        outputs_to_process = self.processing_queue.copy()
        self.processing_queue.clear()

        return await self.process_batch(outputs_to_process)
