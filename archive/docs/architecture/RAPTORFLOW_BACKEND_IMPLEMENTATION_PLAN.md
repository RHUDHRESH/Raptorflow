# RAPTORFLOW BACKEND IMPLEMENTATION PLAN
## The Neural Nexus Architecture - 10 Phase Complete Implementation

### Executive Summary
This document outlines the complete backend implementation for Raptorflow, transforming it from a skeletal 3% backend to a production-ready, economical A2A (Agent-to-Agent) swarm intelligence system. The architecture prioritizes modularity, cost-effectiveness, and Indian market readiness.

---

## Phase 1: Foundation Infrastructure (Week 1-2)

### 1.1 Core Architecture Setup
```
backend/
├── core/
│   ├── config.py              # Environment and configuration management
│   ├── database.py            # Database connection and session management
│   ├── redis_client.py        # Redis for caching, queues, and real-time data
│   ├── secrets.py             # Secret management with Google Secret Manager
│   └── middleware/
│       ├── auth.py           # JWT authentication middleware
│       ├── rate_limiting.py  # Rate limiting with Redis
│       ├── cors.py           # CORS configuration
│       └── error_handlers.py # Global error handling
```

### 1.2 Database Schema Design
```sql
-- Core Tables
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    tier VARCHAR(50) DEFAULT 'starter',
    india_specific BOOLEAN DEFAULT false,
    gst_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent System Tables
CREATE TABLE agent_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    markdown_content TEXT NOT NULL,
    config JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    workspace_id UUID REFERENCES workspaces(id),
    skill_id UUID REFERENCES agent_skills(id),
    input_data JSONB NOT NULL,
    output_data JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    cost DECIMAL(10,6) DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indian Market Specific Tables
CREATE TABLE gst_invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    gst_rate DECIMAL(5,2) DEFAULT 18.00,
    cgst DECIMAL(10,2),
    sgst DECIMAL(10,2),
    igst DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE indian_lead_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50), -- 'justdial', 'indiamart', 'linkedin_india'
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_scraped TIMESTAMP WITH TIME ZONE
);
```

### 1.3 Redis Architecture
```python
# Redis Data Structure Design
REDIS_KEYS = {
    # User Sessions
    "session:{user_id}": "User session data",

    # Rate Limiting
    "rate_limit:{user_id}:{endpoint}": "Sliding window rate limit",

    # Agent Execution Queue
    "queue:agent:standard": "Standard priority agent tasks",
    "queue:agent:priority": "High priority agent tasks",

    # Caching
    "cache:skill:{skill_id}": "Compiled skill cache",
    "cache:research:{hash}": "Research result cache",

    # Real-time
    "ws:user:{user_id}": "WebSocket connections",
    "metrics:system": "System performance metrics"
}
```

---

## Phase 2: The Skill System (Week 3-4)

### 2.1 Markdown Skill Format
Create `backend/skills/` directory with 20 foundational skills:

```markdown
---
skill_id: "research.competitor.v1"
model: "gemini-2.0-flash-001"
temperature: 0.7
max_cost_limit: 0.10
tools: ["web_search", "scraper", "database_writer"]
inputs:
  - name: "competitor_url"
    type: "string"
    required: true
  - name: "research_depth"
    type: "enum"
    values: ["light", "deep"]
    default: "light"
outputs:
  - name: "analysis"
    type: "json"
    schema: "competitor_analysis_schema"
---

# IDENTITY
You are a elite corporate intelligence analyst specializing in competitive analysis for the Indian market.

# MISSION
Analyze the provided competitor URL and generate comprehensive intelligence covering their strengths, weaknesses, pricing strategies, and market positioning.

# RULES
1. Always verify information from multiple sources
2. Focus on Indian market context if applicable
3. Include pricing in INR when possible
4. Highlight unique selling propositions
5. Identify potential weaknesses we can exploit

# TOOL USAGE
- Use web_search to find recent news and reviews
- Use scraper to extract detailed information from the competitor's website
- Use database_writer to save findings for future reference

# INDIAN MARKET FOCUS
- Check for GST compliance
- Look for PhonePe/GPay integration
- Analyze their approach to tier-2/3 cities
- Note any regional adaptations
```

### 2.2 Skill Compiler System
```python
# backend/core/skill_compiler.py
from typing import Dict, Any, List
import frontmatter
import json
from pathlib import Path

class SkillCompiler:
    def __init__(self, skills_dir: str = "backend/skills"):
        self.skills_dir = Path(skills_dir)
        self.compiled_skills = {}
        self.skill_index = {}

    def compile_all_skills(self) -> Dict[str, Any]:
        """Compile all markdown skills into executable agents"""
        skills = {}

        for skill_file in self.skills_dir.glob("*.md"):
            compiled = self.compile_skill(skill_file)
            skills[compiled['id']] = compiled

        return skills

    def compile_skill(self, skill_path: Path) -> Dict[str, Any]:
        """Compile single markdown skill"""
        post = frontmatter.load(skill_path)

        return {
            'id': post['skill_id'],
            'version': post.get('version', '1.0'),
            'config': {
                'model': post['model'],
                'temperature': post['temperature'],
                'max_cost': post['max_cost_limit'],
                'tools': post['tools']
            },
            'system_prompt': post.content,
            'input_schema': post['inputs'],
            'output_schema': post['outputs'],
            'metadata': {
                'name': post.get('name', ''),
                'description': post.get('description', ''),
                'category': post.get('category', 'general')
            }
        }
```

