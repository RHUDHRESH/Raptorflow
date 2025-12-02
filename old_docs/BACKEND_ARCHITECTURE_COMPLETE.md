# Complete Backend Architecture Design
**Status**: 🔴 In Design (0% Implementation)

**Scope**: All 16 core backend systems for 70+ agent autonomous marketing platform
**Team Capacity**: 2-3 full-time backend engineers
**Timeline**: Weeks 1-22 (22 weeks to full implementation)
**Cost Model**: $10/user/month across all systems

---

## PART I: EXECUTIVE ARCHITECTURE OVERVIEW

### System Layers (Bottom to Top)

```
┌─────────────────────────────────────────────────────┐
│         FRONTEND LAYER (React 19 + WebSocket)       │
├─────────────────────────────────────────────────────┤
│         API GATEWAY LAYER (FastAPI)                 │
├─────────────────────────────────────────────────────┤
│    AGENT ORCHESTRATION LAYER (70+ Agents)           │
│    ├─ Council of Lords (7 supervisors)              │
│    ├─ Research Guild (20 agents)                    │
│    ├─ Muse Guild (30 agents)                        │
│    ├─ Matrix Guild (20 agents)                      │
│    └─ Guardian Guild (10 agents)                    │
├─────────────────────────────────────────────────────┤
│    MESSAGE BACKBONE (RaptorBus - Redis Pub/Sub)     │
├─────────────────────────────────────────────────────┤
│    DATA LAYER                                       │
│    ├─ Cache (Redis key-value)                       │
│    ├─ Database (Supabase PostgreSQL)                │
│    ├─ Vector DB (ChromaDB for RAG)                  │
│    └─ External APIs (SEMrush, Ahrefs, NewsAPI)      │
├─────────────────────────────────────────────────────┤
│    INFRASTRUCTURE LAYER                             │
│    ├─ Monitoring & Logging (Datadog/CloudWatch)     │
│    ├─ Cost Tracking                                 │
│    ├─ Error Handling & DLQ                          │
│    └─ Authentication & RBAC                         │
└─────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology | Purpose | Status |
|-------|-----------|---------|--------|
| **API** | FastAPI (async Python) | HTTP endpoint layer | ✅ Ready |
| **Message Bus** | RaptorBus (Redis Pub/Sub) | Agent communication | ✅ Ready |
| **Agent Framework** | LangGraph + Pydantic | Agent lifecycle mgmt | 🔴 Design Only |
| **Database** | Supabase PostgreSQL | Persistent storage (56 tables) | ✅ Schema Ready |
| **Cache** | Redis (Upstash) | Hot data + pub/sub | ✅ RaptorBus Ready |
| **Vector DB** | ChromaDB | RAG embeddings | 🔴 Design Only |
| **Auth** | Supabase Auth + JWT | User management | ✅ Exists |
| **LLM Models** | Vertex AI, Claude, Mistral | AI inference | ✅ Integrated |
| **Deployment** | GCP Cloud Run | Serverless backend | ✅ Ready |
| **Logging** | Structured JSON logs | Debugging & monitoring | 🔴 Design Only |

---

## PART II: CORE SYSTEM DESIGNS (16 Systems)

---

## SYSTEM 1: API LAYER & REQUEST ROUTING

### Purpose
FastAPI application server handling HTTP requests, authentication, and routing to agent orchestration layer.

### Architecture

```
HTTP Request
    ↓
[FastAPI Router] → [Auth Middleware] → [Validation] → [Rate Limiting]
    ↓
[Route Handler] → [Service Layer] → [Agent Orchestration] → [RaptorBus]
    ↓
[Response Formatter] → HTTP Response
```

### Core Files to Create

#### 1. `backend/main.py` - Application Entry Point
```python
# 500 lines
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Routers
from routers import campaigns, moves, agents, intelligence, gamification

# Initialization
async def lifespan(app: FastAPI):
    # Startup
    await init_raptor_bus()
    await init_cache_layer()
    await init_vector_db()
    await init_monitoring()
    yield
    # Shutdown
    await cleanup_raptor_bus()
    await cleanup_cache()

app = FastAPI(
    title="RaptorFlow Codex API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://raptorflow.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(campaigns.router)
app.include_router(moves.router)
app.include_router(agents.router)
app.include_router(intelligence.router)
app.include_router(gamification.router)
```

#### 2. `backend/routers/campaigns.py` - Campaign Endpoints
```python
# 400 lines
from fastapi import APIRouter, Depends, HTTPException
from schemas import CampaignCreate, CampaignResponse
from services import CampaignService
from auth import get_current_user

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

@router.post("/")
async def create_campaign(
    data: CampaignCreate,
    user = Depends(get_current_user)
) -> CampaignResponse:
    """
    Create new campaign with positioning
    - Validates objective type
    - Initializes positioning
    - Dispatches RES-001 (Market Researcher) agent
    - Returns campaign context
    """
    pass

@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    user = Depends(get_current_user)
) -> dict:
    """
    Get campaign with full context:
    - Positioning statement
    - Message architecture
    - Target cohorts
    - Current quests
    - War briefs
    """
    pass

@router.post("/{campaign_id}/generate-brief")
async def generate_war_brief(
    campaign_id: str,
    user = Depends(get_current_user)
) -> dict:
    """
    Dispatch Matrix Guild to generate intelligence brief
    - Analyzes competitive landscape
    - Identifies market shifts
    - Returns actionable insights
    - Stores in war_briefs table
    """
    pass

@router.post("/{campaign_id}/create-quest")
async def create_campaign_quest(
    campaign_id: str,
    quest_data: dict,
    user = Depends(get_current_user)
) -> dict:
    """
    Create gamified campaign milestone (quest)
    - Defines chapters
    - Sets success metrics
    - Dispatches Muse Guild for content
    - Returns quest structure
    """
    pass
```

#### 3. `backend/routers/agents.py` - Agent Management Endpoints
```python
# 300 lines
router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.get("/registry")
async def get_agent_registry(user = Depends(get_current_user)):
    """
    Get all 70+ agents in registry with:
    - Role, guild, capabilities
    - Performance metrics
    - Cost tracking
    - Availability status
    """
    pass

@router.get("/{agent_code}/memories")
async def get_agent_memories(
    agent_code: str,
    query: str,
    user = Depends(get_current_user)
):
    """
    RAG query against agent memories
    - Vector similarity search
    - Returns relevant codex knowledge
    - Filters by memory type
    """
    pass

@router.post("/{agent_code}/invoke")
async def invoke_agent(
    agent_code: str,
    request: dict,
    user = Depends(get_current_user)
):
    """
    Direct agent invocation (for testing/manual)
    - Routes through RaptorBus
    - Tracks cost & performance
    - Waits for response
    """
    pass

@router.get("/council/decisions")
async def get_council_decisions(user = Depends(get_current_user)):
    """
    Get recent Council of Lords decisions
    - Routing decisions
    - Priority overrides
    - Approval logs
    """
    pass
```

#### 4. `backend/middleware/auth.py` - Authentication & Authorization
```python
# 250 lines
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredential
import jwt
from supabase import create_client

