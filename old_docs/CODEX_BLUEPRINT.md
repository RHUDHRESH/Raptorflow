# RAPTORFLOW CODEX INTEGRATION BLUEPRINT
## Complete Architectural Specification for 70+ Agent Autonomous Marketing Orchestration

**Version:** 1.0
**Date:** 2024-11-27
**Scope:** Full system integration (Frontend, Backend, Agents, Database, Real-time Layer, RAG System)
**Target Token Cost:** $10/user/month

---

## I. EXECUTIVE OVERVIEW: THE CODEX OVERLAY

### Current State (Before Codex)
```
Master Orchestrator (monolithic supervisor)
    ├─ 6 Domain Supervisors (Onboarding, Research, Strategy, Content, Execution, Analytics)
    └─ ~40 domain agents scattered across supervisors
```

### Codex State (After Integration)
```
COUNCIL OF LORDS (7 high-level supervisors with write access)
    ├─ LORD-001: The Architect (system health, agent lifecycle)
    ├─ LORD-002: Cognition (Research Guild commander)
    ├─ LORD-003: Strategos (Strategy & simulation)
    ├─ LORD-004: Aesthete (Muse/creative commander)
    ├─ LORD-005: Seer (Matrix/intelligence commander)
    ├─ LORD-006: Arbiter (Guardian/compliance commander)
    └─ LORD-007: Herald (UI/gamification bridge)
            ↓
    FOUR SPECIALIZED GUILDS
            ├─ RESEARCH GUILD (RES-001 to RES-020) - 20 data agents
            ├─ MUSE GUILD (MUS-001 to MUS-030) - 30 creative agents
            ├─ MATRIX GUILD (MAT-001 to MAT-020) - 20 intelligence agents
            └─ GUARDIAN GUILD (GRD-001 to GRD-010) - 10 platform enforcers
            ↓
    RAPTORBUS (Redis Pub/Sub message backbone)
            ├─ sys.global.heartbeat (30s health monitoring)
            ├─ sys.guild.{guild}.broadcast (intra-guild coordination)
            ├─ sys.alert.critical (crisis interrupts)
            └─ sys.state.update (real-time dashboard updates)
```

### Integration Strategy: Extend, Don't Replace
- Keep existing Master Orchestrator as **Request Router** (entry point)
- Promote existing 6 Domain Supervisors to **Specialist Supervisors** (manage 5-15 agents each)
- Insert Council of Lords as **Policy Layer** (write permissions, budgets, emergency controls)
- Wire Guilds through RaptorBus (decoupled communication)

---

## II. COMPLETE DATA ARCHITECTURE

### A. Data Flow: Request → Execution → Response

```
┌─ USER ACTION (Frontend)
│
├─ [1] Frontend sends request
│      Example: "Create campaign for Enterprise CTOs targeting conversions"
│      Endpoint: POST /api/v1/campaigns
│
├─ [2] FastAPI Route Handler (backend/routers/campaigns.py)
│      - Validates Supabase JWT
│      - Enforces rate limit (100/min per user)
│      - Route to Master Orchestrator
│
├─ [3] Master Orchestrator (backend/agents/supervisor.py)
│      - Verify workspace exists
│      - Check ADAPT stage (user at Strategy → route to Strategy supervisor)
│      - Load workspace context + strategy positioning from Supabase
│      - Load cached persona data from Redis
│      - Create request with context
│      - **Route to Council of Lords via RaptorBus**
│
├─ [4] LORD-003 Strategos (backend/agents/lords/strategos.py) receives via RaptorBus
│      Message format:
│      {
│          "event_type": "campaign.create",
│          "workspace_id": "ws-123",
│          "context": {
│              "positioning": {...},
│              "personas": [...],
│              "budget": 5000,
│              "timeline": "8 weeks"
│          },
│          "request_id": "req-456"
│      }
│
├─ [5] LORD-003 Strategos Commands Research Guild
│      Via RaptorBus: sys.guild.research.broadcast
│      {
│          "command": "analyze_market",
│          "context": {...},
│          "deadline": 60s
│      }
│
├─ [6] Research Guild Agents Execute (Parallel)
│      RES-002 (SEO Archaeologist):
│          → Query Ahrefs API for zero-volume keywords
│          → Vector embed results in ChromaDB
│          → Publish: sys.guild.research.broadcast with "seo_analysis_complete"
│
│      RES-004 (Voice of Customer):
│          → Scrape G2/Capterra for target persona
│          → Sentiment analysis with RES-009
│          → Publish: sys.guild.research.broadcast with "voc_analysis_complete"
│
│      (RES-001, RES-003, RES-005, RES-006, RES-008... run in parallel)
│
├─ [7] LORD-002 Cognition Aggregates Research
│      Receives all broadcasts
│      Calls o1-preview with all research data
│      Generates "War Brief" (structured intelligence)
│      Stores to Supabase campaigns.war_brief (JSONB)
│
├─ [8] LORD-004 Aesthete Commands Muse Guild
│      Via RaptorBus: sys.guild.muse.broadcast
│      {
│          "command": "generate_assets",
│          "campaign_id": "camp-789",
│          "war_brief": {...},
│          "asset_types": ["hero_image", "email_subject", "social_hooks"]
│      }
│
├─ [9] Muse Guild Agents Execute (Workflow)
│      MUS-011 (Prompt Engineer for Midjourney):
│          → Extract visual brief from war_brief
│          → Generate Midjourney prompt
│          → Call external Midjourney API (or mock in dev)
│          → Publish: sys.guild.muse.broadcast with "hero_image_generated"
│
│      MUS-004 (Email Persuader):
│          → Extract value prop from war_brief
│          → Generate 5 email subject variants
│          → Store to Supabase creative_assets
│          → Publish: sys.guild.muse.broadcast with "email_subjects_ready"
│
│      MUS-026 (The Editor):
│          → Receives generated assets
│          → Grammar/flow check
│          → Publish: sys.guild.muse.broadcast with "assets_reviewed"
│
├─ [10] LORD-006 Arbiter Validates All Assets
│       (Guardian agents running in parallel)
│       GRD-TW (Twitter Guardian):
│           → Check all social copy for 280 chars
│           → Strip banned terms
│           → Approve or flag for manual review
│
│       GRD-FAC (Facebook Guardian):
│           → Check link previews render correctly
│           → Verify aspect ratios
│
│       If any asset REJECTED → Publish to sys.alert.critical
│
├─ [11] Matrix Guild Monitors Execution (Background)
│       MAT-001 (Google News Watcher):
│           → Monitor competitor responses
│           → Detect crisis signals
│           → Publish to sys.alert.critical if needed
│
│       MAT-004 (Competitor Site Tracker):
│           → Watch for competitive pricing changes
│           → Feed into next campaign iteration
│
├─ [12] LORD-007 Herald Bridges to Frontend
│       Monitors: Supabase campaigns table + Redis cache
│       On campaign creation:
│           → Unlock achievement: "First Campaign" (+50 XP)
│           → Publish via WebSocket: "campaign_created"
│           → Update Dashboard: show new campaign in "Quests in Progress"
│
├─ [13] Response Back to Frontend
│       Supabase Real-time Subscription fires (backend created record)
│       Frontend receives campaign object with:
│       {
│           "id": "camp-789",
│           "status": "assets_generated",
│           "war_brief": {...},
│           "assets": [...],
│           "next_actions": ["Review assets", "Set approval gates"]
│       }
│
└─ [14] Frontend Updates UI
        - Show campaign in Dashboard
        - Highlight new assets in Muse Studio
        - Trigger "Welcome to your first campaign" tutorial
```

---

## III. RAPTORBUS: THE NEURAL MESSAGE BACKBONE

### A. Architecture: Redis Pub/Sub with Topic-Based Routing