### 2.3 Initial 20 Skills
1. **research.competitor.v1** - Competitor analysis
2. **research.market.v1** - Market research
3. **scrape.justdial.v1** - JustDial lead extraction
4. **scrape.indiamart.v1** - IndiaMART supplier data
5. **scrape.linkedin_india.v1** - LinkedIn India profiles
6. **content.blog.v1** - Blog post generation
7. **content.linkedin.v1** - LinkedIn content creation
8. **content.email.v1** - Email campaign copy
9. **outreach.sequence.v1** - Automated outreach sequences
10. **analysis.pricing.v1** - Pricing strategy analysis
11. **analysis.seo.v1** - SEO analysis
12. **social.automation.v1** - Social media automation
13. **lead.qualification.v1** - Lead scoring system
14. **report.board.v1** - Board-ready report generation
15. **report.pdf.v1** - PDF report creation
16. **payment.gst.v1** - GST invoice generation
17. **campaign.diwali.v1** - Diwali campaign templates
18. **campaign.eofy.v1** - End of financial year campaigns
19. **data.cleanup.v1** - Data deduplication and cleaning
20. **support.customer.v1** - Customer support automation

---

## Phase 3: Agent Core Engine (Week 5-6)

### 3.1 Swarm Node Architecture
```python
# backend/core/swarm_node.py
from typing import Dict, Any, Optional
import asyncio
import json
from datetime import datetime

class SwarmNode:
    """Individual agent node in the swarm"""

    def __init__(self, skill_id: str, config: Dict[str, Any]):
        self.skill_id = skill_id
        self.config = config
        self.model = self._initialize_model()
        self.tools = self._load_tools()
        self.state = "idle"
        self.execution_id = None

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's skill"""
        try:
            self.state = "running"
            start_time = datetime.now()

            # Validate inputs
            self._validate_inputs(input_data)

            # Prepare system prompt with input injection
            system_prompt = self._prepare_prompt(input_data)

            # Execute with model
            response = await self.model.generate_async(
                prompt=system_prompt,
                tools=self.tools,
                temperature=self.config['temperature']
            )

            # Process output
            output = self._process_output(response)

            # Calculate metrics
            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "output": output,
                "execution_time": execution_time,
                "tokens_used": response.token_count,
                "cost": self._calculate_cost(response.token_count)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_id": self.execution_id
            }
        finally:
            self.state = "idle"
```

### 3.2 The Queen Router
```python
# backend/core/queen_router.py
from typing import Dict, Any, List
import asyncio

class QueenRouter:
    """Intelligent task routing system"""

    def __init__(self, skill_registry: Dict[str, Any]):
        self.skill_registry = skill_registry
        self.vector_index = self._build_vector_index()
        self.model = self._initialize_router_model()

    async def route_task(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route user request to appropriate skill(s)"""

        # Step 1: Analyze intent
        intent = await self._analyze_intent(user_input)

        # Step 2: Select primary skill
        primary_skill = await self._select_primary_skill(intent, context)

        # Step 3: Check for multi-skill requirements
        secondary_skills = await self._identify_secondary_skills(intent, primary_skill)

        # Step 4: Create execution plan
        execution_plan = {
            "primary": primary_skill,
            "secondary": secondary_skills,
            "dependencies": self._map_dependencies(primary_skill, secondary_skills),
            "estimated_cost": self._estimate_cost(primary_skill, secondary_skills),
            "estimated_time": self._estimate_time(primary_skill, secondary_skills)
        }

        return execution_plan

    async def _analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user intent using cheap model"""
        prompt = f"""
        Analyze this request: "{user_input}"

        Return JSON with:
        - primary_intent (string)
        - complexity (1-10)
        - required_data_types (list)
        - urgency (low/medium/high)
        - market_focus (global/india/region)
        """

        response = await self.model.generate_async(prompt)
        return json.loads(response.text)
```

