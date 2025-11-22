"""
Tag Assignment Agent - Assigns psychographic/demographic tags to ICPs.

Analyzes ICP descriptions and selects 5-15 most relevant tags from the
50+ tag catalog defined in persona.py. Returns tags with confidence scores.

Uses Vertex AI Gemini (fast model) for efficient tag selection.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

from backend.agents.base_agent import BaseAgent
from backend.models.persona import TAG_OPTIONS
from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id


logger = logging.getLogger(__name__)


# System prompt for tag assignment
TAG_ASSIGNMENT_SYSTEM_PROMPT = """You are an expert at classifying customer profiles with psychographic and demographic tags.

Your role:
- Analyze ICP descriptions and attributes
- Select the most relevant tags from a predefined catalog
- Assign confidence scores to each tag
- Return 5-15 tags that best describe the customer profile

You must ONLY use tags from the provided catalog. Never invent new tags.
Return tags ranked by relevance with confidence scores."""


class TagAssignmentAgent(BaseAgent):
    """
    Assigns tags from TAG_OPTIONS catalog to ICP profiles.

    Analyzes:
    - ICP description/summary
    - Demographics (industry, company size, role)
    - Psychographics (motivations, risk tolerance, values)

    Returns:
    - 5-15 most relevant tags
    - Confidence score for each tag
    - Category groupings
    """

    def __init__(self):
        super().__init__(name="TagAssignmentAgent")
        self.tag_catalog = TAG_OPTIONS

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assign tags to an ICP profile.

        Args:
            payload: Dict containing:
                - icp_description: str (executive summary or full description)
                - demographics: Dict (optional)
                - psychographics: Dict (optional)

        Returns:
            Dict with:
                - agent: str (agent name)
                - output: Dict with:
                    - tags: List[str] (selected tags)
                    - tag_confidences: Dict[str, float]
                    - categories: Dict[str, List[str]] (tags grouped by category)
        """
        correlation_id = get_correlation_id()
        self.log("Assigning tags to ICP profile")

        # Extract inputs
        icp_description = payload.get("icp_description", "")
        demographics = payload.get("demographics", {})
        psychographics = payload.get("psychographics", {})

        if not icp_description and not demographics and not psychographics:
            error_msg = "No ICP information provided for tag assignment"
            self.log(error_msg, level="error")
            raise ValueError(error_msg)

        # Build prompt
        prompt = self._build_prompt(
            icp_description=icp_description,
            demographics=demographics,
            psychographics=psychographics,
        )

        try:
            # Call Vertex AI with fast model
            self.log("Calling Vertex AI Gemini for tag assignment")
            response_json = await vertex_ai_client.generate_json(
                prompt=prompt,
                system_prompt=TAG_ASSIGNMENT_SYSTEM_PROMPT,
                model="fast",
                temperature=0.3,  # Lower temperature for more deterministic tagging
                max_tokens=2048,
            )

            self.log("Received tag assignment response")

            # Validate and process tags
            tag_data = self._process_tags(response_json)

            self.log(f"Assigned {len(tag_data['tags'])} tags successfully")

            return {
                "agent": self.name,
                "output": tag_data,
            }

        except Exception as e:
            error_msg = f"Tag assignment failed: {str(e)}"
            self.log(error_msg, level="error", exc_info=True)
            raise

    def _build_prompt(
        self,
        icp_description: str,
        demographics: Dict[str, Any],
        psychographics: Dict[str, Any],
    ) -> str:
        """
        Build XML-structured prompt for tag assignment.

        Args:
            icp_description: Executive summary or description
            demographics: Demographic attributes
            psychographics: Psychographic attributes

        Returns:
            XML-formatted prompt
        """
        # Format demographics
        demo_text = "\n".join([
            f"- {key}: {value}"
            for key, value in demographics.items()
            if value
        ]) if demographics else "Not provided"

        # Format psychographics
        psycho_text = "\n".join([
            f"- {key}: {value}"
            for key, value in psychographics.items()
            if value and not isinstance(value, (list, dict))
        ]) if psychographics else "Not provided"

        # Format psychographic lists
        if psychographics:
            for key in ["motivations", "values", "objections"]:
                if key in psychographics and psychographics[key]:
                    psycho_text += f"\n- {key}: {', '.join(psychographics[key])}"

        # Format tag catalog
        tag_catalog_text = ", ".join(self.tag_catalog)

        prompt = f"""
<context>
You are assigning psychographic and demographic tags to an Ideal Customer Profile.

ICP Description:
{icp_description}

Demographics:
{demo_text}

Psychographics:
{psycho_text}
</context>

<task>
Select the 5-15 most relevant tags from the catalog below that best describe this ICP.

Consider:
1. Industry and company characteristics → industry/vertical tags
2. Buyer behavior and decision patterns → behavioral tags
3. Team structure and culture → organizational tags
4. Technology adoption and preferences → technical tags
5. Marketing and sales approach → GTM tags

For each selected tag, assign a confidence score (0.0-1.0) indicating how well it fits.
</task>

<tag_catalog>
Available tags (you MUST only select from these):

{tag_catalog_text}
</tag_catalog>

<output_format>
Return a JSON object with this structure:

{{
  "selected_tags": [
    {{
      "tag": "tag_name_from_catalog",
      "confidence": 0.95,
      "reason": "Brief reason for selection"
    }},
    ...
  ]
}}

Requirements:
- Select 5-15 tags minimum
- All tags must exist in the catalog above
- Confidence scores must be between 0.0 and 1.0
- Order tags by confidence (highest first)
- Provide brief reason for each tag
- Return ONLY valid JSON
</output_format>
"""
        return prompt

    def _process_tags(self, response_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate tag assignment response.

        Args:
            response_json: Raw JSON from LLM

        Returns:
            Processed tag data with validation
        """
        selected_tags = response_json.get("selected_tags", [])

        if not selected_tags:
            self.log("No tags returned by model, using fallback", level="warning")
            return self._fallback_tags()

        # Validate and extract tags
        valid_tags = []
        tag_confidences = {}
        tag_reasons = {}

        for tag_entry in selected_tags:
            tag_name = tag_entry.get("tag", "")
            confidence = tag_entry.get("confidence", 0.5)
            reason = tag_entry.get("reason", "")

            # Validate tag exists in catalog
            if tag_name in self.tag_catalog:
                valid_tags.append(tag_name)
                tag_confidences[tag_name] = confidence
                tag_reasons[tag_name] = reason
            else:
                # Try to map to closest known tag
                mapped_tag = self._map_to_known_tag(tag_name)
                if mapped_tag:
                    self.log(f"Mapped unknown tag '{tag_name}' to '{mapped_tag}'")
                    valid_tags.append(mapped_tag)
                    tag_confidences[mapped_tag] = confidence * 0.8  # Reduce confidence
                    tag_reasons[mapped_tag] = f"Mapped from: {tag_name}. {reason}"
                else:
                    self.log(f"Ignoring unknown tag: {tag_name}", level="warning")

        # Ensure we have at least 5 tags
        if len(valid_tags) < 5:
            self.log(f"Only {len(valid_tags)} tags found, adding defaults", level="warning")
            valid_tags.extend(self._get_default_tags())
            valid_tags = list(set(valid_tags))[:15]  # Deduplicate and cap at 15

        # Categorize tags
        categories = self._categorize_tags(valid_tags)

        return {
            "tags": valid_tags,
            "tag_confidences": tag_confidences,
            "tag_reasons": tag_reasons,
            "categories": categories,
            "total_tags": len(valid_tags),
        }

    def _map_to_known_tag(self, unknown_tag: str) -> str | None:
        """
        Map an unknown tag to the closest known tag using fuzzy matching.

        Args:
            unknown_tag: Tag not in catalog

        Returns:
            Closest known tag or None
        """
        unknown_lower = unknown_tag.lower().replace("-", "_").replace(" ", "_")

        # Direct substring match
        for known_tag in self.tag_catalog:
            if unknown_lower in known_tag or known_tag in unknown_lower:
                return known_tag

        # Common mappings
        mappings = {
            "startup": "founder_led",
            "enterprise": "enterprise_it",
            "smb": "smb_owner",
            "saas": "saas",
            "b2b": "b2b",
            "b2c": "b2c",
            "tech": "technical_buyer",
            "developer": "developer_tooling",
            "marketing": "marketing_leader",
            "sales": "sales_leader",
            "data": "data_driven",
            "ai": "ai_first",
            "security": "security_first",
        }

        for keyword, known_tag in mappings.items():
            if keyword in unknown_lower and known_tag in self.tag_catalog:
                return known_tag

        return None

    def _get_default_tags(self) -> List[str]:
        """Get default fallback tags."""
        return [
            "b2b",
            "data_driven",
            "value_buyer",
            "process_oriented",
            "performance_marketing",
        ]

    def _fallback_tags(self) -> Dict[str, Any]:
        """Return fallback tag assignment if LLM fails."""
        default_tags = self._get_default_tags()
        return {
            "tags": default_tags,
            "tag_confidences": {tag: 0.5 for tag in default_tags},
            "tag_reasons": {tag: "Fallback tag" for tag in default_tags},
            "categories": self._categorize_tags(default_tags),
            "total_tags": len(default_tags),
        }

    def _categorize_tags(self, tags: List[str]) -> Dict[str, List[str]]:
        """
        Group tags into categories.

        Args:
            tags: List of tag names

        Returns:
            Dict of category -> tags
        """
        categories = {
            "demographic": [],
            "psychographic": [],
            "behavioral": [],
            "technical": [],
            "industry": [],
        }

        # Industry tags
        industry_tags = [
            "healthcare", "finserv", "education", "manufacturing",
            "ecommerce", "saas", "marketplace",
        ]

        # Demographic tags
        demographic_tags = [
            "enterprise_it", "midmarket_ops", "smb_owner", "agency_owner",
            "founder_led", "remote_first", "hybrid_team", "distributed_team",
            "in_office", "global_team",
        ]

        # Behavioral tags
        behavioral_tags = [
            "early_adopter", "fast_follower", "cost_sensitive", "value_buyer",
            "premium_buyer", "trial_focused", "freemium_motion",
        ]

        # Technical tags
        technical_tags = [
            "developer_tooling", "ai_first", "automation_focus",
            "security_first", "compliance_led", "data_driven",
        ]

        # Psychographic (everything else)
        for tag in tags:
            if tag in industry_tags:
                categories["industry"].append(tag)
            elif tag in demographic_tags:
                categories["demographic"].append(tag)
            elif tag in behavioral_tags:
                categories["behavioral"].append(tag)
            elif tag in technical_tags:
                categories["technical"].append(tag)
            else:
                categories["psychographic"].append(tag)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}


# Global instance
tag_assignment_agent = TagAssignmentAgent()
