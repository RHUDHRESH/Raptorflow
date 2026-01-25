"""
Reddit Market Intelligence Service
Advanced Reddit scraping and market intelligence for Raptorflow
"""

import asyncio
import json
import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from backend.services.search.reddit_native import RedditNativeScraper

# Import AI services
from backend.services.vertex_ai_service import vertex_ai_service

logger = logging.getLogger(__name__)


class PostType(str, Enum):
    """Types of Reddit posts"""

    QUESTION = "question"
    DISCUSSION = "discussion"
    COMPLAINT = "complaint"
    PRAISE = "praise"
    REQUEST = "request"
    ANNOUNCEMENT = "announcement"
    REVIEW = "review"
    OTHER = "other"


class Sentiment(str, Enum):
    """Sentiment analysis results"""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class PainPointCategory(str, Enum):
    """Categories of pain points"""

    TECHNICAL = "technical"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    CUSTOMER_SERVICE = "customer_service"
    PRODUCT_FEATURES = "product_features"
    USER_EXPERIENCE = "user_experience"
    INTEGRATION = "integration"
    PRICING = "pricing"
    SUPPORT = "support"


@dataclass
class RedditPost:
    """Individual Reddit post"""

    id: str
    title: str
    content: str
    subreddit: str
    author: str
    score: int
    comments_count: int
    created_at: datetime
    url: str
    post_type: PostType
    sentiment: Sentiment
    keywords: List[str] = field(default_factory=list)
    pain_points: List[str] = field(default_factory=list)
    mentions_competitors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "content": (
                self.content[:500] + "..." if len(self.content) > 500 else self.content
            ),
            "subreddit": self.subreddit,
            "author": self.author,
            "score": self.score,
            "comments_count": self.comments_count,
            "created_at": self.created_at.isoformat(),
            "url": self.url,
            "post_type": self.post_type.value,
            "sentiment": self.sentiment.value,
            "keywords": self.keywords,
            "pain_points": self.pain_points,
            "mentions_competitors": self.mentions_competitors,
            "metadata": self.metadata,
        }


