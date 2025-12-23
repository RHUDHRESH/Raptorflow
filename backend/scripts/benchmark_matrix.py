import argparse
import statistics
import time

import requests


def benchmark_matrix(url: str, iterations: int = 10):
    """
    SOTA Performance Benchmarking for Matrix.
    Verifies <200ms latency.
    """
    print(f"SOTA Benchmarking: Starting latency test against {url}")
    latencies = []

    for i in range(iterations):
        start = time.perf_counter()
        res = requests.get(f"{url}/v1/matrix/overview?workspace_id=verify_ws")
        end = time.perf_counter()

        if res.status_code == 200:
            latencies.append((end - start) * 1000)  # ms
        else:
            print(f"Iteration {i} failed: {res.status_code}")

    if not latencies:
        return False

    avg = statistics.mean(latencies)
    p95 = (
        statistics.quantiles(latencies, n=20)[18]
        if len(latencies) >= 20
        else max(latencies)
    )

    print(f"Results: Avg={avg:.2f}ms, P95={p95:.2f}ms")

    if avg < 200:
        print("✓ Performance benchmark PASSED (<200ms avg).")
        return True
    else:
        print("✗ Performance benchmark FAILED (>200ms avg).")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Performance Benchmarking")
    parser.add_argument(
        "--url", help="Base URL of Matrix API", default="http://localhost:8080"
    )

    # In CI/CD we would run it. For now we initialize.
    print("SOTA Benchmarker Initialized.")
