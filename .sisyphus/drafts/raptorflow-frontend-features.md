# RaptorFlow Frontend Features Documentation

## Overview

RaptorFlow is a **Marketing Automation OS** built with Next.js 14, featuring an AI-powered campaign orchestration platform. The frontend follows a "quiet luxury" design aesthetic with a paper/canvas color palette and blueprint-inspired visual language.

**Tech Stack:**
- Next.js 14 App Router
- TypeScript
- Tailwind CSS
- GSAP for animations
- Framer Motion
- Zustand for state management
- Supabase for backend

---

## Core Features

### 1. 📊 Dashboard

**Location:** `/dashboard`
**Purpose:** Central command center for marketing operations

**Key Components:**
- **Today's Win Card** - A focused, single high-impact task recommendation that changes daily
  - Shows task title, description, impact level (high/medium/low)
  - Category tags (Foundation, Move, Campaign, Analysis)
  - Actions: Mark Complete or Skip to next win
  - Animations: Cards animate in/out when completed/skipped

- **Metrics Grid** - Quick stats overview:
  - Active Moves
  - Active Campaigns  
  - ICPs Defined
  - Channels

- **Current Focus Section** - Displays the active Move in progress:
  - Progress bar (animated)
  - Tasks completed
  - Days remaining
  - Linked campaigns count
  - Action buttons

- **Foundation Card** - Shows foundation completion status:
  - Positioning (locked/draft)
  - ICPs count
  - Messaging status
  - Lock/Unlock capability

- **Quick Actions** - Links to:
  - Create Move
  - Open Muse
  - View Campaigns

**Data Model:**
```typescript
interface Win {
  id: string;
  title: string;
  description: string;
  impact: "high" | "medium" | "low";
  completed: boolean;
  category: "foundation" | "move" | "campaign" | "analysis";
}
```

---

### 2. ⚡ Moves

**Location:** `/moves`
**Purpose:** Strategic initiative management and tactical execution

**Concept:**
Moves are 7-14 day tactical sprints designed to achieve specific marketing objectives. They follow a "Choose Your Battles" philosophy where the system proposes 3-5 AI-suggested moves, and users commit to 1-2 at a time.

**Key Components:**

#### Move Categories
1. **Ignite** - Launch & Hype (product drops, feature releases)
2. **Capture** - Acquisition & Sales (lead generation, sales pushes)
3. **Authority** - Brand & Reputation (thought leadership, trust building)
4. **Repair** - PR & Crisis (damage control, sentiment management)
5. **Rally** - Community & Loyalty (reactivation, referrals, UGC)

#### Proposed Moves Section
- AI-suggested moves ranked by expected payoff
- Each card shows:
  - Title & Category
  - Expected Payoff (e.g., "+30% signups")
  - Effort Level (Low/Medium/High)
  - Risk Level (Low/Medium/High)
  - Confidence Score (High/Medium/Low)
  - Reasoning tooltip
- Actions: Commit (animated transition to Active) or Dismiss (swipe away)

#### Active Moves Section
- List or Calendar view toggle
- Cards show:
  - Status (Active/Paused/Completed)
  - Progress bar (animated GSAP)
  - Days remaining countdown
  - Linked campaigns count
  - Category icon/color
- Click to open detail modal

#### Move Detail Modal
- Full move information
- Timeline with milestones
- Linked campaigns list
- Evidence panel
- Key assumptions
- Pause/Resume/Edit actions

#### Moves Calendar Component
- Month/Week view toggle
- Visual timeline with colored bars for each move
- Category-based color coding
- Click to view move details
- Today highlight
- GSAP animated transitions

**Data Model:**
```typescript
interface Move {
  id: string;
  name: string;
  category: MoveCategory; // ignite | capture | authority | repair | rally
  status: MoveStatus; // draft | active | completed | paused
  duration: number; // 7 or 14 days typical
  goal: string;
  tone: string;
  context: string;
  execution: ExecutionDay[];
  progress?: number;
  icp?: string;
  campaignId?: string;
  metrics?: string[];
}

interface ExecutionDay {
  day: number;
  phase: string;
  pillarTask: TaskItem;
  clusterActions: TaskItem[];
  networkAction: TaskItem;
}
```

---

### 3. 📢 Campaigns

**Location:** `/campaigns`
**Purpose:** Outcome-linked marketing execution plans

