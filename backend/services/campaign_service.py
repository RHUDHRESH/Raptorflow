"""
Campaign Service

Handles all campaign-related operations including:
- Creating and managing campaigns
- Campaign health score calculation
- Move recommendation engine
- Channel strategy optimization
- Pacing analysis and alerts
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json

class CampaignService:
    """Service for managing strategic campaigns"""
    
    def __init__(self, supabase_client):
        self.db = supabase_client
    
    async def create_campaign(
        self,
        workspace_id: str,
        positioning_id: str,
        name: str,
        description: str,
        objective: str,  # awareness, consideration, conversion, retention, advocacy
        objective_statement: str,
        primary_metric: str,
        target_value: float,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        budget_total: Optional[float] = None,
        channel_strategy: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new campaign
        
        Args:
            workspace_id: Workspace ID
            positioning_id: Linked positioning ID
            name: Campaign name
            description: Campaign description
            objective: Campaign objective (awareness/consideration/conversion/retention/advocacy)
            objective_statement: Natural language objective
            primary_metric: Main metric to track
            target_value: Target number for primary metric
            start_date: Campaign start date
            end_date: Campaign end date
            budget_total: Total budget
            channel_strategy: Array of {channel, role, budget_percentage, frequency}
            
        Returns:
            Created campaign record
        """
        result = await self.db.table('campaigns').insert({
            'workspace_id': workspace_id,
            'positioning_id': positioning_id,
            'name': name,
            'description': description,
            'objective': objective,
            'objective_statement': objective_statement,
            'primary_metric': primary_metric,
            'target_value': target_value,
            'start_date': start_date,
            'end_date': end_date,
            'budget_total': budget_total,
            'budget_currency': 'USD',
            'channel_strategy': json.dumps(channel_strategy or []),
            'status': 'draft',
            'health_score': None,
            'current_performance': json.dumps({})
        }).execute()
        
        return result.data[0] if result.data else None
    
    async def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign by ID"""
        result = await self.db.table('campaigns').select('*').eq(
            'id', campaign_id
        ).single().execute()
        
        if result.data:
            # Parse JSONB fields
            result.data['channel_strategy'] = json.loads(result.data['channel_strategy'])
            result.data['current_performance'] = json.loads(result.data['current_performance'])
        
        return result.data if result.data else None
    
    async def list_campaigns(
        self,
        workspace_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List campaigns for a workspace"""
        query = self.db.table('campaigns').select('*').eq('workspace_id', workspace_id)
        
        if status:
            query = query.eq('status', status)
        
        result = await query.order('created_at', desc=True).execute()
        
        # Parse JSONB fields
        for campaign in result.data:
            campaign['channel_strategy'] = json.loads(campaign['channel_strategy'])
            campaign['current_performance'] = json.loads(campaign['current_performance'])
        
        return result.data
    
    async def update_campaign(
        self,
        campaign_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a campaign"""
        # Convert JSONB fields if present
        if 'channel_strategy' in updates:
            updates['channel_strategy'] = json.dumps(updates['channel_strategy'])
        if 'current_performance' in updates:
            updates['current_performance'] = json.dumps(updates['current_performance'])
        
        result = await self.db.table('campaigns').update(updates).eq(
            'id', campaign_id
        ).execute()
        
        return result.data[0] if result.data else None
    
    async def launch_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Launch a campaign (set status to active)"""
        return await self.update_campaign(campaign_id, {
            'status': 'active',
            'launched_at': datetime.utcnow().isoformat()
        })
    
    async def pause_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Pause a campaign"""
        return await self.update_campaign(campaign_id, {'status': 'paused'})
    
    async def complete_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Mark campaign as completed"""
        return await self.update_campaign(campaign_id, {
            'status': 'completed',
            'completed_at': datetime.utcnow().isoformat()
        })
    
    # =========================================================================
    # COHORT TARGETING
    # =========================================================================
    
    async def add_cohort_to_campaign(
        self,
        campaign_id: str,
        cohort_id: str,
        priority: str = 'secondary',  # primary or secondary
        journey_stage_current: Optional[str] = None,
        journey_stage_target: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a cohort to a campaign"""
        # If setting as primary, demote existing primary
        if priority == 'primary':
            await self.db.table('campaign_cohorts').update({
                'priority': 'secondary'
            }).eq('campaign_id', campaign_id).eq('priority', 'primary').execute()
        
        result = await self.db.table('campaign_cohorts').insert({
            'campaign_id': campaign_id,
            'cohort_id': cohort_id,
            'priority': priority,
            'journey_stage_current': journey_stage_current,
            'journey_stage_target': journey_stage_target
        }).execute()
        
        return result.data[0] if result.data else None
    
    async def remove_cohort_from_campaign(
        self,
        campaign_id: str,
        cohort_id: str
    ) -> bool:
        """Remove a cohort from a campaign"""
        await self.db.table('campaign_cohorts').delete().eq(
            'campaign_id', campaign_id
        ).eq('cohort_id', cohort_id).execute()
        
        return True
    
    async def get_campaign_cohorts(
        self,
        campaign_id: str
    ) -> List[Dict[str, Any]]:
        """Get all cohorts for a campaign"""
        result = await self.db.table('campaign_cohorts').select(
            '*, cohorts(*)'
        ).eq('campaign_id', campaign_id).execute()
        
        return result.data
    
    # =========================================================================
    # HEALTH SCORE CALCULATION
    # =========================================================================
    
    async def calculate_health_score(self, campaign_id: str) -> int:
        """
        Calculate campaign health score (0-100)
        
        Factors:
        - Pacing vs target (40%)
        - Budget utilization (20%)
        - Move completion rate (20%)
        - Engagement metrics (20%)
        
        Returns:
            Health score 0-100
        """
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            return 0
        
        score = 0
        
        # 1. Pacing vs target (40 points)
        if campaign['target_value'] and campaign['current_performance']:
            current = campaign['current_performance'].get(campaign['primary_metric'], 0)
            target = campaign['target_value']
            
            # Calculate expected progress based on time
            if campaign['start_date'] and campaign['end_date']:
                start = datetime.fromisoformat(campaign['start_date'])
                end = datetime.fromisoformat(campaign['end_date'])
                now = datetime.utcnow()
                
                total_days = (end - start).days
                elapsed_days = (now - start).days
                
                if total_days > 0:
                    expected_progress = elapsed_days / total_days
                    actual_progress = current / target if target > 0 else 0
                    
                    # Score based on how close actual is to expected
                    pacing_ratio = actual_progress / expected_progress if expected_progress > 0 else 0
                    
                    if pacing_ratio >= 1.0:
                        score += 40  # Ahead of schedule
                    elif pacing_ratio >= 0.9:
                        score += 35  # On track
                    elif pacing_ratio >= 0.7:
                        score += 25  # Slightly behind
                    elif pacing_ratio >= 0.5:
                        score += 15  # Behind
                    else:
                        score += 5   # Significantly behind
        
        # 2. Budget utilization (20 points)
        # TODO: Implement budget tracking
        score += 15  # Default moderate score
        
        # 3. Move completion rate (20 points)
        # Get moves for this campaign
        moves_result = await self.db.table('moves').select('*').eq(
            'campaign_id', campaign_id
        ).execute()
        
        if moves_result.data:
            total_moves = len(moves_result.data)
            completed_moves = len([m for m in moves_result.data if m.get('status') == 'completed'])
            
            completion_rate = completed_moves / total_moves if total_moves > 0 else 0
            score += int(completion_rate * 20)
        else:
            score += 10  # No moves yet, moderate score
        
        # 4. Engagement metrics (20 points)
        # TODO: Implement engagement tracking
        score += 15  # Default moderate score
        
        # Update campaign with new health score
        await self.update_campaign(campaign_id, {'health_score': score})
        
        return score
    
    # =========================================================================
    # MOVE RECOMMENDATIONS
    # =========================================================================
    
    async def generate_move_recommendations(
        self,
        campaign_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generate AI-powered move recommendations for a campaign
        
        Returns:
            List of recommended moves with:
            - name
            - description
            - journey_from
            - journey_to
            - duration (days)
            - channels
            - proof_point
        """
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            return []
        
        # Get campaign cohorts
        cohorts = await self.get_campaign_cohorts(campaign_id)
        primary_cohort = next((c for c in cohorts if c['priority'] == 'primary'), None)
        
        # Get positioning and message architecture
        positioning = await self.db.table('positioning').select('*').eq(
            'id', campaign['positioning_id']
        ).single().execute()
        
        msg_arch = await self.db.table('message_architecture').select('*').eq(
            'positioning_id', campaign['positioning_id']
        ).single().execute()
        
        # Generate recommendations based on objective
        recommendations = []
        
        if campaign['objective'] == 'awareness':
            recommendations.append({
                'name': 'Authority Establishment Sprint',
                'description': 'Build credibility with thought leadership content',
                'journey_from': 'unaware',
                'journey_to': 'problem_aware',
                'duration': 14,
                'channels': [cs['channel'] for cs in campaign['channel_strategy'] if cs.get('role') == 'reach'],
                'proof_point': msg_arch.data['proof_points'][0]['claim'] if msg_arch.data else None,
                'intensity': 'standard'
            })
        
        if campaign['objective'] in ['consideration', 'conversion']:
            recommendations.append({
                'name': 'Proof Delivery Campaign',
                'description': 'Show evidence with case studies and testimonials',
                'journey_from': 'problem_aware',
                'journey_to': 'solution_aware',
                'duration': 14,
                'channels': [cs['channel'] for cs in campaign['channel_strategy'] if cs.get('role') == 'engage'],
                'proof_point': msg_arch.data['proof_points'][1]['claim'] if msg_arch.data and len(msg_arch.data['proof_points']) > 1 else None,
                'intensity': 'standard'
            })
            
            recommendations.append({
                'name': 'Objection Handling Sequence',
                'description': 'Address common concerns proactively',
                'journey_from': 'solution_aware',
                'journey_to': 'product_aware',
                'duration': 7,
                'channels': [cs['channel'] for cs in campaign['channel_strategy'] if cs.get('role') in ['engage', 'convert']],
                'proof_point': msg_arch.data['proof_points'][2]['claim'] if msg_arch.data and len(msg_arch.data['proof_points']) > 2 else None,
                'intensity': 'aggressive'
            })
        
        if campaign['objective'] == 'conversion':
            recommendations.append({
                'name': 'Conversion Sprint',
                'description': 'Push for action with urgency and clear CTAs',
                'journey_from': 'product_aware',
                'journey_to': 'most_aware',
                'duration': 7,
                'channels': [cs['channel'] for cs in campaign['channel_strategy'] if cs.get('role') == 'convert'],
                'proof_point': 'Clear value + risk reversal',
                'intensity': 'aggressive'
            })
        
        if campaign['objective'] == 'retention':
            recommendations.append({
                'name': 'Value Reinforcement Loop',
                'description': 'Remind them why they chose you',
                'journey_from': 'most_aware',
                'journey_to': 'most_aware',
                'duration': 28,
                'channels': [cs['channel'] for cs in campaign['channel_strategy'] if cs.get('role') == 'retain'],
                'proof_point': 'Success stories and new features',
                'intensity': 'light'
            })
        
        if campaign['objective'] == 'advocacy':
            recommendations.append({
                'name': 'Advocacy Activation',
                'description': 'Turn customers into promoters',
                'journey_from': 'most_aware',
                'journey_to': 'most_aware',
                'duration': 21,
                'channels': [cs['channel'] for cs in campaign['channel_strategy']],
                'proof_point': 'Community and recognition',
                'intensity': 'standard'
            })
        
        return recommendations
    
    # =========================================================================
    # ANALYTICS
    # =========================================================================
    
    async def get_campaign_summary(self, campaign_id: str) -> Dict[str, Any]:
        """Get comprehensive campaign summary"""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            return {}
        
        # Get cohorts
        cohorts = await self.get_campaign_cohorts(campaign_id)
        
        # Get moves
        moves = await self.db.table('moves').select('*').eq(
            'campaign_id', campaign_id
        ).execute()
        
        # Calculate health score
        health_score = await self.calculate_health_score(campaign_id)
        
        # Determine health status
        if campaign['end_date'] and datetime.fromisoformat(campaign['end_date']) < datetime.utcnow():
            health_status = 'completed'
        elif campaign['start_date'] and datetime.fromisoformat(campaign['start_date']) > datetime.utcnow():
            health_status = 'upcoming'
        elif health_score >= 80:
            health_status = 'healthy'
        elif health_score >= 60:
            health_status = 'on_track'
        elif health_score >= 40:
            health_status = 'at_risk'
        else:
            health_status = 'critical'
        
        return {
            **campaign,
            'total_cohorts': len(cohorts),
            'total_moves': len(moves.data) if moves.data else 0,
            'health_score': health_score,
            'health_status': health_status
        }
