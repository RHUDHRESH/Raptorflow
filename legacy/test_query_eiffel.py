import asyncio
import os
import sys
import json

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Mock env for testing
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["VERTEX_AI_PROJECT_ID"] = "test-project"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["WEBHOOK_SECRET"] = "test-webhook-secret"

from backend.services.search.orchestrator import SOTASearchOrchestrator

async def test_eiffel_query():
    query = "Eiffel Tower and resulting marketing strategy"
    print(f"🚀 Machine Query: '{query}'")
    print("-" * 50)
    
    orchestrator = SOTASearchOrchestrator()
    try:
        results = await orchestrator.query(query, limit=5)
        
        if not results:
            print("❌ No results found. (Check if SearXNG cluster is active)")
        else:
            for i, res in enumerate(results):
                print(f"[{i+1}] {res.get('title')}")
                print(f"    Source: {res.get('source')}")
                print(f"    URL:    {res.get('url')}")
                print(f"    Snippet: {res.get('snippet')[:150]}...")
                print("-" * 30)
                
    except Exception as e:
        print(f"💥 Machine Error: {str(e)}")
    finally:
        await orchestrator.close()

if __name__ == "__main__":
    asyncio.run(test_eiffel_query())
