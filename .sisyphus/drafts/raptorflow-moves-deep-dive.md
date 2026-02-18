# RaptorFlow: Deep Dive into Moves

## Overview

**Moves** are the core tactical execution unit in RaptorFlow - structured 7-14 day marketing sprints designed to achieve specific business objectives. Think of them as "growth experiments" or "marketing campaigns" with a defined lifecycle, execution plan, and measurable outcomes.

---

## Philosophy & Concept

### The "Choose Your Battles" Approach
RaptorFlow follows a philosophy where the system presents AI-suggested moves (3-5 options), and users commit to only 1-2 at a time. This prevents:
- **Scope creep** from trying to do everything
- **Context switching** between too many initiatives
- **Lack of focus** on what matters most

### Move Lifecycle
```
Draft → Active → (Paused) → Completed
```

1. **Draft** - Created but not started, can be edited freely
2. **Active** - Currently executing, tasks being completed daily
3. **Paused** - Temporarily halted, can be resumed
4. **Completed** - All tasks done, outcome recorded

---

## Data Models

### Core Types (src/components/moves/types.ts)

#### MoveCategory - The 5 Archetypes

```typescript
type MoveCategory = 'ignite' | 'capture' | 'authority' | 'repair' | 'rally';
```

| Category | Icon | Purpose | Use Cases |
|----------|------|---------|-----------|
| **Ignite** | ⚡ Zap (Amber) | Launch & Hype | Product drops, feature releases, major announcements |
| **Capture** | 🧲 Magnet (Blue) | Acquisition & Sales | Lead generation, sales pushes, B2B outreach |
| **Authority** | 👑 Crown (Purple) | Brand & Reputation | Thought leadership, personal branding, trust building |
| **Repair** | 🛡️ Shield (Red) | PR & Crisis | Damage control, addressing bad reviews, fixing mistakes |
| **Rally** | ❤️ Heart (Pink) | Community & Loyalty | Reactivation, referrals, UGC, LTV improvement |

Each category has:
- **Name**: Display name
- **Tagline**: Short descriptor (e.g., "Launch & Hype")
- **Description**: What it achieves
- **useFor**: Array of specific use cases
- **Goal**: The primary objective

#### TaskStatus & TaskItem

```typescript
type TaskStatus = 'pending' | 'in-progress' | 'done' | 'blocked';

interface TaskItem {
    id: string;
    title: string;
    description?: string;
    status: TaskStatus;
    channel?: string;      // e.g., "linkedin", "email", "dm"
    note?: string;         // Optional note added on completion
}
```

#### ExecutionDay - The Daily Structure

```typescript
interface ExecutionDay {
    day: number;              // 1-7 or 1-14
    phase: string;            // e.g., "Setup", "Asset", "Launch", "Distribution"
    pillarTask: TaskItem;     // Core focus task (HIGH effort)
    clusterActions: TaskItem[]; // Supporting tasks (MEDIUM effort)
    networkAction: TaskItem;  // Outreach task (LOW effort)
}
```

**The Three Task Types:**

1. **Pillar Task** (Core Focus)
   - High effort, high impact
   - The "main thing" for that day
   - Must be completed for day success
   - Icon: ⚡ Zap

2. **Cluster Actions** (Amplify)
   - Medium effort supporting tasks
   - Content distribution, asset creation
   - Can be 1-3 tasks depending on time commitment
   - Icon: 🔗 Share2

3. **Network Action** (Outreach)
   - Low effort but consistent
   - Direct messages, emails, calls
   - Usually 5 DMs per day
   - Icon: 💬 MessageSquare

#### Move Interface

```typescript
interface Move {
    id: string;
    name: string;
    category: MoveCategory;
    status: MoveStatus;           // 'draft' | 'active' | 'completed' | 'paused'
    duration: number;             // 7 or 14 days typical
    goal: string;                 // Primary objective statement
    tone: string;                 // e.g., "Professional & Direct"
    context: string;              // Background/situation
    attachments?: string[];       // File references
    createdAt: string;            // ISO timestamp
    startDate?: string;           // When move started
    endDate?: string;             // When move ended
    execution: ExecutionDay[];    // Array of days with tasks
    progress?: number;            // 0-100 completion
    icp?: string;                 // Target Ideal Customer Profile
    campaignId?: string;          // Linked campaign (optional)
    metrics?: string[];           // Success metrics to track
    workspaceId?: string;         // Multi-tenancy
    isLocked?: boolean;           // Prevent editing
}
```

