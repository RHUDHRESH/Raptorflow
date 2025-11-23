"""
Sample usage examples for the Predictive Performance Engine.

This file demonstrates how to use each module of the performance engine
to predict, optimize, and improve content performance.
"""

import asyncio
from backend.performance import (
    engagement_predictor,
    conversion_optimizer,
    viral_potential_scorer,
    ab_test_orchestrator,
    competitive_benchmarker,
    performance_memory
)


async def example_engagement_prediction():
    """Example: Predict engagement for blog post."""
    print("\n=== EXAMPLE 1: Engagement Prediction ===\n")

    blog_content = """
    Artificial Intelligence is Transforming Marketing: Here's How

    The marketing landscape is experiencing a revolutionary shift thanks to AI.
    From personalized customer experiences to predictive analytics, AI is enabling
    marketers to work smarter, not harder.

    In this comprehensive guide, we'll explore:
    - How AI improves customer targeting
    - Automated content creation strategies
    - Predictive analytics for campaign optimization
    - Real-world success stories

    Join thousands of forward-thinking marketers who are already leveraging AI
    to 10x their results. Download our free guide to get started today!
    """

    result = await engagement_predictor.predict_engagement(
        content=blog_content,
        content_type="blog",
        platform="blog",
        workspace_id="demo-workspace",
        keywords=["AI", "marketing", "automation"]
    )

    print("Predicted Engagement Metrics:")
    print(f"  Likes: {result['predictions']['likes']:.0f}")
    print(f"  Shares: {result['predictions']['shares']:.0f}")
    print(f"  Comments: {result['predictions']['comments']:.0f}")
    print(f"  CTR: {result['predictions']['ctr']:.2%}")
    print(f"  Confidence Level: {result['confidence_level']:.2%}")

    print("\nTop Recommendations:")
    for rec in result['recommendations'][:3]:
        print(f"  • {rec}")


async def example_conversion_optimization():
    """Example: Optimize conversion elements."""
    print("\n=== EXAMPLE 2: Conversion Optimization ===\n")

    landing_page = """
    Revolutionary AI Marketing Tool

    Our platform helps businesses automate their marketing campaigns.
    Features include email automation, social media scheduling, and analytics.

    Pricing starts at $99/month. Click here to learn more.
    """

    result = await conversion_optimizer.analyze_conversion_potential(
        content=landing_page,
        content_type="landing_page",
        workspace_id="demo-workspace",
        target_action="signup"
    )

    print(f"Conversion Score: {result['conversion_score']:.2%}")
    print(f"CTA Score: {result['cta_analysis']['score']:.2%}")
    print(f"Urgency Score: {result['urgency_score']:.2%}")
    print(f"Trust Score: {result['trust_score']:.2%}")

    print("\nTop Recommendations:")
    for rec in result['recommendations'][:3]:
        print(f"  [{rec['priority'].upper()}] {rec['recommendation']}")
        print(f"    Example: {rec.get('example', 'N/A')}")

    print("\nOptimized CTA Suggestions:")
    for cta in result['optimized_ctas'][:3]:
        print(f"  • {cta['cta_text']}")


