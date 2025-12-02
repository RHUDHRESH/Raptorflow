# Migration Guide: Converting Agents to Memory-Enhanced Base Classes

This guide explains how to migrate existing RaptorFlow agents from `BaseAgent` to `BaseAgentEnhanced` to leverage the new memory system.

## Table of Contents

1. [Overview](#overview)
2. [Benefits of Memory-Enhanced Agents](#benefits)
3. [Migration Steps](#migration-steps)
4. [Complete Example: ICP Builder Agent](#complete-example)
5. [Supervisor Migration](#supervisor-migration)
6. [Testing Your Migration](#testing)
7. [Common Pitfalls](#common-pitfalls)

---

## Overview

The new `BaseAgentEnhanced` class extends `BaseAgent` with memory capabilities:

- **Automatic memory recall**: Agents automatically search for relevant past experiences before executing
- **Context enrichment**: Input context is enriched with recalled memories and user preferences
- **Performance tracking**: Execution metrics are automatically stored for analysis
- **Feedback learning**: Agents can learn from user feedback over time

### Key Changes

| Feature | BaseAgent | BaseAgentEnhanced |
|---------|-----------|-------------------|
| execute() method | Implements directly | Calls _execute_core() |
| Memory integration | Manual | Automatic |
| Performance tracking | Manual | Automatic |
| User preferences | Not supported | Automatic |
| Feedback loop | Not supported | Built-in |

---

## Benefits

1. **Learn from past executions**: Agents recall similar past tasks and improve based on what worked
2. **User preference awareness**: Automatically apply user preferences (tone, length, style)
3. **Performance insights**: Track execution times, quality scores, and user ratings over time
4. **Reduce redundant work**: Reuse successful patterns from memory
5. **Continuous improvement**: Learn from user feedback without code changes

---

## Migration Steps

### Step 1: Update Imports

**Before:**
```python
from backend.agents.base_agent import BaseAgent
```

**After:**
```python
from backend.agents.base_enhanced import BaseAgentEnhanced
from backend.memory.manager import MemoryManager
```

### Step 2: Update Class Declaration

**Before:**
```python
class ICPBuilderAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ICPBuilderAgent")
```

**After:**
```python
class ICPBuilderAgent(BaseAgentEnhanced):
    def __init__(self, memory: MemoryManager):
        super().__init__(name="ICPBuilderAgent", memory=memory)
```

### Step 3: Rename execute() to _execute_core()

**Before:**
```python
async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    # Agent logic here
    result = await self._build_icp(payload)
    return {
        "agent": self.name,
        "output": result
    }
```

**After:**
```python
async def _execute_core(self, enriched_context: Dict[str, Any]) -> Dict[str, Any]:
    # Agent logic here (use enriched_context instead of payload)
    result = await self._build_icp(enriched_context)
    return result  # Just return the result, metadata is added automatically
```

### Step 4: Implement Required Abstract Methods

Add these three required methods:

```python
def _get_task_type(self) -> str:
    """Return task type identifier for memory categorization."""
    return "icp_building"

def _create_input_summary(self, payload: Dict[str, Any]) -> str:
    """Create brief summary of input for memory search."""
    company = payload.get("company_name", "unknown")
    industry = payload.get("industry", "unknown")
    return f"Build ICP for {company} in {industry} industry"

def _create_output_summary(self, result: Dict[str, Any]) -> str:
    """Create brief summary of output for memory storage."""
    icp_name = result.get("icp_name", "Unknown")
    confidence = result.get("confidence", 0)
    return f"Created ICP '{icp_name}' with {confidence:.0%} confidence"
```

### Step 5: Access Enriched Context

The `enriched_context` parameter contains:

- **Original payload**: Access via `enriched_context["original_payload"]` or directly (all original fields are present)
- **Recalled memories**: `enriched_context["recalled_memories"]` (list of MemoryEntry objects)
- **Memory summaries**: `enriched_context["memory_summaries"]` (simplified summaries)
- **User preferences**: `enriched_context["user_preferences"]` (user preference dictionary)
- **Feedback stats**: `enriched_context["average_user_rating"]`, `enriched_context["total_feedback_count"]`

Example usage:

```python
async def _execute_core(self, enriched_context: Dict[str, Any]) -> Dict[str, Any]:
    # Access original input
    company_name = enriched_context.get("company_name", "")

    # Check user preferences
    user_prefs = enriched_context.get("user_preferences", {})
    preferred_tone = user_prefs.get("preferred_tone", "professional")

    # Review past successful ICPs
    memory_summaries = enriched_context.get("memory_summaries", [])
    if memory_summaries:
        self.log(f"Found {len(memory_summaries)} similar past ICPs")
        # Use patterns from successful past executions

    # Execute with enriched context
    result = await self._build_icp(enriched_context, tone=preferred_tone)
    return result
```

### Step 6: Update Agent Instantiation

**Before:**
```python
# In supervisor or router
icp_builder_agent = ICPBuilderAgent()
```

**After:**
```python
# Create memory manager (typically in main.py or supervisor)
memory = MemoryManager(workspace_id="ws_123", user_id="u_456")

# Pass to agent
icp_builder_agent = ICPBuilderAgent(memory=memory)
```

---

## Complete Example: ICP Builder Agent

### Before (BaseAgent)

```python
from backend.agents.base_agent import BaseAgent

class ICPBuilderAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ICPBuilderAgent")

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.log(f"Building ICP for company: {payload.get('company_name')}")

        company_name = payload.get("company_name", "")
        industry = payload.get("industry", "")
        product_description = payload.get("product_description", "")

        # Validate input
        if not company_name or not product_description:
            raise ValueError("Missing required fields")

        # Build ICP
        result = await self._build_icp(company_name, industry, product_description)

        return {
            "agent": self.name,
            "output": result
        }

    async def _build_icp(self, company_name, industry, product_description):
        # ICP building logic
        return {"icp_name": "...", "confidence": 0.85}
```

### After (BaseAgentEnhanced)

```python
from backend.agents.base_enhanced import BaseAgentEnhanced
from backend.memory.manager import MemoryManager

class ICPBuilderAgent(BaseAgentEnhanced):
    def __init__(self, memory: MemoryManager):
        super().__init__(name="ICPBuilderAgent", memory=memory)

    async def _execute_core(self, enriched_context: Dict[str, Any]) -> Dict[str, Any]:
        """Core ICP building logic with memory-enriched context."""
        self.log(f"Building ICP for company: {enriched_context.get('company_name')}")

        # Access original input
        company_name = enriched_context.get("company_name", "")
        industry = enriched_context.get("industry", "")
        product_description = enriched_context.get("product_description", "")

        # Validate input
        if not company_name or not product_description:
            raise ValueError("Missing required fields")

        # Use user preferences if available
        user_prefs = enriched_context.get("user_preferences", {})
        avg_rating = enriched_context.get("average_user_rating", 0)

        # Learn from past successful ICPs
        memory_summaries = enriched_context.get("memory_summaries", [])
        successful_patterns = [
            m for m in memory_summaries
            if m.get("user_feedback", {}).get("rating", 0) >= 4
        ]

        self.log(f"Found {len(successful_patterns)} highly-rated past ICPs")

        # Build ICP (potentially using insights from memory)
        result = await self._build_icp(
            company_name,
            industry,
            product_description,
            successful_patterns=successful_patterns
        )

        return result  # Memory storage happens automatically

    def _get_task_type(self) -> str:
        return "icp_building"

    def _create_input_summary(self, payload: Dict[str, Any]) -> str:
        company = payload.get("company_name", "unknown")
        industry = payload.get("industry", "unknown")
        return f"Build ICP for {company} in {industry} industry"

    def _create_output_summary(self, result: Dict[str, Any]) -> str:
        icp_name = result.get("icp_name", "Unknown")
        confidence = result.get("confidence", 0)
        return f"Created ICP '{icp_name}' with {confidence:.0%} confidence"

    async def _build_icp(self, company_name, industry, product_description, successful_patterns=None):
        # ICP building logic (can now use successful_patterns)
        return {"icp_name": "...", "confidence": 0.85}
```

### Key Differences

1. **Constructor**: Now accepts `MemoryManager`
2. **execute() → _execute_core()**: Method renamed and signature changed
3. **Return value**: Return just the result, not wrapped in `{"agent": ..., "output": ...}`
4. **Context parameter**: Use `enriched_context` instead of `payload`
5. **New methods**: Added `_get_task_type()`, `_create_input_summary()`, `_create_output_summary()`
6. **Memory usage**: Can now access past experiences and user preferences

---

## Supervisor Migration

Supervisors should also be migrated to `BaseSupervisorEnhanced` to pass memory context to sub-agents.

### Before (BaseSupervisor)

```python
from backend.agents.base_agent import BaseSupervisor

class ContentSupervisor(BaseSupervisor):
    def __init__(self):
        super().__init__(name="content_supervisor")

        # Register sub-agents
        self.register_agent("blog_writer", BlogWriterAgent())
        self.register_agent("email_writer", EmailWriterAgent())

    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if "blog" in goal:
            return await self.sub_agents["blog_writer"].execute(context)
        elif "email" in goal:
            return await self.sub_agents["email_writer"].execute(context)
```

### After (BaseSupervisorEnhanced)

```python
from backend.agents.supervisor_enhanced import BaseSupervisorEnhanced
from backend.memory.manager import MemoryManager

class ContentSupervisor(BaseSupervisorEnhanced):
    def __init__(self, memory: MemoryManager):
        super().__init__(name="content_supervisor", memory=memory)

        # Register enhanced sub-agents (they share the same memory)
        self.register_enhanced_agent("blog_writer", BlogWriterAgent(memory))
        self.register_enhanced_agent("email_writer", EmailWriterAgent(memory))

    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if "blog" in goal:
            # Use invoke_agent helper for automatic tracking
            return await self.invoke_agent("blog_writer", context)
        elif "email" in goal:
            return await self.invoke_agent("email_writer", context)

        # Or invoke multiple agents in parallel
        # results = await self.invoke_agents_parallel([
        #     {"agent_name": "blog_writer", "payload": context},
        #     {"agent_name": "email_writer", "payload": context}
        # ])
```

### Supervisor Benefits

1. **Shared memory**: All sub-agents can learn from each other's experiences
2. **Workflow tracking**: Supervisor stores multi-agent workflow patterns
3. **Helper methods**: `invoke_agent()`, `invoke_agents_parallel()`, `invoke_agents_sequential()`
4. **Performance insights**: Track which agents are most invoked and successful

---

## Testing Your Migration

### Unit Test Example

Create a test file (e.g., `backend/tests/agents/test_icp_builder_enhanced.py`):

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.agents.research.icp_builder_agent import ICPBuilderAgent
from backend.memory.manager import MemoryManager

@pytest.fixture
def mock_memory():
    """Create a mock MemoryManager for testing."""
    memory = MagicMock(spec=MemoryManager)
    memory.workspace_id = "test_workspace"
    memory.user_id = "test_user"

    # Mock search to return empty list (no memories)
    memory.search = AsyncMock(return_value=[])

    # Mock remember to return a memory ID
    memory.remember = AsyncMock(return_value="mem_test_123")

    # Mock get_user_preferences to return empty prefs
    memory.get_user_preferences = AsyncMock(return_value={
        "total_feedback_count": 0,
        "average_rating": 0.0
    })

    return memory

@pytest.mark.asyncio
async def test_icp_builder_calls_memory_search(mock_memory):
    """Test that ICPBuilderAgent searches memory before executing."""
    agent = ICPBuilderAgent(memory=mock_memory)

    payload = {
        "company_name": "TestCorp",
        "industry": "SaaS",
        "product_description": "AI-powered analytics"
    }

    result = await agent.execute(payload)

    # Verify memory.search() was called
    assert mock_memory.search.called
    assert result["status"] == "success"

@pytest.mark.asyncio
async def test_icp_builder_stores_result(mock_memory):
    """Test that ICPBuilderAgent stores result in memory."""
    agent = ICPBuilderAgent(memory=mock_memory)

    payload = {
        "company_name": "TestCorp",
        "industry": "SaaS",
        "product_description": "AI-powered analytics"
    }

    result = await agent.execute(payload)

    # Verify memory.remember() was called
    assert mock_memory.remember.called

    # Check that memory_id is in metadata
    assert "memory_id" in result["metadata"]
    assert result["metadata"]["memory_id"] == "mem_test_123"

@pytest.mark.asyncio
async def test_feedback_learning(mock_memory):
    """Test that agent can process user feedback."""
    agent = ICPBuilderAgent(memory=mock_memory)

    mock_memory.add_feedback = AsyncMock(return_value=True)

    feedback = {
        "rating": 4,
        "comments": "Good ICP but needs more pain points",
        "helpful": True
    }

    result = await agent.learn_from_feedback("mem_123", feedback)

    assert result["status"] == "success"
    assert mock_memory.add_feedback.called
```

### Integration Test Example

```python
@pytest.mark.asyncio
async def test_icp_builder_with_real_memory():
    """Integration test with real MemoryManager (in-memory storage)."""
    memory = MemoryManager(workspace_id="test_ws", user_id="test_user")
    agent = ICPBuilderAgent(memory=memory)

    # First execution (no memories)
    payload1 = {
        "company_name": "TestCorp",
        "industry": "SaaS",
        "product_description": "AI analytics"
    }

    result1 = await agent.execute(payload1)
    assert result1["status"] == "success"

    # Second execution (should recall first execution)
    payload2 = {
        "company_name": "TestCorp2",
        "industry": "SaaS",  # Same industry
        "product_description": "AI reporting"
    }

    result2 = await agent.execute(payload2)
    assert result2["status"] == "success"
    assert result2["metadata"]["recalled_memory_count"] >= 1  # Should recall first execution
```

---

## Common Pitfalls

### ❌ Pitfall 1: Not passing MemoryManager to constructor

**Wrong:**
```python
agent = ICPBuilderAgent()  # Missing memory parameter
```

**Correct:**
```python
memory = MemoryManager(workspace_id="ws_123")
agent = ICPBuilderAgent(memory=memory)
```

### ❌ Pitfall 2: Returning wrapped result from _execute_core()

**Wrong:**
```python
async def _execute_core(self, enriched_context):
    result = {"icp_name": "..."}
    return {"agent": self.name, "output": result}  # Don't wrap!
```

**Correct:**
```python
async def _execute_core(self, enriched_context):
    result = {"icp_name": "..."}
    return result  # Just return the result
```

### ❌ Pitfall 3: Accessing payload instead of enriched_context

**Wrong:**
```python
async def _execute_core(self, enriched_context):
    company = payload.get("company_name")  # payload is not defined!
```

**Correct:**
```python
async def _execute_core(self, enriched_context):
    company = enriched_context.get("company_name")  # Use enriched_context
    # Or access original payload explicitly:
    # company = enriched_context["original_payload"]["company_name"]
```

### ❌ Pitfall 4: Forgetting to implement abstract methods

**Wrong:**
```python
class ICPBuilderAgent(BaseAgentEnhanced):
    async def _execute_core(self, enriched_context):
        # ... only implements _execute_core
```

**Correct:**
```python
class ICPBuilderAgent(BaseAgentEnhanced):
    async def _execute_core(self, enriched_context):
        # ...

    def _get_task_type(self) -> str:
        return "icp_building"

    def _create_input_summary(self, payload) -> str:
        return f"Build ICP for {payload.get('company_name')}"

    def _create_output_summary(self, result) -> str:
        return f"Created {result.get('icp_name')}"
```

### ❌ Pitfall 5: Not using shared memory in supervisors

**Wrong:**
```python
class ContentSupervisor(BaseSupervisorEnhanced):
    def __init__(self, memory: MemoryManager):
        super().__init__("content_supervisor", memory)

        # Creating separate memory for each agent - they won't share learnings!
        blog_memory = MemoryManager(workspace_id="ws_123")
        email_memory = MemoryManager(workspace_id="ws_123")

        self.register_enhanced_agent("blog_writer", BlogWriter(blog_memory))
        self.register_enhanced_agent("email_writer", EmailWriter(email_memory))
```

**Correct:**
```python
class ContentSupervisor(BaseSupervisorEnhanced):
    def __init__(self, memory: MemoryManager):
        super().__init__("content_supervisor", memory)

        # Use shared memory so agents can learn from each other
        self.register_enhanced_agent("blog_writer", BlogWriter(memory))
        self.register_enhanced_agent("email_writer", EmailWriter(memory))
```

---

## Next Steps

1. **Migrate one agent at a time**: Start with a simple agent (e.g., `icp_builder_agent.py`)
2. **Write tests**: Ensure your migration works correctly
3. **Monitor performance**: Check that memory search and storage work as expected
4. **Iterate**: Gradually migrate more agents and supervisors
5. **Collect feedback**: Use `learn_from_feedback()` to continuously improve

For questions or issues, refer to:
- `backend/agents/base_enhanced.py` - Enhanced agent implementation
- `backend/agents/supervisor_enhanced.py` - Enhanced supervisor implementation
- `backend/memory/manager.py` - MemoryManager API reference
- `backend/tests/agents/test_base_enhanced.py` - Comprehensive test examples
