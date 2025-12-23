# Implementation Plan: End-to-End Moves & Campaigns Frontend Hardening

## Phase 1: Environment & Config Hardening (Tasks 1-5)
- [x] 1. Task: Add `inference_simple` (Vertex API Key) to `.env.example` and local env [853b2ba]
- [x] 2. Task: Implement centralized `src/lib/inference-config.ts` for provider management [853b2ba]
- [x] 3. Task: Write failing tests for inference configuration loading and validation [853b2ba]
- [x] 4. Task: Implement config validation logic to ensure Vertex AI is the singular path [853b2ba]
- [ ] 5. Task: Conductor - User Manual Verification 'Environment & Config' (Protocol in workflow.md)

## Phase 2: Code Audit & Connectivity Fixes (Tasks 6-15) [checkpoint: 57f36ee]
- [x] 6. Task: Audit all files in `src/app/moves` and `src/app/campaigns` for broken links [9376403]
- [x] 7. Task: Audit shared UI components used by Moves/Campaigns [9376403]
- [x] 8. Task: Write failing tests for core API fetchers and Supabase hooks [9376403]
- [x] 9. Task: Fix broken imports and map frontend API calls to Backend Agentic nodes [9376403]
- [x] 10. Task: Standardize React state management for asynchronous agent responses [9376403]
- [x] 11. Task: Remove unused or redundant code in the Moves/Campaigns routes [9376403]
- [x] 12. Task: Implement error boundary components for graceful inference failures [9376403]
- [x] 13. Task: Refactor state synchronization to prevent UI flickering during updates [9376403]
- [x] 14. Task: Verify >80% unit test coverage for new/modified frontend logic [9376403]
- [x] 15. Task: Conductor - User Manual Verification 'Code Audit & Connectivity' (Protocol in workflow.md) [57f36ee]

## Phase 3: Campaign Module Production Integration (Tasks 16-25) [checkpoint: e22784a]
- [x] 16. Task: Connect UI triggers to the 90-day arc generation agent node [36c5a83]
- [x] 17. Task: Implement real-time status polling for campaign strategy generation [89fb8b5]
- [x] 18. Task: Write failing integration tests for the Campaign creation-to-persistence flow [89fb8b5]
- [x] 19. Task: Integrate "Campaign Auditor" feedback display into the UI [927ea80]
- [x] 20. Task: Implement the interactive Gantt chart update logic based on backend response [d9697cf]
- [x] 21. Task: Build the interactive "Strategic Pivot" cards in the Dashboard [6ef8318]
- [x] 22. Task: Connect Pivot Card actions to backend strategy update nodes [05970ae]
- [x] 23. Task: Implement optimistic UI updates for campaign state changes [61302f3]
- [x] 24. Task: Verify Campaign UI state matches Supabase record after inference [717019d]
- [x] 25. Task: Conductor - User Manual Verification 'Campaign Integration' (Protocol in workflow.md) [e22784a]


## Phase 4: Move Module Production Integration (Tasks 26-35)
- [x] 26. Task: Connect UI triggers to the weekly move generation agent node [dde2d0b]
- [x] 27. Task: Implement interactive decomposition of milestones into Move packets [80cdd80]
- [x] 28. Task: Write failing integration tests for Move generation and status tracking [f5bd0a1]
- [x] 29. Task: Integrate "Move Refiner" critique and adjustment UI [5ae053f]
- [x] 30. Task: Implement resource/tool verification feedback in the Moves view [de8d74e]
- [x] 31. Task: Connect move execution status (Pending -> Executed) to backend updates [4b89c66]
- [x] 32. Task: Implement progress bar synchronization between Moves and Campaigns [efdc454]
- [~] 33. Task: Build the detailed "Move Packet" view (Description, Owner, Tools)
- [ ] 34. Task: Verify Move UI state matches backend database exactly
- [ ] 35. Task: Conductor - User Manual Verification 'Move Integration' (Protocol in workflow.md)

## Phase 5: Final E2E Hardening & Verification (Tasks 36-40)
- [ ] 36. Task: Implement automated E2E smoke test (Playwright) for the full user journey
- [ ] 37. Task: Execute full system build and verify zero Next.js errors or warnings
- [ ] 38. Task: Perform manual side-by-side audit (UI vs DB vs Agent Logs)
- [ ] 39. Task: Conduct "Clean Console" audit during real-time inference execution
- [ ] 40. Task: Conductor - Final Track Completion Review & Checkpoint
