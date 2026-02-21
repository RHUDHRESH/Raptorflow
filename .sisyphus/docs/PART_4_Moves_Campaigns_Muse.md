# PART 4 — MOVES AND CAMPAIGNS: THE TACTICAL EXECUTION LAYER

## 4.1 Overview of Moves and Campaigns Architecture

The Moves and Campaigns system represents the tactical execution layer of RaptorFlow, sitting above the Business Context Model (BCM) and below the Muse AI orchestration engine. Where the BCM provides the strategic brain of the system (business context, ICP profiles, brand voice), and where Muse handles the generative AI aspects (creating content, suggesting strategies), the Moves and Campaigns layer provides the operational framework for executing marketing tactics in a structured, measurable way. This layer translates high-level strategic direction from the BCM into discrete, actionable units of work that can be executed over time, tracked for progress, and measured for effectiveness. The architecture follows a hierarchical organization where Campaigns serve as containers for one or more Moves, providing organizational context and objective alignment, while Moves represent individual tactical efforts with specific goals, durations, and execution plans. This hierarchical structure enables marketing teams to think strategically at the campaign level while maintaining tactical flexibility at the move level, creating a system that supports both top-down strategy alignment and bottom-up tactical innovation.

The separation between Campaigns and Moves reflects a fundamental marketing planning distinction: campaigns answer the question "why are we doing this?" while moves answer the question "what exactly are we doing?" A campaign might be "Q1 Lead Generation Push" with the objective of acquiring new customers, while the Moves within that campaign might include "LinkedIn Thought Leadership Series" to build authority, "Email Nurture Sequence" to capture leads, and "Partner Co-Marketing Initiative" to expand reach. Each Move has its own goal, timeline, and execution plan, but all are aligned under the campaign's strategic objective. This structure enables both aggregate reporting at the campaign level (how are we doing toward our Q1 goals?) and detailed tracking at the move level (is this specific tactical effort working?). The system is designed to support both AI-generated moves (where Muse suggests tactical approaches based on BCM) and manually created moves (where users input their own tactical plans), giving flexibility for different levels of AI augmentation.

## 4.2 Campaign Data Model

### 4.2.1 Database Schema

The campaigns table in Supabase serves as the primary storage for campaign records, with the following schema definition extracted from the canonical migration file. The table includes workspace_id as a mandatory foreign key to workspaces, establishing the tenant isolation required for multi-tenant operation. Each campaign has a title (required), description (optional), and objective field that uses a constrained CHECK to ensure data quality. The objective field accepts exactly six values: 'acquire' for lead generation campaigns, 'convert' for campaigns focused on turning leads into customers, 'launch' for product or feature launch campaigns, 'proof' for social proof and case study campaigns, 'retain' for customer retention and loyalty campaigns, and 'reposition' for brand repositioning or pivot campaigns. These six objectives map to common marketing use cases and enable aggregate reporting by objective type across the platform.

The status field similarly uses a CHECK constraint to enforce valid states: 'planned' indicates the campaign has been created but not yet activated, 'active' indicates the campaign is currently running, 'paused' indicates temporary suspension (can be resumed), 'wrapup' indicates the campaign is in its final phase (typically used for follow-up activities after main execution), and 'archived' indicates the campaign is no longer active but retained for historical reference. Additional fields include bcm_version (recording which version of the BCM was active when the campaign was created or last updated, enabling historical context for AI suggestions), start_date and end_date for temporal planning, budget_allocated and budget_spent for financial tracking, and kpi_targets as a JSONB field for storing objective-specific key performance indicators. The kpi_targets JSONB structure allows each campaign to define its own success metrics without requiring schema changes, supporting the varied nature of different campaign objectives.

```sql
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    objective TEXT DEFAULT 'acquire' CHECK (objective IN ('acquire', 'convert', 'launch', 'proof', 'retain', 'reposition')),
    status TEXT DEFAULT 'planned' CHECK (status IN ('planned', 'active', 'paused', 'wrapup', 'archived')),
    bcm_version INTEGER,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    budget_allocated NUMERIC DEFAULT 0,
    budget_spent NUMERIC DEFAULT 0,
    kpi_targets JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_campaigns_workspace ON campaigns(workspace_id);
CREATE INDEX idx_campaigns_status ON campaigns(workspace_id, status);
```

The table includes two composite indexes for common query patterns: idx_campaigns_workspace enables efficient listing of all campaigns within a workspace, while idx_campaigns_status enables efficient filtering by both workspace and status, supporting common operations like "show all active campaigns in this workspace." The foreign key relationship to workspaces uses ON DELETE CASCADE, ensuring that when a workspace is deleted, all associated campaigns are automatically removed, maintaining referential integrity and preventing orphaned records. The relationship to the BCM through bcm_version is informational only (no foreign key constraint), allowing the system to record which BCM version was active without enforcing strict coupling.

### 4.2.2 Backend API Models

The FastAPI backend defines Pydantic models for request and response handling, ensuring type safety and input validation at the API boundary. The CampaignCreate model defines the required and optional fields for campaign creation, with name as the only required field (mapped to the title column in the database), while description, objective, and status are all optional with sensible defaults. The objective field defaults to 'acquire' if not specified, aligning with the most common campaign objective for new campaigns. The status defaults to 'active' when creating new campaigns, though this can be overridden to 'planned' if the user wants to prepare a campaign before activating it. The objective and status fields are normalized through helper functions that validate against the allowed values and standardize the input (lowercased and stripped of whitespace), returning HTTP 400 errors with descriptive messages if invalid values are provided.

```python
class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[str] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[str] = None

class CampaignOut(BaseModel):
    id: str
    workspace_id: str
    title: str
    description: Optional[str] = None
    objective: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
```

The CampaignOut model defines the response shape for all campaign read operations, including the id (returned as a string for JSON compatibility), workspace_id (enabling clients to verify workspace context), title, description, objective, status, and timestamps. The created_at and updated_at fields are optional in the model to accommodate database records that might not have these values populated (though they default to now() in the schema). The API returns campaigns through the terminal_adapter which handles the actual database operations, abstracting the storage layer and enabling future changes to the persistence mechanism without modifying the API routes.

### 4.2.3 API Routes

The campaigns router exposes six endpoints for full CRUD (Create, Read, Update, Delete) plus a special endpoint for retrieving a campaign with its associated moves. All endpoints require a valid X-Workspace-Id header for tenant scoping, and all enforce the BCM readiness check through the workspace_guard module, ensuring that campaigns can only be created or manipulated after the workspace has completed onboarding and has a valid BCM. The GET /campaigns/ endpoint returns a paginated list of all campaigns in the workspace, filtered by the workspace_id from the header. The POST /campaigns/ endpoint creates a new campaign with the provided fields, returning the created campaign with its generated ID and timestamps. The GET /campaigns/{campaign_id} endpoint retrieves a single campaign by ID, returning 404 if not found. The PATCH /campaigns/{campaign_id} endpoint allows partial updates to existing campaigns, validating that only allowed fields are modified. The DELETE /campaigns/{campaign_id} endpoint removes a campaign, returning 204 No Content on success. The GET /campaigns/{campaign_id}/moves-bundle endpoint is a special endpoint that returns both the campaign and all associated moves in a single response, reducing the number of round-trips needed for the common UI pattern of viewing campaign details with its moves.

