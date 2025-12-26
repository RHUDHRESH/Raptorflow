'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Campaign, CampaignObjective, RAGStatus } from '@/lib/campaigns-types';
import { getCampaignProgress, getMovesByCampaign } from '@/lib/campaigns';
import { CampaignCard } from '@/components/campaigns/CampaignCard';
import { NewCampaignWizard } from '@/components/campaigns/NewCampaignWizard';
import { Button } from '@/components/ui/button';
import {
    Plus,
    Search,
    ChevronDown,
    Target,
    Zap,
    Users,
    DollarSign,
    RefreshCw,
    Rocket,
    Briefcase,
    ArrowRight
} from 'lucide-react';
import { useCampaigns } from '@/hooks/useCampaigns';
import { InferenceErrorBoundary } from '@/components/layout/InferenceErrorBoundary';
import styles from '@/components/campaigns/Campaigns.module.css';

type FilterStatus = 'all' | 'active' | 'planned' | 'paused' | 'completed';
type FilterObjective = 'all' | CampaignObjective;
type FilterRAG = 'all' | RAGStatus;

export default function CampaignsPage() {
    const { campaigns, refresh: refreshCampaigns } = useCampaigns(10000);
    const [showWizard, setShowWizard] = useState(false);
    const [campaignMetadata, setCampaignMetadata] = useState<Record<string, any>>({});

    // Filters
    const [statusFilter, setStatusFilter] = useState<FilterStatus>('active');
    const [objectiveFilter, setObjectiveFilter] = useState<FilterObjective>('all');
    const [ragFilter, setRagFilter] = useState<FilterRAG>('all');

    useEffect(() => {
        const fetchMeta = async () => {
            const meta: Record<string, any> = {};
            for (const c of campaigns) {
                const [progress, moves] = await Promise.all([
                    getCampaignProgress(c.id),
                    getMovesByCampaign(c.id)
                ]);
                meta[c.id] = {
                    progress,
                    activeMove: moves.find(m => m.status === 'active'),
                    queuedMoves: moves.filter(m => m.status === 'queued'),
                    completedMoves: moves.filter(m => m.status === 'completed')
                };
            }
            setCampaignMetadata(meta);
        };
        if (campaigns.length > 0) fetchMeta();
    }, [campaigns]);

    const handleCampaignCreated = useCallback(() => {
        refreshCampaigns();
        setShowWizard(false);
    }, [refreshCampaigns]);

    // Filter campaigns
    const filteredCampaigns = campaigns.filter(c => {
        if (statusFilter !== 'all' && c.status !== statusFilter) return false;
        if (objectiveFilter !== 'all' && c.objective !== objectiveFilter) return false;
        if (ragFilter !== 'all' && c.ragStatus !== ragFilter) return false;
        return true;
    });

    // Group by urgency
    const needsAttention = filteredCampaigns.filter(c =>
        c.status === 'active' && (c.ragStatus === 'amber' || c.ragStatus === 'red')
    );
    const activeCampaigns = filteredCampaigns.filter(c =>
        c.status === 'active' && c.ragStatus === 'green'
    );
    const scheduledCampaigns = filteredCampaigns.filter(c => c.status === 'planned');
    const completedCampaigns = filteredCampaigns.filter(c =>
        c.status === 'completed' || c.status === 'archived'
    );

    const isEmpty = campaigns.length === 0;

    return (
        <AppLayout>
            <InferenceErrorBoundary>
                <div className={styles.pageContainer}>
                    {/* Sticky Top Bar */}
                    <div className={styles.topBar}>
                        <div className={styles.topBarLeft}>
                            <h1 className={styles.pageTitle}>Campaigns</h1>
                        </div>

                        <div className={styles.topBarRight}>
                            <button className={styles.searchBtn}>
                                <Search style={{ width: 18, height: 18 }} />
                            </button>
                            <button
                                className={styles.primaryBtn}
                                onClick={() => setShowWizard(true)}
                            >
                                <Plus style={{ width: 16, height: 16 }} />
                                New Campaign
                            </button>
                        </div>
                    </div>

                    {/* Command Strip - Filters */}
                    {!isEmpty && (
                        <div className={styles.commandStrip}>
                            <button
                                className={`${styles.filterChip} ${statusFilter === 'active' ? styles.active : ''}`}
                                onClick={() => setStatusFilter(statusFilter === 'active' ? 'all' : 'active')}
                            >
                                Status: Active
                                <ChevronDown style={{ width: 14, height: 14 }} />
                            </button>

                            <button
                                className={`${styles.filterChip} ${objectiveFilter !== 'all' ? styles.active : ''}`}
                                onClick={() => setObjectiveFilter('all')}
                            >
                                Objective
                                <ChevronDown style={{ width: 14, height: 14 }} />
                            </button>

                            <button
                                className={`${styles.filterChip} ${ragFilter !== 'all' ? styles.active : ''}`}
                                onClick={() => setRagFilter('all')}
                            >
                                RAG
                                <ChevronDown style={{ width: 14, height: 14 }} />
                            </button>

                            <button className={styles.filterChip}>
                                Duration
                                <ChevronDown style={{ width: 14, height: 14 }} />
                            </button>

                            <button className={`${styles.filterChip} ${styles.sortChip}`}>
                                Sort: Needs attention
                                <ChevronDown style={{ width: 14, height: 14 }} />
                            </button>
                        </div>
                    )}

                    {/* Main Content */}
                    <div className={styles.mainContent}>
                        {isEmpty ? (
                            /* Empty State */
                            <div className={styles.emptyState}>
                                <div className={styles.emptyIcon}>
                                    <Target style={{ width: 36, height: 36 }} />
                                </div>
                                <h2 className={styles.emptyTitle}>Launch Your First Campaign</h2>
                                <p className={styles.emptyText}>
                                    Campaigns are 90-day focused initiatives. Each one contains Moves—tactical sprints that drive real results.
                                </p>
                                <div className={styles.emptyActions}>
                                    <button
                                        className={styles.emptyTile}
                                        onClick={() => setShowWizard(true)}
                                    >
                                        <div className={styles.emptyTileIcon}>
                                            <Rocket style={{ width: 22, height: 22 }} />
                                        </div>
                                        <div className={styles.emptyTileTitle}>Acquisition Campaign</div>
                                        <div className={styles.emptyTileDesc}>
                                            Book calls, generate leads, grow pipeline
                                        </div>
                                    </button>
                                    <button
                                        className={styles.emptyTile}
                                        onClick={() => setShowWizard(true)}
                                    >
                                        <div className={styles.emptyTileIcon}>
                                            <Briefcase style={{ width: 22, height: 22 }} />
                                        </div>
                                        <div className={styles.emptyTileTitle}>Custom Campaign</div>
                                        <div className={styles.emptyTileDesc}>
                                            Build from scratch with your own objective
                                        </div>
                                    </button>
                                </div>
                            </div>
                        ) : (
                            /* Campaign Sections */
                            <>
                                {/* Needs Attention */}
                                {needsAttention.length > 0 && (
                                    <div className={styles.section}>
                                        <div className={styles.sectionHeader}>
                                            <div className={styles.sectionIndicator}>
                                                <div className={`${styles.sectionDot} ${styles.attention}`} />
                                                <span className={styles.sectionTitle}>Needs Attention</span>
                                            </div>
                                            <span className={styles.sectionCount}>({needsAttention.length})</span>
                                        </div>
                                        <div className={`${styles.campaignsGrid} ${needsAttention.length === 1 ? styles.single : ''}`}>
                                            {needsAttention.map(campaign => (
                                                <CampaignCard
                                                    key={campaign.id}
                                                    campaign={campaign}
                                                    progress={campaignMetadata[campaign.id]?.progress}
                                                    activeMove={campaignMetadata[campaign.id]?.activeMove}
                                                    variant="attention"
                                                />
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Active */}
                                {activeCampaigns.length > 0 && (
                                    <div className={styles.section}>
                                        <div className={styles.sectionHeader}>
                                            <div className={styles.sectionIndicator}>
                                                <div className={`${styles.sectionDot} ${styles.active}`} />
                                                <span className={styles.sectionTitle}>Active</span>
                                            </div>
                                            <span className={styles.sectionCount}>({activeCampaigns.length})</span>
                                        </div>
                                        <div className={styles.campaignsGrid}>
                                            {activeCampaigns.map(campaign => (
                                                <CampaignCard
                                                    key={campaign.id}
                                                    campaign={campaign}
                                                    progress={campaignMetadata[campaign.id]?.progress}
                                                    activeMove={campaignMetadata[campaign.id]?.activeMove}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Scheduled */}
                                {scheduledCampaigns.length > 0 && (
                                    <div className={styles.section}>
                                        <div className={styles.sectionHeader}>
                                            <div className={styles.sectionIndicator}>
                                                <div className={`${styles.sectionDot} ${styles.scheduled}`} />
                                                <span className={styles.sectionTitle}>Scheduled</span>
                                            </div>
                                            <span className={styles.sectionCount}>({scheduledCampaigns.length})</span>
                                        </div>
                                        <div className={styles.campaignsGrid}>
                                            {scheduledCampaigns.map(campaign => (
                                                <CampaignCard
                                                    key={campaign.id}
                                                    campaign={campaign}
                                                    progress={campaignMetadata[campaign.id]?.progress}
                                                    activeMove={campaignMetadata[campaign.id]?.activeMove}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Completed / Archived */}
                                {completedCampaigns.length > 0 && (
                                    <div className={styles.section}>
                                        <div className={styles.sectionHeader}>
                                            <div className={styles.sectionIndicator}>
                                                <div className={`${styles.sectionDot} ${styles.completed}`} />
                                                <span className={styles.sectionTitle}>Completed / Archived</span>
                                            </div>
                                            <span className={styles.sectionCount}>({completedCampaigns.length})</span>
                                            <button className={styles.expandBtn}>
                                                Expand
                                                <ArrowRight style={{ width: 14, height: 14 }} />
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                </div>
            </InferenceErrorBoundary>

            <NewCampaignWizard
                open={showWizard}
                onOpenChange={setShowWizard}
                onComplete={handleCampaignCreated}
            />
        </AppLayout>
    );
}
