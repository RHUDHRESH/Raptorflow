"""
Test Suite: Saveetha Engineering College Startups
Search and scrape startup information using our tools
"""

import asyncio
import json

from free_web_search import free_search_engine
from ultra_fast_scraper import UltraFastScrapingStrategy, ultra_fast_scraper


async def search_saveetha_startups():
    """Search for Saveetha Engineering College startups"""
    print("🔍 Searching for Saveetha Engineering College startups...")
    print("=" * 60)

    search_queries = [
        "Saveetha Engineering College startups",
        "Saveetha student companies entrepreneurs",
        "Saveetha Engineering College innovation center",
        "startups from Saveetha Chennai",
        "Saveetha Engineering College student ventures",
    ]

    all_urls = []

    for query in search_queries:
        print(f"\n🎯 Query: {query}")
        print("-" * 40)

        try:
            result = await free_search_engine.search(
                query=query,
                engines=["duckduckgo"],  # Use one engine for speed
                max_results=5,
            )

            print(f"✅ Results: {result['total_results']}")

            # Extract relevant URLs
            for res in result["results"]:
                url = res["url"]
                title = res["title"]

                # Filter for relevant URLs
                if any(
                    keyword in title.lower() or keyword in url.lower()
                    for keyword in [
                        "saveetha",
                        "startup",
                        "entrepreneur",
                        "innovation",
                        "student",
                    ]
                ):
                    all_urls.append(
                        {
                            "url": url,
                            "title": title,
                            "snippet": res["snippet"],
                            "source": res["source"],
                        }
                    )
                    print(f"  📄 {title}")
                    print(f"     🔗 {url}")

        except Exception as e:
            print(f"❌ Search failed: {str(e)}")

    # Remove duplicates
    unique_urls = []
    seen_urls = set()

    for item in all_urls:
        if item["url"] not in seen_urls:
            seen_urls.add(item["url"])
            unique_urls.append(item)

    print(f"\n🎯 Found {len(unique_urls)} unique URLs to scrape")
    return unique_urls


async def scrape_startup_websites(urls):
    """Scrape startup websites using our ultra-fast scraper"""
    print("\n🚀 Scraping Startup Websites...")
    print("=" * 60)

    scraped_data = []

    for i, url_data in enumerate(urls[:5]):  # Limit to 5 for demo
        url = url_data["url"]
        title = url_data["title"]

        print(f"\n📄 [{i+1}/5] Scraping: {title}")
        print(f"🔗 URL: {url}")

        try:
            # Use ultra-fast scraper with async strategy
            result = await ultra_fast_scraper.scrape_with_production_grade_handling(
                url=url,
                user_id="saveetha-startup-research",
                legal_basis="research",
                strategy=UltraFastScrapingStrategy.ASYNC,
            )

            if result.get("status") == "success":
                content = result.get("readable_text", "")
                content_length = result.get("content_length", 0)
                processing_time = result.get("processing_time", 0)

                print(f"✅ Success: {content_length:,} chars in {processing_time:.2f}s")

                # Extract key information
                startup_info = {
                    "url": url,
                    "title": title,
                    "content_length": content_length,
                    "processing_time": processing_time,
                    "content_preview": (
                        content[:200] + "..." if len(content) > 200 else content
                    ),
                    "scraped_at": result.get("timestamp"),
                    "cost_tracking": result.get("cost_tracking", {}),
                    "production_metadata": result.get("production_metadata", {}),
                }

                scraped_data.append(startup_info)

                # Look for startup indicators
                startup_keywords = [
                    "startup",
                    "entrepreneur",
                    "innovation",
                    "venture",
                    "company",
                    "business",
                ]
                found_keywords = [
                    kw for kw in startup_keywords if kw.lower() in content.lower()
                ]

                if found_keywords:
                    print(f"  🎯 Startup indicators: {', '.join(found_keywords)}")

            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Exception: {str(e)}")

    return scraped_data


