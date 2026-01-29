"""
RaptorFlow LLM Service
Phase 1.2.1: LLM Integration Layer

Handles integration with Large Language Models for fact extraction, analysis,
and content generation. Supports OpenAI GPT-4 and Google Vertex AI.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

import openai
from openai import AsyncOpenAI
from google.cloud import aiplatform
from google.cloud.aiplatform import Gapic
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import tiktoken

from fastapi import HTTPException
from pydantic import BaseModel

from .config import get_settings
from .core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class LLMProvider(str, Enum):
    """Available LLM providers."""

    OPENAI = "openai"
    GOOGLE_VERTEX = "google_vertex"
    AUTO = "auto"  # Automatically choose best provider


class ModelType(str, Enum):
    """Available model types."""

    GPT4_TURBO = "gpt-4-turbo"
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"


@dataclass
class LLMRequest:
    """LLM request configuration."""

    prompt: str
    model: ModelType
    temperature: float = 0.1
    max_tokens: int = 2000
    provider: Optional[LLMProvider] = None
    system_prompt: Optional[str] = None
    context: Optional[Dict] = None


@dataclass
class LLMResponse:
    """LLM response result."""

    content: str
    model_used: str
    provider_used: str
    tokens_used: int
    cost: float
    processing_time: float
    finish_reason: str
    created_at: datetime


@dataclass
class TokenUsage:
    """Token usage information."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class ExtractionContext:
    """Context for fact extraction."""

    document_type: Optional[str] = None
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    industry: Optional[str] = None
    business_context: Optional[Dict] = None


class PromptManager:
    """Prompt template management for LLM interactions."""

    def __init__(self):
        self.templates = {
            "fact_extraction": self._get_fact_extraction_template(),
            "contradiction_detection": self._get_contradiction_template(),
            "icp_generation": self._get_icp_generation_template(),
            "market_analysis": self._get_market_analysis_template(),
            "competitive_intelligence": self._get_competitive_template(),
        }

    async def get_prompt(self, template_name: str, context: ExtractionContext) -> str:
        """
        Get formatted prompt template.

        Args:
            template_name: Name of the template
            context: Context for formatting

        Returns:
            Formatted prompt string
        """
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")

        template = self.templates[template_name]

        # Format template with context
        formatted_prompt = template.format(
            document_type=context.document_type or "Unknown",
            industry=context.industry or "General",
            workspace_id=context.workspace_id or "",
            business_context=json.dumps(context.business_context or {}, indent=2),
        )

        return formatted_prompt

    def _get_fact_extraction_template(self) -> str:
        """Template for fact extraction."""
        return """
        You are an expert business analyst tasked with extracting key facts from business documents.

        Document Type: {document_type}
        Industry: {industry}

        Business Context:
        {business_context}

        Please extract the following types of facts from the provided document:
        1. Business Metrics (revenue, growth rates, market share, etc.)
        2. Strategic Information (goals, objectives, initiatives, etc.)
        3. Operational Details (processes, systems, teams, etc.)
        4. Market Information (customers, competitors, trends, etc.)
        5. Financial Information (investments, costs, profitability, etc.)

        For each fact extracted, provide:
        - The fact statement
        - Confidence score (0-1)
        - Source context
        - Category (one of the 5 categories above)

        Format your response as JSON:
        {{
            "facts": [
                {{
                    "statement": "fact statement",
                    "confidence": 0.9,
                    "source": "relevant text from document",
                    "category": "business_metrics"
                }}
            ]
        }}

        Document content:
        {content}
        """

    def _get_contradiction_template(self) -> str:
        """Template for contradiction detection."""
        return """
        You are an expert analyst specializing in identifying logical contradictions in business information.

        Document Type: {document_type}
        Industry: {industry}

        Analyze the following facts and identify any contradictions:

        Facts:
        {facts}

        Look for:
        1. Numerical inconsistencies
        2. Logical impossibilities
        3. Timeline conflicts
        4. Causal impossibilities
        5. Strategic misalignments

        For each contradiction found, provide:
        - Description of the contradiction
        - Severity score (0-1)
        - Conflicting facts involved
        - Suggested resolution

        Format your response as JSON:
        {{
            "contradictions": [
                {{
                    "description": "description of contradiction",
                    "severity": 0.8,
                    "conflicting_facts": ["fact1", "fact2"],
                    "resolution": "suggested resolution"
                }}
            ]
        }}
        """

    def _get_icp_generation_template(self) -> str:
        """Template for ICP generation."""
        return """
        You are an expert marketing strategist specializing in Ideal Customer Profile (ICP) creation.

        Industry: {industry}
        Business Context:
        {business_context}

        Based on the provided business information, generate detailed ICP profiles.

        For each ICP, include:
        1. Demographics (age, income, education, location)
        2. Psychographics (values, interests, lifestyle)
        3. Behavioral patterns (buying habits, decision process)
        4. Pain points and challenges
        5. Goals and aspirations
        6. Communication preferences
        7. Fit score (0-1)

        Generate 3-5 distinct ICP profiles.

        Format your response as JSON:
        {{
            "icp_profiles": [
                {{
                    "name": "ICP Name",
                    "demographics": {{...}},
                    "psychographics": {{...}},
                    "behaviors": {{...}},
                    "pain_points": [...],
                    "goals": [...],
                    "communication": {{...}},
                    "fit_score": 0.85
                }}
            ]
        }}
        """

    def _get_market_analysis_template(self) -> str:
        """Template for market analysis."""
        return """
        You are an expert market analyst with deep expertise in competitive intelligence and market dynamics.

        Industry: {industry}
        Business Context:
        {business_context}

        Analyze the market position and provide insights on:
        1. Market size and growth potential
        2. Competitive landscape
        3. Market trends and opportunities
        4. Threats and challenges
        5. Strategic recommendations

        Format your response as JSON:
        {{
            "market_analysis": {{
                "market_size": {{...}},
                "competitors": [...],
                "trends": [...],
                "opportunities": [...],
                "threats": [...],
                "recommendations": [...]
            }}
        }}
        """

    def _get_competitive_template(self) -> str:
        """Template for competitive intelligence."""
        return """
        You are an expert competitive intelligence analyst.

        Industry: {industry}
        Business Context:
        {business_context}

        Analyze competitive positioning and provide:
        1. Key competitors identification
        2. Competitive strengths and weaknesses
        3. Market positioning analysis
        4. Differentiation opportunities
        5. Strategic recommendations

        Format your response as JSON:
        {{
            "competitive_analysis": {{
                "competitors": [...],
                "positioning": {{...}},
                "opportunities": [...],
                "recommendations": [...]
            }}
        }}
        """