@dataclass
class MarketInsight:
    """Market insight from Reddit analysis"""

    category: str
    insight: str
    evidence_count: int
    confidence: float
    examples: List[str]
    sentiment_distribution: Dict[str, int]
    urgency_score: float
    opportunity_score: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RedditIntelligence:
    """Complete Reddit market intelligence"""

    posts_analyzed: int
    subreddits_analyzed: List[str]
    time_period: str
    insights: List[MarketInsight]
    pain_points: List[Dict[str, Any]]
    competitor_mentions: Dict[str, int]
    sentiment_trends: Dict[str, float]
    trending_topics: List[str]
    recommendations: List[str]
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class RedditMarketIntelligence:
    """Advanced Reddit market intelligence service"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scraper = RedditNativeScraper()

        # Pain point keywords
        self.pain_point_keywords = self._initialize_pain_point_keywords()

        # Competitor keywords
        self.competitor_keywords = [
            "hubspot",
            "salesforce",
            "marketo",
            "pardot",
            "mailchimp",
            "constantcontact",
            "activecampaign",
            "convertkit",
            "klaviyo",
            "sendinblue",
            "campaign monitor",
            "getresponse",
            "aweber",
            "infusionsoft",
            "ontraport",
            "drip",
            "customer.io",
        ]

        # Post type patterns
        self.post_patterns = self._initialize_post_patterns()

        # Sentiment keywords
        self.sentiment_keywords = self._initialize_sentiment_keywords()

    def _initialize_pain_point_keywords(self) -> Dict[PainPointCategory, List[str]]:
        """Initialize keywords for pain point detection"""
        return {
            PainPointCategory.TECHNICAL: [
                "bug",
                "crash",
                "slow",
                "broken",
                "error",
                "glitch",
                "freeze",
                "lag",
                "technical issue",
                "system down",
                "integration problem",
                "api error",
            ],
            PainPointCategory.FINANCIAL: [
                "expensive",
                "cost",
                "price",
                "budget",
                "roi",
                "investment",
                "afford",
                "overpriced",
                "hidden fees",
                "billing issue",
                "payment problem",
            ],
            PainPointCategory.OPERATIONAL: [
                "workflow",
                "process",
                "inefficient",
                "complicated",
                "difficult",
                "complex",
                "time consuming",
                "manual",
                "automation",
                "streamline",
                "optimize",
            ],
            PainPointCategory.STRATEGIC: [
                "strategy",
                "planning",
                "growth",
                "scaling",
                "expansion",
                "vision",
                "direction",
                "goals",
                "objectives",
                "roadmap",
                "alignment",
            ],
            PainPointCategory.CUSTOMER_SERVICE: [
                "support",
                "customer service",
                "help",
                "response time",
                "ticket",
                "chat",
                "phone",
                "email",
                "service quality",
                "representative",
            ],
            PainPointCategory.PRODUCT_FEATURES: [
                "feature",
                "functionality",
                "capability",
                "missing",
                "need",
                "want",
                "request",
                "suggestion",
                "improvement",
                "enhancement",
                "addition",
            ],
            PainPointCategory.USER_EXPERIENCE: [
                "ux",
                "ui",
                "interface",
                "design",
                "usability",
                "user experience",
                "navigation",
                "layout",
                "visual",
                "intuitive",
                "user friendly",
            ],
            PainPointCategory.INTEGRATION: [
                "integration",
                "connect",
                "sync",
                "link",
                "api",
                "third party",
                "compatibility",
                "connection",
                "bridge",
                "interface",
                "middleware",
            ],
            PainPointCategory.PRICING: [
                "pricing",
                "plan",
                "tier",
                "subscription",
                "license",
                "fee",
                "cost structure",
                "payment model",
                "billing cycle",
                "upgrade",
            ],
            PainPointCategory.SUPPORT: [
                "documentation",
                "tutorial",
                "guide",
                "help",
                "training",
                "onboarding",
                "knowledge base",
                "faq",
                "resources",
                "learning",
            ],
        }

    def _initialize_post_patterns(self) -> Dict[PostType, List[str]]:
        """Initialize patterns for post type detection"""
        return {
            PostType.QUESTION: [
                r"how do i",
                r"how can i",
                r"what is",
                r"where can i",
                r"when should",
                r"can someone",
                r"anyone know",
                r"looking for",
                r"need help",
                r"\?",
            ],
            PostType.COMPLAINT: [
                r"frustrated",
                r"annoyed",
                r"disappointed",
                r"terrible",
                r"awful",
                r"hate",
                r"worst",
                r"problem",
                r"issue",
                r"broken",
                r"doesn't work",
            ],
            PostType.PRAISE: [
                r"love",
                r"amazing",
                r"excellent",
                r"perfect",
                r"great",
                r"awesome",
                r"fantastic",
                r"wonderful",
                r"best",
                r"highly recommend",
                r"thank you",
            ],
            PostType.REQUEST: [
                r"looking for",
                r"need",
                r"want",
                r"seeking",
                r"searching",
                r"recommendation",
                r"suggestion",
                r"advice",
                r"opinion",
            ],
            PostType.REVIEW: [
                r"review",
                r"experience",
                r"opinion",
                r"thoughts",
                r"feedback",
                r"rating",
                r"assessment",
                r"evaluation",
            ],
        }

    def _initialize_sentiment_keywords(self) -> Dict[Sentiment, List[str]]:
        """Initialize keywords for sentiment analysis"""
        return {
            Sentiment.POSITIVE: [
                "love",
                "great",
                "excellent",
                "amazing",
                "perfect",
                "awesome",
                "fantastic",
                "wonderful",
                "best",
                "good",
                "helpful",
                "useful",
                "effective",
                "successful",
                "solved",
                "fixed",
                "worked",
                "recommend",
                "thank",
                "appreciate",
            ],
            Sentiment.NEGATIVE: [
                "hate",
                "terrible",
                "awful",
                "worst",
                "bad",
                "poor",
                "useless",
                "ineffective",
                "broken",
                "failed",
                "problem",
                "issue",
                "error",
                "bug",
                "crash",
                "slow",
                "frustrated",
                "annoyed",
                "disappointed",
                "waste",
                "regret",
            ],
            Sentiment.NEUTRAL: [
                "okay",
                "fine",
                "average",
                "normal",
                "standard",
                "typical",
                "regular",
                "information",
                "question",
                "how",
                "what",
                "where",
                "when",
                "why",
            ],
        }

    async def analyze_reddit_market(
        self, company_info: Dict[str, Any]
    ) -> RedditIntelligence:
        """Analyze Reddit for market intelligence"""
        start_time = datetime.now()

        # Determine search parameters
        industry = company_info.get("industry", "marketing technology")
        target_audience = company_info.get("target_audience", "marketers")
        product_category = company_info.get("product_category", "marketing automation")

        # Define relevant subreddits
        subreddits = self._get_relevant_subreddits(
            industry, target_audience, product_category
        )

        # Collect posts from subreddits
        all_posts = []
        for subreddit in subreddits:
            try:
                posts = await self._scrape_subreddit(subreddit, limit=100)
                all_posts.extend(posts)
            except Exception as e:
                self.logger.error(f"Error scraping subreddit {subreddit}: {e}")

        # Analyze posts
        analyzed_posts = []
        for post in all_posts:
            analyzed_post = await self._analyze_post(post, company_info)
            analyzed_posts.append(analyzed_post)

        # Generate insights
        insights = await self._generate_insights(analyzed_posts, company_info)

        # Extract pain points
        pain_points = self._extract_pain_points(analyzed_posts)

        # Analyze competitor mentions
        competitor_mentions = self._analyze_competitor_mentions(analyzed_posts)

        # Calculate sentiment trends
        sentiment_trends = self._calculate_sentiment_trends(analyzed_posts)

        # Identify trending topics
        trending_topics = self._identify_trending_topics(analyzed_posts)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            insights, pain_points, analyzed_posts
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        return RedditIntelligence(
            posts_analyzed=len(analyzed_posts),
            subreddits_analyzed=subreddits,
            time_period="Last 30 days",
            insights=insights,
            pain_points=pain_points,
            competitor_mentions=competitor_mentions,
            sentiment_trends=sentiment_trends,
            trending_topics=trending_topics,
            recommendations=recommendations,
            processing_time=processing_time,
            metadata={
                "industry": industry,
                "target_audience": target_audience,
                "product_category": product_category,
                "analysis_date": datetime.now().isoformat(),
            },
        )

    def _get_relevant_subreddits(
        self, industry: str, target_audience: str, product_category: str
    ) -> List[str]:
        """Get relevant subreddits based on company info"""
        base_subreddits = [
            "marketing",
            "sales",
            "entrepreneur",
            "smallbusiness",
            "startup",
            "SaaS",
            "B2B",
            "digitalmarketing",
            "marketingautomation",
        ]

        # Add industry-specific subreddits
        industry_mapping = {
            "marketing technology": ["martech", "adtech", "marketingtech"],
            "sales": ["sales", "salesops", "salesforce"],
            "customer service": ["customerservice", "cxs", "custserv"],
            "ecommerce": ["ecommerce", "shopify", "woocommerce"],
            "finance": ["fintech", "finance", "accounting"],
        }

        industry_subs = industry_mapping.get(industry.lower(), [])

        # Add audience-specific subreddits
        audience_mapping = {
            "marketers": ["marketing", "digitalmarketing", "ppc", "seo"],
            "founders": ["founders", "entrepreneur", "startup"],
            "executives": ["executives", "leadership", "management"],
            "developers": ["programming", "webdev", "devops"],
        }

        audience_subs = audience_mapping.get(target_audience.lower(), [])

        # Combine and deduplicate
        all_subreddits = list(set(base_subreddits + industry_subs + audience_subs))

        return all_subreddits[:10]  # Limit to 10 subreddits

    async def _scrape_subreddit(
        self, subreddit: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Scrape posts from subreddit using real Native Scraper"""
        try:
            # Construct a broad search query for the subreddit
            search_query = f"subreddit:{subreddit}"
            results = await self.scraper.query(search_query, limit=min(limit, 50))

            posts = []
            for res in results:
                # Add necessary fields for RedditPost dataclass
                posts.append(
                    {
                        "id": (
                            res["url"].split("/")[-2]
                            if len(res["url"].split("/")) > 2
                            else "unknown"
                        ),
                        "title": res["title"],
                        "content": res["snippet"],
                        "subreddit": subreddit,
                        "author": "unknown",  # Native search doesn't return author easily without thread fetch
                        "score": res.get("metadata", {}).get("ups", 0),
                        "comments_count": res.get("metadata", {}).get(
                            "num_comments", 0
                        ),
                        "created_at": datetime.now(),  # Placeholder timestamp
                        "url": res["url"],
                    }
                )

            return posts
        except Exception as e:
            self.logger.error(f"Failed to scrape subreddit {subreddit}: {e}")
            return []

    async def _analyze_post(
        self, post: Dict[str, Any], company_info: Dict[str, Any]
    ) -> RedditPost:
        """Analyze individual Reddit post"""
        title = post.get("title", "")
        content = post.get("content", "")
        full_text = f"{title} {content}"

        # Determine post type
        post_type = self._determine_post_type(full_text)

        # Analyze sentiment
        sentiment = self._analyze_sentiment(full_text)

        # Extract keywords
        keywords = self._extract_keywords(full_text)

        # Identify pain points
        pain_points = self._identify_pain_points(full_text)

        # Find competitor mentions
        competitor_mentions = self._find_competitor_mentions(full_text)

        return RedditPost(
            id=post.get("id", ""),
            title=title,
            content=content,
            subreddit=post.get("subreddit", ""),
            author=post.get("author", ""),
            score=post.get("score", 0),
            comments_count=post.get("comments_count", 0),
            created_at=post.get("created_at", datetime.now()),
            url=post.get("url", ""),
            post_type=post_type,
            sentiment=sentiment,
            keywords=keywords,
            pain_points=pain_points,
            mentions_competitors=competitor_mentions,
            metadata={
                "text_length": len(full_text),
                "engagement_score": post.get("score", 0)
                + post.get("comments_count", 0),
            },
        )

    def _determine_post_type(self, text: str) -> PostType:
        """Determine post type from text"""
        text_lower = text.lower()

        for post_type, patterns in self.post_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return post_type

        return PostType.OTHER

    def _analyze_sentiment(self, text: str) -> Sentiment:
        """Analyze sentiment of text"""
        text_lower = text.lower()

        positive_count = sum(
            1
            for word in self.sentiment_keywords[Sentiment.POSITIVE]
            if word in text_lower
        )
        negative_count = sum(
            1
            for word in self.sentiment_keywords[Sentiment.NEGATIVE]
            if word in text_lower
        )
        neutral_count = sum(
            1
            for word in self.sentiment_keywords[Sentiment.NEUTRAL]
            if word in text_lower
        )

        if positive_count > negative_count and positive_count > neutral_count:
            return Sentiment.POSITIVE
        elif negative_count > positive_count and negative_count > neutral_count:
            return Sentiment.NEGATIVE
        elif neutral_count > positive_count and neutral_count > negative_count:
            return Sentiment.NEUTRAL
        elif positive_count == negative_count and positive_count > 0:
            return Sentiment.MIXED
        else:
            return Sentiment.NEUTRAL

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction - in production would use NLP
        marketing_keywords = [
            "automation",
            "campaign",
            "lead",
            "conversion",
            "roi",
            "analytics",
            "email",
            "social",
            "content",
            "seo",
            "ppc",
            "funnel",
            "segmentation",
            "personalization",
            "integration",
            "crm",
            "customer",
            "engagement",
            "traffic",
            "revenue",
            "growth",
            "strategy",
            "optimization",
        ]

        text_lower = text.lower()
        found_keywords = [
            keyword for keyword in marketing_keywords if keyword in text_lower
        ]

        return found_keywords

    def _identify_pain_points(self, text: str) -> List[str]:
        """Identify pain points in text"""
        text_lower = text.lower()
        found_pain_points = []

        for category, keywords in self.pain_point_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_pain_points.append(f"{category.value}: {keyword}")

        return found_pain_points

    def _find_competitor_mentions(self, text: str) -> List[str]:
        """Find competitor mentions in text"""
        text_lower = text.lower()
        found_competitors = []

        for competitor in self.competitor_keywords:
            if competitor in text_lower:
                found_competitors.append(competitor)

        return found_competitors

    async def _generate_insights(
        self, posts: List[RedditPost], company_info: Dict[str, Any]
    ) -> List[MarketInsight]:
        """Generate market insights from posts"""
        insights = []

        # Group posts by pain points
        pain_point_groups = defaultdict(list)
        for post in posts:
            for pain_point in post.pain_points:
                pain_point_groups[pain_point].append(post)

        # Generate insights for each pain point
        for pain_point, related_posts in pain_point_groups.items():
            if len(related_posts) >= 3:  # Only consider significant pain points
                insight = await self._create_pain_point_insight(
                    pain_point, related_posts
                )
                insights.append(insight)

        # Generate sentiment insights
        sentiment_insight = self._create_sentiment_insight(posts)
        insights.append(sentiment_insight)

        # Generate competitor insights
        competitor_insight = self._create_competitor_insight(posts)
        insights.append(competitor_insight)

        return insights

    async def _create_pain_point_insight(
        self, pain_point: str, posts: List[RedditPost]
    ) -> MarketInsight:
        """Create insight from pain point analysis"""
        # Calculate sentiment distribution
        sentiment_counts = Counter(post.sentiment.value for post in posts)

        # Calculate urgency based on negative sentiment and engagement
        negative_posts = [p for p in posts if p.sentiment == Sentiment.NEGATIVE]
        urgency_score = (
            len(negative_posts)
            / len(posts)
            * sum(p.score for p in negative_posts)
            / max(1, len(negative_posts))
        )

        # Calculate opportunity based on positive sentiment and questions
        positive_posts = [p for p in posts if p.sentiment == Sentiment.POSITIVE]
        question_posts = [p for p in posts if p.post_type == PostType.QUESTION]
        opportunity_score = (len(positive_posts) + len(question_posts)) / len(posts)

        # Extract examples
        examples = [post.title for post in posts[:5]]

        return MarketInsight(
            category="Pain Point Analysis",
            insight=f"Users frequently struggle with {pain_point}. This represents a significant opportunity for solutions.",
            evidence_count=len(posts),
            confidence=min(1.0, len(posts) / 10),  # More posts = higher confidence
            examples=examples,
            sentiment_distribution=dict(sentiment_counts),
            urgency_score=min(1.0, urgency_score / 100),  # Normalize to 0-1
            opportunity_score=min(1.0, opportunity_score),
        )

    def _create_sentiment_insight(self, posts: List[RedditPost]) -> MarketInsight:
        """Create sentiment analysis insight"""
        sentiment_counts = Counter(post.sentiment.value for post in posts)
        total_posts = len(posts)

        positive_ratio = sentiment_counts.get("positive", 0) / total_posts
        negative_ratio = sentiment_counts.get("negative", 0) / total_posts

        if positive_ratio > 0.6:
            insight = "Market sentiment is predominantly positive, indicating satisfaction with current solutions."
            opportunity_score = 0.3  # Lower opportunity in satisfied market
        elif negative_ratio > 0.4:
            insight = "Significant negative sentiment indicates market dissatisfaction and opportunity for improvement."
            opportunity_score = 0.8  # Higher opportunity in dissatisfied market
        else:
            insight = "Mixed market sentiment suggests room for differentiation and improvement."
            opportunity_score = 0.6

        examples = [
            post.title for post in posts if post.sentiment != Sentiment.NEUTRAL
        ][:3]

        return MarketInsight(
            category="Sentiment Analysis",
            insight=insight,
            evidence_count=total_posts,
            confidence=0.8,
            examples=examples,
            sentiment_distribution=dict(sentiment_counts),
            urgency_score=negative_ratio,
            opportunity_score=opportunity_score,
        )

    def _create_competitor_insight(self, posts: List[RedditPost]) -> MarketInsight:
        """Create competitor analysis insight"""
        competitor_mentions = defaultdict(int)
        for post in posts:
            for competitor in post.mentions_competitors:
                competitor_mentions[competitor] += 1

        if not competitor_mentions:
            insight = "Limited competitor discussion suggests either market dominance or lack of awareness."
        else:
            top_competitor = max(competitor_mentions, key=competitor_mentions.get)
            insight = f"{top_competitor.title()} is most frequently mentioned, indicating market leadership or common comparison point."

        examples = [
            f"{comp}: {count} mentions"
            for comp, count in list(competitor_mentions.items())[:3]
        ]

        return MarketInsight(
            category="Competitor Analysis",
            insight=insight,
            evidence_count=len(posts),
            confidence=0.7,
            examples=examples,
            sentiment_distribution={},
            urgency_score=0.5,
            opportunity_score=0.6,
        )

    def _extract_pain_points(self, posts: List[RedditPost]) -> List[Dict[str, Any]]:
        """Extract and rank pain points"""
        pain_point_counts = defaultdict(int)
        pain_point_sentiment = defaultdict(
            lambda: {"positive": 0, "negative": 0, "neutral": 0}
        )

        for post in posts:
            for pain_point in post.pain_points:
                pain_point_counts[pain_point] += 1
                pain_point_sentiment[pain_point][post.sentiment.value] += 1

        # Create ranked pain points
        ranked_pain_points = []
        for pain_point, count in sorted(
            pain_point_counts.items(), key=lambda x: x[1], reverse=True
        ):
            sentiment_data = pain_point_sentiment[pain_point]
            total = sum(sentiment_data.values())

            ranked_pain_points.append(
                {
                    "pain_point": pain_point,
                    "frequency": count,
                    "sentiment_distribution": sentiment_data,
                    "negative_ratio": (
                        sentiment_data["negative"] / total if total > 0 else 0
                    ),
                    "urgency_score": (count / len(posts))
                    * (sentiment_data["negative"] / total if total > 0 else 0),
                }
            )

        return ranked_pain_points[:10]  # Top 10 pain points

    def _analyze_competitor_mentions(self, posts: List[RedditPost]) -> Dict[str, int]:
        """Analyze competitor mentions"""
        competitor_counts = defaultdict(int)

        for post in posts:
            for competitor in post.mentions_competitors:
                competitor_counts[competitor] += 1

        return dict(sorted(competitor_counts.items(), key=lambda x: x[1], reverse=True))

    def _calculate_sentiment_trends(self, posts: List[RedditPost]) -> Dict[str, float]:
        """Calculate sentiment trends over time"""
        # Group posts by week
        weekly_sentiment = defaultdict(
            lambda: {"positive": 0, "negative": 0, "neutral": 0}
        )

        for post in posts:
            week_key = post.created_at.strftime("%Y-W%U")
            weekly_sentiment[week_key][post.sentiment.value] += 1

        # Calculate sentiment ratios
        sentiment_trends = {}
        for week, counts in weekly_sentiment.items():
            total = sum(counts.values())
            if total > 0:
                sentiment_trends[week] = counts["positive"] / total

        return sentiment_trends

    def _identify_trending_topics(self, posts: List[RedditPost]) -> List[str]:
        """Identify trending topics from keywords"""
        all_keywords = []
        for post in posts:
            all_keywords.extend(post.keywords)

        keyword_counts = Counter(all_keywords)
        trending = [keyword for keyword, count in keyword_counts.most_common(10)]

        return trending

    def _generate_recommendations(
        self,
        insights: List[MarketInsight],
        pain_points: List[Dict[str, Any]],
        posts: List[RedditPost],
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Pain point recommendations
        high_urgency_pain_points = [
            pp for pp in pain_points if pp["urgency_score"] > 0.5
        ]
        if high_urgency_pain_points:
            top_pain_point = high_urgency_pain_points[0]
            recommendations.append(
                f"Address {top_pain_point['pain_point']} - mentioned {top_pain_point['frequency']} times with high urgency"
            )

        # Opportunity recommendations
        high_opportunity_insights = [
            insight for insight in insights if insight.opportunity_score > 0.7
        ]
        if high_opportunity_insights:
            recommendations.append(
                "Focus on high-opportunity areas identified in market analysis"
            )

        # Sentiment recommendations
        negative_posts = [p for p in posts if p.sentiment == Sentiment.NEGATIVE]
        if len(negative_posts) / len(posts) > 0.4:
            recommendations.append(
                "Address common complaints to improve market perception"
            )

        # Competitor recommendations
        if any(post.mentions_competitors for post in posts):
            recommendations.append(
                "Monitor competitor discussions to identify differentiation opportunities"
            )

        # Content recommendations
        question_posts = [p for p in posts if p.post_type == PostType.QUESTION]
        if len(question_posts) > len(posts) * 0.3:
            recommendations.append(
                "Create educational content addressing common questions"
            )

        # General recommendations
        recommendations.extend(
            [
                "Monitor Reddit discussions regularly for market insights",
                "Engage with community to understand pain points better",
                "Use insights to inform product development and marketing",
            ]
        )

        return recommendations[:8]  # Top 8 recommendations


# Export service
__all__ = [
    "RedditMarketIntelligence",
    "RedditIntelligence",
    "RedditPost",
    "MarketInsight",
]
