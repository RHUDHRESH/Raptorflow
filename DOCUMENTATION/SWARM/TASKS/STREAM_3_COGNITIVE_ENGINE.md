# STREAM 3: COGNITIVE ENGINE (100 Prompts)

> **INSTRUCTIONS**: Copy each prompt to your AI assistant. Each is self-contained.
> **CONTEXT**: Reference `DOCUMENTATION/SWARM/IMPLEMENTATION/03_COGNITIVE_ENGINE.md`

---

## PROMPTS 1-25: Perception Module

### PROMPT 1
```
Create backend/cognitive/__init__.py exporting: CognitiveEngine, PerceptionModule, PlanningModule, ReflectionModule, ApprovalGate, AdversarialCritic.
```

### PROMPT 2
```
Create backend/cognitive/models.py: @dataclass PerceivedInput with raw_text, entities, intent, sentiment, urgency (1-5), context_signals. @dataclass ExecutionPlan with goal, steps, estimated_cost, estimated_time, risk_level. @dataclass ReflectionResult with quality_score, issues, suggestions, approved.
```

### PROMPT 3
```
Create backend/cognitive/perception/__init__.py exporting: PerceptionModule, EntityExtractor, IntentDetector, SentimentAnalyzer, UrgencyClassifier.
```

### PROMPT 4
```
Create backend/cognitive/perception/entity_extractor.py: EntityExtractor using LLM. async extract(text: str) -> List[Entity]. Entity types: person, company, product, location, date, money, percentage. Confidence scores. Uses FLASH_LITE model.
```

### PROMPT 5
```
Create backend/cognitive/perception/intent_detector.py: IntentDetector. IntentType enum (CREATE, READ, UPDATE, DELETE, ANALYZE, GENERATE, RESEARCH, APPROVE, CLARIFY). async detect(text: str) -> DetectedIntent with intent_type, confidence, sub_intents, parameters.
```

### PROMPT 6
```
Create backend/cognitive/perception/sentiment_analyzer.py: SentimentAnalyzer. Sentiment enum (POSITIVE, NEGATIVE, NEUTRAL, MIXED). async analyze(text: str) -> SentimentResult with sentiment, confidence, emotional_signals (frustrated, excited, confused, etc.).
```

### PROMPT 7
```
Create backend/cognitive/perception/urgency_classifier.py: UrgencyClassifier. async classify(text: str) -> UrgencyResult with level (1-5), signals, deadline_mentioned (datetime | None). Keywords: ASAP, urgent, deadline, immediately = high urgency.
```

### PROMPT 8
```
Create backend/cognitive/perception/context_signals.py: ContextSignalExtractor. async extract(text: str, history: List[dict]) -> ContextSignals with topic_continuity, reference_to_prior, new_topic, implicit_assumptions.
```

### PROMPT 9
```
Create backend/cognitive/perception/module.py: PerceptionModule orchestrates all extractors. async perceive(text: str, history: List[dict]) -> PerceivedInput. Runs extractors in parallel. Aggregates results.
```

### PROMPT 10
```
Create backend/cognitive/perception/preprocessing.py: InputPreprocessor. clean(text: str) removes noise. normalize(text: str) standardizes format. expand_abbreviations(text: str). spell_correct(text: str).
```

### PROMPT 11
```
Create backend/cognitive/perception/clarification.py: ClarificationDetector. async needs_clarification(perceived: PerceivedInput) -> bool. async generate_clarification_question(perceived: PerceivedInput) -> str. Handles ambiguous inputs.
```

### PROMPT 12
```
Create backend/cognitive/perception/multimodal.py: MultimodalPerception. async perceive_image(image_bytes: bytes) -> ImageAnalysis using Gemini vision. async perceive_document(pdf_bytes: bytes) -> DocumentAnalysis. For file uploads.
```

---

## PROMPTS 13-35: Planning Module

### PROMPT 13
```
Create backend/cognitive/planning/__init__.py exporting: PlanningModule, TaskDecomposer, StepPlanner, CostEstimator, RiskAssessor, PlanValidator.
```