async def example_viral_scoring():
    """Example: Score viral potential."""
    print("\n=== EXAMPLE 3: Viral Potential Scoring ===\n")

    viral_content = """
    You Won't Believe What Happened When We Tried This Marketing Hack!

    🤯 SHOCKING results that changed everything...

    We tested 10 different strategies and discovered one game-changing approach
    that TRIPLED our engagement overnight. Here's the insider secret that
    marketing gurus don't want you to know:

    The 5-Step Viral Content Formula:
    1. Start with an emotional hook
    2. Add surprising statistics
    3. Include social proof
    4. Provide actionable value
    5. End with a compelling CTA

    This method helped 10,000+ marketers go viral. Your turn! 🚀

    Tag someone who needs to see this! 👇
    """

    result = await viral_potential_scorer.score_viral_potential(
        content=viral_content,
        title="The Marketing Hack That Changed Everything",
        content_type="social_post",
        platform="linkedin"
    )

    print(f"Viral Score: {result['viral_score']:.2%}")
    print(f"Emotion Score: {result['emotion_analysis']['high_arousal_score']:.2%}")
    print(f"Practical Value: {result['practical_value_score']:.2%}")
    print(f"Storytelling Score: {result['storytelling_score']:.2%}")

    print(f"\nDominant Emotion: {result['emotion_analysis']['dominant_emotion']}")

    print("\nViral Elements Found:")
    for element in result['viral_elements']:
        print(f"  ✓ {element}")

    print("\nOptimization Suggestions:")
    for suggestion in result['optimization_suggestions'][:3]:
        print(f"  [{suggestion['priority'].upper()}] {suggestion['suggestion']}")


async def example_ab_test():
    """Example: Create and run A/B test."""
    print("\n=== EXAMPLE 4: A/B Test Orchestration ===\n")

    base_content = """
    Learn How to Master Digital Marketing

    Our comprehensive course covers everything you need to know about
    modern digital marketing strategies. Sign up today to get started.
    """

    result = await ab_test_orchestrator.create_test(
        base_content=base_content,
        content_type="email",
        platform="email",
        workspace_id="demo-workspace",
        test_name="Email Subject Line Test",
        num_variants=3,
        test_objective="conversion"
    )

    print(f"Test ID: {result['test_id']}")
    print(f"Test Name: {result['test_name']}")

    print("\nGenerated Variants:")
    for i, variant in enumerate(result['recommended_variants'], 1):
        print(f"\n  Variant {i} ({variant['strategy']}):")
        print(f"    Composite Score: {variant['composite_score']:.2%}")
        print(f"    Content Preview: {variant['content'][:100]}...")

    print(f"\nExpected Winner: {result['expected_winner']['variant_id']}")
    print(f"Confidence: {result['expected_winner']['confidence']}")

    print("\nNext Steps:")
    for step in result['next_steps']:
        print(f"  • {step}")


async def example_competitive_analysis():
    """Example: Analyze competitor content."""
    print("\n=== EXAMPLE 5: Competitive Benchmarking ===\n")

    # Analyze competitor
    competitor_result = await competitive_benchmarker.analyze_competitor(
        competitor_name="MarketingPro Inc",
        content_samples=[
            "How to 10x your marketing ROI with proven AI strategies. Join 50,000+ marketers.",
            "Case Study: How we helped Company X achieve 500% growth in 6 months.",
            "The future of marketing: 7 trends that will dominate 2024."
        ],
        platform="linkedin"
    )

    print(f"Competitor: {competitor_result['competitor_name']}")
    print(f"Content Quality Score: {competitor_result['content_quality_score']:.2%}")
    print(f"SEO Score: {competitor_result['seo_score']:.2%}")

    print("\nStrengths:")
    for strength in competitor_result['strengths']:
        print(f"  ✓ {strength}")

    print("\nWeaknesses:")
    for weakness in competitor_result['weaknesses']:
        print(f"  ⚠ {weakness}")

    print("\nOpportunities (gaps to exploit):")
    for opportunity in competitor_result['opportunities']:
        print(f"  💡 {opportunity}")

    # Compare with your content
    your_content = "Marketing tips and best practices for 2024"
    your_metrics = {
        "engagement_rate": 0.035,
        "conversion_rate": 0.02,
        "likes": 50,
        "shares": 10
    }

    comparison = await competitive_benchmarker.compare_with_competitors(
        your_content=your_content,
        your_metrics=your_metrics,
        competitor_analyses=[competitor_result],
        platform="linkedin"
    )

    print(f"\n\nYour Competitive Position: {comparison['competitive_position']['overall_position'].upper()}")

    print("\nYour Advantages:")
    for adv in comparison['competitive_position']['advantages']:
        print(f"  ✓ {adv}")

    print("\nAreas to Improve:")
    for imp in comparison['competitive_position']['improvements_needed']:
        print(f"  ⚠ {imp}")