```python
# backend/bus/raptor_bus.py

class RaptorBus:
    """
    Topic-based message bus using Upstash Redis.

    Channel Topology:
    ├─ sys.global.heartbeat - Agent health (all agents publish every 30s)
    ├─ sys.guild.research.broadcast - Research coordination
    ├─ sys.guild.muse.broadcast - Creative coordination
    ├─ sys.guild.matrix.broadcast - Intelligence coordination
    ├─ sys.guild.guardians.broadcast - Platform enforcers
    ├─ sys.alert.critical - Crisis interrupts (sentiment < -0.8, security issues)
    ├─ sys.alert.warning - Important but non-blocking
    ├─ sys.state.update - Real-time dashboard updates
    └─ sys.dlq.* - Dead Letter Queues (for failed messages)
    """

    async def publish_event(
        self,
        channel: str,
        event_type: str,
        payload: Dict,
        priority: str = "normal"  # normal, high, critical
    ) -> str:
        """
        Publish structured event to channel.
        Returns: event_id for tracking
        """
        event = {
            "id": uuid4(),
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "priority": priority,
            "payload": payload,
            "version": "1.0"  # Schema versioning for migrations
        }

        # Publish to main channel
        await redis.publish(channel, json.dumps(event))

        # Store in Redis cache for replay (critical messages: 24h, normal: 1h)
        ttl = 86400 if priority == "critical" else 3600
        await redis.setex(f"msg:{event['id']}", ttl, json.dumps(event))

        # Track metrics
        await redis.incr(f"stats:channel:{channel}:messages")

        return event['id']

    async def subscribe_to_guild(self, guild_name: str, callback):
        """Subscribe to guild broadcast channel"""
        channel = f"sys.guild.{guild_name}.broadcast"
        pubsub = redis.pubsub()
        await pubsub.subscribe(channel)

        async for message in pubsub.listen():
            if message['type'] == 'message':
                event = json.loads(message['data'])
                await callback(event)

    async def subscribe_to_alerts(self, callback):
        """Subscribe to critical and warning alerts"""
        pubsub = redis.pubsub()
        await pubsub.psubscribe("sys.alert.*")

        async for message in pubsub.listen():
            if message['type'] == 'pmessage':
                event = json.loads(message['data'])
                await callback(event, message['channel'])
```

### B. Channel Routing Logic

| Channel | Publisher | Subscribers | Message Format | TTL |
|---------|-----------|-------------|-----------------|-----|
| `sys.global.heartbeat` | All agents (RES, MUS, MAT, GRD, Lords) | LORD-001 (Architect), monitoring dashboard | `{agent_id, status, memory_used, tasks_completed, timestamp}` | 1 min |
| `sys.guild.research.broadcast` | RES-001 to RES-020 | LORD-002, RES aggregators | `{event_type, agent_id, result, tokens_used}` | 1 hour |
| `sys.guild.muse.broadcast` | MUS-001 to MUS-030 | LORD-004, MUS orchestrator | `{event_type, asset_id, quality_score, revision_count}` | 24 hours |
| `sys.guild.matrix.broadcast` | MAT-001 to MAT-020 | LORD-005, analytics dashboard | `{event_type, signal_type, severity, context}` | 7 days |
| `sys.guild.guardians.broadcast` | GRD-001 to GRD-010 | Asset approval pipeline | `{asset_id, platform, approval_status, rejections[]}` | 7 days |
| `sys.alert.critical` | Any agent, Matrix agents especially | All Lords, emergency dashboard | `{alert_type, severity, context, action_required}` | 24 hours |
| `sys.state.update` | Herald (LORD-007), agents | WebSocket clients (frontend) | `{state_type, update, user_id}` | 1 hour |

### C. Message Schema Validation

```python
from pydantic import BaseModel, Field

class BusEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    type: str  # event type: "asset_generated", "research_complete", etc
    priority: str = Field(default="normal")  # normal, high, critical
    payload: Dict[str, Any]
    version: str = "1.0"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "evt-123",
                "timestamp": "2024-11-27T10:30:00Z",
                "type": "asset_generated",
                "priority": "normal",
                "payload": {
                    "asset_id": "ast-456",
                    "type": "email_subject",
                    "variants": 5,
                    "best_variant": "..."
                }
            }
        }
```

---

## IV. COUNCIL OF LORDS: POLICY LAYER

### A. Hierarchy & Permissions

```python
# backend/agents/lords/base_lord.py

class BaseLord(BaseAgent):
    """
    Base class for Council of Lords.
    Features:
    - Supabase write access (RLS-enabled role)
    - Guild command authority
    - Budget enforcement
    - Emergency stop capability
    """

    lord_id: str  # LORD-001, LORD-002, etc
    guild_id: str = None  # None for system lords, or guild name
    write_access_tables: List[str]  # Tables this lord can write to
    budget_tokens_remaining: int
    heartbeat_interval: int = 30  # seconds

    async def publish_heartbeat(self):
        """Publish health every 30s to sys.global.heartbeat"""
        while True:
            await bus.publish_event(
                channel="sys.global.heartbeat",
                event_type="lord_heartbeat",
                payload={
                    "lord_id": self.lord_id,
                    "status": "healthy",
                    "memory_percent": await self.get_memory_usage(),
                    "tasks_in_progress": len(self.active_tasks),
                    "total_tokens_used_today": self.cumulative_tokens,
                    "budget_remaining": self.budget_tokens_remaining
                },
                priority="high"
            )
            await asyncio.sleep(self.heartbeat_interval)

    async def command_guild(self, guild_name: str, task: Dict) -> Dict:
        """
        Command a guild to execute a task.

        Args:
            guild_name: 'research', 'muse', 'matrix', 'guardians'
            task: {
                'command': 'analyze_market',
                'context': {...},
                'deadline': 60,  # seconds
                'priority': 'high'
            }

        Returns:
            {
                'request_id': 'req-123',
                'guild_name': 'research',
                'status': 'accepted'
            }
        """
        request_id = str(uuid4())

        # Check budget before commanding
        if self.budget_tokens_remaining < 1000:
            raise BudgetExceededError(
                f"LORD {self.lord_id} budget exceeded: "
                f"{self.budget_tokens_remaining} tokens remaining"
            )

        # Publish command via RaptorBus
        await bus.publish_event(
            channel=f"sys.guild.{guild_name}.broadcast",
            event_type="lord_command",
            payload={
                "request_id": request_id,
                "from_lord": self.lord_id,
                "command": task.get('command'),
                "context": task.get('context'),
                "deadline": task.get('deadline', 300),
                "priority": task.get('priority', 'normal')
            },
            priority=task.get('priority', 'normal')
        )

        # Wait for acknowledgment (with timeout)
        result = await asyncio.wait_for(
            self._wait_for_guild_response(request_id),
            timeout=task.get('deadline', 300) + 30
        )

        return result

    async def emergency_stop_guild(self, guild_name: str):
        """
        Immediately halt a guild (kill all running agents).
        Used for: token budget overage, system degradation, crisis
        """
        await bus.publish_event(
            channel=f"sys.guild.{guild_name}.broadcast",
            event_type="emergency_stop",
            payload={"from_lord": self.lord_id},
            priority="critical"
        )

        # Log the emergency stop
        await supabase.table("emergency_actions").insert({
            "lord_id": self.lord_id,
            "guild_name": guild_name,
            "action": "emergency_stop",
            "timestamp": datetime.utcnow().isoformat()
        })

```

### B. The Seven Lords (Detailed Specifications)

