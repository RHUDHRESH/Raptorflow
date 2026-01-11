# STREAM 1: ROUTING & AGENTS (100 Prompts)

> **INSTRUCTIONS**: Copy each prompt to your AI assistant. Each is self-contained.
> **CONTEXT**: Reference `DOCUMENTATION/SWARM/IMPLEMENTATION/01_ROUTING_ARCHITECTURE.md`

---

## PROMPTS 1-20: Core Infrastructure

### PROMPT 1
```
Create backend/requirements.txt with: langchain>=0.2.0, langchain-google-vertexai>=1.0.0, langgraph>=0.1.0, langchain-community>=0.2.0, sentence-transformers>=2.2.0, pydantic>=2.0.0, httpx>=0.25.0, numpy>=1.24.0, supabase>=2.0.0, upstash-redis>=0.15.0, python-jose>=3.3.0, uvicorn>=0.23.0, fastapi>=0.100.0, google-cloud-aiplatform>=1.38.0, vertexai>=1.38.0
```

### PROMPT 2
```
Create backend/agents/__init__.py exporting: AgentConfig, ModelTier from .config; VertexAILLM from .llm; BaseAgent from .base; AgentState from .state
```

### PROMPT 3
```
Create backend/agents/config.py with: (1) ModelTier enum: FLASH_LITE="gemini-2.0-flash-lite", FLASH="gemini-2.0-flash", PRO="gemini-1.5-pro". (2) AgentConfig(BaseSettings) with GCP_PROJECT_ID, GCP_REGION="us-central1", SUPABASE_URL, SUPABASE_SERVICE_KEY, UPSTASH_REDIS_URL, UPSTASH_REDIS_TOKEN from env. (3) MODEL_COSTS dict mapping tiers to cost/1K tokens. (4) estimate_cost(input_tokens, output_tokens, tier) function.
```

### PROMPT 4
```
Create backend/agents/llm.py: (1) Initialize vertexai with config. (2) VertexAILLM class using ChatVertexAI with model_tier, tracking tokens/cost. Methods: async generate(prompt, system_prompt), async generate_structured(prompt, output_schema: BaseModel), get_usage(). (3) Helper: get_llm(tier), async quick_generate(prompt, tier).
```

### PROMPT 5
```
Create backend/agents/state.py: (1) AgentState(TypedDict) with: messages (Annotated[list, add_messages]), workspace_id, user_id, session_id, current_agent, routing_path: List[str], memory_context: Dict, foundation_summary, active_icps: List[Dict], pending_approval: bool, error, output, tokens_used, cost_usd. (2) @dataclass WorkspaceContext, ExecutionTrace. (3) create_initial_state() helper.
```

### PROMPT 6
```
Create backend/agents/base.py: Abstract BaseAgent class with __init__(name, description, model_tier), abstract get_system_prompt(), abstract async execute(state) -> AgentState, get_tools(), register_tool(tool), async _call_llm(prompt, system_prompt), _update_state(state, **updates). Include logging.
```

### PROMPT 7
```
Create backend/agents/tools/__init__.py exporting: WebSearchTool, WebScraperTool, DatabaseTool, ContentGenTool, ToolRegistry from their modules.
```

### PROMPT 8
```
Create backend/agents/tools/base.py: (1) @dataclass ToolResult with success, data, error, tokens_used, latency_ms. (2) ToolError(Exception) with tool_name, message, details. (3) RaptorflowTool(BaseTool) base class with workspace_id, _log_call(), _log_result(), _handle_error().
```

### PROMPT 9
```
Create backend/agents/tools/web_search.py: Import FreeWebSearchEngine from cloud-scraper/free_web_search.py. WebSearchInput schema (query, max_results, engines). WebSearchTool(RaptorflowTool) with name="web_search", async _arun calling search engine, formatting results.
```

### PROMPT 10
```
Create backend/agents/tools/web_scraper.py: WebScraperInput schema (url, extract_text). WebScraperTool using httpx and BeautifulSoup. Validate URLs, extract text, truncate to 5000 chars, handle errors.
```

### PROMPT 11
```
Create backend/agents/tools/database.py: DatabaseQueryInput schema (table: Literal["foundations","icp_profiles","moves","campaigns","muse_assets"], workspace_id, filters, limit). DatabaseTool using Supabase client. CRITICAL: Always filter by workspace_id. Read-only queries.
```

