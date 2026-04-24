# RAPTORFLOW MASTER DOCUMENT SERIES
## Volume 9: Muse, the Content Engine, Competitive Intelligence, Daily Wins, and Nudges

---

# Opening: The Features That Create Daily Habit

Campaigns create the strategic structure. The features in this volume create the daily habit. A user who comes back every morning to read their Daily Wins briefing, who opens Muse when they have a marketing question, who uses the Content Engine when they need something written, who checks the Intel dashboard when they hear a competitor mentioned — this user is churning at close to zero. Not because the product has locked them in, but because it has become genuinely useful in the texture of their daily work.

This volume documents five features that together constitute the daily product experience: Muse (the thinking partner), the Content Engine (the generation system), Competitive Intelligence (the monitoring pipeline), Daily Wins (the morning briefing), and Nudges (the proactive alert system). Each is documented at the same level of granularity as previous volumes — every data model, every logic path, every connection to the PRL and agent system, every edge case.

---

# Part One: Muse — The Context-Aware Thinking Partner

## Chapter 1.1 — What Muse Is at Its Core

Muse is not a chatbot with marketing knowledge. The distinction matters and must be understood before any implementation decision is made. A chatbot with marketing knowledge answers marketing questions from a static knowledge base. Muse assembles a complete understanding of the user's specific situation — their business, their active campaigns, their recent conversations, their competitive environment, their current performance — and provides guidance that is specific to that situation rather than generically correct.

The mechanism of this specificity is the spatial awareness system. Muse knows where the user is in the product at the moment they invoke it. Not metaphorically — literally. When a user clicks the Muse icon while viewing Day 3 of Move 2 of their Spring Launch Campaign, Muse knows that is where they are. The day, the Move, the Campaign, the task they were looking at — all of this is in the Muse context before the user types a single word. The response to 'help me with today's content' is therefore specific to the exact piece of content due today in the exact Move they were viewing, with the exact brand voice and ICP constraints from their Foundation, without the user having to specify any of that.

## Chapter 1.2 — The Spatial Awareness Stack

The Muse spatial awareness stack has seven layers, assembled in order from most to least specific:

**Layer 1 — Current Screen Context:** What page, tab, campaign, move, day, or task is the user currently viewing? This is captured from the frontend state at the moment Muse is invoked. The current screen context is the primary frame for interpreting any ambiguous request.

**Layer 2 — Active Work Context:** What active campaigns exist? Which ones are in execution? Which tasks are due today or overdue? Which content is pending approval? This layer answers 'what is happening right now in my marketing operation.'

**Layer 3 — Temporal Context:** What day is it? What happened yesterday? What is scheduled for the next seven days? This layer gives Muse the ability to connect the current moment to the recent past and near future without the user having to explain the timeline.

**Layer 4 — Performance Context:** How are active campaigns performing? Are there metrics that are significantly above or below projection? This layer is assembled by querying the campaign_performance_log for the most recent data points across all active campaigns.

**Layer 5 — Intelligence Context:** What has the competitive intelligence pipeline detected recently? Are there any pending intel alerts? This layer ensures that Muse's advice is informed by the current competitive landscape rather than a static view of the market.

**Layer 6 — Foundation Context:** The complete Foundation JSON — positioning, ICP, competitors, brand voice, goals, channels. This layer is always present and is cached via Vertex AI context caching.

**Layer 7 — Pattern Context:** What has the user asked about repeatedly? What working style patterns has the Muse memory system detected? What preferences has the user expressed in past conversations? This layer personalises the response style and proactively surfaces relevant patterns.

The complete context assembly for a Muse invocation takes under 200 milliseconds. The Foundation layer is cached. Layers 1-3 are assembled from the frontend state and the campaign tables (fast database queries). Layers 4-5 query the performance log and intelligence tables (slightly slower). Layer 7 retrieves pattern ripples from the PRL (CORTEX retrieval, under 10ms).

## Chapter 1.3 — The Muse Routing Logic

Every Muse message is routed to the appropriate agent tier based on what the message requires. The routing is assessed by a lightweight classifier that runs before the main inference call.

**Route 1 — Direct Muse Response (Strategist, Flash-Lite Reasoning):**
The Strategist handles conversational Muse responses for strategic and tactical questions that do not require Council deliberation. Used for: 'how is my campaign doing', 'should I post today or tomorrow', 'what does this performance data mean', 'give me five headline options for this task'. The Strategist's response is informed by the full spatial awareness context and the Strategist's accumulated PRL knowledge of this client.

**Route 2 — Content Generation (Assigned Avatar, Flash-Lite Normal):**
When the Muse request is primarily a content generation request — 'write me a caption for today's post', 'give me ad copy for this product', 'draft an email for this campaign' — the request is routed to the appropriate avatar based on content type. Ogilvy for ad copy and long-form. Vaynerchuk for social captions. Draper for email narratives. The avatar's skill weave and the client's accumulated content performance data inform the generation.

