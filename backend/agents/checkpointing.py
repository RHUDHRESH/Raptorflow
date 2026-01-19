"""
Redis-based checkpoint saver for LangGraph workflows.
Provides persistent storage of workflow state with TTL management.
"""

    def __init__(self, redis_client=None, ttl_hours: int = 24):
        self.ttl_seconds = ttl_hours * 3600
        if redis_client:
            self.redis = redis_client
        else:
            config = get_config()
            import redis
            self.redis = redis.from_url(
                config.UPSTASH_REDIS_URL,
                password=config.UPSTASH_REDIS_TOKEN,
                decode_responses=False,
            )

    def _make_key(self, thread_id: str, checkpoint_ns: str = "") -> str:
        if checkpoint_ns:
            return f"checkpoint:{checkpoint_ns}:{thread_id}"
        return f"checkpoint:{thread_id}"

    def _serialize_checkpoint(self, checkpoint: Checkpoint) -> bytes:
        return pickle.dumps(checkpoint)

    def _deserialize_checkpoint(self, data: bytes) -> Checkpoint:
        return pickle.loads(data)

    async def save_checkpoint(
        self,
        checkpoint: Checkpoint,
        config: RunnableConfig,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        try:
            thread_id = config.get("configurable", {}).get("thread_id")
            checkpoint_ns = config.get("configurable", {}).get("checkpoint_ns", "")
            if not thread_id:
                raise ValueError("thread_id must be provided in config")
            key = self._make_key(thread_id, checkpoint_ns)
            checkpoint_data = {
                "checkpoint": self._serialize_checkpoint(checkpoint),
                "config": json.dumps(config),
                "metadata": json.dumps(metadata or {)},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
            }
            await self.redis.hset(key, mapping=checkpoint_data)
            await self.redis.expire(key, self.ttl_seconds)
        except Exception as e:
            raise RuntimeError(f"Failed to save checkpoint: {str(e)}")

    async def get_checkpoint(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        try:
            thread_id = config.get("configurable", {}).get("thread_id")
            checkpoint_ns = config.get("configurable", {}).get("checkpoint_ns", "")
            if not thread_id:
                return None
            key = self._make_key(thread_id, checkpoint_ns)
            data = await self.redis.hgetall(key)
            if not data:
                return None
            checkpoint = self._deserialize_checkpoint(data.get(b"checkpoint") or data.get("checkpoint"))
            saved_config = json.loads(data.get(b"config") or data.get("config"))
            metadata = json.loads(data.get(b"metadata") or data.get("metadata"))
            return CheckpointTuple(config=saved_config, checkpoint=checkpoint, metadata=metadata)
        except Exception as e:
            raise RuntimeError(f"Failed to get checkpoint: {str(e)}")

    async def list_checkpoints(self, config: RunnableConfig, *, filter: dict = None, before: dict = None, limit: int = None):
        return []

class SupabaseCheckpointer(BaseCheckpointSaver):
    """
    Supabase-based checkpoint saver for LangGraph workflows.
    Consolidates state in the primary industrial database.
    """

    def __init__(self, client=None):
        self.client = client or get_supabase_client()
        self.table_name = "agent_checkpoints"

    async def save_checkpoint(
        self,
        checkpoint: Checkpoint,
        config: RunnableConfig,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        thread_id = config.get("configurable", {}).get("thread_id")
        checkpoint_ns = config.get("configurable", {}).get("checkpoint_ns", "")
        workspace_id = config.get("configurable", {}).get("workspace_id", "system")

        if not thread_id:
            raise ValueError("thread_id must be provided")

        payload = {
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
            "workspace_id": workspace_id,
            "checkpoint": checkpoint,
            "metadata": metadata or {},
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        try:
            self.client.table(self.table_name).upsert(payload, on_conflict="thread_id,checkpoint_ns").execute()
        except Exception as e:
            logger.error(f"SupabaseCheckpointer: Failed to save: {e}")

    async def get_checkpoint(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = config.get("configurable", {}).get("thread_id")
        checkpoint_ns = config.get("configurable", {}).get("checkpoint_ns", "")

        if not thread_id:
            return None

        try:
            result = self.client.table(self.table_name) \
                .select("*") \
                .eq("thread_id", thread_id) \
                .eq("checkpoint_ns", checkpoint_ns) \
                .maybe_single() \
                .execute()

            if not result.data:
                return None

            data = result.data
            return CheckpointTuple(
                config=config,
                checkpoint=data["checkpoint"],
                metadata=data["metadata"]
            )
        except Exception as e:
            logger.error(f"SupabaseCheckpointer: Failed to get: {e}")
            return None

    async def list_checkpoints(self, config: RunnableConfig, *, filter: dict = None, before: dict = None, limit: int = None):
        return []

class WorkspaceCheckpointer(RedisCheckpointer):
    """
    Workspace-specific checkpointer with enhanced isolation.
    """

    def __init__(self, workspace_id: str, redis_client=None, ttl_hours: int = 24):
        super().__init__(redis_client, ttl_hours)
        self.workspace_id = workspace_id

    def _make_key(self, thread_id: str, checkpoint_ns: str = "") -> str:
        base_key = super()._make_key(thread_id, checkpoint_ns)
        return f"workspace:{self.workspace_id}:{base_key}"

    async def save_checkpoint(
        self,
        checkpoint: Checkpoint,
        config: RunnableConfig,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        if metadata is None:
            metadata = {}
        metadata["workspace_id"] = self.workspace_id
        await super().save_checkpoint(checkpoint, config, metadata)

# Factory functions
def create_redis_checkpointer(workspace_id: Optional[str] = None, ttl_hours: int = 24) -> BaseCheckpointSaver:
    if workspace_id:
        return WorkspaceCheckpointer(workspace_id, ttl_hours=ttl_hours)
    return RedisCheckpointer(ttl_hours=ttl_hours)

def create_supabase_checkpointer() -> BaseCheckpointSaver:
    return SupabaseCheckpointer()

def create_memory_checkpointer() -> BaseCheckpointSaver:
    from langchain_core.checkpoint.memory import MemorySaver
    return MemorySaver()