```python
@router.get("/", response_model=CampaignListOut)
async def list_campaigns(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignListOut:
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)
    # Returns all campaigns for the workspace

@router.post("/", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreate,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignOut:
    # Creates a new campaign

@router.get("/{campaign_id}/moves-bundle", response_model=CampaignMovesBundleOut)
async def get_campaign_moves_bundle(
    campaign_id: str,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignMovesBundleOut:
    # Returns campaign with all its moves
```

### 4.2.4 Frontend Store

The frontend campaign store (campaignStore.ts) uses Zustand for state management, following the same pattern as other stores in the application. The store maintains an array of Campaign objects, loading state, and error state, providing actions for fetching, creating, updating, and deleting campaigns. The Campaign type definition on the frontend includes id, title, description, objective, status, createdAt, and updatedAt fields, mapping from the API response (which uses snake_case for some fields) to camelCase for consistency with TypeScript conventions. The store includes a mapper function that transforms API responses into the frontend type, handling nullable fields and providing defaults where needed. The getCampaignById selector enables looking up a campaign by its ID from the cached state, supporting scenarios where the UI needs to display campaign details without making an additional API call.

```typescript
export type Campaign = {
  id: string;
  title: string;
  description: string;
  objective: string;
  status: string;
  createdAt?: string;
  updatedAt?: string;
};

type CampaignStore = {
  campaigns: Campaign[];
  isLoading: boolean;
  error: string | null;
  fetchCampaigns: (workspaceId: string) => Promise<void>;
  createCampaign: (workspaceId: string, input: CreateCampaignInput) => Promise<Campaign>;
  updateCampaign: (workspaceId: string, campaignId: string, patch: UpdateCampaignInput) => Promise<Campaign>;
  deleteCampaign: (workspaceId: string, campaignId: string) => Promise<void>;
  getCampaignById: (campaignId: string) => Campaign | undefined;
};
```

## 4.3 Move Data Model

### 4.3.1 Database Schema

The moves table serves as the core entity for tactical marketing execution, with a more complex schema than campaigns to support the varied nature of marketing tactics. The table includes workspace_id as the primary tenant isolation key, campaign_id as an optional foreign key linking the move to a parent campaign (the relationship is optional because moves can exist independently of campaigns), title as the required name of the move, and description for additional context. The goal field uses a CHECK constraint to define the objective of the move, with options including 'leads' for lead generation, 'calls' for booking calls or meetings, 'sales' for direct revenue, 'proof' for building social proof, 'distribution' for content distribution, and 'activation' for customer activation or re-engagement. These goal values represent the primary business outcome the move is designed to achieve, enabling aggregate reporting on which types of outcomes are being pursued.

The channel field specifies the primary marketing channel for the move, with CHECK constraints enforcing valid values: 'linkedin' for LinkedIn content and outreach, 'email' for email marketing campaigns, 'instagram' for Instagram content, 'whatsapp' for WhatsApp messaging, 'cold_dm' for cold direct messages (typically on social platforms), 'partnerships' for partner/co-marketing activities, and 'twitter' for Twitter/X content. The channel field is important for Muse AI suggestions, as the AI needs to know which channel to optimize content for, and for reporting on channel effectiveness across the workspace. The status field uses another CHECK constraint with values 'draft' (created but not yet activated), 'queued' (ready to start but waiting for execution trigger), 'active' (currently executing), 'completed' (successfully finished), and 'abandoned' (stopped before completion). These statuses enable tracking the lifecycle of each move from creation through completion.

```sql
CREATE TABLE moves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    goal TEXT DEFAULT 'leads' CHECK (goal IN ('leads', 'calls', 'sales', 'proof', 'distribution', 'activation')),
    channel TEXT DEFAULT 'email' CHECK (channel IN ('linkedin', 'email', 'instagram', 'whatsapp', 'cold_dm', 'partnerships', 'twitter')),
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'queued', 'active', 'completed', 'abandoned')),
    priority INTEGER DEFAULT 3 CHECK (priority >= 1 AND priority <= 5),
    icp_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL,
    bcm_version INTEGER,
    duration_days INTEGER DEFAULT 7,
    start_date TIMESTAMPTZ,
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    hypothesis TEXT,
    action_steps TEXT[] DEFAULT '{}',
    execution_result JSONB DEFAULT '{}',
    tool_requirements JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

Additional fields include priority (1-5 scale for indicating relative importance or urgency), icp_id (linking the move to a specific Ideal Customer Profile for targeted messaging), bcm_version (recording the BCM version for context), duration_days (defaulting to 7 days but configurable for different tactical approaches), start_date and due_date for temporal planning, completed_at for recording when the move finished, hypothesis for documenting the strategic assumption the move is testing, action_steps as a TEXT[] array for storing the ordered list of actions to take, execution_result as JSONB for storing the outcome data including generated content and performance metrics, and tool_requirements as JSONB for storing the AI-generated tactical plan (this is where the Move execution details are stored, see Section 4.4 for details). The tool_requirements JSONB field is particularly important as it stores the structured output from Muse AI when generating move execution plans, containing the day-by-day tactical activities.

### 4.3.2 Frontend Type Definitions

The frontend TypeScript definitions provide a richer model than the database schema alone, extending the core fields with additional properties needed for UI rendering and state management. The Move interface includes all database fields plus frontend-specific computed values and nested structures. The category field is a TypeScript enum with five values: 'ignite' for maximum noise campaigns (product drops, store openings, feature releases), 'capture' for acquisition and sales campaigns, 'authority' for brand and reputation building, 'repair' for crisis management and damage control, and 'rally' for community and loyalty campaigns. These categories provide a higher-level classification than goals, enabling users to quickly understand the strategic intent of a move. The execution field is an array of ExecutionDay objects representing the day-by-day execution plan, while progress is a computed percentage (0-100) indicating how much of the execution plan has been completed.

```typescript
export type MoveCategory = 'ignite' | 'capture' | 'authority' | 'repair' | 'rally';

export interface MoveCategoryInfo {
    id: MoveCategory;
    name: string;
    tagline: string;
    description: string;
    useFor: string[];
    goal: string;
}

