"""
Semantic Layer Test Suite

Comprehensive tests demonstrating all semantic intelligence capabilities
with sample data and expected outputs.

Run with: python -m pytest backend/semantic/test_semantic_layer.py -v
Or directly: python backend/semantic/test_semantic_layer.py
"""

import asyncio
import json
from typing import Any, Dict
import structlog

from backend.semantic.intent_detector import intent_detector
from backend.semantic.entity_extractor import entity_extractor
from backend.semantic.emotional_intelligence import emotional_intelligence_agent
from backend.semantic.topic_modeler import topic_modeler
from backend.semantic.semantic_similarity import semantic_similarity

logger = structlog.get_logger(__name__)

# Sample content for testing
SAMPLE_BLOG_POST = """
AI is revolutionizing B2B marketing automation in ways we couldn't imagine just five years ago.

For marketing directors and CMOs at B2B SaaS companies, the challenge has always been the same:
how do you scale personalized outreach without sacrificing quality? How do you nurture thousands
of leads while making each one feel like your only customer?

Enter AI-powered marketing automation. Today's platforms like HubSpot, Marketo, and Salesforce are
integrating deep learning models that can predict customer behavior, optimize send times, and even
generate personalized content at scale.

But here's what most people miss: AI isn't replacing marketers—it's amplifying their capabilities.
Think of it as a force multiplier. Your team can now focus on strategy and creativity while AI handles
the repetitive tasks of segmentation, A/B testing, and performance optimization.

The results speak for themselves. Companies implementing AI-driven automation are seeing 40% higher
engagement rates and 25% faster sales cycles. That's not just incremental improvement—that's
transformational change.

Ready to join the revolution? The future of B2B marketing is already here.
"""

SAMPLE_EMAIL_COPY = """
Subject: You're leaving 40% more revenue on the table

Hi Sarah,

I noticed your team is still using manual processes for lead scoring.

Here's the problem: while your marketing team is spending 15 hours per week manually qualifying leads,
your competitors are using AI to do it in real-time.

The cost? You're losing 40% of hot leads to faster-moving competitors.

But there's good news. Our AI-powered lead scoring engine can be up and running in your MarTech stack
in less than 48 hours. No complex integration. No months-long implementation.

Just plug it in, and watch your conversion rates climb.

Interested? Let's schedule a 15-minute demo this week.

Best,
Mike
"""

SAMPLE_ICP_DESCRIPTION = """
Marketing Directors at B2B SaaS companies with 50-200 employees. They're responsible for demand
generation, lead nurturing, and proving ROI on marketing spend. They use tools like HubSpot,
Salesforce, and Google Analytics daily.

Their main pain points include: struggling to scale personalization, difficulty proving marketing
ROI, and being overwhelmed by data without actionable insights. They're looking for solutions that
integrate easily with their existing tech stack and don't require a data science team to operate.

They value efficiency, data-driven decision making, and clear ROI metrics. They're early adopters
of martech but skeptical of overly complex solutions.
"""

SAMPLE_CONTENT_CORPUS = [
    {
        "id": "content_1",
        "content": "Machine learning is transforming customer segmentation in marketing..."
    },
    {
        "id": "content_2",
        "content": "The rise of predictive analytics in B2B sales forecasting..."
    },
    {
        "id": "content_3",
        "content": "How AI-powered chatbots are improving customer support response times..."
    },
    {
        "id": "content_4",
        "content": "Marketing automation best practices for B2B SaaS companies..."
    },
    {
        "id": "content_5",
        "content": "Understanding the customer journey with advanced analytics..."
    }
]


