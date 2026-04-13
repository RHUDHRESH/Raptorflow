**RAPTORFLOW**

MASTER DOCUMENT SERIES

**VOLUME EIGHT**

**Campaigns, Moves, and the Dynamic Replanning Engine**

_How campaigns are created, structured, executed, and adapted — every state, every logic path, every connection to intelligence and memory_

CONFIDENTIAL — INTERNAL BLUEPRINT

# **Opening: Campaigns Are Not Plans. They Are Living Systems.**

The word campaign implies a fixed plan that is executed. This is the wrong mental model for how Campaigns work in RaptorFlow. A Campaign in RaptorFlow is a living strategic system — one that was designed at a specific moment with specific information, that executes against a specific goal, and that continuously responds to new information as it arrives. A Campaign that never changes is a Campaign that is ignoring what it is learning.

The most important thing about the Campaign and Move system is not how they are created. It is how they respond. How they respond when a task is missed. How they respond when a competitor does something unexpected. How they respond when performance data comes in significantly above or below projection. How they respond when the user changes something about their Foundation. How they respond to the passage of time.

A campaign management system that does not respond to these events is a project management tool dressed up in marketing language. The RaptorFlow Campaign and Move system is something different: a strategic executive that monitors, interprets, and adapts — continuously, autonomously, and in ways that reflect a genuine understanding of what the campaign is trying to achieve and why.

This volume describes everything about how Campaigns and Moves work, from the data model to the creation flow to the complete set of state transitions to the Dynamic Replanning Engine that makes them genuinely adaptive. Every logic path is documented. Every edge case is addressed. Every connection to the intelligence system, the PRL, and the agent avatars is specified.

# **Part One: The Campaign Data Model**

## **Chapter 1.1 — The campaigns Table**

Every Campaign in the system is represented by a row in the campaigns table. The table is designed to support the full lifecycle of a Campaign — from draft through active execution through completion and archival — with enough state to allow the Dynamic Replanning Engine to understand the Campaign's history, current position, and projected trajectory.

CREATE TABLE campaigns (

campaign_id TEXT PRIMARY KEY,

org_id UUID NOT NULL,

name TEXT NOT NULL,

status TEXT NOT NULL DEFAULT 'draft',

primary_goal TEXT NOT NULL,

goal_category TEXT NOT NULL,

kpi_target JSONB NOT NULL,

target_icp_id UUID REFERENCES foundation_icps(id),

ad_budget_monthly INTEGER,

start_date DATE NOT NULL,

end_date DATE NOT NULL,

brief_text TEXT NOT NULL,

brief_context JSONB,

strategic_rationale TEXT,

created_by_session TEXT,

replanning_count INTEGER NOT NULL DEFAULT 0,

last_replanned_at TIMESTAMPTZ,

performance_snapshot JSONB,

intelligence_snapshot JSONB,

created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

);

The status field has seven valid values representing the complete Campaign lifecycle. Draft is the initial state when the Campaign exists in the database but has not yet been presented to the user for approval. Pending_approval is the state after the Strategist has produced the Campaign structure and it is waiting for user confirmation. Active is the executing state. Paused is when the user has deliberately paused execution. Replanning is the transient state during autonomous replanning — the Campaign is temporarily not active while the replanning session runs. Completed is the state after the end_date has passed and all Moves have resolved. Archived is the long-term storage state after completion.

The kpi_target field is a JSONB object with a structure that matches the goal_category. For a traffic goal: {metric: 'monthly_visitors', target_value: 50000, current_value: 12000, baseline_date: '2026-03-01'}. For a leads goal: {metric: 'monthly_leads', target_value: 200, current_value: 45, baseline_date: '2026-03-01'}. For a revenue goal: {metric: 'marketing_attributed_revenue', target_value: 500000, current_value: 85000, currency: 'INR'}. The current_value is updated regularly by the Analytics Director's monitoring process.

The performance_snapshot field stores a regularly updated summary of campaign performance against the kpi_target. It is structured as {snapshot_date: timestamp, current_value: number, trajectory: 'on_track' | 'above_target' | 'below_target' | 'critical', projected_end_value: number, last_updated_by: 'analytics_director'}. This snapshot is what the Dynamic Replanning Engine checks when evaluating the KPI deviation trigger.

The intelligence_snapshot field stores the most recent competitive intelligence state that was relevant to this campaign. It includes any competitor changes detected since the campaign began and their assessed impact on the campaign strategy. This snapshot is used by the Replanning Engine to determine whether intelligence changes have reached the threshold for triggering a review.

## **Chapter 1.2 — The campaign_moves Table**

Every Campaign contains one or more Moves. Moves are the tactical containers within the Campaign — each Move has its own sub-goal, its own timeline, and its own set of daily tasks. The relationship between a Campaign and its Moves is one-to-many, with the ordering of Moves determined by their sequence_number.

CREATE TABLE campaign_moves (

move_id TEXT PRIMARY KEY,

campaign_id TEXT NOT NULL REFERENCES campaigns(campaign_id),

org_id UUID NOT NULL,

sequence_number INTEGER NOT NULL,

name TEXT NOT NULL,

sub_goal TEXT NOT NULL,

move_type TEXT NOT NULL,

status TEXT NOT NULL DEFAULT 'pending',

start_date DATE NOT NULL,

end_date DATE NOT NULL,

target_channels TEXT\[\] NOT NULL,

strategic_intent TEXT NOT NULL,

council_rationale JSONB,

performance_data JSONB,

completion_criteria JSONB NOT NULL,

tasks_completed INTEGER NOT NULL DEFAULT 0,

tasks_total INTEGER NOT NULL DEFAULT 0,

tasks_missed INTEGER NOT NULL DEFAULT 0,

created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

);

The move_type field classifies the Move's strategic purpose: awareness (building reach and brand recognition), consideration (nurturing interested prospects), conversion (driving purchase decisions), retention (reducing churn and deepening engagement), reactivation (re-engaging lapsed customers), and launch (coordinating the release of something new). The move_type drives both the content generation approach and the performance metrics used to evaluate the Move's success.

The council_rationale field is a JSONB object containing the structured output of the Council session that designed this Move. It records which agents contributed, what their key positions were, how disagreements were resolved, and what the Strategist's synthesis reasoning was. This rationale is referenced by the Replanning Engine when evaluating whether a change in circumstances would alter the Council's reasoning — if the change directly affects the assumption on which a key council position was based, replanning is more likely to be recommended.

The completion_criteria field defines what success looks like for this specific Move. It is a JSONB object with the Move-specific performance thresholds that indicate the sub-goal has been achieved. For an awareness Move: {min_reach: 50000, min_impressions: 200000, min_engagement_rate: 0.03}. For a conversion Move: {min_conversions: 50, min_roas: 2.5, max_cpa: 1000}. The completion_criteria are set during Move creation and are used by the Analytics Director to assess whether the Move is on track and whether it has succeeded.

