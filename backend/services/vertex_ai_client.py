"""
Vertex AI client with unified interface for all supported models
Gemini, Claude Sonnet, Claude Haiku, and Mistral OCR
"""

import json
import asyncio
from typing import Any, Dict, List, Optional, AsyncGenerator
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

# Vertex AI imports
try:
    from google import genai
    from google.genai import types
    from vertexai.generative_models import GenerativeModel
    from vertexai.preview.generative_models import GenerativeModel as PreviewGenerativeModel
except ImportError:
    genai = None
    types = None
    GenerativeModel = None
    PreviewGenerativeModel = None

# Claude via Vertex
try:
    from anthropic import AnthropicVertex
except ImportError:
    AnthropicVertex = None

# Mistral OCR
try:
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
except ImportError:
    MistralClient = None
    ChatMessage = None

from backend.core.config import get_settings
import structlog

logger = structlog.get_logger(__name__)


class VertexAIClient:
    """Unified Vertex AI client supporting multiple models"""

    def __init__(self):
        settings = get_settings()

        # GCP configuration
        self.project_id = settings.gcp_project_id
        self.location = settings.gcp_location or "us-central1"

        # Model configurations
        # NOTE: All Claude models are re-routed to Gemini as per configuration policy
        self.models = {
            "reasoning": settings.MODEL_REASONING or "gemini-2.0-flash-thinking-exp-01-21",
            "fast": settings.MODEL_FAST or "gemini-2.5-flash-002",
            "creative": "gemini-1.5-pro-002", # Re-routed from Claude Sonnet
            "creative_fast": "gemini-2.5-flash-002", # Re-routed from Claude Haiku
            "ocr": settings.MODEL_OCR or "mistral-ocr"
        }

        # Default settings
        self.default_temperature = settings.default_temperature or 0.7
        self.max_retries = settings.max_retries or 3

        # Initialize clients
        self.gemini_client = None
        self.anthropic_client = None
        self.mistral_client = None

        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize all AI clients"""
        try:
            if genai and self.project_id:
                self.gemini_client = genai.Client(
                    vertexai=True,
                    project=self.project_id,
                    location=self.location
                )
                logger.info("Initialized Gemini client")

            if AnthropicVertex and self.project_id:
                self.anthropic_client = AnthropicVertex(
                    region=self.location,
                    project_id=self.project_id
                )
                logger.info("Initialized Anthropic Vertex client")

            if MistralClient:
                # Initialize Mistral client (API key needed)
                self.mistral_client = MistralClient(api_key=getattr(get_settings(), 'MISTRAL_API_KEY', None))
                logger.info("Initialized Mistral client")

        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI clients: {e}")
            raise

    def _get_model_config(self, model_type: str) -> Dict[str, Any]:
        """Get model configuration for the specified type"""
        if model_type not in self.models:
            raise ValueError(f"Unknown model type: {model_type}")

        model_name = self.models[model_type]
        config = {"model": model_name, "type": model_type}

        # Model-specific configurations
        if "gemini" in model_name.lower():
            config.update({
                "client": "gemini",
                "max_output_tokens": 4096,
                "top_p": 0.8
            })
        elif "claude" in model_name.lower():
            config.update({
                "client": "anthropic",
                "max_tokens": 4096
            })
        elif "mistral" in model_name.lower():
            config.update({
                "client": "mistral",
                "max_tokens": 4096
            })

        return config

    @retry(
        retry=retry_if_exception_type((Exception,)),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(3),
        before_sleep=lambda retry_state: logger.warning(
            "Retrying Vertex AI call",
            attempt=retry_state.attempt_number,
            wait=retry_state.next_action.sleep
        )
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_type: str = "fast",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Unified chat completion across all supported models

        Args:
            messages: List of message dicts with 'role' and 'content'
            model_type: Type of model to use ("reasoning", "fast", "creative", "creative_fast", "ocr")
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_format: Optional response format (e.g., {"type": "json_object"})
            **kwargs: Additional model-specific parameters

        Returns:
            Generated response text
        """
        config = self._get_model_config(model_type)
        temperature = temperature or self.default_temperature

        logger.debug(
            "Making chat completion request",
            model_type=model_type,
            model=config["model"],
            message_count=len(messages)
        )

        # Route to appropriate client
        if config["client"] == "gemini":
            return await self._gemini_chat_completion(
                messages, config, temperature, max_tokens, response_format, **kwargs
            )
        elif config["client"] == "anthropic":
            return await self._anthropic_chat_completion(
                messages, config, temperature, max_tokens, response_format, **kwargs
            )
        elif config["client"] == "mistral":
            return await self._mistral_chat_completion(
                messages, config, temperature, max_tokens, response_format, **kwargs
            )
        else:
            raise ValueError(f"Unsupported client type: {config['client']}")

    async def _gemini_chat_completion(
        self,
        messages: List[Dict[str, str]],
        config: Dict[str, Any],
        temperature: float,
        max_tokens: Optional[int],
        response_format: Optional[Dict[str, Any]],
        **kwargs
    ) -> str:
        """Handle Gemini model chat completion"""
        if not self.gemini_client:
            raise RuntimeError("Gemini client not initialized")

        # Convert messages to Gemini format
        gemini_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            # Convert roles
            if role == "system":
                gemini_messages.append({"role": "user", "parts": [content]})
                gemini_messages.append({"role": "model", "parts": ["I understand the system context."]})
            else:
                gemini_role = "model" if role == "assistant" else "user"
                gemini_messages.append({"role": gemini_role, "parts": [content]})

        # Generation config
        generation_config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens or config.get("max_output_tokens"),
            top_p=config.get("top_p")
        )

        # Add JSON format if requested
        if response_format and response_format.get("type") == "json_object":
            generation_config.response_mime_type = "application/json"

        try:
            response = await self.gemini_client.aio.models.generate_content(
                model=config["model"],
                contents=gemini_messages,
                config=generation_config
            )

            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text
            else:
                raise RuntimeError("No content generated by Gemini")

        except Exception as e:
            logger.error(f"Gemini chat completion failed: {e}")
            raise

    async def _anthropic_chat_completion(
        self,
        messages: List[Dict[str, str]],
        config: Dict[str, Any],
        temperature: float,
        max_tokens: Optional[int],
        response_format: Optional[Dict[str, Any]],
        **kwargs
    ) -> str:
        """Handle Anthropic model chat completion"""
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized")

        # Convert messages to Anthropic format
        anthropic_messages = []
        system_message = None

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                system_message = content
            else:
                anthropic_role = "assistant" if role == "assistant" else "user"
                anthropic_messages.append({
                    "role": anthropic_role,
                    "content": content
                })

        try:
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model=config["model"],
                messages=anthropic_messages,
                system=system_message,
                temperature=temperature,
                max_tokens=max_tokens or config.get("max_tokens")
            )

            if response.content and response.content[0].type == "text":
                content = response.content[0].text
                logger.debug(
                    "Anthropic completion",
                    model=config["model"],
                    tokens_used=response.usage.input_tokens + response.usage.output_tokens
                )
                return content
            else:
                raise RuntimeError("No content generated by Anthropic")

        except Exception as e:
            logger.error(f"Anthropic chat completion failed: {e}")
            raise

    async def _mistral_chat_completion(
        self,
        messages: List[Dict[str, str]],
        config: Dict[str, Any],
        temperature: float,
        max_tokens: Optional[int],
        response_format: Optional[Dict[str, Any]],
        **kwargs
    ) -> str:
        """Handle Mistral model chat completion"""
        if not self.mistral_client:
            raise RuntimeError("Mistral client not initialized")

        # Convert messages to Mistral format
        mistral_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            mistral_messages.append(ChatMessage(role=role, content=content))

        try:
            response = await asyncio.to_thread(
                self.mistral_client.chat,
                messages=mistral_messages,
                model=config["model"],
                temperature=temperature,
                max_tokens=max_tokens or config.get("max_tokens")
            )

            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content
                logger.debug(
                    "Mistral completion",
                    model=config["model"],
                    tokens_used=getattr(response.usage, 'total_tokens', 0) if response.usage else 0
                )
                return content
            else:
                raise RuntimeError("No content generated by Mistral")

        except Exception as e:
            logger.error(f"Mistral chat completion failed: {e}")
            raise

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_type: str = "fast",
        **kwargs
    ) -> str:
        """
        Simple text generation helper

        Args:
            prompt: User prompt
            system_prompt: Optional system message
            model_type: Type of model to use
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return await self.chat_completion(messages, model_type=model_type, **kwargs)

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_type: str = "fast",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output

        Args:
            prompt: User prompt
            system_prompt: Optional system message
            model_type: Type of model to use
            **kwargs: Additional parameters

        Returns:
            Parsed JSON dict
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.chat_completion(
            messages,
            model_type=model_type,
            response_format={"type": "json_object"},
            **kwargs
        )

        return json.loads(response)

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model_type: str = "fast",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat completion (for real-time UI)

        Args:
            messages: List of message dicts
            model_type: Model type to use
            **kwargs: Additional parameters

        Yields:
            Content chunks as they arrive
        """
        # For now, implement as non-streaming and yield the full response
        # Real streaming implementation would depend on specific model capabilities
        response = await self.chat_completion(messages, model_type=model_type, **kwargs)
        yield response

    async def batch_completions(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        model_type: str = "fast",
        concurrency: int = 5,
        **kwargs
    ) -> List[str]:
        """
        Generate multiple completions concurrently

        Args:
            prompts: List of user prompts
            system_prompt: Optional system message for all
            model_type: Model type to use
            concurrency: Max concurrent requests
            **kwargs: Additional parameters

        Returns:
            List of generated texts
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def limited_generate(prompt: str) -> str:
            async with semaphore:
                return await self.generate_text(prompt, system_prompt, model_type=model_type, **kwargs)

        tasks = [limited_generate(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)

    async def ocr_image(self, image_url: str, model_type: str = "ocr") -> str:
        """
        Perform OCR on an image using Mistral OCR or Gemini Vision

        Args:
            image_url: URL of the image to process
            model_type: Model to use ("ocr" for Mistral, or "fast"/"reasoning" for Gemini Vision)

        Returns:
            Extracted text from the image
        """
        config = self._get_model_config(model_type)
        logger.info(f"Performing OCR using {config['model']} on {image_url}")

        try:
            if config["client"] == "mistral" and self.mistral_client:
                # Mistral OCR implementation
                # Note: Depending on SDK version, this might be client.ocr.process or similar
                # For now, we use the chat completion with image content if supported, 
                # or assume a specific ocr endpoint if available in the client.
                # Since Mistral OCR is new, we'll attempt a chat completion with image_url which is standard for vision models
                
                messages = [
                    ChatMessage(role="user", content=[
                        {"type": "text", "text": "Transcribe the text in this image exactly."},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ])
                ]
                
                response = await asyncio.to_thread(
                    self.mistral_client.chat,
                    model=config["model"],
                    messages=messages
                )
                
                if response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content
                
            elif config["client"] == "gemini" and self.gemini_client:
                # Gemini Vision implementation
                # Gemini supports images via parts
                # Note: We need to handle image loading/passing correctly for Gemini
                # This is a simplified placeholder for image URL handling
                
                # For Gemini via Vertex AI, we typically pass GCS URI or base64
                # Here we just pass text prompt for now as a placeholder if URL fetching isn't implemented
                
                prompt = f"Extract text from image at: {image_url}"
                return await self.generate_text(prompt, model_type=model_type)

            raise ValueError(f"OCR not supported for client: {config['client']}")

        except Exception as e:
            logger.error(f"OCR failed: {e}")
            raise


# Global singleton instance
vertex_ai_client = VertexAIClient()
