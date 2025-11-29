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
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from backend.agents.base_agent import BaseAgentEnhanced
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
- Learn from past successful ICP patterns to improve recommendations

You return only valid JSON adhering to the schema provided in the task.
Be thorough, specific, and evidence-based. Never hallucinate - use "Unknown" if information is missing."""


class ICPBuilderAgent(BaseAgentEnhanced):
    """
    Builds structured ICP profiles from basic company inputs.

    Inherits from BaseAgent and implements execute() to:
    1. Construct XML-formatted prompt
    2. Call Vertex AI Gemini (fast model)
    3. Validate response against ICPResponse schema
    4. Return structured dict
    """

    def __init__(self):
        super().__init__(name="ICPBuilderAgent", auto_remember=True)

    async def _execute_with_memory(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build ICP from company information with memory integration.

        Args:
            payload: Dict containing:
                - company_name: str
                - industry: str
                - product_description: str
                - target_market: Optional[str]
                - target_geo: Optional[str]
                - workspace_id: str (for memory context)

        Returns:
            Dict with:
                - status: str
                - agent: str (agent name)
                - output: Dict (ICPResponse data)
                - success_score: float
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
            return {
                "status": "error",
                "agent": self.name,
                "error": error_msg,
                "success_score": 0.0,
            }

        try:
            # Recall similar ICPs from past successes
            past_icps = await self.recall(
                query=f"successful ICP for {industry} industry with product: {product_description[:100]}",
                memory_types=["success"],
                min_success_score=0.7,
                top_k=3,
            )

            # Extract patterns from past successful ICPs
            past_patterns = self._extract_icp_patterns(past_icps)

            # Construct XML-formatted prompt with learned patterns
            prompt = self._build_prompt(
                company_name=company_name,
                industry=industry,
                product_description=product_description,
                target_market=target_market,
                target_geo=target_geo,
                past_patterns=past_patterns,
            )

            # Call Vertex AI Gemini with fast model
            self.log("Calling Vertex AI Gemini (fast model) with learned patterns")
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

            # Calculate success score based on confidence and completeness
            success_score = self._calculate_icp_success_score(icp_data)

            # Result will be automatically stored by auto_remember=True
            result = {
                "status": "success",
                "agent": self.name,
                "output": icp_data,
                "success_score": success_score,
                "used_past_patterns": len(past_icps) > 0,
            }

            self.log(
                "ICP built successfully",
                success_score=success_score,
                used_patterns=len(past_icps),
            )

            # Publish completion event
            await self.publish_event(
                "agent.research.icp_generated",
                {
                    "company_name": company_name,
                    "industry": industry,
                    "icp_name": icp_data.get("icp_name"),
                    "confidence": icp_data.get("confidence")
                }
            )

            return result

        except Exception as e:
            error_msg = f"ICP building failed: {str(e)}"
            self.log(error_msg, level="error", exc_info=True)
            return {
                "status": "error",
                "agent": self.name,
                "error": error_msg,
                "success_score": 0.0,
            }

    def _extract_icp_patterns(self, past_icps: list[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract common patterns from past successful ICPs.

        Args:
            past_icps: List of memory records with similar ICPs

        Returns:
            Dictionary with extracted patterns
        """
        if not past_icps:
            return {}

        patterns = {
            "common_pain_points": [],
            "effective_triggers": [],
            "typical_decision_structures": [],
            "successful_messaging_themes": [],
        }

        for mem in past_icps:
            result = mem.get("result", {}).get("output", {})
            if result:
                patterns["common_pain_points"].extend(result.get("pain_points", []))
                patterns["effective_triggers"].extend(result.get("behavioral_triggers", []))
                if result.get("decision_structure"):
                    patterns["typical_decision_structures"].append(result["decision_structure"])

        # Deduplicate and limit
        patterns["common_pain_points"] = list(set(patterns["common_pain_points"]))[:5]
        patterns["effective_triggers"] = list(set(patterns["effective_triggers"]))[:5]
        patterns["typical_decision_structures"] = list(set(patterns["typical_decision_structures"]))[:3]

        return patterns

    def _calculate_icp_success_score(self, icp_data: Dict[str, Any]) -> float:
        """
        Calculate success score for generated ICP.

        Args:
            icp_data: ICP response data

        Returns:
            Success score (0.0-1.0)
        """
        # Base score on confidence
        score = icp_data.get("confidence", 0.5)

        # Boost for completeness
        completeness_factors = [
            len(icp_data.get("pain_points", [])) >= 3,
            len(icp_data.get("goals", [])) >= 3,
            len(icp_data.get("behavioral_triggers", [])) >= 3,
            icp_data.get("demographics", {}).get("buyer_role") != "Unknown",
            bool(icp_data.get("budget")),
            bool(icp_data.get("timeline")),
        ]
        completeness = sum(completeness_factors) / len(completeness_factors)

        # Weighted average
        final_score = (score * 0.6) + (completeness * 0.4)

        return round(min(final_score, 1.0), 2)

    def _build_prompt(
        self,
        company_name: str,
        industry: str,
        product_description: str,
        target_market: str,
        target_geo: str,
        past_patterns: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Build XML-structured prompt for ICP generation.

        Args:
            company_name: Name of company
            industry: Industry/vertical
            product_description: What the product does
            target_market: Target market segment
            target_geo: Geographic target
            past_patterns: Optional patterns from similar past ICPs

        Returns:
            XML-formatted prompt string
        """
        # Build past patterns context
        patterns_context = ""
        if past_patterns and any(past_patterns.values()):
            patterns_context = "\n<learned_patterns>\nBased on similar successful ICPs in the past:\n"

            if past_patterns.get("common_pain_points"):
                patterns_context += f"\nCommon pain points observed:\n"
                for pp in past_patterns["common_pain_points"][:3]:
                    patterns_context += f"- {pp}\n"

            if past_patterns.get("effective_triggers"):
                patterns_context += f"\nEffective behavioral triggers:\n"
                for trigger in past_patterns["effective_triggers"][:3]:
                    patterns_context += f"- {trigger}\n"

            if past_patterns.get("typical_decision_structures"):
                patterns_context += f"\nTypical decision structures: {', '.join(past_patterns['typical_decision_structures'][:2])}\n"

            patterns_context += "\nConsider these patterns but adapt them to this specific context.\n</learned_patterns>\n"

        prompt = f"""
<context>
You are building an Ideal Customer Profile (ICP) for {company_name}.

Company Information:
- Name: {company_name}
- Industry: {industry}
- Product: {product_description}
- Target Market: {target_market or "To be determined"}
- Geography: {target_geo}
{patterns_context}
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
