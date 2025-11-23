"""
Pain Point Miner Agent - Extracts and categorizes pain points.

Analyzes ICP descriptions and existing pain points to:
1. Extract specific pain points
2. Categorize them: operational, financial, strategic
3. Map each pain point to how the product solves it

Uses Vertex AI Gemini (fast model) for efficient analysis.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from backend.agents.base_agent import BaseAgent
from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id


logger = logging.getLogger(__name__)


# System prompt for pain point mining
PAIN_POINT_MINER_SYSTEM_PROMPT = """You are an expert at identifying and categorizing customer pain points.

Your role:
- Analyze ICP descriptions and extract specific pain points
- Categorize pain points into: operational, financial, strategic
- Map each pain point to potential solutions
- Identify pain severity and urgency
- Extract language patterns customers use when describing problems

Be specific and actionable. Focus on real, concrete challenges, not generic platitudes."""


class PainPointMinerAgent(BaseAgent):
    """
    Mines and categorizes pain points from ICP data.

    Categorizes pain points as:
    - Operational: Day-to-day workflow challenges, inefficiencies
    - Financial: Budget, ROI, cost-related issues
    - Strategic: Long-term goals, competitive positioning, growth

    Maps each pain point to how the product addresses it.
    """

    def __init__(self):
        super().__init__(name="PainPointMinerAgent")

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and categorize pain points.

        Args:
            payload: Dict containing:
                - icp_description: str (executive summary)
                - existing_pain_points: List[str] (optional)
                - product_description: str (to map solutions)

        Returns:
            Dict with:
                - agent: str (agent name)
                - output: Dict with:
                    - operational: List[Dict] (pain points with solutions)
                    - financial: List[Dict] (pain points with solutions)
                    - strategic: List[Dict] (pain points with solutions)
                    - all_pain_points: List[str] (flat list)
        """
        correlation_id = get_correlation_id()
        self.log("Mining and categorizing pain points")

        # Extract inputs
        icp_description = payload.get("icp_description", "")
        existing_pain_points = payload.get("existing_pain_points", [])
        product_description = payload.get("product_description", "")

        if not icp_description and not existing_pain_points:
            error_msg = "No ICP information or existing pain points provided"
            self.log(error_msg, level="error")
            raise ValueError(error_msg)

        # Build prompt
        prompt = self._build_prompt(
            icp_description=icp_description,
            existing_pain_points=existing_pain_points,
            product_description=product_description,
        )

        try:
            # Call Vertex AI with fast model
            self.log("Calling Vertex AI Gemini for pain point mining")
            response_json = await vertex_ai_client.generate_json(
                prompt=prompt,
                system_prompt=PAIN_POINT_MINER_SYSTEM_PROMPT,
                model="fast",
                temperature=0.6,  # Moderate temperature for balanced creativity
                max_tokens=3072,
            )

            self.log("Received pain point mining response")

            # Process and validate
            pain_point_data = self._process_pain_points(response_json)

            self.log(f"Categorized {pain_point_data['total_pain_points']} pain points")

            return {
                "agent": self.name,
                "output": pain_point_data,
            }

        except Exception as e:
            error_msg = f"Pain point mining failed: {str(e)}"
            self.log(error_msg, level="error", exc_info=True)
            raise

    def _build_prompt(
        self,
        icp_description: str,
        existing_pain_points: List[str],
        product_description: str,
    ) -> str:
        """
        Build XML-structured prompt for pain point mining.

        Args:
            icp_description: ICP executive summary
            existing_pain_points: Already identified pain points
            product_description: Product/service description

        Returns:
            XML-formatted prompt
        """
        # Format existing pain points
        pain_points_text = "\n".join([
            f"- {pp}" for pp in existing_pain_points
        ]) if existing_pain_points else "None provided"

        prompt = f"""
<context>
You are analyzing customer pain points for this ICP:

ICP Description:
{icp_description}

Existing Pain Points:
{pain_points_text}

Product/Service:
{product_description}
</context>

<task>
Extract and categorize pain points into three categories:

1. OPERATIONAL Pain Points
   - Day-to-day workflow challenges
   - Process inefficiencies
   - Team productivity issues
   - Time-consuming manual tasks
   - Tool/technology limitations

2. FINANCIAL Pain Points
   - Budget constraints
   - ROI concerns
   - Cost inefficiencies
   - Revenue impact
   - Wasted spending

3. STRATEGIC Pain Points
   - Long-term growth challenges
   - Competitive positioning
   - Market trends
   - Scaling issues
   - Strategic alignment

For each pain point:
- Be specific and concrete (not generic)
- Explain the impact/severity
- Map to how the product addresses it
- Rate urgency (high/medium/low)
</task>

<output_format>
Return a JSON object with this structure:

{{
  "operational": [
    {{
      "pain_point": "Specific operational pain point",
      "impact": "Description of the impact this has",
      "urgency": "high|medium|low",
      "solution_mapping": "How the product solves this pain point"
    }},
    ...
  ],
  "financial": [
    {{
      "pain_point": "Specific financial pain point",
      "impact": "Description of the impact",
      "urgency": "high|medium|low",
      "solution_mapping": "How the product solves this pain point"
    }},
    ...
  ],
  "strategic": [
    {{
      "pain_point": "Specific strategic pain point",
      "impact": "Description of the impact",
      "urgency": "high|medium|low",
      "solution_mapping": "How the product solves this pain point"
    }},
    ...
  ]
}}

Requirements:
- Include 3-5 pain points per category
- Be specific and actionable
- Base solution mappings on the product description provided
- Focus on high-impact pain points
- Use language customers actually use
- Return ONLY valid JSON
</output_format>
"""
        return prompt

    def _process_pain_points(
        self,
        response_json: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Process and validate pain point response.

        Args:
            response_json: Raw JSON from LLM

        Returns:
            Processed pain point data
        """
        operational = response_json.get("operational", [])
        financial = response_json.get("financial", [])
        strategic = response_json.get("strategic", [])

        # Validate structure
        if not operational and not financial and not strategic:
            self.log("No pain points returned, using fallback", level="warning")
            return self._fallback_pain_points()

        # Extract flat list of all pain points
        all_pain_points = []
        for category in [operational, financial, strategic]:
            for item in category:
                if isinstance(item, dict) and "pain_point" in item:
                    all_pain_points.append(item["pain_point"])
                elif isinstance(item, str):
                    all_pain_points.append(item)

        # Count by urgency
        urgency_counts = {"high": 0, "medium": 0, "low": 0}
        for category in [operational, financial, strategic]:
            for item in category:
                if isinstance(item, dict):
                    urgency = item.get("urgency", "medium")
                    urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1

        return {
            "operational": operational,
            "financial": financial,
            "strategic": strategic,
            "all_pain_points": all_pain_points,
            "total_pain_points": len(all_pain_points),
            "urgency_breakdown": urgency_counts,
            "categories": {
                "operational": len(operational),
                "financial": len(financial),
                "strategic": len(strategic),
            },
        }

    def _fallback_pain_points(self) -> Dict[str, Any]:
        """
        Return fallback pain points if LLM fails.

        Returns:
            Minimal pain point structure
        """
        self.log("Using fallback pain points", level="warning")

        fallback_operational = [
            {
                "pain_point": "Manual, time-consuming processes",
                "impact": "Reduces team productivity and increases error rate",
                "urgency": "high",
                "solution_mapping": "Automates repetitive tasks",
            },
            {
                "pain_point": "Lack of visibility into key metrics",
                "impact": "Difficult to make data-driven decisions",
                "urgency": "medium",
                "solution_mapping": "Provides real-time dashboards and reports",
            },
        ]

        fallback_financial = [
            {
                "pain_point": "Inefficient resource allocation",
                "impact": "Wasted budget on low-ROI activities",
                "urgency": "high",
                "solution_mapping": "Optimizes spending with AI-driven insights",
            },
        ]

        fallback_strategic = [
            {
                "pain_point": "Difficulty scaling operations",
                "impact": "Growth limited by operational bottlenecks",
                "urgency": "medium",
                "solution_mapping": "Provides scalable infrastructure",
            },
        ]

        all_pain_points = [
            item["pain_point"]
            for item in fallback_operational + fallback_financial + fallback_strategic
        ]

        return {
            "operational": fallback_operational,
            "financial": fallback_financial,
            "strategic": fallback_strategic,
            "all_pain_points": all_pain_points,
            "total_pain_points": len(all_pain_points),
            "urgency_breakdown": {"high": 2, "medium": 2, "low": 0},
            "categories": {
                "operational": len(fallback_operational),
                "financial": len(fallback_financial),
                "strategic": len(fallback_strategic),
            },
        }


# Global instance
pain_point_miner_agent = PainPointMinerAgent()
