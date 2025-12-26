/**
 * Radar — Industrial Backend Bridge
 * Communicates with Python Agentic Spine
 */

import { Signal, Dossier, MOCK_ANGLES } from '@/components/radar/types';

export interface RadarSignalBackend {
    id: string;
    type: string;
    source: string;
    content: string;
    confidence: number;
    timestamp: string;
    strength: string;
    freshness: string;
    action_suggestion: string;
    evidence_count: number;
}

export interface RadarDossierBackend {
    id: string;
    title: string;
    summary: string;
    hypotheses: string[];
    recommended_experiments: string[];
    copy_snippets: string[];
    market_narrative: string;
    pinned_signals_count: number;
    created_at: string;
    is_published: boolean;
}

export interface RadarAnalyticsBackend {
    signal_trends: any;
    competitor_analysis: any;
    market_dynamics: any;
    predictive_insights: any;
}

export interface RadarSchedulerBackend {
    status: string;
    tenant_id: string;
    is_active: boolean;
    cache_size: number;
    active_tasks: number;
}

export interface RadarNotificationBackend {
    type: string;
    priority: string;
    title: string;
    message: string;
    created_at: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

import { supabase } from './supabase';

// Core Radar Functions
export async function scanRecon(icpId: string, sourceUrls?: string[]): Promise<Signal[]> {
    const { data: { user } } = await supabase.auth.getUser();
    const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

    const requestBody = sourceUrls ? { source_urls: sourceUrls } : {};

    const response = await fetch(`${API_URL}/v1/radar/scan/recon`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Tenant-ID': tenantId
        },
        body: JSON.stringify({ icp_id: icpId, ...requestBody })
    });
    if (!response.ok) {
        throw new Error('Failed to perform recon scan');
    }
    const data: RadarSignalBackend[] = await response.json();
    return data.map(mapSignalFromBackend);
}

export async function generateDossier(campaignId: string, signalIds?: string[]): Promise<Dossier[]> {
    const { data: { user } } = await supabase.auth.getUser();
    const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

    const requestBody = signalIds ? { signal_ids: signalIds } : {};

    const response = await fetch(`${API_URL}/v1/radar/scan/dossier`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Tenant-ID': tenantId
        },
        body: JSON.stringify({ campaign_id: campaignId, ...requestBody })
    });
    if (!response.ok) {
        throw new Error('Failed to generate dossier');
    }
    const data: RadarDossierBackend = await response.json();
    return [mapDossierFromBackend(data)];
}

// Analytics Functions
export async function getSignalTrends(windowDays: number = 30): Promise<RadarAnalyticsBackend> {
    const { data: { user } } = await supabase.auth.getUser();
    const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

    const response = await fetch(`${API_URL}/v1/radar/analytics/trends?window_days=${windowDays}`, {
        headers: {
            'X-Tenant-ID': tenantId
        }
    });
    if (!response.ok) {
        throw new Error('Failed to get signal trends');
    }
    return await response.json();
}

export async function getCompetitorAnalysis(): Promise<RadarAnalyticsBackend> {
    const { data: { user } } = await supabase.auth.getUser();
    const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

    const response = await fetch(`${API_URL}/v1/radar/analytics/competitors`, {
        headers: {
            'X-Tenant-ID': tenantId
        }
    });
    if (!response.ok) {
        throw new Error('Failed to get competitor analysis');
    }
    return await response.json();
}

export async function getMarketIntelligence(): Promise<RadarAnalyticsBackend> {
    const { data: { user } } = await supabase.auth.getUser();
    const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

    const response = await fetch(`${API_URL}/v1/radar/analytics/intelligence`, {
        headers: {
            'X-Tenant-ID': tenantId
        }
    });
    if (!response.ok) {
        throw new Error('Failed to get market intelligence');
    }
    return await response.json();
}

export async function getOpportunities(): Promise<any[]> {
    const { data: { user } } = await supabase.auth.getUser();
    const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

    const response = await fetch(`${API_URL}/v1/radar/analytics/opportunities`, {
        headers: {
            'X-Tenant-ID': tenantId
        }
    });
    if (!response.ok) {
        throw new Error('Failed to get opportunities');
    }
    return await response.json();
}

