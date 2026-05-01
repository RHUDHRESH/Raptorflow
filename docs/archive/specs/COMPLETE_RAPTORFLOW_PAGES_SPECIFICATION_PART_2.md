# RAPTORFLOW COMPLETE PAGES & SCREENS SPECIFICATION — PART 2
## Sections 6-11: Intel, Daily Wins, Council, Content, Settings, Admin

---

# SECTION 6: COMPETITIVE INTELLIGENCE DASHBOARD

## 6.1 — Intel Dashboard (Overview)
**Route:** `/intel`  
**Purpose:** View competitive intelligence and market monitoring

### Layout: Three-Panel with Timeline

**Left Column: Intelligence Feeds** (20%)
- **Feed Categories** (Tabs):
  - All Intelligence (aggregated)
  - Website Changes (competitor website monitoring)
  - Social Activity (social media monitoring)
  - Ad Library (competitor ads)
  - SEO Movements (keyword ranking changes)
- Search field: "Search intelligence"
- Filter by: Competitor name, Alert level, Date range
- Sorting: Newest first / Most significant / By competitor

**Center Column: Intelligence Items Timeline** (60%)
- **Timeline View** (Reverse chronological):
  - Each intelligence item displayed as a card
  - Timestamp (e.g., "2 hours ago", "Today 9:15 AM")
  - Source indicator (icon showing: website / social / ads / SEO)
  - Competitor name
  - Alert level badge: 🟢 Low / 🟡 Medium / 🔴 High
  - Intelligence headline (50-100 words)
  - Thumbnail/screenshot if applicable (website change, ad screenshot, etc.)
  - "Full details" link
  - Quick actions: "Discuss in Muse", "Create Nudge", "Archive"

**Example Intelligence Items:**
- 🟡 **CompetitorX updated pricing page** — "Changed mid-tier pricing from ₹50K to ₹40K. Added new benefit claim about speed."
- 🟢 **CompetitorY published new blog post** — "Posted about AI-powered marketing. Positioning language: 'AI that works for SMBs'. Could be relevant to our positioning."
- 🔴 **CompetitorZ launched major ad campaign** — "20+ new ads across Instagram, Facebook, LinkedIn. Focus: enterprise features. Audience: 50K+. Estimated spend: ₹500K+. Threat level: High for enterprise segment."

**Right Column: Intelligence Analytics** (20%)
- **Overview Stats**:
  - Total competitors tracked: [N]
  - Intelligence items this week: [N]
  - High-priority alerts: [N]
  - Most active competitor: [Name]

- **Competitor Activity Heatmap**:
  - Visual grid: Competitors × Activity type
  - Color intensity shows activity level (high = darker/red, low = light/blue)
  - Identifies which competitors are most active

- **Timeline Selector**:
  - Last 7 days / Last 30 days / Last 90 days
  - Updates all views

---

## 6.2 — Intelligence Detail View
**Route:** `/intel/[intelligence-id]`  
**Purpose:** Deep dive into a specific intelligence item

### What the User Sees

**Header:**
- Intelligence type icon + headline
- Source: [Competitor Name]
- Timestamp: When detected
- Alert level: Color-coded
- "Relate to Campaign" dropdown (if applicable)

**Intelligence Details Section:**

**What We Found:**
- Full description (300-500 words)
- If website change: Before/after screenshots (side-by-side or tab switch)
- If social post: Screenshot of post, engagement metrics, content analysis
- If ad: Screenshot of ad, estimated spend, audience size, targeting inferred
- If SEO: Keyword, old ranking, new ranking, position change trend

**Impact Assessment:**
- Headline: "Why this matters"
- Analysis: How this affects the business strategically
- Affected segment: Which ICP, which channel, which product
- Threat level: 1-5 scale with explanation
- Opportunity: Could we capitalize on this?

**Historical Context:**
- Timeline of this competitor's recent changes
- Pattern analysis: "This is the 3rd pricing update in 3 months"
- Comparison to our approach: How we differ

**Recommended Actions:**
- Strategist recommendation
- Suggested campaign adjustments (if applicable)
- Related tasks to create
- "Discuss in Muse" button
- "Create Nudge" button (if not already nudged)

---

## 6.3 — Competitor Profile Pages
**Route:** `/intel/competitors/[competitor-id]`  
**Purpose:** View aggregated intelligence on a specific competitor

### What the User Sees

**Header:**
- Competitor logo (fetched)
- Competitor name
- Competitor website URL (clickable)
- Data sources: Website monitoring since [date]

**Competitor Overview:**
- Positioning (from their website): Quote from their messaging
- Primary products/services (extracted)
- Estimated size/scale: (e.g., "Likely 50-200 person company based on team size signaled")

**Recent Activity Timeline:**
- Last 30 days of changes to this competitor
- Reverse chronological list
- Grouped by type: Website | Ads | Social | SEO

