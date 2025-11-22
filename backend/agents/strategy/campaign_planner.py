"""
Campaign Planner Agent - Generates move sequences, sprints, tasks, and content calendars.
Implements ADAPT framework for strategic campaign planning.
"""

import structlog
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from backend.config.prompts import MASTER_SUPERVISOR_SYSTEM_PROMPT
from backend.services.vertex_ai_client import vertex_ai_client
from backend.models.campaign import (
    MoveRequest, MoveResponse, Task, Sprint, LineOfOperation, 
    MoveMetrics
)
from backend.models.persona import ICPProfile
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class CampaignPlannerAgent:
    """
    Plans comprehensive marketing campaigns (moves) using ADAPT framework.
    
    ADAPT Framework:
    - Analyze: Understand the situation
    - Design: Craft the strategy
    - Advance: Execute tactical moves
    - Pivot: Adapt based on feedback
    - Track: Measure and learn
    
    Responsibilities:
    - Generate move sequences (Burst/Long patterns)
    - Create sprint structures with tasks
    - Determine lines of operation per channel
    - Build content calendar with daily/weekly tasks
    - Identify required assets (blogs, emails, social posts, visuals)
    """
    
    def __init__(self):
        self.move_patterns = {
            "burst": {
                "duration_days": 14,
                "intensity": "high",
                "description": "High-intensity 2-week campaign with daily actions"
            },
            "sustained": {
                "duration_days": 90,
                "intensity": "medium",
                "description": "3-month sustained presence with weekly rhythm"
            },
            "always_on": {
                "duration_days": 365,
                "intensity": "low",
                "description": "Year-long ambient presence with monthly themes"
            }
        }
    
    async def generate_campaign(
        self, 
        move_request: MoveRequest,
        icps: List[ICPProfile],
        market_insights: Optional[Dict[str, Any]] = None
    ) -> MoveResponse:
        """
        Generates a complete campaign (move) from request.
        
        Args:
            move_request: Campaign requirements
            icps: Target ICPs
            market_insights: Optional market research data
            
        Returns:
            Complete MoveResponse with sprints, tasks, and LOOs
        """
        correlation_id = get_correlation_id()
        logger.info(
            "Generating campaign plan",
            goal=move_request.goal,
            timeframe_days=move_request.timeframe_days,
            channels=move_request.channels,
            correlation_id=correlation_id
        )
        
        # Determine move pattern
        pattern = self._determine_pattern(move_request.timeframe_days)
        
        # Generate strategic approach using LLM
        strategic_plan = await self._generate_strategic_approach(
            move_request, icps, market_insights, pattern
        )
        
        # Create lines of operation per channel
        loos = await self._create_lines_of_operation(
            strategic_plan, move_request.channels, move_request.timeframe_days
        )
        
        # Build sprints with tasks
        sprints = await self._build_sprints(
            strategic_plan, loos, move_request.timeframe_days
        )
        
        # Assemble final move response
        move = MoveResponse(
            id=uuid4(),
            workspace_id=move_request.workspace_id,
            name=strategic_plan.get("move_name", move_request.name),
            goal=move_request.goal,
            status="planning",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=move_request.timeframe_days),
            target_cohort_ids=move_request.target_cohort_ids,
            channels=move_request.channels,
            lines_of_operation=loos,
            current_metrics=MoveMetrics()
        )
        
        logger.info(
            "Campaign plan generated",
            move_id=move.id,
            num_loos=len(loos),
            num_sprints=sum(len(loo.sprints) for loo in loos),
            correlation_id=correlation_id
        )
        
        return move
    
    async def _generate_strategic_approach(
        self,
        move_request: MoveRequest,
        icps: List[ICPProfile],
        market_insights: Optional[Dict],
        pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Uses LLM to generate strategic approach.
        """
        # Build context
        icp_summaries = "\n".join([
            f"- {icp.name}: {icp.executive_summary[:200]}"
            for icp in icps[:3]  # Top 3 ICPs
        ])
        
        insights_summary = ""
        if market_insights:
            insights_summary = f"\n\nMarket Insights:\n{market_insights.get('summary', 'N/A')}"
        
        prompt = f"""
You are a strategic campaign planner implementing the ADAPT framework.

CAMPAIGN REQUEST:
Goal: {move_request.goal}
Timeframe: {move_request.timeframe_days} days
Pattern: {pattern['description']}
Channels: {', '.join(move_request.channels)}
Budget: {move_request.budget or 'Not specified'}

TARGET ICPS:
{icp_summaries}

CONSTRAINTS:
{move_request.constraints or 'None specified'}
{insights_summary}

Using the ADAPT framework, design a strategic campaign:

1. **Analyze**: What's the core challenge? What's the opportunity?
2. **Design**: What's the overarching strategy? What's the narrative arc?
3. **Advance**: What are the key phases/sprints?
4. **Pivot**: What are the decision points to adjust?
5. **Track**: What are the success metrics?

Return JSON:
{{
    "move_name": "Catchy campaign name",
    "strategy_summary": "2-3 sentence strategy overview",
    "narrative_arc": "The story we're telling across this campaign",
    "phases": [
        {{
            "name": "Phase name",
            "duration_days": 7,
            "objective": "What this phase achieves",
            "key_actions": ["action 1", "action 2"]
        }}
    ],
    "decision_points": ["When to pivot or adjust"],
    "success_metrics": ["metric 1", "metric 2"],
    "content_themes": ["theme 1", "theme 2"]
}}
"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": MASTER_SUPERVISOR_SYSTEM_PROMPT + "\nYou are a master strategist using the ADAPT framework."
                },
                {"role": "user", "content": prompt}
            ]
            
            response = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            strategic_plan = json.loads(response)
            
            return strategic_plan
            
        except Exception as e:
            logger.error(f"Strategic approach generation failed: {e}")
            return self._fallback_strategy(move_request, pattern)
    
    async def _create_lines_of_operation(
        self,
        strategic_plan: Dict[str, Any],
        channels: List[str],
        timeframe_days: int
    ) -> List[LineOfOperation]:
        """
        Creates lines of operation for each channel.
        """
        loos = []
        
        for channel in channels:
            loo = LineOfOperation(
                id=uuid4(),
                name=f"{channel.title()} Operations",
                description=f"Activities and content for {channel}",
                target_channels=[channel],
                sprints=[],  # Will be populated by _build_sprints
                status="active"
            )
            loos.append(loo)
        
        return loos
    
    async def _build_sprints(
        self,
        strategic_plan: Dict[str, Any],
        loos: List[LineOfOperation],
        total_timeframe_days: int
    ) -> List[Sprint]:
        """
        Builds sprints with tasks based on phases.
        """
        all_sprints = []
        current_date = datetime.utcnow()
        
        phases = strategic_plan.get("phases", [])
        
        for idx, phase in enumerate(phases):
            sprint_duration = phase.get("duration_days", 7)
            
            # Create tasks for this sprint
            tasks = []
            for action_idx, action in enumerate(phase.get("key_actions", [])):
                task = Task(
                    id=uuid4(),
                    name=action,
                    description=f"Phase {idx + 1}: {phase.get('objective', '')}",
                    status="pending",
                    due_date=current_date + timedelta(days=sprint_duration - 1),
                    priority="high" if idx == 0 else "medium"
                )
                tasks.append(task)
            
            sprint = Sprint(
                id=uuid4(),
                name=phase.get("name", f"Sprint {idx + 1}"),
                start_date=current_date,
                end_date=current_date + timedelta(days=sprint_duration),
                goals=[phase.get("objective", "")],
                tasks=tasks,
                status="planned"
            )
            
            all_sprints.append(sprint)
            
            # Assign sprint to relevant LOO (distribute across channels)
            if loos:
                loo_idx = idx % len(loos)
                loos[loo_idx].sprints.append(sprint)
            
            current_date += timedelta(days=sprint_duration)
        
        return all_sprints
    
    def _determine_pattern(self, timeframe_days: int) -> Dict[str, Any]:
        """Determines move pattern based on timeframe."""
        if timeframe_days <= 21:
            return self.move_patterns["burst"]
        elif timeframe_days <= 120:
            return self.move_patterns["sustained"]
        else:
            return self.move_patterns["always_on"]
    
    def _fallback_strategy(self, move_request: MoveRequest, pattern: Dict) -> Dict[str, Any]:
        """Provides fallback strategy if LLM fails."""
        return {
            "move_name": f"{move_request.goal} Campaign",
            "strategy_summary": f"Execute {move_request.goal} over {move_request.timeframe_days} days",
            "narrative_arc": "Build awareness, generate engagement, drive conversions",
            "phases": [
                {
                    "name": "Launch",
                    "duration_days": 7,
                    "objective": "Initial awareness push",
                    "key_actions": ["Create content", "Engage audience"]
                },
                {
                    "name": "Growth",
                    "duration_days": 14,
                    "objective": "Scale engagement",
                    "key_actions": ["Amplify reach", "Nurture leads"]
                }
            ],
            "decision_points": ["Week 1: Review engagement metrics"],
            "success_metrics": ["Reach", "Engagement", "Conversions"],
            "content_themes": ["Value proposition", "Social proof"]
        }

    async def generate_30_60_90_plan(
        self,
        move_request: MoveRequest,
        icps: List[ICPProfile],
        market_insights: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates explicit 30/60/90-day marketing plan.

        Each period (30/60/90 days) includes:
        - Campaign phases (moves)
        - Deliverables (content, campaigns, assets)
        - Success metrics (KPIs)
        - Required resources (team, budget, tools)

        Args:
            move_request: Campaign requirements
            icps: Target ICPs with persona data
            market_insights: Optional market research data

        Returns:
            Structured 30/60/90 plan with detailed breakdowns
        """
        correlation_id = get_correlation_id()
        logger.info(
            "Generating 30/60/90-day plan",
            goal=move_request.goal,
            correlation_id=correlation_id
        )

        # Build ICP context
        icp_summaries = "\n".join([
            f"- {icp.name}: {icp.executive_summary[:200]}\n  Pain Points: {', '.join(icp.pain_points[:3])}"
            for icp in icps[:3]
        ])

        insights_summary = ""
        if market_insights:
            insights_summary = f"\n\nMarket Insights:\n{market_insights.get('answer', 'N/A')[:300]}"

        prompt = f"""
You are a strategic campaign planner creating a 30/60/90-day marketing plan.

CAMPAIGN GOAL: {move_request.goal}
CHANNELS: {', '.join(move_request.channels)}
BUDGET: {move_request.budget or 'Not specified'}

TARGET ICPs:
{icp_summaries}
{insights_summary}

Create a detailed 30/60/90-day plan following this structure:

**First 30 Days** (Foundation & Quick Wins):
- Focus: Build foundation, create core assets, generate early momentum
- Phase name and objectives
- Key deliverables (content, campaigns, assets)
- Success metrics/KPIs
- Required resources (team, budget breakdown, tools)

**Days 31-60** (Scale & Optimize):
- Focus: Scale what's working, optimize based on data
- Phase name and objectives
- Key deliverables
- Success metrics/KPIs
- Required resources

**Days 61-90** (Maximize & Prepare for Next):
- Focus: Maximize impact, prepare for sustainability
- Phase name and objectives
- Key deliverables
- Success metrics/KPIs
- Required resources

Return JSON:
{{
    "plan_summary": "2-3 sentence overview of the 90-day journey",
    "first_30_days": {{
        "phase_name": "Foundation Phase",
        "focus": "What we're focusing on",
        "objectives": ["objective 1", "objective 2"],
        "deliverables": [
            {{
                "type": "blog_post|email|social_campaign|landing_page|video|webinar",
                "description": "What this deliverable is",
                "quantity": 5,
                "due_week": 2
            }}
        ],
        "campaigns": [
            {{
                "name": "Campaign name",
                "description": "Brief description",
                "channels": ["linkedin", "email"],
                "duration_days": 14
            }}
        ],
        "success_metrics": [
            {{
                "metric": "KPI name",
                "target": "Target value",
                "measurement_method": "How we measure this"
            }}
        ],
        "required_resources": {{
            "team": ["Content creator", "Social media manager"],
            "budget_allocation": "$X for ads, $Y for tools",
            "tools": ["Tool 1", "Tool 2"]
        }}
    }},
    "days_31_60": {{
        "phase_name": "Scale Phase",
        "focus": "What we're focusing on",
        "objectives": ["objective 1", "objective 2"],
        "deliverables": [...],
        "campaigns": [...],
        "success_metrics": [...],
        "required_resources": {{...}}
    }},
    "days_61_90": {{
        "phase_name": "Maximize Phase",
        "focus": "What we're focusing on",
        "objectives": ["objective 1", "objective 2"],
        "deliverables": [...],
        "campaigns": [...],
        "success_metrics": [...],
        "required_resources": {{...}}
    }},
    "milestones": [
        {{
            "day": 30,
            "milestone": "What should be achieved",
            "decision_point": "What to evaluate/decide"
        }}
    ],
    "dependencies": ["Dependency 1", "Dependency 2"],
    "risks": ["Risk 1", "Risk 2"]
}}
"""

        try:
            messages = [
                {
                    "role": "system",
                    "content": MASTER_SUPERVISOR_SYSTEM_PROMPT + "\nYou create detailed 30/60/90-day marketing plans."
                },
                {"role": "user", "content": prompt}
            ]

            response = await openai_client.chat_completion(
                messages=messages,
                temperature=0.6,
                max_tokens=3500,
                response_format={"type": "json_object"}
            )

            import json
            plan = json.loads(response)

            # Add metadata
            plan["workspace_id"] = str(move_request.workspace_id)
            plan["goal"] = move_request.goal
            plan["channels"] = move_request.channels
            plan["target_cohort_ids"] = [str(cid) for cid in move_request.target_cohort_ids]
            plan["created_at"] = datetime.utcnow().isoformat()

            logger.info(
                "30/60/90-day plan generated",
                total_deliverables=sum([
                    len(plan.get("first_30_days", {}).get("deliverables", [])),
                    len(plan.get("days_31_60", {}).get("deliverables", [])),
                    len(plan.get("days_61_90", {}).get("deliverables", []))
                ]),
                correlation_id=correlation_id
            )

            return plan

        except Exception as e:
            logger.error(f"30/60/90 plan generation failed: {e}")
            return self._fallback_30_60_90_plan(move_request)

    def _fallback_30_60_90_plan(self, move_request: MoveRequest) -> Dict[str, Any]:
        """Fallback 30/60/90 plan if LLM fails."""
        return {
            "plan_summary": f"90-day plan for {move_request.goal}",
            "first_30_days": {
                "phase_name": "Foundation",
                "focus": "Build core assets and foundation",
                "objectives": ["Create core content", "Launch initial campaigns"],
                "deliverables": [
                    {
                        "type": "blog_post",
                        "description": "Core content pieces",
                        "quantity": 4,
                        "due_week": 2
                    }
                ],
                "campaigns": [],
                "success_metrics": [
                    {
                        "metric": "Content published",
                        "target": "4 pieces",
                        "measurement_method": "Count"
                    }
                ],
                "required_resources": {
                    "team": ["Content creator"],
                    "budget_allocation": "To be determined",
                    "tools": ["CMS", "Analytics"]
                }
            },
            "days_31_60": {
                "phase_name": "Scale",
                "focus": "Scale successful initiatives",
                "objectives": ["Increase reach"],
                "deliverables": [],
                "campaigns": [],
                "success_metrics": [],
                "required_resources": {}
            },
            "days_61_90": {
                "phase_name": "Optimize",
                "focus": "Optimize and prepare for next quarter",
                "objectives": ["Maximize ROI"],
                "deliverables": [],
                "campaigns": [],
                "success_metrics": [],
                "required_resources": {}
            },
            "milestones": [
                {"day": 30, "milestone": "Foundation complete", "decision_point": "Evaluate initial results"}
            ],
            "dependencies": [],
            "risks": ["Plan generation failed - using fallback"],
            "error": True
        }


# Global instance
campaign_planner = CampaignPlannerAgent()

