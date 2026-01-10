import json
import time

import requests


def simple_scrape():
    """Simple, fast scraping that just works"""

    urls = [
        "https://www.reddit.com/r/python/hot.json",
        "https://www.reddit.com/r/coffee/hot.json",
        "https://www.reddit.com/r/minnesota/hot.json",
    ]

    print("🚀 SIMPLE SCRAPING")
    print("=" * 30)

    results = []
    start_time = time.time()

    for url in urls:
        try:
            print(f"Scraping: {url}")
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results.append(
                    {
                        "url": url,
                        "posts": len(data.get("data", {}).get("children", [])),
                        "status": "success",
                    }
                )
                print(f"  ✅ Got {len(data.get('data', {}).get('children', []))} posts")
            else:
                print(f"  ❌ Status: {response.status_code}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    total_time = time.time() - start_time

    print(f"\n📊 RESULTS:")
    print(f"   Total URLs: {len(urls)}")
    print(f"   Successful: {len(results)}")
    print(f"   Time: {total_time:.2f}s")
    print(f"   Speed: {len(results)/total_time:.1f} req/s")

    return results


if __name__ == "__main__":
    simple_scrape()
