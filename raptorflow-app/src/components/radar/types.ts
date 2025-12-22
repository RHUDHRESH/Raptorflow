export type RadarMode = 'recon' | 'dossier';

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
    prompt: string; // The prompt to send to Muse
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
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3), // 3 hours ago
        source: { name: 'TechCrunch', type: 'news' },
        confidence: 'high',
        angles: [MOCK_ANGLES[0], MOCK_ANGLES[1], MOCK_ANGLES[2]],
        tags: ['funding', 'competitor'],
    },
    {
        id: 's2',
        title: 'New EU AI Regulation Draft Leaked',
        whyItMatters: 'Stricter compliance for automated outreach. Your "human-in-the-loop" feature is now a killer USP.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 12),
        source: { name: 'Politico', type: 'regulation' },
        confidence: 'high',
        angles: [MOCK_ANGLES[0], MOCK_ANGLES[3], MOCK_ANGLES[1]],
        tags: ['regulation', 'market'],
    },
    {
        id: 's3',
        title: 'LinkedIn Algorithm favors "Helpful" comments',
        whyItMatters: 'Shift your strategy from engagement bait to deep value comments. Update your team SOPs.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24),
        source: { name: 'Algorithm Report', type: 'blog' },
        confidence: 'medium',
        angles: [MOCK_ANGLES[1], MOCK_ANGLES[4], MOCK_ANGLES[5]],
        tags: ['trends', 'social'],
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
        whatChanged: 'Buyer sentiment has shifted against faceless automation. Response rates for standard sequences are down 40% industry-wide.',
        whyItMatters: {
            impacts: ['Your current outbound sequence volume is losing effectiveness.', 'Personal brand is no longer optional.'],
            objections: ['"I dont have time to write"', '"I am not an influencer"'],
            opportunities: ['Launch a "Founder Logs" series.', 'Pivot sales copy to "I built this for you".'],
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
        sources: [{ name: 'Gartner Report', type: 'news' }, { name: 'SalesHacker', type: 'blog' }],
    },
];
