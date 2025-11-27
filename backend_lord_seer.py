# backend/agents/council_of_lords/seer.py
# RaptorFlow Codex - Seer Lord Agent
# Phase 2A Week 6 - Trend Prediction & Market Intelligence

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from abc import ABC
import uuid

from agents.base_agent import BaseAgent, AgentRole, AgentStatus, Capability, CapabilityHandler

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA STRUCTURES
# ============================================================================

class ForecastType(Enum):
    """Forecast types"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    POLYNOMIAL = "polynomial"
    SEASONAL = "seasonal"
    CYCLICAL = "cyclical"


class TrendDirection(Enum):
    """Trend direction indicators"""
    STRONGLY_UP = "strongly_up"
    UP = "up"
    STABLE = "stable"
    DOWN = "down"
    STRONGLY_DOWN = "strongly_down"


class ConfidenceLevel(Enum):
    """Confidence levels for predictions"""
    VERY_HIGH = "very_high"  # 80-100%
    HIGH = "high"  # 60-80%
    MEDIUM = "medium"  # 40-60%
    LOW = "low"  # 20-40%
    VERY_LOW = "very_low"  # 0-20%


class IntelligenceType(Enum):
    """Types of market intelligence"""
    COMPETITIVE = "competitive"
    MARKET_TREND = "market_trend"
    CUSTOMER_BEHAVIOR = "customer_behavior"
    TECHNOLOGY = "technology"
    REGULATORY = "regulatory"
    ECONOMIC = "economic"


class TrendPrediction:
    """Trend prediction result"""

    def __init__(
        self,
        prediction_id: str,
        metric_name: str,
        current_value: float,
        forecast_type: str,
        trend_direction: str,
        confidence: float,
        forecast_period_days: int,
        predicted_values: List[float],
        forecast_type_enum: ForecastType,
    ):
        self.prediction_id = prediction_id
        self.metric_name = metric_name
        self.current_value = current_value
        self.forecast_type = forecast_type
        self.trend_direction = trend_direction
        self.confidence = min(100, max(0, confidence))
        self.forecast_period_days = forecast_period_days
        self.predicted_values = predicted_values
        self.forecast_type_enum = forecast_type_enum
        self.created_at = datetime.utcnow()
        self.analysis_notes = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "prediction_id": self.prediction_id,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "forecast_type": self.forecast_type,
            "trend_direction": self.trend_direction,
            "confidence": self.confidence,
            "forecast_period_days": self.forecast_period_days,
            "predicted_values": self.predicted_values,
            "created_at": self.created_at.isoformat(),
            "analysis_notes": self.analysis_notes,
        }


class MarketIntelligence:
    """Market intelligence report"""

    def __init__(
        self,
        intelligence_id: str,
        intelligence_type: str,
        title: str,
        summary: str,
        source: str,
        impact_score: float,
        relevance_score: float,
        key_insights: List[str],
        action_items: List[str],
    ):
        self.intelligence_id = intelligence_id
        self.intelligence_type = intelligence_type
        self.title = title
        self.summary = summary
        self.source = source
        self.impact_score = min(100, max(0, impact_score))
        self.relevance_score = min(100, max(0, relevance_score))
        self.key_insights = key_insights
        self.action_items = action_items
        self.created_at = datetime.utcnow()
        self.threat_level = "low"  # low, medium, high, critical

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "intelligence_id": self.intelligence_id,
            "intelligence_type": self.intelligence_type,
            "title": self.title,
            "summary": self.summary,
            "source": self.source,
            "impact_score": self.impact_score,
            "relevance_score": self.relevance_score,
            "key_insights": self.key_insights,
            "action_items": self.action_items,
            "threat_level": self.threat_level,
            "created_at": self.created_at.isoformat(),
        }


class PerformanceAnalysis:
    """Performance analysis report"""

    def __init__(
        self,
        analysis_id: str,
        scope: str,  # campaign, guild, organization
        scope_id: str,
        metrics: Dict[str, float],
        performance_score: float,
        trend_analysis: Dict[str, str],
        strengths: List[str],
        weaknesses: List[str],
        recommendations: List[str],
    ):
        self.analysis_id = analysis_id
        self.scope = scope
        self.scope_id = scope_id
        self.metrics = metrics
        self.performance_score = min(100, max(0, performance_score))
        self.trend_analysis = trend_analysis
        self.strengths = strengths
        self.weaknesses = weaknesses
        self.recommendations = recommendations
        self.created_at = datetime.utcnow()
        self.comparison_data = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "analysis_id": self.analysis_id,
            "scope": self.scope,
            "scope_id": self.scope_id,
            "metrics": self.metrics,
            "performance_score": self.performance_score,
            "trend_analysis": self.trend_analysis,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat(),
        }


class StrategicRecommendation:
    """Strategic recommendation based on analysis"""

    def __init__(
        self,
        recommendation_id: str,
        title: str,
        description: str,
        priority: str,  # critical, high, normal, low
        expected_impact: float,
        implementation_effort: float,
        success_probability: float,
        supporting_insights: List[str],
        required_resources: Dict[str, Any],
    ):
        self.recommendation_id = recommendation_id
        self.title = title
        self.description = description
        self.priority = priority
        self.expected_impact = min(100, max(0, expected_impact))
        self.implementation_effort = min(100, max(0, implementation_effort))
        self.success_probability = min(100, max(0, success_probability))
        self.supporting_insights = supporting_insights
        self.required_resources = required_resources
        self.created_at = datetime.utcnow()
        self.status = "proposed"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "recommendation_id": self.recommendation_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "expected_impact": self.expected_impact,
            "implementation_effort": self.implementation_effort,
            "success_probability": self.success_probability,
            "supporting_insights": self.supporting_insights,
            "required_resources": self.required_resources,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class ForecastReport:
    """Comprehensive forecast report"""

    def __init__(
        self,
        report_id: str,
        title: str,
        forecast_period_days: int,
        trend_predictions: List[TrendPrediction],
        intelligence_summaries: List[MarketIntelligence],
        key_insights: List[str],
        risk_factors: List[str],
        opportunities: List[str],
        overall_confidence: float,
    ):
        self.report_id = report_id
        self.title = title
        self.forecast_period_days = forecast_period_days
        self.trend_predictions = trend_predictions
        self.intelligence_summaries = intelligence_summaries
        self.key_insights = key_insights
        self.risk_factors = risk_factors
        self.opportunities = opportunities
        self.overall_confidence = min(100, max(0, overall_confidence))
        self.created_at = datetime.utcnow()
        self.report_status = "ready"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "report_id": self.report_id,
            "title": self.title,
            "forecast_period_days": self.forecast_period_days,
            "trend_predictions": [p.to_dict() for p in self.trend_predictions],
            "intelligence_summaries": [i.to_dict() for i in self.intelligence_summaries],
            "key_insights": self.key_insights,
            "risk_factors": self.risk_factors,
            "opportunities": self.opportunities,
            "overall_confidence": self.overall_confidence,
            "report_status": self.report_status,
            "created_at": self.created_at.isoformat(),
        }


# ============================================================================
# SEER LORD AGENT
# ============================================================================


class SeerLord(BaseAgent):
    """
    Seer Lord - Manages trend prediction, market intelligence, and forecasting.
    Provides strategic insights based on data analysis and pattern recognition.
    """

    def __init__(self):
        super().__init__()
        self.name = "Seer Lord"
        self.role = AgentRole.seer
        self.status = AgentStatus.idle

        # Register capabilities
        self.capabilities = [
            Capability(name="predict_trend", handler=self._predict_trend),
            Capability(name="gather_intelligence", handler=self._gather_intelligence),
            Capability(name="analyze_performance", handler=self._analyze_performance),
            Capability(name="generate_recommendation", handler=self._generate_recommendation),
            Capability(name="get_forecast_report", handler=self._get_forecast_report),
        ]

        # State storage
        self.trend_predictions: Dict[str, TrendPrediction] = {}
        self.market_intelligence: Dict[str, MarketIntelligence] = {}
        self.performance_analyses: Dict[str, PerformanceAnalysis] = {}
        self.strategic_recommendations: Dict[str, StrategicRecommendation] = {}
        self.forecast_reports: Dict[str, ForecastReport] = {}

        # Performance metrics
        self.total_predictions_made = 0
        self.total_intelligence_gathered = 0
        self.total_recommendations_generated = 0
        self.average_prediction_confidence = 0.0
        self.prediction_accuracy_rate = 0.0

    async def execute(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Seer capability"""
        logger.info(f"🔮 Seer Lord executing: {task}")

        try:
            self.status = AgentStatus.active

            # Route to capability handler
            for capability in self.capabilities:
                if capability.name == task:
                    result = await capability.handler(**parameters)
                    self.status = AgentStatus.idle
                    return result

            raise ValueError(f"Unknown task: {task}")

        except Exception as e:
            logger.error(f"❌ Seer execution error: {e}")
            self.status = AgentStatus.error
            return {"success": False, "error": str(e)}

    async def _predict_trend(self, **kwargs) -> Dict[str, Any]:
        """Predict market or metric trends"""
        metric_name = kwargs.get("metric_name", "unknown")
        historical_values = kwargs.get("historical_values", [])
        forecast_period_days = kwargs.get("forecast_period_days", 30)
        forecast_type = kwargs.get("forecast_type", "linear")

        prediction_id = f"pred_{uuid.uuid4().hex[:8]}"

        try:
            # Calculate current value
            current_value = historical_values[-1] if historical_values else 0.0

            # Determine trend direction
            if len(historical_values) >= 2:
                recent_avg = sum(historical_values[-5:]) / min(5, len(historical_values))
                older_avg = sum(historical_values[: min(5, len(historical_values))]) / min(5, len(historical_values))
                change_percent = ((recent_avg - older_avg) / older_avg * 100) if older_avg != 0 else 0
            else:
                change_percent = 0

            # Determine trend direction enum
            if change_percent > 10:
                trend_direction = TrendDirection.STRONGLY_UP.value
            elif change_percent > 2:
                trend_direction = TrendDirection.UP.value
            elif change_percent < -10:
                trend_direction = TrendDirection.STRONGLY_DOWN.value
            elif change_percent < -2:
                trend_direction = TrendDirection.DOWN.value
            else:
                trend_direction = TrendDirection.STABLE.value

            # Generate predicted values based on forecast type
            predicted_values = self._generate_forecast(
                historical_values, forecast_period_days, ForecastType(forecast_type)
            )

            # Calculate confidence based on data consistency
            confidence = self._calculate_confidence(historical_values) * 100

            # Create prediction object
            prediction = TrendPrediction(
                prediction_id=prediction_id,
                metric_name=metric_name,
                current_value=current_value,
                forecast_type=forecast_type,
                trend_direction=trend_direction,
                confidence=confidence,
                forecast_period_days=forecast_period_days,
                predicted_values=predicted_values,
                forecast_type_enum=ForecastType(forecast_type),
            )

            self.trend_predictions[prediction_id] = prediction
            self.total_predictions_made += 1
            self.average_prediction_confidence = (
                (self.average_prediction_confidence * (self.total_predictions_made - 1) + confidence)
                / self.total_predictions_made
            )

            logger.info(f"✅ Trend predicted: {metric_name} ({prediction_id})")

            return {
                "success": True,
                "prediction_id": prediction_id,
                "metric_name": metric_name,
                "current_value": current_value,
                "trend_direction": trend_direction,
                "confidence": confidence,
                "predicted_values": predicted_values,
                "forecast_type": forecast_type,
            }

        except Exception as e:
            logger.error(f"Trend prediction error: {e}")
            raise

    async def _gather_intelligence(self, **kwargs) -> Dict[str, Any]:
        """Gather market intelligence"""
        intelligence_type = kwargs.get("intelligence_type", "market_trend")
        title = kwargs.get("title", "Market Intelligence")
        summary = kwargs.get("summary", "")
        source = kwargs.get("source", "internal_analysis")
        key_insights = kwargs.get("key_insights", [])

        intelligence_id = f"intel_{uuid.uuid4().hex[:8]}"

        try:
            # Calculate impact and relevance scores
            impact_score = 50 + (len(key_insights) * 5)  # Base 50 + insight bonus
            relevance_score = 60 + (len(key_insights) * 3)

            # Generate action items
            action_items = [f"Action: {insight[:30]}..." for insight in key_insights[:3]]

            # Create intelligence object
            intelligence = MarketIntelligence(
                intelligence_id=intelligence_id,
                intelligence_type=intelligence_type,
                title=title,
                summary=summary,
                source=source,
                impact_score=impact_score,
                relevance_score=relevance_score,
                key_insights=key_insights,
                action_items=action_items,
            )

            # Determine threat level
            if impact_score > 80:
                intelligence.threat_level = "critical"
            elif impact_score > 60:
                intelligence.threat_level = "high"
            elif impact_score > 40:
                intelligence.threat_level = "medium"
            else:
                intelligence.threat_level = "low"

            self.market_intelligence[intelligence_id] = intelligence
            self.total_intelligence_gathered += 1

            logger.info(f"✅ Intelligence gathered: {title} ({intelligence_id})")

            return {
                "success": True,
                "intelligence_id": intelligence_id,
                "intelligence_type": intelligence_type,
                "title": title,
                "impact_score": impact_score,
                "relevance_score": relevance_score,
                "threat_level": intelligence.threat_level,
                "key_insights": key_insights,
                "action_items": action_items,
            }

        except Exception as e:
            logger.error(f"Intelligence gathering error: {e}")
            raise

    async def _analyze_performance(self, **kwargs) -> Dict[str, Any]:
        """Analyze performance metrics"""
        scope = kwargs.get("scope", "campaign")  # campaign, guild, organization
        scope_id = kwargs.get("scope_id", "")
        metrics = kwargs.get("metrics", {})

        analysis_id = f"perf_{uuid.uuid4().hex[:8]}"

        try:
            # Calculate performance score
            metric_values = list(metrics.values()) if isinstance(metrics, dict) else []
            performance_score = sum(metric_values) / len(metric_values) if metric_values else 50

            # Analyze trends
            trend_analysis = {}
            for metric_name, value in metrics.items():
                if value > 75:
                    trend_analysis[metric_name] = "strong"
                elif value > 50:
                    trend_analysis[metric_name] = "normal"
                else:
                    trend_analysis[metric_name] = "weak"

            # Identify strengths and weaknesses
            strengths = [m for m, t in trend_analysis.items() if t == "strong"]
            weaknesses = [m for m, t in trend_analysis.items() if t == "weak"]

            # Generate recommendations
            recommendations = []
            if weaknesses:
                recommendations.append(f"Improve weak metrics: {', '.join(weaknesses[:2])}")
            if performance_score < 60:
                recommendations.append("Comprehensive performance review needed")
            recommendations.append(f"Maintain strong performance in: {', '.join(strengths[:2])}")

            # Create analysis object
            analysis = PerformanceAnalysis(
                analysis_id=analysis_id,
                scope=scope,
                scope_id=scope_id,
                metrics=metrics,
                performance_score=performance_score,
                trend_analysis=trend_analysis,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations,
            )

            self.performance_analyses[analysis_id] = analysis

            logger.info(f"✅ Performance analyzed: {scope}/{scope_id} ({analysis_id})")

            return {
                "success": True,
                "analysis_id": analysis_id,
                "scope": scope,
                "scope_id": scope_id,
                "performance_score": performance_score,
                "trend_analysis": trend_analysis,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "recommendations": recommendations,
            }

        except Exception as e:
            logger.error(f"Performance analysis error: {e}")
            raise

    async def _generate_recommendation(self, **kwargs) -> Dict[str, Any]:
        """Generate strategic recommendation"""
        title = kwargs.get("title", "Strategic Recommendation")
        description = kwargs.get("description", "")
        priority = kwargs.get("priority", "normal")
        supporting_insights = kwargs.get("supporting_insights", [])
        required_resources = kwargs.get("required_resources", {})

        recommendation_id = f"rec_{uuid.uuid4().hex[:8]}"

        try:
            # Calculate expected impact and success probability
            expected_impact = 50 + (len(supporting_insights) * 5)
            success_probability = 60 + (len(supporting_insights) * 2)
            implementation_effort = 50 + len(required_resources) * 10

            # Create recommendation object
            recommendation = StrategicRecommendation(
                recommendation_id=recommendation_id,
                title=title,
                description=description,
                priority=priority,
                expected_impact=expected_impact,
                implementation_effort=implementation_effort,
                success_probability=success_probability,
                supporting_insights=supporting_insights,
                required_resources=required_resources,
            )

            self.strategic_recommendations[recommendation_id] = recommendation
            self.total_recommendations_generated += 1

            logger.info(f"✅ Recommendation generated: {title} ({recommendation_id})")

            return {
                "success": True,
                "recommendation_id": recommendation_id,
                "title": title,
                "priority": priority,
                "expected_impact": expected_impact,
                "implementation_effort": implementation_effort,
                "success_probability": success_probability,
                "supporting_insights": supporting_insights,
            }

        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            raise

    async def _get_forecast_report(self, **kwargs) -> Dict[str, Any]:
        """Generate comprehensive forecast report"""
        title = kwargs.get("title", "Market Forecast Report")
        forecast_period_days = kwargs.get("forecast_period_days", 30)
        include_predictions = kwargs.get("include_predictions", True)
        include_intelligence = kwargs.get("include_intelligence", True)

        report_id = f"report_{uuid.uuid4().hex[:8]}"

        try:
            # Collect recent predictions
            trend_predictions = list(self.trend_predictions.values())[-5:] if include_predictions else []

            # Collect recent intelligence
            intelligence_summaries = list(self.market_intelligence.values())[-5:] if include_intelligence else []

            # Generate key insights
            key_insights = []
            if trend_predictions:
                strong_trends = [p.metric_name for p in trend_predictions if p.confidence > 75]
                key_insights.append(f"Strong trends detected in: {', '.join(strong_trends[:2])}")

            if intelligence_summaries:
                threats = [i.title for i in intelligence_summaries if i.threat_level == "critical"]
                if threats:
                    key_insights.append(f"Critical issues identified: {', '.join(threats[:2])}")

            # Identify risks and opportunities
            risk_factors = [
                f"Risk: Data volatility in recent forecasts",
                f"Risk: Market uncertainty within {forecast_period_days} days",
            ]
            opportunities = [
                f"Opportunity: Strong growth indicators detected",
                f"Opportunity: Untapped market segments emerging",
            ]

            # Calculate overall confidence
            confidence_scores = [p.confidence for p in trend_predictions] if trend_predictions else []
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 50

            # Create report
            report = ForecastReport(
                report_id=report_id,
                title=title,
                forecast_period_days=forecast_period_days,
                trend_predictions=trend_predictions,
                intelligence_summaries=intelligence_summaries,
                key_insights=key_insights,
                risk_factors=risk_factors,
                opportunities=opportunities,
                overall_confidence=overall_confidence,
            )

            self.forecast_reports[report_id] = report

            logger.info(f"✅ Forecast report generated: {title} ({report_id})")

            return {
                "success": True,
                "report_id": report_id,
                "title": title,
                "forecast_period_days": forecast_period_days,
                "overall_confidence": overall_confidence,
                "predictions_count": len(trend_predictions),
                "intelligence_count": len(intelligence_summaries),
                "key_insights": key_insights,
                "risk_factors": risk_factors,
                "opportunities": opportunities,
            }

        except Exception as e:
            logger.error(f"Forecast report generation error: {e}")
            raise

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _generate_forecast(
        self, historical_values: List[float], periods: int, forecast_type: ForecastType
    ) -> List[float]:
        """Generate forecast values based on type"""
        if not historical_values:
            return [50.0] * periods

        last_value = historical_values[-1]
        predicted = []

        if forecast_type == ForecastType.LINEAR:
            # Linear extrapolation
            if len(historical_values) >= 2:
                slope = (historical_values[-1] - historical_values[-2]) / (len(historical_values) - 1)
                for i in range(periods):
                    predicted.append(last_value + slope * (i + 1))
            else:
                predicted = [last_value] * periods

        elif forecast_type == ForecastType.EXPONENTIAL:
            # Exponential growth
            growth_rate = 1.02
            for i in range(periods):
                predicted.append(last_value * (growth_rate ** (i + 1)))

        elif forecast_type == ForecastType.SEASONAL:
            # Seasonal pattern
            if len(historical_values) >= 7:
                seasonal_avg = sum(historical_values[-7:]) / 7
                for i in range(periods):
                    seasonal_factor = 1 + 0.1 * ((i % 7) - 3.5) / 3.5
                    predicted.append(seasonal_avg * seasonal_factor)
            else:
                predicted = [last_value] * periods

        else:  # Default to polynomial or stable
            predicted = [last_value * (1.0 + 0.01 * (i % 10)) for i in range(periods)]

        return predicted

    def _calculate_confidence(self, historical_values: List[float]) -> float:
        """Calculate prediction confidence based on data"""
        if len(historical_values) < 2:
            return 0.3

        # Calculate coefficient of variation
        mean = sum(historical_values) / len(historical_values)
        variance = sum((x - mean) ** 2 for x in historical_values) / len(historical_values)
        std_dev = variance ** 0.5

        # Inverse relationship: lower variation = higher confidence
        cv = (std_dev / mean) if mean != 0 else 0
        confidence = max(0.3, min(0.95, 1.0 - cv))

        # Bonus for more data points
        if len(historical_values) >= 10:
            confidence = min(0.95, confidence + 0.1)
        elif len(historical_values) >= 5:
            confidence = min(0.95, confidence + 0.05)

        return confidence

    async def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trend predictions"""
        predictions = list(self.trend_predictions.values())[-limit:]
        return [p.to_dict() for p in predictions]

    async def get_recent_intelligence(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent market intelligence"""
        intelligence = list(self.market_intelligence.values())[-limit:]
        return [i.to_dict() for i in intelligence]

    async def get_recent_recommendations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent recommendations"""
        recommendations = list(self.strategic_recommendations.values())[-limit:]
        return [r.to_dict() for r in recommendations]

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get Seer performance summary"""
        return {
            "predictions_made": self.total_predictions_made,
            "intelligence_gathered": self.total_intelligence_gathered,
            "recommendations_generated": self.total_recommendations_generated,
            "average_confidence": self.average_prediction_confidence,
            "accuracy_rate": self.prediction_accuracy_rate,
            "forecast_reports_generated": len(self.forecast_reports),
            "status": self.status.value,
        }
