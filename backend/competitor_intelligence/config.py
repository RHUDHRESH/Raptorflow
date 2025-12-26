"""
Configuration and constants for competitor intelligence
"""

from enum import Enum
from typing import Dict, Any

class CompetitorConfig:
    """Configuration settings for competitor intelligence."""
    
    # Default monitoring frequencies (in hours)
    DEFAULT_MONITORING_FREQUENCY = 24
    MIN_MONITORING_FREQUENCY = 1
    MAX_MONITORING_FREQUENCY = 720  # 30 days
    
    # Confidence thresholds
    MIN_CONFIDENCE_THRESHOLD = 0.3
    HIGH_CONFIDENCE_THRESHOLD = 0.8
    
    # Alert settings
    MAX_ALERTS_PER_HOUR = 50
    ALERT_RETENTION_DAYS = 30
    
    # Analysis settings
    MAX_COMPETITORS_PER_ANALYSIS = 20
    ANALYSIS_RETENTION_DAYS = 90
    
    # Memory settings
    MAX_PROFILES_PER_THREAD = 100
    MAX_INSIGHTS_PER_THREAD = 1000
    
    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "monitoring_frequency": cls.DEFAULT_MONITORING_FREQUENCY,
            "confidence_threshold": cls.MIN_CONFIDENCE_THRESHOLD,
            "max_alerts_per_hour": cls.MAX_ALERTS_PER_HOUR,
            "max_competitors_per_analysis": cls.MAX_COMPETITORS_PER_ANALYSIS,
            "max_profiles_per_thread": cls.MAX_PROFILES_PER_THREAD,
            "max_insights_per_thread": cls.MAX_INSIGHTS_PER_THREAD
        }
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize configuration."""
        validated = config.copy()
        
        # Validate monitoring frequency
        freq = validated.get("monitoring_frequency", cls.DEFAULT_MONITORING_FREQUENCY)
        validated["monitoring_frequency"] = max(cls.MIN_MONITORING_FREQUENCY, 
                                             min(cls.MAX_MONITORING_FREQUENCY, freq))
        
        # Validate confidence threshold
        threshold = validated.get("confidence_threshold", cls.MIN_CONFIDENCE_THRESHOLD)
        validated["confidence_threshold"] = max(0.0, min(1.0, threshold))
        
        return validated


class CompetitorOperationType(str, Enum):
    """Types of competitor intelligence operations."""
    DISCOVER = "discover"
    ANALYZE = "analyze"
    MONITOR = "monitor"
    REPORT = "report"
    BENCHMARK = "benchmark"
    TRACK_INSIGHT = "track_insight"
    GROUP = "group"


class CompetitorDataSource(str, Enum):
    """Sources of competitor intelligence."""
    WEB_SCRAPING = "web_scraping"
    SOCIAL_MEDIA = "social_media"
    NEWS_ARTICLES = "news_articles"
    FINANCIAL_REPORTS = "financial_reports"
    USER_REPORTS = "user_reports"
    AUTOMATED_MONITORING = "automated_monitoring"
    MANUAL_RESEARCH = "manual_research"
    API_INTEGRATION = "api_integration"


class CompetitorAlertType(str, Enum):
    """Types of competitor alerts."""
    PRICE_CHANGE = "price_change"
    FEATURE_LAUNCH = "feature_launch"
    MARKETING_CAMPAIGN = "marketing_campaign"
    WEBSITE_UPDATE = "website_update"
    PARTNERSHIP_ANNOUNCEMENT = "partnership_announcement"
    FUNDING_NEWS = "funding_news"
    EXECUTIVE_CHANGE = "executive_change"
    MARKET_EXPANSION = "market_expansion"


# Default prompts for competitor intelligence
DEFAULT_COMPETITOR_PROMPTS = {
    "discovery": (
        "You are a competitive intelligence expert. Discover and profile competitors "
        "in the specified market. Focus on identifying key players, their positioning, "
        "and strategic significance. Provide detailed profiles with confidence scores."
    ),
    "analysis": (
        "You are a strategic analyst. Perform comprehensive competitive analysis "
        "including SWOT assessment, positioning analysis, and threat evaluation. "
        "Provide actionable insights and strategic recommendations."
    ),
    "monitoring": (
        "You are a market intelligence monitor. Track competitor activities and "
        "identify significant changes, trends, and opportunities. Generate alerts "
        "for important developments."
    )
}
