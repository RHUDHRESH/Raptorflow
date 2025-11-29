import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    ArrowLeft,
    Edit2,
    Target,
    Users,
    Zap,
    Calendar,
    BarChart3,
    ChevronRight,
    CheckCircle2,
    Clock,
    AlertCircle,
    TrendingUp
} from 'lucide-react';
import {
    HeroSection,
    LuxeHeading,
    LuxeButton,
    LuxeCard,
    LuxeBadge,
    StatCard,
    TimelineView,
    LuxeSkeleton
} from '../components/ui/PremiumUI';
import { pageTransition, fadeInUp, staggerContainer } from '../utils/animations';
import { campaignService } from '../services/campaignService';
import { toast } from '../components/Toast';

export default function CampaignDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [campaign, setCampaign] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCampaign = async () => {
            setLoading(true);
            try {
                const { data, error } = await campaignService.getCampaign(id);
                if (data) {
                    setCampaign(data);
                } else {
                    console.error(error);
                    toast.error('Failed to load campaign');
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        if (id) fetchCampaign();
    }, [id]);

    if (loading) {
        return (
            <div className="max-w-[1440px] mx-auto px-6 py-8 space-y-8">
                <LuxeSkeleton className="h-64 w-full rounded-2xl" />
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    {[...Array(4)].map((_, i) => (
                        <LuxeSkeleton key={i} className="h-40 rounded-xl" />
                    ))}
                </div>
            </div>
        );
    }

    if (!campaign) return <div className="p-10 text-center">Campaign not found</div>;

    // Transform moves for TimelineView
    const timelineItems = (campaign.moves && campaign.moves.length > 0 ? campaign.moves : [
        { id: 'm1', name: 'Authority Sprint', status: 'completed', type: 'Authority', metric: '45 Leads', end_date: 'Oct 12' },
        { id: 'm2', name: 'Consideration Sprint', status: 'active', type: 'Consideration', metric: '12 Demos', end_date: 'Oct 24' },
        { id: 'm3', name: 'Objection Crusher', status: 'planned', type: 'Objection', metric: 'Pending', end_date: 'Nov 05' },
    ]).map(move => ({
        title: move.name,
        date: move.end_date || 'TBD',
        description: `${move.type} • Goal: ${move.metric || 'TBD'}`,
        status: move.status
    }));

    return (
        <motion.div
            className="max-w-[1440px] mx-auto px-6 py-8 space-y-12"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={staggerContainer}
        >
            {/* Hero Section */}
            <motion.div variants={fadeInUp}>
                <div className="mb-6">
                    <button
                        onClick={() => navigate('/campaigns')}
                        className="flex items-center text-sm text-neutral-500 hover:text-neutral-900 transition-colors group"
                    >
                        <ArrowLeft className="w-4 h-4 mr-1 group-hover:-translate-x-1 transition-transform" />
                        Back to Campaigns
                    </button>
                </div>

                <HeroSection
                    title={campaign.name}
                    subtitle={campaign.description || `Objective: ${campaign.objective}`}
                    metrics={[
                        { label: 'Health Score', value: `${campaign.health_score || 92}%` },
                        { label: 'Budget Used', value: `${Math.round((campaign.budget_spent / campaign.budget_total) * 100) || 0}%` },
                        { label: 'Days Left', value: '14' }
                    ]}
                    actions={
                        <div className="flex gap-3">
                            <LuxeButton
                                className="bg-white text-neutral-900 hover:bg-neutral-100 border-none"
                                onClick={() => navigate(`/campaigns/${id}/edit`)}
                            >
                                <Edit2 className="w-4 h-4 mr-2" />
                                Edit Campaign
                            </LuxeButton>
                            <LuxeBadge
                                variant={campaign.status === 'active' ? 'dark' : 'neutral'}
                                className="px-4 py-2 text-sm bg-white/10 text-white border-white/20 backdrop-blur-sm"
                            >
                                {campaign.status.toUpperCase()}
                            </LuxeBadge>
                        </div>
                    }
                />
            </motion.div>

            {/* Quick Stats */}
            <motion.div
                className="grid grid-cols-1 md:grid-cols-4 gap-6"
                variants={staggerContainer}
            >
                <StatCard
                    label="Primary Metric"
                    value={`${campaign.current_value || 0}`}
                    change={`Target: ${campaign.target_value}`}
                    icon={Target}
                    trend="up"
                />

                <StatCard
                    label="Budget Spent"
                    value={`$${(campaign.budget_spent || 0).toLocaleString()}`}
                    change={`of $${(campaign.budget_total || 0).toLocaleString()}`}
                    icon={BarChart3}
                    trend="neutral"
                />

                <StatCard
                    label="Cohorts"
                    value={campaign.cohorts?.length || 0}
                    change="Active segments"
                    icon={Users}
                    trend="neutral"
                />

                <StatCard
                    label="Channels"
                    value={campaign.channels?.length || 0}
                    change="Active channels"
                    icon={Zap}
                    trend="neutral"
                />
            </motion.div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left: Strategy & Config */}
                <motion.div variants={fadeInUp} className="space-y-8">
                    <LuxeCard title="Targeting Strategy" className="h-full">
                        <div className="space-y-8">
                            <div>
                                <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider block mb-4">Cohorts in Scope</label>
                                <div className="space-y-3">
                                    {campaign.cohorts?.map((c, i) => (
                                        <div key={i} className="flex items-center gap-4 p-3 bg-neutral-50 border border-neutral-100 rounded-xl hover:border-neutral-300 transition-colors">
                                            <div className="w-8 h-8 rounded-full bg-white border border-neutral-200 flex items-center justify-center text-neutral-500 shadow-sm">
                                                <Users className="w-4 h-4" />
                                            </div>
                                            <span className="font-medium text-neutral-900">{c.cohort_id}</span>
                                        </div>
                                    )) || <span className="text-sm text-neutral-400 italic">No cohorts defined</span>}
                                </div>
                            </div>

                            <div className="h-px bg-neutral-100 w-full" />

                            <div>
                                <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider block mb-4">Active Channels</label>
                                <div className="flex flex-wrap gap-2">
                                    {campaign.channels?.map((c, i) => (
                                        <div key={i} className="flex items-center gap-2 px-3 py-1.5 bg-neutral-900 text-white rounded-full text-sm font-medium">
                                            <Zap className="w-3 h-3" />
                                            {c.channel}
                                        </div>
                                    )) || <span className="text-sm text-neutral-400 italic">No channels defined</span>}
                                </div>
                            </div>

                            <div className="h-px bg-neutral-100 w-full" />

                            <div>
                                <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider block mb-4">Timeline</label>
                                <div className="flex items-center gap-2 text-neutral-900 font-medium">
                                    <Calendar className="w-4 h-4 text-neutral-500" />
                                    {new Date(campaign.start_date).toLocaleDateString()} — {new Date(campaign.end_date).toLocaleDateString()}
                                </div>
                            </div>
                        </div>
                    </LuxeCard>
                </motion.div>

                {/* Right: Moves Timeline & Analytics */}
                <motion.div variants={fadeInUp} className="lg:col-span-2 space-y-8">
                    {/* Performance Placeholder */}
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <h3 className="font-display text-xl font-medium text-neutral-900">Performance Overview</h3>
                        </div>
                        <LuxeCard className="p-12 flex flex-col items-center justify-center text-center border-dashed bg-neutral-50/50 min-h-[240px]">
                            <div className="w-16 h-16 bg-white rounded-full shadow-sm flex items-center justify-center mb-4">
                                <BarChart3 className="w-8 h-8 text-neutral-300" />
                            </div>
                            <h4 className="font-display text-lg font-medium text-neutral-900 mb-2">Campaign Analytics</h4>
                            <p className="text-neutral-500 max-w-md leading-relaxed">
                                Performance charts and detailed metrics will appear here as the campaign progresses and data is collected.
                            </p>
                        </LuxeCard>
                    </div>

                    {/* Move Sequence */}
                    <div className="space-y-6">
                        <div className="flex items-center justify-between">
                            <h3 className="font-display text-xl font-medium text-neutral-900">Move Sequence</h3>
                            <LuxeButton size="sm" icon={Target} variant="outline">Add Move</LuxeButton>
                        </div>

                        <LuxeCard className="p-8">
                            <TimelineView items={timelineItems} />
                        </LuxeCard>
                    </div>
                </motion.div>
            </div>
        </motion.div>
    );
}
