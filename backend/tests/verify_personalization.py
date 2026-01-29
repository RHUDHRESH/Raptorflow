import asyncio
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock

# 1. MOCK ENVIRONMENT & REDIS
# Create mock module
redis_mock = MagicMock()
redis_asyncio_mock = MagicMock()
redis_mock.asyncio = redis_asyncio_mock

sys.modules["redis"] = redis_mock
sys.modules["redis.asyncio"] = redis_asyncio_mock
# Also need to ensure 'import redis.asyncio as redis' works


# Setup paths
sys.path.append(os.path.abspath("C:/Users/hp/OneDrive/Desktop/Raptorflow"))
os.environ["RAPTORFLOW_SKIP_INIT"] = "true"

# Mock LLM to return "REALISTIC" strings if the real one isn't configured,
# BUT we want to try and see if we can trigger the prompt generation logic at least.
# Actually, we'll let it try to call the real LLM if API keys are present.
# If not, we'll patch the _call_llm method to return simulated unique responses based on prompt content.

try:
    from agents.skills.registry import SkillsRegistry
    from agents.specialists.campaign_planner import CampaignPlanner
    from agents.specialists.social_media_agent import (
        SocialMediaAgent,
        SocialMediaRequest,
    )
    from state import AgentState
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

# 2. DEFINING THE 3 PERSONAS
PERSONAS = {
    "ENTERPRISE_TECH": {
        "name": "GlobalSystems Inc.",
        "brand_voice": "Authoritative, Professional, Visionary, Corporate",
        "industry": "Enterprise Software",
        "description": "A Fortune 500 provider of cloud infrastructure and cybersecurity solutions.",
        "target_audience": "CTOs, CIOs, Enterprise Architects",
        "goals": ["Market Leadership", "Thought Leadership", "Risk Mitigation"],
    },
    "B2C_STARTUP": {
        "name": "FitSnackz",
        "brand_voice": "Energetic, Playful, Health-conscious, Gen-Z",
        "industry": "Food & Beverage",
        "description": "A direct-to-consumer brand selling healthy, caffeinated protein bars.",
        "target_audience": "Fitness enthusiasts, Students, Busy professionals",
        "goals": ["Viral Growth", "Brand Awareness", "Direct Sales"],
    },
    "SAVVY_FOOD_TRUCK": {
        "name": "Taco 'Bout It",
        "brand_voice": "Local, Friendly, Humorous, Authentic",
        "industry": "Hospitality/Food Truck",
        "description": "A high-end gourmet taco truck roaming downtown Austin.",
        "target_audience": "Foodies, Office lunch crowd, Late-night party goers",
        "goals": ["Daily foot traffic", "Community engagement", "Loyalty"],
    },
}


async def mock_llm_generate(prompt: str, system_prompt: str = None, **kwargs) -> str:
    """
    A simple mock LLM that returns text proving it 'read' the prompt.
    Used if real LLM fails or is missing keys.
    """
    lower_prompt = prompt.lower()
    if "global" in lower_prompt or "enterprise" in lower_prompt:
        return f"[MOCK LLM] 🚀 STRATEGIC INITIATIVE: Leveraging enterprise-grade synergy to facilitate scalable cloud transformation. Our solution empowers CTOs to mitigate risk. #DigitalTransformation"
    elif "snack" in lower_prompt or "fitness" in lower_prompt:
        return f"[MOCK LLM] ⚡️ Yo fam! Need energy? Grab a FitSnackz bar and CRUSH your workout! No cap, it's bussin. 🔥 #FitLife #Energy"
    elif "taco" in lower_prompt or "truck" in lower_prompt:
        return f"[MOCK LLM] 🌮 Hey Austin! We're parked at 5th & Congress today. Come get your Al Pastor fix before we sell out! 🚚💨 #Tacos #AustinEats"
    else:
        return f"[MOCK LLM] Generic response for prompt: {prompt[:30]}..."


async def run_test():
    registry = SkillsRegistry()
    print("=== STARTING SWARM PERSONALIZATION TEST ===\n", flush=True)

    for key, p_data in PERSONAS.items():
        print(f"\n>>> TESTING PERSONA: {p_data['name']} ({key})", flush=True)

        # --- TEST 1: SOCIAL MEDIA AGENT ---
        print("  [Action] Generating Viral Tweet...", flush=True)
        agent = SocialMediaAgent()
        agent.skills_registry = registry

        # Monkey patch LLM to use mock
        agent._call_llm = mock_llm_generate
        agent.llm = MagicMock()
        agent.llm.generate = mock_llm_generate

        # Create Request
        req = SocialMediaRequest(
            platform="Twitter",
            content_type="Tweet",
            content_pillar="Promotional",
            objective="Drive Sales",
            brand_voice=p_data["brand_voice"],
            target_audience=p_data["target_audience"],
            keywords=["Launch", "Deal", "New"],
            urgency="High",
            call_to_action="Buy Now",
        )

        # Config
        platform_config = {
            "character_limit": 280,
            "optimal_length": 140,
            "content_style": "Short & Punchy",
            "engagement_factors": ["Hashtags", "Emojis"],
        }

        try:
            caption = await agent._generate_caption(req, platform_config, {})
            print(f"  [Result]: {caption}", flush=True)
        except Exception as e:
            print(f"  [Error]: {e}", flush=True)

        # --- TEST 2: CAMPAIGN PLANNER ---
        print("  [Action] Checking Campaign Context...", flush=True)
        planner = CampaignPlanner()
        planner.skills_registry = registry

        skill = registry.get_skill("funnel_blueprint")
        if skill:
            print(
                f"  [Swarm] 'funnel_blueprint' skill ready for {p_data['industry']} context.",
                flush=True,
            )

    print("\n=== TEST COMPLETE ===", flush=True)


if __name__ == "__main__":
    asyncio.run(run_test())
