# Specification: The RaptorFlow Expert Council (Agentic OS)

## 1. Vision & Overview
RaptorFlow is evolving into a **SOTA Agentic Marketing OS**. We are implementing a **Council of 12 Expert Marketers**—autonomous agents with distinct personas, "Past Exploits" (skills), and heuristic rulesets. These agents collaborate via a "Hybrid Cognitive Architecture" to debate strategy, critique execution, and autonomously drive Campaigns, Moves, and Blackbox experiments.

The goal is **"Quiet Luxury Intelligence"**: the user receives the output of a world-class marketing department, backed by transparent, multi-agent reasoning.

---

## 2. The Expert Council (12 Personas)
Each agent is a specialized `ExpertSpecialist` instance:
1. **Direct Response Architect** | 2. **Viral Alchemist** | 3. **Brand Philosopher** | 4. **Data Quant** | 5. **Community Catalyst** | 6. **Media Buyer Strategist** | 7. **SEO/Content Moat Builder** | 8. **PR & Media Specialist** | 9. **Behavioral Psychologist** | 10. **Product Marketing Lead** | 11. **Partnership/Affiliate Hunter** | 12. **Retention & LTV Specialist**

---

## 3. Cognitive Architecture & Interaction
- **Asynchronous Swarm:** Continuous monitoring of Radar/Blackbox signals.
- **Hierarchical Waterfall:** Strategy (90-day arcs) flows into Tactics (weekly moves).
- **Council Debate:** High-stakes decisions require a "Fan-out" debate, synthesis by a Moderator, and final clearance by a Governor.

---

## 4. "Calculated Genius" Improvement Engines (The Learning Loop)
To make the agents "actually useful" and "better than nothing," they utilize four evolution systems:

### 4.1 Outcome-Based Weighting (The Blackbox Loop)
Agents "Reflect" on the ROI of every Move. Successful tactics increase an agent's "Influence Weight" in the council; failures trigger a heuristic update to prevent repetition of errors.

### 4.2 Recursive Critique (The Red Team)
Every proposal undergoes a **Red Team Review**. Three opposing experts attempt to "break" the strategy. The proposing agent must address these critiques before the move is finalized.

### 4.3 Skill Synthesis (RAG Evolution)
A **Librarian Agent** extracts "Atomic Rules" from user-uploaded case studies in the **Skill Studio**, updating the core knowledge base of relevant experts in real-time.

### 4.4 Synthetic Rehearsal (Simulated Experiments)
Agents run 100+ variations of a campaign in a simulated Blackbox environment, selecting the "Genius Version" based on mathematical win-probability before showing it to the user.

---

## 5. Functional Requirements
- **Exploits & Heuristics:** Managed via `.md` case studies and `.yaml` rulesets.
- **Rationale Package:** Every output includes:
    - **Debate Transcript:** Summary of expert arguments.
    - **Rejected Paths:** 2-3 alternatives and why they were discarded.
    - **Confidence Metrics:** Multi-agent alignment score (RAG).
    - **Historical Parallel:** Reference to the specific "Exploit" that inspired the move.
- **UI/UX Components:**
    - **Council Chamber:** Real-time visual feed of agent activity.
    - **Move Pedigree Drawer:** Deep-dive into reasoning.
    - **Skill Studio:** Interface for training agents with custom docs.

---

## 6. Implementation Phases
- **Phase 1: Foundation & Skill Studio:** Codify personas, build the Skill Studio/Librarian.
- **Phase 2: The Council Graph:** Implement LangGraph "Council" nodes with Debate/Critique logic.
- **Phase 3: The Learning Spine:** Connect Blackbox outcomes to agent reflection and weighting.
- **Phase 4: Matrix & Visualization:** Ship the Council Chamber and Pedigree UI.

---

## 7. Acceptance Criteria
- [ ] 12 distinct experts are active with verifiable, unique reasoning styles.
- [ ] Every "Move" includes a Rationale Package (Debate, Rejections, Parallel).
- [ ] Agents autonomously "Reflect" and update heuristics based on Blackbox ROI data.
- [ ] Users can "Train" agents via the Skill Studio with custom campaign docs.
