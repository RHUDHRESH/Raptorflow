# Implementation Plan: Moves & Campaigns 100-Step Production Roadmap

## Phase 1: Environment & Infrastructure (Tasks 1-10)
- [x] 1. Task: Initialize GCP Secret Manager for API keys (Vertex AI, Supabase, Upstash)
- [x] 2. Task: Setup Supabase Database Schema for `campaigns` and `moves` tables
- [x] 3. Task: Configure Upstash Redis instance for Episodic Memory session state
- [x] 4. Task: Write failing tests for Environment Variable loading and validation
- [x] 5. Task: Implement `core/config.py` with Pydantic for strict environment validation
- [x] 6. Task: Setup BigQuery datasets for raw data ingestion and "Gold" storage
- [x] 7. Task: Initialize Vercel project and link to the repository for frontend deployment
- [x] 8. Task: Configure GitHub Actions CI for multi-repo test execution
- [x] 9. Task: Verify connectivity across all infra components (Supabase, Redis, GCP)
- [x] 10. Task: Conductor - User Manual Verification 'Environment & Infrastructure' (Protocol in workflow.md)

## Phase 2: Data Ingestion & 'VACUUM' Quality Engine (Tasks 11-20)
- [ ] 11. Task: Create ingestion script for 30k lines of business context from instructions
- [ ] 12. Task: Implement 'VACUUM' Valid node: Check data types and mandatory fields
- [ ] 13. Task: Implement 'VACUUM' Accurate node: Cross-reference data points for consistency
- [ ] 14. Task: Write failing tests for Data Cleaning pipeline
- [ ] 15. Task: Implement PySpark-style ETL to convert raw context to Parquet in GCS
- [ ] 16. Task: Execute 'VACUUM' Uniform: Standardize formatting for coordinates and dates
- [ ] 17. Task: Execute 'VACUUM' Unified: Merge conflicting context into a single source of truth
- [ ] 18. Task: Index "Gold" context into pgvector for semantic retrieval
- [ ] 19. Task: Verify data quality scores (>95% valid records)
- [ ] 20. Task: Conductor - User Manual Verification 'Data Ingestion & VACUUM Engine' (Protocol in workflow.md)

## Phase 3: Cognitive Spine - LangGraph Foundation (Tasks 21-30)
- [ ] 21. Task: Define `State` schema for the Moves & Campaigns orchestrator
- [ ] 22. Task: Implement LangGraph `SqliteSaver` for local persistence
- [ ] 23. Task: Write failing tests for Graph state transitions and cycle handling
- [ ] 24. Task: Implement the "Router" node for directing between Campaign and Move tasks
- [ ] 25. Task: Configure `PostgresSaver` (Supabase) for production persistence
- [ ] 26. Task: Implement error handling nodes (Retries, Fallbacks)
- [ ] 27. Task: Define HITL (Human-in-the-loop) interruption points for approvals
- [ ] 28. Task: Setup visual graph rendering for debugging and documentation
- [ ] 29. Task: Verify state recovery from episodic memory after simulated crashes
- [ ] 30. Task: Conductor - User Manual Verification 'Cognitive Spine' (Protocol in workflow.md)

## Phase 4: Tiered Memory & Context Retrieval (Tasks 31-40)
- [ ] 31. Task: Implement `EpisodicMemory` class using Redis/Upstash
- [ ] 32. Task: Implement `SemanticMemory` class using Supabase pgvector
- [ ] 33. Task: Write failing tests for RAG (Retrieval Augmented Generation) context injection
- [ ] 34. Task: Implement similarity search node with MMR (Maximal Marginal Relevance)
- [ ] 35. Task: Create `LongTermMemory` for historical outcome storage (Postgres)
- [ ] 36. Task: Implement context pruning to fit within LLM context windows (Taulli pattern)
- [ ] 37. Task: Setup metadata filtering for targeted context retrieval
- [ ] 38. Task: Verify retrieval latency targets (<150ms for semantic lookup)
- [ ] 39. Task: Integrate memory updater node to update state after successful actions
- [ ] 40. Task: Conductor - User Manual Verification 'Tiered Memory' (Protocol in workflow.md)

## Phase 5: Campaign Module - Strategic Planning (Tasks 41-50)
- [ ] 41. Task: Design `CampaignPlanner` agent persona and system prompts
- [ ] 42. Task: Implement 90-day arc generation logic from Business Context
- [ ] 43. Task: Write failing tests for Strategic Alignment (Campaign vs Brand Kit)
- [ ] 44. Task: Implement KPI objective setter node within the campaign graph
- [ ] 45. Task: Create the Gantt chart data structure for campaign visualization
- [ ] 46. Task: Implement the "Campaign Auditor" node for internal reflection
- [ ] 47. Task: Setup the frontend `CampaignView` with Shadcn/UI Gantt components
- [ ] 48. Task: Verify multi-agent brainstorming for campaign pivots
- [ ] 49. Task: Integrate campaign data persistence into Supabase
- [ ] 50. Task: Conductor - User Manual Verification 'Campaign Planning' (Protocol in workflow.md)

