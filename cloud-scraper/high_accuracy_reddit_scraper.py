"""
High-Accuracy Reddit Scraper - 95%+ Similarity Target
Uses multiple techniques to match web search results accuracy
"""

import json
import re
import statistics
import time
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup


class HighAccuracyRedditScraper:
    """Reddit scraper optimized for 95%+ similarity with web search"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

        # Multiple search engines for validation
        self.search_engines = [
            "https://duckduckgo.com/html/",
            "https://html.search.brave.com/search",
            "https://html.qwant.com/results",
        ]

    def enhanced_reddit_scrape(self, subreddit, sort="hot", limit=25):
        """Enhanced Reddit scraping with multiple data points"""

        print(f"🔴 ENHANCED REDDIT SCRAPE: r/{subreddit}")
        print("=" * 50)

        posts_data = []

        # Try multiple Reddit endpoints for comprehensive data
        endpoints = [
            f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}",
            f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}",
            f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}",
        ]

        for endpoint in endpoints:
            try:
                response = self.session.get(endpoint, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    for post in data.get("data", {}).get("children", []):
                        post_data = post.get("data", {})

                        # Extract comprehensive data
                        title = post_data.get("title", "")
                        selftext = post_data.get("selftext", "")
                        url = post_data.get("url", "")
                        score = post_data.get("score", 0)
                        comments = post_data.get("num_comments", 0)
                        author = post_data.get("author", "")
                        created_utc = post_data.get("created_utc", 0)
                        subreddit_name = post_data.get("subreddit", "")
                        flair = post_data.get("link_flair_text", "")

                        # Extract keywords from title and content
                        all_text = f"{title} {selftext}".lower()
                        keywords = self._extract_keywords(all_text)

                        post_info = {
                            "title": title,
                            "selftext": selftext[:200],  # First 200 chars
                            "url": url,
                            "score": score,
                            "comments": comments,
                            "author": author,
                            "created_utc": created_utc,
                            "created_date": datetime.fromtimestamp(
                                created_utc
                            ).strftime("%Y-%m-%d"),
                            "subreddit": subreddit_name,
                            "flair": flair,
                            "keywords": keywords,
                            "text_length": len(title + selftext),
                        }

                        # Avoid duplicates
                        if not any(
                            p["title"] == post_info["title"] for p in posts_data
                        ):
                            posts_data.append(post_info)

                    print(f"✅ Scraped {len(posts_data)} posts from {endpoint}")
                    break  # Success, no need to try other endpoints

                else:
                    print(
                        f"⚠️  Endpoint failed: {endpoint} (HTTP {response.status_code})"
                    )

            except Exception as e:
                print(f"❌ Error with {endpoint}: {e}")

        # Sort by score and comments (engagement)
        posts_data.sort(key=lambda x: (x["score"] + x["comments"]), reverse=True)

        print(f"📊 Final: {len(posts_data)} unique posts from r/{subreddit}")
        return posts_data[:limit]

    def multi_engine_web_search(self, query, num_results=15):
        """Search multiple engines for better validation"""

        print(f"🔍 MULTI-ENGINE WEB SEARCH: {query}")
        print("=" * 50)

        all_results = []

        for engine_url in self.search_engines:
            try:
                params = {"q": query}

                if "brave" in engine_url:
                    params["source"] = "web"
                elif "qwant" in engine_url:
                    params["t"] = "web"

                response = self.session.get(engine_url, params=params, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")

                    engine_results = []

                    # Parse based on engine
                    if "duckduckgo" in engine_url:
                        result_divs = soup.find_all("div", class_="result")
                        for result_div in result_divs[:num_results]:
                            title_tag = result_div.find("a", class_="result__a")
                            snippet_tag = result_div.find("a", class_="result__snippet")

                            if title_tag:
                                title = title_tag.get_text(strip=True)
                                snippet = (
                                    snippet_tag.get_text(strip=True)
                                    if snippet_tag
                                    else ""
                                )
                                keywords = self._extract_keywords(f"{title} {snippet}")

                                engine_results.append(
                                    {
                                        "title": title,
                                        "snippet": snippet,
                                        "keywords": keywords,
                                        "engine": "duckduckgo",
                                    }
                                )

                    elif "brave" in engine_url:
                        result_divs = soup.find_all("div", {"data-type": "web"})
                        for result_div in result_divs[:num_results]:
                            title_tag = result_div.find("a")
                            snippet_tag = result_div.find(
                                "div", class_="snippet-description"
                            )

                            if title_tag:
                                title = title_tag.get_text(strip=True)
                                snippet = (
                                    snippet_tag.get_text(strip=True)
                                    if snippet_tag
                                    else ""
                                )
                                keywords = self._extract_keywords(f"{title} {snippet}")

                                engine_results.append(
                                    {
                                        "title": title,
                                        "snippet": snippet,
                                        "keywords": keywords,
                                        "engine": "brave",
                                    }
                                )

                    elif "qwant" in engine_url:
                        result_divs = soup.find_all("div", class_="result")
                        for result_div in result_divs[:num_results]:
                            title_tag = result_div.find("a", class_="result--web")
                            snippet_tag = result_div.find("p", class_="result__desc")

                            if title_tag:
                                title = title_tag.get_text(strip=True)
                                snippet = (
                                    snippet_tag.get_text(strip=True)
                                    if snippet_tag
                                    else ""
                                )
                                keywords = self._extract_keywords(f"{title} {snippet}")

                                engine_results.append(
                                    {
                                        "title": title,
                                        "snippet": snippet,
                                        "keywords": keywords,
                                        "engine": "qwant",
                                    }
                                )

                    all_results.extend(engine_results)
                    print(
                        f"✅ {engine_url.split('//')[1].split('.')[0]}: {len(engine_results)} results"
                    )

                else:
                    print(f"❌ {engine_url}: HTTP {response.status_code}")

            except Exception as e:
                print(f"❌ Error with {engine_url}: {e}")

        # Remove duplicates
        seen_titles = set()
        unique_results = []
        for result in all_results:
            title_lower = result["title"].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_results.append(result)

        print(f"📊 Total unique results: {len(unique_results)}")
        return unique_results

    def _extract_keywords(self, text):
        """Extract meaningful keywords"""

        # Clean and tokenize
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

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
            "this",
            "that",
            "these",
            "those",
            "what",
            "which",
            "who",
            "when",
            "where",
            "why",
            "how",
            "just",
            "like",
            "get",
            "got",
            "make",
            "made",
            "take",
            "took",
        }

        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        # Count frequency
        keyword_freq = {}
        for keyword in keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1

        return sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    def calculate_similarity(self, reddit_posts, web_results):
        """Calculate comprehensive similarity score"""

        print(f"📊 CALCULATING SIMILARITY")
        print("=" * 50)

        # Extract all keywords
        reddit_keywords = []
        web_keywords = []

        for post in reddit_posts:
            reddit_keywords.extend([kw[0] for kw in post["keywords"]])

        for result in web_results:
            web_keywords.extend([kw[0] for kw in result["keywords"]])

        # Create frequency dictionaries
        reddit_freq = {}
        web_freq = {}

        for kw in reddit_keywords:
            reddit_freq[kw] = reddit_freq.get(kw, 0) + 1

        for kw in web_keywords:
            web_freq[kw] = web_freq.get(kw, 0) + 1

        # Find common keywords
        reddit_set = set(reddit_freq.keys())
        web_set = set(web_freq.keys())
        common_keywords = reddit_set.intersection(web_set)

        # Calculate similarity metrics
        if reddit_set and web_set:
            jaccard_similarity = len(common_keywords) / len(reddit_set.union(web_set))
        else:
            jaccard_similarity = 0

        # Weighted similarity (by frequency)
        weighted_common = 0
        total_weight = 0

        for keyword in common_keywords:
            reddit_weight = reddit_freq[keyword]
            web_weight = web_freq[keyword]
            weighted_common += min(reddit_weight, web_weight)
            total_weight += max(reddit_weight, web_weight)

        if total_weight > 0:
            weighted_similarity = weighted_common / total_weight
        else:
            weighted_similarity = 0

        # Topic similarity (top keywords)
        reddit_top = set(
            [
                kw[0]
                for kw in sorted(reddit_freq.items(), key=lambda x: x[1], reverse=True)[
                    :10
                ]
            ]
        )
        web_top = set(
            [
                kw[0]
                for kw in sorted(web_freq.items(), key=lambda x: x[1], reverse=True)[
                    :10
                ]
            ]
        )
        topic_similarity = (
            len(reddit_top.intersection(web_top)) / len(reddit_top.union(web_top))
            if reddit_top.union(web_top)
            else 0
        )

        # Overall similarity (weighted average)
        overall_similarity = (
            jaccard_similarity * 0.3
            + weighted_similarity * 0.4
            + topic_similarity * 0.3
        )

        print(f"📈 Jaccard Similarity: {jaccard_similarity:.2%}")
        print(f"📈 Weighted Similarity: {weighted_similarity:.2%}")
        print(f"📈 Topic Similarity: {topic_similarity:.2%}")
        print(f"📈 Overall Similarity: {overall_similarity:.2%}")
        print(f"🔍 Common Keywords: {len(common_keywords)}")
        print(f"📝 Reddit Keywords: {len(reddit_set)}")
        print(f"🌐 Web Keywords: {len(web_set)}")

        return {
            "overall_similarity": overall_similarity,
            "jaccard_similarity": jaccard_similarity,
            "weighted_similarity": weighted_similarity,
            "topic_similarity": topic_similarity,
            "common_keywords": len(common_keywords),
            "reddit_keywords": len(reddit_set),
            "web_keywords": len(web_set),
            "top_common_keywords": sorted(list(common_keywords))[:10],
        }

    def analyze_content_quality(self, reddit_posts, web_results):
        """Analyze content quality for improvement suggestions"""

        print(f"🔍 CONTENT QUALITY ANALYSIS")
        print("=" * 50)

        # Reddit content analysis
        reddit_scores = [post["score"] for post in reddit_posts]
        reddit_comments = [post["comments"] for post in reddit_posts]
        reddit_lengths = [post["text_length"] for post in reddit_posts]

        avg_score = statistics.mean(reddit_scores) if reddit_scores else 0
        avg_comments = statistics.mean(reddit_comments) if reddit_comments else 0
        avg_length = statistics.mean(reddit_lengths) if reddit_lengths else 0

        # Web content analysis
        web_lengths = [
            len(result["title"] + " " + result["snippet"]) for result in web_results
        ]
        avg_web_length = statistics.mean(web_lengths) if web_lengths else 0

        print(f"📊 Reddit Stats:")
        print(f"   Avg Score: {avg_score:.1f}")
        print(f"   Avg Comments: {avg_comments:.1f}")
        print(f"   Avg Length: {avg_length:.1f} chars")

        print(f"📊 Web Stats:")
        print(f"   Avg Length: {avg_web_length:.1f} chars")

        # Quality assessment
        quality_issues = []

        if avg_score < 10:
            quality_issues.append("Low Reddit engagement scores")

        if avg_comments < 5:
            quality_issues.append("Low Reddit comment activity")

        if avg_length < 100:
            quality_issues.append("Short Reddit content")

        if len(reddit_posts) < 20:
            quality_issues.append("Limited Reddit sample size")

        if len(web_results) < 10:
            quality_issues.append("Limited web search results")

        if quality_issues:
            print(f"⚠️  Quality Issues:")
            for issue in quality_issues:
                print(f"   • {issue}")
        else:
            print(f"✅ Content quality looks good")

        return {
            "avg_reddit_score": avg_score,
            "avg_reddit_comments": avg_comments,
            "avg_reddit_length": avg_length,
            "avg_web_length": avg_web_length,
            "quality_issues": quality_issues,
        }

    def run_accuracy_test(self, subreddit, topic):
        """Run comprehensive accuracy test"""

        print(f"🧪 ACCURACY TEST: r/{subreddit} vs '{topic}'")
        print("=" * 80)

        # Step 1: Enhanced Reddit scraping
        reddit_posts = self.enhanced_reddit_scrape(subreddit)

        # Step 2: Multi-engine web search
        web_results = self.multi_engine_web_search(topic)

        if not reddit_posts or not web_results:
            print(f"❌ Insufficient data for comparison")
            return None

        # Step 3: Calculate similarity
        similarity = self.calculate_similarity(reddit_posts, web_results)

        # Step 4: Analyze content quality
        quality = self.analyze_content_quality(reddit_posts, web_results)

        # Step 5: Determine if 95%+ target met
        target_met = similarity["overall_similarity"] >= 0.95

        print(f"\n🎯 ACCURACY RESULT:")
        print(f"   Target 95%+: {'✅ MET' if target_met else '❌ NOT MET'}")
        print(f"   Actual: {similarity['overall_similarity']:.2%}")

        # Step 6: Improvement suggestions if needed
        if not target_met:
            print(f"\n💡 IMPROVEMENT SUGGESTIONS:")

            if similarity["common_keywords"] < 10:
                print(f"   • Increase Reddit sample size for more keywords")

            if quality["quality_issues"]:
                print(
                    f"   • Address quality issues: {', '.join(quality['quality_issues'])}"
                )

            if similarity["topic_similarity"] < 0.5:
                print(f"   • Focus on top-trending topics in subreddit")

            print(f"   • Try different sort orders (hot, new, top)")
            print(f"   • Expand time range for more posts")

        return {
            "subreddit": subreddit,
            "topic": topic,
            "similarity": similarity,
            "quality": quality,
            "target_met": target_met,
            "reddit_posts_count": len(reddit_posts),
            "web_results_count": len(web_results),
        }


def main():
    """Main execution - achieve 95%+ similarity"""

    print("🎯 HIGH-ACCURACY REDDIT SCRAPER")
    print("=" * 80)
    print("Target: 95%+ similarity with web search results")
    print("Using multi-engine search and enhanced scraping techniques")
    print()

    scraper = HighAccuracyRedditScraper()

    # Test cases with high correlation potential
    test_cases = [
        {"subreddit": "python", "topic": "python programming tutorial"},
        {"subreddit": "MachineLearning", "topic": "machine learning algorithms"},
        {"subreddit": "webdev", "topic": "web development javascript"},
        {"subreddit": "startups", "topic": "startup funding advice"},
        {"subreddit": "coffee", "topic": "coffee brewing methods"},
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 TEST {i}/{len(test_cases)}")
        print(f"Subreddit: r/{test_case['subreddit']}")
        print(f"Topic: {test_case['topic']}")
        print()

        result = scraper.run_accuracy_test(test_case["subreddit"], test_case["topic"])

        if result:
            results.append(result)

            print(
                f"⏱️  Test {i} complete: {result['similarity']['overall_similarity']:.2%} similarity"
            )

        print("=" * 80)
        print()

    # Summary
    if results:
        avg_similarity = statistics.mean(
            [r["similarity"]["overall_similarity"] for r in results]
        )
        target_met_count = sum([1 for r in results if r["target_met"]])

        print(f"📊 SUMMARY")
        print("=" * 80)
        print(f"Tests completed: {len(results)}")
        print(f"Average similarity: {avg_similarity:.2%}")
        print(f"95%+ target met: {target_met_count}/{len(results)}")

        if avg_similarity >= 0.95:
            print(f"✅ SUCCESS: Average similarity meets 95%+ target!")
        elif avg_similarity >= 0.80:
            print(
                f"⚠️  CLOSE: Average similarity {avg_similarity:.2%} - needs refinement"
            )
        else:
            print(
                f"❌ NEEDS WORK: Average similarity {avg_similarity:.2%} - requires improvement"
            )


if __name__ == "__main__":
    main()
