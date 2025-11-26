"""
Creative Brief Service

Auto-generates creative briefs from Moves with full strategic context:
- Positioning and message architecture
- Cohort intelligence (psychographics, objections, decision criteria)
- Single-minded proposition
- Tone and manner
- Mandatories and no-gos
"""

from typing import Dict, Optional, Any, List
from datetime import datetime
import json

class CreativeBriefService:
    """Service for generating creative briefs from strategic context"""
    
    def __init__(self, supabase_client):
        self.db = supabase_client
    
    async def generate_brief_from_move(
        self,
        move_id: str
    ) -> Dict[str, Any]:
        """
        Generate a complete creative brief from a Move
        
        Pulls in:
        - Move details (objective, channels, journey stages)
        - Campaign context
        - Positioning and message architecture
        - Cohort intelligence
        
        Returns:
            Complete creative brief ready for asset creation
        """
        # Get move with campaign
        move = await self.db.table('moves').select(
            '*, campaigns(*)'
        ).eq('id', move_id).single().execute()
        
        if not move.data:
            return None
        
        m = move.data
        campaign = m.get('campaigns')
        
        # Get positioning and message architecture
        if campaign:
            positioning = await self.db.table('positioning').select(
                '*, message_architecture(*)'
            ).eq('id', campaign['positioning_id']).single().execute()
        else:
            # Fallback to active positioning
            positioning = await self.db.table('positioning').select(
                '*, message_architecture(*)'
            ).eq('workspace_id', m['workspace_id']).eq(
                'is_active', True
            ).single().execute()
        
        # Get cohort intelligence
        cohort = await self.db.table('cohorts').select('*').eq(
            'id', m['cohort_id']
        ).single().execute()
        
        # Build the brief
        brief = await self._build_brief(m, campaign, positioning.data if positioning.data else None, cohort.data if cohort.data else None)
        
        return brief
    
    async def _build_brief(
        self,
        move: Dict[str, Any],
        campaign: Optional[Dict[str, Any]],
        positioning: Optional[Dict[str, Any]],
        cohort: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build the creative brief structure"""
        
        # Extract message variant (which proof point to emphasize)
        message_variant = json.loads(move.get('message_variant', '{}'))
        
        # Get message architecture
        msg_arch = positioning.get('message_architecture', {}) if positioning else {}
        proof_points = json.loads(msg_arch.get('proof_points', '[]')) if msg_arch else []
        
        # Parse cohort intelligence
        cohort_data = {}
        if cohort:
            cohort_data = {
                'name': cohort.get('name'),
                'description': cohort.get('description'),
                'psychographics': json.loads(cohort.get('psychographics', '{}')),
                'buying_triggers': json.loads(cohort.get('buying_triggers', '[]')),
                'decision_criteria': json.loads(cohort.get('decision_criteria', '[]')),
                'objection_map': json.loads(cohort.get('objection_map', '[]')),
                'attention_windows': json.loads(cohort.get('attention_windows', '{}')),
            }
        
        # Determine single-minded proposition
        smp = self._generate_single_minded_proposition(
            move, campaign, positioning, message_variant, proof_points
        )
        
        # Determine key message
        key_message = self._generate_key_message(
            move, positioning, message_variant, proof_points
        )
        
        # Determine tone and manner
        tone = self._determine_tone(move, cohort_data)
        
        # Generate mandatories
        mandatories = self._generate_mandatories(move, campaign, positioning)
        
        # Generate no-gos
        no_gos = self._generate_no_gos(cohort_data)
        
        # Success definition
        success = self._define_success(move, campaign)
        
        # Asset requirements
        asset_requirements = json.loads(move.get('asset_requirements', '{}'))
        
        brief = {
            'move_id': move['id'],
            'campaign_id': campaign['id'] if campaign else None,
            'cohort_id': move['cohort_id'],
            
            # Core Brief
            'single_minded_proposition': smp,
            'key_message': key_message,
            'tone_and_manner': tone,
            
            # Strategic Context
            'positioning_context': {
                'category_frame': positioning.get('category_frame') if positioning else None,
                'differentiator': positioning.get('differentiator') if positioning else None,
                'reason_to_believe': positioning.get('reason_to_believe') if positioning else None,
            } if positioning else {},
            
            # Target Audience Context
            'target_cohort_context': cohort_data,
            
            # Journey Context
            'journey_context': {
                'from_stage': move.get('journey_stage_from'),
                'to_stage': move.get('journey_stage_to'),
                'objective': 'Move them from {} to {}'.format(
                    move.get('journey_stage_from', 'current stage'),
                    move.get('journey_stage_to', 'next stage')
                )
            },
            
            # Campaign Context
            'campaign_context': {
                'name': campaign.get('name') if campaign else None,
                'objective': campaign.get('objective') if campaign else None,
                'primary_metric': campaign.get('primary_metric') if campaign else None,
            } if campaign else {},
            
            # Asset Requirements
            'asset_requirements': asset_requirements,
            'channels': move.get('channels', []),
            'intensity': move.get('intensity', 'standard'),
            
            # Guidelines
            'mandatories': mandatories,
            'no_gos': no_gos,
            
            # Success
            'success_definition': success,
            
            # Metadata
            'generated_at': datetime.utcnow().isoformat(),
        }
        
        return brief
    
    def _generate_single_minded_proposition(
        self,
        move: Dict[str, Any],
        campaign: Optional[Dict[str, Any]],
        positioning: Optional[Dict[str, Any]],
        message_variant: Dict[str, Any],
        proof_points: List[Dict[str, Any]]
    ) -> str:
        """Generate the ONE thing this asset must communicate"""
        
        # If message variant specifies a proof point, use that
        if message_variant.get('proof_point_id'):
            proof_point = next(
                (pp for pp in proof_points if pp.get('id') == message_variant['proof_point_id']),
                None
            )
            if proof_point:
                return proof_point.get('claim', '')
        
        # Otherwise, use journey stage transition
        from_stage = move.get('journey_stage_from', '')
        to_stage = move.get('journey_stage_to', '')
        
        if from_stage == 'unaware' and to_stage == 'problem_aware':
            return "You have a problem that needs solving"
        elif from_stage == 'problem_aware' and to_stage == 'solution_aware':
            return "There are solutions available for your problem"
        elif from_stage == 'solution_aware' and to_stage == 'product_aware':
            return "Our solution is the best fit for you"
        elif from_stage == 'product_aware' and to_stage == 'most_aware':
            return "Now is the time to act"
        else:
            # Fallback to positioning differentiator
            if positioning:
                return positioning.get('differentiator', 'Our unique value proposition')
            return "Our unique value proposition"
    
    def _generate_key_message(
        self,
        move: Dict[str, Any],
        positioning: Optional[Dict[str, Any]],
        message_variant: Dict[str, Any],
        proof_points: List[Dict[str, Any]]
    ) -> str:
        """Generate the key message for this asset"""
        
        # Start with proof point if specified
        if message_variant.get('proof_point_id'):
            proof_point = next(
                (pp for pp in proof_points if pp.get('id') == message_variant['proof_point_id']),
                None
            )
            if proof_point:
                evidence = proof_point.get('evidence', [])
                if evidence:
                    return f"{proof_point['claim']}. {evidence[0]}"
                return proof_point.get('claim', '')
        
        # Fallback to positioning
        if positioning:
            category = positioning.get('category_frame', '')
            diff = positioning.get('differentiator', '')
            return f"{category} {diff}"
        
        return "Communicate our unique value"
    
    def _determine_tone(
        self,
        move: Dict[str, Any],
        cohort_data: Dict[str, Any]
    ) -> str:
        """Determine appropriate tone and manner"""
        
        intensity = move.get('intensity', 'standard')
        journey_to = move.get('journey_stage_to', '')
        
        # Base tone on intensity and journey stage
        if intensity == 'aggressive' or journey_to == 'most_aware':
            return "Urgent, direct, action-oriented. Create FOMO and urgency."
        elif intensity == 'light' or journey_to == 'problem_aware':
            return "Educational, helpful, empathetic. Build awareness gently."
        else:
            return "Professional, confident, authoritative. Establish credibility."
    
    def _generate_mandatories(
        self,
        move: Dict[str, Any],
        campaign: Optional[Dict[str, Any]],
        positioning: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate list of mandatory elements"""
        
        mandatories = [
            "Brand logo",
            "Clear call-to-action",
        ]
        
        # Add positioning elements
        if positioning:
            if positioning.get('tagline'):
                mandatories.append(f"Tagline: '{positioning['tagline']}'")
        
        # Add campaign-specific mandatories
        if campaign:
            if campaign.get('primary_metric'):
                mandatories.append(f"Drive {campaign['primary_metric']}")
        
        # Add journey-specific mandatories
        to_stage = move.get('journey_stage_to')
        if to_stage == 'most_aware':
            mandatories.append("Strong CTA (demo, trial, purchase)")
        elif to_stage == 'product_aware':
            mandatories.append("Product features and benefits")
        elif to_stage == 'solution_aware':
            mandatories.append("Problem-solution connection")
        
        return mandatories
    
    def _generate_no_gos(
        self,
        cohort_data: Dict[str, Any]
    ) -> List[str]:
        """Generate list of things to avoid"""
        
        no_gos = []
        
        # Add objections to avoid triggering
        objections = cohort_data.get('objection_map', [])
        for obj in objections[:3]:  # Top 3 objections
            no_gos.append(f"Avoid triggering: '{obj.get('objection')}'")
        
        # Add decision criteria to avoid violating
        criteria = cohort_data.get('decision_criteria', [])
        deal_breakers = [c for c in criteria if c.get('deal_breaker')]
        for db in deal_breakers:
            no_gos.append(f"Must address: {db.get('criterion')}")
        
        if not no_gos:
            no_gos = [
                "Generic stock photos",
                "Jargon without explanation",
                "Overpromising without proof"
            ]
        
        return no_gos
    
    def _define_success(
        self,
        move: Dict[str, Any],
        campaign: Optional[Dict[str, Any]]
    ) -> str:
        """Define how we know this asset worked"""
        
        to_stage = move.get('journey_stage_to', '')
        
        if to_stage == 'most_aware':
            return "Drives conversions (demo requests, trial signups, purchases)"
        elif to_stage == 'product_aware':
            return "Increases product page visits and feature engagement"
        elif to_stage == 'solution_aware':
            return "Generates content engagement and email signups"
        elif to_stage == 'problem_aware':
            return "Increases awareness and social shares"
        else:
            if campaign:
                return f"Contributes to campaign goal: {campaign.get('primary_metric')}"
            return "Moves audience to next journey stage"
    
    # =========================================================================
    # BRIEF MANAGEMENT
    # =========================================================================
    
    async def save_brief(
        self,
        brief: Dict[str, Any],
        workspace_id: str
    ) -> Dict[str, Any]:
        """Save a generated brief for future reference"""
        
        # Store in a briefs table (would need to create this)
        # For now, just return the brief
        return {
            **brief,
            'id': f"brief-{brief['move_id']}",
            'workspace_id': workspace_id,
            'saved_at': datetime.utcnow().isoformat()
        }
    
    async def get_briefs_for_campaign(
        self,
        campaign_id: str
    ) -> List[Dict[str, Any]]:
        """Get all briefs for a campaign"""
        
        # Get all moves for campaign
        moves = await self.db.table('moves').select('*').eq(
            'campaign_id', campaign_id
        ).execute()
        
        # Generate brief for each move
        briefs = []
        for move in moves.data:
            brief = await self.generate_brief_from_move(move['id'])
            if brief:
                briefs.append(brief)
        
        return briefs
    
    async def export_brief_as_markdown(
        self,
        brief: Dict[str, Any]
    ) -> str:
        """Export brief as Markdown for sharing"""
        
        md = f"""# Creative Brief

## Single-Minded Proposition
{brief['single_minded_proposition']}

## Key Message
{brief['key_message']}

## Target Audience
**Cohort:** {brief['target_cohort_context'].get('name', 'N/A')}
**Description:** {brief['target_cohort_context'].get('description', 'N/A')}

### Decision Criteria
"""
        
        for criterion in brief['target_cohort_context'].get('decision_criteria', []):
            md += f"- {criterion.get('criterion')} ({int(criterion.get('weight', 0) * 100)}%)\n"
        
        md += f"""
### Objections to Address
"""
        
        for objection in brief['target_cohort_context'].get('objection_map', [])[:3]:
            md += f"- \"{objection.get('objection')}\" → {objection.get('response', 'N/A')}\n"
        
        md += f"""
## Journey Context
**From:** {brief['journey_context']['from_stage']}  
**To:** {brief['journey_context']['to_stage']}  
**Objective:** {brief['journey_context']['objective']}

## Tone and Manner
{brief['tone_and_manner']}

## Mandatories
"""
        
        for mandatory in brief['mandatories']:
            md += f"- {mandatory}\n"
        
        md += f"""
## No-Gos
"""
        
        for no_go in brief['no_gos']:
            md += f"- {no_go}\n"
        
        md += f"""
## Success Definition
{brief['success_definition']}

## Asset Requirements
**Channels:** {', '.join(brief.get('channels', []))}  
**Intensity:** {brief.get('intensity', 'standard')}

---

*Generated: {brief['generated_at']}*
"""
        
        return md