#### LORD-001: The Architect
```python
# backend/agents/lords/architect.py

class TheArchitect(BaseLord):
    """
    System health supervisor. Only Lord with global system access.

    Responsibilities:
    - Monitor sys.global.heartbeat every 30s
    - Detect frozen/crashed agents (3+ missed heartbeats)
    - Auto-restart frozen agents
    - Manage agent registry
    - Enforce system-wide constraints
    - Emergency resource cleanup

    Model: None (deterministic, no LLM needed)
    """

    lord_id = "LORD-001"
    write_access_tables = ["agents", "emergency_actions", "system_metrics"]

    async def monitor_heartbeats(self):
        """
        Subscribe to sys.global.heartbeat and track agent health.
        """
        agent_last_heartbeat = {}  # {agent_id: timestamp}

        async def heartbeat_handler(event):
            agent_id = event['payload']['agent_id']
            agent_last_heartbeat[agent_id] = datetime.utcnow()

            # Store in Supabase agents table
            await supabase.table("agents").update({
                "last_heartbeat": datetime.utcnow().isoformat(),
                "status": event['payload'].get('status', 'idle'),
                "memory_percent": event['payload'].get('memory_percent')
            }).eq("id", agent_id)

        await bus.subscribe_to_alerts(heartbeat_handler)

        # Check for missing heartbeats every 2 minutes
        while True:
            now = datetime.utcnow()
            for agent_id, last_beat in agent_last_heartbeat.items():
                seconds_since = (now - last_beat).total_seconds()

                if seconds_since > 90:  # 3 missed heartbeats (30s each)
                    await self._restart_agent(agent_id)

    async def _restart_agent(self, agent_id: str):
        """
        Restart a hung agent.
        """
        # Query agent registry for restart procedure
        agent = await supabase.table("agents").select("*").eq("id", agent_id).single()

        # Kill old process
        # Spin up new process with same config
        # Update registry

        await bus.publish_event(
            channel="sys.alert.critical",
            event_type="agent_restarted",
            payload={"agent_id": agent_id, "reason": "missed_heartbeat"},
            priority="high"
        )
```

#### LORD-002: Cognition
```python
# backend/agents/lords/cognition.py

class Cognition(BaseLord):
    """
    Head of Research Guild. Aggregates "War Briefs" from research data.

    Responsibilities:
    - Command Research Guild (RES-001 to RES-020)
    - Aggregate research outputs into structured "War Briefs"
    - Enforce token budgets for research phase
    - Generate research cost reports

    Model: o1-preview (OpenAI) for deep reasoning on research synthesis
    Context: 2M tokens (full Codex spec + competitive intelligence)
    """

    lord_id = "LORD-002"
    guild_id = "research"
    write_access_tables = ["war_briefs", "research_vectors", "competitor_profiles"]
    model = "o1-preview"

    async def synthesize_war_brief(self, campaign_id: str) -> Dict:
        """
        Aggregate all research guild outputs into unified War Brief.

        Input: Campaign context (personas, positioning, objectives)
        Process:
        1. Command research guild to analyze market
        2. Collect outputs from RES-001 to RES-020
        3. Call o1-preview with full research dataset
        4. Generate structured War Brief
        5. Store to war_briefs table

        Output: War Brief (JSONB)
        {
            "campaign_id": "camp-123",
            "generated_at": "2024-11-27T...",
            "research_sources": ["RES-001", "RES-002", ...],
            "market_analysis": {
                "tam": "...",
                "market_trends": [...],
                "competitive_landscape": {...}
            },
            "persona_deep_dive": {
                "buyer_journey": {...},
                "decision_criteria": [...],
                "objection_patterns": [...]
            },
            "messaging_insights": {
                "top_value_props": [...],
                "proof_points": [...],
                "call_to_action_variants": [...]
            },
            "recommended_channels": [...],
            "confidence_score": 0.87,
            "budget_efficiency": 0.92
        }
        """

        # Get campaign context
        campaign = await supabase.table("campaigns").select(
            "*,positioning(*)"
        ).eq("id", campaign_id).single()

        # Get positioning
        positioning = campaign['positioning']

        # Command research guild
        result = await self.command_guild('research', {
            'command': 'analyze_market',
            'context': {
                'positioning': positioning,
                'personas': ...,  # from DB
                'budget': campaign['budget'],
                'timeline': (campaign['end_date'] - campaign['start_date']).days
            },
            'deadline': 300,  # 5 minutes
            'priority': 'high'
        })

        # Collect research outputs
        research_outputs = await self._collect_research_results(result['request_id'])

        # Prepare RAG context (see Section V)
        rag_context = await self._prepare_rag_context(campaign_id)

        # Call o1-preview with research synthesis prompt
        war_brief = await self.llm.generate(
            model="o1-preview",
            prompt=f"""
            Synthesize comprehensive War Brief for campaign.

            Campaign: {campaign['name']}
            Positioning: {json.dumps(positioning)}

            Research Findings:
            {json.dumps(research_outputs, indent=2)}

            Historical Context (from RAG):
            {json.dumps(rag_context['similar_campaigns'], indent=2)}

            Generate structured War Brief with:
            1. Market Analysis (TAM, trends, competitive landscape)
            2. Persona Deep Dive (buyer journey, decision criteria, objections)
            3. Messaging Insights (value props, proof points, CTAs)
            4. Recommended Channels (with rationale)
            5. Risk Assessment
            """,
            max_tokens=4000,
            temperature=1  # o1-preview required
        )

        # Store War Brief
        await supabase.table("war_briefs").insert({
            "campaign_id": campaign_id,
            "content": war_brief,
            "generated_by": self.lord_id,
            "token_cost": war_brief['usage']['total_tokens'],
            "created_at": datetime.utcnow().isoformat()
        })

        return war_brief
```

#### LORD-003: Strategos
```python
# backend/agents/lords/strategos.py

class Strategos(BaseLord):
    """
    War Room Commander using o1-preview for game theory simulations.

    Responsibilities:
    - Generate "Quests" (multi-step campaigns) from research
    - Run Monte Carlo simulations for campaign outcomes
    - Predict conversion rates from historical data
    - Optimize budget allocation across channels
    - Detect competitive threats via game theory analysis

    Model: o1-preview (OpenAI)
    Context: 1M tokens (competitor data, historical campaigns, market dynamics)
    """

    lord_id = "LORD-003"
    write_access_tables = ["campaign_quests", "strategy_simulations", "budget_allocations"]
    model = "o1-preview"

    async def generate_campaign_quest(self, war_brief: Dict) -> Dict:
        """
        Convert War Brief into multi-step Campaign Quest.

        A "Quest" is a gamified campaign structure:
        {
            "quest_id": "qst-123",
            "title": "Conquer the Enterprise CTO Market",
            "chapters": [
                {
                    "chapter_num": 1,
                    "name": "Awareness Phase",
                    "moves": [...],  # Tactical moves
                    "success_criteria": {...},
                    "xp_reward": 100
                },
                ...
            ],
            "estimated_conversion_rate": 0.12,
            "roi": 3.4,
            "confidence": 0.89,
            "risks": [...]
        }
        """

        # Run Monte Carlo simulation with o1-preview
        simulation_result = await self.llm.generate(
            model="o1-preview",
            prompt=f"""
            Simulate 10,000 campaign outcomes using War Brief data.

            War Brief:
            {json.dumps(war_brief, indent=2)}

            For each simulation iteration:
            1. Vary messaging slightly (A/B test variants)
            2. Simulate different market conditions (3 scenarios)
            3. Calculate expected conversion rate
            4. Track budget efficiency

            Return: {
                "simulations": [
                    {"messaging": "...", "conversion_rate": 0.12, "roi": 3.4},
                    ...
                ],
                "mean_conversion_rate": 0.11,
                "confidence_interval": [0.08, 0.14],
                "recommended_strategy": "..."
            }
            """,
            max_tokens=6000
        )

        # Transform into Quest structure
        quest = {
            "campaign_id": war_brief['campaign_id'],
            "title": f"Quest: {war_brief.get('campaign_name')}",
            "description": war_brief['market_analysis']['summary'],
            "estimated_conversion_rate": simulation_result['mean_conversion_rate'],
            "roi": simulation_result['mean_roi'],
            "confidence": simulation_result['confidence'],
            "chapters": await self._generate_quest_chapters(war_brief, simulation_result),
            "total_xp_potential": 500,
            "created_by": self.lord_id
        }

        # Store Quest
        await supabase.table("campaign_quests").insert(quest)

        return quest

    async def run_game_theory_analysis(self, competitors: List[Dict]) -> Dict:
        """
        Analyze competitive landscape using game theory (Nash equilibrium, etc).
        Useful for: pricing strategy, channel selection, timing
        """

        analysis = await self.llm.generate(
            model="o1-preview",
            prompt=f"""
            Perform game theory analysis on competitive landscape.

            Competitors:
            {json.dumps(competitors, indent=2)}

            Determine:
            1. Nash Equilibrium strategies (what will competitors do?)
            2. Our optimal counter-strategy
            3. First-mover advantage estimation
            4. Risk of competitor retaliation

            Return strategic recommendations.
            """,
            max_tokens=4000
        )

        return analysis
```