async def test_intent_detection():
    """Test intent detection on various content types."""
    print("\n" + "="*80)
    print("TEST 1: INTENT DETECTION")
    print("="*80)

    # Test 1: Blog post intent
    print("\n--- Analyzing Blog Post Intent ---")
    blog_intent = await intent_detector.analyze_intent(
        text=SAMPLE_BLOG_POST,
        context={
            "content_type": "blog_post",
            "target_audience": "Marketing Directors at B2B SaaS",
            "stated_goals": "educate and build authority"
        }
    )

    print(f"Primary Intent: {blog_intent['primary']['intent']}")
    print(f"Category: {blog_intent['primary']['category']}")
    print(f"Confidence: {blog_intent['primary']['confidence']}")
    print(f"Emotional Intent: {blog_intent['emotional']['primary_emotion']}")
    print(f"Conversion Goal: {blog_intent['conversion']['desired_action']}")
    print(f"Alignment Score: {blog_intent['alignment']['context_alignment_score']}")

    # Test 2: Email intent
    print("\n--- Analyzing Email Intent ---")
    email_intent = await intent_detector.analyze_intent(
        text=SAMPLE_EMAIL_COPY,
        context={
            "content_type": "email",
            "target_audience": "Marketing Directors",
            "stated_goals": "book demo calls"
        }
    )

    print(f"Primary Intent: {email_intent['primary']['intent']}")
    print(f"Category: {email_intent['primary']['category']}")
    print(f"Conversion Goal: {email_intent['conversion']['desired_action']}")
    print(f"Urgency Level: {email_intent['conversion']['urgency_level']}")

    # Test 3: Compare intents
    print("\n--- Comparing Blog vs Email Intent ---")
    comparison = await intent_detector.compare_intents(blog_intent, email_intent)
    print(f"Primary Intent Shift: {comparison['primary_shift']}")
    print(f"Emotional Shift: {comparison['emotional_shift']}")
    print(f"Conversion Shift: {comparison['conversion_shift']}")

    return {
        "blog_intent": blog_intent,
        "email_intent": email_intent,
        "comparison": comparison
    }


async def test_entity_extraction():
    """Test entity extraction and knowledge graph building."""
    print("\n" + "="*80)
    print("TEST 2: ENTITY EXTRACTION & KNOWLEDGE GRAPHS")
    print("="*80)

    # Test 1: Extract from blog post
    print("\n--- Extracting Entities from Blog Post ---")
    blog_entities = await entity_extractor.extract_entities_and_relations(
        content=SAMPLE_BLOG_POST,
        context={
            "domain": "B2B SaaS Marketing",
            "content_type": "blog_post"
        }
    )

    print(f"Total Entities: {blog_entities['summary']['total_entities']}")
    print(f"Entity Distribution: {json.dumps(blog_entities['summary']['entity_distribution'], indent=2)}")
    print(f"\nKey Entities:")
    for entity in blog_entities['entities'][:5]:
        print(f"  - {entity['text']} ({entity['type']}) - Importance: {entity['importance']}")

    print(f"\nKey Relationships:")
    for rel in blog_entities['relationships'][:5]:
        print(f"  - {rel['source']} → {rel['relation']} → {rel['target']}")

    # Test 2: Extract from ICP
    print("\n--- Extracting Entities from ICP Description ---")
    icp_entities = await entity_extractor.extract_entities_and_relations(
        content=SAMPLE_ICP_DESCRIPTION,
        context={
            "domain": "B2B SaaS",
            "content_type": "icp_profile"
        }
    )

    print(f"Total Entities: {icp_entities['summary']['total_entities']}")
    print(f"Central Concepts: {icp_entities['summary']['central_concepts']}")

    # Test 3: Build cumulative graph
    print("\n--- Building Cumulative Knowledge Graph ---")
    cumulative_graph = await entity_extractor.build_cumulative_graph(
        contents=[SAMPLE_BLOG_POST, SAMPLE_ICP_DESCRIPTION],
        workspace_id="test_workspace"
    )

    print(f"Cumulative Entities: {len(cumulative_graph['entities'])}")
    print(f"Cumulative Relationships: {len(cumulative_graph['relationships'])}")
    print(f"Graph Density: {cumulative_graph['summary']['graph_density']:.2f}")

    return {
        "blog_entities": blog_entities,
        "icp_entities": icp_entities,
        "cumulative_graph": cumulative_graph
    }