### PROMPT 12
```
Create backend/agents/tools/content_gen.py: ContentGenInput schema (content_type: Literal["email","social_post","blog_intro","ad_copy","headline"], topic, tone, length, target_audience, brand_voice_notes). ContentGenTool using FLASH model. Build detailed prompts, return generated content.
```

### PROMPT 13
```
Create backend/agents/tools/registry.py: Singleton ToolRegistry with _tools dict, _categories dict. Methods: register(tool, category), get(name), get_by_category(category), get_all(), list_tools(). initialize_default_tools() function registering all tools. get_tools_for_agent(categories) helper.
```

### PROMPT 14
```
Create backend/agents/routing/__init__.py exporting: SemanticRouter, HLKRouter, IntentRouter, RoutingPipeline, RoutingDecision.
```

### PROMPT 15
```
Create backend/agents/routing/semantic.py: ROUTE_DEFINITIONS dict with routes (onboarding, moves, muse, blackbox, research, analytics, general) and example phrases. SemanticRouteResult dataclass. SemanticRouter using SentenceTransformer("all-MiniLM-L6-v2"). _build_route_embeddings() pre-computes. route(query, threshold=0.5) returns best match with cosine similarity.
```

### PROMPT 16
```
Create backend/agents/routing/hlk.py: HLKClassification(BaseModel) with domain, category, agent, confidence, reasoning. HLKRouteResult dataclass. HLKRouter with CLASSIFICATION_PROMPT template listing domains/agents. async route(request) using FLASH_LITE, parsing JSON response.
```

### PROMPT 17
```
Create backend/agents/routing/intent.py: Entity(BaseModel) with name, type, value. IntentResult(BaseModel) with primary_intent, secondary_intents, entities, required_tools, required_data, complexity, constraints, clarification_needed, clarification_question. IntentRouter with INTENT_PROMPT. async extract_intent(request) using FLASH.
```

### PROMPT 18
```
Create backend/agents/routing/pipeline.py: RoutingDecision dataclass with target_agent, routing_path, confidence, semantic/hlk/intent results, total_latency_ms. RoutingPipeline with ROUTE_TO_AGENT mapping. async route(request, fast_mode) chains: Semantic (exit if >0.85), HLK, Intent (skip if fast_mode).
```

### PROMPT 19
```
Create backend/agents/dispatcher.py: AgentRegistry class with _agents dict, register(name, class), get(name), list_agents(). AgentDispatcher with routing_pipeline. async dispatch(request, workspace_id, user_id, session_id, fast_mode) routes, gets agent, creates state, executes, returns final state.
```

### PROMPT 20
```
Create backend/agents/preprocessing.py: RequestPreprocessor with db_tool. async preprocess(state) loads foundation (summary, brand_voice, guardrails) and ICPs from database, injects into state. async _load_foundation(workspace_id), async _load_icps(workspace_id) helpers.
```

---

## PROMPTS 21-40: Specialist Agents

### PROMPT 21
```
Create backend/agents/specialists/__init__.py exporting all specialist agents: OnboardingOrchestrator, EvidenceProcessor, FactExtractor, ICPArchitect, MoveStrategist, ContentCreator, CampaignPlanner, BlackBoxStrategist, MarketResearchAgent, AnalyticsAgent, DailyWinsGenerator.
```

### PROMPT 22
```
Create backend/agents/specialists/onboarding_orchestrator.py: OnboardingOrchestrator(BaseAgent) guides 13-step onboarding. System prompt explains all steps (Evidence Vault → Launch). execute() determines user's current step, provides guidance. Uses FLASH model.
```

### PROMPT 23
```
Create backend/agents/specialists/evidence_processor.py: ProcessedEvidence(BaseModel) with item_id, source_type, source_name, content, content_type, word_count, key_topics, processing_status. EvidenceProcessor uses WebScraperTool. async execute() processes URLs/files. async process_url(url) extracts key topics using LLM.
```

### PROMPT 24
```
Create backend/agents/specialists/fact_extractor.py: FactCategory enum (company_info, positioning, target_audience, proof_points, differentiators, constraints). ExtractedFact(BaseModel) with category, fact, confidence, source, source_quote, needs_verification. FactExtractor extracts facts with JSON output, confidence scoring.
```

### PROMPT 25
```
Create backend/agents/specialists/icp_architect.py: MarketSophisticationStage enum (1-5). Demographics, Psychographics, Behaviors, ICPProfile BaseModels. ICPArchitect builds ICPs using psychology principles. System prompt references Eugene Schwartz stages, JTBD framework. Returns 2-3 detailed ICPs as JSON.
```

