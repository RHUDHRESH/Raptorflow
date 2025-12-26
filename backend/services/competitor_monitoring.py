import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass
from enum import Enum

from models.swarm import (
    CompetitorProfile,
    CompetitorGroup,
    CompetitorInsight,
    CompetitorAnalysis,
    CompetitorType,
    CompetitorThreatLevel,
    SwarmState,
)
from memory.swarm_l1 import SwarmL1MemoryManager

logger = logging.getLogger("raptorflow.services.competitor_monitoring")


class MonitoringFrequency(str, Enum):
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class CompetitorAlert:
    """Alert for significant competitor activity."""
    competitor_id: str
    alert_type: str
    severity: str
    title: str
    description: str
    detected_at: datetime
    confidence: float


class CompetitorMonitoringService:
    """
    Service for monitoring competitor activities and generating intelligence.
    Provides automated competitor tracking, analysis, and alerting capabilities.
    """

    def __init__(self, memory_manager: SwarmL1MemoryManager):
        self.memory_manager = memory_manager
        self.monitoring_active = False
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}

    async def start_monitoring(self, competitor_ids: List[str], frequency: MonitoringFrequency = MonitoringFrequency.DAILY):
        """Start monitoring specified competitors."""
        logger.info(f"Starting competitor monitoring for {len(competitor_ids)} competitors")
        
        self.monitoring_active = True
        
        # Update watchlist in memory
        await self.memory_manager.update_competitor_watchlist(competitor_ids)
        
        # Start monitoring task for each frequency
        task_key = f"monitor_{frequency.value}"
        if task_key in self.monitoring_tasks:
            self.monitoring_tasks[task_key].cancel()
        
        self.monitoring_tasks[task_key] = asyncio.create_task(
            self._monitoring_loop(competitor_ids, frequency)
        )
        
        logger.info(f"Competitor monitoring started with frequency: {frequency.value}")

    async def stop_monitoring(self):
        """Stop all competitor monitoring activities."""
        logger.info("Stopping competitor monitoring...")
        
        self.monitoring_active = False
        
        # Cancel all monitoring tasks
        for task in self.monitoring_tasks.values():
            if not task.done():
                task.cancel()
        
        self.monitoring_tasks.clear()
        logger.info("Competitor monitoring stopped")

    async def _monitoring_loop(self, competitor_ids: List[str], frequency: MonitoringFrequency):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                await self._perform_competitor_scan(competitor_ids)
                await self._update_last_scan_time()
                
                # Sleep based on frequency
                sleep_duration = self._get_sleep_duration(frequency)
                await asyncio.sleep(sleep_duration)
                
            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _perform_competitor_scan(self, competitor_ids: List[str]):
        """Perform a scan of competitor activities."""
        logger.info(f"Performing competitor scan for {len(competitor_ids)} competitors")
        
        alerts = []
        
        for competitor_id in competitor_ids:
            try:
                # Get competitor profile
                profile = await self.memory_manager.get_competitor_profile(competitor_id)
                if not profile:
                    logger.warning(f"Competitor profile not found: {competitor_id}")
                    continue
                
                # Scan for changes (mock implementation)
                new_alerts = await self._scan_competitor_changes(profile)
                alerts.extend(new_alerts)
                
                # Update last scan time for this competitor
                profile.last_updated = datetime.now()
                await self.memory_manager.update_competitor_profile(profile)
                
            except Exception as e:
                logger.error(f"Error scanning competitor {competitor_id}: {e}")
        
        # Process alerts
        if alerts:
            await self._process_alerts(alerts)
        
        logger.info(f"Competitor scan completed. Generated {len(alerts)} alerts")

    async def _scan_competitor_changes(self, profile: CompetitorProfile) -> List[CompetitorAlert]:
        """Scan for changes in competitor profile (mock implementation)."""
        alerts = []
        
        # In a real implementation, this would:
        # - Scrape competitor websites
        # - Monitor social media
        # - Check news sources
        # - Analyze pricing changes
        # - Track feature updates
        
        # Mock detection of changes
        if profile.website:
            # Simulate detecting a website change
            alert = CompetitorAlert(
                competitor_id=profile.id,
                alert_type="website_update",
                severity="medium",
                title=f"Website Update Detected: {profile.name}",
                description=f"Changes detected on {profile.website}",
                detected_at=datetime.now(),
                confidence=0.8
            )
            alerts.append(alert)
        
        return alerts

    async def _process_alerts(self, alerts: List[CompetitorAlert]):
        """Process generated competitor alerts."""
        logger.info(f"Processing {len(alerts)} competitor alerts")
        
        for alert in alerts:
            try:
                # Convert alert to insight
                insight = CompetitorInsight(
                    id=f"alert_{alert.competitor_id}_{int(alert.detected_at.timestamp())}",
                    competitor_id=alert.competitor_id,
                    insight_type=alert.alert_type,
                    title=alert.title,
                    description=alert.description,
                    impact_assessment=alert.severity,
                    confidence=alert.confidence,
                    source="automated_monitoring",
                    tags=["monitoring", alert.alert_type, alert.severity]
                )
                
                # Store insight
                await self.memory_manager.add_competitor_insight(insight)
                
                logger.info(f"Processed alert: {alert.title}")
                
            except Exception as e:
                logger.error(f"Error processing alert: {e}")

    async def _update_last_scan_time(self):
        """Update the timestamp of the last competitor scan."""
        await self.memory_manager.update_last_competitor_scan(datetime.now())

    def _get_sleep_duration(self, frequency: MonitoringFrequency) -> int:
        """Get sleep duration in seconds based on frequency."""
        frequency_map = {
            MonitoringFrequency.REAL_TIME: 60,      # 1 minute
            MonitoringFrequency.HOURLY: 3600,       # 1 hour
            MonitoringFrequency.DAILY: 86400,      # 24 hours
            MonitoringFrequency.WEEKLY: 604800,    # 7 days
            MonitoringFrequency.MONTHLY: 2592000,  # 30 days
        }
        return frequency_map.get(frequency, 86400)

    async def generate_competitor_intelligence_report(self, competitor_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate comprehensive competitor intelligence report."""
        logger.info("Generating competitor intelligence report...")
        
        # Get all competitor profiles if none specified
        if competitor_ids is None:
            all_profiles = await self.memory_manager.get_all_competitor_profiles()
            competitor_ids = [p.id for p in all_profiles]
        
        # Gather data
        profiles = []
        insights = []
        analyses = []
        
        for competitor_id in competitor_ids:
            profile = await self.memory_manager.get_competitor_profile(competitor_id)
            if profile:
                profiles.append(profile)
        
        all_insights = await self.memory_manager.get_all_competitor_insights()
        insights = [i for i in all_insights if i.competitor_id in competitor_ids]
        
        all_analyses = await self.memory_manager.get_all_competitor_analyses()
        analyses = [a for a in all_analyses if any(cid in a.competitor_ids for cid in competitor_ids)]
        
        # Generate report
        report = {
            "generated_at": datetime.now().isoformat(),
            "competitors_analyzed": len(profiles),
            "total_insights": len(insights),
            "total_analyses": len(analyses),
            "competitor_profiles": [p.model_dump() for p in profiles],
            "recent_insights": [i.model_dump() for i in sorted(insights, key=lambda x: x.discovered_at, reverse=True)[:10]],
            "latest_analyses": [a.model_dump() for a in sorted(analyses, key=lambda x: x.analyzed_at, reverse=True)[:5]],
            "threat_distribution": self._calculate_threat_distribution(profiles),
            "insight_trends": self._calculate_insight_trends(insights),
            "recommendations": self._generate_recommendations(profiles, insights, analyses)
        }
        
        logger.info(f"Competitor intelligence report generated for {len(profiles)} competitors")
        return report

    def _calculate_threat_distribution(self, profiles: List[CompetitorProfile]) -> Dict[str, int]:
        """Calculate distribution of threat levels among competitors."""
        distribution = {level.value: 0 for level in CompetitorThreatLevel}
        for profile in profiles:
            distribution[profile.threat_level.value] += 1
        return distribution

    def _calculate_insight_trends(self, insights: List[CompetitorInsight]) -> Dict[str, Any]:
        """Calculate trends from competitor insights."""
        if not insights:
            return {"total": 0, "by_type": {}, "by_impact": {}}
        
        # Group insights by type and impact
        by_type = {}
        by_impact = {"low": 0, "medium": 0, "high": 0}
        
        for insight in insights:
            # By type
            insight_type = insight.insight_type
            by_type[insight_type] = by_type.get(insight_type, 0) + 1
            
            # By impact
            impact = insight.impact_assessment.lower()
            if impact in by_impact:
                by_impact[impact] += 1
        
        return {
            "total": len(insights),
            "by_type": by_type,
            "by_impact": by_impact,
            "recent_count": len([i for i in insights if i.discovered_at > datetime.now() - timedelta(days=7)])
        }

    def _generate_recommendations(self, profiles: List[CompetitorProfile], insights: List[CompetitorInsight], analyses: List[CompetitorAnalysis]) -> List[str]:
        """Generate strategic recommendations based on competitor intelligence."""
        recommendations = []
        
        # High threat competitors
        high_threat = [p for p in profiles if p.threat_level == CompetitorThreatLevel.HIGH or p.threat_level == CompetitorThreatLevel.CRITICAL]
        if high_threat:
            recommendations.append(f"Priority monitoring required for {len(high_threat)} high-threat competitors")
        
        # Recent insights
        recent_insights = [i for i in insights if i.discovered_at > datetime.now() - timedelta(days=7)]
        if len(recent_insights) > 5:
            recommendations.append("High competitor activity detected - consider increasing monitoring frequency")
        
        # Market leaders
        market_leaders = [p for p in profiles if p.competitor_type == CompetitorType.MARKET_LEADER]
        if market_leaders:
            recommendations.append(f"Monitor {len(market_leaders)} market leaders for strategic positioning insights")
        
        # Common weaknesses
        if profiles:
            common_weaknesses = {}
            for profile in profiles:
                for weakness in profile.weaknesses:
                    common_weaknesses[weakness] = common_weaknesses.get(weakness, 0) + 1
            
            if common_weaknesses:
                most_common = max(common_weaknesses.items(), key=lambda x: x[1])
                recommendations.append(f"Common weakness identified: {most_common[0]} (appears in {most_common[1]} competitors)")
        
        return recommendations


class CompetitorAnalysisService:
    """
    Service for performing deep competitor analysis.
    Provides various analysis methods and strategic insights.
    """

    def __init__(self, memory_manager: SwarmL1MemoryManager):
        self.memory_manager = memory_manager

    async def perform_swot_analysis(self, competitor_ids: List[str]) -> Dict[str, Any]:
        """Perform SWOT analysis for specified competitors."""
        logger.info(f"Performing SWOT analysis for {len(competitor_ids)} competitors")
        
        swot_data = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": [],
            "competitor_specific": {}
        }
        
        for competitor_id in competitor_ids:
            profile = await self.memory_manager.get_competitor_profile(competitor_id)
            if not profile:
                continue
            
            competitor_swot = {
                "strengths": profile.strengths,
                "weaknesses": profile.weaknesses,
                "opportunities": profile.opportunities,
                "threats": profile.threats
            }
            
            swot_data["competitor_specific"][competitor_id] = competitor_swot
            
            # Aggregate data
            swot_data["strengths"].extend(profile.strengths)
            swot_data["weaknesses"].extend(profile.weaknesses)
            swot_data["opportunities"].extend(profile.opportunities)
            swot_data["threats"].extend(profile.threats)
        
        # Remove duplicates and count frequencies
        for category in ["strengths", "weaknesses", "opportunities", "threats"]:
            items = swot_data[category]
            unique_items = list(set(items))
            item_counts = {item: items.count(item) for item in unique_items}
            swot_data[category] = dict(sorted(item_counts.items(), key=lambda x: x[1], reverse=True))
        
        logger.info("SWOT analysis completed")
        return swot_data

    async def perform_positioning_analysis(self, competitor_ids: List[str]) -> Dict[str, Any]:
        """Analyze competitive positioning."""
        logger.info(f"Performing positioning analysis for {len(competitor_ids)} competitors")
        
        positioning_data = {
            "market_segments": {},
            "value_propositions": {},
            "target_audiences": {},
            "pricing_models": {},
            "threat_levels": {}
        }
        
        for competitor_id in competitor_ids:
            profile = await self.memory_manager.get_competitor_profile(competitor_id)
            if not profile:
                continue
            
            # Market segment analysis
            segment = profile.competitor_type.value
            positioning_data["market_segments"][segment] = positioning_data["market_segments"].get(segment, 0) + 1
            
            # Value proposition analysis
            if profile.value_proposition:
                vp = profile.value_proposition
                positioning_data["value_propositions"][competitor_id] = vp
            
            # Target audience analysis
            for audience in profile.target_audience:
                positioning_data["target_audiences"][audience] = positioning_data["target_audiences"].get(audience, 0) + 1
            
            # Pricing model analysis
            if profile.pricing_model:
                pm = profile.pricing_model
                positioning_data["pricing_models"][pm] = positioning_data["pricing_models"].get(pm, 0) + 1
            
            # Threat level analysis
            threat = profile.threat_level.value
            positioning_data["threat_levels"][threat] = positioning_data["threat_levels"].get(threat, 0) + 1
        
        logger.info("Positioning analysis completed")
        return positioning_data

    async def identify_competitive_gaps(self, competitor_ids: List[str]) -> List[str]:
        """Identify gaps in the competitive landscape."""
        logger.info(f"Identifying competitive gaps for {len(competitor_ids)} competitors")
        
        profiles = []
        for competitor_id in competitor_ids:
            profile = await self.memory_manager.get_competitor_profile(competitor_id)
            if profile:
                profiles.append(profile)
        
        if not profiles:
            return []
        
        # Analyze gaps
        gaps = []
        
        # Feature gaps
        all_features = set()
        for profile in profiles:
            all_features.update(profile.key_features)
        
        # Common features (offered by most competitors)
        feature_counts = {}
        for feature in all_features:
            count = sum(1 for p in profiles if feature in p.key_features)
            feature_counts[feature] = count
        
        # Rare features (potential differentiation opportunities)
        rare_features = [f for f, c in feature_counts.items() if c <= len(profiles) * 0.3]
        if rare_features:
            gaps.append(f"Underserved features: {', '.join(rare_features[:3])}")
        
        # Pricing gaps
        pricing_models = set(p.pricing_model for p in profiles if p.pricing_model)
        if len(pricing_models) <= 2:
            gaps.append("Limited pricing model diversity in market")
        
        # Market segment gaps
        segments = set(p.competitor_type.value for p in profiles)
        if CompetitorType.NICHE_PLAYER.value not in segments:
            gaps.append("Potential for niche market positioning")
        
        # Target audience gaps
        all_audiences = set()
        for profile in profiles:
            all_audiences.update(profile.target_audience)
        
        if len(all_audiences) < 5:
            gaps.append("Limited target audience segmentation - opportunity for specialized focus")
        
        logger.info(f"Identified {len(gaps)} competitive gaps")
        return gaps

    async def generate_competitive_benchmarks(self, competitor_ids: List[str]) -> Dict[str, Any]:
        """Generate competitive benchmarks."""
        logger.info(f"Generating competitive benchmarks for {len(competitor_ids)} competitors")
        
        benchmarks = {
            "feature_coverage": {},
            "pricing_analysis": {},
            "market_presence": {},
            "threat_assessment": {}
        }
        
        profiles = []
        for competitor_id in competitor_ids:
            profile = await self.memory_manager.get_competitor_profile(competitor_id)
            if profile:
                profiles.append(profile)
        
        if not profiles:
            return benchmarks
        
        # Feature coverage benchmark
        all_features = set()
        for profile in profiles:
            all_features.update(profile.key_features)
        
        for profile in profiles:
            coverage = len([f for f in all_features if f in profile.key_features]) / len(all_features) * 100
            benchmarks["feature_coverage"][profile.id] = {
                "name": profile.name,
                "coverage_percentage": coverage,
                "total_features": len(profile.key_features),
                "unique_features": len([f for f in profile.key_features if f not in all_features - set(profile.key_features)])
            }
        
        # Pricing analysis benchmark
        pricing_data = {}
        for profile in profiles:
            if profile.pricing_model:
                pricing_data[profile.id] = {
                    "name": profile.name,
                    "model": profile.pricing_model,
                    "tiers": len(profile.pricing_tiers)
                }
        
        benchmarks["pricing_analysis"] = pricing_data
        
        # Market presence benchmark
        for profile in profiles:
            benchmarks["market_presence"][profile.id] = {
                "name": profile.name,
                "type": profile.competitor_type.value,
                "threat_level": profile.threat_level.value,
                "market_share": profile.market_share
            }
        
        # Threat assessment benchmark
        threat_distribution = {}
        for profile in profiles:
            threat = profile.threat_level.value
            threat_distribution[threat] = threat_distribution.get(threat, 0) + 1
        
        benchmarks["threat_assessment"] = threat_distribution
        
        logger.info("Competitive benchmarks generated")
        return benchmarks
