# Council Campaign AI Report

**Branch:** `fix/council-streaming-and-campaign-ai`  
**Base:** `fix/next-rust-migration`

## Baseline State (Pre-Patch)

| Check                     | Result                               |
| ------------------------- | ------------------------------------ |
| `pnpm structural:check`   | PASS (0 violations, 34 gap warnings) |
| `pnpm typecheck`          | PASS                                 |
| `cargo check --workspace` | PASS                                 |

## Current Map

### Existing Council Routes

- `POST /api/v1/council` - start_session (creates session, no AI)
- `GET /api/v1/council` - list_sessions
- `GET /api/v1/council/{session_id}` - get_session
- `GET /api/v1/council/{session_id}/messages` - get_session_messages

### Missing Council Routes (Gaps)

- `POST /api/v1/council/{session_id}/start` - Generate positions with AI
- `GET /api/v1/council/{session_id}/stream` - SSE progress stream
- `POST /api/v1/council/{session_id}/synthesize` - Synthesize positions with AI

### Existing Campaign Routes

- CRUD for campaigns, moves, tasks, briefs

### Missing Campaign Routes (Gaps)

- `POST /api/v1/campaigns/{id}/evaluate` - AI evaluation
- `POST /api/v1/campaigns/{id}/moves/generate` - AI move generation

### DB Helpers Available

- `create_agent_position(pool, position_id, org_id, session_id, avatar_key, round_number, content, extracted_ripple_data)`
- `update_council_session_status(pool, session_id, org_id, status)`
- `create_campaign_move`, `create_campaign_task`
- `create_generated_content` - for storing evaluations and synthesis

### Bedrock Available

- `converse_large(prompt, max_tokens)` - for heavy AI tasks
- `converse_fast(prompt, max_tokens)` - for lighter tasks
- `converse_json(model_id, prompt, max_tokens)` - parses JSON response

## Implementation Tasks

- [ ] Add routes to router.rs
- [ ] Implement council start handler
- [ ] Implement council stream handler (SSE)
- [ ] Implement council synthesize handler
- [ ] Implement campaign evaluate handler
- [ ] Implement campaign generate moves handler
- [ ] Add AI helper utilities
- [ ] Update frontend API client
- [ ] Tombstone gap routes
- [ ] Update gap ledger
- [ ] Run tests

## Red Team Results

(to be filled after execution)
