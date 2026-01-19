# Implementation Plan: UI/UX & Notification Polish (Track: UX_POLISH_20260119)

## Phase 1: Foundation & Notification Infrastructure [checkpoint: c20342c0]
This phase sets up the local state management for session-based notifications and the base components for feedback.

- [x] Task: Create `useNotificationStore` using Zustand or React Context for session-based alerts.
    - [x] Write tests to verify notification adding/removing logic.
    - [x] Implement the store.
- [x] Task: Standardize `Sonner` toast configurations in a central utility.
    - [x] Write tests to ensure consistent styling and duration.
    - [x] Implement utility functions (`notify.success`, `notify.error`).
- [x] Task: Create reusable Skeleton components for core modules.
    - [x] Write tests for rendering states.
    - [x] Implement skeleton loaders for Foundation and Moves dashboards.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Foundation & Notification Infrastructure' (Protocol in workflow.md)

## Phase 2: Navigation & Command Palette
Implementing the "ease of access" features including the Ctrl+K interface.

- [x] Task: Implement the Command Palette (Ctrl+K) using `cmdk` or Shadcn `Command`.
    - [x] Write tests for keyboard trigger and search filtering.
    - [x] Implement navigation logic to core modules.
- [x] Task: Enhance Breadcrumbs and Active Sidebar states.
    - [x] Write tests for path-matching logic.
    - [x] Update `Sidebar` and `Header` components with visual active states.
- [x] Task: Implement hover micro-interactions across primary action buttons.
    - [x] Use Framer Motion for subtle scale/fade transitions.
    - [x] Verify animations don't break functional tests.
- [~] Task: Conductor - User Manual Verification 'Phase 2: Navigation & Command Palette' (Protocol in workflow.md)

## Phase 3: Notification UI & Contextual Help
Building the visible notification center and in-app guidance.

- [ ] Task: Create the `NotificationBell` and `NotificationDropdown` components.
    - [ ] Write tests for "new" indicator logic and empty states.
    - [ ] Implement UI and connect to `useNotificationStore`.
- [ ] Task: Add "Info Bubbles" (Tooltips) for strategic terminology.
    - [ ] Create a glossary of terms (RICP, Soundbite Studio, etc.).
    - [ ] Implement Shadcn `Tooltip` components in the Foundation module.
- [ ] Task: Implement Module Empty States.
    - [ ] Design and implement guiding UI for modules with no data.
    - [ ] Verify "Call to Action" buttons lead to the correct flows.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Notification UI & Contextual Help' (Protocol in workflow.md)

## Phase 4: Mobile Audit & Final Polish
Ensuring the "MasterClass" feel extends to all devices.

- [ ] Task: Conduct a Mobile UI Audit and fix responsiveness issues.
    - [ ] Fix layout shifts on small screens.
    - [ ] Ensure all touch targets are at least 44x44px.
- [ ] Task: Final visual consistency check and performance verification.
    - [ ] Run Lighthouse or similar audit for performance impact.
    - [ ] Verify all Sonner toasts match the updated design.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Mobile Audit & Final Polish' (Protocol in workflow.md)
