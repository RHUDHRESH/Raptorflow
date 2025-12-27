# Implementation Plan: The RaptorFlow "Master Council" Agentic OS

This plan details the 100-task roadmap to build a world-class, autonomous marketing department integrated into the RaptorFlow codebase.

## Phase 1: Individual Agent Codification (DNA & Tools)
Each agent is built as a specialized class with unique tools, system prompts, and "Past Exploit" RAG context.

### 1. The Direct Response Architect (ROI/Conversion)
- [x] **Task 1: Implement `DirectResponseAgent` class with `conversion_optimization` tool.** (66d61d5)
- [x] **Task 2: Equip with "Scientific Advertising" heuristic (Claude Hopkins ruleset).** (69452d2)
- [x] **Task 3: Grant access to `Blackbox_ROI_History` to identify high-converting patterns.** (2599351)

### 2. The Viral Alchemist (Hooks/Social)
- [x] **Task 4: Implement `ViralAlchemistAgent` with `radar_trend_analyzer` tool.** (67ef30b)
- [x] **Task 5: Equip with "Hook Matrix" (100+ proven social hook templates).** (cefcfbb)
- [x] **Task 6: Grant access to `Radar_Search` to find trending memes/topics in the user's niche.** (cb9f478)

### 3. The Brand Philosopher (Positioning/Aesthetic)
- [x] **Task 7: Implement `BrandPhilosopherAgent` with `style_guide_enforcer` tool.** (709bcae)
- [x] **Task 8: Equip with "Precision Soundbite Framework 3.0" logic.** (b394596)
- [x] **Task 9: Grant access to `Foundation_BrandKit` to ensure 100% narrative alignment.** (1c831fe)

### 4. The Data Quant (Analytics/Pattern Recognition)
- [x] **Task 10: Implement `DataQuantAgent` with `bigquery_query_engine` tool.** (c81ea83)
- [x] **Task 11: Equip with "Bayesian Confidence Scorer" for experiment outcomes.** (c81ea83)
- [x] **Task 12: Grant access to `Matrix_KPI_Stream` for real-time performance monitoring.** (747f467)

### 5. The Community Catalyst (Dark Social/Retention)
- [x] **Task 13: Implement `CommunityCatalystAgent` with `sentiment_analysis` tool.** (81369dd)
- [x] **Task 14: Equip with "Network Effect" growth heuristics.** (81369dd)
- [x] **Task 15: Grant access to `Supabase_User_Logs` to identify power-user segments.** (1488abc)

### 6. The Media Buyer Strategist (Paid Scaling)
- [x] **Task 16: Implement `MediaBuyerAgent` with `budget_pacing_simulator` tool.** (d159995)
- [x] **Task 17: Equip with "Unit Economics" (CAC/LTV) calculator.** (d159995)
- [x] **Task 18: Grant access to `Ad_Platform_Mocks` (for simulating ad-spend efficiency).** (367e5da)

### 7. The SEO/Content Moat Builder (Authority)
- [x] **Task 19: Implement `SEOMoatAgent` with `semantic_cluster_generator` tool.** (b7ba515)
- [x] **Task 20: Equip with "Topical Authority" mapping logic.** (b7ba515)
- [x] **Task 21: Grant access to `Radar_Keywords` to find low-competition, high-intent gaps.** (466408c)

### 8. The PR & Media Specialist (Outreach)
- [x] **Task 22: Implement `PRSpecialistAgent` with `journalist_pitch_architect` tool.** (8f08f3a)
- [x] **Task 23: Equip with "Narrative Hook" outreach frameworks.** (9d40b1f)
- [x] **Task 24: Grant access to `Radar_Events` to find relevant podcasts/conferences.** (a6f7eb7)

### 9. The Behavioral Psychologist (Consumer Triggers)
- [x] **Task 25: Implement `PsychologistAgent` with `jtbd_framework_analyzer` tool.** (4291f4b)
- [x] **Task 26: Equip with "Cialdini's 6 Principles" of influence.** (d45acd9)
- [x] **Task 27: Grant access to `Cohorts_Intelligence` to map triggers to specific ICPs.** (2a5d648)

### 10. The Product Marketing Lead (GTM/Value)
- [x] **Task 28: Implement `ProductLeadAgent` with `benefit_to_feature_mapper` tool.** (ffcd5f0)
- [x] **Task 29: Equip with "Positioning Canvas" logic.** (de90875)
- [x] **Task 30: Grant access to Muse_Asset_Archive to repurpose product demos.** (05c1d23)