## **Chapter 1.3 — The campaign_tasks Table**

Each day of each Move contains a set of tasks — the specific, actionable items that the user needs to complete to advance the Move's sub-goal. Tasks are the atomic units of campaign execution.

CREATE TABLE campaign_tasks (

task_id TEXT PRIMARY KEY,

move_id TEXT NOT NULL REFERENCES campaign_moves(move_id),

campaign_id TEXT NOT NULL,

org_id UUID NOT NULL,

day_number INTEGER NOT NULL,

scheduled_date DATE NOT NULL,

task_type TEXT NOT NULL,

title TEXT NOT NULL,

description TEXT NOT NULL,

channel TEXT,

assigned_agent_id UUID,

status TEXT NOT NULL DEFAULT 'pending',

content_ready BOOLEAN NOT NULL DEFAULT FALSE,

content_id TEXT REFERENCES generated_content(content_id),

completed_at TIMESTAMPTZ,

missed_at TIMESTAMPTZ,

override_reason TEXT,

created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

);

The task_type field classifies what type of task this is: publish_content (a piece of content that needs to be approved and posted), review_performance (a scheduled performance analysis review), approve_content (content that has been generated and needs user approval before publishing), create_content (content that needs to be generated — typically for content types not pre-generated), execute_ad (an ad campaign action — budget change, targeting update, creative swap), conduct_outreach (a specific outreach action), or monitor_intel (a scheduled competitive intelligence review).

The content_ready field indicates whether the associated content for this task has been pre-generated and is waiting in the generated_content table. Most publish_content tasks will have content_ready true by the time the task becomes due, because the Content Engine pre-generates content for upcoming tasks during off-peak hours. The user's job is to review and approve, not to generate from scratch.

The assigned_agent_id links the task to the avatar who was responsible for creating the content or strategy associated with this task. This attribution supports the Office visualization — showing which agent is responsible for which day's work — and the PRL — ripples from this task are attributed to the assigned agent's private stream.

## **Chapter 1.4 — The generated_content Table**

All content generated for campaigns — ad copy variants, social captions, blog drafts, email body copy — is stored in the generated_content table. This content is associated with campaign tasks and is what the user reviews and approves before publishing.

CREATE TABLE generated_content (

content_id TEXT PRIMARY KEY,

org_id UUID NOT NULL,

campaign_id TEXT REFERENCES campaigns(campaign_id),

move_id TEXT REFERENCES campaign_moves(move_id),

task_id TEXT REFERENCES campaign_tasks(task_id),

content_type TEXT NOT NULL,

channel TEXT,

content_body TEXT NOT NULL,

content_variants JSONB,

voice_compliance_score FLOAT,

generating_agent_id UUID,

generation_model TEXT NOT NULL,

generation_prompt TEXT,

status TEXT NOT NULL DEFAULT 'draft',

user_feedback TEXT,

performance_data JSONB,

created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

approved_at TIMESTAMPTZ

);

The content_variants field stores multiple versions of the same content where variants are appropriate — headline A/B variants, multiple caption options for the user to choose from, alternative CTA formulations. The structure is a JSON array where each element has a variant_label (A, B, C or descriptive) and the variant_body text.

The performance_data field is populated after the content has been published and performance data is available. For social posts: {impressions: number, engagement_rate: float, clicks: number, shares: number}. For ads: {reach: number, ctr: float, conversions: number, cost_per_result: float}. This data becomes the raw input for the Analytics Director's content performance analysis and for the PRL ripples that close the learning loop from content generation to performance outcome.

# **Part Two: The Campaign Creation Flow**

## **Chapter 2.1 — The Brief Submission**

The Campaign creation flow begins when the user submits a brief. The brief is not a free-form text input — it is a structured conversation between the user and the Campaign Strategist, mediated by the brief form UI, that extracts all the information required for a Council session to produce a useful Campaign structure.

The brief form collects five elements. Primary goal: what the Campaign is trying to achieve, expressed in terms of one of the Foundation KPIs. The user selects from the goal categories established in their Foundation (traffic, leads, conversions, awareness, retention, or launch) and specifies numerical targets where applicable. Timeline: start date and end date. The Strategist evaluates whether the goal is achievable within the timeline given the available Foundation context — a dramatically ambitious goal in a very short timeline will be flagged.

Specific context: any information specific to this Campaign that is not in the Foundation. A seasonal relevance (the campaign is for Diwali). A specific event (there is a trade show in two weeks). A specific constraint (the ad budget is limited to twenty thousand rupees this month). A competitive response (a competitor just launched something and this Campaign is a response). This context supplements the Foundation and shapes the Council's approach.

Channel preferences: the user can specify which channels they want this Campaign to prioritize, or leave it to the Strategist's judgment. If specified, the channel preference is treated as a hard constraint — the Council will not design Moves for channels the user has excluded. ICP targeting: which ICP should this Campaign primarily target. Defaults to the primary ICP from the Foundation but can be overridden for Campaigns that are specifically designed for a secondary ICP.

## **Chapter 2.2 — Brief Evaluation by the Campaign Strategist**

After the user submits the brief, the Campaign Strategist evaluates it before accepting it and convening the Council. The evaluation is a Flash-Lite Reasoning inference call that checks the brief against five criteria and produces a structured evaluation result.

Criterion 1: Goal clarity. Is the goal specific enough to plan for? 'Grow the business' is not a specific goal. 'Generate 150 qualified leads in the next 60 days from the manufacturing sector ICP' is specific. Goals that are too vague receive a specific clarification request identifying exactly what needs to be clarified.

Criterion 2: Timeline feasibility. Is the goal achievable within the timeline given reasonable campaign design? The Strategist checks the goal against the Foundation's historical baseline (if available) and against general benchmarks for the goal category and industry. A traffic doubling goal in 14 days is flagged as highly ambitious for an organic campaign but achievable with significant paid investment — the Strategist notes the implication.

Criterion 3: Context sufficiency. Is there enough context about this specific Campaign's situation to design it appropriately? The most common insufficiency is when the Campaign is a response to something competitive or contextual that the Foundation does not capture. If the user mentions 'our competitor launched something last week' but does not explain what the competitor launched, the Strategist asks for that detail.

Criterion 4: Foundation alignment. Does the Campaign goal align with the Foundation's stated priorities? A Campaign goal that directly contradicts a Foundation KPI priority is flagged — not rejected, but questioned: 'Your Foundation identifies customer retention as a secondary priority and lead generation as primary. This Campaign is focused on retention. Is this a deliberate priority shift, or should we treat this as a supplementary Campaign?'

Criterion 5: Resource alignment. Does the Campaign scope match the budget and team capacity available? A Campaign that requires sophisticated multi-channel paid media execution for a user who has indicated they have no current paid media experience is flagged for scope adjustment.

If the brief passes all five criteria, the Strategist accepts it. If any criterion fails, the Strategist sends a specific clarification request — not a generic 'please provide more information' but a precise question addressing the specific gap. The user must respond to the clarification before the Council is convened.

