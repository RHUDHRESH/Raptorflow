"""
Complete Saveetha Engineering College Startups Analysis
Full search and scrape with comprehensive data extraction
"""

import asyncio
import json
from datetime import datetime, timezone

from free_web_search import free_search_engine
from ultra_fast_scraper import UltraFastScrapingStrategy, ultra_fast_scraper


async def comprehensive_saveetha_analysis():
    """Complete analysis of Saveetha Engineering College startups"""
    print("🚀 Complete Saveetha Engineering College Startups Analysis")
    print("=" * 70)

    # Initialize results structure
    analysis_results = {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_type": "comprehensive_startup_intelligence",
            "tools_used": ["free_web_search", "ultra_fast_scraper"],
            "target": "Saveetha Engineering College Startups",
        },
        "search_phase": {},
        "scraping_phase": {},
        "intelligence_analysis": {},
        "performance_metrics": {},
    }

    # Phase 1: Comprehensive Search
    print("\n🔍 PHASE 1: COMPREHENSIVE SEARCH")
    print("-" * 50)

    search_queries = [
        "Saveetha Engineering College startups",
        "Saveetha student companies entrepreneurs",
        "Saveetha Engineering College innovation center",
        "Saveetha Technology Business Incubator STBI",
        "Saveetha Engineering College alumni startups",
        "startups from Saveetha Chennai Tamil Nadu",
        "Saveetha Engineering College entrepreneurship development cell",
        "student ventures Saveetha University",
        "Saveetha innovation lab incubation",
        "successful companies Saveetha graduates",
    ]

    all_search_results = []
    search_stats = {
        "total_queries": len(search_queries),
        "successful_queries": 0,
        "total_results": 0,
        "engines_used": set(),
        "processing_time": 0,
    }

    for i, query in enumerate(search_queries):
        print(f"\n🎯 Query {i+1}/{len(search_queries)}: {query}")

        try:
            result = await free_search_engine.search(
                query=query, engines=["duckduckgo", "brave"], max_results=8
            )

            search_stats["successful_queries"] += 1
            search_stats["total_results"] += result["total_results"]
            search_stats["engines_used"].update(result["engines_used"])
            search_stats["processing_time"] += result["processing_time"]

            print(
                f"✅ Results: {result['total_results']} | Time: {result['processing_time']:.2f}s"
            )

            # Filter and store relevant results
            for res in result["results"]:
                if any(
                    keyword in res["title"].lower()
                    or keyword in res["snippet"].lower()
                    or keyword in res["url"].lower()
                    for keyword in [
                        "saveetha",
                        "startup",
                        "entrepreneur",
                        "innovation",
                        "incubator",
                        "student",
                    ]
                ):

                    all_search_results.append(
                        {
                            "query": query,
                            "title": res["title"],
                            "url": res["url"],
                            "snippet": res["snippet"],
                            "source": res["source"],
                            "relevance_score": res["relevance_score"],
                            "timestamp": res["timestamp"],
                        }
                    )

        except Exception as e:
            print(f"❌ Failed: {str(e)}")

    # Remove duplicates
    unique_results = []
    seen_urls = set()

    for result in all_search_results:
        if result["url"] not in seen_urls:
            seen_urls.add(result["url"])
            unique_results.append(result)

    search_stats["engines_used"] = list(search_stats["engines_used"])
    search_stats["unique_results"] = len(unique_results)

    analysis_results["search_phase"] = {
        "statistics": search_stats,
        "results": unique_results,
    }

    print(f"\n📊 Search Phase Summary:")
    print(
        f"  ✅ Queries processed: {search_stats['successful_queries']}/{search_stats['total_queries']}"
    )
    print(f"  📄 Unique results: {search_stats['unique_results']}")
    print(f"  🔧 Engines used: {', '.join(search_stats['engines_used'])}")
    print(f"  ⏱️  Total time: {search_stats['processing_time']:.2f}s")

    # Phase 2: Comprehensive Scraping
    print(f"\n🚀 PHASE 2: COMPREHENSIVE SCRAPING")
    print("-" * 50)

    # Select top URLs for scraping
    urls_to_scrape = unique_results[:8]  # Scrape top 8 most relevant

    scraped_data = []
    scraping_stats = {
        "total_urls": len(urls_to_scrape),
        "successful_scrapes": 0,
        "failed_scrapes": 0,
        "total_content": 0,
        "total_processing_time": 0,
        "total_cost": 0,
        "strategies_used": set(),
    }

    for i, url_data in enumerate(urls_to_scrape):
        url = url_data["url"]
        title = url_data["title"]

        print(f"\n📄 [{i+1}/{len(urls_to_scrape)}] Scraping: {title[:60]}...")
        print(f"🔗 URL: {url}")

        try:
            # Try async strategy first, fallback to others if needed
            strategies = [
                UltraFastScrapingStrategy.ASYNC,
                UltraFastScrapingStrategy.PARALLEL,
                UltraFastScrapingStrategy.TURBO,
            ]

            scrape_result = None
            strategy_used = None

            for strategy in strategies:
                try:
                    scrape_result = (
                        await ultra_fast_scraper.scrape_with_production_grade_handling(
                            url=url,
                            user_id="saveetha-comprehensive-analysis",
                            legal_basis="research",
                            strategy=strategy,
                        )
                    )
                    strategy_used = strategy.value
                    break
                except:
                    continue

            if scrape_result and scrape_result.get("status") == "success":
                content = scrape_result.get("readable_text", "")
                content_length = scrape_result.get("content_length", 0)
                processing_time = scrape_result.get("processing_time", 0)
                cost_data = scrape_result.get("cost_tracking", {})
                cost = cost_data.get("estimated_cost", 0)

                scraping_stats["successful_scrapes"] += 1
                scraping_stats["total_content"] += content_length
                scraping_stats["total_processing_time"] += processing_time
                scraping_stats["total_cost"] += cost
                scraping_stats["strategies_used"].add(strategy_used)

                print(
                    f"✅ Success: {content_length:,} chars in {processing_time:.2f}s ({strategy_used})"
                )
                print(f"💰 Cost: ${cost:.6f}")

                # Extract startup intelligence
                startup_intelligence = extract_startup_intelligence(content, title, url)

                scraped_item = {
                    "url": url,
                    "title": title,
                    "content_length": content_length,
                    "processing_time": processing_time,
                    "cost": cost,
                    "strategy_used": strategy_used,
                    "scraped_at": scrape_result.get("timestamp"),
                    "content_preview": (
                        content[:300] + "..." if len(content) > 300 else content
                    ),
                    "startup_intelligence": startup_intelligence,
                    "production_metadata": scrape_result.get("production_metadata", {}),
                    "search_relevance": url_data["relevance_score"],
                }

                scraped_data.append(scraped_item)

                # Show key findings
                if startup_intelligence["startup_indicators"]:
                    print(
                        f"🎯 Indicators: {', '.join(startup_intelligence['startup_indicators'][:3])}"
                    )

            else:
                scraping_stats["failed_scrapes"] += 1
                print(f"❌ Failed: All strategies exhausted")

        except Exception as e:
            scraping_stats["failed_scrapes"] += 1
            print(f"❌ Exception: {str(e)}")

    scraping_stats["strategies_used"] = list(scraping_stats["strategies_used"])

    if scraping_stats["successful_scrapes"] > 0:
        scraping_stats["avg_processing_time"] = (
            scraping_stats["total_processing_time"]
            / scraping_stats["successful_scrapes"]
        )
        scraping_stats["avg_cost_per_scrape"] = (
            scraping_stats["total_cost"] / scraping_stats["successful_scrapes"]
        )
        scraping_stats["chars_per_second"] = (
            scraping_stats["total_content"] / scraping_stats["total_processing_time"]
        )
    else:
        scraping_stats["avg_processing_time"] = 0
        scraping_stats["avg_cost_per_scrape"] = 0
        scraping_stats["chars_per_second"] = 0

    analysis_results["scraping_phase"] = {
        "statistics": scraping_stats,
        "scraped_data": scraped_data,
    }

    print(f"\n📊 Scraping Phase Summary:")
    print(
        f"  ✅ Successful: {scraping_stats['successful_scrapes']}/{scraping_stats['total_urls']}"
    )
    print(f"  📄 Total content: {scraping_stats['total_content']:,} chars")
    print(f"  ⏱️  Avg time: {scraping_stats['avg_processing_time']:.2f}s")
    print(f"  💰 Total cost: ${scraping_stats['total_cost']:.6f}")
    print(f"  ⚡ Speed: {scraping_stats['chars_per_second']:.0f} chars/s")

    # Phase 3: Intelligence Analysis
    print(f"\n🧠 PHASE 3: INTELLIGENCE ANALYSIS")
    print("-" * 50)

    intelligence_analysis = analyze_comprehensive_intelligence(
        scraped_data, unique_results
    )
    analysis_results["intelligence_analysis"] = intelligence_analysis

    # Phase 4: Performance Metrics
    print(f"\n📈 PHASE 4: PERFORMANCE METRICS")
    print("-" * 50)

    performance_metrics = {
        "overall_performance": {
            "total_time": search_stats["processing_time"]
            + scraping_stats["total_processing_time"],
            "total_cost": scraping_stats["total_cost"],
            "success_rate": scraping_stats["successful_scrapes"]
            / scraping_stats["total_urls"],
            "data_extracted": scraping_stats["total_content"],
        },
        "tool_performance": {
            "free_web_search": {
                "queries_processed": search_stats["successful_queries"],
                "results_found": search_stats["unique_results"],
                "avg_time_per_query": search_stats["processing_time"]
                / max(search_stats["successful_queries"], 1),
                "engines_used": search_stats["engines_used"],
            },
            "ultra_fast_scraper": {
                "sites_scraped": scraping_stats["successful_scrapes"],
                "avg_time_per_site": scraping_stats["avg_processing_time"],
                "avg_cost_per_site": scraping_stats["avg_cost_per_scrape"],
                "chars_per_second": scraping_stats["chars_per_second"],
                "strategies_used": scraping_stats["strategies_used"],
            },
        },
    }

    analysis_results["performance_metrics"] = performance_metrics

    print(f"📊 Overall Performance:")
    print(
        f"  ⏱️  Total time: {performance_metrics['overall_performance']['total_time']:.2f}s"
    )
    print(
        f"  💰 Total cost: ${performance_metrics['overall_performance']['total_cost']:.6f}"
    )
    print(
        f"  🎯 Success rate: {performance_metrics['overall_performance']['success_rate']:.1%}"
    )
    print(
        f"  📄 Data extracted: {performance_metrics['overall_performance']['data_extracted']:,} chars"
    )

    # Save comprehensive results
    output_file = "saveetha_startups_comprehensive_analysis.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)

    print(f"\n🎉 COMPREHENSIVE ANALYSIS COMPLETED!")
    print("=" * 70)
    print(f"📁 Results saved to: {output_file}")
    print(f"📊 Total data points: {len(unique_results) + len(scraped_data)}")
    print(
        f"💰 Total cost: ${performance_metrics['overall_performance']['total_cost']:.6f}"
    )
    print(
        f"⚡ Processing speed: {performance_metrics['overall_performance']['data_extracted'] / performance_metrics['overall_performance']['total_time']:.0f} chars/s"
    )

    return analysis_results


