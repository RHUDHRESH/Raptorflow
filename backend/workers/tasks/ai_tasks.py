"""
AI-related background tasks for Celery
Handles OpenAI API calls, agent processing, and other AI workloads
"""

import logging
import time
from typing import Any, Dict, List, Optional

from backend.core.celery_manager import celery_app
from backend.core.circuit_breaker import get_resilient_client

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="workers.tasks.ai_tasks.process_openai_request")
def process_openai_request(
    self,
    user_id: str,
    workspace_id: str,
    prompt: str,
    model: str = "gpt-4",
    max_tokens: int = 1000,
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """
    Process OpenAI API request in background

    Args:
        user_id: User ID
        workspace_id: Workspace ID
        prompt: Input prompt
        model: OpenAI model to use
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature

    Returns:
        Dictionary with response and metadata
    """
    try:
        logger.info(f"Processing OpenAI request for user {user_id}")

        # Get resilient HTTP client
        client = get_resilient_client()

        # Make API call with circuit breaker protection
        import asyncio

        async def make_request():
            response = await client.post(
                service_name="openai",
                url="https://api.openai.com/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    "Content-Type": "application/json",
                },
            )
            return response.json()

        # Run async request in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response_data = loop.run_until_complete(make_request())
        loop.close()

        # Extract response
        if "choices" in response_data and len(response_data["choices"]) > 0:
            content = response_data["choices"][0]["message"]["content"]
            usage = response_data.get("usage", {})

            return {
                "success": True,
                "content": content,
                "usage": usage,
                "model": model,
                "user_id": user_id,
                "workspace_id": workspace_id,
                "processing_time": time.time(),
            }
        else:
            raise Exception("Invalid response from OpenAI API")

    except Exception as e:
        logger.error(f"OpenAI request failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "user_id": user_id,
            "workspace_id": workspace_id,
        }


@celery_app.task(bind=True, name="workers.tasks.ai_tasks.process_agent_chain")
def process_agent_chain(
    self,
    user_id: str,
    workspace_id: str,
    agent_name: str,
    input_data: Dict[str, Any],
    chain_steps: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Process multi-step agent chain in background

    Args:
        user_id: User ID
        workspace_id: Workspace ID
        agent_name: Name of the agent
        input_data: Input data for the chain
        chain_steps: List of processing steps

    Returns:
        Dictionary with chain results
    """
    try:
        logger.info(f"Processing agent chain {agent_name} for user {user_id}")

        results = []
        current_data = input_data

        for i, step in enumerate(chain_steps):
            step_name = step.get("name", f"step_{i}")
            step_type = step.get("type", "process")

            logger.info(f"Executing step {step_name}")

            # Process step based on type
            if step_type == "openai":
                # Submit OpenAI sub-task
                from core.celery_manager import get_task_manager

                manager = get_task_manager()

                subtask = manager.submit_task(
                    task_name="workers.tasks.ai_tasks.process_openai_request",
                    kwargs={
                        "user_id": user_id,
                        "workspace_id": workspace_id,
                        "prompt": step.get("prompt", ""),
                        "model": step.get("model", "gpt-4"),
                        "max_tokens": step.get("max_tokens", 1000),
                        "temperature": step.get("temperature", 0.7),
                    },
                )

                # Wait for subtask completion
                while not subtask.ready():
                    time.sleep(0.1)

                step_result = subtask.get()

            elif step_type == "transform":
                # Simple data transformation
                step_result = {
                    "success": True,
                    "data": current_data,
                    "transform": step.get("transform", {}),
                }

            else:
                step_result = {
                    "success": False,
                    "error": f"Unknown step type: {step_type}",
                }

            # Check if step failed
            if not step_result.get("success", False):
                logger.error(f"Step {step_name} failed: {step_result.get('error')}")
                return {
                    "success": False,
                    "error": f"Chain failed at step {step_name}",
                    "failed_step": step_name,
                    "results": results,
                }

            # Update current data
            current_data = step_result.get("data", step_result)
            results.append({"step": step_name, "result": step_result})

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "current_step": i + 1,
                    "total_steps": len(chain_steps),
                    "step_name": step_name,
                    "progress": ((i + 1) / len(chain_steps)) * 100,
                },
            )

        return {
            "success": True,
            "agent_name": agent_name,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "results": results,
            "final_data": current_data,
        }

    except Exception as e:
        logger.error(f"Agent chain processing failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "agent_name": agent_name,
            "user_id": user_id,
            "workspace_id": workspace_id,
        }


@celery_app.task(bind=True, name="workers.tasks.ai_tasks.process_icp_generation")
def process_icp_generation(
    self,
    user_id: str,
    workspace_id: str,
    foundation_data: Dict[str, Any],
    generation_config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Process ICP generation in background

    Args:
        user_id: User ID
        workspace_id: Workspace ID
        foundation_data: Foundation data for ICP generation
        generation_config: Generation configuration

    Returns:
        Dictionary with generated ICPs
    """
    try:
        logger.info(f"Generating ICPs for user {user_id}")

        # Simulate ICP generation process
        time.sleep(2)  # Simulate processing time

        # Generate ICPs using actual generation logic
        # TODO: Implement real ICP generation using AI models
        generated_icps = [
            {
                "id": f"icp_{i}",
                "name": f"ICP {i+1}",
                "description": f"Generated ICP {i+1} based on foundation data",
                "attributes": {
                    "industry": foundation_data.get("industry", "Technology"),
                    "size": foundation_data.get("company_size", "Mid-Market"),
                    "region": foundation_data.get("region", "North America"),
                },
            }
            for i in range(generation_config.get("count", 3))
        ]

        return {
            "success": True,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "generated_icps": generated_icps,
            "generation_config": generation_config,
        }

    except Exception as e:
        logger.error(f"ICP generation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "user_id": user_id,
            "workspace_id": workspace_id,
        }