#### MoveBriefData (Creation Output)

```typescript
interface MoveBriefData {
    name: string;
    category: MoveCategory;
    duration: MoveDuration;
    goal: string;
    tone: string;
    strategy: string;      // Compiled strategic summary
    metrics: string[];     // Category-specific metrics
    icp?: string;
}
```

---

## Component Architecture

### 1. MoveCreateWizard (682 lines)
**Purpose**: 4-step wizard for creating new moves

**Steps:**
1. **Objective** (`"objective"`) - Select category from 5 options
2. **Context** (`"context"`) - Choose ICP, describe situation, set time commitment (15m/30m/1h+)
3. **Clarify** (`"clarify"`) - Answer 3 questions:
   - "Why haven't they bought yet?" (resistance)
   - "What is the core offer?" (offer)
   - "What is the ideal outcome?" (outcome)
4. **Preview** (`"preview"`) - Review generated brief and execution plan

**Key Features:**
- Loads cohorts/ICPs from Foundation
- Generates execution plan from templates
- Time commitment affects cluster action count (15m=1, 30m=2, 1h+=3)
- Uses `buildTemplateBrief()` and `buildTemplateExecution()` functions

### 2. MoveGallery (391 lines)
**Purpose**: Grid display of all moves with filtering

**Features:**
- Filter tabs: All, Active, Draft, Completed
- Search by name/category
- Move cards showing:
  - Category icon
  - Name and category
  - Campaign badge (if linked)
  - Progress bar
  - Status badge
  - Day counter (for active moves)
  - Action menu (Start/Pause/Delete)
- Opens MoveIntelCenter in modal on click

### 3. MoveIntelCenter (344 lines)
**Purpose**: Detailed view of a single move

**Two Tabs:**
1. **Strategy Tab**
   - Core objective display
   - Context & rationale
   - Target ICP, Tone, Category
   - Success metrics

2. **Execution Tab**
   - Expandable day cards
   - Each day shows:
     - Phase label
     - Pillar task (highlighted)
     - Cluster actions
     - Network action
   - Progress tracking
   - Complete Move button

### 4. TodaysAgenda (316 lines)
**Purpose**: Aggregated daily task list across ALL active moves

**Key Features:**
- Flattens tasks from all active moves
- Shows only today's tasks (calculated from startDate)
- Progress ring showing completion %
- Task list with:
  - Type icons (pillar/cluster/network)
  - Channel labels
  - Move context
  - Campaign indicators
  - "Ask Muse" quick action
- TaskDetailPopup on click

### 5. TodayView (269 lines)
**Purpose**: Alternative "Battle Card" view of today's tasks

**Features:**
- "Today's Orders" header with date
- Progress stats (completed/total)
- DailyMoveCards showing:
  - Move context
  - Day progress
  - Task rows with type icons
  - Hover actions
- Blueprint Card styling

### 6. ExecutionGrid (159 lines)
**Purpose**: Full 7-day execution plan table

**Structure:**
```
| DAY | PHASE | PILLAR (CORE) | CLUSTER (AMPLIFY) | NETWORK (PUSH) |
```

**Features:**
- Phase color coding (Tease/Reveal/Proof/Urgency/Close/Sustain)
- Task status indicators
- Channel labels
- Effort level legend

### 7. MoveBrief (124 lines)
**Purpose**: Strategy Lock display

**Shows:**
- Category and icon
- Duration, Tone
- Goal statement
- Strategy summary
- Key metrics

### 8. Supporting Components

| Component | Purpose |
|-----------|---------|
| **MoveCategoryIcon** | Renders category icons with colors |
| **MoveCategorySelector** | Grid of 5 category cards with animations |
| **MoveCard** | Simple card for basic move display |
| **MoveCategoryTag** | Badge showing category |
| **MoveIntelOverview** | Stats summary (active/completed/task rate) |
| **TaskDetailPopup** | Modal for individual task details |
| **MovesCalendar** | Calendar view with move bars |
| **MovesCalendarPro** | Enhanced calendar |
| **StatusDot** | Visual status indicator |

---

## State Management (Zustand)

### movesStore.ts

