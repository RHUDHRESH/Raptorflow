# Implementation Plan: Auth and Onboarding Overhaul

## Phase 1: Authentication & Social Login (TDD)
- [x] Task: Set up test suite for authentication flows 356ad96
- [ ] Task: Implement social login (Google, GitHub) support
    - [ ] Write failing tests for social login redirection and callback
    - [ ] Implement Google login integration
    - [ ] Implement GitHub login integration
    - [ ] Verify social login tests pass
- [ ] Task: Enhance user session and profile creation logic
    - [ ] Write failing tests for user profile persistence upon social sign-up
    - [ ] Implement profile creation with social data (Name, Email)
    - [ ] Verify profile persistence tests pass
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Authentication & Social Login' (Protocol in workflow.md)

## Phase 2: New User Onboarding & Profile Setup (TDD)
- [ ] Task: Implement Profile Setup flow
    - [ ] Write failing tests for profile information collection (Role, Company)
    - [ ] Create UI components for profile setup using illustrative style
    - [ ] Implement backend logic to save role and company data
    - [ ] Verify profile setup tests pass
- [ ] Task: Implement Integrated Tier Selection
    - [ ] Write failing tests for tier selection during onboarding
    - [ ] Create UI for tier selection with illustrative plan benefits
    - [ ] Implement backend logic to link user to selected tier
    - [ ] Verify tier selection tests pass
- [ ] Task: Implement Product Walkthrough ("Quick Start")
    - [ ] Write failing tests for first-login walkthrough trigger
    - [ ] Create illustrative tutorial components/overlays
    - [ ] Implement frontend logic to manage walkthrough state
    - [ ] Verify walkthrough tests pass
- [ ] Task: Conductor - User Manual Verification 'Phase 2: New User Onboarding & Profile Setup' (Protocol in workflow.md)

## Phase 3: Recurring User Experience & Dashboard (TDD)
- [ ] Task: Implement "Welcome Back" Dashboard
    - [ ] Write failing tests for fetching recent activity
    - [ ] Create UI for recent activity feed and "resume" links
    - [ ] Implement backend service for activity tracking and retrieval
    - [ ] Verify dashboard tests pass
- [ ] Task: Implement Notification Center
    - [ ] Write failing tests for fetching and marking notifications as read
    - [ ] Create UI for notification dropdown/center
    - [ ] Implement backend logic for system notifications
    - [ ] Verify notification tests pass
- [ ] Task: Implement Subscription Management in Dashboard
    - [ ] Write failing tests for plan upgrade/downgrade from dashboard
    - [ ] Create UI for managing subscriptions
    - [ ] Implement logic to process plan changes
    - [ ] Verify subscription management tests pass
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Recurring User Experience & Dashboard' (Protocol in workflow.md)

## Phase 4: Final Payment Page Redesign & Polish
- [ ] Task: Visual Redesign of Payment Pages
    - [ ] Implement full-page redesign using illustrative graphics and icons
    - [ ] Ensure all tier benefits are clearly communicated per spec
    - [ ] Perform cross-browser and mobile responsive testing
- [ ] Task: Final System Integration and End-to-End Testing
    - [ ] Run full test suite and verify >80% coverage
    - [ ] Perform final audit against project guidelines
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Payment Page Redesign & Polish' (Protocol in workflow.md)
