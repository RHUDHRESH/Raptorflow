# RAPTORFLOW AGENT SWARM - COMPLETE IMPLEMENTATION PLAN

**Document Version**: 1.0
**Date**: 2025-01-25
**Status**: Implementation Blueprint

---

## EXECUTIVE SUMMARY

RaptorFlow currently has:
- ✅ **33+ agents** across 6 domain supervisors
- ✅ **LangGraph orchestration** with 8 workflow graphs
- ✅ **Comprehensive database schema** with pgvector for semantic memory
- ✅ **Production-ready backend** (FastAPI + Redis + Supabase)

**Critical Gap**: The architecture is **hierarchical** (supervisor-worker), not a true **collaborative swarm**. Agents communicate only through supervisors, not peer-to-peer.

This plan transforms RaptorFlow into a **full event-driven multi-agent swarm** with:
- Real-time agent collaboration
- Parallel execution
- Self-improving loops
- Dynamic agent spawning
- Consensus mechanisms

---

## TABLE OF CONTENTS

1. [Current vs. Target Architecture](#1-current-vs-target-architecture)
2. [Agent Mapping: Existing → Swarm Topology](#2-agent-mapping)
3. [New Infrastructure Required](#3-new-infrastructure-required)
4. [Agent Communication Protocols](#4-agent-communication-protocols)
5. [New Agents to Build](#5-new-agents-to-build)
6. [Database Schema Extensions](#6-database-schema-extensions)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Code Examples & Scaffolding](#8-code-examples)

---

## 1. CURRENT VS. TARGET ARCHITECTURE

### Current Architecture (Hierarchical)

```
Master Orchestrator
    ├── Onboarding Supervisor
    │   ├── Profile Builder
    │   └── Questionnaire Engine
    ├── Customer Intelligence Supervisor
    │   ├── ICP Builder
    │   ├── Psychographic Profiler
    │   ├── Pain Point Miner
    │   └── Tag Assignment
    ├── Strategy Supervisor
    │   ├── Campaign Planner
    │   ├── Market Research
    │   └── Ambient Search
    ├── Content Supervisor
    │   ├── Hook Generator
    │   ├── Blog/Email/Social Writers
    │   ├── Meme/Carousel Agents
    │   └── Brand Voice
    ├── Execution Supervisor
    │   ├── Scheduler
    │   ├── Email Agent (stub)
    │   ├── Canva Agent
    │   └── Publisher Agents (stubs)
    └── Analytics Supervisor
        ├── Metrics Collector
        ├── Insight Agent
        └── Campaign Review
```

**Communication Flow**: Request → Master → Supervisor → Specialist → Supervisor → Master → Response

**Limitations**:
- No parallel cross-domain collaboration (Strategy + Content can't talk directly)
- No agent-to-agent learning
- No dynamic consensus
- Single point of failure (supervisor bottleneck)

---

### Target Architecture (Swarm Mesh)

```
                    APEX CORTEX (Master Orchestrator)
                            |
        ┌───────────────────┴───────────────────┐
        |                                       |
   POLICY ARBITER                      EVENT BUS (Redis Pub/Sub)
        |                                       |
   ┌────┴────┬────────┬────────┬───────────────┴────┐
   |         |        |        |                     |
STRATEGY  CREATION SIGNALS  BRAND/RISK        COHORT INTELLIGENCE
DIRECTOR  DIRECTOR DIRECTOR  DIRECTOR           MESH
   |         |        |        |                     |
   v         v        v        v                     v
┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐             ┌─────┐
│Move │  │Muse │  │Optri│  │Fire │             │Psych│
│Arch │  │Forge│  │Matrix│ │wall │             │eLens│
└─────┘  └─────┘  └─────┘  └─────┘             └─────┘
   |         |        |        |                     |
┌──┴──┐  ┌──┴──┐  ┌──┴──┐  ┌──┴──┐             ┌──┴──┐
│Split│  │Lyra │  │Pulse│  │Crisis│            │Mirror│
│Mind │  │Quill│  │Seer │  │Maven│             │Scout│
└─────┘  └─────┘  └─────┘  └─────┘             └─────┘
   |         |        |        |                     |
   └─────────┴────────┴────────┴─────────────────────┘
                      |
              SHARED MEMORY LAYER
              (PostgreSQL + pgvector + Redis)
```

**Communication Flow**:
- Event-driven: Agents subscribe to topics
- Peer-to-peer: Agents message each other directly
- Consensus: Multi-agent debate orchestrator
- Parallel: Multiple agents work simultaneously

---

## 2. AGENT MAPPING

### Mapping Existing Agents to Swarm Pods

| **Swarm Pod** | **Swarm Agent** | **Existing Agent** | **Status** | **Gaps** |
|---------------|-----------------|--------------------|-----------:|----------|
| **STRATEGY POD** | | | | |
| | MoveArchitect | Campaign Planner | ✅ 90% | Needs event bus integration |
| | PsycheLens | Psychographic Profiler + ICP Builder | ✅ 95% | Needs real-time cohort drift detection |
| | SplitMind | *NEW* | ❌ 0% | A/B test design agent missing |
| **CREATION POD** | | | | |
| | MuseForge | Hook Generator + Brand Voice | ✅ 80% | Needs multi-channel ideation |
| | LyraQuill | Blog/Email/Social Writers | ✅ 90% | Needs critique integration |
| | NoirFrame | *NEW* | ❌ 0% | Visual design direction missing |
| | PortaMorph | *NEW* | ❌ 0% | Cross-platform adaptation missing |
| **SIGNALS POD** | | | | |
| | OptiMatrix | Analytics Agent + Insight Agent | ✅ 70% | Needs pattern library |
| | PulseSeer | *NEW* | ❌ 0% | Trend detection missing |
| | MirrorScout | *NEW* | ❌ 0% | Competitor analysis missing |
| **BRAND/RISK POD** | | | | |
| | FirewallMaven | Critic Agent + Guardian Agent | ✅ 85% | Needs crisis monitoring |
| **EXECUTIVE MESH** | | | | |
| | Apex Cortex | Master Orchestrator | ✅ 95% | Needs policy arbiter separation |
| | Policy Arbiter | *NEW* | ❌ 0% | Conflict resolution missing |

### Agents Currently Missing (6 NEW Agents)

1. **SplitMind** (EXP-01) - A/B Test Design & Interpretation
2. **NoirFrame** (VIS-01) - Visual Design Direction
3. **PortaMorph** (ADAPT-01) - Cross-Platform Content Adaptation
4. **PulseSeer** (TREND-01) - Trend Detection & Prediction
5. **MirrorScout** (COMP-01) - Competitor Analysis
6. **Policy Arbiter** (PA) - Multi-Agent Conflict Resolution

---

## 3. NEW INFRASTRUCTURE REQUIRED

### 3.1 Event Bus Layer (CRITICAL)

**Current**: Redis message queue (basic pub/sub)
**Target**: Full event-driven architecture with typed events

**Implementation**:

```python
# backend/messaging/event_bus.py

from typing import TypedDict, Literal, List, Dict, Any
from redis import Redis
from pydantic import BaseModel
import json
from datetime import datetime

class EventType:
    GOAL_REQUEST = "goal.request"
    MOVE_PLAN = "move.plan"
    CONTENT_BRIEF = "content.brief"
    DRAFT_ASSET = "content.draft"
    PERFORMANCE_UPDATE = "metrics.update"
    TREND_ALERT = "trend.alert"
    RISK_ALERT = "risk.alert"
    EXPERIMENT_DESIGN = "experiment.design"
    EXPERIMENT_RESULT = "experiment.result"
    CRISIS_INCIDENT = "crisis.incident"
    POLICY_DECISION = "policy.decision"
    COHORT_DRIFT = "cohort.drift"

class AgentMessage(BaseModel):
    id: str
    type: str  # EventType
    origin: str  # agent_id
    targets: List[str]  # agent_ids
    payload: Dict[str, Any]
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    correlation_id: str  # move_id, campaign_id, etc.
    timestamp: datetime
    ttl: int = 3600  # seconds

class EventBus:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def publish(self, message: AgentMessage):
        """Publish message to all targets"""
        for target in message.targets:
            channel = f"agent.{target}"
            self.redis.publish(
                channel,
                message.model_dump_json()
            )

        # Also publish to event log for audit
        self.redis.zadd(
            f"events:{message.correlation_id}",
            {message.model_dump_json(): message.timestamp.timestamp()}
        )

    def subscribe(self, agent_id: str, callback):
        """Subscribe to messages for this agent"""
        pubsub = self.redis.pubsub()
        pubsub.subscribe(f"agent.{agent_id}")

        for message in pubsub.listen():
            if message['type'] == 'message':
                msg = AgentMessage.model_validate_json(message['data'])
                callback(msg)

    def broadcast(self, message: AgentMessage):
        """Broadcast to all agents (for system-wide events)"""
        self.redis.publish("agent.*", message.model_dump_json())
```

**Usage**:
```python
# In any agent
event_bus = EventBus(redis_client)

# Publish
message = AgentMessage(
    id=str(uuid4()),
    type=EventType.CONTENT_BRIEF,
    origin="IDEA-01",
    targets=["COPY-01", "VIS-01"],
    payload={"brief_id": "123", "cohort_id": "456"},
    priority="HIGH",
    correlation_id="move-789"
)
event_bus.publish(message)

# Subscribe
def handle_message(msg: AgentMessage):
    if msg.type == EventType.CONTENT_BRIEF:
        # Generate content
        pass

event_bus.subscribe("COPY-01", handle_message)
```

---

### 3.2 Shared Context Bus

**Purpose**: Real-time shared state for multi-agent collaboration

```python
# backend/messaging/context_bus.py

class ContextBus:
    """Shared scratchpad for agents working on the same task"""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def set_context(self, correlation_id: str, key: str, value: Any, ttl: int = 3600):
        """Set a context variable"""
        ctx_key = f"context:{correlation_id}:{key}"
        self.redis.setex(ctx_key, ttl, json.dumps(value))

    def get_context(self, correlation_id: str, key: str) -> Any:
        """Get a context variable"""
        ctx_key = f"context:{correlation_id}:{key}"
        val = self.redis.get(ctx_key)
        return json.loads(val) if val else None

    def get_all_context(self, correlation_id: str) -> Dict[str, Any]:
        """Get entire context for a task"""
        pattern = f"context:{correlation_id}:*"
        keys = self.redis.keys(pattern)
        context = {}
        for key in keys:
            field = key.decode().split(":")[-1]
            context[field] = json.loads(self.redis.get(key))
        return context

    def lock(self, correlation_id: str, resource: str, agent_id: str, ttl: int = 60):
        """Lock a resource for exclusive access"""
        lock_key = f"lock:{correlation_id}:{resource}"
        return self.redis.set(lock_key, agent_id, nx=True, ex=ttl)

    def unlock(self, correlation_id: str, resource: str):
        """Release a lock"""
        lock_key = f"lock:{correlation_id}:{resource}"
        self.redis.delete(lock_key)
```

**Usage**:
```python
# MoveArchitect sets initial context
ctx_bus.set_context("move-789", "strategy_phase", "planning")
ctx_bus.set_context("move-789", "target_cohorts", ["cohort-A", "cohort-B"])

# MuseForge reads context
cohorts = ctx_bus.get_context("move-789", "target_cohorts")

# LyraQuill locks resource while writing
if ctx_bus.lock("move-789", "email_draft", "COPY-01"):
    # Write draft
    ctx_bus.set_context("move-789", "email_draft", draft_content)
    ctx_bus.unlock("move-789", "email_draft")
```

---

### 3.3 Agent Registry & Discovery

**Purpose**: Agents advertise capabilities, tasks discover agents

```python
# backend/messaging/agent_registry.py

class AgentCapability(BaseModel):
    agent_id: str
    agent_name: str
    capabilities: List[str]  # ["content_generation", "social_linkedin", "tone_professional"]
    load: int  # Current number of active tasks
    max_concurrent: int
    avg_latency_ms: float
    success_rate: float
    last_heartbeat: datetime

class AgentRegistry:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def register(self, capability: AgentCapability):
        """Register agent capabilities"""
        key = f"agent:{capability.agent_id}"
        self.redis.setex(key, 120, capability.model_dump_json())  # 2min TTL, must heartbeat

        # Index by capability
        for cap in capability.capabilities:
            self.redis.sadd(f"capability:{cap}", capability.agent_id)

    def find_agents(self, required_capabilities: List[str]) -> List[AgentCapability]:
        """Find agents matching all required capabilities"""
        sets = [f"capability:{cap}" for cap in required_capabilities]

        if not sets:
            return []

        # Intersection of sets
        agent_ids = self.redis.sinter(*sets)

        agents = []
        for agent_id in agent_ids:
            data = self.redis.get(f"agent:{agent_id.decode()}")
            if data:
                agents.append(AgentCapability.model_validate_json(data))

        # Sort by load (least busy first) and success rate
        agents.sort(key=lambda a: (a.load / a.max_concurrent, -a.success_rate))
        return agents

    def update_load(self, agent_id: str, delta: int):
        """Update agent's current load"""
        data = self.redis.get(f"agent:{agent_id}")
        if data:
            cap = AgentCapability.model_validate_json(data)
            cap.load += delta
            cap.last_heartbeat = datetime.utcnow()
            self.redis.setex(f"agent:{agent_id}", 120, cap.model_dump_json())
```

**Usage**:
```python
# Agent startup
registry = AgentRegistry(redis_client)
registry.register(AgentCapability(
    agent_id="COPY-01",
    agent_name="LyraQuill",
    capabilities=["content_generation", "copywriting", "email", "linkedin", "tone_professional"],
    load=0,
    max_concurrent=5,
    avg_latency_ms=2500,
    success_rate=0.94
))

# Task needs an agent
agents = registry.find_agents(["content_generation", "email", "tone_professional"])
best_agent = agents[0]  # Least loaded agent with required skills
```

---

### 3.4 Consensus Orchestrator

**Purpose**: Multi-agent debate & voting for critical decisions

```python
# backend/agents/consensus/orchestrator.py

class ConsensusOrchestrator:
    """Manages multi-agent debates and consensus decisions"""

    def __init__(self, event_bus: EventBus, context_bus: ContextBus):
        self.event_bus = event_bus
        self.context_bus = context_bus

    async def initiate_debate(
        self,
        topic: str,
        correlation_id: str,
        participants: List[str],  # agent_ids
        question: str,
        context: Dict[str, Any],
        rounds: int = 2,
        voting_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Run a multi-round debate among agents

        Returns:
            {
                "decision": "scale|tweak|kill",
                "confidence": 0.85,
                "votes": {"STRAT-01": "scale", "METRIC-01": "scale"},
                "reasoning": {"STRAT-01": "...", ...}
            }
        """

        # Round 1: Initial positions
        positions = {}
        for agent_id in participants:
            position = await self._get_agent_position(
                agent_id, topic, question, context
            )
            positions[agent_id] = position

        # Round 2+: Debate rounds
        for round_num in range(1, rounds):
            # Share all positions
            self.context_bus.set_context(
                correlation_id,
                f"debate_positions_round_{round_num}",
                positions
            )

            # Agents revise positions after seeing others
            new_positions = {}
            for agent_id in participants:
                revised = await self._revise_position(
                    agent_id, topic, question, context, positions
                )
                new_positions[agent_id] = revised

            positions = new_positions

        # Final vote
        votes = {}
        reasoning = {}
        for agent_id in participants:
            vote = positions[agent_id]["decision"]
            votes[agent_id] = vote
            reasoning[agent_id] = positions[agent_id]["reasoning"]

        # Calculate consensus
        vote_counts = {}
        for vote in votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1

        winner = max(vote_counts, key=vote_counts.get)
        confidence = vote_counts[winner] / len(votes)

        return {
            "decision": winner,
            "confidence": confidence,
            "votes": votes,
            "reasoning": reasoning,
            "consensus_reached": confidence >= voting_threshold
        }

    async def _get_agent_position(
        self,
        agent_id: str,
        topic: str,
        question: str,
        context: Dict[str, Any]
    ):
        # Call agent's LLM with debate prompt
        # Return structured position
        pass

    async def _revise_position(
        self,
        agent_id: str,
        topic: str,
        question: str,
        context: Dict[str, Any],
        other_positions: Dict[str, Any]
    ):
        # Agent sees other positions and revises
        pass
```

---

## 4. AGENT COMMUNICATION PROTOCOLS

### 4.1 Message Types & Schemas

```python
# backend/models/agent_messages.py

from pydantic import BaseModel
from typing import List, Dict, Any, Literal
from datetime import datetime

# Goal Request (User → Apex Cortex)
class GoalRequest(BaseModel):
    goal_type: Literal["reach", "engagement", "conversion", "revenue", "retention", "authority", "insight"]
    description: str
    cohorts: List[str]  # cohort_ids
    timeframe_days: int
    intensity: Literal["light", "standard", "aggressive"]
    constraints: Dict[str, Any] = {}

# Move Plan (Strategy → Creation/Execution)
class MovePlan(BaseModel):
    move_id: str
    name: str
    objective: str
    target_cohorts: List[str]
    channels: List[str]
    kpi_primary: str
    kpi_target: float
    start_date: datetime
    end_date: datetime
    content_needs: List[Dict[str, Any]]  # [{"type": "blog", "topic": "..."}]

# Content Brief (Strategy/Muse → Content Agents)
class ContentBrief(BaseModel):
    brief_id: str
    move_id: str
    cohort_id: str
    channel: str
    format: str  # "blog", "email", "linkedin_post", etc.
    objective: str
    tone_tags: List[str]
    hard_constraints: Dict[str, Any]  # {"max_length": 280, "required_cta": True}
    context: Dict[str, Any]  # Market research, cohort psychographics, etc.

# Draft Asset (Content → Critic → Execution)
class DraftAsset(BaseModel):
    asset_id: str
    brief_id: str
    channel: str
    format: str
    body: str
    metadata: Dict[str, Any]  # Skeleton, hook_type, emotional_tone, etc.
    status: Literal["draft", "under_review", "approved", "rejected"]
    created_by: str  # agent_id

# Performance Update (Metrics → Strategy/Content)
class PerformanceUpdate(BaseModel):
    move_id: str
    asset_id: str | None
    metrics: Dict[str, float]  # {"impressions": 1200, "clicks": 45, "conversions": 3}
    verdict: Literal["winner", "average", "dead"]
    patterns: List[str]  # Detected patterns: ["proof_heavy", "pain_focused"]
    recommendation: str

# Trend Alert (PulseSeer → Strategy/Content)
class TrendAlert(BaseModel):
    trend_id: str
    topic: str
    platforms: List[str]
    velocity: float  # Growth rate
    lifecycle_stage: Literal["emerging", "peak", "declining"]
    relevant_cohorts: List[str]
    opportunity_score: float
    expiry_date: datetime

# Risk Alert (FirewallMaven → Policy Arbiter)
class RiskAlert(BaseModel):
    asset_id: str
    risk_type: Literal["brand_misalignment", "legal", "toxicity", "backlash_potential"]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    details: str
    recommended_action: Literal["approve", "revise", "reject", "escalate"]

# Experiment Design (SplitMind → Execution)
class ExperimentDesign(BaseModel):
    experiment_id: str
    hypothesis: str
    variants: List[Dict[str, Any]]  # [{"variant": "A", "asset_id": "..."}, ...]
    sample_size_per_variant: int
    duration_days: int
    success_metric: str
    stop_conditions: Dict[str, Any]

# Policy Decision (Policy Arbiter → All)
class PolicyDecision(BaseModel):
    decision_id: str
    conflict_id: str
    agents_involved: List[str]
    decision: str  # "approve", "reject", "escalate_human"
    reasoning: str
    overrides: Dict[str, Any]  # Which agent's recommendation was followed
```

---

### 4.2 Communication Patterns

#### Pattern 1: Request-Response
```python
# Agent A requests something from Agent B
event_bus.publish(AgentMessage(
    type=EventType.CONTENT_BRIEF,
    origin="IDEA-01",
    targets=["COPY-01"],
    correlation_id="move-123"
))

# Agent B responds
event_bus.publish(AgentMessage(
    type=EventType.DRAFT_ASSET,
    origin="COPY-01",
    targets=["IDEA-01", "CRISIS-01"],  # Send to requester + critic
    correlation_id="move-123"
))
```

#### Pattern 2: Fan-Out (Parallel Broadcast)
```python
# Apex Cortex fans out to all domain directors
event_bus.publish(AgentMessage(
    type=EventType.GOAL_REQUEST,
    origin="APEX",
    targets=["STRAT-DIR", "CREATION-DIR", "SIGNALS-DIR", "RISK-DIR"],
    correlation_id="move-123"
))
```

#### Pattern 3: Pub/Sub (Interested Parties)
```python
# Any agent can subscribe to performance updates
def handle_performance_update(msg):
    if msg.payload['verdict'] == 'winner':
        # Learn from success
        pass

event_bus.subscribe("METRIC-01", handle_performance_update)
```

#### Pattern 4: Consensus
```python
# Policy Arbiter initiates debate
result = await consensus_orchestrator.initiate_debate(
    topic="Should we scale this Move?",
    participants=["STRAT-01", "METRIC-01", "CRISIS-01"],
    question="Move X shows 2x ROI but rising negative sentiment. Scale, tweak, or kill?",
    context={
        "move_id": "123",
        "metrics": {...},
        "sentiment": {...}
    }
)

if result['consensus_reached']:
    # Execute decision
    pass
else:
    # Escalate to human
    pass
```

---

## 5. NEW AGENTS TO BUILD

### 5.1 SplitMind (EXP-01) - A/B Test Designer

**Purpose**: Design and interpret experiments

**Tools**:
- Read move_metrics, asset_metrics
- Create experiments table entries
- Statistical analysis (Bayesian or frequentist)

**Workflow**:
1. Receive hypothesis from Strategy Director
2. Design variants (what to test: hook, CTA, tone, visual)
3. Calculate sample size needed
4. Set stop conditions (significance, min duration)
5. Monitor results
6. Declare winner when conditions met

**Database Schema**:
```sql
CREATE TABLE experiments (
  id UUID PRIMARY KEY,
  move_id UUID REFERENCES moves(id),
  hypothesis TEXT,
  variants JSONB,  -- [{"variant": "A", "asset_id": "..."}, ...]
  sample_size_per_variant INT,
  duration_days INT,
  success_metric TEXT,
  stop_conditions JSONB,
  status TEXT,  -- "running", "completed", "stopped"
  winner_variant TEXT,
  confidence FLOAT,
  created_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ
);

CREATE TABLE experiment_results (
  id UUID PRIMARY KEY,
  experiment_id UUID REFERENCES experiments(id),
  variant TEXT,
  metric_name TEXT,
  metric_value FLOAT,
  sample_size INT,
  timestamp TIMESTAMPTZ
);
```

**Agent Code Skeleton**:
```python
# backend/agents/strategy/split_mind.py

from backend.agents.base import BaseAgent
from backend.models.agent_messages import ExperimentDesign

class SplitMindAgent(BaseAgent):
    """A/B Test Design & Interpretation Agent"""

    agent_id = "EXP-01"
    agent_name = "SplitMind"

    async def design_experiment(
        self,
        move_id: str,
        hypothesis: str,
        context: Dict[str, Any]
    ) -> ExperimentDesign:
        """
        Design an experiment based on hypothesis

        Example hypothesis: "Proof-heavy hooks outperform question hooks for Founders cohort"
        """

        # Step 1: Determine what to vary
        variants = await self._design_variants(hypothesis, context)

        # Step 2: Calculate sample size
        sample_size = self._calculate_sample_size(
            baseline_rate=context.get('baseline_conversion', 0.05),
            mde=context.get('min_detectable_effect', 0.2),  # 20% lift
            alpha=0.05,
            power=0.8
        )

        # Step 3: Set stop conditions
        stop_conditions = {
            "min_sample": sample_size,
            "min_duration_days": 7,
            "max_duration_days": 28,
            "significance_threshold": 0.05
        }

        # Step 4: Create experiment
        experiment = ExperimentDesign(
            experiment_id=str(uuid4()),
            hypothesis=hypothesis,
            variants=variants,
            sample_size_per_variant=sample_size,
            duration_days=14,
            success_metric=context.get('success_metric', 'conversion_rate'),
            stop_conditions=stop_conditions
        )

        # Step 5: Save to DB
        await self.db.experiments.insert(experiment.model_dump())

        return experiment

    async def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Analyze experiment results and declare winner"""

        # Fetch results
        results = await self.db.experiment_results.filter(experiment_id=experiment_id).all()

        # Group by variant
        variant_stats = self._compute_variant_stats(results)

        # Run statistical test
        winner, confidence = self._bayesian_ab_test(variant_stats)

        # Update experiment
        await self.db.experiments.update(
            experiment_id,
            {
                "status": "completed",
                "winner_variant": winner,
                "confidence": confidence,
                "completed_at": datetime.utcnow()
            }
        )

        return {
            "winner": winner,
            "confidence": confidence,
            "stats": variant_stats
        }

    def _calculate_sample_size(
        self,
        baseline_rate: float,
        mde: float,
        alpha: float,
        power: float
    ) -> int:
        """Calculate required sample size per variant"""
        # Use statsmodels or custom formula
        from statsmodels.stats.power import zt_ind_solve_power

        effect_size = mde  # Simplified
        n = zt_ind_solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            ratio=1.0,
            alternative='two-sided'
        )
        return int(n)

    def _bayesian_ab_test(self, variant_stats: Dict) -> Tuple[str, float]:
        """Run Bayesian A/B test"""
        # Use PyMC or scipy
        # Return winner and probability of being best
        pass
```

---

### 5.2 NoirFrame (VIS-01) - Visual Design Director

**Purpose**: Generate visual design direction (not actual images, but specifications)

**Tools**:
- Brand guidelines DB
- Pattern library (what visuals worked before)
- Canva template IDs
- Image generation prompt templates

**Workflow**:
1. Receive content brief
2. Determine visual style (mood, color palette, composition)
3. Generate specs for designer or Canva API
4. Validate brand compliance

**Agent Code Skeleton**:
```python
# backend/agents/creation/noir_frame.py

class NoirFrameAgent(BaseAgent):
    """Visual Design Direction Agent"""

    agent_id = "VIS-01"
    agent_name = "NoirFrame"

    async def design_visual(
        self,
        brief: ContentBrief,
        cohort: Dict[str, Any],
        brand_guidelines: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate visual design specification

        Returns:
            {
                "mood": "aspirational",
                "color_palette": ["#1E3A8A", "#F59E0B"],
                "composition": "hero_with_text_overlay",
                "elements": ["founder_photo", "proof_metrics", "cta_button"],
                "canva_template_id": "DAFxyz123",
                "image_gen_prompt": "Professional founder in modern office, confident pose...",
                "aspect_ratio": "16:9"
            }
        """

        # Step 1: Determine mood from brief + cohort
        mood = self._infer_mood(brief, cohort)

        # Step 2: Select color palette from brand guidelines
        colors = brand_guidelines['color_palette']

        # Step 3: Choose composition based on channel + format
        composition = self._select_composition(brief.channel, brief.format)

        # Step 4: Generate Canva template recommendation or image prompt
        if brief.format in ["instagram_post", "linkedin_carousel"]:
            canva_template = self._find_canva_template(brief.format, mood)
        else:
            canva_template = None

        image_prompt = self._generate_image_prompt(brief, mood, composition)

        return {
            "mood": mood,
            "color_palette": colors,
            "composition": composition,
            "canva_template_id": canva_template,
            "image_gen_prompt": image_prompt,
            "aspect_ratio": self._get_aspect_ratio(brief.channel, brief.format)
        }

    def _infer_mood(self, brief: ContentBrief, cohort: Dict[str, Any]) -> str:
        """Infer visual mood from tone tags and cohort psychographics"""

        tone_tags = brief.tone_tags
        cohort_tags = cohort.get('tags', [])

        # Mapping: tone + cohort → mood
        mood_map = {
            ("professional", "results_driven"): "aspirational",
            ("empathetic", "problem_aware"): "relatable",
            ("urgent", "time_scarce"): "bold",
            ("educational", "learning_focused"): "clean_minimal"
        }

        # Simple lookup (in production, use LLM)
        for (tone, cohort_tag), mood in mood_map.items():
            if tone in tone_tags and cohort_tag in cohort_tags:
                return mood

        return "neutral"
```

---

### 5.3 PortaMorph (ADAPT-01) - Cross-Platform Adapter

**Purpose**: Adapt content from one platform to another

**Workflow**:
1. Take source content (e.g., blog post)
2. Identify target platform constraints
3. Reformat while preserving core message

**Agent Code Skeleton**:
```python
# backend/agents/creation/porta_morph.py

class PortaMorphAgent(BaseAgent):
    """Cross-Platform Content Adaptation Agent"""

    agent_id = "ADAPT-01"
    agent_name = "PortaMorph"

    async def adapt_content(
        self,
        source_asset: Dict[str, Any],
        target_channel: str,
        target_format: str
    ) -> str:
        """
        Adapt content from source to target platform

        Example: Blog post → LinkedIn carousel (10 slides)
        """

        source_body = source_asset['body']
        source_format = source_asset['format']

        # Platform constraints
        constraints = self._get_platform_constraints(target_channel, target_format)

        # LLM prompt for adaptation
        prompt = f"""
        Adapt this {source_format} content for {target_channel} {target_format}.

        Source content:
        {source_body}

        Target constraints:
        - Max length: {constraints['max_length']}
        - Tone: {constraints['tone']}
        - Structure: {constraints['structure']}

        Preserve the core message and hook, but reformat appropriately.
        """

        adapted_content = await self.llm.generate(prompt)

        return adapted_content

    def _get_platform_constraints(self, channel: str, format: str) -> Dict[str, Any]:
        """Get platform-specific constraints"""

        constraints = {
            ("linkedin", "post"): {
                "max_length": 3000,
                "tone": "professional",
                "structure": "hook + story + cta"
            },
            ("twitter", "thread"): {
                "max_length": 280,  # per tweet
                "tone": "conversational",
                "structure": "numbered_sequence"
            },
            ("instagram", "carousel"): {
                "max_length": 2200,  # caption
                "tone": "visual_first",
                "structure": "slide_sequence"
            }
        }

        return constraints.get((channel, format), {})
```

---

### 5.4 PulseSeer (TREND-01) - Trend Detection

**Purpose**: Monitor trends and alert agents

**Tools**:
- Google Trends API
- Twitter Trending API
- Reddit API
- News aggregators

**Workflow**:
1. Scrape trending topics
2. Filter by relevance to workspace cohorts
3. Predict lifecycle stage (emerging/peak/declining)
4. Alert Strategy + Content agents

**Agent Code Skeleton**:
```python
# backend/agents/signals/pulse_seer.py

class PulseSeerAgent(BaseAgent):
    """Trend Detection & Prediction Agent"""

    agent_id = "TREND-01"
    agent_name = "PulseSeer"

    async def scan_trends(
        self,
        cohorts: List[str],
        platforms: List[str] = ["twitter", "reddit", "google"]
    ) -> List[TrendAlert]:
        """Scan for emerging trends relevant to cohorts"""

        alerts = []

        for platform in platforms:
            trends = await self._fetch_platform_trends(platform)

            for trend in trends:
                # Filter by cohort relevance
                relevance_score = self._score_relevance(trend, cohorts)

                if relevance_score > 0.6:
                    # Predict lifecycle
                    lifecycle_stage = self._predict_lifecycle(trend)

                    alert = TrendAlert(
                        trend_id=str(uuid4()),
                        topic=trend['topic'],
                        platforms=[platform],
                        velocity=trend['growth_rate'],
                        lifecycle_stage=lifecycle_stage,
                        relevant_cohorts=cohorts,
                        opportunity_score=relevance_score * trend['volume'],
                        expiry_date=self._estimate_expiry(trend)
                    )

                    alerts.append(alert)

        return alerts

    async def _fetch_platform_trends(self, platform: str) -> List[Dict]:
        """Fetch trending topics from platform API"""
        # Twitter API, Google Trends, Reddit, etc.
        pass

    def _predict_lifecycle(self, trend: Dict) -> str:
        """Predict where trend is in lifecycle"""

        # Simple heuristic (in production, use time-series model)
        age_days = (datetime.utcnow() - trend['first_seen']).days
        growth_rate = trend['growth_rate']

        if age_days < 3 and growth_rate > 2.0:
            return "emerging"
        elif age_days < 7 and growth_rate > 1.5:
            return "peak"
        else:
            return "declining"
```

---

### 5.5 MirrorScout (COMP-01) - Competitor Analyst

**Purpose**: Track competitor content and strategies

**Tools**:
- Web scraping (BeautifulSoup, Playwright)
- Social API access
- Meta Ad Library API
- SERP APIs

**Workflow**:
1. Monitor competitor profiles/websites
2. Extract content patterns (hooks, offers, channels)
3. Identify their "Moves" (campaign patterns)
4. Alert Strategy agents

**Agent Code Skeleton**:
```python
# backend/agents/signals/mirror_scout.py

class MirrorScoutAgent(BaseAgent):
    """Competitor Analysis Agent"""

    agent_id = "COMP-01"
    agent_name = "MirrorScout"

    async def analyze_competitor(
        self,
        competitor_url: str,
        platforms: List[str] = ["linkedin", "twitter"]
    ) -> Dict[str, Any]:
        """Deep dive on a competitor"""

        # Scrape website
        website_data = await self._scrape_website(competitor_url)

        # Scrape social profiles
        social_data = {}
        for platform in platforms:
            social_data[platform] = await self._scrape_social(platform, competitor_url)

        # Extract patterns
        content_patterns = self._extract_patterns(website_data, social_data)

        # Infer their strategy
        strategy = self._infer_strategy(content_patterns)

        return {
            "competitor_url": competitor_url,
            "content_patterns": content_patterns,
            "inferred_strategy": strategy,
            "posting_frequency": social_data.get('linkedin', {}).get('posts_per_week'),
            "top_performing_hooks": content_patterns['top_hooks']
        }

    async def _scrape_website(self, url: str) -> Dict:
        """Scrape competitor website for content"""
        # Playwright or BeautifulSoup
        pass

    def _extract_patterns(self, website_data, social_data) -> Dict:
        """Extract content patterns using LLM"""

        prompt = f"""
        Analyze this competitor's content and identify patterns:

        Website: {website_data['text'][:2000]}
        LinkedIn posts: {social_data.get('linkedin', {}).get('recent_posts', [])}

        Identify:
        1. Hook types (question, proof, pain, urgency)
        2. Offers (lead magnet, demo, consultation)
        3. Messaging themes
        4. Content formats (blog, video, carousel)
        """

        analysis = await self.llm.generate(prompt)
        return analysis
```

---

### 5.6 Policy Arbiter (PA) - Conflict Resolver

**Purpose**: Resolve conflicts between agent recommendations

**Workflow**:
1. Receive conflicting recommendations
2. Evaluate each using decision framework
3. Issue final decision
4. Optionally escalate to human

**Agent Code Skeleton**:
```python
# backend/agents/executive/policy_arbiter.py

class PolicyArbiterAgent(BaseAgent):
    """Multi-Agent Conflict Resolution Agent"""

    agent_id = "PA"
    agent_name = "PolicyArbiter"

    async def resolve_conflict(
        self,
        conflict_id: str,
        agents_involved: List[str],
        recommendations: Dict[str, Any],
        context: Dict[str, Any]
    ) -> PolicyDecision:
        """
        Resolve conflict between agents

        Example:
            MoveArchitect says "SCALE" (high ROI)
            FirewallMaven says "KILL" (brand risk)
        """

        # Step 1: Assess priority
        priorities = {
            "CRISIS-01": 10,  # Brand risk always highest
            "METRIC-01": 8,   # Data-driven insights high
            "STRAT-01": 6,    # Strategy medium
            "IDEA-01": 4      # Creative lower
        }

        # Step 2: Check if any agent is a "veto agent"
        veto_agents = ["CRISIS-01"]  # FirewallMaven can veto
        for agent_id in veto_agents:
            if agent_id in agents_involved:
                rec = recommendations[agent_id]
                if rec['action'] in ['reject', 'kill']:
                    return PolicyDecision(
                        decision_id=str(uuid4()),
                        conflict_id=conflict_id,
                        agents_involved=agents_involved,
                        decision=rec['action'],
                        reasoning=f"Veto by {agent_id}: {rec['reasoning']}",
                        overrides={"winning_agent": agent_id}
                    )

        # Step 3: Weight by priority and confidence
        scores = {}
        for agent_id, rec in recommendations.items():
            priority = priorities.get(agent_id, 5)
            confidence = rec.get('confidence', 0.5)
            scores[agent_id] = priority * confidence

        winner = max(scores, key=scores.get)

        # Step 4: Check if consensus is needed
        if max(scores.values()) / sum(scores.values()) < 0.5:
            # No clear winner, initiate debate
            debate_result = await self._initiate_consensus_debate(
                conflict_id, agents_involved, recommendations, context
            )
            return debate_result

        # Step 5: Issue decision
        return PolicyDecision(
            decision_id=str(uuid4()),
            conflict_id=conflict_id,
            agents_involved=agents_involved,
            decision=recommendations[winner]['action'],
            reasoning=f"Decision based on {winner}'s recommendation (priority: {priorities[winner]}, confidence: {recommendations[winner]['confidence']})",
            overrides={"winning_agent": winner}
        )
```

---

## 6. DATABASE SCHEMA EXTENSIONS

### 6.1 New Tables Required

```sql
-- Agent Registry (for dynamic discovery)
CREATE TABLE agent_registry (
  agent_id TEXT PRIMARY KEY,
  agent_name TEXT,
  capabilities TEXT[],
  current_load INT DEFAULT 0,
  max_concurrent INT DEFAULT 5,
  avg_latency_ms FLOAT,
  success_rate FLOAT,
  last_heartbeat TIMESTAMPTZ
);

-- Agent Messages (audit log)
CREATE TABLE agent_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type TEXT,
  origin TEXT,
  targets TEXT[],
  payload JSONB,
  priority TEXT,
  correlation_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_messages_correlation ON agent_messages(correlation_id);
CREATE INDEX idx_agent_messages_type ON agent_messages(type);

-- Experiments (for SplitMind)
CREATE TABLE experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  move_id UUID REFERENCES moves(id),
  hypothesis TEXT,
  variants JSONB,
  sample_size_per_variant INT,
  duration_days INT,
  success_metric TEXT,
  stop_conditions JSONB,
  status TEXT DEFAULT 'running',
  winner_variant TEXT,
  confidence FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

CREATE TABLE experiment_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experiment_id UUID REFERENCES experiments(id),
  variant TEXT,
  metric_name TEXT,
  metric_value FLOAT,
  sample_size INT,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Trends (for PulseSeer)
CREATE TABLE trends (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic TEXT,
  platforms TEXT[],
  velocity FLOAT,
  lifecycle_stage TEXT,
  relevant_cohorts UUID[],
  opportunity_score FLOAT,
  first_seen TIMESTAMPTZ,
  expiry_date TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Competitor Intelligence (for MirrorScout)
CREATE TABLE competitors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT,
  url TEXT,
  platforms JSONB,
  last_analyzed TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE competitor_content (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  competitor_id UUID REFERENCES competitors(id),
  platform TEXT,
  content_type TEXT,
  body TEXT,
  metadata JSONB,
  performance_metrics JSONB,
  scraped_at TIMESTAMPTZ DEFAULT NOW()
);

-- Policy Decisions (for Policy Arbiter)
CREATE TABLE policy_decisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conflict_id TEXT,
  agents_involved TEXT[],
  decision TEXT,
  reasoning TEXT,
  overrides JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Visual Design Specs (for NoirFrame)
CREATE TABLE visual_designs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id UUID,
  mood TEXT,
  color_palette TEXT[],
  composition TEXT,
  canva_template_id TEXT,
  image_gen_prompt TEXT,
  aspect_ratio TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent Debates (for Consensus Orchestrator)
CREATE TABLE agent_debates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic TEXT,
  correlation_id TEXT,
  participants TEXT[],
  rounds JSONB,  -- [{"round": 1, "positions": {...}}, ...]
  final_decision TEXT,
  confidence FLOAT,
  consensus_reached BOOLEAN,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 6.2 Extend Existing Tables

```sql
-- Add agent tracking to assets
ALTER TABLE assets ADD COLUMN created_by_agent TEXT;
ALTER TABLE assets ADD COLUMN reviewed_by_agents TEXT[];
ALTER TABLE assets ADD COLUMN agent_debate_id UUID REFERENCES agent_debates(id);

-- Add experiment tracking to assets
ALTER TABLE assets ADD COLUMN experiment_id UUID REFERENCES experiments(id);
ALTER TABLE assets ADD COLUMN experiment_variant TEXT;

-- Add trend tracking to moves
ALTER TABLE moves ADD COLUMN triggered_by_trend_id UUID REFERENCES trends(id);

-- Add competitor analysis to moves
ALTER TABLE moves ADD COLUMN competitor_analysis JSONB;
```

---

## 7. IMPLEMENTATION ROADMAP

### PHASE 1: Infrastructure (Weeks 1-2) - CRITICAL

**Goal**: Build event bus, message protocols, agent registry

**Tasks**:
1. ✅ **Event Bus Implementation**
   - [ ] Implement `EventBus` class with Redis Pub/Sub
   - [ ] Define all `AgentMessage` Pydantic models
   - [ ] Create message type enum (`EventType`)
   - [ ] Add audit logging for all messages
   - [ ] Test: Publish/subscribe between 2 agents

2. ✅ **Context Bus Implementation**
   - [ ] Implement `ContextBus` for shared scratchpad
   - [ ] Add locking mechanism for resource coordination
   - [ ] Test: Multiple agents updating shared context

3. ✅ **Agent Registry**
   - [ ] Implement `AgentRegistry` with capability indexing
   - [ ] Add heartbeat mechanism
   - [ ] Add load balancing (least-loaded agent selection)
   - [ ] Test: Register 5 agents, find by capability

4. ✅ **Database Migrations**
   - [ ] Create all new tables (experiments, trends, competitors, etc.)
   - [ ] Extend existing tables (assets, moves)
   - [ ] Run migrations on dev environment
   - [ ] Seed test data

**Deliverables**:
- `backend/messaging/event_bus.py`
- `backend/messaging/context_bus.py`
- `backend/messaging/agent_registry.py`
- `backend/models/agent_messages.py`
- Migration files in `database/migrations/`

**Success Criteria**:
- Agents can publish/subscribe to events
- Shared context is accessible by all agents
- Agent registry tracks 10+ agents with capabilities

---

### PHASE 2: New Agents (Weeks 3-5) - HIGH PRIORITY

**Goal**: Build the 6 missing agents

**Tasks**:
1. ✅ **SplitMind (A/B Test Agent)**
   - [ ] Create `backend/agents/strategy/split_mind.py`
   - [ ] Implement `design_experiment()` method
   - [ ] Implement `analyze_experiment()` with Bayesian stats
   - [ ] Integrate with move creation workflow
   - [ ] Test: Create experiment, run for 7 days, declare winner

2. ✅ **NoirFrame (Visual Design Agent)**
   - [ ] Create `backend/agents/creation/noir_frame.py`
   - [ ] Implement `design_visual()` method
   - [ ] Build mood inference logic
   - [ ] Integrate with Canva service
   - [ ] Test: Generate visual specs for 5 different briefs

3. ✅ **PortaMorph (Cross-Platform Adapter)**
   - [ ] Create `backend/agents/creation/porta_morph.py`
   - [ ] Implement `adapt_content()` method
   - [ ] Define platform constraints table
   - [ ] Test: Blog → LinkedIn carousel, Email → Twitter thread

4. ✅ **PulseSeer (Trend Detection)**
   - [ ] Create `backend/agents/signals/pulse_seer.py`
   - [ ] Integrate Google Trends API
   - [ ] Integrate Twitter Trends API
   - [ ] Implement lifecycle prediction
   - [ ] Schedule daily trend scan
   - [ ] Test: Detect 3 emerging trends

5. ✅ **MirrorScout (Competitor Analysis)**
   - [ ] Create `backend/agents/signals/mirror_scout.py`
   - [ ] Implement web scraping with Playwright
   - [ ] Implement pattern extraction with LLM
   - [ ] Schedule weekly competitor scans
   - [ ] Test: Analyze 2 competitors, extract patterns

6. ✅ **Policy Arbiter (Conflict Resolution)**
   - [ ] Create `backend/agents/executive/policy_arbiter.py`
   - [ ] Implement `resolve_conflict()` method
   - [ ] Define priority matrix
   - [ ] Integrate with consensus orchestrator
   - [ ] Test: Resolve 5 conflict scenarios

**Deliverables**:
- 6 new agent files
- Integration tests for each agent
- API endpoints to trigger agents
- Documentation for each agent

**Success Criteria**:
- All 6 agents can be invoked via API
- Agents communicate via event bus
- Agents store results in DB

---

### PHASE 3: Consensus & Collaboration (Weeks 6-7) - MEDIUM PRIORITY

**Goal**: Enable multi-agent debates and parallel workflows

**Tasks**:
1. ✅ **Consensus Orchestrator**
   - [ ] Create `backend/agents/consensus/orchestrator.py`
   - [ ] Implement `initiate_debate()` method
   - [ ] Build multi-round debate logic
   - [ ] Add voting and confidence scoring
   - [ ] Test: 3-agent debate on "Scale vs. Kill" decision

2. ✅ **Parallel Workflow Execution**
   - [ ] Modify master orchestrator to fan-out
   - [ ] Implement barrier synchronization (wait for all agents)
   - [ ] Add timeout handling for slow agents
   - [ ] Test: Fan-out to 4 agents, collect results

3. ✅ **Cross-Domain Collaboration**
   - [ ] Strategy + Content real-time collaboration
   - [ ] Signals → Strategy feedback loop
   - [ ] Risk → All sectors broadcast
   - [ ] Test: Move creation with 4 sectors collaborating

**Deliverables**:
- `backend/agents/consensus/orchestrator.py`
- Updated master orchestrator with parallel execution
- Integration tests for multi-agent workflows

**Success Criteria**:
- 3+ agents can debate and reach consensus
- Agents from different sectors can collaborate in real-time
- No deadlocks or race conditions

---

### PHASE 4: Self-Improving Loops (Weeks 8-10) - MEDIUM PRIORITY

**Goal**: Agents learn from outcomes and adapt

**Tasks**:
1. ✅ **Agent Recommendation Tracking**
   - [ ] Create `agent_recommendations` table
   - [ ] Log all agent recommendations with expected impact
   - [ ] Track actual impact vs. expected
   - [ ] Calculate agent trust score
   - [ ] Test: 100 recommendations, compute trust scores

2. ✅ **Pattern Evolution**
   - [ ] Cluster high-performing assets into pattern families
   - [ ] Update pattern library weekly
   - [ ] Propagate patterns to Muse/Content agents
   - [ ] Test: Identify 10 winning patterns

3. ✅ **Meta-Learning Agent** (use existing code from `backend/services/meta_learning.py`)
   - [ ] Expose meta-learning as a scheduled job
   - [ ] Run weekly: analyze agent performance
   - [ ] Adjust agent routing weights
   - [ ] Test: Improve recommendation accuracy by 10%

**Deliverables**:
- `agent_recommendations` table
- Scheduled jobs for pattern evolution and meta-learning
- Dashboard showing agent trust scores

**Success Criteria**:
- Agent recommendations improve over time
- Pattern library grows and is used by content agents
- Meta-learning reduces bad recommendations

---

### PHASE 5: Integration & Production Readiness (Weeks 11-12) - HIGH PRIORITY

**Goal**: Wire everything together, deploy

**Tasks**:
1. ✅ **Frontend-Backend Integration**
   - [ ] Wire Moves page to backend API
   - [ ] Wire Cohorts page to backend API
   - [ ] Wire Strategy wizard to backend API
   - [ ] Wire Muse to content agents
   - [ ] Add real-time updates (Supabase Realtime)
   - [ ] Test: Full user flow end-to-end

2. ✅ **Background Jobs**
   - [ ] Start Celery workers
   - [ ] Schedule daily sweep automation
   - [ ] Schedule weekly review generation
   - [ ] Schedule trend scanning
   - [ ] Schedule competitor analysis
   - [ ] Test: All scheduled jobs run successfully

3. ✅ **Social Media Publishing**
   - [ ] Complete LinkedIn publisher
   - [ ] Complete Twitter publisher
   - [ ] Complete Instagram publisher
   - [ ] Test: Publish to all 3 platforms

4. ✅ **Monitoring & Observability**
   - [ ] Integrate Sentry for error tracking
   - [ ] Add PostHog backend events
   - [ ] Set up Cloud Logging dashboards
   - [ ] Add Prometheus metrics (optional)
   - [ ] Test: Track errors and events

5. ✅ **CI/CD Pipeline**
   - [ ] GitHub Actions for tests
   - [ ] Automated deployment to staging
   - [ ] Automated deployment to production
   - [ ] Test: Deploy to production

**Deliverables**:
- Fully integrated frontend
- Background jobs running
- Social publishing working
- Monitoring dashboards
- CI/CD pipeline

**Success Criteria**:
- Users can create Moves and see real data
- Content is generated and published automatically
- System is observable and debuggable
- Zero-downtime deployments

---

### PHASE 6: Advanced Features (Weeks 13+) - LOW PRIORITY

**Goal**: Polish, optimize, advanced capabilities

**Tasks**:
1. Event sourcing layer
2. Agent marketplace (dynamic agent spawning)
3. Advanced A/B testing framework
4. Predictive analytics (conversion forecasting)
5. Multi-brand support (enterprise)

---

## 8. CODE EXAMPLES

### 8.1 End-to-End Workflow: Move Creation with Swarm

```python
# backend/workflows/move_creation_swarm.py

from backend.messaging.event_bus import EventBus, AgentMessage, EventType
from backend.messaging.context_bus import ContextBus
from backend.messaging.agent_registry import AgentRegistry
from backend.models.agent_messages import GoalRequest, MovePlan, ContentBrief

async def create_move_with_swarm(
    goal: GoalRequest,
    workspace_id: str,
    user_id: str
):
    """
    Full swarm workflow for move creation

    Steps:
    1. Apex Cortex receives goal
    2. Fan-out to Strategy, Signals, Cohort sectors
    3. MoveArchitect designs move
    4. PsycheLens verifies cohorts
    5. PulseSeer checks trends
    6. MirrorScout checks competitors
    7. Policy Arbiter resolves conflicts
    8. MuseForge creates content briefs
    9. LyraQuill writes copy
    10. NoirFrame designs visuals
    11. FirewallMaven reviews
    12. Execution agents publish
    """

    correlation_id = f"move-{uuid4()}"

    # Initialize communication layers
    event_bus = EventBus(redis_client)
    context_bus = ContextBus(redis_client)
    registry = AgentRegistry(redis_client)

    # Step 1: Apex Cortex receives goal
    context_bus.set_context(correlation_id, "goal", goal.model_dump())
    context_bus.set_context(correlation_id, "workspace_id", workspace_id)
    context_bus.set_context(correlation_id, "user_id", user_id)

    # Step 2: Fan-out to sectors (PARALLEL)
    event_bus.publish(AgentMessage(
        id=str(uuid4()),
        type=EventType.GOAL_REQUEST,
        origin="APEX",
        targets=["STRAT-01", "PSY-01", "TREND-01", "COMP-01"],
        payload=goal.model_dump(),
        priority="HIGH",
        correlation_id=correlation_id
    ))

    # Step 3: Wait for all agents to respond (barrier sync)
    await wait_for_agents(
        correlation_id,
        ["STRAT-01", "PSY-01", "TREND-01", "COMP-01"],
        timeout_seconds=60
    )

    # Step 4: Collect responses from context bus
    move_plan = context_bus.get_context(correlation_id, "move_plan")  # From STRAT-01
    cohort_analysis = context_bus.get_context(correlation_id, "cohort_analysis")  # From PSY-01
    trends = context_bus.get_context(correlation_id, "trends")  # From TREND-01
    competitor_intel = context_bus.get_context(correlation_id, "competitor_intel")  # From COMP-01

    # Step 5: Check for conflicts
    if move_plan and competitor_intel and competitor_intel['similar_campaign_active']:
        # Initiate debate
        from backend.agents.executive.policy_arbiter import PolicyArbiterAgent
        arbiter = PolicyArbiterAgent()

        decision = await arbiter.resolve_conflict(
            conflict_id=str(uuid4()),
            agents_involved=["STRAT-01", "COMP-01"],
            recommendations={
                "STRAT-01": {"action": "proceed", "reasoning": "High ROI potential"},
                "COMP-01": {"action": "tweak", "reasoning": "Competitor running similar campaign"}
            },
            context={"move_plan": move_plan, "competitor_intel": competitor_intel}
        )

        if decision.decision == "tweak":
            # Ask STRAT-01 to revise
            event_bus.publish(AgentMessage(
                type=EventType.MOVE_PLAN,
                origin="PA",
                targets=["STRAT-01"],
                payload={"action": "revise", "reason": decision.reasoning},
                correlation_id=correlation_id
            ))

            # Wait for revised plan
            await wait_for_agents(correlation_id, ["STRAT-01"], timeout_seconds=30)
            move_plan = context_bus.get_context(correlation_id, "move_plan")

    # Step 6: Create move in database
    move_id = await db.moves.insert({
        "workspace_id": workspace_id,
        "name": move_plan['name'],
        "objective": move_plan['objective'],
        "target_cohorts": move_plan['cohorts'],
        "channels": move_plan['channels'],
        "kpi_primary": move_plan['kpi'],
        "kpi_target": move_plan['target'],
        "created_by_agent": "STRAT-01"
    })

    # Step 7: Trigger content creation (PARALLEL)
    content_briefs = move_plan['content_needs']

    for brief in content_briefs:
        event_bus.publish(AgentMessage(
            type=EventType.CONTENT_BRIEF,
            origin="IDEA-01",
            targets=["COPY-01", "VIS-01"],
            payload=brief,
            correlation_id=correlation_id
        ))

    # Step 8: Wait for content generation
    await wait_for_agents(correlation_id, ["COPY-01", "VIS-01"], timeout_seconds=120)

    # Step 9: Trigger review
    drafts = context_bus.get_context(correlation_id, "draft_assets")

    for draft in drafts:
        event_bus.publish(AgentMessage(
            type=EventType.DRAFT_ASSET,
            origin="COPY-01",
            targets=["CRISIS-01"],
            payload=draft,
            correlation_id=correlation_id
        ))

    # Step 10: Wait for review
    await wait_for_agents(correlation_id, ["CRISIS-01"], timeout_seconds=30)

    review_results = context_bus.get_context(correlation_id, "review_results")

    # Step 11: If approved, schedule publishing
    approved_assets = [a for a in review_results if a['status'] == 'approved']

    for asset in approved_assets:
        # Schedule via execution agents
        await schedule_asset_publication(asset, move_id)

    return {
        "move_id": move_id,
        "status": "created",
        "assets_approved": len(approved_assets),
        "assets_rejected": len([a for a in review_results if a['status'] == 'rejected'])
    }

async def wait_for_agents(
    correlation_id: str,
    agent_ids: List[str],
    timeout_seconds: int
):
    """Wait for all agents to finish their tasks"""

    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        all_done = True

        for agent_id in agent_ids:
            status = context_bus.get_context(correlation_id, f"{agent_id}_status")
            if status != "done":
                all_done = False
                break

        if all_done:
            return

        await asyncio.sleep(1)

    # Timeout
    raise TimeoutError(f"Agents {agent_ids} did not complete within {timeout_seconds}s")
```

---

### 8.2 Agent Base Class with Event Bus Integration

```python
# backend/agents/base_swarm_agent.py

from abc import ABC, abstractmethod
from backend.messaging.event_bus import EventBus, AgentMessage
from backend.messaging.context_bus import ContextBus
from backend.messaging.agent_registry import AgentRegistry, AgentCapability

class BaseSwarmAgent(ABC):
    """Base class for all swarm agents"""

    def __init__(
        self,
        redis_client,
        db,
        llm_client,
        agent_id: str,
        agent_name: str,
        capabilities: List[str]
    ):
        self.event_bus = EventBus(redis_client)
        self.context_bus = ContextBus(redis_client)
        self.registry = AgentRegistry(redis_client)
        self.db = db
        self.llm = llm_client

        self.agent_id = agent_id
        self.agent_name = agent_name
        self.capabilities = capabilities

        # Register this agent
        self.registry.register(AgentCapability(
            agent_id=agent_id,
            agent_name=agent_name,
            capabilities=capabilities,
            load=0,
            max_concurrent=5,
            avg_latency_ms=2000,
            success_rate=0.9,
            last_heartbeat=datetime.utcnow()
        ))

        # Start listening for messages
        self.start_listening()

    def start_listening(self):
        """Subscribe to event bus"""
        self.event_bus.subscribe(self.agent_id, self.handle_message)

    async def handle_message(self, message: AgentMessage):
        """Handle incoming messages"""

        correlation_id = message.correlation_id

        try:
            # Update load
            self.registry.update_load(self.agent_id, +1)

            # Set status
            self.context_bus.set_context(correlation_id, f"{self.agent_id}_status", "working")

            # Dispatch to handler
            if message.type == "goal.request":
                result = await self.handle_goal_request(message)
            elif message.type == "content.brief":
                result = await self.handle_content_brief(message)
            # ... other types

            # Store result in context
            self.context_bus.set_context(correlation_id, f"{self.agent_id}_result", result)

            # Set status done
            self.context_bus.set_context(correlation_id, f"{self.agent_id}_status", "done")

            # Update load
            self.registry.update_load(self.agent_id, -1)

        except Exception as e:
            # Log error
            self.context_bus.set_context(correlation_id, f"{self.agent_id}_error", str(e))
            self.context_bus.set_context(correlation_id, f"{self.agent_id}_status", "error")

            # Update load
            self.registry.update_load(self.agent_id, -1)

    @abstractmethod
    async def handle_goal_request(self, message: AgentMessage):
        """Override in subclass"""
        pass

    @abstractmethod
    async def handle_content_brief(self, message: AgentMessage):
        """Override in subclass"""
        pass
```

---

## 9. NEXT STEPS

### Immediate Actions (This Week)

1. **Review this plan** with the team
2. **Prioritize phases** based on business goals
3. **Assign owners** for each phase
4. **Set up project tracking** (GitHub Projects, Linear, etc.)
5. **Create detailed tickets** for Phase 1 tasks

### Questions to Resolve

1. Do we need NATS/Kafka or is Redis Pub/Sub sufficient?
2. What's the budget for API calls (trend APIs, competitor scraping)?
3. Do we need real-time collaboration or can we use polling?
4. What's the testing strategy for multi-agent workflows?
5. How do we handle agent versioning (if we update agent logic)?

---

## 10. CONCLUSION

This plan transforms RaptorFlow from a **hierarchical agent system** into a **true collaborative swarm** with:

- ✅ **Event-driven architecture** for real-time communication
- ✅ **Peer-to-peer agent messaging** for collaboration
- ✅ **Consensus mechanisms** for critical decisions
- ✅ **Self-improving loops** for continuous learning
- ✅ **Dynamic agent discovery** for optimal task assignment
- ✅ **Parallel execution** for speed

**Timeline**: 12-16 weeks to full production-ready swarm

**Risk**: Complexity increases; need strong testing and monitoring

**Reward**: Industry-leading AI marketing OS with unmatched automation and intelligence

---

**End of Implementation Plan**