### PROMPT 14
```
Create backend/cognitive/planning/models.py: @dataclass PlanStep with id, description, agent, tools, inputs, outputs, dependencies (list of step ids), estimated_tokens, estimated_cost. @dataclass ExecutionPlan with goal, steps, total_cost, total_time, risk_level, requires_approval.
```

### PROMPT 15
```
Create backend/cognitive/planning/decomposer.py: TaskDecomposer using LLM. async decompose(goal: str, context: dict) -> List[SubTask]. Breaks complex goals into atomic tasks. Each task maps to one agent capability.
```

### PROMPT 16
```
Create backend/cognitive/planning/step_planner.py: StepPlanner. async plan_steps(subtasks: List[SubTask], available_agents: List[str]) -> List[PlanStep]. Orders steps, identifies dependencies, assigns agents.
```

### PROMPT 17
```
Create backend/cognitive/planning/cost_estimator.py: CostEstimator. estimate_step_cost(step: PlanStep) -> float estimates tokens and USD. estimate_plan_cost(plan: ExecutionPlan) -> CostEstimate. Uses MODEL_COSTS from config.
```

### PROMPT 18
```
Create backend/cognitive/planning/risk_assessor.py: RiskAssessor. RiskLevel enum (LOW, MEDIUM, HIGH, CRITICAL). async assess(plan: ExecutionPlan) -> RiskAssessment with level, factors, mitigations. Factors: cost, external calls, data sensitivity, irreversibility.
```

### PROMPT 19
```
Create backend/cognitive/planning/validator.py: PlanValidator. async validate(plan: ExecutionPlan) -> ValidationResult with valid, errors, warnings. Checks: all agents exist, dependencies are acyclic, budget fits, tools available.
```

### PROMPT 20
```
Create backend/cognitive/planning/optimizer.py: PlanOptimizer. async optimize(plan: ExecutionPlan) -> ExecutionPlan. Parallelizes independent steps. Batches similar operations. Reduces cost where possible.
```

### PROMPT 21
```
Create backend/cognitive/planning/module.py: PlanningModule orchestrates planning. async plan(goal: str, perceived: PerceivedInput, context: WorkspaceContext) -> ExecutionPlan. Uses decomposer, planner, estimator, assessor, validator.
```

### PROMPT 22
```
Create backend/cognitive/planning/replanning.py: Replanner. async replan(original: ExecutionPlan, failure: StepFailure) -> ExecutionPlan. Handles step failures. Adjusts remaining steps. May skip or retry.
```

### PROMPT 23
```
Create backend/cognitive/planning/checkpoints.py: PlanCheckpointer. async checkpoint(plan: ExecutionPlan, completed_steps: List[str]). async resume(checkpoint_id) -> ExecutionPlan. Persists partial progress.
```

### PROMPT 24
```
Create backend/cognitive/planning/budget_tracker.py: BudgetTracker. async check_budget(user_id: str, estimated_cost: float) -> BudgetCheck with allowed, remaining, warning. async deduct(user_id: str, actual_cost: float). Prevents overspend.
```

### PROMPT 25
```
Create backend/cognitive/planning/templates.py: PlanTemplates. COMMON_PLANS dict with templates for common goals: "generate_blog_post", "research_competitor", "create_move". async apply_template(template_name, variables) -> ExecutionPlan.
```

---

## PROMPTS 26-45: Reflection Module

### PROMPT 26
```
Create backend/cognitive/reflection/__init__.py exporting: ReflectionModule, QualityScorer, SelfCritic, CorrectionPlanner, ImprovementExecutor.
```

### PROMPT 27
```
Create backend/cognitive/reflection/models.py: @dataclass QualityScore with overall (0-100), dimensions: Dict[str, int], issues: List[Issue], passed: bool. @dataclass Issue with severity, dimension, description, location, suggestion.
```

### PROMPT 28
```
Create backend/cognitive/reflection/scorer.py: QualityScorer using LLM. async score(output: str, criteria: List[str]) -> QualityScore. Dimensions: accuracy, relevance, coherence, brand_compliance, actionability. Threshold: 70 to pass.
```

