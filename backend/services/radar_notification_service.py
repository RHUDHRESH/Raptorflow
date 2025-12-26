"""
Radar Notification Service - Alerts and notifications for important signals
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from models.radar_models import (
    Signal,
    SignalCategory,
    SignalStrength,
    SignalFreshness,
)

logger = logging.getLogger("raptorflow.radar_notifications")


class RadarNotificationService:
    """
    Service for managing Radar notifications and alerts.
    Handles signal prioritization, notification rules, and delivery.
    """

    def __init__(self):
        # Notification rules and thresholds
        self.notification_rules = {
            "high_strength_signals": {
                "enabled": True,
                "threshold": 1,  # Notify on any high strength signal
                "categories": ["offer", "hook", "trend"],
            },
            "competitor_activity_spikes": {
                "enabled": True,
                "threshold": 5,  # 5+ signals from same competitor in 24h
                "window_hours": 24,
            },
            "trend_signals": {
                "enabled": True,
                "threshold": 3,  # 3+ trend signals in 24h
                "window_hours": 24,
            },
            "pricing_changes": {
                "enabled": True,
                "threshold": 1,  # Any pricing signal
                "strength_filter": ["high", "medium"],
            },
        }

    async def process_signal_notifications(
        self, 
        signals: List[Signal], 
        tenant_preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Process signals and generate notifications."""
        notifications = []
        
        # Apply tenant preferences
        rules = self._apply_tenant_preferences(tenant_preferences)
        
        # High strength signal notifications
        high_strength_notifications = await self._check_high_strength_signals(signals, rules)
        notifications.extend(high_strength_notifications)
        
        # Competitor activity spike notifications
        spike_notifications = await self._check_competitor_spikes(signals, rules)
        notifications.extend(spike_notifications)
        
        # Trend signal notifications
        trend_notifications = await self._check_trend_signals(signals, rules)
        notifications.extend(trend_notifications)
        
        # Pricing change notifications
        pricing_notifications = await self._check_pricing_changes(signals, rules)
        notifications.extend(pricing_notifications)
        
        # Remove duplicates and prioritize
        unique_notifications = self._deduplicate_notifications(notifications)
        prioritized_notifications = self._prioritize_notifications(unique_notifications)
        
        return prioritized_notifications[:10]  # Return top 10 notifications

    async def _check_high_strength_signals(
        self, 
        signals: List[Signal], 
        rules: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for high strength signals."""
        notifications = []
        
        rule = rules.get("high_strength_signals", {})
        if not rule.get("enabled", False):
            return notifications
        
        threshold = rule.get("threshold", 1)
        allowed_categories = rule.get("categories", [])
        
        high_strength_signals = [
            s for s in signals 
            if s.strength == SignalStrength.HIGH 
            and (not allowed_categories or s.category.value in allowed_categories)
        ]
        
        if len(high_strength_signals) >= threshold:
            for signal in high_strength_signals:
                notification = {
                    "type": "high_strength_signal",
                    "priority": "high",
                    "title": f"High Strength {signal.category.value.title()} Signal",
                    "message": signal.content[:100] + "...",
                    "signal_id": signal.id,
                    "category": signal.category.value,
                    "strength": signal.strength.value,
                    "source": signal.source_competitor or "Unknown",
                    "created_at": signal.created_at.isoformat(),
                    "action_suggestion": signal.action_suggestion,
                }
                notifications.append(notification)
        
        return notifications

    async def _check_competitor_spikes(
        self, 
        signals: List[Signal], 
        rules: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for competitor activity spikes."""
        notifications = []
        
        rule = rules.get("competitor_activity_spikes", {})
        if not rule.get("enabled", False):
            return notifications
        
        threshold = rule.get("threshold", 5)
        window_hours = rule.get("window_hours", 24)
        
        # Group signals by competitor
        by_competitor = {}
        for signal in signals:
            competitor = signal.source_competitor or "Unknown"
            if competitor not in by_competitor:
                by_competitor[competitor] = []
            by_competitor[competitor].append(signal)
        
        # Check for activity spikes
        for competitor, competitor_signals in by_competitor.items():
            # Filter signals within time window
            cutoff_time = datetime.utcnow() - timedelta(hours=window_hours)
            recent_signals = [
                s for s in competitor_signals 
                if s.created_at >= cutoff_time
            ]
            
            if len(recent_signals) >= threshold:
                notification = {
                    "type": "competitor_activity_spike",
                    "priority": "medium",
                    "title": f"Activity Spike: {competitor}",
                    "message": f"{len(recent_signals)} signals detected in {window_hours}h",
                    "competitor": competitor,
                    "signal_count": len(recent_signals),
                    "window_hours": window_hours,
                    "signal_ids": [s.id for s in recent_signals],
                    "created_at": datetime.utcnow().isoformat(),
                }
                notifications.append(notification)
        
        return notifications

    async def _check_trend_signals(
        self, 
        signals: List[Signal], 
        rules: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for trend signals."""
        notifications = []
        
        rule = rules.get("trend_signals", {})
        if not rule.get("enabled", False):
            return notifications
        
        threshold = rule.get("threshold", 3)
        window_hours = rule.get("window_hours", 24)
        
        # Filter trend signals within time window
        cutoff_time = datetime.utcnow() - timedelta(hours=window_hours)
        recent_trend_signals = [
            s for s in signals 
            if s.category == SignalCategory.TREND 
            and s.created_at >= cutoff_time
        ]
        
        if len(recent_trend_signals) >= threshold:
            notification = {
                "type": "trend_signals",
                "priority": "medium",
                "title": "Market Trend Activity",
                "message": f"{len(recent_trend_signals)} trend signals detected",
                "signal_count": len(recent_trend_signals),
                "window_hours": window_hours,
                "signal_ids": [s.id for s in recent_trend_signals],
                "created_at": datetime.utcnow().isoformat(),
            }
            notifications.append(notification)
        
        return notifications

    async def _check_pricing_changes(
        self, 
        signals: List[Signal], 
        rules: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for pricing changes."""
        notifications = []
        
        rule = rules.get("pricing_changes", {})
        if not rule.get("enabled", False):
            return notifications
        
        threshold = rule.get("threshold", 1)
        strength_filter = rule.get("strength_filter", ["high", "medium"])
        
        # Filter pricing signals
        pricing_signals = [
            s for s in signals 
            if s.category == SignalCategory.OFFER
            and s.strength.value in strength_filter
        ]
        
        if len(pricing_signals) >= threshold:
            for signal in pricing_signals:
                notification = {
                    "type": "pricing_change",
                    "priority": "high",
                    "title": "Pricing Change Detected",
                    "message": signal.content[:100] + "...",
                    "signal_id": signal.id,
                    "competitor": signal.source_competitor or "Unknown",
                    "strength": signal.strength.value,
                    "created_at": signal.created_at.isoformat(),
                    "action_suggestion": signal.action_suggestion,
                }
                notifications.append(notification)
        
        return notifications

    def _apply_tenant_preferences(
        self, 
        tenant_preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply tenant-specific preferences to notification rules."""
        if not tenant_preferences:
            return self.notification_rules
        
        # Deep copy rules
        customized_rules = {}
        for rule_name, rule_config in self.notification_rules.items():
            customized_rules[rule_name] = rule_config.copy()
        
        # Apply tenant preferences
        for rule_name, preference in tenant_preferences.items():
            if rule_name in customized_rules:
                customized_rules[rule_name].update(preference)
        
        return customized_rules

    def _deduplicate_notifications(self, notifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate notifications."""
        seen = set()
        unique_notifications = []
        
        for notification in notifications:
            # Create unique key based on type and relevant fields
            if notification["type"] == "high_strength_signal":
                key = f"{notification['type']}_{notification['signal_id']}"
            elif notification["type"] == "competitor_activity_spike":
                key = f"{notification['type']}_{notification['competitor']}"
            elif notification["type"] == "trend_signals":
                key = f"{notification['type']}_{notification['signal_count']}"
            elif notification["type"] == "pricing_change":
                key = f"{notification['type']}_{notification['signal_id']}"
            else:
                key = f"{notification['type']}_{notification['title']}"
            
            if key not in seen:
                seen.add(key)
                unique_notifications.append(notification)
        
        return unique_notifications

    def _prioritize_notifications(self, notifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize notifications by importance."""
        priority_order = {"high": 1, "medium": 2, "low": 3}
        
        # Sort by priority, then by creation time (newest first)
        prioritized = sorted(
            notifications,
            key=lambda x: (priority_order.get(x["priority"], 3), x["created_at"]),
            reverse=True
        )
        
        return prioritized

    async def create_daily_digest(
        self, 
        signals: List[Signal], 
        tenant_id: str
    ) -> Dict[str, Any]:
        """Create daily digest of important signals."""
        # Get signals from last 24 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        daily_signals = [s for s in signals if s.created_at >= cutoff_time]
        
        if not daily_signals:
            return {
                "type": "daily_digest",
                "title": "Daily Radar Digest",
                "message": "No significant signals detected in the last 24 hours.",
                "signal_count": 0,
                "created_at": datetime.utcnow().isoformat(),
            }
        
        # Categorize signals
        by_category = {}
        by_strength = {"high": 0, "medium": 0, "low": 0}
        
        for signal in daily_signals:
            category = signal.category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(signal)
            by_strength[signal.strength.value] += 1
        
        # Create digest
        digest = {
            "type": "daily_digest",
            "title": "Daily Radar Digest",
            "message": f"{len(daily_signals)} signals detected in the last 24 hours",
            "signal_count": len(daily_signals),
            "by_category": {cat: len(signals) for cat, signals in by_category.items()},
            "by_strength": by_strength,
            "top_signals": [
                {
                    "id": s.id,
                    "category": s.category.value,
                    "content": s.content[:50] + "...",
                    "strength": s.strength.value,
                    "source": s.source_competitor or "Unknown",
                }
                for s in sorted(daily_signals, key=lambda x: self._strength_to_numeric(x.strength), reverse=True)[:5]
            ],
            "created_at": datetime.utcnow().isoformat(),
        }
        
        return digest

    def _strength_to_numeric(self, strength: SignalStrength) -> float:
        """Convert strength to numeric value."""
        mapping = {
            SignalStrength.LOW: 0.3,
            SignalStrength.MEDIUM: 0.6,
            SignalStrength.HIGH: 0.9,
        }
        return mapping.get(strength, 0.5)