## Phase 6: Move Module - Weekly Task Breakdown (Tasks 51-60)
- [ ] 51. Task: Design `MoveGenerator` agent persona and prompts
- [ ] 52. Task: Implement logic to map weekly "Moves" to 90-day Campaign milestones
- [ ] 53. Task: Write failing tests for Task Priority and Deadline calculation
- [ ] 54. Task: Implement the "Move Refiner" node for actionable task formatting
- [ ] 55. Task: Create the `MovePacket` data structure (Description, Owner, Tools needed)
- [ ] 56. Task: Implement the "Resource Manager" node to check for tool availability
- [ ] 57. Task: Setup the frontend `MovesDashboard` with interactive task cards
- [ ] 58. Task: Verify the link between completed Moves and Campaign progress
- [ ] 59. Task: Integrate Move persistence and status tracking
- [ ] 60. Task: Conductor - User Manual Verification 'Move Generation' (Protocol in workflow.md)

## Phase 7: Toolbelt - Agentic Skills & Execution (Tasks 61-70)
- [ ] 61. Task: Implement `WebSearch` tool with Tavily/Serper integration
- [ ] 62. Task: Implement `AssetGen` skill for generating copy and image prompts (Muse integration)
- [ ] 63. Task: Write failing tests for Tool Sandbox execution and error catching
- [ ] 64. Task: Implement `SocialAPI` skeletons (LinkedIn, X) for Move execution
- [ ] 65. Task: Create the `SkillExecutor` node for handling tool calls in LangGraph
- [ ] 66. Task: Implement output parsing for tool results back into the graph state
- [ ] 67. Task: Setup tool usage telemetry (Token count, Latency, Success rate)
- [ ] 68. Task: Verify agent's ability to "think" (reason) before calling tools (o1 pattern)
- [ ] 69. Task: Implement the "Safety Validator" for tool outputs
- [ ] 70. Task: Conductor - User Manual Verification 'Toolbelt Skills' (Protocol in workflow.md)

## Phase 8: Inference Optimization & Performance (Tasks 71-80)
- [ ] 71. Task: Implement result caching in Redis for expensive LLM calls
- [ ] 72. Task: Setup prompt versioning using LangSmith or local templates
- [ ] 73. Task: Write failing tests for Cache Hits and Latency targets
- [ ] 74. Task: Implement batch processing for non-interactive agent tasks
- [ ] 75. Task: Optimize semantic search indices for faster RAG
- [ ] 76. Task: Implement "Streaming" responses for interactive agent components
- [ ] 77. Task: Configure model-specific optimizations (e.g., using GPT-4o-mini for simple nodes)
- [ ] 78. Task: Verify cache invalidation logic for stale context
- [ ] 79. Task: Integrate "Inference Cost Governor" to prevent budget overruns
- [ ] 80. Task: Conductor - User Manual Verification 'Inference Optimization' (Protocol in workflow.md)

## Phase 9: Governance, MLOps & Monitoring (Tasks 81-90)
- [ ] 81. Task: Setup GCP Cloud Monitoring dashboard for Agent Telemetry
- [ ] 82. Task: Implement `QualityGate` nodes for automated outcome evaluation
- [ ] 83. Task: Write failing tests for Alerting thresholds (Cost, Failure rate)
- [ ] 84. Task: Implement "Audit Trail" logger for all agent decisions
- [ ] 85. Task: Setup LangSmith (or alternative) for tracing complex multi-agent runs
- [ ] 86. Task: Implement automated hyperparameter tuning for prompt templates (Osipov pattern)
- [ ] 87. Task: Create the "Kill-Switch" UI component in Matrix for emergency stop
- [ ] 88. Task: Verify "Drift Detection" for agent performance over time
- [ ] 89. Task: Integrate performance scores into the `metadata.json` updates
- [ ] 90. Task: Conductor - User Manual Verification 'Governance & Monitoring' (Protocol in workflow.md)

## Phase 10: Final Integration & Production Deployment (Tasks 91-100)
- [ ] 91. Task: Perform full E2E system integration test (Foundation -> Campaign -> Moves)
- [ ] 92. Task: Execute load testing on the Cognitive Spine
- [ ] 93. Task: Write failing tests for Final Deployment Smoke Test
- [ ] 94. Task: Deploy backend to GCP Cloud Run with production env vars
- [ ] 95. Task: Deploy frontend to Vercel with proper API routing
- [ ] 96. Task: Finalize documentation (README, API Docs, User Guide)
- [ ] 97. Task: Implement "Post-Launch" monitoring heartbeat
- [ ] 98. Task: Verify mobile responsiveness for all new UI modules
- [ ] 99. Task: Create the Final Production Release commit and Git Note
- [ ] 100. Task: Conductor - Final Track Completion Review & Checkpoint