### PROMPT 29
```
Create backend/cognitive/reflection/critic.py: SelfCritic using LLM. async critique(output: str, goal: str, context: dict) -> Critique with issues, severity_counts, recommendations. Adversarial self-review.
```

### PROMPT 30
```
Create backend/cognitive/reflection/correction_planner.py: CorrectionPlanner. async plan_corrections(critique: Critique) -> List[Correction]. Correction with target, action, expected_improvement. Prioritizes by severity.
```

### PROMPT 31
```
Create backend/cognitive/reflection/executor.py: ImprovementExecutor using LLM. async execute_corrections(output: str, corrections: List[Correction]) -> str. Applies corrections iteratively. Returns improved output.
```

### PROMPT 32
```
Create backend/cognitive/reflection/module.py: ReflectionModule orchestrates reflection loop. async reflect(output: str, goal: str, context: dict, max_iterations: int = 3) -> ReflectionResult. Loops until quality threshold or max iterations.
```

### PROMPT 33
```
Create backend/cognitive/reflection/brand_checker.py: BrandChecker. async check_brand_compliance(content: str, brand_voice: str, guardrails: List[str]) -> BrandCheckResult with compliant, violations, suggestions.
```

### PROMPT 34
```
Create backend/cognitive/reflection/fact_checker.py: FactChecker. async check_facts(content: str, source_material: str) -> FactCheckResult with verified_claims, unverified_claims, contradictions.
```

### PROMPT 35
```
Create backend/cognitive/reflection/consistency_checker.py: ConsistencyChecker. async check_consistency(content: str, prior_content: List[str]) -> ConsistencyResult with consistent, inconsistencies, recommended_changes.
```

### PROMPT 36
```
Create backend/cognitive/reflection/plagiarism_detector.py: PlagiarismDetector. async check_originality(content: str) -> OriginalityResult with score, similar_sources. Uses web search to find matches.
```

### PROMPT 37
```
Create backend/cognitive/reflection/tone_analyzer.py: ToneAnalyzer. async analyze_tone(content: str, target_tone: str) -> ToneAnalysisResult with detected_tone, matches_target, adjustments_needed.
```

### PROMPT 38
```
Create backend/cognitive/reflection/readability.py: ReadabilityAnalyzer. analyze(content: str) -> ReadabilityResult with flesch_kincaid_grade, avg_sentence_length, complex_word_percentage, suggestions.
```

### PROMPT 39
```
Create backend/cognitive/reflection/seo_checker.py: SEOChecker. async check_seo(content: str, target_keywords: List[str]) -> SEOCheckResult with keyword_density, title_optimization, meta_suggestions, internal_link_opportunities.
```

### PROMPT 40
```
Create backend/cognitive/reflection/learning.py: ReflectionLearner. async record_reflection(output_id, initial_score, final_score, corrections). async get_common_issues(workspace_id). Learns from patterns to prevent recurring issues.
```

---

## PROMPTS 41-60: Human-in-the-Loop (HITL)

### PROMPT 41
```
Create backend/cognitive/hitl/__init__.py exporting: ApprovalGate, ApprovalRequest, FeedbackCollector, HumanOverride.
```

### PROMPT 42
```
Create backend/cognitive/hitl/models.py: @dataclass ApprovalRequest with gate_id, workspace_id, user_id, output_preview, risk_level, reason, created_at, expires_at, status (pending/approved/rejected/expired). @dataclass ApprovalResponse with approved, feedback, modified_output.
```

### PROMPT 43
```
Create supabase/migrations/20240204_approval_gates.sql: Table approval_gates with id UUID PK, workspace_id UUID FK, user_id UUID, request_type TEXT, output_preview TEXT, risk_level INT, reason TEXT, status TEXT DEFAULT 'pending', response_feedback TEXT, responded_at, created_at, expires_at. Index on (workspace_id, status).
```

### PROMPT 44
```
Create backend/cognitive/hitl/gate.py: ApprovalGate. async request_approval(workspace_id, user_id, output, risk_level, reason) -> gate_id. async check_status(gate_id) -> status. async wait_for_approval(gate_id, timeout=300) -> ApprovalResponse. Polls or uses pubsub.
```