# Supabase Auth
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_current_user(credentials: HTTPAuthCredential = Depends(HTTPBearer())):
    """
    Verify JWT token from Supabase Auth
    Extract user_id and workspace_id
    Return user context for RLS enforcement
    """
    try:
        token = credentials.credentials
        user = await verify_jwt_token(token)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

async def verify_workspace_access(
    workspace_id: str,
    user = Depends(get_current_user)
):
    """
    Verify user has access to workspace (via workspace_members)
    Enforce RLS isolation
    """
    pass

async def check_permission(
    required_role: str,
    user = Depends(get_current_user)
):
    """
    RBAC check - verify user has required role
    Roles: admin, lord_operator, analyst, viewer
    """
    pass
```

#### 5. `backend/schemas/` - Pydantic Models
```python
# 400 lines total across multiple files

# schemas/campaigns.py
class CampaignCreate(BaseModel):
    name: str
    objective_type: str  # awareness, consideration, conversion, retention, advocacy
    positioning: PositioningData
    target_cohorts: List[str]
    budget: Optional[float]
    start_date: Optional[date]

class CampaignResponse(BaseModel):
    id: str
    name: str
    status: str  # planning, approved, active, paused, completed
    positioning_id: str
    target_cohorts: List[dict]
    war_briefs: List[dict]
    quests: List[dict]
    created_at: datetime

# schemas/agents.py
class AgentResponse(BaseModel):
    code: str  # LORD-001, RES-005, etc
    name: str
    role: str  # lord, research, muse, matrix, guardian
    guild: str
    capabilities: List[str]
    is_active: bool
    success_rate: float
    avg_response_time_ms: int

# schemas/errors.py
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    request_id: str
    timestamp: datetime
    suggestion: Optional[str]
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | FastAPI | Async-first, auto docs, Pydantic validation |
| Auth | Supabase JWT | Built-in, secure, workspace isolation |
| Rate Limiting | Token bucket | Per-user & per-agent quotas |
| Request Timeout | 30-120s | Long operations OK, prevents hanging |
| Response Format | JSON | Standard, WebSocket-compatible |

### Dependencies
- fastapi==0.104.1
- pydantic==2.5.0
- supabase==2.0.0
- python-jose==3.3.0
- httpx==0.25.0

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 1-2 (40 hours)

---

## SYSTEM 2: AGENT FRAMEWORK & LIFECYCLE

### Purpose
Base classes and utilities for agent creation, lifecycle management, and communication.

### Architecture

```
┌─────────────────────────────────┐
│       BaseAgent (Abstract)       │
│  - execute()                    │
│  - handle_error()               │
│  - track_cost()                 │
│  - emit_event()                 │
└──────────────┬──────────────────┘
               │
    ┌──────────┼──────────┐
    ↓          ↓          ↓
[LordAgent] [GuildAgent] [UtilityAgent]
    │          │          │
    └──────────┼──────────┘
               ↓
    ┌──────────────────────┐
    │   Agent Executor     │
    │  - invoke agent()    │
    │  - handle response() │
    │  - track metrics()   │
    └──────────────────────┘
```

### Core Files to Create

#### 1. `backend/agents/base_agent.py` - Base Agent Class
```python
# 400 lines
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from langchain_core.messages import BaseMessage
import uuid

class AgentContext(BaseModel):
    """Context passed to every agent execution"""
    workspace_id: str
    user_id: str
    request_id: str
    campaign_id: Optional[str]
    parent_agent_code: Optional[str]
    budget_remaining: float

    class Config:
        arbitrary_types_allowed = True

class AgentExecutionResult(BaseModel):
    """Result returned from agent execution"""
    agent_code: str
    status: str  # 'success', 'partial', 'error'
    output: Any
    confidence: float  # 0-1 confidence in result
    tokens_used: int
    cost_cents: float
    execution_time_ms: int
    error: Optional[str]
    traces: Optional[List[dict]]  # Debug traces

class BaseAgent(ABC):
    """
    Abstract base class for all agents
    Enforces consistent interface and tracking
    """

    def __init__(
        self,
        code: str,  # LORD-001, RES-005, etc
        name: str,
        role: str,  # lord, research, muse, matrix, guardian
        guild: str,
        primary_model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system_prompt: str = ""
    ):
        self.code = code
        self.name = name
        self.role = role
        self.guild = guild
        self.primary_model = primary_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt

    async def execute(
        self,
        input_data: dict,
        context: AgentContext
    ) -> AgentExecutionResult:
        """
        Main execution method - all agents must implement
        Handles:
        - Input validation
        - Cost tracking
        - Error handling
        - Response formatting
        """
        request_id = context.request_id
        start_time = datetime.now()

        try:
            # Log execution start
            await self._log_execution_start(request_id)

            # Validate inputs
            await self._validate_inputs(input_data)

            # Get memories (RAG context)
            memories = await self._get_relevant_memories(input_data, context)

            # Build prompt
            prompt = await self._build_prompt(input_data, memories)

            # Call LLM
            response = await self._call_llm(prompt)

            # Parse & validate response
            output = await self._parse_response(response)

            # Track metrics
            tokens_used = self._calculate_tokens(prompt, response)
            cost_cents = self._calculate_cost(tokens_used)

            # Store result
            await self._store_execution_result(
                request_id, output, tokens_used, cost_cents
            )

            return AgentExecutionResult(
                agent_code=self.code,
                status='success',
                output=output,
                confidence=1.0,
                tokens_used=tokens_used,
                cost_cents=cost_cents,
                execution_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )

        except Exception as e:
            return AgentExecutionResult(
                agent_code=self.code,
                status='error',
                output=None,
                confidence=0.0,
                tokens_used=0,
                cost_cents=0,
                execution_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                error=str(e)
            )

    @abstractmethod
    async def _parse_response(self, response: str) -> Any:
        """Subclass-specific response parsing"""
        pass

    async def _validate_inputs(self, input_data: dict):
        """Validate input data structure"""
        if not input_data:
            raise ValueError("Input data cannot be empty")

    async def _get_relevant_memories(
        self,
        input_data: dict,
        context: AgentContext
    ) -> List[dict]:
        """
        Retrieve relevant memories from RAG system
        - Query vector DB (ChromaDB)
        - Filter by memory type
        - Return top-K results with scores
        """
        pass

    async def _build_prompt(
        self,
        input_data: dict,
        memories: List[dict]
    ) -> str:
        """Build LLM prompt with system prompt + context + input"""
        pass

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM (Claude, Gemini, etc) based on model selection"""
        pass

    def _calculate_tokens(self, prompt: str, response: str) -> int:
        """Estimate tokens used (for cost calculation)"""
        # Rough estimate: 1 token ≈ 4 characters
        return (len(prompt) + len(response)) // 4

    def _calculate_cost(self, tokens_used: int) -> float:
        """Calculate cost in cents based on model pricing"""
        # Pricing varies by model - implement per model
        pass

    async def _log_execution_start(self, request_id: str):
        """Log execution start for debugging"""
        pass

    async def _store_execution_result(
        self,
        request_id: str,
        output: Any,
        tokens_used: int,
        cost_cents: float
    ):
        """Store execution metadata in database for tracking"""
        pass
```