async def test_emotional_intelligence():
    """Test emotional intelligence analysis."""
    print("\n" + "="*80)
    print("TEST 3: EMOTIONAL INTELLIGENCE ANALYSIS")
    print("="*80)

    # Test 1: Blog post emotional journey
    print("\n--- Analyzing Blog Post Emotional Journey ---")
    blog_emotional = await emotional_intelligence_agent.analyze_emotional_journey(
        content=SAMPLE_BLOG_POST,
        context={
            "target_audience": "Marketing Directors at B2B SaaS",
            "content_goal": "educate and inspire",
            "brand_values": ["innovation", "authenticity", "results-driven"]
        }
    )

    print(f"Emotional Trajectory: {blog_emotional['emotional_arc']['trajectory']}")
    print(f"Starting Emotion: {blog_emotional['emotional_arc']['starting_emotion']}")
    print(f"Ending Emotion: {blog_emotional['emotional_arc']['ending_emotion']}")
    print(f"\nEmotional Resonance:")
    print(f"  - Overall: {blog_emotional['emotional_resonance']['overall_resonance']:.2f}")
    print(f"  - Empathy: {blog_emotional['emotional_resonance']['empathy_score']:.2f}")
    print(f"  - Authenticity: {blog_emotional['emotional_resonance']['authenticity_score']:.2f}")

    print(f"\nPsychological Triggers:")
    for trigger in blog_emotional['psychological_triggers'][:3]:
        print(f"  - {trigger['trigger_type']}: {trigger['description']}")

    print(f"\nPersuasion Techniques:")
    for technique in blog_emotional['persuasion_techniques'][:3]:
        print(f"  - {technique['technique']}: Sophistication {technique['sophistication']:.2f}")

    # Test 2: Email emotional analysis
    print("\n--- Analyzing Email Emotional Journey ---")
    email_emotional = await emotional_intelligence_agent.analyze_emotional_journey(
        content=SAMPLE_EMAIL_COPY,
        context={
            "target_audience": "Marketing Directors",
            "content_goal": "book demo calls"
        }
    )

    print(f"Emotional Trajectory: {email_emotional['emotional_arc']['trajectory']}")
    print(f"Overall Resonance: {email_emotional['emotional_resonance']['overall_resonance']:.2f}")
    print(f"Manipulation Score: {email_emotional.get('manipulation_score', 0):.2f}")
    print(f"Ethical Score: {email_emotional['ethical_assessment']['ethical_score']:.2f}")

    # Test 3: Compare emotional profiles
    print("\n--- Comparing Emotional Profiles ---")
    comparison = await emotional_intelligence_agent.compare_emotional_profiles(
        content1=SAMPLE_BLOG_POST,
        content2=SAMPLE_EMAIL_COPY
    )

    print(f"Trajectory Comparison: {comparison['trajectory_comparison']}")
    print(f"Resonance Delta: {comparison['resonance_delta']:.2f}")
    print(f"Recommendation: {comparison['recommendation']}")

    return {
        "blog_emotional": blog_emotional,
        "email_emotional": email_emotional,
        "comparison": comparison
    }