## **Chapter 2.3 — The Council Session for Campaign Planning**

Once the brief is accepted, the Campaign Strategist convenes the relevant Council agents for the Campaign planning session. The Complexity Router determines the session tier based on the Campaign's complexity assessment. Most Campaign planning sessions are Operational (3 to 5 agents) or Strategic (5 to 8 agents). War Room sessions for Campaign planning are reserved for major strategic pivots or launches that have significant business implications beyond normal marketing.

The Campaign planning session operates differently from a standard Council question session. It has three distinct phases rather than the standard two-phase debate-and-synthesis structure.

### **Phase 1: Situation Assessment**

In Phase 1, the Strategist briefs all participating agents on the Campaign brief, the relevant Foundation context, and the current competitive intelligence state. Each agent is given the opportunity to raise flags — issues with the brief that might affect the Campaign design — before any strategic recommendations are made. The Strategist synthesizes these flags into a shared situational understanding that all agents work from in Phase 2.

Phase 1 is not visible to the user in real time — it runs synchronously as part of the context assembly before the Phase 2 streaming begins. The flags raised in Phase 1 are incorporated into each agent's Phase 2 context, ensuring that the debate is informed by the complete situational picture rather than each agent working from their own partial view.

### **Phase 2: Strategic Design Debate**

Phase 2 is the standard Council debate phase — agents generate their positions on the Campaign strategy simultaneously, these are synthesized by the Strategist, and the debate is visible to the user in the Council view if they are watching.

For Campaign planning specifically, each agent's position includes three components: a recommended Move sequence (which types of Moves should the Campaign include, in what order, for how long), a channel mix recommendation (which channels should each Move focus on and how should budget be allocated), and a content strategy outline (what types of content should be produced for each Move and what emotional and rational positioning it should use).

The debate between agents about Campaign structure is one of the richest in the system. Ogilvy argues for adequate time in an awareness Move before pushing for conversion — rushing to conversion without established brand awareness is, in his view, the most common and most costly mistake in campaign planning. Patel argues for a faster transition to conversion based on what the platform data shows about this category's conversion windows. Hopkins argues that the Move sequence should be determined by testing rather than by theory — launch a short test of both approaches and let the results determine the sequence. The synthesis must navigate all three positions.

### **Phase 3: Tactical Specification**

Phase 3 converts the synthesized Campaign strategy into the specific Move and task structure that will be stored in the database. This phase runs after the synthesis is complete and is not typically visible to the user — it is computational rather than deliberative.

The Strategist takes the synthesis and generates: the specific Move records with their sub-goals, timelines, and completion criteria; the daily task list for each Move; and the content pre-generation schedule (which content should be pre-generated, by which agent, on which day before the task is due). This structured output is stored in the campaign_moves and campaign_tasks tables.

## **Chapter 2.4 — Campaign Approval and Activation**

After the Council session completes and the tactical specification is stored, the Campaign is presented to the user for approval. The status transitions from draft to pending_approval. The user sees the Campaign structure in the Campaign view: the goal and timeline, the Move sequence with each Move's sub-goal and duration, the expected outcome projections, and the strategic rationale.

The expected outcome projections are generated by the Analytics Director based on the Campaign structure and the Foundation's historical performance baselines. They are expressed as ranges rather than point estimates — 'expected to generate between 80 and 150 leads over 60 days' — because point estimates create false precision. The range reflects the genuine uncertainty in campaign outcome projection and is calibrated to be realistic rather than optimistic.

The user has three options in the approval flow: Approve as presented, Request modifications to specific Moves or tasks, or Reject and start over with a revised brief.

Approve as presented: the Campaign status transitions to active, the start_date is confirmed, and the content pre-generation schedule begins running. The first tasks appear in the user's dashboard task list on the scheduled_date of the first task. The Office animation shows the Campaign strategist filing the approved brief and briefing the relevant agents.

Request modifications: the user specifies what they want changed — a Move that seems too long, a channel they want removed, a content approach they want adjusted. These modifications are processed through a mini-Council session (typically 2 to 3 agents) that incorporates the changes into the Campaign structure while maintaining strategic coherence. The modified Campaign is re-presented for approval.

Reject and restart: the user provides feedback on why the Campaign structure is wrong. The feedback becomes context for a new briefing session. The Strategist incorporates the feedback into the next brief evaluation, ensuring the new approach addresses the user's concerns.

# **Part Three: Campaign Execution**

## **Chapter 3.1 — The Daily Task Experience**

Once a Campaign is active, the user's daily interaction with it is primarily through the task list. The task list shows all tasks due today across all active Campaigns and Moves, organized by Campaign and sorted by urgency.

For each task, the user sees: the task title and a brief description, the channel it applies to, the Campaign and Move it belongs to, whether content is ready for review (content_ready flag), and the action buttons appropriate to the task type.

For a publish_content task with content ready: the user sees the pre-generated content, can review it, can request edits (which triggers a content revision generation), can approve it (status transitions to approved), or can reject it and request completely new content. The approve action is one click. The entire review-and-approve flow for a typical social post should take under 60 seconds for a user who is satisfied with the content.

For a review_performance task: the Analytics Director's prepared performance summary appears inline in the task, showing the relevant metrics for the period under review. The user reads the summary, marks the task complete, and is shown the Strategist's recommended action based on the performance data.

For an execute_ad task: the task shows the specific ad management action to take — 'increase daily budget on this ad set from 500 to 750 rupees' — with the strategic reasoning behind it. The user takes the action in their ad platform and marks the task complete. At launch, ad execution tasks are advisory rather than automated — the system recommends; the user executes. Post-launch, direct ad platform integration is on the roadmap.

## **Chapter 3.2 — Content Pre-Generation**

The content pre-generation system ensures that content is ready for the user to review before the task is due, rather than being generated on demand when the user opens the task. This is the mechanism that creates the 'team has done the work before you arrived' experience.

The pre-generation schedule is calculated during Campaign activation. For each publish_content task, the content generation is scheduled for three days before the task's scheduled_date. This gives the user three days to review, request revisions, and approve before the content needs to be published. If the content generation is scheduled during off-peak hours — typically between 1 AM and 5 AM IST — it is batched with other pre-generation operations to reduce inference costs.

The pre-generation call specifies: the content_type, the channel, the task context (which Move and what sub-goal), the Foundation context (brand voice, ICP, positioning), the assigned agent (which Council avatar or intern is generating this specific piece), and any specific guidance from the Move's content strategy outline produced during Campaign planning.

The generating agent for each piece of content is determined by the content type. Ad copy is assigned to Ogilvy or Hopkins. Social captions are assigned to Vaynerchuk or Godin depending on whether the Move is reach-focused or community-focused. Blog post drafts are assigned to Draper for narrative pieces and Ogilvy for research-backed long-form. Email copy is assigned to Hopkins for conversion-focused sequences and Draper for brand story sequences. The assignments are stored in the campaign_tasks.assigned_agent_id field.

