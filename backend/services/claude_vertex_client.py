"""
Claude Vertex AI Client for RaptorFlow

Handles communication with Anthropic's Claude models (Haiku 4.5, Sonnet 4.5)
via Google Cloud Vertex AI. Uses standard Vertex AI API calls.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Union
import aiohttp

from backend.core.config import get_settings
from backend.utils.logging_config import get_logger
from backend.core.request_context import get_current_workspace_id, get_current_user_id

logger = get_logger("claude_vertex_client")


class ClaudeVertexClient:
    """
    Client for interacting with Claude models via Vertex AI.

    Supports Claude Haiku 4.5 and Claude Sonnet 4.5 with full compatibility:
    - Haiku 4.5: Fast, cost-effective, near-frontier performance
    - Sonnet 4.5: Best for coding, agents, computer use
    - 200K context window standard (1M beta for Sonnet)
    - Extended thinking and enhanced tool orchestration
    """

    def __init__(self):
        self.config = get_settings()

    def _get_base_url(self) -> str:
        """Get the Vertex AI Claude endpoint URL (global region)."""
        return "https://claude-ai.googleapis.com/v1"

    def _get_endpoint_url(self, project_id: str, model_name: str) -> str:
        """Construct the full Claude Vertex AI endpoint URL with model."""
        base = self._get_base_url()
        return f"{base}/projects/{project_id}/locations/global/publishers/anthropic/models/{model_name}"

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

    def _prepare_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Prepare messages in Claude Vertex format.

        Claude Vertex expects the standard Anthropic messages format:
        [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
        """
        # Validate and normalize input messages
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                # Support multimodal content (images, PDF, text)
                content = msg["content"]
                if isinstance(content, str):
                    formatted_messages.append({
                        "role": msg["role"],
                        "content": content
                    })
                elif isinstance(content, list):
                    # Multimodal content
                    formatted_messages.append({
                        "role": msg["role"],
                        "content": content
                    })
                else:
                    # Handle non-dict content
                    formatted_messages.append({
                        "role": msg["role"],
                        "content": str(content)
                    })
            elif isinstance(msg, str):
                # Plain string becomes user message
                formatted_messages.append({
                    "role": "user",
                    "content": msg
                })

        return formatted_messages

    async def chat_completion(
        self,
        messages: List[Union[Dict[str, str], str]],
        model_name: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        thinking: Optional[str] = None  # "low" or "high" for Claude 3.5+ models
    ) -> str:
        """
        Make a chat completion call to Claude via Vertex AI.

        Args:
            messages: List of message dicts or strings
            model_name: Claude model name (e.g., "claude-haiku-4-5@20251001")
            temperature: Override default temperature
            max_tokens: Override default max tokens (up to 64K output)
            stream: Whether to use streaming response
            thinking: "low" or "high" for Claude 3.5+ thinking mode

        Returns:
            Model response text

        Raises:
            Exception: If API call fails
        """
        # Validate configuration
        if not self.config.gcp_project_id:
            raise Exception("GCP project ID not configured for Claude Vertex")

        # Prepare request
        formatted_messages = self._prepare_messages(messages)

        request_data = {
            "anthropic_version": "vertex-2023-10-16",
            "messages": formatted_messages,
            "max_tokens": max_tokens or self.config.default_max_tokens,
            "stream": stream
        }

        # Add temperature if provided
        if temperature is not None:
            request_data["temperature"] = temperature

        # Add thinking level for Claude 3.5+ models (Sonnet 4.5, Haiku 4.5)
        if thinking and model_name.startswith(("claude-sonnet-4-5", "claude-haiku-4-5")):
            budget_tokens = 16000 if thinking == "high" else (1024 if thinking == "low" else 1024)
            request_data["thinking"] = {"type": "enabled", "budget_tokens": budget_tokens}

        # Get endpoint URL
        endpoint_url = self._get_endpoint_url(self.config.gcp_project_id, model_name)

        try:
            # Get auth token
            auth_token = await self._get_auth_token()

            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }

            logger.info(
                "Making Claude Vertex call",
                endpoint_url=endpoint_url,
                model=model_name,
                message_count=len(formatted_messages),
                stream=stream,
                thinking=thinking,
                workspace_id=get_current_workspace_id(),
                user_id=get_current_user_id()
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint_url,
                    headers=headers,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=600)  # 10 minute timeout for complex reasoning
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Claude Vertex API error: {response.status}", error=error_text)
                        raise Exception(f"Claude Vertex API error {response.status}: {error_text}")

                    if stream:
                        # Handle streaming response
                        response_text = ""
                        async for line in response.content:
                            try:
                                line_str = line.decode()
                                if line_str.startswith("data: "):
                                    # Claude streaming format
                                    if line_str.strip() == "data: [DONE]":
                                        break
                                    event_data = json.loads(line_str[6:])
                                    if "delta" in event_data and "text" in event_data["delta"]:
                                        response_text += event_data["delta"]["text"]
                            except json.JSONDecodeError:
                                pass  # Skip invalid JSON lines
                        return response_text
                    else:
                        # Handle single response
                        result = await response.json()

                        # Extract content from Claude response format
                        if "content" in result and len(result["content"]) > 0:
                            content_block = result["content"][0]
                            if "text" in content_block:
                                return content_block["text"]
                            else:
                                return content_block.get("text", "")
                        else:
                            return str(result)

        except Exception as e:
            logger.error("Claude Vertex call failed", error=str(e), model=model_name)
            raise

    async def health_check(self) -> bool:
        """
        Perform basic health check for Claude Vertex client.

        Returns True if configuration is valid, False otherwise.
        """
        try:
            # Check if GCP project is configured
            if not self.config.gcp_project_id:
                logger.warning("GCP project ID not configured for Claude Vertex")
                return False

            # Try to get auth token
            await self._get_auth_token()
            return True

        except Exception as e:
            logger.warning(f"Claude Vertex health check failed: {e}")
            return False

    # Convenience methods for specific models
    async def haiku_45_completion(self, messages: List[Union[Dict[str, str], str]], **kwargs) -> str:
        """Convenience method for Claude Haiku 4.5."""
        return await self.chat_completion(
            messages=messages,
            model_name=self.config.claude_haiku_45_model,
            **kwargs
        )

    async def sonnet_45_completion(self, messages: List[Union[Dict[str, str], str]], **kwargs) -> str:
        """Convenience method for Claude Sonnet 4.5."""
        return await self.chat_completion(
            messages=messages,
            model_name=self.config.claude_sonnet_45_model,
            **kwargs
        )


# Global instance
claude_vertex_client = ClaudeVertexClient()

# Convenience functions for backward compatibility
async def haiku_45_completion(*args, **kwargs) -> str:
    """Convenience function for Claude Haiku 4.5 completions."""
    return await claude_vertex_client.haiku_45_completion(*args, **kwargs)

async def sonnet_45_completion(*args, **kwargs) -> str:
    """Convenience function for Claude Sonnet 4.5 completions."""
    return await claude_vertex_client.sonnet_45_completion(*args, **kwargs)