**Concept:**
Campaigns are structured initiatives with defined phases, tasks, and metrics. Each campaign is linked to a Move and tracks progress through Setup → Content → Distribution → Analysis phases.

**Key Components:**

#### Campaign Cards (Timeline View)
- Expandable cards showing:
  - Status badge (Active/Draft/Paused/Completed)
  - Linked Move name
  - Phase progress bar
  - Phase indicator dots
  - Current metric progress (e.g., "156/200 leads")
  - Days until deadline
  - Click to expand and see:
    - Objective statement
    - Hypothesis
    - Start/deadline dates
    - Task checklist with checkboxes

#### Stats Row
- Active campaigns count
- Draft count
- Completed count
- Total count
- Trend indicators

#### List View
- Table view with columns:
  - Campaign name + objective
  - Linked Move
  - Status badge
  - Progress bar
  - Metric (current/target)
  - Deadline

#### Task Management
- Checkbox tasks per phase
- GSAP animated checkmarks
- Status: todo → in-progress → done
- Visual feedback on completion

**Data Model:**
```typescript
interface Campaign {
  id: string;
  name: string;
  moveId: string;
  moveName: string;
  status: "draft" | "active" | "paused" | "completed";
  objective: string;
  metric: {
    name: string;
    target: number;
    current: number;
    unit: string;
  };
  timeline: {
    startDate: Date;
    endDate: Date;
    phases: Phase[];
  };
  tasks: Task[];
  hypothesis: string;
  deadline: Date;
}
```

---

### 4. 💡 Muse (AI Content Assistant)

**Location:** `/muse`
**Purpose:** AI-powered content generation and refinement

**Concept:**
Muse is an AI chat interface that helps create marketing content based on the user's foundation (positioning, ICPs, messaging). It operates in three modes and provides context-aware suggestions.

**Key Components:**

#### Chat Interface
- Message bubbles (user vs assistant)
- Typing indicator animation
- Quick action chips at bottom
- Context panel (collapsible)

#### Three Modes
1. **Chat** - General conversation and brainstorming
2. **Generate** - Create new content from prompts
3. **Refine** - Improve existing copy

#### Quick Actions
- "Write a headline" - Generate headline options
- "Refine this copy" - Improve existing text
- "Generate email" - Create email sequences
- "Create social post" - Platform-specific content

#### AI Response Features
- Confidence level indicator (High/Medium/Low)
- Sources citation (Foundation data used)
- Assumptions listed
- Suggestion chips for next actions
- Copy to clipboard
- Thumbs up/down feedback

#### Context Panel
- Current Move context
- Selected text reference
- Mode-specific options:
  - Use brand voice
  - Include CTA
  - SEO optimized
  - Short form

**Mock Response Examples:**
- Headlines with different angles
- Full email sequences with subject lines
- Launch sequences with week-by-week breakdowns
- Refined copy with change explanations

---

### 5. 📓 Blackbox

**Location:** `/blackbox`
**Purpose:** Decision log and change history

**Concept:**
The Blackbox is a timeline-based audit trail that records all significant decisions, changes, assumptions, and lock/unlock events across the platform. It's like a flight recorder for marketing decisions.

**Key Components:**

#### Timeline View
- Vertical timeline with connector lines
- Chronological entry cards
- Filters by type and module

#### Entry Types
1. **Decision** - Strategic choices made (e.g., "Rescheduled Q2 to Q1")
2. **Change** - Modifications to existing items
3. **Assumption** - Validated or invalidated assumptions
4. **Lock** - Foundation elements locked
5. **Unlock** - Foundation elements unlocked for editing

#### Entry Card Structure
- Type icon and label
- Timestamp
- Module tag (Moves, Foundation, Campaigns, etc.)
- Action description
- Entity name
- Reason (quoted explanation)
- Impact list (affected items)
- Diff viewer (before/after comparison)
- User attribution
- Details button

#### Filters
- By type (Decision/Change/Assumption/Lock)
- By module (Foundation/Moves/Campaigns/etc.)
- Export log functionality

**Data Model:**
```typescript
interface BlackboxEntry {
  id: string;
  type: "decision" | "change" | "assumption" | "lock" | "unlock";
  timestamp: Date;
  user: string;
  module: string;
  entity: string;
  action: string;
  reason: string;
  impact: string[];
  diff?: {
    before: string;
    after: string;
  };
}
```

---

### 6. 🎯 Matrix

**Location:** `/matrix`
**Purpose:** Status dashboard for all initiatives