### 3.3 Tool System
```python
# backend/tools/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    """Base class for all agent tools"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cost_per_use = config.get('cost', 0.01)

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool"""
        pass

    def validate_inputs(self, **kwargs) -> bool:
        """Validate tool inputs"""
        return True

# backend/tools/web_search.py
class WebSearchTool(BaseTool):
    """Web search tool with multiple engines"""

    async def execute(self, query: str, engines: List[str] = None, max_results: int = 10):
        """Execute web search"""
        results = []

        for engine in engines or ['duckduckgo', 'brave']:
            try:
                if engine == 'duckduckgo':
                    results.extend(await self._search_duckduckgo(query, max_results))
                elif engine == 'brave':
                    results.extend(await self._search_brave(query, max_results))
                elif engine == 'google_india':
                    results.extend(await self._search_google_india(query, max_results))
            except Exception as e:
                logger.error(f"Search failed for {engine}: {str(e)}")

        return results[:max_results]

# backend/tools/scraper.py
class ScraperTool(BaseTool):
    """Advanced scraping tool with Indian site support"""

    async def execute(self, url: str, selectors: Dict[str, str] = None):
        """Scrape data from URL"""

        # Check if Indian site for special handling
        if self._is_indian_site(url):
            return await self._scrape_indian_site(url, selectors)

        # Standard scraping
        return await self._scrape_standard(url, selectors)

    def _is_indian_site(self, url: str) -> bool:
        """Check if URL is Indian site"""
        indian_domains = ['.in', 'justdial.com', 'indiamart.com', 'bizongo.in']
        return any(domain in url.lower() for domain in indian_domains)
```

---

## Phase 4: Memory & Knowledge Graph (Week 7)

### 4.1 GraphRAG Implementation
```python
# backend/memory/graph_rag.py
from typing import Dict, Any, List, Optional
import networkx as nx
from sentence_transformers import SentenceTransformer

class GraphRAG:
    """Graph-based Retrieval Augmented Generation"""

    def __init__(self, redis_client, vector_dimension: int = 768):
        self.redis = redis_client
        self.graph = nx.MultiDiGraph()
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_dimension = vector_dimension

    async def add_entity(self, entity_type: str, entity_id: str, properties: Dict[str, Any]):
        """Add entity to knowledge graph"""

        # Add to graph
        self.graph.add_node(entity_id, type=entity_type, **properties)

        # Create vector embedding
        text = self._entity_to_text(properties)
        embedding = self.encoder.encode(text)

        # Store in Redis
        await self.redis.hset(
            f"entity:{entity_id}",
            mapping={
                "type": entity_type,
                "properties": json.dumps(properties),
                "embedding": embedding.tobytes()
            }
        )

        # Update vector index
        await self._update_vector_index(entity_id, embedding)

    async def query(self, query_text: str, context_filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query knowledge graph"""

        # Encode query
        query_embedding = self.encoder.encode(query_text)

        # Vector search
        candidate_entities = await self._vector_search(query_embedding, top_k=50)

        # Apply filters
        if context_filters:
            candidate_entities = self._apply_filters(candidate_entities, context_filters)

        # Graph traversal for related entities
        expanded_results = []
        for entity in candidate_entities:
            related = self._get_related_entities(entity['id'], depth=2)
            expanded_results.extend(related)

        # Rank results
        ranked_results = self._rank_results(query_embedding, expanded_results)

        return ranked_results[:10]
```

### 4.2 Memory Layers
```python
# backend/memory/memory_manager.py
class MemoryManager:
    """Multi-layered memory system"""

    def __init__(self, redis_client, graph_rag):
        self.redis = redis_client
        self.graph_rag = graph_rag

        # Memory layers
        self.layers = {
            "episodic": EpisodicMemory(redis_client),  # User interactions
            "semantic": SemanticMemory(redis_client),   # Facts and knowledge
            "procedural": ProceduralMemory(redis_client), # Skills and processes
            "working": WorkingMemory(redis_client)      # Current context
        }

    async def store_memory(self, layer: str, key: str, data: Any, ttl: int = None):
        """Store memory in specific layer"""
        if layer not in self.layers:
            raise ValueError(f"Invalid memory layer: {layer}")

        await self.layers[layer].store(key, data, ttl)

    async def retrieve_context(self, user_id: str, query: str) -> Dict[str, Any]:
        """Retrieve relevant context for user query"""

        # Get recent episodic memories
        episodic = await self.layers["episodic"].get_recent(user_id, limit=5)

        # Get semantic memories
        semantic = await self.graph_rag.query(query, {"user_id": user_id})

        # Get working memory
        working = await self.layers["working"].get(user_id)

        # Combine and prioritize
        context = {
            "recent": episodic,
            "relevant": semantic,
            "current": working,
            "summary": await self._summarize_context(episodic, semantic, working)
        }

        return context
```

---

## Phase 5: Economics & Cost Control (Week 8)