### 11. The Partnership/Affiliate Hunter (Leverage)
- [x] **Task 31: Implement `PartnershipAgent` with `audience_overlap_detector` tool.** (f5e2a8c)
- [x] **Task 32: Equip with "Win-Win" incentive modeling.** (56b7b90)
- [x] **Task 33: Grant access to `Radar_Competitors` to find potential "Enemy of my Enemy" partners.** (38f0b72)

### 12. The Retention & LTV Specialist (Lifecycle)
- [x] **Task 34: Implement `RetentionAgent` with `churn_prediction_heuristics` tool.** (84dce40)
- [x] **Task 35: Equip with "Milestone-Based" messaging rules.** (58df533)
- [ ] **Task 36: Grant access to `Blackbox_Longitudinal_Data` to analyze customer decay.**

- [ ] **Task 36.1: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)**

---

## Phase 2: Agent-to-Agent (A2A) Decision Architecture
Optimizing how they talk to each other to create "Calculated Genius" moves.

- [ ] **Task 37: Implement the `Blackboard_State` in LangGraph for shared Agent memory.**
- [ ] **Task 38: Build the `Council_Debate` node: parallel "Thought" generation.**
- [ ] **Task 39: Implement `Cross_Critique` logic: Agents must critique at least 2 other proposals.**
- [ ] **Task 40: Build the `Consensus_Scorer`: Weighted voting based on the current Goal.**
- [ ] **Task 41: Implement `Synthesis_Node`: A Moderator agent writes the final "Strategic Decree.".**
- [ ] **Task 42: Create `Reasoning_Chain` metadata: Save the full debate log to Supabase.**
- [ ] **Task 43: Build the `Rejection_Logger`: Record why certain paths were discarded.**

- [ ] **Task 43.1: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)**

---

## Phase 3: Proactive Intelligence (Radar & Events)
The agents "watch" the world and tell the user what to do.

- [ ] **Task 44: Implement `Radar_Continuous_Scan`: Auto-search for niche events (e.g., "SaaS Meetup in SF").**
- [ ] **Task 45: Build `Event_Opportunity_Evaluator`: Agents score events vs. Brand Goals.**
- [ ] **Task 46: Implement `Proactive_Task_Generator`: Create a "Go to this event" task in Moves.**
- [ ] **Task 47: Create `Brief_Builder`: If the user accepts an event task, agents generate a "Cheat Sheet" for that event.**
- [ ] **Task 48: Build `Competitor_Radar_Watcher`: Agents alert the user when a competitor changes positioning.**

- [ ] **Task 48.1: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)**

---

## Phase 4: Propagative Execution (Campaign -> Move -> Muse)
The Council's decisions automatically flow into the rest of the app.

- [ ] **Task 49: Implement `Campaign_Arc_Generator`: 90-day plan based on Council Consensus.**
- [ ] **Task 50: Build `Move_Decomposition_Engine`: Breaking Campaigns into weekly Moves.**
- [ ] **Task 51: Propagative Move Creation: Auto-inserting Move records into Supabase.**
- [ ] **Task 52: Muse Asset Pre-Generation Trigger: Moves automatically send `Asset_Briefs` to Muse.**
- [ ] **Task 53: Implement `Muse_Worker_Queue`: Asynchronous asset generation (Images/Copy) for pending Moves.**
- [ ] **Task 54: Create `Asset_Linkage_Metadata`: Connect Move ID to Muse Artifact ID.**
- [ ] **Task 55: Build `User_Approval_Workflow`: User clicks "Approve" on a Move -> Muse assets are finalized.**

- [ ] **Task 55.1: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)**

---

## Phase 5: "Calculated Genius" Reasoning UI
Showing the depth of thought in the "Operator's View."

- [ ] **Task 56: Design the `Council_Chamber` UI: 12-avatar grid with real-time "Thought" pulses.**
- [ ] **Task 57: Build the `Rationale_Drawer` component in the Moves module.**
- [ ] **Task 58: Implement `Pedigree_Visualizer`: A tree view showing which Agent proposed what.**
- [ ] **Task 59: Build `Confidence_Heatmap`: Shows Agent alignment on a Move.**
- [ ] **Task 60: Implement `Historical_Parallel_UI`: "This move is like the 1994 Nike [Exploit]...".**