export const MOVE_CATEGORIES: Record<MoveCategory, MoveCategoryInfo> = {
    ignite: {
        id: 'ignite',
        name: 'Ignite',
        tagline: 'Launch & Hype',
        description: 'Maximum noise in a short window',
        useFor: ['New product drops', 'Store openings', 'Feature releases', 'Major announcements'],
        goal: 'Maximum noise in a short window',
    },
    capture: {
        id: 'capture',
        name: 'Capture',
        tagline: 'Acquisition & Sales',
        description: 'Direct revenue or qualified leads',
        useFor: ['Increasing footfall', 'Getting B2B leads', 'Closing end-of-quarter sales'],
        goal: 'Direct revenue or qualified leads',
    },
    authority: {
        id: 'authority',
        name: 'Authority',
        tagline: 'Brand & Reputation',
        description: 'Mindshare and credibility',
        useFor: ['Thought leadership', 'Personal branding', 'Building trust'],
        goal: 'Mindshare and credibility',
    },
    repair: {
        id: 'repair',
        name: 'Repair',
        tagline: 'PR & Crisis',
        description: 'Damage control and sentiment shift',
        useFor: ['Handling bad reviews', 'Addressing controversy', 'Fixing public mistakes'],
        goal: 'Damage control and sentiment shift',
    },
    rally: {
        id: 'rally',
        name: 'Rally',
        tagline: 'Community & Loyalty',
        description: 'Deepen relationships with existing users',
        useFor: ['Reactivating old customers', 'Increasing LTV', 'Driving referrals/UGC'],
        goal: 'Deepening relationships with existing users',
    },
};
```

The ExecutionDay interface represents a single day's tactical activities within a move, with fields for day number, phase name, pillarTask (the main task for the day), clusterActions (additional supporting tasks), and networkAction (networking or distribution task). The TaskItem interface defines individual tasks with id, title, description, status (pending, in-progress, done, blocked), channel (which platform or medium), and note (optional completion notes added by users). This hierarchical structure enables detailed day-by-day planning and tracking of marketing tactics, with each day having a primary focus (pillarTask) supported by secondary activities (clusterActions) and distribution activities (networkAction).

```typescript
export interface ExecutionDay {
    day: number;
    phase: string;
    pillarTask: TaskItem;
    clusterActions: TaskItem[];
    networkAction: TaskItem;
}

export interface TaskItem {
    id: string;
    title: string;
    description?: string;
    status: TaskStatus;
    channel?: string;
    note?: string;
}

export type MoveStatus = 'draft' | 'active' | 'completed' | 'paused';
export type MoveDuration = number;

export interface Move {
    id: string;
    name: string;
    category: MoveCategory;
    status: MoveStatus;
    duration: MoveDuration;
    goal: string;
    tone: string;
    context: string;
    attachments?: string[];
    createdAt: string;
    startDate?: string;
    endDate?: string;
    execution: ExecutionDay[];
    progress?: number;
    icp?: string;
    campaignId?: string;
    metrics?: string[];
    workspaceId?: string;
    isLocked?: boolean;
}
```

### 4.3.3 Backend API Models

The backend MoveModel Pydantic class defines the API contract for move operations, with all fields matching the frontend type where applicable. The model includes all required fields (id, name, category, status, duration, goal, tone, context, createdAt) and optional fields (attachments, startDate, endDate, execution, progress, icp, campaignId, metrics, workspaceId). The execution field is defined as List[Dict[str, Any]] to accommodate the flexible JSON structure of execution plans. The attachments field is an optional list of strings for storing references to attached files or assets. The MovePatch model defines the allowed fields for partial updates, using Optional types for all fields to support PATCH semantics where only specified fields are updated.

```python
class MoveModel(BaseModel):
    id: str
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    status: str
    duration: int
    goal: str
    tone: str
    context: str
    attachments: Optional[List[str]] = None
    createdAt: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    execution: List[Dict[str, Any]] = Field(default_factory=list)
    progress: Optional[int] = None
    icp: Optional[str] = None
    campaignId: Optional[str] = None
    metrics: Optional[List[str]] = None
    workspaceId: Optional[str] = None
```

### 4.3.4 API Routes

The moves router exposes four primary endpoints: list all moves, create a new move, update an existing move, and delete a move. All endpoints require X-Workspace-Id header and enforce BCM readiness. The list endpoint returns all moves for the workspace, with validation to skip malformed moves that fail schema parsing (preventing a single corrupt record from breaking the entire list). The create endpoint accepts a complete MoveModel and returns the created move with assigned ID. The update endpoint accepts a MovePatch with optional fields and performs partial update semantics. The delete endpoint removes a move by ID, returning 204 No Content on success. All UUID parameters are validated before being passed to the service layer, returning 400 Bad Request for invalid UUID format.

```python
@router.get("/", response_model=MoveListOut)
async def list_moves(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> MoveListOut:
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)
    # Returns all moves for workspace