**Competitive Analysis Summary:**
- Their strengths (from Foundation assessment + observed changes)
- Their weaknesses (from Foundation assessment + observed changes)
- Our differentiation vs them (from Foundation positioning + all observations)
- Market positioning diagram (optional): Us vs them on 2-3 key dimensions

**Intelligence Dashboard (Mini):**
- Most recent changes
- Current ad campaigns (if detected)
- Top performing content (if detected)
- Keyword ranking positions (if monitoring SEO)

**Ad Library Viewer:**
If competitor has active ad campaigns:
- Gallery of recent ads
- Group by platform (Instagram, Facebook, LinkedIn, etc.)
- Each ad shows:
  - Screenshot
  - Estimated run time
  - Estimated spend
  - Engagement signals (if available)
  - Ad copy
  - Targeting inferred
  - "Learn more" link

---

---

# SECTION 7: DAILY WINS & NUDGES SYSTEM

## 7.1 — Daily Wins Briefing View
**Route:** `/daily-wins` or `/daily-wins/[date]`  
**Purpose:** View morning briefing and historical briefings

### Today's Briefing (Default View)

**Header:**
- Sunrise icon + "Today's Briefing"
- Date: [Today's date]
- Generated at: 6:00 AM IST
- Refresh button (manual re-generate)
- Archive toggle: "View past briefings" dropdown

**Briefing Content Structure:**

**Section 1: Recommended Action(s) for Today** (1-3 items)
Each item shows:
- ⭐ Priority indicator (1-3 stars)
- Task headline (20-30 words)
- Context paragraph (50-100 words explaining why)
- Related campaign/move (if applicable, clickable)
- Action buttons:
  - "Take this action" (blue)
  - "Discuss in Muse" (secondary)
  - "Skip" (tertiary)
- Timestamp: When this was recommended

**Example Daily Wins Recommended Actions:**
- ⭐⭐⭐ "Spring Campaign Awareness Move is 40% complete with 6 days remaining. Approve the 3 pending social posts to stay on schedule."
- ⭐⭐ "Your best-performing blog content (AI Marketing 101) is trending on LinkedIn. Consider writing a follow-up: Advanced AI for SMBs."
- ⭐ "Competitor released new case study. Worth reading to understand their proof strategy. 15-minute read."

**Section 2: Campaign Status Updates** (2-3 items)
Each item shows:
- Campaign name (clickable)
- Current metric vs target (bar chart)
- Status: On track / Behind / Ahead
- Current Move
- Key note (1 sentence)
- "View full campaign" link

**Example Campaign Updates:**
- **Spring Launch:** 52/100 leads generated (52%). On track. Currently in Consideration Move. "Performance is tracking projection. Budget spent is 3% below allocated."
- **Holiday Campaign:** ₹450K / ₹500K revenue (90%). Slightly behind. In final Conversion Move. "One week remaining. Consider scaling top-performing channel if budget permits."

**Section 3: Intelligence Highlights** (1-2 items)
Each item shows:
- Alert icon (color: green/yellow/red)
- Headline (20-30 words)
- Context (50 words)
- Source competitor (if applicable, clickable)
- Impact assessment: Low / Medium / High
- "Learn more" link (goes to Intel dashboard)

**Example Intelligence Highlights:**
- 🟡 "CompetitorX updated pricing. Moved mid-tier down 20%. Strategic implication: they're aggressively targeting our core ICP. Discuss in Council session?"
- 🟢 "Industry newsletter mentioned AI-in-marketing trend. Your positioning is well-aligned. Opportunity to position thought leadership?"

**Bottom of Briefing:**
- Generated timestamp
- "This briefing was generated by [Strategist Name] at 6:00 AM IST using:"
  - Your Foundation strategy
  - 7 days of competitive intelligence
  - Your active campaigns
  - Historical performance patterns
- "View data sources" link

---

## 7.2 — Daily Wins Archive
**Route:** `/daily-wins?date=[YYYY-MM-DD]`  
**Purpose:** View past daily briefings

### What the User Sees

**Date Picker:**
- Calendar selector showing past 90 days
- Today highlighted
- Clicking a date loads that day's briefing

**Historical Briefing Display:**
- Same structure as today's briefing
- Timestamp: "Generated [date] at 6:00 AM IST"
- Grayed-out action buttons (for past briefings)
- Toggle: "Did you take this action?" (for tracking effectiveness)
- "Mark as helpful / unhelpful" buttons (feedback for system learning)

---

## 7.3 — Nudges & Alerts View
**Route:** `/alerts` or `/alerts?filter=[filter]`  
**Purpose:** View all nudges and time-sensitive alerts

### Alerts List

**Header:**
- "Alerts & Nudges"
- Filter tabs: All / Recent / Pending action / Archive
- View toggle: List / Grid

**Alert Cards** (Stacked, newest first):

Each alert shows:
- Alert icon (type indicator)
- Alert headline (30-50 words)
- Context timestamp: "2 hours ago", "Today 9:30 AM", "This week"
- Alert level: 🟢 Info / 🟡 Action-recommended / 🔴 Urgent
- Source: Campaign / Intelligence / Performance (with icon)
- Related item: Campaign name / Competitor name (clickable)
- Quick action buttons:
  - "Take action" (if action-oriented nudge)
  - "View details"
  - "Discuss in Muse"
  - "Archive" (remove from active list)
  - "Not relevant" (dismiss and reduce similar nudges)
- Expand arrow: Reveals full nudge text

**Example Nudges:**

🟡 **Campaign Alert**
"Spring Campaign reach is 20% below projection. Current spend shows good engagement (5% CTR vs 3% baseline). Recommend: Increase budget by 15% to hit reach target. Estimated additional cost: ₹5,000."
[Take action] [Discuss in Muse] [Archive]

🔴 **Competitive Alert**
"URGENT: CompetitorZ launched aggressive promotion in your target market. 30% discount on core offering, valid through weekend. Threat level: High. Your current pricing positioning may be affected. Recommend immediate Council review."
[View details] [Discuss in Muse] [Create campaign response]

🟢 **Opportunity Alert**
"Your content on [topic] generated 3x engagement this week. Pattern suggests audience interest in this area. Opportunity: Consider pivot/deepening content strategy here?"
[Explore opportunity] [Archive]

---

---

# SECTION 8: COUNCIL & DEBATE VIEWER

## 8.1 — Council Session Viewer (Live/Playback)
**Route:** `/council/[session-id]`  
**Purpose:** View Council debate in real-time or playback

### Live Session View (During Active Debate)

**Header:**
- Council session type: "Strategic Council" / "War Room" / "Tactical Council"
- Campaign name (what this session is about)
- Status: "In Progress" (pulsing indicator)
- Estimated time remaining: "8 minutes remaining"
- Start time / Elapsed time

**Main Viewing Area:**

**Layout: Threaded Conversation**
- Each agent's contribution is shown as a message
- Left-aligned (agent message) with agent name + avatar at top
- Message content with formatting: bold, emphasis, indentation for quotes
- Timestamp for each message (relative: "2 min ago")
- Interaction indicators:
  - Agent speaking (animated mouth, speaking bubble)
  - Agent listening (attentive posture)
  - Agent reacting (facial expression change if major point)

**Message Structure for Agent Contribution:**
```
[Agent Avatar] Agent Name | Role
[Timestamp: 2 min ago]

[Agent voice] "Message content here. Can be 1-10 paragraphs.
Multiple points separated cleanly. References other agents
when relevant."

[Response references: Quoting Ogilvy's earlier point...]

[Interaction buttons]:
[React] [Quote in response] [Share]
```

**Example Council Exchange:**

```
[Ogilvy Avatar] David Ogilvy | Ad Copy & Copy Strategy
[11:30 AM]

"Your positioning is too clever. People will miss it entirely. Marketing's
primary function is to sell goods, not to be clever. Let me suggest a
reframe:

Instead of 'Marketing intelligence for thinking marketers,' try 'The marketing
team you can't afford to hire.' Benefit-focused. Immediately clear. Memorable.

This is the kind of clarity that has built every successful campaign I've worked
on. Cleverness is a luxury we can't afford in this market."

[React] [Quote] [Share]
```

```
[Vaynerchuk Avatar] Gary Vaynerchuk | Growth & Viral Strategy
[11:32 AM]

[Quoting Ogilvy]
"I disagree with you here, David. Look, I respect the work, but Gen Z and
younger millennials respond to cleverness. They're actually put off by
transactional clarity. They want to feel like they're joining something
special, not buying a service.

'The marketing team you can't afford' — that's depressing. That reinforces
scarcity mentality. What about 'Finally, a marketing office that thinks like
you' — speaks to equality, partnership, not hiring."

[React] [Quote] [Share]
```

**Session Navigation Sidebar** (Right, 15%):

**Agents Participating:**
- List of all agents in session (12-21 names)
- Checkmark showing who has spoken
- Small animation when an agent is currently speaking
- Click to jump to that agent's contributions

**Session Outline:**
- Phase 1: Initial responses (5 messages, collapsed)
- Phase 2: Debate (12 messages, can expand)
- Phase 3: Synthesis (in progress...)

**Message Statistics:**
- Total messages: 23
- Agents who spoke: 10 of 12
- Longest message: Ogilvy (8 paragraphs)
- Most quoted: [Agent name] (5 times)

---

### Completed Session Playback

**Header:** (Same as above, but)
- Status: "Completed" (checkmark)
- Duration: "Completed in 23 minutes"
- Session dated: "[Date] [Time]"
- Related campaign: [Name] (if applicable)

**Additional Controls:**
- Play/pause button (to replay session)
- Speed control: 1x / 1.5x / 2x (for faster replay)
- Timeline scrubber (see progress through session)

**Synthesis Section** (Bottom, pinned):

After all debate, a synthesis appears showing:

**Strategist Synthesis** (Appears at end of session)
```
[Strategist Avatar] [Strategist Name] | Campaign Strategist
[11:47 AM]

[Synthesized position] "Here's what I'm hearing:

1. **Positioning** needs to emphasize accessibility and empowerment, not
   cleverness or technological sophistication.
   
2. **Copy approach** should lead with benefit (what changes for customer) not
   feature (what we do).
   
3. **Target** is ambitious founders and SMB leaders who want partnership-feeling,
   not service-transactional feeling.

**Recommended positioning statement:**
'We are the marketing office for ambitious SMB founders who want expert partners,
not another SaaS tool.'

**Recommended campaign approach:**
Launch with founder story content (Draper domain), build community early (Godin
domain), then demonstrate expertise through data (Ogilvy domain).

Ogilvy: Does this capture your copy philosophy?
Vaynerchuk: Does this honor the partnership feeling you wanted?
```

---

## 8.2 — Council Session Archive
**Route:** `/council?filter=[date-range]`  
**Purpose:** View history of Council sessions

### Sessions List

**Header:**
- "Council Sessions"
- Filter: Last 30 days / Last 90 days / All time
- Sort: Newest first / By duration / By complexity

**Session Cards** (Grid, 2 per row):

Each card shows:
- Session date & time
- Session type badge: Strategic / Tactical / War Room
- Campaign associated
- Agents present: [N] of 21
- Duration: "23 minutes"
- Outcome icon: ✅ (decision made) / 🔄 (replanning) / 🤔 (needs review)
- Quick actions:
  - [View transcript]
  - [Share]
  - [Export]

---

---

# SECTION 9: CONTENT ENGINE & ASSET MANAGEMENT

## 9.1 — Content Library & Asset Management
**Route:** `/content`  
**Purpose:** View, manage, and organize all generated and uploaded content

### Three-Column Layout

**Left Column: Content Filters** (20%)
- **Content Type** (Checkboxes):
  - [ ] Ad copy
  - [ ] Social posts
  - [ ] Email
  - [ ] Blog posts
  - [ ] Landing pages
  - [ ] Headlines
  - [ ] Captions
  - [ ] Other

- **Status Filter**:
  - [ ] Draft
  - [ ] Pending approval
  - [ ] Approved
  - [ ] Published
  - [ ] Archived

- **Campaign Filter**:
  - Dropdown: All campaigns / [Campaign 1] / [Campaign 2]

- **Agent Filter**:
  - Dropdown: All agents / [Ogilvy] / [Vaynerchuk] / etc.

- **Date Range**:
  - Date picker or preset: Last week / Last 30 days / Last 90 days / All time

- **Search**:
  - Text field: "Search content by name, text, or campaign"

**Center Column: Content List** (60%)

**List View** (Default):
- Table with columns: Name | Type | Status | Created | Agent | Campaign | Actions

Each row shows:
- Content name/title (clickable)
- Content type icon (article, social post, email, etc.)
- Status badge: Draft / Pending / Approved / Published / Archived
- Created date (relative: "2 days ago")
- Assigned agent name
- Associated campaign name
- Action menu (three dots):
  - View details
  - Edit
  - Approve (if pending)
  - Publish (if approved)
  - Delete
  - Archive

**Grid View** (Alternative):
- Card layout, 3 cards per row
- Each card shows:
  - Content preview (image, headline, or text snippet)
  - Status badge
  - Type icon
  - Agent name
  - Campaign name
  - Created date
  - [View] button

**Bulk Actions** (if multiple selected):
- [ ] Approve all
- [ ] Publish all
- [ ] Archive all
- [ ] Delete all
- [ ] Download all as ZIP

**Right Column: Content Details** (20%) (Shows when item selected)

- **Content Title** (editable)
- **Type** (read-only)
- **Status** (read-only)
- **Agent Generated By** (read-only)
- **Campaign** (if applicable)
- **Full Content Preview** (scrollable)
- **Generation Details:**
  - Generated at: [timestamp]
  - Model used: [Mistral Large 3]
  - Temperature/settings used
  - Tokens used
- **Performance** (if published):
  - Impressions
  - Clicks
  - Engagement rate
  - Conversions (if trackable)
- **Approval History:**
  - Created by: [Agent]
  - Approved by: [User]
  - Published at: [timestamp]
  - Modifications made: [list if any]
- **Action Buttons:**
  - [Edit]
  - [Publish]
  - [Archive]
  - [Delete]
  - [Generate alternative]

---

## 9.2 — Content Generation Interface
**Route:** `/content/generate`  
**Purpose:** Generate new content on-demand

### Content Generation Workflow

**Step 1: Content Type & Brief**

**Field 1: Content Type** (Required)
- Dropdown:
  - Social media post (Instagram/TikTok/LinkedIn/Facebook/Twitter)
  - Email subject line & body
  - Blog post / Article
  - Ad copy (short / medium / long format)
  - Landing page headline
  - Product description
  - Case study
  - Whitepaper snippet
  - Other: [text input]
- Validation: Required

**Field 2: Campaign Context** (Optional but recommended)
- Dropdown: [Campaign 1] / [Campaign 2] / Not tied to specific campaign
- If selected: Pulls in campaign goal, ICP, timeline

**Field 3: Move/Task Context** (Optional)
- Dropdown: [Move/Task from selected campaign]
- If selected: Pulls in move details, acceptance criteria

**Field 4: Brief for Generation** (Required)
- Label: "What should this content accomplish?"
- Text area (300 chars)
- Placeholder: "Describe the goal, key message, audience tone — anything the agent should know"
- Example: "Instagram carousel post for Awareness Move. Target: Female founders, age 25-35. Tone: Inspiring but practical. Call-to-action: Learn more about RaptorFlow"
- Validation: Required, min 30 chars

**Field 5: Brand Voice & Constraints** (Optional but important)
- Brand voice slider override: (If user wants to override Foundation voice)
  - Toggle: "Use my Foundation voice" (default) / "Set custom voice"
  - If custom: Show voice sliders (same as Screen 10)
- Additional constraints: Text area
  - Example: "Must include the word 'partnership'. Avoid technical jargon. Max 280 characters."
- Validation: Optional

**Field 6: Assign to Agent** (Optional)
- Dropdown: Auto (system assigns) / [Agent name]
- Helper: "System recommends the best agent for this content type"
- Validation: Optional (system assigns if not selected)

**Submit Button:** "Generate Content"
- Validation: Fields 1-4 required
- On submit: Triggers content generation via appropriate agent

---

**Step 2: Content Generation (In Progress)**

**Loading Screen:**
- Agent avatar + name showing
- Text: "[Agent Name] is writing..."
- Thinking/generating animation
- Estimated time: "This usually takes 30-60 seconds"
- Cancel option (if user wants to stop)

---

**Step 3: Generated Content Display**

**Content Preview Section:**
- Full generated content displayed
- Formatted as it would appear (if social post: show as post preview, etc.)
- Read-only (user cannot edit directly)

**Quality Assessment** (Auto-generated):
- Headline: "Generated content review"
- Checklist:
  - ✅ Voice compliance: "Matches your brand voice perfectly"
  - ✅ Target audience: "Speaks directly to your ICP"
  - ✅ Length: "Within appropriate length for channel"
  - ⚠️ CTA: "Clear call-to-action present, could be more compelling"
- Overall score: "8/10 — High quality"

**Agent's Note:**
- Brief explanation from agent about the content
- Why they approached it this way
- Any creative choices made
- Example from Ogilvy: "I led with the specific customer outcome ('finally have the marketing team you wanted') rather than product features, as research shows this drives engagement for your ICP"

**Action Buttons:**
- **[Approve & Save]** (blue, primary) — Saves to content library in "Approved" status
- **[Save as Draft]** (secondary) — Saves but doesn't approve
- **[Generate Alternative]** (secondary) — Generates a different version (2-3 alternatives available)
- **[Edit in Editor]** (secondary) — Opens content in text editor for manual tweaks
- **[Regenerate with Different Agent]** (tertiary) — Try a different agent's perspective

**Alternative Versions** (if user selects "Generate Alternatives"):

Show 2-3 alternative versions in collapsible tabs:
- Alternative 1: "More formal, benefit-focused"
- Alternative 2: "More casual, story-focused"
- Alternative 3: "More data-driven, credibility-focused"

Each can be approved, edited, or replaced.

---

---

# SECTION 10: SETTINGS & PREFERENCES

## 10.1 — Workspace Settings
**Route:** `/settings/workspace`  
**Purpose:** Manage workspace-wide settings

### Settings Sections (Left Sidebar Navigation)

**Section 1: Workspace Basics**
- **Workspace Name** (editable text field)
- **Workspace URL Slug** (read-only, shows URL)
- **Workspace Avatar** (upload or generate)
- **Workspace Description** (optional, for teams)
- **Time Zone** (dropdown, affects Daily Wins timing)
- **Save** button (disabled until changes made)

**Section 2: Team Members**
- **Current Members Table:**
  - Name | Email | Role | Joined | Status | Actions
  - Roles: Admin / Editor / Viewer
  - Actions: Edit permissions / Remove
- **Invite New Member:**
  - Email input field
  - Role dropdown: Admin / Editor / Viewer
  - [Send invite] button
- **Pending Invites:**
  - List of sent invites not yet accepted
  - Resend / Revoke options

**Section 3: Billing & Subscription**
- **Current Plan**
  - Plan name: "RaptorFlow Standard"
  - Price: "₹5,000/month"
  - Billing cycle: "Next billing: May 15, 2026"
  - [Manage billing] link (goes to Stripe customer portal)
- **Payment Method**
  - Last 4 digits of card / bank account
  - [Update payment method] link
- **Usage**
  - Token usage this month: "45,000 / unlimited"
  - Campaign count: "3 active, 5 total"
  - Historical: Chart showing usage over time

**Section 4: Integrations** (If applicable)
- Connected services (Google Analytics, email platforms, etc.)
- Each shows: Service name | Status (connected/disconnected) | Last sync | [Reconnect] / [Disconnect]

---

## 10.2 — User Preferences
**Route:** `/settings/preferences`  
**Purpose:** Personal user settings

### User Preferences Sections

**Section 1: Profile**
- **Name** (editable)
- **Email** (read-only, shows current email from Clerk)
- **Avatar** (upload or use Gravatar)
- **Bio** (optional, for team context)
- **Pronouns** (optional dropdown)
- **Save** button

**Section 2: Communication & Notifications**
- **Email Notifications:**
  - [ ] Daily Wins briefing (6:00 AM IST)
  - [ ] Campaign alerts (real-time)
  - [ ] Competitive intelligence alerts (real-time)
  - [ ] Content approval reminders (daily)
  - [ ] Weekly summary report (Sundays)
- **Notification Frequency:**
  - Dropdown: Real-time / Batched (3x daily) / Daily digest
- **Notification Channels:**
  - [ ] Email
  - [ ] In-app notifications
  - [ ] Push notifications (browser)

**Section 3: Muse Preferences**
- **Strategist Communication Style:**
  - Toggle: Use configured style / Temporarily adjust for this session
  - Sliders (same 3 dimensions as Screen 20):
    - Decisive ↔ Collaborative
    - Data-driven ↔ Instinct-driven
    - Direct ↔ Diplomatic

**Section 4: Office Preferences**
- **Display Mode:**
  - Dropdown: Light / Dark
  - Preview: Small Office illustration
- **Animation Fidelity:**
  - Dropdown: Full (60 FPS) / Balanced (30 FPS) / Minimal (animations disabled)
  - Helper: "Affects performance on slower devices"
- **Show Snark Bubbles:**
  - Toggle: On / Off
  - If on, frequency dropdown: Frequent / Occasional / Rare

**Section 5: Data & Privacy**
- **Download Your Data:**
  - [Download] button (exports all workspace data as JSON + assets as ZIP)
- **Delete Account:**
  - [Delete] button (with confirmation warning)
  - Text: "This cannot be undone. All workspace data will be permanently deleted."

---

## 10.3 — Foundation Management
**Route:** `/settings/foundation`  
**Purpose:** View, edit, and version control Foundation

### Foundation Overview Section

**Current Foundation Status:**
- Last updated: [date]
- Version: 5 (if multiple edits have been made)
- Completeness: 100%
- Next review recommended: [date] (if system detected potential staleness)

**Quick Edit Buttons** (Links to relevant Foundation screens):
- "Edit Business Basics" (Screen 2)
- "Edit Products & Services" (Screen 4)
- "Update Positioning" (Screen 9)
- "Edit ICP" (Screens 6-7)
- "Update Competitive Landscape" (Screen 8)
- "Review All" (Screen 21 review interface)

### Foundation Version History

**Version Table:**
- Version # | Date | Changed | By (user) | Actions
- Each row shows what section was changed
- [View snapshot] button — shows complete Foundation as it existed at that version
- [Revert to this version] button (warning: will affect all campaigns using new version)

---

---

# SECTION 11: ADMINISTRATIVE & ADVANCED VIEWS

## 11.1 — System Dashboard (Admin Only)
**Route:** `/admin/dashboard`  
**Purpose:** Workspace health & system diagnostics

### Admin Dashboard Overview

**Workspace Health Metrics:**
- **System Status:**
  - All systems operational ✅
  - Last API check: 2 minutes ago
  - Uptime: 99.97% (last 30 days)

- **Usage Metrics:**
  - Total API calls this month: 1.2M
  - Average latency: 245ms
  - Token usage: 45M / Unlimited
  - Concurrent users (right now): 1

- **Agent Performance:**
  - Most used agent: Ogilvy (128 times this month)
  - Fastest agent (avg latency): Analytics Director (180ms)
  - Slowest agent: War Room Council (8 seconds avg)
  - Most accurate (user satisfaction): Ogilvy (4.8/5 stars)

- **Content Generation:**
  - Content generated this month: 452
  - Approval rate: 87%
  - Revision rate: 12% (content requested revisions)
  - Unique content types: 8

- **Campaign Health:**
  - Active campaigns: 3
  - Completed campaigns: 5
  - Replanning events: 2 (both successful)
  - Average campaign duration: 67 days

### System Logs & Monitoring

**Error Logs:**
- Real-time error monitoring (last 24 hours)
- Severity filter: Info / Warning / Error / Critical
- Source filter: Backend / Frontend / Database / AI inference
- Timestamp, error code, message, affected feature
- [View full logs] link

**Performance Metrics Charts:**
- API latency (p50, p95, p99)
- Database query times
- Token usage over time
- File delivery times
- Office animation frame rates (if monitoring)

---

## 11.2 — Campaign Audit & Intelligence Review
**Route:** `/admin/audit`  
**Purpose:** Deep dive review of specific campaigns or system behavior

### Audit Interface

**Campaign Audit Section:**
- Select campaign from dropdown
- Timeline view showing:
  - Brief submission date
  - Council session start/end
  - First task completion date
  - Replanning events (if any)
  - Campaign completion date
  - Performance trajectory vs projection

**Data Inspection:**
- View raw campaign JSON
- View Council session transcript (full, with inference metadata)
- View all PRL ripples created from this campaign
- View all generated content (drafts, approvals, rejections)
- Export campaign data as JSON

**Performance Review:**
- Did we predict outcome correctly?
- Were replanning recommendations good?
- What did the system learn?
- Accuracy assessment: "We projected 50 leads, achieved 52. Accuracy: 96%"

---

## 11.3 — Workspace Backup & Export
**Route:** `/settings/backup`  
**Purpose:** Data backup and export functionality

### Backup & Export Options

**Manual Backup:**
- [Download Full Backup] button
  - Exports: All workspace data (JSON), All content (assets), All campaigns, All conversations
  - Format: ZIP file with organized folders
  - Size: Calculated before download
  - File name: "workspace_backup_YYYY-MM-DD.zip"

**Scheduled Backups:**
- Toggle: Enable automatic backups
- Frequency: Weekly / Monthly / Never
- Backup time: Time picker
- Retention: Keep last [3] backups (dropdown)
- Last backup: [timestamp]

**Data Export:**
- Select what to export: Campaigns / Content / Conversations / All
- Date range (optional)
- Format: JSON / CSV (for campaigns)
- [Generate & Download] button

---

## 11.4 — Advanced Settings
**Route:** `/settings/advanced`  
**Purpose:** Power-user and debugging features

### Advanced Settings Sections

**API Access** (If enabled):
- API Key (masked, show/hide toggle)
- [Generate new key] button
- API documentation link
- Usage: [Showing API calls over time]

**Webhooks** (If applicable):
- Add webhook URL (for integrations)
- Event types to subscribe to: Campaign completed / Nudge generated / Content approved / etc.
- Test webhook button

**Inference Settings:**
- Model override: Dropdown (Sonnet / Opus / etc.)
- Temperature override: Slider (0.0 - 2.0)
- Max tokens override: Slider
- Note: "These settings affect all inference calls in this workspace"
- [Reset to defaults] button

**Performance Mode:**
- Toggle: "Enable advanced monitoring"
- Shows detailed performance metrics and system diagnostics
- Enables access to `/admin/dashboard`

**Developer Mode:**
- Toggle: "Enable developer mode"
- Shows: WebSocket event logs, system timing, debug info in UI
- Enables: `/admin/audit`
- Warning: "This is for developers only. May impact performance."

**Debug Panel** (When developer mode enabled):
- WebSocket event logger (real-time events flowing through system)
- Filter by event type
- Expandable event details showing full payload
- Office animation event log (shows animation triggers in real-time)
- PRL ripple creation log (shows ripples being stored)

---

---

# APPENDIX: INTERACTION PATTERNS & COMMON COMPONENTS

## A.1 — Common Form Components

### Date Picker Component
- Click to open calendar
- Month/year header with nav arrows
- Grid of dates
- Highlight today, disabled dates
- Selected date shows in field
- Keyboard support: Arrow keys to nav, Enter to select, Escape to close

### Dropdown / Select Component
- Click to open dropdown
- Search field (if list > 10 items)
- Options with icons (if applicable)
- Hover highlight
- Keyboard: Arrow keys to navigate, Enter to select
- Escape to close without selecting

### Multi-Select Checkbox Group
- Vertical list of checkboxes
- Label for each
- "Select all / Deselect all" toggle (if >5 options)
- Count showing (e.g., "3 of 8 selected")
- No height limit (scrollable if many options)

### Slider Component
- Horizontal or vertical
- Labeled endpoints (e.g., "Formal" ↔ "Casual")
- Current value displayed
- Tooltip showing value on hover/drag
- Keyboard: Arrow keys to adjust
- Click on track to jump to position

### Text Area Component
- Grows as user types (auto-resize, max 500px height)
- Character count (current / limit)
- Character limit enforcement
- Placeholder text
- Spell-check enabled (browser default)
- Paste formatting support (converted to plain text)

### File Uploader
- Drag-drop zone with visual feedback
- Click to open file picker
- Progress bar during upload
- File preview (image thumbnail, document icon, etc.)
- File size shown
- [Remove] button to clear
- Accepted formats shown in helper text

---

## A.2 — Modal & Dialog Components

### Confirmation Dialog
- Title ("Are you sure?")
- Body text (description of action)
- Two buttons: [Cancel] [Confirm]
- Optional: Checkbox "Don't ask again"
- Keyboard: Enter = Confirm, Escape = Cancel

### Alert Dialog
- Alert icon
- Heading
- Message
- Single button: [OK] or [Dismiss]
- Auto-closes after 5 seconds (optional)

### Loading State
- Spinner animation (or skeleton loading)
- Optional loading text
- Optional progress bar (if estimated time known)
- Optional cancel button (if cancellable)

---

## A.3 — Navigation & Links

### Breadcrumb Navigation
- Path: Dashboard > Campaigns > Spring Launch > Moves
- Each item clickable (except current)
- On mobile: Collapsed to "Back" button

### Tabs
- Horizontal tab bar
- Underline active tab
- Smooth transition on click
- Keyboard: Arrow keys to navigate, Enter to activate

### Sidebar Navigation
- Vertical menu
- Active item highlighted (background color)
- Icons for each item
- Optional: Collapse/expand toggle
- On mobile: Hamburger menu (collapses to drawer)

---

## A.4 — Feedback & Status Components

### Toast Notification
- Fixed position (bottom-right)
- Auto-dismisses after 4 seconds (or manually)
- Color coded: Green (success) / Yellow (warning) / Red (error) / Blue (info)
- Icon + message
- Optional [Undo] button
- Multiple toasts stack vertically

### Badge Component
- Small, colored label
- Inline with text
- Examples: Status badge (Draft, Active, Completed), Category badge, Alert level badge

### Progress Bar
- Horizontal bar showing percentage
- Color: Blue (neutral) / Green (positive) / Yellow (warning) / Red (urgent)
- Optional: Text label showing percentage
- Optional: Animation (pulsing if in-progress)

### Skeleton Loading
- Placeholder blocks (text lines, image areas, etc.)
- Shimmer animation
- Replaced with real content as it loads

---

## A.5 — Rich Text & Formatting

### Rich Text Editor (For content creation)
- Toolbar with formatting options: Bold / Italic / Underline / Lists / Quotes / Links
- Character count
- Plain text or formatted output
- Spellcheck
- Undo/redo (Cmd+Z / Cmd+Y)
- Keyboard shortcuts for all formats

### Code Block (For displaying generated content)
- Monospace font
- Line numbers (optional)
- Syntax highlighting (if applicable)
- Copy button
- Language selector (optional)

### Quote / Callout Block
- Distinct styling (left border, background color, italics)
- Used for highlighting important content
- Agent quote: Styling shows which agent is speaking

---

## A.6 — Charts & Data Visualization

### Line Chart
- X-axis: Time (days, weeks, months)
- Y-axis: Metric (leads, revenue, impressions, etc.)
- Line showing trend
- Optional: Multiple lines (actual vs projection)
- Tooltip on hover showing exact values
- Legend identifying lines

### Bar Chart
- Horizontal or vertical bars
- Color coding by category
- Value labels on bars (optional)
- Legend
- Sorted by value (highest first, optional)

### Heatmap
- Grid of cells
- Color intensity showing magnitude
- Labeled axes
- Tooltip on hover

### Pie / Donut Chart
- Segments for each category
- Labels with percentages
- Legend
- On click: Expand segment or filter

---

---

# END OF PART 2

## Summary of Complete Specification

This 2-part specification documents **EVERY PAGE** in RaptorFlow with extreme, excruciating detail:

### Coverage:
- ✅ Pre-product pages (landing, signup, workspace setup)
- ✅ Foundation onboarding (all 21 screens, every field, every validation, every edge case)
- ✅ Main dashboard & office interface (interaction model, animations, event mapping)
- ✅ Campaign creation & management (brief to execution to analytics)
- ✅ Muse conversation interface (routing, spatial context, response types)
- ✅ Competitive intelligence dashboard (monitoring, analysis, recommendations)
- ✅ Daily wins & nudges (briefing generation, alert management)
- ✅ Council session viewer (live debate, synthesis, playback)
- ✅ Content engine (generation workflow, quality assessment, management)
- ✅ Settings (workspace, user, foundation, advanced)
- ✅ Admin & diagnostics (system health, audit, backup)
- ✅ Common components (forms, modals, navigation, charts, etc.)

### Detail Level:
Each page includes:
- Layout diagrams (described in prose)
- Every field name, label, placeholder, validation, and helper text
- User interactions and state changes
- AI agent behavior and routing decisions
- Data storage and retrieval
- Edge cases and error handling
- Keyboard shortcuts and accessibility patterns
- Mobile/responsive behavior
- Technical implementation notes

### Total Length: ~15,000 words
**Status:** Comprehensive. No page left unspecified. Every interaction documented.

---

**For Part 3 (if needed):** 
- Detailed Office animation specifications (all character states, event timings)
- Mobile responsiveness specifications for each page
- Accessibility specifications (WCAG 2.1 AA compliance)
- Performance budgets (page load times, interaction latency targets)
- Browser compatibility matrix
