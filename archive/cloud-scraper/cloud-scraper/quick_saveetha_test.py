"""
Quick Test: Saveetha Engineering College Startups
Fast search and scrape using our tools
"""

import asyncio

from free_web_search import free_search_engine


async def quick_test():
    print("🔍 Quick Test: Saveetha Engineering College Startups")
    print("=" * 50)

    try:
        # Simple search
        result = await free_search_engine.search(
            query="Saveetha Engineering College startups",
            engines=["duckduckgo"],
            max_results=3,
        )

        print(f"✅ Search completed")
        print(f"📊 Results: {result['total_results']}")
        print(f"⏱️  Time: {result['processing_time']:.2f}s")

        print(f"\n📋 Top Results:")
        for i, res in enumerate(result["results"][:3]):
            print(f"{i+1}. {res['title'][:50]}...")
            print(f"   🔗 {res['url']}")
            print(f"   📊 Score: {res['relevance_score']:.2f}")

        # Show URLs for scraping
        urls = [res["url"] for res in result["results"][:2]]
        print(f"\n🎯 URLs ready for scraping: {len(urls)}")
        for i, url in enumerate(urls):
            print(f"{i+1}. {url}")

        print(f"\n🚀 Ready to scrape with ultra_fast_scraper!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    finally:
        await free_search_engine.close()


if __name__ == "__main__":
    asyncio.run(quick_test())
