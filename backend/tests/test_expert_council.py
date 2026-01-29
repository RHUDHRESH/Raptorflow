"""
Unit test for Expert Council agentic system.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add root and backend to sys.path
root_path = str(Path(__file__).parent.parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

backend_path = str(Path(__file__).parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# SURGICAL ENV INJECTION
from dotenv import load_dotenv

load_dotenv()
if not os.getenv("VERTEX_AI_API_KEY"):
    # Attempt to find it manually in .env
    with open(Path(root_path) / ".env", "r") as f:
        for line in f:
            if "VERTEX_AI_API_KEY=" in line:
                os.environ["VERTEX_AI_API_KEY"] = line.split("=")[1].strip()
                print(
                    f"🚀 Surgically injected API Key from env (Length: {len(os.environ['VERTEX_AI_API_KEY'])})"
                )

from .services.expert_council import get_expert_council_swarm, create_swarm_session


async def test_council_session():
    print("🚀 Starting Expert Council SWARM Test Session...")

    swarm = get_expert_council_swarm()
    swarm.demo_mode = False  # FORCE REAL INFERENCE

    mission = "Refine the positioning for RaptorFlow to target Series A B2B SaaS founders. Use the Category Design and Moat Engineering protocols."
    workspace_context = {
        "company_name": "RaptorFlow",
        "industry": "Marketing Technology",
        "stage": "Growth",
        "target_market": "B2B SaaS",
    }

    state = create_swarm_session(mission, workspace_context)

    print(f"Mission: {mission}")
    print("-" * 50)

    # Run the graph
    result = await swarm.workflow.ainvoke(state)

    discussion = result["discussion"]

    print("\n--- DISCUSSION HISTORY ---")
    for contribution in discussion.contributions:
        print(f"\n[{contribution.agent_name} ({contribution.type})]:")
        print(contribution.content)
        print("-" * 20)

    print("\n--- FINAL REPORT ---")
    print(result["final_report"])

    print("\n✅ Test Session Complete.")


if __name__ == "__main__":
    asyncio.run(test_council_session())