def extract_startup_intelligence(content, title, url):
    """Extract comprehensive startup intelligence from content"""

    # Startup-related keywords
    startup_keywords = [
        "startup",
        "entrepreneur",
        "entrepreneurship",
        "incubator",
        "incubation",
        "venture",
        "funding",
        "investment",
        "investor",
        "pitch",
        "accelerator",
        "innovation",
        "innovate",
        "disrupt",
        "disruption",
        "unicorn",
        "scale-up",
        "founder",
        "co-founder",
        "team",
        "mentor",
        "mentorship",
        "guidance",
        "prototype",
        "mvp",
        "product",
        "service",
        "solution",
        "technology",
        "business",
        "company",
        "enterprise",
        "revenue",
        "profit",
        "growth",
        "market",
        "customer",
        "user",
        "client",
        "industry",
        "sector",
    ]

    # Education-specific keywords
    education_keywords = [
        "student",
        "alumni",
        "university",
        "college",
        "institution",
        "campus",
        "research",
        "development",
        "lab",
        "laboratory",
        "center",
        "centre",
        "department",
        "faculty",
        "professor",
        "academic",
        "education",
    ]

    # Success indicators
    success_keywords = [
        "success",
        "successful",
        "achievement",
        "award",
        "recognition",
        "milestone",
        "launched",
        "established",
        "founded",
        "created",
        "developed",
        "deployed",
    ]

    content_lower = content.lower()
    title_lower = title.lower()

    intelligence = {
        "startup_indicators": [],
        "education_indicators": [],
        "success_indicators": [],
        "key_entities": [],
        "focus_areas": [],
        "sentiment_indicators": [],
        "contact_info": [],
        "dates_and_numbers": [],
    }

    # Extract startup indicators
    for keyword in startup_keywords:
        if keyword in content_lower or keyword in title_lower:
            intelligence["startup_indicators"].append(keyword)

    # Extract education indicators
    for keyword in education_keywords:
        if keyword in content_lower:
            intelligence["education_indicators"].append(keyword)

    # Extract success indicators
    for keyword in success_keywords:
        if keyword in content_lower:
            intelligence["success_indicators"].append(keyword)

    # Extract common startup focus areas
    focus_areas = {
        "AI/ML": [
            "artificial intelligence",
            "machine learning",
            "ai",
            "ml",
            "deep learning",
        ],
        "IoT": ["internet of things", "iot", "connected devices", "smart"],
        "Healthcare": ["healthcare", "medical", "health", "pharma", "biotech"],
        "EdTech": ["education technology", "edtech", "learning", "e-learning"],
        "FinTech": ["financial technology", "fintech", "banking", "payment"],
        "GreenTech": ["green technology", "cleantech", "sustainable", "renewable"],
        "SaaS": ["software as a service", "saas", "platform", "subscription"],
        "E-commerce": ["e-commerce", "ecommerce", "online store", "marketplace"],
    }

    for area, keywords in focus_areas.items():
        if any(keyword in content_lower for keyword in keywords):
            intelligence["focus_areas"].append(area)

    # Extract contact information (basic patterns)
    import re

    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    phone_pattern = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"

    emails = re.findall(email_pattern, content)
    phones = re.findall(phone_pattern, content)

    intelligence["contact_info"] = {
        "emails": emails[:5],  # Limit to first 5
        "phone_numbers": phones[:3],  # Limit to first 3
    }

    # Extract numbers and quantities
    number_pattern = r"\b\d{1,4}(?:,\d{3})*(?:\.\d+)?\b"
    numbers = re.findall(number_pattern, content)

    intelligence["dates_and_numbers"] = numbers[:10]  # Limit to first 10

    # Calculate content metrics
    intelligence["content_metrics"] = {
        "word_count": len(content.split()),
        "char_count": len(content),
        "startup_keyword_density": len(intelligence["startup_indicators"])
        / max(len(content.split()), 1),
        "education_keyword_density": len(intelligence["education_indicators"])
        / max(len(content.split()), 1),
    }

    return intelligence


