"""
Radar Analytics Service - Advanced analytics and insights for competitive intelligence
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from models.radar_models import (
    Signal,
    SignalCategory,
    SignalCluster,
    SignalFreshness,
    SignalStrength,
)

logger = logging.getLogger("raptorflow.radar_analytics")


class RadarAnalyticsService:
    """
    Advanced analytics service for Radar signals and competitive intelligence.
    Provides trend analysis, competitor insights, and predictive analytics.
    """

    def __init__(self):
        # Trend analysis windows
        self.analysis_windows = {
            "daily": 7,
            "weekly": 30,
            "monthly": 90,
        }

    async def analyze_signal_trends(
        self, 
        signals: List[Signal], 
        window_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze signal trends over time."""
        cutoff_date = datetime.utcnow() - timedelta(days=window_days)
        recent_signals = [s for s in signals if s.created_at >= cutoff_date]
        
        # Group signals by day and category
        daily_signals = {}
        category_trends = {}
        
        for signal in recent_signals:
            day_key = signal.created_at.date().isoformat()
            
            if day_key not in daily_signals:
                daily_signals[day_key] = {"total": 0}
                for category in SignalCategory:
                    daily_signals[day_key][category.value] = 0
            
            daily_signals[day_key]["total"] += 1
            daily_signals[day_key][signal.category.value] += 1
        
        # Calculate category trends
        for category in SignalCategory:
            category_signals = [s for s in recent_signals if s.category == category]
            category_trends[category.value] = {
                "count": len(category_signals),
                "strength_distribution": self._calculate_strength_distribution(category_signals),
                "freshness_distribution": self._calculate_freshness_distribution(category_signals),
                "growth_rate": self._calculate_growth_rate(category_signals, window_days),
            }
        
        return {
            "period_days": window_days,
            "total_signals": len(recent_signals),
            "daily_signals": daily_signals,
            "category_trends": category_trends,
            "top_competitors": self._get_top_competitors(recent_signals),
            "signal_velocity": self._calculate_signal_velocity(recent_signals),
        }

    async def analyze_competitor_patterns(
        self, 
        signals: List[Signal]
    ) -> Dict[str, Any]:
        """Analyze competitor behavior patterns."""
        competitor_analysis = {}
        
        # Group signals by competitor
        by_competitor = {}
        for signal in signals:
            competitor = signal.source_competitor or "Unknown"
            if competitor not in by_competitor:
                by_competitor[competitor] = []
            by_competitor[competitor].append(signal)
        
        # Analyze each competitor
        for competitor, competitor_signals in by_competitor.items():
            analysis = {
                "total_signals": len(competitor_signals),
                "category_breakdown": self._get_category_breakdown(competitor_signals),
                "activity_pattern": self._analyze_activity_pattern(competitor_signals),
                "strength_profile": self._calculate_strength_profile(competitor_signals),
                "recent_focus": self._get_recent_focus(competitor_signals),
                "threat_level": self._assess_threat_level(competitor_signals),
            }
            competitor_analysis[competitor] = analysis
        
        return {
            "competitors": competitor_analysis,
            "market_leaders": self._identify_market_leaders(competitor_analysis),
            "emerging_threats": self._identify_emerging_threats(competitor_analysis),
        }

    def _identify_market_leaders(self, competitor_analysis: Dict[str, Any]) -> List[str]:
        """Identify market leaders based on signal volume and strength."""
        leaders = []
        for competitor, analysis in competitor_analysis.items():
            if analysis["total_signals"] > 10 and analysis["strength_profile"]["high_strength"] > 0.3:
                leaders.append(competitor)
        return leaders[:3]  # Top 3 leaders

    def _identify_emerging_threats(self, competitor_analysis: Dict[str, Any]) -> List[str]:
        """Identify emerging threats based on recent activity spikes."""
        threats = []
        for competitor, analysis in competitor_analysis.items():
            if analysis["activity_pattern"]["recent_spike"] and analysis["threat_level"] in ["medium", "high"]:
                threats.append(competitor)
        return threats[:3]  # Top 3 threats

    async def generate_market_intelligence(
        self, 
        signals: List[Signal], 
        clusters: List[SignalCluster]
    ) -> Dict[str, Any]:
        """Generate comprehensive market intelligence."""
        # Signal analysis
        signal_insights = await self.analyze_signal_trends(signals)
        competitor_insights = await self.analyze_competitor_patterns(signals)
        
        # Cluster analysis
        cluster_insights = self._analyze_clusters(clusters)
        
        # Market dynamics
        market_dynamics = self._analyze_market_dynamics(signals, clusters)
        
        # Predictive insights
        predictive_insights = self._generate_predictive_insights(signals, clusters)
        
        return {
            "signal_trends": signal_insights,
            "competitor_analysis": competitor_insights,
            "cluster_analysis": cluster_insights,
            "market_dynamics": market_dynamics,
            "predictive_insights": predictive_insights,
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def identify_opportunities(
        self, 
        signals: List[Signal], 
        tenant_objectives: List[str]
    ) -> List[Dict[str, Any]]:
        """Identify strategic opportunities based on signal analysis."""
        opportunities = []
        
        # Analyze gaps in competitor offerings
        offer_gaps = self._identify_offer_gaps(signals)
        opportunities.extend(offer_gaps)
        
        # Analyze messaging opportunities
        messaging_opportunities = self._identify_messaging_opportunities(signals)
        opportunities.extend(messaging_opportunities)
        
        # Analyze timing opportunities
        timing_opportunities = self._identify_timing_opportunities(signals)
        opportunities.extend(timing_opportunities)
        
        # Score opportunities by relevance to objectives
        scored_opportunities = self._score_opportunities(opportunities, tenant_objectives)
        
        return sorted(scored_opportunities, key=lambda x: x["score"], reverse=True)[:10]

    def _calculate_strength_distribution(self, signals: List[Signal]) -> Dict[str, int]:
        """Calculate distribution of signal strengths."""
        distribution = {"low": 0, "medium": 0, "high": 0}
        for signal in signals:
            distribution[signal.strength.value] += 1
        return distribution

    def _calculate_freshness_distribution(self, signals: List[Signal]) -> Dict[str, int]:
        """Calculate distribution of signal freshness."""
        distribution = {"fresh": 0, "warm": 0, "stale": 0}
        for signal in signals:
            distribution[signal.freshness.value] += 1
        return distribution

    def _calculate_growth_rate(self, signals: List[Signal], window_days: int) -> float:
        """Calculate growth rate of signals over time window."""
        if len(signals) < 2:
            return 0.0
        
        # Split signals into two halves
        mid_point = len(signals) // 2
        first_half = signals[:mid_point]
        second_half = signals[mid_point:]
        
        # Calculate rate
        first_period_rate = len(first_half) / (window_days / 2)
        second_period_rate = len(second_half) / (window_days / 2)
        
        if first_period_rate == 0:
            return 100.0 if second_period_rate > 0 else 0.0
        
        growth = ((second_period_rate - first_period_rate) / first_period_rate) * 100
        return round(growth, 2)

    def _get_top_competitors(self, signals: List[Signal]) -> List[Dict[str, Any]]:
        """Get most active competitors."""
        competitor_counts = {}
        for signal in signals:
            competitor = signal.source_competitor or "Unknown"
            competitor_counts[competitor] = competitor_counts.get(competitor, 0) + 1
        
        # Sort and return top 5
        sorted_competitors = sorted(competitor_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {"competitor": name, "signal_count": count}
            for name, count in sorted_competitors[:5]
        ]

    def _calculate_signal_velocity(self, signals: List[Signal]) -> Dict[str, float]:
        """Calculate signal velocity (signals per day)."""
        if not signals:
            return {"velocity": 0.0, "trend": "stable"}
        
        # Calculate date range
        dates = [s.created_at.date() for s in signals]
        date_range = (max(dates) - min(dates)).days + 1
        
        velocity = len(signals) / date_range
        
        # Determine trend
        recent_signals = [s for s in signals if s.created_at >= datetime.utcnow() - timedelta(days=7)]
        recent_velocity = len(recent_signals) / 7
        
        if recent_velocity > velocity * 1.2:
            trend = "accelerating"
        elif recent_velocity < velocity * 0.8:
            trend = "decelerating"
        else:
            trend = "stable"
        
        return {
            "velocity": round(velocity, 2),
            "recent_velocity": round(recent_velocity, 2),
            "trend": trend,
        }

    def _get_category_breakdown(self, signals: List[Signal]) -> Dict[str, int]:
        """Get breakdown of signals by category."""
        breakdown = {}
        for signal in signals:
            category = signal.category.value
            breakdown[category] = breakdown.get(category, 0) + 1
        return breakdown

    def _analyze_activity_pattern(self, signals: List[Signal]) -> Dict[str, Any]:
        """Analyze competitor activity patterns."""
        if not signals:
            return {"pattern": "inactive", "frequency": 0}
        
        # Calculate days between signals
        sorted_signals = sorted(signals, key=lambda x: x.created_at)
        intervals = []
        
        for i in range(1, len(sorted_signals)):
            interval = (sorted_signals[i].created_at - sorted_signals[i-1].created_at).days
            intervals.append(interval)
        
        if not intervals:
            return {"pattern": "single_event", "frequency": 0}
        
        avg_interval = sum(intervals) / len(intervals)
        
        if avg_interval <= 7:
            pattern = "highly_active"
        elif avg_interval <= 30:
            pattern = "moderately_active"
        else:
            pattern = "sporadic"
        
        # Check for recent spike (last 7 days vs previous 7 days)
        recent_spike = False
        if len(signals) >= 2:
            now = datetime.utcnow()
            week_ago = now - timedelta(days=7)
            two_weeks_ago = now - timedelta(days=14)
            
            recent_signals = [s for s in signals if s.created_at >= week_ago]
            previous_signals = [s for s in signals if two_weeks_ago <= s.created_at < week_ago]
            
            if len(recent_signals) > len(previous_signals) * 2:
                recent_spike = True
        
        return {
            "pattern": pattern,
            "frequency": round(1 / avg_interval, 3) if avg_interval > 0 else 0,
            "avg_interval_days": round(avg_interval, 1),
            "recent_spike": recent_spike,
        }

    def _calculate_strength_profile(self, signals: List[Signal]) -> Dict[str, Any]:
        """Calculate strength profile for competitor signals."""
        if not signals:
            return {"avg_strength": 0.0, "high_strength_ratio": 0.0}
        
        strength_values = [self._strength_to_numeric(s.strength) for s in signals]
        avg_strength = sum(strength_values) / len(strength_values)
        
        high_strength_count = len([s for s in signals if s.strength == SignalStrength.HIGH])
        high_strength_ratio = high_strength_count / len(signals)
        
        return {
            "avg_strength": round(avg_strength, 2),
            "high_strength": round(high_strength_ratio, 2),
            "strength_distribution": self._calculate_strength_distribution(signals),
        }

    def _get_recent_focus(self, signals: List[Signal]) -> List[str]:
        """Get competitor's recent focus areas."""
        recent_signals = [s for s in signals if s.freshness == SignalFreshness.FRESH]
        category_counts = {}
        
        for signal in recent_signals:
            category = signal.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Sort by frequency and return top 3
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        return [category for category, count in sorted_categories[:3]]

    def _assess_threat_level(self, signals: List[Signal]) -> str:
        """Assess threat level based on signal analysis."""
        if not signals:
            return "low"
        
        # Factors for threat assessment
        high_strength_ratio = len([s for s in signals if s.strength == SignalStrength.HIGH]) / len(signals)
        recent_activity = len([s for s in signals if s.freshness == SignalFreshness.FRESH]) / len(signals)
        signal_diversity = len(set(s.category for s in signals)) / len(SignalCategory)
        
        threat_score = (high_strength_ratio * 0.4) + (recent_activity * 0.4) + (signal_diversity * 0.2)
        
        if threat_score >= 0.7:
            return "high"
        elif threat_score >= 0.4:
            return "medium"
        else:
            return "low"

    def _strength_to_numeric(self, strength: SignalStrength) -> float:
        """Convert strength to numeric value."""
        mapping = {
            SignalStrength.LOW: 0.3,
            SignalStrength.MEDIUM: 0.6,
            SignalStrength.HIGH: 0.9,
        }
        return mapping.get(strength, 0.5)

    def _analyze_clusters(self, clusters: List[SignalCluster]) -> Dict[str, Any]:
        """Analyze signal clusters."""
        if not clusters:
            return {"total_clusters": 0, "top_themes": []}
        
        # Sort clusters by signal count
        sorted_clusters = sorted(clusters, key=lambda x: x.signal_count, reverse=True)
        
        return {
            "total_clusters": len(clusters),
            "avg_cluster_size": round(sum(c.signal_count for c in clusters) / len(clusters), 1),
            "top_themes": [
                {"theme": cluster.theme, "signal_count": cluster.signal_count, "category": cluster.category.value}
                for cluster in sorted_clusters[:5]
            ],
            "category_distribution": self._get_cluster_category_distribution(clusters),
        }

    def _get_cluster_category_distribution(self, clusters: List[SignalCluster]) -> Dict[str, int]:
        """Get distribution of clusters by category."""
        distribution = {}
        for cluster in clusters:
            category = cluster.category.value
            distribution[category] = distribution.get(category, 0) + 1
        return distribution

    def _analyze_market_dynamics(self, signals: List[Signal], clusters: List[SignalCluster]) -> Dict[str, Any]:
        """Analyze overall market dynamics."""
        # Signal velocity
        total_signals = len(signals)
        recent_signals = len([s for s in signals if s.freshness == SignalFreshness.FRESH])
        
        # Market activity level
        if recent_signals > total_signals * 0.5:
            activity_level = "high"
        elif recent_signals > total_signals * 0.25:
            activity_level = "medium"
        else:
            activity_level = "low"
        
        return {
            "activity_level": activity_level,
            "signal_density": total_signals,
            "cluster_density": len(clusters),
            "market_maturity": self._assess_market_maturity(signals, clusters),
        }

    def _assess_market_maturity(self, signals: List[Signal], clusters: List[SignalCluster]) -> str:
        """Assess market maturity based on signal patterns."""
        # High diversity and clustering indicates mature market
        signal_diversity = len(set(s.category for s in signals))
        cluster_ratio = len(clusters) / len(signals) if signals else 0
        
        if signal_diversity >= 4 and cluster_ratio > 0.3:
            return "mature"
        elif signal_diversity >= 2:
            return "developing"
        else:
            return "emerging"

    def _generate_predictive_insights(self, signals: List[Signal], clusters: List[SignalCluster]) -> List[Dict[str, Any]]:
        """Generate predictive insights based on signal analysis."""
        insights = []
        
        # Trend predictions
        trend_signals = [s for s in signals if s.category == SignalCategory.TREND]
        if len(trend_signals) > 3:
            insights.append({
                "type": "trend_prediction",
                "confidence": 0.7,
                "insight": "High trend activity suggests market evolution phase",
                "action": "Monitor for additional trend signals",
            })
        
        # Competitive pressure
        high_strength_signals = [s for s in signals if s.strength == SignalStrength.HIGH]
        if len(high_strength_signals) > len(signals) * 0.3:
            insights.append({
                "type": "competitive_pressure",
                "confidence": 0.8,
                "insight": "High proportion of strong signals indicates competitive pressure",
                "action": "Review competitive positioning",
            })
        
        return insights

    def _identify_offer_gaps(self, signals: List[Signal]) -> List[Dict[str, Any]]:
        """Identify gaps in competitor offerings."""
        # This would analyze pricing gaps, feature gaps, etc.
        return []

    def _identify_messaging_opportunities(self, signals: List[Signal]) -> List[Dict[str, Any]]:
        """Identify messaging opportunities."""
        # This would analyze messaging patterns and gaps
        return []

    def _identify_timing_opportunities(self, signals: List[Signal]) -> List[Dict[str, Any]]:
        """Identify timing opportunities."""
        # This would analyze timing patterns
        return []

    def _score_opportunities(self, opportunities: List[Dict[str, Any]], objectives: List[str]) -> List[Dict[str, Any]]:
        """Score opportunities based on alignment with objectives."""
        # This would score opportunities based on relevance to objectives
        return opportunities
