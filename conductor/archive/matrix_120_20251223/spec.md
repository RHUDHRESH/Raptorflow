# Track Specification: Matrix — The Agentic Control Center

## 1. Overview
The **Matrix** is the "Boardroom View" of RaptorFlow—a 100% production-ready, deterministic engine for system-wide command, control, and observability. It serves as the unified interface where founders monitor agent health, strategic campaign ROI, and MLOps performance. It is the "Kill-Switch" for the entire RaptorFlow ecosystem.

## 2. Functional Requirements

### 2.1 Agentic Orchestration & Roles
- **Hierarchical Supervisor:** A "Matrix Lead" node that manages specialized sub-agents.
- **Micro-Agent Pool:**
    - `DriftAnalyzer`: Monitors data distribution changes (GCS/Parquet).
    - `Governor`: Tracks financial burn and budget limits in real-time.
    - `SecurityAuditor`: Ensures PII redaction and policy compliance.
- **Hybrid Deterministic Core:** High-performance code paths for critical "Kill-Switch" actions and resource monitoring.

### 2.2 Memory Architecture
- **Short-Term (L1):** Upstash/Redis for millisecond-latency "Thought-Loops" and active thread state.
- **Long-Term (L2):** Supabase `pgvector` for "Episodic Memory" (historical success/failure of moves).
- **Episodic Recall:** RAG-based context injection for historical campaign retrieval.

### 2.3 Skills Taxonomy
- **Tactical Skills:** `EmergencyHalt`, `InferenceThrottling`, `AutomatedRollback`.
- **Analytical Skills:** `PredictiveROI`, `DriftReporting`, `BudgetForecasting`.
- **System Skills:** `ArtifactLifecycleManagement` (GCS/BigQuery sync).

### 2.4 Storage & Lifecycle
- **Operational Data:** Supabase (PostgreSQL) for active state and metadata.
- **Analytical "Gold Zone":** GCS (Parquet) for immutable, high-scale datasets.
- **Warehouse:** BigQuery for longitudinal performance analysis.
- **Shadow Inference:** Continuous logging of vNext models against Production baseline.

## 3. Technical Specifications

### 3.1 API & Data Contracts
- `GET /v1/matrix/overview`: Real-time health metrics.
- `POST /v1/matrix/kill-switch`: Global system halt.
- `GET /v1/matrix/mlops/drift`: Parquet-based distribution analysis.
- **Schema:** Unified `Telemetry` and `State` models using Pydantic.

### 3.2 Performance & Observability
- **Latency:** <200ms for Dashboard state updates via Supabase Realtime.
- **Throughput:** Capable of processing 100+ concurrent agent traces.
- **Observability:** Centralized `serving.py` logging for all inference calls.

## 4. Cloud Infrastructure
- **Deployment:** Cloud Run (Backend), Vercel (Frontend).
- **Secrets:** GCP Secret Manager.
- **Observability:** Cloud Logging & BigQuery Analytics.

## 5. Acceptance Criteria
- [ ] Global Kill-Switch stops all running LangGraph threads within <1s.
- [ ] Data drift alerts trigger when distribution changes exceed 10% (Osipov pattern).
- [ ] Agent traces are successfully archived from Supabase to GCS/Parquet.
- [ ] Code coverage for the Matrix service exceeds 90%.
