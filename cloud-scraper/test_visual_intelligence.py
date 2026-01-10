"""
Visual Intelligence Test Script - Test Visual Design Intelligence Extractor
"""

import asyncio
import json

from visual_intelligence_extractor import visual_intelligence_extractor


async def test_visual_intelligence():
    print("🎨 Testing Visual Design Intelligence Extractor")
    print("=" * 60)

    # Test sites for visual analysis
    test_sites = [
        {
            "name": "PepsiCo",
            "url": "https://www.pepsico.com/en/",
            "description": "Beverage and food company - strong brand colors",
        },
        {
            "name": "McDonald's",
            "url": "https://www.mcdonalds.com/us/en-us.html",
            "description": "Fast food chain - iconic red and yellow",
        },
        {
            "name": "Intecalic",
            "url": "https://intecalic.com/",
            "description": "Technology company - modern design",
        },
        {
            "name": "Ausdauer Groups",
            "url": "https://www.ausdauergroups.in/",
            "description": "Business group - professional design",
        },
    ]

    results = {}

    for site in test_sites:
        print(f'\n🎯 Analyzing Visual Design: {site["name"]}')
        print(f'📍 URL: {site["url"]}')
        print(f'📝 Description: {site["description"]}')
        print("-" * 50)

        try:
            start_time = asyncio.get_event_loop().time()

            # Extract visual intelligence
            result = await visual_intelligence_extractor.extract_visual_intelligence(
                url=site["url"],
                user_id=f'test-user-{site["name"].lower().replace(" ", "-")}',
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
                visual_intel = result.get("visual_intelligence", {})

                # Color Analysis
                color_analysis = visual_intel.get("color_analysis", {})
                primary_colors = color_analysis.get("primary_colors", [])
                secondary_colors = color_analysis.get("secondary_colors", [])
                accent_colors = color_analysis.get("accent_colors", [])

                print(f"\n🎨 COLOR PALETTE:")
                if primary_colors:
                    print(f'  🔴 Primary: {", ".join(primary_colors[:3])}')
                if secondary_colors:
                    print(f'  🟠 Secondary: {", ".join(secondary_colors[:3])}')
                if accent_colors:
                    print(f'  🟡 Accent: {", ".join(accent_colors[:3])}')

                # Typography Analysis
                typography_analysis = visual_intel.get("typography_analysis", {})
                primary_fonts = typography_analysis.get("primary_fonts", [])
                font_hierarchy = typography_analysis.get("font_hierarchy", [])

                print(f"\n📝 TYPOGRAPHY:")
                if primary_fonts:
                    print(f'  🔤 Primary Fonts: {", ".join(primary_fonts[:3])}')
                if font_hierarchy:
                    print(f"  📐 Font Hierarchy: {len(font_hierarchy)} levels")
                    for i, font in enumerate(font_hierarchy[:3]):
                        print(
                            f'    Level {font.get("hierarchy_level", i+1)}: {font.get("font_family", "Unknown")} ({font.get("font_size", "Unknown")})'
                        )

                # Visual Motifs
                visual_motifs = visual_intel.get("visual_motifs", {})
                motifs = visual_motifs.get("motifs", [])
                dominant_style = visual_motifs.get("dominant_style", "unknown")

                print(f"\n🎭 VISUAL MOTIFS:")
                print(f"  🎨 Dominant Style: {dominant_style}")
                if motifs:
                    print(f"  📋 Identified Motifs: {len(motifs)}")
                    for motif in motifs[:3]:
                        print(
                            f'    • {motif.get("type", "Unknown")}: {motif.get("description", "No description")[:50]}...'
                        )

                # Communication Analysis
                communication_analysis = visual_intel.get("communication_analysis", {})
                style = communication_analysis.get("style", "unknown")
                tone = communication_analysis.get("tone", "unknown")
                formality_level = communication_analysis.get("formality_level", 0)
                keyword_patterns = communication_analysis.get("keyword_patterns", [])

                print(f"\n💬 COMMUNICATION STYLE:")
                print(f"  🗣️  Style: {style}")
                print(f"  🎭 Tone: {tone}")
                print(f"  📊 Formality Level: {formality_level:.2f}")
                if keyword_patterns:
                    print(
                        f'  🔑 Top Keywords: {", ".join([kw[0] for kw in keyword_patterns[:5]])}'
                    )

                # Design Intelligence
                design_intel = visual_intel.get("design_intelligence", {})
                brand_personality = design_intel.get("brand_personality", {})
                target_audience = design_intel.get("target_audience", {})
                industry_alignment = design_intel.get("industry_alignment", {})

                print(f"\n🧠 DESIGN INTELLIGENCE:")
                if brand_personality:
                    print(f"  🎯 Brand Personality: {brand_personality}")
                if target_audience:
                    print(f"  👥 Target Audience: {target_audience}")
                if industry_alignment:
                    print(f"  🏭 Industry Alignment: {industry_alignment}")

                # Performance Metrics
                extraction_metadata = result.get("extraction_metadata", {})
                confidence_score = extraction_metadata.get("confidence_score", 0)
                strategies_used = extraction_metadata.get("strategies_used", [])

                print(f"\n📊 PERFORMANCE METRICS:")
                print(f"  🎯 Confidence Score: {confidence_score:.2f}")
                print(f'  🔧 Strategies Used: {", ".join(strategies_used)}')

            else:
                print(f'❌ Error: {result.get("error", "Unknown error")}')

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results[site["name"]] = {"error": str(e), "site_info": site}

    # Summary
    print(f"\n📊 VISUAL INTELLIGENCE SUMMARY")
    print("=" * 60)

    successful_sites = {
        k: v
        for k, v in results.items()
        if "result" in v and v["result"].get("status") == "success"
    }

    if successful_sites:
        print(
            f"✅ Successfully Analyzed: {len(successful_sites)}/{len(test_sites)} sites"
        )
        print(
            f'⏱️  Average Processing Time: {sum(v["result"].get("processing_time", 0) for v in successful_sites.values()) / len(successful_sites):.2f}s'
        )

        print(f"\n🎨 COLOR INSIGHTS:")
        for site_name, data in successful_sites.items():
            visual_intel = data["result"].get("visual_intelligence", {})
            color_analysis = visual_intel.get("color_analysis", {})
            primary_colors = color_analysis.get("primary_colors", [])

            print(f"\n🏢 {site_name}:")
            if primary_colors:
                print(f'   🎨 Primary Colors: {", ".join(primary_colors)}')
            else:
                print(f"   🎨 No primary colors identified")

        print(f"\n📝 TYPOGRAPHY INSIGHTS:")
        for site_name, data in successful_sites.items():
            visual_intel = data["result"].get("visual_intelligence", {})
            typography_analysis = visual_intel.get("typography_analysis", {})
            primary_fonts = typography_analysis.get("primary_fonts", [])

            print(f"\n🏢 {site_name}:")
            if primary_fonts:
                print(f'   🔤 Primary Fonts: {", ".join(primary_fonts)}')
            else:
                print(f"   🔤 No fonts identified")

        print(f"\n💬 COMMUNICATION INSIGHTS:")
        for site_name, data in successful_sites.items():
            visual_intel = data["result"].get("visual_intelligence", {})
            communication_analysis = visual_intel.get("communication_analysis", {})
            style = communication_analysis.get("style", "unknown")
            formality_level = communication_analysis.get("formality_level", 0)

            print(f"\n🏢 {site_name}:")
            print(f"   🗣️  Style: {style}")
            print(f"   📊 Formality: {formality_level:.2f}")

        print(f"\n🎭 DESIGN STYLE COMPARISON:")
        for site_name, data in successful_sites.items():
            visual_intel = data["result"].get("visual_intelligence", {})
            visual_motifs = visual_intel.get("visual_motifs", {})
            dominant_style = visual_motifs.get("dominant_style", "unknown")

            print(f"   🏢 {site_name}: {dominant_style}")

        # Cross-site analysis
        print(f"\n🔍 CROSS-SITE ANALYSIS:")

        # Common color patterns
        all_primary_colors = []
        for data in successful_sites.values():
            visual_intel = data["result"].get("visual_intelligence", {})
            color_analysis = visual_intel.get("color_analysis", {})
            all_primary_colors.extend(color_analysis.get("primary_colors", []))

        if all_primary_colors:
            from collections import Counter

            color_frequency = Counter(all_primary_colors)
            print(f"   🎨 Most Common Colors: {color_frequency.most_common(3)}")

        # Communication style distribution
        communication_styles = []
        for data in successful_sites.values():
            visual_intel = data["result"].get("visual_intelligence", {})
            communication_analysis = visual_intel.get("communication_analysis", {})
            communication_styles.append(communication_analysis.get("style", "unknown"))

        if communication_styles:
            style_frequency = Counter(communication_styles)
            print(f"   💬 Communication Styles: {dict(style_frequency)}")

        # Typography trends
        all_fonts = []
        for data in successful_sites.values():
            visual_intel = data["result"].get("visual_intelligence", {})
            typography_analysis = visual_intel.get("typography_analysis", {})
            all_fonts.extend(typography_analysis.get("primary_fonts", []))

        if all_fonts:
            font_frequency = Counter(all_fonts)
            print(f"   🔤 Popular Fonts: {font_frequency.most_common(3)}")

    else:
        print(f"❌ No sites were successfully analyzed")

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

    print(f"\n🎉 VISUAL INTELLIGENCE ANALYSIS COMPLETE!")
    print(
        f"📊 Results include: Color palettes, Typography analysis, Visual motifs, Communication patterns, Design intelligence"
    )


if __name__ == "__main__":
    asyncio.run(test_visual_intelligence())