### PROMPT 45
```
Create backend/cognitive/hitl/risk_rules.py: ApprovalRiskRules. requires_approval(action_type, risk_level, cost) -> bool. Rules: cost > $0.50, risk > 3, external posts, deletions. Configurable per workspace.
```

### PROMPT 46
```
Create backend/cognitive/hitl/feedback.py: FeedbackCollector. async request_feedback(gate_id, specific_questions: List[str]). async record_feedback(gate_id, rating, comments, corrections). Links to approval flow.
```

### PROMPT 47
```
Create backend/cognitive/hitl/override.py: HumanOverride. async apply_override(gate_id, modified_output). async reject_with_instructions(gate_id, instructions). Handles user modifications.
```

### PROMPT 48
```
Create backend/cognitive/hitl/notifications.py: ApprovalNotifier. async notify_pending(user_id, gate_id, preview). async notify_expiring(user_id, gate_id, time_remaining). Webhook or email notifications.
```

### PROMPT 49
```
Create backend/cognitive/hitl/auto_approve.py: AutoApprover. async check_auto_approval(request: ApprovalRequest) -> bool. Auto-approves low-risk, similar to prior approved. Learning from user patterns.
```

### PROMPT 50
```
Create backend/cognitive/hitl/escalation.py: EscalationManager. async escalate(gate_id, reason). async assign_reviewer(gate_id, reviewer_id). For team workflows with multiple approvers.
```

### PROMPT 51
```
Create backend/cognitive/hitl/timeout_handler.py: TimeoutHandler. async handle_timeout(gate_id). Options: auto_reject, auto_approve_if_low_risk, notify_and_extend. Configurable per workspace.
```

### PROMPT 52
```
Create backend/cognitive/hitl/audit.py: ApprovalAudit. async log_decision(gate_id, decision, reason). async get_audit_trail(workspace_id, date_range). Compliance logging.
```

---

## PROMPTS 53-70: Adversarial Critic

### PROMPT 53
```
Create backend/cognitive/critic/__init__.py exporting: AdversarialCritic, RedTeamAgent, BiasDetector, FailureModeAnalyzer.
```

### PROMPT 54
```
Create backend/cognitive/critic/adversarial.py: AdversarialCritic using PRO model (rare, high-value). async critique(output: str, goal: str) -> AdversarialCritique. Tries to find flaws. Devil's advocate mode.
```

### PROMPT 55
```
Create backend/cognitive/critic/red_team.py: RedTeamAgent. async attack(content: str) -> List[Vulnerability]. Finds: factual errors, logical fallacies, brand violations, offensive content, legal risks.
```

### PROMPT 56
```
Create backend/cognitive/critic/bias_detector.py: BiasDetector. async detect_bias(content: str) -> BiasReport with detected_biases (gender, racial, political, etc.), severity, locations, suggestions.
```

### PROMPT 57
```
Create backend/cognitive/critic/failure_modes.py: FailureModeAnalyzer. async analyze(plan: ExecutionPlan) -> List[FailureMode]. Predicts what could go wrong. Suggests mitigations.
```

### PROMPT 58
```
Create backend/cognitive/critic/edge_cases.py: EdgeCaseTester. async generate_edge_cases(input_type: str) -> List[EdgeCase]. Tests content against edge cases. Validates robustness.
```

### PROMPT 59
```
Create backend/cognitive/critic/competitor_lens.py: CompetitorLens. async critique_as_competitor(content: str, competitors: List[str]) -> CompetitorCritique. How would competitors attack this?
```

### PROMPT 60
```
Create backend/cognitive/critic/customer_lens.py: CustomerLens. async critique_as_customer(content: str, icp: dict) -> CustomerCritique. Would the ICP believe this? Trust it? Act on it?
```

---

## PROMPTS 61-80: Cognitive Engine Integration

### PROMPT 61
```
Create backend/cognitive/engine.py: CognitiveEngine main class. __init__ creates all modules. async process(input: str, state: AgentState) -> CognitiveResult orchestrates: perceive → plan → execute → reflect → approve if needed.
```

### PROMPT 62
```
Create backend/cognitive/pipeline.py: CognitivePipeline defines processing stages. async run_pipeline(input, state) with hooks: pre_perception, post_perception, pre_planning, post_planning, etc.
```

