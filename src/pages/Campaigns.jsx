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
    Zap,
    Edit2,
    Archive,
    Filter,
    LayoutGrid,
    List
} from 'lucide-react';
import { cn } from '../utils/cn';
import {
    LuxeButton,
    LuxeCard,
    LuxeBadge,
    LuxeInput,
    HeroSection,
    StatCard,
    EmptyState,
    FilterPills,
    ProgressRing,
    LuxeSkeleton
} from '../components/ui/PremiumUI';
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
    const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

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
        avg_health: Math.round(campaigns.reduce((sum, c) => sum + c.health_score, 0) / (campaigns.length || 1)),
        at_risk: campaigns.filter(c => c.health_score < 60).length,
    };

    const statusFilters = [
        { value: 'all', label: 'All Statuses' },
        { value: 'active', label: 'Active', count: campaigns.filter(c => c.status === 'active').length },
        { value: 'draft', label: 'Draft', count: campaigns.filter(c => c.status === 'draft').length },
        { value: 'paused', label: 'Paused', count: campaigns.filter(c => c.status === 'paused').length },
        { value: 'completed', label: 'Completed', count: campaigns.filter(c => c.status === 'completed').length },
    ];

    return (
        <motion.div
            className="space-y-12 max-w-[1440px] mx-auto px-6 py-8"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={staggerContainer}
        >
            <motion.div variants={fadeInUp}>
                <HeroSection
                    title="Campaigns"
                    subtitle="Orchestrate all marketing activities from positioning to execution."
                    metrics={[
                        { label: 'Total Campaigns', value: stats.total.toString() },
                        { label: 'Active Now', value: stats.active.toString() },
                        { label: 'Avg Health', value: `${stats.avg_health}%` }
                    ]}
                    actions={
                        <LuxeButton
                            onClick={() => navigate('/campaigns/new')}
                            className="bg-white text-neutral-900 hover:bg-neutral-100 border-none"
                        >
                            <Plus className="w-4 h-4 mr-2" />
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
                <StatCard
                    label="Total Campaigns"
                    value={stats.total}
                    icon={Target}
                    trend="neutral"
                />
                <StatCard
                    label="Active"
                    value={stats.active}
                    icon={Play}
                    trend="up"
                    change="+1 this month"
                />
                <StatCard
                    label="Avg Health"
                    value={`${stats.avg_health}%`}
                    icon={TrendingUp}
                    trend={stats.avg_health >= 70 ? 'up' : 'down'}
                    sparklineData={[65, 68, 72, 75, 74, 78, stats.avg_health]}
                />
                <StatCard
                    label="At Risk"
                    value={stats.at_risk}
                    icon={AlertCircle}
                    trend={stats.at_risk > 0 ? 'down' : 'neutral'}
                    change={stats.at_risk > 0 ? 'Needs attention' : 'All good'}
                />
            </motion.div>

            {/* Search & Filters */}
            <motion.div variants={fadeInUp} className="space-y-6">
                <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
                    <div className="flex-1 w-full md:max-w-md">
                        <LuxeInput
                            icon={Search}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            placeholder="Search campaigns..."
                            className="h-12"
                        />
                    </div>

                    <div className="flex items-center gap-2 bg-neutral-100 p-1 rounded-lg">
                        <button
                            onClick={() => setViewMode('grid')}
                            className={cn(
                                "p-2 rounded-md transition-all",
                                viewMode === 'grid' ? "bg-white shadow-sm text-neutral-900" : "text-neutral-500 hover:text-neutral-900"
                            )}
                        >
                            <LayoutGrid className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => setViewMode('list')}
                            className={cn(
                                "p-2 rounded-md transition-all",
                                viewMode === 'list' ? "bg-white shadow-sm text-neutral-900" : "text-neutral-500 hover:text-neutral-900"
                            )}
                        >
                            <List className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                <div className="flex flex-wrap gap-4 items-center justify-between border-b border-neutral-100 pb-4">
                    <FilterPills
                        filters={statusFilters}
                        activeFilter={filterStatus}
                        onFilterChange={setFilterStatus}
                    />

                    <div className="flex items-center gap-2">
                        <Filter className="w-4 h-4 text-neutral-400" />
                        <select
                            value={filterObjective}
                            onChange={(e) => setFilterObjective(e.target.value)}
                            className="bg-transparent border-none text-sm font-medium text-neutral-600 focus:ring-0 cursor-pointer"
                        >
                            <option value="all">All Objectives</option>
                            <option value="awareness">Awareness</option>
                            <option value="consideration">Consideration</option>
                            <option value="conversion">Conversion</option>
                            <option value="retention">Retention</option>
                            <option value="advocacy">Advocacy</option>
                        </select>
                    </div>
                </div>
            </motion.div>

            {/* Campaigns List */}
            {isLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3].map((i) => (
                        <LuxeSkeleton key={i} className="h-[400px] rounded-2xl" />
                    ))}
                </div>
            ) : filteredCampaigns.length === 0 ? (
                <EmptyState
                    icon={Target}
                    title="No campaigns found"
                    description={searchTerm || filterStatus !== 'all' || filterObjective !== 'all'
                        ? 'Try adjusting your filters to see results.'
                        : 'Create your first campaign to get started with marketing orchestration.'}
                    action={
                        !searchTerm && filterStatus === 'all' && filterObjective === 'all' ? (
                            () => navigate('/campaigns/new')
                        ) : null
                    }
                    actionLabel="Create Campaign"
                />
            ) : (
                <motion.div
                    className={cn(
                        "gap-6",
                        viewMode === 'grid' ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3" : "flex flex-col space-y-4"
                    )}
                    variants={staggerContainer}
                >
                    {filteredCampaigns.map((campaign) => {
                        const statusInfo = CAMPAIGN_STATUSES[campaign.status];
                        const pacingInfo = PACING_STATUS[campaign.pacing_status];
                        const progress = (campaign.current_value / campaign.target_value) * 100;

                        return (
                            <motion.div
                                key={campaign.id}
                                variants={fadeInUp}
                            >
                                <LuxeCard
                                    className="h-full hover:shadow-xl transition-all duration-300 group cursor-pointer"
                                    onClick={() => navigate(`/campaigns/${campaign.id}`)}
                                >
                                    <div className="p-6">
                                        <div className="flex items-start justify-between mb-6">
                                            <div className="flex gap-2">
                                                <LuxeBadge variant={statusInfo.color === 'dark' ? "dark" : "neutral"}>
                                                    {statusInfo.label}
                                                </LuxeBadge>
                                                <LuxeBadge variant="neutral">
                                                    {pacingInfo.label}
                                                </LuxeBadge>
                                            </div>
                                            <button
                                                onClick={(e) => { e.stopPropagation(); navigate(`/campaigns/${campaign.id}/edit`); }}
                                                className="p-2 text-neutral-400 hover:text-neutral-900 hover:bg-neutral-100 rounded-full transition-colors opacity-0 group-hover:opacity-100"
                                            >
                                                <Edit2 className="w-4 h-4" />
                                            </button>
                                        </div>

                                        <h3 className="font-display text-2xl font-medium text-neutral-900 mb-2 group-hover:text-neutral-700 transition-colors line-clamp-2">
                                            {campaign.name}
                                        </h3>
                                        <p className="text-sm text-neutral-500 mb-6 line-clamp-2 h-10">
                                            {campaign.description}
                                        </p>

                                        <div className="flex items-center justify-between mb-6">
                                            <div className="flex items-center gap-4">
                                                <div className="flex -space-x-2">
                                                    {[...Array(3)].map((_, i) => (
                                                        <div key={i} className="w-8 h-8 rounded-full bg-neutral-100 border-2 border-white flex items-center justify-center text-xs font-medium text-neutral-600">
                                                            {String.fromCharCode(65 + i)}
                                                        </div>
                                                    ))}
                                                </div>
                                                <span className="text-xs text-neutral-500 font-medium">
                                                    {campaign.cohorts.length} Cohorts
                                                </span>
                                            </div>
                                            <div className="text-right">
                                                <span className="text-2xl font-display font-medium text-neutral-900">
                                                    {campaign.health_score}%
                                                </span>
                                                <span className="block text-[10px] uppercase tracking-wider text-neutral-400 font-bold">
                                                    Health
                                                </span>
                                            </div>
                                        </div>

                                        <div className="pt-6 border-t border-neutral-100">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-xs font-bold text-neutral-400 uppercase tracking-wider">
                                                    Progress
                                                </span>
                                                <span className="text-xs font-medium text-neutral-900">
                                                    {Math.round(progress)}%
                                                </span>
                                            </div>
                                            <div className="w-full h-1.5 bg-neutral-100 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-neutral-900 rounded-full transition-all duration-1000"
                                                    style={{ width: `${Math.min(progress, 100)}%` }}
                                                />
                                            </div>
                                            <div className="flex justify-between mt-2">
                                                <span className="text-xs text-neutral-500">
                                                    {new Date(campaign.start_date).toLocaleDateString()}
                                                </span>
                                                <span className="text-xs text-neutral-500">
                                                    {new Date(campaign.end_date).toLocaleDateString()}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </LuxeCard>
                            </motion.div>
                        );
                    })}
                </motion.div>
            )}
        </motion.div>
    );
}
