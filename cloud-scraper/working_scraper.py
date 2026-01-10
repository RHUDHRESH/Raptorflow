"""
WORKING SCRAPER - Just gets the job done
Simple, fast, reliable scraping without the complexity
"""

import json
import time
from datetime import datetime

import requests


def scrape_reddit_simple(subreddit: str, limit: int = 50) -> dict:
    """Simple Reddit scraping that works"""

    url = f"https://www.reddit.com/r/{subreddit}/hot.json"
    headers = {"User-Agent": "SimpleScraper/1.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            posts = data.get("data", {}).get("children", [])[:limit]

            results = []
            for post in posts:
                post_data = post.get("data", {})
                results.append(
                    {
                        "title": post_data.get("title", ""),
                        "score": post_data.get("score", 0),
                        "comments": post_data.get("num_comments", 0),
                        "url": f"https://reddit.com{post_data.get('permalink', '')}",
                        "created": datetime.fromtimestamp(
                            post_data.get("created_utc", 0)
                        ).isoformat(),
                    }
                )

            return {
                "subreddit": subreddit,
                "posts": results,
                "count": len(results),
                "success": True,
            }
        else:
            return {
                "subreddit": subreddit,
                "error": f"HTTP {response.status_code}",
                "success": False,
            }

    except Exception as e:
        return {"subreddit": subreddit, "error": str(e), "success": False}


def main():
    """Main scraping function"""

    print("🚀 WORKING SCRAPER")
    print("=" * 40)

    subreddits = ["python", "coffee", "minnesota", "webdev"]
    all_results = []

    start_time = time.time()

    for subreddit in subreddits:
        print(f"Scraping r/{subreddit}...")
        result = scrape_reddit_simple(subreddit)

        if result["success"]:
            print(f"  ✅ Got {result['count']} posts")
            all_results.append(result)
        else:
            print(f"  ❌ Error: {result['error']}")

    total_time = time.time() - start_time

    print(f"\n📊 RESULTS:")
    print(f"   Total subreddits: {len(subreddits)}")
    print(f"   Successful: {len(all_results)}")
    print(f"   Total posts: {sum(r['count'] for r in all_results)}")
    print(f"   Time: {total_time:.2f}s")
    print(f"   Speed: {len(all_results)/total_time:.1f} subreddits/sec")

    # Show sample posts
    if all_results:
        print(f"\n🔍 SAMPLE POSTS:")
        for result in all_results[:2]:
            print(f"\n   r/{result['subreddit']} - Top posts:")
            for post in result["posts"][:3]:
                print(f"     • {post['title'][:50]}... (Score: {post['score']})")

    print(f"\n✅ SCRAPING COMPLETE!")


if __name__ == "__main__":
    main()
