"""
MASTER DURESS TEST - RaptorFlow Systems
Puts every agent and service under extreme pressure.
"""

import asyncio
import json
import logging
from datetime import datetime

# Import Agents
from backend.agents.specialists.brand_audit_agent import BrandAuditEngine
from backend.agents.specialists.buying_process_agent import BuyingProcessArchitect
from backend.agents.specialists.capability_rating_agent import CapabilityRatingEngine
from backend.agents.specialists.category_advisor import CategoryAdvisor
from backend.agents.specialists.comparative_angle_agent import ComparativeAngleGenerator
from backend.agents.specialists.contradiction_detector import ContradictionDetector
from backend.agents.specialists.focus_sacrifice_engine import FocusSacrificeEngine
from backend.agents.specialists.icp_deep_generator import ICPDeepGenerator
from backend.agents.specialists.message_hierarchy_agent import MessageHierarchyArchitect
from backend.agents.specialists.messaging_rules_engine import MessagingRulesEngine
from backend.agents.specialists.perceptual_map_generator import PerceptualMapGenerator
from backend.agents.specialists.positioning_statement_generator import (
    PositioningStatementGenerator,
)
from backend.agents.specialists.pricing_optimization_agent import (
    PricingOptimizationAgent,
)
from backend.agents.specialists.soundbites_generator import SoundbitesGenerator
from backend.agents.specialists.strategic_grid_agent import StrategicGridGenerator
from backend.agents.specialists.truth_sheet_generator import TruthSheetGenerator
from backend.services.audit_service import audit_service
from backend.services.automation_service import automation_service
from backend.services.brand_voice_service import brand_voice_service
from backend.services.brief_service import brief_service
from backend.services.coaching_service import coaching_service

# Import Services
from backend.services.crm_service import crm_service
from backend.services.repurposing_service import PlatformType, repurposing_service
from backend.services.seo_service import seo_service

logging.basicConfig(level=logging.ERROR)


async def stress_test_agent(name, agent, state):
    print(f"Testing Agent: {name}...")
    try:
        res = await agent.execute(state)
        print(f"  [OK] {name} responded.")
        return True
    except Exception as e:
        print(f"  [FAIL] {name} crashed under duress: {str(e)}")
        return False


async def stress_test_service(name, coro):
    print(f"Testing Service: {name}...")
    try:
        res = await coro
        print(f"  [OK] {name} completed.")
        return True
    except Exception as e:
        print(f"  [FAIL] {name} failed: {str(e)}")
        return False


async def run_master_duress():
    print("=== BEGINNING MASTER DURESS TEST ===")

    # 1. Chaos State (Messy Context)
    chaos_state = {
        "ucid": "RF-CHAOS-999",
        "business_context": {
            "identity": {
                "company_name": "",
                "industry": "None",
                "mission": "To make things and stuff.",
            },
            "positioning": {"differentiator": "None"},
        },
        "step_data": {"auto_extraction": {"facts": []}, "truth_sheet": {"entries": []}},
    }

    # 2. Agent Gauntlet
    agents = [
        ("BrandAudit", BrandAuditEngine()),
        ("Pricing", PricingOptimizationAgent()),
        ("Contradiction", ContradictionDetector()),
        ("TruthSheet", TruthSheetGenerator()),
        ("Comparative", ComparativeAngleGenerator()),
        ("Category", CategoryAdvisor()),
        ("Capability", CapabilityRatingEngine()),
        ("Perceptual", PerceptualMapGenerator()),
        ("StrategicGrid", StrategicGridGenerator()),
        ("Positioning", PositioningStatementGenerator()),
        ("FocusSacrifice", FocusSacrificeEngine()),
        ("ICP", ICPDeepGenerator()),
        ("BuyingProcess", BuyingProcessArchitect()),
        ("MessagingRules", MessagingRulesEngine()),
        ("Soundbites", SoundbitesGenerator()),
        ("Hierarchy", MessageHierarchyArchitect()),
    ]

    for name, agent in agents:
        await stress_test_agent(name, agent, chaos_state)

    # 3. Service Stress (Malformed Inputs)
    print("\n--- SERVICE STRESS ---")

    services = [
        (
            "CRM Personalize",
            crm_service.personalize_content(
                "", {"name": "Test", "company": "TestCorp", "title": "Tester"}
            ),
        ),
        (
            "Repurpose",
            repurposing_service.repurpose_content("junk text", PlatformType.TWITTER),
        ),
        (
            "Voice Analysis",
            brand_voice_service.analyze_brand_voice(["sample 1"], "test-user"),
        ),
        ("Content Audit", audit_service.audit_content_library([], ["Win everything"])),
        ("SEO Optimize", seo_service.optimize_content("spam spam spam", ["keyword"])),
        ("Brief Gen", brief_service.generate_brief("", {})),
        ("Automation", automation_service.create_content_sequence("Do a flip")),
        ("Coaching", coaching_service.get_strategic_critique("Bad content", {})),
    ]

    for name, coro in services:
        await stress_test_service(name, coro)

    print("\n=== MASTER DURESS TEST COMPLETE ===")


if __name__ == "__main__":
    asyncio.run(run_master_duress())