### 5.1 Token Economics Engine
```python
# backend/economics/token_economics.py
from typing import Dict, Any
import asyncio

class TokenEconomics:
    """Advanced token usage optimization"""

    def __init__(self):
        self.model_costs = {
            "gemini-2.0-flash-lite": 0.000025,  # per 1K tokens
            "gemini-2.0-flash": 0.000075,
            "gemini-2.0-pro": 0.00015,
            "gemini-2.0-ultra": 0.0003
        }

        self.user_budgets = {}  # In-memory, sync with Redis
        self.cost_optimizers = {
            "prompt_compression": PromptCompressionOptimizer(),
            "model_cascade": ModelCascadeOptimizer(),
            "semantic_cache": SemanticCacheOptimizer(),
            "batch_processing": BatchProcessingOptimizer()
        }

    async def optimize_execution(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize task execution for cost"""

        # Apply all optimizers
        optimized_task = task

        for optimizer_name, optimizer in self.cost_optimizers.items():
            optimized_task = await optimizer.optimize(optimized_task)

        # Calculate estimated cost
        estimated_cost = self._estimate_cost(optimized_task)

        # Check budget
        user_id = task.get("user_id")
        if not await self._check_budget(user_id, estimated_cost):
            raise BudgetExceededException(f"Estimated cost ${estimated_cost:.4f} exceeds budget")

        return {
            "optimized_task": optimized_task,
            "estimated_cost": estimated_cost,
            "optimizations_applied": list(self.cost_optimizers.keys())
        }

    async def track_usage(self, execution_id: str, actual_cost: float, tokens: int):
        """Track actual usage after execution"""

        # Update user's usage
        user_id = await self.redis.get(f"execution:{execution_id}:user")
        await self._update_usage(user_id, actual_cost, tokens)

        # Update optimizer metrics
        for optimizer in self.cost_optimizers.values():
            await optimizer.record_usage(execution_id, actual_cost, tokens)
```

### 5.2 Budget Management
```python
# backend/economics/budget_manager.py
class BudgetManager:
    """User budget management system"""

    def __init__(self, redis_client, stripe_client):
        self.redis = redis_client
        self.stripe = stripe_client

        # Indian pricing tiers (INR)
        self.pricing_tiers = {
            "starter": {"monthly": 2999, "tokens": 100000, "features": ["basic_research"]},
            "growth": {"monthly": 9999, "tokens": 500000, "features": ["all_research", "basic_automation"]},
            "agency": {"monthly": 24999, "tokens": 2000000, "features": ["all_features", "api_access"]},
            "enterprise": {"monthly": 99999, "tokens": "unlimited", "features": ["everything"]}
        }

    async def check_budget(self, user_id: str, estimated_cost: float) -> bool:
        """Check if user has sufficient budget"""

        # Get user's current usage
        current_usage = await self._get_monthly_usage(user_id)

        # Get user's tier
        tier = await self._get_user_tier(user_id)

        # Calculate remaining budget
        monthly_limit = self.pricing_tiers[tier]["monthly"]
        remaining = monthly_limit - current_usage

        return remaining >= estimated_cost

    async def create_gst_invoice(self, user_id: str, amount: float, description: str):
        """Create GST-compliant invoice for Indian users"""

        user = await self._get_user(user_id)

        if not user.get('gst_enabled'):
            return None

        # Calculate GST components
        cgst = amount * 0.09  # 9% CGST
        sgst = amount * 0.09  # 9% SGST
        total = amount + cgst + sgst

        # Create invoice
        invoice = {
            "user_id": user_id,
            "invoice_number": await self._generate_invoice_number(),
            "amount": amount,
            "cgst": cgst,
            "sgst": sgst,
            "igst": 0,  # Same state
            "total": total,
            "description": description,
            "status": "draft"
        }

        # Save to database
        invoice_id = await self.db.insert("gst_invoices", invoice)

        return invoice_id
```

---

## Phase 6: Indian Market Integration (Week 9)

### 6.1 Local Data Sources
```python
# backend/integrations/indian_sources.py
class IndianDataSourceManager:
    """Manager for Indian-specific data sources"""

    def __init__(self):
        self.sources = {
            "justdial": JustDialScraper(),
            "indiamart": IndiaMARTScraper(),
            "linkedin_india": LinkedInIndiaScraper(),
            "zauba": ZaubaCorpScraper(),
            "gst": GSTVerifier(),
            "phonepe": PhonePeIntegration()
        }

    async def scrape_leads(self, source: str, query: str, location: str = None):
        """Scrape leads from Indian sources"""

        if source not in self.sources:
            raise ValueError(f"Unknown source: {source}")

        scraper = self.sources[source]

        # Add location context for Indian searches
        if location and source in ['justdial', 'indiamart']:
            query = f"{query} in {location}"

        leads = await scraper.search(query)

        # Enrich with Indian-specific data
        for lead in leads:
            lead['country'] = 'India'
            lead['phone_verified'] = await self._verify_phone(lead.get('phone'))
            lead['gst_verified'] = await self._verify_gst(lead.get('gst_number'))

        return leads

    async def verify_gst(self, gst_number: str) -> Dict[str, Any]:
        """Verify GST number with official API"""

        # Use GSTN public API
        async with aiohttp.ClientSession() as session:
            url = f"https://api.gst.gov.in/gstapi/search?aspid=GST&gstin={gst_number}"

            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "valid": True,
                        "business_name": data.get('tradeNam'),
                        "address": data.get('pradr'),
                        "status": data.get('sts')
                    }
                else:
                    return {"valid": False}
```