### PROMPT 63
```
Create backend/cognitive/context.py: CognitiveContext. async build_context(workspace_id) gathers all relevant context for cognitive processing. Foundation, ICPs, history, constraints.
```

### PROMPT 64
```
Create backend/cognitive/execution.py: PlanExecutor. async execute_plan(plan: ExecutionPlan, state: AgentState) -> ExecutionResult. Executes steps, handles failures, tracks progress.
```

### PROMPT 65
```
Create backend/cognitive/monitoring.py: CognitiveMonitor. async monitor_execution(execution_id) tracks progress. async get_execution_status(). Real-time updates.
```

### PROMPT 66
```
Create backend/cognitive/traces.py: CognitiveTracer. async trace(stage, input, output, latency). async get_trace(execution_id) -> full trace. For debugging and optimization.
```

### PROMPT 67
```
Create backend/cognitive/caching.py: CognitiveCache. async cache_perception(input_hash, result). async cache_plan(goal_hash, plan). Avoids recomputation for similar inputs.
```

### PROMPT 68
```
Create backend/cognitive/parallel.py: ParallelExecutor. async execute_parallel(steps: List[PlanStep]) runs independent steps concurrently. Respects dependencies. Aggregates results.
```

### PROMPT 69
```
Create backend/cognitive/retry.py: RetryManager. async retry_step(step: PlanStep, error: Exception, attempt: int) -> RetryDecision. Exponential backoff. Max retries. Alternative strategies.
```

### PROMPT 70
```
Create backend/cognitive/fallback.py: FallbackHandler. async handle_fallback(step: PlanStep, error: Exception) -> FallbackResult. Graceful degradation. Human escalation if critical.
```

---

## PROMPTS 71-85: Protocol Standardization

### PROMPT 71
```
Create backend/cognitive/protocols/__init__.py exporting: AgentProtocol, MessageFormat, HandoffProtocol, ErrorProtocol.
```

### PROMPT 72
```
Create backend/cognitive/protocols/messages.py: MessageFormat standard. @dataclass AgentMessage with from_agent, to_agent, message_type (request/response/error/handoff), payload, correlation_id, timestamp.
```

### PROMPT 73
```
Create backend/cognitive/protocols/handoff.py: HandoffProtocol. async initiate_handoff(from_agent, to_agent, state, reason). async accept_handoff(handoff_id). async reject_handoff(handoff_id, reason). Clean agent transitions.
```

### PROMPT 74
```
Create backend/cognitive/protocols/errors.py: ErrorProtocol. ErrorCode enum. @dataclass ProtocolError with code, message, recoverable, suggested_action. Standardized error handling.
```

### PROMPT 75
```
Create backend/cognitive/protocols/schemas.py: Protocol schemas for all agent inputs/outputs. Define JSON schemas. Validation functions. Type safety.
```

### PROMPT 76
```
Create backend/cognitive/protocols/versioning.py: ProtocolVersion. CURRENT_VERSION = "1.0". async negotiate_version(peer_version). Backwards compatibility.
```

### PROMPT 77
```
Create backend/cognitive/protocols/discovery.py: AgentDiscovery. async discover_agents() -> List[AgentDescriptor]. async get_agent_capabilities(agent_name). Dynamic agent registration.
```

### PROMPT 78
```
Create backend/cognitive/protocols/routing_rules.py: RoutingRules. async get_rules() -> List[RoutingRule]. async add_rule(rule). async evaluate_rules(input) -> target_agent. Configurable routing.
```

---

## PROMPTS 79-100: API & Testing

### PROMPT 79
```
Create backend/api/v1/cognitive.py: POST /cognitive/process with input, context. Returns CognitiveResult. POST /cognitive/plan with goal. GET /cognitive/execution/{id}/status. WebSocket for streaming.
```

### PROMPT 80
```
Create backend/api/v1/approvals.py: GET /approvals/pending lists pending for user. POST /approvals/{id}/approve. POST /approvals/{id}/reject with feedback. GET /approvals/{id}/status.
```