- [ ] **Task 60.1: Conductor - User Manual Verification 'Phase 5' (Protocol in workflow.md)**

---

## Phase 6: Skill Studio & User Coaching
Enabling the user to train their 12 experts.

- [ ] **Task 61: Build `Skill_Upload_Zone`: Drag-and-drop for PDFs/Docs.**
- [ ] **Task 62: Implement `Librarian_Agent_Processor`: Extracts heuristics from uploads.**
- [ ] **Task 63: Build `Agent_Training_Dashboard`: View and edit each agent's "Learned Skills.".**
- [ ] **Task 64: Implement `Heuristic_Editor`: Direct text editing of an agent's "Never/Always" rules.**
- [ ] **Task 65: Create `Skill_Propagation_Test`: Run a mock prompt to verify a new skill is "active.".**

- [ ] **Task 65.1: Conductor - User Manual Verification 'Phase 6' (Protocol in workflow.md)**

---

## Phase 7: Blackbox Integration & Reflection (The Learning Loop)
Agents get smarter based on what actually happened.

- [ ] **Task 66: Implement `Post_Mortem_Trigger`: Run after a Move is "Executed" in Blackbox.**
- [ ] **Task 67: Build `Reflection_Node`: Agents analyze delta between `Predicted ROI` vs. `Actual`.**
- [ ] **Task 68: Implement `Auto_Correction_Heuristic`: Agents rewrite their own prompts based on failure.**
- [ ] **Task 69: Build `Success_Reinforcement`: Agents prioritize "Winning" exploits in the next debate.**
- [ ] **Task 70: Create `Influence_Weight_Update`: ROI-based voting weight adjustment.**

- [ ] **Task 70.1: Conductor - User Manual Verification 'Phase 7' (Protocol in workflow.md)**

---

## Phase 8: Advanced Toolbelt (The "World-Class" Capabilities)
Giving agents the power to actually execute marketing.

- [ ] **Task 71: Implement `Search_Native_V2`: Support for LinkedIn/X/Reddit scraping (via Brave/DDG).**
- [ ] **Task 72: Build `Ad_Copy_Validator`: Checks copy vs. Facebook/Google ad policies.**
- [ ] **Task 73: Implement `Image_Gen_Director`: Agents write high-fidelity prompts for Muse/DALL-E/Midjourney.**
- [ ] **Task 74: Build `Code_Snippet_Generator`: Data Quant writes SQL for Matrix custom reports.**
- [ ] **Task 75: Create `Email_Sequence_Architect`: Multi-step drip logic generation.**

- [ ] **Task 75.1: Conductor - User Manual Verification 'Phase 8' (Protocol in workflow.md)**

---

## Phase 9: System Reliability & Performance
Ensuring the "Agentic OS" doesn't crash or cost a fortune.

- [ ] **Task 76: Implement `Token_Budget_Manager`: Prevents agents from over-thinking and burning budget.**
- [ ] **Task 77: Build `Parallel_Inference_Optimizer`: Run 12 agent calls in parallel.**
- [ ] **Task 78: Implement `Response_Caching`: Cache agent "Thoughts" for common scenarios.**
- [ ] **Task 79: Build `Agent_Health_Monitor`: Detects if an agent is hallucinating or "Stuck.".**
- [ ] **Task 80: Create `Dry_Run_Simulator`: Test the whole Council without hitting live APIs.**

- [ ] **Task 80.1: Conductor - User Manual Verification 'Phase 9' (Protocol in workflow.md)**

---

## Phase 10: Final Polish & "Quiet Luxury" Delivery
Making it feel like a surgical instrument.

- [ ] **Task 81: Implement `Framer_Motion` layout transitions for the Council Chamber.**
- [ ] **Task 82: Build `JetBrains_Mono` typography integration for reasoning logs.**
- [ ] **Task 83: Create `Sound_Design`: Subtle "click" and "hum" feedback for Agent activity.**
- [ ] **Task 84: Implement `Progressive_Disclosure`: Hide the "Debate" unless the user clicks "Show Reasoning.".**
- [ ] **Task 85: Build `Daily_Briefing_Email`: A "Letter from the Council" summarizing today's moves.**
- [ ] **Task 86: Final Code Review: Ensure 100% compliance with `UI.md` and `BrandKit.md`.**
- [ ] **Task 87: Deployment to Production.**

- [ ] **Task 87.1: Conductor - User Manual Verification 'Phase 10' (Protocol in workflow.md)**
