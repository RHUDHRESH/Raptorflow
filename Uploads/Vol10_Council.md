# RAPTORFLOW MASTER DOCUMENT SERIES
## Volume 10: The Council and Deliberation Engine

---

# Opening: Why the Council Is the Product's Highest-Value Feature

Most users discover RaptorFlow through the daily utility — the briefings, the content, the intel. Most users stay because of the Council. The experience of watching twelve distinct expert minds engage with your specific business problem, argue about the best approach from genuinely different philosophical starting points, and produce a synthesis that none of them would have reached alone — this is the experience that converts users from satisfied customers into advocates.

The Council is not a feature that was added to make the product feel impressive. It is the primary mechanism through which the system produces strategic intelligence that is qualitatively different from what any single agent could produce. The diversity of perspectives is not cosmetic diversity. The Ogilvy-Patel tension produces better campaign recommendations than either Ogilvy or Patel alone produces. The Godin-Sharp disagreement about whether to focus on loyal customers or new buyers produces better audience strategy than either position alone. The Council works because the disagreement is real, the resolution requires genuine synthesis, and the synthesis is better than the average of the inputs.

This volume documents the Council system completely — how sessions are structured, how debates are run, how synthesis is produced, how the Strategist manages the dynamics, and how every Council interaction feeds back into the PRL to improve subsequent sessions.

---

# Part One: Council Session Architecture

## Chapter 1.1 — Session Types and Their Differences

Every Council session is one of four types, each with different scope, different agent composition, and different synthesis requirements.

**Tactical Session (2-3 agents, Flash-Lite Reasoning, 15-30 seconds total):**
Used for specific, bounded questions with clear right answers. 'Should I use this headline or that one?' 'What is the best posting time for this campaign?' 'Does this copy align with our brand voice?' Tactical sessions are fast, cheap, and precise. They do not involve debate rounds — each agent provides their assessment, and the Strategist synthesises in one pass.

**Operational Session (3-5 agents, Flash-Lite Reasoning, 45-90 seconds total):**
Used for Move planning, channel strategy questions, content calendar design, and mid-campaign adjustments. Agents provide positions, there is a single response round where each can address another's position, and the Strategist synthesises. The synthesis is typically 300-500 words. Used most frequently in day-to-day campaign management.

**Strategic Session (5-8 agents, Flash-Lite Reasoning + Pro for synthesis, 2-4 minutes total):**
Used for full Campaign planning, positioning reviews, competitive response decisions, and ICP refinement. Multiple debate rounds. Position, counter-position, synthesis attempt, final positions, final synthesis. The synthesis is 500-1000 words with a structured Campaign or strategic recommendation.

**War Room (8-13 agents, Gemini Pro for synthesis, 5-10 minutes total):**
Used for major strategic decisions: annual marketing strategy, significant brand repositioning, new market entry, major underperformance crisis response. All relevant Council members participate. The debate is multi-round with genuine adversarial positions. The synthesis is a comprehensive strategic recommendation with specific action plans.

## Chapter 1.2 — Session Lifecycle States

A Council session moves through the following states in sequence:

```
initialising → context_assembly → agents_briefed → debate_round_1 → 
[debate_round_2 if strategic/war_room] → synthesis_in_progress → 
synthesis_complete → events_harvested → closed
```

Each state transition is recorded in the council_sessions table with a timestamp. This allows precise measurement of where time is spent in the session lifecycle and where latency improvements would have the most impact.