def analyze_comprehensive_intelligence(scraped_data, search_results):
    """Analyze comprehensive intelligence from all data"""

    analysis = {
        "startup_ecosystem_analysis": {},
        "key_findings": [],
        "trending_topics": [],
        "success_patterns": [],
        "opportunities": [],
        "recommendations": [],
    }

    if not scraped_data:
        return analysis

    # Aggregate all intelligence
    all_startup_indicators = []
    all_education_indicators = []
    all_focus_areas = []
    all_success_indicators = []
    total_content = 0

    for item in scraped_data:
        intel = item.get("startup_intelligence", {})
        all_startup_indicators.extend(intel.get("startup_indicators", []))
        all_education_indicators.extend(intel.get("education_indicators", []))
        all_focus_areas.extend(intel.get("focus_areas", []))
        all_success_indicators.extend(intel.get("success_indicators", []))
        total_content += item.get("content_length", 0)

    # Count frequencies
    from collections import Counter

    startup_indicator_counts = Counter(all_startup_indicators)
    education_indicator_counts = Counter(all_education_indicators)
    focus_area_counts = Counter(all_focus_areas)
    success_indicator_counts = Counter(all_success_indicators)

    # Startup ecosystem analysis
    analysis["startup_ecosystem_analysis"] = {
        "maturity_level": assess_ecosystem_maturity(startup_indicator_counts),
        "primary_activities": get_top_items(startup_indicator_counts, 5),
        "education_integration": get_top_items(education_indicator_counts, 5),
        "focus_areas": get_top_items(focus_area_counts, 5),
        "success_factors": get_top_items(success_indicator_counts, 5),
        "ecosystem_health": {
            "activity_score": min(len(all_startup_indicators) / 10, 1.0),
            "diversity_score": min(len(set(all_focus_areas)) / 5, 1.0),
            "success_rate": min(
                len(all_success_indicators) / max(len(all_startup_indicators), 1), 1.0
            ),
        },
    }

    # Key findings
    analysis["key_findings"] = [
        f"Strong startup presence with {len(all_startup_indicators)} indicators",
        f"Active education integration with {len(all_education_indicators)} educational references",
        f"Diverse focus areas: {len(set(all_focus_areas))} different sectors",
        f"Success indicators: {len(all_success_indicators)} achievement markers",
        f"Total content analyzed: {total_content:,} characters",
    ]

    # Trending topics
    analysis["trending_topics"] = [
        topic for topic, count in startup_indicator_counts.most_common(5)
    ]

    # Success patterns
    analysis["success_patterns"] = [
        pattern for pattern, count in success_indicator_counts.most_common(3)
    ]

    # Opportunities
    if focus_area_counts:
        analysis["opportunities"] = [
            f"Focus on {area} sector"
            for area, count in focus_area_counts.most_common(3)
        ]

    # Recommendations
    analysis["recommendations"] = [
        "Leverage strong education-startup integration",
        "Focus on high-potential focus areas identified",
        "Scale successful patterns across more initiatives",
        "Enhance mentorship and funding programs",
    ]

    return analysis