async def test_topic_modeling():
    """Test topic extraction and clustering."""
    print("\n" + "="*80)
    print("TEST 4: TOPIC MODELING")
    print("="*80)

    # Test 1: Extract topics from single document
    print("\n--- Extracting Topics from Blog Post ---")
    blog_topics = await topic_modeler.extract_topics(
        content=SAMPLE_BLOG_POST,
        context={
            "domain": "B2B Marketing",
            "min_topics": 3,
            "max_topics": 7
        }
    )

    print(f"Total Topics: {blog_topics['summary']['total_topics']}")
    print(f"Primary Topic: {blog_topics['summary']['primary_topic']}")
    print(f"Topic Diversity: {blog_topics['summary']['topic_diversity']:.2f}")

    print(f"\nExtracted Topics:")
    for topic in blog_topics['topics'][:5]:
        print(f"  - {topic['name']} (weight: {topic['weight']:.2f})")
        print(f"    Keywords: {', '.join(topic['keywords'][:5])}")

    # Test 2: Extract topics from corpus
    print("\n--- Extracting Topics from Corpus ---")
    corpus_topics = await topic_modeler.extract_topics_from_corpus(
        documents=SAMPLE_CONTENT_CORPUS,
        context={
            "domain": "B2B SaaS"
        }
    )

    print(f"Documents Analyzed: {corpus_topics['metadata']['document_count']}")
    print(f"Total Topics: {corpus_topics['metadata']['total_topics_extracted']}")
    print(f"Clusters Identified: {len(corpus_topics.get('clusters', []))}")

    if corpus_topics.get('clusters'):
        print(f"\nTopic Clusters:")
        for cluster in corpus_topics['clusters'][:3]:
            print(f"  - {cluster['name']}: {len(cluster['topics'])} topics")

    if corpus_topics.get('trends', {}).get('trending_topics'):
        print(f"\nTrending Topics:")
        for trend in corpus_topics['trends']['trending_topics'][:3]:
            print(f"  - {trend['topic']}: {trend['frequency']} occurrences ({trend['trend']})")

    return {
        "blog_topics": blog_topics,
        "corpus_topics": corpus_topics
    }


async def test_semantic_similarity():
    """Test semantic similarity and search."""
    print("\n" + "="*80)
    print("TEST 5: SEMANTIC SIMILARITY")
    print("="*80)

    # Test 1: Compute similarity between two texts
    print("\n--- Computing Similarity Between Blog and Email ---")
    similarity = await semantic_similarity.compute_similarity(
        text1=SAMPLE_BLOG_POST,
        text2=SAMPLE_EMAIL_COPY
    )

    print(f"Similarity Score: {similarity:.4f}")
    print(f"Interpretation: {'Similar' if similarity > 0.75 else 'Somewhat similar' if similarity > 0.5 else 'Different'}")

    # Test 2: Detect duplicates in corpus
    print("\n--- Detecting Duplicates in Corpus ---")
    test_texts = [
        SAMPLE_BLOG_POST,
        SAMPLE_EMAIL_COPY,
        SAMPLE_BLOG_POST,  # Exact duplicate
        SAMPLE_ICP_DESCRIPTION
    ]

    duplicates = await semantic_similarity.detect_duplicates(
        texts=test_texts,
        threshold=0.95
    )

    print(f"Duplicate Pairs Found: {len(duplicates)}")
    for dup in duplicates:
        print(f"  - Texts {dup['index1']} and {dup['index2']}: {dup['similarity']:.4f}")
        if dup['is_exact_duplicate']:
            print(f"    ⚠️  Exact duplicate detected!")

    # Test 3: Semantic search
    print("\n--- Semantic Search ---")
    search_results = await semantic_similarity.semantic_search(
        query="AI marketing automation tools",
        documents=SAMPLE_CONTENT_CORPUS,
        top_k=3
    )

    print(f"Top {len(search_results)} Results:")
    for i, result in enumerate(search_results, 1):
        print(f"{i}. Document {result['document_id']}")
        print(f"   Relevance: {result['relevance_score']:.4f}")
        print(f"   Preview: {result['content'][:80]}...")

    # Test 4: Clustering
    print("\n--- Clustering Content by Similarity ---")
    corpus_texts = [doc['content'] for doc in SAMPLE_CONTENT_CORPUS]
    clusters = await semantic_similarity.cluster_by_similarity(
        texts=corpus_texts
    )

    print(f"Clusters Identified: {clusters['num_clusters']}")
    for cluster in clusters['clusters'][:3]:
        print(f"\nCluster {cluster['cluster_id']}:")
        print(f"  Members: {len(cluster['members'])}")
        for member in cluster['members'][:2]:
            print(f"    - {member['text_preview'][:60]}...")

    return {
        "similarity_score": similarity,
        "duplicates": duplicates,
        "search_results": search_results,
        "clusters": clusters
    }