**Concept:**
Matrix provides a health overview of all moves and campaigns, highlighting what needs attention. It uses a traffic light system for quick status assessment.

**Key Components:**

#### Status Cards
Four summary cards at top:
- **On Track** (green) - Healthy initiatives
- **Stuck** (red) - Blocked items needing help
- **At Risk** (yellow) - Potential issues
- **Needs Decision** (gray) - Awaiting choices

Click to filter initiatives by status.

#### Initiative Cards Grid
Each card shows:
- Type badge (Move/Campaign)
- Status badge
- Initiative name
- Owner name
- Last update time (relative: "Today", "Yesterday", "3 days ago")
- Health score (0-100%) with color-coded bar
- Blockers list (if any)
- Action buttons

**Status Configurations:**
- On Track: Green border, checkmark icon
- Stuck: Red border, alert circle icon, red blockers
- At Risk: Yellow border, warning triangle icon
- Needs Decision: Gray border, help circle icon

---

### 7. 🏗️ Foundation

**Location:** `/foundation`
**Purpose:** Define core positioning, ICPs, and messaging

**Concept:**
Foundation is where users establish their marketing fundamentals before executing campaigns. Elements can be locked once finalized to prevent accidental changes.

**Key Components:**

#### Progress Overview
- Overall completion percentage
- Sections complete counter
- Breakdown by category (Positioning/ICPs/Messaging)

#### Positioning Card
Editable fields (when unlocked):
- Company Name
- Tagline (with AI generate button)
- Value Proposition (with AI generate button)
- Problem Statement
- Solution Statement
- Lock/Unlock toggle with modal confirmation

#### ICPs Section
- Grid of ICP cards
- Each ICP shows:
  - Name
  - Description
  - Firmographics (company size, industry)
  - Pain Points (tag chips)
  - Goals (tag chips)
- Add/Edit/Delete capability (when unlocked)
- GSAP hover animations

#### Messaging Card
Two tabs:
1. **Core Tab:**
   - One-liner (elevator pitch)
   - Elevator Pitch (longer version)
   - Key Messages (numbered list, add/remove)
   - AI generate buttons

2. **Proof Points Tab:**
   - List of claims with evidence type
   - Status (Validated/Pending)
   - Visual indicators

**Lock Mechanism:**
- Sections can be locked to prevent edits
- Locked sections show version number
- Unlock creates a new draft version
- Campaign generation requires locked positioning

---

### 8. 📅 Moves Calendar

**Component:** `MovesCalendar.tsx`
**Purpose:** Visual timeline for move scheduling

**Features:**
- Month/Week view toggle
- Color-coded move bars by category:
  - Growth: Charcoal
  - Retention: Muted ink
  - Positioning: Light border
  - Conversion: Soft accent
- Move title appears on start day
- "+N more" indicator when day has many moves
- Today highlight
- GSAP animated month transitions
- Hover effects on move bars
- Click to view move details

**Empty State:**
- Calendar icon illustration
- "No moves scheduled" message
- Create Move button

---

### 9. 🏆 Growth Hooks & Daily Wins

**Files:** `growth-hooks.ts`, Dashboard "Today's Win" feature

**Concept:**
Gamification elements that encourage consistent usage and celebrate progress.

**Features:**

#### Daily Wins System
- Single high-impact task presented daily
- Categories: Foundation, Move, Campaign, Analysis
- Impact levels: High/Medium/Low
- Actions: Complete (triggers celebration) or Skip (animates away)
- New win loads after completion

#### Experiment Streak
- Tracks consecutive days of experiments run
- Toast notifications:
  - First experiment: "First Experiment Logged! +10 Momentum"
  - Every 3rd experiment: Streak celebration message
  - Regular: "Evidence logged to Black Box"
- Stored in localStorage

#### Move Completion Rewards
- Randomized encouraging messages:
  - "Nice work! Your strategic arc is 5% closer to completion."
  - "Move executed. The engine is refining its next recommendation."
  - "Momentum building. Your execution velocity is in the top 10%."
  - "Surgical execution. ROI data will be available in 48h."

---

## Navigation & Shell

### Sidebar (Paper Terminal Design)
- Fixed left navigation
- Blueprint aesthetic with accent lines
- Navigation items:
  - Onboarding
  - Dashboard
  - Foundation
  - Moves
  - Campaigns
  - Muse (with "AI" badge)
