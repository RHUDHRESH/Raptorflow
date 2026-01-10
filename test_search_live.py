import asyncio

from backend.core.search_native import NativeSearch


async def test():
    search = NativeSearch()
    queries = ["ice cream", "ducks", "polar bears"]

    print("🚀 INITIALIZING RAPTOR SEARCH TEST...")

    for q in queries:
        print(f"\n--- RESULTS FOR: {q.upper()} ---")
        results = await search.query(q, limit=2)

        if not results:
            print("❌ No results found (check internet connection).")
        else:
            for i, res in enumerate(results, 1):
                print(f"{i}. {res['title']}")
                print(f"   URL: {res['url']}")
                print(f"   SNIPPET: {res['snippet'][:150]}...")
                print("-" * 10)

    await search.close()


if __name__ == "__main__":
    asyncio.run(test())
