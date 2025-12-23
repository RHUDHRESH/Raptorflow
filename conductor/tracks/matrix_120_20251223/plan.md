# Implementation Plan: Matrix — The Agentic Control Center (120-Phase Deep Build)

#### Block A: Foundation & Core Telemetry (Phases 1-10) [checkpoint: 58820c9]
- [x] Phase 001: Backend - Define `TelemetryEvent` Pydantic model with strict validation. 4d7f3ef
- [x] Phase 002: Backend - Define `SystemState` schema for real-time agent pool tracking. 3c678cf
- [x] Phase 003: Backend - Implement `MatrixService` interface in `backend/services/matrix_service.py`. bb99768
- [x] Phase 004: Backend - Write Red Phase tests for `MatrixService.initialize_telemetry_stream()`. bbe002a
- [x] Phase 005: Backend - Implement `MatrixService.initialize_telemetry_stream()` (Upstash integration). 0d80a3f
- [x] Phase 006: Backend - Create `TelemetryMiddleware` to capture all API latencies and error rates. f5c9a7a
- [x] Phase 007: Backend - Write Red Phase tests for `MatrixService.capture_agent_heartbeat()`. a70a29b
- [x] Phase 008: Backend - Implement `MatrixService.capture_agent_heartbeat()` with expiration logic. 8019b0d
- [x] Phase 009: Backend - Implement centralized `serving.py` for logging model inference metadata. d0f3e1f
- [x] Phase 010: Conductor - User Manual Verification 'Foundation & Core Telemetry' (Protocol in workflow.md)

