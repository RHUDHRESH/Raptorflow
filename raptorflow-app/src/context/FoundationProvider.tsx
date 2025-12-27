'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import {
    FoundationData,
    IcpProfile,
    DirectCompetitor,
    SimpleCohort,
    SimpleCompetitor,
    SimpleCampaign,
    MessagingData,
    PositioningData,
    CompetitionData,
    CohortsData,
    BusinessData,
} from '@/lib/foundation-types';

// === Context Types ===
interface FoundationContextValue {
    // Raw data
    foundation: FoundationData | null;
    isLoading: boolean;
    error: string | null;

    // Simplified accessors for modules
    getCohorts: () => SimpleCohort[];
    getCompetitors: () => SimpleCompetitor[];
    getCampaigns: () => SimpleCampaign[];
    getIcps: () => IcpProfile[];

    // Full section accessors
    getMessaging: () => MessagingData | null;
    getPositioning: () => PositioningData | null;
    getCompetition: () => CompetitionData | null;
    getBusiness: () => BusinessData | null;

    // Utility
    reload: () => Promise<void>;
}

const FoundationContext = createContext<FoundationContextValue | undefined>(undefined);

// === Provider Component ===
export function FoundationProvider({ children }: { children: ReactNode }) {
    const [foundation, setFoundation] = useState<FoundationData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadFoundation = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch('/foundation_test.json');
            if (!response.ok) {
                throw new Error(`Failed to load foundation: ${response.statusText}`);
            }
            const data: FoundationData = await response.json();
            setFoundation(data);
        } catch (err) {
            console.error('Failed to load foundation data:', err);
            setError(err instanceof Error ? err.message : 'Unknown error loading foundation');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        loadFoundation();
    }, [loadFoundation]);

    // === Simplified Accessors ===

    const getCohorts = useCallback((): SimpleCohort[] => {
        if (!foundation?.cohorts?.icps) return [];
        return foundation.cohorts.icps.map((icp) => ({
            id: icp.icp_id,
            name: icp.name,
        }));
    }, [foundation]);

    const getCompetitors = useCallback((): SimpleCompetitor[] => {
        if (!foundation?.competition) return [];
        const competitors: SimpleCompetitor[] = [];

        // Add direct competitors
        foundation.competition.direct.forEach((c) => {
            competitors.push({
                name: c.name,
                strength: c.strength,
                weakness: c.weakness,
            });
        });

        // Add indirect competitors as simple names
        foundation.competition.indirect.forEach((name) => {
            competitors.push({ name });
        });

        return competitors;
    }, [foundation]);

    const getCampaigns = useCallback((): SimpleCampaign[] => {
        if (!foundation) return [];
        // Derive campaigns from positioning value themes & GTM channels
        const campaigns: SimpleCampaign[] = [];

        // Create campaigns from value themes
        foundation.positioning?.components?.value_themes?.forEach((theme, index) => {
            campaigns.push({
                id: `campaign-theme-${index}`,
                name: `${theme} Campaign`,
            });
        });

        // Create campaigns from top channels
        foundation.ops?.go_to_market?.channels_top3?.forEach((channel, index) => {
            campaigns.push({
                id: `campaign-channel-${index}`,
                name: `${channel} Push`,
            });
        });

        return campaigns;
    }, [foundation]);

    const getIcps = useCallback((): IcpProfile[] => {
        return foundation?.cohorts?.icps || [];
    }, [foundation]);

    // === Full Section Accessors ===

    const getMessaging = useCallback((): MessagingData | null => {
        return foundation?.messaging || null;
    }, [foundation]);

    const getPositioning = useCallback((): PositioningData | null => {
        return foundation?.positioning || null;
    }, [foundation]);

    const getCompetition = useCallback((): CompetitionData | null => {
        return foundation?.competition || null;
    }, [foundation]);

    const getBusiness = useCallback((): BusinessData | null => {
        return foundation?.business || null;
    }, [foundation]);

    const value: FoundationContextValue = {
        foundation,
        isLoading,
        error,
        getCohorts,
        getCompetitors,
        getCampaigns,
        getIcps,
        getMessaging,
        getPositioning,
        getCompetition,
        getBusiness,
        reload: loadFoundation,
    };

    return (
        <FoundationContext.Provider value={value}>
            {children}
        </FoundationContext.Provider>
    );
}

// === Hook for consuming Foundation data ===
export function useFoundation(): FoundationContextValue {
    const context = useContext(FoundationContext);
    if (context === undefined) {
        throw new Error('useFoundation must be used within a FoundationProvider');
    }
    return context;
}

// === Convenience hook for quick cohort/competitor access ===
export function useFoundationMentions() {
    const { getCohorts, getCompetitors, getCampaigns, isLoading } = useFoundation();
    return {
        cohorts: getCohorts(),
        competitors: getCompetitors(),
        campaigns: getCampaigns(),
        isLoading,
    };
}
