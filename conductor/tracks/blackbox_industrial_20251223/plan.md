# Plan: Blackbox Industrial Implementation (100 Phases)

## Phase 1: Foundation & Infrastructure (Phases 1-10)
- [x] Task 1: Create `backend/models/blackbox.py` (Pydantic schemas for Telemetry, Outcomes, Learnings) [0a557c0]
- [~] Task 2: Define SQL Migration for `blackbox_telemetry` (ID, move_id, agent_id, trace, tokens, latency, timestamp)
- [ ] Task 3: Define SQL Migration for `blackbox_outcomes` (ID, source, value, confidence, timestamp)
- [x] Task 4: Define SQL Migration for `blackbox_learnings` (ID, content, embedding, source_ids, type) [c66ca91]
- [x] Task 5: Setup BigQuery Dataset `raptorflow_analytics` and table `telemetry_stream` [f5362dd]
- [x] Task 6: Configure GCP Secret Manager for Blackbox (API Keys for Search, Scrape) [0a1a6df]
- [x] Task 7: Initialize `backend/services/blackbox_service.py` skeleton [2359810]
- [x] Task 8: Configure Upstash Redis client in `backend/core/cache.py` for Blackbox [9f32cb2]
- [x] Task 9: Implement `BlackboxService._get_bigquery_client()` with service account auth [a582ad5]
- [ ] Task 10: Conductor - User Manual Verification 'Foundation & Infrastructure'

## Phase 2: Telemetry & Tracing (Phases 11-20)
- [ ] Task 11: Implement `BlackboxService.log_telemetry(trace_data)` (Async PG write)
- [ ] Task 12: Implement `BlackboxService.stream_to_bigquery(trace_data)` (Async BQ stream)
- [ ] Task 13: Create `backend/core/middleware.py` trace_id generator
- [ ] Task 14: Implement `@trace_agent` decorator for automated logging
- [ ] Task 15: Implement `BlackboxService.get_agent_audit_log(agent_id)`
- [ ] Task 16: Write Unit Test: `test_telemetry_capture_integrity`
- [ ] Task 17: Write Unit Test: `test_bigquery_streaming_latency`
- [ ] Task 18: Implement `BlackboxService.calculate_move_cost(move_id)`
- [ ] Task 19: Create `backend/api/v1/blackbox_telemetry.py` endpoints
- [ ] Task 20: Conductor - User Manual Verification 'Telemetry & Tracing'

## Phase 3: Cognitive Memory & Vector Store (Phases 21-30)
- [ ] Task 21: Implement `BlackboxService.upsert_learning_embedding(text, metadata)`
- [ ] Task 22: Setup Vertex AI embedding client integration
- [ ] Task 23: Implement `BlackboxService.search_strategic_memory(query, limit)`
- [ ] Task 24: Implement `BlackboxService.link_learning_to_evidence(learning_id, trace_ids)`
- [ ] Task 25: Implement Learning Categorization logic (Strategic, Tactical, Content)
- [ ] Task 26: Write Unit Test: `test_vector_search_relevance`
- [ ] Task 27: Implement `BlackboxService.get_memory_context_for_planner(move_type)`
- [ ] Task 28: Implement Memory Pruning logic (Removing redundant/outdated insights)
- [ ] Task 29: Create `backend/api/v1/blackbox_memory.py` endpoints
- [ ] Task 30: Conductor - User Manual Verification 'Cognitive Memory'

## Phase 4: Agentic Orchestration - LangGraph Spine (Phases 31-40)
- [ ] Task 31: Create `backend/graphs/blackbox_analysis.py` (Base State Definition)
- [ ] Task 32: Implement `AnalysisState` (telemetry, findings, outcomes, reflection)
- [ ] Task 33: Define Graph Node: `ingest_telemetry_node`
- [ ] Task 34: Define Graph Node: `extract_insights_node` (Agentic)
- [ ] Task 35: Define Graph Node: `attribute_outcomes_node` (Math-heavy)
- [ ] Task 36: Define Graph Node: `reflect_and_validate_node` (Self-correction)
- [ ] Task 37: Implement Conditional Edges for Graph (Retry on low confidence)
- [ ] Task 38: Integrate `BlackboxService` into LangGraph nodes
- [ ] Task 39: Write Integration Test: `test_blackbox_graph_execution`
- [ ] Task 40: Conductor - User Manual Verification 'LangGraph Spine'

## Phase 5: Multi-Agent Specialists (Phases 41-50)
- [ ] Task 41: Implement `BlackboxSpecialist` (Base Agent Class)
- [ ] Task 42: Create `ROI_Analyst_Agent` (System prompts focused on attribution)
- [ ] Task 43: Create `Strategic_Drift_Agent` (Detects deviation from Foundation)
- [ ] Task 44: Create `Competitor_Intelligence_Agent` (Feeds on scrape telemetry)
- [ ] Task 45: Implement Agent Collaboration protocol (Shared state updates)
- [ ] Task 46: Implement "Critique" loop between Analyst and Supervisor
- [ ] Task 47: Write Unit Test: `test_agent_specialization_accuracy`
- [ ] Task 48: Implement Tool: `fetch_historical_performance_tool`
- [ ] Task 49: Implement Tool: `fetch_brand_kit_alignment_tool`
- [ ] Task 50: Conductor - User Manual Verification 'Multi-Agent Specialists'

