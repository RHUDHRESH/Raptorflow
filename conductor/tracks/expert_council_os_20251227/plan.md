# Implementation Plan: The RaptorFlow "Master Council" Agentic OS

This plan details the 100-task roadmap to build a world-class, autonomous marketing department integrated into the RaptorFlow codebase.

## Phase 1: Individual Agent Codification (DNA & Tools) [checkpoint: 130ec75]
Each agent is built as a specialized class with unique tools, system prompts, and "Past Exploit" RAG context.

- [x] **Task 1: Codify `Direct_Response_Agent`: DNA focused on conversion and hooks.** (993e20b)
- [x] **Task 2: Codify `Viral_Alchemist`: DNA focused on social loops and hooks.** (993e20b)
- [x] **Task 3: Codify `Brand_Philosopher`: DNA focused on positioning and tone.** (993e20b)
- [x] **Task 4: Codify `Data_Quant`: DNA focused on competitive gaps.** (993e20b)
- [x] **Task 5: Codify `Community_Catalyst`: DNA focused on owned audience.** (993e20b)
- [x] **Task 6: Codify `Media_Buyer`: DNA focused on paid arbitrage.** (993e20b)
- [x] **Task 7: Codify `SEO_Moat`: DNA focused on search intent.** (993e20b)
- [x] **Task 8: Codify `PR_Specialist`: DNA focused on earned media.** (993e20b)
- [x] **Task 9: Codify `Psychologist`: DNA focused on cognitive biases.** (993e20b)
- [x] **Task 10: Codify `Product_Lead`: DNA focused on PMF and features.** (993e20b)
- [x] **Task 11: Codify `Partnership_Lead`: DNA focused on ecosystem leverage.** (993e20b)
- [x] **Task 12: Codify `Retention_Lead`: DNA focused on LTV and churn.** (993e20b)

- [x] **Task 13: Build `Exploit_RAG_Service`: Vector store for "Historical Marketing Wins."** (993e20b)
- [x] **Task 14: Implement `DNA_Injector`: Middleware to inject agent-specific constraints into every prompt.** (993e20b)
- [x] **Task 15: Create `Toolbelt_Registry`: Unified interface for all 12 agents to access shared tools.** (993e20b)

- [x] **Task 16: Integrate `Brave_Search` for real-time market data.** (993e20b)
- [x] **Task 17: Build `Competitor_Price_Monitor`: Scrapes and compares competitor pricing.** (993e20b)
- [x] **Task 18: Implement `Social_Sentiment_Analyzer`: Gauges brand perception on X/Reddit.** (993e20b)
- [x] **Task 19: Create `Ads_Library_Crawler`: Analyzes active competitor ads.** (993e20b)
- [x] **Task 20: Build `Content_Audit_Tool`: Analyzes current brand assets for gaps.** (993e20b)
- [x] **Task 21: Implement `Keyword_Difficulty_Scorer` for SEO moat building.** (993e20b)
- [x] **Task 22: Create `Viral_Loop_Simulator`: Predicts social shares based on hook quality.** (993e20b)
- [x] **Task 23: Build `Psychology_Red_Teamer`: Checks copy for "Too salesy" vs "Scientific" balance.** (993e20b)
- [x] **Task 24: Implement `Partner_Network_Mapper`: Identifies complementary SaaS tools.** (993e20b)
- [x] **Task 25: Create `LTV_Projection_Tool` for retention modeling.** (993e20b)
- [x] **Task 26: Build `Media_Mix_Optimizer`: Suggests budget allocation across channels.** (993e20b)
- [x] **Task 27: Implement `PR_Journalist_Pitch_Tool`: Finds relevant tech journalists.** (993e20b)
- [x] **Task 28: Add `Conversion_Rate_Predictor` based on direct response best practices.** (993e20b)
- [x] **Task 29: Build `Customer_Journey_Mapper` for Product Lead insights.** (993e20b)
- [x] **Task 30: Integrate `BigQuery_Analytics` for Data Quant depth.** (993e20b)
- [x] **Task 31: Create `Retention_Churn_Monitor` for early warning signals.** (993e20b)
- [x] **Task 32: Build `Community_Engagement_Scorer` for Discord/Slack communities.** (993e20b)
- [x] **Task 33: Implement `Paid_Search_Arbitrage_Finder` for Media Buyer.** (993e20b)
- [x] **Task 34: Create `Backlink_Opportunity_Finder` for SEO Moat.** (993e20b)
- [x] **Task 35: Build `Cognitive_Load_Auditor` for landing page copy.** (993e20b)
- [x] **Task 36: Grant access to `Blackbox_Longitudinal_Data` to analyze customer decay.** (993e20b)

