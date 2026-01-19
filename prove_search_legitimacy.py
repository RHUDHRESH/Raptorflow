import asyncio
import os
import sys
from datetime import datetime

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Mock env for testing
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["VERTEX_AI_PROJECT_ID"] = "test-project"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["WEBHOOK_SECRET"] = "test-webhook-secret"
os.environ["SEARXNG_URL"] = "http://localhost:8080"

from backend.services.search.orchestrator import SOTASearchOrchestrator

async def prove_legitimacy():
    # Query 1: Basic Definition
    # Query 2: Something extremely current (Today's hours or weather at the tower)
    queries = [
        "What is the Eiffel Tower official definition",
        "Eiffel Tower opening hours today January 19 2026"
    ]
    
    orchestrator = SOTASearchOrchestrator()
    print(f"🕵️  LEGITIMACY CHECK: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    try:
        for q in queries:
            print(f"🔍 MACHINE QUERY: '{q}'")
            results = await orchestrator.query(q, limit=3)
            
            if not results:
                print("❌ No results retrieved.")
            else:
                for res in results:
                    print(f"   - [{res.get('source')}] {res.get('title')}")
                    print(f"     LINK: {res.get('url')}")
                    print(f"     SNIPPET: {res.get('snippet')[:160]}...")
            print("-" * 60)
                
    except Exception as e:
        print(f"💥 Error: {str(e)}")
    finally:
        await orchestrator.close()

if __name__ == "__main__":
    asyncio.run(prove_legitimacy())
