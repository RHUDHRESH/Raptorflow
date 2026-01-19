/* ══════════════════════════════════════════════════════════════════════════════
   MOVES — Type Definitions
   Tactical sprint execution types for RaptorFlow
   ══════════════════════════════════════════════════════════════════════════════ */

// --- Move Categories ---
// --- Move Categories ---
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

// --- Task Status ---
export type TaskStatus = 'pending' | 'in-progress' | 'done' | 'blocked';

// --- Task Item ---
export interface TaskItem {
    id: string;
    title: string;
    description?: string;
    status: TaskStatus;
    channel?: string;
    note?: string;  // Optional note added on completion
}

// --- Execution Day ---
export interface ExecutionDay {
    day: number;
    phase: string;
    pillarTask: TaskItem;
    clusterActions: TaskItem[];
    networkAction: TaskItem;
}

// --- Move Status ---
export type MoveStatus = 'draft' | 'active' | 'completed' | 'paused';

// --- Move Duration ---
export type MoveDuration = number;  // 7 or 14 typical, but flexible for experimental moves

// --- Move ---
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
    progress?: number; // 0-100
    icp?: string;
    campaignId?: string;
    metrics?: string[];
}

// --- Move Brief (Strategy Lock) ---
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

// --- Wizard State ---
export type WizardStep = 'category' | 'context' | 'brief' | 'preview';

export interface MoveWizardState {
    step: WizardStep;
    category: MoveCategory | null;
    context: string;
    attachments: File[];
    brief: MoveBriefData | null;
    isLoading: boolean;
}
