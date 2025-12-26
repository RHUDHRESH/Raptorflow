import json
import logging
from typing import Any, List, Optional
from datetime import datetime

from memory.short_term import L1ShortTermMemory
from models.swarm import SwarmTask, CompetitorProfile, CompetitorGroup, CompetitorInsight, CompetitorAnalysis

logger = logging.getLogger("raptorflow.memory.swarm_l1")


class SwarmL1MemoryManager:
    """
    SOTA Swarm L1 Memory Manager.
    Coordinates real-time state synchronization between swarm agents.
    Uses Redis hashes and sets for efficient cross-agent data access.
    """

    def __init__(self, thread_id: str):
        self.thread_id = thread_id
        self.l1 = L1ShortTermMemory()
        self.prefix = f"swarm:{thread_id}:"
        self.tasks_key = f"{self.prefix}tasks"
        self.knowledge_key = f"{self.prefix}knowledge"
        self.competitor_profiles_key = f"{self.prefix}competitor_profiles"
        self.competitor_groups_key = f"{self.prefix}competitor_groups"
        self.competitor_insights_key = f"{self.prefix}competitor_insights"
        self.competitor_analyses_key = f"{self.prefix}competitor_analyses"

    async def update_task(self, task: SwarmTask):
        """Updates or adds a sub-task in the swarm's real-time state."""
        try:
            # We use a Redis hash for tasks within a thread
            full_key = self.tasks_key
            field = task.id
            serialized = task.model_dump_json()
            if self.l1.client:
                await self.l1.client.hset(full_key, field, serialized)
                logger.info(f"Swarm Task {task.id} updated in L1 hash.")
            else:
                # Fallback for missing client
                logger.warning("No Redis client available for swarm task update.")
        except Exception as e:
            logger.error(f"Failed to update swarm task in L1: {e}")

    async def get_all_tasks(self) -> List[SwarmTask]:
        """Retrieves all sub-tasks for the current swarm run."""
        try:
            if not self.l1.client:
                return []
            raw_tasks = await self.l1.client.hgetall(self.tasks_key)
            tasks = []
            for field, val in raw_tasks.items():
                if isinstance(val, bytes):
                    val = val.decode("utf-8")
                tasks.append(SwarmTask.model_validate_json(val))
            return tasks
        except Exception as e:
            logger.error(f"Failed to retrieve swarm tasks from L1: {e}")
            return []

    async def update_knowledge(self, key: str, value: Any):
        """Adds a finding to the swarm's shared knowledge pool."""
        try:
            if not self.l1.client:
                return
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            if isinstance(value, str):
                try:
                    json.loads(value)
                    serialized = value
                except json.JSONDecodeError:
                    serialized = json.dumps(value)
            else:
                serialized = json.dumps(value)
            await self.l1.client.hset(self.knowledge_key, key, serialized)
            logger.info(f"Swarm knowledge '{key}' updated in L1 hash.")
        except Exception as e:
            logger.error(f"Failed to update swarm knowledge in L1: {e}")

    async def get_knowledge(self, key: str) -> Optional[Any]:
        """Retrieves a specific finding from the shared knowledge pool."""
        try:
            if not self.l1.client:
                return None
            raw = await self.l1.client.hget(self.knowledge_key, key)
            if raw:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                return json.loads(raw)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve swarm knowledge from L1: {e}")
            return None

    async def update_competitor_profile(self, competitor: CompetitorProfile):
        """Updates or adds a competitor profile in the swarm's real-time state."""
        try:
            full_key = self.competitor_profiles_key
            field = competitor.id
            serialized = competitor.model_dump_json()
            if self.l1.client:
                await self.l1.client.hset(full_key, field, serialized)
                logger.info(f"Competitor Profile {competitor.id} updated in L1 hash.")
            else:
                logger.warning("No Redis client available for competitor profile update.")
        except Exception as e:
            logger.error(f"Failed to update competitor profile in L1: {e}")

    async def get_competitor_profile(self, competitor_id: str) -> Optional[CompetitorProfile]:
        """Retrieves a specific competitor profile."""
        try:
            if not self.l1.client:
                return None
            raw = await self.l1.client.hget(self.competitor_profiles_key, competitor_id)
            if raw:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                return CompetitorProfile.model_validate_json(raw)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve competitor profile from L1: {e}")
            return None

    async def get_all_competitor_profiles(self) -> List[CompetitorProfile]:
        """Retrieves all competitor profiles for the current swarm run."""
        try:
            if not self.l1.client:
                return []
            raw_profiles = await self.l1.client.hgetall(self.competitor_profiles_key)
            profiles = []
            for field, val in raw_profiles.items():
                if isinstance(val, bytes):
                    val = val.decode("utf-8")
                profiles.append(CompetitorProfile.model_validate_json(val))
            return profiles
        except Exception as e:
            logger.error(f"Failed to retrieve competitor profiles from L1: {e}")
            return []

    async def update_competitor_group(self, group: CompetitorGroup):
        """Updates or adds a competitor group in the swarm's real-time state."""
        try:
            full_key = self.competitor_groups_key
            field = group.id
            serialized = group.model_dump_json()
            if self.l1.client:
                await self.l1.client.hset(full_key, field, serialized)
                logger.info(f"Competitor Group {group.id} updated in L1 hash.")
            else:
                logger.warning("No Redis client available for competitor group update.")
        except Exception as e:
            logger.error(f"Failed to update competitor group in L1: {e}")

    async def get_all_competitor_groups(self) -> List[CompetitorGroup]:
        """Retrieves all competitor groups for the current swarm run."""
        try:
            if not self.l1.client:
                return []
            raw_groups = await self.l1.client.hgetall(self.competitor_groups_key)
            groups = []
            for field, val in raw_groups.items():
                if isinstance(val, bytes):
                    val = val.decode("utf-8")
                groups.append(CompetitorGroup.model_validate_json(val))
            return groups
        except Exception as e:
            logger.error(f"Failed to retrieve competitor groups from L1: {e}")
            return []

    async def add_competitor_insight(self, insight: CompetitorInsight):
        """Adds a competitor insight to the swarm's real-time state."""
        try:
            if not self.l1.client:
                return
            # Use a list to store insights (as a JSON array in Redis)
            existing_insights = await self.get_all_competitor_insights()
            existing_insights.append(insight)
            serialized = json.dumps([insight.model_dump() for insight in existing_insights])
            await self.l1.client.set(self.competitor_insights_key, serialized)
            logger.info(f"Competitor Insight {insight.id} added to L1.")
        except Exception as e:
            logger.error(f"Failed to add competitor insight to L1: {e}")

    async def get_all_competitor_insights(self) -> List[CompetitorInsight]:
        """Retrieves all competitor insights for the current swarm run."""
        try:
            if not self.l1.client:
                return []
            raw = await self.l1.client.get(self.competitor_insights_key)
            if raw:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                insights_data = json.loads(raw)
                return [CompetitorInsight.model_validate(insight) for insight in insights_data]
            return []
        except Exception as e:
            logger.error(f"Failed to retrieve competitor insights from L1: {e}")
            return []

    async def add_competitor_analysis(self, analysis: CompetitorAnalysis):
        """Adds a competitor analysis to the swarm's real-time state."""
        try:
            if not self.l1.client:
                return
            # Use a list to store analyses
            existing_analyses = await self.get_all_competitor_analyses()
            existing_analyses.append(analysis)
            serialized = json.dumps([analysis.model_dump() for analysis in existing_analyses])
            await self.l1.client.set(self.competitor_analyses_key, serialized)
            logger.info(f"Competitor Analysis {analysis.id} added to L1.")
        except Exception as e:
            logger.error(f"Failed to add competitor analysis to L1: {e}")

    async def get_all_competitor_analyses(self) -> List[CompetitorAnalysis]:
        """Retrieves all competitor analyses for the current swarm run."""
        try:
            if not self.l1.client:
                return []
            raw = await self.l1.client.get(self.competitor_analyses_key)
            if raw:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                analyses_data = json.loads(raw)
                return [CompetitorAnalysis.model_validate(analysis) for analysis in analyses_data]
            return []
        except Exception as e:
            logger.error(f"Failed to retrieve competitor analyses from L1: {e}")
            return []

    async def get_competitor_watchlist(self) -> List[str]:
        """Retrieves the current competitor watchlist."""
        try:
            if not self.l1.client:
                return []
            raw = await self.l1.client.get(f"{self.prefix}competitor_watchlist")
            if raw:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                return json.loads(raw)
            return []
        except Exception as e:
            logger.error(f"Failed to retrieve competitor watchlist from L1: {e}")
            return []

    async def update_competitor_watchlist(self, watchlist: List[str]):
        """Updates the competitor watchlist."""
        try:
            if not self.l1.client:
                return
            serialized = json.dumps(watchlist)
            await self.l1.client.set(f"{self.prefix}competitor_watchlist", serialized)
            logger.info(f"Competitor watchlist updated with {len(watchlist)} items.")
        except Exception as e:
            logger.error(f"Failed to update competitor watchlist in L1: {e}")

    async def get_last_competitor_scan(self) -> Optional[datetime]:
        """Retrieves the timestamp of the last competitor scan."""
        try:
            if not self.l1.client:
                return None
            raw = await self.l1.client.get(f"{self.prefix}last_competitor_scan")
            if raw:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                return datetime.fromisoformat(raw)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve last competitor scan from L1: {e}")
            return None

    async def update_last_competitor_scan(self, timestamp: datetime):
        """Updates the timestamp of the last competitor scan."""
        try:
            if not self.l1.client:
                return
            serialized = timestamp.isoformat()
            await self.l1.client.set(f"{self.prefix}last_competitor_scan", serialized)
            logger.info(f"Last competitor scan updated to {timestamp}.")
        except Exception as e:
            logger.error(f"Failed to update last competitor scan in L1: {e}")
