"""
Reddit Scraper Validation Test
Actually scrapes Reddit and compares with web search results
No async wrappers, no hardcoded prompts, direct scraping only
"""

import json
import re
import time
from datetime import datetime
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup


class RedditScraperTest:
    """Direct Reddit scraper with validation against web search"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

    def scrape_reddit_subreddit(self, subreddit_name, limit=25):
        """Actually scrape Reddit subreddit using .json endpoint"""

        print(f"🔴 SCRAPING REDDIT: r/{subreddit_name}")

        try:
            # Reddit .json endpoint - no API key required
            url = f"https://www.reddit.com/r/{subreddit_name}/new.json?limit={limit}"

            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                posts = []
                for post in data.get("data", {}).get("children", []):
                    post_data = post.get("data", {})

                    posts.append(
                        {
                            "title": post_data.get("title", ""),
                            "url": post_data.get("url", ""),
                            "score": post_data.get("score", 0),
                            "comments": post_data.get("num_comments", 0),
                            "created_utc": post_data.get("created_utc", 0),
                            "subreddit": post_data.get("subreddit", ""),
                            "author": post_data.get("author", ""),
                            "selftext": post_data.get("selftext", "")[
                                :200
                            ],  # First 200 chars
                        }
                    )

                print(f"✅ Reddit scraped: {len(posts)} posts from r/{subreddit_name}")
                return posts

            else:
                print(f"❌ Reddit scrape failed: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Reddit scrape error: {e}")
            return []

    def web_search_validation(self, query, num_results=10):
        """Search web for validation - no API keys"""

        print(f"🔍 WEB SEARCH: {query}")

        try:
            # DuckDuckGo HTML search
            search_url = "https://duckduckgo.com/html/"
            params = {"q": query}

            response = self.session.get(search_url, params=params, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                results = []
                result_divs = soup.find_all("div", class_="result")

                for result_div in result_divs[:num_results]:
                    title_tag = result_div.find("a", class_="result__a")
                    snippet_tag = result_div.find("a", class_="result__snippet")

                    if title_tag:
                        title = title_tag.get_text(strip=True)
                        url = title_tag.get("href", "")
                        snippet = (
                            snippet_tag.get_text(strip=True) if snippet_tag else ""
                        )

                        results.append(
                            {
                                "title": title,
                                "url": url,
                                "snippet": snippet,
                                "source": "duckduckgo",
                            }
                        )

                print(f"✅ Web search: {len(results)} results for '{query}'")
                return results

            else:
                print(f"❌ Web search failed: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Web search error: {e}")
            return []

    def extract_keywords(self, text):
        """Extract keywords from text"""

        # Simple keyword extraction
        words = re.findall(r"\b\w+\b", text.lower())

        # Filter out common words
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "must",
        }

        keywords = [word for word in words if len(word) > 2 and word not in stop_words]

        # Count frequency
        keyword_freq = {}
        for keyword in keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1

        return sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    def compare_results(self, reddit_posts, web_results, topic):
        """Compare Reddit posts with web search results"""

        print(f"\n📊 COMPARING RESULTS for: {topic}")
        print("=" * 50)

        # Extract keywords from both sources
        reddit_text = " ".join(
            [post["title"] + " " + post.get("selftext", "") for post in reddit_posts]
        )
        web_text = " ".join(
            [result["title"] + " " + result["snippet"] for result in web_results]
        )

        reddit_keywords = self.extract_keywords(reddit_text)
        web_keywords = self.extract_keywords(web_text)

        # Find common keywords
        reddit_keyword_set = set([kw[0] for kw in reddit_keywords])
        web_keyword_set = set([kw[0] for kw in web_keywords])

        common_keywords = reddit_keyword_set.intersection(web_keyword_set)

        # Calculate similarity score
        if reddit_keyword_set and web_keyword_set:
            similarity = len(common_keywords) / len(
                reddit_keyword_set.union(web_keyword_set)
            )
        else:
            similarity = 0

        print(f"🔍 Reddit keywords: {len(reddit_keyword_set)}")
        print(f"🔍 Web keywords: {len(web_keyword_set)}")
        print(f"🔍 Common keywords: {len(common_keywords)}")
        print(f"📈 Similarity score: {similarity:.2%}")

        # Show top common keywords
        common_keywords_list = []
        for keyword in common_keywords:
            reddit_count = next(
                (count for kw, count in reddit_keywords if kw == keyword), 0
            )
            web_count = next((count for kw, count in web_keywords if kw == keyword), 0)
            common_keywords_list.append((keyword, reddit_count + web_count))

        common_keywords_list.sort(key=lambda x: x[1], reverse=True)

        print(f"\n🔥 TOP COMMON KEYWORDS:")
        for keyword, total_count in common_keywords_list[:5]:
            print(f"  • {keyword}: {total_count} mentions")

        # Validate scraper accuracy
        if similarity > 0.3:
            validation = "✅ SCRAPER ACCURATE"
            confidence = "High"
        elif similarity > 0.15:
            validation = "⚠️  SCRAPER MODERATE"
            confidence = "Medium"
        else:
            validation = "❌ SCRAPER INACCURATE"
            confidence = "Low"

        print(f"\n🎯 VALIDATION: {validation}")
        print(f"📊 Confidence: {confidence}")

        return {
            "topic": topic,
            "reddit_posts": len(reddit_posts),
            "web_results": len(web_results),
            "similarity_score": similarity,
            "common_keywords": len(common_keywords),
            "validation": validation,
            "confidence": confidence,
            "top_keywords": common_keywords_list[:5],
        }

    def run_parallel_test(self, topic, subreddit):
        """Run parallel test: Reddit scrape + web search validation"""

        print(f"\n🚀 PARALLEL TEST: {topic}")
        print("=" * 60)

        start_time = time.time()

        # Test 1: Reddit scraping
        reddit_posts = self.scrape_reddit_subreddit(subreddit)

        # Test 2: Web search validation
        web_results = self.web_search_validation(topic)

        # Test 3: Compare results
        comparison = self.compare_results(reddit_posts, web_results, topic)

        end_time = time.time()
        comparison["time_elapsed"] = end_time - start_time

        return comparison

    def run_multiple_tests(self):
        """Run multiple tests to remove bias"""

        print("🧪 MULTIPLE VALIDATION TESTS")
        print("=" * 80)
        print("Testing Reddit scraper against web search validation")
        print("No async wrappers, no hardcoded prompts, direct scraping only")
        print()

        # Test cases - different topics and subreddits
        test_cases = [
            {
                "topic": "coffee brewing",
                "subreddit": "coffee",
                "description": "Coffee brewing discussions",
            },
            {
                "topic": "python programming",
                "subreddit": "python",
                "description": "Python programming help",
            },
            {
                "topic": "startup funding",
                "subreddit": "startups",
                "description": "Startup funding discussions",
            },
            {
                "topic": "machine learning",
                "subreddit": "MachineLearning",
                "description": "ML research and discussions",
            },
            {
                "topic": "web development",
                "subreddit": "webdev",
                "description": "Web development techniques",
            },
        ]

        results = []

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 TEST {i}/{len(test_cases)}: {test_case['description']}")
            print(f"Topic: {test_case['topic']}")
            print(f"Subreddit: r/{test_case['subreddit']}")

            result = self.run_parallel_test(test_case["topic"], test_case["subreddit"])
            results.append(result)

            print(f"⏱️  Time: {result['time_elapsed']:.2f}s")
            print(f"📊 Result: {result['validation']} ({result['confidence']})")

            # Small delay between tests
            time.sleep(2)

        # Summary analysis
        print(f"\n📈 SUMMARY ANALYSIS")
        print("=" * 80)

        accurate_tests = [r for r in results if "ACCURATE" in r["validation"]]
        moderate_tests = [r for r in results if "MODERATE" in r["validation"]]
        inaccurate_tests = [r for r in results if "INACCURATE" in r["validation"]]

        avg_similarity = sum(r["similarity_score"] for r in results) / len(results)
        avg_time = sum(r["time_elapsed"] for r in results) / len(results)

        print(f"✅ Accurate tests: {len(accurate_tests)}/{len(results)}")
        print(f"⚠️  Moderate tests: {len(moderate_tests)}/{len(results)}")
        print(f"❌ Inaccurate tests: {len(inaccurate_tests)}/{len(results)}")
        print(f"📊 Average similarity: {avg_similarity:.2%}")
        print(f"⏱️  Average time: {avg_time:.2f}s")

        # Overall validation
        if len(accurate_tests) >= len(results) * 0.6:
            overall_validation = "✅ REDDIT SCRAPER VALIDATED"
            overall_confidence = "HIGH"
        elif len(accurate_tests) + len(moderate_tests) >= len(results) * 0.7:
            overall_validation = "⚠️  REDDIT SCRAPER MODERATE"
            overall_confidence = "MEDIUM"
        else:
            overall_validation = "❌ REDDIT SCRAPER FAILED"
            overall_confidence = "LOW"

        print(f"\n🎯 OVERALL VALIDATION: {overall_validation}")
        print(f"📊 OVERALL CONFIDENCE: {overall_confidence}")

        return results, {
            "accurate_tests": len(accurate_tests),
            "moderate_tests": len(moderate_tests),
            "inaccurate_tests": len(inaccurate_tests),
            "avg_similarity": avg_similarity,
            "avg_time": avg_time,
            "overall_validation": overall_validation,
            "overall_confidence": overall_confidence,
        }


def main():
    """Main execution"""

    print("🔴 REDDIT SCRAPER VALIDATION TEST")
    print("=" * 80)
    print("Actually scraping Reddit and validating against web search")
    print("No async wrappers, no hardcoded prompts, direct scraping only")
    print()

    scraper_test = RedditScraperTest()

    try:
        results, summary = scraper_test.run_multiple_tests()

        print(f"\n🎉 TESTING COMPLETE")
        print("=" * 80)
        print(f"Final Result: {summary['overall_validation']}")
        print(f"Confidence: {summary['overall_confidence']}")
        print(f"Tests Run: {len(results)}")
        print(f"Average Similarity: {summary['avg_similarity']:.2%}")

        if summary["overall_confidence"] == "HIGH":
            print("\n✅ Reddit scraper is ACCURATE and ready for production")
        elif summary["overall_confidence"] == "MEDIUM":
            print("\n⚠️  Reddit scraper is MODERATE - use with caution")
        else:
            print("\n❌ Reddit scraper needs improvement before production")

        return summary["overall_confidence"] == "HIGH"

    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
