"""
Vertex AI Client - Unified interface for Gemini and Claude models via Vertex AI.
Supports: Gemini 2.0 Flash, Gemini 2.5 Flash, Claude Sonnet 4.5, Claude Haiku 4.5, Mistral OCR
"""

import structlog
from typing import List, Dict, Any, Optional, Literal
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type

from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Content, Part
from anthropic import AnthropicVertex

from backend.config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class VertexAIClient:
    """
    Unified client for Vertex AI models.
    
    Model Selection Strategy:
    - Reasoning (complex tasks): Gemini 2.0 Flash Thinking
    - Fast (simple tasks): Gemini 2.5 Flash  
    - Creative (content generation): Claude Sonnet 4.5
    - Creative Fast (quick content): Claude Haiku 4.5
    - OCR (document processing): Mistral OCR
    """
    
    def __init__(self):
        # Initialize Vertex AI
        aiplatform.init(
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_LOCATION
        )
        
        # Initialize Anthropic for Claude models via Vertex
        self.anthropic_client = AnthropicVertex(
            region=settings.GOOGLE_CLOUD_LOCATION,
            project_id=settings.GOOGLE_CLOUD_PROJECT
        )
        
        # Model mapping
        self.models = {
            "reasoning": settings.MODEL_REASONING,
            "fast": settings.MODEL_FAST,
            "creative": settings.MODEL_CREATIVE,
            "creative_fast": settings.MODEL_CREATIVE_FAST,
            "ocr": settings.MODEL_OCR
        }
        
        logger.info("Vertex AI Client initialized", project=settings.GOOGLE_CLOUD_PROJECT)
    
    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(Exception)
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_type: Literal["reasoning", "fast", "creative", "creative_fast", "ocr"] = "fast",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None,
        **kwargs
    ) -> str:
        """
        Unified chat completion interface.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model_type: Which model to use
            temperature: Generation temperature
            max_tokens: Max output tokens
            response_format: Optional format (e.g., {"type": "json_object"})
            
        Returns:
            Generated text response
        """
        model_name = self.models.get(model_type, self.models["fast"])
        temp = temperature if temperature is not None else settings.DEFAULT_TEMPERATURE
        
        try:
            # Route to appropriate model family
            if "claude" in model_name or "sonnet" in model_name or "haiku" in model_name:
                return await self._call_claude(messages, model_name, temp, max_tokens, response_format)
            else:
                return await self._call_gemini(messages, model_name, temp, max_tokens, response_format)
                
        except Exception as e:
            logger.error(f"Chat completion failed: {e}", model=model_name)
            raise
    
    async def _call_gemini(
        self,
        messages: List[Dict[str, str]],
        model_name: str,
        temperature: float,
        max_tokens: Optional[int],
        response_format: Optional[Dict]
    ) -> str:
        """Calls Gemini models via Vertex AI."""
        try:
            # Initialize Gemini model
            model = GenerativeModel(model_name)
            
            # Convert messages to Gemini format
            gemini_messages = self._convert_to_gemini_format(messages)
            
            # Generation config
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens or 8192,
            }
            
            # Add JSON mode if requested
            if response_format and response_format.get("type") == "json_object":
                generation_config["response_mime_type"] = "application/json"
            
            # Generate
            response = await model.generate_content_async(
                gemini_messages,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini call failed: {e}")
            raise
    
    async def _call_claude(
        self,
        messages: List[Dict[str, str]],
        model_name: str,
        temperature: float,
        max_tokens: Optional[int],
        response_format: Optional[Dict]
    ) -> str:
        """Calls Claude models via Anthropic Vertex SDK."""
        try:
            # Separate system message from conversation
            system_message = ""
            conversation_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    conversation_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add JSON instruction if needed
            if response_format and response_format.get("type") == "json_object":
                system_message += "\n\nYou must respond with valid JSON only. No other text."
            
            # Call Claude via Anthropic Vertex
            response = await self.anthropic_client.messages.create(
                model=model_name,
                max_tokens=max_tokens or 4096,
                temperature=temperature,
                system=system_message if system_message else None,
                messages=conversation_messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Claude call failed: {e}")
            raise
    
    def _convert_to_gemini_format(self, messages: List[Dict[str, str]]) -> List[Content]:
        """Converts OpenAI-style messages to Gemini Content format."""
        gemini_contents = []
        
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            content = Content(
                role=role,
                parts=[Part.from_text(msg["content"])]
            )
            gemini_contents.append(content)
        
        return gemini_contents
    
    async def process_ocr(
        self,
        image_data: bytes,
        prompt: str = "Extract all text from this image accurately."
    ) -> str:
        """
        Processes OCR using Mistral OCR model.
        
        Args:
            image_data: Image bytes
            prompt: OCR instruction
            
        Returns:
            Extracted text
        """
        try:
            # Use Mistral OCR model via Vertex
            model = GenerativeModel(self.models["ocr"])
            
            # Create image part
            image_part = Part.from_data(image_data, mime_type="image/jpeg")
            text_part = Part.from_text(prompt)
            
            response = await model.generate_content_async([image_part, text_part])
            
            return response.text
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-004"  # Google's embedding model
    ) -> List[List[float]]:
        """
        Generates embeddings using Google's embedding model.
        
        Args:
            texts: List of texts to embed
            model: Embedding model name
            
        Returns:
            List of embedding vectors
        """
        try:
            from vertexai.language_models import TextEmbeddingModel
            
            embedding_model = TextEmbeddingModel.from_pretrained(model)
            embeddings = await embedding_model.get_embeddings_async(texts)
            
            return [emb.values for emb in embeddings]
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise


# Global instance
vertex_ai_client = VertexAIClient()

