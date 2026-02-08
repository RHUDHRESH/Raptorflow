# Implementation Plan: BCM Dynamic Evolution Engine (Everything Engine)

This plan implements a dynamic, event-sourced BCM system that records and evolves based on every user action and business move.

## Phase 1: Foundation & Event Ledger Schema
Establish the core data structures and database schema for the Event-Sourced BCM.

- [~] Task: Define the `bcm_events` table schema in Supabase
    - [ ] Create a table to store discrete JSON events (type, payload, metadata, timestamp, ucid)
    - [ ] Set up RLS policies for workspace isolation
- [ ] Task: Create the "Everything" BCM JSON Schema
    - [ ] Define the base structure for Brand, Positioning, History, and Interaction logs
    - [ ] Implement a validation layer for incoming event payloads
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation' (Protocol in workflow.md)

## Phase 2: Event Ingestion & State Projection
Implement the logic to record events and project them into a current "Live State."

- [ ] Task: Implement the Event Recorder Service
    - [ ] Write tests for recording events to the ledger
    - [ ] Implement the `recordEvent` function in the Backend Domain
- [ ] Task: Implement the State Projection Engine
    - [ ] Write tests for reconstructing BCM state from a list of events
    - [ ] Implement a `getLatestBCM` function that aggregates the event history into a single JSON object
- [ ] Task: Integrate with Universal Agent State Sync
    - [ ] Ensure the Universal Agent can read from the projected BCM state
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Ingestion & Projection' (Protocol in workflow.md)

## Phase 3: Total Integration (The "Everything" Loop)
Connect every part of the system (Moves, History, Search) to the BCM ledger.

- [ ] Task: Hook "Moves" into the Ledger
    - [ ] Write tests: Completing a move should trigger a `MOVE_COMPLETED` event
    - [ ] Update the Moves service to record events upon status changes
- [ ] Task: Hook "History & Telemetry" into the Ledger
    - [ ] Implement recording of `USER_INTERACTION` and `AI_PROMPT` events
- [ ] Task: Implement Evolutionary AI Logic
    - [ ] Create a skill for the Universal Agent to "Refine Context" based on the last 50 events
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Total Integration' (Protocol in workflow.md)

## Phase 4: Optimization & Final Polish
Ensure the "Everything" engine is economical and performant.

- [ ] Task: Implement Semantic Compression (The "Sweeper")
    - [ ] Write tests for synthesizing multiple events into a single "Checkpoint" event
    - [ ] Implement the background job to compress old event logs into strategic summaries
- [ ] Task: Final End-to-End Verification
    - [ ] Run full system tests to ensure "Everything" is tracked and the BCM evolves correctly
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Optimization' (Protocol in workflow.md)