#### 2. `backend/agents/lords/base_lord.py` - Lord Agent Base
```python
# 300 lines
from agents.base_agent import BaseAgent, AgentContext, AgentExecutionResult
from typing import List, Dict

class LordCommand(BaseModel):
    """Command issued by a Lord to guilds"""
    guild: str  # research, muse, matrix, guardians
    agent_codes: List[str]  # which agents to invoke
    priority: str  # low, normal, high, critical
    deadline: Optional[datetime]
    context: Dict[str, Any]

class BaseLord(BaseAgent):
    """
    Base class for Council of Lords
    Lords are strategic supervisors with:
    - Cross-guild coordination
    - Decision authority
    - Budget management
    - Strategy oversight
    """

    def __init__(self, code: str, name: str, responsibility: str):
        super().__init__(
            code=code,
            name=name,
            role='lord',
            guild='council',
            primary_model='claude-opus-4-1'
        )
        self.responsibility = responsibility

    async def make_strategic_decision(
        self,
        situation: dict,
        context: AgentContext
    ) -> LordCommand:
        """
        Make strategic decision and issue commands
        - Analyze situation
        - Decide which guilds/agents to invoke
        - Set priorities and deadlines
        - Return command for orchestrator
        """
        pass

    async def approve_guild_output(
        self,
        guild_name: str,
        guild_output: dict,
        context: AgentContext
    ) -> bool:
        """
        Approve or reject output from a guild
        - Verify quality
        - Check alignment with strategy
        - Return approval decision
        """
        pass

    async def allocate_budget(
        self,
        available_budget: float,
        pending_tasks: List[dict],
        context: AgentContext
    ) -> Dict[str, float]:
        """
        Allocate budget across pending tasks
        - Prioritize by strategic importance
        - Account for agent costs
        - Return allocation plan
        """
        pass
```

#### 3. `backend/agents/executor.py` - Agent Executor
```python
# 350 lines
from raptorbus import RaptorBus, BusEvent
from agents.base_agent import BaseAgent, AgentContext, AgentExecutionResult
from database import Database
from cache import Cache

class AgentExecutor:
    """
    Orchestrates agent execution via RaptorBus
    Handles:
    - Agent routing
    - Event dispatch
    - Response collection
    - Error handling & DLQ
    - Cost tracking
    """

    def __init__(self, raptor_bus: RaptorBus, db: Database, cache: Cache):
        self.bus = raptor_bus
        self.db = db
        self.cache = cache
        self.registry = {}  # Agent code -> Agent instance

    async def register_agent(self, agent: BaseAgent):
        """Register an agent in the executor"""
        self.registry[agent.code] = agent

    async def invoke_agent(
        self,
        agent_code: str,
        input_data: dict,
        context: AgentContext,
        wait_for_response: bool = True,
        timeout_seconds: int = 60
    ) -> AgentExecutionResult:
        """
        Invoke an agent with RaptorBus
        - Create event
        - Publish to guild channel
        - Wait for response (optional)
        - Track metrics
        """

        # Create event
        event = BusEvent(
            type='agent_invocation',
            source_agent_id='orchestrator',
            destination_guild=self._get_guild(agent_code),
            payload={
                'agent_code': agent_code,
                'input_data': input_data,
                'context': context.model_dump()
            },
            request_id=context.request_id
        )

        # Publish event
        await self.bus.publish_event(event)

        # Wait for response if requested
        if wait_for_response:
            result = await self._wait_for_response(
                context.request_id,
                timeout_seconds
            )
            return result
        else:
            return AgentExecutionResult(
                agent_code=agent_code,
                status='queued',
                output={'message': 'Agent queued for execution'},
                confidence=0.0,
                tokens_used=0,
                cost_cents=0,
                execution_time_ms=0
            )

    async def invoke_agent_parallel(
        self,
        agent_codes: List[str],
        input_data: dict,
        context: AgentContext,
        timeout_seconds: int = 120
    ) -> Dict[str, AgentExecutionResult]:
        """
        Invoke multiple agents in parallel
        - Dispatch all at once
        - Collect responses
        - Return results dict
        """
        pass

    async def invoke_with_dependencies(
        self,
        agent_dag: Dict[str, List[str]],
        context: AgentContext
    ) -> Dict[str, AgentExecutionResult]:
        """
        Invoke agents with dependency ordering
        - Topological sort
        - Execute in dependency order
        - Pass outputs as inputs to dependents
        """
        pass

    async def _wait_for_response(
        self,
        request_id: str,
        timeout_seconds: int
    ) -> AgentExecutionResult:
        """Poll for agent response"""
        pass

    def _get_guild(self, agent_code: str) -> str:
        """Extract guild from agent code"""
        prefix = agent_code.split('-')[0]
        guild_map = {
            'LORD': 'council',
            'RES': 'research',
            'MUSE': 'muse',
            'MTX': 'matrix',
            'GRD': 'guardians'
        }
        return guild_map.get(prefix, 'research')
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 2-3 (50 hours)

---

## SYSTEM 3: COUNCIL OF LORDS (7 Agents)

### Purpose
High-level strategic decision makers that coordinate and oversee all other agents.

### The 7 Lords

| Code | Name | Responsibility | Model | Decisions |
|------|------|-----------------|-------|-----------|
| **LORD-001** | The Architect | System design & integration | Claude Opus | Route requests, approve architectures |
| **LORD-002** | The Cognition | Learning & knowledge mgmt | Claude Opus | Update RAG, knowledge validation |
| **LORD-003** | The Strategos | Strategic planning | Claude Opus | Campaign strategy, goal setting |
| **LORD-004** | The Aesthete | Creative quality | Claude 4.5 | Content review, brand alignment |
| **LORD-005** | The Seer | Prediction & forecasting | Gemini 2.5 Flash | Forecast results, predict trends |
| **LORD-006** | The Arbiter | Conflict resolution | Claude Opus | Resolve agent disagreements |
| **LORD-007** | The Herald | Communication & reporting | Claude 4.5 | Generate reports, send notifications |

### Design Files to Create

#### `backend/agents/lords/architect.py` - THE ARCHITECT (LORD-001)
```python
# 250 lines
class TheArchitect(BaseLord):
    """
    System architect overseeing all operations
    Responsibilities:
    - Route requests to appropriate guilds
    - Approve major architectural decisions
    - Manage inter-guild coordination
    - Monitor system health
    """

    async def route_request(
        self,
        request: dict,
        context: AgentContext
    ) -> LordCommand:
        """
        Route incoming request to appropriate guild(s)
        - Analyze request type
        - Determine which agents needed
        - Set sequence and priorities
        - Return routing command
        """
        # Example routing logic:
        request_type = request.get('type')

        if request_type == 'new_campaign':
            # Route: RES-001 (researcher) -> MUSE agents (content) -> MTX (analysis)
            return LordCommand(
                guild='research',
                agent_codes=['RES-001'],  # Market researcher
                priority='high',
                context={'campaign_data': request}
            )

        elif request_type == 'competitive_analysis':
            # Route: MTX agents (Matrix) for intelligence
            return LordCommand(
                guild='matrix',
                agent_codes=['MTX-001', 'MTX-002'],  # Intel agents
                priority='normal',
                context=request
            )

        # etc for other request types
        pass

    async def approve_architecture(
        self,
        proposed_architecture: dict,
        context: AgentContext
    ) -> bool:
        """
        Approve or reject proposed system changes
        - Validates against design principles
        - Checks impact on other systems
        - Returns approval decision
        """
        pass

    async def coordinate_guilds(
        self,
        guilds_in_use: List[str],
        shared_context: dict,
        context: AgentContext
    ) -> dict:
        """
        Coordinate between multiple guilds
        - Define interfaces
        - Set handoff points
        - Manage dependencies
        """
        pass
