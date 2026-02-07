import pytest

pytest.skip(
    "Archived manual test script; use explicit run if needed.", allow_module_level=True
)

import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath("C:/Users/hp/OneDrive/Desktop/Raptorflow"))

# Set env var to skip auto-init
os.environ["RAPTORFLOW_SKIP_INIT"] = "true"

print("DEBUG: Starting imports...")
try:
    from agents.skills.registry import SkillsRegistry

    print("DEBUG: Imported SkillsRegistry")
    from agents.specialists.campaign_planner import CampaignPlanner

    print("DEBUG: Imported CampaignPlanner")
    from agents.specialists.social_media_agent import SocialMediaAgent

    print("DEBUG: Imported SocialMediaAgent")
    from agents.specialists.competitor_intel import CompetitorIntelAgent

    print("DEBUG: Imported CompetitorIntelAgent")
    from agents.specialists.icp_architect import ICPArchitect

    print("DEBUG: Imported ICPArchitect")
    from agents.specialists.analytics_agent import AnalyticsAgent

    print("DEBUG: Imported AnalyticsAgent")
except Exception as e:
    print(f"DEBUG: Import failed: {e}")
    sys.exit(1)


async def test_integration():
    print("Initializing Skills Registry...")
    registry = SkillsRegistry()

    print("\n--- Testing Agent Instantiation & Skill Access ---\n")

    agents_to_test = [
        ("CampaignPlanner", CampaignPlanner),
        ("SocialMediaAgent", SocialMediaAgent),
        ("CompetitorIntelAgent", CompetitorIntelAgent),
        ("ICPArchitect", ICPArchitect),
        ("AnalyticsAgent", AnalyticsAgent),
    ]

    for name, cls in agents_to_test:
        print(f"Testing {name}...")
        try:
            agent = cls()
            # Manually inject registry since we skipped system init
            agent.skills_registry = registry

            # Check for specific skills
            required_skills = {
                "CampaignPlanner": ["funnel_blueprint"],
                "SocialMediaAgent": ["social_pulse", "viral_hook"],
                "CompetitorIntelAgent": ["competitor_scout"],
                "ICPArchitect": ["persona_builder"],
                "AnalyticsAgent": ["forecast_oracle"],
            }

            missing = []
            for skill_id in required_skills.get(name, []):
                skill = registry.get_skill(skill_id)
                if skill:
                    print(f"  [✓] Found skill: {skill_id}")
                else:
                    print(f"  [X] Missing skill: {skill_id}")
                    missing.append(skill_id)

            if not missing:
                print(f"  > {name} integration verified.")
            else:
                print(f"  > {name} missing skills: {missing}")

        except Exception as e:
            print(f"  [!] Failed to instantiate {name}: {e}")
        print("-" * 30)


if __name__ == "__main__":
    asyncio.run(test_integration())