#### Block B: Osipov Data Engineering - The Gold Zone (Phases 11-20) [checkpoint: aab7e9d]
- [x] Phase 011: Backend - Configure GCS `raptorflow-gold-zone` bucket for Parquet storage. 8d2409f
- [x] Phase 012: Backend - Implement `ParquetExporter` using `pyarrow` for telemetry archival. 2a6a5e9
- [x] Phase 013: Backend - Write Red Phase tests for `ParquetExporter.export_batch()`. 8f5a739
- [x] Phase 014: Backend - Implement `ParquetExporter.export_batch()` with schema evolution support. 42a9f23
- [x] Phase 015: Backend - Create `GCSLifecycleManager` for moving raw logs to archival storage. 68b3a7e
- [x] Phase 016: Backend - Implement `BigQueryMatrixLoader` for periodic Parquet-to-BigQuery sync. b2d6484
- [x] Phase 017: Backend - Write Red Phase tests for `BigQueryMatrixLoader.sync_partition()`. 5636db5
- [x] Phase 018: Backend - Implement BigQuery views for longitudinal performance analysis. 51f7178
- [x] Phase 019: Backend - Implement `StorageEfficiencyAuditor` (Osipov's cost tracking pattern). 1b1b7bb
- [x] Phase 020: Conductor - User Manual Verification 'Osipov Data Engineering' (Protocol in workflow.md)

#### Block C: Taulli Agentic Spine & Supervisor Pattern (Phases 21-35) [checkpoint: 259a75c]
- [x] Phase 021: Backend - Implement `MatrixSupervisorAgent` using LangGraph. 6663fc9
- [x] Phase 022: Backend - Define `MatrixState` TypedDict for supervisor orchestration. fff88df
- [x] Phase 023: Backend - Implement `DriftAnalyzerAgent` (Statistical test specialist). b3afef7
- [x] Phase 024: Backend - Implement `GovernorAgent` (Budget & Token limit specialist). 9e040e6
- [x] Phase 025: Backend - Implement `SecurityAuditorAgent` (PII & Policy specialist). b3e32b3
- [x] Phase 026: Backend - Write Red Phase tests for `MatrixSupervisor.route_intent()`. 3d57909
- [x] Phase 027: Backend - Implement `MatrixSupervisor.route_intent()` (Intent detection). 32987a9
- [x] Phase 028: Backend - Implement `MatrixSupervisor.delegate_to_specialist()`. 5273e3e
- [x] Phase 029: Backend - Implement `MatrixSupervisor.aggregate_findings()`. 9695fe1
- [x] Phase 030: Backend - Implement `HandoffProtocol` for agent-to-agent communication. ad88c48
- [x] Phase 031: Backend - Write Red Phase tests for `MatrixSupervisor.execute_loop()`. 78a944b
- [x] Phase 032: Backend - Implement `MatrixSupervisor.execute_loop()` with state persistence. fdca748
- [x] Phase 033: Backend - Implement `HumanInTheLoop` (HITL) interrupt node for critical approvals. b8543ae
- [x] Phase 034: Backend - Implement `AgentPoolMonitor` for real-time thread counting. 8238ca7
- [x] Phase 035: Conductor - User Manual Verification 'Agentic Spine' (Protocol in workflow.md)

#### Block D: Skills & Tool Taxonomy (Phases 36-50) [checkpoint: edef386]
- [x] Phase 036: Backend - Define `MatrixSkill` base class and registration system. 1baffca
- [x] Phase 037: Backend - Implement `EmergencyHaltSkill` (The Kill-Switch). 1fad000
- [x] Phase 038: Backend - Implement `InferenceThrottlingSkill` (Rate limiting). 8980b21
- [x] Phase 039: Backend - Implement `CachePurgeSkill` (Upstash management). b31e9bc
- [x] Phase 040: Backend - Write Red Phase tests for `EmergencyHaltSkill.execute()`. 9c417b3
- [x] Phase 041: Backend - Implement `EmergencyHaltSkill.execute()` with thread-kill logic. aeafcb3
- [x] Phase 042: Backend - Implement `ResourceScalingSkill` (Mock for Cloud Run scaling). aeafcb3
- [x] Phase 043: Backend - Implement `ArchiveLogsSkill` (GCS trigger). 7c53770
- [x] Phase 044: Backend - Implement `RetrainTriggerSkill` (MLOps lifecycle). 7c53770
- [x] Phase 045: Backend - Define `SkillPrivilegeMatrix` (RBAC for tools). 7c53770
- [x] Phase 046: Backend - Write Red Phase tests for `SkillSelectorAgent.pick_best_tool()`. 7c53770
- [x] Phase 047: Backend - Implement `SkillSelectorAgent.pick_best_tool()` (Few-shot prompting). 7c53770
- [x] Phase 048: Backend - Implement `ToolExecutionWrapper` with comprehensive error handling. 7c53770
- [x] Phase 049: Backend - Implement `ToolOutputValidator` for structured JSON verification. 7c53770
- [x] Phase 050: Conductor - User Manual Verification 'Skills & Tool Taxonomy' (Protocol in workflow.md) 9e36083

#### Block E: Memory Architecture & RAG Hardening (Phases 51-65)
- [ ] Phase 051: Backend - Implement `L1_ShortTermMemory` using Redis (Upstash).
- [ ] Phase 052: Backend - Implement `L2_EpisodicMemory` using Supabase `pgvector`.
- [ ] Phase 053: Backend - Implement `L3_SemanticMemory` (Brand Foundation lookup).
- [ ] Phase 054: Backend - Write Red Phase tests for `MemoryManager.store_trace()`.
- [ ] Phase 055: Backend - Implement `MemoryManager.store_trace()` with embeddings.
- [ ] Phase 056: Backend - Implement `RAGRetrievalNode` with citation support.
- [ ] Phase 057: Backend - Implement `MemoryDecayPolicy` (Pruning old short-term state).
- [ ] Phase 058: Backend - Implement `EpisodicRecall` (Retrieve similar campaign outcomes).
- [ ] Phase 059: Backend - Write Red Phase tests for `RAG.calculate_relevance_score()`.
- [ ] Phase 060: Backend - Implement `ContextWindowCompressor` for token efficiency.
- [ ] Phase 061: Backend - Implement `KnowledgeGraphConnector` (Conceptual linking).
- [ ] Phase 062: Backend - Implement `MemorySelfReflection` agent (Summarizes daily events).
- [ ] Phase 063: Backend - Implement `AgentSharedState` (Common context pool).
- [ ] Phase 064: Backend - Implement `StateCheckpointManager` (LangGraph checkpointing).
- [ ] Phase 065: Conductor - User Manual Verification 'Memory & RAG' (Protocol in workflow.md)

#### Block F: Osipov MLOps Guardrails (Phases 66-80)
- [ ] Phase 066: Backend - Implement `DriftDetectionService` (Statistical K-S tests).
- [ ] Phase 067: Backend - Write Red Phase tests for `DriftDetection.calculate_p_value()`.
- [ ] Phase 068: Backend - Implement `DriftDetection.calculate_p_value()`.
- [ ] Phase 069: Backend - Implement `ShadowInferenceService` (Parallel model runs).
- [ ] Phase 070: Backend - Implement `PerformanceComparator` (vNext vs Production).
- [ ] Phase 071: Backend - Write Red Phase tests for `ShadowInference.log_comparison()`.
- [ ] Phase 072: Backend - Implement `ShadowInference.log_comparison()`.
- [ ] Phase 073: Backend - Implement `InferenceLatencyAlert` (Trigger on >P95 spike).
- [ ] Phase 074: Backend - Implement `ModelAccuracyMonitor` (Feedback loop integration).
- [ ] Phase 075: Backend - Implement `DeterministicFallback` (Switch to heuristic on LLM fail).
- [ ] Phase 076: Backend - Implement `SystemSanityCheck` (Periodic agent health probe).
- [ ] Phase 077: Backend - Implement `CostGovernor` (Calculate daily dollar burn).
- [ ] Phase 078: Backend - Implement `KillSwitchCircuitBreaker` (Auto-halt on critical drift).
- [ ] Phase 079: Backend - Implement `ModelLineageTracker` (GCS artifact linking).
- [ ] Phase 080: Conductor - User Manual Verification 'MLOps Guardrails' (Protocol in workflow.md)

#### Block G: API, Security & Governance (Phases 81-90)
- [ ] Phase 081: Backend - Create `api/v1/matrix.py` FastAPI router.
- [ ] Phase 082: Backend - Implement `GET /overview` (Aggregated health dashboard).
- [ ] Phase 083: Backend - Implement `POST /kill-switch` with audit logging.
- [ ] Phase 084: Backend - Implement `GET /mlops/drift` (Detailed statistical report).
- [ ] Phase 085: Backend - Implement `GET /governance/burn` (Financial data).
- [ ] Phase 086: Backend - Implement `PII_Redactor` utility for all telemetry logs.
- [ ] Phase 087: Backend - Implement `RBAC_Guard` (Restricting Matrix to Admin).
- [ ] Phase 088: Backend - Implement `AuditLogService` (Tracking who touched the Matrix).
- [ ] Phase 089: Backend - Write Integration Tests for all Matrix Endpoints.
- [ ] Phase 090: Conductor - User Manual Verification 'API & Security' (Protocol in workflow.md)

#### Block H: Frontend Boardroom UI (UX) (Phases 91-100)
- [ ] Phase 091: Frontend - Scaffold `MatrixDashboard` with RaptorFlow tokens.
- [ ] Phase 092: Frontend - Implement `SystemStatusHeader` (RAG status indicator).
- [ ] Phase 093: Frontend - Implement `AgentPoolList` (Real-time active threads).
- [ ] Phase 094: Frontend - Implement `GlobalKillSwitchButton` with safety double-tap.
- [ ] Phase 095: Frontend - Build `DriftChart` using Shadcn/Charts.
- [ ] Phase 096: Frontend - Build `FinancialBurnChart` (Daily/Monthly view).
- [ ] Phase 097: Frontend - Implement `InferenceLogExplorer` (JetBrains Mono style).
- [ ] Phase 098: Frontend - Implement `LoadingSkeletons` and `EmptyStates`.
- [ ] Phase 099: Frontend - Conduct 100% Phase Verification & Final Smoke Test.
- [ ] Phase 100: Conductor - User Manual Verification 'The Boardroom View' (Protocol in workflow.md)

#### Block I: Infrastructure, DevOps & Cloud Push (Phases 101-120)
- [ ] Phase 101: DevOps - Enable GCP APIs: Cloud Run, BigQuery, GCS, Secret Manager, Cloud Build.
- [ ] Phase 102: DevOps - Configure Supabase Project: Enable `pgvector`, Realtime, and Auth.
- [ ] Phase 103: DevOps - Provision Upstash Redis instance and configure Global Rate Limiting.
- [ ] Phase 104: DevOps - Create `raptorflow-matrix-sa` (Service Account) with minimal IAM roles.
- [ ] Phase 105: Backend - Integrate GCP Secret Manager for Supabase/Upstash/Vertex keys.
- [ ] Phase 106: Backend - Configure Cloud Run `service.yaml` with memory/CPU limits & VPC connectors.
- [ ] Phase 107: Backend - Implement `HealthCheck` endpoint for Cloud Run liveness/readiness probes.
- [ ] Phase 108: DevOps - Create GitHub Actions workflow: `backend-ci-cd.yml` (Test -> Build -> Cloud Run).
- [ ] Phase 109: Frontend - Configure Vercel project with Environment Variable injection for Matrix API.
- [ ] Phase 110: Frontend - Implement Supabase Auth Guard for the Matrix Dashboard (`/matrix`).
- [ ] Phase 111: DevOps - Setup Staging vs. Production environment branching (Supabase/GCP).
- [ ] Phase 112: Backend - Configure CORS policies between Vercel (Frontend) and Cloud Run (Backend).
- [ ] Phase 113: Backend - Implement Cloud Logging structured logs for centralized agent tracing.
- [ ] Phase 114: MLOps - Configure BigQuery scheduled queries for daily Matrix analytical reports.
- [ ] Phase 115: DevOps - Implement "Blue-Green" deployment logic via GitHub Actions and Cloud Run.
- [ ] Phase 116: Security - Prune IAM roles and enable Cloud Armor (WAF) for Matrix API protection.
- [ ] Phase 117: Monitoring - Setup GCP Error Reporting & Alerts for Matrix "Kill-Switch" triggers.
- [ ] Phase 118: Verification - Conduct E2E Production Smoke Test: Auth -> Matrix -> Agent Trace.
- [ ] Phase 119: Performance - Benchmarking: Verify <200ms latency for production Matrix updates.
- [ ] Phase 120: Conductor - User Manual Verification 'Infrastructure, DevOps & Cloud Push' (Protocol in workflow.md)