```

#### `backend/agents/lords/cognition.py` - THE COGNITION (LORD-002)
```python
# 250 lines
class TheCognition(BaseLord):
    """
    Learning & knowledge management
    Responsibilities:
    - Maintain and update agent knowledge
    - RAG system management
    - Learning from outcomes
    - Knowledge validation
    """

    async def update_agent_knowledge(
        self,
        agent_code: str,
        new_knowledge: dict,
        context: AgentContext
    ):
        """
        Update agent's knowledge base (RAG)
        - Validate new knowledge
        - Store as embeddings
        - Associate with memory type
        """
        pass

    async def extract_learnings(
        self,
        execution_result: dict,
        context: AgentContext
    ) -> dict:
        """
        Extract learnings from execution result
        - Identify patterns
        - Extract insights
        - Store for future reference
        """
        pass
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 4-7 (80 hours)

---

## SYSTEM 4: RESEARCH GUILD (20 Agents)

### Purpose
Data collection, market research, and intelligence gathering from external sources.

### The 20 Research Agents

```
RES-001: Market Researcher
  ├─ Analyzes target market size, segments, trends
  └─ Uses: SEMrush, SimilarWeb, industry reports

RES-002: Competitor Analyst
  ├─ Researches competitor strategies, positioning, tactics
  └─ Uses: Competitor websites, LinkedIn, Twitter

RES-003: Audience Researcher
  ├─ Digs into persona details, pain points, motivations
  └─ Uses: Survey data, forums, social listening

RES-004: Industry Trend Analyst
  ├─ Identifies emerging trends, disruptors, shifts
  └─ Uses: NewsAPI, industry blogs, research reports

... (16 more specialized researchers)

RES-020: Synthesis Agent
  └─ Aggregates all research into cohesive brief
```

### Design Files to Create

#### `backend/agents/research/base_researcher.py`
```python
# 200 lines
class BaseResearcher(GuildAgent):
    """
    Base class for research agents
    All researchers:
    - Take a topic/target
    - Gather data from sources
    - Analyze and synthesize
    - Return structured findings
    """

    async def research(
        self,
        topic: str,
        context: AgentContext
    ) -> dict:
        """Main research execution"""
        # 1. Gather raw data from sources
        raw_data = await self._gather_data(topic)

        # 2. Clean & structure
        structured_data = await self._structure_data(raw_data)

        # 3. Analyze
        analysis = await self._analyze(structured_data)

        # 4. Extract insights
        insights = await self._extract_insights(analysis)

        return {
            'topic': topic,
            'raw_data': raw_data,
            'analysis': analysis,
            'insights': insights,
            'sources': [...]
        }

    @abstractmethod
    async def _gather_data(self, topic: str) -> List[dict]:
        """Subclass implements specific data gathering"""
        pass
```

#### `backend/agents/research/res_001_market_researcher.py`
```python
# 250 lines
from external_apis import semrush, similarweb, brave_search
from typing import Dict, List

class RES001MarketResearcher(BaseResearcher):
    """RES-001: Market Researcher"""

    async def _gather_data(self, market_query: str) -> List[dict]:
        """
        Gather market data from multiple sources
        Uses:
        - SEMrush: market size, keyword volume, trends
        - SimilarWeb: market position, traffic
        - Google Trends: interest evolution
        - News APIs: recent market developments
        """

        data = []

        # SEMrush market research
        semrush_data = await semrush.market_research(market_query)
        data.append({
            'source': 'semrush',
            'data': semrush_data
        })

        # SimilarWeb market analysis
        similarweb_data = await similarweb.get_market_stats(market_query)
        data.append({
            'source': 'similarweb',
            'data': similarweb_data
        })

        # Google Trends
        trends_data = await brave_search.get_trends(market_query)
        data.append({
            'source': 'google_trends',
            'data': trends_data
        })

        return data

    async def _analyze(self, structured_data: dict) -> dict:
        """
        Analyze market data
        Extract: size, growth rate, segments, opportunities
        """
        analysis = {
            'market_size': ...,
            'growth_rate': ...,
            'segments': [...],
            'opportunities': [...]
        }
        return analysis
```

#### `backend/agents/research/maniacal_onboarding.py`
```python
# 400 lines - The Maniacal Onboarding system (deterministic 12-step workflow)

class ManiacalOnboarding:
    """
    12-step deterministic onboarding workflow
    Creates complete campaign foundation in sequence:

    Steps 1-3: Understanding the Customer
    Steps 4-6: Understanding the Market
    Steps 7-9: Competitive Positioning
    Steps 10-12: Go-to-Market Strategy
    """

    async def run_onboarding(
        self,
        company_data: dict,
        context: AgentContext
    ) -> dict:
        """Run all 12 steps sequentially"""

        results = {}

        # STEP 1: Gather company fundamentals
        step1 = await self._step_1_fundamentals(company_data)
        results['fundamentals'] = step1

        # STEP 2: Deep dive company analysis
        step2 = await self._step_2_company_deep_dive(step1)
        results['company_analysis'] = step2

        # STEP 3: Define personas
        step3 = await self._step_3_personas(step2)
        results['personas'] = step3

        # STEP 4: Market size & segments
        step4 = await self._step_4_market_research(company_data, step3)
        results['market'] = step4

        # STEP 5: Industry analysis
        step5 = await self._step_5_industry_analysis(step4)
        results['industry'] = step5

        # STEP 6: Trends & opportunities
        step6 = await self._step_6_trends(step5)
        results['trends'] = step6

        # STEP 7: Competitor analysis
        step7 = await self._step_7_competitors(company_data, step6)
        results['competitors'] = step7

        # STEP 8: Positioning framework
        step8 = await self._step_8_positioning(step3, step7)
        results['positioning'] = step8

        # STEP 9: Messaging strategy
        step9 = await self._step_9_messaging(step8)
        results['messaging'] = step9

        # STEP 10: Channel strategy
        step10 = await self._step_10_channels(step9, step4)
        results['channels'] = step10

        # STEP 11: Content pillars
        step11 = await self._step_11_content_pillars(step9)
        results['content_pillars'] = step11

        # STEP 12: Campaign roadmap
        step12 = await self._step_12_roadmap(step11)
        results['roadmap'] = step12

        return {
            'status': 'complete',
            'steps': results,
            'total_research_minutes': self._calculate_research_time(results)
        }

    async def _step_1_fundamentals(self, company_data: dict) -> dict:
        """
        Step 1: What does the company do?
        - Gather: products, revenue model, growth, team, funding
        """
        return {}

    async def _step_2_company_deep_dive(self, fundamentals: dict) -> dict:
        """
        Step 2: Deep dive into company
        - Analyze: GTM history, wins/losses, brand perception
        """
        return {}

    # ... Steps 3-12 follow similar pattern
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 8-11 (120 hours)

---

## SYSTEM 5: MUSE GUILD (30 Agents)

### Purpose
Creative content generation - copy, visuals, assets, creative strategy.

### The 30 Muse Agents

```
MUSE-001-005: Copywriters (headlines, body copy, CTAs)
MUSE-006-010: Content Strategists (pillar content, narratives)
MUSE-011-015: Visual Designers (with Canva API integration)
MUSE-016-020: Video Strategists (script, concept, direction)
MUSE-021-025: Social Media Specialists (platform-specific content)
MUSE-026-030: Creative Directors (oversees creative quality)
```

### Design Files to Create

#### `backend/agents/muse/muse_001_headline_copywriter.py`
```python
# 200 lines
class MUSE001HeadlineCopywriter(GuildAgent):
    """
    Generates compelling headlines for campaigns
    Uses: Brand voice, positioning, competitive intel
    Output: 5-10 headline variants with scoring
    """

    async def generate_headlines(
        self,
        campaign_context: dict,
        audience: dict,
        context: AgentContext
    ) -> dict:
        """
        Generate headlines optimized for conversion
        - Analyzes positioning
        - Tests different angles
        - Scores by predicted impact
        - Returns variants
        """

        headlines = []

        # Prompt the LLM to generate headlines
        prompt = f"""
        Create 5 compelling headlines for a {campaign_context['objective_type']} campaign:

        Positioning: {campaign_context['positioning']}
        Audience: {audience['persona']}
        Problem: {audience['pain_point']}

        Requirements:
        - Benefit-focused
        - 60 characters max
        - Tested copywriting formulas
        - Action-oriented

        Output as JSON: [{{"headline": "...", "formula": "...", "reasoning": "..."}}]
        """

        response = await self._call_llm(prompt)
        headlines = self._parse_json_response(response)

        return {
            'headlines': headlines,
            'recommended': headlines[0],  # Top by default
            'variants': headlines[1:]
        }