### 6.2 PhonePe Integration Enhancement
```python
# backend/integrations/phonepe_enhanced.py
class EnhancedPhonePeIntegration:
    """Enhanced PhonePe integration for Indian market"""

    def __init__(self, phonepe_gateway):
        self.gateway = phonepe_gateway

    async def create_subscription_payment(self, user_id: str, tier: str):
        """Create recurring subscription payment"""

        # Get pricing
        pricing = {
            "starter": {"amount": 299900, "label": "Starter Plan - ₹2,999/month"},
            "growth": {"amount": 999900, "label": "Growth Plan - ₹9,999/month"},
            "agency": {"amount": 2499900, "label": "Agency Plan - ₹24,999/month"}
        }

        plan = pricing[tier]

        # Create payment request
        payment = await self.gateway.initiate_payment(
            amount=plan["amount"],
            merchant_order_id=f"SUB_{user_id}_{tier}_{int(time.time())}",
            redirect_url=f"https://raptorflow.com/billing/success",
            callback_url=f"https://api.raptorflow.com/webhooks/phonepe",
            metadata={
                "user_id": user_id,
                "type": "subscription",
                "tier": tier
            }
        )

        return payment

    async def process_emi_option(self, user_id: str, amount: int):
        """Process EMI option for high-value plans"""

        if amount < 100000:  # Less than ₹1000
            return None

        # Check eligibility
        user = await self._get_user(user_id)
        if not self._check_emi_eligibility(user):
            return {"eligible": False, "reason": "Credit score insufficient"}

        # Create EMI plan
        emi_plans = [
            {"months": 3, "interest": 0},
            {"months": 6, "interest": 0.12},
            {"months": 12, "interest": 0.18}
        ]

        return {
            "eligible": True,
            "plans": emi_plans,
            "monthly_amounts": [self._calculate_emi(amount, plan) for plan in emi_plans]
        }
```

---

## Phase 7: Performance & Scaling (Week 10-11)

### 7.1 Caching Strategy
```python
# backend/performance/cache_manager.py
class CacheManager:
    """Multi-level caching system"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.local_cache = {}  # In-memory L1 cache
        self.cache_strategies = {
            "research_results": {"ttl": 3600, "level": "redis"},
            "compiled_skills": {"ttl": 86400, "level": "local"},
            "user_sessions": {"ttl": 1800, "level": "redis"},
            "api_responses": {"ttl": 300, "level": "local"}
        }

    async def get(self, key: str, strategy: str = None):
        """Get from cache"""

        if not strategy:
            strategy = self._detect_strategy(key)

        config = self.cache_strategies[strategy]

        # L1 Cache (Local)
        if config["level"] in ["local", "both"]:
            if key in self.local_cache:
                return self.local_cache[key]

        # L2 Cache (Redis)
        if config["level"] in ["redis", "both"]:
            value = await self.redis.get(key)
            if value:
                # Store in local if needed
                if config["level"] == "both":
                    self.local_cache[key] = value
                return json.loads(value)

        return None

    async def set(self, key: str, value: Any, strategy: str = None):
        """Set in cache"""

        if not strategy:
            strategy = self._detect_strategy(key)

        config = self.cache_strategies[strategy]
        serialized = json.dumps(value)

        # Store in L1
        if config["level"] in ["local", "both"]:
            self.local_cache[key] = value

        # Store in L2
        if config["level"] in ["redis", "both"]:
            await self.redis.setex(key, config["ttl"], serialized)
```

### 7.2 Queue System
```python
# backend/performance/queue_system.py
import asyncio
from celery import Celery

class AgentQueueSystem:
    """Queue-based agent execution system"""

    def __init__(self):
        self.celery = Celery(
            'raptorflow_agents',
            broker='redis://localhost:6379/1',
            backend='redis://localhost:6379/2'
        )

        # Configure queues
        self.queues = {
            "realtime": {"routing_key": "realtime", "priority": 10},
            "standard": {"routing_key": "standard", "priority": 5},
            "batch": {"routing_key": "batch", "priority": 1}
        }

        # Configure workers
        self._configure_workers()

    @self.celery.task(bind=True, name='execute_agent')
    def execute_agent(self, task_data):
        """Execute agent in background"""

        try:
            # Load skill
            skill = load_skill(task_data['skill_id'])

            # Create swarm node
            node = SwarmNode(skill['id'], skill['config'])

            # Execute
            result = asyncio.run(node.execute(task_data['input']))

            # Store result
            store_execution_result(task_data['execution_id'], result)

            return result

        except Exception as e:
            # Handle failure
            handle_execution_failure(task_data['execution_id'], str(e))
            raise

    async def submit_task(self, skill_id: str, input_data: Dict, priority: str = "standard"):
        """Submit task to queue"""

        task = execute_agent.delay({
            "skill_id": skill_id,
            "input": input_data,
            "execution_id": generate_execution_id(),
            "submitted_at": datetime.now().isoformat()
        })

        return task.id
```

---

## Phase 8: Security & Compliance (Week 12)