When pre-generation fails — an inference error, a safety filter trigger, a timeout — the system retries up to three times with a 30-minute delay between retries. If all retries fail, the task is flagged with status content_generation_failed, and a Nudge is generated for the user indicating that this specific task needs attention. The user can manually trigger content generation or modify the task to use different content parameters.

## **Chapter 3.3 — Task Status Transitions**

Understanding all the possible state transitions for a task is essential for implementing the task management system correctly. Tasks do not just transition from pending to completed — they can follow several different paths depending on user actions and system events.

The task begins in pending state. When the task's scheduled_date arrives — the midnight transition determined by the IST cron job — the task transitions to due. When content is successfully pre-generated for the task, the content_ready field is set to true and the task status transitions to ready_for_review. When the user approves the content but has not yet published it, the task transitions to approved. When the user marks the task as complete (for non-content tasks) or confirms publication (for content tasks), the task transitions to completed. The completed_at timestamp is set and the campaign_moves.tasks_completed count is incremented.

When a task's due date passes without the user completing it, the missed detection job (running every 2 hours) identifies it and transitions the task to missed. The missed_at timestamp is set, the campaign_moves.tasks_missed count is incremented, and the Dynamic Replanning Engine is notified to evaluate whether this miss warrants a replanning session.

The user can also override a task — marking it as not applicable or completing it through an alternative method not tracked in the system. The override action requires the user to provide a brief reason, which is stored in the override_reason field. Overridden tasks are treated the same as completed tasks for replanning evaluation purposes.

A task can also be modified — its scheduled_date can be moved, its channel can be changed, its assigned agent can be changed. Modifications are tracked through the campaign_tasks audit log and considered by the Replanning Engine when assessing whether the Campaign's execution is following the planned trajectory.

# **Part Four: The Dynamic Replanning Engine**

## **Chapter 4.1 — The Three Triggers**

The Dynamic Replanning Engine monitors all active Campaigns continuously and evaluates three distinct trigger conditions every two hours. Each trigger has its own evaluation logic, its own threshold for initiating a replanning session, and its own set of agents most relevant to the replanning analysis.

### **Trigger 1: Task Miss Assessment**

