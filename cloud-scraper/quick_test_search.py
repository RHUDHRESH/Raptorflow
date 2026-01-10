"""
Quick Test Free Web Search Service
Minimal test to verify functionality
"""

import asyncio

from free_web_search import free_search_engine


async def quick_test():
    print("🔍 Quick Test: Free Web Search")
    print("=" * 40)

    try:
        result = await free_search_engine.search(
            query="python scraping", engines=["duckduckgo"], max_results=3
        )

        print(f"✅ Status: {result.get('engines_used', [])}")
        print(f"📊 Results: {result.get('total_results', 0)}")
        print(f"⏱️  Time: {result.get('processing_time', 0):.2f}s")

        if result.get("results"):
            for i, res in enumerate(result["results"][:2]):
                print(f"{i+1}. {res['title'][:50]}...")
                print(f"   Score: {res['relevance_score']:.2f}")

        print("\n🎉 Free search working!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await free_search_engine.close()


if __name__ == "__main__":
    asyncio.run(quick_test())
