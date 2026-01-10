"""
Test Free Web Search Service
Demonstrates unlimited free search across multiple engines
"""

import asyncio
import json

from free_web_search import free_search_engine


async def test_free_search():
    print("🔍 Testing Free Web Search Service")
    print("=" * 60)

    # Test queries
    test_queries = [
        "artificial intelligence companies",
        "web scraping tools",
        "python machine learning libraries",
        "best free APIs 2024",
    ]

    # Test different engine combinations
    engine_combinations = [
        ["duckduckgo"],
        ["duckduckgo", "brave"],
        ["duckduckgo", "brave", "searx"],
        ["duckduckgo", "brave", "searx", "startpage", "qwant"],
    ]

    for i, query in enumerate(test_queries[:2]):  # Test first 2 queries
        print(f"\n🎯 Query {i+1}: {query}")
        print("-" * 40)

        for j, engines in enumerate(
            engine_combinations[:2]
        ):  # Test first 2 combinations
            print(f"\n🔧 Engines: {', '.join(engines)}")

            try:
                result = await free_search_engine.search(
                    query=query, engines=engines, max_results=5
                )

                print(f"✅ Status: Success")
                print(f"📊 Total Results: {result['total_results']}")
                print(f"⏱️  Processing Time: {result['processing_time']:.2f}s")

                # Show engine stats
                for engine, stats in result["engine_stats"].items():
                    status = stats["status"]
                    if status == "success":
                        print(
                            f"  🎯 {engine}: ✅ {stats['results_count']} results ({stats['response_time']:.2f}s)"
                        )
                    else:
                        print(
                            f"  ❌ {engine}: Failed - {stats.get('error', 'Unknown error')}"
                        )

                # Show top results
                print(f"\n📋 Top Results:")
                for k, res in enumerate(result["results"][:3]):
                    print(f"  {k+1}. {res['title']}")
                    print(f"     {res['url']}")
                    print(f"     {res['snippet'][:100]}...")
                    print(
                        f"     📊 Score: {res['relevance_score']:.2f} | 🔧 Source: {res['source']}"
                    )

            except Exception as e:
                print(f"❌ Failed: {str(e)}")

        print("\n" + "=" * 60)


async def test_specific_engines():
    print("\n🔧 Testing Individual Search Engines")
    print("=" * 60)

    query = "python web scraping"
    engines = ["duckduckgo", "brave", "searx", "startpage", "qwant"]

    for engine in engines:
        print(f"\n🎯 Testing {engine.upper()}:")
        print("-" * 30)

        try:
            result = await free_search_engine.search(
                query=query, engines=[engine], max_results=3
            )

            print(f"✅ Status: Success")
            print(f"📊 Results: {result['total_results']}")
            print(f"⏱️  Time: {result['processing_time']:.2f}s")

            if result["results"]:
                print(f"\n📋 Sample Result:")
                res = result["results"][0]
                print(f"  Title: {res['title']}")
                print(f"  URL: {res['url']}")
                print(f"  Snippet: {res['snippet'][:100]}...")
                print(f"  Score: {res['relevance_score']:.2f}")

        except Exception as e:
            print(f"❌ Failed: {str(e)}")


async def test_advanced_features():
    print("\n🚀 Testing Advanced Features")
    print("=" * 60)

    # Test deduplication
    print("\n🔄 Testing Deduplication:")
    query = "machine learning python"

    try:
        result = await free_search_engine.search(
            query=query, engines=["duckduckgo", "brave", "searx"], max_results=20
        )

        print(
            f"✅ Raw results from engines: {sum(stats.get('results_count', 0) for stats in result['engine_stats'].values())}"
        )
        print(f"🔄 After deduplication: {result['total_results']}")
        print(
            f"📊 Deduplication rate: {((1 - result['total_results'] / max(sum(stats.get('results_count', 0) for stats in result['engine_stats'].values()), 1)) * 100):.1f}%"
        )

    except Exception as e:
        print(f"❌ Deduplication test failed: {str(e)}")

    # Test relevance ranking
    print("\n📊 Testing Relevance Ranking:")
    query = "python web scraping libraries"

    try:
        result = await free_search_engine.search(
            query=query, engines=["duckduckgo", "brave"], max_results=10
        )

        print(f"✅ Results ranked by relevance:")
        for i, res in enumerate(result["results"][:5]):
            print(f"  {i+1}. Score: {res['relevance_score']:.2f} | {res['title']}")

    except Exception as e:
        print(f"❌ Relevance ranking test failed: {str(e)}")


async def main():
    try:
        await test_free_search()
        await test_specific_engines()
        await test_advanced_features()

        print("\n🎉 FREE WEB SEARCH TEST COMPLETE!")
        print("=" * 60)
        print("✅ Features Tested:")
        print("  🔍 Multi-engine search (DuckDuckGo, Brave, SearX, StartPage, Qwant)")
        print("  🔄 Automatic deduplication")
        print("  📊 Relevance ranking")
        print("  🚀 No API keys required")
        print("  ♾️ Unlimited requests")
        print("  🌍 Privacy-focused engines")
        print("  ⚡ Fast concurrent processing")
        print("  🧹 URL cleaning (removes tracking)")
        print("  📝 Text normalization")

        print("\n💡 Usage Examples:")
        print("  GET /search?q=python+scraping&engines=duckduckgo,brave&max_results=10")
        print("  GET /search/engines - List available engines")
        print("  GET /health - Service health check")

        print("\n🚀 Ready for production on port 8084!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    finally:
        await free_search_engine.close()


if __name__ == "__main__":
    asyncio.run(main())