#### LORD-004: Aesthete
```python
# backend/agents/lords/aesthete.py

class Aesthete(BaseLord):
    """
    Creative Director commanding Muse Guild (MUS-001 to MUS-030).

    Responsibilities:
    - Orchestrate creative asset generation (text, visual, video)
    - Enforce brand consistency across all assets
    - Validate generated images against brand guidelines (vision)
    - Manage Canva template selection and autofill
    - Run asset debate/critique loops for quality

    Model: gemini-1.5-pro (Google) - 2M token context for brand codex
    Context: Brand guidelines, visual assets, past campaigns, style guide
    """

    lord_id = "LORD-004"
    guild_id = "muse"
    write_access_tables = ["creative_assets", "canva_designs", "brand_deviations"]
    model = "gemini-1.5-pro"

    async def orchestrate_asset_generation(self, war_brief: Dict) -> List[Dict]:
        """
        Generate creative assets for campaign.

        Flow:
        1. Extract creative brief from War Brief
        2. Route to specialized Muse agents (text, visual, video)
        3. Run debate orchestrator for critique
        4. Validate against brand guidelines
        5. Store approved assets
        """

        # Extract creative requirements
        creative_brief = {
            "messaging": war_brief.get('messaging_insights'),
            "personas": war_brief.get('persona_deep_dive'),
            "brand_elements": await self._get_brand_context(),
            "asset_types_needed": ["hero_image", "email_subject", "social_hooks", "landing_page_copy"]
        }

        # Command Muse Guild
        result = await self.command_guild('muse', {
            'command': 'generate_assets',
            'context': creative_brief,
            'deadline': 600,  # 10 minutes
            'priority': 'high'
        })

        # Collect generated assets
        assets = await self._collect_muse_outputs(result['request_id'])

        # Run debate orchestrator for quality check
        debated_assets = await self._run_asset_debate(assets)

        # Validate brand consistency
        validated_assets = await self._validate_brand_consistency(debated_assets)

        # Store approved assets
        for asset in validated_assets:
            await supabase.table("creative_assets").insert({
                "campaign_id": war_brief['campaign_id'],
                "type": asset['type'],
                "content": asset['content'],
                "variants": asset.get('variants', []),
                "quality_score": asset.get('quality_score'),
                "brand_alignment_score": asset.get('brand_alignment'),
                "created_by": self.lord_id
            })

        return validated_assets

    async def select_canva_template(self, asset_brief: Dict) -> str:
        """
        Select best Canva template for asset.

        Algorithm:
        1. Feature extraction (text length, has image?, color palette)
        2. Tag matching from brand_templates table
        3. Sentiment alignment (match brief sentiment to template style)
        4. Freshness constraint (avoid templates used < 7 days)
        5. Return top candidate
        """

        # Use gemini-1.5-pro to analyze template options
        recommendation = await self.llm.generate(
            model="gemini-1.5-pro",
            prompt=f"""
            Select best Canva template for asset.

            Asset Brief:
            {json.dumps(asset_brief, indent=2)}

            Available Templates (with tags and previews):
            {json.dumps(await self._get_available_templates(asset_brief), indent=2)}

            Choose template that:
            1. Matches sentiment of copy
            2. Aligns with brand visual identity
            3. Hasn't been used in last 7 days
            4. Supports required asset dimensions

            Return: template_id and rationale
            """,
            max_tokens=1000
        )

        return recommendation['template_id']
```

#### LORD-005: Seer
```python
# backend/agents/lords/seer.py

class Seer(BaseLord):
    """
    Intelligence Chief monitoring real-time data streams.

    Responsibilities:
    - Command Matrix Guild (MAT-001 to MAT-020)
    - Detect "Newsjacking" opportunities (real-time events)
    - Trigger alerts when sentiment thresholds crossed
    - Monitor competitor activities
    - Detect emerging market trends
    - Feed insights back to campaigns for optimization

    Model: gemini-1.5-flash (Google) - fast, low-cost for high-volume processing
    Context: Market trends, competitor data, sentiment scores
    """

    lord_id = "LORD-005"
    guild_id = "matrix"
    write_access_tables = ["alerts_log", "trend_velocity_metrics", "newsjack_opportunities"]
    model = "gemini-1.5-flash"

    async def monitor_signals(self):
        """
        Subscribe to Matrix Guild broadcasts and process signals.
        """

        async def signal_handler(event, channel):
            signal = event['payload']

            # Process based on signal type
            if signal['signal_type'] == 'competitor_move':
                await self._analyze_competitor_move(signal)
            elif signal['signal_type'] == 'sentiment_shift':
                await self._check_sentiment_threshold(signal)
            elif signal['signal_type'] == 'trend_emerging':
                await self._detect_newsjack_opportunity(signal)
            elif signal['signal_type'] == 'crisis':
                await self._trigger_crisis_response(signal)

        await bus.subscribe_to_alerts(signal_handler)

    async def _detect_newsjack_opportunity(self, signal: Dict) -> Dict:
        """
        When trending topic detected, decide if we should newsjack.

        Process:
        1. Analyze trending topic relevance to our positioning
        2. Check if we can authentically comment
        3. Generate rapid response content
        4. Alert team via Slack/WebSocket
        """

        # Use gemini-1.5-flash for rapid analysis
        analysis = await self.llm.generate(
            model="gemini-1.5-flash",
            prompt=f"""
            Newsjack opportunity analysis.

            Trending: {signal['topic']}
            Relevance Score: {signal['relevance_to_our_niche']}

            Questions:
            1. Can we authentically comment?
            2. Does it align with our positioning?
            3. What's the viral potential?
            4. How quickly do we need to act?

            If viable, generate rapid response tweet/LinkedIn post.
            """,
            max_tokens=500
        )

        if analysis.get('recommend_newsjack'):
            # Create urgent alert
            await bus.publish_event(
                channel="sys.alert.critical",
                event_type="newsjack_opportunity",
                payload={
                    "opportunity": signal['topic'],
                    "response": analysis['suggested_content'],
                    "urgency": "high",
                    "expires_in_minutes": 60
                },
                priority="critical"
            )

            # Notify team via WebSocket
            await self._broadcast_to_dashboard({
                "type": "newsjack_alert",
                "data": analysis
            })
```

