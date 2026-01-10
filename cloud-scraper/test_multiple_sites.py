"""
Multi-Site Test Script - Test Ultra-Fast Scraper on Multiple Websites
"""

import asyncio
import json

from ultra_fast_scraper import UltraFastScrapingStrategy, ultra_fast_scraper


async def test_multiple_sites():
    print("🚀 Testing Ultra-Fast Scraper on Multiple Websites")
    print("=" * 60)

    # Test sites
    sites = [
        {
            "name": "PepsiCo",
            "url": "https://www.pepsico.com/en/",
            "description": "Beverage and food company",
        },
        {
            "name": "McDonald's",
            "url": "https://www.mcdonalds.com/us/en-us.html",
            "description": "Fast food restaurant chain",
        },
        {
            "name": "Intecalic",
            "url": "https://intecalic.com/",
            "description": "Technology company",
        },
        {
            "name": "Ausdauer Groups",
            "url": "https://www.ausdauergroups.in/",
            "description": "Business group website",
        },
    ]

    # Use async strategy for maximum speed
    strategy = UltraFastScrapingStrategy.ASYNC

    results = {}

    for site in sites:
        print(f'\n🎯 Scraping {site["name"]} ({site["url"]})')
        print("-" * 50)

        try:
            start_time = asyncio.get_event_loop().time()

            result = await ultra_fast_scraper.scrape_with_ultra_speed(
                url=site["url"],
                user_id=f'test-user-{site["name"].lower().replace(" ", "-")}',
                legal_basis="research",
                strategy=strategy,
            )

            end_time = asyncio.get_event_loop().time()
            total_time = end_time - start_time

            results[site["name"]] = {
                "result": result,
                "total_time": total_time,
                "site_info": site,
            }

            print(f'✅ Status: {result.get("status", "unknown")}')
            print(f'⏱️  Processing Time: {result.get("processing_time", 0):.2f}s')
            print(f"🕐 Total Time: {total_time:.2f}s")

            if result.get("status") == "success":
                content_length = result.get("content_length", 0)
                readable_text = result.get("readable_text", "")
                title = result.get("title", "No title")
                links = result.get("links", [])

                print(f"📄 Title: {title}")
                print(f"📏 Content Length: {content_length:,} characters")
                print(f"📖 Readable Text: {len(readable_text):,} characters")
                print(f"🔗 Links Found: {len(links)}")

                # Show ultra performance metrics
                if "ultra_performance" in result:
                    perf = result["ultra_performance"]
                    print(f'⚡ Speed Score: {perf.get("speed_score", 0):.1f}')

                # Show cost tracking
                if "ultra_cost" in result:
                    cost = result["ultra_cost"]
                    print(f'💰 Cost: ${cost.get("estimated_cost", 0):.6f}')
                    print(
                        f'📈 Speed Improvement: {cost.get("speed_improvement", 0):.1f}%'
                    )

                # Extract key information
                print(f"\n📋 KEY INFORMATION:")

                # Extract company description from text
                if readable_text:
                    # Look for common description patterns
                    text_lower = readable_text.lower()

                    # Company description
                    desc_patterns = [
                        "about us",
                        "who we are",
                        "our company",
                        "we are",
                        "we provide",
                        "we offer",
                        "specializes in",
                        "focused on",
                    ]

                    description_found = False
                    for pattern in desc_patterns:
                        if pattern in text_lower:
                            # Extract a snippet around this pattern
                            pattern_pos = text_lower.find(pattern)
                            if pattern_pos != -1:
                                start = max(0, pattern_pos - 50)
                                end = min(len(readable_text), pattern_pos + 200)
                                snippet = (
                                    readable_text[start:end].replace("\n", " ").strip()
                                )
                                print(f"  📝 {pattern.title()}: {snippet}...")
                                description_found = True
                                break

                    if not description_found:
                        # Use first paragraph as description
                        first_para = (
                            readable_text.split("\n\n")[0].replace("\n", " ").strip()
                        )
                        if len(first_para) > 50:
                            print(f"  📝 Description: {first_para[:200]}...")

                # Extract contact information
                if readable_text:
                    import re

                    # Email addresses
                    emails = re.findall(
                        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                        readable_text,
                    )
                    if emails:
                        print(f"  📧 Emails: {emails[:3]}")  # Show first 3

                    # Phone numbers
                    phones = re.findall(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", readable_text)
                    if phones:
                        print(f"  📞 Phones: {phones[:3]}")  # Show first 3

                    # Social media links
                    social_links = [
                        link
                        for link in links
                        if any(
                            social in link["url"].lower()
                            for social in [
                                "facebook",
                                "twitter",
                                "linkedin",
                                "instagram",
                            ]
                        )
                    ]
                    if social_links:
                        print(f"  🌐 Social Media: {len(social_links)} links found")

                # Extract business categories
                if readable_text:
                    business_keywords = [
                        "technology",
                        "software",
                        "services",
                        "solutions",
                        "products",
                        "food",
                        "beverage",
                        "restaurant",
                        "hospitality",
                        "retail",
                        "manufacturing",
                        "industrial",
                        "automotive",
                        "healthcare",
                        "finance",
                        "banking",
                        "insurance",
                        "investment",
                        "consulting",
                    ]

                    found_keywords = [
                        kw for kw in business_keywords if kw in text_lower
                    ]
                    if found_keywords:
                        print(
                            f'  🏢 Business Categories: {", ".join(found_keywords[:5])}'
                        )

                # Extract key links
                if links:
                    important_links = links[:5]  # Show first 5 links
                    print(f"  🔗 Key Links:")
                    for link in important_links:
                        link_text = link.get("text", "No text")[:50]
                        link_url = link.get("url", "")
                        print(f"    • {link_text}: {link_url}")

            else:
                print(f'❌ Error: {result.get("error", "Unknown error")}')

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results[site["name"]] = {"error": str(e), "site_info": site}

    # Summary
    print(f"\n📊 MULTI-SITE SCRAPING SUMMARY")
    print("=" * 60)

    successful_sites = {
        k: v
        for k, v in results.items()
        if "result" in v and v["result"].get("status") == "success"
    }

    if successful_sites:
        print(f"✅ Successfully Scraped: {len(successful_sites)}/{len(sites)} sites")
        print(
            f'⏱️  Average Processing Time: {sum(v["result"].get("processing_time", 0) for v in successful_sites.values()) / len(successful_sites):.2f}s'
        )
        print(
            f'💰 Average Cost: ${sum(v["result"].get("ultra_cost", {}).get("estimated_cost", 0) for v in successful_sites.values()) / len(successful_sites):.6f}'
        )

        print(f"\n📋 SITE DETAILS:")
        for site_name, data in successful_sites.items():
            result = data["result"]
            site_info = data["site_info"]

            print(f'\n🏢 {site_name} ({site_info["description"]})')
            print(f'   📄 Title: {result.get("title", "No title")}')
            print(f'   📏 Content: {result.get("content_length", 0):,} chars')
            print(f'   ⏱️  Time: {result.get("processing_time", 0):.2f}s')
            print(
                f'   💰 Cost: ${result.get("ultra_cost", {}).get("estimated_cost", 0):.6f}'
            )

            # Key insights
            readable_text = result.get("readable_text", "")
            if readable_text:
                text_lower = readable_text.lower()

                # Extract main purpose
                purposes = {
                    "food & beverage": [
                        "food",
                        "beverage",
                        "restaurant",
                        "drink",
                        "snack",
                    ],
                    "technology": [
                        "technology",
                        "software",
                        "digital",
                        "tech",
                        "innovation",
                    ],
                    "manufacturing": [
                        "manufacturing",
                        "production",
                        "industrial",
                        "factory",
                    ],
                    "services": ["services", "solutions", "consulting", "professional"],
                    "retail": ["retail", "store", "shop", "consumer", "product"],
                }

                main_purpose = None
                for purpose, keywords in purposes.items():
                    if any(keyword in text_lower for keyword in keywords):
                        main_purpose = purpose
                        break

                if main_purpose:
                    print(f"   🎯 Main Purpose: {main_purpose.title()}")

                # Extract key features
                features = []
                if "global" in text_lower or "worldwide" in text_lower:
                    features.append("Global Presence")
                if "innov" in text_lower:
                    features.append("Innovation Focus")
                if "sustain" in text_lower:
                    features.append("Sustainability")
                if "quality" in text_lower:
                    features.append("Quality Focus")
                if "customer" in text_lower:
                    features.append("Customer Centric")

                if features:
                    print(f'   ⭐ Key Features: {", ".join(features)}')
    else:
        print(f"❌ No sites were successfully scraped")

    # Show failed sites
    failed_sites = {
        k: v
        for k, v in results.items()
        if "error" in v or ("result" in v and v["result"].get("status") != "success")
    }
    if failed_sites:
        print(f"\n❌ Failed Sites: {len(failed_sites)}")
        for site_name, data in failed_sites.items():
            site_info = data.get("site_info", {})
            error = data.get("error", "Unknown error")
            print(f"   • {site_name}: {error}")


if __name__ == "__main__":
    asyncio.run(test_multiple_sites())
