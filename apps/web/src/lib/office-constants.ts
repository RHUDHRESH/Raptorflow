/**
 * RaptorFlow Office Design System Constants
 * 
 * RULE: Layer 1 (Canvas) and Layer 2 (UI Chrome) constants are strictly separated.
 */

/* ─────────────────────────────────────────────────────────────────────────────
   LAYER 1: PIXIJS CANVAS DESIGN TOKENS
   ───────────────────────────────────────────────────────────────────────────── */

export const CANVAS_COLORS = {
  env: {
    wall:         '#F5EEDC', // Wall Cream
    carpet_a:     '#783841', // Carpet Burgundy
    carpet_b:     '#8C8782', // Carpet Grey
    wood:         '#4B2D19', // Wood Walnut
    light_wash:   '#FFFBEF', // Warm wash
    glass:        'rgba(200, 220, 240, 0.3)', // Glass walls
  },
  events: {
    amber:        '#FFB932', // Pager / File delivery
    blue:         '#50A0F0', // Speech / Thought
    green:        '#5ABE64', // Success glow
    alert:        '#EB6446', // Red Alert
  },
  skin: [
    '#FFDCB9', // Skin 1
    '#EEBE95', // Skin 2
    '#D4956A', // Skin 3
    '#BE7044', // Skin 4
    '#9A5530', // Skin 5
    '#7A3D20', // Skin 6
    '#643C28', // Skin 7
  ],
} as const;

/* ─────────────────────────────────────────────────────────────────────────────
   AGENT CONFIGURATION
   ───────────────────────────────────────────────────────────────────────────── */

export const AGENT_KEYS = [
  // Legends
  'ogilvy', 'bernbach', 'hopkins', 'draper', 'patel', 'vaynerchuk',
  // Specialists
  'sharp', 'godin', 'kotler', 'ries', 'cialdini', 'sutherland',
  // Core Operational
  'analytics_director', 'content_editor', 'seo_specialist', 'ad_specialist',
  'social_manager', 'email_specialist', 'research_intern', 'outreach_specialist',
  // User Strategist
  'strategist'
] as const;

export type AgentKey = typeof AGENT_KEYS[number];

/**
 * Fallback colors used when spritesheets are missing.
 * These are visually distinct to ensure the layout remains readable.
 */
export const PLACEHOLDER_COLORS: Record<AgentKey, string> = {
  ogilvy: '#7c3aed',
  bernbach: '#2563eb',
  hopkins: '#0891b2',
  draper: '#059669',
  patel: '#db2777',
  vaynerchuk: '#ea580c',
  sharp: '#4b5563',
  godin: '#ca8a04',
  kotler: '#16a34a',
  ries: '#9333ea',
  cialdini: '#2563eb',
  sutherland: '#be123c',
  analytics_director: '#444444',
  content_editor: '#555555',
  seo_specialist: '#666666',
  ad_specialist: '#222222',
  social_manager: '#333333',
  email_specialist: '#777777',
  research_intern: '#888888',
  outreach_specialist: '#999999',
  strategist: '#f59e0b',
};

/* ─────────────────────────────────────────────────────────────────────────────
   ASSET MANIFEST
   ───────────────────────────────────────────────────────────────────────────── */

export const ASSET_PATHS = {
  characters: (key: AgentKey) => `/office/characters/${key}-spritesheet`,
  characterPng: (key: AgentKey) => `/office/characters/${key}-spritesheet.png`,
  characterJson: (key: AgentKey) => `/office/characters/${key}-spritesheet.json`,
  prop: (name: string) => `/office/props/${name}`,
  atlas: '/office/office-atlas.json',
  background: (name: string) => `/office/backgrounds/${name}.png`,
};

/* ─────────────────────────────────────────────────────────────────────────────
   ANIMATION & VIEWPORT TIMING
   ───────────────────────────────────────────────────────────────────────────── */

export const ANIMATION_DURATIONS = {
  BREATHE: 3.5, // seconds
  WALK_SPEED_PX_PER_MS: 0.15,
  PAGER_BUZZ: 0.8,
  SPEAK_GLOW: 0.4,
  CONFERENCE_WALK_DELAY_PER_AGENT: 0.2,
  NUDGE_PANEL_SLIDE: 0.25, // seconds (Framer Motion)
};

export const ZOOM_LEVELS = {
  OVERVIEW: 0.6,
  WORKING: 1.0,
  DETAIL: 1.8,
  CLOSEUP: 2.5,
  HIGH_DETAIL_THRESHOLD: 1.5,
} as const;

/* ─────────────────────────────────────────────────────────────────────────────
   OFFICE TOPOLOGY
   ───────────────────────────────────────────────────────────────────────────── */

export interface OfficeZone {
  id: string;
  label: string;
  defaultPosition: { x: number; y: number };
  isPrivate: boolean;
  capacity: number;
}

export const OFFICE_ZONES: Record<string, OfficeZone> = {
  reception: {
    id: 'reception',
    label: 'RECEPTION',
    defaultPosition: { x: 50, y: 50 },
    isPrivate: false,
    capacity: 4
  },
  strategist_office: {
    id: 'strategist_office',
    label: 'STRATEGIST OFFICE',
    defaultPosition: { x: 200, y: 50 },
    isPrivate: true,
    capacity: 2
  },
  conference_room: {
    id: 'conference_room',
    label: 'THE COUNCIL',
    defaultPosition: { x: 400, y: 150 },
    isPrivate: true,
    capacity: 12
  },
  content_studio: {
    id: 'content_studio',
    label: 'CONTENT STUDIO',
    defaultPosition: { x: 50, y: 250 },
    isPrivate: false,
    capacity: 6
  },
  intel_lab: {
    id: 'intel_lab',
    label: 'INTEL LAB',
    defaultPosition: { x: 400, y: 50 },
    isPrivate: false,
    capacity: 4
  },
  research_station: {
    id: 'research_station',
    label: 'RESEARCH STATION',
    defaultPosition: { x: 200, y: 300 },
    isPrivate: false,
    capacity: 4
  },
  server_room: {
    id: 'server_room',
    label: 'SERVER ROOM',
    defaultPosition: { x: 500, y: 300 },
    isPrivate: true,
    capacity: 0
  }
};
