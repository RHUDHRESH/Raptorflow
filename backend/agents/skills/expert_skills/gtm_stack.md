---
id: GTMStackSkill
expert: Jax (GTM Developer)
category: operations
level: master
tools:
  - api_connector
  - stack_auditor
  - security_compliance_scanner
complexity: high-density
logic_type: architectural_integration
---

# EXPERT SKILL: GTM STACK ARCHITECTURE & INTEGRATION

This is the technical blueprint for selecting, connecting, and optimizing the Marketing Technology (MarTech) stack. Designed for the GTM Developer (Jax) to ensure data sovereignty and technical execution speed.

## 1. ARCHITECTURAL INITIALIZATION
Before execution, Jax must define the `Stack_Topology` (Monolithic vs. Best-of-Breed).
- IF `Team_Size` < 10: Trigger `Lean_Integrated_Stack` sequence.
- IF `Team_Size` >= 10: Trigger `Modular_Decoupled_Stack` sequence.

## 2. PROCEDURAL EXECUTION (200-LINE DENSITY)

### PHASE 1: DATA SOVEREIGNTY AUDIT (Lines 1-50)
1. Map the `Single_Source_of_Truth` (SSOT).
   - Candidate A: CRM (Salesforce/HubSpot).
   - Candidate B: Data Warehouse (BigQuery/Snowflake).
   - Candidate C: Customer Data Platform (Segment/Rudderstack).
2. Execute `Data_Leakage_Scan`:
   - Identify tools that store customer data but don't sync back to the SSOT.
   - [Logic]: Mark all "Data Islands" for immediate API-wiring.
3. Establish `ID_Resolution_Protocol`:
   - How do we track a user from Anonymous (Browser Cookie) to Known (Email)?
   - Logic: Mandate `Deterministic_Matching` over `Probabilistic` for high-ticket B2B.
4. Set up `Privacy_by_Design`:
   - Verify GDPR/CCPA consent-propagation across all API endpoints.
   - IF `Consent_Token` is missing: Block outbound communication for that user ID.
5. Engineer the `Data_Mapping_Matrix`:
   - Field 1: User_ID (Internal).
   - Field 2: Lead_Score (Sera's Math).
   - Field 3: Persona_Archetype (Marcus's Strategy).
   - Field 4: Current_Stage (Lifecycle).

### PHASE 2: TOOL SELECTION & VETTING (Lines 51-100)
6. Run the `MarTech_Utility_Filter`:
   - For every tool in the stack, calculate `Cost_per_Used_Feature`.
   - IF `Utility_Ratio` < 0.2: Flag for removal or replacement.
7. Execute `API_Performance_Vetting`:
   - Measure average latency for tool-to-tool webhooks.
   - Target: < 1.5 seconds for "Real-time" events.
8. Define the `Core_Stack_Components`:
   - **Ingestion:** Typeform, Webflow, Custom Next.js.
   - **Intelligence:** Clearbit, Apollo, GPT-4 Service.
   - **Engagement:** Customer.io, Beehiiv, LinkedIn API.
   - **Analysis:** PostHog, The Matrix (Internal).
9. Map `Integration_Flows`:
   - Flow 1: Webhook -> Enrichment -> CRM.
   - Flow 2: CRM_Event -> Trigger_Sequence -> Slack_Alert.
   - Flow 3: Billing_Event -> Data_Warehouse -> LTV_Model.

### PHASE 3: CUSTOMER JOURNEY WIRING (Lines 101-150)
10. Engineer the `Lifecycle_State_Machine`:
    - Define 5 States: [Unaware, Aware, Intent, Active, Churned].
    - Logic: Use a `State_Controller` to prevent overlapping sequences.
    - (Example: Don't send a "Welcome" email if they just "Bought").
11. Build the `Attribute_Propagation_Engine`:
    - When Marcus defines a "Cohort," how does Jax tag them in the stack?
    - [Logic]: Automated "Segment" creation via API based on RICP demographics.
12. Execute `Trigger_Optimization_Protocol`:
    - Identify "High-Entropy" triggers (e.g., Abandoned Cart, Pricing View).
    - Logic: Increase retry-priority for these events.
13. Map `Omnichannel_Sync`:
    - Ensure that if a user unsubscribes on Email, they are also muted on SMS/LinkedIn.
    - Logic: Centralized `Unsubscribe_Master_DB`.

### PHASE 4: RESILIENCE & SCALING (Lines 151-200)
14. Audit `Stack_Security_Compliance`:
    - Check for `Hardcoded_API_Keys` in the code injection scripts.
    - Verify `OAuth_Scoping` (Principle of Least Privilege).
15. Setup `Monitoring_Alerts`:
    - IF `Lead_Flow` == 0 for 4 hours: Trigger `P0_Emergency_Alert`.
    - IF `API_Error_Rate` > 5%: Trigger `Auto_Failover` to local DB.
16. Execute `Load_Capacity_Simulation`:
    - What happens if 10,000 leads arrive in 1 minute?
    - [Logic]: Mandate `Asynchronous_Queueing` (Redis/RabbitMQ) for all ingestion.
17. Build the `Implementation_Roadmap_Gantt`:
    - Step 1: SSOT Setup (Week 1).
    - Step 2: Enrichment & Sync (Week 2).
    - Step 3: Lifecycle Automation (Week 3).
18. FINAL TECHNICAL SIGN-OFF:
    - Is the data flow documented?
    - Is the privacy layer secure?
    - IF NO: Re-architect the `Phase 1` SSOT.
    - IF YES: Sync with `Analyst` for data-tracking approval.

## 3. EDGE CASE LOGIC
- **Scenario: Changing CRM (The "HubSpot to Salesforce" Nightmare).**
  - [Logic]: Use an `Abstraction_Layer` (e.g., Segment) to minimize logic-rewriting.
- **Scenario: 3rd Party API Outage.**
  - [Logic]: Enable `Shadow_Logging` to re-play missed events once the API recovers.
- **Scenario: Duplicate Identity Collision.**
  - [Logic]: Resolve based on `Verification_Level` (Paid Account ID > Email > Cookie).

## 4. DEVELOPER'S NOTES (Line 200+)
The GTM Stack is the engine of the business. If the engine is messy, the driver (Founder) can't see the road. I build engines that are clean, fast, and surgical. I don't "link tools"; I architect data flows.
