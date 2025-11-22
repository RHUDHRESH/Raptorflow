"""
ICP Builder Agent - Creates structured Ideal Customer Profiles.

Accepts company information and builds a comprehensive ICP with:
- Executive summary
- Demographics (company size, industry, role, location)
- Psychographics (motivations, risk tolerance, decision style)
- Pain points and goals
- Budget and timeline estimates
- Behavioral triggers

Uses Vertex AI Gemini (fast model) with XML-structured prompts.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from pydantic import ValidationError

from backend.agents.base_agent import BaseAgent
from backend.models.persona import Demographics, ICPResponse, Psychographics
from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id


logger = logging.getLogger(__name__)


# System prompt for ICP building
ICP_BUILDER_SYSTEM_PROMPT = """You are an expert customer intelligence analyst specializing in building Ideal Customer Profiles (ICPs).

Your role:
- Analyze company and product information to infer target customer profiles
- Extract structured demographics and psychographics
- Identify pain points, goals, and behavioral triggers
- Provide actionable insights for marketing and sales

You return only valid JSON adhering to the schema provided in the task.
Be thorough, specific, and evidence-based. Never hallucinate - use "Unknown" if information is missing."""


class ICPBuilderAgent(BaseAgent):
    """
    Builds structured ICP profiles from basic company inputs.

    Inherits from BaseAgent and implements execute() to:
    1. Construct XML-formatted prompt
    2. Call Vertex AI Gemini (fast model)
    3. Validate response against ICPResponse schema
    4. Return structured dict
    """

    def __init__(self):
        super().__init__(name="ICPBuilderAgent")

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build ICP from company information.

        Args:
            payload: Dict containing:
                - company_name: str
                - industry: str
                - product_description: str
                - target_market: Optional[str]
                - target_geo: Optional[str]

        Returns:
            Dict with:
                - agent: str (agent name)
                - output: Dict (ICPResponse data)
        """
        correlation_id = get_correlation_id()
        self.log(f"Building ICP for company: {payload.get('company_name', 'Unknown')}")

        # Extract inputs
        company_name = payload.get("company_name", "")
        industry = payload.get("industry", "")
        product_description = payload.get("product_description", "")
        target_market = payload.get("target_market", "")
        target_geo = payload.get("target_geo", "Global")

        if not company_name or not product_description:
            error_msg = "Missing required fields: company_name and product_description"
            self.log(error_msg, level="error")
            raise ValueError(error_msg)

        # Construct XML-formatted prompt
        prompt = self._build_prompt(
            company_name=company_name,
            industry=industry,
            product_description=product_description,
            target_market=target_market,
            target_geo=target_geo,
        )

        try:
            # Call Vertex AI Gemini with fast model
            self.log("Calling Vertex AI Gemini (fast model)")
            response_json = await vertex_ai_client.generate_json(
                prompt=prompt,
                system_prompt=ICP_BUILDER_SYSTEM_PROMPT,
                model="fast",  # Use fast Gemini model
                temperature=0.5,
                max_tokens=4096,
            )

            self.log("Received ICP response from Gemini")

            # Validate against ICPResponse schema
            icp_data = self._validate_and_transform(response_json, company_name)

            self.log("ICP validation successful")

            return {
                "agent": self.name,
                "output": icp_data,
            }

        except Exception as e:
            error_msg = f"ICP building failed: {str(e)}"
            self.log(error_msg, level="error", exc_info=True)
            raise

    def _build_prompt(
        self,
        company_name: str,
        industry: str,
        product_description: str,
        target_market: str,
        target_geo: str,
    ) -> str:
        """
        Build XML-structured prompt for ICP generation.

        Args:
            company_name: Name of company
            industry: Industry/vertical
            product_description: What the product does
            target_market: Target market segment
            target_geo: Geographic target

        Returns:
            XML-formatted prompt string
        """
        prompt = f"""
<context>
You are building an Ideal Customer Profile (ICP) for {company_name}.

Company Information:
- Name: {company_name}
- Industry: {industry}
- Product: {product_description}
- Target Market: {target_market or "To be determined"}
- Geography: {target_geo}
</context>

<task>
Analyze the company and product information to build a comprehensive ICP. Infer the most likely customer profile based on:
1. The industry and product description
2. Common patterns in similar companies
3. Value propositions implied by the product

Extract structured information across these dimensions:
- Demographics (company size, revenue, industry, location, buyer role)
- Psychographics (motivations, risk tolerance, decision style, buying behavior)
- Pain points (3-5 specific challenges this product solves)
- Goals (3-5 objectives the customer wants to achieve)
- Budget and timeline estimates
- Behavioral triggers (events that prompt buying action)
</task>

<output_format>
Return a JSON object with this exact structure:

{{
  "icp_name": "A descriptive name for this ICP (e.g., 'Scaling SaaS Founders', 'Enterprise IT Directors')",
  "executive_summary": "2-3 sentence summary of who this customer is and why they need the product",
  "demographics": {{
    "company_size": "Employee range (e.g., '11-50', '51-200', '201-500')",
    "revenue_range": "Annual revenue range if applicable (e.g., '$1M-$10M')",
    "industry": "Primary industry vertical",
    "geography": "Primary geographic market",
    "buyer_role": "Specific job title/role of decision maker"
  }},
  "psychographics": {{
    "motivation": "Primary buying motivation (e.g., 'ROI-driven', 'Innovation-seeking')",
    "motivations": ["List of 3-5 specific motivations"],
    "risk_tolerance": "Conservative | Moderate | Aggressive",
    "decision_style": "How they make decisions (e.g., 'Data-driven', 'Consensus-based')",
    "buying_behavior": "Typical buying pattern (e.g., 'Trial-first', 'Reference-driven')",
    "values": ["List of 3-5 core values"],
    "objections": ["List of 3-5 common objections or concerns"]
  }},
  "pain_points": [
    "Specific pain point 1 (be concrete, not generic)",
    "Specific pain point 2",
    "Specific pain point 3",
    "etc. (3-5 total)"
  ],
  "goals": [
    "Specific goal 1",
    "Specific goal 2",
    "etc. (3-5 total)"
  ],
  "behavioral_triggers": [
    "Event or threshold that creates urgency 1",
    "Event or threshold that creates urgency 2",
    "etc. (3-5 total)"
  ],
  "budget": "Typical budget range (e.g., '$10K-$50K annually')",
  "timeline": "Typical decision timeline (e.g., '1-3 months')",
  "decision_structure": "How decisions are made (e.g., 'Single stakeholder', 'Committee of 3-5')",
  "confidence": 0.85,
  "sources": ["Industry knowledge", "Product analysis", "Market patterns"]
}}

IMPORTANT:
- Be specific and actionable
- Base inferences on the product and industry provided
- Use "Unknown" for fields you cannot confidently infer
- Ensure all lists have 3-5 items minimum
- Return ONLY the JSON, no additional text
</output_format>
"""
        return prompt

    def _validate_and_transform(
        self,
        response_json: Dict[str, Any],
        company_name: str,
    ) -> Dict[str, Any]:
        """
        Validate and transform LLM response into ICPResponse schema.

        Args:
            response_json: Raw JSON from LLM
            company_name: Company name for fallback

        Returns:
            Validated ICP data dict

        Raises:
            ValidationError: If response doesn't match schema
        """
        try:
            # Extract nested fields if needed
            demographics_data = response_json.get("demographics", {})
            psychographics_data = response_json.get("psychographics", {})

            # Validate Demographics
            demographics = Demographics(**demographics_data)

            # Validate Psychographics
            psychographics = Psychographics(**psychographics_data)

            # Build ICPResponse
            icp_response = ICPResponse(
                icp_name=response_json.get("icp_name", f"{company_name} Target Customer"),
                executive_summary=response_json.get("executive_summary", ""),
                demographics=demographics,
                psychographics=psychographics,
                pain_points=response_json.get("pain_points", []),
                goals=response_json.get("goals", []),
                behavioral_triggers=response_json.get("behavioral_triggers", []),
                budget=response_json.get("budget"),
                timeline=response_json.get("timeline"),
                decision_structure=response_json.get("decision_structure"),
                confidence=response_json.get("confidence", 0.75),
                sources=response_json.get("sources", ["LLM inference"]),
                tags=[],  # Tags assigned by separate agent
            )

            # Return as dict
            return icp_response.model_dump()

        except ValidationError as e:
            self.log(f"ICP validation failed: {e}", level="error")
            # Return fallback ICP
            return self._fallback_icp(company_name, response_json)

    def _fallback_icp(
        self,
        company_name: str,
        raw_response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create minimal fallback ICP if validation fails.

        Args:
            company_name: Company name
            raw_response: Original LLM response

        Returns:
            Minimal valid ICP dict
        """
        self.log("Using fallback ICP due to validation failure", level="warning")

        fallback = ICPResponse(
            icp_name=raw_response.get("icp_name", f"{company_name} Customer"),
            executive_summary=raw_response.get(
                "executive_summary",
                f"Target customer for {company_name}",
            ),
            demographics=Demographics(
                buyer_role=raw_response.get("demographics", {}).get("buyer_role", "Unknown"),
            ),
            psychographics=Psychographics(),
            pain_points=raw_response.get("pain_points", [])[:5],
            goals=raw_response.get("goals", [])[:5],
            behavioral_triggers=[],
            confidence=0.5,
            sources=["Fallback - partial data"],
            tags=[],
        )

        return fallback.model_dump()


# Global instance
icp_builder_agent = ICPBuilderAgent()