```

#### `backend/agents/muse/muse_011_visual_designer.py`
```python
# 250 lines
from external_apis import canva_api

class MUSE011VisualDesigner(GuildAgent):
    """
    Creates visual assets using Canva API
    - Generates design concepts
    - Creates actual assets in Canva
    - Returns asset URLs
    """

    async def create_campaign_visuals(
        self,
        campaign: dict,
        context: AgentContext
    ) -> dict:
        """
        Create complete visual asset set
        - Hero image
        - Social graphics (4 variations)
        - Email headers
        - Display ads
        """

        # Step 1: Design concept
        design_brief = await self._create_design_brief(campaign)

        # Step 2: Generate Canva designs
        canva_projects = []

        # Hero image
        hero = await canva_api.create_design(
            template='hero_image',
            brand_colors=campaign['brand_colors'],
            headline=campaign['headline'],
            subheading=campaign['subheading']
        )
        canva_projects.append(hero)

        # Social graphics
        for platform in ['instagram', 'facebook', 'linkedin']:
            social = await canva_api.create_design(
                template=f'{platform}_post',
                content=campaign['content'],
                brand_colors=campaign['brand_colors']
            )
            canva_projects.append(social)

        return {
            'designs': canva_projects,
            'download_urls': [p['url'] for p in canva_projects],
            'total_assets': len(canva_projects)
        }
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 12-15 (100 hours)

---

## SYSTEM 6: MATRIX GUILD (20 Agents)

### Purpose
Intelligence gathering, signal processing, competitive analysis, crisis detection.

### The 20 Matrix Agents

```
MTX-001-005: Competitive Intelligence Specialists
MTX-006-010: Market Signal Processors
MTX-011-015: Threat Analyzers
MTX-016-020: Predictive Analytics Specialists
```

### Design Structure
```
backend/agents/matrix/
├── mtx_001_competitor_tracker.py
├── mtx_006_signal_processor.py
├── mtx_011_threat_analyzer.py
└── mtx_016_predictive_analyst.py
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 12-15 (80 hours)

---

## SYSTEM 7: GUARDIAN GUILD (10 Agents)

### Purpose
Compliance, policy enforcement, brand safety, platform-specific rules.

### The 10 Guardian Agents

```
GRD-001-002: Google Policy Enforcers
GRD-003-004: Facebook/Meta Policy Enforcers
GRD-005-006: LinkedIn Policy Enforcers
GRD-007-008: Brand Safety Validators
GRD-009-010: Legal/Compliance Checkers
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 12-15 (60 hours)

---

## SYSTEM 8: RAG SYSTEM (Retrieval Augmented Generation)

### Purpose
Vector embeddings and knowledge base for agent context injection.

### Architecture

```
Knowledge Sources
    ├─ Codex Knowledge (system concepts)
    ├─ Campaign History (past results)
    ├─ Competitive Intelligence (market intel)
    ├─ Industry Research (articles, reports)
    └─ User Preferences (org settings)
         ↓
    [Embedding Generation (OpenAI/Gemini)]
         ↓
    [ChromaDB Vector Store]
         ↓
    [Vector Similarity Search]
         ↓
    [Retrieved Context] → [Injected into Agent Prompts]
```

### Core Files to Create

#### `backend/services/rag_service.py`
```python
# 300 lines
from chromadb import Client
from embeddings import OpenAIEmbedding
from typing import List, Dict

class RAGService:
    """
    Manages vector embeddings and RAG queries
    """

    def __init__(self):
        self.chroma_client = Client()
        self.embedding_model = OpenAIEmbedding()

        # Collections for different memory types
        self.collections = {
            'codex_knowledge': None,
            'campaign_briefs': None,
            'competitor_intel': None,
            'industry_research': None,
            'user_preferences': None
        }

    async def initialize_collections(self):
        """Create ChromaDB collections"""
        for collection_name in self.collections:
            self.collections[collection_name] = (
                self.chroma_client.create_collection(name=collection_name)
            )

    async def add_memory(
        self,
        collection: str,
        text: str,
        metadata: dict = None
    ) -> str:
        """
        Add a memory (text chunk) to RAG system
        - Embed text
        - Store in ChromaDB
        - Return memory ID
        """

        # Generate embedding
        embedding = await self.embedding_model.embed(text)

        # Store in collection
        memory_id = str(uuid.uuid4())
        self.collections[collection].add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}]
        )

        return memory_id

    async def query_memory(
        self,
        collection: str,
        query_text: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Query for relevant memories
        - Embed query
        - Vector similarity search
        - Return top-K results
        """

        # Generate query embedding
        query_embedding = await self.embedding_model.embed(query_text)

        # Search
        results = self.collections[collection].query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Format results
        formatted = []
        for i, doc in enumerate(results['documents'][0]):
            formatted.append({
                'text': doc,
                'distance': results['distances'][0][i],
                'metadata': results['metadatas'][0][i]
            })

        return formatted

    async def populate_codex_knowledge(self):
        """
        Populate initial Codex knowledge
        - Load Codex Blueprint
        - Split into chunks
        - Generate embeddings
        - Store in chromadb
        """

        knowledge_chunks = [
            {
                'text': 'The Architect (LORD-001) oversees system architecture...',
                'metadata': {'type': 'lord', 'agent': 'LORD-001'}
            },
            # ... more chunks
        ]

        for chunk in knowledge_chunks:
            await self.add_memory('codex_knowledge', chunk['text'], chunk['metadata'])
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 3-4 (40 hours)

---

## SYSTEM 9: EXTERNAL API INTEGRATIONS

### Purpose
Connectors to third-party data sources and services.

### APIs to Integrate

| API | Purpose | Rate Limit | Cost |
|-----|---------|-----------|------|
| **SEMrush** | Keyword research, market data | 120/min | $120/mo |
| **Ahrefs** | Backlink, competitor data | 100/day | $99-999/mo |
| **NewsAPI** | News aggregation | 500/day | Free-$450/mo |
| **Brave Search** | Alternative search engine | 100/day | Free-$10/mo |
| **Canva API** | Design generation | 1000/day | Built-in |
| **Twitter API** | Social listening | Depends | Free-$100/mo |
| **LinkedIn API** | B2B data | Depends | Free-$600/mo |
| **Google Trends** | Trend analysis | Rate limited | Free |

### Design Files to Create

#### `backend/external_apis/__init__.py`
```python
# 100 lines
from .semrush import SEMrushClient
from .ahrefs import AhrefsClient
from .newsapi import NewsAPIClient
from .brave_search import BraveSearchClient
from .canva import CanvaAPIClient
from .twitter import TwitterClient
from .linkedin import LinkedInClient