### PROMPT 81
```
Create backend/api/v1/feedback.py: POST /feedback with output_id, rating, comments. GET /feedback/summary for workspace. POST /feedback/{id}/apply for corrections.
```

### PROMPT 82
```
Create tests/cognitive/__init__.py and tests/cognitive/conftest.py: Fixtures for cognitive tests. mock_llm, sample_perceived_input, sample_plan, test_workspace.
```

### PROMPT 83
```
Create tests/cognitive/test_perception.py: Tests for PerceptionModule. test_entity_extraction(), test_intent_detection(), test_sentiment_analysis(), test_full_perception().
```

### PROMPT 84
```
Create tests/cognitive/test_planning.py: Tests for PlanningModule. test_decomposition(), test_step_planning(), test_cost_estimation(), test_risk_assessment().
```

### PROMPT 85
```
Create tests/cognitive/test_reflection.py: Tests for ReflectionModule. test_quality_scoring(), test_self_critique(), test_correction_execution(), test_reflection_loop().
```

### PROMPT 86
```
Create tests/cognitive/test_hitl.py: Tests for HITL. test_approval_request(), test_approval_flow(), test_timeout_handling(), test_feedback_collection().
```

### PROMPT 87
```
Create tests/cognitive/test_critic.py: Tests for AdversarialCritic. test_adversarial_critique(), test_bias_detection(), test_failure_mode_analysis().
```

### PROMPT 88
```
Create tests/cognitive/test_engine.py: Integration tests for CognitiveEngine. test_full_processing_flow(), test_with_approval(), test_with_reflection_loop().
```

### PROMPT 89
```
Create tests/cognitive/test_protocols.py: Tests for protocols. test_message_format(), test_handoff_protocol(), test_error_handling().
```

### PROMPT 90
```
Create backend/cognitive/benchmarks/perception_bench.py: Benchmark perception accuracy. Test against labeled dataset. Measure precision, recall, F1 for entity extraction.
```

### PROMPT 91
```
Create backend/cognitive/benchmarks/planning_bench.py: Benchmark planning efficiency. Measure decomposition quality, cost estimation accuracy, execution success rate.
```

### PROMPT 92
```
Create backend/cognitive/benchmarks/reflection_bench.py: Benchmark reflection effectiveness. Measure quality improvement per iteration, convergence speed.
```

### PROMPT 93
```
Create backend/cognitive/scripts/tune_prompts.py: Script to tune cognitive prompts. A/B test different prompt versions. Track performance metrics.
```

### PROMPT 94
```
Create backend/cognitive/scripts/analyze_failures.py: Script to analyze cognitive failures. Categorize failure types. Generate insights. Suggest improvements.
```

### PROMPT 95
```
Create backend/cognitive/config.py: CognitiveConfig. quality_threshold: int = 70. max_reflection_iterations: int = 3. approval_timeout_seconds: int = 300. Configurable parameters.
```

### PROMPT 96
```
Create backend/cognitive/metrics.py: CognitiveMetrics. Track: perception_accuracy, planning_efficiency, reflection_improvement, approval_latency, overall_success_rate.
```

### PROMPT 97
```
Create backend/cognitive/logging.py: CognitiveLogger. Structured logging for all cognitive operations. Log levels per module. Request correlation.
```

### PROMPT 98
```
Create backend/cognitive/errors.py: Custom exceptions. PerceptionError, PlanningError, ReflectionError, ApprovalTimeoutError, BudgetExceededError, ProtocolError.
```

### PROMPT 99
```
Create backend/cognitive/health.py: CognitiveHealthChecker. async check_all_modules() verifies perception, planning, reflection, HITL are operational. Returns detailed health report.
```

### PROMPT 100
```
Create backend/cognitive/README.md: Documentation for cognitive engine. Architecture overview, module descriptions, configuration guide, extension points, examples.
```

---

## VERIFICATION

After all prompts completed, verify:
- [ ] Perception extracts entities correctly
- [ ] Planning creates valid execution plans
- [ ] Reflection improves output quality
- [ ] Approval gates work with timeouts
- [ ] Adversarial critic finds issues
- [ ] Full pipeline processes end-to-end
- [ ] All tests pass
