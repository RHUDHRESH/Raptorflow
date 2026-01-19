"""
Reddit Researcher Agent
Scrapes Reddit for market intelligence and pain points
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import re
import requests
import time
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PostType(Enum):
    """Types of Reddit posts"""
    QUESTION = "question"
    DISCUSSION = "discussion"
    COMPLAINT = "complaint"
    RECOMMENDATION = "recommendation"
    ANNOUNCEMENT = "announcement"
    OTHER = "other"


class PainPointCategory(Enum):
    """Categories of pain points"""
    TECHNICAL = "technical"
    FINANCIAL = "financial"
    PROCESS = "process"
    USER_EXPERIENCE = "user_experience"
    INTEGRATION = "integration"
    SUPPORT = "support"
    PERFORMANCE = "performance"
    PRICING = "pricing"
    OTHER = "other"


@dataclass
class RedditPost:
    """Represents a Reddit post"""
    id: str
    title: str
    content: str
    subreddit: str
    author: str
    score: int
    comments_count: int
    created_at: datetime
    post_type: PostType
    url: str
    pain_points: List[str]
    sentiment: float
    relevance_score: float


@dataclass
class PainPoint:
    """Represents a detected pain point"""
    id: str
    category: PainPointCategory
    description: str
    severity: float
    frequency: int
    source_posts: List[str]
    quotes: List[str]
    suggested_solution: Optional[str]


@dataclass
class RedditResearchReport:
    """Report of Reddit research findings"""
    posts_analyzed: int
    subreddits_analyzed: List[str]
    pain_points: List[PainPoint]
    market_insights: List[str]
    competitor_mentions: List[Dict[str, Any]]
    sentiment_analysis: Dict[str, float]
    recommendations: List[str]
    research_summary: str


class RedditResearcher:
    """Reddit market intelligence researcher"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pain_point_counter = 0
        self.pain_point_patterns = self._load_pain_point_patterns()
        self.subreddit_keywords = self._load_subreddit_keywords()
        self.sentiment_keywords = self._load_sentiment_keywords()
        
        # Rate limiting and user agent rotation
        self.last_request_time = 0
        self.request_interval = 6  # 6 seconds between requests (10 per minute)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
    
    def _load_pain_point_patterns(self) -> Dict[PainPointCategory, List[str]]:
        """Load patterns for detecting pain points"""
        return {
            PainPointCategory.TECHNICAL: [
                r"(?:bug|error|crash|freeze|slow|lag|performance|technical|issue|problem)",
                r"(?:doesn't work|not working|broken|failed|glitch|malfunction)",
                r"(?:code|api|integration|compatibility|technical debt|scalability)"
            ],
            PainPointCategory.FINANCIAL: [
                r"(?:expensive|costly|price|pricing|fee|charge|payment|billing)",
                r"(?:too expensive|overpriced|not worth|cost too much|budget)",
                r"(?:roi|return on investment|value|money|afford|cheap)"
            ],
            PainPointCategory.PROCESS: [
                r"(?:workflow|process|complicated|complex|difficult|hard to use)",
                r"(?:too many steps|confusing|unclear|documentation|onboarding)",
                r"(?:setup|configuration|implementation|deployment|migration)"
            ],
            PainPointCategory.USER_EXPERIENCE: [
                r"(?:ux|ui|interface|design|usability|user experience|user friendly)",
                r"(?:intuitive|easy to use|user interface|navigation|layout)",
                r"(?:frustrating|annoying|confusing|hard to navigate|cluttered)"
            ],
            PainPointCategory.INTEGRATION: [
                r"(?:integration|api|connect|sync|import|export|compatibility)",
                r"(?:doesn't integrate|no api|can't connect|sync issues|compatibility)",
                r"(?:third party|external tools|connectors|plugins|extensions)"
            ],
            PainPointCategory.SUPPORT: [
                r"(?:support|help|customer service|assistance|documentation|tutorial)",
                r"(?:no support|poor support|slow response|unhelpful|documentation)",
                r"(?:community|forum|knowledge base|faq|guides|help docs)"
            ],
            PainPointCategory.PERFORMANCE: [
                r"(?:slow|lag|performance|speed|fast|responsive|load time)",
                r"(?:too slow|performance issues|speed problems|load time|latency)",
                r"(?:optimization|efficiency|resource usage|memory|cpu)"
            ],
            PainPointCategory.PRICING: [
                r"(?:pricing|price|cost|fee|subscription|license|freemium)",
                r"(?:pricing model|tier|plan|package|enterprise|startup)",
                r"(?:free trial|demo|pricing page|cost calculator|quote)"
            ]
        }
    
    def _load_subreddit_keywords(self) -> Dict[str, List[str]]:
        """Load relevant subreddits and keywords"""
        return {
            "startups": ["startup", "founder", "entrepreneur", "business", "saas"],
            "SaaS": ["saas", "software", "b2b", "subscription", "recurring"],
            "Entrepreneur": ["entrepreneur", "business owner", "founder", "startup"],
            "smallbusiness": ["small business", "smb", "local business", "main street"],
            "sysadmin": ["it", "sysadmin", "devops", "infrastructure", "server"],
            "webdev": ["web development", "frontend", "backend", "full stack"],
            "ProductManagement": ["product management", "product manager", "product"],
            "sales": ["sales", "selling", "revenue", "crm", "prospecting"],
            "marketing": ["marketing", "advertising", "growth", "acquisition"],
            "finance": ["finance", "accounting", "bookkeeping", "financial"]
        }
    
    def _load_sentiment_keywords(self) -> Dict[str, List[str]]:
        """Load sentiment analysis keywords"""
        return {
            "positive": [
                "love", "great", "excellent", "amazing", "perfect", "awesome",
                "fantastic", "wonderful", "brilliant", "outstanding", "helpful",
                "useful", "effective", "efficient", "recommend", "best"
            ],
            "negative": [
                "hate", "terrible", "awful", "horrible", "worst", "useless",
                "broken", "crap", "garbage", "waste", "disappointed", "frustrated",
                "annoying", "confusing", "difficult", "problem", "issue", "bug"
            ]
        }
    
    def _generate_pain_point_id(self) -> str:
        """Generate unique pain point ID"""
        self.pain_point_counter += 1
        return f"PP-{self.pain_point_counter:03d}"
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent for request"""
        return random.choice(self.user_agents)
    
    def _rate_limit(self):
        """Apply rate limiting to requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_interval:
            sleep_time = self.request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _fetch_subreddit_json(self, subreddit: str, after: str = None, limit: int = 25) -> Optional[Dict[str, Any]]:
        """Fetch subreddit data via JSON endpoint"""
        try:
            self._rate_limit()
            
            # Build URL
            url = f"https://www.reddit.com/r/{subreddit}.json"
            params = {"limit": limit}
            if after:
                params["after"] = after
            
            headers = {
                "User-Agent": self._get_random_user_agent(),
                "Accept": "application/json"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Failed to fetch {subreddit}: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching {subreddit}: {e}")
            return None
    
    def _fetch_post_json(self, subreddit: str, post_id: str) -> Optional[Dict[str, Any]]:
        """Fetch individual post and comments via JSON endpoint"""
        try:
            self._rate_limit()
            
            url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
            headers = {
                "User-Agent": self._get_random_user_agent(),
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Failed to fetch post {post_id}: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching post {post_id}: {e}")
            return None
    
    def _parse_post_data(self, post_data: Dict[str, Any]) -> Optional[RedditPost]:
        """Parse Reddit post data from JSON response"""
        try:
            data = post_data.get("data", {})
            
            # Extract basic information
            post_id = data.get("id", "")
            title = data.get("title", "")
            content = data.get("selftext", "")
            subreddit = data.get("subreddit", "")
            author = data.get("author", "")
            score = data.get("score", 0)
            comments_count = data.get("num_comments", 0)
            created_utc = data.get("created_utc", 0)
            url = data.get("url", "")
            
            # Convert timestamp
            created_at = datetime.fromtimestamp(created_utc)
            
            # Calculate other attributes
            post_type = self._classify_post_type(title, content)
            sentiment = self._calculate_sentiment(content)
            pain_points = self._extract_pain_points(content)
            
            return RedditPost(
                id=post_id,
                title=title,
                content=content,
                subreddit=subreddit,
                author=author,
                score=score,
                comments_count=comments_count,
                created_at=created_at,
                post_type=post_type,
                url=url,
                pain_points=pain_points,
                sentiment=sentiment,
                relevance_score=0.0
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing post data: {e}")
            return None
    
    def _classify_post_type(self, title: str, content: str) -> PostType:
        """Classify the type of Reddit post"""
        text = (title + " " + content).lower()
        
        if any(word in text for word in ["how", "what", "why", "when", "where", "?"]):
            return PostType.QUESTION
        elif any(word in text for word in ["problem", "issue", "bug", "error", "complaint"]):
            return PostType.COMPLAINT
        elif any(word in text for word in ["recommend", "suggest", "best", "top"]):
            return PostType.RECOMMENDATION
        elif any(word in text for word in ["announcing", "launch", "new", "release"]):
            return PostType.ANNOUNCEMENT
        else:
            return PostType.DISCUSSION
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score (-1 to 1)"""
        text_lower = text.lower()
        positive_count = sum(1 for word in self.sentiment_keywords["positive"] if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_keywords["negative"] if word in text_lower)
        
        total_words = len(text_lower.split())
        if total_words == 0:
            return 0.0
        
        # Normalize sentiment
        sentiment = (positive_count - negative_count) / max(positive_count + negative_count, 1)
        return max(-1.0, min(1.0, sentiment))
    
    def _extract_pain_points(self, text: str) -> List[str]:
        """Extract pain points from text"""
        pain_points = []
        text_lower = text.lower()
        
        for category, patterns in self.pain_point_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    # Extract context around the match
                    match_start = text_lower.find(match)
                    if match_start != -1:
                        context_start = max(0, match_start - 50)
                        context_end = min(len(text_lower), match_start + len(match) + 50)
                        context = text[context_start:context_end].strip()
                        
                        pain_point = f"{category.value}: {context}"
                        if pain_point not in pain_points:
                            pain_points.append(pain_point)
        
        return pain_points
    
    def _calculate_relevance(self, post: RedditPost, keywords: List[str]) -> float:
        """Calculate relevance score based on keywords"""
        text = (post.title + " " + post.content).lower()
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text)
        
        # Factor in engagement (score and comments)
        engagement_score = min(post.score / 100, 1.0) + min(post.comments_count / 50, 1.0)
        
        # Calculate relevance
        relevance = (keyword_matches / len(keywords)) * 0.7 + (engagement_score / 2) * 0.3
        return min(1.0, relevance)
    
    async def search_reddit(self, query: str, subreddit: str = None, limit: int = 100) -> List[RedditPost]:
        """
        Search Reddit for posts related to the query using JSON endpoints
        
        Args:
            query: Search query
            subreddit: Specific subreddit to search (optional)
            limit: Maximum number of posts to retrieve
        
        Returns:
            List of RedditPost objects
        """
        posts = []
        query_lower = query.lower()
        
        # Determine relevant subreddits
        relevant_subreddits = []
        if subreddit:
            relevant_subreddits = [subreddit]
        else:
            for sub, keywords in self.subreddit_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    relevant_subreddits.append(sub)
        
        if not relevant_subreddits:
            relevant_subreddits = ["startups", "SaaS", "Entrepreneur", "smallbusiness", "sysadmin"]
        
        # Fetch posts from each subreddit
        for sub in relevant_subreddits:
            try:
                # Fetch first page
                subreddit_data = self._fetch_subreddit_json(sub, limit=min(limit // len(relevant_subreddits), 25))
                
                if subreddit_data and "data" in subreddit_data and "children" in subreddit_data["data"]:
                    for child in subreddit_data["data"]["children"]:
                        post = self._parse_post_data(child)
                        if post:
                            posts.append(post)
                
                # Fetch additional pages if needed (pagination)
                if len(posts) < limit and subreddit_data:
                    after = subreddit_data["data"].get("after")
                    page_count = 0
                    
                    while after and len(posts) < limit and page_count < 3:  # Max 3 pages per subreddit
                        subreddit_data = self._fetch_subreddit_json(sub, after=after, limit=25)
                        
                        if subreddit_data and "data" in subreddit_data and "children" in subreddit_data["data"]:
                            for child in subreddit_data["data"]["children"]:
                                post = self._parse_post_data(child)
                                if post:
                                    posts.append(post)
                        
                        after = subreddit_data["data"].get("after") if subreddit_data else None
                        page_count += 1
                
                # Break if we have enough posts
                if len(posts) >= limit:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error fetching from r/{sub}: {e}")
                continue
        
        # Filter for relevance based on query keywords
        keywords = query.split()
        for post in posts:
            post.relevance_score = self._calculate_relevance(post, keywords)
        
        # Filter and sort by relevance
        relevant_posts = [p for p in posts if p.relevance_score > 0.1]
        relevant_posts.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return relevant_posts[:limit]
    
    async def analyze_pain_points(self, posts: List[RedditPost]) -> List[PainPoint]:
        """Analyze posts to identify common pain points"""
        pain_point_data = {}
        
        # Collect all pain points from posts
        for post in posts:
            for pain_point_str in post.pain_points:
                # Parse category and description
                if ":" in pain_point_str:
                    category_str, description = pain_point_str.split(":", 1)
                    try:
                        category = PainPointCategory(category_str)
                    except ValueError:
                        category = PainPointCategory.OTHER
                else:
                    category = PainPointCategory.OTHER
                    description = pain_point_str
                
                # Group similar pain points
                key = f"{category.value}:{description[:50]}"  # First 50 chars as key
                
                if key not in pain_point_data:
                    pain_point_data[key] = {
                        "category": category,
                        "descriptions": [],
                        "source_posts": [],
                        "quotes": [],
                        "severity_sum": 0.0
                    }
                
                pain_point_data[key]["descriptions"].append(description)
                pain_point_data[key]["source_posts"].append(post.id)
                
                # Add quote if not already present
                quote = f"r/{post.subreddit}: {post.title}"
                if quote not in pain_point_data[key]["quotes"]:
                    pain_point_data[key]["quotes"].append(quote)
                
                # Calculate severity based on sentiment and engagement
                severity = abs(post.sentiment) * 0.5 + (post.score + post.comments_count) / 1000 * 0.5
                pain_point_data[key]["severity_sum"] += severity
        
        # Create PainPoint objects
        pain_points = []
        for key, data in pain_point_data.items():
            if len(data["source_posts"]) >= 2:  # Only include pain points mentioned multiple times
                # Get most common description
                from collections import Counter
                most_common_desc = Counter(data["descriptions"]).most_common(1)[0][0]
                
                # Calculate average severity
                avg_severity = data["severity_sum"] / len(data["source_posts"])
                
                # Generate suggested solution
                suggested_solution = self._generate_solution_suggestion(data["category"], most_common_desc)
                
                pain_point = PainPoint(
                    id=self._generate_pain_point_id(),
                    category=data["category"],
                    description=most_common_desc,
                    severity=min(1.0, avg_severity),
                    frequency=len(data["source_posts"]),
                    source_posts=data["source_posts"],
                    quotes=data["quotes"][:3],  # Top 3 quotes
                    suggested_solution=suggested_solution
                )
                pain_points.append(pain_point)
        
        # Sort by severity and frequency
        pain_points.sort(key=lambda x: (x.severity * x.frequency), reverse=True)
        
        return pain_points
    
    def _generate_solution_suggestion(self, category: PainPointCategory, description: str) -> str:
        """Generate a suggested solution for a pain point"""
        suggestions = {
            PainPointCategory.TECHNICAL: "Consider technical improvements, bug fixes, or performance optimizations",
            PainPointCategory.FINANCIAL: "Review pricing strategy, offer flexible plans, or improve value proposition",
            PainPointCategory.PROCESS: "Simplify workflows, improve documentation, or streamline onboarding",
            PainPointCategory.USER_EXPERIENCE: "Redesign interface, improve navigation, or enhance usability",
            PainPointCategory.INTEGRATION: "Develop APIs, improve connectors, or enhance compatibility",
            PainPointCategory.SUPPORT: "Improve response times, enhance documentation, or expand support channels",
            PainPointCategory.PERFORMANCE: "Optimize speed, improve efficiency, or upgrade infrastructure",
            PainPointCategory.PRICING: "Adjust pricing tiers, offer trials, or improve value communication"
        }
        
        return suggestions.get(category, "Address the core issue through product improvements or service enhancements")
    
    async def generate_market_insights(self, posts: List[RedditPost], pain_points: List[PainPoint]) -> List[str]:
        """Generate market insights from Reddit analysis"""
        insights = []
        
        # Analyze sentiment trends
        if posts:
            avg_sentiment = sum(post.sentiment for post in posts) / len(posts)
            if avg_sentiment < -0.2:
                insights.append("Overall sentiment is negative - market may be underserved or frustrated")
            elif avg_sentiment > 0.2:
                insights.append("Overall sentiment is positive - market is satisfied but may have unmet needs")
        
        # Analyze most discussed topics
        if pain_points:
            top_pain_point = pain_points[0]
            insights.append(f"Most common pain point: {top_pain_point.category.value} - {top_pain_point.description[:100]}...")
        
        # Analyze engagement patterns
        high_engagement_posts = [p for p in posts if p.score + p.comments_count > 100]
        if high_engagement_posts:
            insights.append(f"{len(high_engagement_posts)} posts have high engagement - indicates strong interest")
        
        # Analyze subreddit distribution
        subreddit_counts = {}
        for post in posts:
            subreddit_counts[post.subreddit] = subreddit_counts.get(post.subreddit, 0) + 1
        
        if subreddit_counts:
            top_subreddit = max(subreddit_counts.items(), key=lambda x: x[1])
            insights.append(f"Most active community: r/{top_subreddit[0]} with {top_subreddit[1]} posts")
        
        return insights
    
    async def research_market(self, query: str, company_domain: str = "", competitors: List[str] = None) -> RedditResearchReport:
        """
        Conduct comprehensive Reddit market research
        
        Args:
            query: Research query (e.g., "project management software")
            company_domain: Company's domain for context
            competitors: List of competitor names to track
        
        Returns:
            RedditResearchReport with findings
        """
        # Search Reddit
        posts = await self.search_reddit(query, limit=100)
        
        # Filter for relevance
        keywords = query.split() + (competitors or [])
        for post in posts:
            post.relevance_score = self._calculate_relevance(post, keywords)
        
        relevant_posts = [p for p in posts if p.relevance_score > 0.3]
        
        # Analyze pain points
        pain_points = await self.analyze_pain_points(relevant_posts)
        
        # Generate market insights
        market_insights = await self.generate_market_insights(relevant_posts, pain_points)
        
        # Analyze competitor mentions
        competitor_mentions = []
        if competitors:
            for competitor in competitors:
                mentions = [p for p in relevant_posts if competitor.lower() in (p.title + " " + p.content).lower()]
                if mentions:
                    competitor_mentions.append({
                        "competitor": competitor,
                        "mention_count": len(mentions),
                        "avg_sentiment": sum(m.sentiment for m in mentions) / len(mentions),
                        "top_posts": [{"id": m.id, "title": m.title, "sentiment": m.sentiment} for m in mentions[:3]]
                    })
        
        # Sentiment analysis
        sentiment_analysis = {
            "overall": sum(p.sentiment for p in relevant_posts) / len(relevant_posts) if relevant_posts else 0,
            "by_post_type": {}
        }
        
        for post_type in PostType:
            type_posts = [p for p in relevant_posts if p.post_type == post_type]
            if type_posts:
                sentiment_analysis["by_post_type"][post_type.value] = sum(p.sentiment for p in type_posts) / len(type_posts)
        
        # Generate recommendations
        recommendations = []
        if pain_points:
            recommendations.append(f"Address top {min(3, len(pain_points))} pain points in product development")
        
        if sentiment_analysis["overall"] < -0.1:
            recommendations.append("Market sentiment is negative - opportunity for differentiation")
        
        if competitor_mentions:
            recommendations.append("Monitor competitor discussions for positioning opportunities")
        
        # Generate summary
        summary = f"Analyzed {len(relevant_posts)} relevant Reddit posts from {len(set(p.subreddit for p in relevant_posts))} subreddits. "
        summary += f"Identified {len(pain_points)} unique pain points. "
        
        if pain_points:
            summary += f"Top issue: {pain_points[0].category.value} ({pain_points[0].frequency} mentions). "
        
        if sentiment_analysis["overall"] > 0:
            summary += "Market sentiment is generally positive."
        elif sentiment_analysis["overall"] < 0:
            summary += "Market sentiment shows frustration - opportunity for better solution."
        
        return RedditResearchReport(
            posts_analyzed=len(relevant_posts),
            subreddits_analyzed=list(set(p.subreddit for p in relevant_posts)),
            pain_points=pain_points,
            market_insights=market_insights,
            competitor_mentions=competitor_mentions,
            sentiment_analysis=sentiment_analysis,
            recommendations=recommendations,
            research_summary=summary
        )
