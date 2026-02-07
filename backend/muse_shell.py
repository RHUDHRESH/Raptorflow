import asyncio
import logging

from dotenv import load_dotenv

from backend.graphs.spine_v3 import build_ultimate_spine

# 1. Load Environment (Supabase, Vertex, Upstash)
load_dotenv()

# Configure logging to see the inner monologue of the agents
logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
logger = logging.getLogger("muse_shell")


async def run_muse():
    print("\n" + "X" * 60)
    print("   MUSE SOTA FORTRESS - INTERACTIVE SHELL")
    print("X" * 60 + "\n")

    # 2. Build the Real Graph
    logger.info("Initializing Agent Spine...")
    app = build_ultimate_spine()

    # 3. Interactive Loop
    while True:
        user_input = input("\n[USER] Enter your marketing goal (or 'quit'): ")
        if user_input.lower() in ["quit", "exit"]:
            break

        print("\n[AI] Muse is engaging the Fortress crews...")

        config = {"configurable": {"thread_id": "shell_session_1"}}

        # SOTA: Execute the graph
        # Note: This will perform REAL LLM and Tool calls if API keys are set!
        try:
            async for output in app.astream({"raw_prompt": user_input}, config=config):
                # Print the node that just finished
                for node_name, result in output.items():
                    print(f"\n--- Node '{node_name}' Finished ---")
                    if "status" in result:
                        print(f"Status: {result['status']}")
                    if "current_draft" in result:
                        print(
                            f"Latest Draft Preview:\n{result['current_draft'][:200]}..."
                        )
        except Exception as e:
            print(f"\n[ERROR] The Fortress encountered an issue: {e}")
            logger.error(e, exc_info=True)

    print("\nShutting down Muse. Fortress remains active.")


if __name__ == "__main__":
    asyncio.run(run_muse())