- [x] **Task 36.1: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)** (130ec75)


---

## Phase 2: Agent-to-Agent (A2A) Decision Architecture [checkpoint: ec23d0c]
Optimizing how they talk to each other to create "Calculated Genius" moves.

- [x] **Task 37: Implement the `Blackboard_State` in LangGraph for shared Agent memory.** (55d25bd)
- [x] **Task 38: Build the `Council_Debate` node: parallel "Thought" generation.** (e253de1)
- [x] **Task 39: Implement `Cross_Critique` logic: Agents must critique at least 2 other proposals.** (da12ac6)
- [x] **Task 40: Build the `Consensus_Scorer`: Weighted voting based on the current Goal.** (848a519)
- [x] **Task 41: Implement `Synthesis_Node`: A Moderator agent writes the final "Strategic Decree.".** (2309faa)
- [x] **Task 42: Create `Reasoning_Chain` metadata: Save the full debate log to Supabase.** (84ea150)
- [x] **Task 43: Build the `Rejection_Logger`: Record why certain paths were discarded.** (2936678)

- [x] **Task 43.1: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)** (ec23d0c)

---

## Phase 3: Proactive Intelligence (Radar & Events) [checkpoint: ec23d0c]
The agents "watch" the world and tell the user what to do.

- [x] **Task 44: Implement `Radar_Continuous_Scan`: Auto-search for niche events (e.g., "SaaS Meetup in SF").** (0e19289)
- [x] **Task 45: Build `Event_Opportunity_Evaluator`: Agents score events vs. Brand Goals.** (d4446ef)
- [x] **Task 46: Implement `Proactive_Task_Generator`: Create a "Go to this event" task in Moves.** (91bc6a3)
- [x] **Task 47: Create `Brief_Builder`: If the user accepts an event task, agents generate a "Cheat Sheet" for that event.** (a092c06)
- [x] **Task 48: Build `Competitor_Radar_Watcher`: Agents alert the user when a competitor changes positioning.** (aee006e)

- [x] **Task 48.1: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)** (ec23d0c)

---

## Phase 4: Propagative Execution (Campaign -> Move -> Muse) [checkpoint: ec23d0c]
Consensus triggers action.

- [x] **Task 49: Implement `Campaign_Arc_Generator`: 90-day plan based on Council Consensus.** (ec23d0c)
- [x] **Task 50: Build `Move_Decomposition_Engine`: Breaking Campaigns into weekly Moves.** (ec23d0c)
- [x] **Task 51: Implement `Move_Refiner`: Tool selection and prompt engineering for each Move.** (ec23d0c)
- [x] **Task 52: Build `Propagative_Executor`: Saving refined Moves to the `moves` table.** (ec23d0c)
- [x] **Task 53: Conductor - User Manual Verification 'Phase 4'.** (ec23d0c)
- [x] **Task 54: Implement `Success_Predictor`: Confidence scoring for Moves.** (ec23d0c)
- [x] **Task 55: Build `Kill_Switch_Monitor`: Discarding moves with < 40% confidence.** (ec23d0c)
- [x] **Task 56: Implement `Strategy_Recalibrator`: Looping back to Debate if all Moves fail.** (ec23d0c)
- [x] **Task 57: Conductor - User Manual Verification 'Phase 5'.** (ec23d0c)

- [x] **Task 57.1: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)** (ec23d0c)

---

## Phase 5: Strategic Self-Correction (Matrix & Kill-Switch) [checkpoint: 56cc789]
The council corrects itself.

- [x] **Task 58: Design the `Council_Chamber` UI: 12-avatar grid with real-time "Thought" pulses.** (56cc789)
- [x] **Task 59: Build the `Rationale_Drawer` component in the Moves module.** (56cc789)
- [x] **Task 60: Implement `Pedigree_Visualizer`: A tree view showing which Agent proposed what.** (56cc789)
- [x] **Task 61: Build `Confidence_Heatmap`: Shows Agent alignment on a Move.** (56cc789)
- [x] **Task 62: Implement `Historical_Parallel_UI`: "This move is like the 1994 Nike [Exploit]...".** (56cc789)