#### LORD-006: Arbiter
```python
# backend/agents/lords/arbiter.py

class Arbiter(BaseLord):
    """
    Compliance Officer and gatekeeper to social media APIs.

    Responsibilities:
    - Command Guardian Agents (GRD-001 to GRD-010)
    - Enforce platform limits (character counts, media limits, hashtag counts)
    - Reject content with banned terms or hallucinations
    - Validate URLs before publishing
    - Manage API keys securely
    - Audit all published content

    Security Note:
    - Only Lord with direct write-access to social_media_api_keys table
    - All other Lords must request content through Arbiter
    - API rate limits enforced at Lord level
    """

    lord_id = "LORD-006"
    write_access_tables = ["social_media_api_keys", "content_audit_log", "approval_flags"]

    async def validate_content_for_platform(
        self,
        content: str,
        platform: str,
        asset_id: str
    ) -> Dict:
        """
        Multi-layer validation before content is published.

        Layers:
        1. Invoke Guardian agents (format, limits, terms)
        2. Check for hallucinations (fact verification)
        3. Verify URLs (no broken links)
        4. Audit logging
        5. Approval gate (manual if high-risk)

        Return: {
            "status": "APPROVED" | "REJECTED" | "NEEDS_REVIEW",
            "issues": [...],
            "approved_by": "LORD-006",
            "timestamp": "..."
        }
        """

        validation_result = {
            "asset_id": asset_id,
            "platform": platform,
            "validation_layers": []
        }

        # Layer 1: Guardian agent validation
        guardian_agent = self._get_guardian_for_platform(platform)
        guardian_result = await guardian_agent.validate(content, platform)
        validation_result['validation_layers'].append(guardian_result)

        if not guardian_result['passed']:
            return {
                "status": "REJECTED",
                "issues": guardian_result['violations'],
                "approved_by": self.lord_id
            }

        # Layer 2: Hallucination detection
        hallucination_check = await self._check_hallucinations(content)
        validation_result['validation_layers'].append(hallucination_check)

        if hallucination_check['has_hallucinations']:
            return {
                "status": "NEEDS_REVIEW",
                "issues": ["Potential hallucinations detected"],
                "approved_by": "MANUAL_REVIEW_REQUIRED"
            }

        # Layer 3: URL validation
        if any(url in content for url in self._extract_urls(content)):
            url_check = await self._verify_urls(content)
            validation_result['validation_layers'].append(url_check)

        # If all layers pass
        return {
            "status": "APPROVED",
            "issues": [],
            "approved_by": self.lord_id,
            "timestamp": datetime.utcnow().isoformat()
        }
```

#### LORD-007: Herald
```python
# backend/agents/lords/herald.py

class Herald(BaseLord):
    """
    UI/Gamification bridge translating system logs into narrative updates.

    Responsibilities:
    - Monitor campaign and quest completions
    - Trigger WebSocket events for XP gains, level-ups, achievements
    - Generate achievement unlocks with narrative
    - Create dashboard notifications
    - Maintain user engagement through storytelling

    Model: llama-3.1-70b via Groq (fast, narrative-focused)
    """

    lord_id = "LORD-007"
    write_access_tables = ["user_achievements", "notifications", "user_stats"]
    model = "llama-3.1-70b"  # via Groq for speed

    async def monitor_completions(self):
        """
        Watch for campaign/move completions and trigger achievements.
        """

        # Subscribe to state updates
        async def state_handler(event):
            state_type = event['payload'].get('type')

            if state_type == 'campaign_completed':
                await self._handle_campaign_completion(event['payload'])
            elif state_type == 'move_completed':
                await self._handle_move_completion(event['payload'])
            elif state_type == 'quest_chapter_complete':
                await self._handle_quest_milestone(event['payload'])

        await bus.subscribe_to_alerts(state_handler)

    async def _handle_campaign_completion(self, payload: Dict):
        """
        Campaign finished - unlock achievement, award XP, update level.
        """

        campaign_id = payload['campaign_id']
        user_id = payload['user_id']
        results = payload.get('results', {})

        # Calculate XP based on campaign performance
        xp_earned = self._calculate_xp(results)

        # Check for achievement unlocks
        achievements = await self._check_achievements(user_id, campaign_id, results)

        # Generate narrative for dashboard
        narrative = await self.llm.generate(
            model="llama-3.1-70b",
            prompt=f"""
            Generate short, engaging narrative (1-2 sentences) for achievement unlock.

            Achievement: {achievements[0]['name']}
            Campaign Results: {json.dumps(results)}

            Tone: Heroic but helpful. Reference the Codex/Kingdom metaphor.
            Example: "Your campaign conquered the market! You've unlocked the 'Conqueror' achievement."
            """,
            max_tokens=100
        )

        # Award achievements
        for achievement in achievements:
            await supabase.table("user_achievements").insert({
                "user_id": user_id,
                "achievement_id": achievement['id'],
                "unlocked_at": datetime.utcnow().isoformat(),
                "narrative": narrative
            })

        # Update user stats
        current_stats = await supabase.table("user_stats").select("*").eq("user_id", user_id).single()
        new_level = self._calculate_level(current_stats['total_xp'] + xp_earned)

        await supabase.table("user_stats").update({
            "total_xp": current_stats['total_xp'] + xp_earned,
            "level": new_level,
            "last_milestone": datetime.utcnow().isoformat()
        }).eq("user_id", user_id)

        # Broadcast WebSocket event to frontend
        await self._broadcast_to_user(user_id, {
            "type": "achievement_unlocked",
            "achievement": achievements[0],
            "xp_earned": xp_earned,
            "new_level": new_level,
            "narrative": narrative
        })
```

---

## V. RAG SYSTEM: FULL CONTEXT INJECTION

### A. Vector Embedding Strategy

```python
# backend/services/rag_manager.py

class RAGManager:
    """
    Retrieval-Augmented Generation for agent context.

    Embeds:
    - Codex spec (70 pages) - system design, agent descriptions
    - Historical campaign results - what worked, ROI patterns
    - Competitive intelligence - how competitors positioned
    - Research artifacts - market analysis from past projects
    - Message architecture library - proven positioning statements
    - Asset library - top-performing creative

    Retrieval: Vector similarity + semantic search
    """

    def __init__(self):
        self.chromadb_client = chromadb.Client()
        self.embedding_model = "text-embedding-3-small"  # OpenAI
        self.retrieval_temperature = 0.0  # Deterministic for retrieval

    async def index_codex(self, codex_text: str, workspace_id: str = "global"):
        """
        Split Codex into chunks and index with embeddings.

        Chunking strategy:
        - Section-level chunks (Agent descriptions, workflow steps)
        - Overlap window (20% between chunks for context)
        - Metadata tagging (agent_id, guild, category)
        """

        chunks = self._chunk_codex(codex_text, chunk_size=1000, overlap=200)

        collection = self.chromadb_client.get_or_create_collection(
            name=f"codex_ws_{workspace_id}",
            metadata={"description": "RaptorFlow Codex specification"}
        )

        for i, chunk in enumerate(chunks):
            embedding = await self._get_embedding(chunk['text'])

            collection.add(
                ids=[f"codex_chunk_{i}"],
                embeddings=[embedding],
                metadatas=[{
                    "source": "codex",
                    "section": chunk['section'],
                    "agent_id": chunk.get('agent_id'),
                    "guild": chunk.get('guild')
                }],
                documents=[chunk['text']]
            )

    async def index_campaign_results(self, campaign_result: Dict, workspace_id: str):
        """
        After campaign completes, index results for future retrieval.
        """

        result_text = f"""
        Campaign: {campaign_result['name']}
        Positioning: {campaign_result['positioning']['statement']}
        Persona: {campaign_result['target_persona']['name']}
        Channels: {', '.join(campaign_result['channels'])}

        Results:
        - Conversions: {campaign_result['conversions']}
        - Conversion Rate: {campaign_result['conversion_rate']}
        - ROI: {campaign_result['roi']}
        - Cost per Conversion: {campaign_result['cost_per_conversion']}
        - Key Success Factors: {campaign_result['success_factors']}
        - What Didn't Work: {campaign_result['failures']}
        """

        collection = self.chromadb_client.get_or_create_collection(
            name=f"campaigns_ws_{workspace_id}"
        )

        embedding = await self._get_embedding(result_text)
        collection.add(
            ids=[f"campaign_{campaign_result['id']}"],
            embeddings=[embedding],
            metadatas=[{
                "campaign_id": campaign_result['id'],
                "roi": campaign_result['roi'],
                "conversion_rate": campaign_result['conversion_rate'],
                "date": campaign_result['completion_date']
            }],
            documents=[result_text]
        )

    async def retrieve_context(
        self,
        query: str,
        workspace_id: str,
        context_type: str = "all",  # codex, campaigns, competitors, research
        top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant context chunks for agent.

        Used by: Any agent needing context
        Query examples:
        - "How should we approach CTOs?" → retrieves related personas, successful campaigns
        - "What's the process for campaign creation?" → retrieves codex sections
        - "How did positioning work for similar companies?" → retrieves competitor intel
        """

        collections_to_search = {
            "all": ["codex", "campaigns", "competitors", "research"],
            "codex": ["codex"],
            "campaigns": ["campaigns"],
            "competitors": ["competitors"],
            "research": ["research"]
        }[context_type]

        results = []

        for collection_name in collections_to_search:
            try:
                collection = self.chromadb_client.get_collection(
                    name=f"{collection_name}_ws_{workspace_id}"
                )

                query_embedding = await self._get_embedding(query)

                search_results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where={"relevance": {"$gt": 0.6}}
                )

                # Format results
                for i, doc in enumerate(search_results['documents'][0]):
                    results.append({
                        "collection": collection_name,
                        "content": doc,
                        "similarity": search_results['distances'][0][i],
                        "metadata": search_results['metadatas'][0][i]
                    })
            except Exception as e:
                # Collection might not exist
                pass

        # Sort by similarity
        results.sort(key=lambda x: x['similarity'])

        return results[:top_k]

    async def inject_context_into_prompt(
        self,
        agent_task: str,
        workspace_id: str,
        context_type: str = "all"
    ) -> str:
        """
        Take agent task and augment with retrieved context.

        Example input:
        agent_task = "Generate campaign for Enterprise CTOs"

        Example output:
        """
        Generate campaign for Enterprise CTOs.

        Relevant Context from Historical Campaigns:

        [Similar Campaign 1]
        - Positioning statement: "..."
        - What worked: [key factors]
        - ROI: 3.2x

        [Similar Campaign 2]
        - ...

        Related Codex Section (Agent Selection):
        [Relevant agent descriptions]

        Apply these lessons when generating your campaign.
        """
        """

        # Retrieve context
        context_chunks = await self.retrieve_context(
            agent_task,
            workspace_id,
            context_type=context_type,
            top_k=3
        )

        # Format into prompt injection
        context_text = "Relevant Context:\n\n"
        for chunk in context_chunks:
            context_text += f"[{chunk['collection'].upper()}]\n"
            context_text += chunk['content']
            context_text += "\n\n"

        augmented_prompt = f"""
        Task: {agent_task}

        {context_text}

        Use the above context to improve your analysis and output.
        """

        return augmented_prompt
```

