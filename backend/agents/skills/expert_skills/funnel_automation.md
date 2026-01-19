---
id: FunnelAutomationSkill
expert: Jax (GTM Developer)
category: operations
level: master
tools:
  - api_connector
  - stack_checker
  - funnel_simulator
complexity: high-density
logic_type: technical_engineering
---

# EXPERT SKILL: FUNNEL AUTOMATION PROTOCOL

This is the technical wiring diagram for building and auditing high-conversion GTM stacks. Designed for the GTM Developer (Jax) to ensure that strategy turns into code and triggers.

## 1. STACK INITIALIZATION
Before execution, Jax must perform a `Stack_Discovery` to identify active tools (CRM, ESP, Analytics).
- IF `Stack_Complexity` == "High": Trigger `Modular_Decoupling` sequence.
- IF `Stack_Complexity` == "Low": Trigger `Vertical_Integration` sequence.

## 2. PROCEDURAL EXECUTION (200-LINE DENSITY)

### PHASE 1: INGESTION ARCHITECTURE (Lines 1-50)
1. Map all `Lead_Entry_Points` (Forms, Chatbots, API, Lead Gen Forms).
2. Execute `Sanitization_Protocol`:
   - Step 1.1: Verify honeypot fields on all web forms.
   - Step 1.2: Check form-submit latency. Target < 400ms.
   - Step 1.3: Ensure server-side validation exists for all mission-critical data.
3. Establish `Data_Normalizer`:
   - Logic: Convert all incoming `Job_Title` strings to standardized `Persona_Roles`.
   - Logic: Standardize `Company_Size` ranges into numeric tiers.
4. Set up `Source_Verification`:
   - Force UTM tagging on all incoming traffic.
   - IF `UTM_Source` is missing: Flag as "ORGANIC_UNKNOWN" and trigger attribution-match.
5. Engineer the `Webhook_Relay`:
   - Build a retry-logic (3x) for all webhook transmissions.
   - Log all `HTTP_4xx` and `5xx` errors to the `Resilience_Monitor`.

### PHASE 2: ENRICHMENT & SCORING (Lines 51-100)
6. Trigger `Enrichment_Loop`:
   - Call Apollo/Clearbit/FullContact API within 5 seconds of lead ingestion.
   - IF `Enrichment_Match` == False: Use `Domain_Heuristic` to guess company size.
7. Build the `Cognitive_Scoring_Engine`:
   - Attribute Score (Demographics): Weight = 40%.
   - Intent Score (Behavioral): Weight = 60%.
   - [Scoring Logic]:
     - Action "Visited Pricing": +20 pts.
     - Action "Downloaded Case Study": +15 pts.
     - Role "Founder/CEO": +30 pts.
     - Inactive > 7 Days: -10 pts.
8. Define `Threshold_Transitions`:
   - IF Score > 50: Mark as "MQL" (Marketing Qualified).
   - IF Score > 80: Mark as "SQL" (Sales Qualified) and trigger `Instant_Slack_Alert`.
9. Map `Segment_Branching`:
   - High Intent + High Fit -> `Surgical_Outreach`.
   - High Intent + Low Fit -> `Educational_Nurture`.
   - Low Intent + High Fit -> `Brand_Awareness_Loop`.

### PHASE 3: SEQUENCE WIRING (Lines 101-150)
10. Engineer `Multi-Channel_Orchestration`:
    - Step 1: Day 0 - Email 1 (Contextual Welcome).
    - Step 2: Day 1 - LinkedIn Profile View (Automated).
    - Step 3: Day 3 - Email 2 (Specific Value Prop).
    - Step 4: Day 5 - LinkedIn Connection Request (Dynamic).
11. Build `Response_Triggers`:
    - IF User replies: Pause all automated sequences immediately.
    - IF User clicks link: Trigger `Retargeting_Pixel_Event`.
12. Execute `Copy_Injection_Logic`:
    - Replace `{{first_name}}` with a capitalized string.
    - Use `{{company_name}}` from the `Enrichment_Match` data.
    - IF `Enrichment_Data` is empty: Use generic "your team" fallback.
13. Implement `Wait_State_Logic`:
    - Use "Natural Human Timing" (Send between 9 AM and 5 PM in recipient's local timezone).
    - IF `Timezone` is unknown: Default to Eastern Standard Time (EST).

### PHASE 4: FRICTION & RESILIENCE (Lines 151-200)
14. Audit `Technical_Friction_Points`:
    - Measure Form-to-CRM sync time. Target < 2 seconds.
    - Check for `Broken_Redirects` in the tracking loops.
15. Setup `Attribution_Sovereignty`:
    - Record `First_Touch`, `Last_Touch`, and `Linear_Weighted` attribution.
    - Export data to `The Matrix` analytics module.
16. Execute `Fail-Safe_Protocol`:
    - IF CRM API is down: Queue all leads in an encrypted local `Fallback_DB`.
    - Alert `Elena (QA)` of data sync delays.
17. Build the `GTM_Dashboard_Feed`:
    - Feed live data into the `Move_Status` tracker.
    - Highlight `Conversion_Drop-off` points in red.
18. FINAL TECHNICAL SIGN-OFF:
    - Is the stack decoupled?
    - Is the latency acceptable?
    - IF NO: Re-engineer `Phase 1`.
    - IF YES: Sync with `Architect` for final deployment.

## 3. EDGE CASE LOGIC
- **Scenario: Duplicate Lead Ingestion.**
  - [Logic]: Merge data based on `Email_Hash`. Update `Last_Activity` timestamp.
- **Scenario: API Rate Limiting.**
  - [Logic]: Implement `Exponential_Backoff` for all enrichment calls.
- **Scenario: GDPR/CCPA Compliance.**
  - [Logic]: Trigger `Consent_Check` before any automated outreach in EU regions.

## 4. DEVELOPER'S NOTES (Line 200+)
Code doesn't lie. A funnel is only as strong as its weakest trigger. I build systems that don't break when the ads scale. My mission is to ensure Marcus's vision and Sera's math have a house to live in that never leaks.