**Route 3 — Mini-Council (2-3 agents, Flash-Lite Reasoning):**
For questions that genuinely benefit from multiple expert perspectives but do not warrant a full Council session — 'should I use Meta or LinkedIn for this campaign', 'is my pricing strategy limiting my conversion rate', 'how should I position against this new competitor' — the router convenes a mini-Council with the 2-3 most relevant avatars. The mini-Council follows the same fan-out pattern as a standard Council session but runs faster due to the reduced agent count.

**Route 4 — Analytics Director (Flash-Lite Normal):**
For data interpretation questions — 'why is my CTR dropping', 'what does this engagement rate mean', 'is this A/B test result statistically significant' — the request is routed to the Analytics Director, who has the performance data context and the analytical framework to give a specific, evidence-backed answer.

## Chapter 1.4 — The Conversation Data Model

```sql
CREATE TABLE muse_conversations (
  conversation_id    TEXT PRIMARY KEY,
  org_id             UUID NOT NULL,
  user_id            UUID NOT NULL,
  title              TEXT,
  context_snapshot   JSONB,
  message_count      INTEGER NOT NULL DEFAULT 0,
  last_message_at    TIMESTAMPTZ,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE muse_messages (
  message_id         TEXT PRIMARY KEY,
  conversation_id    TEXT NOT NULL REFERENCES muse_conversations(conversation_id),
  org_id             UUID NOT NULL,
  role               TEXT NOT NULL,
  content            TEXT NOT NULL,
  token_count        INTEGER,
  model_used         TEXT,
  routing_decision   TEXT,
  responding_agent   TEXT,
  spatial_context    JSONB,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

The context_snapshot field in muse_conversations stores a snapshot of the spatial awareness context at the time the conversation was started. This allows the conversation history to be interpreted correctly even if the user's context has changed since the conversation began.

The spatial_context field in muse_messages stores the specific screen context at the time each message was sent. Different messages in the same conversation may have different spatial contexts if the user navigated between messages.

## Chapter 1.5 — The Muse Memory System

The Muse memory system operates on two timescales: within-conversation memory (the conversation history in the context window) and cross-conversation memory (the PRL ripples created from conversation patterns).

**Within-conversation memory:** All messages in the current conversation are included in the generation context, up to the model's context window limit. When a conversation grows long enough to approach the context window limit, a progressive summarisation is applied: older messages are replaced with a rolling summary that preserves the key decisions, preferences expressed, and insights developed, while removing the specific back-and-forth that led to them.

**Cross-conversation memory:** The Muse pattern analysis job runs nightly and analyses the accumulated conversation history for each user. It extracts: recurring topics (what does this user keep asking about?), preference signals (how do they prefer to receive answers — detailed or brief, data-backed or principle-based?), knowledge gaps (what concepts do they repeatedly ask about?), and business changes (new information about the business mentioned in conversation that might warrant Foundation updates).

These patterns are stored as user_preference and semantic ripples in the Strategist's private PRL stream and are injected into the Muse context at session initialization. A user who consistently asks for bullet-point summaries rather than prose explanations will find that Muse defaults to bullet points without being asked. A user who keeps asking about their Instagram strategy will find that the Strategist proactively surfaces Instagram-relevant insights.

## Chapter 1.6 — Muse and the Foundation Update Loop

One of the most valuable Muse functions is detecting Foundation drift — situations where the user's current business reality has diverged from what the Foundation documents. Muse conversations are a rich source of this drift detection because users naturally describe what is happening in their business when asking for advice.

When the Muse pattern analysis detects a Foundation drift signal — a new product mentioned that is not in the Foundation, a change in primary ICP referenced repeatedly, a new competitor named multiple times — it generates a Foundation Update Nudge: 'In your recent conversations, you have mentioned [new product/change] several times. Would you like to add this to your Foundation so your agents can plan campaigns for it?'

The user can accept the nudge (which opens the relevant Foundation screen pre-filled with the extracted information), dismiss it, or ask Muse to discuss it further. This creates a feedback loop where Muse conversations continuously improve the Foundation quality without requiring the user to consciously manage it.

---

# Part Two: The Content Engine

## Chapter 2.1 — Content Architecture

The Content Engine generates five types of content: ad copy, social posts, blog and long-form, email copy, and content calendars. Each type has a distinct generation pipeline, a distinct avatar assignment, and distinct quality evaluation criteria.

All content generation follows the same seven-step pipeline regardless of type:

1. **Foundation context assembly** — brand voice profile, positioning statement, relevant ICP, competitors, content territories
2. **Campaign context assembly** — if this content is for a specific campaign, the Move strategy, the task context, the completion criteria
3. **Avatar context assembly** — the assigned avatar's ContextPack from the PRL/EEL
4. **Generation call** — the appropriate Flash-Lite model with the full context
5. **Brand voice compliance check** — automated scoring against the voice fingerprint
6. **Variant generation** — for content types where variants add value (headlines, CTAs)
7. **Storage** — in the generated_content table with all metadata

## Chapter 2.2 — Ad Copy Generation

Ad copy generation is the highest-frequency content type and the one most directly connected to measurable commercial outcomes. The quality of ad copy determines click-through rates, which determines how efficiently the user's ad budget translates into business results.

**The primary generating avatars for ad copy:**
- Ogilvy: the primary generator for all ad copy. His research-backed, benefit-specific, headline-focused approach produces copy that is both creatively strong and performance-tested in principle.
- Hopkins: co-generator, provides the direct response angle and the specific offer framing. His contribution typically appears in the CTA and the body copy structure.
- Bernbach: consulted for creative differentiation — when the copy needs to break through by being genuinely surprising rather than just clear and compelling.

**The ad copy generation context** includes: the specific product or service being advertised, the ICP being targeted (pulled from Foundation, may be overridden for campaign-specific targeting), the campaign objective (awareness / consideration / conversion), the platform (Meta, Google, LinkedIn), the format (single image, carousel, video, search), character limits for the platform and format, the brand voice profile, and the competitive differentiation points from the Foundation.

**Variant generation:** All ad copy is generated with variants. Headlines: 5-7 variants ranging from benefit-focused to curiosity-driven to social proof-led. Primary text: 2-3 variants at different lengths and emotional registers. CTA: 3-5 options. The variants are scored against each other by the QA Director's compliance check and the top performers are surfaced to the user.

**Performance feedback loop:** When ad performance data becomes available — CTR, conversion rate, ROAS — it is logged to campaign_performance_log and associated with the specific generated_content record through the task relationship. The Analytics Director's monitoring surfaces this data as a PRL ripple in Ogilvy's private stream. After 20+ ad copy evaluations, Ogilvy's skill in ad copy for this specific client has been calibrated to what actually performs, not just what principle predicts will perform.

## Chapter 2.3 — Social Post Generation

Social post generation runs on a higher volume but lower stakes basis than ad copy. The typical user generates 15-25 social posts per month across all active campaigns and organic content.

**Platform-specific generation:** Each social platform has distinct format requirements that are enforced at the generation level. Instagram captions: 150-300 words, emoji usage calibrated to brand voice personality score on the formal-casual dimension (formal brands get minimal emoji, casual brands get moderate emoji), 5-10 hashtags in the first comment rather than the caption. LinkedIn posts: 150-1,200 words depending on the content type, no emoji unless brand voice is casual, professional framing, clear point of view. Twitter/X: under 280 characters for the primary post, thread structure for longer content.

**The content calendar generation path:** When the user requests a content calendar rather than individual posts, the Content Engine generates a week or month's worth of posts in a single operation. The calendar generation respects: the content territories from the Foundation, the posting frequency recommended for each channel based on the user's current activity level and target channels, the variety principle (no more than two posts of the same content type in any five-day period), and the campaign context (campaign-specific content is woven into the calendar alongside non-campaign content).

**Posting time recommendations:** For each generated post, the Content Engine includes a posting time recommendation. This recommendation is generated by Patel's intern, who queries the platform timing data available from the intelligence pipeline's social monitoring. The recommendation is not a generic best practice — it is derived from the actual engagement patterns of the user's audience on their specific account.

## Chapter 2.4 — Blog and Long-Form Generation

Blog and long-form content generation is the highest-investment content type in terms of generation cost and editing effort. A blog post generated by the Content Engine is a genuine first draft — 800 to 2,500 words, with proper structure, researched claims where applicable, and SEO considerations integrated — not a short summary or an outline.

**Avatar assignment for long-form:**
- Ogilvy: research-backed articles, opinion pieces with strong evidence, industry analysis pieces. His long-form copy structure skill produces well-argued, clearly structured articles.
- Draper: brand story pieces, founder narrative content, emotional connection content. His narrative sensibility produces long-form that reads like a story rather than an argument.
- Godin: thought leadership and perspective pieces, content that challenges conventional wisdom in the industry. His reframing approach creates long-form that generates genuine reader engagement.

**The SEO integration:** Blog posts are generated with keyword awareness from the Foundation's keyword list (Screen 16 of onboarding). The primary keyword for the post is identified from the request context and incorporated into the title, the first paragraph, and naturally throughout the body. The QA Director's compliance check includes a basic keyword density review — not over-optimised (which the Google algorithm penalises) but consistently present.

**Long-form generation cost:** A 1,500-word blog post generation call uses approximately 500 input tokens (context) and 2,000 output tokens (content). At Flash-Lite Normal pricing, this is approximately $0.00095 per post — under one cent per blog draft. The real cost is the 30-60 seconds of editing the user invests to refine the draft to their satisfaction.

## Chapter 2.5 — Brand Voice Compliance

The brand voice compliance system is the quality gate between content generation and content delivery. Every piece of generated content passes through it before being presented to the user.

**The two-step compliance check:**

Step 1 — Structural compliance (pure logic, no inference): Does the content violate any hard rules in the Foundation? Forbidden phrases present? Character limits exceeded? Competitor names used inappropriately? Platform format violated? This check runs in milliseconds with no inference cost.

Step 2 — Semantic compliance (Flash-Lite Normal): The generated content is embedded and compared against the voice fingerprint — the vector embedding of the brand voice profile from the Foundation. Cosine similarity between the content embedding and the voice fingerprint is the compliance score. Score above 0.80: passes. Score 0.60-0.80: passes with a soft warning flag visible in the UI. Score below 0.60: auto-revision triggered.

**Auto-revision:** When compliance score is below 0.60, the Content Engine does not show the failing content to the user. Instead, it generates a revised version with the compliance score explicitly incorporated into the generation prompt: 'The previous version scored 0.54 on brand voice compliance. The brand voice requires [specific characteristics from the failing dimensions]. Rewrite with stronger adherence to these characteristics.' The revised version is shown to the user instead. If the revised version also fails (rare), both are shown with compliance scores so the user can decide.

---

# Part Three: Competitive Intelligence — The Monitoring Pipeline

## Chapter 3.1 — Architecture Overview

The intelligence pipeline is the system's continuous window into the competitive environment. It runs four monitoring subsystems entirely on custom Rust infrastructure with no third-party API costs: website change detection, social media monitoring, ad library tracking, and SEO/SERP monitoring.

All four subsystems share a common infrastructure: a pool of chromiumoxide (headless Chrome) instances managed by the browser pool module, a reqwest HTTP client for lightweight requests, the governor rate limiting crate for polite scraping, and the scraper crate for HTML parsing. All scraping logic is in the `src/intelligence/` directory of the Rust backend.

**Anti-detection configuration for chromiumoxide instances:**
- Randomized user agent strings rotating across Windows, macOS, and Linux browser profiles
- Consistent fingerprint within each session (same GPU renderer string, same memory size, same screen resolution)
- Physics-based mouse movement simulation for interactive pages (not linear, has acceleration curves)
- Human-like timing: 200-800ms random delays between actions
- IP rotation through a proxy pool (using the governor crate for rate limiting per proxy)
- Per-competitor rate limiting: maximum 1 request per 5 minutes per competitor domain

## Chapter 3.2 — Website Change Detection

**Schedule:** Every 24 hours per competitor, staggered so all competitors are not scanned simultaneously.

**The scan process:**

1. Fetch the competitor's key pages using reqwest (not headless browser for static pages — faster and cheaper). Key pages: homepage, /pricing, /product or /services, /about. For pages that require JavaScript rendering, chromiumoxide is used.

2. Extract the meaningful text content from each page using the scraper crate. Boilerplate is stripped: navigation menus, footer content, cookie notices, generic legal text. Only content-bearing sections are retained.

3. Compute a content hash of the extracted text using SHA-256. Compare against the stored hash in competitor_snapshots.

4. If the hash has changed: compute a text diff using the Myers algorithm. Classify the change type using a Flash-Lite Normal inference call with the diff as input. Classification output: {change_type: 'pricing' | 'messaging' | 'feature' | 'positioning' | 'team' | 'design' | 'other', significance: 'minor' | 'moderate' | 'major', summary: string, affected_campaigns: array of campaign IDs that reference this competitor}.

5. Store the new snapshot in competitor_snapshots. Store the diff and classification in competitor_diffs. If significance is 'major', generate an intelligence alert and evaluate against active campaigns for replanning relevance.

**Data model:**
```sql
CREATE TABLE competitor_snapshots (
  snapshot_id        TEXT PRIMARY KEY,
  competitor_id      UUID NOT NULL,
  org_id             UUID NOT NULL,
  page_url           TEXT NOT NULL,
  content_hash       TEXT NOT NULL,
  extracted_text     TEXT NOT NULL,
  snapshot_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE competitor_diffs (
  diff_id            TEXT PRIMARY KEY,
  competitor_id      UUID NOT NULL,
  org_id             UUID NOT NULL,
  page_url           TEXT NOT NULL,
  change_type        TEXT NOT NULL,
  significance       TEXT NOT NULL,
  summary            TEXT NOT NULL,
  raw_diff           TEXT NOT NULL,
  affected_campaign_ids TEXT[],
  detected_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## Chapter 3.3 — Social Media Monitoring

**Schedule:** Every 6 hours per competitor.

**What is monitored:** Public posts from all social platforms where the competitor has an active presence. Platforms supported at launch: Instagram (public posts via web scraping), LinkedIn (public company posts), Twitter/X (public posts), and Facebook (public page posts).

**The monitoring process:**

1. Fetch the competitor's social profile pages using chromiumoxide. Extract post content, post timestamps, and available engagement metrics (likes, comments, shares — not all platforms expose these in their public web interface).

2. Identify new posts since the last monitoring run by comparing post timestamps against the last_monitored_at timestamp in the competitor_social_accounts table.

3. For new posts, run a Flash-Lite Normal batch inference call that classifies each post's: content theme (which of the competitor's content territories does this post serve?), format type (educational, promotional, social proof, behind-the-scenes, event announcement), and engagement level relative to this competitor's typical performance (above average, average, below average).

4. Detect messaging shifts by comparing the current month's content theme distribution against the previous month's distribution. If any theme has shifted by more than 20 percentage points, flag as a messaging shift. Store as a competitor_social_signal with signal_type 'messaging_shift'.

5. Identify high-performing posts (engagement level 'above average') and store their content characteristics — format, theme, length, emotional register — in the competitor_content_patterns table. These patterns inform the Daily Wins briefing's content strategy recommendations.

**Data model additions:**
```sql
CREATE TABLE competitor_social_posts (
  post_id            TEXT PRIMARY KEY,
  competitor_id      UUID NOT NULL,
  org_id             UUID NOT NULL,
  platform           TEXT NOT NULL,
  content            TEXT NOT NULL,
  content_theme      TEXT,
  format_type        TEXT,
  engagement_level   TEXT,
  raw_engagement     JSONB,
  posted_at          TIMESTAMPTZ NOT NULL,
  scraped_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## Chapter 3.4 — Ad Library Monitoring

**Schedule:** Every 12 hours per competitor.

**Meta Ad Library:** Accessed via chromiumoxide browsing the public Meta Ad Library at https://www.facebook.com/ads/library. The browser is configured to avoid triggering Meta's bot detection by using realistic session timing and the anti-detection configuration described above.

Search process: navigate to the Meta Ad Library, search by the competitor's Facebook page name or domain, extract all active ads. For each ad: the ad creative text (primary text, headline, description), the ad format (image, video, carousel, collection), the estimated active duration (Meta shows the date the ad started running), and the call to action text.

**Google Ads Transparency Center:** Similarly accessed via chromiumoxide at https://adstransparency.google.com. Search by advertiser name or domain. Extract active ads with their creative text.

**Processing pipeline:**

1. Compare newly scraped ads against the stored ad_library_entries for this competitor. Identify: new ads (not in the stored set), paused ads (previously stored as active, not found in current scrape), creative changes (same ad ID but different creative text).

2. Run a batch Flash-Lite Normal inference call that analyses the current active ad set for: dominant messaging themes, apparent target audience signals in the copy, creative format distribution, any notable offer or promotion language. This analysis produces the competitor's current 'advertising posture' — what they are emphasising at this moment.

3. Compare the current advertising posture against the previous posture. If significant changes are detected (a new theme appearing, an old theme disappearing, a major shift in offer framing), generate an intelligence alert.

4. Store screenshots of new ads in S3 (bucket path: intelligence/{org_id}/{competitor_id}/ads/{date}/). Store the ad data in the ad_library_entries table.

**Data model:**
```sql
CREATE TABLE ad_library_entries (
  entry_id           TEXT PRIMARY KEY,
  competitor_id      UUID NOT NULL,
  org_id             UUID NOT NULL,
  platform           TEXT NOT NULL,
  ad_text            TEXT NOT NULL,
  ad_format          TEXT,
  cta_text           TEXT,
  first_seen_at      TIMESTAMPTZ NOT NULL,
  last_seen_at       TIMESTAMPTZ NOT NULL,
  status             TEXT NOT NULL DEFAULT 'active',
  screenshot_s3_key  TEXT,
  messaging_themes   TEXT[],
  audience_signals   TEXT[]
);
```

## Chapter 3.5 — SEO and SERP Monitoring

**Schedule:** Weekly per tracked keyword set.

**The monitoring process:**

1. For each keyword in the user's Foundation keyword list, perform a web search using chromiumoxide navigating to a search engine with the keyword query. Extract the top 10 organic results: domain, page title, meta description, estimated position.

2. Record the user's domain's position (if present in top 10) and each competitor's position (if present in top 10) in the seo_rankings table.

3. Compare current positions against the previous week's positions. Flag significant changes: user's domain dropping more than 3 positions, user's domain entering top 10 for the first time, a competitor entering top 5.

4. For competitor domains that have moved into higher rankings: identify what content they have published recently for the keyword (by checking their sitemap or blog for new content containing the keyword). Store any newly identified competitor content as a competitor_content_signal.

**Data model:**
```sql
CREATE TABLE seo_rankings (
  ranking_id         TEXT PRIMARY KEY,
  org_id             UUID NOT NULL,
  keyword            TEXT NOT NULL,
  user_domain_rank   INTEGER,
  competitor_ranks   JSONB,
  tracked_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## Chapter 3.6 — The Intel Dashboard

The Intel dashboard aggregates all intelligence outputs into a single view. Its structure:

**Competitor cards:** One card per tracked competitor. Each card shows: current website status (last checked, any recent changes), recent ad activity (number of active ads, any new ads in the last 7 days), social posting frequency (current week vs last week), SEO ranking for the user's top 5 keywords.

**Timeline view:** A chronological feed of all detected competitive changes, most recent first. Each item shows: what changed, when, which competitor, what the system's significance assessment was. Filters by competitor, by change type, by significance level.

**Ad Gallery:** A visual grid of competitor ads currently running. Organised by competitor, then by platform. Each ad shows the creative text and any available format metadata.

**SEO Ranking Chart:** A time-series chart showing ranking positions for the top tracked keywords, with lines for the user's domain and each tracked competitor. Changes over the last 30 days visible at a glance.

---

# Part Four: Daily Wins

## Chapter 4.1 — What Daily Wins Is

The Daily Wins briefing is the product's daily conversation with the user. It is generated every morning at 04:00 IST for all active users and is waiting in their interface when they open the app. It is not a data report. It is a curated narrative, in the Strategist's voice, covering what matters most from the last 24 hours and what to focus on today.

The core design principle: one clear recommendation per briefing. Not five things to consider. Not a comprehensive status report. One specific action that, if taken today, will move the business forward most meaningfully. This focus is the hardest thing to get right and the thing that makes the briefing valuable rather than overwhelming.

## Chapter 4.2 — The Briefing Generation Process

**04:00 IST:** The daily_wins generation job runs. For each active org, the job assembles the briefing context:

- Last 24 hours of performance data from campaign_performance_log
- All intel alerts detected in the last 24 hours (competitor_diffs, ad_library_entries with status change, seo_rankings with significant movement)
- Current active campaign status (for each active campaign: status, current Move, tasks due today, tasks missed yesterday)
- The user's Foundation (cached)
- The Strategist's personality configuration (to write the briefing in the right voice)

This context is submitted as a batch inference request to Vertex AI (50% cost reduction on batch processing). The generation uses Flash-Lite Normal with the Strategist's persona as the system context.

**The generation prompt structure:** 'You are [Strategist name], the Campaign Strategist for [Company name]. Using the following information about yesterday's performance and overnight competitive activity, write a morning briefing for [user name]. The briefing should: be written in your characteristic voice ([personality dimensions]), lead with the most important insight, include no more than three items of information, and close with a single specific recommended action for today. Do not be generic. Every element of the briefing should be specific to this business's situation.'

**Briefing sections:**

**Section 1 — The Lead:** The single most important thing that happened or was detected in the last 24 hours. This is determined by the Strategist's synthesis of all context — the item with the highest combined significance (performance importance × intelligence relevance × action urgency). If nothing significant happened, the lead is still something specific: the most interesting data point from yesterday's performance, not 'everything is fine.'

**Section 2 — The Context (optional, 1-2 items max):** Supporting context that makes the lead item understandable. Not additional news items — supporting detail for the lead. If the lead is about an underperforming ad campaign, the context might be the competitive activity that might explain it.

**Section 3 — Today's Focus:** The one specific task or action that the Strategist recommends for today. This must be actionable within the day, specific (not 'work on your marketing'), and connected to the lead item or to the highest-priority active campaign task.

## Chapter 4.3 — Daily Wins Data Model

```sql
CREATE TABLE daily_wins (
  win_id             TEXT PRIMARY KEY,
  org_id             UUID NOT NULL,
  generated_at       TIMESTAMPTZ NOT NULL,
  lead_summary       TEXT NOT NULL,
  full_briefing      TEXT NOT NULL,
  recommended_action TEXT NOT NULL,
  recommended_action_type TEXT NOT NULL,
  recommended_action_data JSONB,
  viewed_at          TIMESTAMPTZ,
  acted_on_at        TIMESTAMPTZ,
  action_outcome     TEXT
);
```

The recommended_action_type field classifies what kind of action is being recommended: approve_content (action_data includes the content_id), review_campaign (action_data includes the campaign_id), respond_to_intel (action_data includes the diff_id), adjust_budget (action_data includes the campaign_id and recommended change), publish_post (action_data includes the task_id), or strategic_review (for broader strategic decisions with no specific database action).

The acted_on field and action_outcome field track whether the user followed the recommendation and what happened. This data is stored as a PRL ripple in the Strategist's stream and contributes to the Strategist's learning about which types of recommendations this user actually acts on.

## Chapter 4.4 — The Morning Meeting Animation

At 09:00 IST (configurable), the Office animation shows the morning meeting. The Campaign Strategist walks from their office to the conference room. The agents most relevant to the current active campaigns follow. They assemble around the table. The meeting runs for the duration of the morning meeting animation — approximately 60-90 seconds of animation.

The content of the morning meeting animation is generated alongside the Daily Wins briefing. Each agent's contribution to the meeting is a brief speech bubble that reflects their perspective on the day's most important item: Patel might comment on the platform performance data, Ogilvy on the quality of the overnight content generation, the Analytics Director on the performance trends. These contributions are generated by a Flash-Lite Normal batch call alongside the main briefing.

The morning meeting animation is the Office equivalent of the Daily Wins briefing — the same information, shown through the lens of the living office rather than through a text report. Users who engage with the morning meeting animation report higher daily active usage than users who read only the text briefing.

---

# Part Five: Nudges

## Chapter 5.1 — What Nudges Are and Are Not

Nudges are proactive, time-sensitive, in-app alerts generated when the system detects something that the user needs to know about now. The distinction from Daily Wins is urgency: Daily Wins aggregates overnight activity for morning review. Nudges surface when something requires attention before the next morning briefing.

What nudges are NOT: push notifications (in-app only at launch), email alerts (not at launch), or any form of outbound communication. They appear in the user's Nudge panel when they are in the app, and are queued for the next app open if the user is not currently active.

**Three categories of Nudge:**

**Intel Nudge:** A competitive change of high significance has been detected that may require a response. Triggered when competitor_diffs.significance = 'major' AND the change affects an active campaign. The Nudge includes: what changed, which competitor, why it might matter for the active campaign, and a quick action button to view the full diff or to open the relevant campaign.

**Performance Nudge:** A campaign performance metric has deviated significantly from projection. Triggered when the KPI deviation trigger threshold is crossed. The Nudge includes: which metric, the current value, the projected value, the gap, and a quick action button to view the campaign performance or to ask Muse for analysis.

**Opportunity Nudge:** The system has detected an opportunity that the user should capitalise on while it exists. Examples: a keyword where the user's ranking has suddenly improved (creating an opportunity to capitalise with fresh content), a platform's algorithm rewarding a specific content format that the user is not currently using, a competitor pausing their ads (creating a temporary reduction in competitive pressure). Opportunity Nudges use softer language than intel or performance Nudges — they are invitations, not alarms.

## Chapter 5.2 — Nudge Generation Logic

The Nudge evaluation job runs every 2 hours. Its logic:

1. **Load all active campaigns for all orgs.** Evaluate each campaign against the three Nudge triggers.

2. **Intel Nudge evaluation:** For each major significance competitor_diff detected since the last evaluation run, assess: does this diff involve a competitor that is referenced in any active campaign's Foundation context? Does the change type (pricing, messaging, feature) directly affect the Campaign strategy? If yes to both, generate an Intel Nudge.

3. **Performance Nudge evaluation:** For each active campaign, load the current performance trajectory. Compare against the kpi_target. If the deviation threshold is crossed (>20% from target with >5 days remaining), generate a Performance Nudge. Suppress if a Nudge about this campaign's performance was already generated in the last 48 hours (prevent Nudge fatigue).

4. **Opportunity Nudge evaluation:** Run a Flash-Lite Normal inference call with the current intel data, performance data, and campaign context that specifically looks for positive signals — things that are going unusually well or windows of opportunity that are briefly open. This call produces zero to one opportunity identification per org per evaluation run.

5. **Deduplication and rate limiting:** A user should not receive more than 3 Nudges per 24-hour period. If more Nudge triggers fire than the limit allows, only the highest-priority Nudges are sent. Priority order: Intel Nudge (immediate competitive threat) > Performance Nudge (active campaign at risk) > Opportunity Nudge (positive signal to capitalise on).

## Chapter 5.3 — Nudge Data Model

```sql
CREATE TABLE nudges (
  nudge_id           TEXT PRIMARY KEY,
  org_id             UUID NOT NULL,
  user_id            UUID NOT NULL,
  nudge_type         TEXT NOT NULL,
  priority           TEXT NOT NULL,
  title              TEXT NOT NULL,
  body               TEXT NOT NULL,
  action_type        TEXT,
  action_data        JSONB,
  source_type        TEXT NOT NULL,
  source_id          TEXT NOT NULL,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  delivered_at       TIMESTAMPTZ,
  viewed_at          TIMESTAMPTZ,
  acted_on_at        TIMESTAMPTZ,
  dismissed_at       TIMESTAMPTZ,
  suppressed         BOOLEAN NOT NULL DEFAULT FALSE
);
```

The source_type and source_id fields link the Nudge to its source — the specific competitor_diff, performance_log entry, or opportunity detection that triggered it. This linkage allows the user to navigate directly to the source for more context and allows the PRL to associate Nudge outcomes with their triggers.

Nudge outcomes — viewed, acted on, dismissed, ignored — are stored and analysed by the Muse pattern system. A user who consistently dismisses Intel Nudges but acts on Performance Nudges will find that the Nudge engine gradually reduces Intel Nudge frequency for this user. Personalisation of Nudge frequency and type is a natural output of the outcome tracking.

---

# Part Six: How These Features Connect to Each Other

## Chapter 6.1 — The Complete Daily Intelligence Loop

The five features in this volume form a coherent daily intelligence loop:

The **Intelligence Pipeline** continuously monitors. When it detects something significant, it does two things simultaneously: it stores the raw intelligence in the database for the Intel dashboard, and it evaluates whether the intelligence warrants a **Nudge** for immediate user attention.

Every morning at 04:00 IST, the **Daily Wins** job assembles everything the intelligence pipeline detected overnight, everything the campaign performance system tracked, and everything the active campaigns need attention on — and synthesises it into the morning briefing.

When the user opens the app, they see their Daily Wins briefing and any pending Nudges. They can ask **Muse** to elaborate on anything in the briefing. They can use the **Content Engine** to execute today's recommended task if it involves content creation.

When they act on a Nudge or a Daily Wins recommendation, the outcome is tracked and becomes a PRL ripple that teaches the system which recommendations this user finds actionable and which they do not.

When **Campaigns** change in response to intelligence — through the Dynamic Replanning Engine — the new campaign state feeds back into the intelligence pipeline's evaluation context, ensuring that future intelligence monitoring is relevant to the new campaign approach.

The loop closes completely: intelligence → nudge/briefing → user action → campaign adjustment → updated intelligence evaluation context → next cycle of intelligence.

## Chapter 6.2 — The PRL Connections

All five features generate PRL ripples. The ripples created across these features collectively constitute the most valuable knowledge in the entire system — not the agent-to-agent debates in Council sessions, but the user-to-product-to-reality interaction data that shows what actually works for this specific business.

Muse conversation ripples: what questions the user asks, what answers they act on, what topics they keep returning to.

Content performance ripples: which content pieces performed above or below expectation, what characteristics they had, what avatar generated them.

Intelligence accuracy ripples: which competitive changes the system detected that turned out to matter, which it detected that turned out not to matter, which it missed.

Daily Wins action ripples: which recommended actions the user took, which they ignored, what the outcomes were when they acted.

Nudge response ripples: which nudge types this user responds to, which they dismiss, what the correlation is between nudge response and campaign performance.

Together, these ripples create a progressively more accurate model of what works for this specific user in this specific business in this specific market. At month 1, the system's recommendations are informed by general marketing principles and client Foundation data. At month 12, they are also informed by 12 months of tracking what this specific user actually does, what produces results when they do it, and what the competitive environment has looked like over that period.

---

# Appendix: Data Flow Diagram — The Intelligence Loop

The complete data flow for the intelligence system in text form, for implementation reference:

```
INTELLIGENCE PIPELINE
  ├── Website Change Detection (daily)
  │     → competitor_snapshots
  │     → competitor_diffs
  │     → [if significant] intel_alerts
  │
  ├── Social Monitoring (every 6h)
  │     → competitor_social_posts
  │     → [if shift detected] competitor_social_signals
  │
  ├── Ad Library Monitoring (every 12h)
  │     → ad_library_entries
  │     → [if new/changed] intel_alerts
  │
  └── SEO Monitoring (weekly)
        → seo_rankings
        → [if movement] intel_alerts

NUDGE EVALUATION (every 2h)
  ├── Reads: intel_alerts, campaign_performance_log, campaigns
  ├── Evaluates: trigger conditions per campaign
  └── Writes: nudges [max 3/user/24h]

DAILY WINS GENERATION (04:00 IST)
  ├── Reads: all intel from last 24h, campaign performance, active tasks
  ├── Generates: briefing via Flash-Lite Normal batch
  └── Writes: daily_wins, queues delivery

MUSE INVOCATION (user-triggered)
  ├── Assembles: 7-layer spatial context
  ├── Routes: to Strategist / Avatar / Mini-Council / Analytics Director
  ├── Generates: via Flash-Lite Reasoning or Normal
  └── Writes: muse_messages, PRL ripples

CONTENT GENERATION (scheduled or on-demand)
  ├── Assembles: Foundation + Campaign + Avatar context
  ├── Generates: via Flash-Lite Normal
  ├── Validates: voice compliance check
  └── Writes: generated_content, campaign_tasks.content_ready = true
```