### B. RAG Integration Points

| Agent | Context Type | Usage |
|-------|--------------|-------|
| RES-020 (Synthesis Engine) | codex + campaigns + research | Aggregate research findings |
| LORD-003 (Strategos) | campaigns + competitors | Game theory analysis |
| LORD-004 (Aesthete) | campaigns + assets + codex | Template selection, brand validation |
| MUS-026 (The Editor) | campaigns + assets | Content editing guidance |
| LORD-002 (Cognition) | codex + research + campaigns | War Brief synthesis |

---

## VI. GUILD SPECIFICATIONS

### A. RESEARCH GUILD (RES-001 to RES-020)

#### Data Collection Strategy
```
All research data flows through:
1. Collection (agents scrape, query APIs)
2. Embedding (vector embeddings stored in ChromaDB)
3. Aggregation (RES-020 synthesis or LORD-002 aggregation)
4. Storage (Supabase research_vectors, competitor_profiles tables)
5. Retrieval (RAG system pulls for future campaigns)
```

#### Agent Breakdown (20 specialized agents)

| Agent | Tool | Input | Output | Cost |
|-------|------|-------|--------|------|
| RES-001: Competitor Spy | SerperDev, SHA-256 | Competitor domains | Price changes, feature releases | Low |
| RES-002: SEO Archaeologist | Ahrefs/SEMrush | Niche keywords | Zero-volume, high-intent keywords | Med |
| RES-003: Trend Surfer | Google Trends API | Industry keywords | Correlated cultural events | Low |
| RES-004: Voice of Customer | G2/Capterra scraper | Product category | Customer pain points, reviews | Low |
| RES-005: Shadow Cartographer | CRM API | Email inbox | Decision influencers, buying group | Med |
| RES-006: Tech Stack Detective | BuiltWith API | Competitor domain | Technology stack, integrations | Low |
| RES-007: Influencer Scout | Social Graph API | Industry keywords | Micro-influencers, thought leaders | Med |
| RES-008: Content Auditor | Scrapy + BeautifulSoup | Competitor domains | Content calendar, formats, topics | Low |
| RES-009: Sentiment Miner | NLTK, TextBlob | Social/review data | Sentiment trends, pain points | Low |
| RES-010: Backlink Hunter | Moz API | Competitor domains | High-authority linking sites | Med |
| RES-011: UX Critiquer | Selenium + Vision | Competitor URLs | UX issues, design patterns | Low |
| RES-012: News Junkie | NewsAPI | Industry keywords | Recent announcements, trends | Low |
| RES-013: Forum Lurker | Discourse scraper | Forum URLs | User questions, common issues | Low |
| RES-014: Patent Watcher | USPTO API | Company/keywords | Patent filings, tech moats | Low |
| RES-015: Pricing Analyst | Custom scraper | Pricing pages | Price history, features matrix | Low |
| RES-016: Ad Creative Spy | FB Ad Library + Vision | Competitor accounts | Winning ad creatives, hooks | Med |
| RES-017: Persona Simulator | Internal simulation | Persona description | Realistic persona responses | Low |
| RES-018: Keyword Clusterer | Pandas/SciKit | Keyword list | Semantic clusters, themes | Low |
| RES-019: Offer Deconstructor | Funnel analyzer | Landing pages | Offer structure, scarcity tactics | Low |
| RES-020: Synthesis Engine | o1-preview | All research outputs | Cohesive "War Brief" | High |

### B. MUSE GUILD (MUS-001 to MUS-030)

#### Workflow: Draft → Debate → Revision → Final

```
MUS-002 (Long-Form Weaver) generates Draft_V1
    ↓
Panel Critique: [MUS-026 Editor, RES-002 SEO, LORD-006 Arbiter]
    Each evaluates on different criteria
    ↓
Aggregate Feedback (scored 1-10)
    ↓
If Score < 8:
    MUS-002 generates Draft_V2 (with chain-of-thought revision note)
    Loop up to 3 iterations
    ↓
Final Draft stored with revision history
```

### C. MATRIX GUILD (MAT-001 to MAT-020)

#### Real-Time vs Batch Intelligence

```
REAL-TIME AGENTS (Running 24/7, lightweight)
├─ MAT-001: Google News Watcher (NewsAPI, 15min)
├─ MAT-002: Twitter Streamer (Twitter API, real-time)
├─ MAT-003: Reddit Monitor (PRAW, 1 hour)
└─ MAT-004: Competitor Site Tracker (ChangeDetection.io, 6 hours)

All publish to: sys.guild.matrix.broadcast → sys.state.update → Dashboard

BATCH AGENTS (Run nightly via Vertex AI Pipeline)
├─ MAT-013: Podcast Transcriber (Whisper, weekly)
├─ MAT-009: Keyword Volatility (SEMrush, daily)
└─ MAT-014-020: Various batch jobs

All results stored in: intelligence_logs table
Queryable by RAG system for trend analysis
```

#### Signal-to-Alert Pipeline

```
Raw Signal (e.g., Tweet)
    ↓
[Relevance Filter]
    - Is author verified user?
    - Do they have 500+ followers?
    - Mentions our industry/keywords?
    ↓ (No: discard)
    ↓ (Yes: continue)
[Enrichment]
    - Query Supabase: Is author a customer/prospect?
    - Historical context: Have we seen similar signals?
    - Sentiment score (VADER, TextBlob)
    ↓
[Routing]
    If sentiment < -0.8:
        → sys.alert.critical (crisis)
    If sentiment > 0.8 AND followers > 10k:
        → LORD-005 (opportunity)
    Else:
        → intelligence_logs (standard archival)
```