## Phase 6: ROI & Attribution Engine (Phases 51-60)
- [ ] Task 51: Implement `BlackboxService.compute_roi(campaign_id)`
- [ ] Task 52: Define Attribution Models (First-touch, Last-touch, Linear)
- [ ] Task 53: Implement `OutcomeIngestionService` (External webhook handler)
- [ ] Task 54: Implement `BlackboxService.calculate_momentum_score()`
- [ ] Task 55: Implement Statistical Confidence calculator for attribution
- [ ] Task 56: Write Unit Test: `test_roi_calculation_math`
- [ ] Task 57: Implement `BlackboxService.get_roi_matrix_data()`
- [ ] Task 58: Create `backend/api/v1/blackbox_roi.py` endpoints
- [ ] Task 59: Implement BigQuery SQL for complex longitudinal analysis
- [ ] Task 60: Conductor - User Manual Verification 'ROI Engine'

## Phase 7: The Learning Flywheel (Phases 61-70)
- [ ] Task 61: Implement `BlackboxService.trigger_learning_cycle()` (Background task)
- [ ] Task 62: Implement `LearningAgent` (Summarizes outcomes into pivots)
- [ ] Task 63: Implement `PivotRecommendation` generator
- [ ] Task 64: Implement logic to update `Foundation` modules from `Blackbox` insights
- [ ] Task 65: Implement "Evidence Packaging" (Attaching trace links to insights)
- [ ] Task 66: Write Unit Test: `test_learning_flywheel_output`
- [ ] Task 67: Implement `BlackboxService.get_learning_feed()`
- [ ] Task 68: Implement "Insight Validation" (Human-in-the-loop approval state)
- [ ] Task 69: Create `backend/api/v1/blackbox_learning.py` endpoints
- [ ] Task 70: Conductor - User Manual Verification 'Learning Flywheel'

## Phase 8: Frontend - Dashboard & Explorer (Phases 71-80)
- [ ] Task 71: Create `raptorflow-app/src/app/blackbox/layout.tsx` (Premium sidebar)
- [ ] Task 72: Build `Blackbox.BoardroomView`: Executive Summary Cards
- [ ] Task 73: Build `Blackbox.MomentumChart`: Animated SVG/Canvas chart
- [ ] Task 74: Build `Blackbox.TelemetryFeed`: Real-time trace component
- [ ] Task 75: Build `Blackbox.TraceDetail`: Modal for prompt/response inspection
- [ ] Task 76: Build `Blackbox.ROIMatrix`: Data table with heatmap cells
- [ ] Task 77: Implement `raptorflow-app/src/lib/api/blackbox.ts` (Fetchers)
- [ ] Task 78: Build `Blackbox.PivotCard`: Interactive recommendation UI
- [ ] Task 79: Implement "One-click Pivot" execution logic in UI
- [ ] Task 80: Conductor - User Manual Verification 'Frontend Dashboard'

## Phase 9: Advanced UI & Visualization (Phases 81-90)
- [ ] Task 81: Build `Blackbox.EvidenceLog`: List of search/scrape links
- [ ] Task 82: Build `Blackbox.AgentAuditLog`: Raw prompt/response viewer
- [ ] Task 83: Build `Blackbox.MetricDelta`: Animated percentage change
- [ ] Task 84: Implement `Blackbox.export_summary_pdf()`
- [ ] Task 85: Build `Blackbox.StrategicDriftRadar`: Radar chart for alignment
- [ ] Task 86: Build `Blackbox.CostHeatmap`: Token usage by module
- [ ] Task 87: Implement Responsive Layout for Mobile (iPhone)
- [ ] Task 88: Add Framer Motion transitions to all Blackbox navigation
- [ ] Task 89: Build `Blackbox.EmptyState`: Premium placeholder system
- [ ] Task 90: Conductor - User Manual Verification 'Advanced UI'

## Phase 10: Hardening, Security & Scale (Phases 91-100)
- [ ] Task 91: Implement Rate Limiting for all Blackbox API endpoints
- [ ] Task 92: Audit GCP Secret Manager permissions for Production
- [ ] Task 93: Implement PII Masking in telemetry logs
- [ ] Task 94: Perform Load Test: 1000 concurrent telemetry streams
- [ ] Task 95: Optimize BigQuery query costs (Partitioning/Clustering)
- [ ] Task 96: Implement `Blackbox.Service.Auto_Cleanup` (Telemetry retention)
- [ ] Task 97: Final End-to-End Integration Test: Move -> Outcome -> Learning
- [ ] Task 98: Update `README.md` with Blackbox Architecture diagrams
- [ ] Task 99: Final Design Gate Review: Alignment with "Quiet Luxury" tokens
- [ ] Task 100: Conductor - User Manual Verification 'Final Hardening'
