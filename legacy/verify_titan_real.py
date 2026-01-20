import asyncio
import os
import json
from backend.services.titan.orchestrator import TitanOrchestrator

async def main():
    print("🚀 Initializing Titan Real-World Verification...")
    
    # Ensure environment is set for local run
    os.environ["RAPTORFLOW_SKIP_INIT"] = "true"
    
    orchestrator = TitanOrchestrator()
    
    query = "Google Vertex AI Search features"
    
    print(f"\n1. Testing LITE Mode (Search Only) for: '{query}'")
    lite_result = await orchestrator.execute(query, mode="LITE", max_results=3)
    print(f"Count: {lite_result['count']}")
    for res in lite_result['results']:
        print(f" - [{res['source']}] {res['title']} ({res['url']})")

    print(f"\n2. Testing RESEARCH Mode (Multiplexed Search + Scrape) for: '{query}'")
    research_result = await orchestrator.execute(query, mode="RESEARCH", max_results=2)
    print(f"Count: {research_result['count']}")
    for res in research_result['results']:
        has_content = "Yes" if res.get("full_content") else "No"
        print(f" - {res['title']} | Scraped Content: {has_content}")
        if res.get("full_content"):
            print(f"   Content Preview: {res['full_content'][:150]}...")

    print(f"\n3. Testing DEEP Mode (Recursive Traversal) for: '{query}'")
    deep_result = await orchestrator.execute(query, mode="DEEP", max_results=2)
    print(f"Count: {deep_result['count']}")
    print(f"Recursive Pages Discovered: {len(deep_result.get('deep_research_data', []))}")
    for i, data in enumerate(deep_result.get('deep_research_data', [])):
        print(f" - Domain {i+1} Traversal: {len(data.get('urls_scraped', []))} pages scraped")

    await orchestrator.close()
    print("\n✅ Verification Complete.")

if __name__ == "__main__":
    asyncio.run(main())