class CostTracker:
    """LLM usage cost tracking."""

    def __init__(self):
        self.pricing = {
            LLMProvider.OPENAI: {
                ModelType.GPT4: {"input": 0.03, "output": 0.06},  # per 1K tokens
                ModelType.GPT4_TURBO: {"input": 0.01, "output": 0.03},
                ModelType.GPT35_TURBO: {"input": 0.0015, "output": 0.002},
            },
            LLMProvider.GOOGLE_VERTEX: {
                ModelType.GEMINI_PRO: {
                    "input": 0.0005,
                    "output": 0.0015,
                },  # per 1K tokens
                ModelType.GEMINI_PRO_VISION: {"input": 0.0025, "output": 0.0075},
            },
        }

    async def track_usage(
        self, usage: TokenUsage, model: ModelType, provider: LLMProvider
    ) -> float:
        """
        Track usage and calculate cost.

        Args:
            usage: Token usage information
            model: Model used
            provider: Provider used

        Returns:
            Total cost in USD
        """
        if provider not in self.pricing or model not in self.pricing[provider]:
            logger.warning(f"No pricing available for {provider}/{model}")
            return 0.0

        pricing = self.pricing[provider][model]
        input_cost = (usage.prompt_tokens / 1000) * pricing["input"]
        output_cost = (usage.completion_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost

        # Log usage for billing
        await self._log_usage(usage, model, provider, total_cost)

        return total_cost

    async def _log_usage(
        self, usage: TokenUsage, model: ModelType, provider: LLMProvider, cost: float
    ):
        """Log usage for billing and analytics."""
        # Implementation would log to database or analytics service
        logger.info(
            f"LLM Usage - Provider: {provider}, Model: {model}, "
            f"Tokens: {usage.total_tokens}, Cost: ${cost:.6f}"
        )


class OpenAIProvider:
    """OpenAI LLM provider implementation."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY, organization=settings.OPENAI_ORG_ID
        )
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI."""
        start_time = time.time()

        try:
            # Prepare messages
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.prompt})

            # Make API call
            response = await self.client.chat.completions.create(
                model=request.model.value,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            # Calculate processing time
            processing_time = time.time() - start_time

            # Extract response data
            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            )

            # Calculate cost
            cost_tracker = CostTracker()
            cost = await cost_tracker.track_usage(
                usage, request.model, LLMProvider.OPENAI
            )

            return LLMResponse(
                content=content,
                model_used=request.model.value,
                provider_used=LLMProvider.OPENAI.value,
                tokens_used=usage.total_tokens,
                cost=cost,
                processing_time=processing_time,
                finish_reason=finish_reason,
                created_at=datetime.utcnow(),
            )

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"OpenAI provider error: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to generate response with OpenAI"
            )

    def count_tokens(self, text: str) -> int:
        """Count tokens for text."""
        return len(self.tokenizer.encode(text))


