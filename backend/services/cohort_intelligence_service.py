"""
Cohort Intelligence Service

Handles enhanced cohort operations including:
- Strategic attribute management
- Health score calculation
- Journey distribution tracking
- Buying trigger analysis
- Decision criteria validation
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import json

class CohortIntelligenceService:
    """Service for managing cohort strategic intelligence"""
    
    def __init__(self, supabase_client):
        self.db = supabase_client
    
    # =========================================================================
    # BUYING TRIGGERS
    # =========================================================================
    
    async def add_buying_trigger(
        self,
        cohort_id: str,
        trigger: str,
        strength: str,  # low, medium, high
        timing: Optional[str] = None,
        signal: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a buying trigger to a cohort"""
        # Get current triggers
        cohort = await self.db.table('cohorts').select('buying_triggers').eq(
            'id', cohort_id
        ).single().execute()
        
        if not cohort.data:
            return None
        
        triggers = cohort.data.get('buying_triggers', [])
        
        # Add new trigger
        triggers.append({
            'trigger': trigger,
            'strength': strength,
            'timing': timing,
            'signal': signal
        })
        
        # Update cohort
        result = await self.db.table('cohorts').update({
            'buying_triggers': json.dumps(triggers)
        }).eq('id', cohort_id).execute()
        
        return result.data[0] if result.data else None
    
    async def update_buying_triggers(
        self,
        cohort_id: str,
        triggers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update all buying triggers for a cohort"""
        result = await self.db.table('cohorts').update({
            'buying_triggers': json.dumps(triggers)
        }).eq('id', cohort_id).execute()
        
        return result.data[0] if result.data else None
    
    # =========================================================================
    # DECISION CRITERIA
    # =========================================================================
    
    def validate_decision_criteria(self, criteria: List[Dict[str, Any]]) -> bool:
        """Validate that decision criteria weights sum to 1.0"""
        if not criteria:
            return True
        
        total_weight = sum(c.get('weight', 0) for c in criteria)
        return abs(total_weight - 1.0) < 0.01
    
    async def update_decision_criteria(
        self,
        cohort_id: str,
        criteria: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update decision criteria for a cohort
        
        Validates that weights sum to 1.0
        """
        if not self.validate_decision_criteria(criteria):
            raise ValueError("Decision criteria weights must sum to 1.0")
        
        result = await self.db.table('cohorts').update({
            'decision_criteria': json.dumps(criteria)
        }).eq('id', cohort_id).execute()
        
        return result.data[0] if result.data else None
    
    # =========================================================================
    # OBJECTION MAP
    # =========================================================================
    
    async def add_objection(
        self,
        cohort_id: str,
        objection: str,
        frequency: str,  # rare, occasional, common, very_common
        stage: Optional[str] = None,
        response: Optional[str] = None,
        linked_asset_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add an objection to the cohort's objection map"""
        # Get current objections
        cohort = await self.db.table('cohorts').select('objection_map').eq(
            'id', cohort_id
        ).single().execute()
        
        if not cohort.data:
            return None
        
        objections = cohort.data.get('objection_map', [])
        
        # Add new objection
        objections.append({
            'objection': objection,
            'frequency': frequency,
            'stage': stage,
            'response': response,
            'linked_asset_ids': linked_asset_ids or []
        })
        
        # Update cohort
        result = await self.db.table('cohorts').update({
            'objection_map': json.dumps(objections)
        }).eq('id', cohort_id).execute()
        
        return result.data[0] if result.data else None
    
    async def update_objection_map(
        self,
        cohort_id: str,
        objections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update all objections for a cohort"""
        result = await self.db.table('cohorts').update({
            'objection_map': json.dumps(objections)
        }).eq('id', cohort_id).execute()
        
        return result.data[0] if result.data else None
    
    # =========================================================================
    # ATTENTION WINDOWS
    # =========================================================================
    
    async def update_attention_windows(
        self,
        cohort_id: str,
        windows: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update attention windows for a cohort
        
        Format:
        {
            "linkedin": {
                "best_times": ["Tue 9am", "Wed 2pm"],
                "receptivity": "high",
                "preferred_formats": ["Carousel", "Video"]
            }
        }
        """
        result = await self.db.table('cohorts').update({
            'attention_windows': json.dumps(windows)
        }).eq('id', cohort_id).execute()
        
        return result.data[0] if result.data else None
    
    # =========================================================================
    # JOURNEY DISTRIBUTION
    # =========================================================================
    
    def validate_journey_distribution(self, distribution: Dict[str, float]) -> bool:
        """Validate that journey distribution percentages sum to 1.0"""
        total = sum(distribution.values())
        return abs(total - 1.0) < 0.01
    
    async def update_journey_distribution(
        self,
        cohort_id: str,
        distribution: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Update journey distribution for a cohort
        
        Validates that percentages sum to 1.0
        
        Format:
        {
            "unaware": 0.2,
            "problem_aware": 0.3,
            "solution_aware": 0.25,
            "product_aware": 0.15,
            "most_aware": 0.1
        }
        """
        if not self.validate_journey_distribution(distribution):
            raise ValueError("Journey distribution percentages must sum to 1.0")
        
        result = await self.db.table('cohorts').update({
            'journey_distribution': json.dumps(distribution)
        }).eq('id', cohort_id).execute()
        
        return result.data[0] if result.data else None
    
    # =========================================================================
    # COMPETITIVE FRAME
    # =========================================================================
    
    async def update_competitive_frame(
        self,
        cohort_id: str,
        competitive_frame: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update competitive frame for a cohort
        
        Format:
        {
            "direct_competitors": ["HubSpot", "Marketo"],
            "category_alternatives": ["Hiring agency", "Building in-house"],
            "switching_triggers": ["Price increase", "Feature gap"]
        }
        """
        result = await self.db.table('cohorts').update({
            'competitive_frame': json.dumps(competitive_frame)
        }).eq('id', cohort_id).execute()
        
        return result.data[0] if result.data else None
    
    # =========================================================================
    # DECISION MAKING UNIT
    # =========================================================================
    
    async def update_decision_making_unit(
        self,
        cohort_id: str,
        dmu: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update decision making unit for a cohort
        
        Format:
        {
            "roles": ["CTO", "CMO", "VP Marketing"],
            "influencers": ["Marketing Director", "Sales Ops"],
            "decision_maker": "CTO",
            "approval_chain": ["CMO → CTO → CFO"]
        }
        """
        result = await self.db.table('cohorts').update({
            'decision_making_unit': json.dumps(dmu)
        }).eq('id', cohort_id).execute()
        
        return result.data[0] if result.data else None
    
    # =========================================================================
    # HEALTH SCORE
    # =========================================================================
    
    async def calculate_health_score(self, cohort_id: str) -> int:
        """
        Calculate cohort health score (0-100)
        
        Factors:
        - Strategic attributes completeness (40%)
        - Journey distribution health (20%)
        - Recent engagement (20%)
        - Data freshness (20%)
        
        Returns:
            Health score 0-100
        """
        cohort = await self.db.table('cohorts').select('*').eq(
            'id', cohort_id
        ).single().execute()
        
        if not cohort.data:
            return 0
        
        c = cohort.data
        score = 0
        
        # 1. Strategic attributes completeness (40 points)
        attributes_score = 0
        if c.get('buying_triggers') and len(json.loads(c['buying_triggers'])) > 0:
            attributes_score += 8
        if c.get('decision_criteria') and len(json.loads(c['decision_criteria'])) > 0:
            attributes_score += 8
        if c.get('objection_map') and len(json.loads(c['objection_map'])) > 0:
            attributes_score += 8
        if c.get('attention_windows') and len(json.loads(c['attention_windows'])) > 0:
            attributes_score += 8
        if c.get('competitive_frame'):
            attributes_score += 8
        
        score += attributes_score
        
        # 2. Journey distribution health (20 points)
        if c.get('journey_distribution'):
            dist = json.loads(c['journey_distribution'])
            # Healthy distribution has most people in middle stages
            if dist.get('solution_aware', 0) > 0.2 or dist.get('product_aware', 0) > 0.15:
                score += 20
            elif dist.get('problem_aware', 0) > 0.2:
                score += 15
            else:
                score += 10
        
        # 3. Recent engagement (20 points)
        # TODO: Implement engagement tracking
        score += 15  # Default moderate score
        
        # 4. Data freshness (20 points)
        if c.get('last_validated'):
            last_validated = datetime.fromisoformat(c['last_validated'])
            days_since = (datetime.utcnow() - last_validated).days
            
            if days_since <= 30:
                score += 20
            elif days_since <= 60:
                score += 15
            elif days_since <= 90:
                score += 10
            else:
                score += 5
        else:
            score += 5  # Never validated
        
        # Update cohort with new health score
        await self.db.table('cohorts').update({
            'health_score': score
        }).eq('id', cohort_id).execute()
        
        return score
    
    async def validate_cohort(self, cohort_id: str) -> Dict[str, Any]:
        """Mark cohort as validated and update health score"""
        health_score = await self.calculate_health_score(cohort_id)
        
        result = await self.db.table('cohorts').update({
            'last_validated': datetime.utcnow().isoformat(),
            'health_score': health_score
        }).eq('id', cohort_id).execute()
        
        return result.data[0] if result.data else None
    
    # =========================================================================
    # ANALYTICS
    # =========================================================================
    
    async def get_cohort_summary(self, cohort_id: str) -> Dict[str, Any]:
        """Get comprehensive cohort summary with all strategic attributes"""
        cohort = await self.db.table('cohorts').select('*').eq(
            'id', cohort_id
        ).single().execute()
        
        if not cohort.data:
            return {}
        
        c = cohort.data
        
        # Parse JSONB fields
        summary = {
            **c,
            'buying_triggers': json.loads(c.get('buying_triggers', '[]')),
            'decision_criteria': json.loads(c.get('decision_criteria', '[]')),
            'objection_map': json.loads(c.get('objection_map', '[]')),
            'attention_windows': json.loads(c.get('attention_windows', '{}')),
            'journey_distribution': json.loads(c.get('journey_distribution', '{}')),
            'competitive_frame': json.loads(c.get('competitive_frame', '{}')),
            'decision_making_unit': json.loads(c.get('decision_making_unit', '{}'))
        }
        
        # Calculate health score if not present
        if not summary.get('health_score'):
            summary['health_score'] = await self.calculate_health_score(cohort_id)
        
        return summary
    
    async def get_journey_summary(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get journey distribution summary for all cohorts in workspace"""
        # Use the helper view
        result = await self.db.table('cohort_journey_summary').select('*').eq(
            'workspace_id', workspace_id
        ).execute()
        
        return result.data
