"""
AI21 Jamba Large 1.6 Client for RaptorFlow

Handles communication with AI21 Labs' Jamba Large 1.6 model via Google Cloud Vertex AI
Self-deploy endpoints. Uses rawPredict API with chat messages format.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Union
import aiohttp

from backend.core.config import get_settings
from backend.utils.logging_config import get_logger
from backend.core.request_context import get_current_workspace_id, get_current_user_id

logger = get_logger("jamba_client")


class JambaLargeClient:
    """
    Client for interacting with AI21 Jamba Large 1.6 via Vertex AI rawPredict endpoints.

    Jamba Large uses the AI21 Jamba API format within Vertex AI rawPredict:
    - Uses "rawPredict" endpoint
    - Standard chat message format with roles and content
    - Supports both streaming and non-streaming responses
    - 256K context window optimized for enterprise workloads
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
            "gcloud", "auth", "application-default", "print-access-token",
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
        Prepare messages in Jamba Large format.

        Jamba Large expects standard AI21 chat format:
        {
            "messages": [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ],
            "temperature": 0.7,
            "top_p": 1.0,
            "n": 1,
            "stop": "\n"
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
            "messages": formatted_messages,
            "temperature": self.config.default_temperature,
            "top_p": 1.0,
            "n": 1,
            "stop": "\n"
        }

    async def chat_completion(
        self,
        messages: List[Union[Dict[str, str], str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        Make a chat completion call to Jamba Large 1.6.

        Args:
            messages: List of message dicts or strings
            temperature: Override default temperature
            max_tokens: Override default max tokens (not used in current API)
            stream: Whether to use streaming response (not implemented yet)

        Returns:
            Model response text

        Raises:
            Exception: If API call fails
        """
        # Validate configuration
        if not self.config.jamba_large_endpoint_id:
            raise Exception("Jamba Large endpoint ID not configured")

        if not self.config.gcp_project_id:
            raise Exception("GCP project ID not configured for Jamba Large")

        # Prepare request
        request_data = self._prepare_messages(messages)

        # Override parameters if provided
        if temperature is not None:
            request_data["temperature"] = temperature
        if max_tokens is not None:
            # Jamba Large doesn't use max_tokens in the request, but we can use it for logging
            logger.info(f"Jamba Large max_tokens parameter ignored: {max_tokens}")

        # Get endpoint URL - use streamRawPredict for streaming, rawPredict for regular
        endpoint_url = self._get_endpoint_url(
            self.config.gcp_project_id,
            self.config.gcp_location,
            self.config.jamba_large_endpoint_id
        )

        if stream:
            endpoint_url = endpoint_url.replace(":rawPredict", ":streamRawPredict")

        try:
            # Get auth token
            auth_token = await self._get_auth_token()

            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }

            logger.info(
                "Making Jamba Large call",
                endpoint_url=endpoint_url,
                message_count=len(request_data["messages"]),
                stream=stream,
                workspace_id=get_current_workspace_id(),
                user_id=get_current_user_id()
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint_url,
                    headers=headers,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=600)  # 10 minute timeout for long context
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Jamba Large API error: {response.status}", error=error_text)
                        raise Exception(f"Jamba Large API error {response.status}: {error_text}")

                    if stream:
                        # Handle streaming response
                        response_text = ""
                        async for line in response.content:
                            try:
                                # Jamba streaming format is SSE-like
                                line_str = line.decode()
                                if line_str.startswith("data: "):
                                    event_data = json.loads(line_str[6:])
                                    if "content" in event_data:
                                        response_text += event_data["content"]
                                    # Check for stop condition
                                    finish_reason = event_data.get("finish_reason")
                                    if finish_reason in ["stop", "length", "error"]:
                                        break
                            except json.JSONDecodeError:
                                pass  # Skip invalid JSON lines
                        return response_text
                    else:
                        # Handle single response
                        result = await response.json()

                        # Extract content from Jamba response format
                        if "choices" in result and len(result["choices"]) > 0:
                            choice = result["choices"][0]
                            if "message" in choice and "content" in choice["message"]:
                                return choice["message"]["content"]
                            elif "text" in choice:
                                return choice["text"]

                        # Fallback for different response formats
                        logger.warning("Unexpected Jamba response format", response=result)
                        return str(result)

        except Exception as e:
            logger.error("Jamba Large call failed", error=str(e))
            raise

    async def health_check(self) -> bool:
        """
        Perform basic health check for Jamba Large.

        Returns True if configuration is valid, False otherwise.
        """
        try:
            # Check if required config is present
            if not self.config.jamba_large_endpoint_id or not self.config.gcp_project_id:
                logger.warning("Jamba Large configuration incomplete")
                return False

            # Try to get auth token (basic gcloud check)
            await self._get_auth_token()
            return True

        except Exception as e:
            logger.warning(f"Jamba Large health check failed: {e}")
            return False


# Global instance
jamba_client = JambaLargeClient()

# Convenience function for backward compatibility
async def chat_completion(*args, **kwargs) -> str:
    """Convenience function for chat completions."""
    return await jamba_client.chat_completion(*args, **kwargs)