### PROMPT 26
```
Create backend/agents/specialists/move_strategist.py: MoveCategory enum (ignite, capture, authority, repair, rally). TaskPriority enum. ExecutionTask, MoveStrategy BaseModels. MoveStrategist plans marketing moves with daily execution tasks, success metrics. Duration 7-14 days.
```

### PROMPT 27
```
Create backend/agents/specialists/content_creator.py: ContentCreator(BaseAgent) is the "Muse" agent. Generates content types: email, social, blog, ad, script, carousel. Applies brand voice. System prompt emphasizes matching voice exactly, targeting ICP, ready-to-publish quality. Returns multiple variations.
```

### PROMPT 28
```
Create backend/agents/specialists/campaign_planner.py: CampaignPhase, Campaign BaseModels. CampaignPlanner orchestrates multi-move campaigns. Defines phases (awareness, consideration, conversion), coordinates moves, allocates budget, sets success metrics. Duration weeks-months.
```

### PROMPT 29
```
Create backend/agents/specialists/blackbox_strategist.py: BlackBoxStrategy(BaseModel) with name, focus_area (acquisition/retention/revenue/brand_equity/virality), risk_level 1-10, risk_reasons, phases (Hook/Pivot/Close), expected_upside, potential_downside. System prompt: creative but ethical, actionable strategies.
```

### PROMPT 30
```
Create backend/agents/specialists/market_research.py: CustomerInsight, CompetitorProfile, MarketTrend, ResearchBrief BaseModels. MarketResearchAgent uses WebSearchTool to research customers, competitors, trends. Returns structured research with source citations.
```

### PROMPT 31
```
Create backend/agents/specialists/analytics_agent.py: Trend, Recommendation, Anomaly, AnalyticsReport BaseModels. AnalyticsAgent analyzes campaign performance using DatabaseTool. Returns metrics, trends, insights, recommendations. Identifies anomalies.
```

### PROMPT 32
```
Create backend/agents/specialists/daily_wins.py: DailyWin(BaseModel) with topic, angle, hook, outline, platform, estimated_time, trend_source, relevance_score. DailyWinsGenerator uses WebSearchTool to find trends, generates quick content ideas. Low-effort, high-impact.
```

### PROMPT 33
```
Create backend/agents/specialists/email_specialist.py: EmailContent(BaseModel) with subject_lines (3-5), preview_text, body_html, body_plain, cta, personalization_tokens. EmailSpecialist generates cold outreach, follow-ups, newsletters, promotional, nurture sequences.
```

### PROMPT 34
```
Create backend/agents/specialists/social_media_agent.py: SocialPost(BaseModel) with platform, content, hashtags, media_suggestions, best_posting_time, engagement_hooks. SocialMediaAgent generates platform-specific content (LinkedIn professional, Twitter concise, Instagram visual).
```

### PROMPT 35
```
Create backend/agents/specialists/blog_writer.py: Section, BlogPost(BaseModel) with title, meta_description, outline, content_html, word_count, seo_keywords, internal_link_suggestions. BlogWriter creates SEO-optimized articles, thought leadership, how-to guides.
```

### PROMPT 36
```
Create backend/agents/specialists/quality_checker.py: QualityReport(BaseModel) with overall_score 0-100, factual_accuracy, brand_voice_compliance, constraint_violations, suggestions, approved. QualityChecker validates outputs against foundation data and brand guidelines.
```

### PROMPT 37
```
Create backend/agents/specialists/revision_agent.py: RevisionAgent takes content and feedback, applies corrections while maintaining consistency. Methods: async revise(content, feedback), async apply_corrections(content, corrections). Tracks revision history.
```

### PROMPT 38
```
Create backend/agents/specialists/competitor_intel.py: Activity, ContentStrategy, CompetitorIntel BaseModels. CompetitorIntelAgent monitors competitors using WebSearchTool. Analyzes positioning, content strategy, strengths, weaknesses, opportunities.
```

### PROMPT 39
```
Create backend/agents/specialists/trend_analyzer.py: TrendAnalysis(BaseModel) with trend_name, description, relevance_to_brand, lifecycle_stage (emerging/peak/declining), opportunity_window, recommended_angle. TrendAnalyzer monitors trends, predicts relevance decay.
```

### PROMPT 40
```
Create backend/agents/specialists/persona_simulator.py: PersonaSimulation(BaseModel) with icp_name, content_evaluated, likely_reaction, attention_score, objections, questions, action_likelihood. PersonaSimulator role-plays as ICP to evaluate content effectiveness.
```

