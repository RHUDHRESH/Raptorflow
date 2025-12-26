// =====================================================
// RADAR TYPES — Full Data Model
// =====================================================

export type RadarMode = 'recon' | 'dossier';
export type RadarTab = 'alerts' | 'watchlists' | 'sources' | 'analytics' | 'scheduler' | 'notifications';

// =====================================================
// Core Types
// =====================================================

export type ScanFrequency = 'hourly' | 'daily' | 'weekly';
export type AlertType = 'pricing' | 'messaging' | 'content' | 'funding' | 'feature' | 'hiring';
export type AlertStatus = 'new' | 'reviewed' | 'dismissed' | 'actioned';
export type ImpactLevel = 'high' | 'medium' | 'low';
export type ConfidenceLevel = 'high' | 'medium' | 'low';
export type EvidenceType = 'url' | 'screenshot' | 'linkedin' | 'twitter' | 'pdf';
export type ReconType = 'pricing' | 'messaging' | 'channel' | 'full';
export type WatchlistType = 'competitors' | 'trends' | 'custom';

// =====================================================
// Evidence Source
// =====================================================

export interface EvidenceSource {
    id: string;
    type: EvidenceType;
    name: string;
    value: string; // URL or file path
    lastChecked?: Date;
    health: number; // 0-100
    thumbnail?: string;
}

// =====================================================
// Competitor
// =====================================================

export interface Competitor {
    id: string;
    name: string;
    website?: string;
    linkedIn?: string;
    twitter?: string;
    logo?: string;
    sources: EvidenceSource[];
    lastRecon?: Date;
    notes?: string;
}

// =====================================================
// Watchlist
// =====================================================

export interface Watchlist {
    id: string;
    name: string;
    description?: string;
    type: WatchlistType;
    competitors: Competitor[];
    signalTypes: AlertType[];
    scanFrequency: ScanFrequency;
    lastScan?: Date;
    nextScan?: Date;
    status: 'active' | 'paused';
    createdAt: Date;
    updatedAt: Date;
}

// =====================================================
// Alert
// =====================================================

export interface Alert {
    id: string;
    watchlistId: string;
    watchlistName: string;
    competitorId: string;
    competitorName: string;
    type: AlertType;
    title: string;
    summary: string;
    details?: string[];
    impact: ImpactLevel;
    confidence: ConfidenceLevel;
    evidence: EvidenceSource[];
    createdAt: Date;
    status: AlertStatus;
    actionedMoveId?: string;
}

// =====================================================
// Recon Configuration
// =====================================================

export interface ReconConfig {
    type: ReconType;
    competitorId: string;
    sources: EvidenceSource[];
    keyQuestions: string[];
}

// =====================================================
// Radar Status
// =====================================================

export interface RadarStatus {
    activeWatchlists: number;
    newAlerts24h: number;
    nextScanIn: string; // e.g., "4h 30m"
    sourceHealth: number; // 0-100 average
}

// =====================================================
// Legacy Types (Backward Compatibility)
// =====================================================

export type SignalConfidence = 'high' | 'medium' | 'low';

export type SignalSource = {
    name: string;
    type: 'news' | 'social' | 'blog' | 'competitor' | 'regulation' | 'video';
    url?: string;
};

export type SignalAngle = {
    id: string;
    label: string;
    type: 'contrarian' | 'practical' | 'story' | 'meme' | 'data' | 'hot-take';
    prompt: string;
};

export interface Signal {
    id: string;
    title: string;
    whyItMatters: string;
    timestamp: Date;
    source: SignalSource;
    confidence: SignalConfidence;
    angles: SignalAngle[];
    tags: string[];
    isSaved?: boolean;
}

export interface Dossier {
    id: string;
    title: string;
    date: Date;
    summary: string[];
    whatChanged: string;
    whyItMatters: {
        impacts: string[];
        objections: string[];
        opportunities: string[];
    };
    marketNarrative: {
        believing: string;
        overhyped: string;
        underrated: string;
    };
    recommendedMove: {
        name: string;
        target: string;
        action: string;
    };
    assets: {
        email: boolean;
        post: boolean;
        meme: boolean;
        landing: boolean;
    };
    sources: SignalSource[];
}

export type TimeWindow = '24h' | '7d' | '30d';

// =====================================================
// Mock Data
// =====================================================

