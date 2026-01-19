"""
Channel Strategy Optimizer Agent
Optimizes GTM channel selection and prioritization
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ChannelType(Enum):
    """Types of marketing channels"""
    CONTENT = "content"  # Blog, SEO, thought leadership
    PAID_SEARCH = "paid_search"  # Google Ads, Bing
    PAID_SOCIAL = "paid_social"  # LinkedIn, Facebook, Twitter ads
    ORGANIC_SOCIAL = "organic_social"  # Social media organic
    EMAIL = "email"  # Email marketing, newsletters
    EVENTS = "events"  # Conferences, webinars, meetups
    PARTNERSHIPS = "partnerships"  # Partner marketing, integrations
    OUTBOUND = "outbound"  # Cold outreach, sales-led
    COMMUNITY = "community"  # Community building, forums
    PR = "pr"  # Press, media relations
    REFERRAL = "referral"  # Customer referral programs
    PRODUCT_LED = "product_led"  # PLG, freemium, trials


class ChannelPhase(Enum):
    """Go-to-market phase"""
    DISCOVERY = "discovery"
    CONSIDERATION = "consideration"
    DECISION = "decision"
    RETENTION = "retention"


class BudgetTier(Enum):
    """Budget tier"""
    BOOTSTRAP = "bootstrap"  # < $5K/month
    GROWTH = "growth"  # $5K-$25K/month
    SCALE = "scale"  # $25K-$100K/month
    ENTERPRISE = "enterprise"  # $100K+/month


@dataclass
class ChannelRecommendation:
    """A channel recommendation"""
    id: str
    channel: ChannelType
    name: str
    description: str
    fit_score: float  # 0-100
    effort: str  # low, medium, high
    time_to_results: str  # immediate, weeks, months
    budget_required: str
    priority: int  # 1 = highest
    tactics: List[str]
    kpis: List[str]
    risks: List[str]
    synergies: List[str]  # Works well with these channels


@dataclass
class ChannelMix:
    """Recommended channel mix"""
    primary_channels: List[ChannelRecommendation]
    secondary_channels: List[ChannelRecommendation]
    future_channels: List[ChannelRecommendation]
    budget_allocation: Dict[str, float]  # channel -> percentage
    timeline: Dict[str, str]  # phase -> channels
    total_score: float
    recommendations: List[str]
    summary: str


class ChannelStrategyOptimizer:
    """AI-powered channel strategy optimization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.channel_counter = 0
        self.channel_data = self._load_channel_data()
    
    def _generate_channel_id(self) -> str:
        self.channel_counter += 1
        return f"CHN-{self.channel_counter:03d}"
    
    def _load_channel_data(self) -> Dict[str, Dict[str, Any]]:
        """Load channel characteristics"""
        return {
            ChannelType.CONTENT: {
                "name": "Content Marketing & SEO",
                "description": "Blog posts, guides, thought leadership for organic search",
                "effort": "high",
                "time_to_results": "3-6 months",
                "budget_required": "$2K-$10K/month",
                "best_for": ["saas", "b2b", "complex_products"],
                "tactics": ["Blog strategy", "SEO optimization", "Content calendar", "Guest posting"],
                "kpis": ["Organic traffic", "Domain authority", "Content engagement", "Lead generation"],
                "risks": ["Long time to ROI", "Requires consistency", "Content quality variance"],
            },
            ChannelType.PAID_SEARCH: {
                "name": "Paid Search (SEM)",
                "description": "Google Ads, Bing Ads for high-intent traffic",
                "effort": "medium",
                "time_to_results": "immediate",
                "budget_required": "$5K-$50K/month",
                "best_for": ["high_intent", "established_category", "b2b"],
                "tactics": ["Keyword research", "Ad copy testing", "Landing page optimization", "Bid management"],
                "kpis": ["CPC", "Conversion rate", "ROAS", "Quality score"],
                "risks": ["Rising CPCs", "Competition", "Budget burn"],
            },
            ChannelType.PAID_SOCIAL: {
                "name": "Paid Social Advertising",
                "description": "LinkedIn, Facebook, Twitter ads for targeted reach",
                "effort": "medium",
                "time_to_results": "1-4 weeks",
                "budget_required": "$3K-$30K/month",
                "best_for": ["b2b_linkedin", "awareness", "retargeting"],
                "tactics": ["Audience targeting", "Creative testing", "Retargeting", "Lead gen forms"],
                "kpis": ["CPL", "CTR", "Conversion rate", "Reach"],
                "risks": ["Ad fatigue", "Platform changes", "Rising costs"],
            },
            ChannelType.ORGANIC_SOCIAL: {
                "name": "Organic Social Media",
                "description": "Building audience on LinkedIn, Twitter, etc.",
                "effort": "medium",
                "time_to_results": "2-6 months",
                "budget_required": "$0-$2K/month",
                "best_for": ["thought_leadership", "community", "brand"],
                "tactics": ["Content calendar", "Engagement strategy", "Community building", "Employee advocacy"],
                "kpis": ["Followers", "Engagement rate", "Reach", "Share of voice"],
                "risks": ["Algorithm changes", "Time intensive", "Slow growth"],
            },
            ChannelType.EMAIL: {
                "name": "Email Marketing",
                "description": "Nurture sequences, newsletters, campaigns",
                "effort": "medium",
                "time_to_results": "1-2 months",
                "budget_required": "$500-$5K/month",
                "best_for": ["nurturing", "retention", "upsell"],
                "tactics": ["List building", "Segmentation", "Automation", "A/B testing"],
                "kpis": ["Open rate", "Click rate", "Conversion", "List growth"],
                "risks": ["Deliverability", "List fatigue", "Spam complaints"],
            },
            ChannelType.OUTBOUND: {
                "name": "Outbound Sales",
                "description": "Cold email, LinkedIn outreach, cold calling",
                "effort": "high",
                "time_to_results": "1-3 months",
                "budget_required": "$5K-$20K/month",
                "best_for": ["enterprise", "high_aov", "targeted"],
                "tactics": ["Prospect research", "Personalization", "Multi-touch sequences", "Social selling"],
                "kpis": ["Reply rate", "Meeting rate", "Pipeline", "Win rate"],
                "risks": ["Spam filters", "Brand risk", "High effort per lead"],
            },
            ChannelType.PRODUCT_LED: {
                "name": "Product-Led Growth",
                "description": "Free trials, freemium, self-serve onboarding",
                "effort": "high",
                "time_to_results": "3-6 months",
                "budget_required": "$0-$5K/month",
                "best_for": ["saas", "self_serve", "viral_potential"],
                "tactics": ["Free tier design", "Onboarding optimization", "In-app upsells", "Viral loops"],
                "kpis": ["Signups", "Activation", "Conversion to paid", "Expansion revenue"],
                "risks": ["Free user costs", "Conversion challenges", "Support burden"],
            },
            ChannelType.EVENTS: {
                "name": "Events & Webinars",
                "description": "Conferences, webinars, meetups for engagement",
                "effort": "high",
                "time_to_results": "1-3 months",
                "budget_required": "$2K-$50K/month",
                "best_for": ["enterprise", "education", "demos"],
                "tactics": ["Webinar series", "Conference speaking", "User meetups", "Virtual events"],
                "kpis": ["Registrations", "Attendance", "Leads", "Pipeline"],
                "risks": ["High cost", "Low show rates", "Planning overhead"],
            },
            ChannelType.PARTNERSHIPS: {
                "name": "Partnerships & Integrations",
                "description": "Co-marketing, integration partnerships, affiliates",
                "effort": "high",
                "time_to_results": "3-6 months",
                "budget_required": "$0-$10K/month",
                "best_for": ["ecosystem", "enterprise", "expansion"],
                "tactics": ["Partner program", "Co-marketing", "Integration directory", "Affiliate program"],
                "kpis": ["Partner leads", "Integration usage", "Co-sell deals", "Affiliate revenue"],
                "risks": ["Partner dependency", "Long sales cycles", "Management overhead"],
            },
            ChannelType.REFERRAL: {
                "name": "Referral Programs",
                "description": "Customer referral incentives and programs",
                "effort": "low",
                "time_to_results": "1-3 months",
                "budget_required": "$0-$5K/month",
                "best_for": ["viral", "nps_high", "b2c_b2b"],
                "tactics": ["Referral incentives", "Customer advocacy", "Review programs", "Case studies"],
                "kpis": ["Referral rate", "NPS", "Reviews", "Referral revenue"],
                "risks": ["Gaming", "Low adoption", "Incentive costs"],
            },
        }
    
    def _calculate_fit_score(self, channel: ChannelType, company_info: Dict, icp_data: Dict, positioning: Dict) -> float:
        """Calculate how well a channel fits the company"""
        score = 50  # Base score
        
        channel_data = self.channel_data.get(channel, {})
        best_for = channel_data.get("best_for", [])
        
        # Industry/category fit
        category = company_info.get("category", "").lower()
        if "saas" in category and "saas" in best_for:
            score += 15
        if "b2b" in category and "b2b" in best_for:
            score += 10
        
        # Stage fit
        stage = company_info.get("stage", "growth")
        if stage == "startup" and channel in [ChannelType.CONTENT, ChannelType.ORGANIC_SOCIAL, ChannelType.PRODUCT_LED]:
            score += 10
        elif stage == "growth" and channel in [ChannelType.PAID_SEARCH, ChannelType.PAID_SOCIAL]:
            score += 10
        elif stage == "enterprise" and channel in [ChannelType.OUTBOUND, ChannelType.EVENTS, ChannelType.PARTNERSHIPS]:
            score += 10
        
        # ICP fit
        icp_segment = icp_data.get("tier", "")
        if "enterprise" in str(icp_segment).lower() and channel == ChannelType.OUTBOUND:
            score += 15
        if "startup" in str(icp_segment).lower() and channel == ChannelType.PRODUCT_LED:
            score += 15
        
        # Category path fit
        category_path = positioning.get("category_path", "safe")
        if category_path == "bold" and channel in [ChannelType.CONTENT, ChannelType.PR, ChannelType.EVENTS]:
            score += 10  # Category creators need education
        
        return min(100, max(0, score))
    
    async def optimize_channel_strategy(self, company_info: Dict[str, Any], icp_data: Dict[str, Any] = None, positioning: Dict[str, Any] = None, budget_tier: str = "growth") -> ChannelMix:
        """
        Optimize channel strategy for GTM
        
        Args:
            company_info: Company information
            icp_data: ICP profile data
            positioning: Positioning data
            budget_tier: Budget tier (bootstrap, growth, scale, enterprise)
        
        Returns:
            ChannelMix with prioritized channel recommendations
        """
        icp_data = icp_data or {}
        positioning = positioning or {}
        
        # Score all channels
        channel_scores = []
        for channel_type, data in self.channel_data.items():
            fit_score = self._calculate_fit_score(channel_type, company_info, icp_data, positioning)
            
            recommendation = ChannelRecommendation(
                id=self._generate_channel_id(),
                channel=channel_type,
                name=data["name"],
                description=data["description"],
                fit_score=fit_score,
                effort=data["effort"],
                time_to_results=data["time_to_results"],
                budget_required=data["budget_required"],
                priority=0,  # Will be set after sorting
                tactics=data["tactics"],
                kpis=data["kpis"],
                risks=data["risks"],
                synergies=[]  # Will be filled
            )
            channel_scores.append(recommendation)
        
        # Sort by fit score
        channel_scores.sort(key=lambda x: x.fit_score, reverse=True)
        
        # Assign priorities
        for i, channel in enumerate(channel_scores):
            channel.priority = i + 1
        
        # Split into categories
        primary = channel_scores[:3]
        secondary = channel_scores[3:6]
        future = channel_scores[6:]
        
        # Calculate budget allocation
        total_primary_score = sum(c.fit_score for c in primary)
        budget_allocation = {}
        for channel in primary:
            budget_allocation[channel.channel.value] = round((channel.fit_score / total_primary_score) * 100, 1)
        
        # Create timeline
        timeline = {
            "month_1": ", ".join([c.name for c in primary[:2]]),
            "month_2_3": ", ".join([c.name for c in primary]),
            "month_4_6": ", ".join([c.name for c in primary + secondary[:2]]),
        }
        
        # Recommendations
        recommendations = [
            f"Start with {primary[0].name} - highest fit score ({primary[0].fit_score:.0f}%)",
            f"Add {primary[1].name} in parallel for quick wins",
            f"Consider {secondary[0].name} once primary channels are optimized",
        ]
        
        total_score = sum(c.fit_score for c in primary) / len(primary) if primary else 0
        
        summary = f"Analyzed {len(channel_scores)} channels. Top 3: {', '.join([c.name for c in primary])}. "
        summary += f"Average fit score: {total_score:.0f}%."
        
        return ChannelMix(
            primary_channels=primary,
            secondary_channels=secondary,
            future_channels=future,
            budget_allocation=budget_allocation,
            timeline=timeline,
            total_score=total_score,
            recommendations=recommendations,
            summary=summary
        )
    
    def get_strategy_summary(self, mix: ChannelMix) -> Dict[str, Any]:
        """Get summary for display"""
        return {
            "primary_channels": [{"name": c.name, "score": c.fit_score, "effort": c.effort} for c in mix.primary_channels],
            "secondary_channels": [{"name": c.name, "score": c.fit_score} for c in mix.secondary_channels],
            "budget_allocation": mix.budget_allocation,
            "timeline": mix.timeline,
            "recommendations": mix.recommendations,
            "summary": mix.summary
        }
