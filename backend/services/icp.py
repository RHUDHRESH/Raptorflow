"""
ICP service for business logic operations
Handles ICP-related business logic and validation
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.core.models import ValidationError
from backend.core.supabase_mgr import get_supabase_client
from backend.db.foundations import FoundationRepository
from backend.db.icps import ICPRepository
from backend.db.moves import MoveRepository
from backend.services.business_context_generator import get_business_context_generator
from backend.services.business_context_graph import get_business_context_graph, create_initial_workflow_state
from backend.schemas import RICP
from backend.redis_core.cache import cached


class ICPService:
    """Service for ICP business logic"""

    def __init__(self):
        self.repository = ICPRepository()
        self.foundation_repository = FoundationRepository()
        self.supabase = get_supabase_client()
        self.graph = get_business_context_graph()

    async def derive_trinity(
        self, workspace_id: str, cohort_name: str, context_override: Optional[str] = None
    ) -> RICP:
        """
        Derive the Trinity (Cohort, ICP, Persona) for a specific cohort.
        """
        # 1. Get foundation context
        foundation = await self.foundation_repository.get_by_workspace(workspace_id)
        if not foundation:
            raise ValidationError("Foundation data must be established before deriving cohorts")

        # 2. Prepare state for graph
        # We simulate an icp_list with just the desired cohort name
        icp_input = {
            "name": cohort_name,
            "description": context_override or f"A target segment named {cohort_name} for {foundation.get('company_name')}"
        }
        
        state = create_initial_workflow_state(
            workspace_id=workspace_id,
            user_id="system", # Derived by system
            foundation_data=foundation,
            icp_list=[icp_input]
        )

        # 3. Run the RICP/ICP enhancement node directly or run full graph
        # Since we only want the RICP for this cohort, we'll use the enhance_icp_node
        result = await self.graph.enhance_icp_node(state)
        
        if not result["context_data"].ricps:
            return self.graph.get_fallback_icp(icp_input)

        ricp = result["context_data"].ricps[0]
        
        # 4. Save to database
        db_data = {
            "name": ricp.name,
            "persona_name": ricp.persona_name,
            "avatar": ricp.avatar,
            "demographics": ricp.demographics.model_dump(),
            "psychographics": ricp.psychographics.model_dump(),
            "market_sophistication": {
                "stage": ricp.market_sophistication,
                "stage_name": self._get_sophistication_name(ricp.market_sophistication)
            },
            "confidence": ricp.confidence,
            "fit_score": ricp.confidence, # Map confidence to fit score for legacy
            "summary": f"{ricp.name}: {ricp.psychographics.identity}"
        }
        
        created = await self.repository.create(workspace_id, db_data)
        
        # Update ricp ID with database ID
        ricp.id = created.get("id", ricp.id)
        
        return ricp

    def _get_sophistication_name(self, stage: int) -> str:
        return {
            1: "Unaware",
            2: "Problem Aware",
            3: "Solution Aware",
            4: "Product Aware",
            5: "Most Aware"
        }.get(stage, "Unknown")

    async def create_icp(
        self, workspace_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create new ICP with validation

        Args:
            workspace_id: Workspace ID
            data: ICP data

        Returns:
            Created ICP data
        """
        # Validate required fields
        if not data.get("name"):
            raise ValidationError("ICP name is required")

        # Validate market sophistication
        if "market_sophistication" in data:
            soph = data["market_sophistication"]
            if not isinstance(soph, int) or soph < 1 or soph > 5:
                raise ValidationError(
                    "Market sophistication must be an integer between 1 and 5"
                )

        # Validate fit score
        if "fit_score" in data:
            score = data["fit_score"]
            if not isinstance(score, int) or score < 0 or score > 100:
                raise ValidationError("Fit score must be an integer between 0 and 100")

        # Check workspace ICP limit (max 3 for free tier, higher for paid tiers)
        workspace = (
            await self.supabase.table("workspaces")
            .select("*")
            .eq("id", workspace_id)
            .single()
            .execute()
        )
        if workspace.data:
            user = (
                await self.supabase.table("users")
                .select("*")
                .eq("id", workspace.data["user_id"])
                .single()
                .execute()
            )
            if user.data:
                tier = user.data.get("subscription_tier", "free")
                max_icps = {"free": 3, "starter": 5, "pro": 10, "enterprise": 50}.get(
                    tier, 3
                )

                current_count = await self.repository.count_by_workspace(workspace_id)
                if current_count >= max_icps:
                    raise ValidationError(f"Maximum ICP limit reached for {tier} tier")

        return await self.repository.create(workspace_id, data)

    async def generate_from_foundation(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        Generate ICPs from foundation data

        Args:
            workspace_id: Workspace ID

        Returns:
            List of generated ICPs
        """
        return await self.repository.generate_from_foundation(workspace_id)

    async def set_primary(self, workspace_id: str, icp_id: str) -> bool:
        """
        Set ICP as primary for workspace

        Args:
            workspace_id: Workspace ID
            icp_id: ICP ID

        Returns:
            True if successful, False otherwise
        """
        # Verify ICP belongs to workspace
        icp = await self.repository.get_by_id(icp_id, workspace_id)
        if not icp:
            raise ValidationError("ICP not found")

        return await self.repository.set_primary(workspace_id, icp_id)

    @cached(ttl=3600, cache_type="icps")
    async def get_primary(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get primary ICP for workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Primary ICP data or None if not found
        """
        return await self.repository.get_primary(workspace_id)

    @cached(ttl=3600, cache_type="icps")
    async def list_icps(
        self, workspace_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List ICPs for workspace with optional filters

        Args:
            workspace_id: Workspace ID
            filters: Optional filters

        Returns:
            List of ICP data
        """
        return await self.repository.list_by_workspace(workspace_id, filters)

    async def update_icp(
        self, icp_id: str, workspace_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update ICP with validation

        Args:
            icp_id: ICP ID
            workspace_id: Workspace ID
            data: Update data

        Returns:
            Updated ICP data or None if not found
        """
        # Validate data
        if "market_sophistication" in data:
            soph = data["market_sophistication"]
            if not isinstance(soph, int) or soph < 1 or soph > 5:
                raise ValidationError(
                    "Market sophistication must be an integer between 1 and 5"
                )

        if "fit_score" in data:
            score = data["fit_score"]
            if not isinstance(score, int) or score < 0 or score > 100:
                raise ValidationError("Fit score must be an integer between 0 and 100")

        result = await self.repository.update(icp_id, workspace_id, data)
        
        if result:
            # Invalidate ICP related caches
            from backend.redis_core.cache import CacheService
            cache = CacheService()
            await cache.invalidate_pattern(workspace_id, "icps*")
            
        return result

    async def delete_icp(self, icp_id: str, workspace_id: str) -> bool:
        """
        Delete ICP

        Args:
            icp_id: ICP ID
            workspace_id: Workspace ID

        Returns:
            True if deleted, False otherwise
        """
        # Check if it's primary ICP
        icp = await self.repository.get_by_id(icp_id, workspace_id)
        if icp and icp.get("is_primary"):
            # Find another ICP to make primary
            other_icps = await self.repository.list_by_workspace(
                workspace_id, {"is_primary": False}
            )
            if other_icps:
                await self.repository.set_primary(workspace_id, other_icps[0]["id"])

        return await self.repository.delete(icp_id, workspace_id)

    async def get_icp_with_analysis(
        self, icp_id: str, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get ICP with additional analysis data

        Args:
            icp_id: ICP ID
            workspace_id: Workspace ID

        Returns:
            ICP data with analysis or None if not found
        """
        icp = await self.repository.get_by_id(icp_id, workspace_id)
        if not icp:
            return None

        # Get related moves
        moves_result = (
            await self.supabase.table("moves")
            .select("*")
            .eq("target_icp_id", icp_id)
            .execute()
        )
        icp["related_moves"] = moves_result.data if moves_result.data else []

        # Get related assets
        assets_result = (
            await self.supabase.table("muse_assets")
            .select("*")
            .eq("target_icp_id", icp_id)
            .execute()
        )
        icp["related_assets"] = assets_result.data if assets_result.data else []

        # Calculate engagement metrics
        icp["move_count"] = len(icp["related_moves"])
        icp["asset_count"] = len(icp["related_assets"])

        return icp

    async def analyze_icp_performance(self, workspace_id: str) -> Dict[str, Any]:
        """
        Analyze ICP performance across workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Performance analysis data
        """
        icps = await self.list_icps(workspace_id)

        analysis = {
            "total_icps": len(icps),
            "primary_icp": None,
            "performance_by_icp": [],
            "top_performing_icp": None,
            "recommendations": [],
        }

        # Find primary ICP
        for icp in icps:
            if icp.get("is_primary"):
                analysis["primary_icp"] = icp
                break

        # Analyze each ICP
        for icp in icps:
            icp_analysis = await self.get_icp_with_analysis(icp["id"], workspace_id)
            if icp_analysis:
                performance = {
                    "icp_id": icp["id"],
                    "name": icp["name"],
                    "fit_score": icp.get("fit_score", 0),
                    "move_count": icp_analysis.get("move_count", 0),
                    "asset_count": icp_analysis.get("asset_count", 0),
                    "engagement_score": icp_analysis.get("move_count", 0)
                    + icp_analysis.get("asset_count", 0),
                }
                analysis["performance_by_icp"].append(performance)

        # Find top performing ICP
        if analysis["performance_by_icp"]:
            top_icp = max(
                analysis["performance_by_icp"], key=lambda x: x["engagement_score"]
            )
            analysis["top_performing_icp"] = top_icp

        # Generate recommendations
        if len(icps) < 3:
            analysis["recommendations"].append(
                "Consider creating more ICPs to diversify targeting"
            )

        if analysis["top_performing_icp"] and not analysis["primary_icp"]:
            analysis["recommendations"].append(
                f"Consider setting {analysis['top_performing_icp']['name']} as primary ICP"
            )

        return analysis

    async def validate_icp_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate ICP data before saving

        Args:
            data: ICP data to validate

        Returns:
            True if valid, raises ValidationError if invalid
        """
        # Required fields
        required_fields = ["name"]
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f"Required field missing: {field}")

        # Validate name length
        if len(data["name"]) > 100:
            raise ValidationError("ICP name too long (max 100 characters)")

        # Validate tagline length if provided
        if "tagline" in data and len(data["tagline"]) > 200:
            raise ValidationError("Tagline too long (max 200 characters)")

        # Validate market sophistication
        if "market_sophistication" in data:
            soph = data["market_sophistication"]
            if not isinstance(soph, int) or soph < 1 or soph > 5:
                raise ValidationError(
                    "Market sophistication must be an integer between 1 and 5"
                )

        # Validate fit score
        if "fit_score" in data:
            score = data["fit_score"]
            if not isinstance(score, int) or score < 0 or score > 100:
                raise ValidationError("Fit score must be an integer between 0 and 100")

        # Validate JSON fields
        json_fields = [
            "demographics",
            "psychographics",
            "behaviors",
            "pain_points",
            "goals",
        ]
        for field in json_fields:
            if field in data and not isinstance(data[field], list):
                raise ValidationError(f"{field} must be a list")

        return True
