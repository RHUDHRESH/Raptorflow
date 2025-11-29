"""
Scheduler Agent - Determines optimal posting times and generates daily checklists.
Uses analytics data to find best engagement windows for each platform.
"""

import structlog
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import json

from backend.services.vertex_ai_client import vertex_ai_client
from backend.services.supabase_client import supabase_client
from backend.models.campaign import Task, Sprint
from backend.utils.correlation import get_correlation_id
from backend.utils.cache import redis_cache
from backend.agents.base_agent import BaseAgent

logger = structlog.get_logger(__name__)


class SchedulerAgent(BaseAgent):
    """
    Optimizes content scheduling based on audience engagement patterns.
    Generates daily/weekly checklists for execution.
    """
    
    def __init__(self):
        super().__init__(name="scheduler_agent")
        self.llm = vertex_ai_client
        # Default best times per platform (can be overridden by analytics)
        self.default_optimal_times = {
            "linkedin": ["08:00", "12:00", "17:00"],  # Business hours
            "twitter": ["09:00", "12:00", "15:00", "18:00"],  # Multiple daily windows
            "instagram": ["11:00", "14:00", "19:00"],  # Lunch and evening
            "facebook": ["13:00", "15:00", "19:00"],  # Afternoon and evening
            "youtube": ["14:00", "20:00"],  # Afternoon and prime time
            "email": ["08:00", "13:00"],  # Morning and post-lunch
        }
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute scheduling tasks.
        
        Args:
            payload: Dictionary containing:
                - task_type: "get_optimal_times", "generate_checklist", "schedule_batch"
                - workspace_id: UUID/str
                - ... other params depending on task
        """
        try:
            task_type = payload.get("task_type")
            workspace_id_str = payload.get("workspace_id")
            workspace_id = UUID(workspace_id_str) if workspace_id_str else None
            correlation_id = payload.get("correlation_id")

            self.log(f"Executing scheduler task: {task_type}", level="info")

            if task_type == "get_optimal_times":
                platform = payload.get("platform")
                date_str = payload.get("date")
                date = datetime.fromisoformat(date_str) if date_str else datetime.now()
                count = payload.get("count", 1)
                
                times = await self.get_optimal_post_times(workspace_id, platform, date, count, correlation_id)
                return {
                    "status": "success",
                    "result": [t.isoformat() for t in times],
                    "metadata": {"count": len(times)}
                }
                
            elif task_type == "generate_checklist":
                move_id_str = payload.get("move_id")
                move_id = UUID(move_id_str) if move_id_str else None
                date_str = payload.get("date")
                date = datetime.fromisoformat(date_str) if date_str else datetime.now()
                
                tasks = await self.generate_daily_checklist(workspace_id, move_id, date, correlation_id)
                return {
                    "status": "success",
                    "result": [t.model_dump() for t in tasks],  # Assuming Task is Pydantic
                    "metadata": {"count": len(tasks)}
                }
                
            elif task_type == "schedule_batch":
                move_id_str = payload.get("move_id")
                move_id = UUID(move_id_str) if move_id_str else None
                content_variants = payload.get("content_variants", [])
                start_date_str = payload.get("start_date")
                start_date = datetime.fromisoformat(start_date_str) if start_date_str else datetime.now()
                end_date_str = payload.get("end_date")
                end_date = datetime.fromisoformat(end_date_str) if end_date_str else datetime.now() + timedelta(days=7)
                
                schedule = await self.schedule_content_batch(
                    workspace_id, move_id, content_variants, start_date, end_date, correlation_id
                )
                
                await self.publish_event(
                    "agent.execution.content_scheduled",
                    {
                        "workspace_id": str(workspace_id),
                        "move_id": str(move_id),
                        "items_scheduled": len(schedule)
                    }
                )
                
                return {
                    "status": "success",
                    "result": schedule,
                    "metadata": {"count": len(schedule)}
                }
            
            else:
                raise ValueError(f"Unknown task_type: {task_type}")

        except Exception as e:
            self.log(f"Scheduler task failed: {str(e)}", level="error")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_optimal_post_times(
        self,
        workspace_id: UUID,
        platform: str,
        date: datetime,
        count: int = 1,
        correlation_id: str = None
    ) -> List[datetime]:
        """
        Determines optimal posting times for a platform on a given date.
        Uses historical engagement data if available, falls back to defaults.
        
        Args:
            workspace_id: User's workspace
            platform: Social platform
            date: Target date
            count: Number of time slots needed
            
        Returns:
            List of optimal datetime objects
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Getting optimal post times", platform=platform, date=date.date(), count=count, correlation_id=correlation_id)
        
        cache_key = f"optimal_times:{workspace_id}:{platform}:{date.date()}"
        cached_times = await redis_cache.get(cache_key)
        if cached_times:
            return [datetime.fromisoformat(t) for t in cached_times[:count]]
        
        # Try to get analytics data for this workspace/platform
        try:
            analytics_data = await supabase_client.fetch_all(
                "metrics_snapshot",
                {"workspace_id": str(workspace_id), "platform": platform}
            )
            
            if analytics_data and len(analytics_data) > 10:
                # Have enough data to use AI for pattern analysis
                optimal_times = await self._analyze_engagement_patterns(
                    analytics_data,
                    platform,
                    count,
                    correlation_id
                )
            else:
                # Use defaults
                optimal_times = self._get_default_times(platform, date, count)
        except Exception as e:
            logger.warning(f"Failed to fetch analytics, using defaults: {e}", correlation_id=correlation_id)
            optimal_times = self._get_default_times(platform, date, count)
        
        # Cache for 7 days
        await redis_cache.set(cache_key, [t.isoformat() for t in optimal_times], ttl=604800)
        
        return optimal_times
    
    def _get_default_times(self, platform: str, date: datetime, count: int) -> List[datetime]:
        """Gets default optimal times for a platform."""
        time_strings = self.default_optimal_times.get(platform, ["12:00"])
        times = []
        
        for time_str in time_strings[:count]:
            hour, minute = map(int, time_str.split(":"))
            optimal_datetime = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            times.append(optimal_datetime)
        
        return times
    
    async def _analyze_engagement_patterns(
        self,
        analytics_data: List[Dict],
        platform: str,
        count: int,
        correlation_id: str
    ) -> List[datetime]:
        """Uses AI to analyze engagement patterns and suggest optimal times."""
        # Prepare analytics summary for LLM
        engagement_summary = json.dumps(analytics_data[-50:])  # Last 50 data points
        
        prompt = f"""Analyze this {platform} engagement data and identify the {count} best times of day to post.

**Analytics Data** (last 50 posts with timestamps and engagement):
{engagement_summary}

**Task**: Identify the {count} time windows (HH:MM format) that historically get the highest engagement (likes, comments, shares).

Output as JSON array: ["HH:MM", "HH:MM", ...]
"""
        
        messages = [
            {"role": "system", "content": "You are a data analyst specializing in social media engagement optimization."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Use fast model for quick analysis
            llm_response = await self.llm.chat_completion(
                messages,
                model_type="fast",
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            time_strings = json.loads(llm_response)
            if not isinstance(time_strings, list):
                raise ValueError("Invalid response format")
            
            # Convert to datetime objects
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            times = []
            for time_str in time_strings[:count]:
                hour, minute = map(int, time_str.split(":"))
                times.append(today.replace(hour=hour, minute=minute))
            
            return times
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}", correlation_id=correlation_id)
            return self._get_default_times(platform, datetime.now(), count)
    
    async def generate_daily_checklist(
        self,
        workspace_id: UUID,
        move_id: UUID,
        date: datetime,
        correlation_id: str = None
    ) -> List[Task]:
        """
        Generates a daily checklist of tasks for a specific move/campaign.
        
        Args:
            workspace_id: User's workspace
            move_id: Campaign ID
            date: Target date
            
        Returns:
            List of tasks due on that date
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Generating daily checklist", move_id=move_id, date=date.date(), correlation_id=correlation_id)
        
        # Fetch move details
        move_data = await supabase_client.fetch_one("moves", {"id": str(move_id), "workspace_id": str(workspace_id)})
        if not move_data:
            raise ValueError(f"Move {move_id} not found")
        
        # Get all tasks for this move
        tasks_data = await supabase_client.fetch_all("tasks", {"move_id": str(move_id)})
        
        # Filter tasks due on target date
        daily_tasks = []
        for task_data in tasks_data:
            task = Task(**task_data)
            if task.due_date and task.due_date.date() == date.date():
                daily_tasks.append(task)
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        daily_tasks.sort(key=lambda t: priority_order.get(t.priority, 1))
        
        logger.info("Daily checklist generated", task_count=len(daily_tasks), correlation_id=correlation_id)
        return daily_tasks
    
    async def schedule_content_batch(
        self,
        workspace_id: UUID,
        move_id: UUID,
        content_variants: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime,
        correlation_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Schedules multiple content pieces across optimal times.
        
        Args:
            workspace_id: User's workspace
            move_id: Campaign ID
            content_variants: List of content to schedule
            start_date: Campaign start
            end_date: Campaign end
            
        Returns:
            List of scheduled posts with timestamps
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Scheduling content batch", count=len(content_variants), correlation_id=correlation_id)
        
        scheduled_posts = []
        current_date = start_date
        content_index = 0
        
        while current_date <= end_date and content_index < len(content_variants):
            variant = content_variants[content_index]
            platform = variant.get("platform", "linkedin")
            
            # Get optimal time for this platform
            optimal_times = await self.get_optimal_post_times(
                workspace_id,
                platform,
                current_date,
                count=1,
                correlation_id=correlation_id
            )
            
            scheduled_posts.append({
                "content_id": variant.get("id"),
                "platform": platform,
                "scheduled_time": optimal_times[0].isoformat(),
                "move_id": str(move_id)
            })
            
            content_index += 1
            
            # Move to next day if we've scheduled content for today
            if content_index % 2 == 0:  # Adjust frequency as needed
                current_date += timedelta(days=1)
        
        logger.info("Content batch scheduled", scheduled_count=len(scheduled_posts), correlation_id=correlation_id)
        return scheduled_posts


scheduler_agent = SchedulerAgent()