```typescript
interface MovesState {
  moves: Move[];
  pendingMove: Partial<Move> | null;  // Draft move being created
  isLoading: boolean;
  error: string | null;

  // CRUD Operations
  fetchMoves: (workspaceId: string) => Promise<void>;
  addMove: (move: Move, workspaceId: string) => Promise<void>;
  updateMove: (moveId: string, updates: Partial<Move>, workspaceId: string) => Promise<void>;
  deleteMove: (moveId: string, workspaceId: string) => Promise<void>;
  
  // Utility
  cloneMove: (moveId: string, workspaceId: string) => Promise<Move | null>;
  setPendingMove: (move: Partial<Move> | null) => void;
  
  // Selectors
  getMoveById: (moveId: string) => Move | undefined;
  getActiveMoves: () => Move[];
  getCompletedMoves: () => Move[];
  getDraftMoves: () => Move[];
}
```

**Key Patterns:**
- Optimistic updates (UI updates immediately, API syncs in background)
- Rollback on error
- Workspace-scoped (multi-tenancy)
- No Supabase client (uses HTTP service)

---

## API Integration

### moves.service.ts

```typescript
export const movesService = {
  async list(workspaceId: string): Promise<Move[]>
  async create(workspaceId: string, move: Move): Promise<Move>
  async update(workspaceId: string, moveId: string, patch: MovePatch): Promise<Move>
  async delete(workspaceId: string, moveId: string): Promise<void>
}
```

**MovePatch Type:**
```typescript
export type MovePatch = Partial<
  Pick<
    Move,
    | "name" | "category" | "status" | "duration" | "goal" | "tone"
    | "context" | "attachments" | "startDate" | "endDate"
    | "execution" | "progress" | "icp" | "campaignId" | "metrics"
  >
>;
```

**Endpoints:**
- `GET /moves` - List all moves
- `POST /moves` - Create new move
- `PATCH /moves/:id` - Update move
- `DELETE /moves/:id` - Delete move

---

## Execution Plan Generation

### Template System (MoveCreateWizard.tsx)

**Phase Names (7-Day Cycle):**
```typescript
const phases = ["Setup", "Asset", "Launch", "Distribution", "Follow-up", "Optimize", "Review"];
```

**Pillar Task Templates by Category:**

| Day | Ignite | Capture | Authority | Repair | Rally |
|-----|--------|---------|-----------|--------|-------|
| 1 | Define hook + CTA | Define ICP + targets | Pick POV angle | Write truth statement | Define win moment |
| 2 | Draft flagship post | Build offer page | Write long-form post | Create remediation plan | Create activation nudge |
| 3 | Launch flagship | Write outbound sequence | Publish + engage | Publish update | Run community touchpoint |
| 4 | Repurpose to micro-cuts | Send 25 outreaches | Create carousel | Reach out to 10 users | Spotlight 3 user wins |
| 5 | Partner push | Follow up + book calls | Secure distribution partners | Collect feedback | Launch referral/UGC ask |
| 6 | Objection handling | Tighten pitch | Publish case breakdown | Monitor sentiment | Follow-up responders |
| 7 | Review + next sprint | Review pipeline | Review signals | Set prevention guardrails | Review engagement |

**Cluster Actions Template:**
```typescript
const buildClusterActions = (day: number): { title: string; channel: string }[] => {
  const base = [
    { title: `Prep supporting asset for Day ${day}`, channel: "content" },
    { title: "Distribute to your primary channel", channel: "linkedin" },
    { title: "Log results + note what to tweak", channel: "ops" },
  ];
  return base.slice(0, clusterCount); // 1-3 based on time commitment
};
```

**Network Action Template:**
```typescript
const buildNetworkAction = (day: number): { title: string; channel: string } => {
  return {
    title: `DM 5 ${target}${msg} (Day ${day})`,
    channel: "dm"
  };
};
```

---

## Progress Calculation

### Task-Level Progress
```typescript
// In MoveIntelCenter.tsx
const progress = useMemo(() => {
  let total = 0;
  let completed = 0;
  move.execution.forEach(day => {
    total += 1 + (day.clusterActions?.length || 0) + 1; // pillar + clusters + network
    if (day.pillarTask?.status === 'done') completed++;
    day.clusterActions?.forEach(t => { if (t.status === 'done') completed++; });
    if (day.networkAction?.status === 'done') completed++;
  });
  return { completed, total, percentage: Math.round((completed / total) * 100) };
}, [move.execution]);
```