### D. GUARDIAN GUILD (GRD-001 to GRD-010)

#### Platform-Specific Enforcers

```python
# backend/agents/guardians/grd_tw_twitter.py

class TwitterGuardian(BaseGuardian):
    platform = "twitter"
    hard_limit = 280  # Standard user
    soft_limit = 260  # Warning threshold
    premium_hard_limit = 25000

    def enforce_brevity(self, content: str) -> Dict:
        if len(content) > self.hard_limit:
            return {
                "status": "REJECTED",
                "issue": f"Exceeds {self.hard_limit} character limit",
                "current_length": len(content),
                "action_required": "Summarize"
            }
        elif len(content) > self.soft_limit:
            return {
                "status": "WARNING",
                "issue": "Approaching character limit",
                "action_required": "UserApprovalRequired"
            }
        return {"status": "PASSED"}
```

Each Guardian can:
- Enforce character/media limits
- Check for banned hashtags or terms
- Validate media aspect ratios
- Verify URL shortening
- Check for required disclosures (influencer ads, etc)

---

## VII. MANIACAL ONBOARDING GRAPH

### 12-Step Deterministic Workflow

```python
# backend/graphs/maniacal_onboarding_graph.py

maniacal_onboarding_nodes = [
    ("step_1_dns_verification", "Verify domain ownership", RES-006),
    ("step_2_brand_voice", "Calibrate brand voice & tone", RES-008),
    ("step_3_competitor_identify", "Identify direct competitors", RES-002),
    ("step_4_technographic", "Profile competitor tech stack", RES-006),
    ("step_5_social_footprint", "Map social presence", RES-001),
    ("step_6_review_ingestion", "Ingest customer reviews/testimonials", RES-004),
    ("step_7_pain_extraction", "Extract ICP pain points", RES-020),
    ("step_8_keyword_gap", "Keyword gap analysis", RES-002),
    ("step_9_icp_hypothesis", "Generate ICP hypothesis", RES-005),
    ("step_10_content_audit", "Audit existing content", RES-008),
    ("step_11_visual_baseline", "Establish visual brand baseline", RES-011),
    ("step_12_war_brief", "Generate War Brief", LORD-002),
]

# Each step:
# 1. Executes deterministically
# 2. Stores result to Supabase with checkpoint ID
# 3. Can resume from any checkpoint if interrupted
# 4. Feeds data to next step
# 5. Total time: ~10-15 minutes depending on API latency
```

---

## VIII. DATABASE SCHEMA EXTENSIONS

### New Tables (30+)

```sql
-- COUNCIL OF LORDS & AGENTS
CREATE TABLE agents (
    id VARCHAR(20) PRIMARY KEY,  -- LORD-001, RES-001, etc
    name VARCHAR(100),
    guild VARCHAR(20),  -- COUNCIL, RESEARCH, MUSE, MATRIX, GUARDIANS
    tier VARCHAR(20),  -- SUPERVISOR, SPECIALIST
    model VARCHAR(100),
    status VARCHAR(20) DEFAULT 'IDLE',
    last_heartbeat TIMESTAMP DEFAULT NOW(),
    total_tasks_completed INT DEFAULT 0,
    total_tokens_used INT DEFAULT 0,
    average_quality_score NUMERIC(3,2),
    write_access_tables TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- RAG: Vector embeddings storage
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(20) REFERENCES agents(id),
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- OpenAI text-embedding-3-small
    metadata JSONB,  -- {collection, source, relevance_score}
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    accessed_count INT DEFAULT 0,
    last_accessed TIMESTAMP
);

-- STRATEGIC POSITIONING
CREATE TABLE positioning (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    name VARCHAR(200),
    problem_statement TEXT,
    for_whom TEXT,
    category_frame TEXT,
    differentiator TEXT,
    reason_to_believe TEXT,
    competitive_alternative TEXT,
    message_variants JSONB,  -- {tagline, elevator_pitch, narrative}
    confidence_score NUMERIC(3,2),
    is_active BOOLEAN DEFAULT false,
    validated_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- CAMPAIGNS (Strategic objectives)
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    name VARCHAR(200) NOT NULL,
    positioning_id UUID REFERENCES positioning(id),
    objective_type VARCHAR(50),  -- awareness, consideration, conversion, retention, advocacy
    objective_metric VARCHAR(100),  -- e.g., "50 demo requests"
    objective_value NUMERIC,
    target_cohort_id UUID REFERENCES cohorts(id),
    budget NUMERIC,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'planning',  -- planning, active, paused, completed, archived
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- WAR BRIEFS (Aggregated research)
CREATE TABLE war_briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    content JSONB,  -- Full structured intelligence
    generated_by VARCHAR(20),  -- LORD-002 or agent ID
    confidence_score NUMERIC(3,2),
    token_cost INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- CAMPAIGN QUESTS (Gamified multi-step campaigns)
CREATE TABLE campaign_quests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    title VARCHAR(200),
    description TEXT,
    chapters JSONB,  -- [{chapter_num, name, moves, success_criteria, xp_reward}]
    estimated_conversion_rate NUMERIC(5,4),
    estimated_roi NUMERIC(6,2),
    confidence NUMERIC(3,2),
    total_xp_potential INT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- CREATIVE ASSETS (Generated content)
CREATE TABLE creative_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    move_id UUID REFERENCES moves(id),
    type VARCHAR(50),  -- email_subject, social_hook, hero_image, etc
    content TEXT,
    variants JSONB,  -- [{text, score}]
    quality_score NUMERIC(3,2),
    brand_alignment_score NUMERIC(3,2),
    created_by VARCHAR(20),  -- Agent or user ID
    approved_by VARCHAR(20),  -- Guardian agent or user
    approval_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- INTELLIGENCE LOGS (Matrix Guild outputs)
CREATE TABLE intelligence_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    signal_type VARCHAR(50),  -- competitor_move, sentiment_shift, trend_emerging, crisis
    source VARCHAR(50),  -- agent_id or API name
    content JSONB,
    relevance_score NUMERIC(3,2),
    sentiment NUMERIC(4,2),  -- -1.0 to 1.0
    severity VARCHAR(20),  -- low, medium, high, critical
    requires_action BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- GAMIFICATION: Achievements
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    code VARCHAR(50) UNIQUE,
    name VARCHAR(100),
    description TEXT,
    xp_value INT DEFAULT 100,
    icon_url TEXT,
    unlock_condition JSONB,  -- {event_type, trigger, value}
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_achievements (
    user_id UUID REFERENCES auth.users(id),
    achievement_id UUID REFERENCES achievements(id),
    unlocked_at TIMESTAMP DEFAULT NOW(),
    narrative TEXT,  -- Story behind unlock
    metadata JSONB,
    PRIMARY KEY (user_id, achievement_id)
);

CREATE TABLE user_stats (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id),
    workspace_id UUID REFERENCES workspaces(id),
    current_streak INT DEFAULT 0,
    total_xp INT DEFAULT 0,
    level INT DEFAULT 1,
    last_login_at TIMESTAMP,
    last_milestone_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ALERTS (Real-time notifications)
CREATE TABLE alerts_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    alert_type VARCHAR(50),  -- newsjack_opportunity, crisis, competitor_move, etc
    severity VARCHAR(20),  -- low, medium, high, critical
    content JSONB,
    action_required BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    acknowledged_at TIMESTAMP,
    acknowledged_by UUID REFERENCES auth.users(id)
);

-- TREND VELOCITY METRICS
CREATE TABLE trend_velocity_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    trend_name VARCHAR(200),
    current_velocity NUMERIC(10,2),  -- Growth rate
    previous_velocity NUMERIC(10,2),
    acceleration NUMERIC(10,2),  -- Change in velocity
    predicted_peak_date DATE,
    newsjack_opportunity_score NUMERIC(3,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## IX. COST OPTIMIZATION: $10/USER/MONTH TARGET

### Token Budget Strategy

```
Target: $10/user/month
Assumptions:
- Average LLM cost: $0.005 per 1K tokens
- User makes 20 campaigns/month
- Each campaign uses ~40K tokens (research + strategy + content)
- Total tokens/user: 800K/month
- Cost: 800K * $0.005 / 1000 = $4 (research + strategy)

