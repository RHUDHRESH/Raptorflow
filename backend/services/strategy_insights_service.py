"""
Strategy Insights Service

Generates AI-powered strategic insights from campaign performance,
cohort behavior, and positioning validation. Creates feedback loops
to continuously improve strategic decisions.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json

class StrategyInsightsService:
    """Service for generating strategic insights and recommendations"""
    
    def __init__(self, supabase_client):
        self.db = supabase_client
    
    # =========================================================================
    # CAMPAIGN INSIGHTS
    # =========================================================================
    
    async def generate_campaign_insights(
        self,
        campaign_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generate insights from campaign performance
        
        Analyzes:
        - Pacing vs targets
        - Channel performance
        - Move effectiveness
        - Cohort engagement
        
        Returns:
            List of actionable insights
        """
        # Get campaign with all related data
        campaign = await self.db.table('campaigns').select(
            '*, campaign_cohorts(cohorts(*)), moves(*)'
        ).eq('id', campaign_id).single().execute()
        
        if not campaign.data:
            return []
        
        c = campaign.data
        insights = []
        
        # 1. Pacing Analysis
        pacing_insight = await self._analyze_pacing(c)
        if pacing_insight:
            insights.append(pacing_insight)
        
        # 2. Channel Performance
        channel_insights = await self._analyze_channels(c)
        insights.extend(channel_insights)
        
        # 3. Move Effectiveness
        move_insights = await self._analyze_moves(c)
        insights.extend(move_insights)
        
        # 4. Cohort Engagement
        cohort_insights = await self._analyze_cohort_engagement(c)
        insights.extend(cohort_insights)
        
        # Save insights to database
        for insight in insights:
            await self._save_insight(campaign_id, insight)
        
        return insights
    
    async def _analyze_pacing(self, campaign: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze campaign pacing vs target"""
        
        if not campaign.get('start_date') or not campaign.get('end_date'):
            return None
        
        start = datetime.fromisoformat(campaign['start_date'])
        end = datetime.fromisoformat(campaign['end_date'])
        now = datetime.utcnow()
        
        # Calculate expected progress
        total_days = (end - start).days
        elapsed_days = (now - start).days
        
        if total_days <= 0:
            return None
        
        expected_progress = elapsed_days / total_days
        
        # Calculate actual progress
        current = campaign.get('current_performance', {}).get(campaign['primary_metric'], 0)
        target = campaign.get('target_value', 0)
        
        if target <= 0:
            return None
        
        actual_progress = current / target
        
        # Determine pacing status
        if actual_progress >= expected_progress * 1.1:
            severity = 'positive'
            action = 'maintain'
            message = f"Campaign is ahead of schedule ({int(actual_progress * 100)}% vs {int(expected_progress * 100)}% expected). Maintain current strategy."
        elif actual_progress >= expected_progress * 0.9:
            severity = 'neutral'
            action = 'monitor'
            message = f"Campaign is on track ({int(actual_progress * 100)}% vs {int(expected_progress * 100)}% expected). Continue monitoring."
        elif actual_progress >= expected_progress * 0.7:
            severity = 'warning'
            action = 'adjust'
            message = f"Campaign is slightly behind ({int(actual_progress * 100)}% vs {int(expected_progress * 100)}% expected). Consider increasing intensity or budget."
        else:
            severity = 'critical'
            action = 'intervene'
            message = f"Campaign is significantly behind ({int(actual_progress * 100)}% vs {int(expected_progress * 100)}% expected). Immediate intervention needed."
        
        return {
            'type': 'pacing',
            'severity': severity,
            'action': action,
            'message': message,
            'data': {
                'expected_progress': expected_progress,
                'actual_progress': actual_progress,
                'current_value': current,
                'target_value': target
            }
        }
    
    async def _analyze_channels(self, campaign: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze channel performance"""
        
        insights = []
        channel_strategy = json.loads(campaign.get('channel_strategy', '[]'))
        
        # TODO: Get actual channel performance data
        # For now, generate placeholder insights
        
        for channel in channel_strategy:
            # Placeholder: In real implementation, compare actual vs expected performance
            insights.append({
                'type': 'channel_performance',
                'severity': 'neutral',
                'action': 'monitor',
                'message': f"{channel['channel']} performing as expected for {channel['role']} role.",
                'data': {
                    'channel': channel['channel'],
                    'role': channel['role']
                }
            })
        
        return insights
    
    async def _analyze_moves(self, campaign: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze move effectiveness"""
        
        insights = []
        moves = campaign.get('moves', [])
        
        if not moves:
            return insights
        
        # Calculate completion rate
        total_moves = len(moves)
        completed_moves = len([m for m in moves if m.get('status') == 'completed'])
        completion_rate = completed_moves / total_moves if total_moves > 0 else 0
        
        if completion_rate < 0.5:
            insights.append({
                'type': 'move_completion',
                'severity': 'warning',
                'action': 'accelerate',
                'message': f"Only {int(completion_rate * 100)}% of moves completed. Accelerate execution to stay on track.",
                'data': {
                    'total_moves': total_moves,
                    'completed_moves': completed_moves,
                    'completion_rate': completion_rate
                }
            })
        elif completion_rate >= 0.8:
            insights.append({
                'type': 'move_completion',
                'severity': 'positive',
                'action': 'maintain',
                'message': f"Strong move execution ({int(completion_rate * 100)}% completed). Keep up the momentum.",
                'data': {
                    'total_moves': total_moves,
                    'completed_moves': completed_moves,
                    'completion_rate': completion_rate
                }
            })
        
        return insights
    
    async def _analyze_cohort_engagement(self, campaign: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze cohort engagement patterns"""
        
        insights = []
        
        # TODO: Implement cohort engagement analysis
        # Would analyze:
        # - Which cohorts are responding best
        # - Journey stage progression
        # - Engagement by channel
        
        return insights
    
    # =========================================================================
    # COHORT INSIGHTS
    # =========================================================================
    
    async def generate_cohort_insights(
        self,
        cohort_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generate insights about cohort intelligence quality and gaps
        
        Analyzes:
        - Strategic attribute completeness
        - Data freshness
        - Journey distribution health
        - Engagement patterns
        
        Returns:
            List of recommendations to improve cohort intelligence
        """
        cohort = await self.db.table('cohorts').select('*').eq(
            'id', cohort_id
        ).single().execute()
        
        if not cohort.data:
            return []
        
        c = cohort.data
        insights = []
        
        # 1. Completeness Check
        completeness_insights = self._check_completeness(c)
        insights.extend(completeness_insights)
        
        # 2. Freshness Check
        freshness_insight = self._check_freshness(c)
        if freshness_insight:
            insights.append(freshness_insight)
        
        # 3. Journey Distribution Health
        journey_insight = self._check_journey_health(c)
        if journey_insight:
            insights.append(journey_insight)
        
        return insights
    
    def _check_completeness(self, cohort: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check strategic attribute completeness"""
        
        insights = []
        
        # Check buying triggers
        buying_triggers = json.loads(cohort.get('buying_triggers', '[]'))
        if len(buying_triggers) == 0:
            insights.append({
                'type': 'missing_attribute',
                'severity': 'warning',
                'action': 'add',
                'message': 'Add buying triggers to understand what drives urgency for this cohort.',
                'data': {'attribute': 'buying_triggers'}
            })
        
        # Check decision criteria
        decision_criteria = json.loads(cohort.get('decision_criteria', '[]'))
        if len(decision_criteria) == 0:
            insights.append({
                'type': 'missing_attribute',
                'severity': 'warning',
                'action': 'add',
                'message': 'Define decision criteria to know what matters most to this cohort.',
                'data': {'attribute': 'decision_criteria'}
            })
        
        # Check objection map
        objection_map = json.loads(cohort.get('objection_map', '[]'))
        if len(objection_map) < 3:
            insights.append({
                'type': 'incomplete_attribute',
                'severity': 'neutral',
                'action': 'expand',
                'message': f'Add more objections (currently {len(objection_map)}, recommend 3+) to prepare better responses.',
                'data': {'attribute': 'objection_map', 'current_count': len(objection_map)}
            })
        
        return insights
    
    def _check_freshness(self, cohort: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check data freshness"""
        
        last_validated = cohort.get('last_validated')
        if not last_validated:
            return {
                'type': 'data_freshness',
                'severity': 'warning',
                'action': 'validate',
                'message': 'This cohort has never been validated. Review and validate strategic attributes.',
                'data': {'days_since_validation': None}
            }
        
        last_validated_date = datetime.fromisoformat(last_validated)
        days_since = (datetime.utcnow() - last_validated_date).days
        
        if days_since > 90:
            return {
                'type': 'data_freshness',
                'severity': 'warning',
                'action': 'validate',
                'message': f'Cohort data is {days_since} days old. Validate and update strategic attributes.',
                'data': {'days_since_validation': days_since}
            }
        elif days_since > 60:
            return {
                'type': 'data_freshness',
                'severity': 'neutral',
                'action': 'monitor',
                'message': f'Cohort data is {days_since} days old. Consider validating soon.',
                'data': {'days_since_validation': days_since}
            }
        
        return None
    
    def _check_journey_health(self, cohort: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check journey distribution health"""
        
        journey_distribution = json.loads(cohort.get('journey_distribution', '{}'))
        
        if not journey_distribution:
            return {
                'type': 'journey_distribution',
                'severity': 'warning',
                'action': 'set',
                'message': 'Set journey distribution to understand where this cohort is in their awareness journey.',
                'data': {}
            }
        
        # Check if too many people are unaware (might need more top-of-funnel)
        unaware = journey_distribution.get('unaware', 0)
        if unaware > 0.5:
            return {
                'type': 'journey_distribution',
                'severity': 'neutral',
                'action': 'adjust',
                'message': f'{int(unaware * 100)}% are unaware. Consider awareness campaigns to move them forward.',
                'data': {'unaware_percentage': unaware}
            }
        
        # Check if too many people are most_aware (might need conversion push)
        most_aware = journey_distribution.get('most_aware', 0)
        if most_aware > 0.3:
            return {
                'type': 'journey_distribution',
                'severity': 'positive',
                'action': 'convert',
                'message': f'{int(most_aware * 100)}% are most aware. Great opportunity for conversion campaigns.',
                'data': {'most_aware_percentage': most_aware}
            }
        
        return None
    
    # =========================================================================
    # POSITIONING INSIGHTS
    # =========================================================================
    
    async def validate_positioning(
        self,
        positioning_id: str
    ) -> Dict[str, Any]:
        """
        Validate positioning effectiveness based on campaign performance
        
        Analyzes:
        - Campaign success rates using this positioning
        - Message architecture resonance
        - Proof point effectiveness
        
        Returns:
            Validation report with recommendations
        """
        # Get positioning
        positioning = await self.db.table('positioning').select(
            '*, message_architecture(*)'
        ).eq('id', positioning_id).single().execute()
        
        if not positioning.data:
            return {}
        
        # Get campaigns using this positioning
        campaigns = await self.db.table('campaigns').select('*').eq(
            'positioning_id', positioning_id
        ).execute()
        
        if not campaigns.data:
            return {
                'status': 'untested',
                'message': 'No campaigns have used this positioning yet.',
                'recommendations': ['Create a campaign to test this positioning']
            }
        
        # Calculate success metrics
        total_campaigns = len(campaigns.data)
        successful_campaigns = len([c for c in campaigns.data if c.get('health_score', 0) >= 70])
        success_rate = successful_campaigns / total_campaigns if total_campaigns > 0 else 0
        
        # Determine validation status
        if success_rate >= 0.7:
            status = 'validated'
            message = f'Strong positioning ({int(success_rate * 100)}% campaign success rate)'
            recommendations = ['Maintain current positioning', 'Consider expanding to more cohorts']
        elif success_rate >= 0.5:
            status = 'moderate'
            message = f'Moderate positioning ({int(success_rate * 100)}% campaign success rate)'
            recommendations = ['Test message architecture variations', 'Refine proof points']
        else:
            status = 'needs_work'
            message = f'Weak positioning ({int(success_rate * 100)}% campaign success rate)'
            recommendations = ['Review and revise positioning', 'Test alternative differentiators', 'Validate with target cohorts']
        
        return {
            'status': status,
            'message': message,
            'success_rate': success_rate,
            'total_campaigns': total_campaigns,
            'successful_campaigns': successful_campaigns,
            'recommendations': recommendations
        }
    
    # =========================================================================
    # INSIGHT MANAGEMENT
    # =========================================================================
    
    async def _save_insight(
        self,
        campaign_id: str,
        insight: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save insight to database"""
        
        result = await self.db.table('strategy_insights').insert({
            'campaign_id': campaign_id,
            'insight_type': insight['type'],
            'severity': insight['severity'],
            'recommended_action': insight['action'],
            'message': insight['message'],
            'data': json.dumps(insight.get('data', {})),
            'status': 'new',
            'created_at': datetime.utcnow().isoformat()
        }).execute()
        
        return result.data[0] if result.data else None
    
    async def get_insights_for_campaign(
        self,
        campaign_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all insights for a campaign"""
        
        query = self.db.table('strategy_insights').select('*').eq(
            'campaign_id', campaign_id
        ).order('created_at', desc=True)
        
        if status:
            query = query.eq('status', status)
        
        result = await query.execute()
        return result.data
    
    async def mark_insight_as_acted(
        self,
        insight_id: str
    ) -> Dict[str, Any]:
        """Mark insight as acted upon"""
        
        result = await self.db.table('strategy_insights').update({
            'status': 'acted',
            'acted_at': datetime.utcnow().isoformat()
        }).eq('id', insight_id).execute()
        
        return result.data[0] if result.data else None
    
    async def dismiss_insight(
        self,
        insight_id: str
    ) -> Dict[str, Any]:
        """Dismiss an insight"""
        
        result = await self.db.table('strategy_insights').update({
            'status': 'dismissed',
            'acted_at': datetime.utcnow().isoformat()
        }).eq('id', insight_id).execute()
        
        return result.data[0] if result.data else None
    
    # =========================================================================
    # DASHBOARD ANALYTICS
    # =========================================================================
    
    async def get_workspace_analytics(
        self,
        workspace_id: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive workspace analytics
        
        Returns:
            Dashboard-ready analytics data
        """
        # Get all campaigns
        campaigns = await self.db.table('campaigns').select('*').eq(
            'workspace_id', workspace_id
        ).execute()
        
        # Get all cohorts
        cohorts = await self.db.table('cohorts').select('*').eq(
            'workspace_id', workspace_id
        ).execute()
        
        # Get all moves
        moves = await self.db.table('moves').select('*').eq(
            'workspace_id', workspace_id
        ).execute()
        
        # Calculate metrics
        total_campaigns = len(campaigns.data) if campaigns.data else 0
        active_campaigns = len([c for c in (campaigns.data or []) if c.get('status') == 'active'])
        avg_health = sum(c.get('health_score', 0) for c in (campaigns.data or [])) / total_campaigns if total_campaigns > 0 else 0
        
        total_cohorts = len(cohorts.data) if cohorts.data else 0
        healthy_cohorts = len([c for c in (cohorts.data or []) if c.get('health_score', 0) >= 70])
        
        total_moves = len(moves.data) if moves.data else 0
        completed_moves = len([m for m in (moves.data or []) if m.get('status') == 'completed'])
        
        return {
            'campaigns': {
                'total': total_campaigns,
                'active': active_campaigns,
                'avg_health': int(avg_health),
                'at_risk': len([c for c in (campaigns.data or []) if c.get('health_score', 0) < 60])
            },
            'cohorts': {
                'total': total_cohorts,
                'healthy': healthy_cohorts,
                'needs_attention': total_cohorts - healthy_cohorts
            },
            'moves': {
                'total': total_moves,
                'completed': completed_moves,
                'completion_rate': completed_moves / total_moves if total_moves > 0 else 0
            }
        }
