/**
 * Campaign Dashboard
 * 
 * Central view for all campaigns with health tracking, pacing indicators,
 * and quick actions. Integrates with campaign_service.py for real-time data.
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
    Plus,
    Search,
    Filter,
    Play,
    Pause,
    MoreVertical,
    TrendingUp,
    TrendingDown,
    AlertCircle,
    CheckCircle2,
    Clock,
    Target,
    Users,
    BarChart3,
    Calendar,
    DollarSign,
    Zap,
    Eye,
    Edit2,
    Copy,
    Archive,
    ArrowRight
} from 'lucide-react';
import { cn } from '../../utils/cn';

// =============================================================================
// CONSTANTS
// =============================================================================

const CAMPAIGN_STATUSES = {
    draft: { label: 'Draft', color: 'neutral', icon: Clock },
    active: { label: 'Active', color: 'green', icon: Play },
    paused: { label: 'Paused', color: 'amber', icon: Pause },
    completed: { label: 'Completed', color: 'blue', icon: CheckCircle2 },
    archived: { label: 'Archived', color: 'neutral', icon: Archive },
};

const PACING_STATUS = {
    ahead: { label: 'Ahead', color: 'green', icon: TrendingUp },
    on_track: { label: 'On Track', color: 'blue', icon: CheckCircle2 },
    behind: { label: 'Behind', color: 'amber', icon: Clock },
    at_risk: { label: 'At Risk', color: 'red', icon: AlertCircle },
};

// Mock campaigns data
const MOCK_CAMPAIGNS = [
    {
        id: 'camp-1',
        name: 'Q1 Enterprise CTO Conversion',
        description: 'Convert Enterprise CTOs to demo requests',
        status: 'active',
        objective: 'conversion',
        health_score: 85,
        pacing_status: 'ahead',
        start_date: '2025-01-01',
        end_date: '2025-03-31',
        budget_total: 50000,
        budget_spent: 18000,
        primary_metric: 'Demo requests',
        target_value: 50,
        current_value: 23,
        cohorts: [
            { id: 'c1', name: 'Enterprise CTOs', priority: 'primary' }
        ],
        channels: ['LinkedIn', 'Email', 'Phone'],
        total_moves: 4,
        completed_moves: 2,
    },
    {
        id: 'camp-2',
        name: 'Startup Founder Awareness',
        description: 'Build awareness among startup founders',
        status: 'active',
        objective: 'awareness',
        health_score: 72,
        pacing_status: 'on_track',
        start_date: '2025-01-15',
        end_date: '2025-02-28',
        budget_total: 25000,
        budget_spent: 12000,
        primary_metric: 'Impressions',
        target_value: 100000,
        current_value: 48000,
        cohorts: [
            { id: 'c2', name: 'Startup Founders', priority: 'primary' }
        ],
        channels: ['Twitter', 'LinkedIn', 'Email'],
        total_moves: 3,
        completed_moves: 1,
    },
    {
        id: 'camp-3',
        name: 'Marketing Director Retention',
        description: 'Keep marketing directors engaged',
        status: 'paused',
        objective: 'retention',
        health_score: 58,
        pacing_status: 'behind',
        start_date: '2024-12-01',
        end_date: '2025-03-31',
        budget_total: 15000,
        budget_spent: 8000,
        primary_metric: 'NPS',
        target_value: 50,
        current_value: 42,
        cohorts: [
            { id: 'c3', name: 'Marketing Directors', priority: 'primary' }
        ],
        channels: ['Email', 'Webinars'],
        total_moves: 5,
        completed_moves: 3,
    },
];

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function CampaignDashboard() {
    const navigate = useNavigate();
    const [campaigns, setCampaigns] = useState(MOCK_CAMPAIGNS);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const [filterObjective, setFilterObjective] = useState('all');

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
        <div className="space-y-8 animate-fade-in">
            {/* Hero Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="runway-card relative overflow-hidden p-10"
            >
                <div className="absolute inset-0 bg-gradient-to-r from-white via-neutral-50 to-white" />
                <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-4">
                        <span className="micro-label tracking-[0.5em]">Campaign Command Center</span>
                        <span className="h-px w-16 bg-neutral-200" />
                    </div>

                    <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased mb-4">
                        Campaigns
                    </h1>

                    <p className="text-neutral-600 max-w-2xl mb-6">
                        Orchestrate all marketing activities from positioning to execution
                    </p>

                    <Link
                        to="/strategy/campaigns/new"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-neutral-900 text-white rounded-lg font-medium hover:bg-neutral-800 transition-colors"
                    >
                        <Plus className="w-5 h-5" />
                        New Campaign
                    </Link>
                </div>
            </motion.div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 }}
                    className="runway-card p-6"
                >
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-neutral-500">Total Campaigns</span>
                        <Target className="w-5 h-5 text-neutral-400" />
                    </div>
                    <div className="text-3xl font-bold text-neutral-900">{stats.total}</div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                    className="runway-card p-6"
                >
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-neutral-500">Active</span>
                        <Play className="w-5 h-5 text-green-600" />
                    </div>
                    <div className="text-3xl font-bold text-green-600">{stats.active}</div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 }}
                    className="runway-card p-6"
                >
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-neutral-500">Avg Health</span>
                        <TrendingUp className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="text-3xl font-bold text-blue-600">{stats.avg_health}%</div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.4 }}
                    className="runway-card p-6"
                >
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-neutral-500">At Risk</span>
                        <AlertCircle className="w-5 h-5 text-red-600" />
                    </div>
                    <div className="text-3xl font-bold text-red-600">{stats.at_risk}</div>
                </motion.div>
            </div>

            {/* Search & Filters */}
            <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1 relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                    <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Search campaigns..."
                        className="w-full pl-12 pr-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                    />
                </div>

                <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                >
                    <option value="all">All Statuses</option>
                    <option value="draft">Draft</option>
                    <option value="active">Active</option>
                    <option value="paused">Paused</option>
                    <option value="completed">Completed</option>
                </select>

                <select
                    value={filterObjective}
                    onChange={(e) => setFilterObjective(e.target.value)}
                    className="px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                >
                    <option value="all">All Objectives</option>
                    <option value="awareness">Awareness</option>
                    <option value="consideration">Consideration</option>
                    <option value="conversion">Conversion</option>
                    <option value="retention">Retention</option>
                    <option value="advocacy">Advocacy</option>
                </select>
            </div>

            {/* Campaigns List */}
            <div className="space-y-4">
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
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className="runway-card p-6 hover:shadow-lg transition-shadow"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <h3 className="font-serif text-xl text-neutral-900">{campaign.name}</h3>
                                        <span className={cn(
                                            "px-2 py-1 text-xs border rounded capitalize",
                                            statusInfo.color === 'green' ? "bg-green-50 text-green-700 border-green-200" :
                                                statusInfo.color === 'amber' ? "bg-amber-50 text-amber-700 border-amber-200" :
                                                    statusInfo.color === 'blue' ? "bg-blue-50 text-blue-700 border-blue-200" :
                                                        "bg-neutral-50 text-neutral-700 border-neutral-200"
                                        )}>
                                            <StatusIcon className="w-3 h-3 inline mr-1" />
                                            {statusInfo.label}
                                        </span>
                                        <span className={cn(
                                            "px-2 py-1 text-xs border rounded",
                                            pacingInfo.color === 'green' ? "bg-green-50 text-green-700 border-green-200" :
                                                pacingInfo.color === 'blue' ? "bg-blue-50 text-blue-700 border-blue-200" :
                                                    pacingInfo.color === 'amber' ? "bg-amber-50 text-amber-700 border-amber-200" :
                                                        "bg-red-50 text-red-700 border-red-200"
                                        )}>
                                            <PacingIcon className="w-3 h-3 inline mr-1" />
                                            {pacingInfo.label}
                                        </span>
                                    </div>
                                    <p className="text-sm text-neutral-600 mb-3">{campaign.description}</p>

                                    {/* Cohorts & Channels */}
                                    <div className="flex items-center gap-4 text-xs text-neutral-500">
                                        <div className="flex items-center gap-1">
                                            <Users className="w-3 h-3" />
                                            {campaign.cohorts.map(c => c.name).join(', ')}
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Zap className="w-3 h-3" />
                                            {campaign.channels.join(', ')}
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Calendar className="w-3 h-3" />
                                            {new Date(campaign.start_date).toLocaleDateString()} - {new Date(campaign.end_date).toLocaleDateString()}
                                        </div>
                                    </div>
                                </div>

                                {/* Health Score */}
                                <div className="flex items-center gap-4">
                                    <div className="text-center">
                                        <div className={cn(
                                            "text-2xl font-bold",
                                            campaign.health_score >= 80 ? "text-green-600" :
                                                campaign.health_score >= 60 ? "text-blue-600" :
                                                    campaign.health_score >= 40 ? "text-amber-600" :
                                                        "text-red-600"
                                        )}>
                                            {campaign.health_score}
                                        </div>
                                        <div className="text-xs text-neutral-500">Health</div>
                                    </div>

                                    {/* Actions */}
                                    <div className="flex items-center gap-2">
                                        {campaign.status === 'active' && (
                                            <button
                                                onClick={() => handlePauseCampaign(campaign.id)}
                                                className="p-2 text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
                                                title="Pause campaign"
                                            >
                                                <Pause className="w-4 h-4" />
                                            </button>
                                        )}
                                        {campaign.status === 'paused' && (
                                            <button
                                                onClick={() => handleResumeCampaign(campaign.id)}
                                                className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                                title="Resume campaign"
                                            >
                                                <Play className="w-4 h-4" />
                                            </button>
                                        )}
                                        <Link
                                            to={`/strategy/campaigns/${campaign.id}`}
                                            className="p-2 text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
                                            title="View details"
                                        >
                                            <Eye className="w-4 h-4" />
                                        </Link>
                                        <Link
                                            to={`/strategy/campaigns/${campaign.id}/edit`}
                                            className="p-2 text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
                                            title="Edit campaign"
                                        >
                                            <Edit2 className="w-4 h-4" />
                                        </Link>
                                    </div>
                                </div>
                            </div>

                            {/* Progress Bars */}
                            <div className="grid grid-cols-3 gap-4">
                                {/* Metric Progress */}
                                <div>
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-xs text-neutral-500">{campaign.primary_metric}</span>
                                        <span className="text-xs font-semibold text-neutral-900">
                                            {campaign.current_value} / {campaign.target_value}
                                        </span>
                                    </div>
                                    <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                                        <div
                                            className={cn(
                                                "h-full rounded-full transition-all",
                                                progress >= 100 ? "bg-green-500" :
                                                    progress >= 75 ? "bg-blue-500" :
                                                        progress >= 50 ? "bg-amber-500" :
                                                            "bg-red-500"
                                            )}
                                            style={{ width: `${Math.min(progress, 100)}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Budget Progress */}
                                <div>
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-xs text-neutral-500">Budget</span>
                                        <span className="text-xs font-semibold text-neutral-900">
                                            ${(campaign.budget_spent / 1000).toFixed(0)}k / ${(campaign.budget_total / 1000).toFixed(0)}k
                                        </span>
                                    </div>
                                    <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-purple-500 rounded-full transition-all"
                                            style={{ width: `${Math.min(budgetProgress, 100)}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Moves Progress */}
                                <div>
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-xs text-neutral-500">Moves</span>
                                        <span className="text-xs font-semibold text-neutral-900">
                                            {campaign.completed_moves} / {campaign.total_moves}
                                        </span>
                                    </div>
                                    <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-neutral-900 rounded-full transition-all"
                                            style={{ width: `${Math.min(moveProgress, 100)}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    );
                })}
            </div>

            {/* Empty State */}
            {filteredCampaigns.length === 0 && (
                <div className="text-center py-12 runway-card">
                    <Target className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-neutral-900 mb-2">No campaigns found</h3>
                    <p className="text-neutral-600 mb-6">
                        {searchTerm || filterStatus !== 'all' || filterObjective !== 'all'
                            ? 'Try adjusting your filters'
                            : 'Create your first campaign to get started'}
                    </p>
                    {!searchTerm && filterStatus === 'all' && filterObjective === 'all' && (
                        <Link
                            to="/strategy/campaigns/new"
                            className="inline-flex items-center gap-2 px-6 py-3 bg-neutral-900 text-white rounded-lg font-medium hover:bg-neutral-800"
                        >
                            <Plus className="w-5 h-5" />
                            Create Campaign
                        </Link>
                    )}
                </div>
            )}
        </div>
    );
}