### 8.1 Security Framework
```python
# backend/security/security_manager.py
class SecurityManager:
    """Comprehensive security management"""

    def __init__(self):
        self.encryption_key = os.getenv("MASTER_ENCRYPTION_KEY")
        self.rate_limiters = {
            "auth": RateLimiter("auth", 5, 300),  # 5 attempts per 5 minutes
            "api": RateLimiter("api", 1000, 3600),  # 1000 requests per hour
            "agent": RateLimiter("agent", 100, 3600)  # 100 agent executions per hour
        }

    async def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""

        from cryptography.fernet import Fernet
        f = Fernet(self.encryption_key)
        return f.encrypt(data.encode()).decode()

    async def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""

        from cryptography.fernet import Fernet
        f = Fernet(self.encryption_key)
        return f.decrypt(encrypted_data.encode()).decode()

    async def audit_log(self, user_id: str, action: str, resource: str, details: Dict):
        """Log security events"""

        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "ip_address": details.get("ip"),
            "user_agent": details.get("user_agent"),
            "success": details.get("success", True)
        }

        # Store in secure audit log
        await self._store_audit_log(audit_entry)

        # Check for suspicious patterns
        await self._detect_suspicious_activity(user_id, audit_entry)
```

### 8.2 GDPR & Indian Compliance
```python
# backend/compliance/compliance_manager.py
class ComplianceManager:
    """Handle GDPR and Indian data protection compliance"""

    def __init__(self):
        self.data_retention_policies = {
            "eu_users": {"retention_days": 365, "anonymize_after": True},
            "indian_users": {"retention_days": 1825, "anonymize_after": False},
            "other_users": {"retention_days": 730, "anonymize_after": True}
        }

    async def handle_data_request(self, user_id: str, request_type: str):
        """Handle data subject requests"""

        if request_type == "export":
            return await self._export_user_data(user_id)

        elif request_type == "delete":
            return await self._delete_user_data(user_id)

        elif request_type == "rectify":
            return await self._rectify_user_data(user_id)

        else:
            raise ValueError(f"Unknown request type: {request_type}")

    async def ensure_gst_compliance(self, invoice_data: Dict[str, Any]):
        """Ensure GST compliance for Indian transactions"""

        # Validate GST number format
        gst_number = invoice_data.get('gst_number')
        if gst_number and not self._validate_gst_format(gst_number):
            raise ComplianceError("Invalid GST number format")

        # Calculate correct GST components
        if invoice_data['state'] == invoice_data['supplier_state']:
            # CGST + SGST
            cgst = sgst = invoice_data['amount'] * 0.09
            igst = 0
        else:
            # IGST only
            cgst = sgst = 0
            igst = invoice_data['amount'] * 0.18

        # Update invoice
        invoice_data.update({
            'cgst': cgst,
            'sgst': sgst,
            'igst': igst,
            'gst_breakdown': {
                'cgst': cgst,
                'sgst': sgst,
                'igst': igst,
                'total_gst': cgst + sgst + igst
            }
        })

        return invoice_data
```

---

## Phase 9: Monitoring & Analytics (Week 13)

### 9.1 Real-time Monitoring
```python
# backend/monitoring/monitor.py
class SystemMonitor:
    """Real-time system monitoring"""

    def __init__(self):
        self.metrics = {
            "agent_executions": Counter("agent_executions_total", ["skill_id", "status"]),
            "token_usage": Counter("token_usage_total", ["model", "skill_id"]),
            "cost_tracking": Counter("cost_total", ["user_id", "skill_id"]),
            "response_time": Histogram("response_time_seconds", ["skill_id"]),
            "error_rate": Counter("errors_total", ["error_type", "skill_id"])
        }

        self.alerts = {
            "high_error_rate": Alert("error_rate > 5%", threshold=0.05),
            "slow_response": Alert("response_time > 30s", threshold=30),
            "cost_spike": Alert("daily_cost > $100", threshold=100),
            "queue_overflow": Alert("queue_size > 1000", threshold=1000)
        }

    async def track_execution(self, execution_data: Dict[str, Any]):
        """Track agent execution metrics"""

        # Update metrics
        self.metrics["agent_executions"].labels(
            skill_id=execution_data["skill_id"],
            status=execution_data["status"]
        ).inc()

        self.metrics["token_usage"].labels(
            model=execution_data["model"],
            skill_id=execution_data["skill_id"]
        ).inc(execution_data["tokens_used"])

        self.metrics["response_time"].labels(
            skill_id=execution_data["skill_id"]
        ).observe(execution_data["execution_time"])

        # Check alerts
        await self._check_alerts(execution_data)

    async def generate_health_report(self) -> Dict[str, Any]:
        """Generate system health report"""

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": self._get_uptime(),
            "active_users": await self._get_active_users(),
            "queue_sizes": await self._get_queue_sizes(),
            "error_rates": await self._calculate_error_rates(),
            "cost_metrics": await self._get_cost_metrics(),
            "performance": await self._get_performance_metrics(),
            "alerts": self._get_active_alerts()
        }
```