The task miss trigger evaluates whether missed tasks have reached a threshold that warrants Campaign restructuring. A single missed task is not typically a trigger — campaigns always have some execution variance. The evaluation considers: the severity of the missed task (was it critical to the Move's execution? Was it a publish_content task on a high-value date?), the cumulative miss rate for this Move (what percentage of tasks have been missed?), and the projected impact on the Move's completion criteria if the miss pattern continues.

The threshold formula: trigger if (critical_tasks_missed > 0) OR (tasks_missed_rate > 0.20 AND remaining_days > 3). A single critical task missed triggers immediate evaluation. A miss rate above 20 percent with more than three days remaining triggers evaluation if the projected completion criteria achievement falls below 60 percent. The 60 percent threshold is configurable per Campaign based on the Campaign's stated goal priority — high-priority Campaigns use a tighter threshold.

When the task miss trigger fires, the Impact Assessment runs first. The Impact Assessment is a lightweight Flash-Lite Normal inference call that takes the missed task details and the Move's completion criteria and produces a structured impact estimate: {impact_level: 'negligible' | 'moderate' | 'significant' | 'critical', projected_goal_achievement: float, recommended_action: string}. Only impact levels of 'significant' or 'critical' proceed to a full replanning session. Negligible and moderate impacts generate an informational Nudge without triggering a replanning session.

### **Trigger 2: Intelligence Change Assessment**

The intelligence trigger evaluates whether competitive or market changes detected by the intelligence pipeline have reached a threshold that warrants Campaign strategy review. Not every competitive change triggers a review — the evaluation filters for changes that are directly relevant to the active Campaign's approach.

The relevance assessment: a competitive change is relevant to an active Campaign if it satisfies at least one of three conditions. First, the change is made by a competitor who targets the same ICP the Campaign is targeting, on a channel the Campaign is actively using. Second, the change involves a competitor's messaging that directly addresses the same customer problem the Campaign's content is addressing. Third, the change involves a significant increase in competitor ad spend in the same channel at the same time period the Campaign is running — this creates a competitive pressure on reach and cost that the Campaign's budget assumptions may not have accounted for.

Relevance assessment runs as part of the Nudge evaluation job. When a competitive change is detected by the intelligence pipeline, it is cross-referenced against all active Campaigns to identify which are affected. For affected Campaigns, the impact level is assessed: {affected_campaigns: array, impact_per_campaign: object, time_sensitivity: 'immediate' | 'this_week' | 'this_month'}. Only immediate or this_week impacts proceed to replanning evaluation. This_month impacts generate a Nudge that informs the user of the change without triggering autonomous replanning.

The intelligence trigger must balance sensitivity — catching changes that genuinely require Campaign adaptation — against noise. A competitor posting more frequently on Instagram is not the same as a competitor launching a competing product at a lower price point. The impact assessment must distinguish between these and only escalate the truly consequential changes.

### **Trigger 3: KPI Deviation Assessment**

The KPI deviation trigger evaluates whether the Campaign's performance against its target KPI has deviated significantly enough from the projection to warrant reviewing the Campaign approach. Both positive and negative deviations can trigger evaluation — significant overperformance is as worth analyzing as significant underperformance.

The deviation threshold: trigger if the current trajectory projects a final outcome that differs from the target by more than 20 percent in either direction, and there are more than five days remaining in the Campaign. The five-day floor prevents pointless replanning when there is not enough time remaining for any strategic change to have a meaningful impact.

Overperformance trigger: if the Campaign is tracking significantly above target, the evaluation asks whether budget acceleration would increase the eventual outcome proportionally. If the answer is yes, the Replanning Engine generates a recommendation to increase ad spend or increase content frequency rather than a structural Campaign change. The Strategist presents this as an opportunity Nudge rather than a replanning session.

Underperformance trigger: if the Campaign is tracking significantly below target, a full replanning session is initiated with the Analytics Director and the most relevant Council agents for the goal category. The session analyzes what is underperforming, why, and what adjustments would improve the trajectory.

## **Chapter 4.2 — The Replanning Session**

When any trigger escalates to a full replanning session, the Replanning Engine creates a replanning session in the Harness. A replanning session is a special type of autonomous Council session that runs without requiring real-time user participation.

The replanning session has a distinct structure from a standard Campaign planning session. It is constrained to produce minimal necessary changes — the smallest modifications to the Campaign structure that address the identified problem — rather than a complete Campaign redesign. This constraint is important: users have invested cognitive energy in the existing Campaign plan and extensive changes create unnecessary disruption. The replanning philosophy is surgical, not wholesale.

### **The Replanning Brief**

The Replanning Engine automatically constructs the replanning brief from the trigger data and the current Campaign state. The brief structure: the original Campaign goal and timeline, the current status and performance data, the specific trigger that caused this review (which trigger fired and what it found), the elements of the Campaign that appear to be working (to be preserved), and the specific hypothesis about what needs to change and why.

The hypothesis is the most important part of the replanning brief. A replanning session without a hypothesis is a fishing expedition — the agents are looking for any solution to an undefined problem. A replanning session with a hypothesis is efficient — the agents evaluate whether the hypothesis is correct, refine it if not, and develop a specific solution if yes.

Example hypothesis for a task miss trigger: 'The execution shortfall in Move 2 (Conversion) is primarily caused by the content approval requirement creating a bottleneck. The user is not approving content quickly enough before the publish window. The hypothesis is that either the content should be pre-generated and auto-approved for low-stakes content types, or the Move timeline should be extended by one week to allow the current approval cadence to continue.'

Example hypothesis for an intelligence trigger: 'CompetitorX's launch of a discount offer targeting the same ICP has created a price-competitive environment that the current Campaign's messaging does not address. The Campaign's current Move 3 (Conversion) uses feature-benefit messaging. The hypothesis is that adding a value-comparison message component to Move 3 would help counter the competitor's discount offer by demonstrating value at the current price point.'

### **The Replanning Session Agents**

The agents selected for a replanning session are determined by the trigger type and the Campaign's primary domain. Task miss triggers select: the Analytics Director (to provide the performance data analysis), the Strategist's orchestration, and one to two Campaign-relevant Council agents who can suggest tactical adjustments. Intelligence triggers select: the Market Research Lead (to brief on the competitive change), the Campaign-relevant Council agents who addressed the affected component of the strategy, and the Media Buyer if the change affects channel competition and cost. KPI deviation triggers select: the Analytics Director (primary), plus the agents who designed the underperforming Move, plus one counterpoint agent who might identify a non-obvious solution.

### **The Replanning Output**

The replanning session produces a structured output: a list of proposed changes to the Campaign structure, each with a change description, the strategic reasoning behind it, the expected impact on the Campaign's goal trajectory, and an urgency level (implement immediately, implement this week, implement at next Move transition).

The proposed changes are presented to the user through a Campaign Alert — a special type of notification that shows the changes, the reasoning, and options for how to respond. The user can: accept all changes (auto-applied), accept selected changes (user selects which changes to apply), modify changes (user adjusts a proposed change before applying), or reject and override (user disagrees with the analysis and maintains the current Campaign structure with a note explaining why).

If the user does not respond to the Campaign Alert within 48 hours, the Replanning Engine applies changes with urgency level 'implement immediately' automatically. Changes with 'implement this week' or 'implement at next Move transition' urgency are not applied until the user explicitly accepts them.

## **Chapter 4.3 — What Replanning Can and Cannot Change**

The replanning philosophy of minimal necessary change has specific implications for what kinds of changes the Replanning Engine will propose and what it will not propose.

Replanning CAN propose: adjusting the timeline of an existing Move (extending or shortening it), adjusting the daily task count within a Move (reducing if execution capacity is insufficient, adding if performance is running ahead of schedule), changing the channel mix within a Move (removing an underperforming channel, adding a channel that is showing unexpected opportunity), adjusting the content approach within a Move (modifying the messaging angle, the content format, or the creative direction), adding a new Move to the Campaign (typically adding a supplementary Move after the planned sequence), adjusting the ad budget allocation within the Campaign's approved budget envelope.

Replanning CANNOT propose: changing the Campaign's primary goal (that would require a new Campaign creation process), extending the Campaign beyond its original end_date without explicit user approval, creating a new Campaign (the Replanning Engine can only modify existing Campaigns), fundamentally restructuring all Moves (more than 50 percent changed constitutes a new Campaign, not a replan), or changing the target ICP (ICP changes represent a strategic pivot that requires user decision rather than autonomous adaptation).

These boundaries ensure that autonomous replanning enhances the Campaign without replacing the user's strategic judgment. The user retains control over the biggest decisions while the system handles the continuous operational adaptation that would otherwise require constant manual attention.

## **Chapter 4.4 — The Replanning and PRL Connection**

Every replanning event — trigger, session, proposed changes, user response — generates ripples in the PRL. These ripples are among the most strategically valuable in the system because they encode what happened when plans met reality, which is exactly the learning that makes future Campaign planning more accurate.

The ripples created by replanning events: a Level Two ripple recording what the trigger was and what specific data triggered it. A Level Three ripple recording the analysis that the replanning session produced — the hypothesis about why the trigger occurred and what it means for the Campaign strategy. A Level Four ripple recording the predictive implication — given what happened to this Campaign at this point, what does that predict about similar Campaigns in similar circumstances?

The Level Four replanning ripples are the most valuable for future Campaign planning. After several Campaign cycles, the Strategist's Level Four ripple stream contains specific predictive models: 'Conversion Moves launched in this industry category with this ICP tend to underperform their projections when the competitive environment includes active discount offers from category leaders. Conversion Move projections should be adjusted downward by 25 to 30 percent in this competitive context.' This is knowledge that no generic marketing framework captures but that emerges naturally from the specific experience of this system with this client.

# **Part Five: The Move System in Depth**

## **Chapter 5.1 — The Move as a Strategic Action**

A Move is more than a tactical plan. It is a strategic action — a deliberate intervention in the market that is designed to shift the Campaign's trajectory toward its goal. Understanding Moves at this level of abstraction is important because it shapes how the system evaluates Move success and how agents design Moves during Campaign planning.

Every Move has a theory of change: a statement of what the Move is trying to do, how it is trying to do it, and what evidence would indicate that the theory was right. The theory of change is encoded in the council_rationale JSONB field during Campaign planning. It is not just the operational plan — it is the strategic reasoning behind the plan, which is what the Replanning Engine uses to evaluate whether the plan should be maintained or adjusted.

When a Move's performance data arrives and is analyzed by the Analytics Director, the analysis is evaluated against the Move's theory of change. If the performance data is consistent with the theory — if the Move is achieving what the theory predicted it would achieve — the theory is confirmed and the Move's strategic approach is strengthened in the PRL. If the performance data is inconsistent with the theory — if the Move is failing to achieve what the theory predicted — the analysis must determine whether the theory was wrong or whether the execution was wrong. These require different responses.

A wrong theory — where the strategic approach was fundamentally mistaken — requires Move-level replanning to change the approach. A wrong execution — where the strategic approach is correct but implementation was flawed (poor content, wrong timing, insufficient budget) — requires tactical adjustment without strategic change. The Analytics Director's performance analysis and the Replanning Engine's hypothesis construction together navigate this distinction.

## **Chapter 5.2 — Move Sequencing and Dependencies**

Moves within a Campaign are not always independent. Some Moves create the conditions that subsequent Moves depend on. An awareness Move is supposed to build the audience that a conversion Move will then convert. A consideration Move is supposed to nurture the leads that a conversion Move will close. These dependencies affect how Moves should be evaluated and how the Replanning Engine handles Move-level failures.

Move dependencies are not explicitly stored as foreign keys in the database — that would be over-engineering for a system that currently handles a maximum of five to seven Moves per Campaign. Instead, dependencies are encoded in the council_rationale field as dependency_assumptions: a JSON array of statements about what this Move assumes has been achieved by preceding Moves. 'This Move assumes that the awareness campaign has established familiarity with the brand among at least 50,000 unique users in the target ICP segment.'

When the Analytics Director evaluates a Move's performance, it checks the dependency_assumptions of the current Move against the performance data of the preceding Move. If the preceding Move did not meet the level of achievement that the current Move assumes — if the awareness campaign only reached 30,000 users when the conversion Move assumes 50,000 — this is reported as a dependency shortfall in the Replanning Engine's evaluation context. The Replanning Engine can then propose extending the awareness Move, adjusting the conversion Move's projections, or launching a supplementary awareness effort in parallel with the conversion Move.

## **Chapter 5.3 — Move Completion and Transition**

A Move transitions from active to completed when one of three conditions is met: all tasks in the Move have reached a terminal status (completed, missed, or overridden), the Move's end_date has been reached regardless of task completion, or the Move's completion_criteria have been fully met before the end_date (early completion).

Early completion is the most positive outcome and should be celebrated in the interface. When a Move completes its criteria ahead of schedule, the user sees a celebration indicator — a subtle animation in the Campaign view and a congratulatory message from the Strategist in the Muse interface. The Strategist also evaluates whether the remaining time before the next Move's scheduled start can be productively used, and if so, proposes an acceleration of the Campaign timeline.

End-date completion — reaching the end_date with tasks completed but completion criteria not fully met — is the most common outcome. The Analytics Director evaluates what was achieved relative to criteria and presents a Move retrospective: what worked, what fell short, what the implications are for the next Move. The retrospective is stored as a Level Three ripple in the relevant agents' PRL streams.

Failed completion — reaching the end_date with significant task misses and significantly unmet criteria — triggers a deeper analysis. The Replanning Engine evaluates whether the Campaign goal is still achievable with the remaining Moves, whether the failed Move's strategy should be partially repeated in a modified form, or whether the Campaign's goal needs to be revised downward based on what the Move's failure has revealed about the achievability of the original target.

## **Chapter 5.4 — The Move Retrospective**

At the conclusion of every Move — regardless of whether it completed successfully, partially, or with significant shortfalls — the Analytics Director generates a Move retrospective. The retrospective is a structured analysis that closes the learning loop from the Move's execution back to the agents who designed it and to the PRL that will inform future Campaign planning.

The retrospective structure: performance summary (what the Move achieved against its completion_criteria), execution summary (task completion rate, content approval rate, any significant missed tasks), key insights (what the performance data suggests about the audience's response to the Move's approach, what channel performed best, what content format generated the most engagement), and forward implications (what this Move's outcomes predict about the next Move's approach and the overall Campaign's trajectory).

The retrospective is delivered to the user as a structured report in the Campaign view. It is also processed by the Event Harvester to create PRL ripples for all agents involved in this Move's design. The agents who designed the Move's approach receive private ripples that update their accuracy models for predicting Move performance in this context. These ripples become the training data for improved predictions in future Campaign planning sessions.

# **Part Six: How Campaigns Connect to the Rest of the System**

## **Chapter 6.1 — Campaigns and the Intelligence Pipeline**

The intelligence pipeline does not just monitor competitors for general awareness — it monitors them in the specific context of active Campaigns. When a competitive change is detected, the first evaluation it receives is Campaign-contextual: which active Campaigns does this change affect, and how?

This Campaign-contextual evaluation requires the intelligence pipeline to know what each active Campaign is trying to achieve, what channels it is using, what ICP it is targeting, and what messaging it is deploying. All of this is available through the Campaign data model and is loaded into the intelligence evaluation context when the pipeline processes each competitive signal.

The result is competitive intelligence that is already pre-filtered and pre-analyzed for Campaign relevance before it reaches the user. The user does not see a raw feed of everything competitors are doing — they see a curated selection of competitive signals that matter for the specific campaigns they are currently running. This curation is what makes the intelligence useful rather than overwhelming.

The Campaign-intelligence connection also runs in reverse: Campaign performance data that differs significantly from projections triggers an intelligence review. When a conversion Move is underperforming, the Replanning Engine does not only look at the Move's execution data — it also checks the intelligence pipeline for any competitive changes in the relevant channel and ICP that might explain the underperformance. The intelligence and campaign systems are designed as a coherent analytical whole, not as independent features.

## **Chapter 6.2 — Campaigns and the PRL**

The relationship between Campaigns and the PRL is bidirectional. Campaigns generate ripples — from the brief evaluation, from Council planning sessions, from Move execution events, from performance data, from replanning sessions. These ripples accumulate in the agents' private and shared_campaign streams and inform every subsequent decision about this Campaign.

The PRL also shapes Campaigns. When the Context Assembler builds the ContextPack for a Campaign planning session, it retrieves ripples from previous Campaign planning sessions for this client. These ripples contain the accumulated knowledge about what types of Campaigns have worked for this client, what Move sequences have produced the best outcomes, what content approaches have resonated with this ICP, and what competitive conditions have historically required strategy adjustments. The Council planning the new Campaign is not starting from scratch — they are starting from a PRL-informed understanding of what has worked before.

This learning from Campaign to Campaign is one of the most significant value drivers of the system. A client's first Campaign will be planned from Foundation context and general agent expertise. Their fifth Campaign will be planned from Foundation context, general expertise, and four Campaigns worth of accumulated specific knowledge. Their twentieth Campaign will be planned with an understanding of their market, their ICP, and their competitive environment that has been tested and refined over twenty cycles of execution, measurement, and adaptation. The Campaigns get better. Not because the agents get smarter in general — because they get smarter about this specific client.

## **Chapter 6.3 — Campaigns and Muse**

Muse is spatially aware of the Campaign context. When a user opens Muse while viewing a Campaign, the current Campaign's context is the primary frame through which Muse interprets the conversation. This spatial awareness means that Muse can answer campaign-specific questions without requiring the user to explain what campaign they are asking about.

The Muse-Campaign integration enables several types of high-value interaction. Campaign status questions: 'How is the spring launch campaign doing?' — Muse answers with the current performance data, the Analytics Director's assessment, and the Strategist's recommended next action. Campaign-specific content requests: 'Give me five alternative headline options for tomorrow's ad' — Muse generates the alternatives within the specific context of the Move the user is currently in, with the brand voice and ICP constraints from the Foundation, without requiring the user to specify any of this context.

Campaign decision support: 'Should I pause Move 2 and move straight to Move 3?' — Muse routes this to the Strategist and relevant agents, who evaluate the decision against the Campaign's theory of change, the current performance data, and any relevant PRL ripples from previous similar decisions. The response is a specific recommendation with reasoning, not a generic answer about campaign management theory.

The Muse-Campaign integration also enables proactive Muse behavior. When the Strategist's autonomous monitoring identifies something worth the user's attention — a pending decision point, an upcoming high-priority task, a performance trend worth noting — Muse surfaces it at the appropriate moment in the user's workflow rather than waiting for the user to ask.

## **Chapter 6.4 — Campaigns and the Office**

The Office visualization reflects Campaign activity in ways that make the Campaign feel real and the agents feel invested. When a Campaign is in active execution, the open plan area shows visible activity: the agents assigned to current Move tasks are at their desks working, their workstations show content-in-progress, their interns are carrying research materials between desks.

When a replanning session is triggered, the corresponding office animation fires: the Strategist receives a notification (the performance monitor on the corner office desk flashes), the Strategist calls a focused meeting (not a full conference room assembly — a round table meeting with the specific agents involved in the replanning), and the meeting runs visibly through the glass walls for the duration of the replanning session.

When a Move completes, the completion is celebrated in the Office: the relevant agents receive a brief moment of visible satisfaction — Ogilvy setting down his pen and leaning back, Patel checking his phone and nodding, Vaynerchuk briefly standing and appearing pleased. The Office celebrations are brief — 15 to 20 seconds — and understated, because the 1980s corporate environment is not given to theatrical celebration. But they are present, and they make the Campaign's milestones feel earned rather than just logged.

When a task is missed, the Office shows a different animation: the Strategist's performance monitor flashes, Maya receives a message and walks to the Strategist's office, the Strategist has a brief quiet meeting with the relevant agent about the miss. No drama. No visible reprimand. Just the quiet acknowledgment that something did not happen as planned and the office is aware of it. This understated treatment of failures reflects the professional culture the Office is designed to embody.

# **Part Seven: The Campaign Database — Complete Schema**

## **Chapter 7.1 — Additional Supporting Tables**

Beyond the four primary tables (campaigns, campaign_moves, campaign_tasks, generated_content), several supporting tables are required for the complete Campaign system.

CREATE TABLE campaign_briefs (

brief_id TEXT PRIMARY KEY,

org_id UUID NOT NULL,

campaign_id TEXT REFERENCES campaigns(campaign_id),

status TEXT NOT NULL DEFAULT 'submitted',

original_text TEXT NOT NULL,

structured_data JSONB NOT NULL,

evaluation_result JSONB,

clarification_history JSONB,

created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

);

The campaign_briefs table preserves the complete brief submission and evaluation history. This allows the Strategist's evaluation to be reviewed if the user disagrees with a rejection, and allows the PRL to learn from brief quality patterns over time. The clarification_history field is a JSON array of {question: string, answer: string, timestamp: timestamp} objects that records the complete clarification dialogue for each brief.

CREATE TABLE replan_sessions (

replan_id TEXT PRIMARY KEY,

campaign_id TEXT NOT NULL REFERENCES campaigns(campaign_id),

org_id UUID NOT NULL,

trigger_type TEXT NOT NULL,

trigger_data JSONB NOT NULL,

hypothesis TEXT NOT NULL,

participating_agents TEXT\[\] NOT NULL,

proposed_changes JSONB NOT NULL,

user_response TEXT,

applied_changes JSONB,

created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

resolved_at TIMESTAMPTZ

);

The replan_sessions table records every replanning session — its trigger, the hypothesis, the proposed changes, how the user responded, and what was actually applied. This history is invaluable for auditing the system's autonomous behavior and for the PRL's learning about what types of replanning recommendations users accept and which they reject.

CREATE TABLE campaign_performance_log (

log_id TEXT PRIMARY KEY,

campaign_id TEXT NOT NULL REFERENCES campaigns(campaign_id),

move_id TEXT REFERENCES campaign_moves(move_id),

org_id UUID NOT NULL,

metric_name TEXT NOT NULL,

metric_value FLOAT NOT NULL,

data_source TEXT NOT NULL,

recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

);

The campaign_performance_log provides a time-series record of all performance metrics for all campaigns. This table is the primary data source for the Analytics Director's trend analysis and trajectory projection, for the KPI deviation trigger evaluation, and for the PRL ripples that encode performance learning.

## **Chapter 7.2 — Indexes for Query Performance**

The Campaign tables require careful indexing to support the query patterns of the Replanning Engine, the Analytics Director's monitoring, and the user-facing Campaign views.

Critical indexes: on campaigns for the daily active campaign scan — composite index on (org_id, status) where status = 'active'; on campaign_moves for Move ordering within a Campaign — composite index on (campaign_id, sequence_number); on campaign_tasks for the daily task list generation — composite index on (org_id, scheduled_date, status); on campaign_tasks for the miss detection job — composite index on (org_id, status, scheduled_date) where status = 'due' or status = 'ready_for_review'; on generated_content for content retrieval by task — index on task_id where content_id is not null; on campaign_performance_log for time-series queries — composite index on (campaign_id, metric_name, recorded_at DESC).

All Campaign tables have RLS enabled with the same org_id policy as all other RaptorFlow tables. The Campaign tables do not need agent-level isolation — campaign data is shared across all agents — but they do need tenant isolation.

# **Part Eight: The Moves System — Specific Logic for Each Move Type**

## **Chapter 8.1 — The Awareness Move**

The Awareness Move is typically the first Move in any Campaign that is targeting customers who are not already familiar with the brand. Its goal is to build reach and familiarity — to get the brand in front of the maximum number of qualified potential customers and leave a positive impression.

Awareness Moves are evaluated on reach metrics rather than conversion metrics. The completion_criteria for an awareness Move: minimum reach (unique people reached), minimum frequency (average impressions per reached person), and a brand sentiment indicator where available. The Analytics Director does not evaluate an awareness Move on conversion rate — that would be measuring the wrong thing. Awareness Moves that succeed create the conditions for subsequent Moves to succeed; they do not generate conversions directly.

Content for Awareness Moves: brand story content (Draper's domain), value proposition content (Ogilvy's domain), social proof content (Cialdini's domain — testimonials and social proof signals that establish credibility). The content should be reach-optimized — designed for the format the platform algorithm distributes most widely, at the posting time that generates the most impressions per rupee of spend.

The Replanning Engine's intervention logic for Awareness Moves: if reach is below 60 percent of target after 50 percent of the Move's timeline, evaluate whether budget increase would solve the problem (likely if the content is performing well in terms of engagement rate) or whether the content approach is wrong (if the engagement rate is also low). Recommend accordingly.

## **Chapter 8.2 — The Consideration Move**

The Consideration Move targets people who are aware of the brand and are in the process of evaluating it against alternatives. The goal is to provide the information, social proof, and differentiation arguments that help the potential customer conclude that this brand is the right choice.

Consideration Moves are evaluated on engagement depth metrics — the length of content interactions, the percentage of video content viewed to completion, click-through rates to deeper content, email open rates and read times. These metrics indicate that potential customers are spending meaningful time with the brand's content rather than merely seeing it.

Content for Consideration Moves: in-depth product or service explanations (Ogilvy's domain), comparison content (Ries's domain — positioning against alternatives), case study and testimonial content (Cialdini's domain), FAQ and objection-handling content (Hopkins's domain — direct response to the specific objections that prevent conversion), and educational content that demonstrates expertise (Godin's domain — content that serves the audience genuinely rather than selling to them).

The Consideration Move has the strongest dependency on preceding awareness activity. When the Replanning Engine evaluates a Consideration Move that is underperforming, the first check is whether the preceding Awareness Move met its dependency assumptions. Consideration Move underperformance that is caused by insufficient awareness should be addressed by awareness amplification, not by changing the consideration content.

## **Chapter 8.3 — The Conversion Move**

The Conversion Move targets people who are aware of and interested in the brand and are ready to make a purchase decision. The goal is to make the conversion as easy and compelling as possible — removing friction, creating urgency where genuine, and providing the final confidence boost that converts consideration into action.

Conversion Moves are evaluated on the most direct business metrics: conversion rate, cost per conversion, and return on ad spend. The Analytics Director tracks these against the completion_criteria and the baseline established in the Campaign planning session.

Content for Conversion Moves: direct response copy (Hopkins's primary domain — specific offers, specific calls to action, specific urgency where genuine), social proof aggregation (Cialdini's domain — at the conversion stage, aggregating the most compelling proof that others have already made this decision), scarcity and urgency elements (Cialdini's domain — genuine scarcity communicated clearly, not manufactured urgency), and simplified decision framing (Sutherland's domain — making the decision feel psychologically easy rather than risky).

The Conversion Move is the most sensitive to competitive activity. When CompetitorX launches a discount offer during an active Conversion Move, the intelligence trigger is most likely to evaluate to a significant impact level, because the competitor is directly competing for the same purchase decisions at the same moment. The Replanning Engine's hypothesis for intelligence-triggered replanning during a Conversion Move typically involves adding value-demonstration content that justifies the current price point relative to the competitor's offer.

## **Chapter 8.4 — The Retention Move**

The Retention Move targets existing customers rather than new prospects. Its goal is to reduce churn, deepen engagement, and create the conditions for repeat purchase and referral. Retention Moves are fundamentally different from acquisition Moves in their content approach, their success metrics, and their agent assignments.

Retention Moves are evaluated on retention metrics: churn rate reduction, repeat purchase rate, customer satisfaction indicators, and referral activity. These metrics are typically measured over longer periods than acquisition metrics — retention effects take weeks to months to fully manifest, which requires the Campaign timeline to be set appropriately.

Content for Retention Moves: customer success content (demonstrating ongoing value — Godin's domain, focused on tribe membership and ongoing belonging), product education content (helping customers get more value from what they have purchased — Hopkins's domain, focused on the specific features and use cases they may not be using), community building content (Godin's domain — creating connections between customers, not just between the brand and individual customers), and appreciation content (acknowledging customer loyalty — Draper's domain, using narrative and emotional connection to strengthen the relationship).

## **Chapter 8.5 — The Launch Move**

The Launch Move is a special category designed for the introduction of something new — a new product, a new service, a new offering, or a significant update to an existing one. Launch Moves combine elements of awareness, consideration, and conversion into a coordinated sequence that is more compressed and more concentrated than a standard multi-Move Campaign.

Launch Moves have a specific pre-launch phase that is distinct from the standard Move execution flow. The pre-launch phase runs for one to two weeks before the launch date and generates teaser content, builds anticipation through social media signaling, and prepares the customer base for the launch announcement. The pre-launch phase is not a separate Move — it is a special phase of the Launch Move with its own set of tasks.

Launch Moves require the most intensive Council session of any Move type, because they combine strategic breadth (awareness, positioning, conversion, and sometimes PR) with operational complexity (coordinating multiple content types across multiple channels for a compressed timeline). War Room Council sessions are appropriate for major product launches. The Council's coordination in a Launch Move planning session is the most visible demonstration of the system's value for a complex real-world marketing challenge.

# **Part Nine: Edge Cases and Failure Modes**

## **Chapter 9.1 — Campaign With No Performance Data**

In the early days of a new Campaign, performance data is sparse or absent. The Analytics Director cannot make meaningful trajectory assessments, and the Replanning Engine cannot evaluate KPI deviation. The system must handle this period gracefully without false alarms.

The early-campaign period is defined as the first 20 percent of the Campaign timeline or the first seven days, whichever is shorter. During this period, the KPI deviation trigger is suppressed — no replanning sessions are triggered based on performance data alone. The task miss trigger and intelligence trigger continue to operate normally, because these do not depend on performance data.

After the early-campaign period ends, performance data begins to inform the trajectory assessment. The Analytics Director applies confidence-weighted projections: projections based on sparse data carry explicit uncertainty ranges that are wider than projections based on fuller datasets. The Replanning Engine respects these uncertainty ranges — it does not trigger replanning for a deviation that falls within the projection's uncertainty range.

## **Chapter 9.2 — Conflicting Intelligence and Performance Signals**

Sometimes the intelligence pipeline and the performance data send conflicting signals. The intelligence pipeline might show a competitor increasing ad spend significantly in the Campaign's target channel (a threat signal), while the Campaign's performance data is tracking above projection (a positive signal). Which signal should the Replanning Engine prioritize?

The resolution principle: performance data reflects what is currently happening; intelligence data predicts what is about to happen. When they conflict, the Replanning Engine generates an Informational Nudge rather than a replanning session — presenting both signals to the user and offering the Strategist's assessment of how they reconcile. 'Your current performance is ahead of target, which is excellent. However, CompetitorX has significantly increased their ad spend in the same channel. This may create competitive pressure on reach and cost in the coming weeks. We recommend monitoring closely for the next three days before adjusting the Campaign approach.' The user is informed and can make an active decision rather than having the system choose autonomously in an ambiguous situation.

## **Chapter 9.3 — User Foundation Changes During Active Campaigns**

When the user updates their Foundation while a Campaign is running, the update creates potential inconsistency between the Campaign's strategy (designed with the old Foundation) and the new Foundation values. The system must identify and flag these inconsistencies.

Foundation change impact assessment: when a Foundation update is saved, a background job runs a consistency check against all active Campaigns. The check identifies: any Campaign that references the changed Foundation element in its strategy (stored in council_rationale), any content pre-generation jobs that used the old Foundation values (in generated_content where approved_at is null), and any pending tasks whose approach was based on the changed element.

For each identified inconsistency, a Campaign Alert is generated. The Alert describes which Campaign element was based on the old Foundation value and what needs to be reviewed or regenerated. Pre-generated but unapproved content is automatically flagged for review — the user is told that this content was generated with the previous Foundation values and should be regenerated or reviewed carefully before approval. The Campaign's strategic rationale notes are updated to reflect the Foundation change and its potential implications.