export const MOCK_WATCHLISTS: Watchlist[] = [
    {
        id: 'wl-1',
        name: 'SaaS Competitors',
        description: 'Direct product competitors in the marketing automation space',
        type: 'competitors',
        competitors: [
            {
                id: 'comp-1',
                name: 'Competitor A',
                website: 'https://competitor-a.com',
                sources: [
                    { id: 'src-1', type: 'url', name: 'Pricing Page', value: 'https://competitor-a.com/pricing', health: 95 },
                    { id: 'src-2', type: 'linkedin', name: 'Company Page', value: 'https://linkedin.com/company/competitor-a', health: 88 },
                ],
                lastRecon: new Date(Date.now() - 1000 * 60 * 60 * 2),
            },
            {
                id: 'comp-2',
                name: 'Competitor B',
                website: 'https://competitor-b.com',
                sources: [
                    { id: 'src-3', type: 'url', name: 'Blog', value: 'https://competitor-b.com/blog', health: 92 },
                ],
                lastRecon: new Date(Date.now() - 1000 * 60 * 60 * 24),
            },
        ],
        signalTypes: ['pricing', 'messaging', 'content'],
        scanFrequency: 'daily',
        lastScan: new Date(Date.now() - 1000 * 60 * 60 * 2),
        nextScan: new Date(Date.now() + 1000 * 60 * 60 * 4.5),
        status: 'active',
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7),
        updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 2),
    },
    {
        id: 'wl-2',
        name: 'Industry Trends',
        description: 'Keywords and objections in the market',
        type: 'trends',
        competitors: [],
        signalTypes: ['content', 'messaging'],
        scanFrequency: 'weekly',
        lastScan: new Date(Date.now() - 1000 * 60 * 60 * 24),
        status: 'active',
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 14),
        updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24),
    },
];

export const MOCK_ALERTS: Alert[] = [
    {
        id: 'alert-1',
        watchlistId: 'wl-1',
        watchlistName: 'SaaS Competitors',
        competitorId: 'comp-1',
        competitorName: 'Competitor A',
        type: 'pricing',
        title: 'Pricing Change Detected',
        summary: 'Competitor A removed their "Starter" tier and increased Pro plan to $499/mo',
        details: [
            'Removed "Starter" tier completely',
            'Pro plan increased from $299/mo to $499/mo',
            'Enterprise pricing now requires demo',
        ],
        impact: 'high',
        confidence: 'high',
        evidence: [
            { id: 'ev-1', type: 'screenshot', name: 'Pricing Page Snapshot', value: '/evidence/pricing-1.png', health: 100 },
        ],
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2),
        status: 'new',
    },
    {
        id: 'alert-2',
        watchlistId: 'wl-1',
        watchlistName: 'SaaS Competitors',
        competitorId: 'comp-2',
        competitorName: 'Competitor B',
        type: 'messaging',
        title: 'New Messaging Angle Spotted',
        summary: 'Competitor B is now positioning around "stop wasting resources" — a direct competitive hook',
        impact: 'medium',
        confidence: 'medium',
        evidence: [
            { id: 'ev-2', type: 'linkedin', name: 'LinkedIn Post', value: 'https://linkedin.com/post/123', health: 100 },
        ],
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 8),
        status: 'new',
    },
];

export const MOCK_RADAR_STATUS: RadarStatus = {
    activeWatchlists: 5,
    newAlerts24h: 12,
    nextScanIn: '4h 30m',
    sourceHealth: 94,
};

// Legacy mock data
export const MOCK_ANGLES: SignalAngle[] = [
    { id: 'a1', label: 'Contrarian', type: 'contrarian', prompt: 'Write a contrarian take on this...' },
    { id: 'a2', label: 'Practical', type: 'practical', prompt: 'Give me actionable steps based on this...' },
    { id: 'a3', label: 'Founder Story', type: 'story', prompt: 'Turn this into a founder story...' },
    { id: 'a4', label: 'Data', type: 'data', prompt: 'Analyze the numbers here...' },
    { id: 'a5', label: 'Hot Take', type: 'hot-take', prompt: 'Give me a hot take on this...' },
    { id: 'a6', label: 'Meme', type: 'meme', prompt: 'Make a meme about this...' },
];

export const MOCK_SIGNALS: Signal[] = [
    {
        id: 's1',
        title: 'Competitor X raises $20M Series A',
        whyItMatters: 'They are pivoting to enterprise. Your SMB moat is safe for now, but watch their pricing.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3),
        source: { name: 'TechCrunch', type: 'news' },
        confidence: 'high',
        angles: [MOCK_ANGLES[0], MOCK_ANGLES[1], MOCK_ANGLES[2]],
        tags: ['funding', 'competitor'],
    },
];

export const MOCK_DOSSIERS: Dossier[] = [
    {
        id: 'd1',
        title: 'The "Founder-Led Sales" Shift',
        date: new Date(),
        summary: [
            'Market is tiring of SDR automation.',
            'Trust is the new currency.',
            'Founders need to be the face again.',
        ],
        whatChanged: 'Buyer sentiment has shifted against faceless automation.',
        whyItMatters: {
            impacts: ['Your current outbound is losing effectiveness.'],
            objections: ['"I dont have time to write"'],
            opportunities: ['Launch a "Founder Logs" series.'],
        },
        marketNarrative: {
            believing: 'Outbound is dead.',
            overhyped: 'AI Agents replacing SDRs entirely.',
            underrated: 'Video emails from founders.',
        },
        recommendedMove: {
            name: 'Operation Glass House',
            target: 'Increase reply rate by 15%',
            action: 'Replace first drip email with a 30s Loom video from you.',
        },
        assets: { email: true, post: true, meme: false, landing: false },
        sources: [{ name: 'Gartner Report', type: 'news' }],
    },
];
