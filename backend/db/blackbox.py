"""
Blackbox Strategies repository for database operations
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from backend.core.supabase_mgr import get_supabase_client

from .base import Repository
from .filters import Filter, build_query
from .pagination import PaginatedResult, Pagination


class BlackboxRepository(Repository):
    """Repository for blackbox strategy operations"""

    def __init__(self):
        super().__init__(get_supabase_client())

    async def list_pending(
        self, workspace_id: str, pagination: Optional[Pagination] = None
    ) -> PaginatedResult:
        """List pending strategies for a workspace"""
        query = (
            self.client.table("blackbox_strategies")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("status", "proposed")
        )

        if pagination:
            query = query.order("created_at", desc=True).range(
                pagination.page * pagination.page_size,
                (pagination.page + 1) * pagination.page_size - 1,
            )

        result = query.execute()

        if pagination:
            count_result = (
                self.client.table("blackbox_strategies")
                .select("id", count="exact")
                .eq("workspace_id", workspace_id)
                .eq("status", "proposed")
                .execute()
            )
            total = count_result.count or 0

            return PaginatedResult(
                items=result.data or [],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size,
            )

        return PaginatedResult(
            items=result.data or [],
            total=len(result.data or []),
            page=0,
            page_size=len(result.data or []),
            total_pages=1,
        )

    async def accept_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Accept a strategy and convert it to a move"""
        # Get strategy details
        strategy_result = (
            self.client.table("blackbox_strategies")
            .select("*")
            .eq("id", strategy_id)
            .single()
            .execute()
        )

        if not strategy_result.data:
            return None

        strategy = strategy_result.data

        # Create move from strategy
        move_data = {
            "workspace_id": strategy["workspace_id"],
            "name": strategy["name"],
            "category": "ignite",  # Default category for blackbox strategies
            "goal": strategy.get("expected_upside", "Execute blackbox strategy"),
            "strategy": {
                "source": "blackbox",
                "original_strategy_id": strategy_id,
                "risk_level": strategy.get("risk_level"),
                "risk_reasons": strategy.get("risk_reasons", []),
                "phases": strategy.get("phases", []),
                "expected_upside": strategy.get("expected_upside"),
                "potential_downside": strategy.get("potential_downside"),
            },
            "status": "draft",
            "duration_days": 30,  # Default duration
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }

        # Create the move
        move_result = self.client.table("moves").insert(move_data).execute()

        if not move_result.data:
            return None

        move = move_result.data[0]

        # Update strategy to mark as accepted and link to move
        strategy_update = {
            "status": "accepted",
            "accepted_at": datetime.utcnow().isoformat(),
            "converted_move_id": move["id"],
        }

        self.client.table("blackbox_strategies").update(strategy_update).eq(
            "id", strategy_id
        ).execute()

        return {"strategy": strategy, "move": move, "conversion_successful": True}

    async def reject_strategy(
        self, strategy_id: str, reason: Optional[str] = None
    ) -> bool:
        """Reject a strategy"""
        update_data = {"status": "rejected"}

        if reason:
            update_data["rejection_reason"] = reason

        result = (
            self.client.table("blackbox_strategies")
            .update(update_data)
            .eq("id", strategy_id)
            .execute()
        )
        return len(result.data or []) > 0

    async def get_strategy_analysis(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed analysis of a strategy"""
        strategy = await self.get(strategy_id)
        if not strategy:
            return None

        # Calculate risk metrics
        risk_level = strategy.get("risk_level", 5)
        risk_reasons = strategy.get("risk_reasons", [])

        # Analyze phases
        phases = strategy.get("phases", [])
        phase_count = len(phases)
        estimated_duration = sum(phase.get("duration_days", 0) for phase in phases)

        # Risk assessment
        risk_categories = {
            "low": risk_level <= 3,
            "medium": risk_level > 3 and risk_level <= 7,
            "high": risk_level > 7,
        }

        return {
            "strategy_id": strategy_id,
            "risk_level": risk_level,
            "risk_category": next(k for k, v in risk_categories.items() if v),
            "risk_reasons": risk_reasons,
            "phase_count": phase_count,
            "estimated_duration_days": estimated_duration,
            "expected_upside": strategy.get("expected_upside"),
            "potential_downside": strategy.get("potential_downside"),
            "focus_area": strategy.get("focus_area"),
            "status": strategy.get("status"),
            "created_at": strategy.get("created_at"),
            "accepted_at": strategy.get("accepted_at"),
        }

    async def get_workspace_risk_profile(self, workspace_id: str) -> Dict[str, Any]:
        """Get risk profile for workspace strategies"""
        result = (
            self.client.table("blackbox_strategies")
            .select("*")
            .eq("workspace_id", workspace_id)
            .execute()
        )
        strategies = result.data or []

        if not strategies:
            return {"workspace_id": workspace_id, "total_strategies": 0}

        # Calculate risk distribution
        risk_levels = [s.get("risk_level", 5) for s in strategies]
        avg_risk = sum(risk_levels) / len(risk_levels) if risk_levels else 0

        risk_distribution = {"low": 0, "medium": 0, "high": 0}
        for risk_level in risk_levels:
            if risk_level <= 3:
                risk_distribution["low"] += 1
            elif risk_level <= 7:
                risk_distribution["medium"] += 1
            else:
                risk_distribution["high"] += 1

        # Focus area distribution
        focus_areas = {}
        for strategy in strategies:
            area = strategy.get("focus_area", "unknown")
            focus_areas[area] = focus_areas.get(area, 0) + 1

        # Conversion rates
        total_proposed = len([s for s in strategies if s.get("status") == "proposed"])
        total_accepted = len([s for s in strategies if s.get("status") == "accepted"])
        conversion_rate = (
            (total_accepted / (total_proposed + total_accepted) * 100)
            if (total_proposed + total_accepted) > 0
            else 0
        )

        return {
            "workspace_id": workspace_id,
            "total_strategies": len(strategies),
            "average_risk_level": avg_risk,
            "risk_distribution": risk_distribution,
            "focus_areas": focus_areas,
            "conversion_rate": conversion_rate,
            "total_proposed": total_proposed,
            "total_accepted": total_accepted,
            "total_converted": len(
                [s for s in strategies if s.get("converted_move_id")]
            ),
        }

    async def get_strategy_recommendations(
        self, workspace_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get strategy recommendations based on workspace profile"""
        # Get workspace risk profile
        risk_profile = await self.get_workspace_risk_profile(workspace_id)

        # Get pending strategies
        pending_result = (
            self.client.table("blackbox_strategies")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("status", "proposed")
            .order("risk_level", asc=True)
            .limit(limit)
            .execute()
        )
        strategies = pending_result.data or []

        # Add recommendation scores
        recommended_strategies = []
        for strategy in strategies:
            score = 100  # Base score

            # Adjust based on risk (prefer lower risk for conservative profiles)
            if risk_profile.get("average_risk_level", 5) < 4:
                score -= (strategy.get("risk_level", 5) - 3) * 10

            # Adjust based on focus area balance
            focus_areas = risk_profile.get("focus_areas", {})
            current_area = strategy.get("focus_area", "unknown")
            if focus_areas.get(current_area, 0) > 2:
                score -= 15  # Penalize over-represented areas

            # Ensure score doesn't go negative
            score = max(0, score)

            recommended_strategies.append(
                {
                    **strategy,
                    "recommendation_score": score,
                    "recommendation_reason": self._get_recommendation_reason(
                        strategy, risk_profile
                    ),
                }
            )

        # Sort by recommendation score
        recommended_strategies.sort(
            key=lambda x: x["recommendation_score"], reverse=True
        )

        return recommended_strategies

    def _get_recommendation_reason(
        self, strategy: Dict[str, Any], risk_profile: Dict[str, Any]
    ) -> str:
        """Generate recommendation reason for a strategy"""
        risk_level = strategy.get("risk_level", 5)
        focus_area = strategy.get("focus_area", "unknown")

        reasons = []

        if risk_level <= 3:
            reasons.append("Low risk profile")
        elif risk_level >= 8:
            reasons.append("High potential reward")

        focus_areas = risk_profile.get("focus_areas", {})
        if focus_areas.get(focus_area, 0) == 0:
            reasons.append(f"New focus area: {focus_area}")
        elif focus_areas.get(focus_area, 0) == 1:
            reasons.append(f"Complementary to existing {focus_area} strategies")

        if strategy.get("expected_upside"):
            reasons.append("Strong expected upside")

        return "; ".join(reasons) if reasons else "General recommendation"

    async def batch_update_status(self, strategy_ids: List[str], status: str) -> int:
        """Update status for multiple strategies"""
        valid_statuses = ["proposed", "accepted", "rejected", "archived"]
        if status not in valid_statuses:
            raise ValueError(
                f"Invalid status: {status}. Must be one of: {valid_statuses}"
            )

        update_data = {"status": status}
        if status == "accepted":
            update_data["accepted_at"] = datetime.utcnow().isoformat()

        # Update in batches
        updated_count = 0
        batch_size = 50

        for i in range(0, len(strategy_ids), batch_size):
            batch = strategy_ids[i : i + batch_size]
            result = (
                self.client.table("blackbox_strategies")
                .update(update_data)
                .in_("id", batch)
                .execute()
            )
            updated_count += len(result.data or [])

        return updated_count

    async def get_strategy_timeline(self, strategy_id: str) -> List[Dict[str, Any]]:
        """Get timeline of strategy events"""
        strategy = await self.get(strategy_id)
        if not strategy:
            return []

        timeline = []

        # Strategy creation
        if strategy.get("created_at"):
            timeline.append(
                {
                    "type": "strategy_proposed",
                    "date": strategy["created_at"],
                    "description": f"Strategy '{strategy.get('name')}' proposed",
                    "details": {
                        "risk_level": strategy.get("risk_level"),
                        "focus_area": strategy.get("focus_area"),
                    },
                }
            )

        # Strategy acceptance
        if strategy.get("accepted_at"):
            timeline.append(
                {
                    "type": "strategy_accepted",
                    "date": strategy["accepted_at"],
                    "description": f"Strategy '{strategy.get('name')}' accepted",
                    "details": {"converted_move_id": strategy.get("converted_move_id")},
                }
            )

        # Get move events if converted
        if strategy.get("converted_move_id"):
            move_result = (
                self.client.table("moves")
                .select("*")
                .eq("id", strategy["converted_move_id"])
                .single()
                .execute()
            )
            if move_result.data:
                move = move_result.data

                if move.get("created_at"):
                    timeline.append(
                        {
                            "type": "move_created",
                            "date": move["created_at"],
                            "description": f"Move '{move.get('name')}' created from strategy",
                            "details": {"move_id": move["id"]},
                        }
                    )

                if move.get("started_at"):
                    timeline.append(
                        {
                            "type": "move_started",
                            "date": move["started_at"],
                            "description": f"Move '{move.get('name')}' started",
                            "details": {"move_id": move["id"]},
                        }
                    )

                if move.get("completed_at"):
                    timeline.append(
                        {
                            "type": "move_completed",
                            "date": move["completed_at"],
                            "description": f"Move '{move.get('name')}' completed",
                            "details": {"move_id": move["id"]},
                        }
                    )

        # Sort by date
        timeline.sort(key=lambda x: x["date"], reverse=True)

        return timeline

    async def archive_old_strategies(
        self, workspace_id: str, days_old: int = 90
    ) -> int:
        """Archive strategies older than specified days"""
        from datetime import timedelta

        cutoff_date = (datetime.utcnow() - timedelta(days=days_old)).isoformat()

        result = (
            self.client.table("blackbox_strategies")
            .update({"status": "archived"})
            .eq("workspace_id", workspace_id)
            .lt("created_at", cutoff_date)
            .neq("status", "archived")
            .execute()
        )

        return len(result.data or [])

    async def get_strategy_performance_metrics(
        self, workspace_id: str
    ) -> Dict[str, Any]:
        """Get performance metrics for strategies"""
        # Get all strategies for workspace
        strategies_result = (
            self.client.table("blackbox_strategies")
            .select("*")
            .eq("workspace_id", workspace_id)
            .execute()
        )
        strategies = strategies_result.data or []

        if not strategies:
            return {"workspace_id": workspace_id, "total_strategies": 0}

        # Basic metrics
        total_strategies = len(strategies)
        proposed_strategies = len(
            [s for s in strategies if s.get("status") == "proposed"]
        )
        accepted_strategies = len(
            [s for s in strategies if s.get("status") == "accepted"]
        )
        rejected_strategies = len(
            [s for s in strategies if s.get("status") == "rejected"]
        )
        converted_strategies = len(
            [s for s in strategies if s.get("converted_move_id")]
        )

        # Success metrics (based on converted moves)
        converted_move_ids = [
            s["converted_move_id"] for s in strategies if s.get("converted_move_id")
        ]
        successful_conversions = 0

        if converted_move_ids:
            moves_result = (
                self.client.table("moves")
                .select("status")
                .in_("id", converted_move_ids)
                .execute()
            )
            moves = moves_result.data or []
            successful_conversions = len(
                [m for m in moves if m.get("status") == "completed"]
            )

        # Calculate rates
        acceptance_rate = (
            (accepted_strategies / total_strategies * 100)
            if total_strategies > 0
            else 0
        )
        conversion_rate = (
            (converted_strategies / total_strategies * 100)
            if total_strategies > 0
            else 0
        )
        success_rate = (
            (successful_conversions / converted_strategies * 100)
            if converted_strategies > 0
            else 0
        )

        return {
            "workspace_id": workspace_id,
            "total_strategies": total_strategies,
            "proposed_strategies": proposed_strategies,
            "accepted_strategies": accepted_strategies,
            "rejected_strategies": rejected_strategies,
            "converted_strategies": converted_strategies,
            "successful_conversions": successful_conversions,
            "acceptance_rate": acceptance_rate,
            "conversion_rate": conversion_rate,
            "success_rate": success_rate,
        }
