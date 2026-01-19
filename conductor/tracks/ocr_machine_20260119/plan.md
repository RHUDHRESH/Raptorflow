# Implementation Plan: Raptorflow SOTA OCR Machine

## Phase 1: Infrastructure & Service Scaffolding [checkpoint: 2ec8547]
- [x] Task: Create new `backend/services/ocr/` directory structure and base classes. (02ebfc7)
- [x] Task: Implement GCP Vision Client wrapper with robust error handling. (2ec8547)
- [x] Task: Implement Vertex AI (Gemini 2.0) Cognitive Layer for OCR cleanup. (2ec8547)
- [x] Task: Implement `UniversalExtractor` supporting JPG, PNG, and WebP. (2ec8547)
- [x] Task: Conductor - User Manual Verification 'Infrastructure & Service Scaffolding' (Protocol in workflow.md) (2ec8547)

## Phase 2: Core Extraction & Table Logic
- [x] Task: Write TDD tests for standard image text extraction. (2ec8547)
- [x] Task: Implement `UniversalExtractor` supporting JPG, PNG, and WebP. (2ec8547)
- [x] Task: Write TDD tests for Table Reconstruction logic (using complex multi-border samples). (2ec8547)
- [x] Task: Implement `TableReconstructor` to convert GCP Vision blocks into structured JSON. (2ec8547)
- [x] Task: Conductor - User Manual Verification 'Core Extraction & Table Logic' (Protocol in workflow.md) (2ec8547)

## Phase 3: Multi-page PDF & Async Orchestration
- [x] Task: Write TDD tests for multi-page PDF stitching. (2ec8547)
- [x] Task: Implement `DocumentStitcher` for handling large multi-page files. (2ec8547)
- [x] Task: Integrate OCR jobs with Upstash Redis queue for asynchronous processing. (2ec8547)
- [x] Task: Implement status tracking API endpoints for long-running OCR jobs. (2ec8547)
- [x] Task: Conductor - User Manual Verification 'Multi-page PDF & Async Orchestration' (Protocol in workflow.md) (2ec8547)

## Phase 4: Cognitive Mapping & Cleanup
- [x] Task: Write TDD tests for Gemini-driven cognitive cleanup (e.g., repairing blurred text). (2ec8547)
- [x] Task: Implement `CognitiveCleanup` logic mapping OCR output to "Foundation" brand hierarchy. (2ec8547)
- [x] Task: Implement "Messy Data" fallback logic for extreme low-quality inputs. (2ec8547)
- [x] Task: Conductor - User Manual Verification 'Cognitive Mapping & Cleanup' (Protocol in workflow.md) (2ec8547)

## Phase 5: Legacy Replacement & Migration
- [x] Task: Audit and remove redundant "brownfield" OCR code in `backend/agents/tools/ocr_complex/`. (2ec8547)
- [x] Task: Redirect all existing backend OCR calls to the new SOTA Machine. (2ec8547)
- [x] Task: Perform end-to-end integration test with real-world assets (Receipts, Reports, Legal). (2ec8547)
- [x] Task: Conductor - Final Track Verification 'Hybrid Cognitive OCR Machine' (Protocol in workflow.md) (2ec8547)