Remaining budget: $6 for:
- Canva API calls ($0.20/job)
- External API usage (SEMrush, Ahrefs - amortized)
- Vector embeddings (low cost with caching)
```

### Optimization Tactics

```python
# 1. MODEL SELECTION
# Use cheapest model that works
o1-preview: Only for synthesis & game theory (1-2 calls/campaign)
gemini-2.5-flash: Default for research, analytics, matrix
claude-haiku: Small tasks, fast creative iterations
llama-3.1-70b: Narrative generation (cheapest + fast)

# 2. AGGRESSIVE CACHING
CACHE_TTL = {
    "personas": 30 * 24 * 3600,  # 30 days (they don't change)
    "competitor_profiles": 7 * 24 * 3600,  # 7 days
    "market_analysis": 3 * 24 * 3600,  # 3 days
    "creative_assets": 24 * 3600,  # 1 day (expiration when campaign ends)
    "research_vectors": 30 * 24 * 3600  # 30 days (reference data)
}

# 3. BATCH PROCESSING
# Instead of real-time:
# - Run research in batches (1x/day instead of real-time)
# - Batch intelligence agent analysis
# - Group similar queries to leverage caching

# 4. APPROXIMATION FOR LOW-STAKES TASKS
# Use simpler models:
# - URL validation: Regex instead of LLM
# - Formatting checks: Guardian agents (logic-based, no LLM)
# - Template selection: Similarity matching instead of LLM analysis

# 5. CONTEXT WINDOW OPTIMIZATION
# Pre-slice large contexts to fit token budgets
# Use RAG to inject only relevant context (not full Codex)
# Compress historical data using summarization

# 6. REQUEST DEDUPLICATION
# Check Redis cache before calling LLM
# If similar query run < 1 hour ago, return cached result
# Vector similarity search for query dedup

# 7. USER-TIER BASED BUDGETS
free_tier = 100_000 tokens/month (heavy caching, simplified paths)
pro_tier = 500_000 tokens/month (standard)
enterprise_tier = 2_000_000 tokens/month (unlimited o1-preview, real-time)

# 8. EXTERNAL API OPTIMIZATION
# SEMrush, Ahrefs: Share subscriptions across users
# Cache results: Don't re-query same keywords
# Batch APIs: Pull multiple analyses in one call
```

---

## X. FRONTEND INTEGRATION MAP

### New Pages to Build/Extend

```
Existing Pages to Integrate Codex:
├─ Dashboard.jsx
│   └─ Add: Throne Room redesign (Kingdom metaphor)
│   └─ Add: Real-time agent status widget
│   └─ Add: Alerts from Matrix Guild
│   └─ Add: XP/achievement progress
│
├─ Cohorts.jsx
│   └─ Extend: Add 7 new strategic attributes UI
│   └─ Add: Buying triggers calendar
│   └─ Add: Decision criteria weighted matrix
│   └─ Add: Objection mapping (objection → response asset)
│
└─ Moves.jsx
    └─ Extend: Show linked campaign for each move
    └─ Add: Suggested moves from Strategos

New Pages to Create:
├─ /strategy/positioning-workshop
│   └─ 5-step wizard (who/problem/us/proof/messaging)
│   └─ Integrated competitive analysis (calls LORD-002)
│
├─ /campaigns/builder
│   └─ 5-step campaign orchestration
│   └─ Auto-suggested Moves from LORD-003
│   └─ Budget allocation by channel
│
├─ /muse/studio
│   └─ Asset gallery with filters
│   └─ Version history per asset
│   └─ Debate/revision comments
│   └─ Live Canva template preview
│
├─ /matrix/radar
│   └─ Live 2D intelligence dashboard
│   └─ Real-time alert notifications
│   └─ Trend velocity visualizations
│   └─ Newsjack opportunity banners
│
└─ /quests
    └─ Active quests with chapter progress
    └─ Achievement showcase
    └─ XP & level progress
```

### WebSocket Real-Time Events

```javascript
// Frontend subscribes to:
ws.on('campaign:created', (campaign) => {
    // Update dashboard, highlight in sidebar
})

ws.on('asset:generated', (asset) => {
    // Notify Muse Studio subscribers
    // Show "New asset ready" toast
})

ws.on('alert:newsjack', (opportunity) => {
    // Show critical banner in dashboard
    // "Trending: [topic] - Create response? [Yes] [No]"
})

ws.on('achievement:unlocked', (achievement) => {
    // Overlay toast with narrative
    // "+ 100 XP" animation
    // Level progress bar update
})

ws.on('agent:heartbeat', (agent_status) => {
    // Update "Agent Status" widget in dashboard
    // Show which agents are busy
})
```

---

## XI. IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Weeks 1-4)
- [ ] RaptorBus implementation (Redis Pub/Sub)
- [ ] Base Lord classes (BaseLord, permission system)
- [ ] Database migrations (all new tables)
- [ ] RAG system (ChromaDB, embedding pipeline)

### Phase 2: Council of Lords (Weeks 5-8)
- [ ] LORD-001 Architect (health monitoring)
- [ ] LORD-002 Cognition (Research aggregation)
- [ ] LORD-003 Strategos (Strategy generation)
- [ ] Tests for Lord-Guild communication

### Phase 3: Research Guild (Weeks 9-12)
- [ ] RES-001 to RES-010 (10 basic agents)
- [ ] Maniacal Onboarding Graph (12 steps)
- [ ] War Brief generation
- [ ] Tests for research pipeline

### Phase 4: Creative & Intelligence (Weeks 13-18)
- [ ] Muse Guild (MUS-001 to MUS-030)
- [ ] Matrix Guild (MAT-001 to MAT-020)
- [ ] Guardian Guild (GRD-001 to GRD-010)
- [ ] Integration tests for full pipelines

### Phase 5: Frontend & Real-Time (Weeks 19-22)
- [ ] Throne Room Dashboard redesign
- [ ] Positioning Workshop UI
- [ ] Campaign Builder UI
- [ ] Muse Studio interface
- [ ] Radar Module dashboard
- [ ] WebSocket integration

### Phase 6: External APIs & Polish (Weeks 23-26)
- [ ] Canva integration
- [ ] SEMrush/Ahrefs wrappers
- [ ] NewsAPI integration
- [ ] Cost monitoring & optimization

### Phase 7: Gamification & Launch (Weeks 27-30)
- [ ] Gamification system (XP, levels, achievements)
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Documentation & deployment

---

## XII. SUCCESS METRICS

### System Metrics
- **Agent uptime:** > 99.5%
- **Average request latency:** < 5s
- **Token cost per campaign:** < $0.50
- **Heartbeat response time:** < 100ms

### Business Metrics
- **Time to create campaign:** < 15 minutes
- **Campaign conversion improvement:** +30% vs. baseline
- **Content quality score:** > 8/10 (human review)
- **User engagement (gamification):** > 40% daily active users

### Cost Metrics
- **Cost per user per month:** < $10
- **Cost per campaign:** < $2
- **Cache hit ratio:** > 60%

---

This blueprint is comprehensive. Implement in phases, and adjust based on:
1. Actual token usage (may need to prune agents)
2. API reliability (fallback strategies if APIs fail)
3. User feedback (which features drive engagement)

Ready to implement Phase 1? Start with RaptorBus + Database migrations.