class GoogleVertexProvider:
    """Google Vertex AI provider implementation."""

    def __init__(self):
        self.project_id = settings.GCP_PROJECT_ID
        self.location = settings.GCP_LOCATION or "us-central1"
        self.client = None

    async def _get_client(self):
        """Initialize Vertex AI client."""
        if self.client is None:
            self.client = aiplatform.gapic.PredictionServiceClient(
                client_options={
                    "api_endpoint": f"{self.location}-aiplatform.googleapis.com"
                }
            )
        return self.client

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Google Vertex AI."""
        start_time = time.time()

        try:
            client = await self._get_client()

            # Prepare request
            endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{request.model.value}"

            # Construct prompt
            instances = [
                {
                    "content": request.prompt,
                    "system_instruction": (
                        request.system_prompt if request.system_prompt else None
                    ),
                }
            ]

            parameters = {
                "temperature": request.temperature,
                "max_output_tokens": request.max_tokens,
                "candidate_count": 1,
            }

            # Make API call
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.predict(
                    endpoint=endpoint, instances=instances, parameters=parameters
                ),
            )

            # Calculate processing time
            processing_time = time.time() - start_time

            # Extract response
            prediction = response.predictions[0]
            content = prediction.get("content", "")
            finish_reason = prediction.get("safety_ratings", [{}])[0].get(
                "blocked", False
            )

            # Token usage (Vertex AI provides different format)
            usage_metadata = prediction.get("usage_metadata", {})
            usage = TokenUsage(
                prompt_tokens=usage_metadata.get("prompt_token_count", 0),
                completion_tokens=usage_metadata.get("candidates_token_count", 0),
                total_tokens=usage_metadata.get("total_token_count", 0),
            )

            # Calculate cost
            cost_tracker = CostTracker()
            cost = await cost_tracker.track_usage(
                usage, request.model, LLMProvider.GOOGLE_VERTEX
            )

            return LLMResponse(
                content=content,
                model_used=request.model.value,
                provider_used=LLMProvider.GOOGLE_VERTEX.value,
                tokens_used=usage.total_tokens,
                cost=cost,
                processing_time=processing_time,
                finish_reason=str(finish_reason),
                created_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Google Vertex AI error: {e}")
            raise HTTPException(
                status_code=500, detail=f"Google Vertex AI error: {str(e)}"
            )

    def count_tokens(self, text: str) -> int:
        """Count tokens for text (simplified)."""
        # Vertex AI uses different tokenization
        # This is a simplified approximation
        return len(text.split()) * 1.3  # Rough estimate


class LLMService:
    """Main LLM service orchestrating multiple providers."""

    def __init__(self):
        self.openai_provider = OpenAIProvider()
        self.vertex_provider = GoogleVertexProvider()
        self.prompt_manager = PromptManager()
        self.cost_tracker = CostTracker()
        self.default_provider = settings.LLM_PROVIDER or LLMProvider.AUTO

    async def extract_facts(self, content: str, context: ExtractionContext) -> Dict:
        """
        Extract facts from content using LLM.

        Args:
            content: Document content
            context: Extraction context

        Returns:
            Extracted facts as structured data
        """
        # Get prompt template
        prompt = await self.prompt_manager.get_prompt("fact_extraction", context)

        # Format prompt with content
        formatted_prompt = prompt.format(
            content=content[:8000]
        )  # Limit for token count

        # Create LLM request
        request = LLMRequest(
            prompt=formatted_prompt,
            model=ModelType.GPT4_TURBO,
            temperature=0.1,
            max_tokens=2000,
            provider=await self._choose_provider(),
        )

        # Generate response
        response = await self.generate_response(request)

        # Parse JSON response
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse fact extraction response: {e}")
            return {"facts": []}

    async def detect_contradictions(self, facts: List[Dict]) -> Dict:
        """
        Detect contradictions in facts using LLM.

        Args:
            facts: List of extracted facts

        Returns:
            Contradiction analysis as structured data
        """
        # Format facts for prompt
        facts_text = json.dumps(facts, indent=2)

        # Get prompt template
        context = ExtractionContext()
        prompt = await self.prompt_manager.get_prompt(
            "contradiction_detection", context
        )

        # Format prompt
        formatted_prompt = prompt.format(facts=facts_text)

        # Create LLM request
        request = LLMRequest(
            prompt=formatted_prompt,
            model=ModelType.GPT4_TURBO,
            temperature=0.1,
            max_tokens=2000,
            provider=await self._choose_provider(),
        )

        # Generate response
        response = await self.generate_response(request)

        # Parse JSON response
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse contradiction detection response: {e}")
            return {"contradictions": []}

    async def generate_icp_profiles(self, business_data: Dict) -> Dict:
        """
        Generate ICP profiles using LLM.

        Args:
            business_data: Business information

        Returns:
            Generated ICP profiles as structured data
        """
        # Create context
        context = ExtractionContext(
            industry=business_data.get("industry"), business_context=business_data
        )

        # Get prompt template
        prompt = await self.prompt_manager.get_prompt("icp_generation", context)

        # Format prompt with business data
        business_text = json.dumps(business_data, indent=2)
        formatted_prompt = prompt.format(business_context=business_text)

        # Create LLM request
        request = LLMRequest(
            prompt=formatted_prompt,
            model=ModelType.GPT4_TURBO,
            temperature=0.3,  # Higher temperature for creativity
            max_tokens=3000,
            provider=await self._choose_provider(),
        )

        # Generate response
        response = await self.generate_response(request)

        # Parse JSON response
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ICP generation response: {e}")
            return {"icp_profiles": []}

    async def generate_market_analysis(self, business_data: Dict) -> Dict:
        """
        Generate market analysis using LLM.

        Args:
            business_data: Business information

        Returns:
            Market analysis as structured data
        """
        # Create context
        context = ExtractionContext(
            industry=business_data.get("industry"), business_context=business_data
        )

        # Get prompt template
        prompt = await self.prompt_manager.get_prompt("market_analysis", context)

        # Format prompt with business data
        business_text = json.dumps(business_data, indent=2)
        formatted_prompt = prompt.format(business_context=business_text)

        # Create LLM request
        request = LLMRequest(
            prompt=formatted_prompt,
            model=ModelType.GPT4_TURBO,
            temperature=0.2,
            max_tokens=2500,
            provider=await self._choose_provider(),
        )

        # Generate response
        response = await self.generate_response(request)

        # Parse JSON response
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse market analysis response: {e}")
            return {"market_analysis": {}}

    async def generate_competitive_intelligence(self, business_data: Dict) -> Dict:
        """
        Generate competitive intelligence using LLM.

        Args:
            business_data: Business information

        Returns:
            Competitive intelligence as structured data
        """
        # Create context
        context = ExtractionContext(
            industry=business_data.get("industry"), business_context=business_data
        )

        # Get prompt template
        prompt = await self.prompt_manager.get_prompt(
            "competitive_intelligence", context
        )

        # Format prompt with business data
        business_text = json.dumps(business_data, indent=2)
        formatted_prompt = prompt.format(business_context=business_text)

        # Create LLM request
        request = LLMRequest(
            prompt=formatted_prompt,
            model=ModelType.GPT4_TURBO,
            temperature=0.2,
            max_tokens=2500,
            provider=await self._choose_provider(),
        )

        # Generate response
        response = await self.generate_response(request)

        # Parse JSON response
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse competitive intelligence response: {e}")
            return {"competitive_analysis": {}}

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """
        Generate response using appropriate provider.

        Args:
            request: LLM request configuration

        Returns:
            LLM response
        """
        provider = request.provider or await self._choose_provider()

        if provider == LLMProvider.OPENAI:
            return await self.openai_provider.generate_response(request)
        elif provider == LLMProvider.GOOGLE_VERTEX:
            return await self.vertex_provider.generate_response(request)
        else:
            # Default to OpenAI
            return await self.openai_provider.generate_response(request)

    async def _choose_provider(self) -> LLMProvider:
        """Choose the best provider based on availability and cost."""
        if self.default_provider != LLMProvider.AUTO:
            return self.default_provider

        # Auto selection logic
        # For now, prefer OpenAI for reliability
        return LLMProvider.OPENAI

    async def call_llm_with_retry(
        self, request: LLMRequest, max_retries: int = 3
    ) -> LLMResponse:
        """
        Call LLM with retry logic.

        Args:
            request: LLM request
            max_retries: Maximum number of retries

        Returns:
            LLM response
        """
        base_delay = 1

        for attempt in range(max_retries):
            try:
                return await self.generate_response(request)
            except HTTPException as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(
                    f"LLM call failed, retrying in {base_delay * (2 ** attempt)}s: {e}"
                )
                await asyncio.sleep(base_delay * (2**attempt))


# Pydantic models for API responses
class LLMResponseModel(BaseModel):
    """Response model for LLM generation."""

    content: str
    model_used: str
    provider_used: str
    tokens_used: int
    cost: float
    processing_time: float
    finish_reason: str


class FactExtractionResponse(BaseModel):
    """Response model for fact extraction."""

    facts: List[Dict]
    total_facts: int
    processing_time: float
    confidence_score: float


# Error classes
class LLMError(Exception):
    """Base LLM error."""

    pass


class ProviderNotAvailableError(LLMError):
    """LLM provider not available."""

    pass


class TokenLimitExceededError(LLMError):
    """Token limit exceeded."""

    pass


class ModelNotAvailableError(LLMError):
    """Model not available."""

    pass