---

## PROMPTS 41-60: LangGraph Workflows

### PROMPT 41
```
Create backend/agents/graphs/__init__.py exporting: create_raptorflow_graph, OnboardingGraph, MoveExecutionGraph, ContentGraph, ResearchGraph.
```

### PROMPT 42
```
Create backend/agents/graphs/main.py: create_raptorflow_graph() using StateGraph(AgentState). Nodes: preprocess, route, execute, quality_check, approval_gate, postprocess. Edges with conditional routing. Compile with MemorySaver checkpointing.
```

### PROMPT 43
```
Create backend/agents/graphs/onboarding.py: OnboardingState(TypedDict) extends AgentState with current_step, completed_steps, evidence. OnboardingGraph with nodes for each of 13 steps. Conditional edges for step transitions. Resume capability.
```

### PROMPT 44
```
Create backend/agents/graphs/move_execution.py: MoveExecutionState with move_id, current_day, tasks. MoveExecutionGraph nodes: generate_tasks, schedule_tasks, execute_task, generate_content, mark_complete, update_progress.
```

### PROMPT 45
```
Create backend/agents/graphs/content.py: ContentState with content_type, draft, feedback, versions. ContentGraph nodes: draft, review, revise, approve. Loop back on feedback. Version tracking.
```

### PROMPT 46
```
Create backend/agents/graphs/research.py: ResearchState with query, sources, findings. ResearchGraph nodes: plan, search, scrape, analyze, synthesize. Source validation. Confidence scoring.
```

### PROMPT 47
```
Create backend/agents/graphs/hitl.py: ApprovalState with pending_output, risk_level, gate_id. HITLGraph with request_approval, wait_for_response, handle_timeout, process_feedback nodes. Use interrupt_before for approval. Persist state during wait.
```

### PROMPT 48
```
Create backend/agents/graphs/reflection.py: ReflectionGraph nodes: evaluate_output, generate_critique, plan_corrections, execute_revision, re_evaluate. Loop until quality threshold met or max iterations.
```

### PROMPT 49
```
Create backend/agents/coordination.py: AgentMessage(BaseModel) with from_agent, to_agent, message_type, payload, timestamp. Coordination functions for agent-to-agent messaging, handoffs, shared state.
```

### PROMPT 50
```
Create backend/agents/checkpointing.py: RedisCheckpointer(BaseCheckpointSaver) using Upstash Redis. async save_checkpoint(session_id, state), async load_checkpoint(session_id), async list_checkpoints(workspace_id). TTL management.
```

### PROMPT 51
```
Create backend/agents/compiler.py: GraphCompiler singleton. compile_graph(graph), get_compiled_graph(name), reload_graph(name), validate_graph(graph). Cache compiled graphs. Hot reload support.
```

### PROMPT 52
```
Create backend/agents/streaming.py: async stream_agent_response(state) -> AsyncGenerator yielding tokens. format_sse_event(event_type, data). StreamingResponseHandler for FastAPI SSE.
```

### PROMPT 53
```
Create backend/agents/errors.py: AgentExecutionError, RoutingError, ToolExecutionError, MemoryAccessError, ApprovalTimeoutError, BudgetExceededError custom exceptions with context attributes.
```

### PROMPT 54
```
Create backend/agents/metrics.py: @dataclass AgentMetrics with agent_name, execution_count, avg_latency_ms, total_tokens, total_cost_usd, success_rate, avg_quality_score. MetricsCollector singleton tracking per-agent metrics.
```

### PROMPT 55
```
Create backend/agents/tracer.py: @dataclass TraceStep with step_name, input, output, latency_ms, tokens. ExecutionTracer implementing LangChain BaseTracer. Records all steps, tool calls. Export for debugging.
```

### PROMPT 56
```
Create backend/agents/testing.py: mock_llm_response(response), create_test_state(**kwargs), async run_agent_test(agent, input). Pytest fixtures for agent testing. Mock tools.
```

### PROMPT 57
```
Create backend/agents/warmup.py: async warmup_agents() preloads models, primes caches, compiles graphs. async warmup_models() initializes Vertex AI. async verify_connections() checks Supabase, Redis.
```

### PROMPT 58
```
Create backend/agents/rate_limiter.py: AgentRateLimiter using Redis. async check_limit(user_id, agent), async record_call(user_id, agent), get_limit_for_tier(tier, agent). Returns retry_after on limit exceeded.
```