// Scheduler Functions
export async function startScheduler(): Promise<RadarSchedulerBackend> {
    const { data: { user } } = await supabase.auth.getUser();
    const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

    const response = await fetch(`${API_URL}/v1/radar/scheduler/start`, {
        method: 'POST',
        headers: {
            'X-Tenant-ID': tenantId
        }
    });
    if (!response.ok) {
        throw new Error('Failed to start scheduler');
    }
    return await response.json();
}

export async function stopScheduler(): Promise<RadarSchedulerBackend> {
    const { data: { user } } = await supabase.auth.getUser();
    const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

    const response = await fetch(`${API_URL}/v1/radar/scheduler/stop`, {
        method: 'POST',
        headers: {
            'X-Tenant-ID': tenantId
        }
    });
    if (!response.ok) {
        throw new Error('Failed to stop scheduler');
    }
    return await response.json();
}

export async function scheduleManualScan(sourceIds: string[], scanType: string = 'recon'): Promise<any> {
    const { data: { user } } = await supabase.auth.getUser();
    const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

    const response = await fetch(`${API_URL}/v1/radar/scheduler/scan/manual`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Tenant-ID': tenantId
        },
        body: JSON.stringify({ source_ids: sourceIds, scan_type: scanType })
    });
    if (!response.ok) {
        throw new Error('Failed to schedule manual scan');
    }
    return await response.json();
}

export async function getSchedulerStatus(): Promise<RadarSchedulerBackend> {
    const { data: { user } } = await supabase.auth.getUser();
    const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

    const response = await fetch(`${API_URL}/v1/radar/scheduler/status`, {
        headers: {
            'X-Tenant-ID': tenantId
        }
    });
    if (!response.ok) {
        throw new Error('Failed to get scheduler status');
    }
    return await response.json();
}

export async function getSourceHealth(): Promise<any> {
    const { data: { user } } = await supabase.auth.getUser();
    const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

    const response = await fetch(`${API_URL}/v1/radar/scheduler/health`, {
        headers: {
            'X-Tenant-ID': tenantId
        }
    });
    if (!response.ok) {
        throw new Error('Failed to get source health');
    }
    return await response.json();
}

// Notification Functions
export async function processNotifications(signalIds: string[], tenantPreferences?: any): Promise<RadarNotificationBackend[]> {
    const { data: { user } } = await supabase.auth.getUser();
    const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

    const response = await fetch(`${API_URL}/v1/radar/notifications/process`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Tenant-ID': tenantId
        },
        body: JSON.stringify({ signal_ids: signalIds, tenant_preferences: tenantPreferences })
    });
    if (!response.ok) {
        throw new Error('Failed to process notifications');
    }
    return await response.json();
}

export async function getDailyDigest(): Promise<RadarNotificationBackend> {
    const { data: { user } } = await supabase.auth.getUser();
    const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

    const response = await fetch(`${API_URL}/v1/radar/notifications/digest/daily`, {
        headers: {
            'X-Tenant-ID': tenantId
        }
    });
    if (!response.ok) {
        throw new Error('Failed to get daily digest');
    }
    return await response.json();
}

function mapSignalFromBackend(s: RadarSignalBackend): Signal {
    return {
        id: s.id,
        title: s.content,
        whyItMatters: s.action_suggestion || "Strategic signal detected from " + s.source,
        timestamp: new Date(s.timestamp),
        source: { name: s.source, type: 'competitor' },
        confidence: s.confidence > 0.8 ? 'high' : s.confidence > 0.5 ? 'medium' : 'low',
        angles: [MOCK_ANGLES[0], MOCK_ANGLES[1]], // Dynamic angles would be next phase
        tags: [s.type, s.strength, s.freshness, 'competitor'],
    };
}

function mapDossierFromBackend(d: RadarDossierBackend): Dossier {
    return {
        id: d.id,
        title: d.title,
        date: new Date(d.created_at),
        summary: [d.summary],
        whatChanged: d.market_narrative || "Market dynamics detected",
        whyItMatters: {
            impacts: d.hypotheses,
            objections: ["Competitor positioning"],
            opportunities: d.recommended_experiments
        },
        marketNarrative: {
            believing: "Current market assumptions",
            overhyped: "Overhyped trends",
            underrated: "Underrated opportunities"
        },
        recommendedMove: {
            name: "Strategic Response",
            target: "Key Segments",
            action: d.copy_snippets[0] || "Execute based on intelligence"
        },
        assets: { email: true, post: true, meme: true, landing: true },
        sources: [{ name: "Radar Intelligence", type: 'competitor' }]
    };
}
