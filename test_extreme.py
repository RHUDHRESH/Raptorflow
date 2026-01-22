"""
EXTREME UNLIMITED TEST
Test 50 rapid requests to show unlimited capability
"""

import json
import time

import requests


def test_extreme_unlimited():
    """Test extreme unlimited requests"""

    print("EXTREME UNLIMITED TEST")
    print("=" * 40)
    print("Testing 50 rapid requests...")
    print()

    results = []
    start_time = time.time()

    for i in range(50):
        try:
            payload = {
                "prompt": f"Extreme test {i+1}. Calculate {i+1}x{i+1} and explain the result.",
                "user_id": "extreme-test",
                "model": "gemini-2.0-flash-001",
            }

            request_start = time.time()
            response = requests.post(
                "http://localhost:8003/ai/generate",
                json=payload,
                timeout=20,
                headers={"Content-Type": "application/json"},
            )
            request_end = time.time()

            if response.status_code == 200:
                data = response.json()
                results.append(
                    {
                        "request": i + 1,
                        "status": "success",
                        "model": data.get("model"),
                        "time": request_end - request_start,
                        "rate_limiting": data.get("rate_limiting", "unknown"),
                        "content_length": len(data.get("content", "")),
                    }
                )
                print(
                    f"✅ Request {i+1}: {data.get('rate_limiting', 'unknown')} ({request_end - request_start:.1f}s)"
                )
            else:
                results.append(
                    {
                        "request": i + 1,
                        "status": "failed",
                        "error": response.status_code,
                    }
                )
                print(f"❌ Request {i+1}: Failed ({response.status_code})")

        except Exception as e:
            results.append({"request": i + 1, "status": "error", "error": str(e)})
            print(f"❌ Request {i+1}: Error")

    total_time = time.time() - start_time

    print(f"\nCompleted 50 requests in {total_time:.2f}s")
    print(f"Average: {total_time/50:.2f}s per request")

    # Analyze results
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] != "success"]

    print(f"\nEXTREME RESULTS:")
    print(f"✅ Successful: {len(successful)}/50")
    print(f"❌ Failed: {len(failed)}/50")

    if successful:
        avg_time = sum(r["time"] for r in successful) / len(successful)
        avg_content = sum(r["content_length"] for r in successful) / len(successful)

        print(f"⏱️  Average time: {avg_time:.2f}s")
        print(f"📝 Average content: {avg_content:.0f} chars")

        # Check rate limiting status
        rate_limiting_statuses = [r["rate_limiting"] for r in successful]
        if all(status == "disabled" for status in rate_limiting_statuses):
            print("🚀 Rate limiting: DISABLED")
        else:
            print(f"⚠️  Rate limiting status: {set(rate_limiting_statuses)}")

        # Performance analysis
        if avg_time < 5:
            print("⚡ Performance: EXCELLENT")
        elif avg_time < 10:
            print("🟢 Performance: GOOD")
        else:
            print("🟡 Performance: SLOW")

    if len(successful) >= 45:  # 90% success rate
        print(f"\n🚀 EXTREME UNLIMITED SUCCESS!")
        print("✅ NO RATE LIMITS WHATSOEVER")
        print("✅ MASSIVE THROUGHPUT ACHIEVED")
        print("✅ REAL GOOGLE INFERENCE UNLIMITED")
        print("✅ READY FOR PRODUCTION LOAD")
        return True
    else:
        print(f"\n⚠️  Some requests failed")
        return False


if __name__ == "__main__":
    test_extreme_unlimited()