### PROMPT 59
```
Create backend/agents/cost_estimator.py: @dataclass CostEstimate with estimated_input_tokens, estimated_output_tokens, estimated_cost_usd, model_breakdown. estimate_cost(request, agent), check_budget(user_id, estimated_cost).
```

### PROMPT 60
```
Create backend/agents/context_builder.py: ContextBuilder gathers relevant context for agents. async build_context(workspace_id, query, max_tokens) fetches from memory, compresses, formats for prompt injection.
```

---

## PROMPTS 61-80: Advanced Routing & Tools

### PROMPT 61
```
Create backend/agents/routing/context_aware.py: ContextAwareRouter considers user history, workspace data, recent interactions for personalized routing. Methods: async route_with_context(request, workspace_context).
```

### PROMPT 62
```
Create backend/agents/routing/fallback.py: FallbackRouter handles unrecognized requests. generate_clarification(request), get_default_agent(), graceful_degradation(). Returns helpful prompts.
```

### PROMPT 63
```
Create backend/agents/routing/multi_intent.py: MultiIntentRouter splits compound requests. async split_request(request), async route_parallel(intents), aggregate_results(results). Handles "do X and also Y".
```

### PROMPT 64
```
Create backend/agents/routing/optimizer.py: RouteOptimizer learns from successful routes. update_embeddings_from_feedback(route, success), prune_unused_routes(), ab_test_routes(). Improves over time.
```

### PROMPT 65
```
Create backend/agents/routing/analytics.py: RoutingAnalytics tracks usage, accuracy, misroutes. log_route(decision, outcome), get_accuracy_report(), identify_problem_routes(). Dashboard data.
```

### PROMPT 66
```
Create backend/agents/tools/research.py: ResearchTool combines web_search + web_scraper + analysis. async research_topic(topic, depth) returns structured findings with citations, confidence scores.
```

### PROMPT 67
```
Create backend/agents/tools/memory_tool.py: MemoryTool for agents to query memory. async search_memory(workspace_id, query, types), async store_memory(workspace_id, content, type). Workspace-scoped.
```

### PROMPT 68
```
Create backend/agents/tools/approval_tool.py: ApprovalTool creates approval gates. async request_approval(output, risk_level, reason), async check_approval(gate_id), async cancel_approval(gate_id).
```

### PROMPT 69
```
Create backend/agents/tools/analytics_tool.py: AnalyticsTool queries performance data. async get_metrics(workspace_id, date_range), async compare_periods(period1, period2), async get_top_performers().
```

### PROMPT 70
```
Create backend/agents/tools/scheduling_tool.py: SchedulingTool for content scheduling. async find_optimal_time(content_type, platform), async check_conflicts(datetime), async schedule_content(content_id, datetime).
```

### PROMPT 71
```
Create backend/agents/tools/template_tool.py: TemplateTool manages content templates. async get_templates(category), async fill_template(template_id, variables), async save_as_template(content).
```

### PROMPT 72
```
Create backend/agents/tools/feedback_tool.py: FeedbackTool captures user feedback. async record_feedback(output_id, rating, comments), async get_feedback_summary(workspace_id), async apply_learnings().
```

### PROMPT 73
```
Create backend/agents/tools/export_tool.py: ExportTool exports content in formats. async export_to_pdf(content), async export_to_docx(content), async export_to_html(content).
```

### PROMPT 74
```
Create backend/agents/tools/integration_tool.py: IntegrationTool connects external services. async post_to_linkedin(content), async send_email(email_content), async update_crm(data). Stub implementations.
```

### PROMPT 75
```
Create backend/agents/skills/__init__.py: Export SkillCard, SkillRegistry, SkillExecutor, load_skill.
```

### PROMPT 76
```
Create backend/agents/skills/models.py: SkillCard(BaseModel) with name, description, version, model_tier, cost_limit, tools, input_schema, output_schema, prompt_template. SkillMetadata for registry.
```

### PROMPT 77
```
Create backend/agents/skills/registry.py: SkillRegistry singleton. register_skill(skill_card), get_skill(name), search_skills(query) using semantic similarity, list_skills(), hot_reload().
```

### PROMPT 78
```
Create backend/agents/skills/executor.py: SkillExecutor validates inputs, injects context, executes skill, validates output. async execute_skill(skill_name, inputs, context), estimate_skill_cost(skill_name, inputs).
```

### PROMPT 79
```
Create backend/agents/skills/loader.py: load_skill(filepath) parses YAML frontmatter + markdown body. load_skills_from_directory(dirpath). SkillParser extracts metadata and prompt template.
```

