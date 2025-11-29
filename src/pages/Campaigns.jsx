/**
 * Campaigns Page
 * 
 * Central view for all campaigns with health tracking, pacing indicators,
 * and quick actions.
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
    Plus,
    Search,
    Play,
    Pause,
    TrendingUp,
    AlertCircle,
    CheckCircle2,
    Clock,
    Target,
    Users,
    Calendar,
    Zap,
    Eye,
    Edit2,
    Archive
} from 'lucide-react';
import { cn } from '../utils/cn';
import { PageHeader, LuxeButton, LuxeCard, LuxeBadge, LuxeInput, LuxeEmptyState, LuxeStat } from '../components/ui/PremiumUI';
import { pageTransition, fadeInUp, staggerContainer } from '../utils/animations';
import { campaignService } from '../services/campaignService';
import { useWorkspace } from '../context/WorkspaceContext';

// =============================================================================
// CONSTANTS
// =============================================================================

const CAMPAIGN_STATUSES = {
    draft: { label: 'Draft', color: 'neutral', icon: Clock },
    active: { label: 'Active', color: 'dark', icon: Play },
    paused: { label: 'Paused', color: 'neutral', icon: Pause },
    completed: { label: 'Completed', color: 'neutral', icon: CheckCircle2 },
    archived: { label: 'Archived', color: 'neutral', icon: Archive },
};

const PACING_STATUS = {
    ahead: { label: 'Ahead', color: 'dark', icon: TrendingUp },
    on_track: { label: 'On Track', color: 'neutral', icon: CheckCircle2 },
    behind: { label: 'Behind', color: 'neutral', icon: Clock },
    at_risk: { label: 'At Risk', color: 'neutral', icon: AlertCircle },
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function Campaigns() {
    const navigate = useNavigate();
    const { activeWorkspace } = useWorkspace();
    const [campaigns, setCampaigns] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const [filterObjective, setFilterObjective] = useState('all');

    useEffect(() => {
        const fetchCampaigns = async () => {
            if (!activeWorkspace?.id) return;
            setIsLoading(true);
            try {
                const { data, error } = await campaignService.getCampaigns(activeWorkspace.id);
                if (data) {
                    setCampaigns(data);
                } else if (error) {
                    console.error("Failed to fetch campaigns", error);
                }
            } catch (err) {
                console.error("Error fetching campaigns", err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchCampaigns();
    }, [activeWorkspace]);

    // Filter campaigns
    const filteredCampaigns = campaigns.filter(campaign => {
        const matchesSearch = campaign.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            campaign.description.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = filterStatus === 'all' || campaign.status === filterStatus;
        const matchesObjective = filterObjective === 'all' || campaign.objective === filterObjective;
        return matchesSearch && matchesStatus && matchesObjective;
    });

    // Calculate summary stats
    const stats = {
        total: campaigns.length,
        active: campaigns.filter(c => c.status === 'active').length,
        avg_health: Math.round(campaigns.reduce((sum, c) => sum + c.health_score, 0) / campaigns.length),
        at_risk: campaigns.filter(c => c.health_score < 60).length,
    };

    const handlePauseCampaign = (campaignId) => {
        setCampaigns(campaigns.map(c =>
            c.id === campaignId ? { ...c, status: 'paused' } : c
        ));
    };

    const handleResumeCampaign = (campaignId) => {
        setCampaigns(campaigns.map(c =>
            c.id === campaignId ? { ...c, status: 'active' } : c
        ));
    };

    return (
        <motion.div
            className="space-y-12"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={pageTransition}
        >
            <motion.div variants={fadeInUp}>
                <PageHeader
                    title="Campaigns"
                    subtitle="Orchestrate all marketing activities from positioning to execution."
                    action={
                        <LuxeButton
                            onClick={() => navigate('/campaigns/new')}
                            icon={Plus}
                            size="lg"
                        >
                            New Campaign
                        </LuxeButton>
                    }
                />
            </motion.div>

            {/* Stats Overview */}
            <motion.div
                className="grid grid-cols-1 md:grid-cols-4 gap-6"
                variants={staggerContainer}
            >
                <motion.div variants={fadeInUp}>
                    <LuxeStat
                        label="Total Campaigns"
                        value={stats.total}
                        icon={Target}
                    />
                </motion.div>

                <motion.div variants={fadeInUp}>
                    <LuxeStat
                        label="Active"
                        value={stats.active}
                        icon={Play}
                    />
                </motion.div>

                <motion.div variants={fadeInUp}>
                    <LuxeStat
                        label="Avg Health"
                        value={isNaN(stats.avg_health) ? '—' : `${stats.avg_health}%`}
                        icon={TrendingUp}
                    />
                </motion.div>

                <motion.div variants={fadeInUp}>
                    <LuxeStat
                        label="At Risk"
                        value={stats.at_risk}
                        icon={AlertCircle}
                    />
                </motion.div>
            </motion.div>

            {/* Search & Filters */}
            <div className="flex flex-col md:flex-row gap-4 items-end">
                <div className="flex-1">
                    <LuxeInput
                        icon={Search}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Search campaigns..."
                        className="h-12"
                    />
                </div>

                <div className="relative min-w-[180px]">
                    <select
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                        className="w-full h-12 px-4 bg-white border border-neutral-200 rounded-md text-sm font-medium text-neutral-900 focus:outline-none focus:border-neutral-900 focus:ring-1 focus:ring-neutral-900 appearance-none transition-all"
                    >
                        <option value="all">All Statuses</option>
                        <option value="draft">Draft</option>
                        <option value="active">Active</option>
                        <option value="paused">Paused</option>
                        <option value="completed">Completed</option>
                    </select>
                    <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-neutral-500">
                        <svg width="10" height="6" viewBox="0 0 10 6" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M1 1L5 5L9 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                </div>

                <div className="relative min-w-[180px]">
                    <select
                        value={filterObjective}
                        onChange={(e) => setFilterObjective(e.target.value)}
                        className="w-full h-12 px-4 bg-white border border-neutral-200 rounded-md text-sm font-medium text-neutral-900 focus:outline-none focus:border-neutral-900 focus:ring-1 focus:ring-neutral-900 appearance-none transition-all"
                    >
                        <option value="all">All Objectives</option>
                        <option value="awareness">Awareness</option>
                        <option value="consideration">Consideration</option>
                        <option value="conversion">Conversion</option>
                        <option value="retention">Retention</option>
                        <option value="advocacy">Advocacy</option>
                    </select>
                    <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-neutral-500">
                        <svg width="10" height="6" viewBox="0 0 10 6" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M1 1L5 5L9 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                </div>
            </div>

            {/* Campaigns List */}
            <motion.div
                className="space-y-4"
                variants={staggerContainer}
            >
                {filteredCampaigns.map((campaign, index) => {
                    const statusInfo = CAMPAIGN_STATUSES[campaign.status];
                    const pacingInfo = PACING_STATUS[campaign.pacing_status];
                    const StatusIcon = statusInfo.icon;
                    const PacingIcon = pacingInfo.icon;

                    const progress = (campaign.current_value / campaign.target_value) * 100;
                    const budgetProgress = (campaign.budget_spent / campaign.budget_total) * 100;
                    const moveProgress = (campaign.completed_moves / campaign.total_moves) * 100;

                    return (
                        <motion.div
                            key={campaign.id}
                            variants={fadeInUp}
                        >
                            <LuxeCard className="p-6 hover:shadow-md transition-shadow group" onClick={() => navigate(`/campaigns/${campaign.id}`)}>
                                <div className="flex items-start justify-between mb-6">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            <h3 className="font-display text-xl text-neutral-900 group-hover:text-neutral-700 transition-colors">{campaign.name}</h3>
                                            <LuxeBadge variant={statusInfo.color === 'dark' ? "dark" : "neutral"}>
                                                {statusInfo.label}
                                            </LuxeBadge>
                                            <LuxeBadge variant={pacingInfo.color === 'dark' ? "dark" : "neutral"}>
                                                {pacingInfo.label}
                                            </LuxeBadge>
                                        </div>
                                        <p className="text-sm text-neutral-500 max-w-3xl leading-relaxed">{campaign.description}</p>
                                    </div>

                                    <div className="flex items-center gap-4">
                                        <div className="text-right">
                                            <div className="text-2xl font-display font-medium text-neutral-900">
                                                {campaign.health_score}%
                                            </div>
                                            <div className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Health</div>
                                        </div>

                                        <div className="flex items-center gap-1">
                                            <button
                                                onClick={(e) => { e.stopPropagation(); navigate(`/campaigns/${campaign.id}/edit`); }}
                                                className="p-2 text-neutral-400 hover:text-neutral-900 hover:bg-neutral-100 rounded-md transition-colors"
                                            >
                                                <Edit2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                {/* Grid Info */}
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pt-6 border-t border-neutral-100">
                                    <div>
                                        <div className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-1">Primary Metric</div>
                                        <div className="flex items-baseline gap-2">
                                            <span className="text-sm font-medium text-neutral-900">
                                                {campaign.current_value} / {campaign.target_value}
                                            </span>
                                            <span className="text-xs text-neutral-500">{campaign.primary_metric}</span>
                                        </div>
                                        <div className="w-full h-1 bg-neutral-100 mt-2">
                                            <div
                                                className="h-full bg-neutral-900"
                                                style={{ width: `${Math.min(progress, 100)}%` }}
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <div className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-1">Budget</div>
                                        <div className="flex items-baseline gap-2">
                                            <span className="text-sm font-medium text-neutral-900">
                                                ${(campaign.budget_spent / 1000).toFixed(1)}k
                                            </span>
                                            <span className="text-xs text-neutral-500">/ ${(campaign.budget_total / 1000).toFixed(1)}k</span>
                                        </div>
                                        <div className="w-full h-1 bg-neutral-100 mt-2">
                                            <div
                                                className="h-full bg-neutral-400"
                                                style={{ width: `${Math.min(budgetProgress, 100)}%` }}
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <div className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-1">Timeline</div>
                                        <div className="text-sm font-medium text-neutral-900">
                                            {new Date(campaign.start_date).toLocaleDateString()} — {new Date(campaign.end_date).toLocaleDateString()}
                                        </div>
                                    </div>

                                    <div>
                                        <div className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-1">Scope</div>
                                        <div className="flex flex-wrap gap-2">
                                            <span className="text-xs text-neutral-600 bg-neutral-50 px-2 py-0.5 rounded border border-neutral-100">
                                                {campaign.cohorts.length} Cohorts
                                            </span>
                                            <span className="text-xs text-neutral-600 bg-neutral-50 px-2 py-0.5 rounded border border-neutral-100">
                                                {campaign.channels.length} Channels
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </LuxeCard>
                        </motion.div>
                    );
                })}
            </motion.div>

            {/* Loading State */}
            {isLoading && (
                <div className="flex justify-center py-20">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900"></div>
                </div>
            )}

            {/* Empty State */}
            {!isLoading && filteredCampaigns.length === 0 && (
                <LuxeEmptyState
                    icon={Target}
                    title="No campaigns found"
                    description={searchTerm || filterStatus !== 'all' || filterObjective !== 'all'
                        ? 'Try adjusting your filters to see results.'
                        : 'Create your first campaign to get started with marketing orchestration.'}
                    action={
                        !searchTerm && filterStatus === 'all' && filterObjective === 'all' ? (
                            <LuxeButton
                                onClick={() => navigate('/campaigns/new')}
                                icon={Plus}
                            >
                                Create Campaign
                            </LuxeButton>
                        ) : null
                    }
                />
            )}
        </motion.div>
    );
}
