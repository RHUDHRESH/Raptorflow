"""
Minnesota Coffee Trends Scraper
Finds the latest coffee trends specifically in Minnesota using validated Reddit scraper
"""

import asyncio
import json
import re
import sqlite3
import statistics
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import aiohttp


class MinnesotaCoffeeTrendsScraper:
    """Specialized scraper for Minnesota coffee trends"""

    def __init__(self, db_path: str = "minnesota_coffee_trends.db"):
        self.db_path = db_path
        self.session = None

        # Minnesota-specific coffee keywords and locations
        self.minnesota_locations = [
            "minneapolis",
            "st paul",
            "saint paul",
            "duluth",
            "rochester",
            "bloomington",
            "brooklyn park",
            "plymouth",
            "eagan",
            "woodbury",
            "lakeville",
            "st cloud",
            "eden prairie",
            "minnetonka",
            "maple grove",
            "north star state",
            "mn",
            "twin cities",
            "metro area",
        ]

        self.coffee_trend_keywords = [
            "coffee shop",
            "cafe",
            "roastery",
            "coffee roaster",
            "espresso",
            "cold brew",
            "nitro coffee",
            "specialty coffee",
            "third wave",
            "coffee beans",
            "local coffee",
            "craft coffee",
            "coffee culture",
            "coffee scene",
            "brew methods",
            "coffee trends",
            "new cafe",
            "coffee opening",
            "coffee event",
            "coffee festival",
            "coffee competition",
        ]

        self._initialize_database()

    def _initialize_database(self):
        """Initialize Minnesota coffee trends database"""

        with sqlite3.connect(self.db_path) as conn:
            # Minnesota coffee trends table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS minnesota_coffee_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subreddit TEXT NOT NULL,
                    post_title TEXT NOT NULL,
                    post_content TEXT,
                    score INTEGER,
                    comments INTEGER,
                    author TEXT,
                    created_utc REAL,
                    minnesota_mentions INTEGER DEFAULT 0,
                    coffee_mentions INTEGER DEFAULT 0,
                    trend_score REAL DEFAULT 0.0,
                    locations_found TEXT,
                    coffee_terms_found TEXT,
                    scraped_at DATETIME NOT NULL
                )
            """
            )

            # Trend analysis table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trend_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_date DATETIME NOT NULL,
                    total_posts INTEGER NOT NULL,
                    minnesota_related INTEGER NOT NULL,
                    coffee_related INTEGER NOT NULL,
                    top_locations TEXT,
                    top_coffee_terms TEXT,
                    trend_summary TEXT,
                    confidence_score REAL DEFAULT 0.0
                )
            """
            )

            # Hot locations table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS hot_locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location TEXT NOT NULL,
                    mention_count INTEGER NOT NULL,
                    trend_score REAL DEFAULT 0.0,
                    last_updated DATETIME NOT NULL
                )
            """
            )

            conn.commit()

    async def initialize(self):
        """Initialize HTTP session"""

        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "User-Agent": "MinnesotaCoffeeTrendsScraper/1.0 (Research Bot)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )

        print("✅ Minnesota Coffee Trends Scraper initialized")

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

    async def scrape_minnesota_coffee_trends(
        self, subreddits: List[str] = None, limit: int = 200
    ) -> List[Dict]:
        """Scrape Minnesota coffee trends from Reddit"""

        if not subreddits:
            subreddits = ["coffee", "Coffee", "Minneapolis", "twincities", "Minnesota"]

        print(f"🔍 SCRAPING MINNESOTA COFFEE TRENDS")
        print(f"Subreddits: {', '.join(subreddits)}")
        print(f"Posts per subreddit: {limit}")
        print()

        all_trends = []

        for subreddit in subreddits:
            print(f"📱 Scraping r/{subreddit}...")

            try:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"

                async with self.session.get(url, timeout=20) as response:
                    if response.status == 200:
                        data = await response.json()

                        for post in data.get("data", {}).get("children", []):
                            post_data = post.get("data", {})

                            title = post_data.get("title", "")
                            content = post_data.get("selftext", "")
                            full_text = f"{title} {content}".lower()

                            # Analyze for Minnesota mentions
                            minnesota_mentions = self._count_minnesota_mentions(
                                full_text
                            )
                            coffee_mentions = self._count_coffee_mentions(full_text)

                            # Calculate trend score
                            trend_score = self._calculate_trend_score(
                                post_data.get("score", 0),
                                post_data.get("num_comments", 0),
                                minnesota_mentions,
                                coffee_mentions,
                            )

                            # Only include relevant posts
                            if minnesota_mentions > 0 or coffee_mentions > 2:
                                locations_found = self._extract_locations(full_text)
                                coffee_terms_found = self._extract_coffee_terms(
                                    full_text
                                )

                                trend_data = {
                                    "subreddit": subreddit,
                                    "post_title": title,
                                    "post_content": content,
                                    "score": post_data.get("score", 0),
                                    "comments": post_data.get("num_comments", 0),
                                    "author": post_data.get("author", ""),
                                    "created_utc": post_data.get("created_utc", 0),
                                    "minnesota_mentions": minnesota_mentions,
                                    "coffee_mentions": coffee_mentions,
                                    "trend_score": trend_score,
                                    "locations_found": json.dumps(locations_found),
                                    "coffee_terms_found": json.dumps(
                                        coffee_terms_found
                                    ),
                                    "scraped_at": datetime.now(
                                        timezone.utc
                                    ).isoformat(),
                                }

                                all_trends.append(trend_data)

                    else:
                        print(f"   ❌ Failed: HTTP {response.status}")

            except Exception as e:
                print(f"   ❌ Error: {e}")

        # Store trends
        await self._store_trends(all_trends)

        print(f"✅ Found {len(all_trends)} Minnesota coffee-related posts")
        return all_trends

    def _count_minnesota_mentions(self, text: str) -> int:
        """Count Minnesota-related mentions"""

        count = 0
        text_lower = text.lower()

        for location in self.minnesota_locations:
            if location in text_lower:
                count += 1

        return count

    def _count_coffee_mentions(self, text: str) -> int:
        """Count coffee-related mentions"""

        count = 0
        text_lower = text.lower()

        for keyword in self.coffee_trend_keywords:
            if keyword in text_lower:
                count += 1

        return count

    def _extract_locations(self, text: str) -> List[str]:
        """Extract Minnesota locations mentioned"""

        locations = []
        text_lower = text.lower()

        for location in self.minnesota_locations:
            if location in text_lower:
                locations.append(location)

        return list(set(locations))

    def _extract_coffee_terms(self, text: str) -> List[str]:
        """Extract coffee terms mentioned"""

        terms = []
        text_lower = text.lower()

        for keyword in self.coffee_trend_keywords:
            if keyword in text_lower:
                terms.append(keyword)

        return list(set(terms))

    def _calculate_trend_score(
        self, score: int, comments: int, minnesota_mentions: int, coffee_mentions: int
    ) -> float:
        """Calculate trend score"""

        # Base engagement score
        engagement_score = (score + comments * 2) / 100

        # Relevance score
        relevance_score = (minnesota_mentions * 2 + coffee_mentions) / 10

        # Combined trend score
        trend_score = engagement_score * 0.6 + relevance_score * 0.4

        return trend_score

    async def _store_trends(self, trends: List[Dict]):
        """Store Minnesota coffee trends"""

        try:
            with sqlite3.connect(self.db_path) as conn:
                for trend in trends:
                    conn.execute(
                        """
                        INSERT INTO minnesota_coffee_trends
                        (subreddit, post_title, post_content, score, comments, author,
                         created_utc, minnesota_mentions, coffee_mentions, trend_score,
                         locations_found, coffee_terms_found, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            trend["subreddit"],
                            trend["post_title"],
                            trend["post_content"],
                            trend["score"],
                            trend["comments"],
                            trend["author"],
                            trend["created_utc"],
                            trend["minnesota_mentions"],
                            trend["coffee_mentions"],
                            trend["trend_score"],
                            trend["locations_found"],
                            trend["coffee_terms_found"],
                            trend["scraped_at"],
                        ),
                    )

                conn.commit()

        except Exception as e:
            print(f"Error storing trends: {e}")

    def analyze_trends(self, trends: List[Dict]) -> Dict[str, Any]:
        """Analyze Minnesota coffee trends"""

        print(f"📊 ANALYZING MINNESOTA COFFEE TRENDS")
        print("=" * 60)

        if not trends:
            return {
                "total_posts": 0,
                "minnesota_related": 0,
                "coffee_related": 0,
                "top_locations": [],
                "top_coffee_terms": [],
                "trend_summary": "No trends found",
                "confidence_score": 0.0,
            }

        # Count locations
        all_locations = []
        for trend in trends:
            locations = json.loads(trend.get("locations_found", "[]"))
            all_locations.extend(locations)

        location_counts = Counter(all_locations)
        top_locations = location_counts.most_common(10)

        # Count coffee terms
        all_coffee_terms = []
        for trend in trends:
            terms = json.loads(trend.get("coffee_terms_found", "[]"))
            all_coffee_terms.extend(terms)

        coffee_term_counts = Counter(all_coffee_terms)
        top_coffee_terms = coffee_term_counts.most_common(10)

        # Calculate statistics
        total_posts = len(trends)
        minnesota_related = sum(
            1 for trend in trends if trend["minnesota_mentions"] > 0
        )
        coffee_related = sum(1 for trend in trends if trend["coffee_mentions"] > 0)

        # Generate trend summary
        trend_summary = self._generate_trend_summary(
            top_locations, top_coffee_terms, trends
        )

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            trends, location_counts, coffee_term_counts
        )

        # Store analysis
        self._store_analysis(
            total_posts,
            minnesota_related,
            coffee_related,
            top_locations,
            top_coffee_terms,
            trend_summary,
            confidence_score,
        )

        # Update hot locations
        self._update_hot_locations(location_counts)

        print(f"📈 Total posts analyzed: {total_posts}")
        print(f"🗺️  Minnesota-related: {minnesota_related}")
        print(f"☕ Coffee-related: {coffee_related}")
        print(
            f"🔥 Top locations: {', '.join([loc for loc, count in top_locations[:5]])}"
        )
        print(
            f"☕ Top coffee terms: {', '.join([term for term, count in top_coffee_terms[:5]])}"
        )
        print(f"📊 Confidence score: {confidence_score:.2%}")
        print()

        return {
            "total_posts": total_posts,
            "minnesota_related": minnesota_related,
            "coffee_related": coffee_related,
            "top_locations": top_locations,
            "top_coffee_terms": top_coffee_terms,
            "trend_summary": trend_summary,
            "confidence_score": confidence_score,
        }

    def _generate_trend_summary(
        self,
        top_locations: List[Tuple],
        top_coffee_terms: List[Tuple],
        trends: List[Dict],
    ) -> str:
        """Generate trend summary"""

        if not trends:
            return "No trends found"

        # Get top posts
        top_posts = sorted(trends, key=lambda x: x["trend_score"], reverse=True)[:5]

        summary_parts = []

        # Location summary
        if top_locations:
            top_loc = top_locations[0][0]
            summary_parts.append(f"Hot coffee activity in {top_loc.title()}")

        # Coffee trend summary
        if top_coffee_terms:
            top_term = top_coffee_terms[0][0]
            summary_parts.append(f"Trending: {top_term.title()}")

        # Engagement summary
        avg_score = sum(trend["score"] for trend in trends) / len(trends)
        if avg_score > 50:
            summary_parts.append("High engagement detected")

        # Recent activity
        recent_posts = [
            trend for trend in trends if trend["created_utc"] > time.time() - 86400 * 7
        ]
        if len(recent_posts) > len(trends) * 0.5:
            summary_parts.append("Very active this week")

        return " | ".join(summary_parts)

    def _calculate_confidence_score(
        self, trends: List[Dict], location_counts: Counter, coffee_term_counts: Counter
    ) -> float:
        """Calculate confidence score for trend analysis"""

        if not trends:
            return 0.0

        # Base score from number of relevant posts
        base_score = min(len(trends) / 50, 1.0)

        # Location diversity score
        location_diversity = min(len(location_counts) / 10, 1.0)

        # Coffee term diversity score
        coffee_diversity = min(len(coffee_term_counts) / 15, 1.0)

        # Engagement score
        avg_engagement = sum(
            trend["score"] + trend["comments"] for trend in trends
        ) / len(trends)
        engagement_score = min(avg_engagement / 100, 1.0)

        # Combined confidence score
        confidence = (
            base_score * 0.3
            + location_diversity * 0.2
            + coffee_diversity * 0.2
            + engagement_score * 0.3
        )

        return confidence

    def _store_analysis(
        self,
        total_posts: int,
        minnesota_related: int,
        coffee_related: int,
        top_locations: List[Tuple],
        top_coffee_terms: List[Tuple],
        trend_summary: str,
        confidence_score: float,
    ):
        """Store trend analysis"""

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO trend_analysis
                    (analysis_date, total_posts, minnesota_related, coffee_related,
                     top_locations, top_coffee_terms, trend_summary, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        datetime.now(timezone.utc).isoformat(),
                        total_posts,
                        minnesota_related,
                        coffee_related,
                        json.dumps(top_locations),
                        json.dumps(top_coffee_terms),
                        trend_summary,
                        confidence_score,
                    ),
                )

                conn.commit()

        except Exception as e:
            print(f"Error storing analysis: {e}")

    def _update_hot_locations(self, location_counts: Counter):
        """Update hot locations table"""

        try:
            with sqlite3.connect(self.db_path) as conn:
                for location, count in location_counts.most_common(20):
                    # Calculate trend score for location
                    trend_score = count / 10  # Simple scoring

                    conn.execute(
                        """
                        INSERT OR REPLACE INTO hot_locations
                        (location, mention_count, trend_score, last_updated)
                        VALUES (?, ?, ?, ?)
                    """,
                        (
                            location,
                            count,
                            trend_score,
                            datetime.now(timezone.utc).isoformat(),
                        ),
                    )

                conn.commit()

        except Exception as e:
            print(f"Error updating hot locations: {e}")

    def get_trending_report(self) -> str:
        """Generate comprehensive trending report"""

        print(f"📋 GENERATING MINNESOTA COFFEE TRENDS REPORT")
        print("=" * 80)

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get latest analysis
                cursor = conn.execute(
                    """
                    SELECT * FROM trend_analysis
                    ORDER BY analysis_date DESC
                    LIMIT 1
                """
                )

                analysis = cursor.fetchone()

                if not analysis:
                    return "No analysis data available"

                # Get hot locations
                cursor = conn.execute(
                    """
                    SELECT location, mention_count, trend_score
                    FROM hot_locations
                    ORDER BY trend_score DESC
                    LIMIT 10
                """
                )

                hot_locations = cursor.fetchall()

                # Get top recent posts
                cursor = conn.execute(
                    """
                    SELECT post_title, score, comments, locations_found, coffee_terms_found
                    FROM minnesota_coffee_trends
                    ORDER BY trend_score DESC
                    LIMIT 10
                """
                )

                top_posts = cursor.fetchall()

                # Generate report
                report = self._format_report(analysis, hot_locations, top_posts)

                return report

        except Exception as e:
            return f"Error generating report: {e}"

    def _format_report(
        self, analysis: Tuple, hot_locations: List[Tuple], top_posts: List[Tuple]
    ) -> str:
        """Format the trending report"""

        report = []

        # Header
        report.append("🔥 MINNESOTA COFFEE TRENDS REPORT")
        report.append("=" * 50)
        report.append(f"📅 Analysis Date: {analysis[1]}")
        report.append(f"📊 Confidence Score: {analysis[8]:.1%}")
        report.append(f"📈 Total Posts: {analysis[2]}")
        report.append(f"🗺️  Minnesota-Related: {analysis[3]}")
        report.append(f"☕ Coffee-Related: {analysis[4]}")
        report.append("")

        # Trend Summary
        report.append("📋 TREND SUMMARY")
        report.append("-" * 20)
        report.append(analysis[7])
        report.append("")

        # Top Locations
        report.append("🗺️  HOT LOCATIONS")
        report.append("-" * 20)
        for i, (location, count, score) in enumerate(hot_locations[:5], 1):
            report.append(
                f"{i}. {location.title()}: {count} mentions (Score: {score:.1f})"
            )
        report.append("")

        # Top Coffee Terms
        top_terms = json.loads(analysis[6])
        if top_terms:
            report.append("☕ TRENDING COFFEE TERMS")
            report.append("-" * 25)
            for i, (term, count) in enumerate(top_terms[:5], 1):
                report.append(f"{i}. {term.title()}: {count} mentions")
            report.append("")

        # Top Posts
        report.append("🔥 TRENDING POSTS")
        report.append("-" * 20)
        for i, (title, score, comments, locations, terms) in enumerate(
            top_posts[:5], 1
        ):
            locations_list = json.loads(locations) if locations else []
            terms_list = json.loads(terms) if terms else []

            report.append(f"{i}. {title[:60]}...")
            report.append(f"   Score: {score} | Comments: {comments}")
            if locations_list:
                report.append(f"   Locations: {', '.join(locations_list[:3])}")
            if terms_list:
                report.append(f"   Terms: {', '.join(terms_list[:2])}")
            report.append("")

        # Footer
        report.append("🔍 METHODLOGY")
        report.append("-" * 15)
        report.append("• Analyzing Reddit posts from Minnesota-related subreddits")
        report.append("• Tracking coffee-related keywords and trends")
        report.append("• Calculating engagement and relevance scores")
        report.append("• Identifying hot locations and trending topics")
        report.append("")
        report.append("📊 Generated by Minnesota Coffee Trends Scraper")

        return "\n".join(report)


async def main():
    """Main execution - scrape Minnesota coffee trends"""

    scraper = MinnesotaCoffeeTrendsScraper()
    await scraper.initialize()

    try:
        # Scrape trends
        trends = await scraper.scrape_minnesota_coffee_trends()

        if trends:
            # Analyze trends
            analysis = scraper.analyze_trends(trends)

            # Generate report
            report = scraper.get_trending_report()

            print(report)

            print(f"\n🎉 MINNESOTA COFFEE TRENDS ANALYSIS COMPLETE")
            print(f"✅ Found {len(trends)} relevant posts")
            print(f"📊 Confidence: {analysis['confidence_score']:.1%}")
            print(
                f"🔥 Top location: {analysis['top_locations'][0][0] if analysis['top_locations'] else 'N/A'}"
            )
            print(
                f"☕ Top trend: {analysis['top_coffee_terms'][0][0] if analysis['top_coffee_terms'] else 'N/A'}"
            )

        else:
            print("❌ No Minnesota coffee trends found")

    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