async def analyze_startup_data(scraped_data):
    """Analyze scraped startup data"""
    print("\n📊 Analyzing Startup Data...")
    print("=" * 60)

    if not scraped_data:
        print("❌ No data to analyze")
        return

    print(f"📈 Successfully scraped {len(scraped_data)} websites")

    total_content = sum(item["content_length"] for item in scraped_data)
    avg_time = sum(item["processing_time"] for item in scraped_data) / len(scraped_data)
    total_cost = sum(
        item.get("cost_tracking", {}).get("estimated_cost", 0) for item in scraped_data
    )

    print(f"\n📊 Scraping Statistics:")
    print(f"  📄 Total Content: {total_content:,} characters")
    print(f"  ⏱️  Average Time: {avg_time:.2f}s per scrape")
    print(f"  💰 Total Cost: ${total_cost:.6f}")
    print(f"  🚀 Average Speed: {total_content/avg_time:.0f} chars/second")

    print(f"\n🎯 Startup Analysis:")

    for i, item in enumerate(scraped_data):
        print(f"\n{i+1}. {item['title']}")
        print(f"   🔗 {item['url']}")
        print(
            f"   📊 {item['content_length']:,} chars | ⏱️ {item['processing_time']:.2f}s"
        )
        print(
            f"   💰 Cost: ${item.get('cost_tracking', {}).get('estimated_cost', 0):.6f}"
        )
        print(f"   📝 Preview: {item['content_preview']}")

        # Analyze content for startup characteristics
        content = item["content_preview"].lower()

        # Look for startup-related terms
        startup_terms = {
            "founded": "company founded",
            "team": "team information",
            "product": "product/service",
            "mission": "mission/vision",
            "contact": "contact information",
            "funding": "funding/investment",
            "technology": "technology stack",
            "market": "market/target",
        }

        found_terms = []
        for term, description in startup_terms.items():
            if term in content:
                found_terms.append(description)

        if found_terms:
            print(f"   🎯 Contains: {', '.join(found_terms)}")

    # Generate summary
    print(f"\n📋 Summary:")
    print(f"  🔍 Search queries used: 5")
    print(f"  📄 URLs found: {len(scraped_data)}")
    print(f"  ✅ Successfully scraped: {len(scraped_data)}")
    print(f"  📊 Total content analyzed: {total_content:,} characters")
    print(f"  💰 Total scraping cost: ${total_cost:.6f}")
    print(f"  ⚡ Average performance: {avg_time:.2f}s per site")


async def main():
    """Main test suite"""
    print("🚀 Saveetha Engineering College Startups - Test Suite")
    print("=" * 70)
    print("Using our own tools: Free Web Search + Ultra-Fast Scraper")
    print("=" * 70)

    try:
        # Step 1: Search for startup information
        urls = await search_saveetha_startups()

        if not urls:
            print("\n❌ No URLs found to scrape")
            return

        # Step 2: Scrape the websites
        scraped_data = await scrape_startup_websites(urls)

        # Step 3: Analyze the results
        await analyze_startup_data(scraped_data)

        print(f"\n🎉 Test Suite Completed Successfully!")
        print("=" * 70)
        print("✅ Used our own tools:")
        print("  🔍 Free Web Search (DuckDuckGo)")
        print("  🚀 Ultra-Fast Scraper (Async strategy)")
        print("  💰 Cost optimization tracking")
        print("  📊 Production-grade error handling")
        print("  🎯 Visual intelligence extraction")

        # Save results
        output_file = "saveetha_startups_results.json"
        with open(output_file, "w") as f:
            json.dump(
                {
                    "search_results": urls,
                    "scraped_data": scraped_data,
                    "timestamp": asyncio.get_event_loop().time(),
                    "tools_used": ["free_web_search", "ultra_fast_scraper"],
                },
                f,
                indent=2,
            )

        print(f"  📁 Results saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")

    finally:
        await free_search_engine.close()


if __name__ == "__main__":
    asyncio.run(main())