class ExternalAPIManager:
    """
    Centralized management of all external APIs
    - Handles authentication
    - Rate limiting
    - Cost tracking
    - Error handling
    """

    def __init__(self):
        self.semrush = SEMrushClient()
        self.ahrefs = AhrefsClient()
        self.newsapi = NewsAPIClient()
        self.brave = BraveSearchClient()
        self.canva = CanvaAPIClient()
        self.twitter = TwitterClient()
        self.linkedin = LinkedInClient()

    async def initialize(self):
        """Initialize all API clients"""
        await self.semrush.authenticate()
        await self.ahrefs.authenticate()
        # ... etc
```

#### `backend/external_apis/semrush.py`
```python
# 200 lines
import aiohttp
from typing import Dict, List

class SEMrushClient:
    """
    SEMrush API wrapper
    Methods: market_research, competitor_keywords, domain_analytics
    """

    BASE_URL = "https://api.semrush.com"

    async def market_research(self, query: str) -> Dict:
        """
        Research a market/industry
        Returns: size, growth rate, segments
        """

        params = {
            'key': self.api_key,
            'type': 'phrase_related',
            'phrase': query,
            'database': 'us'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL, params=params) as resp:
                return await resp.json()

    async def competitor_keywords(self, domain: str) -> List[Dict]:
        """
        Get keywords that competitor ranks for
        """
        pass

    async def domain_analytics(self, domain: str) -> Dict:
        """
        Analyze a competitor domain
        """
        pass
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 6-8 (60 hours)

---

## SYSTEM 10: CACHING LAYER (Redis)

### Purpose
High-speed caching for hot data and frequently accessed information.

### Caching Strategy

```
Cache Types:
1. Agent Responses (24-48 hours)
2. Market Data (7 days)
3. Competitor Profiles (7 days)
4. Personas (30 days)
5. Campaign Results (1 year)
6. User Preferences (30 days)
7. RAG Embeddings (7 days)

Invalidation Triggers:
- Manual invalidation
- TTL expiration
- Dependent data changes
- User action
```

### Design Files to Create

#### `backend/services/cache_service.py`
```python
# 250 lines
import redis
from typing import Any, Optional
import json
from datetime import timedelta

class CacheService:
    """
    Redis cache management for hot data
    Separate from RaptorBus (which uses Redis pub/sub)
    """

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hour

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = None
    ):
        """Set cached value with TTL"""
        ttl = ttl_seconds or self.default_ttl
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )

    async def invalidate(self, pattern: str):
        """Invalidate keys matching pattern"""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

    # Cache warming strategies
    async def warm_market_data(self, markets: List[str]):
        """Pre-populate cache with market data"""
        for market in markets:
            data = await self._fetch_market_data(market)
            await self.set(
                f"market_data:{market}",
                data,
                ttl_seconds=7 * 24 * 3600  # 7 days
            )

    async def warm_competitor_profiles(self, competitors: List[str]):
        """Pre-populate cache with competitor profiles"""
        for competitor in competitors:
            profile = await self._fetch_competitor_profile(competitor)
            await self.set(
                f"competitor:{competitor}",
                profile,
                ttl_seconds=7 * 24 * 3600  # 7 days
            )
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 3-4 (25 hours)

---

## SYSTEM 11: COST TRACKING & OPTIMIZATION

### Purpose
Monitor LLM costs, optimize model selection, enforce $10/user/month budget.

### Cost Model

```
Token Pricing (approximate):
- Gemini 2.5 Flash: $0.075 / 1M input tokens, $0.30 / 1M output tokens
- Claude 3.5 Sonnet: $3 / 1M input, $15 / 1M output
- Claude 3 Opus: $15 / 1M input, $75 / 1M output
- o1-preview: $15 / 1M input, $60 / 1M output

Monthly Budget: $10/user/month

Strategy:
1. Use Gemini Flash for high-volume tasks (90%)
2. Use Claude Sonnet for medium tasks (8%)
3. Use Claude Opus for Lords only (2%)
4. Cache responses aggressively
5. Batch process when possible
```

### Design Files to Create

#### `backend/services/cost_tracker.py`
```python
# 300 lines
from database import Database
from typing import Dict

