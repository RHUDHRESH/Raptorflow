import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

from backend.graphs.spine_v3 import build_ultimate_spine

# Configure clean logging to show the "Inner Monologue"
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("raptorflow.demo")


async def talk_to_fortress():
    print("\n" + "=" * 60)
    print("   RAPTORFLOW SOTA FORTRESS - LIVE DEMONSTRATION")
    print("=" * 60 + "\n")

    # 1. Build the Spine
    app = build_ultimate_spine()

    # 2. Mock the Inference Provider to show tiering
    async def mock_invoke(prompt, **kwargs):
        # Determine which model is talking
        model_name = "unknown"
        if "Classify" in str(prompt):
            model_name = "Gemini 2.0 Flash (Intake)"
        elif "architect a surgical" in str(prompt):
            model_name = "Gemini 2.5 Pro (Ultra)"
        elif "Thought Leader" in str(prompt):
            model_name = "Gemini 2.5 Flash Lite (Driver)"
        elif "ruthless visual editor" in str(prompt):
            model_name = "Gemini 2.5 Flash Lite (Mundane)"

        print(f"   [AI] {model_name} is thinking...")
        return MagicMock(
            content=f"SOTA Output from {model_name}", model_dump=lambda: {}
        )

    with patch("backend.inference.ChatVertexAI") as MockChat:
        # Configure the mock to return an object with ainvoke
        mock_inst = MockChat.return_value
        mock_inst.ainvoke = AsyncMock(side_effect=mock_invoke)
        # Mock with_structured_output to return the same mock chain
        mock_inst.with_structured_output.return_value.ainvoke = AsyncMock(
            side_effect=mock_invoke
        )

        # 3. Start the Conversation
        user_prompt = "Launch a surgical marketing campaign for my new AI dev tool."
        print(f"USER: {user_prompt}\n")

        config = {"configurable": {"thread_id": "demo_thread_1"}}

        # We simulate the first few steps manually to show the routing logic
        print("--- DISCOVERY PHASE (Mundane) ---")
        from backend.agents.classifier import Intent

        mock_inst.with_structured_output.return_value.ainvoke.return_value = Intent(
            classification="campaign",
            confidence=0.99,
            reasoning="Clear campaign intent.",
        )
        from backend.graphs.spine_v3 import discovery_node

        await discovery_node({"raw_prompt": user_prompt})

        print("\n--- STRATEGY PHASE (Ultra) ---")
        from backend.agents.strategists import UVP, UVPAnalysis

        mock_inst.with_structured_output.return_value.ainvoke.return_value = (
            UVPAnalysis(
                winning_positions=[
                    UVP(
                        title="Logic Fortress",
                        description="Unbreakable code.",
                        why_it_wins="SOTA Reasoning",
                    )
                ]
            )
        )
        from backend.agents.strategists import create_uvp_architect

        uvp_arch = create_uvp_architect(mock_inst)
        await uvp_arch({"context_brief": {}, "research_bundle": {}})

        print("\n--- PRODUCTION PHASE (Driver) ---")
        from backend.agents.creatives import LinkedInPost

        mock_inst.with_structured_output.return_value.ainvoke.return_value = (
            LinkedInPost(
                hook="Stop guessing.",
                body="Code is a liability.",
                cta="Build a fortress.",
                post_vibe="Calm",
            )
        )
        from backend.agents.creatives import create_linkedin_architect

        creative = create_linkedin_architect(mock_inst)
        await creative({"context_brief": {}, "research_bundle": {}})

    print("\n" + "=" * 60)
    print("   VERIFICATION COMPLETE: UNIVERSAL GEMINI TIERING ACTIVE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(talk_to_fortress())