- [x] **Task 62.1: Conductor - User Manual Verification 'Phase 5' (Protocol in workflow.md)** (56cc789)

---

## Phase 6: Skill Studio & User Coaching
Enabling the user to train their 12 experts.

- [ ] **Task 63: Build `Skill_Upload_Zone`: Drag-and-drop for PDFs/Docs.**
- [ ] **Task 64: Implement `Librarian_Agent_Processor`: Extracts heuristics from uploads.**
- [ ] **Task 65: Build `Agent_Training_Dashboard`: View and edit each agent's "Learned Skills.".**
- [ ] **Task 66: Implement `Heuristic_Editor`: Direct text editing of an agent's "Never/Always" rules.**
- [ ] **Task 67: Create `Skill_Propagation_Test`: Run a mock prompt to verify a new skill is "active.".**

- [ ] **Task 67.1: Conductor - User Manual Verification 'Phase 6' (Protocol in workflow.md)**

---

## Phase 7: Blackbox Integration & Reflection (The Learning Loop)
Agents get smarter based on what actually happened.

- [ ] **Task 68: Implement `Post_Mortem_Trigger`: Run after a Move is "Executed" in Blackbox.**
- [ ] **Task 69: Build `Reflection_Node`: Agents analyze delta between `Predicted ROI` vs. `Actual`.**
- [ ] **Task 70: Implement `Auto_Correction_Heuristic`: Agents rewrite their own prompts based on failure.**
- [ ] **Task 71: Build `Success_Reinforcement`: Agents prioritize "Winning" exploits in the next debate.**
- [ ] **Task 72: Create `Influence_Weight_Update`: ROI-based voting weight adjustment.**

- [ ] **Task 72.1: Conductor - User Manual Verification 'Phase 7' (Protocol in workflow.md)**

---

## Phase 8: Advanced Toolbelt (The "World-Class" Capabilities)
Giving agents the power to actually execute marketing.

- [ ] **Task 73: Implement `Search_Native_V2`: Support for LinkedIn/X/Reddit scraping (via Brave/DDG).**
- [ ] **Task 74: Build `Ad_Copy_Validator`: Checks copy vs. Facebook/Google ad policies.**
- [ ] **Task 75: Implement `Image_Gen_Director`: Agents write high-fidelity prompts for Muse/DALL-E/Midjourney.**
- [ ] **Task 76: Build `Code_Snippet_Generator`: Data Quant writes SQL for Matrix custom reports.**
- [ ] **Task 77: Create `Email_Sequence_Architect`: Multi-step drip logic generation.**

- [ ] **Task 77.1: Conductor - User Manual Verification 'Phase 8' (Protocol in workflow.md)**

---

## Phase 9: System Reliability & Performance
Ensuring the "Agentic OS" doesn't crash or cost a fortune.

- [ ] **Task 78: Implement `Token_Budget_Manager`: Prevents agents from over-thinking and burning budget.**
- [ ] **Task 79: Build `Parallel_Inference_Optimizer`: Run 12 agent calls in parallel.**
- [ ] **Task 80: Implement `Response_Caching`: Cache agent "Thoughts" for common scenarios.**
- [ ] **Task 81: Build `Agent_Health_Monitor`: Detects if an agent is hallucinating or "Stuck.".**
- [ ] **Task 82: Create `Dry_Run_Simulator`: Test the whole Council without hitting live APIs.**

- [ ] **Task 82.1: Conductor - User Manual Verification 'Phase 9' (Protocol in workflow.md)**

---

## Phase 10: Final Polish & "Quiet Luxury" Delivery
Making it feel like a surgical instrument.

- [ ] **Task 83: Implement `Framer_Motion` layout transitions for the Council Chamber.**
- [ ] **Task 84: Build `JetBrains_Mono` typography integration for reasoning logs.**
- [ ] **Task 85: Create `Sound_Design`: Subtle "click" and "hum" feedback for Agent activity.**
- [ ] **Task 86: Implement `Progressive_Disclosure`: Hide the "Debate" unless the user clicks "Show Reasoning.".**
- [ ] **Task 87: Build `Daily_Briefing_Email`: A "Letter from the Council" summarizing today's moves.**
- [ ] **Task 88: Final Code Review: Ensure 100% compliance with `UI.md` and `BrandKit.md`.**
- [ ] **Task 89: Deployment to Production.**

- [ ] **Task 89.1: Conductor - User Manual Verification 'Phase 10' (Protocol in workflow.md)**
