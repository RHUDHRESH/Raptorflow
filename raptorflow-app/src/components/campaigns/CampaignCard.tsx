'use client';

import React, { useState, useEffect } from 'react';
import { Campaign, OBJECTIVE_LABELS, CHANNEL_LABELS, RAGStatus } from '@/lib/campaigns-types';
import { ChevronRight, MoreHorizontal, Play, Target, Zap, RefreshCw, DollarSign, Rocket, ArrowRight } from 'lucide-react';
import { getCampaignProgress } from '@/lib/campaigns';
import { useRouter } from 'next/navigation';
import styles from './Campaigns.module.css';

interface CampaignCardProps {
    campaign: Campaign;
    progress?: {
        totalMoves: number;
        completedMoves: number;
        weekNumber: number;
        totalWeeks: number;
    };
    activeMove?: any;
    onClick?: () => void;
    variant?: 'default' | 'attention';
}

const OBJECTIVE_ICONS: Record<string, any> = {
    acquire: Rocket,
    activate: Zap,
    retain: RefreshCw,
    monetize: DollarSign,
    expand: Target,
};

export function CampaignCard({ campaign, progress: initialProgress, activeMove, onClick, variant = 'default' }: CampaignCardProps) {
    const router = useRouter();
    const [progress, setProgress] = useState(initialProgress);

    useEffect(() => {
        if (!initialProgress) {
            getCampaignProgress(campaign.id).then(setProgress);
        }
    }, [campaign.id, initialProgress]);

    // Calculate pacing
    const dayOfCampaign = campaign.timeline?.startDate
        ? Math.floor((Date.now() - new Date(campaign.timeline.startDate).getTime()) / (1000 * 60 * 60 * 24)) + 1
        : 1;
    const totalDays = campaign.timeline?.duration || 90;
    const target = campaign.metrics?.target || 0;
    const current = campaign.metrics?.current || 0;
    const expectedByNow = Math.floor((dayOfCampaign / totalDays) * target);
    const progressPercent = target > 0 ? Math.round((current / target) * 100) : 0;
    const ragStatus = campaign.ragStatus || 'green';

    const Icon = OBJECTIVE_ICONS[campaign.objective] || Target;

    const ragColors: Record<RAGStatus, string> = {
        green: 'green',
        amber: 'amber',
        red: 'red',
    };

    const handleClick = () => {
        if (onClick) {
            onClick();
        } else {
            router.push(`/campaigns/${campaign.id}`);
        }
    };

    return (
        <div
            className={`${styles.campaignCard} ${variant === 'attention' ? styles.attention : ''}`}
            onClick={handleClick}
        >
            {/* Header */}
            <div className={styles.cardHeader}>
                <div className={styles.cardLeft}>
                    <div className={`${styles.objectiveIcon} ${styles[campaign.objective]}`}>
                        <Icon style={{ width: 18, height: 18 }} />
                    </div>
                    <div className={styles.cardTitleGroup}>
                        <span className={`${styles.objectiveBadge} ${styles[campaign.objective]}`}>
                            {OBJECTIVE_LABELS[campaign.objective]?.label || campaign.objective}
                        </span>
                        <h3 className={styles.cardTitle}>{campaign.name}</h3>
                        {campaign.targetAudience && (
                            <span className={styles.cardSubtitle}>{campaign.targetAudience}</span>
                        )}
                    </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    {campaign.channels?.slice(0, 2).map(ch => (
                        <span key={ch} className={styles.chip}>
                            {CHANNEL_LABELS[ch]}
                        </span>
                    ))}
                    <button className={styles.moreBtn} onClick={e => e.stopPropagation()}>
                        <MoreHorizontal style={{ width: 16, height: 16 }} />
                    </button>
                </div>
            </div>

            {/* Pacing Section */}
            <div className={styles.pacingSection}>
                <div className={styles.pacingRow}>
                    <span className={styles.pacingText}>
                        Day <span className={styles.pacingValue}>{Math.min(dayOfCampaign, totalDays)}/{totalDays}</span>
                        {' • '}Target: <span className={styles.pacingValue}>{expectedByNow}</span> by now
                        {' • '}<span className={styles.pacingValue}>{current}</span> actual
                    </span>
                    <div className={styles.progressBar}>
                        <div
                            className={`${styles.progressFill} ${styles[ragColors[ragStatus]]}`}
                            style={{ width: `${Math.min(progressPercent, 100)}%` }}
                        />
                    </div>
                </div>

                <div className={`${styles.ragBadge} ${styles[ragColors[ragStatus]]}`}>
                    <span className={`${styles.ragDot} ${styles[ragColors[ragStatus]]}`} />
                    {ragStatus.toUpperCase()}
                    {ragStatus !== 'green' && (
                        <span className={styles.ragReason}>
                            — {ragStatus === 'amber' ? 'Behind pace' : 'Needs attention'}
                        </span>
                    )}
                </div>
            </div>

            {/* Move Info */}
            <div className={styles.moveInfo}>
                <span className={styles.moveText}>
                    {activeMove ? (
                        <>
                            Moves: <span className={styles.moveHighlight}>1 active</span>
                            {activeMove.name && ` • ${activeMove.name}`}
                            {` • Day ${activeMove.currentDay || 1}/${activeMove.duration || 7}`}
                        </>
                    ) : (
                        <>
                            {progress?.completedMoves || 0}/{progress?.totalMoves || 0} moves completed
                        </>
                    )}
                </span>

                <div className={styles.cardActions}>
                    {!activeMove && campaign.status === 'active' && (
                        <button className={styles.actionBtn} onClick={e => {
                            e.stopPropagation();
                            router.push(`/campaigns/${campaign.id}`);
                        }}>
                            Start next move
                        </button>
                    )}
                    <button className={styles.secondaryBtn} onClick={e => {
                        e.stopPropagation();
                        router.push(`/campaigns/${campaign.id}`);
                    }}>
                        Open
                        <ChevronRight style={{ width: 14, height: 14 }} />
                    </button>
                </div>
            </div>
        </div>
    );
}
