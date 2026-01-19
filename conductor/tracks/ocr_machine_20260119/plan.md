# Implementation Plan: Raptorflow SOTA OCR Machine

## Phase 1: Infrastructure & Service Scaffolding
- [x] Task: Create new `backend/services/ocr/` directory structure and base classes. (02ebfc7)
- [ ] Task: Implement GCP Vision Client wrapper with robust error handling.
- [ ] Task: Implement Vertex AI (Gemini 2.0) Cognitive Layer for OCR cleanup.
- [ ] Task: Conductor - User Manual Verification 'Infrastructure & Service Scaffolding' (Protocol in workflow.md)

## Phase 2: Core Extraction & Table Logic
- [ ] Task: Write TDD tests for standard image text extraction.
- [ ] Task: Implement `UniversalExtractor` supporting JPG, PNG, and WebP.
- [ ] Task: Write TDD tests for Table Reconstruction logic (using complex multi-border samples).
- [ ] Task: Implement `TableReconstructor` to convert GCP Vision blocks into structured JSON.
- [ ] Task: Conductor - User Manual Verification 'Core Extraction & Table Logic' (Protocol in workflow.md)

## Phase 3: Multi-page PDF & Async Orchestration
- [ ] Task: Write TDD tests for multi-page PDF stitching.
- [ ] Task: Implement `DocumentStitcher` for handling large multi-page files.
- [ ] Task: Integrate OCR jobs with Upstash Redis queue for asynchronous processing.
- [ ] Task: Implement status tracking API endpoints for long-running OCR jobs.
- [ ] Task: Conductor - User Manual Verification 'Multi-page PDF & Async Orchestration' (Protocol in workflow.md)

## Phase 4: Cognitive Mapping & Cleanup
- [ ] Task: Write TDD tests for Gemini-driven cognitive cleanup (e.g., repairing blurred text).
- [ ] Task: Implement `CognitiveCleanup` logic mapping OCR output to "Foundation" brand hierarchy.
- [ ] Task: Implement "Messy Data" fallback logic for extreme low-quality inputs.
- [ ] Task: Conductor - User Manual Verification 'Cognitive Mapping & Cleanup' (Protocol in workflow.md)

## Phase 5: Legacy Replacement & Migration
- [ ] Task: Audit and remove legacy "brownfield" OCR code.
- [ ] Task: Redirect all existing backend OCR calls to the new SOTA Machine.
- [ ] Task: Perform final end-to-end integration test with real-world messy assets.
- [ ] Task: Conductor - User Manual Verification 'Legacy Replacement & Migration' (Protocol in workflow.md)
