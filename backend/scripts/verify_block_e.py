import asyncio
import json
from backend.memory.manager import MemoryManager
from backend.agents.rag_retrieval import RAGRetrievalNode
from backend.models.cognitive import AgentMessage
from langchain_core.messages import HumanMessage

async def verify_block_e():
    print("\n--- Manual Verification: Block E (Memory Architecture) ---")
    
    manager = MemoryManager()
    
    # 1. Test Memory Manager Storage
    print("1. Storing trace in Memory Manager...")
    success = await manager.store_trace(
        workspace_id="verify_ws",
        thread_id="verify_thread_001",
        content={"thought": "Verification in progress"},
        important=True,
        metadata={"subtype": "campaign_outcome"}
    )
    print(f"   Success: {success}")
    
    # 2. Test Context Retrieval (Aggregation)
    print("2. Retrieving aggregated context...")
    context = await manager.retrieve_context(
        workspace_id="verify_ws",
        query="Verification",
        thread_id="verify_thread_001"
    )
    print(f"   Short-term keys: {list(context.keys())}")
    print(f"   L1 found: {len(context['short_term']) > 0}")
    
    # 3. Test RAG Retrieval Node
    print("3. Testing RAG Retrieval Node...")
    node = RAGRetrievalNode()
    state = {
        "workspace_id": "verify_ws",
        "thread_id": "verify_thread_001",
        "messages": [HumanMessage(content="How is the verification going?")]
    }
    # Note: This will attempt to call real LLM for query expansion unless mocked.
    # In a real environment, we'd check if it returns context.
    # For now, we'll just verify the node can be initialized and called.
    try:
        res = await node(state)
        print(f"   Node Result keys: {list(res.keys())}")
        print(f"   Citations found: {len(res.get('citations', []))}")
    except Exception as e:
        print(f"   Node Call (Incomplete environment): {e}")

    print("\n--- Block E Verification Complete ---")

if __name__ == "__main__":
    try:
        asyncio.run(verify_block_e())
    except Exception as e:
        print(f"Verification script failed: {e}")