@router.post("/", response_model=MoveModel, status_code=status.HTTP_201_CREATED)
async def create_move(
    move: MoveModel,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> MoveModel:
    # Creates a new move

@router.patch("/{move_id}", response_model=MoveModel)
async def update_move(
    move_id: str,
    patch: MovePatch,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> MoveModel:
    # Updates an existing move

@router.delete("/{move_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_move(
    move_id: str,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
):
    # Deletes a move
```

### 4.3.5 Frontend Store

The movesStore.ts provides comprehensive state management for moves, implementing optimistic updates for better UX. The store maintains the moves array, a pendingMove field for wizard state, loading state, and error state. The fetchMoves action retrieves all moves for a workspace, the addMove action creates a new move with optimistic update (adding to the local array immediately before the API call), the updateMove action updates a move in place optimistically, and the deleteMove action removes a move optimistically. If any API call fails, the store reverts to the previous state, maintaining consistency between UI and backend. The cloneMove action enables duplicating an existing move, creating a copy with a new ID, "(Copy)" appended to the name, reset status to draft, cleared dates, and zero progress—useful for creating variations of successful moves or templates.

```typescript
interface MovesState {
  moves: Move[];
  pendingMove: Partial<Move> | null;
  isLoading: boolean;
  error: string | null;
  fetchMoves: (workspaceId: string) => Promise<void>;
  addMove: (move: Move, workspaceId: string) => Promise<void>;
  updateMove: (moveId: string, updates: Partial<Move>, workspaceId: string) => Promise<void>;
  deleteMove: (moveId: string, workspaceId: string) => Promise<void>;
  cloneMove: (moveId: string, workspaceId: string) => Promise<Move | null>;
  setPendingMove: (move: Partial<Move> | null) => void;
  getMoveById: (moveId: string) => Move | undefined;
  getActiveMoves: () => Move[];
  getCompletedMoves: () => Move[];
  getDraftMoves: () => Move[];
}
```

## 4.4 Move Execution Engine

### 4.4.1 Execution Day Structure

The move execution system is built around the concept of ExecutionDay, a structured representation of tactical activities for a single day within a move's duration. Each ExecutionDay contains a phase string (describing the strategic phase of the day, such as "Awareness," "Consideration," "Conversion," or "Retention"), a pillarTask (the primary focus task for the day), clusterActions (supporting tasks that reinforce the pillar task), and a networkAction (distribution or networking task for amplifying reach). This structure reflects the marketing principle that effective campaigns need primary activities, supporting activities, and distribution activities to succeed. The pillarTask represents the main "thing to do" on that day, while clusterActions represent additional tactical activities that support the pillar, and networkAction represents how the day's output will be distributed or amplified.

The phase progression through a move typically follows a strategic arc: early days focus on awareness and engagement (getting attention, building interest), middle days focus on consideration and conversion (deepening interest, driving action), and later days focus on retention and amplification (ensuring satisfaction, encouraging advocacy). This phased approach enables moves to feel like cohesive campaigns rather than random collections of tasks. The phase names are stored as strings to allow flexibility in how users or AI define the strategic narrative, though common patterns emerge from successful moves. The system does not enforce specific phase names, enabling users to customize the strategic narrative to their specific tactics while maintaining the structural benefits of phased execution.

```typescript
// Example ExecutionDay structure
{
    day: 1,
    phase: "Awareness",
    pillarTask: {
        id: "pillar-001",
        title: "Publish LinkedIn launch post",
        description: "Create and publish the initial announcement post about the new feature",
        status: "pending",
        channel: "linkedin"
    },
    clusterActions: [
        {
            id: "cluster-001",
            title: "Design visual asset",
            description: "Create supporting graphic for the launch post",
            status: "pending",
            channel: "design"
        },
        {
            id: "cluster-002",
            title: "Prepare internal team notification",
            description: "Draft message to encourage internal amplification",
            status: "pending",
            channel: "email"
        }
    ],
    networkAction: {
        id: "network-001",
        title: "Share in relevant LinkedIn groups",
        description: "Post to 3-5 relevant industry groups",
        status: "pending",
        channel: "linkedin"
    }
}
```

### 4.4.2 Task Status Flow

Each TaskItem has a status field that tracks its lifecycle: 'pending' indicates the task has been created but not yet started, 'in-progress' indicates the task is currently being worked on, 'done' indicates the task has been completed, and 'blocked' indicates the task cannot proceed due to a dependency or obstacle. The status transitions are managed both by the frontend (for user-initiated changes) and potentially by the execution engine (for AI-managed moves). The progress percentage for a move is calculated by counting the number of tasks in 'done' status divided by the total number of tasks across all execution days, providing a simple but effective measure of execution completion.

When a user marks a task as complete, they can optionally add a note (the note field on TaskItem) documenting what was done, lessons learned, or results achieved. This note becomes part of the execution history and can be used for future optimization or reflection. The blocked status is particularly important for complex moves with dependencies—when a pillar task is blocked, it typically cascades to blocking the network action (since there's nothing to distribute), though cluster actions might continue independently. Users can add notes when blocking a task to document the reason, helping with later analysis of what obstacles occurred.

### 4.4.3 Progress Tracking

The progress field on Move is a computed value (though stored in the database for efficiency) representing the percentage of completion. The calculation sums all tasks across all execution days, counts those marked as 'done', and divides by the total. A move with 21 tasks (3 tasks per day across 7 days) where 7 tasks are done would have progress of 33%. This simple metric provides an at-a-glance view of move execution status, though it treats all tasks as equal weight. Future enhancements might support weighted progress calculation based on task importance or time allocation.

The progress is stored in the database as an integer (0-100) to enable efficient queries and sorting without computing on-the-fly. The frontend updates progress both when individual tasks change status and when execution days are added or removed. The startDate and endDate fields, when populated, enable calendar views and deadline tracking. The due_date field in the database schema serves as an alternative to endDate for simpler deadline tracking, while completed_at records the actual completion timestamp when the move status transitions to 'completed'.

## 4.5 Move Creation Workflow

### 4.5.1 Move Wizard

The MoveCreateWizard component guides users through a multi-step process for creating new moves. The wizard follows a four-step structure defined by the WizardStep type: 'category' for selecting the move category (ignite, capture, authority, repair, rally), 'context' for providing business context and attachments, 'brief' for defining the strategic brief (name, goal, tone, metrics), and 'preview' for reviewing and confirming the move creation. This wizard pattern ensures users provide all necessary information for effective move execution while breaking the complexity into manageable steps. The wizard state is maintained in the store's pendingMove field, allowing users to navigate back and forth between steps without losing their inputs.

```typescript
export type WizardStep = 'category' | 'context' | 'brief' | 'preview';

export interface MoveWizardState {
    step: WizardStep;
    category: MoveCategory | null;
    context: string;
    attachments: File[];
    brief: MoveBriefData | null;
    isLoading: boolean;
}

export interface MoveBriefData {
    name: string;
    category: MoveCategory;
    duration: MoveDuration;
    goal: string;
    tone: string;
    strategy: string;
    metrics: string[];
    icp?: string;
}
```

### 4.5.2 Category Selection

The category selection step presents users with the five move categories (Ignite, Capture, Authority, Repair, Rally), each with its tagline, description, use cases, and goal. The MoveCategorySelector component renders these options in a visually appealing way, helping users understand which category fits their tactical needs. The category selection determines the strategic framing of the move and influences AI suggestions for execution plans. Each category has specific use cases: Ignite for launches and announcements, Capture for sales and lead generation, Authority for thought leadership, Repair for crisis management, and Rally for community building. The category also influences default parameters for AI-generated execution plans, such as intensity level and channel preferences.

### 4.5.3 Context and Brief

The context step collects the business context for the move, including a free-text description of the situation, any relevant background information, and file attachments that provide additional context (such as product screenshots, competitor materials, or brand guidelines). This context is passed to Muse AI when generating execution plans, ensuring the AI has relevant information for creating tailored tactics. The brief step defines the strategic parameters of the move: name (a descriptive title), category (from previous step), duration (how long the move will run, typically 7 or 14 days), goal (what outcome the move aims to achieve), tone (the communication tone to use, such as "professional," "casual," "urgent," or "educational"), strategy (a narrative description of the approach), metrics (how success will be measured), and optionally icp (which Ideal Customer Profile to target).

### 4.5.4 AI-Generated Execution Plans

When users complete the wizard, they have the option to generate an AI-powered execution plan using Muse. The AI analyzes the move's category, goal, context, and brief to produce a structured execution plan—a series of ExecutionDay objects with pillarTask, clusterActions, and networkAction for each day. This AI generation is optional; users can create moves manually without AI assistance. However, the AI-generated plans provide significant value by offering structured tactical approaches based on best practices for each category and goal combination. Users can review, modify, and approve the AI-generated plan before activating the move, maintaining human oversight while benefiting from AI assistance.

The AI generation process involves sending the move context to the Muse orchestration engine (described in detail in Part 6), which uses the workspace's BCM and the move's strategic parameters to generate an appropriate execution plan. The generated plan is stored in the tool_requirements JSONB field in the database, while also being parsed into the execution array for UI display and interaction. This dual storage ensures compatibility with both the AI system's expectations (JSONB for flexible schema) and the UI's expectations (structured array for rendering).

## 4.6 Campaign-Move Relationship

### 4.6.1 Hierarchical Organization

Campaigns serve as organizational containers for moves, providing strategic context and enabling aggregate reporting. A campaign can contain zero or more moves (though typically at least one), and a move can belong to zero or one campaign (though typically one when part of a coordinated effort). The relationship is optional on both sides, enabling flexibility in how users organize their marketing activities. Some moves might be standalone tactical experiments not tied to a specific campaign, while others might be tightly integrated into campaign execution. The campaign_id field on moves provides the link, and the moves can be queried either independently or within their campaign context.

### 4.6.2 Bundle Endpoint

The GET /campaigns/{campaign_id}/moves-bundle endpoint provides a convenient way to retrieve both a campaign and its associated moves in a single request. This endpoint is designed for the common UI pattern where a user views a campaign's detail page and wants to see all related moves without making separate API calls. The response includes the campaign object (if found) and an array of move objects, enabling efficient data loading for campaign-centric views. The endpoint enforces the same BCM readiness and workspace validation as other endpoints.

```python
@router.get("/{campaign_id}/moves-bundle", response_model=CampaignMovesBundleOut)
async def get_campaign_moves_bundle(
    campaign_id: str,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignMovesBundleOut:
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)
    bundle = await terminal_adapter.campaign_moves_bundle(workspace_id, campaign_id)
    # Returns { campaign: CampaignOut, moves: List[Dict] }
```

### 4.6.3 Cross-Entity Reporting

The campaign-move relationship enables reporting at multiple levels: individual move performance (is this tactical execution working?), campaign performance (is this coordinated effort achieving its objective?), and aggregate workspace performance (which objectives and channels are most effective?). The BCM version tracking on both entities enables historical analysis of how context changes affected marketing outcomes. The KPI targets stored at the campaign level provide targets against which move performance can be measured, while individual move metrics (stored in the metrics array on Move) track tactical-level outcomes.

## 4.7 Move Components UI Architecture

### 4.7.1 Component Overview

The frontend includes numerous components for viewing, editing, and managing moves. The main components include MoveCard (summary card for move lists), MoveBrief (the strategic brief display), MoveCategoryTag (visual indicator of category), MoveCategorySelector (for wizard category selection), MoveCategoryIcon (visual icon for categories), MoveCreateWizard (multi-step creation flow), MoveIntelCenter (analytics and insights view), MoveIntelOverview (summary analytics), MoveGallery (grid view of moves), MovesCalendar (calendar view of move schedules), MovesCalendarPro (enhanced calendar), ExecutionGrid (execution day grid), TaskDetailPopup (task editing), TodaysAgenda (today's tasks), TodayView (daily execution view), StatusDot (visual status indicator), and various other utility components. This component architecture supports multiple view modes (list, grid, calendar, agenda) and interaction patterns (viewing, editing, creating, executing).

### 4.7.2 Move Card and Gallery

The MoveCard component displays a summary of a single move in list or grid contexts, showing the move name, category tag, status indicator, progress bar, goal, duration, and key dates. The MoveGallery component renders a grid of MoveCard components, supporting filtering by status, category, campaign, and other criteria. The gallery supports various layouts and sort options, enabling users to find and manage moves efficiently. The component uses the MoveCategoryTag and StatusDot sub-components for consistent visual language across the application.

### 4.7.3 Calendar Views

The MovesCalendar and MovesCalendarPro components provide temporal visualization of moves, displaying moves on a calendar grid with their scheduled dates. The calendar shows move duration as colored blocks spanning their start and end dates, enabling users to visualize their marketing schedule and identify gaps or overlaps. The Pro version includes additional features such as drag-and-drop rescheduling, conflict detection, and integration with external calendars. The calendar is particularly useful for planning and coordination, showing at a glance what tactical activities are scheduled when.

### 4.7.4 Execution Interface

The ExecutionGrid and TodayView components provide the primary interface for executing moves day-by-day. The ExecutionGrid displays the full execution plan as a grid with days as columns and task types (pillar, cluster, network) as rows, providing a comprehensive view of the entire move's tactical plan. The TodayView focuses on the current day's tasks, showing only the ExecutionDay objects for today with quick actions for marking tasks complete, adding notes, and viewing details. This focused interface reduces cognitive load during execution, presenting users with exactly what they need to do today without overwhelming them with the full plan.

## 4.8 Data Flow Architecture

### 4.8.1 Create Flow

The create flow begins with the user initiating a new move through the MoveCreateWizard. As the user progresses through the wizard steps (category, context, brief, preview), the state is accumulated in the pendingMove field of the movesStore. When the user confirms creation, the store's addMove action is called, which performs an optimistic update (adding the move to the local array immediately for responsive UI) before calling the movesService.create API. The API call posts to the backend /moves/ endpoint with the complete MoveModel, where the terminal_adapter.create_move function handles persistence to Supabase. If the API call fails, the store reverts the optimistic update and displays an error message. If AI execution planning is requested, an additional call to the Muse service generates the execution plan, which is stored in the tool_requirements field.

### 4.8.2 Update Flow

Updates flow through the updateMove action, which similarly performs optimistic updates for responsive UI. The action accepts the move ID, the updates object (partial Move), and the workspace ID. The updates are applied to the local moves array immediately, then the API call (via movesService.update) sends the PATCH request to /moves/{move_id}. Task status updates within the execution array are handled as nested updates within the execution field. For example, marking a task as done would involve updating the specific ExecutionDay and TaskItem within the execution array. The backend validates the update and returns the updated move, which confirms the local state matches the server.

### 4.8.3 Delete Flow

The delete flow removes a move from the local array immediately (optimistic), then calls the API to confirm deletion. If the API call fails, the move is restored to the local array. Deleting a move does not automatically delete associated assets or attachments; those remain in the assets table until explicitly deleted. If the move was associated with a campaign, the campaign_id is set to NULL (due to ON DELETE SET NULL foreign key behavior), preserving the move for historical purposes while removing the campaign association.

---

## PART 5 — MUSE AI ORCHESTRATION ENGINE

## 5.1 Overview of the AI Architecture

The Muse AI Orchestration Engine (often referred to simply as "Muse" or the "AI Hub") is the generative AI layer of RaptorFlow, responsible for producing content, suggesting strategies, generating execution plans, and learning from feedback. The architecture is designed around three core principles: BCM-first context assembly (all AI operations are informed by the Business Context Model), bounded tool calling (AI can only use defined tools with strict policies), and multi-execution modes (different orchestration strategies for different complexity levels). The engine is built using LangGraph for workflow orchestration, Vertex AI (or generative AI API key) as the primary LLM backend, and a layered system of context assembly, planning, execution, and reflection.

The AI Hub is organized into several packages within the backend/ai/ directory: the hub/ package contains the core orchestration logic, the backends/ package contains LLM backend implementations, the prompts/ package contains prompt engineering templates, the orchestration/ package contains execution strategies, and the profiles/ package contains AI personality configurations. This modular architecture enables different AI behaviors for different use cases (content generation vs. strategic planning vs. critique) while sharing core infrastructure. The engine is designed to be backend-agnostic, supporting Vertex AI, Google GenAI API key, and deterministic fallback modes, enabling operation in various environments with different capability requirements.

## 5.2 Execution Modes

### 5.2.1 Single Mode

The SINGLE execution mode is the simplest and fastest mode, where a single LLM call handles the entire request. The model receives the full context (BCM + user prompt + tool definitions) in a single prompt and generates a complete response. This mode is appropriate for straightforward tasks like generating a social media post, writing email copy, or answering simple questions about the business. The trade-off is that complex multi-step reasoning must fit within a single prompt, limiting the model's ability to iterate or validate its work. Single mode uses the lowest amount of tokens and incurs the lowest cost, making it the default for routine content generation tasks.

The mode is defined in the ExecutionMode enum in types.py:

```python
class ExecutionMode(str, Enum):
    SINGLE = "single"
    COUNCIL = "council"
    SWARM = "swarm"
```

### 5.2.2 Council Mode

The COUNCIL execution mode runs multiple LLM calls in a structured debate format, where different "voices" or perspectives are invited to contribute to the response. The council typically includes a primary drafter, a critic/reviewer, and sometimes additional specialist voices (a data analyst for metrics-focused tasks, a brand guardian for voice consistency, a competitor analyst for market context). The mode is appropriate for tasks requiring nuanced judgment or where multiple perspectives improve quality, such as strategic recommendations, content with complex constraints, or sensitive communications. The council produces a synthesized response that incorporates the best elements from each voice. This mode uses more tokens than single mode but produces higher quality output for complex tasks.

### 5.2.3 Swarm Mode

The SWARM execution mode is the most sophisticated and token-intensive, involving multiple agents working in parallel on subtasks that are then synthesized. In swarm mode, different specialized agents (researcher, drafter, editor, validator) work simultaneously on different aspects of a complex task, with a coordinator agent synthesizing their outputs. This mode is appropriate for highly complex tasks like generating comprehensive marketing strategies, creating multi-channel campaign plans, or producing detailed reports. The swarm mode provides the highest quality output for complex tasks but requires significantly more tokens and time to complete.

### 5.2.4 Intensity and Reasoning Depth

Beyond execution mode, the system supports intensity levels (LOW, MEDIUM, HIGH) and reasoning depth levels (LOW, MEDIUM, HIGH) that affect model behavior. Intensity controls the creativity/temperature parameter and the thoroughness of output, with LOW producing more conservative, predictable outputs and HIGH producing more creative, varied outputs. Reasoning depth controls how much internal reasoning the model performs before producing output, with LOW producing faster but potentially less thoughtful responses and HIGH producing more thorough analysis at the cost of speed. These parameters are combined with execution mode to provide fine-grained control over AI behavior for different task requirements.

```python
class IntensityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ReasoningDepth(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

## 5.3 Context Assembly

### 5.3.1 BCM-First Layering

The AI Hub implements a context assembly system called "BCM-first layering," where the Business Context Model serves as the foundation for all AI operations. Before any LLM call, the system assembles a context bundle containing relevant portions of the BCM, user input, conversation history, and tool definitions. The context is layered with the most foundational information at the bottom (BCM core), domain-specific context in the middle (foundations, ICPs), and task-specific information at the top (user prompt, recent interactions). This layering ensures the AI always has appropriate context while managing token limits by prioritizing relevant information.

The context assembly is handled by the context_engine module, which implements logic for selecting which BCM components to include based on the task type. For content generation tasks, the system includes brand voice, messaging guidelines, and relevant ICP profiles. For strategic planning tasks, the system includes competitive landscape, business objectives, and historical performance data. The context engine also handles summarization of long BCM components when needed to fit within token limits, using its own LLM calls to compress context while preserving key information.

### 5.3.2 ContextBundle and ContextNode

The context assembly uses structured data types defined in the hub contracts:

```python
@dataclass
class ContextNodeV1:
    node_type: str  # e.g., "bcm", "foundation", "icp", "conversation"
    node_id: str
    content: str
    relevance_score: float
    source: str  # where this node came from
    metadata: Dict[str, Any]

@dataclass
class ContextBundleV1:
    workspace_id: str
    nodes: List[ContextNodeV1]
    assembled_at: datetime
    token_count: int
    truncated: bool
```

The ContextNode represents a single piece of assembled context, with a type, ID, content, relevance score (how relevant this node is to the current task), source (where it came from), and metadata. The ContextBundle aggregates multiple nodes with metadata about the assembly process, including token count and whether truncation was required. The relevance scoring enables intelligent prioritization when token limits require truncation, ensuring the most relevant context is preserved.

## 5.4 LangGraph Orchestration

### 5.4.1 Graph Structure

The AI Hub uses LangGraph to implement complex orchestration workflows as directed graphs. Each node in the graph represents a step in the AI process (assemble context, call LLM, validate output, refine output, etc.), and edges define the flow between steps. The graph structure enables conditional branching (if output is invalid, go to refinement; if valid, proceed to storage), parallel execution (run multiple independent steps concurrently), and loops (iteration until success or max attempts). The runtime module manages graph execution, handling state management, error recovery, and checkpointing for long-running operations.

The graph is defined with specific nodes for different phases of AI processing. The planning node handles task decomposition and strategy selection. The context node handles context assembly. The generation node handles primary content creation. The critique node handles quality assessment and feedback. The refinement node handles iterative improvement. The storage node handles saving results to the database. This node structure provides modularity and reusability across different task types.

### 5.4.2 State Machine

The orchestration uses a deterministic state machine for tracking task progress through the graph. The state includes current node, accumulated context, generation attempts, validation results, and final output. The state machine ensures reproducible execution and enables recovery from failures by maintaining checkpointed state. If a node fails, the state machine can retry from the last checkpoint rather than restarting entire workflows. This is particularly important for long-running tasks that might encounter transient failures (LLM API timeouts, rate limits, etc.).

```python
@dataclass
class ExecutionTraceV1:
    task_id: str
    workspace_id: str
    mode: ExecutionMode
    state: str  # "assembling", "generating", "validating", "refining", "complete", "failed"
    current_node: str
    context_bundle: Optional[ContextBundleV1]
    attempts: int
    errors: List[str]
    started_at: datetime
    completed_at: Optional[datetime]
    result: Optional[TaskResultV1]
```

## 5.5 Tool Policy and Bounded Calling

### 5.5.1 Tool Definition

The AI Hub implements bounded tool calling through a policy system that defines which tools the AI can use and under what circumstances. Tools are defined with schemas specifying their purpose, input parameters, and usage constraints. The policy system enforces boundaries around AI behavior, preventing the AI from accessing unauthorized data, performing disallowed actions, or exceeding rate limits. This bounded approach is essential for safe operation in a multi-tenant environment where different workspaces must be strictly isolated.

Tools in the system include: database_query (read-only queries against workspace data), content_store (save generated content), asset_upload (manage media assets), notification_send (send notifications to users), web_search (search for external information), and scraper_fetch (fetch content from URLs). Each tool has defined parameters and return types, and the AI is provided with tool definitions but cannot call tools outside its defined set. The policy system also includes usage limits and rate limits to prevent abuse.

### 5.5.2 Policy Profiles

The system supports different policy profiles that define tool access levels for different task types. A "generative" profile might allow content creation and storage but not database queries, while an "analysis" profile might allow database queries and web search but not content generation. The policy module provides functions for building tool policies based on task requirements and normalizing policy profiles to standard formats.

```python
def build_tool_policy(
    task_type: str,
    workspace_id: str,
    intensity: IntensityLevel
) -> ToolPolicy:
    # Returns tool policy for the given task type and workspace

def normalize_policy_profile(profile: str) -> ToolPolicy:
    # Normalizes profile name to full policy

def describe_policy_profiles() -> Dict[str, str]:
    # Returns descriptions of available profiles
```

## 5.6 Prompt Engineering

### 5.6.1 Prompt Structure

The prompt engineering system in RaptorFlow uses a structured approach to building prompts for different task types. Each prompt consists of multiple sections: system instructions (base behavioral guidelines), context blocks (assembled BCM and task context), task specification (the specific request), output format (schema for the response), and constraints (boundaries and limitations). The prompts are stored as templates in the prompts package, with variables that are filled in at runtime based on the specific task and context. This template approach enables consistent behavior across similar tasks while allowing customization for specific contexts.

### 5.6.2 Move Generation Prompts

When generating move execution plans, the prompt engineering system constructs prompts that include: the move's category and goal, the target ICP profile, the brand voice guidelines, the desired tone, historical successful moves (from the workspace's move history), and specific instructions for execution plan format. The prompt instructs the LLM to produce a structured JSON response matching the ExecutionDay schema, with appropriate pillar tasks, cluster actions, and network actions for each day. The prompt also includes constraints around channel selection, timing, and resource requirements.

### 5.6.3 Content Generation Prompts

For content generation tasks (creating social posts, emails, etc.), the prompts include: the content channel and format requirements, the target audience (from ICP), the brand voice guidelines, the specific message or offer to communicate, any timing constraints, and relevant competitive or market context. The prompt specifies the output format (plain text, HTML, markdown, etc.) and includes examples of the desired output style. The LLM generates content that matches these specifications, which is then validated against brand guidelines before being stored.

## 5.7 LLM Backends

### 5.7.1 Backend Abstraction

The AI system supports multiple LLM backends through an abstraction layer that provides a common interface. The base backend class defines the contract: initialize (set up credentials), generate (make a completion request), and health_check (verify connectivity). Specific implementations handle the differences between backends: Vertex AI backend uses Google's Vertex AI API, GenAI API Key backend uses Google's generativeai library, and deterministic fallback provides rule-based responses when no LLM is available. This abstraction enables the system to work in different environments (local development vs. production) with different capability requirements.

```python
class BackendType(str, Enum):
    VERTEX_AI = "vertex_ai"
    GENAI_API_KEY = "genai_api_key"
    DETERMINISTIC_FALLBACK = "deterministic_fallback"
    UNCONFIGURED = "unconfigured"

@dataclass
class BackendHealth:
    status: str
    backend: BackendType
    model: str
    fallback_ready: bool
    detail: Optional[str]
```

### 5.7.2 Vertex AI Integration

The Vertex AI backend integrates with Google's Vertex AI platform for LLM access. The backend supports various model versions and handles authentication through Google Cloud service accounts. Configuration includes project ID, location, and model selection. The backend implements retry logic with exponential backoff for transient failures, timeout handling for long-running requests, and response parsing for Vertex AI's specific response format. The backend also tracks usage metrics (input/output tokens) for cost tracking and quota management.

### 5.7.3 Deterministic Fallback

The deterministic fallback backend provides rule-based responses when no LLM is available, ensuring the system can still function in degraded conditions. The fallback uses template-based generation for common task types, selecting appropriate templates based on task parameters and filling in templates with provided context. While the output quality is lower than LLM-generated content, the fallback ensures basic functionality for critical paths (e.g., move execution plan generation during onboarding demos). The fallback is also used for health checks and testing, where deterministic output is preferred.

## 5.8 Result Handling

### 5.8.1 GenerationResult Structure

The result of any AI generation is wrapped in a GenerationResult object that provides comprehensive metadata about the generation:

```python
@dataclass
class GenerationResult:
    status: str  # "success" or "error"
    text: str  # the generated content
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    generation_time_seconds: float
    model: str
    model_type: str
    backend: BackendType
    error: Optional[str]
    fallback_reason: Optional[str]
    ensemble: Dict[str, Any]  # for council/swarm modes
    metadata: Dict[str, Any]
```

The result includes timing and cost information for billing and optimization, model and backend identification for debugging, error details when failures occur, and ensemble information for multi-model executions (council and swarm modes). The status field indicates success or failure, with the error field providing details on failure.

### 5.8.2 Usage Tracking

Every generation is logged as a CostRecord for tracking usage and billing:

```python
@dataclass
class CostRecord:
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: datetime
    workspace_id: str
    user_id: str
    backend: BackendType
```

Usage records are stored in the database and aggregated for workspace-level billing and usage reports. The system can enforce limits based on subscription tier, tracking usage against allocated quotas and returning errors when limits are exceeded. Usage tracking also enables optimization efforts by identifying patterns in token consumption and opportunities for efficiency improvements.

---

## PART 6 — DATABASE ARCHITECTURE AND CACHING

## 6.1 Complete Schema Overview

### 6.1.1 Tables Summary

The RaptorFlow database consists of 12 core tables organized around the multi-tenant architecture. The workspaces table is the root entity representing tenant organizations, with all other tables linked through workspace_id foreign keys. The workspace_members table provides the many-to-many relationship between users and workspaces with role information. The profiles table extends auth.users with application-specific data. The foundations table stores business context from onboarding. The business_context_manifests table stores versioned BCM snapshots. The icp_profiles table stores Ideal Customer Profile definitions. The campaigns and moves tables store the tactical execution data. The subscription_plans and subscriptions tables handle billing. The audit_logs table provides visibility into system activity.

### 6.1.2 Workspaces Table

The workspaces table is the top-level tenant container:

```sql
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

The name is a human-readable identifier for display, while slug is a URL-safe identifier for programmatic access (used in URLs, API paths, etc.). The settings JSONB field stores workspace-level configuration that doesn't warrant dedicated columns, such as timezone, default language, notification preferences, and feature flags. The slug must be unique across the entire system, preventing collisions between workspaces.

### 6.1.3 Workspace Members Table

The workspace_members table implements the user-workspace relationship:

```sql
CREATE TABLE workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    is_active BOOLEAN DEFAULT true,
    joined_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(workspace_id, user_id)
);
```

The role field defines permissions: 'owner' has full control including billing and deletion, 'admin' has full management but not billing, 'member' has standard access to create and edit resources, 'viewer' has read-only access. The is_active flag enables deactivating members without deleting them, preserving historical associations. The unique constraint ensures a user can only have one membership per workspace, preventing duplicate roles.

### 6.1.4 Profiles Table

The profiles table extends Supabase auth.users with application data:

```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    phone TEXT,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    subscription_plan TEXT DEFAULT 'free',
    subscription_status TEXT DEFAULT 'none',
    onboarding_status TEXT DEFAULT 'pending',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

The profile is linked to the auth.users table through a 1:1 relationship (profile id = user id). The workspace_id can be NULL for users who haven't joined a workspace yet, set when they create or join their first workspace. The subscription fields track billing status, and onboarding_status tracks where users are in the onboarding flow ('pending', 'in_progress', 'completed').

### 6.1.5 Foundations Table

The foundations table stores the business context collected during onboarding:

```sql
CREATE TABLE foundations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    company_info JSONB DEFAULT '{}',
    mission TEXT,
    vision TEXT,
    value_proposition TEXT,
    brand_voice JSONB DEFAULT '{}',
    messaging JSONB DEFAULT '{}',
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(workspace_id)
);
```

The company_info JSONB stores structured company details (industry, size, location, etc.), while mission, vision, and value_proposition are dedicated text fields for the core positioning statements. The brand_voice JSONB stores tone guidelines, vocabulary preferences, and style rules. The messaging JSONB stores key messages, value propositions, and talking points. The status field tracks whether the foundation is being actively used ('active') or archived.

### 6.1.6 ICP Profiles Table

The icp_profiles table stores Ideal Customer Profile definitions:

```sql
CREATE TABLE icp_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    demographics JSONB DEFAULT '{}',
    psychographics JSONB DEFAULT '{}',
    pain_points JSONB DEFAULT '[]',
    goals JSONB DEFAULT '[]',
    objections JSONB DEFAULT '[]',
    market_sophistication INTEGER DEFAULT 3 CHECK (market_sophistication >= 1 AND market_sophistication <= 5),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

The demographics JSONB stores firmographic and demographic data (company size, industry, role, etc.), psychographics stores attitudes and preferences, pain_points stores the challenges the ICP faces, goals stores what the ICP is trying to achieve, and objections stores concerns or barriers to purchase. The market_sophistication field (1-5 scale) indicates how sophisticated the target market is, influencing content complexity and channel selection.

### 6.1.7 Business Context Manifests Table

The business_context_manifests table stores versioned snapshots of the complete BCM:

```sql
CREATE TABLE business_context_manifests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    manifest JSONB NOT NULL,
    source_context JSONB,
    checksum TEXT NOT NULL,
    token_estimate INTEGER,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(workspace_id, version)
);
```

The version field auto-increments for each new snapshot, enabling historical retrieval. The manifest JSONB contains the full BCM (foundations + ICPs + any additional context). The source_context JSONB stores the raw input data used to generate the manifest. The checksum field provides integrity verification, enabling detection of corruption. The token_estimate stores the token count for the manifest, useful for optimization and billing.

### 6.1.8 Subscription Tables

The subscription_plans and subscriptions tables handle billing:

```sql
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    description TEXT,
    price_monthly INTEGER DEFAULT 0,
    price_annual INTEGER DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'INR',
    features JSONB DEFAULT '{}',
    limits JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES subscription_plans(id),
    plan_name TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired', 'past_due', 'trialing')),
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

