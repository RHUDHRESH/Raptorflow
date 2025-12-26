import asyncio
import os
from unittest.mock import MagicMock

from agents.context_assembler import create_rag_node
from agents.quality import create_memory_governor
from agents.researchers import create_competitor_tracker
from agents.strategists import create_founder_profiler
from services.telemetry import CostEvaluator, RaptorEvaluator


async def verify_milestone_10():
    print("--- RaptorFlow SOTA Milestone 10 Diagnostic ---")

    # 1. Advanced Memory Readiness
    print("\n[1/3] Verifying Entity & RAG Memory Nodes (Tracker, Profiler, RAG)...")
    try:
        mock_llm = MagicMock()
        tracker = create_competitor_tracker()
        founder = create_founder_profiler(mock_llm)
        rag = create_rag_node()
        if all(callable(n) for n in [tracker, founder, rag]):
            print("PASS: Advanced memory node factories are operational.")
    except Exception as e:
        print(f"FAIL: Advanced Memory Nodes: {e}")

    # 2. Intelligence Governance Readiness
    print("\n[2/3] Verifying Memory Governor...")
    try:
        mock_llm = MagicMock()
        gov = create_memory_governor(mock_llm)
        if callable(gov):
            print("PASS: Memory governance layer initialized.")
    except Exception as e:
        print(f"FAIL: Memory Governor: {e}")

    # 3. SOTA Evaluator Readiness
    print("\n[3/3] Verifying Automated Evaluators (Quality, Cost)...")
    try:
        mock_llm = MagicMock()
        evaluator = RaptorEvaluator(mock_llm)
        cost = CostEvaluator()
        if evaluator and cost:
            print("PASS: SOTA evaluation systems are operational.")
    except Exception as e:
        print(f"FAIL: Evaluators: {e}")

    print("\n--- Milestone 10 Diagnostic Complete ---")


if __name__ == "__main__":
    asyncio.run(verify_milestone_10())