```sql
CREATE TABLE council_sessions (
  session_id         TEXT PRIMARY KEY,
  org_id             UUID NOT NULL,
  campaign_id        TEXT,
  session_type       TEXT NOT NULL,
  trigger_source     TEXT NOT NULL,
  question_text      TEXT NOT NULL,
  participating_agents TEXT[] NOT NULL,
  state              TEXT NOT NULL DEFAULT 'initialising',
  debate_rounds      INTEGER NOT NULL DEFAULT 0,
  synthesis_model    TEXT,
  synthesis_text     TEXT,
  synthesis_token_count INTEGER,
  total_tokens_used  INTEGER,
  total_cost_usd     FLOAT,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at       TIMESTAMPTZ
);

CREATE TABLE council_agent_positions (
  position_id        TEXT PRIMARY KEY,
  session_id         TEXT NOT NULL REFERENCES council_sessions(session_id),
  agent_id           UUID NOT NULL,
  agent_name         TEXT NOT NULL,
  round_number       INTEGER NOT NULL DEFAULT 1,
  position_text      TEXT NOT NULL,
  core_claim         TEXT,
  key_reasoning      TEXT,
  prediction_embedded JSONB,
  word_count         INTEGER,
  model_used         TEXT NOT NULL,
  token_count        INTEGER,
  generated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## Chapter 1.3 — The Briefing Phase (Phase 0)

Before any agent generates a position, the Strategist assembles a briefing document that is shared with all participating agents. This briefing is the Phase 0 operation — it runs before the user sees any streaming output and typically completes in 1-2 seconds.

The briefing document structure:
- **The question:** the exact question being addressed, restated in the Strategist's voice
- **Relevant Foundation context:** the specific Foundation elements most relevant to this question (not the entire Foundation — only what is needed)
- **Current campaign context:** if applicable, the Move, the task, the performance data relevant to the question
- **Recent intelligence:** any competitive signals detected in the last 72 hours relevant to the question
- **Flags from preliminary assessment:** any issues the Strategist wants agents to consider that they might miss from their individual perspective

The briefing is assembled by the Context Assembler using a targeted retrieval — pulling the most relevant PRL ripples for the question domain, the relevant Foundation sections, and the relevant campaign data. The briefing is then included in each participating agent's ContextPack alongside their private PRL context.

This shared briefing creates a common situational understanding without homogenising the agents' individual perspectives. They all know the same facts. They interpret those facts through completely different lenses.

---

# Part Two: The Debate Mechanics

## Chapter 2.1 — Round 1: Individual Positions

All agents generate their Round 1 positions simultaneously. The fan-out pattern from Volume 7 applies: all inference calls start at the same time, and results are collected as they complete.

Each agent's Round 1 position prompt:

```
Context: [Agent's full ContextPack including Essence Core, Ego Signature, Skill Weave, PRL ripples]

Shared briefing: [The Strategist's briefing document]

Question for the Council: [The specific question]

Provide your position on this question. Your position should:
- Begin with your core claim (one sentence)
- Provide your reasoning (specific to your expertise and experience with this client)
- Note any assumptions underlying your position
- Identify the strongest objection to your position and how you address it
- State what evidence or information would change your position

Write in your characteristic voice. Be specific to this client's situation.
```

The "what evidence would change your position" element is important — it prevents agents from being dogmatic and creates the opening for genuine updating in Round 2.

## Chapter 2.2 — The Strategist's Inter-Round Analysis

After all Round 1 positions are collected, the Strategist performs a brief inter-round analysis before Round 2 begins. This analysis (Flash-Lite Reasoning, ~500 tokens) identifies:

1. **Key agreements:** What are all or most agents agreeing on?
2. **Key disagreements:** Where are the sharpest conflicts?
3. **The most interesting tension:** Which disagreement is most likely to produce genuine insight if explored?
4. **The weakest positions:** Which positions are most vulnerable to the strongest objections raised by other agents?

The inter-round analysis is not shown to the user during the debate. It is used by the Strategist to construct the Round 2 prompts, which direct specific agents to respond to specific positions.

## Chapter 2.3 — Round 2: Direct Engagement (Strategic and War Room Only)

For Strategic and War Room sessions, a second debate round runs where agents directly engage with each other's positions. Unlike Round 1 (where each agent generated independently), Round 2 is targeted: the Strategist's inter-round analysis determines which agent should respond to which position.

The targeting logic: the agent most likely to provide the most useful counter-argument to a given position is the one whose Essence Core is most directly in tension with the position's underlying assumptions. Ogilvy's strongest counter-argument target is Patel's position. Sharp's strongest counter-argument target is Godin's position. Hopkins's strongest counter-argument target is Bernbach's position. These pairings are pre-configured in the Ego Orchestra Lattice.

Round 2 prompt (tailored to each agent):

```
[Agent's ContextPack]

This is Round 2 of the Council debate. You have reviewed the following positions from your colleagues:

[Ogilvy's Round 1 position]
[Patel's Round 1 position]
[Specific other relevant positions]

Your task in Round 2:
1. Respond directly to [Target Agent]'s position. What specifically is wrong with it or what important nuance is it missing?
2. Update your own position if any colleague's argument was strong enough to move you. Be explicit if you are updating.
3. Sharpen your core claim based on the exchange so far.

Maintain your characteristic voice and core convictions.
```

Round 2 is not a free-for-all. Each agent responds to a specific assignment. This prevents the debate from becoming a chaotic multi-way argument and ensures that the most productive tensions are specifically explored.

## Chapter 2.4 — The Synthesis

The Strategist's synthesis is the most important output of the Council session. It is also the most expensive inference call — the only one that uses Gemini Pro for large sessions.

The synthesis prompt is the most carefully constructed prompt in the entire system:

```
You are [Strategist name], Campaign Strategist for [Company name].

Your Council has debated the following question: [Question]

Here are their positions after [1/2] rounds of debate:

[Ogilvy]: [Full Round 1 + Round 2 position]
[Patel]: [Full position]
[All other agents]: [Full positions]

Your task is to synthesise these positions into a single, actionable strategic recommendation.

Synthesis requirements:
1. The synthesis must be better than any individual position — it should incorporate insights that only emerge from the combination of perspectives
2. The synthesis must be specific to [Company name]'s situation — it must reference their Foundation, their current campaigns, their competitive position
3. The synthesis must be actionable — it must end with specific next steps that can be executed
4. The synthesis must be honest about uncertainty — where the evidence is thin, say so
5. The synthesis must acknowledge the strongest counter-argument to your recommendation and explain why the recommendation stands despite it

Structure your synthesis as:
- The recommendation (2-3 sentences)
- The reasoning (which positions contributed what, and why)
- The key assumptions (what must be true for this recommendation to be correct)
- The action plan (specific steps, with responsible avatars where applicable)
- The watch conditions (what would cause you to revise this recommendation)

Write in your characteristic voice. Your Council has given you their best thinking. Give them your best synthesis.
```

The synthesis is streamed to the user in real time. It takes 30-90 seconds to generate depending on length and model. The streaming creates the experience of the Strategist thinking through the synthesis in real time — watching it arrive token by token has a different quality than reading a pre-generated result.

---

# Part Three: Managing the Council Dynamics

## Chapter 3.1 — The Ego Orchestra Lattice in Practice

The Strategist's Ego Orchestra Lattice — described in the EEL volume — is most actively used during the inter-round analysis and synthesis construction phases. The Strategist's knowledge of each avatar's personality means that the synthesis is constructed with awareness of how each avatar will receive it.

**Ogilvy:** Will scrutinise any claim that is not research-backed. The synthesis must ground any creative recommendations in consumer insight language that Ogilvy's framework validates.

**Patel:** Will want specific platform and timing data cited. The synthesis must acknowledge platform considerations explicitly or Patel's next session will relitigate this point.

**Bernbach:** Will dismiss any synthesis that is too safe or conventional. The synthesis should include at least one creative angle that would genuinely surprise someone — even if it is a subordinate recommendation rather than the primary one.

**Hopkins:** Will accept any synthesis that includes a testing protocol. If the synthesis cannot answer 'how will we know if this worked,' Hopkins will keep raising the objection.

**Godin:** Will push back on any synthesis that treats reach as the primary objective without addressing whether the right people are being reached. The synthesis should explicitly address the tribe question.

**Sutherland:** Will be satisfied by any synthesis that acknowledges the irrational element of the decision. Even a parenthetical 'and note that the psychological ease of this option matters beyond its rational merits' will satisfy him.

The Strategist's Ego Orchestra Lattice does not compromise the synthesis to satisfy each avatar. It frames the synthesis in language that each avatar can understand and endorse — not changing what is recommended, but how it is expressed. This is the skill of a great leader managing a great team: the truth is the same; the communication is tailored.

## Chapter 3.2 — When Agents Update Their Positions

Position updating is one of the most diagnostically valuable signals in the Council system. When an agent genuinely updates their position between Round 1 and Round 2 — explicitly acknowledging that a colleague's argument moved them — it indicates that the debate structure is producing genuine learning rather than performative argument.

The position update must be explicit in Round 2: 'Patel's point about the algorithm's current reward structure for Reels is compelling. I am updating my position on content format to acknowledge that short-form video may be appropriate for this audience segment, provided the research into their consumption patterns shows the engagement patterns Patel claims.' This is Ogilvy updating — not abandoning his research principle, but applying it to acknowledge Patel's evidence.

Position updates are detected in the Event Harvester's processing of the session. An explicit acknowledgment of another agent's argument combined with a modified position triggers a positive ripple in both agents' PRL streams: in the updating agent's stream, a learning ripple that records what was updated and why. In the source agent's stream, a predictive accuracy ripple that records that this argument was strong enough to move another avatar.

Over time, these update patterns reveal which agents consistently move others and which consistently move themselves. The Strategist's Ego Orchestra Lattice is enriched by this data — the Strategist learns which combinations of agents produce the most productive updating.

## Chapter 3.3 — Deadlock Handling

Occasionally, Council sessions reach a genuine deadlock: two strong positions in direct conflict with neither having sufficient evidence to overcome the other. Ogilvy arguing for a research-first approach with a specific timeline. Vaynerchuk arguing that the opportunity will be missed by the time the research is complete. Both positions are internally coherent. Neither has compelling evidence that the other is wrong.

The deadlock detection runs during the inter-round analysis for Round 2 sessions. It is identified when: two or more agents' Round 2 positions are substantially unchanged from Round 1 despite direct engagement, and the engagement explicitly acknowledges the other's argument without updating.

When deadlock is detected, the Strategist's synthesis takes a specific structure:

1. **Acknowledge the genuine disagreement:** 'The Council is split on this question, and the split reflects a real uncertainty rather than one party being wrong.'

2. **Name the key assumption that separates the positions:** 'The disagreement ultimately comes down to one question: how much time do we have before the opportunity closes?'

3. **Recommend a resolution mechanism:** Almost always, this is a small test that resolves the key uncertainty: 'Rather than committing to either approach, I recommend a 7-day test that will tell us definitively whether the opportunity is time-sensitive or patient. Here is the specific test design...'

4. **Commit to a fallback:** 'If the test cannot be run within 72 hours for any reason, we will proceed with [specific default approach] because it preserves optionality while the uncertainty is resolved.'

Deadlock is not a failure of the Council system. It is the system being honest about genuine strategic uncertainty rather than producing false confidence. A synthesis that resolves a real uncertainty with a neat-sounding recommendation that one side of the debate would find laughable is worse than a deadlock synthesis that acknowledges the uncertainty and proposes a resolution.

---

# Part Four: The Post-Session Process

## Chapter 4.1 — Private Agent Reflections

After the Council session completes and the synthesis has been delivered, each participating agent runs a private reflection. This reflection is not visible to the user. It is the agent's internal processing of the session's outcome through their Essence Core.

The private reflection prompt (Flash-Lite Reasoning, 300 tokens output):

```
[Agent's ContextPack]

You participated in a Council session that produced the following synthesis:
[Synthesis text]

Your position was:
[Agent's Round 1 + Round 2 position]

Reflect on this session from your perspective. Be honest:
- Was the synthesis right? Where do you agree and where do you disagree?
- Did you learn anything that changes how you would approach similar questions?
- What prediction does this synthesis carry? What would have to be true for it to succeed?
- What would you watch for that would indicate the synthesis should be revised?

This reflection is private. You do not need to be diplomatic.
```

The private reflection is processed by the Event Harvester as a prediction ripple in the agent's private PRL stream. It captures the agent's genuine assessment of the synthesis — which may differ from the public position they took — and the prediction embedded in their interpretation of the session.

When the Campaign's subsequent performance data arrives, these private prediction ripples are updated with the actual outcomes. Over many sessions, the private reflection ripples become the most accurate record of which agents' private assessments were better predictors than the official synthesis. This data informs the Strategist's synthesis weighting — giving more weight to certain agents' concerns when the Ego Orchestra Lattice's experience shows those agents have consistently identified the right risks even when the synthesis went another direction.

## Chapter 4.2 — The Council Session as a PRL Event

The Council session generates a rich set of PRL events across multiple agents simultaneously. Understanding all of them ensures the Event Harvester captures the full learning value of every session.

For **each participating Council avatar:**
- A private_agent episodic ripple recording their position and reasoning (hierarchy level 2)
- A private_agent episodic ripple recording the private reflection (hierarchy level 2)
- If their position was adopted in the synthesis: a private_agent positive prediction ripple (their approach was validated)
- If their position was rejected in the synthesis: a private_agent prediction_error ripple (their approach was not chosen — not that they were wrong, but that the synthesis chose differently)
- Edge links between this session's ripples and ripples from previous sessions involving similar questions

For the **Campaign Strategist:**
- A strategist_only ripple recording the synthesis and the reasoning that produced it (hierarchy level 3)
- A shared_campaign ripple recording the synthesis recommendation (visible to all agents)
- Prediction ripples for each key claim in the synthesis
- Ego Orchestra Lattice ripples recording how each agent behaved in this session (updates to the Strategist's model of each avatar)

For **shared campaign context:**
- A shared_campaign ripple summarising the debate and synthesis for any agent that needs to reference this Council session's conclusions in future work

---

# Part Five: The Complexity Router — Complete Specification

## Chapter 5.1 — The Full Routing Decision Tree

The Complexity Router runs before every Council session initiation. Its complete decision logic:

**Input:** The request (question text + context), the requesting user's org context, the active campaigns, the available agent roster.

**Step 1 — Request Classification:**
Flash-Lite Normal call with structured output:
```json
{
  "domain": "creative | strategic | analytical | operational | mixed",
  "stakes": "routine | moderate | high | critical",
  "requires_perspectives": 1-12,
  "time_sensitive": true/false,
  "has_right_answer": true/false
}
```

**Step 2 — Session Type Selection:**
- If stakes = 'routine' AND requires_perspectives ≤ 2: Tactical
- If stakes = 'moderate' OR (stakes = 'routine' AND requires_perspectives ≤ 4): Operational
- If stakes = 'high' OR requires_perspectives ≥ 5: Strategic
- If stakes = 'critical': War Room

**Step 3 — Agent Selection:**
For the selected session type and domain, select agents by relevance score:
```
relevance_score = (domain_tag_overlap / total_tags) × 10
                + (essence_alignment_to_question × 5)
                + (recent_activation_bonus × 2)  // boosted if agent was active recently
                + (client_history_bonus × 3)     // boosted if agent has high-salience ripples for similar questions
```
Select top N agents where N is the session type maximum.

**Step 4 — Override Check:**
Apply any user override preferences stored in the Strategist's PRL (users who consistently add/remove specific agents for similar request types).

**Step 5 — Synthesis Model Selection:**
- War Room with 8+ agents: Gemini Pro
- Strategic with 6+ agents: Gemini Pro
- All others: Flash-Lite Reasoning

**Output:** AgentSelection struct with participating_agents, session_type, synthesis_model, estimated_cost.

## Chapter 5.2 — The Question Queue

During high-activity periods — when a user is asking multiple Muse questions in rapid succession while also having an active Council session — the Council sessions are queued rather than run concurrently. A user does not typically want two simultaneous Council sessions running; the outputs would conflict and neither would be fully informed by the other.

The question queue is maintained in DragonflyDB as a sorted set per org, sorted by priority. Priority calculation: War Room > Strategic > Operational > Tactical. Within the same priority level, first-in-first-out.

When the queue processes a new session request, it checks whether any session of equal or higher priority is currently running for this org. If yes, the new request is added to the queue with its priority score. If no, the new session starts immediately. Sessions of lower priority than a running session also queue.

The queue is presented to the user in the Council view as a visual indicator: 'Your previous session is synthesising. This question will begin in approximately [estimated seconds].' This transparency prevents the user from thinking the system is slow when it is actually being respectful of in-progress work.

---

# Part Six: Council Economics

## Chapter 6.1 — Cost Per Session Type

Understanding the cost per Council session type is essential for monitoring unit economics and for evaluating whether the routing logic is correctly balancing quality and cost.

**Tactical session (2-3 agents):**
- Context assembly: ~$0.0002 per agent (Foundation cache savings applied)
- Inference: 2-3 × Flash-Lite Reasoning at ~1,000 tokens output = ~$0.0004
- Synthesis: Flash-Lite Reasoning ~$0.0002
- Event Harvester: Flash-Lite Normal ~$0.0001
- **Total: ~$0.0009-0.0013 per Tactical session**

**Operational session (3-5 agents):**
- Context assembly: ~$0.0003-0.0005
- Inference: 3-5 × Flash-Lite Reasoning = ~$0.0006-0.0010
- Synthesis: Flash-Lite Reasoning = ~$0.0003
- **Total: ~$0.0012-0.0018 per Operational session**

**Strategic session (5-8 agents, Pro synthesis):**
- Context assembly: ~$0.0005-0.0008
- Inference: 5-8 × Flash-Lite Reasoning = ~$0.0010-0.0016
- Synthesis: Gemini Pro ~$0.003-0.008 (varies with length)
- **Total: ~$0.004-0.010 per Strategic session**

**War Room (8-13 agents, Pro synthesis):**
- Context assembly: ~$0.0008-0.0013
- Inference: 8-13 × Flash-Lite Reasoning = ~$0.0016-0.0026
- Synthesis: Gemini Pro ~$0.008-0.020
- **Total: ~$0.010-0.024 per War Room session**

At a typical usage pattern of 15 Tactical, 8 Operational, 3 Strategic, and 1 War Room per user per month:
- Tactical: 15 × $0.0011 = $0.017
- Operational: 8 × $0.0015 = $0.012
- Strategic: 3 × $0.007 = $0.021
- War Room: 1 × $0.017 = $0.017
- **Total Council cost per user per month: ~$0.067 (approximately ₹5.60)**

The Council, including all its sophistication, costs less than six rupees per user per month. This is why the economics work.
