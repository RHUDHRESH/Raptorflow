# Implementation Plan: The RaptorFlow "Master Council" Agentic OS

This plan details the 100-task roadmap to build a world-class, autonomous marketing department integrated into the RaptorFlow codebase.

## Phase 1: Individual Agent Codification (DNA & Tools) [checkpoint: 130ec75]
Each agent is built as a specialized class with unique tools, system prompts, and "Past Exploit" RAG context.
...
- [x] **Task 36: Grant access to `Blackbox_Longitudinal_Data` to analyze customer decay.** (993e20b)

- [x] **Task 36.1: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)** (130ec75)


---

## Phase 2: Agent-to-Agent (A2A) Decision Architecture [checkpoint: 4e33c94]
Optimizing how they talk to each other to create "Calculated Genius" moves.

- [x] **Task 37: Implement the `Blackboard_State` in LangGraph for shared Agent memory.** (55d25bd)
- [x] **Task 38: Build the `Council_Debate` node: parallel "Thought" generation.** (e253de1)
- [x] **Task 39: Implement `Cross_Critique` logic: Agents must critique at least 2 other proposals.** (da12ac6)
- [x] **Task 40: Build the `Consensus_Scorer`: Weighted voting based on the current Goal.** (848a519)
- [x] **Task 41: Implement `Synthesis_Node`: A Moderator agent writes the final "Strategic Decree.".** (2309faa)
- [x] **Task 42: Create `Reasoning_Chain` metadata: Save the full debate log to Supabase.** (84ea150)
- [x] **Task 43: Build the `Rejection_Logger`: Record why certain paths were discarded.** (2936678)

- [~] **Task 43.1: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)**

---

## Phase 3: Proactive Intelligence (Radar & Events) [checkpoint: dc96c22]
The agents "watch" the world and tell the user what to do.

- [x] **Task 44: Implement `Radar_Continuous_Scan`: Auto-search for niche events (e.g., "SaaS Meetup in SF").** (0e19289)
- [x] **Task 45: Build `Event_Opportunity_Evaluator`: Agents score events vs. Brand Goals.** (d4446ef)
- [x] **Task 46: Implement `Proactive_Task_Generator`: Create a "Go to this event" task in Moves.** (91bc6a3)
- [x] **Task 47: Create `Brief_Builder`: If the user accepts an event task, agents generate a "Cheat Sheet" for that event.** (a092c06)
- [x] **Task 48: Build `Competitor_Radar_Watcher`: Agents alert the user when a competitor changes positioning.** (aee006e)

- [~] **Task 48.1: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)**

---

## Phase 4: Propagative Execution (Campaign -> Move -> Muse) [checkpoint: 42ae926]
Consensus triggers action.

- [x] **Task 49: Implement `Campaign_Arc_Generator`: 90-day plan based on Council Consensus.** (d9ed706)
- [x] **Task 50: Build `Move_Decomposition_Engine`: Breaking Campaigns into weekly Moves.** (df2aa51)
- [x] **Task 51: Implement `Move_Refiner`: Tool selection and prompt engineering for each Move.** (42aafb7)
- [x] **Task 52: Build `Propagative_Executor`: Saving refined Moves to the `moves` table.** (4c7c13a)
- [~] **Task 53: Conductor - User Manual Verification 'Phase 4'.**
- [x] **Task 54: Implement `Success_Predictor`: Confidence scoring for Moves.** (4068ad0)
- [x] **Task 55: Build `Kill_Switch_Monitor`: Discarding moves with < 40% confidence.** (5c4c3ba)
- [~] **Task 56: Implement `Strategy_Recalibrator`: Looping back to Debate if all Moves fail.**

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
