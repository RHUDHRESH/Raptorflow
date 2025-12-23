'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Campaign } from '@/lib/campaigns-types';
import { getCampaigns } from '@/lib/campaigns';
import { CampaignCard } from '@/components/campaigns/CampaignCard';
import { CampaignEmptyState } from '@/components/campaigns/CampaignEmptyState';
import { NewCampaignWizard } from '@/components/campaigns/NewCampaignWizard';
import { CampaignDetail } from '@/components/campaigns/CampaignDetail';
import { Button } from '@/components/ui/button';
import { StrategicPivotCard } from '@/components/campaigns/StrategicPivotCard';
import { Sparkles, Plus } from 'lucide-react';
import { toast } from 'sonner';

export default function CampaignsPage() {
    const { campaigns, refresh: refreshCampaigns } = useCampaigns(10000);
    const [showWizard, setShowWizard] = useState(false);
    const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
    const [campaignMetadata, setCampaignMetadata] = useState<Record<string, any>>({});

    // Task 21: Mock pivot for display
    const mockPivot = {
        id: 'p1',
        title: 'LinkedIn Outreach Pivot',
        description: 'Focus on Founders in B2B SaaS Niche',
        rationale: 'Recent agent research shows 40% higher engagement in this segment.',
        severity: 'medium' as const
    };

    useEffect(() => {
        const fetchMeta = async () => {
            const meta: Record<string, any> = {};
            for (const c of campaigns) {
                const [progress, moves] = await Promise.all([
                    getCampaignProgress(c.id),
                    getMovesByCampaign(c.id)
                ]);
                meta[c.id] = { progress, activeMove: moves.find(m => m.status === 'active') };
            }
            setCampaignMetadata(meta);
        };
        if (campaigns.length > 0) fetchMeta();
    }, [campaigns]);

    const handleCampaignCreated = useCallback(() => {
        refreshCampaigns();
        setShowWizard(false);
    }, [refreshCampaigns]);

    const handleCampaignUpdated = useCallback((campaign: Campaign) => {
        refreshCampaigns(); // Proper sync
        setSelectedCampaign(campaign);
    }, [refreshCampaigns]);

    const handleCampaignDeleted = useCallback((campaignId: string) => {
        refreshCampaigns(); // Proper sync
        setSelectedCampaign(null);
    }, [refreshCampaigns]);

    const activeCampaigns = campaigns.filter(c => c.status === 'active' || c.status === 'planned');
    const otherCampaigns = campaigns.filter(c => c.status !== 'active' && c.status !== 'planned');

    return (
        <AppLayout>
            <InferenceErrorBoundary>
                <div className="max-w-[1200px] mx-auto px-12 py-12 space-y-12 pb-24 animate-in fade-in duration-500">
                    <div className="flex items-end justify-between border-b border-zinc-200 dark:border-zinc-800 pb-8">
                        <div>
                            <div className="text-xs font-bold uppercase tracking-[0.15em] text-zinc-400 dark:text-zinc-500 mb-3 ml-1">
                                Execution
                            </div>
                            <h1 className="text-[40px] leading-[1.1] font-display font-medium text-zinc-900 dark:text-zinc-100">
                                Campaigns
                            </h1>
                            <p className="text-base text-zinc-500 dark:text-zinc-400 mt-4 max-w-xl leading-relaxed">
                                Organize your marketing into focused 90-day initiatives.
                                Stop guessing, start executing.
                            </p>
                        </div>
                        {campaigns.length > 0 && (
                            <Button
                                onClick={() => setShowWizard(true)}
                                className="rounded-full bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-100 h-11 px-6 shadow-sm hover:shadow-md transition-all"
                            >
                                <Plus className="w-4 h-4 mr-2" />
                                Create Campaign
                            </Button>
                        )}
                    </div>

                    {/* Strategic Pivots (Task 21) */}
                    {activeCampaigns.length > 0 && (
                        <div className="space-y-6">
                            <div className="flex items-center gap-2 mb-2">
                                <Sparkles className="h-4 w-4 text-accent" />
                                <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-500 dark:text-zinc-400">
                                    Agent Recommendations
                                </h3>
                            </div>
                            <StrategicPivotCard
                                pivot={mockPivot}
                                onApply={() => toast.success('Pivot applied to campaign strategy')}
                                onIgnore={() => {}}
                            />
                        </div>
                    )}

                    <div className="min-h-[400px]">
                        {campaigns.length === 0 ? (
                            <CampaignEmptyState onCreateCampaign={() => setShowWizard(true)} />
                        ) : (
                            <div className="space-y-12 animate-in slide-in-from-bottom-4 duration-700 fade-in fill-mode-backwards delay-150">
                                {activeCampaigns.length > 0 && (
                                    <div className="space-y-6">
                                        <div className="flex items-center gap-2 mb-2">
                                            <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 ml-1" />
                                            <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-500 dark:text-zinc-400">
                                                Active Initiatives
                                            </h3>
                                        </div>
                                        <div className="grid grid-cols-1 gap-6">
                                            {activeCampaigns.map(campaign => (
                                                <div
                                                    key={campaign.id}
                                                    className="group transition-all duration-300 hover:-translate-y-1"
                                                >
                                                    <CampaignCard
                                                        campaign={campaign}
                                                        progress={campaignMetadata[campaign.id]?.progress}
                                                        activeMove={campaignMetadata[campaign.id]?.activeMove}
                                                        onClick={() => setSelectedCampaign(campaign)}
                                                    />
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {otherCampaigns.length > 0 && (
                                    <div className="space-y-6">
                                        <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-400 dark:text-zinc-600 pl-4">
                                            Library / Archives
                                        </h3>
                                        <div className="grid grid-cols-1 gap-6 opacity-80 hover:opacity-100 transition-opacity">
                                            {otherCampaigns.map(campaign => (
                                                <div
                                                    key={campaign.id}
                                                    className="group transition-all duration-300 hover:-translate-y-1"
                                                >
                                                    <CampaignCard
                                                        campaign={campaign}
                                                        progress={campaignMetadata[campaign.id]?.progress}
                                                        activeMove={campaignMetadata[campaign.id]?.activeMove}
                                                        onClick={() => setSelectedCampaign(campaign)}
                                                    />
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </InferenceErrorBoundary>

            <NewCampaignWizard
                open={showWizard}
                onOpenChange={setShowWizard}
                onComplete={handleCampaignCreated}
            />

            <CampaignDetail
                campaign={selectedCampaign}
                open={!!selectedCampaign}
                onOpenChange={(open) => !open && setSelectedCampaign(null)}
                onUpdate={handleCampaignUpdated}
                onDelete={handleCampaignDeleted}
                onRefresh={refreshCampaigns}
            />
        </AppLayout>
    );
}