The subscription_plans table defines the available plans (seeded with Free, Starter, Growth, Enterprise), while subscriptions tracks each user's subscription. The features JSONB on plans lists available features as boolean flags, while limits JSONB specifies usage limits (campaigns per month, moves per month, AI generations, etc.).

### 6.1.9 Audit Logs Table

The audit_logs table provides visibility into system activity:

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    actor_id UUID,
    action TEXT NOT NULL,
    target_type TEXT,
    target_id TEXT,
    changes JSONB DEFAULT '{}',
    status TEXT DEFAULT 'success',
    created_at TIMESTAMPTZ DEFAULT now()
);
```

The actor_id identifies who performed the action (can be NULL for system actions), action describes what happened (e.g., "move.created", "campaign.updated"), target_type and target_id identify the affected resource, changes JSONB stores before/after values for updates, and status indicates success or failure.

## 6.2 Row Level Security

### 6.2.1 RLS Configuration

All tables have Row Level Security (RLS) enabled with permissive policies for service role access:

```sql
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
-- ... (all other tables)

CREATE POLICY "Allow all for service role" ON workspaces FOR ALL USING (true);
-- ... (all other tables)
```

The permissive policies allow the service role (used by the backend API) to bypass RLS, while the policies themselves don't restrict anything for service role. For anon/authenticated users, additional policies would be needed, but currently the API uses service role for all database access, so RLS is effectively bypassed at the application level.

### 6.2.2 Workspace Isolation

All data access is scoped by workspace_id through the API layer. The X-Workspace-Id header is required for all workspace-scoped operations, and the workspace_guard module validates this header and enforces BCM readiness before any database access. This workspace isolation ensures that users can only access data within their own workspace, maintaining multi-tenant security at the application layer.

## 6.3 Redis Caching

### 6.3.1 Cache Architecture

The system uses Redis for caching frequently accessed data and for session management. Key cache patterns include: BCM cache (storing assembled BCM for fast AI context retrieval), session cache (storing user session data), and rate limiting (tracking API usage for quota enforcement). The cache is workspace-scoped using workspace_id prefixes in keys, ensuring isolation between tenants.

### 6.3.2 Cache Keys

Common cache key patterns use the format `workspace:{workspace_id}:{resource}:{id}` for specific resources and `workspace:{workspace_id}:{resource}:list` for collections. TTLs vary by resource type: BCM caches have longer TTLs (hours), session caches match session duration, rate limit caches reset with each window. The cache is configured with appropriate eviction policies to prevent memory exhaustion.

---

## PART 7 — AUTHENTICATION AND MULTI-TENANCY

## 7.1 Authentication System

### 7.1.1 Auth Flow

The authentication system uses Supabase Auth for user management, with the backend API validating tokens through the get_current_user dependency. Users sign up and sign in through Supabase Auth (email/password or OAuth providers), receiving a JWT token that is included in API requests. The backend validates the token, extracts the user ID, and uses it for database access control. For workspace-scoped operations, the X-Workspace-Id header identifies which workspace the user is operating in, and the backend validates that the user has access to that workspace through the workspace_members table.

### 7.1.2 User Roles

The system defines four user roles: owner (full control including billing and workspace deletion), admin (full management but cannot access billing), member (standard access to create and edit resources), and viewer (read-only access). These roles are stored in the workspace_members table and checked by the API for operations that require specific permission levels. The role hierarchy is enforced at the API layer through the workspace_guard module, which validates permissions before allowing operations.

## 7.2 Multi-Tenancy Model

### 7.2.1 Workspace as Tenant

The workspace is the primary tenant entity, containing all user data, business context, campaigns, and moves. Each workspace has its own BCM, its own user members, its own subscription, and its own data. Workspaces are isolated at the database level through foreign key relationships and at the application level through workspace_id validation in all API operations.

### 7.2.2 Cross-Workspace Access

Users can belong to multiple workspaces through the workspace_members table, enabling them to work across different organizations. When a user accesses the API, they must specify which workspace they're operating in through the X-Workspace-Id header. The API validates that the user is a member of that workspace before allowing any operation. This per-request workspace selection enables users to switch between their workspaces without re-authenticating.

---

## Summary

This document has covered the Moves and Campaigns tactical execution layer, the Muse AI Orchestration Engine, the database architecture and caching layer, and the authentication and multi-tenancy system. The Moves system provides structured tactical execution with day-by-day planning, task tracking, and progress measurement. The Campaigns system provides organizational containers for moves with strategic alignment. The Muse AI system provides intelligent content generation and execution planning with multiple orchestration modes. The database schema provides a clean multi-tenant structure with appropriate relationships and constraints. Together, these systems form the operational backbone of RaptorFlow, translating strategic context into tactical execution and measuring results.

---

## Document Information

**Total Lines**: Approximately 4,800+ (combined with previous parts)  
**Version**: 1.0.0  
**Last Updated**: 2026-02-20  
**Location**: `.sisyphus/docs/PART_4_Moves_Campaigns_Muse.md`
