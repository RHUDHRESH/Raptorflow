"""
Research Agent Configuration and Setup
Vertex AI integration with Gemini model hierarchy
"""

import os
from typing import Any, Dict

# Vertex AI Configuration
VERTEX_AI_CONFIG = {
    "project_id": os.getenv("VERTEX_AI_PROJECT_ID", "your-project-id"),
    "location": os.getenv("VERTEX_AI_LOCATION", "us-central1"),
    "credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS", None),
}

# Gemini Model Configuration
GEMINI_MODELS = {
    "flashlight": {
        "model_name": "gemini-2.5-flash-lite-preview-06-17",
        "usage_percentage": 85,
        "cost_per_1m_tokens": 0.025,
        "description": "Economical model for standard research tasks",
    },
    "flash": {
        "model_name": "gemini-2.5-flash-preview-04-17",
        "usage_percentage": 10,
        "cost_per_1m_tokens": 0.075,
        "description": "Reasoning model for planning and verification",
    },
    "ultra": {
        "model_name": "gemini-3-flash-preview-00-00",
        "usage_percentage": 5,
        "cost_per_1m_tokens": 0.15,
        "description": "Ultra reasoning model for complex synthesis",
    },
}

# Research Agent Configuration
RESEARCH_AGENT_CONFIG = {
    "max_search_results": 10,
    "max_scrape_urls": 5,
    "default_timeout": 30,
    "retry_attempts": 3,
    "confidence_threshold": 0.7,
    "cost_limit_per_request": 0.01,  # $0.01 per request
    "enable_caching": True,
    "cache_ttl": 3600,  # 1 hour
}

# A→A→P→A→P Inference Pattern Configuration
INFERENCE_PATTERN = {
    "analyze": {
        "model": "flashlight",
        "description": "Parse and understand research request",
        "max_tokens": 1000,
    },
    "assess": {
        "model": "dynamic",  # Based on complexity
        "description": "Determine optimal research strategy",
        "max_tokens": 2000,
    },
    "plan": {
        "model": "flash",
        "description": "Create detailed execution plan",
        "max_tokens": 1500,
    },
    "act": {
        "model": "none",  # Uses search/scrape tools
        "description": "Execute research plan",
        "max_tokens": 0,
    },
    "present": {
        "model": "dynamic",  # Based on depth
        "description": "Synthesize and format results",
        "max_tokens": 3000,
    },
}

# Report Generation Configuration
REPORT_CONFIG = {
    "json": {
        "include_metadata": True,
        "include_sources": True,
        "include_confidence": True,
        "format": "structured",
    },
    "ppt": {
        "max_slides": 10,
        "include_visuals": True,
        "template": "professional",
        "format": "outline",
    },
    "pdf": {
        "include_toc": True,
        "include_appendix": True,
        "page_format": "A4",
        "format": "content",
    },
}

# Search Integration Configuration
SEARCH_INTEGRATION = {
    "free_web_search": {
        "engines": ["duckduckgo", "brave", "searx"],
        "max_results_per_engine": 10,
        "timeout": 15,
    },
    "ultra_fast_scraper": {
        "strategy": "async",
        "timeout": 30,
        "max_content_length": 50000,
        "legal_basis": "research",
    },
}

# Cost Optimization Configuration
COST_OPTIMIZATION = {
    "enable_model_routing": True,
    "cost_tracking": True,
    "budget_alerts": True,
    "daily_budget_limit": 1.0,  # $1 per day
    "monthly_budget_limit": 30.0,  # $30 per month
    "prefer_cheaper_models": True,
    "token_optimization": True,
}

# Monitoring and Logging Configuration
MONITORING_CONFIG = {
    "log_level": "INFO",
    "enable_metrics": True,
    "track_model_usage": True,
    "track_costs": True,
    "track_performance": True,
    "alert_on_failures": True,
    "retention_days": 30,
}

# Error Handling Configuration
ERROR_HANDLING = {
    "max_retries": 3,
    "retry_delay": 1.0,  # seconds
    "fallback_enabled": True,
    "graceful_degradation": True,
    "error_reporting": True,
}

# Security Configuration
SECURITY_CONFIG = {
    "enable_input_validation": True,
    "enable_output_sanitization": True,
    "max_query_length": 1000,
    "allowed_domains": [],  # Empty means all domains allowed
    "blocked_domains": [],
    "enable_rate_limiting": True,
    "requests_per_minute": 60,
}


def get_config() -> Dict[str, Any]:
    """Get complete configuration"""
    return {
        "vertex_ai": VERTEX_AI_CONFIG,
        "gemini_models": GEMINI_MODELS,
        "research_agent": RESEARCH_AGENT_CONFIG,
        "inference_pattern": INFERENCE_PATTERN,
        "reports": REPORT_CONFIG,
        "search_integration": SEARCH_INTEGRATION,
        "cost_optimization": COST_OPTIMIZATION,
        "monitoring": MONITORING_CONFIG,
        "error_handling": ERROR_HANDLING,
        "security": SECURITY_CONFIG,
    }


def validate_config() -> bool:
    """Validate configuration settings"""
    errors = []

    # Check Vertex AI configuration
    if (
        not VERTEX_AI_CONFIG["project_id"]
        or VERTEX_AI_CONFIG["project_id"] == "your-project-id"
    ):
        errors.append("VERTEX_AI_PROJECT_ID not set")

    # Check model percentages sum to 100
    total_percentage = sum(
        model["usage_percentage"] for model in GEMINI_MODELS.values()
    )
    if total_percentage != 100:
        errors.append(
            f"Model usage percentages sum to {total_percentage}, expected 100"
        )

    # Check cost limits
    if RESEARCH_AGENT_CONFIG["cost_limit_per_request"] <= 0:
        errors.append("Cost limit per request must be positive")

    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return False

    return True


if __name__ == "__main__":
    config = get_config()
    print("Research Agent Configuration:")
    print("=" * 50)

    print(f"Vertex AI Project: {VERTEX_AI_CONFIG['project_id']}")
    print(f"Location: {VERTEX_AI_CONFIG['location']}")

    print(f"\nModel Hierarchy:")
    for model, config in GEMINI_MODELS.items():
        print(
            f"  {config['model_name']}: {config['usage_percentage']}% (${config['cost_per_1m_tokens']}/1M tokens)"
        )

    print(f"\nCost Limits:")
    print(f"  Per request: ${RESEARCH_AGENT_CONFIG['cost_limit_per_request']}")
    print(f"  Daily: ${COST_OPTIMIZATION['daily_budget_limit']}")
    print(f"  Monthly: ${COST_OPTIMIZATION['monthly_budget_limit']}")

    print(f"\nConfiguration Valid: {validate_config()}")
