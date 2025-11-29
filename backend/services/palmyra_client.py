"""
Palmyra X4 Client for RaptorFlow

Handles communication with WRITER's Palmyra X4 model via Google Cloud Vertex AI
Self-deploy endpoints. Uses rawPredict API with different message format than
standard Gemini models.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Union
import aiohttp

from backend.core.config import get_settings
from backend.utils.logging_config import get_logger
from backend.core.request_context import get_current_workspace_id, get_current_user_id

logger = get_logger("palmyra_client")


class PalmyraX4Client:
    """
    Client for interacting with Palmyra X4 via Vertex AI rawPredict endpoints.

    Palmyra X4 uses a different message format than standard Gemini models:
    - Uses "rawPredict" instead of "streamGenerateContent"
    - Request format: {"model": "palmyra-x4", "instances": [{ "messages": [...] }], "parameters": {...}}
    - Supports both streaming and non-streaming responses
    """

    def __init__(self):
        self.config = get_settings()

    def _get_base_url(self, region: str = "us-central1") -> str:
        """Get the base Vertex AI endpoint URL."""
        return f"https://{region}-aiplatform.googleapis.com/v1"

    def _get_endpoint_url(self, project_id: str, region: str, endpoint_id: str) -> str:
        """Construct the full rawPredict endpoint URL."""
        base = self._get_base_url(region)
        return f"{base}/projects/{project_id}/locations/{region}/endpoints/{endpoint_id}:rawPredict"

    async def _get_auth_token(self) -> str:
        """Get authentication token for Vertex AI calls."""
        # Use gcloud auth for now - in production, this should use service account keys
        process = await asyncio.create_subprocess_exec(
            "gcloud", "auth", "print-access-token",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            logger.error("Failed to get auth token", error=error_msg)
            raise Exception(f"gcloud auth failed: {error_msg}")

        return stdout.decode().strip()

    def _prepare_messages(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Prepare messages in Palmyra X4 format.

        Palmyra X4 expects:
        {
            "model": "palmyra-x4",
            "instances": [{
                "messages": [
                    {"role": "user", "content": "..."},
                    {"role": "assistant", "content": "..."}
                ]
            }],
            "parameters": {
                "max_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        """
        # Validate and normalize input messages
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                formatted_messages.append({
                    "role": role,
                    "content": content
                })
            elif isinstance(msg, str):
                # Plain string becomes user message
                formatted_messages.append({
                    "role": "user",
                    "content": msg
                })

        return {
            "origin": "vertex-model-garden",
            "model": self.config.palmyra_x4_model,
            "instances": [{
                "messages": formatted_messages
            }],
            "parameters": {
                "max_tokens": self.config.default_max_tokens,
                "temperature": self.config.default_temperature,
                "top_p": 0.9
            }
        }

    async def chat_completion(
        self,
        messages: List[Union[Dict[str, str], str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        Make a chat completion call to Palmyra X4.

        Args:
            messages: List of message dicts or strings
            temperature: Override default temperature
            max_tokens: Override default max tokens
            stream: Whether to use streaming response

        Returns:
            Model response text

        Raises:
            Exception: If API call fails
        """
        # Validate configuration
        if not self.config.palmyra_x4_endpoint_id:
            raise Exception("Palmyra X4 endpoint ID not configured")

        if not self.config.gcp_project_id:
            raise Exception("GCP project ID not configured for Palmyra X4")

        # Prepare request
        request_data = self._prepare_messages(messages)

        # Override parameters if provided
        if temperature is not None:
            request_data["parameters"]["temperature"] = temperature
        if max_tokens is not None:
            request_data["parameters"]["max_tokens"] = max_tokens

        # Get endpoint URL
        endpoint_url = self._get_endpoint_url(
            self.config.gcp_project_id,
            self.config.gcp_location,
            self.config.palmyra_x4_endpoint_id
        )

        # Use streaming or non-streaming
        if stream:
            endpoint_url = endpoint_url.replace(":rawPredict", ":streamRawPredict")
            request_data["Accept"] = "text/event-stream"

        try:
            # Get auth token
            auth_token = await self._get_auth_token()

            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }

            logger.info(
                "Making Palmyra X4 call",
                endpoint_url=endpoint_url,
                message_count=len(request_data["instances"][0]["messages"]),
                stream=stream,
                workspace_id=get_current_workspace_id(),
                user_id=get_current_user_id()
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint_url,
                    headers=headers,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Palmyra X4 API error: {response.status}", error=error_text)
                        raise Exception(f"Palmyra X4 API error {response.status}: {error_text}")

                    if stream:
                        # Handle streaming response
                        response_text = ""
                        async for line in response.content:
                            if line.startswith(b"data: "):
                                try:
                                    event = json.loads(line[6:].decode())
                                    if "text" in event:
                                        response_text += event["text"]
                                except json.JSONDecodeError:
                                    pass  # Skip invalid JSON lines
                        return response_text
                    else:
                        # Handle single response
                        result = await response.json()
                        # Extract text from response (adjust based on actual Palmyra format)
                        if "predictions" in result and len(result["predictions"]) > 0:
                            return result["predictions"][0].get("text", "")
                        else:
                            # Fallback for different response formats
                            return str(result)

        except Exception as e:
            logger.error("Palmyra X4 call failed", error=str(e))
            raise

    async def health_check(self) -> bool:
        """
        Perform basic health check for Palmyra X4.

        Returns True if configuration is valid, False otherwise.
        """
        try:
            # Check if required config is present
            if not self.config.palmyra_x4_endpoint_id or not self.config.gcp_project_id:
                logger.warning("Palmyra X4 configuration incomplete")
                return False

            # Try to get auth token (basic gcloud check)
            await self._get_auth_token()
            return True

        except Exception as e:
            logger.warning(f"Palmyra X4 health check failed: {e}")
            return False


# Global instance
palmyra_client = PalmyraX4Client()

# Convenience function for backward compatibility
async def chat_completion(*args, **kwargs) -> str:
    """Convenience function for chat completions."""
    return await palmyra_client.chat_completion(*args, **kwargs)