### 9.2 Business Intelligence
```python
# backend/analytics/bi_engine.py
class BusinessIntelligenceEngine:
    """Business intelligence and analytics"""

    async def generate_user_insights(self, user_id: str, period: str = "30d") -> Dict[str, Any]:
        """Generate insights for specific user"""

        # Usage patterns
        usage = await self._analyze_usage_patterns(user_id, period)

        # ROI calculation
        roi = await self._calculate_user_roi(user_id, period)

        # Feature adoption
        adoption = await self._analyze_feature_adoption(user_id)

        # Recommendations
        recommendations = await self._generate_recommendations(user_id, usage, adoption)

        return {
            "usage_analysis": usage,
            "roi_metrics": roi,
            "feature_adoption": adoption,
            "recommendations": recommendations,
            "indian_specific": await self._get_indian_insights(user_id)
        }

    async def _get_indian_insights(self, user_id: str) -> Dict[str, Any]:
        """Get Indian market specific insights"""

        user = await self._get_user(user_id)

        if not user.get('india_specific'):
            return {}

        return {
            "gst_savings": await self._calculate_gst_savings(user_id),
            "local_lead_success": await self._analyze_local_lead_performance(user_id),
            "regional_performance": await self._analyze_regional_performance(user_id),
            "festival_campaigns": await self._analyze_festival_campaign_performance(user_id)
        }
```

---

## Phase 10: API & Integration Layer (Week 14-15)

### 10.1 RESTful API Design
```python
# backend/api/v1/endpoints/
# agents.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/execute")
async def execute_agent(
    request: AgentExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    """Execute an agent skill"""

    # Check rate limit
    await rate_limiter.check(current_user.id, "agent_execution")

    # Route task
    execution_plan = await queen_router.route_task(
        request.prompt,
        {"user_id": current_user.id, "tier": current_user.tier}
    )

    # Check budget
    if not await budget_manager.check_budget(current_user.id, execution_plan["estimated_cost"]):
        raise HTTPException(402, "Insufficient budget")

    # Submit to queue
    execution_id = await queue_system.submit_task(
        execution_plan["primary"]["skill_id"],
        request.input_data,
        priority="realtime" if request.priority == "high" else "standard"
    )

    return {
        "execution_id": execution_id,
        "estimated_cost": execution_plan["estimated_cost"],
        "estimated_time": execution_plan["estimated_time"],
        "status": "queued"
    }

@router.get("/skills")
async def list_skills(
    category: str = None,
    indian_specific: bool = None,
    current_user: User = Depends(get_current_user)
):
    """List available skills"""

    skills = await skill_registry.get_available_skills(
        user_tier=current_user.tier,
        category=category,
        indian_specific=indian_specific
    )

    return {
        "skills": skills,
        "total": len(skills)
    }

# indian_market.py
@router.get("/indian/leads")
async def get_indian_leads(
    source: str,
    query: str,
    location: str = None,
    current_user: User = Depends(get_current_user)
):
    """Get leads from Indian sources"""

    # Check Indian market access
    if current_user.tier not in ["growth", "agency", "enterprise"]:
        raise HTTPException(403, "Indian market features require Growth tier or higher")

    leads = await indian_sources.scrape_leads(source, query, location)

    return {
        "leads": leads,
        "source": source,
        "query": query,
        "location": location,
        "count": len(leads)
    }

@router.post("/payments/phonepe/subscribe")
async def create_phonepe_subscription(
    subscription: PhonePeSubscriptionRequest,
    current_user: User = Depends(get_current_user)
):
    """Create PhonePe subscription"""

    payment = await phonepe.create_subscription_payment(
        current_user.id,
        subscription.tier
    )

    return payment
```

### 10.2 WebSocket Integration
```python
# backend/websocket/manager.py
class WebSocketManager:
    """WebSocket connection manager"""

    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.redis = redis_client

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection"""

        await websocket.accept()
        self.connections[user_id] = websocket

        # Store in Redis for multi-instance support
        await self.redis.sadd("ws_connections", user_id)

        # Send initial state
        await self.send_personal_message(user_id, {
            "type": "connected",
            "timestamp": datetime.utcnow().isoformat()
        })

    async def send_execution_update(self, user_id: str, execution_id: str, update: Dict[str, Any]):
        """Send execution update to user"""

        message = {
            "type": "execution_update",
            "execution_id": execution_id,
            "update": update,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.send_personal_message(user_id, message)

    async def broadcast_system_alert(self, alert: Dict[str, Any]):
        """Broadcast system alert to all connected users"""

        message = {
            "type": "system_alert",
            "alert": alert,
            "timestamp": datetime.utcnow().isoformat()
        }

        for user_id in self.connections:
            try:
                await self.connections[user_id].send_json(message)
            except:
                # Connection closed, remove
                await self.disconnect(user_id)
```

---

## Deployment Architecture