class CostTracker:
    """
    Track and optimize LLM costs
    """

    MODEL_PRICING = {
        'gemini-2.5-flash': {
            'input': 0.075 / 1_000_000,  # per token
            'output': 0.30 / 1_000_000
        },
        'claude-3-5-sonnet': {
            'input': 3 / 1_000_000,
            'output': 15 / 1_000_000
        },
        'claude-opus-4-1': {
            'input': 15 / 1_000_000,
            'output': 75 / 1_000_000
        }
    }

    def __init__(self, db: Database):
        self.db = db

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost in dollars"""
        pricing = self.MODEL_PRICING.get(model, {})
        input_cost = input_tokens * pricing.get('input', 0)
        output_cost = output_tokens * pricing.get('output', 0)
        return input_cost + output_cost

    async def track_execution(
        self,
        workspace_id: str,
        agent_code: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        execution_time_ms: int
    ):
        """Log execution metrics for cost tracking"""
        cost = self.calculate_cost(model, input_tokens, output_tokens)

        await self.db.insert('agent_execution_logs', {
            'workspace_id': workspace_id,
            'agent_code': agent_code,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_dollars': cost,
            'execution_time_ms': execution_time_ms,
            'created_at': datetime.now()
        })

    async def get_workspace_cost(
        self,
        workspace_id: str,
        period_days: int = 30
    ) -> float:
        """Get total cost for workspace in period"""
        result = await self.db.fetch_one(f"""
            SELECT SUM(cost_dollars) as total
            FROM agent_execution_logs
            WHERE workspace_id = %s
            AND created_at > NOW() - INTERVAL '{period_days} days'
        """, workspace_id)

        return result['total'] or 0

    async def select_optimal_model(
        self,
        task_type: str,
        budget_remaining: float
    ) -> str:
        """
        Select best model for task within budget
        - Research: Gemini Flash (cheap)
        - Creative: Claude Sonnet (balanced)
        - Strategy: Claude Opus (powerful, use sparingly)
        """

        # Default model selection per task type
        default_model = {
            'research': 'gemini-2.5-flash',
            'content_gen': 'claude-3-5-sonnet',
            'analysis': 'gemini-2.5-flash',
            'strategy': 'claude-opus-4-1',
            'synthesis': 'claude-3-5-sonnet'
        }.get(task_type, 'gemini-2.5-flash')

        # Check if we can afford it
        estimated_cost = self._estimate_task_cost(task_type, default_model)

        if estimated_cost > budget_remaining:
            # Fall back to cheaper model
            return 'gemini-2.5-flash'

        return default_model
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 3-4 (30 hours)

---

## SYSTEM 12: AUTHENTICATION & AUTHORIZATION

### Purpose
Manage user identity, workspace access, and role-based permissions.

### Architecture

```
User Login (via Supabase Auth)
    ↓
[JWT Token Generation]
    ↓
[Token Validation Middleware]
    ↓
[Workspace Access Check]
    ↓
[RLS Policy Enforcement (in Database)]
    ↓
[Authorized Data Access]
```

### Design Files to Create

#### `backend/auth/auth_service.py`
```python
# 250 lines
from supabase import create_client
from jose import jwt
from typing import Optional

class AuthService:
    """
    Authentication & authorization service
    - User login/signup
    - Token generation
    - Workspace access
    - RBAC
    """

    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    async def login(
        self,
        email: str,
        password: str
    ) -> Dict[str, str]:
        """
        Login user
        Returns: access_token, refresh_token
        """
        response = await self.supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })

        return {
            'access_token': response.session.access_token,
            'refresh_token': response.session.refresh_token,
            'user_id': response.user.id
        }

    async def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify JWT token
        Returns: decoded token data or None if invalid
        """
        try:
            decoded = jwt.decode(token, SUPABASE_JWT_SECRET)
            return decoded
        except:
            return None

    async def get_workspace_access(
        self,
        user_id: str
    ) -> List[str]:
        """
        Get all workspaces user has access to
        """
        result = await self.supabase.table('workspace_members').select('workspace_id').eq(
            'user_id', user_id
        ).execute()

        return [row['workspace_id'] for row in result.data]

    async def get_user_role(
        self,
        user_id: str,
        workspace_id: str
    ) -> str:
        """
        Get user's role in a workspace
        Roles: admin, lord_operator, analyst, viewer
        """
        result = await self.supabase.table('workspace_members').select('role').eq(
            'user_id', user_id
        ).eq('workspace_id', workspace_id).single().execute()

        return result.data['role'] if result.data else 'viewer'