### Today's Tasks (TodaysAgenda)
```typescript
// Calculate day number from startDate
const daysSinceStart = Math.floor(
  (today.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
);
const dayNumber = daysSinceStart + 1;

// Get today's execution
const dayExecution = move.execution[dayNumber - 1];

// Extract all tasks
const tasks: FlattenedTask[] = [];
if (dayExecution.pillarTask) pushTask(dayExecution.pillarTask, 'pillar');
dayExecution.clusterActions?.forEach(t => pushTask(t, 'cluster'));
if (dayExecution.networkAction) pushTask(dayExecution.networkAction, 'network');
```

---

## UI/UX Patterns

### Status Styling
```typescript
const statusConfig = {
  draft: { border: "border-warning/30", bg: "bg-warning/5", text: "text-warning" },
  active: { border: "border-success/30", bg: "bg-success/5", text: "text-success" },
  completed: { border: "border-blueprint/30", bg: "bg-blueprint/5", text: "text-blueprint" },
  paused: { border: "border-muted/30", bg: "bg-muted/5", text: "text-muted" },
};
```

### Task Type Colors
- **Pillar**: Blueprint/Blue (`text-[var(--blueprint)]`)
- **Cluster**: Secondary/Muted (`text-[var(--ink-secondary)]`)
- **Network**: Success/Green (`text-[var(--success)]`)

### Animations (GSAP)
- Card entrance: Staggered fade-in with scale
- Hover effects: Lift + shadow
- Progress bars: Smooth fill transitions
- Day expansion: Slide-down reveal

---

## Integration Points

### With Campaigns
- Moves can be linked to campaigns via `campaignId`
- Campaign badge appears on move cards
- Creates parent-child relationship

### With Muse (AI)
- "Ask Muse" button in TaskDetailPopup
- Pre-fills context with task details
- Routes to `/muse?prompt={encoded_context}`

### With Foundation
- Loads ICPs from Foundation for targeting
- Uses positioning data in move context
- Strategy inherits from foundation

### With Growth Hooks
- Completing moves triggers streaks
- Experiment tracking for growth metrics
- Progress notifications

---

## File Structure

```
src/components/moves/
├── types.ts                    # All type definitions
├── MoveCreateWizard.tsx        # 4-step creation wizard
├── MoveGallery.tsx             # Grid display with filters
├── MoveIntelCenter.tsx         # Detailed move view
├── TodaysAgenda.tsx            # Aggregated daily tasks
├── TodayView.tsx               # Alternative battle card view
├── ExecutionGrid.tsx           # 7-day plan table
├── MoveBrief.tsx               # Strategy display
├── MoveCategoryIcon.tsx        # Category icon component
├── MoveCategorySelector.tsx    # Category selection grid
├── MoveCard.tsx                # Basic card component
├── MoveCategoryTag.tsx         # Category badge
├── MoveIntelOverview.tsx       # Stats overview
├── TaskDetailPopup.tsx         # Task modal
├── MovesCalendar.tsx           # Calendar view
├── MovesCalendarPro.tsx        # Enhanced calendar
└── StatusDot.tsx               # Status indicator

src/stores/
└── movesStore.ts               # Zustand state management

src/services/
└── moves.service.ts            # API client
```

---

## Usage Flow

### Creating a Move
1. User clicks "Create Move"
2. Select category (Ignite/Capture/Authority/Repair/Rally)
3. Choose target ICP from Foundation
4. Describe situation/context
5. Select time commitment (15m/30m/1h+)
6. Answer 3 clarification questions
7. Review generated brief
8. Launch move
9. System creates execution plan
10. Move appears in Today's Agenda

### Executing a Move
1. User views Today's Agenda
2. Sees tasks for current day across all moves
3. Clicks task to view details
4. Marks complete or asks Muse for help
5. Progress updates automatically
6. Next day's tasks unlock after completion

### Completing a Move
1. User clicks "Complete Move" in MoveIntelCenter
2. Confirms completion
3. System records outcome
4. Triggers growth hooks (streaks, achievements)
5. Move moves to "Completed" tab
6. Blackbox logs the decision

---

## Key Design Decisions

1. **Three Task Types**: Pillar/Cluster/Network creates consistent structure
2. **Daily Rhythm**: One day at a time prevents overwhelm
3. **Time Commitment**: 15m/30m/1h+ affects task volume
4. **Category Templates**: Pre-built execution plans reduce decision fatigue
5. **Workspace Scoping**: Multi-tenancy support
6. **Optimistic Updates**: Snappy UI feel
7. **Move-Campaign Link**: Optional relationship for campaign tracking

---

*Document generated from deep codebase analysis*
*Total files analyzed: 20+ components, stores, services*
*Last updated: 2026-02-16*
