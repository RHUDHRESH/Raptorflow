import asyncio

from core.fallback import FallbackManager
from services.circuit_breaker import KillSwitchCircuitBreaker
from services.latency_monitor import LatencyMonitor
from services.sanity_check import SystemSanityCheck


async def verify_block_f():
    print("\n--- Manual Verification: Block F (MLOps Guardrails) ---")

    # 1. Test Latency Monitor (Logic only)
    print("1. Testing Latency Monitor P95 calculation...")
    monitor = LatencyMonitor(threshold_ms=1000)
    # 10 normal latencies
    for _ in range(10):
        await monitor.record_and_check("verify_ws", 100.0)
    # One spike
    alert = await monitor.record_and_check("verify_ws", 2000.0)
    print(f"   Latency Alert Triggered: {alert}")

    # 2. Test Fallback Manager
    print("2. Testing Deterministic Fallback...")
    fm = FallbackManager()

    async def failing_task():
        raise ValueError("Simulated LLM Error")

    res = await fm.execute_with_fallback(
        failing_task, fallback_value={"status": "fallback"}
    )
    print(f"   Fallback Result: {res}")

    # 3. Test Circuit Breaker Logic
    print("3. Testing Circuit Breaker logic...")
    cb = KillSwitchCircuitBreaker(drift_threshold=0.1)
    # Should trip on high drift
    tripped = await cb.check_and_trip(
        "verify_ws", drift_score=0.2, reason="Drift Spike"
    )
    print(f"   Circuit Breaker Tripped: {tripped}")

    print("\n--- Block F Verification Complete ---")


if __name__ == "__main__":
    asyncio.run(verify_block_f())
