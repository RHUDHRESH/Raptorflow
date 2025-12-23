import asyncio

from backend.graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator


async def demo():
    config = {"configurable": {"thread_id": "demo-thread-1"}}
    initial_state = {"tenant_id": "demo-tenant", "messages": [], "status": "new"}

    print("\n--- Starting Cognitive Spine Demo ---")
    async for event in moves_campaigns_orchestrator.astream(initial_state, config):
        for node, values in event.items():
            print(f"\nNode: {node}")
            if "messages" in values:
                print(f"Messages: {values['messages']}")

    state = await moves_campaigns_orchestrator.aget_state(config)
    print(f"\nNext expected node: {state.next}")

    if "approve_campaign" in state.next:
        print("\n[HITL] Interrupted for Campaign Approval. Resuming now...")
        # In a real app, this would wait for user input. Here we just resume.
        async for event in moves_campaigns_orchestrator.astream(None, config):
            for node, values in event.items():
                print(f"\nNode: {node}")
                if "messages" in values:
                    print(f"Messages: {values['messages']}")

    print("\n--- Demo Complete ---")


if __name__ == "__main__":
    asyncio.run(demo())