- Secondary: Settings, Help
- Active item indicator with animated accent line
- Workspace switcher with dropdown
- Reset workspace option

### Command Palette (Cmd+K)
- Global search and navigation
- Sections: Modules, System
- Keyboard navigation (arrow keys, Enter)
- Blueprint-inspired border ticks
- Accessible (ARIA labels)

### Breadcrumbs
Context-aware navigation showing path:
- Moves, Campaigns, Muse, Blackbox, Daily Wins, Matrix, etc.

---

## Design System

### Color Palette (Quiet Luxury)
```
--ink-1: #2A2529 (Primary text)
--ink-2: #5C565B (Secondary text)
--ink-3: #847C82 (Muted text)
--bg-canvas: #EFEDE6 (Background)
--bg-surface: #F7F5EF (Card background)
--border-1: #E3DED3 (Borders)
--border-2: #D2CCC0 (Stronger borders)
--status-success: #3D5A42 (Green)
--status-warning: #8B6B3D (Amber)
--status-error: #8B3D3D (Red)
--status-info: #3D5A6B (Blue)
```

### Typography
- Primary: DM Sans (modern sans-serif)
- Technical/Mono: JetBrains Mono (for data, timestamps)
- Serif: Used for brand elements

### Animations (GSAP)
- Page entrance: Staggered reveals
- Card interactions: Hover lift effects
- Progress bars: Smooth fill animations
- State changes: Scale/fade transitions
- Calendar: Month slide transitions

---

## State Management

### Zustand Stores

#### movesStore.ts
- CRUD operations for moves
- Filtering (active, completed, draft)
- Get move by ID
- Workspace-scoped

#### campaignStore.ts
- Campaign CRUD
- Mapping from API format
- Loading/error states

#### foundationStore.ts
- Foundation data persistence
- Lock/unlock state
- Version tracking

#### authStore.ts
- User authentication
- Session management
- Workspace selection

#### notificationStore.ts
- Toast notifications
- Message queue

#### bcmStore.ts
- Business Context Memory
- AI conversation history

---

## Key UX Patterns

### 1. Lock/Unlock System
- Protects finalized foundation elements
- Visual indicators (lock icons, version badges)
- Confirmation modals before locking
- New versions created on unlock

### 2. AI Suggestions
- Confidence scores displayed
- Source attribution
- Multiple options presented
- Easy selection/iteration

### 3. Progress Visualization
- Animated progress bars
- Phase indicators
- Completion percentages
- Trend arrows

### 4. Empty States
- Illustrative icons
- Helpful copy
- Clear CTA buttons
- Context-aware messaging

### 5. Filtering & Views
- Status filters
- View mode toggles (List/Calendar/Timeline)
- Sort options
- Search functionality

---

## Routes Summary

| Route | Feature | Description |
|-------|---------|-------------|
| `/` | Landing Page | Marketing site with GSAP animations |
| `/dashboard` | Dashboard | Overview with daily win and metrics |
| `/foundation` | Foundation | Positioning, ICPs, messaging |
| `/moves` | Moves | Strategic initiative management |
| `/moves?moveId=X` | Move Detail | Specific move view |
| `/campaigns` | Campaigns | Campaign management |
| `/campaigns/[id]` | Campaign Detail | Specific campaign view |
| `/muse` | Muse | AI content assistant |
| `/blackbox` | Blackbox | Decision history log |
| `/matrix` | Matrix | Status dashboard |
| `/settings` | Settings | User preferences |
| `/onboarding` | Onboarding | New user setup flow |

---

## Integration Points

### Backend API
All features communicate with FastAPI backend:
- `/moves` - Move CRUD
- `/campaigns` - Campaign CRUD  
- `/muse/*` - AI generation endpoints
- `/foundation/*` - Foundation data
- `/workspace/*` - Workspace management

### AI Runtime
- LangGraph orchestration
- Vertex AI integration
- Context-aware responses using Foundation data
- Workspace-scoped AI sessions

---

## Future Enhancements (Observed Patterns)

Based on code structure, potential upcoming features:
- **Analytics Dashboard** - Deeper metrics visualization
- **Team Collaboration** - Multiple users per workspace
- **Template Library** - Pre-built move/campaign templates
- **Integration Hub** - Third-party tool connections
- **Advanced AI** - More sophisticated content generation
- **Mobile App** - Responsive mobile experience

---

*Document generated from codebase analysis of RaptorFlow frontend*
*Last updated: 2026-02-16*