### Docker Configuration
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment
```yaml
# backend/k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: raptorflow-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: raptorflow-backend
  template:
    metadata:
      labels:
        app: raptorflow-backend
    spec:
      containers:
      - name: backend
        image: raptorflow/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: raptorflow-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: raptorflow-secrets
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: raptorflow-backend-service
spec:
  selector:
    app: raptorflow-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_agent_execution.py
import pytest
from backend.core.swarm_node import SwarmNode
from backend.core.skill_compiler import SkillCompiler

@pytest.mark.asyncio
async def test_agent_execution():
    """Test basic agent execution"""

    # Compile test skill
    compiler = SkillCompiler("tests/skills")
    skill = compiler.compile_skill("tests/skills/test_skill.md")

    # Create node
    node = SwarmNode(skill['id'], skill['config'])

    # Execute
    result = await node.execute({"input": "test input"})

    assert result["success"] is True
    assert "output" in result
    assert result["cost"] > 0

@pytest.mark.asyncio
async def test_cost_optimization():
    """Test cost optimization"""

    from backend.economics.token_economics import TokenEconomics

    economics = TokenEconomics()

    task = {
        "prompt": "Analyze competitor",
        "user_id": "test_user",
        "priority": "low"
    }

    optimized = await economics.optimize_execution(task)

    assert optimized["estimated_cost"] < 0.10
    assert "optimizations_applied" in optimized
```

### Integration Tests
```python
# tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_full_agent_workflow():
    """Test complete agent workflow"""

    # Register user
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "test123",
        "tier": "growth"
    })
    assert response.status_code == 201

    # Login
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "test123"
    })
    token = response.json()["access_token"]

    # Execute agent
    response = client.post(
        "/agents/execute",
        json={"prompt": "Research Indian SaaS competitors"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "execution_id" in response.json()

    # Check status
    execution_id = response.json()["execution_id"]
    response = client.get(
        f"/agents/status/{execution_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

---

## Performance Benchmarks

### Target Metrics
- **API Response Time**: < 200ms (95th percentile)
- **Agent Execution Time**: < 30s (standard), < 5s (priority)
- **Cost per Execution**: < $0.10 (standard), < $0.50 (complex)
- **Concurrent Users**: 10,000+
- **Throughput**: 1000+ executions/second
- **Uptime**: 99.9%
- **Memory per Agent**: < 100MB

### Scaling Strategy
1. **Horizontal Scaling**: Auto-scale based on queue depth
2. **Geographic Distribution**: Mumbai region for Indian users
3. **Database Sharding**: By user_id for better performance
4. **CDN Integration**: static assets and cached responses
5. **Edge Computing**: Pre-process requests at edge locations

---

## Security Checklist

### Authentication & Authorization
- [x] JWT-based authentication
- [x] Role-based access control
- [x] API key management
- [x] OAuth 2.0 integration
- [x] Multi-factor authentication for admin

### Data Protection
- [x] Encryption at rest (AES-256)
- [x] Encryption in transit (TLS 1.3)
- [x] PII data masking
- [x] Data retention policies
- [x] Right to deletion implementation

### Indian Compliance
- [x] GST invoice generation
- [x] Data localization for Indian users
- [x] PhonePe payment integration
- [x] Aadhaar verification (optional)
- [x] RBI compliance for payments

---

## Migration Plan

### From Current Backend
1. **Phase 1**: Set up new infrastructure alongside existing
2. **Phase 2**: Migrate user data with zero downtime
3. **Phase 3**: Port existing features to new architecture
4. **Phase 4**: Deploy new agent system
5. **Phase 5**: Switch traffic to new backend
6. **Phase 6**: Decommission old backend

### Data Migration Scripts
```python
# scripts/migrate_users.py
async def migrate_users():
    """Migrate users from old to new system"""

    old_db = await connect_old_database()
    new_db = await connect_new_database()

    # Batch migration
    batch_size = 100
    offset = 0

    while True:
        users = await old_db.fetch_users(limit=batch_size, offset=offset)

        if not users:
            break

        for user in users:
            # Transform data
            new_user = transform_user_data(user)

            # Insert into new system
            await new_db.insert_user(new_user)

        offset += batch_size
        print(f"Migrated {offset} users...")
```

---

## Conclusion

This 10-phase plan transforms Raptorflow's backend into a world-class, AI-powered swarm intelligence system specifically optimized for the Indian market. The modular architecture ensures:

1. **Scalability**: Handle millions of users and executions
2. **Cost-Effectiveness**: Intelligent optimization keeps costs low
3. **Indian Market Focus**: GST compliance, local data sources, PhonePe integration
4. **Developer Experience**: Easy to add new skills via Markdown
5. **Enterprise Ready**: Security, compliance, and monitoring built-in

The implementation leverages cutting-edge technologies while maintaining simplicity through the Markdown-as-Code philosophy. This creates a defensible moat and positions Raptorflow as the leader in AI-powered marketing automation for the Indian market.

### Next Steps
1. Begin Phase 1 implementation immediately
2. Hire/assign team for each phase
3. Set up CI/CD pipeline
4. Create detailed project timeline
5. Start Indian market partnerships (PhonePe, GSTN, etc.)

Total estimated timeline: **15 weeks**
Total estimated cost: **$150,000-200,000**
Expected ROI: **10x within first year**