async def test_integration_workflow():
    """Test complete integration workflow."""
    print("\n" + "="*80)
    print("TEST 6: COMPLETE INTEGRATION WORKFLOW")
    print("="*80)

    print("\n--- Simulating Content Generation Workflow ---")

    # Step 1: Analyze intent of content request
    print("\n1. Analyzing content intent...")
    intent = await intent_detector.analyze_intent(
        text="Create blog post about AI marketing automation",
        context={
            "content_type": "blog_post",
            "stated_goals": "educate and convert"
        }
    )
    print(f"   ✓ Intent: {intent['primary']['category']}")

    # Step 2: Extract relevant entities
    print("\n2. Extracting entities from topic...")
    entities = await entity_extractor.extract_specific_entities(
        content="AI marketing automation for B2B SaaS companies",
        entity_types=["TECHNOLOGY", "CONCEPT", "ORGANIZATION"]
    )
    print(f"   ✓ Entities found: {len(entities)}")

    # Step 3: Find similar historical content
    print("\n3. Finding similar historical content...")
    similar = await semantic_similarity.semantic_search(
        query="AI marketing automation",
        documents=SAMPLE_CONTENT_CORPUS,
        top_k=2
    )
    print(f"   ✓ Similar content: {len(similar)} pieces")

    # Step 4: [Content would be generated here]
    print("\n4. [Content generation...]")
    generated_content = SAMPLE_BLOG_POST  # Using sample as placeholder

    # Step 5: Validate emotional resonance
    print("\n5. Validating emotional resonance...")
    emotional = await emotional_intelligence_agent.analyze_emotional_journey(
        content=generated_content
    )
    print(f"   ✓ Resonance score: {emotional['emotional_resonance']['overall_resonance']:.2f}")

    # Step 6: Extract and store topics
    print("\n6. Extracting topics for future reference...")
    topics = await topic_modeler.extract_topics(
        content=generated_content
    )
    print(f"   ✓ Topics extracted: {len(topics['topics'])}")

    # Step 7: Store with embedding for similarity search
    print("\n7. Storing content with embedding...")
    await semantic_similarity.store_content_with_embedding(
        workspace_id="test_workspace",
        content_id="test_content_001",
        content=generated_content,
        metadata={
            "content_type": "blog_post",
            "intent": intent['primary']['category'],
            "resonance_score": emotional['emotional_resonance']['overall_resonance']
        }
    )
    print(f"   ✓ Content stored with semantic embedding")

    print("\n✓ Complete workflow executed successfully!")

    return {
        "intent": intent,
        "entities": entities,
        "similar_content": similar,
        "emotional_analysis": emotional,
        "topics": topics
    }


async def run_all_tests():
    """Run all semantic layer tests."""
    print("\n" + "="*80)
    print("SEMANTIC INTELLIGENCE LAYER - COMPREHENSIVE TEST SUITE")
    print("="*80)

    results = {}

    try:
        results['intent_detection'] = await test_intent_detection()
        results['entity_extraction'] = await test_entity_extraction()
        results['emotional_intelligence'] = await test_emotional_intelligence()
        results['topic_modeling'] = await test_topic_modeling()
        results['semantic_similarity'] = await test_semantic_similarity()
        results['integration_workflow'] = await test_integration_workflow()

        print("\n" + "="*80)
        print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
        print("="*80)

        # Save results to file
        with open('semantic_test_results.json', 'w') as f:
            # Convert non-serializable objects to strings
            serializable_results = json.dumps(results, indent=2, default=str)
            f.write(serializable_results)

        print("\nResults saved to: semantic_test_results.json")

        return results

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # Run tests
    print("Starting Semantic Layer Tests...")
    print("This will demonstrate all capabilities with sample data.\n")

    asyncio.run(run_all_tests())
