"""
Memory System Example - Demonstrating RaptorFlow Memory Architecture

This script demonstrates how to use the comprehensive memory system in RaptorFlow.
It shows examples of:
- Storing and retrieving conversation history
- Tracking agent performance and learning
- Managing workspace context
- Performing semantic search
- Aggregating context from all memory types

Prerequisites:
--------------
- Redis running on localhost:6379 (or configured in settings)
- Supabase database configured (or workspace_memory table created)
- sentence-transformers and chromadb installed

Usage:
------
python backend/examples/memory_system_example.py

Note: This example requires a valid workspace_id. Update the WORKSPACE_ID
constant below with your actual workspace UUID.
"""

import asyncio
from uuid import UUID, uuid4
from datetime import datetime
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer()
    ]
)

from memory.memory_manager import MemoryManager
from memory.base import MemoryError

logger = structlog.get_logger()

# Configuration - Update these with your actual values
WORKSPACE_ID = UUID("00000000-0000-0000-0000-000000000001")  # Replace with actual workspace ID
SESSION_ID = f"session:{uuid4().hex[:8]}"


async def example_conversation_memory(memory: MemoryManager):
    """
    Demonstrate conversation memory usage.

    Conversation memory stores short-term session-based message history
    with automatic expiration (TTL: 1 hour).
    """
    print("\n" + "="*80)
    print("CONVERSATION MEMORY EXAMPLE")
    print("="*80)

    try:
        # Store conversation messages
        messages = [
            {"role": "user", "content": "I want to create a campaign for tech startups"},
            {"role": "assistant", "content": "Great! I'll help you create a campaign targeting tech startups."},
            {"role": "user", "content": "Focus on AI and machine learning companies"},
            {"role": "assistant", "content": "Understood. I'll tailor the campaign for AI/ML companies."}
        ]

        for message in messages:
            await memory.remember(
                memory_type="conversation",
                key=SESSION_ID,
                value=message,
                workspace_id=WORKSPACE_ID
            )
            logger.info("Stored message", role=message["role"])

        # Retrieve conversation history
        history = await memory.recall(
            memory_type="conversation",
            key=SESSION_ID,
            workspace_id=WORKSPACE_ID
        )

        logger.info("Retrieved conversation", message_count=len(history))
        print(f"\nConversation history ({len(history)} messages):")
        for i, msg in enumerate(history, 1):
            print(f"  {i}. [{msg['role']}]: {msg['content']}")

        # Search in conversation
        results = await memory.search(
            query="AI",
            memory_type="conversation",
            workspace_id=WORKSPACE_ID,
            top_k=2
        )

        print(f"\nSearch results for 'AI': {len(results)} matches")
        for result in results:
            print(f"  - {result.get('content', '')[:80]}")

    except MemoryError as e:
        logger.error("Conversation memory error", error=str(e))