async def example_complete_workflow():
    """Example: Complete content optimization workflow."""
    print("\n=== EXAMPLE 6: Complete Content Optimization Workflow ===\n")

    original_content = """
    New Product Launch

    We're excited to announce our new marketing automation tool.
    It has many features and is available now.
    """

    print("STEP 1: Initial Analysis")
    print("-" * 50)

    # Analyze original
    engagement_1 = await engagement_predictor.predict_engagement(
        content=original_content,
        content_type="social_post",
        platform="linkedin",
        workspace_id="demo-workspace"
    )

    conversion_1 = await conversion_optimizer.analyze_conversion_potential(
        content=original_content,
        content_type="social_post",
        workspace_id="demo-workspace"
    )

    viral_1 = await viral_potential_scorer.score_viral_potential(
        content=original_content,
        platform="linkedin"
    )

    print(f"Engagement Confidence: {engagement_1['confidence_level']:.2%}")
    print(f"Conversion Score: {conversion_1['conversion_score']:.2%}")
    print(f"Viral Score: {viral_1['viral_score']:.2%}")

    print("\nSTEP 2: Apply Recommendations")
    print("-" * 50)

    # Improved version
    improved_content = """
    🚀 GAME-CHANGER: Revolutionary Marketing Automation That 10x's Your Results!

    You won't believe how easy it is to automate your entire marketing funnel...

    ✅ AI-powered campaign optimization
    ✅ Real-time analytics dashboard
    ✅ Proven to increase conversions by 300%

    Join 10,000+ marketers who transformed their results!

    🎁 LIMITED TIME: Get 50% off + Free onboarding
    ⚡ Start your free trial - No credit card required

    Ready to scale? Click below 👇
    """

    # Analyze improved version
    engagement_2 = await engagement_predictor.predict_engagement(
        content=improved_content,
        content_type="social_post",
        platform="linkedin",
        workspace_id="demo-workspace"
    )

    conversion_2 = await conversion_optimizer.analyze_conversion_potential(
        content=improved_content,
        content_type="social_post",
        workspace_id="demo-workspace"
    )

    viral_2 = await viral_potential_scorer.score_viral_potential(
        content=improved_content,
        platform="linkedin"
    )

    print(f"Engagement Confidence: {engagement_2['confidence_level']:.2%} "
          f"(+{(engagement_2['confidence_level'] - engagement_1['confidence_level']):.2%})")
    print(f"Conversion Score: {conversion_2['conversion_score']:.2%} "
          f"(+{(conversion_2['conversion_score'] - conversion_1['conversion_score']):.2%})")
    print(f"Viral Score: {viral_2['viral_score']:.2%} "
          f"(+{(viral_2['viral_score'] - viral_1['viral_score']):.2%})")

    print("\nIMPROVEMENT SUMMARY:")
    print(f"  📈 {((engagement_2['confidence_level'] / engagement_1['confidence_level'] - 1) * 100):.1f}% higher engagement potential")
    print(f"  💰 {((conversion_2['conversion_score'] / conversion_1['conversion_score'] - 1) * 100):.1f}% better conversion optimization")
    print(f"  🔥 {((viral_2['viral_score'] / viral_1['viral_score'] - 1) * 100):.1f}% increased viral potential")


async def run_all_examples():
    """Run all examples."""
    print("=" * 70)
    print("PREDICTIVE PERFORMANCE ENGINE - SAMPLE USAGE EXAMPLES")
    print("=" * 70)

    await example_engagement_prediction()
    await example_conversion_optimization()
    await example_viral_scoring()
    await example_ab_test()
    await example_competitive_analysis()
    await example_complete_workflow()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    # Run all examples
    asyncio.run(run_all_examples())