def assess_ecosystem_maturity(indicator_counts):
    """Assess the maturity level of the startup ecosystem"""
    total_indicators = sum(indicator_counts.values())

    if total_indicators > 50:
        return "mature"
    elif total_indicators > 25:
        return "developing"
    elif total_indicators > 10:
        return "emerging"
    else:
        return "nascent"


def get_top_items(counter, n):
    """Get top n items from a counter"""
    return [{"item": item, "count": count} for item, count in counter.most_common(n)]


async def main():
    """Main comprehensive analysis"""
    try:
        results = await comprehensive_saveetha_analysis()

        print(f"\n🎯 FINAL SUMMARY:")
        print(f"=" * 50)
        print(
            f"📊 Search results: {results['search_phase']['statistics']['unique_results']}"
        )
        print(
            f"🚀 Sites scraped: {results['scraping_phase']['statistics']['successful_scrapes']}"
        )
        print(
            f"📄 Content extracted: {results['scraping_phase']['statistics']['total_content']:,} chars"
        )
        print(
            f"💰 Total cost: ${results['performance_metrics']['overall_performance']['total_cost']:.6f}"
        )
        print(
            f"⏱️  Total time: {results['performance_metrics']['overall_performance']['total_time']:.2f}s"
        )
        print(
            f"🎯 Success rate: {results['performance_metrics']['overall_performance']['success_rate']:.1%}"
        )

        if results["intelligence_analysis"]["startup_ecosystem_analysis"]:
            ecosystem = results["intelligence_analysis"]["startup_ecosystem_analysis"]
            print(f"\n🏢 Ecosystem Analysis:")
            print(f"  📈 Maturity: {ecosystem['maturity_level']}")
            print(
                f"  🎯 Health Score: {ecosystem['ecosystem_health']['activity_score']:.2f}"
            )
            print(
                f"  🌐 Diversity: {ecosystem['ecosystem_health']['diversity_score']:.2f}"
            )

        print(
            f"\n🚀 Analysis complete! Check saveetha_startups_comprehensive_analysis.json"
        )

    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")

    finally:
        await free_search_engine.close()


if __name__ == "__main__":
    asyncio.run(main())
