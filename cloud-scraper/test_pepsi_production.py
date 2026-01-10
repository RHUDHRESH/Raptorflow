"""
Test script for production-grade scraper on Pepsi.com
"""

import asyncio
import json

from production_scraper import ProductionScrapingStrategy, production_scraper


async def test_pepsi():
    print("🚀 Testing Production-Grade Scraper on Pepsi.com (Third Time)")
    print("=" * 60)

    # Test with adaptive strategy
    result = await production_scraper.scrape_with_production_grade_handling(
        url="https://www.pepsico.com/en/",
        user_id="test-user-v3",
        legal_basis="research",
        strategy=ProductionScrapingStrategy.ADAPTIVE,
    )

    print("📊 PRODUCTION RESULTS:")
    print(f'Status: {result.get("status", "unknown")}')
    print(
        f'Strategy Used: {result.get("production_metadata", {}).get("scraping_strategy", "unknown")}'
    )
    print(f'Processing Time: {result.get("processing_time", 0):.2f}s')

    if "production_metadata" in result:
        metadata = result["production_metadata"]
        print(f'Data Quality Score: {metadata.get("data_quality_score", 0):.2f}')
        print(f'Compliance Status: {metadata.get("compliance_status", "unknown")}')
        print(f'Edge Cases Detected: {metadata.get("edge_cases_detected", 0)}')

    if "production_cost" in result:
        cost = result["production_cost"]
        print(f'Estimated Cost: ${cost.get("estimated_cost", 0):.6f}')
        print(f'Cost Efficiency: {cost.get("cost_efficiency", 0):.2f}')

    if "data_quality" in result:
        quality = result["data_quality"]
        print(f'Content Length Score: {quality.get("content_length_score", 0):.2f}')
        print(f'Text Ratio Score: {quality.get("text_ratio_score", 0):.2f}')
        print(f'Overall Quality Score: {quality.get("overall_score", 0):.2f}')

    if result.get("status") == "success":
        content_length = result.get("content_length", 0)
        readable_text = result.get("readable_text", "")
        title = result.get("title", "No title")

        print(f"\n📄 CONTENT ANALYSIS:")
        print(f"Title: {title}")
        print(f"Content Length: {content_length:,} characters")
        print(f"Readable Text Length: {len(readable_text):,} characters")
        print(f"Text Preview: {readable_text[:200]}...")

        # Check for enhancements
        enhancements = []
        if "color_palette" in result:
            enhancements.append("Color Palette Extraction")
        if "language" in result:
            enhancements.append(f'Language Detection ({result["language"]})')
        if "content_stats" in result:
            enhancements.append("Content Statistics")
        if "system_info" in result:
            enhancements.append("System Monitoring")
        if "compliance" in result:
            enhancements.append("Compliance Tracking")

        if enhancements:
            print(f'\n🎯 ENHANCEMENTS ACTIVE: {", ".join(enhancements)}')

        # Check for fallback usage
        if result.get("fallback_used"):
            print(f'🔄 Fallback Used: {result["fallback_used"]}')

        # Check for cost tracking
        if "cost_tracking" in result:
            cost_track = result["cost_tracking"]
            print(f'💰 Cost Tracking: ${cost_track.get("estimated_cost", 0):.6f}')

        print(
            f"\n✅ SUCCESS: Production-grade scraping completed with enterprise features!"
        )
    else:
        print(f'\n❌ FAILED: {result.get("error", "Unknown error")}')

        # Check for graceful failure
        if result.get("graceful_failure"):
            print("🛡️ Graceful failure mode activated")
            if "error" in result:
                error_info = result["error"]
                print(
                    f'Suggested Action: {error_info.get("suggested_action", "No suggestion")}'
                )


if __name__ == "__main__":
    asyncio.run(test_pepsi())
