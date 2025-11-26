"""
Positioning Service

Handles all positioning-related operations including:
- Creating and managing positioning statements
- Message architecture management
- Proof point validation
- AI-powered positioning suggestions
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import json

class PositioningService:
    """Service for managing strategic positioning statements"""
    
    def __init__(self, supabase_client):
        self.db = supabase_client
    
    async def create_positioning(
        self,
        workspace_id: str,
        name: str,
        for_cohort_id: Optional[str],
        who_statement: str,
        category_frame: str,
        differentiator: str,
        reason_to_believe: str,
        competitive_alternative: str,
        is_active: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new positioning statement
        
        Args:
            workspace_id: Workspace ID
            name: Positioning name
            for_cohort_id: Target cohort ID (optional)
            who_statement: Problem/need statement
            category_frame: Category definition
            differentiator: Key difference
            reason_to_believe: Proof/evidence
            competitive_alternative: What they'd do without you
            is_active: Set as active positioning
            
        Returns:
            Created positioning record
        """
        # If setting as active, deactivate others first
        if is_active:
            await self.db.table('positioning').update({
                'is_active': False
            }).eq('workspace_id', workspace_id).eq('is_active', True).execute()
        
        # Create positioning
        result = await self.db.table('positioning').insert({
            'workspace_id': workspace_id,
            'name': name,
            'for_cohort_id': for_cohort_id,
            'who_statement': who_statement,
            'category_frame': category_frame,
            'differentiator': differentiator,
            'reason_to_believe': reason_to_believe,
            'competitive_alternative': competitive_alternative,
            'is_active': is_active,
            'is_validated': False
        }).execute()
        
        return result.data[0] if result.data else None
    
    async def get_active_positioning(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get the active positioning for a workspace"""
        result = await self.db.table('positioning').select('*').eq(
            'workspace_id', workspace_id
        ).eq('is_active', True).single().execute()
        
        return result.data if result.data else None
    
    async def update_positioning(
        self,
        positioning_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a positioning statement"""
        result = await self.db.table('positioning').update(updates).eq(
            'id', positioning_id
        ).execute()
        
        return result.data[0] if result.data else None
    
    async def validate_positioning(
        self,
        positioning_id: str,
        market_evidence: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate positioning with market evidence
        
        Args:
            positioning_id: Positioning ID
            market_evidence: Optional market validation data
            
        Returns:
            Updated positioning with validation status
        """
        updates = {'is_validated': True}
        
        if market_evidence:
            # Store evidence in metadata or separate table
            pass
        
        return await self.update_positioning(positioning_id, updates)
    
    async def generate_positioning_variants(
        self,
        positioning_id: str,
        num_variants: int = 3
    ) -> List[Dict[str, str]]:
        """
        Generate alternative positioning variants using AI
        
        Args:
            positioning_id: Base positioning ID
            num_variants: Number of variants to generate
            
        Returns:
            List of positioning variants
        """
        # Get base positioning
        positioning = await self.db.table('positioning').select('*').eq(
            'id', positioning_id
        ).single().execute()
        
        if not positioning.data:
            return []
        
        base = positioning.data
        
        # TODO: Implement AI generation
        # For now, return template variants
        variants = []
        for i in range(num_variants):
            variants.append({
                'who_statement': base['who_statement'],
                'category_frame': f"Variant {i+1}: {base['category_frame']}",
                'differentiator': base['differentiator'],
                'reason_to_believe': base['reason_to_believe']
            })
        
        return variants
    
    # =========================================================================
    # MESSAGE ARCHITECTURE
    # =========================================================================
    
    async def create_message_architecture(
        self,
        positioning_id: str,
        primary_claim: str,
        proof_points: List[Dict[str, Any]],
        tagline: Optional[str] = None,
        elevator_pitch: Optional[str] = None,
        long_form_narrative: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create message architecture for a positioning
        
        Args:
            positioning_id: Positioning ID
            primary_claim: The ONE thing you want them to believe
            proof_points: Array of {claim, evidence[], for_journey_stages[]}
            tagline: 5-7 word memorable tagline
            elevator_pitch: 30-second pitch version
            long_form_narrative: Full story version
            
        Returns:
            Created message architecture record
        """
        result = await self.db.table('message_architecture').insert({
            'positioning_id': positioning_id,
            'primary_claim': primary_claim,
            'proof_points': json.dumps(proof_points),
            'tagline': tagline,
            'elevator_pitch': elevator_pitch,
            'long_form_narrative': long_form_narrative
        }).execute()
        
        return result.data[0] if result.data else None
    
    async def get_message_architecture(
        self,
        positioning_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get message architecture for a positioning"""
        result = await self.db.table('message_architecture').select('*').eq(
            'positioning_id', positioning_id
        ).single().execute()
        
        if result.data:
            # Parse JSONB fields
            result.data['proof_points'] = json.loads(result.data['proof_points'])
        
        return result.data if result.data else None
    
    async def update_message_architecture(
        self,
        message_arch_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update message architecture"""
        # Convert proof_points to JSON if present
        if 'proof_points' in updates:
            updates['proof_points'] = json.dumps(updates['proof_points'])
        
        result = await self.db.table('message_architecture').update(updates).eq(
            'id', message_arch_id
        ).execute()
        
        return result.data[0] if result.data else None
    
    async def add_proof_point(
        self,
        message_arch_id: str,
        claim: str,
        evidence: List[str],
        for_journey_stages: List[str]
    ) -> Dict[str, Any]:
        """Add a proof point to message architecture"""
        # Get current message architecture
        msg_arch = await self.db.table('message_architecture').select('*').eq(
            'id', message_arch_id
        ).single().execute()
        
        if not msg_arch.data:
            return None
        
        # Parse existing proof points
        proof_points = json.loads(msg_arch.data['proof_points'])
        
        # Add new proof point
        proof_points.append({
            'claim': claim,
            'evidence': evidence,
            'for_journey_stages': for_journey_stages
        })
        
        # Update
        return await self.update_message_architecture(message_arch_id, {
            'proof_points': proof_points
        })
    
    async def generate_tagline(
        self,
        positioning_id: str,
        num_options: int = 5
    ) -> List[str]:
        """
        Generate tagline options using AI
        
        Args:
            positioning_id: Positioning ID
            num_options: Number of tagline options to generate
            
        Returns:
            List of tagline options
        """
        # Get positioning
        positioning = await self.db.table('positioning').select('*').eq(
            'id', positioning_id
        ).single().execute()
        
        if not positioning.data:
            return []
        
        # TODO: Implement AI generation
        # For now, return template taglines
        taglines = [
            "Strategy that ships",
            "Marketing warfare, simplified",
            "From chaos to campaigns",
            "Ship campaigns 3x faster",
            "Strategic marketing, executed"
        ]
        
        return taglines[:num_options]
    
    async def generate_elevator_pitch(
        self,
        positioning_id: str
    ) -> str:
        """Generate elevator pitch from positioning"""
        # Get positioning and message architecture
        positioning = await self.db.table('positioning').select('*').eq(
            'id', positioning_id
        ).single().execute()
        
        if not positioning.data:
            return ""
        
        msg_arch = await self.get_message_architecture(positioning_id)
        
        p = positioning.data
        
        # Build elevator pitch
        pitch = f"{p['category_frame']} {p['differentiator']}. "
        
        if msg_arch and msg_arch.get('primary_claim'):
            pitch += f"We help {p['who_statement']} achieve {msg_arch['primary_claim']}. "
        
        pitch += f"{p['reason_to_believe']}."
        
        return pitch
    
    # =========================================================================
    # EXPORT
    # =========================================================================
    
    async def export_as_markdown(
        self,
        positioning_id: str
    ) -> str:
        """Export positioning and message architecture as Markdown"""
        # Get positioning
        positioning = await self.db.table('positioning').select('*').eq(
            'id', positioning_id
        ).single().execute()
        
        if not positioning.data:
            return ""
        
        p = positioning.data
        
        # Get message architecture
        msg_arch = await self.get_message_architecture(positioning_id)
        
        # Build markdown
        md = f"""# Positioning Statement

## For
{p['who_statement']}

## Category
{p['category_frame']}

## Differentiator
{p['differentiator']}

## Reason to Believe
{p['reason_to_believe']}

## Competitive Alternative
{p['competitive_alternative']}

---

# Message Architecture
"""
        
        if msg_arch:
            md += f"""
## Primary Claim
{msg_arch['primary_claim']}

## Proof Points
"""
            for i, pp in enumerate(msg_arch['proof_points'], 1):
                md += f"{i}. {pp['claim']}\n"
            
            if msg_arch.get('tagline'):
                md += f"\n## Tagline\n{msg_arch['tagline']}\n"
            
            if msg_arch.get('elevator_pitch'):
                md += f"\n## Elevator Pitch\n{msg_arch['elevator_pitch']}\n"
        
        return md
    
    async def export_as_json(
        self,
        positioning_id: str
    ) -> Dict[str, Any]:
        """Export positioning and message architecture as JSON"""
        # Get positioning
        positioning = await self.db.table('positioning').select('*').eq(
            'id', positioning_id
        ).single().execute()
        
        if not positioning.data:
            return {}
        
        # Get message architecture
        msg_arch = await self.get_message_architecture(positioning_id)
        
        return {
            'positioning': positioning.data,
            'message_architecture': msg_arch
        }