async def example_agent_memory(memory: MemoryManager):
    """
    Demonstrate agent memory usage for tracking performance and learning.

    Agent memory stores agent-specific patterns, successes, failures,
    and continuously learns from feedback.
    """
    print("\n" + "="*80)
    print("AGENT MEMORY EXAMPLE")
    print("="*80)

    try:
        agent_name = "campaign_planner"

        # Simulate feedback from multiple tasks
        feedbacks = [
            {"success": True, "rating": 5, "strategy": "persona_targeted", "execution_time": 12.5},
            {"success": True, "rating": 4, "strategy": "persona_targeted", "execution_time": 10.2},
            {"success": False, "rating": 2, "strategy": "broad_reach", "execution_time": 15.8},
            {"success": True, "rating": 5, "strategy": "persona_targeted", "execution_time": 11.0},
        ]

        for i, feedback in enumerate(feedbacks, 1):
            await memory.learn_from_feedback(
                agent_name=agent_name,
                feedback=feedback,
                workspace_id=WORKSPACE_ID
            )
            logger.info(f"Processed feedback {i}/{len(feedbacks)}", success=feedback["success"])

        # Retrieve agent memory
        agent_data = await memory.recall(
            memory_type="agent",
            key=agent_name,
            workspace_id=WORKSPACE_ID
        )

        print(f"\nAgent: {agent_name}")
        print(f"  Total tasks: {agent_data.get('total_tasks', 0)}")
        print(f"  Successful: {agent_data.get('successful_tasks', 0)}")
        print(f"  Failed: {agent_data.get('failed_tasks', 0)}")
        print(f"  Success rate: {agent_data.get('success_rate', 0):.2%}")

        patterns = agent_data.get('patterns', {})
        if patterns:
            print("\n  Learned patterns:")
            for strategy, stats in patterns.items():
                print(f"    - {strategy}: {stats.get('count', 0)} uses, "
                      f"avg rating: {stats.get('avg_rating', 0):.1f}")

        # Search for high-performing agents
        high_performers = await memory.search(
            query="high_success",
            memory_type="agent",
            workspace_id=WORKSPACE_ID,
            filters={"min_success_rate": 0.5},
            top_k=5
        )

        print(f"\nHigh-performing agents: {len(high_performers)}")
        for agent in high_performers:
            print(f"  - {agent['agent_name']}: {agent['success_rate']:.2%} "
                  f"({agent['total_tasks']} tasks)")

    except MemoryError as e:
        logger.error("Agent memory error", error=str(e))


async def example_workspace_memory(memory: MemoryManager):
    """
    Demonstrate workspace memory for shared context.

    Workspace memory stores shared information like brand voice,
    ICPs, and preferences that all agents can access.
    """
    print("\n" + "="*80)
    print("WORKSPACE MEMORY EXAMPLE")
    print("="*80)

    try:
        # Store brand voice
        brand_voice = {
            "tone": "professional yet approachable",
            "values": ["innovation", "transparency", "customer success"],
            "avoid": ["technical jargon", "overpromising", "corporate speak"],
            "voice_characteristics": {
                "personality": "helpful expert",
                "formality": "semi-formal",
                "humor": "light, when appropriate"
            }
        }

        await memory.remember(
            memory_type="workspace",
            key="brand_voice",
            value=brand_voice,
            workspace_id=WORKSPACE_ID,
            metadata={"memory_type": "brand_voice", "version": "1.0"}
        )
        logger.info("Stored brand voice")

        # Store ICP
        icp_enterprise = {
            "name": "Enterprise Tech Companies",
            "company_size": "500-5000 employees",
            "industry": "Technology / SaaS",
            "pain_points": [
                "Scaling marketing operations",
                "Attribution and ROI tracking",
                "Personalization at scale"
            ],
            "decision_makers": ["CMO", "VP Marketing", "Head of Growth"],
            "budget_range": "$50k-$500k annually"
        }

        await memory.remember(
            memory_type="workspace",
            key="icp_enterprise",
            value=icp_enterprise,
            workspace_id=WORKSPACE_ID,
            metadata={"memory_type": "icp", "segment": "enterprise"}
        )
        logger.info("Stored ICP")

        # Retrieve brand voice
        retrieved_brand = await memory.recall(
            memory_type="workspace",
            key="brand_voice",
            workspace_id=WORKSPACE_ID
        )

        print("\nBrand Voice:")
        print(f"  Tone: {retrieved_brand.get('tone', 'N/A')}")
        print(f"  Values: {', '.join(retrieved_brand.get('values', []))}")

        # Search for ICPs
        icps = await memory.search(
            query="enterprise",
            memory_type="workspace",
            workspace_id=WORKSPACE_ID,
            filters={"memory_type": "icp"},
            top_k=5
        )

        print(f"\nICPs found: {len(icps)}")
        for icp in icps:
            value = icp.get('value', {})
            print(f"  - {value.get('name', 'Unknown')}: {value.get('company_size', 'N/A')}")

    except MemoryError as e:
        logger.error("Workspace memory error", error=str(e))


