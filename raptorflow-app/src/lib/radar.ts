/**
 * Radar — Industrial Backend Bridge
 * Communicates with Python Agentic Spine
 */

import { Signal, Dossier, MOCK_ANGLES } from '@/components/radar/types';

export interface RadarSignalBackend {
    id: string;
    type: 'move' | 'shift' | 'hook';
    source: string;
    content: string;
    confidence: number;
    timestamp: string;
}

export interface CompetitorDossierBackend {
    id: string;
    name: string;
    threat_level: 'low' | 'medium' | 'high';
    strategy: string;
    vulnerabilities: string;
    target_segments: string[];
    last_updated: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function scanRecon(icpId: string): Promise<Signal[]> {
    const response = await fetch(`${API_URL}/v1/radar/scan/recon?icp_id=${encodeURIComponent(icpId)}`, {
        method: 'POST',
    });
    if (!response.ok) {
        throw new Error('Failed to perform recon scan');
    }
    const data: RadarSignalBackend[] = await response.json();
    return data.map(mapSignalFromBackend);
}

export async function generateDossier(icpId: string): Promise<Dossier[]> {
    const response = await fetch(`${API_URL}/v1/radar/scan/dossier?icp_id=${encodeURIComponent(icpId)}`, {
        method: 'POST',
    });
    if (!response.ok) {
        throw new Error('Failed to generate dossier');
    }
    const data: CompetitorDossierBackend[] = await response.json();
    return data.map(mapDossierFromBackend);
}

function mapSignalFromBackend(s: RadarSignalBackend): Signal {
    return {
        id: s.id,
        title: s.content,
        whyItMatters: "Strategic signal detected from " + s.source,
        timestamp: new Date(s.timestamp),
        source: { name: s.source, type: 'competitor' },
        confidence: s.confidence > 0.8 ? 'high' : s.confidence > 0.5 ? 'medium' : 'low',
        angles: [MOCK_ANGLES[0], MOCK_ANGLES[1]], // Dynamic angles would be next phase
        tags: [s.type, 'competitor'],
    };
}

function mapDossierFromBackend(d: CompetitorDossierBackend): Dossier {
    return {
        id: d.id,
        title: d.name + " Intelligence Report",
        date: new Date(d.last_updated),
        summary: [d.strategy, "Known Vulnerabilities: " + d.vulnerabilities],
        whatChanged: "Competitor is aggressively targeting segments: " + d.target_segments.join(', '),
        whyItMatters: {
            impacts: [d.strategy],
            objections: ["High switching cost"],
            opportunities: ["Target their vulnerable segments: " + d.target_segments.join(', ')]
        },
        marketNarrative: {
            believing: "Incumbents are safe.",
            overhyped: "AI replacement.",
            underrated: "Hyper-personalization."
        },
        recommendedMove: {
            name: "Counter-Pivot Strategy",
            target: "SMB Segment",
            action: "Highlight outdated UI vs RaptorFlow's modern approach."
        },
        assets: { email: true, post: true, meme: true, landing: false },
        sources: [{ name: d.name, type: 'competitor' }]
    };
}