### PROMPT 80
```
Create backend/agents/skills/builtin/content_generation.yaml: Skill card for content generation with name, description, model_tier: FLASH, tools: [content_gen], input_schema (content_type, topic, tone), output_schema, prompt template.
```

---

## PROMPTS 81-100: API & Integration

### PROMPT 81
```
Create backend/api/__init__.py: Export v1 router.
```

### PROMPT 82
```
Create backend/api/v1/__init__.py: Create APIRouter, include all sub-routers (agents, auth, foundation, icps, moves, campaigns, muse, billing) with prefixes.
```

### PROMPT 83
```
Create backend/api/v1/agents.py: POST /execute with AgentRequest(request_type, request_data, stream). Response with success, output, tokens, cost, requires_approval. Uses dispatcher. Auth required.
```

### PROMPT 84
```
Create backend/api/v1/agents_stream.py: POST /execute/stream returns StreamingResponse with SSE events. Yields progress updates, partial outputs, final result.
```

### PROMPT 85
```
Create backend/api/v1/foundation.py: GET / returns foundation for workspace. PUT / updates foundation. GET /summary returns compressed summary. All filter by workspace_id from auth.
```

### PROMPT 86
```
Create backend/api/v1/icps.py: GET / list ICPs, POST / create, GET /{id}, PUT /{id}, DELETE /{id}, POST /{id}/set-primary. All scoped to workspace.
```

### PROMPT 87
```
Create backend/api/v1/moves.py: GET / list, POST / create, GET /{id}, PUT /{id}, DELETE /{id}, POST /{id}/start, POST /{id}/pause, POST /{id}/complete, GET /{id}/tasks.
```

### PROMPT 88
```
Create backend/api/v1/campaigns.py: GET / list, POST / create, GET /{id}, PUT /{id}, DELETE /{id}, GET /{id}/moves, POST /{id}/launch.
```

### PROMPT 89
```
Create backend/api/v1/muse.py: POST /generate with content_type, topic, tone, icp_id. GET /assets list, GET /assets/{id}, PUT /assets/{id}, DELETE /assets/{id}, GET /templates.
```

### PROMPT 90
```
Create backend/api/v1/blackbox.py: POST /generate creates strategy, GET /strategies list, GET /strategies/{id}, POST /strategies/{id}/accept converts to move.
```

### PROMPT 91
```
Create backend/api/v1/daily_wins.py: POST /generate creates today's wins, GET / lists today's wins, POST /{id}/mark-posted, POST /{id}/expand generates full content.
```

### PROMPT 92
```
Create backend/api/v1/approvals.py: GET /pending lists pending approvals, POST /{gate_id}/approve, POST /{gate_id}/reject with reason, GET /{gate_id}/status.
```

### PROMPT 93
```
Create backend/api/v1/memory.py: GET /search with query, types, limit. POST /store with content, type, metadata. GET /stats returns memory analytics. DELETE /{id}.
```

### PROMPT 94
```
Create backend/api/v1/analytics.py: GET /usage returns usage stats, GET /performance returns campaign metrics, GET /costs returns cost breakdown by agent/model.
```

### PROMPT 95
```
Create backend/main.py: FastAPI app with lifespan for startup/shutdown. Include all routers. CORS middleware. Auth middleware. Health endpoint. Initialize agents on startup.
```

### PROMPT 96
```
Create backend/core/startup.py: async initialize_app() verifies Supabase, Redis, Vertex AI connections. Warms up agents. Compiles graphs. Returns health status.
```

### PROMPT 97
```
Create backend/core/shutdown.py: async cleanup_app() closes connections, flushes metrics, saves checkpoints. Graceful shutdown.
```

### PROMPT 98
```
Create backend/core/health.py: HealthChecker with async check_supabase(), check_redis(), check_vertex_ai(), check_agents(). Returns detailed health report.
```

### PROMPT 99
```
Create backend/core/logging_config.py: Configure structured logging with JSON format. Log levels per module. Request ID tracking. Error reporting.
```

### PROMPT 100
```
Create backend/Dockerfile: Python 3.11 base, install requirements, copy code, expose 8080, run with uvicorn. Include health check. Optimize for Cloud Run.
```

---

## VERIFICATION

After all prompts completed, verify:
- [ ] `pip install -r requirements.txt` succeeds
- [ ] All imports resolve correctly
- [ ] `python -m pytest backend/` passes
- [ ] Agents can be instantiated
- [ ] Routing pipeline returns valid decisions
- [ ] API endpoints respond