```

### Status: ✅ MOSTLY COMPLETE (Supabase Auth exists)

**Estimated Implementation**: Week 1 (5 hours integration)

---

## SYSTEM 13: ERROR HANDLING & LOGGING

### Purpose
Structured logging, error categorization, dead-letter queue handling.

### Design Files to Create

#### `backend/services/logger.py`
```python
# 200 lines
import json
import logging
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    """
    Structured JSON logging for all backend events
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)

    def log(
        self,
        level: str,
        message: str,
        **kwargs
    ):
        """
        Log structured event
        Includes: timestamp, service, level, message, context
        """
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'level': level,
            'message': message,
            **kwargs
        }

        self.logger.log(
            getattr(logging, level),
            json.dumps(event)
        )

    def log_execution(
        self,
        agent_code: str,
        status: str,
        tokens_used: int,
        cost: float,
        **kwargs
    ):
        """Log agent execution"""
        self.log(
            'INFO',
            f'Agent execution: {agent_code}',
            agent_code=agent_code,
            status=status,
            tokens_used=tokens_used,
            cost_cents=cost * 100,
            **kwargs
        )

    def log_error(
        self,
        error: Exception,
        context: Dict[str, Any] = None
    ):
        """Log error with context"""
        self.log(
            'ERROR',
            str(error),
            error_type=type(error).__name__,
            error_message=str(error),
            context=context or {}
        )
```

#### `backend/services/dlq_handler.py`
```python
# 200 lines
class DLQHandler:
    """
    Dead-Letter Queue handling for failed messages
    """

    async def process_dlq_message(self, message: Dict):
        """
        Process message from DLQ
        - Log failure
        - Attempt retry with backoff
        - Send alert if still failing
        """
        pass

    async def send_dlq_alert(self, message: Dict, error: Exception):
        """Send alert for messages in DLQ"""
        pass

    async def retry_dlq_message(
        self,
        message: Dict,
        attempt: int = 1,
        max_attempts: int = 3
    ):
        """Retry DLQ message with exponential backoff"""
        pass
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 2-3 (30 hours)

---

## SYSTEM 14: MONITORING & OBSERVABILITY

### Purpose
Real-time metrics, tracing, alerts, and dashboards.

### Metrics to Track

```
Agent Metrics:
- Execution count
- Success rate
- Avg response time
- Cost per execution
- Error rate

System Metrics:
- RaptorBus throughput
- Cache hit rate
- Database latency
- API response time
- External API calls

Cost Metrics:
- Total cost by agent
- Total cost by model
- Total cost by workspace
- Daily cost trend
- Cost per user
```

### Design Files to Create

#### `backend/monitoring/metrics.py`
```python
# 200 lines
from prometheus_client import Counter, Histogram, Gauge
from typing import Dict

class MetricsCollector:
    """
    Prometheus metrics for monitoring
    """

    # Counters
    agent_invocations = Counter(
        'agent_invocations_total',
        'Total agent invocations',
        ['agent_code', 'status']
    )

    tokens_used = Counter(
        'tokens_used_total',
        'Total tokens used',
        ['model', 'guild']
    )

    # Histograms
    execution_time = Histogram(
        'execution_time_seconds',
        'Agent execution time',
        ['agent_code']
    )

    # Gauges
    active_agents = Gauge(
        'active_agents',
        'Currently active agents'
    )

    def record_agent_execution(
        self,
        agent_code: str,
        status: str,
        execution_time_ms: int,
        tokens_used: int
    ):
        """Record agent execution metrics"""
        self.agent_invocations.labels(
            agent_code=agent_code,
            status=status
        ).inc()

        self.execution_time.labels(agent_code=agent_code).observe(
            execution_time_ms / 1000
        )
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 4-5 (35 hours)

---

## SYSTEM 15: TESTING FRAMEWORK

### Purpose
Comprehensive testing at unit, integration, and performance levels.

### Test Structure

```
backend/tests/
├── unit/
│   ├── agents/
│   │   ├── test_lord_agents.py
│   │   ├── test_research_agents.py
│   │   └── test_muse_agents.py
│   ├── services/
│   │   ├── test_rag_service.py
│   │   ├── test_cost_tracker.py
│   │   └── test_cache_service.py
│   └── utils/
│       └── test_helpers.py
├── integration/
│   ├── test_api_campaigns.py
│   ├── test_agent_execution.py
│   ├── test_raptor_bus.py
│   └── test_external_apis.py
├── performance/
│   ├── test_agent_throughput.py
│   ├── test_concurrent_campaigns.py
│   └── test_cache_performance.py
├── fixtures/
│   └── sample_data.py
└── conftest.py
```

### Design Files to Create

#### `backend/tests/unit/agents/test_lord_agents.py`
```python
# 300 lines
import pytest
from agents.lords.architect import TheArchitect
from agents.base_agent import AgentContext

class TestTheArchitect:
    """Tests for The Architect (LORD-001)"""

    @pytest.fixture
    def architect(self):
        return TheArchitect()

    @pytest.fixture
    def agent_context(self):
        return AgentContext(
            workspace_id='test-workspace',
            user_id='test-user',
            request_id='test-request',
            campaign_id=None,
            budget_remaining=100.00
        )

    @pytest.mark.asyncio
    async def test_route_new_campaign(self, architect, agent_context):
        """Test routing of new campaign request"""
        request = {
            'type': 'new_campaign',
            'company': 'ACME Corp',
            'industry': 'Technology'
        }

        command = await architect.route_request(request, agent_context)

        assert command.guild == 'research'
        assert 'RES-001' in command.agent_codes
        assert command.priority == 'high'

    @pytest.mark.asyncio
    async def test_budget_allocation(self, architect, agent_context):
        """Test Lord allocates budget correctly"""
        tasks = [
            {'name': 'research', 'estimated_cost': 20},
            {'name': 'content', 'estimated_cost': 50},
            {'name': 'analysis', 'estimated_cost': 30}
        ]

        allocation = await architect.allocate_budget(100, tasks, agent_context)

        assert allocation['research'] > 0
        assert allocation['content'] > 0
        assert allocation['analysis'] > 0
        assert sum(allocation.values()) <= 100
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 19-22 (80 hours)

---

## SYSTEM 16: DEPLOYMENT & DEVOPS

### Purpose
Containerization, deployment pipelines, environment management.

### Files to Create

#### `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY backend ./backend

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `docker-compose.yml`
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - REDIS_URL=${REDIS_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

#### `.github/workflows/deploy.yml`
```yaml
name: Deploy to GCP Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build and deploy
        run: |
          gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT }}/raptorflow-backend
          gcloud run deploy raptorflow-backend \
            --image gcr.io/${{ secrets.GCP_PROJECT }}/raptorflow-backend \
            --region europe-west1 \
            --set-env-vars SUPABASE_URL=${{ secrets.SUPABASE_URL }}
```

### Status: 🔴 DESIGN ONLY

**Estimated Implementation**: Week 6-7 (30 hours)

---

## PART III: INTEGRATION ROADMAP

### Phase 1: Foundation (Weeks 1-3)
- [x] Database schema (56 tables)
- [x] RaptorBus implementation
- [ ] API layer basic structure
- [ ] Authentication integration
- [ ] Logger & error handling
- [ ] Basic caching layer

**Estimated Hours**: 80
**Deliverables**: Basic HTTP API + message bus ready

### Phase 2: Agent Framework & Lords (Weeks 4-7)
- [ ] Agent base classes
- [ ] 7 Lord agents
- [ ] Agent executor
- [ ] RAG system
- [ ] External API integrations

**Estimated Hours**: 150
**Deliverables**: Lords operational, agent framework ready

### Phase 3: Guild Implementation (Weeks 8-15)
- [ ] Research Guild (20 agents)
- [ ] Muse Guild (30 agents)
- [ ] Matrix Guild (20 agents)
- [ ] Guardian Guild (10 agents)
- [ ] Maniacal Onboarding workflow

**Estimated Hours**: 280
**Deliverables**: 70+ agents operational

### Phase 4: Polish & Testing (Weeks 16-22)
- [ ] Complete testing suite
- [ ] Performance optimization
- [ ] Cost tracking refinement
- [ ] Monitoring & dashboards
- [ ] Deployment pipelines
- [ ] Documentation

**Estimated Hours**: 150
**Deliverables**: Production-ready backend

---

## PART IV: DEPENDENCY GRAPH

```
┌─────────────────┐
│ Database Schema │ (Week 1) ✅
└────────┬────────┘
         │
    ┌────▼─────────────────────────┐
    │ API Layer + RaptorBus         │ (Week 2-3)
    └────┬──────────────────────────┘
         │
    ┌────▼──────────────────────┐
    │ Agent Framework + RAG      │ (Week 3-4)
    │ Cache + Cost Tracking      │
    └────┬─────────────────────┘
         │
   ┌─────┴──────────────────────────────────────┐
   │                                              │
┌──▼──────────┐  ┌──────────────┐  ┌─────────┐ │
│   Council   │  │ External APIs│  │Monitoring│ │
│  of Lords   │  │ Integration  │  │& Logging │ │
└──┬──────────┘  └──────────────┘  └─────────┘ │
   │                                            │
   └────────────────┬────────────────┬──────────┘
                    │                │
         ┌──────────▼──────┐  ┌──────▼──────────┐
         │ Research Guild  │  │ Muse Guild      │
         │ (20 agents)     │  │ (30 agents)     │
         └─────────────────┘  └─────────────────┘

         ┌──────────┐  ┌──────────────────────┐
         │ Matrix   │  │ Guardian Guild       │
         │(20 agts) │  │ (10 agents)          │
         └──────────┘  └──────────────────────┘
                    │                │
                    └────────┬───────┘
                             │
                    ┌────────▼──────────┐
                    │  Testing & Deploy │
                    │  (Weeks 19-22)    │
                    └───────────────────┘
```

---

## PART V: SUCCESS METRICS

### Technical Metrics
- ✅ 16 core backend systems fully designed
- ✅ 70+ agents operational
- ✅ <200ms p95 latency on API endpoints
- ✅ 99.5% uptime SLA
- ✅ <$10/user/month cost target

### Quality Metrics
- ✅ 80%+ test coverage
- ✅ Zero critical security vulnerabilities
- ✅ Structured logging on all operations
- ✅ Monitoring dashboards for all systems

### Business Metrics
- ✅ Campaign creation in <5 minutes
- ✅ Maniacal Onboarding in <2 hours
- ✅ Multi-guild parallelization (3x faster)
- ✅ Cost savings vs alternative solutions

---

## NEXT STEPS

1. **Week 1-2**: Implement API Layer (SYSTEM 1)
2. **Week 2-3**: Implement Agent Framework (SYSTEM 2)
3. **Week 3-4**: Implement RAG System (SYSTEM 8)
4. **Week 4-7**: Implement Council of Lords (SYSTEM 3)
5. **Week 8-11**: Implement Research Guild (SYSTEM 4)
6. **Week 12-15**: Implement Muse/Matrix/Guardian Guilds (SYSTEMS 5-7)
7. **Week 16-22**: Testing, optimization, deployment (SYSTEMS 13-16)

---

**Current Status**: 🟡 DESIGN PHASE COMPLETE - Ready for Implementation Phase

**Next Action**: Begin Week 1 execution with API Layer implementation