async def example_semantic_memory(memory: MemoryManager):
    """
    Demonstrate semantic memory for vector-based search.

    Semantic memory enables finding content based on meaning
    rather than exact keyword matches.
    """
    print("\n" + "="*80)
    print("SEMANTIC MEMORY EXAMPLE")
    print("="*80)

    try:
        # Store various campaign descriptions
        campaigns = [
            {
                "id": "campaign_001",
                "text": "AI-powered marketing automation for enterprise SaaS companies",
                "type": "campaign"
            },
            {
                "id": "campaign_002",
                "text": "Social media strategy for tech startups targeting millennials",
                "type": "campaign"
            },
            {
                "id": "campaign_003",
                "text": "Content marketing focused on machine learning and data science",
                "type": "campaign"
            },
            {
                "id": "campaign_004",
                "text": "Email drip campaign for B2B software solutions",
                "type": "campaign"
            }
        ]

        for campaign in campaigns:
            await memory.remember(
                memory_type="semantic",
                key=campaign["id"],
                value=campaign["text"],
                workspace_id=WORKSPACE_ID,
                metadata={
                    "content_type": campaign["type"],
                    "campaign_id": campaign["id"]
                }
            )
            logger.info("Stored campaign for semantic search", campaign_id=campaign["id"])

        # Semantic search - find campaigns about AI/ML
        query = "artificial intelligence and automation"
        results = await memory.search(
            query=query,
            memory_type="semantic",
            workspace_id=WORKSPACE_ID,
            top_k=3
        )

        print(f"\nSemantic search for: '{query}'")
        print(f"Found {len(results)} similar campaigns:")
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. [{result.get('id')}] "
                  f"(similarity: {result.get('similarity', 0):.3f})")
            print(f"     {result.get('text', '')}")

    except MemoryError as e:
        logger.error("Semantic memory error", error=str(e))


async def example_get_context(memory: MemoryManager):
    """
    Demonstrate getting comprehensive context for a task.

    The get_context method aggregates relevant information from
    all memory types to provide complete context for agent execution.
    """
    print("\n" + "="*80)
    print("GET CONTEXT EXAMPLE")
    print("="*80)

    try:
        # Get comprehensive context for campaign planning
        context = await memory.get_context(
            workspace_id=WORKSPACE_ID,
            task_type="campaign_planning",
            session_id=SESSION_ID,
            include_semantic=True
        )

        print("\nContext for campaign planning task:")
        print(f"\n  Conversation history: {len(context.get('conversation_history', []))} messages")

        agent_patterns = context.get('agent_patterns', {})
        if agent_patterns:
            print(f"\n  Agent patterns:")
            print(f"    Success rate: {agent_patterns.get('success_rate', 0):.2%}")
            print(f"    Total tasks: {agent_patterns.get('total_tasks', 0)}")

        workspace_ctx = context.get('workspace_context', {})
        if workspace_ctx:
            print(f"\n  Workspace context:")
            brand = workspace_ctx.get('brand_voice')
            if brand:
                print(f"    Brand tone: {brand.get('tone', 'N/A')}")
            icps = workspace_ctx.get('icps', [])
            print(f"    ICPs available: {len(icps)}")

        relevant_content = context.get('relevant_content', [])
        print(f"\n  Semantically relevant content: {len(relevant_content)} items")

        print("\n  This context can now be used by agents to make informed decisions!")

    except MemoryError as e:
        logger.error("Get context error", error=str(e))


async def main():
    """
    Main function to run all examples.
    """
    print("\n" + "="*80)
    print("RAPTORFLOW MEMORY SYSTEM EXAMPLES")
    print("="*80)
    print(f"\nWorkspace ID: {WORKSPACE_ID}")
    print(f"Session ID: {SESSION_ID}")

    # Initialize memory manager
    memory = MemoryManager()

    try:
        # Run examples
        await example_conversation_memory(memory)
        await example_agent_memory(memory)
        await example_workspace_memory(memory)
        await example_semantic_memory(memory)
        await example_get_context(memory)

        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*80)

    except Exception as e:
        logger.error("Example failed", error=str(e), exc_info=True)

    finally:
        # Cleanup
        print("\nCleaning up memory connections...")
        await memory.close()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
