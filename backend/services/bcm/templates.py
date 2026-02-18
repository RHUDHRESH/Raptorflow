"""Business context template service for workspace seeding.

Loads and manages the 3 business context templates:
- agency (business_context_agency.json)
- ecommerce (business_context_ecommerce.json)  
- saas (business_context_saas.json)

Provides functions to extract foundation data and seed new workspaces.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Literal, Optional

logger = logging.getLogger(__name__)

# Template types
TemplateType = Literal["agency", "ecommerce", "saas"]

# Load templates from fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

# Cache for loaded templates
_templates_cache: Dict[TemplateType, Dict[str, Any]] = {}


def _load_template(name: TemplateType) -> Dict[str, Any]:
    """Load a template from fixtures directory."""
    file_path = FIXTURES_DIR / f"business_context_{name}.json"
    
    if not file_path.exists():
        raise FileNotFoundError(f"Template file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_template(template_type: TemplateType) -> Dict[str, Any]:
    """Get a business context template by type."""
    if template_type not in _templates_cache:
        _templates_cache[template_type] = _load_template(template_type)
    
    # Return a copy to prevent mutation of cached data
    return _templates_cache[template_type].copy()


def get_all_templates() -> Dict[str, Dict[str, Any]]:
    """Get all available templates."""
    return {
        "agency": get_template("agency"),
        "ecommerce": get_template("ecommerce"),
        "saas": get_template("saas"),
    }


def extract_foundation_data(template: Dict[str, Any]) -> Dict[str, Any]:
    """Extract foundation-relevant data from full business context template."""
    company = template.get("company_profile", {})
    intelligence = template.get("intelligence", {})
    
    # Get messaging pillars from intelligence if available
    messaging = {
        "pillars": [],
        "core_narrative": {},
    }
    
    # Get brand voice if icps available
    brand_voice = {
        "personality": {},
        "vocabulary": {},
    }
    
    # Extract ICPs for messaging insights
    icps = intelligence.get("icps", [])
    if icps:
        # Use first ICP for messaging insights
        first_icp = icps[0]
        psychographics = first_icp.get("psychographics", {})
        messaging["target_audience"] = first_icp.get("name")
        messaging["audience_insights"] = psychographics
    
    return {
        "company_info": {
            "name": company.get("name"),
            "website": company.get("website"),
            "industry": company.get("industry"),
            "stage": company.get("stage"),
            "description": company.get("description"),
        },
        "mission": company.get("description"),  # Use description as mission if no explicit mission
        "vision": None,  # Not in template, will be populated later
        "value_proposition": company.get("description"),
        "brand_voice": brand_voice,
        "messaging": messaging,
        "status": "active",
    }


def extract_icps(template: Dict[str, Any]) -> list:
    """Extract ICPs (Ideal Customer Profiles) from template."""
    intelligence = template.get("intelligence", {})
    return intelligence.get("icps", [])
